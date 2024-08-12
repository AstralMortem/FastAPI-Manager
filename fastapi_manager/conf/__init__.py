import importlib
import os

from fastapi_manager.core.exceptions import ImproperlyConfigured
from fastapi_manager.conf import global_settings

# from fastapi_manager.utils.functional import empty, LazyFactory
from fastapi_manager.utils.lazy import LazyFactory, LazyObject, empty

# Use this to define which settings should be list or tupple
TUPLE_SETTINGS = ("ALLOWED_HOSTS", "INSTALLED_APPS")

# Default settings module in env
ENVIRONMENT_VARIABLE = "SETTINGS_MODULE"


class LazySettings(LazyObject):
    def _setup(self, name=None):
        settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
        if not settings_module:
            desc = ("setting %s" % name) if name else "settings"
            raise ImproperlyConfigured(
                "Requested %s, but settings are not configured. "
                "You must either define the environment variable %s "
                "or call settings.configure() before accessing settings."
                % (desc, ENVIRONMENT_VARIABLE)
            )
        self._wrapped = Settings(settings_module)

    def __getattr__(self, name):
        if (_wrapped := self._wrapped) is empty:
            self._setup(name)
            _wrapped = self._wrapped
        val = getattr(_wrapped, name)
        self.check_special_case(name, val)
        self.__dict__[name] = val
        return val

    def __setattr__(self, name, value):
        if name == "_wrapped":
            self.__dict__.clear()
        else:
            self.__dict__.pop(name, None)
        super().__setattr__(name, value)

    def __delattr__(self, name):
        super().__delattr__(name)
        self.__dict__.pop(name, None)

    def check_special_case(self, name, val):
        pass

    def configure(self, default_settings=global_settings, **options):
        if self._wrapped is not empty:
            raise RuntimeError("Settings already configured.")
        holder = LocalSettingsHolder(default_settings)
        for name, value in options.items():
            if not name.isupper():
                raise TypeError("Setting %r must be uppercase." % name)
            setattr(holder, name, value)
        self._wrapped = holder


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
        for setting in dir(self.SETTINGS_MODULE):
            if setting.isupper():
                setting_value = getattr(self.SETTINGS_MODULE, setting)
                self._validate_special_settings(setting, setting_value)
                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)

    @staticmethod
    def _validate_special_settings(key, value):
        if key in TUPLE_SETTINGS and not isinstance(value, (list, tuple)):
            raise Exception("The %s setting must be a list or a tuple." % key)


class LocalSettingsHolder:
    def __init__(self, default):
        self.__dict__["_deleted"] = set()
        self.default_settings = default

    def __getattr__(self, name):
        if not name.isupper() or name in self._deleted:
            raise AttributeError
        return getattr(self.default_settings, name)

    def __delattr__(self, name):
        self._deleted.add(name)
        if hasattr(self, name):
            super().__delattr__(name)

    def __setattr__(self, name, value):
        self._deleted.discard(name)
        super().__setattr__(name, value)

    def __dir__(self):
        return sorted(
            s
            for s in [*self.__dict__, *dir(self.default_settings)]
            if s not in self._deleted
        )

    def is_overridden(self, setting):
        deleted = setting in self._deleted
        set_locally = setting in self.__dict__
        set_on_default = getattr(
            self.default_settings, "is_overridden", lambda s: False
        )(setting)
        return deleted or set_locally or set_on_default

    def __repr__(self):
        return "<%(cls)s>" % {
            "cls": self.__class__.__name__,
        }


settings = LazySettings()
