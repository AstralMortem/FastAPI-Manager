import threading
from collections import defaultdict
from typing import Dict

from fastapi_manager.apps.config import AppConfig
from fastapi_manager.core.exceptions import AppRegistryNotReady
import asyncio


class Apps:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Apps, cls).__new__(cls)
        return cls._instance

    def __init__(self, installed_apps=None):
        if hasattr(self, "initialized"):
            return
        self.initialized = True

        self.all_models = defaultdict(dict)
        self.app_configs: Dict[str, AppConfig] = {}
        self.apps_ready = self.models_ready = self.ready = False
        self._lock = threading.RLock()

        if installed_apps is not None:
            self.populate(installed_apps)

    def populate(self, installed_apps):
        if self.ready:
            return

        with self._lock:
            if self.ready:
                return

            for entry in installed_apps:
                app_config = AppConfig.create(entry)
                if app_config.label in self.app_configs:
                    raise RuntimeError(f"Duplicate app label: {app_config.label}")
                self.app_configs[app_config.label] = app_config
                app_config.apps = self

            self.apps_ready = True

            for app_config in self.app_configs.values():
                app_config.import_models()

            self.models_ready = True

            for app_config in self.get_app_configs():
                asyncio.run(app_config.on_ready())

            self.ready = True

    def get_app_configs(self):
        self.check_apps_ready()
        return self.app_configs.values()

    def get_app_config(self, app_label):
        self.check_apps_ready()
        try:
            return self.app_configs[app_label]
        except KeyError:
            raise LookupError(f"No installed app with label '{app_label}'.")

    def check_apps_ready(self):
        if not self.apps_ready:
            raise AppRegistryNotReady("Apps aren't loaded yet.")

    def check_models_ready(self):
        if not self.models_ready:
            raise AppRegistryNotReady("Models aren't loaded yet.")


apps = Apps()
