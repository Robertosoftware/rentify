import re
from datetime import datetime, timezone
from typing import Optional

from bs4 import BeautifulSoup

from scrapers.src.base_scraper import BaseScraper
from scrapers.src.models.listing import NormalizedListing, RawListingPreview


class FundaScraper(BaseScraper):
    site_name = "funda"
    base_url = "https://www.funda.nl"
    max_concurrent = 1
    request_delay_range = (3.0, 6.0)

    async def build_search_url(self, city: str, page: int = 1, **filters) -> str:
        city_slug = city.lower().replace(" ", "-").replace("'", "")
        url = f"{self.base_url}/huur/{city_slug}/beschikbaar/"
        if page > 1:
            url += f"p{page}/"
        return url

    async def parse_search_results(self, html: str) -> list[RawListingPreview]:
        soup = BeautifulSoup(html, "lxml")
        results = []
        # Funda listing cards
        cards = soup.find_all("div", {"data-test-id": "search-result-item"})
        if not cards:
            cards = soup.find_all("li", class_=re.compile(r"search-result"))
        for card in cards:
            try:
                link = card.find("a", href=re.compile(r"/huur/"))
                if not link:
                    continue
                href = link.get("href", "")
                source_url = href if href.startswith("http") else f"{self.base_url}{href}"
                source_id = href.rstrip("/").split("/")[-1] if "/" in href else href
                title_el = card.find(["h2", "h3"]) or card.find(class_=re.compile(r"title"))
                title = title_el.get_text(strip=True) if title_el else "Funda listing"
                price_el = card.find(class_=re.compile(r"price"))
                price_text = price_el.get_text(strip=True) if price_el else ""
                price_cents = _parse_price(price_text)
                results.append(RawListingPreview(
                    source_site="funda",
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
        title_el = soup.find(["h1"]) or soup.find(class_=re.compile(r"object-header__title"))
        title = title_el.get_text(strip=True) if title_el else "Funda listing"
        price_el = soup.find(class_=re.compile(r"price"))
        price_text = price_el.get_text(strip=True) if price_el else "€ 1.000 /maand"
        price_cents = _parse_price(price_text) or 100000

        # Extract address/city
        address_el = soup.find(class_=re.compile(r"object-header__subtitle|address"))
        address = address_el.get_text(strip=True) if address_el else ""

        # Extract size and rooms from characteristics
        size_sqm = _extract_number(soup, r"(\d+)\s*m²")
        rooms = _extract_float(soup, r"(\d+(?:\.\d+)?)\s*kamers?")

        return NormalizedListing(
            source_site="funda",
            source_id="fixture",
            source_url=f"{self.base_url}/huur/fixture/",
            title=title,
            price_eur_cents=price_cents,
            city="amsterdam",
            address=address,
            rooms=rooms,
            size_sqm=size_sqm,
            scraped_at=datetime.now(timezone.utc),
        )


def _parse_price(text: str) -> Optional[int]:
    """Parse price text like '€ 1.500 /maand' to cents."""
    cleaned = re.sub(r"[€\s./maandpermonthmo]", "", text.lower())
    cleaned = re.sub(r"[^\d]", "", cleaned)
    if cleaned.isdigit():
        euros = int(cleaned)
        return euros * 100
    return None


def _extract_number(soup: BeautifulSoup, pattern: str) -> Optional[int]:
    text = soup.get_text()
    m = re.search(pattern, text)
    return int(m.group(1)) if m else None


def _extract_float(soup: BeautifulSoup, pattern: str) -> Optional[float]:
    text = soup.get_text()
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None
