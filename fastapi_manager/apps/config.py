from importlib import import_module
import os
from types import ModuleType

from fastapi_manager.core.exceptions import ImproperlyConfigured
from fastapi_manager.utils.module_loading import module_has_submodule, import_string
import inspect

MODELS_MODULE_NAME = "models"
APPS_MODULE_NAME = "apps"


def _get_unique_file_path(module):
    """Attempt to determine app's filesystem path from its module."""
    # See #21874 for extended discussion of the behavior of this method in
    # various cases.
    # Convert to list because __path__ may not support indexing.
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
    def __init__(self, app_name: str, app_module):
        self.name: str = app_name
        self.module = app_module
        self.apps = None
        self.label = app_name.rpartition(".")[2]
        if not self.label.isidentifier():
            raise ImproperlyConfigured(
                f"The app label '{self.label}' is not a valid Python identifier."
            )

        self.path = _get_unique_file_path(app_module)
        self.models_module = None
        self.models = None

    def import_models(self):
        self.models = self.apps.all_models[self.label]
        if module_has_submodule(self.module, MODELS_MODULE_NAME):
            models_module_name = f"{self.name}.{MODELS_MODULE_NAME}"
            self.models_module = import_module(models_module_name)

    async def on_ready(self):
        """
        Override this method in subclasses to run code when FastAPI starts.
        """

    @classmethod
    def create(cls, entry: str):
        app_config_class: type[cls] | None = None
        app_module: ModuleType = None
        app_name: str = None

        try:
            app_module = import_module(entry)
        except Exception:
            pass
        else:
            app_config_class, app_name = cls._get_appconfig_or_default(
                entry, app_module
            )

        if app_config_class is None:
            try:
                # if entry have full name <fastapi_manager.contrib.app.apps.AppConfig>
                # we import and get AppConfig class
                app_config_class = import_string(entry)
            except ImportError:
                pass
        # if import_strings and import_module failed, it`s mean that entry does not have valid value
        if app_module is None and app_config_class is None:
            raise ImproperlyConfigured(
                "Error importing or configuring app '%s'. " "Is it installed?" % entry
            )
        # try to get full app name
        if app_name is None:
            try:
                app_name = app_config_class.name
            except AttributeError:
                raise Exception(f"{entry} class must suply name attribute")

            # Try import module by full name
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

        return app_config_class(app_name, app_module)

    @classmethod
    def _get_appconfig_or_default(cls, entry, app_module):
        app_config_class = None
        app_name = None
        if module_has_submodule(app_module, APPS_MODULE_NAME):
            mod = import_module(f"{entry}.{APPS_MODULE_NAME}")
            for name, obj in inspect.getmembers(mod, inspect.isclass):
                if issubclass(obj, cls) and name != "AppConfig":
                    app_config_class = obj
                    break
        if app_config_class is None:
            app_config_class = cls
            app_name = entry

        return app_config_class, app_name

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

    def get_models(self, include_auto_created=False, include_swapped=False):
        self.apps.check_models_ready()
        for model in self.models.values():
            # if model._meta.auto_created and not include_auto_created:
            #     continue
            # if model._meta.swapped and not include_swapped:
            #     continue
            yield model

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.label)
