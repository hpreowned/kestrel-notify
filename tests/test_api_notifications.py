import httpx
import respx

from tests.conftest import make_request


def test_create_then_get_marks_sent(client, service):
    response = client.post("/v1/notifications", json=make_request())
    assert response.status_code == 202
    nid = response.json()["id"]
    got = client.get(f"/v1/notifications/{nid}")
    assert got.status_code == 200
    assert got.json()["status"] == "SENT"
    assert got.json()["attempts"] == 1
    assert len(service.outbox.entries) == 1


def test_get_unknown_is_404(client):
    response = client.get("/v1/notifications/ntf_missing")
    assert response.status_code == 404
    assert response.json()["detail"] == "notification not found"


def test_invalid_body_is_422(client):
    assert client.post("/v1/notifications", json=make_request(channel="fax")).status_code == 422
    assert client.post("/v1/notifications", json=make_request(event="LOST")).status_code == 422


def test_rate_limit_returns_429(client):
    for _ in range(5):
        assert client.post("/v1/notifications", json=make_request()).status_code == 202
    response = client.post("/v1/notifications", json=make_request())
    assert response.status_code == 429
    assert response.json()["detail"] == "notification rate exceeded"


def test_sms_disabled_by_flag(monkeypatch, service):
    from fastapi.testclient import TestClient

    from notify.main import create_app
    from notify.service import NotificationService
    from notify.settings import Settings

    monkeypatch.setenv("NOTIFY_FEATURE_SMS", "false")
    settings = Settings()
    app_client = TestClient(create_app(settings, NotificationService(settings)))
    body = make_request(channel="sms", recipient="+4915112345678")
    response = app_client.post("/v1/notifications", json=body)
    assert response.status_code == 422
    assert "channel disabled" in response.json()["detail"]


def test_bad_email_dead_letters_without_retry(client, sleeps):
    response = client.post("/v1/notifications", json=make_request(recipient="nonsense"))
    got = client.get(f"/v1/notifications/{response.json()['id']}").json()
    assert got["status"] == "DEAD_LETTERED"
    assert got["attempts"] == 1
    assert got["last_error"] == "invalid email address"
    assert sleeps == []


@respx.mock
def test_webhook_channel_retries_then_dead_letters(client, sleeps):
    url = "https://hooks.example.com/down"
    route = respx.post(url).mock(return_value=httpx.Response(503))
    body = make_request(channel="webhook", recipient=url)
    nid = client.post("/v1/notifications", json=body).json()["id"]
    got = client.get(f"/v1/notifications/{nid}").json()
    assert got["status"] == "DEAD_LETTERED"
    assert route.call_count == 4
    assert len(sleeps) == 3


@respx.mock
def test_webhook_channel_recovers(client):
    url = "https://hooks.example.com/flaky"
    respx.post(url).mock(side_effect=[httpx.Response(500), httpx.Response(200)])
    nid = client.post(
        "/v1/notifications", json=make_request(channel="webhook", recipient=url)
    ).json()["id"]
    got = client.get(f"/v1/notifications/{nid}").json()
    assert got["status"] == "SENT"
    assert got["attempts"] == 2
