#!/usr/bin/env python
"""Stage B main driver: certify the rho=1 period-2 orbit of the frozen CUSUM.

Usage:
    run_stage_b.py [--backend float|arb] [--n-axis N] [--n-tri N]
                   [--center C] [--radius R] [--spacing D] [--bits B]
                   [--tag NAME]

Every operator solve is at a THIN reference error; the e-dependence is carried
analytically by the certified bound on ||G''|| (see `mesh_certificate.py`).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mesh_certificate as mc
from backends import ArbBackend, FloatBackend
from derivative import DerivativeIterator
from domain import (FROZEN_H, FROZEN_K, adaptive_edges,
                    assert_frozen_constants, build_partition)
from enclosure import Iterator, a_priori_bound
from killing import best_killing_bound
from profile_grid import axis_profiles
from transitions import attach_integrals, build_transitions

RESULTS = Path(__file__).resolve().parents[1] / "results"
Z_CUT = 12.0


def crude_gprime_bound(g_bound: float, resolvent: float, e_abs: float) -> float:
    """A priori ||G'||_inf, used only to size a sound warm start."""
    dr = 1.0 + e_abs * mc.INT_ABS_PHI1
    return resolvent * (mc.INT_ABS_PHI1 * g_bound + dr)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="arb", choices=["float", "arb"])
    ap.add_argument("--n-axis", type=int, default=400)
    ap.add_argument("--n-tri", type=int, default=60)
    ap.add_argument("--center", type=float, default=1.0367242887184211)
    ap.add_argument("--radius", type=float, default=0.010)
    ap.add_argument("--spacing", type=float, default=0.001)
    ap.add_argument("--bits", type=int, default=96)
    ap.add_argument("--profile-n", type=int, default=150)
    ap.add_argument("--tag", default="")
    ap.add_argument("--max-iter", type=int, default=400)
    args = ap.parse_args(argv[1:])

    assert_frozen_constants(FROZEN_K, FROZEN_H)
    t_start = time.time()
    c, rad, dz = args.center, args.radius, args.spacing
    n_steps = int(round(rad / dz))
    mesh = np.array([c + i * dz for i in range(-n_steps, n_steps + 1)])
    e_abs_max = float(np.max(np.abs(mesh))) + dz

    def make_backend():
        return (FloatBackend() if args.backend == "float"
                else ArbBackend(bits=args.bits))

    print(f"Stage B  backend={args.backend}  n_axis={args.n_axis} "
          f"n_tri={args.n_tri}  mesh={mesh.size} points "
          f"[{mesh[0]:.6f}, {mesh[-1]:.6f}] spacing {dz}", flush=True)

    (xp, gp), (xm, gm), g00 = axis_profiles(c, args.profile_n)
    ep = adaptive_edges(xp, gp, args.n_axis, 5.0)
    em = adaptive_edges(xm, gm, args.n_axis, 5.0)
    part = build_partition(n_axis=args.n_axis, axis_power=0, n_tri=args.n_tri,
                           axis_p_edges=ep, axis_m_edges=em)
    t0 = time.time()
    geom = build_transitions(part, None, mesh[0], mesh[-1], z_cut=Z_CUT)
    print(f"  partition {part.n_cells} cells, {geom['seg_src'].size} segments "
          f"(geometry {time.time() - t0:.0f}s)", flush=True)

    kill = best_killing_bound(float(mesh[0]), float(mesh[-1]))
    R = kill["resolvent_upper_bound"]
    M_apriori = a_priori_bound(e_abs_max, R)
    gp_crude = crude_gprime_bound(M_apriori, R, e_abs_max)
    inflate = gp_crude * dz * 1.05
    print(f"  killing n={kill['n']}  q>={kill['q_n_lower']:.6f}  "
          f"resolvent<= {R:.4f}   |G|<= {M_apriori:.2f}   "
          f"crude |G'|<= {gp_crude:.1f}  warm-start inflation {inflate:.3f}",
          flush=True)

    rows = []
    warm = None
    backend = make_backend()
    for i, e in enumerate(mesh):
        t1 = time.time()
        st = attach_integrals(geom, backend, float(e), float(e))
        total_mass = float(np.bincount(st.seg_src, st.mass_hi,
                                       minlength=st.n_cells).max())
        it = Iterator(st)
        start = None
        if warm is not None:
            start = (warm[0] - inflate, warm[1] + inflate)
        br = it.run(M_apriori, max_iter=args.max_iter, warm=start)
        warm = (br.lower, br.upper)
        di = DerivativeIterator(st, backend, br.lower, br.upper, R, Z_CUT)
        db = di.run(max_iter=args.max_iter)
        rows.append({
            "e": float(e),
            "G_lo": br.atom_lower, "G_hi": br.atom_upper,
            "G_width": br.atom_width,
            "G_sup_cells": mc.sup_norm(br.lower, br.upper),
            "Gp_lo": db.atom_lower, "Gp_hi": db.atom_upper,
            "Gp_width": db.atom_width,
            "Gp_sup_cells": mc.sup_norm(db.lower, db.upper),
            "H_lo": 2.0 * float(e) + br.atom_lower,
            "H_hi": 2.0 * float(e) + br.atom_upper,
            "F1p_lo": 1.0 + db.atom_lower, "F1p_hi": 1.0 + db.atom_upper,
            "iters_G": br.iterations, "iters_Gp": db.iterations,
            "max_total_mass": total_mass,
            "seconds": time.time() - t1,
        })
        r = rows[-1]
        print(f"  e={e:.6f}  H in [{r['H_lo']:+.6f},{r['H_hi']:+.6f}]  "
              f"F1' in [{r['F1p_lo']:+.4f},{r['F1p_hi']:+.4f}]  "
              f"mass {total_mass:.6f}  ({r['seconds']:.0f}s)", flush=True)

    cert = mc.assemble(
        mesh_e=[r["e"] for r in rows],
        G_lo=[r["G_lo"] for r in rows], G_hi=[r["G_hi"] for r in rows],
        Gp_lo=[r["Gp_lo"] for r in rows], Gp_hi=[r["Gp_hi"] for r in rows],
        G_sup_cells=[r["G_sup_cells"] for r in rows],
        Gp_sup_cells=[r["Gp_sup_cells"] for r in rows],
        resolvent=R, backend_name=backend.name,
        certified_backend=backend.certified,
        precision_bits=getattr(backend, "bits", None),
        grid={"n_axis": args.n_axis, "n_tri": args.n_tri,
              "n_cells": part.n_cells, "n_segments": int(geom["seg_src"].size),
              "z_cut": Z_CUT, "profile_n": args.profile_n},
    )

    payload = {
        "stage": "B", "target": "rho=1 period-2 orbit, frozen CUSUM k=1/2 h=5 m=1",
        "arguments": vars(args), "killing": kill, "rows": rows,
        "certificate": cert.as_dict(),
        "a_priori_G_bound": M_apriori,
        "crude_Gprime_bound": gp_crude,
        "warm_start_inflation": inflate,
        "total_seconds": time.time() - t_start,
    }
    tag = args.tag or args.backend
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / f"stage_b_{tag}.json"
    out.write_text(json.dumps(payload, indent=2, default=float))

    print()
    print(f"  ||G||<= {cert.G_sup:.4f}   ||G'||_mesh <= {cert.Gprime_sup_mesh:.4f}"
          f"   ||G'||_I <= {cert.Gprime_sup_interval:.4f}"
          f"   ||G''||<= {cert.G_second_bound:.2f}"
          f"  (contraction {cert.contraction_factor:.4f})")
    print(f"  root interval I = [{cert.root_I_lo:.6f}, {cert.root_I_hi:.6f}]"
          f"   existence {cert.existence_certified}"
          f"   0 excluded {cert.zero_excluded}")
    print(f"  min H' over I = {cert.Hprime_min_over_I:+.4f}"
          f"   uniqueness {cert.uniqueness_certified}")
    print(f"  F1'(I) in [{cert.F1prime_I_lo:+.5f}, {cert.F1prime_I_hi:+.5f}]"
          f"   lambda2 in [{cert.lambda2_lo:.5f}, {cert.lambda2_hi:.5f}]"
          f"   |lambda2|<1 {cert.multiplier_certified}")
    print(f"  wrote {out}   total {payload['total_seconds']:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
