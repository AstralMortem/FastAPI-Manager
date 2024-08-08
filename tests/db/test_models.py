import pytest
from fastapi_manager.conf import settings
from fastapi_manager.db.models import BaseTable


@pytest.fixture(autouse=True)
def set_database_url():
    settings.DATABASES = {
        "default": {
            "ENGINE": "fastapi_manager.db.backends.Postgresql",
            "OPTIONS": {
                "host": "localhost",
                "port": 5432,
                "username": "test_user",
                "password": "test_password",
                "path": "test_db",
            },
        }
    }


class TableForTest(BaseTable):
    pass


def test_tablename():
    assert TableForTest.__tablename__ == "table_for_test"


# @pytest.mark.asyncio
# async def test_table_creation():
#     async with sessionmanager.session() as session:
#         table = TableForTest()
#         session.add(table)
#         await session.commit()
