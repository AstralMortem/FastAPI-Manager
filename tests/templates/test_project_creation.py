import shutil
from pathlib import Path

import pytest

from fastapi_manager.core.cli.commands.create_project import StartNewProject
from fastapi_manager.utils.filesystem import PathIsNotEmpty, PathAlreadyExists
from contextlib import nullcontext as does_not_raise


@pytest.fixture(scope="function", autouse=True)
def remove_after_tests():
    yield
    path = Path(".").joinpath("test_project").absolute()
    if path.exists():
        shutil.rmtree(path)
    # path2 = Path(".").joinpath("empty").absolute()
    # if path2.exists():
    #     shutil.rmtree(path)


def test_class_init():
    command = StartNewProject("test_project")
    assert command.get_name() == "startproject"


@pytest.mark.parametrize(
    "project_path, result, expected",
    [
        (".", Path(".").absolute(), pytest.raises(PathIsNotEmpty)),
        (None, Path(".").joinpath("test_project").absolute(), does_not_raise()),
        (
            Path(".").parent.parent.absolute(),
            Path(".").parent.parent.absolute(),
            pytest.raises(PathIsNotEmpty),
        ),
    ],
)
def test_project_destination(project_path, result, expected):
    with expected:
        command = StartNewProject("test_project", project_path)
        assert command.destination == result


def test_project_copy_folder():
    command = StartNewProject("test_project")

    assert command.destination.exists()
    dir_1 = ["test_project", "manage.py"]
    for dest in command.destination.iterdir():
        assert dest.name in dir_1

    dir_2 = ["__init__.py", "asgi.py", "routers.py", "settings.py"]
    for dest in command.destination.joinpath("test_project").iterdir():
        assert dest.name in dir_2
