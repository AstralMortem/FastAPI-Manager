from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "posts_post" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL
);
        DROP TABLE IF EXISTS "penis_penises";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "posts_post";"""
