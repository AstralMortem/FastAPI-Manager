from pathlib import Path

import pytest

import os
import pprint
from dynaconf import inspect_settings


@pytest.fixture(scope="session", autouse=True)
def settings():
    os.environ.setdefault("FASTAPI_SETTINGS", "./local_settings.toml")
    from fastapi_manager.conf import settings as conf

    os.environ.setdefault(
        "FASTAPI_PROJECT_DIR", str(Path("local_settings.toml").parent.absolute())
    )
    return conf
