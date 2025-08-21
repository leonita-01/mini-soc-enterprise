from collections import defaultdict, deque
from datetime import timedelta
from .base import Rule
class DNSTunnel(Rule):
    id='dns_tunnel'; severity='high'
    def __init__(self, txt_threshold=30, window_minutes=5, min_avg_label_len=20, min_queries_for_len_check=15):
        self.window=timedelta(minutes=window_minutes); self.txt_threshold=txt_threshold
        self.min_avg_label_len=min_avg_label_len; self.min_queries_for_len_check=min_queries_for_len_check
        self.events=defaultdict(deque)
    def consider(self, e):
        if e.get("source_type")!="dns": return []
        ts=e["ts"]; src=e["src_ip"]; avg_len=(e.get("fields") or {}).get("avg_label_len",0); qtype=(e.get("fields") or {}).get("qtype","?")
        dq=self.events[src]; dq.append((ts, avg_len, qtype)); cutoff=ts-self.window
        while dq and dq[0][0]<cutoff: dq.popleft()
        txt_count=sum(1 for _,_,qt in dq if str(qt).upper()=="TXT")
        if txt_count>=self.txt_threshold:
            return [{"rule_id":self.id,"type":"dns_tunnel","severity":"high","src_ip":src,"details":{"reason":"txt_burst","txt_count":txt_count}}]
        if len(dq)>=self.min_queries_for_len_check:
            avg=sum(v for _,v,_ in dq)/len(dq)
            if avg>=self.min_avg_label_len:
                return [{"rule_id":self.id,"type":"dns_tunnel","severity":"high","src_ip":src,"details":{"reason":"long_labels","avg_label_len":avg}}]
        return []
