import urllib.robotparser
import logging

log = logging.getLogger(__name__)


def can_fetch(base_url: str, path: str = "/", user_agent: str = "*") -> bool:
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{base_url}/robots.txt")
    try:
        rp.read()
        return rp.can_fetch(user_agent, f"{base_url}{path}")
    except Exception as e:
        log.warning(f"Could not fetch robots.txt for {base_url}: {e}")
        return True  # Default to allowing
