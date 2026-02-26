"""Scheduled reminder tasks — enqueued from Stripe webhook handler."""
from datetime import timedelta

import structlog

log = structlog.get_logger()


def schedule_trial_reminders(user_id: str) -> None:
    """Enqueue trial reminder tasks with delays."""
    from app.workers.tasks import send_trial_reminder

    # 48h reminder at day 5 (5 days * 24 * 60 * 60 * 1000 ms)
    send_trial_reminder.send_with_options(args=(user_id, "48h"), delay=5 * 24 * 60 * 60 * 1000)
    # 24h reminder at day 6
    send_trial_reminder.send_with_options(args=(user_id, "24h"), delay=6 * 24 * 60 * 60 * 1000)
    log.info("trial_reminders.scheduled", user_id=user_id)
