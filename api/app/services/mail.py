import logging

import resend

from app.config import settings

logger = logging.getLogger(__name__)


def send_mail(to: str, subject: str, html: str) -> None:
    resend.api_key = settings.resend_api_key
    try:
        resend.Emails.send({"from": settings.resend_from_email, "to": to, "subject": subject, "html": html})
    except Exception:
        logger.exception("Error sending email to %s", to)
