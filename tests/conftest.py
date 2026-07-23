import pytest
from fastapi.testclient import TestClient

from notify.main import create_app
from notify.service import NotificationService
from notify.settings import Settings

TEST_SECRET = "dummy-secret-for-tests"


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("NOTIFY_WEBHOOK_SECRET", TEST_SECRET)
    monkeypatch.setenv("NOTIFY_RATE_LIMIT_PER_MINUTE", "5")
    monkeypatch.setenv("NOTIFY_FEATURE_SMS", "true")


@pytest.fixture
def sleeps():
    return []


@pytest.fixture
def service(env, sleeps):
    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    return NotificationService(Settings(), sleep=fake_sleep, jitter=lambda: 0.5)


@pytest.fixture
def client(service):
    return TestClient(create_app(Settings(), service))


def make_request(**overrides):
    body = {
        "shipment_reference": "SHP-1001",
        "recipient": "ops@example.com",
        "channel": "email",
        "event": "CREATED",
    }
    body.update(overrides)
    return body
