# TODO:
#  Add parser for database settings
#  Add util for checking if modules exists
import importlib

from pydantic import BaseModel, ValidationError

from fastapi_manager.utils.module_loading import import_string


class DatabaseError(Exception):
    def __init__(self, message):
        super().__init__(message)


class EngineDoesNotExist(DatabaseError):
    pass


class DatabaseNotInSettings(DatabaseError):
    pass


class IncorrectDatabaseSetting(DatabaseError):
    pass


class DatabaseManagerError(DatabaseError):
    pass


def get_engine(engine_module) -> type[BaseModel]:
    try:
        return import_string(engine_module)
    except Exception as e:
        raise EngineDoesNotExist(e.args[0])


def validate_database(settings_module, key="default"):
    try:
        databases: dict = getattr(settings_module, "DATABASES")
        engine_path, options = databases[key].values()

        engine = get_engine(engine_path)
        database = engine.model_validate(options)

        return database.get_dsn

    except AttributeError as e:
        raise DatabaseNotInSettings(e)
    except ValidationError as e:
        raise IncorrectDatabaseSetting(e)
