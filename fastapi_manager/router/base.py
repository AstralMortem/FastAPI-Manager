from fastapi import APIRouter


class BaseRouter(APIRouter):
    app_label: str
