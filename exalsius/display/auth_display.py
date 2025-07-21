from rich.console import Console

from exalsius.display.base import BaseDisplayManager


class AuthDisplayManager(BaseDisplayManager):
    def __init__(self, console: Console):
        super().__init__(console)
