from tortoise import Tortoise, expand_db_url
from fastapi_manager.conf import settings
from fastapi_manager.apps import apps
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

modules = {
    app_config.label: {
        "models": [app_config.models_module],
        "default_connection": "default",
    }
    for app_config in apps.get_app_configs()
}

modules.update({"models": {"models": ["aerich.models"]}})

TORTOISE_ORM = {
    "connections": {"default": expand_db_url(settings.DATABASE_URL, settings.DEBUG)},
    "apps": {**modules},
}


def register_db(app: FastAPI):
    register_tortoise(app=app, config=TORTOISE_ORM, generate_schemas=False)
