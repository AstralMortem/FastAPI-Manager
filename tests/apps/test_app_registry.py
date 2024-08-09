import contextlib
import importlib
import os
import sys


import pytest
from fastapi_manager.apps.registry import Apps, apps
from fastapi_manager.apps import AppConfig
from fastapi_manager.core.exceptions import ImproperlyConfigured, AppRegistryNotReady
from utils.lazy import cached_property


def override_settings(test_func):
    def wrapper():
        def override(installed_apps):
            if hasattr(sys.modules["fastapi_manager.apps.registry"], "apps"):
                delattr(sys.modules["fastapi_manager.apps.registry"], "apps")

            apps = Apps(None)
            apps.populate(installed_apps)
            return apps

        test_func(override)

    return wrapper


def test_app_registry_check_apps_ready():
    with pytest.raises(AppRegistryNotReady):
        apps.check_apps_ready()


def test_app_registry_check_models_ready():
    with pytest.raises(AppRegistryNotReady):
        apps.check_models_ready()


def test_app_registry_ready():
    assert apps.ready == False


@override_settings
def test_population_module_not_found(override):
    with pytest.raises(ModuleNotFoundError):
        override(["some_apps"])


class TestOneConfigApp:

    APP_NAME = "one_config_app"
    APP_MODULE = "tests.apps.one_config_app"
    INSTALLED_APPS = [APP_MODULE]

    @cached_property
    def apps(self):
        if hasattr(sys.modules["fastapi_manager.apps.registry"], "apps"):
            delattr(sys.modules["fastapi_manager.apps.registry"], "apps")
        apps = Apps(self.INSTALLED_APPS)
        return apps

    @cached_property
    def app_config(self):
        return self.apps.get_app_config(self.APP_NAME)

    def test_population_one_config_app(self):
        apps = self.apps
        assert apps.models_ready == True
        assert apps.apps_ready == True
        assert apps.ready == True

    def test_get_config(self):
        assert isinstance(self.app_config, AppConfig)

    def test_label(self):
        assert self.app_config.label == self.APP_NAME

    def test_name(self):
        assert self.app_config.name == self.APP_MODULE

    def test_module(self):
        assert self.app_config.module == importlib.import_module(self.APP_MODULE)

    def test_models(self):
        assert self.app_config.models == {}


def test_existed_models():
    INSTALLED_APPS = ["tests.apps.models_app"]
    apps.populate(INSTALLED_APPS)

    assert apps.all_models == {
        "models_app": {"test_model": apps.get_model("models_app", "test_model")}
    }

    model = apps.get_model("models_app", "TestModel")

    assert model.model_name == "test_model"
    assert model.__tablename__ == "test_model"
    assert model.apps == apps
    assert model.app_label == "models_app"
