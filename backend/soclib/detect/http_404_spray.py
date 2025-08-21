from collections import defaultdict, deque
from datetime import timedelta
from .base import Rule
class HTTP404Spray(Rule):
    id='http_404_spray'; severity='medium'
    def __init__(self, threshold=30, window_minutes=5):
        self.threshold=threshold; self.window=timedelta(minutes=window_minutes); self.events=defaultdict(deque)
    def consider(self, e):
        if e.get("source_type") not in ("nginx","apache") or e.get("status")!="404": return []
        dq=self.events[e["src_ip"]]; now=e["ts"]; dq.append(now); cutoff=now-self.window
        while dq and dq[0]<cutoff: dq.popleft()
        if len(dq)>=self.threshold:
            return [{"rule_id":self.id,"type":"http_404_spray","severity":"medium","src_ip":e["src_ip"],"details":{"count":len(dq)}}]
        return []
