"""Wire and domain models. All JSON on the wire is snake_case."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ChannelName(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"


class Event(StrEnum):
    CREATED = "CREATED"
    RESERVED = "RESERVED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"


class CarrierCode(StrEnum):
    NSL = "NSL"  # NorthStar Lines
    BLX = "BLX"  # Baltic Express
    PCR = "PCR"  # Pacific Reach


class Status(StrEnum):
    QUEUED = "QUEUED"
    SENT = "SENT"
    DEAD_LETTERED = "DEAD_LETTERED"


def new_notification_id() -> str:
    return f"ntf_{uuid.uuid4().hex[:12]}"


class NotificationRequest(BaseModel):
    """Body of POST /v1/notifications."""

    model_config = ConfigDict(extra="forbid")

    shipment_reference: str = Field(min_length=1, max_length=64)
    recipient: str = Field(min_length=3, max_length=320)
    channel: ChannelName
    event: Event


class Notification(BaseModel):
    """A queued or delivered notification, as returned by the API."""

    id: str = Field(default_factory=new_notification_id)
    shipment_reference: str
    recipient: str
    channel: ChannelName
    event: Event
    carrier_code: CarrierCode | None = None
    status: Status = Status.QUEUED
    attempts: int = 0
    last_error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BookingEvent(BaseModel):
    """Event pushed by the booking service to POST /v1/webhooks/booking."""

    event: Event
    shipment_reference: str = Field(min_length=1, max_length=64)
    recipient: str = Field(min_length=3, max_length=320)
    channel: ChannelName = ChannelName.EMAIL
    carrier_code: CarrierCode | None = None


class WebhookAccepted(BaseModel):
    notification_id: str
    status: Status


@dataclass(frozen=True)
class Message:
    """A rendered message handed to a channel sender."""

    notification_id: str
    channel: ChannelName
    recipient: str
    event: Event
    shipment_reference: str
    subject: str
    body: str
