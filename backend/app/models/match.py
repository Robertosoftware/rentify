import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, UniqueConstraint
from sqlmodel import Column, DateTime, Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Match(SQLModel, table=True):
    __tablename__ = "matches"
    __table_args__ = (UniqueConstraint("user_id", "listing_id", name="uq_match_user_listing"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    listing_id: uuid.UUID = Field(foreign_key="listings.id", index=True)
    preference_id: uuid.UUID = Field(foreign_key="preferences.id")
    score: float = Field(nullable=False)
    notified: bool = Field(default=False)
    notified_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    notification_channel: str = Field(default="none", sa_column=Column(String(20), nullable=False))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
