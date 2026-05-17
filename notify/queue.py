"""In-memory job queue with retry and dead-letter handling."""

import asyncio
import random
from collections import deque
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

MAX_RETRIES = 3  # see OPS-61
BASE_DELAY_SECONDS = 0.5
MAX_DELAY_SECONDS = 30.0


class JobState(StrEnum):
    PENDING = "pending"
    DONE = "done"
    DEAD = "dead"


@dataclass
class Job:
    notification_id: str
    payload: Any = None
    attempts: int = 0
    last_error: str | None = None
    state: JobState = JobState.PENDING


Handler = Callable[[Job], Awaitable[None]]


class JobQueue:
    """FIFO queue. A handler that raises is retried, then the job is dead-lettered.

    An exception carrying `retryable = False` skips retries.
    """

    def __init__(
        self,
        handler: Handler,
        *,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        jitter: Callable[[], float] = random.random,
        base_delay: float = BASE_DELAY_SECONDS,
    ) -> None:
        self._handler = handler
        self._sleep = sleep
        self._jitter = jitter
        self._base_delay = base_delay
        self._pending: deque[Job] = deque()
        self._dead: list[Job] = []

    @property
    def pending(self) -> int:
        return len(self._pending)

    @property
    def dead_letter(self) -> list[Job]:
        return list(self._dead)

    def put(self, job: Job) -> None:
        self._pending.append(job)

    def backoff_delay(self, retry_number: int) -> float:
        """Exponential delay for the nth retry, scaled by a jitter factor in [0.5, 1.5)."""
        raw = self._base_delay * (2 ** (retry_number - 1)) * (0.5 + self._jitter())
        return min(raw, MAX_DELAY_SECONDS)

    async def run_one(self) -> Job | None:
        """Take the next job and run it to completion or dead-letter. None if empty."""
        if not self._pending:
            return None
        job = self._pending.popleft()
        while True:
            job.attempts += 1
            try:
                await self._handler(job)
            except Exception as exc:  # noqa: BLE001 - any handler failure is retried
                job.last_error = str(exc) or type(exc).__name__
                retries_used = job.attempts - 1
                if not getattr(exc, "retryable", True) or retries_used >= MAX_RETRIES:
                    job.state = JobState.DEAD
                    self._dead.append(job)
                    return job
                await self._sleep(self.backoff_delay(retries_used + 1))
            else:
                job.state = JobState.DONE
                job.last_error = None
                return job

    async def drain(self) -> list[Job]:
        """Run every pending job; return the finished jobs in order."""
        finished: list[Job] = []
        while (job := await self.run_one()) is not None:
            finished.append(job)
        return finished
