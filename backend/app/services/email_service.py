import structlog

from app.config import get_settings

settings = get_settings()
log = structlog.get_logger()


async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    if settings.MOCK_EMAIL:
        log.info("email.mock_send", to=to_email, subject=subject, content_preview=html_content[:200])
        return True

    import httpx

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": settings.SENDGRID_FROM_EMAIL},
                "subject": subject,
                "content": [{"type": "text/html", "value": html_content}],
            },
        )
        if resp.status_code not in (200, 202):
            log.error("email.send_failed", to=to_email, status=resp.status_code)
            return False
        return True
