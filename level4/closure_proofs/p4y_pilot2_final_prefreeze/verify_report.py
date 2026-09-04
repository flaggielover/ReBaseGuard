#!/usr/bin/env python3
"""Re-derive every headline figure in PILOT2_REPORT.md from the result JSON.

A report is only as good as the fact that nothing in it was transcribed by
hand.  Exits non-zero on any mismatch.
"""

from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent / "p4y_precision_governance_pilot" / "src"))
R = ROOT / "results"

from p4y_pilot2.addressing import audit_reachable_domain  # noqa: E402
from p4y_pilot2.project import project  # noqa: E402
from p4y_pilot2.strata import reachable_addresses  # noqa: E402

rep = json.loads((R / "report.json").read_text())
cal = json.loads((R / "calibration.json").read_text())
des = json.loads((R / "design.json").read_text())
val = json.loads((R / "validation.json").read_text())
txt = (ROOT / "PILOT2_REPORT.md").read_text()

failures: list[str] = []


def chk(label: str, ok: bool, detail: str = "") -> None:
    print(("OK   " if ok else "FAIL ") + label + (f"  {detail}" if detail else ""))
    if not ok:
        failures.append(label)


# ------------------------------------------------------------- freeze ordering
head = subprocess.run(["git", "rev-parse", "ff688ec"], cwd=ROOT,
                      capture_output=True, text=True).stdout.strip()
chk("preregistration hash resolves",
    head == "ff688eccf6d4d8de025b10cfade967e70a0694fa", head)
# --full-tree, so paths are repo-relative rather than relative to cwd; without
# it the filter below matches nothing and the "no result file" check passes
# vacuously.
tree = subprocess.run(
    ["git", "ls-tree", "-r", "--full-tree", "--name-only", "ff688ec"],
    cwd=ROOT, capture_output=True, text=True).stdout
own = [ln for ln in tree.splitlines() if "p4y_pilot2_final_prefreeze/" in ln]
chk("the freeze-commit listing is non-empty (the check is not vacuous)",
    len(own) >= 15, f"{len(own)} files")
chk("the freeze commit contains NO result file",
    not any("/results/" in ln for ln in own),
    "; ".join(ln for ln in own if "/results/" in ln) or "none")
chk("the freeze commit contains the preregistration",
    any(ln.endswith("PILOT2_PREREGISTRATION.md") for ln in own))
chk("the freeze commit contains the rule, auditor and strata",
    all(any(ln.endswith(f"src/p4y_pilot2/{n}.py") for ln in own)
        for n in ("rule", "audit", "strata", "addressing")))

# ----------------------------------------------------------------- selection
chk("no kappa/cap pair was selectable", rep["selected"] is None)
chk("selection log records both kappas as unselectable",
    sum("NO SELECTABLE CAP" in ln for ln in rep["selection_log"]) == 2)

# ------------------------------------------------------------- primary endpoint
vc = rep["validation_curve"]
pts = [vc[k][m] for k in vc for m in vc[k]]
chk("472 validation replicates per point",
    all(p["replicates"] == 472 for p in pts))
chk("valid-disposition rate is 1.0000 at every point",
    all(p["valid_rate"] == 1.0 for p in pts))
chk("zero invalid dispositions anywhere", all(p["invalid"] == 0 for p in pts))
chk("valid-disposition CP lower bound 0.9937",
    all(abs(p["valid_lower"] - 0.9937) < 5e-5 for p in pts),
    f"{pts[0]['valid_lower']:.6f}")
chk("valid-disposition bound meets delta = 0.95",
    all(p["valid_lower"] >= 0.95 for p in pts))

best = vc["kappa_B_0.5"]["12"]
chk("best pair attainment 0.9301", abs(best["attainment_rate"] - 0.9301) < 5e-5,
    f"{best['attainment_rate']:.4f}")
chk("best pair attainment lower bound 0.9076",
    abs(best["attainment_lower"] - 0.9076) < 5e-5, f"{best['attainment_lower']:.4f}")
chk("best pair PRECISION_LIMITED 0.0699",
    abs(best["precision_limited_rate"] - 0.0699) < 5e-5,
    f"{best['precision_limited_rate']:.4f}")
chk("attainment floor 0.95 NOT met", best["attainment_rate"] < 0.95)
chk("PRECISION_LIMITED ceiling 0.05 NOT met",
    best["precision_limited_rate"] > 0.05)

# ------------------------------------------------------------------- kappa
worse = 0
for m in ("2", "3", "4", "6", "8", "12"):
    a, b = vc["kappa_A_0.3197"][m], vc["kappa_B_0.5"][m]
    if not (b["attainment_rate"] > a["attainment_rate"]
            and b["precision_limited_rate"] < a["precision_limited_rate"]):
        worse += 1
chk("kappa_B dominates kappa_A at every cap from 2x up", worse == 0)

# ------------------------------------------------------------------ cost
proj = project(mean_multiplier=best["mean_multiplier"],
               tail_multiplier=best["q95_multiplier"], baseline_multiplier=1.0)
chk("q95 multiplier 4.374", abs(best["q95_multiplier"] - 4.3739) < 1e-3,
    f"{best['q95_multiplier']:.4f}")
chk("projected total conservative 108.25 h",
    abs(proj["projected_total_conservative"] - 108.2507) < 1e-2,
    f"{proj['projected_total_conservative']:.2f}")
chk("projected max-config conservative 81.35 h",
    abs(proj["projected_max_config_conservative"] - 81.3516) < 1e-2,
    f"{proj['projected_max_config_conservative']:.2f}")
chk("total cap feasibility FAIL", proj["total_cap_feasibility"] == "FAIL")
chk("per-config cap feasibility FAIL", proj["per_config_cap_feasibility"] == "FAIL")

# ----------------------------------------------------------------- addressing
aud = audit_reachable_domain(reachable_addresses())
chk("frozen reachable domain 1355 addresses, all unique",
    aud["addresses"] == aud["unique_seeds"] == 1355, str(aud["addresses"]))
chk("seed range starts at the Pilot-2 campaign base",
    aud["min_seed"] == 6_310_000_000)

# ------------------------------------------------------------- calibration
alphas = {c["cell"]: c["min_block_mean_alpha"] for c in cal["cells"]}
chk("block-mean Hill alpha above the 2.5 STOP floor on every cell",
    all(v > 2.5 for v in alphas.values()),
    " ".join(f"{k}={v:.2f}" for k, v in alphas.items()))
chk("calibration did not STOP", cal["stopped"] is None)

# ------------------------------------------------------------------- budget
total = (cal["cpu_hours"] + des["cpu_hours"] + val["cpu_hours"])
chk("cumulative CPU 0.5768 h, inside the 3.0 h cap",
    abs(total - 0.5768) < 5e-4 and total < 3.0, f"{total:.4f}")
chk("no STOP fired in any phase",
    cal["stopped"] is None and des["stopped"] is None and val["stopped"] is None)

# ---------------------------------------------------- per-stratum floor failure
ps = rep["validation_curve_per_stratum"]["kappa_B_0.5"]["12"]
below = {k: v["attainment_rate"] for k, v in ps.items()
         if v["attainment_rate"] < 0.90}
chk("three heavy strata fail the 0.90 per-stratum floor at 12x",
    len(below) == 3 and all(k.startswith("H/") for k in below),
    " ".join(f"{k}={v:.3f}" for k, v in sorted(below.items())))
chk("every light-tail stratum attains 1.000 at the smallest cap",
    all(v["attainment_rate"] == 1.0
        for k, v in rep["validation_curve_per_stratum"]["kappa_B_0.5"]["1.5"].items()
        if k.startswith("L/")))

# ------------------------------------------------------------- report citations
for token in ("0.9937", "0.9301", "0.0699", "1.0000", "108.25", "81.35",
              "0.5768", "1 355", "8 801", "2 200 250 000", "4.374"):
    chk(f"report cites {token!r}", token in txt)

print()
if failures:
    print(f"{len(failures)} CHECK(S) FAILED")
    sys.exit(1)
print("ALL CHECKS PASS")
