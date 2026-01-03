"""Per-recipient token bucket rate limiting."""

import time
from collections.abc import Callable
from dataclasses import dataclass


class RateLimitExceededError(Exception):
    """Raised when a recipient has no tokens left."""

    def __init__(self) -> None:
        super().__init__("notification rate exceeded")


@dataclass
class TokenBucket:
    capacity: float
    refill_per_second: float
    tokens: float
    updated_at: float

    def take(self, now: float) -> bool:
        elapsed = max(0.0, now - self.updated_at)
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_second)
        self.updated_at = now
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False


class RecipientRateLimiter:
    """One bucket per recipient; capacity equals the per-minute limit.

    A limit of 0 disables limiting entirely.
    """

    def __init__(self, per_minute: int, clock: Callable[[], float] = time.monotonic) -> None:
        self._per_minute = per_minute
        self._clock = clock
        self._buckets: dict[str, TokenBucket] = {}

    @staticmethod
    def _key(recipient: str) -> str:
        return recipient.strip().lower()

    def check(self, recipient: str) -> None:
        """Consume one token for recipient or raise RateLimitExceededError."""
        if self._per_minute <= 0:
            return
        now = self._clock()
        key = self._key(recipient)
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = TokenBucket(
                capacity=float(self._per_minute),
                refill_per_second=self._per_minute / 60.0,
                tokens=float(self._per_minute),
                updated_at=now,
            )
            self._buckets[key] = bucket
        if not bucket.take(now):
            raise RateLimitExceededError
