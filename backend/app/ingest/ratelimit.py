import asyncio
import time
from typing import Dict

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter


class RateLimiter:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = float(capacity)
        self.tokens = self.capacity
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self.lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_update
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                self.last_update = now

                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return

                wait_time = (1.0 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)

_limiters: Dict[str, RateLimiter] = {}

def get_limiter(provider: str, rate: float = 5.0, capacity: int = 10) -> RateLimiter:
    if provider not in _limiters:
        _limiters[provider] = RateLimiter(rate, capacity)
    return _limiters[provider]

class RateLimitError(Exception):
    pass

def get_retry_policy() -> AsyncRetrying:
    return AsyncRetrying(
        retry=retry_if_exception_type((RateLimitError, httpx.RequestError)),
        wait=wait_exponential_jitter(initial=1, max=60, exp_base=2, jitter=1),
        stop=stop_after_attempt(5)
    )
