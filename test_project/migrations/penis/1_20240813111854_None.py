from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "posts_post" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL
);
        DROP TABLE IF EXISTS "penis_penises";
        CREATE TABLE IF NOT EXISTS "penis_penises" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "penis_name" VARCHAR(255) NOT NULL,
    "length" INT NOT NULL  DEFAULT 1
);
        DROP TABLE IF EXISTS "posts_post";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "posts_post";
        DROP TABLE IF EXISTS "penis_penises";"""
