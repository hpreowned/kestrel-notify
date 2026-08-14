import httpx
import pytest
import respx

from notify.channels import DeliveryError, Outbox, WebhookChannel
from notify.models import ChannelName, Event, Message

URL = "https://hooks.example.com/kestrel"


def msg(recipient=URL):
    return Message("ntf_1", ChannelName.WEBHOOK, recipient, Event.DELIVERED, "SHP-1", "subj", "body")


@respx.mock
async def test_posts_json_payload_and_records():
    route = respx.post(URL).mock(return_value=httpx.Response(200))
    outbox = Outbox()
    await WebhookChannel(outbox).send(msg())
    assert route.call_count == 1
    request = route.calls.last.request
    assert request.headers["X-Kestrel-Event"] == "DELIVERED"
    assert b'"shipment_reference":"SHP-1"' in request.content.replace(b" ", b"")
    assert len(outbox.entries) == 1


@respx.mock
@pytest.mark.parametrize("code", [429, 500, 503])
async def test_server_errors_are_retryable(code):
    respx.post(URL).mock(return_value=httpx.Response(code))
    outbox = Outbox()
    with pytest.raises(DeliveryError) as info:
        await WebhookChannel(outbox).send(msg())
    assert info.value.retryable is True
    assert outbox.entries == []


@respx.mock
async def test_client_error_is_permanent():
    respx.post(URL).mock(return_value=httpx.Response(404))
    with pytest.raises(DeliveryError) as info:
        await WebhookChannel(Outbox()).send(msg())
    assert info.value.retryable is False


@respx.mock
async def test_transport_error_is_retryable():
    respx.post(URL).mock(side_effect=httpx.ConnectError("down"))
    with pytest.raises(DeliveryError) as info:
        await WebhookChannel(Outbox()).send(msg())
    assert info.value.retryable is True


async def test_non_http_recipient_rejected():
    with pytest.raises(DeliveryError) as info:
        await WebhookChannel(Outbox()).send(msg("ftp://nope"))
    assert info.value.retryable is False
