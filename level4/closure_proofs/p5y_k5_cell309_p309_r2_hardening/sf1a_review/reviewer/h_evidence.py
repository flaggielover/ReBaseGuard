"""Read-only summary of the committed SF1-A evidence at b6efec42 (git show only; nothing is executed)."""
import hashlib
import json
import subprocess
import sys

REPO = "/home/user/ReBaseGuard"
EV = "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/sf1a_review/evidence/"
COMMIT = "b6efec42"


def show(rel):
    return subprocess.run(["git", "-C", REPO, "show", f"{COMMIT}:{rel}"], capture_output=True, check=True).stdout


def walk(o, pre="", depth=0, maxd=3):
    if isinstance(o, dict) and depth < maxd:
        for k, v in o.items():
            walk(v, f"{pre}.{k}" if pre else k, depth + 1, maxd)
    elif isinstance(o, list) and depth < maxd and len(o) <= 12 and all(not isinstance(x, (dict, list)) for x in o):
        print(f"  {pre} = {o}")
    elif isinstance(o, list):
        print(f"  {pre} = <list len {len(o)}>")
    else:
        s = str(o)
        print(f"  {pre} = {s[:160]}")


names = sys.argv[1:]
for n in names:
    raw = show(EV + n)
    print(f"=== {n}  sha256={hashlib.sha256(raw).hexdigest()}  bytes={len(raw)}")
    try:
        walk(json.loads(raw), maxd=int(__import__('os').environ.get("MAXD", "3")))
    except ValueError:
        print(raw.decode()[:3000])
