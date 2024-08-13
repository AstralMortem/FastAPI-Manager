from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "posts_post" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS "penis_penises" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "penis_name" VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
