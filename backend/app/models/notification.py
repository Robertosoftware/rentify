import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, String
from sqlmodel import Column, DateTime, Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(UTC)


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    match_id: uuid.UUID | None = Field(default=None, foreign_key="matches.id", nullable=True)
    channel: str = Field(sa_column=Column(String(20), nullable=False))  # telegram, email
    type: str = Field(sa_column=Column(String(50), nullable=False))  # match, trial_ending_48h, etc.
    status: str = Field(default="pending", sa_column=Column(String(20), nullable=False))
    payload: dict = Field(sa_column=Column(JSON, nullable=False))
    error_message: str | None = Field(default=None, nullable=True)
    sent_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
