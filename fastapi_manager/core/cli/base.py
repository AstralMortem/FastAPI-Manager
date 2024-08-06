import os
import typer
from fastapi_manager.templates import NewAppHandler, NewProjectHandler
from fastapi_manager.conf import settings
from alembic.command import revision, upgrade, downgrade
from alembic.config import Config

# from fastapi_manager.db import migration_schema


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
        config_path = self._get_migrations_path() / "alembic.ini"
        return Config(config_path, ini_section=self.app_name)

    def _get_migrations_path(self):
        return settings.MODULES_DIR.joinpath(self.app_name).joinpath("migrations")

    def _get_version_path(self):
        return self._get_migrations_path().joinpath("versions")


class MakeMigrations(AlembicCommand):
    def __init__(self, app_name, message=None):
        super().__init__(app_name)
        self.message = message
        # migration_schema()

    def _action(self):

        revision(
            self.config,
            self.message,
            head=self.get_head(),
            autogenerate=True,
            branch_label=self.get_branch(),
            version_path=self.get_version_path(),
        )

    def is_first_migration(self):
        res = len(os.listdir(str(self._get_version_path()))) == 0
        return res

    def get_head(self):
        if self.is_first_migration():
            return "base"
        return f"{self.app_name}@head"

    def get_branch(self):
        if self.is_first_migration():
            return self.app_name
        return None

    def get_version_path(self):
        if self.is_first_migration():
            return str(self._get_version_path())
        return None


class Migrate(AlembicCommand):
    def _action(self):
        upgrade(self.config, f"{self.app_name}@head")


class Downgrade(AlembicCommand):
    def _action(self):
        downgrade(self.config, f"{self.app_name}@head-1")
