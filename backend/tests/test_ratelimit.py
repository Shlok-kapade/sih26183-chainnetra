import asyncio

import pytest

from app.ingest.ratelimit import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_basic():
    limiter = RateLimiter(rate=10.0, capacity=2)
    # Should be able to acquire 2 tokens immediately
    await limiter.acquire()
    await limiter.acquire()
    # The limiter tokens should be exhausted now
    assert limiter.tokens < 1.0

@pytest.mark.asyncio
async def test_rate_limiter_refill():
    limiter = RateLimiter(rate=100.0, capacity=5)  # Fast refill for test
    # Drain tokens
    for _ in range(5):
        await limiter.acquire()
    # Wait a bit for refill
    await asyncio.sleep(0.1)
    # Should be able to acquire again
    await limiter.acquire()
