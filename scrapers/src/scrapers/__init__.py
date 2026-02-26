from scrapers.src.scrapers.funda import FundaScraper
from scrapers.src.scrapers.pararius import ParariusScraper
from scrapers.src.scrapers.kamernet import KamernetScraper
from scrapers.src.scrapers.huurwoningen import HuurwoningenScraper
from scrapers.src.scrapers.housinganywhere import HousingAnywhereScraper
from scrapers.src.scrapers.direct_bij_eigenaar import DirectBijEigenaarScraper

SCRAPER_REGISTRY: dict = {
    "funda": FundaScraper,
    "pararius": ParariusScraper,
    "kamernet": KamernetScraper,
    "huurwoningen": HuurwoningenScraper,
    "housinganywhere": HousingAnywhereScraper,
    "directbijeigenaar": DirectBijEigenaarScraper,
}
