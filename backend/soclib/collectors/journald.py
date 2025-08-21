import subprocess
def follow_units(units):
    cmd = ["journalctl","-f","-o","cat"]
    for u in units: cmd += ["-u", u]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
    for line in p.stdout:
        yield line.strip()
