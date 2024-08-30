from pathlib import Path

import pytest

import os
import pprint
from dynaconf import inspect_settings

TEST_DIR = Path(__file__).parent.absolute()


@pytest.fixture(scope="function", autouse=True)
def settings():
    os.environ.setdefault(
        "FASTAPI_SETTINGS", str(TEST_DIR.joinpath("local_settings.toml"))
    )

    from fastapi_manager.conf import settings as conf

    os.environ.setdefault("FASTAPI_PROJECT_DIR", str(TEST_DIR))
    os.environ.setdefault(
        "FASTAPI_SETTINGS", str(TEST_DIR.joinpath("local_settings.toml"))
    )
    return conf
