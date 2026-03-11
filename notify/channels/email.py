"""Email channel (stub): validates the address and records to the outbox."""

import re

from notify.channels.base import ChannelSender, DeliveryError
from notify.models import ChannelName, Message

_ADDRESS = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class EmailChannel(ChannelSender):
    name = ChannelName.EMAIL

    async def send(self, message: Message) -> None:
        if not _ADDRESS.match(message.recipient):
            raise DeliveryError("invalid email address", retryable=False)
        self._outbox.record(message)
