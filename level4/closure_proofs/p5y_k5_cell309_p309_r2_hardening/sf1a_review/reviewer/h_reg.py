"""Inspect REG_716946e8.json and FAST_CHECKS content (git show only)."""
import json
import re
import subprocess

REPO = "/home/user/ReBaseGuard"
EV = "b6efec42:level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/sf1a_review/evidence/"


def load(n):
    return json.loads(subprocess.run(["git", "-C", REPO, "show", EV + n], capture_output=True, check=True).stdout)


r = load("REG_716946e8.json")
print("REG top keys:", sorted(r))
for k, v in r.items():
    if not isinstance(v, (dict, list)):
        print(f"  {k} = {v}")
runs = r.get("runs") or r.get("steps") or {}
items = runs.items() if isinstance(runs, dict) else enumerate(runs)
for k, v in items:
    if isinstance(v, dict):
        tail = str(v.get("tail") or v.get("stdout_tail") or v.get("out") or "")
        fails = re.findall(r"\[FAIL\][^\n]*", tail)
        passes = len(re.findall(r"\[PASS\]", tail))
        meta = {kk: vv for kk, vv in v.items() if kk not in ("tail", "stdout_tail", "out", "stderr_tail")}
        print(f"--- {k}: {json.dumps(meta)[:400]}\n    PASS-count-in-tail={passes} FAIL={fails[:5]}\n    tail-end: "
              f"{tail[-500:]!r}")
f = load("FAST_CHECKS_716946e8.json")
print("FAST top keys:", sorted(f))
for k, v in f["steps"].items():
    t = v.get("tail", "")
    fl = re.findall(r'.FAIL.[^\n]*', t)[:3]
    st = re.findall(r'[^\n]*(?:stale|STALE|mismatch)[^\n]*', t)[:3]
    print(f"--- FAST {k}: rc={v.get('rc')} FAIL={fl} stale={st}")
    print("    " + repr(t[-700:]))
