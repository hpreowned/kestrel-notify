"""HMAC signing and verification for the booking webhook."""

import hashlib
import hmac

SIGNATURE_HEADER = "X-Kestrel-Signature"
_PREFIX = "sha256="


class InvalidSignatureError(Exception):
    """Raised when a webhook signature is missing, malformed or wrong."""

    def __init__(self) -> None:
        super().__init__("invalid webhook signature")


def sign(secret: str, body: bytes) -> str:
    """Return the header value `sha256=<hex>` for the given raw body."""
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return _PREFIX + digest


def verify(secret: str, body: bytes, header_value: str | None) -> None:
    """Raise InvalidSignatureError unless header_value matches the body."""
    if not header_value or not header_value.startswith(_PREFIX):
        raise InvalidSignatureError
    expected = sign(secret, body)
    if not hmac.compare_digest(expected.encode("utf-8"), header_value.encode("utf-8")):
        raise InvalidSignatureError
