from typing import Optional, Tuple

from exalsius.cli import config
from exalsius.core.models.login import LoginRequest
from exalsius.core.operations.base import BaseOperation


class LoginOperation(BaseOperation[bool]):
    def __init__(self, login_request: LoginRequest):
        self.login_request = login_request

    def execute(self) -> Tuple[bool, Optional[str]]:
        cfg = config.load()
        cfg.credentials = config.Credentials(
            username=self.login_request.username, password=self.login_request.password
        )
        config.save(cfg)
        return True, None
