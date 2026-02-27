from pathlib import Path
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.asyncio
async def test_huurwoningen_parse_search_results():
    from scrapers.src.scrapers.huurwoningen import HuurwoningenScraper
    html = (FIXTURES / "huurwoningen_search_results.html").read_text()
    scraper = HuurwoningenScraper()
    results = await scraper.parse_search_results(html)
    assert len(results) >= 1
    assert all(r.source_site == "huurwoningen" for r in results)
