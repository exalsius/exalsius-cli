from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, StrictStr

from exls.shared.adapters.ui.facade.interface import IOFacade
from exls.shared.adapters.ui.flow.flow import FlowContext, FlowStep, SequentialFlow
from exls.shared.adapters.ui.flow.steps import (
    ChoicesSpec,
    ConditionalStep,
    PathInputStep,
    SelectRequiredStep,
    TextInputStep,
)
from exls.shared.adapters.ui.input.values import DisplayChoice


class PublicKeySpecDTO(BaseModel):
    create_new: bool = Field(default=False, description="Whether to create a new key")
    path: Path = Field(
        default=Path.home() / ".ssh", description="Path to the key file or directory"
    )
    key_name: Optional[StrictStr] = Field(
        default=None, description="Name of the key file"
    )


class PublicKeyFlow(FlowStep[PublicKeySpecDTO]):
    def _get_action_choices(
        self, model: PublicKeySpecDTO, context: FlowContext
    ) -> ChoicesSpec[bool]:
        return ChoicesSpec[bool](
            choices=[
                DisplayChoice[bool](title="Load from file", value=False),
                DisplayChoice[bool](title="Generate new pair", value=True),
            ],
            default=DisplayChoice[bool](title="Load from file", value=False),
        )

    def execute(
        self,
        model: PublicKeySpecDTO,
        context: FlowContext,
        io_facade: IOFacade[BaseModel],
    ) -> None:
        flow = SequentialFlow[PublicKeySpecDTO](
            steps=[
                SelectRequiredStep[PublicKeySpecDTO, bool](
                    key="create_new",
                    message="Use existing key or generate new pair?",
                    choices_spec=self._get_action_choices,
                ),
                ConditionalStep[PublicKeySpecDTO](
                    condition=lambda m: m.create_new,
                    true_step=PathInputStep[PublicKeySpecDTO](
                        key="path",
                        message="Path to the directory where the key file will be saved:",
                        default=Path.home() / ".ssh",
                    ),
                    false_step=PathInputStep[PublicKeySpecDTO](
                        key="path",
                        message="Path to the public key file:",
                        default=Path.home() / ".ssh" / "id_rsa.pub",
                    ),
                ),
                ConditionalStep[PublicKeySpecDTO](
                    condition=lambda m: m.create_new,
                    true_step=TextInputStep[PublicKeySpecDTO](
                        key="key_name",
                        message="Name of the key file:",
                        default="exls_key",
                    ),
                ),
            ]
        )
        flow.execute(model, context, io_facade)
