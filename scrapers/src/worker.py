#!/usr/bin/env python3
"""Main scraper worker loop."""
import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from scrapers.src.scrapers import SCRAPER_REGISTRY

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / "output"


async def run_scraper_fixture(scraper_name: str, city: str) -> list[dict]:
    """Run a scraper against its fixture file and return normalized listings."""
    fixtures_dir = Path(__file__).parent.parent / "tests" / "fixtures"
    fixture_file = fixtures_dir / f"{scraper_name}_search_results.html"

    if not fixture_file.exists():
        log.warning(f"No fixture found for {scraper_name}: {fixture_file}")
        return []

    fixture_html = fixture_file.read_text(encoding="utf-8")
    scraper_cls = SCRAPER_REGISTRY.get(scraper_name)
    if not scraper_cls:
        log.warning(f"Unknown scraper: {scraper_name}")
        return []

    scraper = scraper_cls()
    previews = await scraper.parse_search_results(fixture_html)
    log.info(f"{scraper_name}: parsed {len(previews)} previews from fixture")

    listings = []
    for preview in previews:
        detail = await scraper.parse_listing_detail(fixture_html)
        if detail:
            # Override with preview data where available
            listing_dict = detail.model_dump()
            listing_dict["source_id"] = preview.source_id
            listing_dict["source_url"] = preview.source_url
            listing_dict["title"] = preview.title
            if preview.price_eur_cents:
                listing_dict["price_eur_cents"] = preview.price_eur_cents
            listings.append(listing_dict)
    return listings


async def main(sources: list[str], cities: list[str], live: bool = False) -> None:
    log.info(f"Scraper worker starting | sources={sources} | cities={cities} | live={live}")
    all_results = {}

    for source in sources:
        if source not in SCRAPER_REGISTRY:
            log.warning(f"Unknown source: {source}")
            continue
        for city in cities:
            if live:
                scraper = SCRAPER_REGISTRY[source]()
                listings = await scraper.scrape_city(city, max_pages=1)
                listing_dicts = [l.model_dump() for l in listings]
            else:
                listing_dicts = await run_scraper_fixture(source, city)

            key = f"{source}:{city}"
            all_results[key] = listing_dicts
            log.info(f"{source}@{city}: {len(listing_dicts)} listings")

    # Write output
    OUTPUT_DIR.mkdir(exist_ok=True)
    out_file = OUTPUT_DIR / f"scrape_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out_file.write_text(json.dumps(all_results, indent=2, default=str))
    log.info(f"Output written to {out_file}")

    total = sum(len(v) for v in all_results.values())
    log.info(f"Scrape complete: {total} total listings across {len(all_results)} source/city pairs")
    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rentify scraper worker")
    parser.add_argument("--sources", default=os.getenv("SCRAPER_SOURCES", "funda,pararius"))
    parser.add_argument("--cities", default=os.getenv("SCRAPER_CITIES", "amsterdam"))
    parser.add_argument("--live", action="store_true", default=os.getenv("ENABLE_LIVE_SCRAPING", "false") == "true")
    args = parser.parse_args()

    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    cities = [c.strip() for c in args.cities.split(",") if c.strip()]
    asyncio.run(main(sources, cities, args.live))
