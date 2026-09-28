from notify.settings import Settings


def test_defaults_without_env(monkeypatch):
    monkeypatch.delenv("NOTIFY_WEBHOOK_SECRET", raising=False)
    monkeypatch.delenv("NOTIFY_RATE_LIMIT_PER_MINUTE", raising=False)
    monkeypatch.delenv("NOTIFY_FEATURE_SMS", raising=False)
    settings = Settings()
    assert settings.secret_value() is None
    assert settings.rate_limit_per_minute == 30
    assert settings.feature_sms is False


def test_reads_env(env):
    settings = Settings()
    assert settings.secret_value() == "dummy-secret-for-tests"
    assert settings.rate_limit_per_minute == 5
    assert settings.feature_sms is True


def test_empty_secret_counts_as_unset(monkeypatch):
    monkeypatch.setenv("NOTIFY_WEBHOOK_SECRET", "")
    assert Settings().secret_value() is None


def test_secret_not_in_repr(env):
    assert "dummy-secret-for-tests" not in repr(Settings())
