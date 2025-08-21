import re
from datetime import datetime
from dateutil import parser as dtp
LOG_RE = re.compile(r'(?P<src>\d+\.\d+\.\d+\.\d+) - (?P<ident>-|\S+) (?P<user>-|\S+) \[(?P<ts>.*?)\] "(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d{3}) (?P<size>\d+) "(?P<ref>[^"]*)" "(?P<ua>[^"]+)"')
def parse_line(line: str, host: str):
    m = LOG_RE.search(line)
    if not m: return None
    try: ts = dtp.parse(m.group("ts").split(" ")[0].replace("/", " "))
    except Exception: ts = datetime.utcnow()
    user = m.group("user");  user = None if user=="-" else user
    return {"ts":ts,"host":host,"src_ip":m.group("src"),"dst_port":80,"user":user,"status":m.group("status"),
            "proto":"http","source_type":"apache","raw":line,"http_path":m.group("path"),
            "fields":{"method":m.group("method"),"bytes":int(m.group("size")),"ua":m.group("ua"),"ref":m.group("ref")}}
