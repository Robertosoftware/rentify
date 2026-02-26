import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Column, DateTime, Field, SQLModel, String


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class FeatureFlag(SQLModel, table=True):
    __tablename__ = "feature_flags"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(sa_column=Column(String(100), unique=True, nullable=False))
    enabled: bool = Field(default=False, nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(String(500), nullable=True))
    updated_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id", nullable=True)
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
