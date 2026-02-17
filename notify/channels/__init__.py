"""Delivery channels."""

from notify.channels.base import ChannelSender, DeliveryError, Outbox, OutboxEntry
from notify.channels.email import EmailChannel
from notify.channels.sms import SmsChannel
from notify.channels.webhook import WebhookChannel
from notify.models import ChannelName


def build_senders(outbox: Outbox) -> dict[ChannelName, ChannelSender]:
    """Create one sender per channel, all recording to the same outbox."""
    senders: list[ChannelSender] = [
        EmailChannel(outbox),
        SmsChannel(outbox),
        WebhookChannel(outbox),
    ]
    return {sender.name: sender for sender in senders}


__all__ = [
    "ChannelSender",
    "DeliveryError",
    "EmailChannel",
    "Outbox",
    "OutboxEntry",
    "SmsChannel",
    "WebhookChannel",
    "build_senders",
]
