"""Matrix comparison, pid-normalized, plus full S09 and per-case classification vs baseline (git show only)."""
import json
import re
import subprocess

REPO = "/home/user/ReBaseGuard"
H = "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/"
SPECS = {"716946e8": "b6efec42:" + H + "sf1a_review/evidence/MATRIX_716946e8.json",
         "a119": "b6efec42:" + H + "r2_candidate_followup/evidence/MATRIX_a119e978.json",
         "a119_run2": "b6efec42:" + H + "r2_candidate_followup/evidence/MATRIX_a119e978_run2.json",
         "base101": "b6efec42:" + H + "evidence/matrix/MATRIX_BASELINE_r2_101ef2cb.json"}
VOL = re.compile(r"/tmp/\S*?(?=['\"\s]|$)|tmp-\d+|fsprobe-\d+|\d{4}-\d{2}-\d{2}T[\d:.]+(Z|[+-]\d\d:\d\d)?|\b[0-9a-f]{40,64}\b")


def norm(o):
    if isinstance(o, dict):
        return {k: norm(v) for k, v in o.items() if k not in ("wall_s",)}
    if isinstance(o, list):
        return [norm(x) for x in o]
    return VOL.sub("<v>", o) if isinstance(o, str) else o


M = {k: {c["id"]: c for c in json.loads(subprocess.run(["git", "-C", REPO, "show", s], capture_output=True,
                                                         check=True).stdout)["cases"]} for k, s in SPECS.items()}
for other in ("a119", "a119_run2"):
    d = [c for c in M["716946e8"] if norm(M["716946e8"][c]) != norm(M[other][c])]
    print(f"716946e8 vs {other}: differing cases (pid/path/time normalized): {d}")
d = [c for c in M["a119"] if norm(M["a119"][c]) != norm(M["a119_run2"][c])]
print(f"a119 vs a119_run2 differing: {d}")
for k in SPECS:
    s = M[k]["S09"]
    print(f"--- S09 {k}: " + json.dumps(norm(s), sort_keys=True)[:900])


def summ(c):
    st = c.get("status_after_crash")
    cls = st.get("classification") if isinstance(st, dict) else st
    rs = c.get("restart") if isinstance(c.get("restart"), dict) else {}
    return (c.get("rc"), cls, c.get("no_trace"), c.get("fresh_start_allowed_after"), rs.get("ok"),
            c.get("risk"), c.get("crash"))


diff = []
for cid in M["716946e8"]:
    a, b = summ(M["716946e8"][cid]), summ(M["base101"][cid])
    if a != b or norm(M["716946e8"][cid]) != norm(M["base101"][cid]):
        diff.append(cid)
print("cases differing from baseline 101ef2cb (normalized full content):", diff)
for cid in M["716946e8"]:
    print(cid, "new", summ(M["716946e8"][cid])[:5], "| base", summ(M["base101"][cid])[:5])
