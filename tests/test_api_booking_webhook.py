import json

from notify.signature import SIGNATURE_HEADER, sign
from tests.conftest import TEST_SECRET

EVENT = {
    "event": "RESERVED",
    "shipment_reference": "SHP-2002",
    "recipient": "ops@example.com",
    "carrier_code": "PCR",
}


def post(client, payload, signature=None, secret=TEST_SECRET):
    raw = json.dumps(payload).encode()
    headers = {"content-type": "application/json"}
    headers[SIGNATURE_HEADER] = signature if signature is not None else sign(secret, raw)
    return client.post("/v1/webhooks/booking", content=raw, headers=headers)


def test_valid_signature_enqueues_and_delivers(client, service):
    response = post(client, EVENT)
    assert response.status_code == 202
    nid = response.json()["notification_id"]
    got = client.get(f"/v1/notifications/{nid}").json()
    assert got["status"] == "SENT"
    assert got["carrier_code"] == "PCR"
    assert "Pacific Reach" in service.outbox.entries[0].body


def test_bad_signature_is_401(client):
    response = post(client, EVENT, signature="sha256=00")
    assert response.status_code == 401
    assert response.json()["detail"] == "invalid webhook signature"


def test_missing_signature_is_401(client):
    response = client.post("/v1/webhooks/booking", json=EVENT)
    assert response.status_code == 401


def test_signature_from_wrong_secret_is_401(client):
    assert post(client, EVENT, secret="somebody-else").status_code == 401


def test_invalid_payload_with_valid_signature_is_422(client):
    assert post(client, {"event": "LOST"}).status_code == 422


def test_unconfigured_secret_is_503(monkeypatch):
    from fastapi.testclient import TestClient

    from notify.main import create_app
    from notify.settings import Settings

    monkeypatch.delenv("NOTIFY_WEBHOOK_SECRET")
    response = post(TestClient(create_app(Settings())), EVENT)
    assert response.status_code == 503
