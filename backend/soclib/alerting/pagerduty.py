import os, requests
from .base import Notifier
class PagerDutyNotifier(Notifier):
    def __init__(self, routing_key=None): self.key=routing_key or os.getenv("PAGERDUTY_ROUTING_KEY")
    def notify(self, alert: dict):
        if not self.key: return
        body = {"routing_key": self.key, "event_action": "trigger",
                "payload": {"summary": f"{alert['type']} from {alert.get('src_ip','?')}", "severity": "critical",
                            "source": "mini-soc", "custom_details": alert}}
        try: requests.post("https://events.pagerduty.com/v2/enqueue", json=body, timeout=5)
        except Exception: pass
