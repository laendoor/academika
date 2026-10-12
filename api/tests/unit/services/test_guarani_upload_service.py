import hashlib

from app.services.guarani_upload_service import _file_hash, _preview_lines


def test_file_hash_is_sha256_of_raw() -> None:
    raw = b"codigo;nombre\n1;TPI\n"
    assert _file_hash(raw) == hashlib.sha256(raw).hexdigest()


def test_file_hash_differs_on_content_change() -> None:
    assert _file_hash(b"a\n") != _file_hash(b"b\n")


def test_preview_lines_returns_header_plus_five() -> None:
    content = "h1;h2\n" + "".join(f"{i};x\n" for i in range(10))
    preview, truncated = _preview_lines(content)
    assert preview == ["h1;h2", "0;x", "1;x", "2;x", "3;x", "4;x"]
    assert truncated is True


def test_preview_lines_short_file_not_truncated() -> None:
    preview, truncated = _preview_lines("h1;h2\n1;x\n2;x\n")
    assert preview == ["h1;h2", "1;x", "2;x"]
    assert truncated is False


def test_preview_lines_caps_huge_content() -> None:
    content = "h1\n" + "y" * (8 * 1024 + 100) + "\n"
    preview, truncated = _preview_lines(content)
    assert sum(len(line) for line in preview) <= 8 * 1024
    assert truncated is True
