import pytest
from fastapi_manager.conf import LazySettings
from . import local_settings


@pytest.fixture(scope="session", autouse=True)
def settings():
    settings = LazySettings()
    settings.configure(local_settings)
    return settings
