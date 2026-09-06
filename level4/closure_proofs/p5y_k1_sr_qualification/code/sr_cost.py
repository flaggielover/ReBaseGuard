"""Honest SR cost instrumentation.

Four strictly separated quantities. Nothing here reuses the historical SR
extrapolation (Gate-2F's 1,868 / 3,092 / 3,697 / 4,597 CPU-hours), which is a
projection under a superseded backend and is listed as a non-reusable route in
config/excluded_routes.json.

    measured_object_cost    CPU seconds actually spent on one object class
    measured_cell_cost      CPU seconds actually spent on one whole cell
    modeled_campaign_cost   measured cell cost x 316 cells, no margin
    conservative_campaign   modeled x contingency, stated with its factor

No claim is made, in either direction, about the 1126 CPU-hour cap until real
cell measurements exist. `campaign_projection` refuses to report a verdict.
"""
from __future__ import annotations

import json
import resource
import time
from contextlib import contextmanager
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
SR_CELLS = 316


@contextmanager
def measure(label: str, sink: list):
    """Measure CPU seconds and peak RSS of a block, appending one record."""
    t0 = time.process_time()
    w0 = time.perf_counter()
    r0 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    try:
        yield
    finally:
        r1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        sink.append({
            "label": label,
            "cpu_seconds": round(time.process_time() - t0, 6),
            "wall_seconds": round(time.perf_counter() - w0, 6),
            "peak_rss_mib": round(max(r0, r1) / 1024.0, 3),
        })


COST_CATEGORIES = (
    "resolvent",      # independent n-step resolvent corroboration, per cell
    "candidate",      # one patch-resolved candidate solve
    "object",         # one object class on one patch
    "patch",          # all objects on one patch
    "midpoint",       # the second propagation performed at e0
    "refinement",     # the monotone whole-cell refinement iteration
    "order3",         # nested order-3 auxiliary evidence, if built
    "assembly",       # exact all-m interval assembly
    "cell",           # one whole cell, all objects and all m
    "provenance",     # TCB hashing, runtime binding, scientific hash
)

SR_LIVE_PATCHES = 3994


def cost_formulas() -> dict:
    """The projection formulas, stated explicitly and never pre-evaluated."""
    return {
        "measured_pilot_cost": "sum of measured category CPU seconds for one pilot cell",
        "modeled_per_cell": "candidate*n_live_patches + midpoint + refinement + assembly + provenance",
        "modeled_316_cells": "modeled_per_cell * 316  (+ resolvent corroboration if run per cell)",
        "conservative_sr": "modeled_316_cells * contingency",
        "combined_campaign": "CUSUM_measured + SR_measured, summed only when BOTH are complete",
        "cap_rule": ("the 1126 CPU-hour cap is adjudicated ONCE on the sum, after "
                     "both detectors finish; neither side may claim it alone"),
        "excluded": "the historical Gate-2F SR extrapolation is not reused",
    }


def by_category(records: list) -> dict:
    """Split measured CPU seconds by cost category (label prefix before ':')."""
    out = {c: {"n": 0, "cpu_seconds": 0.0, "peak_rss_mib": 0.0}
           for c in COST_CATEGORIES}
    for r in records:
        cat = r["label"].split(":")[0]
        if cat not in out:
            continue
        out[cat]["n"] += 1
        out[cat]["cpu_seconds"] += r["cpu_seconds"]
        out[cat]["peak_rss_mib"] = max(out[cat]["peak_rss_mib"], r["peak_rss_mib"])
    return out


def campaign_projection(cell_records: list, *, contingency: float = 2.0) -> dict:
    """Project a campaign from MEASURED cell costs only. No cap verdict."""
    measured = [r["cpu_seconds"] for r in cell_records if r["label"].startswith("cell")]
    if not measured:
        return {
            "status": "NO_MEASURED_CELLS",
            "modeled_campaign_cpu_hours": None,
            "conservative_campaign_cpu_hours": None,
            "cap_cpu_hours": 1126,
            "cap_verdict": "NOT_ESTABLISHED",
            "note": ("No SR cell has been certified yet. No statement is made in "
                     "either direction about the 1126 CPU-hour cap."),
        }
    mean_cell = sum(measured) / len(measured)
    modeled_h = mean_cell * SR_CELLS / 3600.0
    return {
        "status": "MEASURED",
        "n_cells_measured": len(measured),
        "mean_cell_cpu_seconds": round(mean_cell, 3),
        "modeled_campaign_cpu_hours": round(modeled_h, 3),
        "conservative_campaign_cpu_hours": round(modeled_h * contingency, 3),
        "contingency_factor": contingency,
        "cap_cpu_hours": 1126,
        "cap_verdict": "NOT_ESTABLISHED",
        "note": ("Modeled from measured cells only; the historical Gate-2F "
                 "extrapolation is NOT reused. A cap verdict requires the "
                 "adjudicated full-cover measurement."),
    }


def write_report(cell_records: list, path: Path | None = None) -> Path:
    path = path or (NS / "diagnostics/sr_cost_report.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "schema": "k1.sr.cost.v1",
        "records": cell_records,
        "by_category": by_category(cell_records),
        "formulas": cost_formulas(),
        "projection": campaign_projection(cell_records),
    }, indent=1, sort_keys=True) + "\n")
    return path
