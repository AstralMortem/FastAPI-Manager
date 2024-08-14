import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.absolute()
os.environ.setdefault("FASTAPI_SETTINGS", "./test_project/settings.toml")
os.environ.setdefault("PROJECT_DIR", str(PROJECT_DIR))

from fastapi_manager.core.app import get_app

app = get_app()
