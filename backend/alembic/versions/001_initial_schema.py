"""Initial schema — all 6 tables + indexes.

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("auth_provider", sa.String(20), nullable=False, server_default="email"),
        sa.Column("google_id", sa.String(255), nullable=True),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("subscription_status", sa.String(20), nullable=False, server_default="none"),
        sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("telegram_chat_id", sa.String(255), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("gdpr_consent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("google_id"),
        sa.UniqueConstraint("stripe_customer_id"),
    )
    op.create_index("idx_users_email", "users", ["email"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_users_google_id", "users", ["google_id"], postgresql_where=sa.text("google_id IS NOT NULL"))
    op.create_index(
        "idx_users_stripe_customer_id",
        "users",
        ["stripe_customer_id"],
        postgresql_where=sa.text("stripe_customer_id IS NOT NULL"),
    )

    # --------------------------------------------------------------- listings
    op.create_table(
        "listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_site", sa.String(100), nullable=False),
        sa.Column("source_id", sa.String(255), nullable=False),
        sa.Column("source_url", sa.String(2048), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price_eur", sa.Integer(), nullable=False),
        sa.Column("price_type", sa.String(20), nullable=False, server_default="per_month"),
        sa.Column("rooms", sa.Float(), nullable=True),
        sa.Column("bedrooms", sa.Integer(), nullable=True),
        sa.Column("bathrooms", sa.Integer(), nullable=True),
        sa.Column("size_sqm", sa.Integer(), nullable=True),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("neighborhood", sa.String(200), nullable=True),
        sa.Column("postal_code", sa.String(10), nullable=True),
        sa.Column("country_code", sa.String(2), nullable=False, server_default="NL"),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("pet_friendly", sa.Boolean(), nullable=True),
        sa.Column("furnished", sa.Boolean(), nullable=True),
        sa.Column("energy_label", sa.String(5), nullable=True),
        sa.Column("available_from", sa.Date(), nullable=True),
        sa.Column("rental_agent", sa.String(255), nullable=True),
        sa.Column("image_urls", postgresql.JSON(), nullable=True),
        sa.Column("raw_data", postgresql.JSON(), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delisted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_site", "source_id", name="uq_listing_source"),
    )
    op.create_index("idx_listings_source", "listings", ["source_site", "source_id"])
    op.create_index("idx_listings_city_price", "listings", ["city", "price_eur"])

    # ------------------------------------------------------------- preferences
    op.create_table(
        "preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("country_code", sa.String(2), nullable=False, server_default="NL"),
        sa.Column("min_price", sa.Integer(), nullable=True),
        sa.Column("max_price", sa.Integer(), nullable=False),
        sa.Column("min_rooms", sa.Float(), nullable=True),
        sa.Column("max_rooms", sa.Float(), nullable=True),
        sa.Column("min_size_sqm", sa.Integer(), nullable=True),
        sa.Column("max_size_sqm", sa.Integer(), nullable=True),
        sa.Column("pet_friendly", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("furnished", sa.Boolean(), nullable=True),
        sa.Column("keywords", postgresql.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_preferences_user_active", "preferences", ["user_id"], postgresql_where=sa.text("is_active = true")
    )

    # ----------------------------------------------------------------- matches
    op.create_table(
        "matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("preference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("notified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("notified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notification_channel", sa.String(20), nullable=False, server_default="none"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"]),
        sa.ForeignKeyConstraint(["preference_id"], ["preferences.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "listing_id", name="uq_match_user_listing"),
    )
    op.create_index(
        "idx_matches_user_notified", "matches", ["user_id", "notified"], postgresql_where=sa.text("notified = false")
    )

    # ----------------------------------------------------------- notifications
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("match_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("type", sa.String(40), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("payload", postgresql.JSON(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # ----------------------------------------------------------- feature_flags
    op.create_table(
        "feature_flags",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # --------------------------------------------------- default feature flags
    op.execute(
        """
        INSERT INTO feature_flags (id, name, enabled, description, created_at, updated_at)
        VALUES
          (gen_random_uuid(), 'paid_gate_enabled', false,
           'Gate premium features behind active subscription', now(), now()),
          (gen_random_uuid(), 'scraping_enabled', false,
           'Enable scraper workers to run', now(), now()),
          (gen_random_uuid(), 'telegram_notifications_enabled', false,
           'Enable Telegram notification delivery', now(), now()),
          (gen_random_uuid(), 'email_notifications_enabled', false,
           'Enable email notification delivery', now(), now())
        """
    )


def downgrade() -> None:
    op.drop_table("feature_flags")
    op.drop_table("notifications")
    op.drop_index("idx_matches_user_notified", table_name="matches")
    op.drop_table("matches")
    op.drop_index("idx_preferences_user_active", table_name="preferences")
    op.drop_table("preferences")
    op.drop_index("idx_listings_city_price", table_name="listings")
    op.drop_index("idx_listings_source", table_name="listings")
    op.drop_table("listings")
    op.drop_index("idx_users_stripe_customer_id", table_name="users")
    op.drop_index("idx_users_google_id", table_name="users")
    op.drop_index("idx_users_email", table_name="users")
    op.drop_table("users")
