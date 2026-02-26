import uuid
from datetime import datetime, timezone

import pytest

from app.models.listing import Listing
from app.models.preference import Preference
from app.services.matcher import score_listing


def make_listing(**kwargs):
    defaults = dict(
        id=uuid.uuid4(),
        source_site="test",
        source_id="123",
        source_url="https://example.com",
        title="Test Listing",
        price_eur=150000,
        city="amsterdam",
        rooms=2.0,
        size_sqm=60,
        first_seen_at=datetime.now(timezone.utc),
        last_seen_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return Listing(**defaults)


def make_pref(**kwargs):
    defaults = dict(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        city="amsterdam",
        max_price=200000,
        min_price=50000,
        min_rooms=1.0,
        max_rooms=4.0,
        min_size_sqm=40,
        max_size_sqm=120,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return Preference(**defaults)


def test_exact_match_high_score():
    listing = make_listing(city="amsterdam", price_eur=150000, rooms=2.0, size_sqm=60)
    pref = make_pref(city="amsterdam", max_price=200000, min_price=100000, min_rooms=1.0, max_rooms=3.0, min_size_sqm=40, max_size_sqm=100)
    score = score_listing(listing, pref)
    assert score >= 0.8


def test_no_match_low_score():
    listing = make_listing(city="rotterdam")
    pref = make_pref(city="amsterdam")
    score = score_listing(listing, pref)
    assert score < 0.5


def test_partial_match():
    listing = make_listing(city="amsterdam", price_eur=150000, rooms=5.0, size_sqm=60)
    pref = make_pref(city="amsterdam", max_price=200000, min_rooms=1.0, max_rooms=3.0)
    score = score_listing(listing, pref)
    assert 0.5 <= score <= 0.8
