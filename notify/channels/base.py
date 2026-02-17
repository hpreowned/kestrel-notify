"""Channel interface, delivery error and the in-memory outbox."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime

from notify.models import ChannelName, Message


class DeliveryError(Exception):
    """A send failed. retryable=False sends the job straight to dead-letter."""

    def __init__(self, message: str, *, retryable: bool = True) -> None:
        super().__init__(message)
        self.retryable = retryable


@dataclass(frozen=True)
class OutboxEntry:
    notification_id: str
    channel: ChannelName
    recipient: str
    subject: str
    body: str
    sent_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class Outbox:
    """Records every successfully delivered message. Stand-in for real providers."""

    def __init__(self) -> None:
        self._entries: list[OutboxEntry] = []

    def record(self, message: Message) -> OutboxEntry:
        entry = OutboxEntry(
            notification_id=message.notification_id,
            channel=message.channel,
            recipient=message.recipient,
            subject=message.subject,
            body=message.body,
        )
        self._entries.append(entry)
        return entry

    @property
    def entries(self) -> list[OutboxEntry]:
        return list(self._entries)

    def for_channel(self, channel: ChannelName) -> list[OutboxEntry]:
        return [e for e in self._entries if e.channel == channel]

    def clear(self) -> None:
        self._entries.clear()


class ChannelSender(ABC):
    """Interface every delivery channel implements."""

    name: ChannelName

    def __init__(self, outbox: Outbox) -> None:
        self._outbox = outbox

    @abstractmethod
    async def send(self, message: Message) -> None:
        """Deliver message or raise DeliveryError."""
