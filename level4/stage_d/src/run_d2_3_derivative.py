"""D2.3 -- derivative correspondence F'_{1,m}(0) = 1 - Gamma_m.

The derivative is taken from the ACTUAL induced map by central finite
difference, never assumed from m=1 and never taken from the closed form.
Step sizes were committed in notes/D2_3_STEP_PRECOMMIT.md before any data.
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
N_POINT = 500_000
BATCH = 250_000
M_GRID = np.array([1, 2, 5, 10, 20, 50, 75, 100], dtype=np.int64)
L = 120
PRIMARY_STEP = 0.05
STEPS = [0.025, 0.05, 0.10]
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "d2_3_derivative.json"
Z = 1.959964


def _git() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, cwd=ROOT).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def map_at(e: float, key: list[int]) -> tuple[np.ndarray, np.ndarray]:
    """F_{1,m}(e) and its SE, at every m in the grid, from N_POINT cycles."""
    ss = np.random.SeedSequence(key)
    stats = None
    for child in ss.spawn(N_POINT // BATCH):
        rng = np.random.Generator(np.random.PCG64(child))
        s = simulate_stopped(detector=CUSUM, threshold=5.0, e=e,
                             n_paths=BATCH, L=L, m_grid=M_GRID, rng=rng)
        stats = s if stats is None else stats.combine(s)
    return stats.induced_map(e), stats.induced_map_se()


def main() -> None:
    t0 = time.time()
    gm = json.loads((ROOT / "results" / "d2_gamma_m.json").read_text())
    gamma = np.array([r["A"]["gamma_m"] for r in gm["rows"]])
    gamma_se = np.array([r["A"]["se"] for r in gm["rows"]])
    target = 1.0 - gamma

    print(f"D2.3  induced-map derivative,  N = {N_POINT:,} per point", flush=True)
    per_step = {}
    for si, h in enumerate(STEPS):
        fp, sp = map_at(+h, [SEED, 40, si, 0])
        fm, sm = map_at(-h, [SEED, 40, si, 1])
        d = (fp - fm) / (2.0 * h)
        d_se = np.hypot(sp, sm) / (2.0 * h)
        per_step[h] = {"F_plus": fp, "F_minus": fm, "deriv": d, "deriv_se": d_se}
        print(f"  step h = {h:<6} done ({time.time() - t0:5.1f}s)", flush=True)

    # Richardson from the two smallest steps -- DIAGNOSTIC ONLY
    d1, d2 = per_step[0.025]["deriv"], per_step[0.05]["deriv"]
    richardson = (4.0 * d1 - d2) / 3.0

    rows = []
    for j, m in enumerate(M_GRID):
        prim = per_step[PRIMARY_STEP]
        d = float(prim["deriv"][j]); dse = float(prim["deriv_se"][j])
        comb = float(np.hypot(dse, gamma_se[j]))
        disc = d - float(target[j])
        rows.append({
            "m": int(m),
            "gamma_m": float(gamma[j]), "gamma_se": float(gamma_se[j]),
            "target_1_minus_gamma": float(target[j]),
            "primary_step": PRIMARY_STEP,
            "fd_derivative": d, "fd_se": dse,
            "combined_se": comb,
            "discrepancy": disc,
            "n_combined_se": disc / comb if comb > 0 else float("nan"),
            "agrees_within_3se": bool(abs(disc) <= 3.0 * comb),
            "by_step": {str(h): {"deriv": float(per_step[h]["deriv"][j]),
                                 "se": float(per_step[h]["deriv_se"][j]),
                                 "discrepancy": float(per_step[h]["deriv"][j]
                                                      - target[j])}
                        for h in STEPS},
            "richardson_diagnostic": float(richardson[j]),
            "richardson_discrepancy": float(richardson[j] - target[j]),
        })

    n_pass = sum(r["agrees_within_3se"] for r in rows)
    out = {
        "gate": "D2.3",
        "criterion": ("central finite difference of the ACTUAL induced map at "
                      "rho=1 agrees with 1 - Gamma_m within 3 combined SE"),
        "protocol_sha256":
            "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e",
        "precommit_sha256":
            "7b7a54c64f4c86334415a03cd45797e7cb8b923d378fa90180a71f1831588dea",
        "primary_step": PRIMARY_STEP, "steps_tested": STEPS,
        "n_cycles_per_point": N_POINT, "seed_family": SEED,
        "rows": rows,
        "n_m_passing": n_pass, "n_m_total": len(rows),
        "criterion_met_all_m": bool(n_pass == len(rows)),
        "richardson_note": ("Richardson values are a TRUNCATION DIAGNOSTIC only "
                            "and are not the primary estimate."),
        "evidence_status": "NEW-NUMERICAL",
        "git_head": _git(), "python": platform.python_version(),
        "numpy": np.__version__, "elapsed_s": round(time.time() - t0, 1),
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n")

    print(f"\n{'m':>5} {'1-Gamma_m':>11} {'FD(h=.05)':>18} {'disc':>9} "
          f"{'/SE':>7}  {'ok':>3}   {'FD(.025)':>10} {'FD(.10)':>10} {'Rich':>10}",
          flush=True)
    for r in rows:
        print(f"{r['m']:>5} {r['target_1_minus_gamma']:11.4f} "
              f"{r['fd_derivative']:11.4f}+-{r['fd_se']:5.4f} "
              f"{r['discrepancy']:9.4f} {r['n_combined_se']:7.1f}  "
              f"{'YES' if r['agrees_within_3se'] else 'NO ':>3}   "
              f"{r['by_step']['0.025']['deriv']:10.4f} "
              f"{r['by_step']['0.1']['deriv']:10.4f} "
              f"{r['richardson_diagnostic']:10.4f}", flush=True)
    print(f"\n  D2.3: {n_pass}/{len(rows)} m-values agree within 3 combined SE",
          flush=True)
    print(f"  -> {OUT}   ({out['elapsed_s']} s)", flush=True)


if __name__ == "__main__":
    main()
