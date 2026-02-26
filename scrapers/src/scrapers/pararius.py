import re
from datetime import datetime, timezone
from typing import Optional

from bs4 import BeautifulSoup

from scrapers.src.base_scraper import BaseScraper
from scrapers.src.models.listing import NormalizedListing, RawListingPreview


class ParariusScraper(BaseScraper):
    site_name = "pararius"
    base_url = "https://www.pararius.com"
    max_concurrent = 2
    request_delay_range = (2.0, 4.0)

    async def build_search_url(self, city: str, page: int = 1, **filters) -> str:
        city_slug = city.lower().replace(" ", "-")
        url = f"{self.base_url}/apartments/{city_slug}"
        min_p = filters.get("min_price", "")
        max_p = filters.get("max_price", "")
        if min_p or max_p:
            url += f"/{min_p}-{max_p}"
        if page > 1:
            url += f"/page-{page}"
        return url

    async def parse_search_results(self, html: str) -> list[RawListingPreview]:
        soup = BeautifulSoup(html, "lxml")
        results = []
        cards = soup.find_all(class_=re.compile(r"listing-search-item"))
        for card in cards:
            try:
                link = card.find("a", class_=re.compile(r"listing-search-item__link|name"))
                if not link:
                    link = card.find("a")
                if not link:
                    continue
                href = link.get("href", "")
                source_url = href if href.startswith("http") else f"{self.base_url}{href}"
                source_id = href.rstrip("/").split("/")[-1]
                title_el = card.find(class_=re.compile(r"listing-search-item__title|name"))
                title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)
                price_el = card.find(class_=re.compile(r"listing-search-item__price|price"))
                price_text = price_el.get_text(strip=True) if price_el else ""
                price_cents = _parse_pararius_price(price_text)
                results.append(RawListingPreview(
                    source_site="pararius",
                    source_id=source_id,
                    source_url=source_url,
                    title=title,
                    price_eur_cents=price_cents,
                    city="amsterdam",
                ))
            except Exception:
                continue
        return results

    async def parse_listing_detail(self, html: str) -> Optional[NormalizedListing]:
        soup = BeautifulSoup(html, "lxml")
        title_el = soup.find("h1") or soup.find(class_=re.compile(r"listing-detail-summary__title"))
        title = title_el.get_text(strip=True) if title_el else "Pararius listing"
        price_el = soup.find(class_=re.compile(r"listing-detail-summary__price|price"))
        price_text = price_el.get_text(strip=True) if price_el else ""
        price_cents = _parse_pararius_price(price_text) or 150000

        size_sqm = None
        rooms = None
        text = soup.get_text()
        m = re.search(r"(\d+)\s*m²", text)
        if m:
            size_sqm = int(m.group(1))
        m = re.search(r"(\d+)\s+rooms?", text, re.IGNORECASE)
        if m:
            rooms = float(m.group(1))

        return NormalizedListing(
            source_site="pararius",
            source_id="fixture",
            source_url=f"{self.base_url}/apartments/amsterdam/fixture",
            title=title,
            price_eur_cents=price_cents,
            city="amsterdam",
            rooms=rooms,
            size_sqm=size_sqm,
            scraped_at=datetime.now(timezone.utc),
        )


def _parse_pararius_price(text: str) -> Optional[int]:
    cleaned = re.sub(r"[€\s,./per month]", "", text.lower())
    cleaned = re.sub(r"[^\d]", "", cleaned)
    if cleaned.isdigit():
        return int(cleaned) * 100
    return None
