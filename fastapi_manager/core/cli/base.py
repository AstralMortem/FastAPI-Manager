import typer
from fastapi_manager.templates import NewAppHandler, NewProjectHandler
from fastapi_manager.conf import settings
from alembic.command import revision, upgrade, downgrade
from alembic.config import Config


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


class AlembicCommand(BaseCommand):
    def __init__(self, app_name, *args, **kwargs):
        self.app_name = app_name
        self.config = self.__get_config()

    def __get_config(self):
        config_path = (
            settings.MODULES_DIR.joinpath(self.app_name).joinpath("migrations")
            / "alembic.ini"
        )
        return Config(config_path, ini_section=self.app_name)


class MakeMigrations(AlembicCommand):
    def __init__(self, app_name, message=None):
        super().__init__(app_name)
        self.message = message

    def _action(self):
        revision(self.config, self.message, f"{self.app_name}@head", autogenerate=True)


class Migrate(AlembicCommand):
    def _action(self):
        upgrade(self.config, f"{self.app_name}@head")


class Downgrade(AlembicCommand):
    def _action(self):
        downgrade(self.config, f"{self.app_name}@head-1")
