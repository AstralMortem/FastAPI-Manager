import pytest

from fastapi_manager.conf import settings, Settings, ENVIRONMENT_VARIABLE
import os

from fastapi_manager.utils.lazy import LazyObject


@pytest.fixture(scope="module", autouse=True)
def load_environ():
    os.environ.setdefault(ENVIRONMENT_VARIABLE, "tests.settings.local_conf")


def test_settings_lazy_init():
    assert settings._wrapped is None
    assert settings._is_init is False


def test_settings_load():
    assert settings.DEBUG is "TEST"
    assert settings.INSTALLED_APPS == []


@pytest.fixture
def custom_settings():
    return LazyObject(lambda: Settings("tests.settings.local_conf"))


def test_custom_settings_loading(custom_settings):
    custom_settings._load_global_settings()
    assert custom_settings.DEBUG is False
    custom_settings._load_local_settings()
    assert custom_settings.DEBUG == "TEST"


def test_settings_validation():
    with pytest.raises(Exception):
        Settings._validate_special_settings("INSTALLED_APPS", "TEST")
    assert Settings._validate_special_settings("ALLOWED_HOSTS", ["TEST"]) is None
