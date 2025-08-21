import os, threading
from soclib.pipeline import Pipeline, PARSERS
from soclib.collectors.tailer import follow
from soclib.collectors.syslog_server import udp_server, tcp_server
from soclib.collectors.journald import follow_units
from soclib.parsers import ssh_auth, nginx, ufw, dns, apache, apache_error
PIPE = Pipeline()
def push(source, line, host=None):
    parser = PARSERS.get(source)
    if not parser: return
    e = parser(line, host or os.uname().nodename)
    if e: PIPE.handle_event(e)
def run_tailers():
    sources = [("ssh_auth", "/var/log/auth.log"), ("nginx", "/var/log/nginx/access.log"), ("apache_error", "/var/log/apache2/error.log"), ("ufw", "/var/log/ufw.log"), ("dns", "/var/log/dns.log")]
    for name, path in sources:
        if not os.path.exists(path): continue
        def worker(name=name, path=path):
            for line in follow(path): push(name, line)
        threading.Thread(target=worker, daemon=True).start()
def run_syslog():
    udp_server("0.0.0.0", 5514, lambda src, line: push(src, line), "nginx")
    tcp_server("0.0.0.0", 5515, lambda src, line: push(src, line), "nginx")
def run_journald():
    def worker():
        for line in follow_units(["ssh","nginx"]):
            if "sshd" in line: push("ssh_auth", line)
            elif "GET " in line or "POST " in line: push("nginx", line)
    threading.Thread(target=worker, daemon=True).start()
if __name__ == "__main__":
    run_tailers(); run_syslog(); run_journald()
    print("Ingestors running. Ctrl+C to exit."); import time
    while True: time.sleep(1)
