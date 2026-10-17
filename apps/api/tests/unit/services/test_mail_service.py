from unittest.mock import patch

import pytest

from app.config import settings
from app.services.mail import ConsoleMailService, ResendMailService, get_mail_service

# ── ConsoleMailService ────────────────────────────────────────────────────────


def test_console_send_logs(caplog):
    with caplog.at_level("WARNING", logger="app.services.mail"):
        ConsoleMailService().send("a@unq.edu.ar", "Asunto", "<p>Hola</p>")
    assert "[MAIL]" in caplog.text
    assert "a@unq.edu.ar" in caplog.text


# ── ResendMailService ─────────────────────────────────────────────────────────


def test_resend_send_success():
    with patch("app.services.mail.resend") as mock_resend:
        ResendMailService().send("a@unq.edu.ar", "Asunto", "<p>Hola</p>")
    payload = mock_resend.Emails.send.call_args.args[0]
    assert payload["to"] == "a@unq.edu.ar"
    assert payload["subject"] == "Asunto"
    assert payload["html"] == "<p>Hola</p>"
    assert payload["from"] == settings.resend_from_email


def test_resend_send_failure_does_not_raise(caplog):
    with (
        patch("app.services.mail.resend") as mock_resend,
        caplog.at_level("ERROR", logger="app.services.mail"),
    ):
        mock_resend.Emails.send.side_effect = Exception("down")
        ResendMailService().send("a@unq.edu.ar", "Asunto", "<p>Hola</p>")
    assert "Error sending email" in caplog.text


# ── get_mail_service ──────────────────────────────────────────────────────────


def test_get_mail_service_console_without_key(monkeypatch):
    monkeypatch.setattr(settings, "resend_api_key", "")
    assert isinstance(get_mail_service(), ConsoleMailService)


def test_get_mail_service_resend_with_key(monkeypatch):
    monkeypatch.setattr(settings, "resend_api_key", "re_test")
    assert isinstance(get_mail_service(), ResendMailService)


def test_base_send_raises():
    from app.services.mail import MailService

    with pytest.raises(NotImplementedError):
        MailService().send("a@unq.edu.ar", "Asunto", "<p>Hola</p>")
