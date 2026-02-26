import structlog

from app.config import get_settings

settings = get_settings()
log = structlog.get_logger()


async def send_telegram_message(chat_id: str, text: str) -> bool:
    if settings.MOCK_TELEGRAM:
        log.info("telegram.mock_send", chat_id=chat_id, text=text)
        return True

    import httpx

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
        if resp.status_code != 200:
            log.error("telegram.send_failed", chat_id=chat_id, status=resp.status_code)
            return False
        return True
