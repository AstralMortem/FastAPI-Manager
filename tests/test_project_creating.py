from pathlib import Path
from fastapi_manager.core.managment.handlers import CreateProject
import fastapi_manager
import pytest
import shutil
import os

PROJECT_NAME = "test_project"
CURRENT_CWD = Path().cwd()


def _delete_folders(path):
    shutil.rmtree(Path(path).absolute())


def test_project_template_path():
    project = CreateProject(PROJECT_NAME, None)
    assert project._get_full_template_path() == Path(
        fastapi_manager.__file__
    ).parent.joinpath("conf").joinpath("templates").joinpath(project.template_prefix)


def test_project_creation_without_path():
    project = CreateProject(PROJECT_NAME, None)
    assert project._get_destination() == CURRENT_CWD.joinpath(PROJECT_NAME)

    project.execute()

    assert CURRENT_CWD.joinpath(PROJECT_NAME).exists()

    # delete folders after test
    _delete_folders(project.new_template_name)


def test_project_creation_inside_path():
    project = CreateProject(PROJECT_NAME, ".")
    with pytest.raises(Exception):
        assert project._get_destination() == CURRENT_CWD.parent.absolute()

    with pytest.raises(Exception):
        project.execute()


def test_project_creation_inside_new_path():
    project = CreateProject(PROJECT_NAME, "./tests/test_project")
    assert project._get_destination() == Path("./tests/test_project").absolute()
    project.execute()
    assert Path("./tests/test_project").exists()

    _delete_folders(project._get_destination())


def test_project_structure():
    project = CreateProject(PROJECT_NAME, None)
    assert project._get_destination() == CURRENT_CWD.joinpath(PROJECT_NAME)

    project.execute()

    assert ["manage.py", PROJECT_NAME] == os.listdir(project._get_destination())

    assert ["__init__.py", "asgi.py", "routers.py", "settings.py"].sort() == os.listdir(
        project._get_destination().joinpath(PROJECT_NAME)
    ).sort()

    _delete_folders(project._get_destination())
