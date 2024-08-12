from fastapi_manager.core.cli.typer import get_commands


def test_get_commands():
    command_class = list(get_commands())[0]
    assert command_class.__name__ == "StartNewProject"
    assert command_class.command_name == "startproject"
