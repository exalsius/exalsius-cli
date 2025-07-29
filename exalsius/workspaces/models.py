from enum import Enum


class WorkspaceType(str, Enum):
    POD = "pod"
    JUPYTER = "jupyter"
    LLM_INFERENCE = "llm_inference"
