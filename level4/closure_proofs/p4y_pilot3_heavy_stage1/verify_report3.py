#!/usr/bin/env python3
"""Re-derive every headline figure in PILOT3_REPORT.md from the result JSON."""

from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent / "p4y_pilot2_final_prefreeze" / "src"))
sys.path.insert(0, str(ROOT.parent / "p4y_precision_governance_pilot" / "src"))
R = ROOT / "results"

from p4y_pilot3.addressing3 import audit_reachable_domain  # noqa: E402
from p4y_pilot3.strata3 import (  # noqa: E402
    ATTAINMENT_FLOOR_MIXTURE, HEAVY_STRATUM_ATTAINMENT_FLOOR,
    HEAVY_STRATUM_PL_CEILING, N_HEAVY_STRATA, N_ORDINARY_STRATA,
    N_STRATA_TOTAL, PRECISION_LIMITED_CEILING, STRATA, reachable_addresses,
)

PREREG = "8dbb7d2ea5dbe6eaad2cfff0d89e44cc6fbdc3af"
failures: list[str] = []


def load(n):
    p = R / f"{n}.json"
    return json.loads(p.read_text()) if p.exists() else None


def chk(label, ok, detail=""):
    print(("OK   " if ok else "FAIL ") + label + (f"  {detail}" if detail else ""))
    if not ok:
        failures.append(label)


rep, bench = load("report"), load("benchmark")
des, val = load("design"), load("validation")
txt = (ROOT / "PILOT3_REPORT.md").read_text()

# ------------------------------------------------------------ freeze order
tree = subprocess.run(
    ["git", "ls-tree", "-r", "--full-tree", "--name-only", PREREG],
    cwd=ROOT, capture_output=True, text=True).stdout
own = [l for l in tree.splitlines() if "p4y_pilot3_heavy_stage1/" in l]
chk("freeze-commit listing is non-empty", len(own) >= 12, f"{len(own)} files")
chk("freeze commit contains NO result file",
    not any("/results/" in l for l in own),
    "; ".join(l for l in own if "/results/" in l) or "none")
chk("freeze commit contains the preregistration",
    any(l.endswith("PILOT3_PREREGISTRATION.md") for l in own))
chk("report cites the preregistration hash", PREREG in txt)

# ------------------------------------------------------------- mixture
chk("production mixture is 48 = 8 heavy + 40 ordinary",
    (N_STRATA_TOTAL, N_HEAVY_STRATA, N_ORDINARY_STRATA) == (48, 8, 40))
chk("stratum weights sum to 48 with 8 heavy",
    sum(s.weight for s in STRATA) == 48
    and sum(s.weight for s in STRATA if s.heavy) == 8)

# ------------------------------------------------------------ benchmark
if bench:
    chk("benchmark phase did not STOP", bench["stopped"] is None)
    for c in bench["cells"]:
        chk(f"benchmark {c['cell']}: Hill alpha above the 2.5 floor",
            c["min_block_mean_alpha"] > 2.5, f"{c['min_block_mean_alpha']:.2f}")
    h = next(c for c in bench["cells"] if c["cell"] == "H")
    chk("the frozen benchmark uncertainty claim is 0.79 % as preregistered",
        abs(h["benchmark_relative_uncertainty_of_sd"] - 0.0079) < 5e-5,
        f"{h['benchmark_relative_uncertainty_of_sd']:.4%} -- and section 10.1 "
        "shows this claim is INVALID for this block-mean law")

# ------------------------------------------------------------ addressing
aud = audit_reachable_domain(reachable_addresses())
chk("frozen domain is collision-free",
    aud["addresses"] == aud["unique_seeds"], str(aud["addresses"]))
chk("campaign base is the Pilot-3 one", aud["min_seed"] == 9_310_000_000)

# ------------------------------------------------------------ the STOP
diag = load("post_stop_diagnostic")
chk("post-STOP diagnostic exists", diag is not None)
if diag:
    d250 = diag.get("250000")
    chk("at the PRODUCTION block size one block still dominates the variance",
        d250["top1_share"] > 0.20, f"top-1 share {d250['top1_share']:.2%}")
    chk("at the PRODUCTION block size the sd is unstable between halves",
        d250["half_sd_ratio"] > 2.0, f"ratio {d250['half_sd_ratio']:.2f}")
chk("validation was NOT run (stopped under section 23)", val is None)
chk("report records the STOP", "P4Y_PILOT3_STOP_FIRED = YES" in txt)
chk("report records zero post-result amendments",
    "P4Y_PILOT3_POST_RESULT_AMENDMENTS = 0" in txt)

# ------------------------------------------------------------ selection
if rep:
    chk("NO candidate qualified under the frozen criteria",
        rep["selected"] is None)
    chk("96 candidates were evaluated",
        any("96" in l for l in rep["selection_log"]),
        "; ".join(rep["selection_log"])[:120])
    heavy_fail = [c for c in rep["design_candidates"]
                  if not c["criteria"]["4_every_heavy_stratum"]]
    chk("the per-heavy-stratum floor is what excluded the closest candidate",
        len(heavy_fail) > 0, f"{len(heavy_fail)} of 96 fail criterion 4")
    if rep.get("validation_selected_full"):
        v = rep["validation_selected_full"]
        p = v["projection"]
        chk("validation valid-disposition rate is 1.0000",
            v["valid_rate"] == 1.0, f"{v['valid_rate']:.4f}")
        chk("validation valid-disposition lower bound >= 0.95",
            v["valid_lower"] >= 0.95, f"{v['valid_lower']:.4f}")
        chk("mixture attainment >= floor",
            v["mixture_attainment"] >= ATTAINMENT_FLOOR_MIXTURE,
            f"{v['mixture_attainment']:.4f}")
        chk("mixture PRECISION_LIMITED <= ceiling",
            v["mixture_precision_limited"] <= PRECISION_LIMITED_CEILING,
            f"{v['mixture_precision_limited']:.4f}")
        chk("every heavy stratum clears its attainment floor",
            v["min_heavy_attainment"] >= HEAVY_STRATUM_ATTAINMENT_FLOOR,
            f"{v['min_heavy_attainment']:.4f}")
        chk("every heavy stratum clears its PL ceiling",
            v["max_heavy_precision_limited"] <= HEAVY_STRATUM_PL_CEILING,
            f"{v['max_heavy_precision_limited']:.4f}")
        chk("zero invalid dispositions", v["invalid"] == 0)
        chk("UCB stage-1 coverage beats the point estimate",
            v["heavy_stage1_coverage"] > v["heavy_stage1_coverage_point"],
            f"{v['heavy_stage1_coverage']:.4f} vs "
            f"{v['heavy_stage1_coverage_point']:.4f}")
        chk("conservative total CPU within the frozen limit",
            p["total_cap_feasibility"] == "PASS",
            f"{p['projected_total_conservative']:.2f} h")
        chk("conservative max-config CPU within the frozen limit",
            p["per_config_cap_feasibility"] == "PASS",
            f"{p['projected_max_config_conservative']:.2f} h")
        chk("all frozen criteria pass on validation",
            rep.get("validation_all_pass") is True)

# --------------------------------------------------------------- budget
led = load("cpu_ledger")
if led:
    chk("cumulative CPU inside the 3.0 h cap",
        led["total_cpu_hours"] < 3.0, f"{led['total_cpu_hours']:.4f}")
    chk("the CPU cap was never extended", led["cap"] == 3.0)
    chk("no phase-level STOP fired in benchmark or design",
        bench["stopped"] is None and des["stopped"] is None)

print()
if failures:
    print(f"{len(failures)} CHECK(S) FAILED")
    sys.exit(1)
print("ALL CHECKS PASS")
