"""Reviewer probe P6 (brief 59): L-ID-1 'zombie => DEAD'. A child process whose MAIN thread exits (pthread_exit)
while a second thread keeps computing. Linux then shows the thread-group leader in state Z although the process is
alive and burning CPU. Synthetic; no science. Usage: python3 -B probe_zombie_leader.py"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "base"))
import lx_platform as L  # noqa: E402

CHILD = r"""
import ctypes, threading, time, sys
def work():
    t_end = time.time() + 6
    x = 0
    while time.time() < t_end:
        x += 1                      # keeps a CPU busy for ~6 s, then the process exits
threading.Thread(target=work, daemon=False).start()
time.sleep(0.3)
sys.stdout.write("ready\n"); sys.stdout.flush()
libc = ctypes.CDLL(None)
libc.pthread_exit(None)            # the MAIN thread (thread-group leader) exits; the worker thread continues
"""

p = subprocess.Popen([sys.executable, "-c", CHILD], stdout=subprocess.PIPE, text=True)
assert p.stdout.readline().strip() == "ready"
time.sleep(0.05)
ident = L.identity(p.pid)                 # recorded while the leader may already be gone: record via a fresh read
time.sleep(0.5)
rows = []
for _ in range(4):
    st = L.proc_stat(p.pid)
    tasks = sorted(x.name for x in Path(f"/proc/{p.pid}/task").iterdir())
    status = {ln.split(":")[0]: ln.split(":", 1)[1].strip() for ln in Path(f"/proc/{p.pid}/status").read_text().splitlines()
              if ln.split(":")[0] in ("State", "Threads")}
    rows.append({"stat_state": st and st["state"], "utime+stime": st and st["utime"] + st["stime"], "tasks": tasks,
                 "status": status, "identity_state": L.identity_state(ident),
                 "identity_state_with_full_record": L.identity_state(
                     dict(ident, cmdline_sha256=ident["cmdline_sha256"] or "recorded-before-exit"))})
    time.sleep(0.5)
print(json.dumps({"pid": p.pid, "recorded_identity": ident, "process_still_running": p.poll() is None,
                  "rows": rows}, indent=1))
p.wait(timeout=30)
