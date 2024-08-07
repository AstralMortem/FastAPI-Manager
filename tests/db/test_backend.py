from fastapi_manager.db.backends import (
    Postgresql,
    MysqlDB,
    MySQLDsn,
)
import pytest
from contextlib import nullcontext as does_not_raise
import itertools

from pydantic import PostgresDsn

TEST_ASSET = {
    "host": "localhost",
    "port": 5432,
    "path": "test",
    "username": "test_user",
    "password": "test_password",
}


def get_test_dsn(schema, test_dict, converter):
    test = []
    for i in range(len(test_dict)):
        test.append(
            (
                new_dict := dict(itertools.islice(test_dict.items(), i + 1)),
                str(converter.build(scheme=schema, **new_dict)),
                does_not_raise(),
            )
        )
    return test


def functional_test(functions: list[list[tuple]], aditional_tests: list[tuple] = []):
    test = aditional_tests
    for func in functions:
        test.extend(func)
    return test


@pytest.mark.parametrize(
    "options, result, expectation",
    functional_test(
        [
            get_test_dsn("mysql+asyncmy", TEST_ASSET, MySQLDsn),
            [
                (
                    {"dsn": "mysql+aiomysql://localhost"},
                    "mysql+aiomysql://localhost:3306",
                    does_not_raise(),
                ),
                ({}, "test", pytest.raises(Exception)),
                (
                    {"driver": "aiomysql", "host": "localhost"},
                    "mysql+aiomysql://localhost",
                    does_not_raise(),
                ),
            ],
        ],
    ),
)
def test_mysqldb(options, result, expectation):
    with expectation:
        assert result == MysqlDB.model_validate(options).get_dsn


@pytest.mark.parametrize(
    "options, result, expectation",
    functional_test(
        [get_test_dsn("postgresql+asyncpg", TEST_ASSET, PostgresDsn)],
        [
            (
                {"dsn": "postgresql+asyncpg://localhost"},
                "postgresql+asyncpg://localhost",
                does_not_raise(),
            ),
            ({}, "test", pytest.raises(ValueError)),
            (
                {"driver": "asyncio", "host": "localhost"},
                "postgresql+asyncio://localhost",
                does_not_raise(),
            ),
        ],
    ),
)
def test_postgresql(options, result, expectation):
    with expectation:
        assert result == Postgresql.model_validate(options).get_dsn
