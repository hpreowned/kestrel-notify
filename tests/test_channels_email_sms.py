import pytest

from notify.channels import DeliveryError, EmailChannel, Outbox, SmsChannel
from notify.channels.sms import SMS_MAX_CHARS
from notify.models import ChannelName, Event, Message


def msg(channel, recipient, body="hello"):
    return Message("ntf_1", channel, recipient, Event.CREATED, "SHP-1", "subj", body)


async def test_email_records_to_outbox():
    outbox = Outbox()
    await EmailChannel(outbox).send(msg(ChannelName.EMAIL, "a@b.co"))
    assert [e.recipient for e in outbox.for_channel(ChannelName.EMAIL)] == ["a@b.co"]


async def test_email_rejects_bad_address_permanently():
    outbox = Outbox()
    with pytest.raises(DeliveryError) as info:
        await EmailChannel(outbox).send(msg(ChannelName.EMAIL, "not-an-address"))
    assert info.value.retryable is False
    assert outbox.entries == []


async def test_sms_truncates_to_one_segment():
    outbox = Outbox()
    await SmsChannel(outbox).send(msg(ChannelName.SMS, "+4915112345678", "x" * 400))
    (entry,) = outbox.entries
    assert len(entry.body) == SMS_MAX_CHARS


async def test_sms_rejects_bad_number():
    with pytest.raises(DeliveryError) as info:
        await SmsChannel(Outbox()).send(msg(ChannelName.SMS, "call me"))
    assert info.value.retryable is False


def test_outbox_clear():
    outbox = Outbox()
    outbox.record(msg(ChannelName.EMAIL, "a@b.co"))
    outbox.clear()
    assert outbox.entries == []
