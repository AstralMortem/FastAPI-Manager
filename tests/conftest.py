import pytest
import os
from fastapi_manager.conf import ENVIRONMENT_VARIABLE
import time


@pytest.fixture(scope="session", autouse=True)
def load_environ():
    os.environ.setdefault(ENVIRONMENT_VARIABLE, "tests.settings.local_conf")
