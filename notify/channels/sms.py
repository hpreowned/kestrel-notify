"""SMS channel (stub): validates the number, truncates to one segment, records."""

import re
from dataclasses import replace

from notify.channels.base import ChannelSender, DeliveryError
from notify.models import ChannelName, Message

_PHONE = re.compile(r"^\+?[0-9]{7,15}$")
SMS_MAX_CHARS = 160


class SmsChannel(ChannelSender):
    name = ChannelName.SMS

    async def send(self, message: Message) -> None:
        if not _PHONE.match(message.recipient):
            raise DeliveryError("invalid phone number", retryable=False)
        body = message.body
        if len(body) > SMS_MAX_CHARS:
            body = body[: SMS_MAX_CHARS - 1] + "…"
        self._outbox.record(replace(message, body=body))
