from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI
from fastapi_manager.conf import settings
from fastapi_manager.utils.decorators import singleton
import fastapi_manager
from fastapi_manager.routers.base import resolve_urls


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

    def resolve_main_urls(self):
        for router in resolve_urls():
            self.include_router(router)

    def include_router(self, router: APIRouter):
        self._app.include_router(router)


def get_app(lifespan=lifespan):
    fastapi_manager.setup()
    application = Application(lifespan)
    application.resolve_main_urls()

    return application.get_app()
