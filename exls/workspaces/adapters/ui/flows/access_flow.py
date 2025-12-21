from enum import StrEnum
from typing import Optional

from pydantic import Field, StrictStr
from pydantic.main import BaseModel

from exls.shared.adapters.ui.facade.interface import IOFacade
from exls.shared.adapters.ui.flow.flow import FlowContext, FlowStep, SequentialFlow
from exls.shared.adapters.ui.flow.steps import (
    ActionStep,
    ChoicesSpec,
    ConditionalStep,
    SelectRequiredStep,
    TextInputStep,
)
from exls.shared.adapters.ui.flows.keys import PublicKeyFlow, PublicKeySpecDTO
from exls.shared.adapters.ui.input.values import DisplayChoice
from exls.shared.core.crypto import CryptoService


class AccessChoices(StrEnum):
    PASSWORD = "password"
    PUBLIC_KEY = "public_key"


class AccessDTO(BaseModel):
    access_choice: AccessChoices = Field(
        default=AccessChoices.PASSWORD, description="The access choice"
    )
    ssh_password: Optional[StrictStr] = Field(
        default=None,
        description="The SSH password, optional if ssh_public_key is provided",
    )
    ssh_public_key: Optional[StrictStr] = Field(
        default=None,
        description="The SSH public key, optional if ssh_password is provided",
    )


# TODO: This seems like a common flow, we should probably move it to the shared package


class ConfigureWorkspaceAccessFlow(FlowStep[AccessDTO]):
    def __init__(self, service: CryptoService):
        self._service: CryptoService = service

    def _get_access_choices(
        self, model: AccessDTO, context: FlowContext
    ) -> ChoicesSpec[AccessChoices]:
        return ChoicesSpec[AccessChoices](
            choices=[
                DisplayChoice[AccessChoices](
                    title="Password", value=AccessChoices.PASSWORD
                ),
                DisplayChoice[AccessChoices](
                    title="Public Key", value=AccessChoices.PUBLIC_KEY
                ),
            ],
            default=DisplayChoice[AccessChoices](
                title="Password", value=AccessChoices.PASSWORD
            ),
        )

    def _generate_public_key(
        self,
        model: AccessDTO,
        context: FlowContext,
        io_facade: IOFacade[BaseModel],
    ):
        key_spec = PublicKeySpecDTO()
        flow: PublicKeyFlow = PublicKeyFlow()
        flow.execute(key_spec, context, io_facade)
        public_key: str = self._service.resolve_public_key(key_spec)
        model.ssh_public_key = public_key

    def execute(
        self,
        model: AccessDTO,
        context: FlowContext,
        io_facade: IOFacade[BaseModel],
    ):
        flow = SequentialFlow[AccessDTO](
            steps=[
                SelectRequiredStep[AccessDTO, AccessChoices](
                    key="access_choice",
                    message="How do you want to access the workspace?",
                    choices_spec=self._get_access_choices,
                ),
                ConditionalStep[AccessDTO](
                    condition=lambda m: m.access_choice == AccessChoices.PASSWORD,
                    true_step=TextInputStep[AccessDTO](
                        key="ssh_password",
                        message="Enter the SSH password",
                    ),
                ),
                ConditionalStep[AccessDTO](
                    condition=lambda m: m.access_choice == AccessChoices.PUBLIC_KEY,
                    true_step=ActionStep[AccessDTO](
                        action=lambda m, c, f: self._generate_public_key(m, c, f),
                    ),
                ),
            ]
        )
        flow.execute(model, context, io_facade)
