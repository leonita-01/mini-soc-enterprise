import re
from datetime import datetime
from dateutil import parser as dtp
LOG_RE = re.compile(r'(?P<src>\d+\.\d+\.\d+\.\d+) - (?P<user>-|\S+) \[(?P<ts>.*?)\] "(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d{3}) (?P<size>\d+) "(?P<ref>[^"]*)" "(?P<ua>[^"]+)"')
def parse_line(line: str, host: str):
    m = LOG_RE.search(line)
    if not m: return None
    try: ts = dtp.parse(m.group("ts").split(" ")[0].replace("/", " "))
    except Exception: ts = datetime.utcnow()
    ua = m.group("ua")
    return {"ts":ts,"host":host,"src_ip":m.group("src"),"dst_port":80,"user":None if m.group("user")=="-" else m.group("user"),
            "status":m.group("status"),"proto":"http","source_type":"nginx","raw":line,"http_path":m.group("path"),
            "fields":{"method":m.group("method"),"bytes":int(m.group("size")),"ua":ua,"ref":m.group("ref")}}
