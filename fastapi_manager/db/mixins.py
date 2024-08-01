import datetime
from typing import Any, Generic, Optional, TypeVar
import uuid
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field

_ID = TypeVar("_ID")


class IntPrimaryKey(BaseModel):
    id: int | None = Field(default=None, primary_key=True)


class UUIDPrimaryKey(BaseModel):
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)


class TimestampMixin(BaseModel):
    created_at: datetime.datetime | None = Field(
        sa_column=Column(DateTime, nullable=True, server_default=func.now())
    )

    updated_at: datetime.data | None = Field(
        sa_column=Column(DateTime, nullable=True, onupdate=func.now())
    )


class DefaultMixin(UUIDPrimaryKey, TimestampMixin):
    pass
