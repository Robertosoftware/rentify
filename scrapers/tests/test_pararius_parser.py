from pathlib import Path
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.asyncio
async def test_pararius_parse_search_results():
    from scrapers.src.scrapers.pararius import ParariusScraper
    html = (FIXTURES / "pararius_search_results.html").read_text()
    scraper = ParariusScraper()
    results = await scraper.parse_search_results(html)
    assert len(results) >= 1
    assert all(r.source_site == "pararius" for r in results)


@pytest.mark.asyncio
async def test_pararius_parse_listing_detail():
    from scrapers.src.scrapers.pararius import ParariusScraper
    html = (FIXTURES / "pararius_listing_page.html").read_text()
    scraper = ParariusScraper()
    listing = await scraper.parse_listing_detail(html)
    assert listing is not None
    assert listing.price_eur_cents > 0
