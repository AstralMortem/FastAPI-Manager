from aerich import Command
from tortoise import run_async

from fastapi_manager.conf import settings
from fastapi_manager.db.connection import TORTOISE_ORM
from fastapi_manager.core.cli.base import BaseCommand
from fastapi_manager.apps import apps
from fastapi_manager.utils.filesystem import PathChecker


class MakeMigrations(BaseCommand):
    command_name = "makemigrations"

    def __init__(self, app_name: str = None, message: str = None):
        self.aerich: list[Command] | Command = []
        self.message = message
        if app_name is not None:
            self.aerich = Command(
                TORTOISE_ORM, app_name, settings.BASE_DIR.joinpath("migrations")
            )
        else:
            for config in apps.get_app_configs():
                self.aerich.append(
                    Command(
                        TORTOISE_ORM,
                        config.label,
                        settings.BASE_DIR.joinpath("migrations"),
                    )
                )

        self.execute()

    def is_init(self, app_name):
        try:
            PathChecker(
                settings.BASE_DIR.joinpath("migrations").joinpath(app_name)
            ).is_not_exists()
            return True
        except Exception:
            return False

    async def async_action(self):
        if isinstance(self.aerich, list):
            for com in self.aerich:
                await com.init()
                if self.is_init(com.app):
                    await com.init_db(True)
                else:
                    await com.migrate(self.message)
        else:
            await self.aerich.init()
            if self.is_init(self.aerich.app):
                await self.aerich.init_db(True)
            else:
                await self.aerich.migrate(self.message)

    def _action(self):
        run_async(self.async_action())


class Migrate(BaseCommand):
    command_name = "migrate"

    def __init__(self, app_name: str = None):
        self.aerich: list[Command] | Command = []
        if app_name is not None:
            self.aerich = Command(
                TORTOISE_ORM, app_name, settings.BASE_DIR.joinpath("migrations")
            )
        else:
            for config in apps.get_app_configs():
                self.aerich.append(
                    Command(
                        TORTOISE_ORM,
                        config.label,
                        settings.BASE_DIR.joinpath("migrations"),
                    )
                )
        self.execute()

    async def async_action(self):
        if isinstance(self.aerich, list):
            for com in self.aerich:
                await com.init()
                await com.upgrade(True)
        else:
            await self.aerich.init()
            await self.aerich.upgrade(True)

    def _action(self):
        run_async(self.async_action())
