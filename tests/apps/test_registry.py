import importlib
from unittest.mock import patch, MagicMock

import pytest
from fastapi_manager.apps.registry import Apps
from fastapi_manager.apps.config import AppConfig
from fastapi_manager.core.exceptions import AppRegistryNotReady

from tests.apps.test_app.apps import TestAppConfig


@pytest.fixture(autouse=True)
def reset_singleton():
    """
    Fixture that resets the singleton instance before each test.
    """
    Apps._instance = None  # Reset the singleton instance to None
    yield
    Apps._instance = None  # Clean up after the test


def test_apps_singleton():
    apps1 = Apps()
    apps2 = Apps()

    assert apps1 is apps2  # Ensure that Apps is a singleton


def test_apps_initialization():
    installed_apps = ["test_app"]

    apps = Apps(installed_apps=installed_apps)
    assert len(apps.app_configs) == 1

    config = apps.get_app_config("test_app")
    assert config.name == "test_app"
    assert config.label == "test_app"
    assert config.apps == apps


def test_apps_populate():
    installed_apps = ["test_app"]

    with patch("fastapi_manager.apps.config.AppConfig.create") as mock_create:
        mock_app_config = MagicMock(spec=AppConfig, label="test_app")
        mock_create.return_value = mock_app_config

        apps = Apps(installed_apps=installed_apps)
        mock_app_config.import_models.assert_called_once()
        mock_app_config.on_ready.assert_called_once()

        assert apps.apps_ready is True
        assert apps.models_ready is True
        assert apps.ready is True


def test_get_app_configs():
    apps = Apps(installed_apps=["test_app"])

    configs = list(apps.get_app_configs())

    assert len(configs) == 1
    assert configs[0].label == "test_app"


def test_app_registry_not_ready():
    apps = Apps(installed_apps=None)

    with pytest.raises(AppRegistryNotReady):
        apps.get_app_configs()

    with pytest.raises(AppRegistryNotReady):
        apps.get_app_config("test_app")


def test_duplicate_app_label():
    installed_apps = ["test_app", "test_app"]

    with pytest.raises(RuntimeError, match="Duplicate app label:"):
        apps = Apps(installed_apps=installed_apps)


def test_real_app():
    installed_apps = ["test_app"]
    apps = Apps()

    apps.populate(installed_apps)
    app_config = apps.get_app_config("test_app")
    assert app_config.name == "test_app"
    assert app_config.label == "test_app"
    assert app_config.module == importlib.import_module("test_app")
    assert app_config.models_module == importlib.import_module("test_app.models")
