import os
from pathlib import Path
import typer
from .base import BaseCommand, StartNewApp, StartNewProject

cli = typer.Typer()


@cli.command()
def startproject(name: str, path: Path = None):
    StartNewProject(name, path).execute()


@cli.command()
def startapp(name: str, settings: str = None):
    if settings:
        os.environ.setdefault("SETTINGS_MODULE", settings)
    StartNewApp(name).execute()


__all__ = ["cli"]
