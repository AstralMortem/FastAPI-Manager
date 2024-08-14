from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI
from fastapi_manager.conf import settings
import fastapi_manager

# from fastapi_manager.db.connection import register_db
from fastapi_manager.router import url_resolver


@asynccontextmanager
async def default_lifespan(app: FastAPI):
    print("Project started")
    # register_db(app)
    yield
    print("Project stopped")


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

        self.resolve_urls()

    def get_app(self):
        return self._app

    def resolve_urls(self):
        url_resolver(self._app)


def get_app(lifespan=default_lifespan):
    fastapi_manager.setup()
    application = Application(lifespan)
    return application.get_app()
