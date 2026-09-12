"""Wall-time model for the PS1 production campaign, from committed evidence only.

Production dispatches a WHOLE cell group to an idle worker slot (production_launcher.Pool:
`while groups and pool.idle(): submit(slot, group)`; ps1_pool_worker.run_group runs all 3,994
live patches for that group's cells in the one worker). A group is never split across workers,
so the wall time is the makespan of 93 tasks greedily dispatched to 16 slots, and the only
imbalance is quantisation: 93 does not divide by 16.

The qualification harness had a different shape -- all 16 workers split the patch range of ONE
group -- so its within-group worker imbalance is reported here for contrast and is explicitly
NOT part of the production model.
"""
import collections
import glob
import json
import re
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
E = NS / "evidence"
CP = NS.parent
WORKERS = 16


def makespan(tasks, slots):
    """Greedy dynamic dispatch: each task goes to the slot that frees first."""
    load = [0.0] * slots
    count = [0] * slots
    for t in tasks:                       # tasks are taken in manifest order by whichever slot frees first
        i = min(range(slots), key=lambda k: load[k])
        load[i] += t
        count[i] += 1
    return max(load), load, count


def main():
    qs = json.loads((E / "qual_summary.json").read_text())
    man = json.loads((CP / "p5y_k1_ps1_production/config/SHARD_MANIFEST.json").read_text())
    groups = man["groups"]
    st = qs["per_cell_cpu_h_stats"]
    g4 = qs["group4_per_cell_cpu_h"]
    term = qs["terminal_single_cpu_h"][0]

    bases = {"mean_based": st["mean"], "worst_group_based": g4["max"]}
    out = {"schema": "rebaseguard.p5y.k1.ps1.makespan-model.v1",
           "dispatch": "whole group to an idle slot (greedy dynamic); a group is never split across workers",
           "workers": WORKERS, "groups": len(groups),
           "group_sizes": dict(collections.Counter(len(g) for g in groups)),
           "terminal_single_cell_cpu_h": term, "scenarios": {}}
    for name, per_cell in bases.items():
        tasks = [term if len(g) == 1 else len(g) * per_cell for g in groups]
        mk, load, count = makespan(tasks, WORKERS)
        total = sum(tasks)
        out["scenarios"][name] = {
            "per_cell_cpu_h": per_cell, "total_cpu_h": total,
            "ideal_wall_h_if_perfectly_divisible": total / WORKERS,
            "makespan_wall_h": mk, "makespan_wall_days": mk / 24.0,
            "utilisation": total / (WORKERS * mk),
            "quantisation_factor_vs_ideal": mk / (total / WORKERS),
            "groups_per_slot": {str(k): v for k, v in sorted(collections.Counter(count).items())},
            "slot_loads_cpu_h": [round(x, 2) for x in sorted(load, reverse=True)]}

    # contrast: qualification harness topology (16 workers split ONE group's patch range)
    cost = collections.defaultdict(float)
    for f in glob.glob(str(E / "qual/chunks/rec_s*_p_*.jsonl")):
        m = re.search(r"rec_s(\d+)_p_(\d+)\.jsonl$", f)
        cell, w = int(m.group(1)), int(m.group(2))
        for line in open(f):
            cost[(cell, w)] += json.loads(line)["cpu_seconds"]
    qual_groups = {"0-3": [0, 1, 2, 3], "148-151": [148, 149, 150, 151], "360-363": [360, 361, 362, 363]}
    contrast = {}
    for name, cells in qual_groups.items():
        per_w = [sum(cost[(c, w)] for c in cells) / 3600.0 for w in range(WORKERS)]
        contrast[name] = {"slowest_worker_cpu_h": max(per_w), "mean_worker_cpu_h": sum(per_w) / WORKERS,
                          "imbalance": max(per_w) / (sum(per_w) / WORKERS),
                          "core_h_idle_in_window": WORKERS * max(per_w) - sum(per_w)}
    out["qualification_harness_contrast"] = {
        "note": "16 workers split ONE group's patch range; low patch indices carried 290/291 patches against ~244 "
                "and were the expensive ones. This shape does NOT occur in production.",
        "groups": contrast,
        "mean_imbalance": sum(v["imbalance"] for v in contrast.values()) / len(contrast)}
    (E / "qual/makespan_model.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for k, v in out["scenarios"].items():
        print(f"{k}: total {v['total_cpu_h']:.0f} CPU-h  ideal {v['ideal_wall_h_if_perfectly_divisible']/24:.2f} d  "
              f"makespan {v['makespan_wall_days']:.2f} d  utilisation {v['utilisation']:.3f}  "
              f"quantisation {v['quantisation_factor_vs_ideal']:.3f}x")
    print("qualification-harness imbalance (contrast only): %.2fx" % out["qualification_harness_contrast"]["mean_imbalance"])


if __name__ == "__main__":
    main()
