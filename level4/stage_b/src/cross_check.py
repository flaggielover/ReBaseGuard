#!/usr/bin/env python
"""B8 — independent cross-checks of the Stage B certificate.

Route B is not a re-run of Route A with different constants.  It certifies
G at the REFLECTED reference error -e and uses the proved odd symmetry
(Lemma L3) to compare: G(-e) must equal -G(e).  At e = -1.0367 the drift
pushes the PLUS arm, so the reflected run exercises the mirror half of the
state space and a different part of the grid entirely.  A bug that is not
symmetric under the arm swap shows up here.

The remaining comparisons are consistency checks against non-rigorous work
(Stage A Monte Carlo, the Claude Science Bellman branch) and are labelled as
such: they cannot support the certificate, only contradict it.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "level_4_theory_numerics"))

from backends import ArbBackend
from derivative import DerivativeIterator
from domain import adaptive_edges, build_partition
from enclosure import Iterator, a_priori_bound
from killing import best_killing_bound
from profile_grid import axis_profiles
from transitions import build_transitions

RESULTS = Path(__file__).resolve().parents[1] / "results"
SCIENCE = Path(__file__).resolve().parents[3] / "level_4_theory_numerics"
E_STAR = 1.0367242887184211


def certify_at(e, *, n_axis=200, n_tri=32, bits=96):
    bk = ArbBackend(bits=bits)
    (xp, gp), (xm, gm), _ = axis_profiles(abs(e), 150)
    if e < 0:                      # reflected run: swap the two axis profiles
        gp, gm = gm, gp
    ep = adaptive_edges(xp, gp, n_axis, 5.0)
    em = adaptive_edges(xm, gm, n_axis, 5.0)
    part = build_partition(n_axis=n_axis, axis_power=0, n_tri=n_tri,
                           axis_p_edges=ep, axis_m_edges=em)
    st = build_transitions(part, bk, float(e), float(e))
    kill = best_killing_bound(float(e), float(e))
    m0 = a_priori_bound(abs(e), kill["arl_upper_bound"])
    br = Iterator(st).run(m0, max_iter=300)
    db = DerivativeIterator(st, bk, br.lower, br.upper,
                            kill["resolvent_upper_bound"], 12.0).run(max_iter=300)
    return {"e": float(e), "G_lo": br.atom_lower, "G_hi": br.atom_upper,
            "Gp_lo": db.atom_lower, "Gp_hi": db.atom_upper,
            "F1p_lo": 1.0 + db.atom_lower, "F1p_hi": 1.0 + db.atom_upper}


def read_science_branch():
    rows = []
    for line in (SCIENCE / "period2_branch.csv").read_text().splitlines()[1:]:
        parts = line.split(",")
        rows.append({"rho": float(parts[0]), "e_star": float(parts[1]),
                     "F1p": float(parts[2]), "mult": float(parts[3])})
    return rows


def main() -> int:
    t0 = time.time()
    out: dict = {"checks": []}

    print("Route A: certified enclosure at +e*", flush=True)
    a = certify_at(E_STAR)
    print(f"  G(+e*) in [{a['G_lo']:.8f}, {a['G_hi']:.8f}]", flush=True)

    print("Route B: certified enclosure at -e*, compared through Lemma L3",
          flush=True)
    b = certify_at(-E_STAR)
    print(f"  G(-e*) in [{b['G_lo']:.8f}, {b['G_hi']:.8f}]", flush=True)

    # L3: G(-e) = -G(e), so -G(-e) must overlap G(e)
    refl_lo, refl_hi = -b["G_hi"], -b["G_lo"]
    overlap = not (refl_hi < a["G_lo"] or refl_lo > a["G_hi"])
    out["checks"].append({
        "check": "reflection_symmetry_route_B",
        "route_A_G": [a["G_lo"], a["G_hi"]],
        "route_B_minus_G_at_minus_e": [refl_lo, refl_hi],
        "overlap": bool(overlap),
        "passed": bool(overlap),
        "note": "Lemma L3 requires G(-e) = -G(e); the two certified brackets "
                "must intersect. The reflected run drives the opposite CUSUM "
                "arm, so it exercises the mirror half of the state space.",
    })
    print(f"  -G(-e*) in [{refl_lo:.8f}, {refl_hi:.8f}]  overlap: {overlap}",
          flush=True)

    # F_1' is even under L3
    fp_refl_lo, fp_refl_hi = b["F1p_lo"], b["F1p_hi"]
    fp_overlap = not (fp_refl_hi < a["F1p_lo"] or fp_refl_lo > a["F1p_hi"])
    out["checks"].append({
        "check": "derivative_evenness_route_B",
        "route_A_F1p": [a["F1p_lo"], a["F1p_hi"]],
        "route_B_F1p_at_minus_e": [fp_refl_lo, fp_refl_hi],
        "passed": bool(fp_overlap),
        "note": "F_1' is even for an odd differentiable F_1 (Lemma L4/L7).",
    })
    print(f"  F1'(+e*) in [{a['F1p_lo']:.5f},{a['F1p_hi']:.5f}]  "
          f"F1'(-e*) in [{fp_refl_lo:.5f},{fp_refl_hi:.5f}]  "
          f"overlap: {fp_overlap}", flush=True)

    # consistency with non-rigorous prior work
    science = read_science_branch()
    rho1 = [r for r in science if r["rho"] == 1.0][0]
    out["checks"].append({
        "check": "claude_science_bellman",
        "evidence_class": "NON-RIGOROUS (midpoint-collocation Bellman solver)",
        "science_F1p": rho1["F1p"],
        "certified_F1p": [a["F1p_lo"], a["F1p_hi"]],
        "passed": bool(a["F1p_lo"] <= rho1["F1p"] <= a["F1p_hi"]),
        "science_e_star": rho1["e_star"], "science_multiplier": rho1["mult"],
    })
    out["checks"].append({
        "check": "claude_science_G_at_e_star",
        "evidence_class": "NON-RIGOROUS",
        "science_G": -2.0 * E_STAR,
        "certified_G": [a["G_lo"], a["G_hi"]],
        "passed": bool(a["G_lo"] <= -2.0 * E_STAR <= a["G_hi"]),
        "note": "at the Science root, H = 2e + G = 0 exactly, so G = -2 e*.",
    })

    # Stage A Monte Carlo (Gate 4.2 full run)
    stage_a = {"e_star": 1.03695, "e_star_se": 0.00037,
               "F1prime": 0.5954, "multiplier": 0.3545,
               "source": "level4 Gate 4.2 full run, STRONG-CANDIDATE at rho=1"}
    out["checks"].append({
        "check": "stage_a_monte_carlo",
        "evidence_class": "NON-RIGOROUS (Monte Carlo)",
        "stage_a": stage_a,
        "certified_F1p": [a["F1p_lo"], a["F1p_hi"]],
        "passed": bool(a["F1p_lo"] <= stage_a["F1prime"] <= a["F1p_hi"]),
    })

    out["route_A"] = a
    out["route_B"] = b
    out["science_branch"] = science
    out["seconds"] = time.time() - t0
    out["n_passed"] = sum(c["passed"] for c in out["checks"])
    out["n_checks"] = len(out["checks"])
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "cross_check.json").write_text(json.dumps(out, indent=2,
                                                         default=float))
    print(f"\n  {out['n_passed']}/{out['n_checks']} cross-checks passed "
          f"({out['seconds']:.0f}s)")
    for c in out["checks"]:
        print(f"    [{'PASS' if c['passed'] else 'FAIL'}] {c['check']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
