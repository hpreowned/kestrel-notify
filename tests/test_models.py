import pytest
from pydantic import ValidationError

from notify.models import BookingEvent, ChannelName, Event, Notification, NotificationRequest


def test_request_accepts_all_channels_and_events():
    for channel in ChannelName:
        for event in Event:
            req = NotificationRequest(
                shipment_reference="SHP-1", recipient="a@b.co", channel=channel, event=event
            )
            assert req.channel == channel


def test_request_rejects_unknown_channel():
    with pytest.raises(ValidationError):
        NotificationRequest(
            shipment_reference="SHP-1", recipient="a@b.co", channel="pigeon", event="CREATED"
        )


def test_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        NotificationRequest(
            shipment_reference="SHP-1", recipient="a@b.co", channel="email", event="CREATED", x=1
        )


def test_notification_wire_is_snake_case():
    n = Notification(shipment_reference="SHP-1", recipient="a@b.co", channel="email", event="CREATED")
    dumped = n.model_dump(mode="json")
    assert {"shipment_reference", "created_at", "last_error", "carrier_code"} <= set(dumped)
    assert dumped["id"].startswith("ntf_")
    assert dumped["status"] == "QUEUED"


def test_booking_event_carrier_codes():
    ok = BookingEvent.model_validate(
        {"event": "RESERVED", "shipment_reference": "S1", "recipient": "a@b.co", "carrier_code": "NSL"}
    )
    assert ok.channel == ChannelName.EMAIL
    with pytest.raises(ValidationError):
        BookingEvent.model_validate(
            {"event": "RESERVED", "shipment_reference": "S1", "recipient": "a@b.co", "carrier_code": "XXX"}
        )
