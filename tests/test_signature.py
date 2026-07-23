import pytest

from notify.signature import InvalidSignatureError, sign, verify


def test_sign_has_prefix_and_is_stable():
    sig = sign("s3", b"payload")
    assert sig.startswith("sha256=")
    assert sig == sign("s3", b"payload")


def test_verify_accepts_valid():
    verify("s3", b"payload", sign("s3", b"payload"))


@pytest.mark.parametrize("header", [None, "", "sha256=deadbeef", "md5=abc"])
def test_verify_rejects_bad_headers(header):
    with pytest.raises(InvalidSignatureError, match="invalid webhook signature"):
        verify("s3", b"payload", header)


def test_verify_rejects_tampered_body():
    sig = sign("s3", b"payload")
    with pytest.raises(InvalidSignatureError):
        verify("s3", b"payload!", sig)


def test_verify_rejects_wrong_secret():
    with pytest.raises(InvalidSignatureError):
        verify("other", b"payload", sign("s3", b"payload"))
