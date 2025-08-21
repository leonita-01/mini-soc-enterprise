from collections import defaultdict, deque
from datetime import timedelta
from .base import Rule
class SSHBruteForce(Rule):
    id='brute_ssh'; severity='medium'
    def __init__(self, threshold=5, window_minutes=3):
        self.threshold=threshold; self.window=timedelta(minutes=window_minutes); self.failures=defaultdict(deque)
    def consider(self, e):
        if e.get("source_type")!="ssh_auth" or e.get("status")!="ssh_failed": return []
        dq=self.failures[e["src_ip"]]; now=e["ts"]; dq.append(now); cutoff=now-self.window
        while dq and dq[0]<cutoff: dq.popleft()
        if len(dq)>=self.threshold:
            return [{"rule_id":self.id,"type":"brute_ssh","severity":"medium","src_ip":e["src_ip"],"details":{"failures_in_window":len(dq)}}]
        return []
