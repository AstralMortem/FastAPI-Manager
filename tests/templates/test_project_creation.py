from pathlib import Path

import pytest

from fastapi_manager.core.cli.commands.create_project import (
    StartNewProject,
    DirectoryIsNotEmpty,
    DirectoryDoesNotExists,
    ProjectAlreadyExists,
)
from contextlib import nullcontext as does_not_raise


def test_class_init():
    command = StartNewProject("test_project")
    assert command.get_name() == "start_new_project"


@pytest.mark.parametrize(
    "project_path, result, expected",
    [
        (".", Path(".").absolute(), pytest.raises(DirectoryIsNotEmpty)),
        (None, Path(".").joinpath("test_project").absolute(), does_not_raise()),
        (
            Path(".").parent.parent.absolute(),
            Path(".").parent.parent.absolute(),
            pytest.raises(DirectoryIsNotEmpty),
        ),
        (
            Path(".").joinpath("empty"),
            Path(".").joinpath("empty").absolute(),
            does_not_raise(),
        ),
    ],
)
def test_project_destination(project_path, result, expected):
    command = StartNewProject("test_project", project_path)
    with expected:
        assert command.get_destination(False) == result


def test_project_copy_folder():
    command = StartNewProject("test_project")
    command.copy_folder()
