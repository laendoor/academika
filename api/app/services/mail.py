import logging

import resend

from app.config import settings

logger = logging.getLogger(__name__)


class MailService:
    def send(self, to: str, subject: str, html: str) -> None:
        raise NotImplementedError


class ConsoleMailService(MailService):
    def send(self, to: str, subject: str, html: str) -> None:
        logger.warning("[MAIL] To: %s | Subject: %s | Body: %s", to, subject, html)


class ResendMailService(MailService):
    def send(self, to: str, subject: str, html: str) -> None:
        resend.api_key = settings.resend_api_key
        try:
            resend.Emails.send({"from": settings.resend_from_email, "to": to, "subject": subject, "html": html})
        except Exception:
            logger.error("Error sending email to %s", to)


def get_mail_service() -> MailService:
    if settings.resend_api_key:
        return ResendMailService()
    return ConsoleMailService()
