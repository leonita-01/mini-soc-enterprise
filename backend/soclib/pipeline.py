import json, yaml, os
from .db import SessionLocal, Event, Alert
from .alerting.console import ConsoleNotifier
from .alerting.slack import SlackNotifier
from .alerting.emailer import EmailNotifier
from .alerting.webhook import WebhookNotifier
from .alerting.pagerduty import PagerDutyNotifier
from .detect.brute_ssh import SSHBruteForce
from .detect.port_scan import PortScan
from .detect.ioc_match import IOCMatch
from .detect.http_404_spray import HTTP404Spray
from .detect.http_auth_spike import HTTPAuthSpike
from .detect.http_sqli_cmdi import HTTPSigRule
from .detect.dns_tunnel import DNSTunnel
from .suppress import ip_whitelisted
from .correlate import correlate
from .parsers import ssh_auth, nginx, apache, apache_error, ufw, dns
PARSERS = {"ssh_auth": ssh_auth.parse_line, "nginx": nginx.parse_line, "apache": apache.parse_line, "apache_error": apache_error.parse_line, "ufw": ufw.parse_line, "dns": dns.parse_line}
def load_cfg(path="backend/config.yml"):
    import yaml; return yaml.safe_load(open(path))
def load_iocs(ioc_path="data/iocs.json"):
    if not os.path.exists(ioc_path): return [], [], []
    d = json.load(open(ioc_path)); return d.get("ips", []), d.get("domains", []), d.get("hashes", [])
class Pipeline:
    def __init__(self, cfg_path="backend/config.yml"):
        self.cfg_path = cfg_path; self.cfg_mtime = 0; self.reload()
    def reload(self):
        st = os.stat(self.cfg_path); mtime = st.st_mtime
        if mtime == self.cfg_mtime: return
        self.cfg_mtime = mtime
        cfg = load_cfg(self.cfg_path)
        self.host = cfg.get("host", "localhost")
        self.supp = cfg.get("suppression", {})
        i_ips, i_dom, i_hash = load_iocs(cfg.get("ioc_path","data/iocs.json"))
        self.rules = [ SSHBruteForce(**cfg["rules"]["ssh_bruteforce"]), PortScan(**cfg["rules"]["port_scan"]), IOCMatch(i_ips, i_dom, i_hash),
                       HTTP404Spray(**cfg["rules"]["http_404_spray"]), HTTPAuthSpike(**cfg["rules"]["http_auth_spike"]),
                       HTTPSigRule(**cfg["rules"]["http_sqli_cmdi"]), DNSTunnel(**cfg["rules"]["dns_tunnel"]) ]
        self.notifiers = [ConsoleNotifier()]
        s = cfg.get("slack",{})
        if s.get("enabled"): self.notifiers.append(SlackNotifier(s.get("webhook")))
        a = cfg.get("alerts",{})
        if a.get("email",{}).get("enabled"): self.notifiers.append(EmailNotifier(a["email"]["to"]))
        if a.get("webhook",{}).get("enabled"): self.notifiers.append(WebhookNotifier(a["webhook"]["url"]))
        if a.get("pagerduty",{}).get("enabled"): self.notifiers.append(PagerDutyNotifier())
        self.dedup = {}
    def handle_event(self, e: dict):
        self.reload()
        wl = self.supp.get("whitelisted_ips", [])
        if e.get("src_ip") and ip_whitelisted(e["src_ip"], wl): return
        with SessionLocal() as s:
            ev = Event(**{k: e.get(k) for k in ["ts","host","src_ip","dst_ip","dst_port","user","http_path","status","proto","source_type","raw","fields"]})
            s.add(ev); s.commit()
        for r in self.rules:
            for alert in r.consider(e):
                key = (alert["type"], alert.get("src_ip"))
                last = self.dedup.get(key)
                if last and (e["ts"] - last).total_seconds() < 60:  continue
                self.dedup[key] = e["ts"]
                with SessionLocal() as s:
                    a = Alert(rule_id=alert["rule_id"], type=alert["type"], severity=alert["severity"],
                              src_ip=alert.get("src_ip"), dst_ip=alert.get("dst_ip"), details=alert.get("details",{}))
                    s.add(a); s.commit()
                    correlate(a)
                for n in self.notifiers: n.notify(alert)
