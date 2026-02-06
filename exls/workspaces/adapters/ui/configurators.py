from __future__ import annotations

from abc import ABC
from enum import StrEnum
from typing import Any, Dict, List, Protocol, cast, runtime_checkable

from typing_extensions import Optional

from exls.shared.adapters.ui.facade.facade import IOBaseModelFacade
from exls.shared.adapters.ui.input.interfaces import EditDictionaryError
from exls.shared.adapters.ui.input.values import UserCancellationException
from exls.shared.adapters.ui.output.values import OutputFormat
from exls.shared.adapters.ui.shared.render.render import (
    DictToYamlStringRenderer,
    YamlRenderContext,
)
from exls.shared.core.exceptions import ExalsiusError
from exls.shared.core.utils import deep_merge, generate_random_name
from exls.workspaces.core.domain import WorkerGroupResources, WorkspaceGPUVendor


class InvalidWorkspaceConfiguration(ExalsiusError):
    """Exception raised when the workspace configuration is invalid."""

    pass


class IntegratedWorkspaceTemplates(StrEnum):
    JUPYTER = "jupyter-notebook-template"
    MARIMO = "marimo-workspace-template"
    DEV_POD = "vscode-devcontainer-template"
    DIST_TRAINING = "diloco-training-template"
    LLM_D = "llm-d-model-template"
    OTHER = "other"

    @classmethod
    def from_str(cls, value: str) -> IntegratedWorkspaceTemplates:
        try:
            return cls(value)
        except ValueError:
            return cls.OTHER


class WorkspaceEditorRenderBundle:
    def __init__(
        self,
        editor_renderer: DictToYamlStringRenderer,
        editor_render_context: YamlRenderContext,
        message_output_format: OutputFormat,
    ):
        self.editor_renderer: DictToYamlStringRenderer = editor_renderer
        self.editor_render_context: YamlRenderContext = editor_render_context
        self.message_output_format: OutputFormat = message_output_format


@runtime_checkable
class WorkspaceConfigurator(Protocol):
    @property
    def template_id(self) -> str:
        """The ID of the template this configurator supports."""
        ...

    def configure(self, io_facade: IOBaseModelFacade) -> Dict[str, Any]:
        """
        Full workflow: collect inputs -> optional advanced edit -> validate.
        Returns the final valid dictionary of variables.
        """
        ...


class BaseWorkspaceConfigurator(ABC):
    """
    Shared logic for editing and validation.
    """

    def __init__(self, bundle: WorkspaceEditorRenderBundle):
        self._editor_render_bundle: WorkspaceEditorRenderBundle = bundle

    @property
    def template_id(self) -> IntegratedWorkspaceTemplates:
        raise NotImplementedError

    def _validate(
        self,
        ref_variables: Dict[str, Any],
        edited_variables: Dict[str, Any],
        parent_keys: Optional[List[str]] = None,
    ) -> None:
        path = parent_keys or []
        # Validate that all required variables defined in the reference
        # are defined in the edited variables.
        for key, ref_value in ref_variables.items():
            if key not in edited_variables:
                missing_var_path = ".".join(path + [key])
                raise InvalidWorkspaceConfiguration(
                    f"Workspace template configuration requires variable '{missing_var_path}' to be set."
                )

            if isinstance(ref_value, dict) and isinstance(edited_variables[key], dict):
                self._validate(
                    cast(Dict[str, Any], ref_value),
                    cast(Dict[str, Any], edited_variables[key]),
                    parent_keys=path + [key],
                )

    def _configure(
        self, variables: Dict[str, Any], io_facade: IOBaseModelFacade
    ) -> Dict[str, Any]:
        # We do not want to show this to the user
        global_variables: Optional[Dict[str, Any]] = None
        deploymentNumReplicas: Optional[int] = None
        if "global" in variables:
            global_variables = variables.pop("global")
        if "deploymentNumReplicas" in variables:
            deploymentNumReplicas = variables.pop("deploymentNumReplicas")

        # Advanced Editing
        edited_variables: Dict[str, Any] = variables
        if io_facade.ask_confirm(
            message="Do you want to edit the workspace configuration file?",
            default=True,
        ):
            edited_variables = self._run_editor_loop(edited_variables, io_facade)

        # Add back the global variables and deploymentNumReplicas
        if global_variables:
            edited_variables["global"] = global_variables
        if deploymentNumReplicas:
            edited_variables["deploymentNumReplicas"] = deploymentNumReplicas

        return edited_variables

    def configure_and_validate(
        self, variables: Dict[str, Any], io_facade: IOBaseModelFacade
    ) -> Dict[str, Any]:
        edited_variables: Dict[str, Any] = self._configure(variables.copy(), io_facade)
        # Final Validation
        self._validate(variables, edited_variables)
        return edited_variables

    def _run_editor_loop(
        self, variables: Dict[str, Any], io_facade: IOBaseModelFacade
    ) -> Dict[str, Any]:
        current_variables = variables.copy()
        while True:
            try:
                edited_variables: Dict[str, Any] = io_facade.edit_dictionary(
                    dictionary=current_variables,
                    renderer=self._editor_render_bundle.editor_renderer,
                    render_context=self._editor_render_bundle.editor_render_context,
                )
                return edited_variables
            except UserCancellationException:
                io_facade.display_info_message(
                    "User cancelled the workspace template editing. No changes were made.",
                    self._editor_render_bundle.message_output_format,
                )
                return current_variables
            except (EditDictionaryError, Exception) as e:
                io_facade.display_error_message(
                    f"An unexpected error occurred while editing the workspace template: {e}",
                    self._editor_render_bundle.message_output_format,
                )
                try_again: bool = io_facade.ask_confirm(
                    message=(
                        "Do you want to try to edit the workspace template again? "
                        "y: Will load the original workspace template and try to edit it again."
                        "n: Will use the original workspace template and continue with the deployment."
                    ),
                    default=False,
                )
                if not try_again:
                    return current_variables


class JupyterConfigurator(BaseWorkspaceConfigurator):
    def __init__(
        self,
        editor_render_bundle: WorkspaceEditorRenderBundle,
        password: str,
    ):
        super().__init__(editor_render_bundle)
        self._password: str = password

    @property
    def template_id(self) -> IntegratedWorkspaceTemplates:
        return IntegratedWorkspaceTemplates.JUPYTER

    def _validate(
        self,
        ref_variables: Dict[str, Any],
        edited_variables: Dict[str, Any],
        parent_keys: Optional[List[str]] = None,
    ) -> None:
        super()._validate(ref_variables, edited_variables, parent_keys=parent_keys)
        if edited_variables.get("notebookPassword", "") == "":
            raise InvalidWorkspaceConfiguration(
                "Jupyter workspace requires 'notebookPassword' to be set."
            )

    def configure_and_validate(
        self, variables: Dict[str, Any], io_facade: IOBaseModelFacade
    ) -> Dict[str, Any]:
        variables["notebookPassword"] = self._password
        return super().configure_and_validate(variables, io_facade)


class MarimoConfigurator(BaseWorkspaceConfigurator):
    def __init__(
        self,
        editor_render_bundle: WorkspaceEditorRenderBundle,
        password: str,
    ):
        super().__init__(editor_render_bundle)
        self._password: str = password

    @property
    def template_id(self) -> IntegratedWorkspaceTemplates:
        return IntegratedWorkspaceTemplates.MARIMO

    def _validate(
        self,
        ref_variables: Dict[str, Any],
        edited_variables: Dict[str, Any],
        parent_keys: Optional[List[str]] = None,
    ) -> None:
        super()._validate(ref_variables, edited_variables, parent_keys=parent_keys)
        if edited_variables.get("tokenPassword", "") == "":
            raise InvalidWorkspaceConfiguration(
                "Marimo workspace requires 'tokenPassword' to be set."
            )

    def configure_and_validate(
        self, variables: Dict[str, Any], io_facade: IOBaseModelFacade
    ) -> Dict[str, Any]:
        variables["tokenPassword"] = self._password
        return super().configure_and_validate(variables, io_facade)


class DevPodConfigurator(BaseWorkspaceConfigurator):
    def __init__(
        self,
        editor_render_bundle: WorkspaceEditorRenderBundle,
        ssh_password: Optional[str],
        ssh_public_key: Optional[str],
    ):
        super().__init__(editor_render_bundle)
        self._ssh_password: Optional[str] = ssh_password
        self._ssh_public_key: Optional[str] = ssh_public_key

    @property
    def template_id(self) -> IntegratedWorkspaceTemplates:
        return IntegratedWorkspaceTemplates.DEV_POD

    def _validate(
        self,
        ref_variables: Dict[str, Any],
        edited_variables: Dict[str, Any],
        parent_keys: Optional[List[str]] = None,
    ) -> None:
        super()._validate(ref_variables, edited_variables, parent_keys=parent_keys)
        ssh_password: str = edited_variables.get("sshPassword", "")
        ssh_public_key: str = edited_variables.get("sshPublicKey", "")
        if ssh_password == "" and ssh_public_key == "":
            raise InvalidWorkspaceConfiguration(
                "VSCode Dev Pod workspace requires at least one of 'sshPassword' or 'sshPublicKey' to be set and non-empty."
            )

    def configure_and_validate(
        self, variables: Dict[str, Any], io_facade: IOBaseModelFacade
    ) -> Dict[str, Any]:
        variables["sshPassword"] = self._ssh_password or ""
        variables["sshPublicKey"] = self._ssh_public_key or ""
        edited_variables: Dict[str, Any] = self._configure(variables.copy(), io_facade)

        self._validate(variables, edited_variables)
        # This is allows users to delete one of the two access methods during the configuration
        # and still pass the validation.
        if "sshPassword" not in variables:
            variables["sshPassword"] = ""
        if "sshPublicKey" not in variables:
            variables["sshPublicKey"] = ""

        return edited_variables


class LLMInferenceConfigurator(BaseWorkspaceConfigurator):
    def __init__(
        self,
        editor_render_bundle: WorkspaceEditorRenderBundle,
        huggingface_token: str,
        model_name: str,
        workspace_name: str,
        num_gpus: int,
        gpu_vendor: Optional[WorkspaceGPUVendor] = None,
    ):
        super().__init__(editor_render_bundle)
        self._huggingface_token: str = huggingface_token
        self._model_name: str = model_name
        self._workspace_name: str = workspace_name
        self._num_gpus: int = num_gpus
        self._gpu_vendor: Optional[WorkspaceGPUVendor] = gpu_vendor

    @property
    def template_id(self) -> IntegratedWorkspaceTemplates:
        return IntegratedWorkspaceTemplates.LLM_D

    def _extract_model_short_name(self, full_model_name: str) -> str:
        """
        Extract short model name from full HuggingFace model path.
        Example: "Qwen/Qwen3-1.7B" -> "Qwen3-1.7B"
        """
        if "/" in full_model_name:
            return full_model_name.split("/")[-1]
        return full_model_name

    def _validate(
        self,
        ref_variables: Dict[str, Any],
        edited_variables: Dict[str, Any],
        parent_keys: Optional[List[str]] = None,
    ) -> None:
        # Note: We don't validate huggingfaceToken here because it's set programmatically
        # in configure_and_validate() and we trust that value. We only validate the
        # structural elements that come from the template.
        super()._validate(ref_variables, edited_variables, parent_keys=parent_keys)

    def configure_and_validate(
        self, variables: Dict[str, Any], io_facade: IOBaseModelFacade
    ) -> Dict[str, Any]:
        # Set the Hugging Face token - this will be preserved through editing
        variables["huggingfaceToken"] = self._huggingface_token

        # Extract model short name
        model_short_name = self._extract_model_short_name(self._model_name)

        # Configure model artifacts
        if "ms" not in variables:
            variables["ms"] = {}
        variables["ms"]["fullnameOverride"] = f"{self._workspace_name}-ms"
        if "modelArtifacts" not in variables["ms"]:
            variables["ms"]["modelArtifacts"] = {}

        variables["ms"]["modelArtifacts"][
            "authSecretName"
        ] = f"{self._workspace_name}-hf-token"
        variables["ms"]["modelArtifacts"]["uri"] = f"hf://{self._model_name}"
        variables["ms"]["modelArtifacts"]["name"] = self._model_name

        # Set model labels
        if "labels" not in variables["ms"]["modelArtifacts"]:
            variables["ms"]["modelArtifacts"]["labels"] = {}
        variables["ms"]["modelArtifacts"]["labels"]["llm-d.ai/model"] = model_short_name

        # Configure inference pool model server labels
        if "ip" not in variables:
            variables["ip"] = {}
        if "inferencePool" not in variables["ip"]:
            variables["ip"]["inferencePool"] = {}
        if "modelServers" not in variables["ip"]["inferencePool"]:
            variables["ip"]["inferencePool"]["modelServers"] = {}
        if "matchLabels" not in variables["ip"]["inferencePool"]["modelServers"]:
            variables["ip"]["inferencePool"]["modelServers"]["matchLabels"] = {}

        variables["ip"]["inferencePool"]["modelServers"]["matchLabels"][
            "llm-d.ai/model"
        ] = model_short_name

        # Set tensor parallelism to num_gpus (ms.decode.parallelism.tensor)
        if "decode" not in variables["ms"]:
            variables["ms"]["decode"] = {}
        if "parallelism" not in variables["ms"]["decode"]:
            variables["ms"]["decode"]["parallelism"] = {}
        variables["ms"]["decode"]["parallelism"]["tensor"] = self._num_gpus

        # Set accelerator type from resolved GPU vendor (AMD or NVIDIA)
        if "accelerator" not in variables["ms"]:
            variables["ms"]["accelerator"] = {}
        if self._gpu_vendor == WorkspaceGPUVendor.AMD:
            variables["ms"]["accelerator"]["type"] = "amd"
        else:
            # Default to nvidia for NVIDIA, NO_GPU, UNKNOWN, or None
            variables["ms"]["accelerator"]["type"] = "nvidia"

        return super().configure_and_validate(variables, io_facade)


class DistributedTrainingModels(StrEnum):
    RESNET50 = "resnet50"
    RESNET101 = "resnet101"
    WAV2VEC2 = "wav2vec2"
    GPT_NEO = "gpt-neo"
    GPT_NEO_X = "gpt-neo-x"
    # GPT_NEO_TINY = "gpt-neo-tiny"
    GCN = "gcn"

    @classmethod
    def get_dataset_for_model(cls, model: DistributedTrainingModels) -> str:
        if model == cls.RESNET50:
            return "imagenet"
        elif model == cls.RESNET101:
            return "imagenet"
        elif model == cls.WAV2VEC2:
            return "librispeech"
        elif model == cls.GPT_NEO:
            return "c4"
        elif model == cls.GPT_NEO_X:
            return "c4"
        # elif model == cls.GPT_NEO_TINY:
        #    return "c4"
        elif model == cls.GCN:
            return "ogbn_arxiv"


class GradientCompression(StrEnum):
    NO_COMPRESSION = "no"
    WEAK_COMPRESSION = "weak"
    MEDIUM_COMPRESSION = "medium"
    STRONG_COMPRESSION = "strong"
    ULTRA_COMPRESSION = "ultra"


class DistributedTrainingConfigurator(BaseWorkspaceConfigurator):
    def __init__(
        self,
        editor_render_bundle: WorkspaceEditorRenderBundle,
        model: DistributedTrainingModels,
        gradient_compression: GradientCompression,
        wandb_token: str,
        hf_token: str,
        worker_groups: List[WorkerGroupResources],
    ):
        super().__init__(editor_render_bundle)
        self._model: DistributedTrainingModels = model
        self._gradient_compression: GradientCompression = gradient_compression
        self._wandb_token: str = wandb_token
        self._hf_token: str = hf_token
        self._worker_groups: List[WorkerGroupResources] = worker_groups

    @property
    def _heterogenous(self) -> bool:
        return (
            len(
                set(
                    [
                        wg.worker_resources.gpu_vendor
                        for wg in self._worker_groups
                        if wg.worker_resources.gpu_vendor
                    ]
                )
            )
            > 1
        )

    @property
    def min_storage_gb(self) -> int:
        return min([wg.worker_resources.storage_gb for wg in self._worker_groups])

    @property
    def min_memory_gb(self) -> int:
        return min([wg.worker_resources.memory_gb for wg in self._worker_groups])

    @property
    def num_nodes(self) -> int:
        return sum([wg.num_workers for wg in self._worker_groups])

    @property
    def num_amd_nodes(self) -> int:
        return sum(
            [
                wg.num_workers
                for wg in self._worker_groups
                if wg.worker_resources.gpu_vendor == WorkspaceGPUVendor.AMD
            ]
        )

    @property
    def num_nvidia_nodes(self) -> int:
        return sum(
            [
                wg.num_workers
                for wg in self._worker_groups
                if wg.worker_resources.gpu_vendor == WorkspaceGPUVendor.NVIDIA
            ]
        )

    @property
    def template_id(self) -> IntegratedWorkspaceTemplates:
        return IntegratedWorkspaceTemplates.DIST_TRAINING

    def _verify_resources(self):
        if (
            self._model
            in [
                DistributedTrainingModels.WAV2VEC2,
                DistributedTrainingModels.RESNET50,
                DistributedTrainingModels.RESNET101,
            ]
            and self.min_storage_gb < 250
        ):
            raise InvalidWorkspaceConfiguration(
                f"{self._model.value} model requires at least 250GB of storage."
            )
        if self._model == DistributedTrainingModels.GCN and self.min_memory_gb < 32:
            raise InvalidWorkspaceConfiguration(
                "GCN model requires at least 32GB of memory."
            )

    def _get_torch_elastic_config(self) -> Dict[str, Any]:
        min_nodes: int = self.num_nodes
        max_nodes: int = self.num_nodes
        return {
            "minNodes": min_nodes,
            "maxNodes": max_nodes,
        }

    def _get_prgroup_backend(self) -> str:
        if not self._heterogenous:
            return "nccl"
        else:
            return "gloo"

    def _get_gpu_variables(self) -> Dict[str, Any]:
        return {
            "nvidia": {"enabled": self.num_nvidia_nodes > 0},
            "amd": {"enabled": self.num_amd_nodes > 0},
        }

    def _translate_compression_config_for_gradient_compression(
        self, gradient_compression: GradientCompression
    ) -> Dict[str, Any]:
        if gradient_compression == GradientCompression.NO_COMPRESSION:
            return {
                "localSteps": 1,
                "optimMethod": "sgd",
            }
        elif gradient_compression == GradientCompression.WEAK_COMPRESSION:
            return {"localSteps": 20, "optimMethod": "sgd"}
        elif gradient_compression == GradientCompression.MEDIUM_COMPRESSION:
            return {"localSteps": 50, "optimMethod": "sgd"}
        elif gradient_compression == GradientCompression.STRONG_COMPRESSION:
            return {"localSteps": 100, "optimMethod": "sgd"}
        elif gradient_compression == GradientCompression.ULTRA_COMPRESSION:
            return {
                "localSteps": 100,
                "optimMethod": "demo",
                "compressionDecay": 0.95,
                "compressionTopk": 32,
            }

    def _get_training_config_for_model(
        self,
        model: DistributedTrainingModels,
        gradient_compression: GradientCompression,
    ) -> Dict[str, Any]:
        lr: float = 4e-4
        outer_lr: float = 0.7
        compressionDecay: float = 0.9
        compressionTopk: int = 32
        if model in [
            DistributedTrainingModels.GPT_NEO,
            DistributedTrainingModels.GPT_NEO_X,
        ]:
            compressionDecay = 0.999
            if gradient_compression == GradientCompression.ULTRA_COMPRESSION:
                lr = 8e-4
        if model == DistributedTrainingModels.WAV2VEC2:
            lr = 3e-4
            outer_lr = 0.8
            compressionDecay = 0.999
        elif model == DistributedTrainingModels.GCN:
            lr = 1e-4
            compressionDecay = 0.999
        return {
            "lr": lr,
            "outerLr": outer_lr,
            "compressionDecay": compressionDecay,
            "compressionTopk": compressionTopk,
        }

    def _get_model_variables(self, model: DistributedTrainingModels) -> Dict[str, Any]:
        return {
            "model": model.value,
            "dataset": self._model.get_dataset_for_model(model),
        }

    def _get_metadata_variable_defaults(
        self,
        model: DistributedTrainingModels,
        gradient_compression: GradientCompression,
    ) -> Dict[str, Any]:
        trainedModelHfName: str = generate_random_name(
            prefix=f"exls-dist-train-model-{model.value}-compression-{gradient_compression.value}",
            slug_length=2,
        )
        wandbProjectName: str = generate_random_name(
            prefix=f"exls-dist-train-{model.value}", slug_length=2
        )
        wandbGroup: str = wandbProjectName
        wandbRunId: str = generate_random_name(prefix=wandbProjectName, slug_length=2)
        experimentDescription: str = (
            f"Distributed training of {model.value} on {self._model.get_dataset_for_model(model)} "
            f"using compression level {gradient_compression.value}"
        )
        experimentTags: List[str] = [
            "distributed-training",
            model.value,
            self._model.get_dataset_for_model(model),
            f"compression-{gradient_compression.value}",
        ]

        return {
            "huggingfaceToken": self._hf_token,
            "wandbUserKey": self._wandb_token,
            "hfUpload": True,
            "trainedModelHfName": trainedModelHfName,
            "wandbProjectName": wandbProjectName,
            "wandbGroup": wandbGroup,
            "wandbRunId": wandbRunId,
            "experimentDescription": experimentDescription,
            "experimentTags": f"[{', '.join(f'"{tag}"' for tag in experimentTags)}]",
        }

    def configure_and_validate(
        self, variables: Dict[str, Any], io_facade: IOBaseModelFacade
    ) -> Dict[str, Any]:
        if "diloco" not in variables:
            raise InvalidWorkspaceConfiguration(
                "Unexpected error: Variable 'diloco' is not set in the workspace template."
            )
        self._verify_resources()
        gradient_compression_variables: Dict[str, str] = (
            self._translate_compression_config_for_gradient_compression(
                self._gradient_compression
            )
        )
        training_config: Dict[str, str] = self._get_training_config_for_model(
            self._model, self._gradient_compression
        )
        model_variables: Dict[str, str] = self._get_model_variables(self._model)
        metadata_variables: Dict[str, str] = self._get_metadata_variable_defaults(
            self._model, self._gradient_compression
        )
        variables["diloco"] = deep_merge(
            variables["diloco"],
            gradient_compression_variables,
            training_config,
            model_variables,
            metadata_variables,
        )
        variables["diloco"]["pgroupBackend"] = self._get_prgroup_backend()

        if "elastic" not in variables:
            raise InvalidWorkspaceConfiguration(
                "Unexpected error: Variable 'elastic' is not set in the workspace template."
            )
        variables["elastic"] = deep_merge(
            variables["elastic"], self._get_torch_elastic_config()
        )

        if "gpu" not in variables:
            raise InvalidWorkspaceConfiguration(
                "Unexpected error: Variable 'gpu' is not set in the workspace template."
            )
        variables["gpu"] = deep_merge(
            variables["gpu"],
            self._get_gpu_variables(),
        )

        return super().configure_and_validate(variables, io_facade)
