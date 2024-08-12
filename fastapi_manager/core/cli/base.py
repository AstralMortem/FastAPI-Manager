import os

from fastapi_manager.utils.string import convert_to_snake_case


#
class BaseCommand:
    command_name: str = "command"
    command_description: str = None

    def __new__(cls, *args, **kwargs):
        new_class = super().__new__(cls)
        if cls.command_name is None:
            new_class.command_name = convert_to_snake_case(cls.__name__)
        return new_class

    def __init__(self, settings: str | None = None):
        if settings:
            os.environ.setdefault("SETTINGS_MODULE", settings)

    def get_name(self):
        return self.command_name

    def get_description(self):
        return self.command_description

    def _action(self):
        """Override this function with command"""
        raise NotImplementedError

    def execute(self):
        self._action()
