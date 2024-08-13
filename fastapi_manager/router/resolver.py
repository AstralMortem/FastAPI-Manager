import importlib

from fastapi import FastAPI

from fastapi_manager.conf import settings


def url_resolver(app: FastAPI):
    root_router = importlib.import_module(settings.ROOT_ROUTER)
    try:
        endpoints = getattr(root_router, "endpoints")
    except AttributeError:
        raise AttributeError("You need enpoints list in format endpoints=[...]")

    for endpoint in endpoints:
        print(endpoint)
        # app.include_router(endpoint)
