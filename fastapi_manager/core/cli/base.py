import typer
from fastapi_manager.templates import NewAppHandler, NewProjectHandler
from fastapi_manager.conf import settings


class BaseCommand:
    name: str
    description: str

    # override this function
    def _action(self):
        raise NotImplementedError

    def execute(self):
        self._action()


class StartNewProject(BaseCommand):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def _action(self):
        NewProjectHandler(self.name, self.path).copy_template()


class StartNewApp(BaseCommand):
    def __init__(self, name):
        self.name = name
        self.path = settings.MODULES_DIR

    def _action(self):
        NewAppHandler(self.name, self.path).copy_template()
