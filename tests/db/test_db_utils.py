from fastapi_manager.db.utils import get_engine, validate_database
from fastapi_manager.db.backends import MysqlDB, Postgresql
from fastapi_manager.conf import settings


def test_get_engine():
    assert get_engine("fastapi_manager.db.backends.MysqlDB") == MysqlDB
    assert get_engine("fastapi_manager.db.backends.Postgresql") == Postgresql


def test_validate_database():
    settings.DATABASES = {
        "default": {
            "ENGINE": "fastapi_manager.db.backends.Postgresql",
            "OPTIONS": {
                "dsn": "postgresql+asyncpg://localhost/test",
            },
        },
        "postgresql": {
            "ENGINE": "fastapi_manager.db.backends.Postgresql",
            "OPTIONS": {
                "host": "localhost",
                "port": 5432,
                "username": "test_user",
                "password": "test_password",
                "path": "db",
            },
        },
        "mysql": {
            "ENGINE": "fastapi_manager.db.backends.MysqlDB",
            "OPTIONS": {
                "host": "localhost",
                "port": 3306,
                "username": "test_user",
                "password": "test_password",
                "path": "db",
            },
        },
    }

    assert validate_database(settings) == "postgresql+asyncpg://localhost/test"
    assert (
        validate_database(settings, "postgresql")
        == "postgresql+asyncpg://test_user:test_password@localhost:5432/db"
    )
    assert (
        validate_database(settings, "mysql")
        == "mysql+asyncmy://test_user:test_password@localhost:3306/db"
    )
