from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class RawListingPreview(BaseModel):
    source_site: str
    source_id: str
    source_url: str
    title: str
    price_eur_cents: Optional[int] = None
    city: str


class NormalizedListing(BaseModel):
    source_site: str
    source_id: str
    source_url: str
    title: str
    description: Optional[str] = None
    price_eur_cents: int
    price_type: str = "per_month"
    rooms: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    size_sqm: Optional[int] = None
    city: str
    neighborhood: Optional[str] = None
    postal_code: Optional[str] = None
    country_code: str = "NL"
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    pet_friendly: Optional[bool] = None
    furnished: Optional[bool] = None
    energy_label: Optional[str] = None
    available_from: Optional[date] = None
    rental_agent: Optional[str] = None
    image_urls: list[str] = []
    raw_data: Optional[dict] = None
    scraped_at: datetime
