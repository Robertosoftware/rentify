import uuid
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import JSON, String, UniqueConstraint
from sqlmodel import Column, DateTime, Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Listing(SQLModel, table=True):
    __tablename__ = "listings"
    __table_args__ = (UniqueConstraint("source_site", "source_id", name="uq_listing_source"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    source_site: str = Field(sa_column=Column(String(100), nullable=False, index=True))
    source_id: str = Field(sa_column=Column(String(255), nullable=False))
    source_url: str = Field(sa_column=Column(String(2048), nullable=False))
    title: str = Field(sa_column=Column(String(500), nullable=False))
    description: Optional[str] = Field(default=None, nullable=True)
    price_eur: int = Field(nullable=False)
    price_type: str = Field(default="per_month", sa_column=Column(String(20), nullable=False))
    rooms: Optional[float] = Field(default=None, nullable=True)
    bedrooms: Optional[int] = Field(default=None, nullable=True)
    bathrooms: Optional[int] = Field(default=None, nullable=True)
    size_sqm: Optional[int] = Field(default=None, nullable=True)
    city: str = Field(sa_column=Column(String(100), nullable=False, index=True))
    neighborhood: Optional[str] = Field(default=None, sa_column=Column(String(200), nullable=True))
    postal_code: Optional[str] = Field(default=None, sa_column=Column(String(10), nullable=True))
    country_code: str = Field(default="NL", sa_column=Column(String(2), nullable=False))
    address: Optional[str] = Field(default=None, sa_column=Column(String(500), nullable=True))
    latitude: Optional[float] = Field(default=None, nullable=True)
    longitude: Optional[float] = Field(default=None, nullable=True)
    pet_friendly: Optional[bool] = Field(default=None, nullable=True)
    furnished: Optional[bool] = Field(default=None, nullable=True)
    energy_label: Optional[str] = Field(default=None, sa_column=Column(String(5), nullable=True))
    available_from: Optional[date] = Field(default=None, nullable=True)
    rental_agent: Optional[str] = Field(default=None, sa_column=Column(String(255), nullable=True))
    image_urls: Optional[list] = Field(default=None, sa_column=Column(JSON, nullable=True))
    raw_data: Optional[dict] = Field(default=None, sa_column=Column(JSON, nullable=True))
    first_seen_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    last_seen_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    delisted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
