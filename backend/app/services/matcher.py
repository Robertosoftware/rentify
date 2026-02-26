from app.models.listing import Listing
from app.models.preference import Preference

WEIGHTS = {"city": 0.3, "price": 0.3, "rooms": 0.15, "size": 0.15, "extras": 0.1}
MATCH_THRESHOLD = 0.5


def score_listing(listing: Listing, pref: Preference) -> float:
    score = 0.0

    if listing.city.lower() == pref.city.lower():
        score += WEIGHTS["city"]

    if pref.min_price is None or listing.price_eur >= pref.min_price:
        if listing.price_eur <= pref.max_price:
            score += WEIGHTS["price"]

    if pref.min_rooms and pref.max_rooms:
        if listing.rooms and pref.min_rooms <= listing.rooms <= pref.max_rooms:
            score += WEIGHTS["rooms"]
    elif listing.rooms:
        score += WEIGHTS["rooms"]

    if pref.min_size_sqm and pref.max_size_sqm:
        if listing.size_sqm and pref.min_size_sqm <= listing.size_sqm <= pref.max_size_sqm:
            score += WEIGHTS["size"]
    elif listing.size_sqm:
        score += WEIGHTS["size"]

    extras_score = 0.0
    extras_count = 0
    if pref.pet_friendly and listing.pet_friendly is not None:
        extras_count += 1
        if listing.pet_friendly:
            extras_score += 1
    if pref.furnished is not None and listing.furnished is not None:
        extras_count += 1
        if listing.furnished == pref.furnished:
            extras_score += 1
    if extras_count > 0:
        score += WEIGHTS["extras"] * (extras_score / extras_count)

    return round(score, 3)
