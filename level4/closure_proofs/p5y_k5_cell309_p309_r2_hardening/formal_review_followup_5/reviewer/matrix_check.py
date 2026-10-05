#!/usr/bin/env python3
"""Side-by-side crash matrix: baseline r2 (task 3 and task 2 copies) vs candidate a119e978 (run 1, run 2) and 93d55063.
Prints per case: classification / refusal / fsync and link counts / run_start lines."""
import json
from pathlib import Path

B = Path("/tmp/claude-0/-home-user-ReBaseGuard/ede4e097-f9ec-54f5-9e84-81294f8ad688/scratchpad/t5/review/ev")
M = {"base_t3": "r2_candidate/evidence/matrix/MATRIX_BASELINE.json",
     "base_t2": "evidence/matrix/MATRIX_BASELINE_r2_101ef2cb.json",
     "c93d": "r2_candidate/evidence/matrix/MATRIX_CANDIDATE.json",
     "a119": "r2_candidate_followup/evidence/MATRIX_a119e978.json",
     "a119r2": "r2_candidate_followup/evidence/MATRIX_a119e978_run2.json"}
D = {k: json.loads((B / v).read_text()) for k, v in M.items()}
for k, d in D.items():
    print(k, "package", d.get("package_commit"), "runner", (d.get("runner_sha256") or "")[:16], "replica tree",
          (d.get("replica") or {}).get("tree"), "cases", len(d["cases"]), "tool", (d.get("tool_sha256") or "")[:12])


def cell(c):
    if c is None:
        return "-"
    out = c.get("classification") or c.get("classification_after") or ""
    if "runner_refused" in c:
        out += f" refused={c['runner_refused']}"
    if "fsync_ops" in c:
        out += f" fs={c['fsync_ops']} ln={c.get('link_ops')}"
    if "run_start_lines" in c:
        out += f" rs={c['run_start_lines']}"
    if "fresh_start_allowed_after" in c:
        out += f" fresh={c['fresh_start_allowed_after']} notrace={c.get('no_trace')}"
    if "unchanged" in c:
        out += f" unch={c['unchanged']}"
    return out


ids = [c["id"] for c in D["base_t3"]["cases"]]
for i in ids:
    row = {k: next((c for c in d["cases"] if c["id"] == i), None) for k, d in D.items()}
    print(f"\n{i}: {row['base_t3'].get('desc', '')[:110]}")
    for k in D:
        print(f"   {k:7s} {cell(row[k])}")

fm = json.loads((B / "R2_FAILURE_MATRIX.json").read_text())
print("\nR2_FAILURE_MATRIX keys:", list(fm)[:20])
