import inspect
import os
from importlib import import_module
from typing import Any, TYPE_CHECKING

from types import ModuleType

from fastapi_manager.core.exceptions import ImproperlyConfigured
from fastapi_manager.utils.module_loading import module_has_submodule, import_string

MODELS_MODULE_NAME = "models"
APPS_MODULE_NAME = "apps"

if TYPE_CHECKING:
    from .registry import Apps


def get_unique_file_path_to_module(module):
    paths = list(getattr(module, "__path__", []))
    if len(paths) != 1:
        filename = getattr(module, "__file__", None)
        if filename is not None:
            paths = [os.path.dirname(filename)]
        else:
            # For unknown reasons, sometimes the list returned by __path__
            # contains duplicates that must be removed (#25246).
            paths = list(set(paths))
    if len(paths) > 1:
        raise ImproperlyConfigured(
            "The app module %r has multiple filesystem locations (%r); "
            "you must configure this app with an AppConfig subclass "
            "with a 'path' class attribute." % (module, paths)
        )
    elif not paths:
        raise ImproperlyConfigured(
            "The app module %r has no filesystem location, "
            "you must configure this app with an AppConfig subclass "
            "with a 'path' class attribute." % module
        )
    return paths[0]


class AppConfig:

    name: str

    def __init__(self, app_name: str, app_module):
        # Full Python path to the application e.g. 'fastapi_manager.extensions.app1'.
        self.name: str = app_name

        # root module of application
        self.module: Any = app_module

        # app registry, sets in registry.py Apps class
        self.apps: Apps | None = None

        # check label for app, it will be used in regitry dict as key, to get app config by this label
        if not hasattr(self, "label"):
            self.label = app_name.rpartition(".")[2]
        if not self.label.isidentifier():
            raise ImproperlyConfigured(
                "The app label '%s' is not a valid Python identifier." % self.label
            )

        # Filesystem path to the application directory e.g.
        if not hasattr(self, "path"):
            self.path = get_unique_file_path_to_module(app_module)

        # Module of app models, <app.models> None if no models module, sets by import_models()
        self.models_module = None
        self.models = None

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.label)

    def get_model(self, model_name, require_ready=True):
        if require_ready:
            self.apps.check_models_ready()
        else:
            self.apps.check_apps_ready()
        try:
            return self.models[model_name.lower()]
        except KeyError:
            raise LookupError(
                "App '%s' doesn't have a '%s' model." % (self.label, model_name)
            )

    def get_models(self):
        self.apps.check_apps_ready()
        self.apps.check_models_ready()
        for model in self.models.values():
            yield model

    def import_models(self):
        # Dont understand why this is needed TODO: remove it
        # Get models list from app registry by key as app label
        # self.models = self.apps.all_models[self.label]

        # check if inside app folder exist module with models
        if module_has_submodule(self.module, MODELS_MODULE_NAME):
            models_module_name = "%s.%s" % (self.name, MODELS_MODULE_NAME)
            self.models_module = import_module(models_module_name)

    def ready(self):
        """
        Override this method in subclasses to run code when Django starts.
        """
        # TODO: make it work with async also

    @classmethod
    def create(cls, entry: str):
        app_config_class: type[cls] | None = None
        app_name: str | None = None
        app_module: ModuleType | None = None

        # Try to import module by entry
        try:
            app_module = import_module(entry)
        except Exception:
            pass
        else:
            # If app_module has an apps submodule that defines a single
            # AppConfig subclass, use it automatically.
            # To prevent this, an AppConfig subclass can declare a class
            # variable default = False.
            # If the apps module defines more than one AppConfig subclass,
            # the default one can declare default = True.
            # if we don`t find anything, set default AppConfig class, app_name = entry
            app_config_class, app_name = cls.get_apps_or_default(app_module, entry)

        # If import_string succeeds, entry is an app config class.
        if app_config_class is None:
            try:
                app_config_class = import_string(entry)
            except Exception:
                pass

        # If both import_module and import_string failed, it means that entry
        # doesn't have a valid value. So
        if app_module is None and app_config_class is None:
            cls.check_dummy_name(entry)

        # Check for obvious errors. (This check prevents duck typing, but
        # it could be removed if it became a problem in practice.)
        if not issubclass(app_config_class, AppConfig):
            raise ImproperlyConfigured("'%s' isn't a subclass of AppConfig." % entry)

        # Obtain app name here rather than in AppClass.__init__ to keep
        # all error checking for entries in INSTALLED_APPS in one place.
        if app_name is None:
            try:
                app_name = app_config_class.name
            except AttributeError:
                raise ImproperlyConfigured("'%s' must supply a name attribute." % entry)

        # Ensure app_name points to a valid module.
        try:
            app_module = import_module(app_name)
        except ImportError:
            raise ImproperlyConfigured(
                "Cannot import '%s'. Check that '%s.%s.name' is correct."
                % (
                    app_name,
                    app_config_class.__module__,
                    app_config_class.__qualname__,
                )
            )

        # Entry is a path to an app config class.
        return app_config_class(app_name, app_module)

    @classmethod
    def get_apps_or_default(cls, app_module, entry: str):
        app_config_class: type[cls] | None = None
        new_app_name = None
        if module_has_submodule(app_module, APPS_MODULE_NAME):
            mod_path = "%s.%s" % (entry, APPS_MODULE_NAME)
            mod = import_module(mod_path)
            # Check if there's exactly one AppConfig candidate,
            # excluding those that explicitly define default = False.
            app_configs = [
                (name, candidate)
                for name, candidate in inspect.getmembers(mod, inspect.isclass)
                if (
                    issubclass(candidate, cls)
                    and candidate is not cls
                    and getattr(candidate, "default", True)
                )
            ]
            if len(app_configs) == 1:
                app_config_class = app_configs[0][1]
            else:
                # Check if there's exactly one AppConfig subclass,
                # among those that explicitly define default = True.
                app_configs = [
                    (name, candidate)
                    for name, candidate in app_configs
                    if getattr(candidate, "default", False)
                ]
                if len(app_configs) > 1:
                    candidates = [repr(name) for name, _ in app_configs]
                    raise RuntimeError(
                        "%r declares more than one default AppConfig: "
                        "%s." % (mod_path, ", ".join(candidates))
                    )
                elif len(app_configs) == 1:
                    app_config_class = app_configs[0][1]
        if app_config_class is None:
            app_config_class = cls
            new_app_name = entry
        return app_config_class, new_app_name

    @classmethod
    def check_dummy_name(cls, entry: str):
        mod_path, _, cls_name = entry.rpartition(".")
        if mod_path and cls_name[0].isupper():
            # We could simply re-trigger the string import exception, but
            # we're going the extra mile and providing a better error
            # message for typos in INSTALLED_APPS.
            # This may raise ImportError, which is the best exception
            # possible if the module at mod_path cannot be imported.
            mod = import_module(mod_path)
            candidates = [
                repr(name)
                for name, candidate in inspect.getmembers(mod, inspect.isclass)
                if issubclass(candidate, cls) and candidate is not cls
            ]
            msg = "Module '%s' does not contain a '%s' class." % (
                mod_path,
                cls_name,
            )
            if candidates:
                msg += " Choices are: %s." % ", ".join(candidates)
            raise ImportError(msg)
        else:
            # Re-trigger the module import exception.
            import_module(entry)
