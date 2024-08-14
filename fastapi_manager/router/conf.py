import importlib

from fastapi import APIRouter

from fastapi_manager.router.base import BaseRouter
from fastapi_manager.apps import apps
from fastapi_manager.utils.module_loading import module_has_submodule
import inspect

ROUTER_MODULE = "router"


def include(router_path: str) -> BaseRouter:
    app_label = router_path.split(".", 1)[0]
    app_config = apps.get_app_config(app_label)
    if module_has_submodule(app_config.module, "router"):
        router_module = importlib.import_module(f"{app_config.name}.{ROUTER_MODULE}")
    else:
        router_module = importlib.import_module(router_path)

    for name, obj in inspect.getmembers(router_module):
        if name == "ENDPOINTS" and isinstance(obj, BaseRouter):
            setattr(obj, "app_label", app_label)
            return obj
    raise Exception(
        "You must specify global router for app in format ENDPOINTS=APIRouter()"
    )


def path(prefix, router: BaseRouter | APIRouter, *args, **kwargs):
    if prefix == "" or prefix == "/":
        prefix = ""
    if router is None:
        raise Exception("You must set router to instance of BaseRouter or APIRouter")
    new_router = BaseRouter(prefix=prefix, *args, **kwargs)
    new_router.include_router(router)
    return new_router
