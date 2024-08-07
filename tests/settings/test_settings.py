import pytest

from fastapi_manager.conf import settings, Settings, ENVIRONMENT_VARIABLE
import os

from fastapi_manager.utils.lazy import LazyObject


@pytest.fixture
def custom_settings():
    return LazyObject(lambda: Settings("tests.settings.local_conf"))


def test_settings_lazy_init(custom_settings):
    assert custom_settings._wrapped is None
    assert custom_settings._is_init is False


def test_settings_load(custom_settings):
    assert settings.DEBUG is True
    assert settings.INSTALLED_APPS == []


def test_custom_settings_loading(custom_settings):
    custom_settings._load_global_settings()
    assert custom_settings.DEBUG is False
    custom_settings._load_local_settings()
    assert custom_settings.DEBUG == True


def test_settings_validation():
    with pytest.raises(Exception):
        Settings._validate_special_settings("INSTALLED_APPS", "TEST")
    assert Settings._validate_special_settings("ALLOWED_HOSTS", ["TEST"]) is None
