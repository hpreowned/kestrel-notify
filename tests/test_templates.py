import pytest

from notify.models import CarrierCode, Event
from notify.templates import CARRIER_NAMES, render


@pytest.mark.parametrize("event", list(Event))
def test_every_event_has_a_template(event):
    out = render(event, "SHP-9")
    assert "SHP-9" in out.subject
    assert "SHP-9" in out.body
    assert "$" not in out.subject + out.body


def test_carrier_name_is_rendered():
    out = render(Event.IN_TRANSIT, "SHP-9", CarrierCode.BLX)
    assert "Baltic Express" in out.body


def test_missing_carrier_falls_back():
    assert "the carrier" in render(Event.RESERVED, "SHP-9").body


def test_all_carriers_named():
    assert set(CARRIER_NAMES) == {CarrierCode.NSL, CarrierCode.BLX, CarrierCode.PCR}
    assert CARRIER_NAMES[CarrierCode.NSL] == "NorthStar Lines"
