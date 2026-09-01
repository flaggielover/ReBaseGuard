"""Stage 5 -- robustness, sensitivity and edge cases, on EVAL seeds.

Four blocks:

  A. the fresh-budget frontier: SAW recalibrated at k in {m, 2m, 4m} against
     B9 (fixed rho at the same k) and the fixed-rho grid, so the comparison is
     at matched fresh cost everywhere;
  B. finite-reference initialisation e_0 ~ N(0, 1/m_0), m_0 in {20, 50, 100},
     as SECONDARY evidence beside the canonical e_0 = 0;
  C. the SAW-T Gaussian approximation error, measured against a Monte Carlo
     evaluation of the true one-step tail;
  D. the T6-C(iii) plug-in criterion: measured Jensen gap vs measured plug-in
     error, per cell.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from _registry import (RESULTS, RHO_GRID, c_beta_for, calib_for,           # noqa: E402
                       load_calibration, saw_family)

from rebaseguard_p6c.calibrate import SawCalibration                       # noqa: E402
from rebaseguard_p6c.chain import simulate_policy_chain                    # noqa: E402
from rebaseguard_p6c.policy import ConstantPolicy                          # noqa: E402
from rebaseguard_p6c.runner import (_collect, calibrate_saw, run_delay,    # noqa: E402
                                    run_incontrol)
from rebaseguard_p6c.saw import SawPolicy, SawTailPolicy                   # noqa: E402
from rebaseguard_p6c.seeds import generator                                # noqa: E402

DETECTORS = ("cusum", "sr")
M_GRID = (1, 2, 3, 5)
FAMILY = "eval"
PAIR = "robust_paired"
N_IC, N_CYC, BURN = 6000, 80, 15
N_D, SHIFT_CYCLE = 40000, 15
M0_GRID = (20, 50, 100)


def block_a_frontier():
    """SAW recalibrated per k, against matched-k fixed-rho baselines."""
    out = {}
    for det in DETECTORS:
        for m in (1, 3, 5):
            for mult in (1, 2, 4):
                k = mult * m
                r = calibrate_saw(detector=det, m=m, k=k, family="tune",
                                  n_rep=600, n_cycles=150, burn_in=20,
                                  max_iter=5, tol=5e-3, cell_tag=f"calib_k{k}")
                c = r["calib"]
                pols = {f"SAW_M_k{k}": SawPolicy(c, k=k, mode="full",
                                                 name=f"SAW_M(m={m},k={k})")}
                for rho in RHO_GRID:
                    pols[f"B2_rho{rho:g}_k{k}"] = ConstantPolicy(
                        rho=rho, m=m, k=k, name=f"B2_rho{rho:g}(m={m},k={k})")
                pols[f"B0_k{k}"] = ConstantPolicy(rho=0.0, m=m, k=k,
                                                  name=f"B0(m={m},k={k})")
                rows = {}
                for pid, pol in pols.items():
                    ic, res = run_incontrol(policy=pol, detector=det, m=m,
                                            family=FAMILY, n_rep=N_IC,
                                            n_cycles=N_CYC, burn_in=BURN, e0=0.0,
                                            cell_tag=f"front_k{k}", pair_tag=PAIR)
                    d, _ = run_delay(policy=pol, detector=det, m=m, family=FAMILY,
                                     n_rep=N_D, shift=1.0, shift_cycle=SHIFT_CYCLE,
                                     cell_tag=f"front_k{k}", pair_tag=PAIR)
                    dd = d["delay"]
                    rows[pid] = {
                        "Arl0": float(np.mean(ic["Arl0"])),
                        "Rms": float(np.mean(ic["Rms"])),
                        "Fresh": float(np.mean(ic["Fresh"])),
                        "FreshProp": float(np.mean(ic["FreshProp"])),
                        "Wbar": float(np.mean(ic["Wbar"])),
                        "Coll": float(res.tau[:, 1].mean() / res.tau[:, 0].mean()),
                        "Dmean": float(dd.mean()), "Dmed": float(np.median(dd)),
                        "Dq95": float(np.quantile(dd, 0.95)),
                        "Dtail100": float((dd > 100).mean()),
                        "n_events_100": int((dd > 100).sum()),
                    }
                out[f"{det}_m{m}_k{k}"] = {"calib": c.to_dict(),
                                           "jensen_gap_rel": r["jensen_gap_rel"],
                                           "rows": rows}
                print(f"A {det} m={m} k={k} done", flush=True)
    return out


def block_b_finite_reference(cal):
    """e_0 ~ N(0, 1/m_0): the secondary finite-reference robustness regime."""
    out = {}
    for det in DETECTORS:
        for m in (1, 3, 5):
            c = calib_for(cal, det, m)
            cb = c_beta_for(det)
            pols = {
                "B0_fresh_only": ConstantPolicy(rho=0.0, m=m, name="B0"),
                "B3_full_reuse": ConstantPolicy(rho=1.0, m=m, name="B3"),
                "B2_rho0.15": ConstantPolicy(rho=0.15, m=m, name="B2_rho0.15"),
                "B2_rho0.2": ConstantPolicy(rho=0.20, m=m, name="B2_rho0.2"),
                "B2_rho0.25": ConstantPolicy(rho=0.25, m=m, name="B2_rho0.25"),
                "SAW_M": SawPolicy(c, k=m, mode="full", name="SAW_M"),
                "SAW_T": SawTailPolicy(c, cb, k=m, mode="full", name="SAW_T"),
            }
            for m0 in M0_GRID:
                rows = {}
                for pid, pol in pols.items():
                    ic, res = run_incontrol(policy=pol, detector=det, m=m,
                                            family=FAMILY, n_rep=N_IC,
                                            n_cycles=N_CYC, burn_in=BURN,
                                            e0=None, m0=m0,
                                            cell_tag=f"finref_m0{m0}",
                                            pair_tag=PAIR)
                    d, _ = run_delay(policy=pol, detector=det, m=m, family=FAMILY,
                                     n_rep=N_D, shift=1.0, shift_cycle=SHIFT_CYCLE,
                                     e0=None, m0=m0, cell_tag=f"finref_m0{m0}",
                                     pair_tag=PAIR)
                    dd = d["delay"]
                    rows[pid] = {
                        "Arl0": float(np.mean(ic["Arl0"])),
                        "Rms": float(np.mean(ic["Rms"])),
                        "Fresh": float(np.mean(ic["Fresh"])),
                        "Coll": float(res.tau[:, 1].mean() / res.tau[:, 0].mean()),
                        "tau1": float(res.tau[:, 0].mean()),
                        "Dmean": float(dd.mean()), "Dq95": float(np.quantile(dd, 0.95)),
                        "Dtail100": float((dd > 100).mean()),
                    }
                out[f"{det}_m{m}_m0{m0}"] = rows
            print(f"B {det} m={m} done", flush=True)
    return out


def block_c_tail_approximation(cal):
    """How wrong is SAW-T's Gaussian step?  Measured, not assumed."""
    from scipy.stats import norm
    out = {}
    for det in DETECTORS:
        for m in (1, 3, 5):
            c = calib_for(cal, det, m)
            cb = c_beta_for(det)
            rng = generator(family=FAMILY, detector=det, m=m,
                            policy_id="tailcheck", cell_tag="approx")
            res = simulate_policy_chain(detector=det, policy=SawPolicy(c, k=m),
                                        n_rep=3000, n_cycles=80, burn_in=15,
                                        e0=0.0, rng=rng)
            zb, tau, w, u = _collect(res, m)
            mu, s = c.features(zb, tau, w)
            nu = 1.0 / m
            # bin by the predicted mean; compare the Gaussian tail against the
            # empirical tail of the realised rho*U + (1-rho)*fresh at rho fixed
            rho = float(np.median(res.post(res.rho)))
            sd = np.sqrt(rho * rho * s + (1 - rho) ** 2 * nu)
            pred = norm.sf((cb - rho * mu) / sd) + norm.cdf((-cb - rho * mu) / sd)
            g = rng.standard_normal(u.size) / np.sqrt(m)
            real = np.abs(rho * u + (1 - rho) * g) > cb
            qs = np.quantile(np.abs(mu), np.linspace(0, 1, 11))
            bins = []
            for lo, hi in zip(qs[:-1], qs[1:]):
                sel = (np.abs(mu) >= lo) & (np.abs(mu) < hi)
                if sel.sum() < 200:
                    continue
                bins.append({"mu_lo": float(lo), "mu_hi": float(hi),
                             "n": int(sel.sum()),
                             "predicted": float(pred[sel].mean()),
                             "empirical": float(real[sel].mean())})
            out[f"{det}_m{m}"] = {
                "rho_used": rho, "c_beta": cb,
                "overall_predicted": float(pred.mean()),
                "overall_empirical": float(real.mean()),
                "max_abs_bin_gap": float(max(abs(b["predicted"] - b["empirical"])
                                             for b in bins)) if bins else None,
                "bins": bins,
            }
            print(f"C {det} m={m} done", flush=True)
    return out


def block_d_plugin_criterion(cal):
    """T6-C(iii): measured Jensen gap vs measured plug-in error, per cell."""
    out = {}
    for det in DETECTORS:
        for m in M_GRID:
            c = calib_for(cal, det, m)
            nu = 1.0 / m
            rng = generator(family=FAMILY, detector=det, m=m,
                            policy_id="plugin", cell_tag="t6c")
            res = simulate_policy_chain(detector=det, policy=SawPolicy(c, k=m),
                                        n_rep=4000, n_cycles=120, burn_in=15,
                                        e0=0.0, rng=rng)
            zb, tau, w, u = _collect(res, m)
            v_hat = c.v_hat(zb, tau, w)
            rho_hat = np.minimum(nu / (v_hat + nu), 0.95)
            # V_j = E[U^2 | F_j] is estimated by binning on the plug-in itself:
            # within a narrow V_hat bin the realised U^2 average estimates V.
            order = np.argsort(v_hat)
            nb = 200
            edges = np.linspace(0, v_hat.size, nb + 1).astype(int)
            v_true = np.empty_like(v_hat)
            for a, b in zip(edges[:-1], edges[1:]):
                idx = order[a:b]
                v_true[idx] = (u[idx] ** 2).mean()
            rho_star = nu / (v_true + nu)
            vbar = float(v_true.mean())
            gap = float(nu * vbar / (vbar + nu) - (nu * v_true / (v_true + nu)).mean())
            err = float(((v_true + nu) * (rho_hat - rho_star) ** 2).mean())
            out[f"{det}_m{m}"] = {
                "V_bar": vbar, "V_sd": float(v_true.std()),
                "jensen_gap": gap,
                "jensen_gap_rel": float(gap / (nu * vbar / (vbar + nu))),
                "plugin_error": err,
                "criterion_satisfied": bool(err < gap),
                "margin": float(gap - err),
                "predicted_one_step_gain_rel": float((gap - err)
                                                     / (nu * vbar / (vbar + nu))),
                "n": int(v_hat.size), "n_bins": nb,
                "corr_vhat_vtrue": float(np.corrcoef(v_hat, v_true)[0, 1]),
            }
            print(f"D {det} m={m} done", flush=True)
    return out


def main():
    t0 = time.time()
    cal = load_calibration()
    d = block_d_plugin_criterion(cal)
    (RESULTS / "robust_plugin_criterion.json").write_text(json.dumps(d, indent=1))
    c = block_c_tail_approximation(cal)
    (RESULTS / "robust_tail_approx.json").write_text(json.dumps(c, indent=1))
    b = block_b_finite_reference(cal)
    (RESULTS / "robust_finite_reference.json").write_text(json.dumps(b, indent=1))
    a = block_a_frontier()
    (RESULTS / "robust_frontier.json").write_text(json.dumps(a, indent=1))
    print(f"total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
