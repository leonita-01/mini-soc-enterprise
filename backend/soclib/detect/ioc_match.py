from .base import Rule
class IOCMatch(Rule):
    id='ioc_match'; severity='high'
    def __init__(self, ioc_ips=None, ioc_domains=None, ioc_hashes=None):
        self.ioc_ips=set(ioc_ips or []); self.ioc_domains=set(ioc_domains or []); self.ioc_hashes=set(ioc_hashes or [])
    def consider(self, e):
        alerts=[]
        if e.get("src_ip") in self.ioc_ips:
            alerts.append({"rule_id":self.id,"type":"ioc_match","severity":"high","src_ip":e.get("src_ip"),"details":{"hit":"ip"}})
        path=(e.get("http_path") or "").lower()
        if any(d in path for d in self.ioc_domains):
            alerts.append({"rule_id":self.id,"type":"ioc_match","severity":"high","src_ip":e.get("src_ip"),"details":{"hit":"domain_in_path"}})
        return alerts
