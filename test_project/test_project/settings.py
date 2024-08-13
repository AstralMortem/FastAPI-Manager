from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
INSTALLED_APPS = ["posts", "penis"]
DATABASE_URL = "postgres://test_user:test_password@localhost:5432/postgres"
DEBUG = True
