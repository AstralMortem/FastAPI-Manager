import importlib
from pathlib import Path
from fastapi import APIRouter
from fastapi_manager.conf import settings
from fastapi_manager.core.app import Application

router = APIRouter()


def resolve_urls():
    base_dir: Path = settings.BASE_DIR
    urls = importlib.import_module(f"{base_dir.name}.{base_dir.name}.routers")

    App
    return urls.router_list
