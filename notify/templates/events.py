"""Message templates, one per shipment event. Plain string.Template, no jinja2."""

from dataclasses import dataclass
from string import Template

from notify.models import CarrierCode, Event

CARRIER_NAMES: dict[CarrierCode, str] = {
    CarrierCode.NSL: "NorthStar Lines",
    CarrierCode.BLX: "Baltic Express",
    CarrierCode.PCR: "Pacific Reach",
}

_TEMPLATES: dict[Event, tuple[str, str]] = {
    Event.CREATED: (
        "Shipment $reference created",
        "Your shipment $reference has been created and is awaiting a carrier.",
    ),
    Event.RESERVED: (
        "Shipment $reference reserved",
        "Your shipment $reference is reserved with $carrier.",
    ),
    Event.IN_TRANSIT: (
        "Shipment $reference is on its way",
        "Your shipment $reference is in transit with $carrier.",
    ),
    Event.DELIVERED: (
        "Shipment $reference delivered",
        "Your shipment $reference was delivered by $carrier. Thank you for shipping with Kestrel.",
    ),
}


@dataclass(frozen=True)
class Rendered:
    subject: str
    body: str


def render(event: Event, shipment_reference: str, carrier_code: CarrierCode | None = None) -> Rendered:
    """Render the template for event. Unknown carrier renders as 'the carrier'."""
    subject, body = _TEMPLATES[event]
    carrier = CARRIER_NAMES[carrier_code] if carrier_code else "the carrier"
    values = {"reference": shipment_reference, "carrier": carrier}
    return Rendered(
        subject=Template(subject).safe_substitute(values),
        body=Template(body).safe_substitute(values),
    )
