import os, requests, json
from .base import Notifier
class SlackNotifier(Notifier):
    def __init__(self, webhook=None): self.webhook = webhook or os.getenv("SLACK_WEBHOOK_URL")
    def notify(self, alert: dict):
        if not self.webhook: return
        text = f":rotating_light: {alert['type']} from {alert.get('src_ip','?')} severity={alert['severity']}"
        try:
            requests.post(self.webhook, json={"text": text, "blocks": [
                {"type":"section","text":{"type":"mrkdwn","text":f"*Alert:* `{alert['type']}`\n*Src:* {alert.get('src_ip')}\n*Details:* ```{json.dumps(alert.get('details',{}), indent=2)}```"}}]})
        except Exception: pass
