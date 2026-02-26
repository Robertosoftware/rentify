import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ARRAY, String
from sqlmodel import Column, DateTime, Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Preference(SQLModel, table=True):
    __tablename__ = "preferences"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    city: str = Field(sa_column=Column(String(100), nullable=False))
    country_code: str = Field(default="NL", sa_column=Column(String(2), nullable=False))
    min_price: Optional[int] = Field(default=None, nullable=True)
    max_price: int = Field(nullable=False)
    min_rooms: Optional[float] = Field(default=None, nullable=True)
    max_rooms: Optional[float] = Field(default=None, nullable=True)
    min_size_sqm: Optional[int] = Field(default=None, nullable=True)
    max_size_sqm: Optional[int] = Field(default=None, nullable=True)
    pet_friendly: bool = Field(default=False)
    furnished: Optional[bool] = Field(default=None, nullable=True)
    keywords: Optional[list] = Field(default=None, sa_column=Column(ARRAY(String), nullable=True))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
