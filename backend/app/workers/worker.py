import structlog

import dramatiq
from dramatiq.brokers.redis import RedisBroker

from app.config import get_settings

settings = get_settings()
log = structlog.get_logger()

broker = RedisBroker(url=settings.REDIS_URL)
dramatiq.set_broker(broker)

# Import tasks to register them
from app.workers import tasks  # noqa: F401, E402
