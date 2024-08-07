DEBUG = False
API_DOCS_URL = "/docs"
PROJECT_TITLE = "FastAPI"
PROJECT_DESCRIPTION = ""
PROJECT_API_VERSION = "0.1.0"
INSTALLED_APPS = []

DATABASES = {
    "default": {
        "ENGINE": "fastapi_manager.db.backends.Postgresql",
        "OPTIONS": {
            "dsn": "postgresql+asyncpg://localhost/postgres",
        },
    }
}
