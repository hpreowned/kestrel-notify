"""Original fan-out: send one event to every registered contact in a thread pool.

Predates the queue. Each contact is tried once with no retry and no rate limit,
and failures are only printed. Kept for reference while the queue-based path beds in.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

MAX_WORKERS = 8


@dataclass
class Contact:
    kind: str  # "email", "sms" or "webhook"
    address: str


@dataclass
class FanoutResult:
    delivered: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)


def _send_one(contact: Contact, shipment_reference: str, event: str) -> str:
    """Pretend to deliver; the real transports were removed in the queue rewrite."""
    if contact.kind not in ("email", "sms", "webhook"):
        raise ValueError(f"unknown contact kind {contact.kind!r}")
    if not contact.address:
        raise ValueError("empty address")
    return f"{contact.kind}:{contact.address}:{shipment_reference}:{event}"


def fan_out(shipment_reference: str, event: str, contacts: list[Contact]) -> FanoutResult:
    """Deliver event to all contacts concurrently and collect the outcome."""
    result = FanoutResult()
    if not contacts:
        return result
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {
            pool.submit(_send_one, c, shipment_reference, event): c for c in contacts
        }
        for future in as_completed(futures):
            contact = futures[future]
            try:
                future.result()
            except Exception as exc:  # noqa: BLE001
                print(f"fanout failed for {contact.address}: {exc}")
                result.failed.append(contact.address)
            else:
                result.delivered.append(contact.address)
    return result
