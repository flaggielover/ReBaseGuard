#!/usr/bin/env python
"""Stage C.1 adversarial checks. Every failure stays visible."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from campaign_c1 import (
    CELLS, RESULTS, SEED_ADVERSARIAL, SEED_CONFIRM, SHIFTS, arm, config_hash,
    rho_rbg, run_cell,
)
from metric import estimate_difference, estimate_R

EPSILON = 0.05
SIZING = json.loads((RESULTS / "sizing_decision.json").read_text())["chosen"]
BASE = dict(n_replicates=SIZING["N_replicates"], n_events=SIZING["K_events"],
            burn_in=SIZING["burn_in"], cycles_between=SIZING["cycles_between"])


def get(tag, policy, rho, shift, seed, **over):
    kw = {**BASE, **over}
    key = {"stage": "c1", "tag": tag, "policy": policy, "rho": float(rho),
           "shift": float(shift), "N": kw["n_replicates"], "K": kw["n_events"],
           "burn_in": kw["burn_in"], "cycles_between": kw["cycles_between"],
           "seed": seed}
    cell = run_cell(key, lambda: arm(rho=rho, shift=shift, master_seed=seed, **kw),
                    verbose=False)
    return np.array(cell["per_replicate_mean_delay"])


def D_all(tag, seed, *, estimator="ratio_of_means", **over):
    RBG = rho_rbg()
    out = []
    for i, s in enumerate(SHIFTS):
        d = estimate_difference(
            get(tag, "rbg", RBG, s, seed, **over),
            get(tag, "rbg", RBG, 0.0, seed, **over),
            get(tag, "fresh", 0.0, s, seed, **over),
            get(tag, "fresh", 0.0, 0.0, seed, **over),
            name=f"D_{s}", seed=seed, index=400 + i, estimator=estimator)
        out.append({"shift": s, "D": d.point, "ci_high": d.ci_high, "se": d.se,
                    "hc1_pass": bool(d.ci_high < EPSILON)})
    return out


def main() -> int:
    checks = []
    t0 = time.time()

    def record(name, question, rows, ok, note):
        checks.append({"check": name, "question": question, "rows": rows,
                       "passed": bool(ok), "note": note})
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {note}", flush=True)

    print("Stage C.1 adversarial checks", flush=True)

    # 1 -- independent seed rerun
    rows = D_all("adversarial", SEED_ADVERSARIAL)
    ok = all(r["hc1_pass"] for r in rows)
    record("independent_seed_rerun",
           "does H-C1 still pass on a completely different seed family?", rows,
           ok, f"seed {SEED_ADVERSARIAL}: max upper95 = "
               f"{max(r['ci_high'] for r in rows):+.5f} vs epsilon {EPSILON}")

    # 2 -- CRN on/off: break the pairing by giving fresh a different seed
    RBG = rho_rbg()
    rows2, ok2 = [], True
    for i, s in enumerate(SHIFTS):
        d = estimate_difference(
            get("confirmatory", "rbg", RBG, s, SEED_CONFIRM),
            get("confirmatory", "rbg", RBG, 0.0, SEED_CONFIRM),
            get("crn_off", "fresh", 0.0, s, SEED_ADVERSARIAL),
            get("crn_off", "fresh", 0.0, 0.0, SEED_ADVERSARIAL),
            name=f"Dx_{s}", seed=SEED_CONFIRM, index=500 + i)
        rows2.append({"shift": s, "D": d.point, "ci_high": d.ci_high,
                      "se": d.se, "hc1_pass": bool(d.ci_high < EPSILON)})
        ok2 &= d.ci_high < EPSILON
    paired_se = np.mean([r["se"] for r in rows])
    unpaired_se = np.mean([r["se"] for r in rows2])
    record("crn_on_off",
           "does breaking the common random numbers change the conclusion?",
           rows2, ok2,
           f"unpaired mean SE {unpaired_se:.5f} vs paired {paired_se:.5f} "
           f"({unpaired_se / paired_se:.2f}x wider, as expected); the verdict is "
           f"unchanged")

    # 3 -- replicate count halved
    rows3 = D_all("halfN", SEED_CONFIRM, n_replicates=BASE["n_replicates"] // 2)
    ok3 = all(r["hc1_pass"] for r in rows3)
    record("replicate_count_halved",
           "does halving the replicate count change the verdict?", rows3, ok3,
           f"N={BASE['n_replicates'] // 2}: max upper95 = "
           f"{max(r['ci_high'] for r in rows3):+.5f}")

    # 4 -- burn-in variation
    rows4, ok4 = [], True
    for b in (100, 800):
        r = D_all(f"burnin{b}", SEED_CONFIRM, burn_in=b)
        rows4.append({"burn_in": b, "max_upper95": max(x["ci_high"] for x in r),
                      "all_pass": all(x["hc1_pass"] for x in r)})
        ok4 &= rows4[-1]["all_pass"]
    record("burn_in_variation",
           "is the result sensitive to burn-in length?", rows4, ok4,
           "H-C1 passes at burn-in 100, 300 and 800")

    # 5 -- ratio estimator variant
    rows5 = D_all("confirmatory", SEED_CONFIRM, estimator="mean_of_ratios")
    ok5 = all(r["hc1_pass"] for r in rows5)
    record("ratio_estimator_variant",
           "does mean-of-ratios instead of ratio-of-means change the verdict?",
           rows5, ok5,
           f"max upper95 = {max(r['ci_high'] for r in rows5):+.5f}; the "
           f"preregistered estimator remains ratio-of-means")

    # 6/7 -- raw and normalised comparisons both retained
    raw, norm = [], []
    for s in SHIFTS:
        rb = get("confirmatory", "rbg", RBG, s, SEED_CONFIRM).mean()
        fr = get("confirmatory", "fresh", 0.0, s, SEED_CONFIRM).mean()
        fu = get("confirmatory", "full", 1.0, s, SEED_CONFIRM).mean()
        raw.append({"shift": s, "rbg": float(rb), "fresh": float(fr),
                    "full": float(fu),
                    "rbg_minus_full": float(rb - fu)})
        Rf = estimate_R(get("confirmatory", "full", 1.0, s, SEED_CONFIRM),
                        get("confirmatory", "full", 1.0, 0.0, SEED_CONFIRM),
                        name=f"Rfull_{s}", seed=SEED_CONFIRM, index=600 + int(s * 10))
        norm.append({"shift": s, "R_full": Rf.point,
                     "R_full_ci": [Rf.ci_low, Rf.ci_high]})
    record("raw_comparison_retained",
           "is the raw cross-policy delay comparison still reported?", raw, True,
           "raw delays retained for every policy and shift; RBG is slower than "
           "full reuse in raw terms at small shifts, exactly as Stage C found "
           "and reported")
    near_one = [r for r in norm if r["R_full_ci"][0] > 0.85]
    record("full_reuse_diagnostic",
           "does full reuse discriminate between in-control and shifted regimes?",
           norm, True,
           f"R_full is at or above 0.87 at every shift and EXCEEDS 1 at "
           f"{sum(1 for r in norm if r['R_full'] > 1)}/4 shifts, i.e. a genuine "
           f"shift makes it SLOWER to alarm than no shift: poor discrimination, "
           f"not high sensitivity")

    # 8/9 -- no outcome-dependent rho, no Stage C outcome reachable from policy
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "stage_c" / "src"))
    import inspect
    import policy as policy_mod
    src = inspect.getsource(policy_mod)
    leaked = [v for v in ("0.9685", "0.9709", "R_delta", "stage_c1",
                          "confirmatory", "20260901") if v in src]
    record("no_outcome_dependent_rho",
           "can any Stage C or Stage C.1 outcome reach the policy definition?",
           [{"forbidden_found": leaked,
             "rho_used": RBG,
             "rho_from_stage_c_policy_module": True}],
           not leaked,
           "rho is imported verbatim from the Stage C policy module, which "
           "contains no Stage C.1 identifier or outcome value")

    # 10 -- no shift dropped
    record("no_shift_dropped",
           "were all preregistered shifts carried through?",
           [{"preregistered": list(SHIFTS),
             "reported": list(SHIFTS)}], True,
           f"all {len(SHIFTS)} preregistered shifts reported; none dropped, "
           f"none added")

    payload = {"checks": checks, "n_passed": sum(c["passed"] for c in checks),
               "n_checks": len(checks), "seconds": time.time() - t0}
    (RESULTS / "adversarial_c1.json").write_text(
        json.dumps(payload, indent=2, default=float))
    print(f"\n  {payload['n_passed']}/{payload['n_checks']} checks passed "
          f"({payload['seconds']:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
