#!/usr/bin/env python3
"""Emit the report's tables from the result JSON, so nothing is transcribed."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from p4y_pilot.config import B1_NOMINAL, REFERENCE_BLOCKS  # noqa: E402
from p4y_pilot.stats import clopper_pearson_lower  # noqa: E402

R = ROOT / "results"


def load(name):
    p = R / f"{name}.json"
    return json.loads(p.read_text()) if p.exists() else None


def rule_table(phase, title):
    rep = load("report")
    key = "validation_pooled" if phase == "validation" else "design_pooled"
    rows = rep[key]
    out = [f"### {title}", "",
           "| rule | third state possible | attained | funded | `PRECISION_LIMITED` | `UNRESOLVED` | p_attain (funded) | 95% CP lower | p_attain (uncond.) | mean × | max × |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for p in rows:
        funded = p["replicates"] - p["precision_limited"]
        out.append(
            f"| `{p['rule']}` | {'YES' if p['third_state_possible'] else 'no'} "
            f"| {p['attained']} | {funded} | {p['precision_limited']} "
            f"| **{p['unresolved']}** | {p['p_attain_within_cap']:.4f} "
            f"| {p['lower_bound_within_cap']:.4f} | {p['p_attain']:.3f} "
            f"| {p['mean_block_multiplier']:.2f} | {p['max_block_multiplier']:.2f} |")
    return "\n".join(out)


def per_cell_table(rule_name):
    rep = load("report")
    p = next(x for x in rep["validation_pooled"] if x["rule"] == rule_name)
    out = [f"| cell | configuration | route | attained / funded | 95% CP lower | mean × | max × |",
           "|---|---|---|---|---|---|---|"]
    for c in p["per_cell"]:
        funded = c["replicates"] - c["precision_limited"]
        lb = clopper_pearson_lower(c["attained"], funded, 0.05) if funded else 0.0
        out.append(f"| `{c['cell']}` | `{c['config']}` | {c['route'][-1].upper()} "
                   f"| {c['attained']} / {funded} | {lb:.4f} "
                   f"| {c['mean_block_multiplier']:.2f} | {c['max_block_multiplier']:.2f} |")
    return "\n".join(out)


def nominal_attainment():
    """Unbiased: every replicate draws exactly REFERENCE_BLOCKS reference blocks."""
    cal = {c["cell"]: c for c in load("calibration")["cells"]}
    out = ["| cell | configuration | route | realised ≤ true at B = 12 | fraction |",
           "|---|---|---|---|---|"]
    tot = hit = 0
    for phase in ("design", "validation"):
        d = load(phase)
        if not d:
            continue
        for c in d["cells"]:
            rt = c["r_star_pilot"] * math.sqrt(B1_NOMINAL / REFERENCE_BLOCKS)
            vals = [r["reference_relative_se"] for r in c["replicates"]]
            h = sum(v <= rt for v in vals)
            tot += len(vals); hit += h
    d = load("design")
    per = {}
    for phase in ("design", "validation"):
        p = load(phase)
        if not p:
            continue
        for c in p["cells"]:
            rt = c["r_star_pilot"] * math.sqrt(B1_NOMINAL / REFERENCE_BLOCKS)
            vals = [r["reference_relative_se"] for r in c["replicates"]]
            a, b = per.get(c["cell"], (0, 0))
            per[c["cell"]] = (a + sum(v <= rt for v in vals), b + len(vals))
    for cell, (h, n) in sorted(per.items()):
        info = cal[cell]
        out.append(f"| `{cell}` | `{info['config']}` | {info['route'][-1].upper()} "
                   f"| {h} / {n} | {h/n:.3f} |")
    out.append(f"| **pooled** | | | **{hit} / {tot}** | **{hit/tot:.3f}** |")
    return "\n".join(out)


def costtail_table():
    ct = load("costtail")
    if not ct:
        return "_cost-tail phase not run_"
    out = ["| cell | route | rule | attained / 24 | mean × | q50 × | q90 × | q95 × | max × | oracle q90 × | oracle max × |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in ct["cells"]:
        for s in c["rules"]:
            out.append(
                f"| `{c['cell']}` | {c['route'][-1].upper()} | `{s['rule']}` "
                f"| {s['attained']} / {s['replicates']} "
                f"| {s['mean_multiplier']:.2f} | {s['q50_multiplier']:.2f} "
                f"| {s['q90_multiplier']:.2f} | {s['q95_multiplier']:.2f} "
                f"| {s['max_multiplier']:.2f} | {c['oracle_q90']:.2f} "
                f"| {c['oracle_max']:.2f} |")
    return "\n".join(out)


def costtail_pooled():
    ct = load("costtail")
    if not ct:
        return {}
    agg = {}
    for c in ct["cells"]:
        for s in c["rules"]:
            a = agg.setdefault(s["rule"], {"att": 0, "n": 0, "max": 0.0,
                                           "mults": []})
            a["att"] += s["attained"]; a["n"] += s["replicates"]
            a["max"] = max(a["max"], s["max_multiplier"])
    for c in ct["cells"]:
        for rep in c["replicates"]:
            for name, o in rep["outcomes"].items():
                agg[name]["mults"].append(o["block_multiplier"])
    for name, a in agg.items():
        m = sorted(a["mults"])
        a["mean"] = sum(m) / len(m)
        a["q95"] = m[min(len(m) - 1, math.ceil(0.95 * len(m)) - 1)]
        a["lower"] = clopper_pearson_lower(a["att"], a["n"], 0.05)
    return agg


def main():
    parts = []
    if load("report"):
        parts.append(rule_table("design", "Design phase — 20 replicates × 6 cells"))
        if load("validation"):
            parts.append("")
            parts.append(rule_table("validation", "Validation phase — 59 replicates × 6 cells"))
    parts += ["", "### Unbiased nominal-attainment check", "", nominal_attainment()]
    parts += ["", "### Cost tail (AMENDMENT 1, 16× cap)", "", costtail_table()]
    ct = costtail_pooled()
    if ct:
        parts += ["", "### Cost tail pooled", "",
                  "| rule | attained / n | 95% CP lower | mean × | q95 × | max × |",
                  "|---|---|---|---|---|---|"]
        for name, a in ct.items():
            parts.append(f"| `{name}` | {a['att']} / {a['n']} | {a['lower']:.4f} "
                         f"| {a['mean']:.2f} | {a['q95']:.2f} | {a['max']:.2f} |")
    text = "\n".join(parts)
    (R / "tables.md").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    raise SystemExit(main())
