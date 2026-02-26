# Import all models so SQLModel metadata is populated
from app.models.feature_flag import FeatureFlag
from app.models.listing import Listing
from app.models.match import Match
from app.models.notification import Notification
from app.models.preference import Preference
from app.models.user import User

__all__ = ["User", "Preference", "Listing", "Match", "Notification", "FeatureFlag"]
