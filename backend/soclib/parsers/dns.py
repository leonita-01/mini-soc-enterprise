import re
from datetime import datetime
from dateutil import parser as dtp
RE = re.compile(r"client (?P<src>\d+\.\d+\.\d+\.\d+)#\d+ \((?P<qname>[^)]+)\): query: (?P=qname) IN (?P<qtype>\S+)")
def parse_line(line: str, host: str):
    try: ts = dtp.parse(line.split(" client ")[0], fuzzy=True)
    except Exception: ts = datetime.utcnow()
    m = RE.search(line)
    if not m: return None
    qname = m.group("qname"); labels = qname.split(".")
    avg_label_len = sum(len(l) for l in labels)/max(1,len(labels))
    return {"ts":ts,"host":host,"src_ip":m.group("src"),"dst_port":53,"status":"dns_query","proto":"udp","source_type":"dns","raw":line,
            "fields":{"qname":qname,"qtype":m.group("qtype"),"avg_label_len":avg_label_len}}
