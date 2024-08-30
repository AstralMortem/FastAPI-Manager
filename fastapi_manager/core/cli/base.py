import os

from fastapi_manager.utils.string import convert_to_snake_case
import fastapi_manager


#
class BaseCommand:
    command_name: str = "command"
    command_description: str = None

    def __new__(cls, *args, **kwargs):
        new_class = super().__new__(cls)
        if cls.command_name is None:
            new_class.command_name = convert_to_snake_case(cls.__name__)
        fastapi_manager.setup()
        return new_class

    def __init__(self, settings: str | None = None):
        if settings:
            os.environ.setdefault("FASTAPI_SETTINGS", settings)

    def get_name(self):
        return self.command_name

    def get_description(self):
        return self.command_description

    def _action(self):
        """Override this function with command"""
        raise NotImplementedError

    def execute(self):
        # populate apps and other settings before execute command
        # if settings.configured:

        self._action()
