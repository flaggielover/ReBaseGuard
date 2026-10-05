"""Per-case classification and fsync/link counts: 716946e8 vs a119e978 vs baseline 101ef2cb (git show only)."""
import json
import subprocess

REPO = "/home/user/ReBaseGuard"
H = "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/"
SPECS = {"716946e8": H + "sf1a_review/evidence/MATRIX_716946e8.json",
         "a119": H + "r2_candidate_followup/evidence/MATRIX_a119e978.json",
         "base101": H + "evidence/matrix/MATRIX_BASELINE_r2_101ef2cb.json"}
M = {k: {c["id"]: c for c in json.loads(subprocess.run(["git", "-C", REPO, "show", "b6efec42:" + s],
                                                         capture_output=True, check=True).stdout)["cases"]}
     for k, s in SPECS.items()}


def row(c):
    return (c.get("classification"), len(c.get("fsynced") or []), len(c.get("linked") or []) if "linked" in c else "-",
            c.get("fresh_start_allowed_after"), c.get("no_trace"))


disc_new, disc_old = [], []
for cid in M["716946e8"]:
    n, o, b = (row(M[k][cid]) for k in SPECS)
    if n[0] != b[0]:
        disc_new.append(cid)
    if o[0] != b[0]:
        disc_old.append(cid)
    print(f"{cid}: new={n} a119={o} base={b}")
print("classification differs from baseline -> new:", disc_new, " a119:", disc_old, " same set:", disc_new == disc_old)
print("case keys sample:", sorted(M["716946e8"]["C04"]))
