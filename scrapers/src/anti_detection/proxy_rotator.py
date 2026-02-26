import itertools
import os
from typing import Optional


class ProxyRotator:
    def __init__(self) -> None:
        self._proxies: list[str] = []
        self._failures: dict[str, int] = {}
        self._cycle = None
        self._load_proxies()

    def _load_proxies(self) -> None:
        proxy_list = os.getenv("PROXY_LIST", "")
        if proxy_list:
            self._proxies = [p.strip() for p in proxy_list.split(",") if p.strip()]
        pool_url = os.getenv("PROXY_POOL_URL", "")
        if pool_url:
            # In production, fetch from pool URL; for now just note it
            pass
        if self._proxies:
            self._cycle = itertools.cycle(self._proxies)

    def get_proxy(self) -> Optional[str]:
        if not self._cycle:
            return None
        return next(self._cycle)

    def record_failure(self, proxy: str) -> None:
        self._failures[proxy] = self._failures.get(proxy, 0) + 1
        if self._failures[proxy] >= 3:
            self._proxies = [p for p in self._proxies if p != proxy]
            self._cycle = itertools.cycle(self._proxies) if self._proxies else None
