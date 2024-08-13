from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
INSTALLED_APPS = ["test_app"]
DATABASES = "postgresql+asyncpg://test:test@localhost:5432/test"
ROOT_ROUTER = "test_project.router"
