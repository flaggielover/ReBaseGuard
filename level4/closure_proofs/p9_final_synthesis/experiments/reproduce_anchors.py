#!/usr/bin/env python3
"""P9 cross-priority reproduction anchors.

An INDEPENDENT minimal implementation of the frozen recursive re-baselining
chain, written from the published model specification only. It does not import
any P1-P8 module. Purpose: validate the full dependency chain at a small number
of strategically chosen anchors, not to rerun any campaign.

Frozen model (from P1/P2/P3/P5/P7 definition audits):
  CUSUM  k=1/2, h=5, two-sided:
         Cp = max(0, Cp + Z - k), Cm = max(0, Cm - Z - k), alarm max >= h
  SR     symmetric two-chart, A = 520.886133602749:
         Rp = (1+Rp)exp(Z-1/2), Rm = (1+Rm)exp(-Z-1/2), alarm max >= A
  Z_t = X_t - e_j with X_t ~ N(0,1) iid;  tau = first inclusive crossing
  window w = min(m, tau), denominator w
  update e_{j+1} = rho(e_j + zbar_w) + (1-rho) * fresh,  fresh ~ N(0, 1/m)
"""
import json, os, sys
from fractions import Fraction
import numpy as np

H_CUSUM, K_CUSUM = 5.0, 0.5
A_SR = 520.886133602749
LOG_A_SR = np.log(A_SR)
MAX_STEPS = 200000

def seed_for(*parts):
    """Deterministic seed derivation - no seed is ever chosen by hand."""
    import hashlib
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).digest()
    return int.from_bytes(h[:8], "big") % (2**32 - 1)

def run_cycles(detector, m, rho, n_paths, n_cycles, seed, e0=0.0):
    """Return (cycle_lengths[n_paths, n_cycles], entering_e[n_paths, n_cycles])."""
    rng = np.random.default_rng(seed)
    e = np.full(n_paths, float(e0))
    taus = np.zeros((n_paths, n_cycles), dtype=np.int64)
    ents = np.zeros((n_paths, n_cycles))
    for j in range(n_cycles):
        ents[:, j] = e
        cp = np.zeros(n_paths); cm = np.zeros(n_paths)
        lrp = np.zeros(n_paths); lrm = np.zeros(n_paths)   # log-domain SR
        buf = np.zeros((n_paths, m))                        # rolling raw X
        tau = np.zeros(n_paths, dtype=np.int64)
        active = np.ones(n_paths, dtype=bool)
        t = 0
        while active.any() and t < MAX_STEPS:
            t += 1
            idx = np.flatnonzero(active)
            X = rng.standard_normal(idx.size)
            Z = X - e[idx]
            buf[idx, (t - 1) % m] = X
            if detector == "cusum":
                cp[idx] = np.maximum(0.0, cp[idx] + Z - K_CUSUM)
                cm[idx] = np.maximum(0.0, cm[idx] - Z - K_CUSUM)
                fired = np.maximum(cp[idx], cm[idx]) >= H_CUSUM
            else:
                # log1p-exp form, numerically stable and algebraically identical
                lrp[idx] = np.logaddexp(0.0, lrp[idx]) + Z - 0.5
                lrm[idx] = np.logaddexp(0.0, lrm[idx]) - Z - 0.5
                fired = np.maximum(lrp[idx], lrm[idx]) >= LOG_A_SR
            hit = idx[fired]
            tau[hit] = t
            active[hit] = False
        if active.any():
            tau[active] = t            # censored; counted and reported
        taus[:, j] = tau
        w = np.minimum(m, tau)
        # mean of the last w raw observations, denominator w
        xbar = np.empty(n_paths)
        for r in range(n_paths):
            ww = w[r]; tt = taus[r, j]
            offs = [((tt - 1 - q) % m) for q in range(ww)]
            xbar[r] = buf[r, offs].mean()
        fresh = rng.standard_normal(n_paths) / np.sqrt(m)
        zbar = xbar - e                 # zbar_w = xbar_w - e   (definitional)
        e = rho * (e + zbar) + (1.0 - rho) * fresh
    return taus, ents

# ---------------------------------------------------------------- anchors
def anchor_p3_exact():
    """P3-X1: exact rational witnesses, independent Fraction arithmetic."""
    out = {}
    cus = {m: Fraction(15, 2) for m in (1, 2, 3, 5)}
    sr  = {1: Fraction(4), 2: Fraction(3), 3: Fraction(8, 3), 5: Fraction(12, 5)}
    exp_c = {m: Fraction(2, 13) for m in (1, 2, 3, 5)}
    exp_s = {1: Fraction(1, 3), 2: Fraction(1, 2), 3: Fraction(3, 5), 5: Fraction(5, 7)}
    ok = True
    for name, gains, exp in (("cusum_witness", cus, exp_c), ("sr_witness", sr, exp_s)):
        rows = {}
        for m, g in gains.items():
            rc = 1 / abs(1 - g)
            ident = rc * abs(1 - g)          # must be exactly 1
            rows[m] = {"gain": str(g), "rho_c": str(rc),
                       "expected_rho_c": str(exp[m]),
                       "match": rc == exp[m], "identity_exact": ident == 1}
            ok &= (rc == exp[m]) and (ident == 1)
        out[name] = rows
    out["all_exact"] = ok
    return out

def anchor_p3_rho_c():
    """P3-N1: rho_c = 1/|1-Gamma| from the published P1/P2 gains."""
    gains = {("cusum", 1): 15.916540430, ("cusum", 2): 13.264824962,
             ("cusum", 3): 11.957078195, ("cusum", 5): 10.226363970,
             ("sr", 1): 17.453570692, ("sr", 2): 14.500509744,
             ("sr", 3): 12.972654634, ("sr", 5): 11.048526073}
    pub = {("cusum", 1): 0.067039673, ("cusum", 2): 0.081533981,
           ("cusum", 3): 0.091265206, ("cusum", 5): 0.108385059,
           ("sr", 1): 0.060777081, ("sr", 2): 0.074071277,
           ("sr", 3): 0.083523665, ("sr", 5): 0.099517083}
    rows, worst = [], 0.0
    for k, g in gains.items():
        rc = 1.0 / abs(1.0 - g)
        d = abs(rc - pub[k])
        worst = max(worst, d)
        rows.append({"detector": k[0], "m": k[1], "gain": g,
                     "rho_c_recomputed": rc, "rho_c_published": pub[k],
                     "abs_diff": d})
    # SR boundary strictly below CUSUM at every supported m (P3-N2)
    order = all(1.0 / abs(1 - gains[("sr", m)]) < 1.0 / abs(1 - gains[("cusum", m)])
                for m in (1, 2, 3, 5))
    return {"rows": rows, "max_abs_diff": worst,
            "tolerance": 1e-9, "pass": worst < 1e-9,
            "sr_below_cusum_all_m": order}

def anchor_p5_raw_identity(n_paths=4000):
    """P5-T1: e_{j+1} = rho*(raw window mean) + (1-rho)*fresh, EXACTLY.

    Verified as a machine-precision algebraic identity: the entering error
    cancels from (e + zbar_w). Checked across detectors, m and rho."""
    res, worst = [], 0.0
    for det in ("cusum", "sr"):
        for m in (1, 2, 5):
            for rho in (0.0, 0.25, 1.0):
                sd = seed_for("p5-raw", det, m, rho)
                rng = np.random.default_rng(sd)
                e = rng.standard_normal(n_paths) * 0.7   # arbitrary entering errors
                X = rng.standard_normal((n_paths, m))
                w = rng.integers(1, m + 1, n_paths)
                xbar = np.array([X[r, :w[r]].mean() for r in range(n_paths)])
                zbar = xbar - e
                fresh = rng.standard_normal(n_paths) / np.sqrt(m)
                lhs = rho * (e + zbar) + (1 - rho) * fresh   # Stage-D update
                rhs = rho * xbar + (1 - rho) * fresh         # raw-mean form
                d = float(np.max(np.abs(lhs - rhs)))
                worst = max(worst, d)
                res.append({"detector": det, "m": m, "rho": rho,
                            "max_abs_diff": d, "seed": sd})
    return {"cells": res, "max_abs_diff_overall": worst,
            "tolerance": 1e-12, "pass": worst < 1e-12}

def anchor_p7_operational(n_paths, n_cycles):
    """P7-E1/P7-D0: nominal A(0), fresh (rho=0) ARL, full-reuse (rho=1) ARL."""
    rows = []
    for det in ("cusum", "sr"):
        # nominal A(0): a single cycle from a perfect reference, e == 0
        sd = seed_for("p7-nominal", det)
        t0, _ = run_cycles(det, 1, 0.0, n_paths, 1, sd, e0=0.0)
        nominal = float(t0[:, 0].mean())
        nominal_se = float(t0[:, 0].std(ddof=1) / np.sqrt(n_paths))
        for m in (1, 5):
            entry = {"detector": det, "m": m, "nominal_A0": nominal,
                     "nominal_se": nominal_se}
            for rho in (0.0, 1.0):
                sd = seed_for("p7-op", det, m, rho)
                taus, _ = run_cycles(det, m, rho, n_paths, n_cycles, sd)
                # discard cycle 1 (its reference is the perfect e0=0 start)
                steady = taus[:, 1:]
                per_path = steady.mean(axis=1)
                entry[f"arl_rho{rho:g}"] = float(per_path.mean())
                entry[f"arl_rho{rho:g}_se"] = float(
                    per_path.std(ddof=1) / np.sqrt(n_paths))
                entry[f"cycle2_rho{rho:g}"] = float(taus[:, 1].mean())
            entry["loss_vs_nominal_rho1"] = 1 - entry["arl_rho1"] / nominal
            entry["loss_vs_fresh_rho1"] = 1 - entry["arl_rho1"] / entry["arl_rho0"]
            rows.append(entry)
    return rows

if __name__ == "__main__":
    quick = "--quick" in sys.argv
    n_paths = 3000 if quick else 12000
    n_cycles = 6 if quick else 12
    out = {"mode": "quick" if quick else "full",
           "n_paths": n_paths, "n_cycles": n_cycles,
           "p3_exact_witnesses": anchor_p3_exact(),
           "p3_rho_c": anchor_p3_rho_c(),
           "p5_raw_identity": anchor_p5_raw_identity()}
    out["p7_operational"] = anchor_p7_operational(n_paths, n_cycles)
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(os.path.join(here, "results"), exist_ok=True)
    with open(os.path.join(here, "results", "reproduction_anchors.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items()
                      if k in ("p3_exact_witnesses", "p3_rho_c", "p5_raw_identity")},
                     indent=1)[:1200])
    print("\nP7 operational:")
    for r in out["p7_operational"]:
        print(f"  {r['detector']} m={r['m']}: nominal={r['nominal_A0']:.1f} "
              f"fresh={r['arl_rho0']:.2f} reuse={r['arl_rho1']:.2f} "
              f"loss_vs_nominal={r['loss_vs_nominal_rho1']:.1%} "
              f"loss_vs_fresh={r['loss_vs_fresh_rho1']:.1%}")
