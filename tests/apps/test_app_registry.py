import pytest
from fastapi_manager.apps.registry import Apps, apps as apps2


@pytest.fixture(scope="function")
def apps(settings):
    apps = Apps(settings.INSTALLED_APPS)
    return apps


def test_app_registry_check_models_ready(apps):
    assert apps.models_ready == True


def test_app_registry_ready(apps):
    assert apps.ready == True


def test_population_module_not_found(apps):
    with pytest.raises(ModuleNotFoundError):
        apps.set_installed_apps(["not_found"])


# class TestOneConfigApp:
#
#     APP_NAME = "one_config_app"
#     APP_MODULE = "tests.apps.one_config_app"
#     INSTALLED_APPS = [APP_MODULE]
#
#     @cached_property
#     def apps(self):
#         if hasattr(sys.modules["fastapi_manager.apps.registry"], "apps"):
#             delattr(sys.modules["fastapi_manager.apps.registry"], "apps")
#         apps = Apps(self.INSTALLED_APPS)
#         return apps
#
#     @cached_property
#     def app_config(self):
#         return self.apps.get_app_config(self.APP_NAME)
#
#     def test_population_one_config_app(self):
#         apps = self.apps
#         assert apps.models_ready == True
#         assert apps.apps_ready == True
#         assert apps.ready == True
#
#     def test_get_config(self):
#         assert isinstance(self.app_config, AppConfig)
#
#     def test_label(self):
#         assert self.app_config.label == self.APP_NAME
#
#     def test_name(self):
#         assert self.app_config.name == self.APP_MODULE
#
#     def test_module(self):
#         assert self.app_config.module == importlib.import_module(self.APP_MODULE)
#
#     def test_models(self):
#         assert self.app_config.models == {}


def test_existed_models(settings):
    apps2.populate(["tests.apps.models_app"])

    assert apps2.all_models == {
        "models_app": {"test_model": apps2.get_model("models_app", "test_model")}
    }
    model = apps2.get_model("models_app", "TestModel")

    assert model.model_name == "test_model"
    assert model._meta.db_table == "models_app_test_model"
    assert model._meta.app == "models_app"
