import pytest

from notify.ratelimit import RateLimitExceededError, RecipientRateLimiter


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_allows_up_to_capacity_then_blocks():
    limiter = RecipientRateLimiter(3, Clock())
    for _ in range(3):
        limiter.check("a@b.co")
    with pytest.raises(RateLimitExceededError, match="notification rate exceeded"):
        limiter.check("a@b.co")


def test_buckets_are_per_recipient_and_case_insensitive():
    limiter = RecipientRateLimiter(1, Clock())
    limiter.check("a@b.co")
    limiter.check("other@b.co")
    with pytest.raises(RateLimitExceededError):
        limiter.check("A@B.co ")


def test_refills_over_time():
    clock = Clock()
    limiter = RecipientRateLimiter(60, clock)  # one token per second
    for _ in range(60):
        limiter.check("a@b.co")
    with pytest.raises(RateLimitExceededError):
        limiter.check("a@b.co")
    clock.now += 2
    limiter.check("a@b.co")
    limiter.check("a@b.co")
    with pytest.raises(RateLimitExceededError):
        limiter.check("a@b.co")


def test_zero_disables_limiting():
    limiter = RecipientRateLimiter(0, Clock())
    for _ in range(500):
        limiter.check("a@b.co")
