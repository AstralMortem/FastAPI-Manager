from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID, uuid4


class UUIDPrimaryKey:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4())


class IntPrimaryKey:
    id: Mapped[int] = mapped_column(primary_key=True)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.now())


class CommonMixin(UUIDPrimaryKey, TimestampMixin):
    pass
