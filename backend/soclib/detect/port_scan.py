from collections import defaultdict, deque
from datetime import timedelta
from .base import Rule
class PortScan(Rule):
    id='port_scan'; severity='high'
    def __init__(self, distinct_ports=20, window_minutes=2):
        self.window=timedelta(minutes=window_minutes); self.distinct_ports=distinct_ports; self.ports=defaultdict(deque)
    def consider(self, e):
        if e.get("source_type")!="ufw" or e.get("dst_port") is None: return []
        dq=self.ports[e["src_ip"]]; dq.append((e["ts"], e["dst_port"])); cutoff=e["ts"]-self.window
        while dq and dq[0][0]<cutoff: dq.popleft()
        distinct=len({p for _,p in dq})
        if distinct>=self.distinct_ports:
            return [{"rule_id":self.id,"type":"port_scan","severity":"high","src_ip":e["src_ip"],"details":{"distinct_ports":distinct}}]
        return []
