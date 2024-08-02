import importlib
import os
from fastapi_manager.conf import global_settings

# from fastapi_manager.utils.functional import empty, LazyObject
from fastapi_manager.utils.lazy import LazyObject

# Use this to define which settings should be list or tupple
TUPLE_SETTINGS = ("ALLOWED_HOSTS", "INSTALLED_APPS")

# Default settings module in env
ENVIRONMENT_VARIABLE = "SETTINGS_MODULE"


class Settings:
    def __init__(self, settings_module):
        self._explicit_settings = set()
        self.SETTINGS_MODULE = settings_module

        self._load_global_settings()
        self._load_local_settings()

    def is_overridden(self, setting):
        return setting in self._explicit_settings

    def __repr__(self):
        return '<%(cls)s "%(settings_module)s">' % {
            "cls": self.__class__.__name__,
            "settings_module": self.SETTINGS_MODULE,
        }

    def _load_global_settings(self):
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))

    def _load_local_settings(self):
        mod = importlib.import_module(self.SETTINGS_MODULE)
        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)
                self._validate_special_settings(setting, setting_value)
                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)

    def _validate_special_settings(self, key, value):
        if key in TUPLE_SETTINGS and not isinstance(value, (list, tuple)):
            raise Exception("The %s setting must be a list or a tuple." % key)


settings = LazyObject(lambda: Settings(os.environ.get(ENVIRONMENT_VARIABLE)))
