import importlib


class AppConfig:
    name = None
    path = None

    def __init_subclass__(cls) -> None:
        cls.path = cls.__module__
        if not hasattr(cls, "models_module"):
            cls.models_module = cls.path.removesuffix(".apps") + "." + "models"

    @classmethod
    def get_models(cls):
        return next(iter(cls.pools)).get_app_models(cls.name)

    @classmethod
    def get_model(cls, model_name: str):
        app_models = cls.get_models()
        for model in app_models:
            if model.__name__ == model_name or model.__tablename__ == model_name:
                return model
