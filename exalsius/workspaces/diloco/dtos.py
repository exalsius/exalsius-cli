from pathlib import Path
from typing import Optional

from pydantic import Field, PositiveInt, StrictStr

from exalsius.workspaces.dtos import DeployWorkspaceRequestDTO


class DeployDilocoWorkspaceRequestDTO(DeployWorkspaceRequestDTO):
    nodes: PositiveInt = Field(
        ..., description="The number of nodes that are used for training"
    )
    diloco_config_file: Path = Field(
        ..., description="The path to the DiLoCo config file"
    )
    wandb_user_key: Optional[StrictStr] = Field(
        None, description="The user key of the WandB project"
    )
    wandb_project_name: Optional[StrictStr] = Field(
        None, description="The name of the WandB project"
    )
    wandb_group: Optional[StrictStr] = Field(
        None, description="The group of the WandB project"
    )
    huggingface_token: Optional[StrictStr] = Field(
        None, description="The HuggingFace token to use"
    )
