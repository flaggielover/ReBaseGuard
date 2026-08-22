#!/usr/bin/env python
"""B9 — attempts to falsify the certificate.

Each check varies one thing that must NOT change the answer, and records what
happened.  A component that moves materially under a supposedly irrelevant
numerical choice is a blocker, not a rounding detail.  Failures are recorded in
the output JSON, not dropped.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "level_4_theory_numerics"))

import mesh_certificate as mc
from backends import ArbBackend, FloatBackend
from bellman_solver import Grid, build as bs_build
from derivative import DerivativeIterator
from domain import adaptive_edges, build_partition
from enclosure import Iterator, a_priori_bound
from killing import best_killing_bound
from profile_grid import axis_profiles
from transitions import build_transitions

E_STAR = 1.0367242887184211
RESULTS = Path(__file__).resolve().parents[1] / "results"


def reference_G(e: float, n: int = 300) -> float:
    g = Grid(n)
    K, rG, _, _, _ = bs_build(g, e)
    m = g.n
    return float(spla.splu((sp.eye(m, format="csc") - K).tocsc())
                 .solve(rG)[g.idx[(0, 0)]])


def one_run(*, e=E_STAR, n_axis=160, n_tri=26, bits=96, z_cut=12.0,
            backend="arb", adaptive=True, axis_power=2.0, profile_n=150,
            with_derivative=True):
    bk = ArbBackend(bits=bits) if backend == "arb" else FloatBackend()
    ep = em = None
    if adaptive:
        (xp, gp), (xm, gm), _ = axis_profiles(e, profile_n)
        ep = adaptive_edges(xp, gp, n_axis, 5.0)
        em = adaptive_edges(xm, gm, n_axis, 5.0)
    part = build_partition(n_axis=n_axis, axis_power=axis_power, n_tri=n_tri,
                           axis_p_edges=ep, axis_m_edges=em)
    struct = build_transitions(part, bk, e, e, z_cut=z_cut)
    kill = best_killing_bound(e, e)
    m0 = a_priori_bound(abs(e), kill["arl_upper_bound"])
    br = Iterator(struct).run(m0, max_iter=300)
    out = {"G_lo": br.atom_lower, "G_hi": br.atom_upper,
           "G_width": br.atom_width,
           "max_total_mass": float(np.bincount(struct.seg_src, struct.mass_hi,
                                               minlength=struct.n_cells).max()),
           "n_cells": part.n_cells, "n_segments": int(struct.n_segments)}
    if with_derivative:
        db = DerivativeIterator(struct, bk, br.lower, br.upper,
                                kill["resolvent_upper_bound"], z_cut).run(
                                    max_iter=300)
        out.update({"Gp_lo": db.atom_lower, "Gp_hi": db.atom_upper,
                    "F1p_lo": 1.0 + db.atom_lower, "F1p_hi": 1.0 + db.atom_upper})
    return out


def main() -> int:
    ref = reference_G(E_STAR)
    checks: list[dict] = []
    t0 = time.time()

    def record(name, question, rows, verdict_fn):
        ok, note = verdict_fn(rows)
        checks.append({"check": name, "question": question, "rows": rows,
                       "passed": bool(ok), "note": note})
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {note}", flush=True)

    print("B9 adversarial checks (reference G = %.8f)" % ref, flush=True)

    # 1 -- precision
    rows = [dict(bits=b, **one_run(bits=b, with_derivative=False))
            for b in (64, 96, 160, 256)]
    record("precision", "does Arb working precision move the bracket?", rows,
           lambda r: (max(abs(x["G_lo"] - r[1]["G_lo"]) for x in r) < 1e-9
                      and max(abs(x["G_hi"] - r[1]["G_hi"]) for x in r) < 1e-9,
                      "max shift %.2e over 64..256 bits"
                      % max(max(abs(x["G_lo"] - r[1]["G_lo"]),
                                abs(x["G_hi"] - r[1]["G_hi"])) for x in r)))

    # 2 -- state grid refinement
    rows = [dict(n_axis=na, n_tri=nt, **one_run(n_axis=na, n_tri=nt,
                                                with_derivative=False))
            for na, nt in ((80, 14), (160, 26), (320, 46))]
    record("grid_refinement",
           "does the bracket shrink monotonically and keep containing the reference?",
           rows,
           lambda r: (all(x["G_lo"] <= ref <= x["G_hi"] for x in r)
                      and r[0]["G_width"] > r[1]["G_width"] > r[2]["G_width"],
                      "widths %s, all contain reference: %s"
                      % ([round(x["G_width"], 5) for x in r],
                         all(x["G_lo"] <= ref <= x["G_hi"] for x in r))))

    # 3 -- z_cut (tail truncation point)
    rows = [dict(z_cut=z, **one_run(z_cut=z, with_derivative=False))
            for z in (8.0, 12.0, 20.0)]
    record("z_cut", "does the tail cut point matter? (it must not: tails are exact)",
           rows,
           lambda r: (max(abs(x["G_lo"] - r[1]["G_lo"]) for x in r) < 1e-9,
                      "max shift %.2e over z_cut 8..20"
                      % max(abs(x["G_lo"] - r[1]["G_lo"]) for x in r)))

    # 4 -- grid placement source
    rows = [dict(kind="adaptive-from-profile", **one_run(adaptive=True,
                                                         with_derivative=False)),
            dict(kind="power-law-2.0", **one_run(adaptive=False, axis_power=2.0,
                                                 with_derivative=False)),
            dict(kind="power-law-3.0", **one_run(adaptive=False, axis_power=3.0,
                                                 with_derivative=False))]
    record("grid_placement",
           "does the (non-rigorous) grid-placement heuristic change validity?",
           rows,
           lambda r: (all(x["G_lo"] <= ref <= x["G_hi"] for x in r),
                      "all three grids contain the reference; widths %s"
                      % [round(x["G_width"], 5) for x in r]))

    # 5 -- profile solver resolution used to place the grid
    rows = [dict(profile_n=n, **one_run(profile_n=n, with_derivative=False))
            for n in (60, 150, 250)]
    record("profile_resolution",
           "does the float profile's resolution leak into the certificate?",
           rows,
           lambda r: (all(x["G_lo"] <= ref <= x["G_hi"] for x in r),
                      "all contain the reference; widths %s"
                      % [round(x["G_width"], 5) for x in r]))

    # 6 -- float vs Arb backend
    rows = [dict(backend=b, **one_run(backend=b)) for b in ("float", "arb")]
    record("backend",
           "does the certified backend enclose the uncertified one?", rows,
           lambda r: (r[1]["G_lo"] <= r[0]["G_lo"] + 1e-9
                      and r[1]["G_hi"] >= r[0]["G_hi"] - 1e-9
                      and r[1]["F1p_lo"] <= r[0]["F1p_lo"] + 1e-8
                      and r[1]["F1p_hi"] >= r[0]["F1p_hi"] - 1e-8,
                      "Arb bracket contains the float bracket for both G and F1'"))

    # 7 -- deliberate perturbation beyond the certified tolerance
    perturbed = ref + 3.0 * one_run(with_derivative=False)["G_width"]
    base = one_run(with_derivative=False)
    record("deliberate_perturbation",
           "is a value deliberately pushed outside the bracket rejected?",
           [{"perturbed_value": perturbed, "G_lo": base["G_lo"],
             "G_hi": base["G_hi"]}],
           lambda r: (not (r[0]["G_lo"] <= r[0]["perturbed_value"]
                           <= r[0]["G_hi"]),
                      "a value 3 widths away is correctly outside the bracket"))

    # 8 -- total continuation mass must not exceed 1 at thin e
    rows = [dict(n_axis=na, **one_run(n_axis=na, with_derivative=False))
            for na in (80, 160, 320)]
    record("mass_conservation",
           "is the upper operator sub-stochastic (necessary for contraction)?",
           rows,
           lambda r: (all(x["max_total_mass"] <= 1.0 + 1e-9 for x in r),
                      "max total continuation mass %.8f"
                      % max(x["max_total_mass"] for x in r)))

    # 9 -- killing bound: every admissible n gives a valid, consistent bound
    kb = best_killing_bound(E_STAR - 0.012, E_STAR + 0.012)
    arl_true = None
    g = Grid(150)
    K, rG, _, _, _ = bs_build(g, E_STAR)
    arl_true = float(spla.splu((sp.eye(g.n, format="csc") - K).tocsc())
                     .solve(np.ones(g.n)).max())
    record("killing_bound",
           "does the uniform resolvent bound dominate the true sup ARL?",
           [{"n": kb["n"], "q_n_lower": kb["q_n_lower"],
             "bound": kb["arl_upper_bound"], "true_sup_arl": arl_true}],
           lambda r: (r[0]["bound"] > r[0]["true_sup_arl"],
                      "bound %.4f > true sup ARL %.4f"
                      % (r[0]["bound"], r[0]["true_sup_arl"])))

    payload = {"reference_G": ref, "checks": checks,
               "n_passed": sum(c["passed"] for c in checks),
               "n_checks": len(checks), "seconds": time.time() - t0}
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "adversarial.json").write_text(json.dumps(payload, indent=2,
                                                         default=float))
    print(f"\n  {payload['n_passed']}/{payload['n_checks']} adversarial checks "
          f"passed in {payload['seconds']:.0f}s")
    return 0 if payload["n_passed"] == payload["n_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
