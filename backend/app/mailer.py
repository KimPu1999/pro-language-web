import logging, smtplib, uuid
from dataclasses import dataclass
from email.message import EmailMessage
from .config import settings
logger=logging.getLogger("codemaster.mailer")
class Mailer:
    def send_notification(self, recipient: str, subject: str, body: str) -> "MailResult":
        """Send a notification and return evidence-backed provider state.

        Console mode is deliberately not treated as delivery. It is a development
        sink and must not make the notification dashboard claim that an email was sent.
        """
        if settings.mailer_mode == "console":
            logger.info("Development email sink is not configured recipient=%s subject=%s", recipient, subject)
            return MailResult(status="not_configured", provider="console", error_code="email_provider_not_configured")
        message=EmailMessage(); message["From"]=settings.mail_from; message["To"]=recipient; message["Subject"]=subject; message.set_content(body)
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                if settings.smtp_tls: server.starttls()
                if settings.smtp_username: server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(message)
            return MailResult(status="accepted", provider="smtp", provider_message_id=str(uuid.uuid4()))
        except (OSError, smtplib.SMTPException):
            logger.exception("SMTP notification attempt failed recipient=%s", recipient)
            return MailResult(status="failed", provider="smtp", error_code="smtp_send_failed")

    def send(self, recipient: str, subject: str, body: str) -> bool:
        return self.send_notification(recipient, subject, body).status == "accepted"

@dataclass(frozen=True)
class MailResult:
    status: str
    provider: str
    provider_message_id: str | None = None
    error_code: str | None = None
mailer=Mailer()
