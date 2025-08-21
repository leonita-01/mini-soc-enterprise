import time
from pathlib import Path
def follow(path: str):
    p = Path(path)
    with p.open("r", errors="ignore") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5); continue
            yield line
