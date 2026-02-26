import random
from scrapers.src.anti_detection.user_agents import ACCEPT_LANGUAGE_POOL, USER_AGENTS

_last_ua: dict[str, str] = {}  # domain -> last used UA


class AgentRotator:
    def __init__(self) -> None:
        self._agents = USER_AGENTS.copy()

    def get_user_agent(self, domain: str = "") -> str:
        candidates = [ua for ua in self._agents if ua != _last_ua.get(domain, "")]
        ua = random.choice(candidates) if candidates else random.choice(self._agents)
        _last_ua[domain] = ua
        return ua

    def get_headers(self, domain: str = "") -> dict:
        ua = self.get_user_agent(domain)
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": random.choice(ACCEPT_LANGUAGE_POOL),
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
        }
        # Occasionally add Referer
        if random.random() < 0.3:
            headers["Referer"] = "https://www.google.com/"
        # Occasionally add Connection header
        if random.random() < 0.5:
            headers["Connection"] = "keep-alive"
        return headers
