"""D2 -- Gamma_m over the frozen m-grid for the frozen CUSUM.

Convention A (w = min(m, tau), denominator w) is the protocol-frozen primary.
Convention B is carried alongside as the pre-specified estimator-variant
adversarial check. Both are written out; neither is selected after the fact.

Statistical unit: the independent cycle. Intervals: normal CI on the sample
mean, plus a 20-batch bootstrap cross-check, as the protocol requires.
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
from stopped import CUSUM, simulate_stopped                  # noqa: E402

SEED = 20261001
N_TOTAL = 2_000_000
N_BATCHES = 20                       # protocol: batch bootstrap with 20 batches
BATCH = N_TOTAL // N_BATCHES
M_GRID = np.array([1, 2, 5, 10, 20, 50, 75, 100], dtype=np.int64)
L = 120                              # >= max m, room for bracket refinement
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "d2_gamma_m.json"


def _git() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, cwd=ROOT).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def boot_ci(batch_means: np.ndarray, n_boot: int = 20_000,
            seed: int = 7) -> tuple[float, float]:
    """Percentile bootstrap over the 20 batch means."""
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, batch_means.shape[0], size=(n_boot, batch_means.shape[0]))
    draws = batch_means[idx].mean(axis=1)
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def main() -> None:
    t0 = time.time()
    print(f"D2  Gamma_m,  N = {N_TOTAL:,} cycles, m in {list(M_GRID)}", flush=True)

    ss = np.random.SeedSequence([SEED, 20, 0])
    stats = None
    per_batch_A, per_batch_B, per_batch_lag = [], [], []
    per_batch_arl, per_batch_ginf = [], []

    for b, child in enumerate(ss.spawn(N_BATCHES)):
        rng = np.random.Generator(np.random.PCG64(child))
        s = simulate_stopped(detector=CUSUM, threshold=5.0, e=0.0,
                             n_paths=BATCH, L=L, m_grid=M_GRID, rng=rng)
        per_batch_A.append(s.gamma_m("A").copy())
        per_batch_B.append(s.gamma_m("B").copy())
        per_batch_lag.append(s.gamma_lag.copy())
        per_batch_arl.append(s.arl)
        per_batch_ginf.append(s.gamma_inf_A)
        stats = s if stats is None else stats.combine(s)
        print(f"  batch {b + 1:2d}/{N_BATCHES}  ARL0={s.arl:7.2f}  "
              f"G_1={s.gamma_m('A')[0]:6.3f}  G_100={s.gamma_m('A')[-1]:6.3f}  "
              f"({time.time() - t0:5.1f}s)", flush=True)

    per_batch_A = np.array(per_batch_A)
    per_batch_B = np.array(per_batch_B)

    rows = []
    for j, m in enumerate(M_GRID):
        row: dict = {"m": int(m)}
        for conv, pb in (("A", per_batch_A), ("B", per_batch_B)):
            g = float(stats.gamma_m(conv)[j])
            se = float(stats.gamma_m_se(conv)[j])
            lo, hi = boot_ci(pb[:, j])
            row[conv] = {
                "gamma_m": g, "se": se,
                "ci_normal": [g - 1.959964 * se, g + 1.959964 * se],
                "ci_bootstrap": [lo, hi],
                "z_vs_2": (g - 2.0) / se if se > 0 else float("nan"),
                # rho_c defined only where the lower CI bound exceeds 1
                "rho_c": (1.0 / (g - 1.0)) if (g - 1.959964 * se) > 1.0 else None,
                "rho_c_se": (se / (g - 1.0) ** 2) if (g - 1.959964 * se) > 1.0 else None,
            }
        rows.append(row)

    # ---- D2.2 bracket: Gamma_m - 2 must change sign, both ends by > 3 SE ----
    bracket = None
    gA = np.array([r["A"]["gamma_m"] for r in rows])
    sA = np.array([r["A"]["se"] for r in rows])
    for j in range(len(M_GRID) - 1):
        if gA[j] - 2.0 > 3.0 * sA[j] and 2.0 - gA[j + 1] > 3.0 * sA[j + 1]:
            m_lo, m_hi = int(M_GRID[j]), int(M_GRID[j + 1])
            # linear interpolation in log m, SEs propagated from both ends
            f = (gA[j] - 2.0) / (gA[j] - gA[j + 1])
            log_star = np.log(m_lo) + f * (np.log(m_hi) - np.log(m_lo))
            d = gA[j] - gA[j + 1]
            dfd0 = (1.0 / d) - (gA[j] - 2.0) / d ** 2
            dfd1 = (gA[j] - 2.0) / d ** 2
            se_f = np.hypot(dfd0 * sA[j], dfd1 * sA[j + 1])
            se_log = se_f * (np.log(m_hi) - np.log(m_lo))
            bracket = {
                "m_lo": m_lo, "m_hi": m_hi,
                "gamma_lo": float(gA[j]), "gamma_hi": float(gA[j + 1]),
                "se_lo": float(sA[j]), "se_hi": float(sA[j + 1]),
                "z_lo": float((gA[j] - 2.0) / sA[j]),
                "z_hi": float((2.0 - gA[j + 1]) / sA[j + 1]),
                "m_star_interp": float(np.exp(log_star)),
                "m_star_ci": [float(np.exp(log_star - 1.959964 * se_log)),
                              float(np.exp(log_star + 1.959964 * se_log))],
                "note": ("The BRACKET is the primary object; the interpolated "
                         "m_star is secondary and is not a crossing proof."),
            }
            break

    lag = stats.gamma_lag
    arl = stats.arl
    ginf = stats.gamma_inf_A
    ginf_se = float(np.std(per_batch_ginf, ddof=1) / np.sqrt(N_BATCHES))

    out = {
        "gate": "D2",
        "protocol_sha256":
            "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e",
        "detector": "cusum", "k": 0.5, "h": 5.0, "e": 0.0,
        "seed_family": SEED, "seed": [SEED, 20, 0],
        "n_cycles": int(stats.n), "n_batches": N_BATCHES, "L": L,
        "primary_convention": "A",
        "m_grid": [int(m) for m in M_GRID],
        "rows": rows,
        "d2_2_bracket": bracket,
        "d2_1_lag": {
            "gamma_0": float(lag[0]),
            "gamma_first_10": [float(v) for v in lag[:10]],
            "sum_gamma_first_L_lags": float(lag.sum()),
            "sum_gamma_lags_note": ("Sum over the first L lags only, NOT over "
                                    "all lags; compare E_T_sq against ARL0 for "
                                    "the Wald check instead."),
            "arl0": float(arl),
            "E_T_sq": float(stats.E_T_sq),
            "wald_ratio_ETsq_over_arl0": float(stats.E_T_sq / arl),
        },
        "d2_4_asymptote": {
            "gamma_inf_A_E_Tsq_over_tau": float(ginf), "se": ginf_se,
            "ci_normal": [ginf - 1.959964 * ginf_se, ginf + 1.959964 * ginf_se],
            "below_2": bool(ginf + 1.959964 * ginf_se < 2.0),
            "note": "Numerical only. NOT a theorem and NOT an asymptotic proof.",
        },
        "evidence_status": "NEW-NUMERICAL",
        "git_head": _git(), "python": platform.python_version(),
        "numpy": np.__version__, "elapsed_s": round(time.time() - t0, 1),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n")

    print(f"\n{'m':>5} {'Gamma_m (A)':>22} {'z vs 2':>8}   {'Gamma_m (B)':>22}",
          flush=True)
    for r in rows:
        a, bb = r["A"], r["B"]
        print(f"{r['m']:>5} {a['gamma_m']:11.4f} +/- {a['se']:7.4f} "
              f"{a['z_vs_2']:8.1f}   {bb['gamma_m']:11.4f} +/- {bb['se']:7.4f}",
              flush=True)
    print(f"\n  ARL0 = {arl:.3f}   E[T^2] = {stats.E_T_sq:.3f}   "
          f"ratio = {stats.E_T_sq / arl:.5f}", flush=True)
    print(f"  Gamma_inf (A) = E[T^2/tau] = {ginf:.4f} +/- {ginf_se:.4f}", flush=True)
    if bracket:
        print(f"  D2.2 bracket: m* in [{bracket['m_lo']}, {bracket['m_hi']}]  "
              f"(z_lo={bracket['z_lo']:.1f}, z_hi={bracket['z_hi']:.1f})  "
              f"interp m* = {bracket['m_star_interp']:.1f}", flush=True)
    else:
        print("  D2.2 bracket: NONE FOUND at 3 SE on the frozen grid", flush=True)
    print(f"  -> {OUT}   ({out['elapsed_s']} s)", flush=True)


if __name__ == "__main__":
    main()
