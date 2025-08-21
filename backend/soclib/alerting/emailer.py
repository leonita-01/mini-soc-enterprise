import smtplib, os, json
from email.message import EmailMessage
from .base import Notifier
class EmailNotifier(Notifier):
    def __init__(self, to): self.to=to
    def notify(self, alert: dict):
        host=os.getenv("SMTP_HOST"); port=int(os.getenv("SMTP_PORT","25")); user=os.getenv("SMTP_USER"); pw=os.getenv("SMTP_PASS")
        if not host or not self.to: return
        msg = EmailMessage()
        msg["Subject"] = f"[ALERT] {alert['type']} {alert.get('src_ip','')}"
        msg["From"] = user or "soc@example.com"
        msg["To"] = self.to
        msg.set_content(json.dumps(alert, default=str, indent=2))
        try:
            with smtplib.SMTP(host, port, timeout=5) as s:
                if user and pw: s.starttls(); s.login(user, pw)
                s.send_message(msg)
        except Exception: pass
