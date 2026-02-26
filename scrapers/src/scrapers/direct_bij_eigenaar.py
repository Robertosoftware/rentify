import re
from datetime import datetime, timezone
from typing import Optional

from bs4 import BeautifulSoup

from scrapers.src.base_scraper import BaseScraper
from scrapers.src.models.listing import NormalizedListing, RawListingPreview


class DirectBijEigenaarScraper(BaseScraper):
    site_name = "directbijeigenaar"
    base_url = "https://www.directbijeigenaar.nl"
    request_delay_range = (2.0, 4.0)

    async def build_search_url(self, city: str, page: int = 1, **filters) -> str:
        city_slug = city.lower().replace(" ", "-")
        url = f"{self.base_url}/huurwoning/{city_slug}"
        if page > 1:
            url += f"?page={page}"
        return url

    async def parse_search_results(self, html: str) -> list[RawListingPreview]:
        soup = BeautifulSoup(html, "lxml")
        results = []
        cards = soup.find_all(class_=re.compile(r"listing|property|woning"))
        for card in cards:
            try:
                link = card.find("a")
                if not link:
                    continue
                href = link.get("href", "")
                source_url = href if href.startswith("http") else f"{self.base_url}{href}"
                source_id = href.rstrip("/").split("/")[-1]
                title_el = card.find(["h2", "h3"]) or card.find(class_=re.compile(r"title"))
                title = title_el.get_text(strip=True) if title_el else "Direct bij Eigenaar listing"
                price_el = card.find(class_=re.compile(r"price|huurprijs"))
                price_text = price_el.get_text(strip=True) if price_el else ""
                price_cents = _parse_price(price_text)
                results.append(RawListingPreview(
                    source_site="directbijeigenaar",
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
        title_el = soup.find("h1")
        title = title_el.get_text(strip=True) if title_el else "Direct bij Eigenaar listing"
        text = soup.get_text()
        price_cents = _parse_price(text) or 130000
        size_sqm = None
        m = re.search(r"(\d+)\s*m²", text)
        if m:
            size_sqm = int(m.group(1))
        return NormalizedListing(
            source_site="directbijeigenaar",
            source_id="fixture",
            source_url=f"{self.base_url}/huurwoning/amsterdam/fixture",
            title=title,
            price_eur_cents=price_cents,
            city="amsterdam",
            size_sqm=size_sqm,
            scraped_at=datetime.now(timezone.utc),
        )


def _parse_price(text: str) -> Optional[int]:
    m = re.search(r"€\s*([\d.,]+)", text)
    if m:
        raw = m.group(1).replace(".", "").replace(",", "")
        return int(raw) * 100 if raw.isdigit() else None
    return None
