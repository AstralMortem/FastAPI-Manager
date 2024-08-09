import os
from fastapi_manager.core.app import get_app


os.environ.setdefault("SETTINGS_MODULE", "fastapi_test.settings")
app = get_app()
