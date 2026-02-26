import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON
from sqlmodel import Column, DateTime, Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    match_id: Optional[uuid.UUID] = Field(default=None, foreign_key="matches.id", nullable=True)
    channel: str = Field(sa_column=Column(nullable=False))  # telegram, email
    type: str = Field(sa_column=Column(nullable=False))  # match, trial_ending_48h, etc.
    status: str = Field(default="pending", sa_column=Column(nullable=False))
    payload: dict = Field(sa_column=Column(JSON, nullable=False))
    error_message: Optional[str] = Field(default=None, nullable=True)
    sent_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
