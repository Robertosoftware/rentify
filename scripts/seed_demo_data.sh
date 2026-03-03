#!/usr/bin/env bash
# Seed demo listings and matches into the local dev database.
# Requires the demo user to exist first — run create_demo_user.sh if needed.
# Usage: bash scripts/seed_demo_data.sh
set -euo pipefail

DB_URL="${DATABASE_URL_SYNC:-postgresql://postgres:password@localhost:5432/rentify}"

echo "==> Seeding demo listings..."
psql "$DB_URL" <<'SQL'
INSERT INTO listings (
    id, source_site, source_id, source_url, title, description,
    price_eur, price_type, rooms, size_sqm, city, country_code,
    first_seen_at, last_seen_at, created_at
) VALUES
(
    gen_random_uuid(), 'funda', 'demo-001',
    'https://www.funda.nl/huur/amsterdam/demo-001',
    'Spacious 3-room apartment in De Pijp',
    'Light-filled apartment with open kitchen, balcony, and storage room.',
    150000, 'per_month', 3, 85, 'amsterdam', 'NL',
    now(), now(), now()
),
(
    gen_random_uuid(), 'pararius', 'demo-002',
    'https://www.pararius.com/apartments/amsterdam/demo-002',
    'Modern studio in the Jordaan',
    'Fully furnished studio near Westerkerk. Perfect for expats.',
    110000, 'per_month', 1, 42, 'amsterdam', 'NL',
    now(), now(), now()
),
(
    gen_random_uuid(), 'kamernet', 'demo-003',
    'https://kamernet.nl/huren/amsterdam/demo-003',
    'Bright 2-room flat near Vondelpark',
    'Unfurnished apartment with hardwood floors and large windows.',
    130000, 'per_month', 2, 65, 'amsterdam', 'NL',
    now(), now(), now()
),
(
    gen_random_uuid(), 'huurwoningen', 'demo-004',
    'https://www.huurwoningen.nl/in/rotterdam/demo-004',
    'Family house in Rotterdam Zuid',
    '4-room family home with garden and garage.',
    180000, 'per_month', 4, 120, 'rotterdam', 'NL',
    now(), now(), now()
),
(
    gen_random_uuid(), 'funda', 'demo-005',
    'https://www.funda.nl/huur/utrecht/demo-005',
    'Cozy apartment near Utrecht Centraal',
    'Recently renovated, pet-friendly, with bicycle storage.',
    105000, 'per_month', 2, 58, 'utrecht', 'NL',
    now(), now(), now()
)
ON CONFLICT (source_site, source_id) DO NOTHING;
SQL

echo "==> Demo listings inserted (or already present)."
echo "    Run 'cd backend && uv run python scripts/create_demo_user.py' to create the demo user."
