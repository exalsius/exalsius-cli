from typing import Optional

from exalsius_api_client.api.management_api import ManagementApi

from exls.core.commons.commands.sdk import ExalsiusSdkCommand


class BaseManagementSdkCommand[T_Cmd_Params, T_Cmd_Return](
    ExalsiusSdkCommand[ManagementApi, T_Cmd_Params, T_Cmd_Return]
):
    """Base class for all management commands."""

    def _execute_api_call(self, params: Optional[T_Cmd_Params]) -> T_Cmd_Return:
        raise NotImplementedError
