import importlib
import os
from fastapi_manager.conf import global_settings
from fastapi_manager.utils.functional import empty, LazyObject

# Use this to define which settings should be list or tupple
TUPLE_SETTINGS = ("ALLOWED_HOSTS", "INSTALLED_APPS")

# Default settings module in env
ENVIRONMENT_VARIABLE = "SETTINGS_MODULE"


class LazySettings(LazyObject):
    """
    A lazy proxy for either global Django settings or a custom settings object.
    The user can manually configure settings prior to using them. Otherwise,
    Django uses the settings module pointed to by DJANGO_SETTINGS_MODULE.
    """

    def _setup(self, name=None):
        """
        Load the settings module pointed to by the environment variable. This
        is used the first time settings are needed, if the user hasn't
        configured settings manually.
        """
        settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
        if not settings_module:
            desc = ("setting %s" % name) if name else "settings"
            raise Exception(
                "Requested %s, but settings are not configured. "
                "You must either define the environment variable %s "
                "or call settings.configure() before accessing settings."
                % (desc, ENVIRONMENT_VARIABLE)
            )

        self._wrapped = Settings(settings_module)

    def __repr__(self):
        # Hardcode the class name as otherwise it yields 'Settings'.
        if self._wrapped is empty:
            return "<LazySettings [Unevaluated]>"
        return '<LazySettings "%(settings_module)s">' % {
            "settings_module": self._wrapped.SETTINGS_MODULE,
        }

    def __getattr__(self, name):
        """Return the value of a setting and cache it in self.__dict__."""
        if (_wrapped := self._wrapped) is empty:
            self._setup(name)
            _wrapped = self._wrapped
        val = getattr(_wrapped, name)

        # Special case some settings which require further modification.
        # This is done here for performance reasons so the modified value is cached.
        if name in {"MEDIA_URL", "STATIC_URL"} and val is not None:
            val = self._add_script_prefix(val)
        elif name == "SECRET_KEY" and not val:
            raise Exception("The SECRET_KEY setting must not be empty.")

        self.__dict__[name] = val
        return val

    def __setattr__(self, name, value):
        """
        Set the value of setting. Clear all cached values if _wrapped changes
        (@override_settings does this) or clear single values when set.
        """
        if name == "_wrapped":
            self.__dict__.clear()
        else:
            self.__dict__.pop(name, None)
        super().__setattr__(name, value)

    def __delattr__(self, name):
        """Delete a setting and clear it from cache if needed."""
        super().__delattr__(name)
        self.__dict__.pop(name, None)

    def configure(self, default_settings=global_settings, **options):
        """
        Called to manually configure the settings. The 'default_settings'
        parameter sets where to retrieve any unspecified values from (its
        argument must support attribute access (__getattr__)).
        """
        if self._wrapped is not empty:
            raise RuntimeError("Settings already configured.")
        holder = UserSettingsHolder(default_settings)
        for name, value in options.items():
            if not name.isupper():
                raise TypeError("Setting %r must be uppercase." % name)
            setattr(holder, name, value)
        self._wrapped = holder


class UserSettingsHolder:
    """Holder for user configured settings."""

    # SETTINGS_MODULE doesn't make much sense in the manually configured
    # (standalone) case.
    SETTINGS_MODULE = None

    def __init__(self, default_settings):
        """
        Requests for configuration variables not in this class are satisfied
        from the module specified in default_settings (if possible).
        """
        self.__dict__["_deleted"] = set()
        self.default_settings = default_settings

    def __getattr__(self, name):
        if not name.isupper() or name in self._deleted:
            raise AttributeError
        return getattr(self.default_settings, name)

    def __setattr__(self, name, value):
        self._deleted.discard(name)
        super().__setattr__(name, value)

    def __delattr__(self, name):
        self._deleted.add(name)
        if hasattr(self, name):
            super().__delattr__(name)

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
        mod = self._get_local_settings_module()
        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)
                self._validate_special_settings(setting, setting_value)
                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)

    def _validate_special_settings(self, key, value):
        if key in TUPLE_SETTINGS and not isinstance(value, (list, tuple)):
            raise Exception("The %s setting must be a list or a tuple." % key)

    def _get_local_settings_module(self):
        try:
            mod = importlib.import_module(self.SETTINGS_MODULE)
            return mod
        except ImportError as error:
            raise Exception(f"Module '{error.name}' does not exists")


settings = LazySettings()
