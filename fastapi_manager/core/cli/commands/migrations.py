from pathlib import Path

from aerich import Command
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
        self.aerich: list[Command] | Command = []
        self.migration_folder = Path(settings.BASE_DIR).joinpath("migrations")
        self.config = create_db_config(settings)

        # get apps
        self.get_aerich_command()

        self.execute()

    def get_aerich_command(self):
        migration_folder = str(self.migration_folder)
        if self.app_name is not None:
            self.aerich = Command(self.config, self.app_name, migration_folder)
        else:
            aerich_list = []
            for config in apps.get_app_configs():
                aerich_list.append(Command(self.config, config.label, migration_folder))
            self.aerich = aerich_list

    async def async_action(self):
        if isinstance(self.aerich, list):
            for command in self.aerich:
                await self.migration_task(command)
        else:
            await self.migration_task(self.aerich)

    async def migration_task(self, command):
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

    # def is_init(self, app_name):
    #     try:
    #         PathChecker(str(MIGRATIONS_FOLDER.joinpath(app_name))).is_not_exists()
    #         return True
    #     except Exception:
    #         return False

    async def migration_task(self, command):
        await command.init()
        await command.init_db(True)
        await command.migrate(self.message)


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
