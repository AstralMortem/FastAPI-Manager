from typing import Type, Tuple

from tortoise.models import ModelMeta, Model as TModel
from tortoise.fields import UUIDField
from fastapi_manager.apps import apps
from fastapi_manager.utils.string import convert_to_snake_case
from tortoise.contrib.pydantic import pydantic_model_creator


class ModelMetaWrapped(ModelMeta):
    def __new__(mcs, name: str, bases: Tuple[Type, ...], attrs: dict):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, ModelMetaWrapped)]
        if not parents:
            return super_new(mcs, name, bases, attrs)

        module = attrs.get("__module__")
        app_config = apps.get_containing_app_config(module)
        app_label = None
        if app_config is None:
            raise RuntimeError(
                "Model class %s.%s doesn't declare an explicit "
                "app_label and isn't in an application in "
                "INSTALLED_APPS." % (module, name)
            )
        else:
            app_label = app_config.label

        new_class = super_new(mcs, name, bases, attrs)
        new_class._meta.app = app_label

        if not hasattr(new_class, "model_name"):
            new_class.model_name = convert_to_snake_case(name)
        if not hasattr(new_class, "apps"):
            new_class.apps = apps
        new_class._meta.db_table = f"{app_label}_{new_class.model_name}"
        apps.register_model(app_label, new_class)
        if not hasattr(new_class, "pydantic_model"):
            new_class.pydantic_model = pydantic_model_creator(new_class)
        return new_class


class Model(TModel, metaclass=ModelMetaWrapped):
    id = UUIDField(primary_key=True, db_index=True)

    class Meta:
        abstract = True

    def dump_to_pydantic(self):
        return self.pydantic_model.from_tortoise_orm(self)


__all__ = ["Model"]
