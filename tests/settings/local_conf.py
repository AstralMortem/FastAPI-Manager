DEBUG = True
DATABASES = {
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
