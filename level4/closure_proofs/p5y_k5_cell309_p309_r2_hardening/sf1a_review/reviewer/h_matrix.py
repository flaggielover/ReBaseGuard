"""Compare crash-matrix cases across committed evidence files (git show only; nothing executed).
argv: NEW OLD BASE (git specs)."""
import json
import re
import subprocess
import sys

REPO = "/home/user/ReBaseGuard"


def show(spec):
    return json.loads(subprocess.run(["git", "-C", REPO, "show", spec], capture_output=True, check=True).stdout)


VOLATILE = re.compile(r"/tmp/[^\s\"']*|\d{4}-\d{2}-\d{2}T[\d:.]+(Z|[+-]\d\d:\d\d)?|\b[0-9a-f]{40}\b|\b[0-9a-f]{64}\b"
                      r"|pid[ =-]?\d+|fsprobe-\d+|\d+\.\d+ ?s\b")


def norm(o):
    if isinstance(o, dict):
        return {k: norm(v) for k, v in o.items() if k not in ("wall_s", "elapsed", "t", "duration_s")}
    if isinstance(o, list):
        return [norm(x) for x in o]
    if isinstance(o, str):
        return VOLATILE.sub("<v>", o)
    return o


new, old, base = (show(s) for s in sys.argv[1:4])
N = {c["id"]: c for c in new["cases"]}
O = {c["id"]: c for c in old["cases"]}
B = {c["id"]: c for c in base["cases"]}
print("ids equal new/old/base:", list(N) == list(O) == list(B), len(N))
same_struct = []
for cid in N:
    eq = norm(N[cid]) == norm(O.get(cid))
    same_struct.append(eq)
    if not eq:
        a, b = norm(N[cid]), norm(O.get(cid))
        diffk = [k for k in set(a) | set(b) if a.get(k) != b.get(k)]
        print(f"  {cid} new!=a119 on keys {diffk}")
        for k in diffk:
            print(f"     new {k}: {json.dumps(a.get(k))[:300]}")
            print(f"     old {k}: {json.dumps(b.get(k))[:300]}")
print("new == a119 (normalized) for all cases:", all(same_struct))


def key(c):
    return {k: c.get(k) for k in ("rc", "no_trace", "fresh_start_allowed_after")} | {
        "status": (c.get("status_after_crash") or {}).get("classification") if isinstance(c.get("status_after_crash"), dict)
        else c.get("status_after_crash"), "restart": json.dumps(norm(c.get("restart")))[:120]}


disc = []
for cid in N:
    kn, kb = key(N[cid]), key(B[cid])
    if kn != kb:
        disc.append(cid)
        print(f"  DISCRIMINATES {cid}: new={json.dumps(kn)[:260]}")
        print(f"                 {' ' * len(cid)} base={json.dumps(kb)[:260]}")
print("cases where new differs from baseline 101ef2cb:", disc)
print("top-level bindings:", {k: (new.get(k), old.get(k), base.get(k)) for k in ("tool_sha256", "validator_sha256", "schema")})
print("topology new/old:", new.get("topology", {}).get("ok"), old.get("topology", {}).get("ok"),
      new.get("topology", {}).get("tip"), old.get("topology", {}).get("tip"))
