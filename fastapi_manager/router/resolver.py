import importlib

from fastapi import FastAPI

from fastapi_manager.conf import settings


def url_resolver(app: FastAPI):
    root_router = importlib.import_module(settings.ROOT_ROUTER)
    try:
        endpoints = getattr(root_router, "ENDPOINTS")
    except AttributeError:
        raise AttributeError("You need set enpoints list in format ENDPOINTS=[...]")

    for endpoint in endpoints:
        app.include_router(endpoint)
