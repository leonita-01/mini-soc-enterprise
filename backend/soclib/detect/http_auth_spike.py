from collections import defaultdict, deque
from datetime import timedelta
from .base import Rule
class HTTPAuthSpike(Rule):
  id='http_auth_spike'; severity='medium'
  def __init__(self, threshold=15, window_minutes=5, statuses=None):
    self.threshold=threshold; self.window=timedelta(minutes=window_minutes); self.statuses=set(statuses or ["401","403"]); self.d=defaultdict(deque)
  def consider(self, e):
    if e.get("source_type") not in ("nginx","apache") or e.get("status") not in self.statuses: return []
    dq=self.d[e["src_ip"]]; now=e["ts"]; dq.append(now); cutoff=now-self.window
    while dq and dq[0]<cutoff: dq.popleft()
    if len(dq)>=self.threshold:
      return [{"rule_id":self.id,"type":"http_auth_spike","severity":"medium","src_ip":e["src_ip"],"details":{"count":len(dq),"statuses":list(self.statuses)}}]
    return []
