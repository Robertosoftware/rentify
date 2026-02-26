import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Column, DateTime, Field, SQLModel, String


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(sa_column=Column(String(255), unique=True, nullable=False, index=True))
    hashed_password: Optional[str] = Field(default=None, sa_column=Column(String(255), nullable=True))
    full_name: Optional[str] = Field(default=None, sa_column=Column(String(255), nullable=True))
    auth_provider: str = Field(default="email", sa_column=Column(String(20), nullable=False))
    google_id: Optional[str] = Field(default=None, sa_column=Column(String(255), nullable=True, unique=True, index=True))
    stripe_customer_id: Optional[str] = Field(default=None, sa_column=Column(String(255), nullable=True, unique=True))
    subscription_status: str = Field(default="none", sa_column=Column(String(20), nullable=False))
    trial_ends_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    telegram_chat_id: Optional[str] = Field(default=None, sa_column=Column(String(255), nullable=True))
    is_admin: bool = Field(default=False)
    gdpr_consent_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
