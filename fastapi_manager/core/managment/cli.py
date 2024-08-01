import typer
from pathlib import Path
from .handlers import CreateProject

cli_app = typer.Typer()


@cli_app.command()
def startproject(name: str, path: Path = None):
    new_project = CreateProject(name, path)
    new_project.execute()


@cli_app.command()
def startapp(name):
    print("Hello world")


if __name__ == "__main__":
    cli_app()
