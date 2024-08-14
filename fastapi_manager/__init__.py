def setup():
    from fastapi_manager.conf import settings
    from fastapi_manager.apps import apps

    apps.populate(settings.INSTALLED_APPS)
