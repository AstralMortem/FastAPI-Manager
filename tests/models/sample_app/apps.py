from pathlib import Path

from fastapi_manager.apps import AppConfig


class SampleAppConfig(AppConfig):
    name = "tests.models.sample_app"
