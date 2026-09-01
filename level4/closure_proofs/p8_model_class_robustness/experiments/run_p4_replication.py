"""E6: the P4 replication diagnostic.

P4's frozen gate failed because its two independent Route-B replications of the
``t3`` cell differed by 4.605%, above a 3% limit
(``location_family/FINAL_REPORT.md`` section A).  P8 does not own, edit or
re-open that artifact.  What P8 *can* do is measure the sampling behaviour of
the same estimand on its own field and report whether a spread of that size is
what an estimator with a divergent third absolute moment produces at that
sample size.

Design: 12 independent replications per family of ``409,600`` cycles each, at
``m = 1``, CUSUM, the frozen Stage-D thresholds.  Reported per family: the
across-replication spread, the ratio of the observed replication scatter to the
mean nominal within-replication SE, and the max pairwise relative difference --
the statistic P4's gate used.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))
from rebaseguard_p8.config import (                                 # noqa: E402
    FAMILIES, MOMENT_MARGINAL, RESULTS, stage_d_cusum_thresholds)
from rebaseguard_p8.stopped import simulate_batch                   # noqa: E402

N_REPLICATIONS = 12
ROW_BLOCKS = 100                    # 409,600 cycles per replication
EXPERIMENT = "p8_p4_replication_E6"


OUT = RESULTS / "p4_rep"


def one(fam: str) -> dict:
    thr = stage_d_cusum_thresholds()
    rows, t0 = [], time.time()
    for _ in (0,):
        vals, ses = [], []
        for k in range(N_REPLICATIONS):
            s = simulate_batch(experiment=EXPERIMENT, family=fam,
                               detector="cusum", threshold=thr[fam],
                               batch=5000 + k, n_row_blocks=ROW_BLOCKS, L=2)
            g = s.zbar(1, "A") * s.Psi
            vals.append(float(g.mean()))
            ses.append(float(g.std(ddof=1) / np.sqrt(g.size)))
            print(f"  {fam} rep {k+1}/{N_REPLICATIONS} "
                  f"gamma={vals[-1]:.4f} nominal_se={ses[-1]:.4f} "
                  f"[{time.time()-t0:.0f}s]", flush=True)
        v = np.array(vals)
        nominal = float(np.mean(ses))
        observed = float(v.std(ddof=1))
        pair = [abs(v[i] - v[j]) / min(v[i], v[j])
                for i in range(len(v)) for j in range(i + 1, len(v))]
        rows.append({
            "family": fam, "threshold": thr[fam],
            "moment_marginal": fam in MOMENT_MARGINAL,
            "n_replications": N_REPLICATIONS,
            "cycles_per_replication": ROW_BLOCKS * 4096,
            "gamma_values": vals, "nominal_se_values": ses,
            "mean": float(v.mean()),
            "observed_across_replication_sd": observed,
            "mean_nominal_within_replication_se": nominal,
            "variance_inflation_ratio": observed / nominal if nominal else None,
            "max_pairwise_relative_difference": float(max(pair)),
            "mean_pairwise_relative_difference": float(np.mean(pair)),
            "p4_gate_limit": 0.03,
            "would_fail_p4_replication_gate": bool(max(pair) > 0.03)})
        print(f"{fam:11s} mean={v.mean():.4f} sd_obs={observed:.4f} "
              f"se_nom={nominal:.4f} ratio={observed/nominal:.2f} "
              f"maxpair={max(pair):.4f}", flush=True)
    OUT.mkdir(exist_ok=True)
    (OUT / f"{fam}.json").write_text(json.dumps(rows[0], indent=1) + "\n")
    return rows[0]


def merge() -> None:
    from scipy import stats
    rows = [json.loads((OUT / f"{f}.json").read_text()) for f in FAMILIES]
    for r in rows:
        v = np.array(r["gamma_values"])
        pair = np.array([abs(v[i] - v[j]) / min(v[i], v[j])
                         for i in range(v.size) for j in range(i + 1, v.size)])
        rel_sd = r["observed_across_replication_sd"] / r["mean"]
        # P4 compared exactly TWO replications, so the P4-comparable statistic is
        # the behaviour of ONE random pair, not the max over 66 of them.
        r["n_pairs"] = int(pair.size)
        r["empirical_P_single_pair_exceeds_3pct"] = float((pair > 0.03).mean())
        r["normal_approx_P_single_pair_exceeds_3pct"] = float(
            2.0 * stats.norm.sf(0.03 / (np.sqrt(2.0) * rel_sd))) if rel_sd > 0 else None
        r["relative_across_replication_sd"] = float(rel_sd)
        r["median_pairwise_relative_difference"] = float(np.median(pair))
        r["note_on_comparability"] = (
            "P8 uses 409,600 cycles per replication; P4's Route B used 2 "
            "replications of 240,000 paths each, so P4's per-replication SE is "
            "about 1.3x larger than P8's and its single-pair spread is "
            "correspondingly wider. P8 does not adjudicate P4.")
    out = {"schema": "rebaseguard.p8.p4-replication-diagnostic.v1",
           "experiment_tag": EXPERIMENT,
           "purpose": ("diagnose the sampling behaviour of the m=1 raw-reuse "
                       "gain estimator per family. P8 does not edit, re-open or "
                       "adjudicate P4."),
           "p4_reported": {"t3_replication_relative_difference": 0.04605,
                           "frozen_limit": 0.03,
                           "source": "location_family/FINAL_REPORT.md section A"},
           "rows": rows}
    (RESULTS / "p4_replication_diagnostic.json").write_text(
        json.dumps(out, indent=1) + "\n")
    print("merged", len(rows), "families")


if __name__ == "__main__":
    if sys.argv[1] == "--merge":
        merge()
    else:
        one(sys.argv[1])
