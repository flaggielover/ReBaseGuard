"""D3 -- non-Gaussian robustness of the stopped-selection functional.

Order of operations is forced by the protocol and by D3.1:
  1. write the regularity assumptions (notes/D3_REGULARITY.md, 9eafbcd2...);
  2. ARL0-match every family's CUSUM threshold, on its own seed, BEFORE any
     Gamma is computed;
  3. only then estimate Gamma_psi with the CORRECT score for each family.

Gamma_psi is reported exactly as frozen. Gamma_psi / E[psi'] is reported beside
it as the stability-relevant quantity (assumption A5). The naive Gaussian-form
Gamma_T is reported as a DIAGNOSTIC WARNING ONLY and is never primary evidence.
"""
from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calibrate import bisect_threshold                       # noqa: E402
from nongaussian import FAMILIES, expected_psi_prime         # noqa: E402
from stopped import CUSUM, simulate_stopped                  # noqa: E402

SEED = 20261001
N_CAL = 400_000
N_GAMMA = 1_000_000
BATCH = 250_000
M_GRID = np.array([1, 5, 20], dtype=np.int64)
L = 20
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "d3_nongaussian.json"
Z = 1.959964


def _git() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, cwd=ROOT).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def main() -> None:
    t0 = time.time()
    cal0 = json.loads((ROOT / "results" / "calibration_d1.json").read_text())
    target = cal0["cusum"]["arl0"]
    print(f"D3  target ARL0 = {target:.3f} (frozen Gaussian CUSUM, h=5)", flush=True)

    rows = []
    for fi, (name, fam) in enumerate(FAMILIES.items()):
        print(f"\n  [{name}]  Var = {fam.variance:.3f}", flush=True)

        # ---- step 1: ARL0 match, on its own seed, before any Gamma ---------
        if name == "gaussian":
            cal = {"threshold": 5.0, "achieved_arl0": target,
                   "arl0_se": cal0["cusum"]["arl0_se"], "relative_error": 0.0,
                   "note": "frozen h = 5 by definition; not recalibrated"}
            print(f"    threshold h = 5.0 (frozen, control family)", flush=True)
        else:
            cal = bisect_threshold(
                CUSUM, target, lo=2.0, hi=20.0, n_paths=N_CAL,
                root_seed=SEED + 100 + fi, tol_log=1e-3, max_iter=30,
                batch=BATCH, verbose=False,
                innovation=lambda rng, n, f=fam: f.draw(rng, n))
            print(f"    threshold h = {cal['threshold']:.6f}  "
                  f"ARL0 = {cal['achieved_arl0']:.2f} "
                  f"(rel err {cal['relative_error']:+.5f})", flush=True)
        h = cal["threshold"]

        # ---- step 2: Gamma_psi with the CORRECT score ----------------------
        ss = np.random.SeedSequence([SEED, 80, fi])
        stats, bpsi = None, []
        for child in ss.spawn(N_GAMMA // BATCH):
            rng = np.random.Generator(np.random.PCG64(child))
            s = simulate_stopped(detector=CUSUM, threshold=h, e=0.0,
                                 n_paths=BATCH, L=L, m_grid=M_GRID, rng=rng,
                                 innovation=lambda r, n, f=fam: f.draw(r, n),
                                 score=fam.psi)
            bpsi.append(s.gamma_psi().copy())
            stats = s if stats is None else stats.combine(s)

        gpsi = stats.gamma_psi()
        gpsi_se = stats.gamma_psi_se()
        bpsi = np.array(bpsi)
        se_batch = bpsi.std(axis=0, ddof=1) / np.sqrt(bpsi.shape[0])
        gnaive = stats.gamma_m("A")
        gnaive_se = stats.gamma_m_se("A")
        epp = expected_psi_prime(fam)

        per_m = []
        for j, m in enumerate(M_GRID):
            g, se = float(gpsi[j]), float(gpsi_se[j])
            per_m.append({
                "m": int(m),
                "gamma_psi": g, "se": se, "se_batch": float(se_batch[j]),
                "ci": [g - Z * se, g + Z * se],
                "lower_bound_exceeds_2": bool(g - Z * se > 2.0),
                "se_agreement_ratio": float(se_batch[j] / se) if se > 0 else None,
                "gamma_psi_normalised": g / epp,
                "normalised_lower_bound": (g - Z * se) / epp,
                "normalised_lower_bound_exceeds_2": bool((g - Z * se) / epp > 2.0),
                "gamma_T_naive_DIAGNOSTIC_ONLY": float(gnaive[j]),
                "gamma_T_naive_se": float(gnaive_se[j]),
            })

        rows.append({
            "family": name, "variance": fam.variance,
            "unit_variance_rescaled": fam.unit_variance_rescaled,
            "calibration": cal, "threshold": h,
            "arl0_measured": float(stats.arl),
            "E_psi_prime": epp,
            "per_m": per_m,
            "d3_2_primary_m1": per_m[0]["lower_bound_exceeds_2"],
        })
        p1 = per_m[0]
        print(f"    Gamma_psi(m=1) = {p1['gamma_psi']:8.4f} +/- {p1['se']:.4f}  "
              f"lower {p1['ci'][0]:8.4f}  "
              f"{'> 2 PASS' if p1['lower_bound_exceeds_2'] else '<= 2 FAIL'}",
              flush=True)
        print(f"    normalised /E[psi']={epp:.4f}: "
              f"{p1['gamma_psi_normalised']:8.4f} "
              f"(lower {p1['normalised_lower_bound']:.4f})", flush=True)
        print(f"    [diagnostic only] naive Gamma_T = "
              f"{p1['gamma_T_naive_DIAGNOSTIC_ONLY']:.4f}", flush=True)

    n_pass = sum(r["d3_2_primary_m1"] for r in rows)
    n_pass_norm = sum(r["per_m"][0]["normalised_lower_bound_exceeds_2"]
                      for r in rows)
    out = {
        "gate": "D3",
        "protocol_sha256":
            "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e",
        "regularity_sha256":
            "9eafbcd25870a19e20d5f84c763c5252bd44b3af809de4821d1e99555f93626e",
        "target_arl0": target, "n_calibration": N_CAL, "n_gamma": N_GAMMA,
        "m_grid": [int(m) for m in M_GRID], "primary_m": 1, "seed_family": SEED,
        "rows": rows,
        "d3_2_families_passing": n_pass, "d3_2_families_total": len(rows),
        "d3_2_families_passing_normalised": n_pass_norm,
        "d3_3_note": ("gamma_T_naive_DIAGNOSTIC_ONLY is the naive Gaussian-form "
                      "statistic. It is a DIAGNOSTIC WARNING, never primary "
                      "evidence, per protocol D3.3."),
        "a5_note": ("gamma_psi is the frozen estimand. gamma_psi_normalised = "
                    "gamma_psi / E[psi'] is the stability-relevant ratio "
                    "(notes/D3_REGULARITY.md A5). They coincide only for the "
                    "Gaussian."),
        "scope": ("NUMERICAL ROBUSTNESS across six tested families. NOT "
                  "distribution-free, NOT universal, NOT certified. A1 "
                  "(differentiation under the expectation) is UNPROVED for "
                  "every non-Gaussian family."),
        "evidence_status": "NEW-NUMERICAL",
        "git_head": _git(), "python": platform.python_version(),
        "numpy": np.__version__, "elapsed_s": round(time.time() - t0, 1),
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\n  D3.2: {n_pass}/{len(rows)} families have lower bound of "
          f"Gamma_psi above 2 (frozen criterion)", flush=True)
    print(f"        {n_pass_norm}/{len(rows)} when normalised by E[psi'] "
          f"(assumption A5)", flush=True)
    print(f"  -> {OUT}   ({out['elapsed_s']} s)", flush=True)


if __name__ == "__main__":
    main()
