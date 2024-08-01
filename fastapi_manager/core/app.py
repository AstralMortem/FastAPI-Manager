from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_manager.conf import settings
from fastapi_manager.utils.decorators import singleton
import fastapi_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Project started")
    yield
    print("Project stopped")


@singleton
class Application:
    def __init__(self, lifespan):
        self._app: FastAPI = FastAPI(
            lifespan=lifespan,
            debug=settings.DEBUG,
            docs_url=settings.API_DOCS_URL,
            title=settings.PROJECT_TITLE,
            description=settings.PROJECT_DESCRIPTION,
            version=settings.PROJECT_API_VERSION,
        )

    def get_app(self):
        return self._app


def get_app(lifespan=lifespan):
    fastapi_manager.setup()
    return Application(lifespan).get_app()
