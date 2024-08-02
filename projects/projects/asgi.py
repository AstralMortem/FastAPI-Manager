import os
from fastapi_manager.core.app import get_app


os.environ.setdefault("SETTINGS_MODULE", "projects.settings")
app = get_app()
