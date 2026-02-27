from pathlib import Path
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.asyncio
async def test_kamernet_parse_search_results():
    from scrapers.src.scrapers.kamernet import KamernetScraper
    html = (FIXTURES / "kamernet_search_results.html").read_text()
    scraper = KamernetScraper()
    results = await scraper.parse_search_results(html)
    assert len(results) >= 1
    assert all(r.source_site == "kamernet" for r in results)
