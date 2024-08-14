import pprint


def setup():
    from fastapi_manager.conf import settings
    from fastapi_manager.apps import apps
    from dynaconf import inspect_settings

    pprint.pprint(inspect_settings(settings), width=100, indent=2)
    apps.populate(settings.INSTALLED_APPS)
