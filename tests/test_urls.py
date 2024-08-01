from fastapi_manager.conf import settings
from fastapi_manager.routers.base import resolve_urls
from fastapi_manager.core.managment.handlers import CreateProject, StartApp


def test_urls():
    project = CreateProject("test_projects", None)
    project.execute()

    # settings.configure()
    # settings.BASE_DIR = project._get_destination()

    app = StartApp("test_app")
    app.execute()

    assert resolve_urls() == []
