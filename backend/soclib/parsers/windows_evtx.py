from Evtx.Evtx import Evtx
from datetime import datetime
def parse_evtx(file_path: str, host: str):
    events = []
    with Evtx(file_path) as log:
        for rec in log.records():
            xml = rec.xml()
            if "<EventID>4625</EventID>" in xml or "<EventID>4624</EventID>" in xml:
                ts = rec.timestamp()
                status = "winlog_failed" if "4625" in xml else "winlog_success"
                src_ip = None
                for tag in ["IpAddress", "IpPort", "WorkstationName"]:
                    key = f"<Data Name='{tag}'>"
                    if key in xml:
                        val = xml.split(key)[1].split("</Data>")[0]
                        if tag == "IpAddress": src_ip = val
                events.append({"ts": ts if isinstance(ts, datetime) else datetime.utcnow(),
                               "host": host,"src_ip": src_ip,"dst_port": None,"status": status,"proto": None,
                               "source_type": "winlog","raw": xml,"fields": {}})
    return events
