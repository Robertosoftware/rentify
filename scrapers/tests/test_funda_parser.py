from pathlib import Path
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.asyncio
async def test_funda_parse_search_results():
    from scrapers.src.scrapers.funda import FundaScraper
    html = (FIXTURES / "funda_search_results.html").read_text()
    scraper = FundaScraper()
    results = await scraper.parse_search_results(html)
    assert len(results) >= 1
    assert all(r.source_site == "funda" for r in results)
    assert all(r.source_url for r in results)


@pytest.mark.asyncio
async def test_funda_parse_listing_detail():
    from scrapers.src.scrapers.funda import FundaScraper
    html = (FIXTURES / "funda_listing_page.html").read_text()
    scraper = FundaScraper()
    listing = await scraper.parse_listing_detail(html)
    assert listing is not None
    assert listing.source_site == "funda"
    assert listing.price_eur_cents > 0
