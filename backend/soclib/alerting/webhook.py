import requests
from .base import Notifier
class WebhookNotifier(Notifier):
    def __init__(self, url): self.url=url
    def notify(self, alert: dict):
        if not self.url: return
        try: requests.post(self.url, json=alert, timeout=5)
        except Exception: pass
