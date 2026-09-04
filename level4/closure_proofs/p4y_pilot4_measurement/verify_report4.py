#!/usr/bin/env python3
"""Re-derive every headline figure in PILOT4_REPORT.md from the result JSON."""

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

from p4y_pilot4.addressing4 import audit_reachable_domain  # noqa: E402
from p4y_pilot4.design4 import (  # noqa: E402
    ACCURACY_FACTOR, BLOCK_SIZES, BREF_GRID, C_PREFIX, C_SPLIT,
    MAX_PRODUCTION_REFERENCE_HOURS, MAX_TOP1_SHARE, MAX_TOP5_SHARE,
    PILOT4_CPU_CAP_HOURS, R_REFERENCE_DRAWS, TARGET_PROBABILITY,
    reachable_addresses,
)

PREREG = "783151b5417c410d7aecc2e924cc62e2980463a9"
failures: list[str] = []


def load(n):
    p = R / f"{n}.json"
    return json.loads(p.read_text()) if p.exists() else None


def chk(label, ok, detail=""):
    print(("OK   " if ok else "FAIL ") + label + (f"  {detail}" if detail else ""))
    if not ok:
        failures.append(label)


master, ref, gate = load("master"), load("reference"), load("gate")
txt = (ROOT / "PILOT4_REPORT.md").read_text()

# ------------------------------------------------------------- freeze order
tree = subprocess.run(
    ["git", "ls-tree", "-r", "--full-tree", "--name-only", PREREG],
    cwd=ROOT, capture_output=True, text=True).stdout
own = [l for l in tree.splitlines() if "p4y_pilot4_measurement/" in l]
chk("freeze-commit listing is non-empty", len(own) >= 10, f"{len(own)} files")
chk("freeze commit contains NO result file",
    not any("/results/" in l for l in own),
    "; ".join(l for l in own if "/results/" in l) or "none")
chk("freeze commit contains the preregistration",
    any(l.endswith("PILOT4_PREREGISTRATION.md") for l in own))
chk("report cites the preregistration hash", PREREG in txt)

# --------------------------------------------------------------- frozen spec
chk("accuracy factor is 1.25", ACCURACY_FACTOR == 1.25)
chk("target probability is 0.90", TARGET_PROBABILITY == 0.90)
chk("R = 29 gives a CP lower bound of 0.9019 at 29/29",
    R_REFERENCE_DRAWS == 29 and abs(0.05 ** (1 / 29) - 0.9019) < 5e-5)
chk("block-size grid is the frozen one",
    BLOCK_SIZES == (250_000, 1_000_000, 4_000_000))

# ---------------------------------------------------------------- addressing
aud = audit_reachable_domain(reachable_addresses())
chk("frozen address domain is collision-free",
    aud["addresses"] == aud["unique_seeds"], str(aud["addresses"]))
chk("campaign base is the Pilot-4 one", aud["min_seed"] == 12_310_000_000)

# ----------------------------------------------------------------- benchmark
if master:
    chk("master phase did not STOP", master["stopped"] is None)
    for s in master["strata"]:
        for b, row in s["by_block_size"].items():
            c = row["admissible_checks"]
            recomputed = {
                "disjoint_split": row["independent_pool_spread"] <= C_SPLIT,
                "growing_prefix": (1 / C_PREFIX) <= row["prefix_full_over_half"]
                                  <= C_PREFIX,
                "extreme_top1": row["concentration"]["top1"] <= MAX_TOP1_SHARE,
                "extreme_top5": row["concentration"]["top5"] <= MAX_TOP5_SHARE,
            }
            chk(f"{s['stratum']}/{b}: admissibility re-derives", c == recomputed)
            chk(f"{s['stratum']}/{b}: verdict matches its checks",
                row["benchmark_admissible"] == all(c.values()),
                "ADMISSIBLE" if row["benchmark_admissible"] else "REJECTED")

# ------------------------------------------------------------------- gate
if gate:
    chk("gate records whether any block size has an admissible benchmark",
        "any_admissible_block_size" in gate,
        str(gate.get("any_admissible_block_size")))
    if ref and "candidates" in gate:
        for r in gate["candidates"]:
            chk(f"({r['block_paths']},{r['bref']}) affordability re-derives",
                r["criteria"]["E_affordable"]
                == (r["production_reference_hours"]
                    <= MAX_PRODUCTION_REFERENCE_HOURS))
        sel = gate.get("selected")
        chk("selection is consistent with the frozen criteria",
            (sel is None) == (not any(r["selectable"]
                                      for r in gate["candidates"])),
            str(sel))

# ---------------------------------------------------------------- budget
if master and ref:
    total = master["cpu_hours"] + ref["cpu_hours"]
    chk("cumulative CPU inside the frozen cap",
        total < PILOT4_CPU_CAP_HOURS, f"{total:.4f} / {PILOT4_CPU_CAP_HOURS}")
    chk("no STOP fired in either phase",
        master["stopped"] is None and ref["stopped"] is None)

print()
if failures:
    print(f"{len(failures)} CHECK(S) FAILED")
    sys.exit(1)
print("ALL CHECKS PASS")
