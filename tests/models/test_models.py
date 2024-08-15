import os

import pytest
from tortoise.contrib.test import initializer, finalizer

from fastapi_manager.apps.registry import Apps


@pytest.fixture(scope="function")
def setup_apps():
    installed_apps = ["tests.models.sample_app"]
    from fastapi_manager.apps import apps

    apps.populate(installed_apps)
    yield apps
    Apps._instance = None  # Clean up after the test


@pytest.fixture
def app_config(setup_apps):
    config = setup_apps.get_app_config("sample_app")
    return config


def test_models_population(app_config):
    from .sample_app.models import SampleModel

    assert app_config.get_model("sample_model") is SampleModel


def test_models_attrs(app_config, setup_apps):
    from .sample_app.models import SampleModel

    assert SampleModel._meta.app == app_config.label
    assert SampleModel.model_name in app_config.models.keys()
    assert SampleModel._meta.db_table == f"{app_config.label}_sample_model"
    assert SampleModel.apps == setup_apps


def test_models_fields(app_config):
    from .sample_app.models import SampleModel

    assert SampleModel._meta.pk_attr == "id"


# @pytest.mark.asyncio
# async def test_model_pydantic(app_config, initialize_tests):
#     from .sample_app.models import SampleModel
#
#     sample = await SampleModel.create()
#     print(sample)
