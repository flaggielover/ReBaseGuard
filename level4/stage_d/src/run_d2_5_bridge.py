"""D2.5 -- does the Gamma_m crossing predict an operational change?

Design committed in notes/D2_5_PRECOMMIT.md (sha256 fb6272ef...) before any
D2.5 data existed. Statistical unit: the replicate.

Reported whatever it shows. If the metrics vary smoothly with no feature near
m*, the protocol's D2.5 row requires reporting the boundary as MATHEMATICAL,
NOT OPERATIONAL, and that is what will be written.
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
from chain import simulate_chain                             # noqa: E402

SEED = 20261001
M_VALUES = [10, 20, 50, 65, 75, 90, 100]
RHO = 1.0
N_REP = 20_000
N_CYCLES = 80
BURN_IN = 30
SHIFTS = [0.5, 1.0]
SHIFT_CYCLE = 40
SHIFT_BURN = 20
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "d2_5_bridge.json"
Z = 1.959964


def _git() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, cwd=ROOT).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def mse(v: np.ndarray) -> dict:
    """Mean and SE over replicates -- the protocol's unit for D2.5."""
    v = np.asarray(v, dtype=float)
    return {"mean": float(v.mean()),
            "se": float(v.std(ddof=1) / np.sqrt(v.size))}


def boot_ratio(num: np.ndarray, den: np.ndarray, n_boot: int = 20_000,
               seed: int = 11) -> tuple[float, float, float]:
    """Ratio of means with a PAIRED bootstrap over replicates."""
    rng = np.random.default_rng(seed)
    r = float(num.mean() / den.mean())
    idx = rng.integers(0, num.size, size=(n_boot, num.size))
    draws = num[idx].mean(axis=1) / den[idx].mean(axis=1)
    return r, float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def main() -> None:
    t0 = time.time()
    gm = json.loads((ROOT / "results" / "d2_gamma_m.json").read_text())
    br = gm["d2_2_bracket"]
    m_star = br["m_star_interp"]
    print(f"D2.5  monitoring bridge, rho = {RHO}, m* interp = {m_star:.2f} "
          f"(bracket [{br['m_lo']}, {br['m_hi']}])", flush=True)

    rows = []
    for mi, m in enumerate(M_VALUES):
        ss = np.random.SeedSequence([SEED, 70, mi])
        rng = np.random.Generator(np.random.PCG64(ss))
        r = simulate_chain(m=m, rho=RHO, n_rep=N_REP, n_cycles=N_CYCLES,
                           burn_in=BURN_IN, rng=rng)
        post = r.tau[:, BURN_IN:]
        row = {
            "m": m,
            "below_m_star": bool(m < m_star),
            "cycle_arl": mse(r.cycle_arl),
            "reference_mse": mse(r.reference_mse),
            "e_acf1": mse(r.e_acf1),
            "direction_acf1": mse(r.direction_acf1),
            "frac_cycles_tau_lt_m": float((post < m).mean()),
            "mean_abs_e": mse(np.abs(r.e_start[:, BURN_IN:]).mean(axis=1)),
        }

        # baseline-normalised discrimination, paired within replicate
        row["R_delta"] = {}
        for sh in SHIFTS:
            ss2 = np.random.SeedSequence([SEED, 71, mi, int(sh * 100)])
            rng2 = np.random.Generator(np.random.PCG64(ss2))
            rs = simulate_chain(m=m, rho=RHO, n_rep=N_REP,
                                n_cycles=SHIFT_CYCLE + 1, burn_in=SHIFT_BURN,
                                rng=rng2, shift=sh, shift_cycle=SHIFT_CYCLE)
            num = rs.tau[:, SHIFT_CYCLE].astype(float)
            den = rs.tau[:, SHIFT_BURN:SHIFT_CYCLE].mean(axis=1)
            R, lo, hi = boot_ratio(num, den)
            row["R_delta"][str(sh)] = {
                "R": R, "ci": [lo, hi],
                "tau_shift_mean": float(num.mean()),
                "tau_baseline_mean": float(den.mean()),
            }
        rows.append(row)
        print(f"  m={m:>3}  ARL={row['cycle_arl']['mean']:7.2f}  "
              f"MSE={row['reference_mse']['mean']:.4f}  "
              f"eACF1={row['e_acf1']['mean']:+.3f}  "
              f"dirACF1={row['direction_acf1']['mean']:+.3f}  "
              f"R_0.5={row['R_delta']['0.5']['R']:.3f}  "
              f"R_1.0={row['R_delta']['1.0']['R']:.3f}  "
              f"({time.time() - t0:5.1f}s)", flush=True)

    # --- localisation test: is any change concentrated near m*? -------------
    # Largest successive change per metric, in log-m, compared against where
    # m* sits. Purely descriptive; no criterion is invented here.
    logm = np.log(np.array(M_VALUES, dtype=float))
    localisation = {}
    for key in ("cycle_arl", "reference_mse", "e_acf1", "direction_acf1"):
        v = np.array([r[key]["mean"] for r in rows])
        d = np.abs(np.diff(v)) / np.diff(logm)
        j = int(np.argmax(d))
        localisation[key] = {
            "largest_change_between_m": [M_VALUES[j], M_VALUES[j + 1]],
            "rate_per_log_m": [float(x) for x in d],
            "monotone": bool(np.all(np.diff(v) > 0) or np.all(np.diff(v) < 0)),
            "spans_m_star": bool(M_VALUES[j] <= m_star <= M_VALUES[j + 1]),
        }

    out = {
        "gate": "D2.5",
        "question": ("does the Gamma_m local-stability crossing correspond to an "
                     "observable repeated-monitoring consequence?"),
        "protocol_sha256":
            "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e",
        "precommit_sha256":
            "fb6272ef839d7f3b36af3c8a8ace3d3059df7028dda337455b9df6baaf92bba7",
        "rho": RHO, "m_values": M_VALUES, "m_star_interp": m_star,
        "m_star_bracket": [br["m_lo"], br["m_hi"]],
        "n_replicates": N_REP, "n_cycles": N_CYCLES, "burn_in": BURN_IN,
        "shifts": SHIFTS, "shift_cycle": SHIFT_CYCLE,
        "statistical_unit": "replicate",
        "convention": "Stage D: no minimum dwell, truncated window w = min(m, tau)",
        "rows": rows,
        "localisation": localisation,
        "evidence_status": "NEW-NUMERICAL",
        "git_head": _git(), "python": platform.python_version(),
        "numpy": np.__version__, "elapsed_s": round(time.time() - t0, 1),
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\n  -> {OUT}   ({out['elapsed_s']} s)", flush=True)


if __name__ == "__main__":
    main()
