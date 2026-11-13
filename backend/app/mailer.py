import logging, smtplib
from email.message import EmailMessage
from .config import settings
logger=logging.getLogger("codemaster.mailer")
class Mailer:
    def send(self, recipient: str, subject: str, body: str) -> bool:
        if settings.mailer_mode == "console": logger.info("Development email accepted recipient=%s subject=%s", recipient, subject); return True
        message=EmailMessage(); message["From"]=settings.mail_from; message["To"]=recipient; message["Subject"]=subject; message.set_content(body)
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            if settings.smtp_tls: server.starttls()
            if settings.smtp_username: server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
        return True
mailer=Mailer()
