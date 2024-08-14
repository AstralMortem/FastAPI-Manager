import inspect
import importlib
import typer
from .base import BaseCommand

cli = typer.Typer()


def get_commands():
    mod = importlib.import_module("fastapi_manager.core.cli.commands")
    for _, obj in inspect.getmembers(mod, inspect.isclass):
        if issubclass(obj, BaseCommand):
            yield obj


for command in get_commands():

    handler = typer.models.CommandInfo(
        name=command.command_name,
        callback=command,
    )
    cli.registered_commands.append(handler)
