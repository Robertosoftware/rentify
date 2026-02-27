import pytest


def test_deduplicator_module_importable():
    from scrapers.src.deduplicator import upsert_listing, mark_delisted
    assert callable(upsert_listing)
    assert callable(mark_delisted)
