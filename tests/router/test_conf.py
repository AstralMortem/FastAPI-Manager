import pytest
from fastapi import APIRouter
from fastapi_manager.router.base import BaseRouter
from fastapi_manager.router.conf import include, path
from unittest.mock import patch, MagicMock

# Sample router for testing
ENDPOINTS = BaseRouter()

# Mock app configuration
mock_app_config = MagicMock()
mock_app_config.module = "app_module"
mock_app_config.name = "app_name"


@pytest.fixture
def mock_apps():
    with patch("fastapi_manager.apps.apps.get_app_config") as mock_get_app_config:
        mock_get_app_config.return_value = mock_app_config
        yield mock_get_app_config


@pytest.fixture
def mock_importlib():
    with patch("importlib.import_module") as mock_import_module:
        yield mock_import_module


def test_include_correct_router(mock_apps, mock_importlib):
    # Mocking the importlib and module_has_submodule behavior
    with patch(
        "fastapi_manager.utils.module_loading.module_has_submodule"
    ) as mock_module_has_submodule:
        mock_module_has_submodule.return_value = True

        class MockModule:
            ENDPOINTS = ENDPOINTS

        mock_importlib.return_value = MockModule

        router = include("app_name.router")

        assert router == ENDPOINTS


def test_include_no_router(mock_apps, mock_importlib):
    with patch(
        "fastapi_manager.utils.module_loading.module_has_submodule"
    ) as mock_module_has_submodule:
        mock_module_has_submodule.return_value = False
        with pytest.raises(Exception, match="You must specify global router"):
            include("app_name.router")


def test_path_with_prefix():
    base_router = BaseRouter()
    new_router = path("/test", base_router)

    assert new_router.prefix == "/test"
    assert new_router.routes == base_router.routes


def test_path_with_empty_prefix():
    base_router = BaseRouter()
    new_router = path("", base_router)

    assert new_router.prefix == ""
    assert new_router.routes == base_router.routes


def test_path_raises_exception_for_none_router():
    with pytest.raises(
        Exception, match="You must set router to instance of BaseRouter or APIRouter"
    ):
        path("/test", None)
