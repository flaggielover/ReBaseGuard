"""Stage 1 -- foundation: correspondence X1-X5, c_beta, burn-in, calibration.

Nothing here compares policies.  Its whole purpose is that every later number
is believable: the detector is bit-identical to P7's, convention A holds, the
harness reproduces P7's published in-control ARLs, the ARL-calibrated tolerance
radius is derived from P7's closed response curve rather than quoted, and the
SAW plug-in constants are fitted on TUNE seeds only.

    python experiments/stage1_foundation.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent / "p7_statistical_consequences" / "src"))

from rebaseguard_p6c.calibrate import c_beta                       # noqa: E402
from rebaseguard_p6c.chain import simulate_policy_chain            # noqa: E402
from rebaseguard_p6c.policy import ConstantPolicy                  # noqa: E402
from rebaseguard_p6c.runner import calibrate_saw                   # noqa: E402
from rebaseguard_p6c.saw import SawPolicy                          # noqa: E402
from rebaseguard_p6c.seeds import generator                        # noqa: E402
from rebaseguard_p7.chain import simulate_chain                    # noqa: E402

RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)
DETECTORS = ("cusum", "sr")
M_GRID = (1, 2, 3, 5)
BETAS = (0.75, 0.5, 0.25, 0.1)


def x1_bit_identity():
    """A constant policy must reproduce the frozen P7 chain exactly."""
    rows = []
    for det in DETECTORS:
        for m in M_GRID:
            for rho in (0.0, 0.25, 1.0):
                kw = dict(detector=det, n_rep=200, n_cycles=30, burn_in=5, e0=0.0)
                ref = simulate_chain(m=m, rho=rho,
                                     rng=np.random.default_rng(20260901), **kw)
                got = simulate_policy_chain(policy=ConstantPolicy(rho=rho, m=m),
                                            rng=np.random.default_rng(20260901),
                                            **kw)
                rows.append({
                    "detector": det, "m": m, "rho": rho,
                    "tau_identical": bool(np.array_equal(ref.tau, got.tau)),
                    "max_abs_e_diff": float(np.abs(ref.e_start - got.e_start).max()),
                })
    return rows


def x2_convention_a():
    """w = min(m, tau) with the TRUNCATED denominator, recomputed by hand."""
    rows = []
    for det in DETECTORS:
        for m in (3, 5):
            res = simulate_policy_chain(detector=det,
                                        policy=ConstantPolicy(rho=1.0, m=m),
                                        n_rep=2000, n_cycles=20, burn_in=0,
                                        e0=0.0, rng=np.random.default_rng(3))
            # e_{j+1} = 1.0 * (e_j + zbar_j) exactly when rho = 1
            lhs = res.e_start[:, 1:]
            rhs = (res.e_start + res.zbar)[:, :-1]
            trunc = (res.tau < m).mean()
            rows.append({"detector": det, "m": m,
                         "max_abs_update_residual": float(np.abs(lhs - rhs).max()),
                         "fraction_truncated_windows": float(trunc)})
    return rows


def x3_p7_reproduction(n_rep=5000, n_blocks=4):
    """Reproduce P7's published in-control ARL in all 8 families."""
    p7 = json.loads((ROOT.parent / "p7_statistical_consequences" / "results"
                     / "consequences.json").read_text())
    want = {(c["detector"], c["m"], round(c["rho"], 6)): c for c in p7["cells"]}
    rows = []
    for det in DETECTORS:
        for m in M_GRID:
            for rho in (0.0, 0.25, 0.5, 0.75, 1.0):
                key = (det, m, round(rho, 6))
                if key not in want:
                    continue
                ref = want[key]
                per_block = []
                for b in range(n_blocks):
                    rng = generator(family="eval", detector=det, m=m,
                                    policy_id=f"x3_rho{rho}", cell_tag="x3",
                                    block=b)
                    res = simulate_policy_chain(
                        detector=det, policy=ConstantPolicy(rho=rho, m=m),
                        n_rep=n_rep, n_cycles=ref["n_cycles"],
                        burn_in=ref["burn_in"], e0=0.0, rng=rng)
                    per_block.append(res.post(res.tau).mean(axis=1))
                arl = np.concatenate(per_block)
                est = float(arl.mean())
                se = float(arl.std(ddof=1) / np.sqrt(arl.size))
                lo, hi = ref["arl_boot_ci"]
                rows.append({
                    "detector": det, "m": m, "rho": rho,
                    "p6_arl": est, "p6_se": se, "p6_n_rep": int(arl.size),
                    "p7_arl": ref["arl"], "p7_ci": [lo, hi],
                    "z_vs_p7": float((est - ref["arl"])
                                     / np.hypot(se, ref["arl_se"])),
                    "p6_ci_overlaps_p7_ci": bool(
                        (est + 1.96 * se) >= lo and (est - 1.96 * se) <= hi),
                    "p6_ref_rms": float(np.sqrt(
                        (res.post(res.e_start) ** 2).mean())),
                    "p7_ref_rms": ref["ref_rms"],
                })
    return rows


def derive_c_beta():
    return {det: {str(b): c_beta(det, b) for b in BETAS} for det in DETECTORS}


def calibration():
    out = {}
    for det in DETECTORS:
        for m in M_GRID:
            r = calibrate_saw(detector=det, m=m, k=m, family="tune",
                              n_rep=800, n_cycles=200, burn_in=20,
                              max_iter=6, tol=5e-3)
            c = r["calib"]
            # definitive constants from one large final pass under the fixed point
            rng = generator(family="tune", detector=det, m=m,
                            policy_id="calib_big", cell_tag="calib")
            big = simulate_policy_chain(
                detector=det, policy=SawPolicy(c, k=m, mode="full"),
                n_rep=4000, n_cycles=150, burn_in=20, e0=0.0, rng=rng)
            from rebaseguard_p6c.calibrate import fit_from_samples
            from rebaseguard_p6c.runner import _collect
            zb, tau, w, rbar = _collect(big, m)
            final = fit_from_samples(zbar=zb, tau=tau, w=w, rbar=rbar,
                                     detector=det, m=m, k=m, seed_family="tune",
                                     iterations=c.iterations, converged=c.converged)
            v = final.v_hat(zb, tau, w)
            nu = 1.0 / m
            v_bar = float(v.mean())
            q = nu * v / (v + nu)
            out[f"{det}_m{m}"] = {
                "fixed_point": c.to_dict(),
                "final": final.to_dict(),
                "drift": {kk: float(getattr(final, kk) - getattr(c, kk))
                          for kk in ("g0", "g1", "s0", "s1")},
                "n_final": int(zb.size),
                "v_bar": v_bar, "v_sd": float(v.std()),
                "rho_flat": float(nu / (v_bar + nu)),
                "jensen_gap": float(nu * v_bar / (v_bar + nu) - q.mean()),
                "jensen_gap_rel": float(1.0 - q.mean() / (nu * v_bar / (v_bar + nu))),
                "trace": r["trace"],
                "g0_no_tau": r["g0_no_tau"], "s0_no_tau": r["s0_no_tau"],
                "s1_no_tau": r["s1_no_tau"],
                "frac_truncated": float((w < m).mean()),
            }
    return out


def main():
    t0 = time.time()
    out = {"note": "P6 Stage 1 -- foundation.  No policy comparison here."}
    out["x1_bit_identity"] = x1_bit_identity()
    print("X1 done", flush=True)
    out["x2_convention_a"] = x2_convention_a()
    print("X2 done", flush=True)
    out["c_beta"] = derive_c_beta()
    print("c_beta done", flush=True)
    out["x3_p7_reproduction"] = x3_p7_reproduction()
    print("X3 done", flush=True)
    (RESULTS / "correspondence.json").write_text(json.dumps(out, indent=1))
    cal = calibration()
    (RESULTS / "calibration.json").write_text(json.dumps(cal, indent=1))
    print("calibration done", flush=True)
    out["seconds"] = time.time() - t0
    (RESULTS / "correspondence.json").write_text(json.dumps(out, indent=1))

    ok1 = all(r["tau_identical"] and r["max_abs_e_diff"] < 1e-13
              for r in out["x1_bit_identity"])
    ok2 = all(r["max_abs_update_residual"] < 1e-12 for r in out["x2_convention_a"])
    n3 = sum(r["p6_ci_overlaps_p7_ci"] for r in out["x3_p7_reproduction"])
    print(f"X1 all-pass={ok1}  X2 all-pass={ok2}  "
          f"X3 overlap {n3}/{len(out['x3_p7_reproduction'])}  "
          f"max|z|={max(abs(r['z_vs_p7']) for r in out['x3_p7_reproduction']):.2f}")
    print(f"total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
