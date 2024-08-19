from importlib.util import find_spec
from tortoise.contrib.fastapi import register_tortoise
from fastapi import FastAPI


def validate_database_engine(backend: str | None):
    if backend is None:
        raise Exception("You need to set engine value")
    find_spec(backend)


def validate_database(settings_module):
    string = settings_module.DATABASES
    connection_dict = {}

    for key, val in string.items():
        if isinstance(val, dict):
            validate_database_engine(val.get("engine", None))
            connection_dict[key] = dict(val)
        if isinstance(val, str):
            connection_dict[key] = val

    return connection_dict


def get_apps(settings_module):
    apps_dict = {}
    from fastapi_manager.apps import apps

    for app in apps.get_app_configs():
        apps_dict[app.label] = {
            "models": [app.models_module],
            "default_connections": settings_module.DEFAULT_DB_CONNECTION,
        }

    apps_dict["migrations"] = {
        "models": ["aerich.models"],
        "default_connections": settings_module.DEFAULT_DB_CONNECTION,
    }

    return apps_dict


def create_db_config(settings_module):
    return {
        "connections": validate_database(settings_module),
        "apps": get_apps(settings_module),
    }


def register_to_fastapi(settings_module, app: FastAPI, *args, **kwargs):
    register_tortoise(
        app=app, config=create_db_config(settings_module), *args, **kwargs
    )
