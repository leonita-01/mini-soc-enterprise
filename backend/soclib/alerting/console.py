from .base import Notifier
import json
class ConsoleNotifier(Notifier):
    def notify(self, alert: dict):
        print('[ALERT]', json.dumps(alert, default=str))
