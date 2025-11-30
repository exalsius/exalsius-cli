from __future__ import annotations

from abc import ABC
from enum import StrEnum
from typing import Any, Dict, List, Protocol, runtime_checkable

from typing_extensions import Optional

from exls.shared.adapters.ui.input.interfaces import EditDictionaryError
from exls.shared.adapters.ui.input.values import UserCancellationException
from exls.shared.adapters.ui.shared.render.render import YamlRenderContext
from exls.shared.core.domain import ExalsiusError, generate_random_name
from exls.workspaces.adapters.bundle import WorkspacesBundle
from exls.workspaces.adapters.ui.display.display import IOWorkspacesFacade
from exls.workspaces.adapters.ui.dtos import IntegratedWorkspaceTemplates


class InvalidWorkspaceConfiguration(ExalsiusError):
    """Exception raised when the workspace configuration is invalid."""

    pass


@runtime_checkable
class WorkspaceConfigurator(Protocol):
    @property
    def template_id(self) -> str:
        """The ID of the template this configurator supports."""
        ...

    def configure(self, io_facade: IOWorkspacesFacade) -> Dict[str, Any]:
        """
        Full workflow: collect inputs -> optional advanced edit -> validate.
        Returns the final valid dictionary of variables.
        """
        ...


class BaseWorkspaceConfigurator(ABC):
    """
    Shared logic for editing and validation.
    """

    def __init__(self, bundle: WorkspacesBundle):
        self._bundle = bundle

    @property
    def template_id(self) -> IntegratedWorkspaceTemplates:
        raise NotImplementedError

    def _validate(
        self, ref_variables: Dict[str, Any], edited_variables: Dict[str, Any]
    ) -> None:
        # Validate that all required variables defined in the reference
        # are defined in the edited variables.
        for key in ref_variables.keys():
            if key not in edited_variables:
                raise InvalidWorkspaceConfiguration(
                    f"Workspace template configuration requires variable '{key}' to be set."
                )

    def _configure(
        self, variables: Dict[str, Any], io_facade: IOWorkspacesFacade
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
        self, variables: Dict[str, Any], io_facade: IOWorkspacesFacade
    ) -> Dict[str, Any]:
        edited_variables: Dict[str, Any] = self._configure(variables.copy(), io_facade)
        # Final Validation
        self._validate(variables, edited_variables)
        return edited_variables

    def _run_editor_loop(
        self, variables: Dict[str, Any], io_facade: IOWorkspacesFacade
    ) -> Dict[str, Any]:
        editor_render_context: YamlRenderContext = (
            self._bundle.get_editor_render_context(integrated_template=self.template_id)
        )
        current_variables = variables.copy()
        while True:
            try:
                edited_variables: Dict[str, Any] = io_facade.edit_dictionary(
                    dictionary=current_variables,
                    renderer=self._bundle.get_editor_renderer(),
                    render_context=editor_render_context,
                )
                return edited_variables
            except UserCancellationException:
                io_facade.display_info_message(
                    "User cancelled the workspace template editing. No changes were made.",
                    self._bundle.message_output_format,
                )
                return current_variables
            except (EditDictionaryError, Exception) as e:
                io_facade.display_error_message(
                    f"An unexpected error occurred while editing the workspace template: {e}",
                    self._bundle.message_output_format,
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
    def __init__(self, bundle: WorkspacesBundle, password: str):
        super().__init__(bundle)
        self._password: str = password

    @property
    def template_id(self) -> IntegratedWorkspaceTemplates:
        return IntegratedWorkspaceTemplates.JUPYTER

    def _validate(
        self, ref_variables: Dict[str, Any], edited_variables: Dict[str, Any]
    ) -> None:
        super()._validate(ref_variables, edited_variables)
        if edited_variables.get("notebookPassword", "") == "":
            raise InvalidWorkspaceConfiguration(
                "Jupyter workspace requires 'notebookPassword' to be set."
            )

    def configure_and_validate(
        self, variables: Dict[str, Any], io_facade: IOWorkspacesFacade
    ) -> Dict[str, Any]:
        variables["notebookPassword"] = self._password
        return super().configure_and_validate(variables, io_facade)


class MarimoConfigurator(BaseWorkspaceConfigurator):
    def __init__(self, bundle: WorkspacesBundle, password: str):
        super().__init__(bundle)
        self._password: str = password

    @property
    def template_id(self) -> IntegratedWorkspaceTemplates:
        return IntegratedWorkspaceTemplates.MARIMO

    def _validate(
        self, ref_variables: Dict[str, Any], edited_variables: Dict[str, Any]
    ) -> None:
        super()._validate(ref_variables, edited_variables)
        if edited_variables.get("tokenPassword", "") == "":
            raise InvalidWorkspaceConfiguration(
                "Marimo workspace requires 'tokenPassword' to be set."
            )

    def configure_and_validate(
        self, variables: Dict[str, Any], io_facade: IOWorkspacesFacade
    ) -> Dict[str, Any]:
        variables["tokenPassword"] = self._password
        return super().configure_and_validate(variables, io_facade)


class VSCodeDevPodConfigurator(BaseWorkspaceConfigurator):
    def __init__(
        self,
        bundle: WorkspacesBundle,
        ssh_password: Optional[str],
        ssh_public_key: Optional[str],
    ):
        super().__init__(bundle)
        self._ssh_password: Optional[str] = None
        self._ssh_public_key: Optional[str] = None

    @property
    def template_id(self) -> IntegratedWorkspaceTemplates:
        return IntegratedWorkspaceTemplates.VSCODE_DEV_POD

    def _validate(
        self, ref_variables: Dict[str, Any], edited_variables: Dict[str, Any]
    ) -> None:
        super()._validate(ref_variables, edited_variables)
        ssh_password: str = edited_variables.get("sshPassword", "")
        ssh_public_key: str = edited_variables.get("sshPublicKey", "")
        if ssh_password == "" and ssh_public_key == "":
            raise InvalidWorkspaceConfiguration(
                "VSCode Dev Pod workspace requires at least one of 'sshPassword' or 'sshPublicKey' to be set and non-empty."
            )

    def configure_and_validate(
        self, variables: Dict[str, Any], io_facade: IOWorkspacesFacade
    ) -> Dict[str, Any]:
        edited_variables: Dict[str, Any] = self._configure(variables.copy(), io_facade)
        # This is allows users to delete one of the two access methods during the configuration
        # and still pass the validation.
        if "sshPassword" not in edited_variables:
            edited_variables["sshPassword"] = ""
        if "sshPublicKey" not in edited_variables:
            edited_variables["sshPublicKey"] = ""
        self._validate(variables, edited_variables)
        return edited_variables


class DistributedTrainingModels(StrEnum):
    RESNET50 = "resnet50"
    RESNET101 = "resnet101"
    WAV2VEC2 = "wav2vec2"
    GPT_NEO = "gpt-neo"
    GPT_NEO_X = "gpt-neo-x"
    GPT_NEO_TINY = "gpt-neo-tiny"
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
        elif model == cls.GPT_NEO_TINY:
            return "c4_prime"
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
        bundle: WorkspacesBundle,
        model: DistributedTrainingModels,
        gradient_compression: GradientCompression,
        wandb_token: str,
        hf_token: str,
    ):
        super().__init__(bundle)
        self._model: DistributedTrainingModels = model
        self._gradient_compression: GradientCompression = gradient_compression
        self._wandb_token: str = wandb_token
        self._hf_token: str = hf_token

    @property
    def template_id(self) -> IntegratedWorkspaceTemplates:
        return IntegratedWorkspaceTemplates.DIST_TRAINING

    def _translate_compression_config_for_gradient_compression(
        self, gradient_compression: GradientCompression
    ) -> Dict[str, Any]:
        if gradient_compression == GradientCompression.NO_COMPRESSION:
            return {
                "localSteps": 1,
                "optimMethod": "ddp",
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
            DistributedTrainingModels.GPT_NEO_TINY,
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
        self, variables: Dict[str, Any], io_facade: IOWorkspacesFacade
    ) -> Dict[str, Any]:
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

        if "diloco" not in variables:
            raise InvalidWorkspaceConfiguration(
                "Unexpected error: Variable 'diloco' is not set in the workspace template."
            )

        diloco_variables: Dict[str, str] = {
            **variables["diloco"],
            **gradient_compression_variables,
            **training_config,
            **model_variables,
            **metadata_variables,
        }

        variables["diloco"] = diloco_variables
        return super().configure_and_validate(variables, io_facade)
