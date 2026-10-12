import pytest

from app.auth.domains import is_domain_allowed, normalize_domains
from app.errors import BusinessError

# ── normalize_domains ─────────────────────────────────────────────────────────


def test_normalize_ok():
    assert normalize_domains(["@unq.edu.ar", "@gmail.com"]) == ["@unq.edu.ar", "@gmail.com"]


def test_normalize_strips_and_lowercases():
    assert normalize_domains([" @UNQ.EDU.AR ", "*"]) == ["@unq.edu.ar", "*"]


def test_normalize_rejects_empty():
    with pytest.raises(BusinessError):
        normalize_domains([])


def test_normalize_rejects_non_list():
    with pytest.raises(BusinessError):
        normalize_domains("@unq.edu.ar")
    with pytest.raises(BusinessError):
        normalize_domains(None)


def test_normalize_rejects_entry_without_at():
    with pytest.raises(BusinessError):
        normalize_domains(["unq.edu.ar"])


def test_normalize_rejects_non_string_entry():
    with pytest.raises(BusinessError):
        normalize_domains(["@unq.edu.ar", 42])


# ── is_domain_allowed ─────────────────────────────────────────────────────────


def test_allowed_match():
    assert is_domain_allowed("gabi@unq.edu.ar", ["@unq.edu.ar"])


def test_allowed_case_insensitive():
    assert is_domain_allowed("GABI@UNQ.EDU.AR", ["@unq.edu.ar"])


def test_allowed_wildcard():
    assert is_domain_allowed("x@yahoo.com", ["*"])


def test_allowed_wildcard_mixed():
    assert is_domain_allowed("x@yahoo.com", ["*", "@unq.edu.ar"])


def test_denied_other_domain():
    assert not is_domain_allowed("lean@gmail.com", ["@unq.edu.ar"])


def test_denied_empty_list():
    assert not is_domain_allowed("gabi@unq.edu.ar", [])
