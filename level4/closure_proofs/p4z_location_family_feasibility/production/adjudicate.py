#!/usr/bin/env python3
"""P4Z gate adjudication -- the frozen criteria, applied mechanically.

Separate from the runner on purpose: the process that produces numbers does not
decide whether they pass.  Every threshold is read from the frozen sources, no
threshold appears as a literal here except through those sources, and there is
no manual override and no "close enough".

Rounding: every gate comparison is made CONSERVATIVELY, meaning in the
direction that makes a PASS harder.  Statistics are rounded UP (away from zero)
to 12 decimal places before comparison, and limits are used exactly.  At double
precision this changes no decision that is not already at the threshold to
within 1e-12; it is documented so the direction is on the record.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

NS = Path(__file__).resolve().parent.parent
BLOCK_DIR = NS / "production" / "blocks"
ROUND_DP = 12


def _round_up(value: float) -> float:
    """Round a test statistic away from zero -- conservative for <= gates."""
    if not math.isfinite(value):
        return value
    scale = 10 ** ROUND_DP
    return math.ceil(abs(value) * scale) / scale * (1.0 if value >= 0 else -1.0)


def _blocks(cfg_id: str, route: str) -> list[dict]:
    safe = cfg_id.replace("/", "__").replace("@", "_at_")
    directory = BLOCK_DIR / safe
    if not directory.exists():
        return []
    return [json.loads(p.read_text())
            for p in sorted(directory.glob(f"{route}_*.json"))]


def _summarise(docs: list[dict], m: int) -> dict[str, float] | None:
    if len(docs) < 2:
        return None
    values = np.array([d["block_mean"][str(m)] for d in docs], dtype=float)
    mean = float(values.mean())
    se = float(values.std(ddof=1) / math.sqrt(values.size))
    dev = (values - mean) ** 2
    total = float(dev.sum())
    order = np.sort(dev)[::-1]
    return {
        "mean": mean, "mc_se": se, "blocks": int(values.size),
        "relative_se": abs(se / mean) if mean != 0 else math.inf,
        "top1_share_of_block_variance": float(order[0] / total) if total > 0 else 0.0,
        "top5_share_of_block_variance": float(order[:5].sum() / total) if total > 0 else 0.0,
        "paths": int(sum(d["block_paths"] for d in docs)),
        "cpu_seconds": float(sum(d["cpu_seconds"] for d in docs)),
    }


def _truncation_bound(cfg_id: str, m: int, plan: dict) -> dict[str, float] | None:
    """T_B = |R(0.2,0.1) - R(0.05,0.025)|, the frozen Richardson drift."""
    docs = _blocks(cfg_id, "fd_ladder")
    if len(docs) < 2:
        return None
    ladder = plan["fd_ladder_steps"]
    coarse_key = f"{ladder[0]:g}/{ladder[1]:g}"
    fine_key = f"{ladder[2]:g}/{ladder[3]:g}"
    coarse = np.array([d["richardson_by_pair"][coarse_key][str(m)] for d in docs])
    fine = np.array([d["richardson_by_pair"][fine_key][str(m)] for d in docs])
    t_b = abs(float(coarse.mean()) - float(fine.mean()))
    scale = max(abs(float(coarse.mean())), abs(float(fine.mean())))
    return {
        "richardson_coarse_pair": float(coarse.mean()),
        "richardson_frozen_pair": float(fine.mean()),
        "T_B": t_b,
        "relative_drift": t_b / scale if scale > 0 else math.inf,
        "ladder_blocks": int(len(docs)),
        "coarse_pair": coarse_key, "frozen_pair": fine_key,
    }


def adjudicate() -> dict[str, object]:
    plan = json.loads((NS / "production" / "campaign_plan.json").read_text())
    checkpoint = json.loads((NS / "configs" / "checkpoint_p4z.json").read_text())
    thr = plan["thresholds"]
    rel_limit = thr["relative"]
    z_limit = thr["z"]
    r_star = thr["r_star"]
    top1_max = thr["top1_share_max"]
    top5_max = thr["top5_share_max"]
    ladder_max = thr["fd_ladder_relative_max"]

    # the frozen thresholds must still equal their sources
    assert rel_limit == 0.03 and z_limit == 4.0
    assert r_star == checkpoint["gate_thresholds_unchanged"]["r_star"]

    cells, counts = [], {"PASS": 0, "FAIL": 0, "INCONCLUSIVE": 0}
    for cfg in plan["configurations"]:
        a_docs = _blocks(cfg["id"], "rb_score")
        b_docs = _blocks(cfg["id"], "rb_map")
        for m in plan["scope"]["m_grid"]:
            a = _summarise(a_docs, m)
            b = _summarise(b_docs, m)
            ladder = _truncation_bound(cfg["id"], m, plan)
            row = {
                "layer": cfg["layer"], "detector": cfg["detector"],
                "family": cfg["family"], "m": m,
                "configuration": cfg["id"],
                "is_historically_unresolved": m in cfg["unresolved_m"],
                "rb_score": a, "rb_map": b, "fd_ladder": ladder,
            }
            reasons = []
            if a is None or b is None or ladder is None:
                row["gate_result"] = "INCONCLUSIVE"
                row["reasons"] = ["missing blocks for a required route"]
                counts["INCONCLUSIVE"] += 1
                cells.append(row)
                continue

            # --- preconditions, each a frozen kill gate ---------------------
            # K5 and K6 are specified in the checkpoint as evaluated "after all
            # 200 blocks, per route".  The concentration statistic K5 uses is
            # strongly sample-size dependent -- at n = 20 a perfectly Gaussian
            # sample has a median top-1 share of 0.23 against a 0.10 limit, and
            # at n = 200 it has 0.043 -- so the frozen thresholds discriminate
            # only at the block count they were calibrated for.  Evaluating
            # them earlier is not a stricter gate, it is a different one.  A
            # route short of its full block count is INCONCLUSIVE for
            # incompleteness instead.
            full = plan["fixed_policy"]["blocks_per_route_full"]
            complete = a["blocks"] >= full and b["blocks"] >= full
            if not complete:
                row["gate_result"] = "INCONCLUSIVE"
                row["reasons"] = [
                    f"route block counts {a['blocks']}/{b['blocks']} below the "
                    f"frozen {full}; K5 and K6 are specified after all {full} "
                    "blocks and are not evaluated early"]
                row["preconditions"] = {"complete": False}
                counts["INCONCLUSIVE"] += 1
                cells.append(row)
                continue
            k6_a = _round_up(a["relative_se"]) > r_star
            k6_b = _round_up(b["relative_se"]) > r_star
            k5_a = (_round_up(a["top1_share_of_block_variance"]) > top1_max
                    or _round_up(a["top5_share_of_block_variance"]) > top5_max)
            k5_b = (_round_up(b["top1_share_of_block_variance"]) > top1_max
                    or _round_up(b["top5_share_of_block_variance"]) > top5_max)
            k7 = _round_up(ladder["relative_drift"]) > ladder_max
            if k6_a: reasons.append("K6 rb_score relative SE above r*")
            if k6_b: reasons.append("K6 rb_map relative SE above r*")
            if k5_a: reasons.append("K5 rb_score block variance not scale stable")
            if k5_b: reasons.append("K5 rb_map block variance not scale stable")
            if k7: reasons.append("K7 Richardson drift above the ladder limit")

            # --- the frozen correspondence statistics ------------------------
            se_b = math.hypot(b["mc_se"], ladder["T_B"])
            diff = abs(a["mean"] - b["mean"])
            scale = max(abs(a["mean"]), abs(b["mean"]))
            rel = _round_up(diff / scale) if scale > 0 else math.inf
            combined = math.hypot(a["mc_se"], se_b)
            z = _round_up(diff / combined) if combined > 0 else math.inf
            row["correspondence"] = {
                "se_a": a["mc_se"], "se_b_mc": b["mc_se"],
                "T_B": ladder["T_B"], "se_b_total": se_b,
                "absolute_difference": diff,
                "relative_discrepancy": rel,
                "combined_se": combined, "z": z,
                "relative_limit": rel_limit, "z_limit": z_limit,
                "relative_ok": rel <= rel_limit, "z_ok": z <= z_limit,
                "rounding": f"statistics rounded away from zero at {ROUND_DP} dp",
            }
            row["preconditions"] = {
                "K5_rb_score_scale_stable": not k5_a,
                "K5_rb_map_scale_stable": not k5_b,
                "K6_rb_score_meets_r_star": not k6_a,
                "K6_rb_map_meets_r_star": not k6_b,
                "K7_fd_ladder_within_limit": not k7,
            }
            if reasons:
                row["gate_result"] = "INCONCLUSIVE"
            elif rel <= rel_limit and z <= z_limit:
                row["gate_result"] = "PASS"
            else:
                row["gate_result"] = "FAIL"
                if rel > rel_limit:
                    reasons.append("relative discrepancy above 0.03")
                if z > z_limit:
                    reasons.append("|z| above 4.0")
            row["reasons"] = reasons
            counts[row["gate_result"]] += 1
            cells.append(row)

    state_path = NS / "production" / "run_state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    cpu_total = state.get("cpu_seconds_total", 0.0)
    cap = plan["budget"]["total_cpu_cap_hours"]
    doc = {
        "schema": "rebaseguard.p4z-adjudication.v1",
        "result_bearing": True,
        "thresholds_used": {
            "relative": rel_limit, "z": z_limit, "r_star": r_star,
            "top1_share_max": top1_max, "top5_share_max": top5_max,
            "fd_ladder_relative_max": ladder_max,
            "source": "campaign_plan.json, derived from P4_PROTOCOL.json and checkpoint_p4z.json",
            "any_threshold_changed_by_p4z": False,
        },
        "precondition_evaluation_point":
            "K5 and K6 are evaluated only when both routes have their full "
            "frozen block count, as the checkpoint specifies. The K5 "
            "concentration statistic is sample-size dependent: a clean Gaussian "
            "sample has a median top-1 share of 0.23 at n=20 and 0.043 at "
            "n=200, so the frozen 0.10 limit discriminates only at n=200.",
        "rounding_policy":
            "test statistics rounded AWAY FROM ZERO at 12 decimal places before "
            "comparison against exact limits; conservative for every <= gate",
        "counts": counts,
        "cells_total": len(cells),
        "unresolved_residue": {
            "total": sum(1 for c in cells if c["is_historically_unresolved"]),
            "by_result": {
                r: sum(1 for c in cells
                       if c["is_historically_unresolved"] and c["gate_result"] == r)
                for r in ("PASS", "FAIL", "INCONCLUSIVE")},
        },
        "cost": {
            "cpu_hours_total": cpu_total / 3600.0,
            "cap_hours": cap,
            "COST_CAP": "PASS" if cpu_total / 3600.0 <= cap else "FAIL",
            "note": "includes every block produced, failed and inconclusive alike",
        },
        "excluded_configurations": state.get("excluded", {}),
        "killed_configurations": state.get("killed", {}),
        "cells": cells,
    }
    return doc


def main() -> int:
    doc = adjudicate()
    out = NS / "production" / "adjudication.json"
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    c = doc["counts"]
    print(f"cells {doc['cells_total']}   PASS {c['PASS']}   FAIL {c['FAIL']}   "
          f"INCONCLUSIVE {c['INCONCLUSIVE']}")
    print(f"historically unresolved residue: {doc['unresolved_residue']}")
    print(f"CPU {doc['cost']['cpu_hours_total']:.4f} h of {doc['cost']['cap_hours']} "
          f"-> COST_CAP {doc['cost']['COST_CAP']}")
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
