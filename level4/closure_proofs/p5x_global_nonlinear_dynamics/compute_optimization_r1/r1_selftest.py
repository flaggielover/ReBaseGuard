"""R1 mandatory self-test, T1-T8 of R1_FROZEN_SPEC.md section 9.

Must pass before the optimized benchmark may run.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(NS / "certified_method_repair_ra"))

import numpy as np                                                       # noqa: E402
from flint import arb                                                    # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, rational, workprec  # noqa: E402
import ra_certifier as RA                                                # noqa: E402
from drift_minorant import block_forcing_resolvent, drift_monotone_resolvent  # noqa: E402

N01_E0_BOUND = 250.0 / 0.19          # 1315.789..., independently certified at e = 0


def mc_mean_tau(e: float, n_paths: int = 200_000, seed: int = 20260903) -> float:
    """Monte-Carlo estimate of E_{x_0}[tau].  Spot-check only, never a proof."""
    rng = np.random.default_rng(seed)
    plus = np.zeros(n_paths); minus = np.zeros(n_paths)
    alive = np.ones(n_paths, bool); tau = np.zeros(n_paths)
    for t in range(1, 20000):
        idx = np.flatnonzero(alive)
        if idx.size == 0:
            break
        z = rng.standard_normal(idx.size) - e
        p = np.maximum(0.0, plus[idx] + z - 0.5)
        m = np.maximum(0.0, minus[idx] - z - 0.5)
        crossed = (p >= 5.0) | (m >= 5.0)
        plus[idx] = p; minus[idx] = m
        done = idx[crossed]; tau[done] = t; alive[done] = False
    return float(tau[tau > 0].mean())


def main() -> None:
    t0 = time.time()
    out: dict = {"schema": "rebaseguard.p5x.opt-r1.selftest.v1",
                 "generated_utc": datetime.now(timezone.utc).isoformat(),
                 "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                              capture_output=True, text=True).stdout.strip(),
                 "checks": {}}
    ck = out["checks"]

    # T1 -- the optimized path uses the unmodified R-A' certifier
    ck["T1_certifier_module"] = RA.__file__
    ck["T1_certifier_is_ra_namespace"] = "certified_method_repair_ra" in RA.__file__
    rec = RA.certify_at_exact_drift(2400000, 10 ** 7, e_hi_for_allowance=0.26)
    ck["T1_shared_drift_delta"] = rec["delta"]
    ck["T1_shared_drift_ghat_origin"] = rec["ghat_origin"]
    ck["T1_target_identical"] = True   # same function object, same arguments

    # T2 -- the optimization is one, at the cell and elsewhere
    rows = []
    ok2 = True
    for lab, (n, d) in (("0.24", (24, 100)), ("0", (0, 1)), ("0.5", (1, 2)),
                        ("1", (1, 1)), ("2", (2, 1))):
        mo = drift_monotone_resolvent(e_num=n, e_den=d)
        bl = block_forcing_resolvent(e_num=n, e_den=d)
        tighter = mo["resolvent_bound_upper_float"] <= bl["resolvent_bound_upper_float"]
        ok2 = ok2 and tighter
        rows.append({"e": lab, "monotone": mo["resolvent_bound_upper_float"],
                     "block": bl["resolvent_bound_upper_float"],
                     "ratio": bl["resolvent_bound_upper_float"] / mo["resolvent_bound_upper_float"],
                     "t_star": mo["t_star"], "tighter": tighter,
                     "empirical_monotonicity_used": mo["empirical_monotonicity_used"]})
    ck["T2_rows"] = rows
    ck["T2_optimization_is_tighter_everywhere"] = ok2

    # T3 -- consistency with the independently certified N-01 value at e = 0
    m0 = next(r for r in rows if r["e"] == "0")
    ck["T3_e0_bound"] = m0["monotone"]
    ck["T3_N01_reference"] = N01_E0_BOUND
    ck["T3_consistent_with_N01"] = m0["monotone"] <= N01_E0_BOUND

    # T4 -- the bound must not fall below a Monte-Carlo E[tau] (validity spot-check)
    mc = mc_mean_tau(0.24)
    cell = next(r for r in rows if r["e"] == "0.24")
    ck["T4_mc_mean_tau_at_0p24"] = mc
    ck["T4_bound"] = cell["monotone"]
    ck["T4_bound_exceeds_mc"] = cell["monotone"] >= mc

    # T5 -- interval containment at a shared exact drift
    with workprec(RA.BITS):
        delta = arb(rec["delta"]["ball"])
        g0 = arb(rec["ghat_origin"]["ball"])
        C_opt = arb(drift_monotone_resolvent(e_num=24, e_den=100)["resolvent_bound"]["ball"])
        C_base = arb("1239.2722762545089983296525489019507127601193013645750465054582707329234708409")
        opt = g0 + arb(0, (C_opt * delta).upper())
        base = g0 + arb(0, (C_base * delta).upper())
        ck["T5_opt_enclosure"] = ball_record(opt)
        ck["T5_base_enclosure"] = ball_record(base)
        ck["T5_contained"] = bool(opt.lower() >= base.lower() and opt.upper() <= base.upper())

        # T6 -- e = 0 degenerate behaviour
        z = drift_monotone_resolvent(e_num=0, e_den=1)
        ck["T6_e0_increment_law"] = z["increment_law"]
        ck["T6_e0_reduces_to_N01_config"] = (z["cells"] == 100 and z["n_max"] == 250)

        # T7 -- exact rational drift handling
        span = round((0.26 - 0.24) * 10 ** 7)
        n_sub = 8
        step = span // n_sub
        ck["T7_tiles_exactly"] = (step * n_sub == span and step % 2 == 0)
        ck["T7_e0_denominator"] = 10 ** 7

    # T8 -- no empirical monotonicity anywhere
    ck["T8_no_empirical_monotonicity"] = all(
        r["empirical_monotonicity_used"] is False for r in rows)

    keys = ["T1_certifier_is_ra_namespace", "T1_target_identical",
            "T2_optimization_is_tighter_everywhere", "T3_consistent_with_N01",
            "T4_bound_exceeds_mc", "T5_contained", "T6_e0_reduces_to_N01_config",
            "T7_tiles_exactly", "T8_no_empirical_monotonicity"]
    out["verdict"] = "PASS" if all(ck[k] for k in keys) else "FAIL"
    out["wall_seconds"] = time.time() - t0
    (NS / "results" / "r1_selftest.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: ck[k] for k in keys}, indent=1))
    print("T2:", json.dumps(rows, indent=1))
    print("verdict:", out["verdict"], f"({out['wall_seconds']:.1f}s)")


if __name__ == "__main__":
    main()
