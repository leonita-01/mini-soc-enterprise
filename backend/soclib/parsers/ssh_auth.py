import re
from datetime import datetime
from dateutil import parser as dtp
RE_FAIL = re.compile(r"Failed password for (invalid user )?(?P<user>\S+) from (?P<src>\d+\.\d+\.\d+\.\d+) port (?P<port>\d+)")
RE_ACCEPT = re.compile(r"Accepted (password|publickey) for (?P<user>\S+) from (?P<src>\d+\.\d+\.\d+\.\d+)")
def parse_line(line: str, host: str):
    try: ts = dtp.parse(line[:15], fuzzy=True)
    except Exception: ts = datetime.utcnow()
    m = RE_FAIL.search(line)
    if m: return {"ts":ts,"host":host,"src_ip":m.group("src"),"dst_port":22,"user":m.group("user"),"status":"ssh_failed","proto":"tcp","source_type":"ssh_auth","raw":line,"fields":{}}
    m = RE_ACCEPT.search(line)
    if m: return {"ts":ts,"host":host,"src_ip":m.group("src"),"dst_port":22,"user":m.group("user"),"status":"ssh_success","proto":"tcp","source_type":"ssh_auth","raw":line,"fields":{}}
    return None
