from pathlib import Path


from fastapi_manager.db.aerich import Command
from tortoise import run_async

from fastapi_manager.conf import settings
from fastapi_manager.core.cli.base import BaseCommand
from fastapi_manager.apps import apps
from fastapi_manager.utils.filesystem import PathChecker
from fastapi_manager.db.utils import create_db_config


class MigrationBaseCommand(BaseCommand):

    def __init__(self, app_name: str | None = None, settings_file: str = None):
        super().__init__(settings_file)

        # setup migraions command
        self.app_name = app_name

        self.migration_folder = Path(settings.BASE_DIR).joinpath("migrations")
        self.config = create_db_config(settings)
        default_app = list(self.config.get("apps").keys())[0]
        self.aerich = Command(
            self.config, app_name, str(self.migration_folder), default_app
        )

        self.execute()

    async def async_action(self):
        raise NotImplemented

    def _action(self):
        run_async(self.async_action())


class MakeMigrations(MigrationBaseCommand):
    command_name = "makemigrations"

    def __init__(
        self, app_name: str = None, message: str = None, setting_file: str = None
    ):
        self.message = message
        super().__init__(app_name, setting_file)

    async def async_action(self):
        await self.aerich.init()
        await self.aerich.init_db(True)
        await self.aerich.migrate(self.message)


# class Migrate(BaseCommand):
#     command_name = "migrate"
#
#     def __init__(self, app_name: str = None, setting_file: str = None):
#         super().__init__(setting_file)
#         self.aerich: list[Command] | Command = []
#         if app_name is not None:
#             self.aerich = Command(
#                 create_db_config(settings), app_name, str(MIGRATIONS_FOLDER)
#             )
#         else:
#             for config in apps.get_app_configs():
#                 self.aerich.append(
#                     Command(
#                         create_db_config(settings), config.label, str(MIGRATIONS_FOLDER)
#                     )
#                 )
#         self.execute()
#
#     async def async_action(self):
#         if isinstance(self.aerich, list):
#             for com in self.aerich:
#                 await com.init()
#                 await com.upgrade(True)
#         else:
#             await self.aerich.init()
#             await self.aerich.upgrade(True)
#
#     def _action(self):
#         run_async(self.async_action())
