from pathlib import Path

import pytest
from unittest.mock import patch, MagicMock
from fastapi_manager.apps.config import AppConfig
from fastapi_manager.core.exceptions import ImproperlyConfigured


def test_app_config_initialization():
    app_name = "test_app"
    app_module = MagicMock(__name__=app_name, __path__=["/path/to/test_app"])

    config = AppConfig(app_name, app_module)

    assert config.name == app_name
    assert config.label == "test_app"
    assert config.module == app_module
    assert config.apps is None


def test_app_config_invalid_label():
    app_name = "test_app.invalid-label"
    app_module = MagicMock(__name__=app_name, __path__=["/path/to/test_app"])

    with pytest.raises(ImproperlyConfigured):
        AppConfig(app_name, app_module)


def test_app_config_path_resolution():
    app_name = "test_app"
    app_module = MagicMock(__name__=app_name, __path__=["/path/to/test_app"])

    config = AppConfig(app_name, app_module)

    assert config.path == "/path/to/test_app"


def test_app_config_import_models():
    app_name = "test_app"
    app_module = MagicMock(
        __name__=app_name, __path__=[str(Path("test_app").absolute())]
    )

    config = AppConfig(app_name, app_module)
    config.apps = MagicMock(all_models={config.label: {}})

    with patch("fastapi_manager.apps.config.import_module") as mock_import_module:
        config.import_models()

        mock_import_module.assert_called_once_with(f"{app_name}.models")
        assert config.models == config.apps.all_models[config.label]


def test_app_config_create():
    entry = "test_app"

    with patch("fastapi_manager.apps.config.import_module") as mock_import_module:
        mock_module = MagicMock(__name__=entry, __path__=["/path/to/test_app"])
        mock_import_module.return_value = mock_module

        app_config = AppConfig.create(entry)

        assert app_config.name == entry
        assert app_config.module == mock_module
