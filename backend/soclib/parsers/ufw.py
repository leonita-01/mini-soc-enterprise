import re
from datetime import datetime
from dateutil import parser as dtp
RE = re.compile(r"UFW BLOCK.*SRC=(?P<src>\d+\.\d+\.\d+\.\d+).*DPT=(?P<dpt>\d+)")
def parse_line(line: str, host: str):
    try: ts = dtp.parse(line[:15], fuzzy=True)
    except Exception: ts = datetime.utcnow()
    m = RE.search(line)
    if not m: return None
    return {"ts":ts,"host":host,"src_ip":m.group("src"),"dst_port":int(m.group("dpt")),"status":"blocked","proto":"tcp","source_type":"ufw","raw":line,"fields":{}}
