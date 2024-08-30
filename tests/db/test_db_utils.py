import pytest

from fastapi_manager.db.utils import (
    validate_database,
    validate_database_engine,
)


@pytest.mark.skip
def test_db_validation(settings):
    valid_db = validate_database(settings)
    assert valid_db.get("dsn") == "sqlite://:memory"
    assert list(valid_db.get("default").keys()) == ["engine", "credentials"]


def test_engine_validation():
    for engine in ["tortoise.backends.sqlite", "error"]:
        with pytest.raises(Exception):
            assert validate_database_engine(engine)


# def test_apps_connector(settings):
#     from fastapi_manager.apps import apps
#
#     apps.populate(["tests.models.sample_app"])
#     assert get_apps(settings).keys()
