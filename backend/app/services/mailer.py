# SEND demo scam emails to the opted-in judges and people~ eheheh AHAHAHAAHHA (im sleep deprived T-T)

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, make_msgid

from flask import current_app


def send_demo_email(to_email: str, subject: str, body: str)-> bool:
    cfg = current_app.config
    host, port, user, pwd = cfg["SMTP_HOST"], cfg["SMTP_PORT"], cfg["SMTP_USER"], cfg["SMTP_PASS"]
    if not (host and user and pwd):
        current_app.logger.warning("SMTP not configured; skipping send")
        return False

    msg = MIMEMultipart()
    msg["From"] = formataddr((cfg["SMTP_FROM_NAME"], user))
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=False)
    msg["Message-ID"] = make_msgid(domain=user.split("@")[-1])
    msg.attach(MIMEText(body, "Plain"))

    try:
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.starttls()
            server.login(user, pwd)
            server.send_message(msg)

        return True
    except Exception as e:
        current_app.logger.warning("Mail failed: %s", type(e).__name__)
        return False

DEMO_SCAM_TEMPEARTE = """We have detected unusual activity on your account. Your access will be
suspended within 24 hours unless you verify your identity immediately.

Verify now: http://Aether-bank-kyc.example/secure-update

Failure to act will result in permanent account closure.

Nova Bank Security Team
[Demonstration email sent by Team Atheris. Do not click any links.]"""

def send_scam_demo(to_email: str, check_url: str | None = None) -> bool:
    body = DEMO_SCAM_TEMPEARTE
    if check_url:
        body+= f"\n\nCheck this email with Aether:{check_url}"

    return send_demo_email(to_email, "Urgent: Your account will be suspended", body)
    
