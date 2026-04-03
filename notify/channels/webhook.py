"""Webhook channel: POSTs the notification as JSON to the recipient URL."""

import httpx

from notify.channels.base import ChannelSender, DeliveryError, Outbox
from notify.models import ChannelName, Message

EVENT_HEADER = "X-Kestrel-Event"


class WebhookChannel(ChannelSender):
    name = ChannelName.WEBHOOK

    def __init__(self, outbox: Outbox, timeout: float = 5.0) -> None:
        super().__init__(outbox)
        self._timeout = timeout

    async def send(self, message: Message) -> None:
        if not message.recipient.startswith(("http://", "https://")):
            raise DeliveryError("webhook recipient must be an http(s) URL", retryable=False)
        payload = {
            "notification_id": message.notification_id,
            "shipment_reference": message.shipment_reference,
            "event": message.event.value,
            "subject": message.subject,
            "body": message.body,
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    message.recipient, json=payload, headers={EVENT_HEADER: message.event.value}
                )
        except httpx.HTTPError as exc:
            raise DeliveryError(f"webhook transport error: {type(exc).__name__}") from exc
        code = response.status_code
        if code >= 500 or code == 429:
            raise DeliveryError(f"webhook returned {code}")
        if code >= 400:
            raise DeliveryError(f"webhook rejected with {code}", retryable=False)
        self._outbox.record(message)
