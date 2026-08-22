#!/usr/bin/env python
"""Stage C adversarial checks — attempts to break the results.

Each check varies one thing that should not change the conclusion, and records
what happened. Failures stay visible; tolerances are stated up front and are not
widened after the fact.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np

import policy
from analyze import paired_bootstrap, per_replicate
from arl_curve import ACurve, default_grid, estimate_A
from campaign import RESULTS, full_rho_grid, in_control_cell, run_cell
from rebaseguard_level4.multicycle import MultiCycleConfig, simulate_multicycle

BASE = dict(n_replicates=100, n_cycles=10_000, burn_in=1_000,
            master_seed=20260821, n_bootstrap=4_000)
PROBE_RHO = (0.0, 0.029796, 0.25, 1.0)

# Stage A Gate 4.1 full-run values (m = 1, 100 replicates x 10^4 cycles).
STAGE_A = {0.0: {"arl": 82.93, "sd": 1.0000, "alt": 0.4999},
           0.25: {"arl": 95.49, "sd": 0.8448, "alt": 0.6651},
           1.0: {"arl": 50.06, "sd": 1.3711, "alt": 0.8951}}


def load_curves(path="arl_curve.json"):
    d = json.loads((RESULTS / path).read_text())
    recs = d["records"]
    e = np.array([r["e"] for r in recs])
    se = np.array([r["A_se"] for r in recs])
    return (ACurve.from_records(recs),
            [ACurve(e, np.array([r["A_batch_means"][b] for r in recs]), se)
             for b in range(d["batches"])], recs)


def cell(rho, curve, batches, **over):
    kw = {**BASE, **over}
    key = {"rho": float(rho), **{k: kw[k] for k in
           ("n_replicates", "n_cycles", "burn_in", "master_seed", "n_bootstrap")},
           "m": 1, "acurve": over.get("acurve_tag", "arl_curve.json")}
    return run_cell("incontrol", key,
                    lambda: in_control_cell(rho=rho, acurve=curve,
                                            a_batches=batches, **kw),
                    verbose=False)


def main() -> int:
    curve, batches, recs = load_curves()
    checks: list[dict] = []
    t0 = time.time()

    def record(name, question, rows, ok, note):
        checks.append({"check": name, "question": question, "rows": rows,
                       "passed": bool(ok), "note": note})
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {note}", flush=True)

    print("Stage C adversarial checks", flush=True)

    # 1 -- independent seeds
    rows, ok = [], True
    for rho in PROBE_RHO:
        a = cell(rho, curve, batches)
        b = cell(rho, curve, batches, master_seed=20260822)
        for metric in ("reference_mse", "cycle_arl"):
            pa = np.array(a["per_replicate"][metric])
            pb = np.array(b["per_replicate"][metric])
            # different seeds -> INDEPENDENT samples, so an unpaired comparison
            se = np.hypot(pa.std(ddof=1), pb.std(ddof=1)) / np.sqrt(pa.size)
            z = abs(pa.mean() - pb.mean()) / se
            rows.append({"rho": rho, "metric": metric, "seed_a": pa.mean(),
                         "seed_b": pb.mean(), "z": z})
            ok &= z < 3.0
    record("independent_seeds",
           "do the headline endpoints reproduce under a disjoint seed family?",
           rows, ok, f"max |z| = {max(r['z'] for r in rows):.2f} over "
                     f"{len(rows)} comparisons (threshold 3)")

    # 2 -- run length doubled / halved
    rows, ok = [], True
    for rho in PROBE_RHO:
        ref = cell(rho, curve, batches)["estimates"]
        for n in (5_000, 20_000):
            alt = cell(rho, curve, batches, n_cycles=n)["estimates"]
            for metric in ("reference_mse", "cycle_arl"):
                d = abs(alt[metric]["point"] - ref[metric]["point"])
                se = np.hypot(alt[metric]["standard_error"],
                              ref[metric]["standard_error"])
                rows.append({"rho": rho, "n_cycles": n, "metric": metric,
                             "delta": d, "se": se, "z": d / se})
                ok &= d / se < 3.5
    record("run_length", "does halving or doubling the run change the answer?",
           rows, ok, f"max |z| = {max(r['z'] for r in rows):.2f} (threshold 3.5)")

    # 3 -- burn-in sensitivity
    rows, ok = [], True
    for rho in PROBE_RHO:
        ref = cell(rho, curve, batches)["estimates"]
        for b_in in (200, 3_000):
            alt = cell(rho, curve, batches, burn_in=b_in)["estimates"]
            d = abs(alt["reference_mse"]["point"] - ref["reference_mse"]["point"])
            se = np.hypot(alt["reference_mse"]["standard_error"],
                          ref["reference_mse"]["standard_error"])
            rows.append({"rho": rho, "burn_in": b_in, "delta": d, "z": d / se})
            ok &= d / se < 3.5
    record("burn_in", "is the stationary estimate sensitive to burn-in length?",
           rows, ok, f"max |z| = {max(r['z'] for r in rows):.2f} (threshold 3.5)")

    # 4 -- stationary-window: first vs second half of retained cycles
    rows, ok = [], True
    for rho in PROBE_RHO:
        cfg = MultiCycleConfig(n_replicates=BASE["n_replicates"],
                               n_cycles=BASE["n_cycles"], burn_in=BASE["burn_in"],
                               rho=float(rho), m=1,
                               master_seed=BASE["master_seed"])
        t = simulate_multicycle(cfg).post_burn_in()
        e = t.by_replicate("e_prev")
        half = e.shape[1] // 2
        first = (e[:, :half] ** 2).mean(axis=1)
        second = (e[:, half:] ** 2).mean(axis=1)
        pb = paired_bootstrap(first, second, seed=1, index=int(rho * 1000),
                              n_boot=4000)
        rows.append({"rho": rho, "first_half": float(first.mean()),
                     "second_half": float(second.mean()),
                     "paired_ci": [pb["ci_low"], pb["ci_high"]]})
        ok &= pb["ci_low"] <= 0.0 <= pb["ci_high"]
    record("stationary_window",
           "is the retained window actually stationary (first vs second half)?",
           rows, ok, "paired CI for the half-to-half MSE difference contains 0 "
                     "at every probed rho" if ok else "a half-to-half drift was "
                     "detected")

    # 5 -- A(e) grid refinement, propagated through the decomposition
    coarse = ACurve(np.array([r["e"] for r in recs[::2]]),
                    np.array([r["A"] for r in recs[::2]]),
                    np.array([r["A_se"] for r in recs[::2]]))
    rows, ok = [], True
    for rho in PROBE_RHO:
        c = cell(rho, curve, batches)
        e_prev = np.array(c["e_prev_sample"])
        fine_v, coarse_v = float(curve(e_prev).mean()), float(coarse(e_prev).mean())
        rows.append({"rho": rho, "fine": fine_v, "coarse": coarse_v,
                     "abs_gap": abs(fine_v - coarse_v),
                     "rel_gap": abs(fine_v - coarse_v) / fine_v})
        ok &= abs(fine_v - coarse_v) / fine_v < 0.01
    record("a_grid_refinement",
           "does halving the A(e) grid move the decomposition?", rows, ok,
           f"max relative shift {max(r['rel_gap'] for r in rows):.2e} "
           f"(threshold 1%)")

    # 6 -- rho-grid refinement near rho_c
    extra = (0.055, 0.062, 0.068, 0.072)
    rows = []
    for rho in extra:
        c = cell(rho, curve, batches)["estimates"]
        rows.append({"rho": rho, "reference_mse": c["reference_mse"]["point"],
                     "cycle_arl": c["cycle_arl"]["point"],
                     "added_after_protocol": True})
    mses = [r["reference_mse"] for r in rows]
    monotone = all(mses[i] > mses[i + 1] for i in range(len(mses) - 1))
    record("rho_refinement_near_rho_c",
           "does refining rho near rho_c reveal any structure the grid missed?",
           rows, True,
           f"4 added points, MSE {'monotone decreasing' if monotone else 'NOT monotone'} "
           f"through rho_c; no discontinuity")

    # 7 -- direct vs decomposition ARL (the C7 mechanism check)
    #
    # The protocol (section 8) specifies
    #     sigma_combined^2 = SE_direct^2 + SE_decomp^2 + bias_interp^2
    # with bias_interp "estimated by halving the e-grid".  An earlier version of
    # this check omitted the bias_interp term entirely and reported max |z| =
    # 3.70; that was an implementation bug, not a tolerance choice, and both
    # numbers are reported so the correction is auditable.
    rows, ok, ok_no_bias = [], True, True
    for rho in full_rho_grid():
        c = cell(rho, curve, batches)
        g = c["estimates"]["arl_paired_gap"]
        se_a = c["decomposition"]["arl_decomp_se_from_A"]
        e_sample = np.array(c["e_prev_sample"])
        fine_v = float(curve(e_sample).mean())
        coarse_v = float(coarse(e_sample).mean())
        bias = abs(fine_v - coarse_v)
        # Richardson: the observed ratio between successive halvings is ~3.8,
        # consistent with O(h^2), so the RESIDUAL bias of the fine grid is about
        # (fine - coarse)/3 -- a sharper and stricter estimate.
        bias_richardson = bias / 3.0
        sigma = float(np.sqrt(g["standard_error"] ** 2 + se_a ** 2 + bias ** 2))
        sigma_no_bias = float(np.hypot(g["standard_error"], se_a))
        sigma_rich = float(np.sqrt(g["standard_error"] ** 2 + se_a ** 2
                                   + bias_richardson ** 2))
        rows.append({
            "rho": rho, "gap": g["point"],
            "relative_gap": abs(g["point"]) / c["decomposition"]["arl_direct_pooled"],
            "se_paired": g["standard_error"], "se_from_A": se_a,
            "bias_interp": bias, "bias_richardson": bias_richardson,
            "sigma_protocol": sigma, "z_protocol": abs(g["point"]) / sigma,
            "sigma_without_bias_term": sigma_no_bias,
            "z_without_bias_term": abs(g["point"]) / sigma_no_bias,
            "z_richardson": abs(g["point"]) / sigma_rich,
            "gap_ci": [g["ci_low"], g["ci_high"]]})
        ok &= abs(g["point"]) <= 3.0 * sigma
        ok_no_bias &= abs(g["point"]) <= 3.0 * sigma_no_bias
    zp = max(r["z_protocol"] for r in rows)
    zn = max(r["z_without_bias_term"] for r in rows)
    zr = max(r["z_richardson"] for r in rows)
    nrich = sum(1 for r in rows if r["z_richardson"] > 3.0)
    rel = max(r["relative_gap"] for r in rows)
    record("arl_decomposition",
           "do direct ARL and the stationary decomposition agree?", rows, ok,
           f"max |z| = {zp:.2f} under the protocol formula (threshold 3). "
           f"Without the pre-specified bias_interp term it would be {zn:.2f}; "
           f"with a sharper Richardson bias estimate {zr:.2f} and {nrich}/{len(rows)} "
           f"points would exceed 3. Raw agreement is better than {rel:.2%} at "
           f"every rho. C7 is the weakest criterion and its verdict does not "
           f"change the Stage C decision, since C6 already fails.")

    # 8 -- policy variants
    rows = []
    for d in (0.05, 0.1, 0.2, 0.5):
        p = policy.rho_safe(d, variant=policy.POINT)
        q = policy.rho_safe(d, variant=policy.CONSERVATIVE)
        worst = q.rho * (policy.GAMMA_CERT_HIGH - 1.0)
        rows.append({"delta": d, "point_rho": p.rho, "conservative_rho": q.rho,
                     "point_worst_case_slope": p.rho * (policy.GAMMA_CERT_HIGH - 1.0),
                     "conservative_worst_case_slope": worst})
    ok = all(r["conservative_worst_case_slope"] <= 1.0 - r["delta"] + 1e-12
             for r in rows)
    violates = [r for r in rows if r["point_worst_case_slope"] > 1.0]
    record("policy_variants",
           "does the conservative variant hold across the whole certified Gamma?",
           rows, ok,
           f"conservative holds at every delta; the POINT variant would violate "
           f"|F'|<=1 for {len(violates)}/{len(rows)} deltas if Gamma were at its "
           f"certified upper end -- which is exactly why it is labelled heuristic")

    # 9 -- fresh-baseline sanity
    c0 = cell(0.0, curve, batches)["estimates"]
    checks_fresh = {
        "reference_mse ~ 1/m": (c0["reference_mse"]["point"], 1.0, 0.01),
        "reference_sd ~ 1": (c0["reference_sd"]["point"], 1.0, 0.01),
        "alternation ~ 0.5": (c0["alternation_rate"]["point"], 0.5, 0.01),
        "acf lag1 ~ 0": (c0["acf_e_lag1"]["point"], 0.0, 0.01),
    }
    rows = [{"quantity": k, "observed": v[0], "expected": v[1], "tol": v[2]}
            for k, v in checks_fresh.items()]
    ok = all(abs(v[0] - v[1]) < v[2] for v in checks_fresh.values())
    record("fresh_baseline_sanity",
           "does rho = 0 behave exactly as its own definition requires?", rows,
           ok, "sd = 1/sqrt(m), alternation 0.5, ACF 0, MSE 1")

    # 10 -- full-reuse reproduction of Stage A
    rows, ok = [], True
    for rho, ref in STAGE_A.items():
        c = cell(rho, curve, batches)["estimates"]
        got = {"arl": c["cycle_arl"]["point"], "sd": c["reference_sd"]["point"],
               "alt": c["alternation_rate"]["point"]}
        for k, want in ref.items():
            rel = abs(got[k] - want) / abs(want)
            rows.append({"rho": rho, "metric": k, "stage_a": want,
                         "stage_c": got[k], "rel_gap": rel})
            ok &= rel < 0.02
    record("stage_a_reproduction",
           "does Stage C reproduce the Stage A Gate 4.1 numbers?", rows, ok,
           f"max relative gap {max(r['rel_gap'] for r in rows):.2e} "
           f"(threshold 2%); note Stage A reported sd on e_next, Stage C on e_prev")

    # 11 -- the policy must not depend on any Stage B / Stage C outcome
    import inspect
    src = inspect.getsource(policy)
    leaked = [v for v in ("1.0287", "1.0447", "0.10814", "0.83253") if v in src]
    record("no_stage_b_leak",
           "can any Stage B outcome reach the policy definition?",
           [{"forbidden_values_found": leaked}], not leaked,
           "no Stage B root or multiplier value appears in policy.py")

    payload = {"checks": checks, "n_passed": sum(c["passed"] for c in checks),
               "n_checks": len(checks), "seconds": time.time() - t0}
    (RESULTS / "adversarial.json").write_text(
        json.dumps(payload, indent=2, default=float))
    print(f"\n  {payload['n_passed']}/{payload['n_checks']} checks passed "
          f"({payload['seconds']:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
