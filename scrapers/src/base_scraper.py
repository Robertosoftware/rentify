import asyncio
import logging
import random
import urllib.robotparser
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional

import aiohttp

from scrapers.src.anti_detection.agent_rotator import AgentRotator
from scrapers.src.anti_detection.request_throttler import RequestThrottler
from scrapers.src.models.listing import NormalizedListing, RawListingPreview

log = logging.getLogger(__name__)


class BaseScraper(ABC):
    site_name: str = ""
    base_url: str = ""
    max_concurrent: int = 2
    request_delay_range: tuple[float, float] = (2.0, 5.0)
    requires_javascript: bool = False

    def __init__(self) -> None:
        self.agent_rotator = AgentRotator()
        self.throttler = RequestThrottler(
            min_delay=self.request_delay_range[0],
            max_delay=self.request_delay_range[1],
        )
        self._semaphore = asyncio.Semaphore(self.max_concurrent)

    @abstractmethod
    async def build_search_url(self, city: str, page: int = 1, **filters) -> str: ...

    @abstractmethod
    async def parse_search_results(self, html: str) -> list[RawListingPreview]: ...

    @abstractmethod
    async def parse_listing_detail(self, html: str) -> Optional[NormalizedListing]: ...

    async def check_robots(self, path: str = "/") -> bool:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{self.base_url}/robots.txt")
        try:
            rp.read()
            return rp.can_fetch("*", f"{self.base_url}{path}")
        except Exception as e:
            log.warning("robots_check_failed", extra={"site": self.site_name, "error": str(e)})
            return True  # Default to allowing

    async def fetch_page(self, url: str, retries: int = 3) -> str:
        async with self._semaphore:
            headers = self.agent_rotator.get_headers()
            for attempt in range(retries):
                try:
                    await self.throttler.wait(self.site_name)
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                            if resp.status == 429:
                                wait = 30 * (2 ** attempt)
                                log.warning(f"Rate limited on {url}, waiting {wait}s")
                                await asyncio.sleep(wait)
                                headers = self.agent_rotator.get_headers()
                                continue
                            if resp.status == 403:
                                headers = self.agent_rotator.get_headers()
                                if attempt < retries - 1:
                                    continue
                            resp.raise_for_status()
                            return await resp.text()
                except aiohttp.ClientError as e:
                    if attempt == retries - 1:
                        raise
                    delay = 2 ** attempt
                    log.warning(f"Request failed (attempt {attempt+1}), retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
        return ""

    async def random_delay(self) -> None:
        delay = random.uniform(*self.request_delay_range)
        await asyncio.sleep(delay)

    async def scrape_city(self, city: str, max_pages: int = 5, fixture_html: str | None = None) -> list[NormalizedListing]:
        results: list[NormalizedListing] = []
        for page in range(1, max_pages + 1):
            url = await self.build_search_url(city, page)
            try:
                if fixture_html and page == 1:
                    html = fixture_html
                else:
                    html = await self.fetch_page(url)
                previews = await self.parse_search_results(html)
                if not previews:
                    break
                for preview in previews:
                    try:
                        if fixture_html:
                            detail_html = fixture_html
                        else:
                            await self.random_delay()
                            detail_html = await self.fetch_page(preview.source_url)
                        listing = await self.parse_listing_detail(detail_html)
                        if listing:
                            results.append(listing)
                    except Exception as e:
                        log.error(f"Failed to parse listing detail {preview.source_url}: {e}")
            except Exception as e:
                log.error(f"Failed to scrape page {page} of {city}: {e}")
                break
        log.info(f"{self.site_name}: scraped {len(results)} listings from {city}")
        return results
