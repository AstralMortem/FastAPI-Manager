import os
from pathlib import Path
import subprocess

import pytest
import fastapi_manager
from fastapi_manager.core.managment.handlers import CreateProject, StartApp
from fastapi_manager.conf import settings

APP_NAME = "test_app"
PROJECT_NAME = "test_projects"

TEMPLATE_PATH = (
    Path(fastapi_manager.__file__)
    .parent.joinpath("conf")
    .joinpath("templates")
    .absolute()
)


def test_app_creation():
    project = CreateProject(PROJECT_NAME, None)
    project.execute()

    assert project._get_destination() == Path(".").joinpath(PROJECT_NAME).absolute()

    settings.configure()
    settings.BASE_DIR = Path(".").joinpath(PROJECT_NAME).absolute()

    app = StartApp(APP_NAME)

    assert (
        app._get_destination()
        == Path(".").joinpath(PROJECT_NAME).joinpath(APP_NAME).absolute()
    )

    assert app._get_full_template_path() == TEMPLATE_PATH.joinpath("[app_name]")

    app.execute()

    assert app._get_destination().exists() == True
