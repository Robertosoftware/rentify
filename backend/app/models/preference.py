import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, String
from sqlmodel import Column, DateTime, Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(UTC)


class Preference(SQLModel, table=True):
    __tablename__ = "preferences"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    city: str = Field(sa_column=Column(String(100), nullable=False))
    country_code: str = Field(default="NL", sa_column=Column(String(2), nullable=False))
    min_price: int | None = Field(default=None, nullable=True)
    max_price: int = Field(nullable=False)
    min_rooms: float | None = Field(default=None, nullable=True)
    max_rooms: float | None = Field(default=None, nullable=True)
    min_size_sqm: int | None = Field(default=None, nullable=True)
    max_size_sqm: int | None = Field(default=None, nullable=True)
    pet_friendly: bool = Field(default=False)
    furnished: bool | None = Field(default=None, nullable=True)
    keywords: list | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
