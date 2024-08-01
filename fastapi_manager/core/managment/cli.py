import typer
from pathlib import Path
from .handlers import CreateProject, StartApp
from fastapi_cli.cli import app as fastapi_cli

cli_app = typer.Typer(rich_markup_mode="rich")
cli_app.add_typer(fastapi_cli, name="server")


@cli_app.command()
def startproject(name: str, path: Path = None):
    new_project = CreateProject(name, path)
    new_project.execute()


@cli_app.command()
def startapp(name):
    new_app = StartApp(name)
    new_app.execute()


if __name__ == "__main__":
    cli_app()
