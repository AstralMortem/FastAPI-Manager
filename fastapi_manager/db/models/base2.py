from typing import Any, ClassVar, Tuple
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept
from .mixins import CommonMixin
from fastapi_manager.utils.string import convert_to_snake_case
from fastapi_manager.apps import apps


# inherit DeclarativeAttributeIntercept to avoid metaclasses conflcts, `cause DeclarativeBase use it as metaclass
class BaseMeta(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__

        parents = [b for b in bases if isinstance(b, BaseMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        # get module of inherited class
        module = attrs.get("__module__")
        app_label = None
        app_config = apps.get_containing_app_config(module)
        if app_config is None:
            raise RuntimeError(
                "Model class %s.%s doesn't declare an explicit "
                "app_label and isn't in an application in "
                "INSTALLED_APPS." % (module, name)
            )
        else:
            app_label = app_config.label

        new_class = super_new(cls, name, bases, attrs, **kwargs)

        if not hasattr(new_class, "app_label"):
            new_class.app_label = app_label
        if not hasattr(new_class, "apps"):
            new_class.apps = apps
        if not hasattr(new_class, "model_name"):
            new_class.model_name = convert_to_snake_case(name)
        apps.register_model(new_class.app_label, new_class)
        return new_class


# to avoid metaclass conflicts
class CombinedMetaclass(BaseMeta, DeclarativeAttributeIntercept):
    pass


class Model(DeclarativeBase, CommonMixin, metaclass=CombinedMetaclass):
    repr_cols_num: ClassVar[int] = 3
    repr_cols: ClassVar[Tuple] = tuple()

    # TODO: imlement auto __tablename__ with app_label + model_name

    def __repr__(self):
        """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"
