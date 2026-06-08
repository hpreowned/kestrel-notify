"""Notification service: validate, rate limit, enqueue, deliver, track status."""

import asyncio
import random
import time
from collections.abc import Awaitable, Callable

from notify.channels import ChannelSender, Outbox, build_senders
from notify.models import (
    CarrierCode,
    ChannelName,
    Message,
    Notification,
    NotificationRequest,
    Status,
)
from notify.queue import Job, JobQueue, JobState
from notify.ratelimit import RecipientRateLimiter
from notify.settings import Settings
from notify.templates import render


class ChannelDisabledError(Exception):
    """Raised when a request targets a channel switched off by feature flag."""

    def __init__(self, channel: ChannelName) -> None:
        super().__init__(f"channel disabled: {channel.value}")


class NotificationService:
    def __init__(
        self,
        settings: Settings,
        *,
        outbox: Outbox | None = None,
        senders: dict[ChannelName, ChannelSender] | None = None,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        jitter: Callable[[], float] = random.random,
        base_delay: float = 0.5,
    ) -> None:
        self._settings = settings
        self.outbox = outbox or Outbox()
        self._senders = senders or build_senders(self.outbox)
        self._limiter = RecipientRateLimiter(settings.rate_limit_per_minute, clock)
        self._store: dict[str, Notification] = {}
        self.queue = JobQueue(self._deliver, sleep=sleep, jitter=jitter, base_delay=base_delay)

    def submit(
        self, request: NotificationRequest, carrier_code: CarrierCode | None = None
    ) -> Notification:
        """Validate and enqueue a notification. Raises ChannelDisabledError or
        RateLimitExceededError; nothing is stored in either case."""
        if request.channel is ChannelName.SMS and not self._settings.feature_sms:
            raise ChannelDisabledError(request.channel)
        self._limiter.check(request.recipient)
        notification = Notification(
            shipment_reference=request.shipment_reference,
            recipient=request.recipient,
            channel=request.channel,
            event=request.event,
            carrier_code=carrier_code,
        )
        self._store[notification.id] = notification
        self.queue.put(Job(notification_id=notification.id))
        return notification

    def get(self, notification_id: str) -> Notification | None:
        return self._store.get(notification_id)

    async def process_pending(self) -> int:
        """Deliver everything currently queued; returns the number of jobs finished."""
        finished = await self.queue.drain()
        for job in finished:
            self._sync(job)
        return len(finished)

    async def _deliver(self, job: Job) -> None:
        notification = self._store[job.notification_id]
        rendered = render(notification.event, notification.shipment_reference, notification.carrier_code)
        message = Message(
            notification_id=notification.id,
            channel=notification.channel,
            recipient=notification.recipient,
            event=notification.event,
            shipment_reference=notification.shipment_reference,
            subject=rendered.subject,
            body=rendered.body,
        )
        await self._senders[notification.channel].send(message)

    def _sync(self, job: Job) -> None:
        notification = self._store[job.notification_id]
        notification.attempts = job.attempts
        notification.last_error = job.last_error
        notification.status = Status.SENT if job.state is JobState.DONE else Status.DEAD_LETTERED
