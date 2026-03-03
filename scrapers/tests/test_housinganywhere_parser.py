from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.asyncio
async def test_housinganywhere_parse_search_results():
    from scrapers.src.scrapers.housinganywhere import HousingAnywhereScraper

    html = (FIXTURES / "housinganywhere_search_results.html").read_text()
    scraper = HousingAnywhereScraper()
    results = await scraper.parse_search_results(html)
    assert len(results) >= 1
    assert all(r.source_site == "housinganywhere" for r in results)
    assert all(r.source_url.startswith("http") for r in results)
    assert all(r.source_id for r in results)


@pytest.mark.asyncio
async def test_housinganywhere_parse_search_results_price():
    from scrapers.src.scrapers.housinganywhere import HousingAnywhereScraper

    html = (FIXTURES / "housinganywhere_search_results.html").read_text()
    scraper = HousingAnywhereScraper()
    results = await scraper.parse_search_results(html)
    prices = [r.price_eur_cents for r in results if r.price_eur_cents]
    assert len(prices) >= 1
    assert all(p > 0 for p in prices)


@pytest.mark.asyncio
async def test_housinganywhere_parse_listing_detail():
    from scrapers.src.scrapers.housinganywhere import HousingAnywhereScraper

    html = (FIXTURES / "housinganywhere_search_results.html").read_text()
    scraper = HousingAnywhereScraper()
    listing = await scraper.parse_listing_detail(html)
    assert listing is not None
    assert listing.source_site == "housinganywhere"
    assert listing.price_eur_cents > 0


@pytest.mark.asyncio
async def test_housinganywhere_build_search_url():
    from scrapers.src.scrapers.housinganywhere import HousingAnywhereScraper

    scraper = HousingAnywhereScraper()
    url = await scraper.build_search_url("amsterdam")
    assert "amsterdam" in url.lower() or "Amsterdam" in url
    assert url.startswith("https://housinganywhere.com")
