import re
from datetime import datetime
from dateutil import parser as dtp
RE = re.compile(r'\[(?P<ts>[^\]]+)\].*\[client (?P<src>\d+\.\d+\.\d+\.\d+):\d+\] (?P<msg>.*)')
def parse_line(line: str, host: str):
    m = RE.search(line)
    if not m: return None
    try: ts = dtp.parse(m.group("ts"), fuzzy=True)
    except Exception: ts = datetime.utcnow()
    return {"ts":ts,"host":host,"src_ip":m.group("src"),"status":"apache_error","proto":"http","source_type":"apache_error","raw":line,"fields":{"message":m.group("msg")}}
