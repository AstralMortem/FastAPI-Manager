import os
from pathlib import Path
import typer
from .base import StartNewApp, StartNewProject, MakeMigrations, Downgrade, Migrate

cli = typer.Typer()


@cli.command()
def startproject(name: str, path: Path = None):
    StartNewProject(name, path).execute()


@cli.command()
def startapp(name: str, settings: str = None):
    if settings:
        os.environ.setdefault("SETTINGS_MODULE", settings)
    StartNewApp(name).execute()


@cli.command()
def makemigrations(app_name, m: str = None):
    MakeMigrations(app_name, m).execute()


@cli.command()
def migrate(app_name):
    Migrate(app_name).execute()


@cli.command()
def downgrade(app_name):
    Downgrade(app_name).execute()


__all__ = ["cli"]
