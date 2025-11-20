"""Runtime configuration, read from NOTIFY_* environment variables."""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Service settings.

    NOTIFY_WEBHOOK_SECRET       HMAC secret for the booking webhook (never defaulted)
    NOTIFY_RATE_LIMIT_PER_MINUTE  per-recipient bucket size, 0 disables limiting
    NOTIFY_FEATURE_SMS          enables the sms channel
    """

    model_config = SettingsConfigDict(env_prefix="NOTIFY_", extra="ignore")

    webhook_secret: SecretStr | None = None
    rate_limit_per_minute: int = Field(default=30, ge=0)
    feature_sms: bool = False

    def secret_value(self) -> str | None:
        """Return the webhook secret as a plain string, or None when unset/empty."""
        if self.webhook_secret is None:
            return None
        value = self.webhook_secret.get_secret_value()
        return value or None
