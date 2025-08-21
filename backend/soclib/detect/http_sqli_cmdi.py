import re
from collections import defaultdict, deque
from datetime import timedelta
from .base import Rule
SQLI_RE = re.compile(r"(union(\s+all)?\s+select|or\s+1=1|sleep\s*\(|benchmark\s*\()", re.I)
CMDI_RE = re.compile(r"(;|&&|\|\|)\s*(cat|ls|whoami|curl|wget|bash)\b", re.I)
class HTTPSigRule(Rule):
    id='http_sqli_cmdi'; severity='high'
    def __init__(self, threshold=5, window_minutes=5):
        self.threshold=threshold; self.window=timedelta(minutes=window_minutes); self.d=defaultdict(deque)
    def consider(self, e):
        if e.get("source_type") not in ("nginx","apache"): return []
        path=(e.get("http_path") or "")
        if not (SQLI_RE.search(path) or CMDI_RE.search(path)): return []
        dq=self.d[e["src_ip"]]; now=e["ts"]; dq.append(now); cutoff=now-self.window
        while dq and dq[0]<cutoff: dq.popleft()
        if len(dq)>=self.threshold:
            return [{"rule_id":self.id,"type":"http_sqli_cmdi","severity":"high","src_ip":e["src_ip"],"details":{"count":len(dq),"example_path":path[:120]}}]
        return []
