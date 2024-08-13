import importlib
from fastapi import APIRouter
from fastapi_manager.apps import apps
from fastapi_manager.utils.module_loading import cached_import
import inspect


def include(router_path: str) -> APIRouter:
    app_label = router_path.rsplit(".", 1)[0]
    if not apps.is_installed(app_label):
        raise Exception(f"{app_label} not installed, please add it to INSTALLED_APPS")
    router_module = importlib.import_module(router_path)
    router = getattr(router_module, "router")
    if router:
        return router
    raise Exception(
        "You must specify global router for app in format router=APIRouter()"
    )


def path(prefix: str = "", router: APIRouter = None, *args, **kwargs):
    if prefix == "" or prefix == "/":
        prefix = ""
    return APIRouter(prefix=prefix, *args, **kwargs).include_router(router)
