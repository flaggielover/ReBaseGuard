#!/usr/bin/env python3
"""P4ZB Phase 4 -- exploratory ladder study.  NOT RESULT BEARING.

Extends the ladder two rungs below the frozen steps on the four open cells, to
test the out-of-sample predictions of the h^4 model and to map the
pre-asymptotic / asymptotic / noise-dominated regions before any ladder is
frozen.  Uses a seed disjoint from every P4Z, P4ZA and historical seed.
"""
from __future__ import annotations
import json, math, os, sys, time
from pathlib import Path
import numpy as np

NS = Path(__file__).resolve().parent.parent
P4Z = NS.parent / "p4z_location_family_feasibility"
sys.path.insert(0, str(P4Z/"src"))
sys.path.insert(0, str(NS.parent/"p4_theory_generalization"/"src"))
from rebaseguard_p4_general.detectors import Detector       # noqa: E402
from rebaseguard_p4_general.families import REGISTRY        # noqa: E402
from rebaseguard_p4_general.simulate import stream_counter  # noqa: E402
from rebaseguard_p4z.analytic import FAMILY_KITS            # noqa: E402
from rebaseguard_p4z.rbmap import rb_map_batch              # noqa: E402

LADDER = (0.1, 0.05, 0.025, 0.0125, 0.00625)
M_GRID = (1, 2, 3, 5)
BLOCKS = 30
SEED = 4_290_001
PATHS = 32_268           # the frozen P4ZA block size for this configuration
MAX_STEPS = 200_000


def main() -> int:
    for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS","NUMEXPR_NUM_THREADS"):
        if os.environ.get(v) != "1":
            print(f"refusing: {v} must be 1", file=sys.stderr); return 2
    fam, kit = REGISTRY["skewnormal4"], FAMILY_KITS["skewnormal4"]
    det = Detector("cusum", 5.0)
    per = {h: {m: [] for m in M_GRID} for h in LADDER}
    t0 = time.process_time()
    for b in range(BLOCKS):
        for h in LADDER:
            g = rb_map_batch(family=fam, kit=kit, detector_kind="cusum",
                threshold=5.0, m_grid=M_GRID, e_values=(h,-h), n_paths=PATHS,
                seed=SEED, batch=b, max_steps=MAX_STEPS,
                new_state=det.new_state, step_fn=det.step,
                stream_counter=stream_counter)
            for m in M_GRID:
                per[h][m].append(float((-(g[h][m]-g[-h][m])/(2.0*h)).mean()))
        if (b+1) % 10 == 0:
            print(f"  {b+1}/{BLOCKS} blocks, {time.process_time()-t0:.0f} CPU-s", flush=True)
    cpu = time.process_time()-t0

    doc = {"schema":"rebaseguard.p4zb-ladder-study.v1","result_bearing":False,
           "purpose":"test the h^4 model out of sample and map the usable window",
           "configuration":"frozen/cusum@5/skewnormal4","ladder":list(LADDER),
           "blocks":BLOCKS,"block_paths":PATHS,"seed":SEED,
           "cpu_seconds":cpu,"by_m":{}}
    preds = json.loads((NS/"results"/"_predictions.json").read_text())
    print(f"\n{'m':>2s} {'h':>8s} {'D(h)':>11s} {'se':>9s} | {'adj diff':>10s} {'se':>8s} {'p':>6s}")
    for m in M_GRID:
        D = {h: np.array(per[h][m]) for h in LADDER}
        means = {f"{h:g}": float(D[h].mean()) for h in LADDER}
        ses = {f"{h:g}": float(D[h].std(ddof=1)/math.sqrt(BLOCKS)) for h in LADDER}
        diffs, orders, rich, adj = {}, {}, {}, {}
        for hc, hf in zip(LADDER[:-1], LADDER[1:]):
            d = D[hc]-D[hf]
            diffs[f"{hc:g}-{hf:g}"] = {"mean":float(d.mean()),
                "se":float(d.std(ddof=1)/math.sqrt(BLOCKS)),
                "snr":float(abs(d.mean())/(d.std(ddof=1)/math.sqrt(BLOCKS)))}
            R = (4*D[hf]-D[hc])/3.0
            rich[f"{hc:g}/{hf:g}"] = {"mean":float(R.mean()),
                "se":float(R.std(ddof=1)/math.sqrt(BLOCKS))}
        dk = list(diffs)
        for x,y in zip(dk[:-1], dk[1:]):
            ra, rb = diffs[x]["mean"], diffs[y]["mean"]
            orders[f"{x} / {y}"] = math.log2(ra/rb) if rb and ra/rb>0 else float("nan")
        rk = list(rich)
        for x,y in zip(rk[:-1], rk[1:]):
            adj[f"{x} vs {y}"] = {"difference":rich[x]["mean"]-rich[y]["mean"],
                                  "relative":abs(rich[x]["mean"]-rich[y]["mean"])/abs(rich[y]["mean"])}
        p = preds[str(m)]
        doc["by_m"][str(m)] = {"central_difference":means,"central_difference_se":ses,
            "paired_differences":diffs,"implied_orders":orders,
            "richardson":rich,"adjacent_richardson":adj,
            "prediction_test":{
                "D_0.0125_predicted":p["D_0.0125"],"D_0.0125_observed":means["0.0125"],
                "D_0.0125_abs_error":abs(p["D_0.0125"]-means["0.0125"]),
                "D_0.0125_error_in_se":abs(p["D_0.0125"]-means["0.0125"])/ses["0.0125"],
                "D_0.00625_predicted":p["D_0.00625"],"D_0.00625_observed":means["0.00625"],
                "D_0.00625_error_in_se":abs(p["D_0.00625"]-means["0.00625"])/ses["0.00625"],
                "p_fine_predicted":p["p_fine"],
                "p_fine_observed":orders.get("0.05-0.025 / 0.025-0.0125"),
                "p_finer_predicted":p["p_finer"],
                "p_finer_observed":orders.get("0.025-0.0125 / 0.0125-0.00625")}}
        for h in LADDER:
            k=f"{h:g}"
            dd = diffs.get(f"{h:g}-{LADDER[LADDER.index(h)+1]:g}") if h!=LADDER[-1] else None
            print(f"{m:>2d} {h:8.5f} {means[k]:11.6f} {ses[k]:9.6f} | "
                  f"{dd['mean']:10.6f} {dd['se']:8.6f} " % () if False else
                  f"{m:>2d} {h:8.5f} {means[k]:11.6f} {ses[k]:9.6f} | " +
                  (f"{dd['mean']:10.6f} {dd['se']:8.6f} {dd['snr']:6.1f}" if dd else ""))
    (NS/"results"/"ladder_study.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    print(f"\ntotal {cpu:.1f} CPU-s -> results/ladder_study.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
