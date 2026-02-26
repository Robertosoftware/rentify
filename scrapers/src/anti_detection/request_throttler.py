import asyncio
import random
import time
from collections import defaultdict

_circuit_breakers: dict[str, float] = {}  # domain -> disabled_until timestamp
_failure_counts: dict[str, int] = defaultdict(int)
_last_request: dict[str, float] = defaultdict(float)

CIRCUIT_BREAKER_THRESHOLD = 5
CIRCUIT_BREAKER_TIMEOUT = 1800  # 30 minutes


class RequestThrottler:
    def __init__(self, min_delay: float = 2.0, max_delay: float = 5.0) -> None:
        self.min_delay = min_delay
        self.max_delay = max_delay

    async def wait(self, domain: str) -> None:
        # Circuit breaker check
        disabled_until = _circuit_breakers.get(domain, 0)
        if time.time() < disabled_until:
            raise RuntimeError(f"Circuit breaker open for {domain}, disabled until {disabled_until}")

        # Adaptive delay
        elapsed = time.time() - _last_request[domain]
        required = random.uniform(self.min_delay, self.max_delay)
        if elapsed < required:
            await asyncio.sleep(required - elapsed)
        _last_request[domain] = time.time()

    def record_success(self, domain: str) -> None:
        _failure_counts[domain] = 0

    def record_failure(self, domain: str) -> None:
        _failure_counts[domain] += 1
        if _failure_counts[domain] >= CIRCUIT_BREAKER_THRESHOLD:
            _circuit_breakers[domain] = time.time() + CIRCUIT_BREAKER_TIMEOUT
            _failure_counts[domain] = 0
