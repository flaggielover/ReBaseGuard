#!/usr/bin/env python3
"""Run the frozen Priority-4 cross-family correspondence campaign.

Four routes are evaluated and kept apart:

* **Route Q** -- deterministic quadrature for the memoryless detector.  No
  sampling error; tests the mathematics, not the frozen operating point.
* **Route N** -- the deterministic-stopping neutrality control.  The gain must
  be exactly one for every family, which exercises the score, the window and
  the random denominator with a known answer.
* **Route A** -- the score formula under the frozen CUSUM and SR recursions.
* **Route B** -- a common-random-number finite difference of the actual
  conditional-mean map, using no likelihood at all.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
ROOT = CAMPAIGN.parents[2]
sys.path.insert(0, str(CAMPAIGN / "src"))

from rebaseguard_p4_general import quadrature as routeq  # noqa: E402
from rebaseguard_p4_general.detectors import Detector  # noqa: E402
from rebaseguard_p4_general.estimators import (  # noqa: E402
    correspondence, route_a, route_b,
)
from rebaseguard_p4_general.families import REGISTRY  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def name_offset(name: str) -> int:
    """Deterministic per-family seed offset.

    ``hash()`` on a string is randomised per interpreter run, so it must never
    appear in a reproducible seed."""
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % 9973


def run_route_q(protocol: dict) -> dict:
    cfg = protocol["route_q"]
    m_grid = tuple(protocol["m_grid"])
    rows = []
    for name in cfg["families"]:
        family = REGISTRY[name]
        for m in m_grid:
            gain, moments = routeq.gain(family, cfg["c"], m)
            derivative = routeq.map_derivative(family, cfg["c"], m)
            scale = max(abs(gain), 1e-12)
            rows.append({
                "family": name, "m": m,
                "gamma_score_route": gain,
                "negative_map_derivative": -derivative,
                "relative_discrepancy": abs(gain + derivative) / scale,
                "alarm_probability": moments.p,
                "quadrature_error_bound": moments.quad_error,
                "pass": abs(gain + derivative) / scale <= cfg["tolerance_relative"],
            })
    # exact uniform counterexample: g_1(e) = -e * a/(a-c) on |e| < a-c
    a = 3.0 ** 0.5
    c = cfg["c_uniform"]
    uniform_exact = {
        "family": "uniform", "m": 1, "c": c,
        "gamma_score_route": 0.0,
        "negative_map_derivative_exact": a / (a - c),
        "negative_map_derivative_quadrature": -routeq.map_derivative(
            REGISTRY["uniform"], c, 1, tail=2.5
        ),
        "identity_holds": False,
        "reason": "the a.e. interior score of a flat density is zero, but the "
                  "support moves with e, so no local absolute continuity holds",
    }
    return {
        "detector": cfg["detector"], "c": cfg["c"], "rows": rows,
        "all_pass": all(row["pass"] for row in rows),
        "uniform_counterexample": uniform_exact,
        "laplace_closed_form": routeq.laplace_closed_form(2.0 ** -0.5, cfg["c"]),
    }


def run_route_n(protocol: dict) -> dict:
    cfg = protocol["neutrality_control"]
    m_grid = tuple(protocol["m_grid"])
    seed = protocol["master_seeds"]["neutrality"]
    rows = []
    for name, meta in protocol["families"].items():
        if meta["class"] != "THEOREM-SUPPORTED":
            continue
        for horizon in cfg["deterministic_tau"]:
            result = route_a(
                family=REGISTRY[name], detector=Detector("deterministic", horizon),
                m_grid=m_grid, batches=cfg["batches"], paths=cfg["paths"],
                seed=seed + horizon, max_steps=horizon + 2,
            )
            for m in m_grid:
                gamma = result["by_m"][str(m)]["gamma"]
                z = abs(gamma["mean"] - 1.0) / gamma["se"] if gamma["se"] > 0 else 0.0
                rows.append({
                    "family": name, "deterministic_tau": horizon, "m": m,
                    "gamma": gamma["mean"], "se": gamma["se"], "z_against_one": z,
                    "pass": z <= cfg["tolerance_z"],
                })
    return {"rows": rows, "all_pass": all(row["pass"] for row in rows)}


def run_monte_carlo(protocol: dict) -> dict:
    m_grid = tuple(protocol["m_grid"])
    gates = protocol["gates"]
    seeds = protocol["master_seeds"]
    cells = []
    for layer_name, layer in protocol["layers"].items():
        for kind, threshold in layer["detectors"]:
            detector = Detector(kind, threshold)
            for family_name in layer["families"]:
                family = REGISTRY[family_name]
                started = time.time()
                a = route_a(
                    family=family, detector=detector, m_grid=m_grid,
                    batches=layer["route_a"]["batches"],
                    paths=layer["route_a"]["paths"],
                    seed=seeds[f"route_a_{layer_name}"] + name_offset(family_name),
                    max_steps=layer["max_steps"],
                )
                b = route_b(
                    family=family, detector=detector, m_grid=m_grid,
                    batches=layer["route_b"]["batches"],
                    paths=layer["route_b"]["paths"],
                    seed=seeds[f"route_b_{layer_name}"] + name_offset(family_name),
                    fd_steps=tuple(protocol["fd_steps"]),
                    max_steps=layer["max_steps"],
                )
                klass = protocol["families"][family_name]["class"]
                for m in m_grid:
                    ga = a["by_m"][str(m)]["gamma"]
                    gb = b["by_m"][str(m)]["gamma"]
                    corr = correspondence(ga, gb)
                    if klass == "THEOREM-SUPPORTED":
                        verdict = (
                            "PASS"
                            if corr["relative_discrepancy"] <= gates[
                                "correspondence_relative_limit"]
                            and corr["z"] <= gates["correspondence_z_limit"]
                            else "FAIL"
                        )
                    else:
                        verdict = (
                            "COUNTEREXAMPLE-CONFIRMED"
                            if corr["relative_discrepancy"] >= gates[
                                "counterexample_min_relative"]
                            and corr["z"] >= gates["counterexample_min_z"]
                            else "COUNTEREXAMPLE-NOT-DEMONSTRATED"
                        )
                    cells.append({
                        "layer": layer_name, "detector": detector.label,
                        "detector_kind": kind, "threshold": threshold,
                        "family": family_name, "family_class": klass, "m": m,
                        "arl": a["arl"], "unstopped_paths": a["unstopped_paths"],
                        "route_a": ga, "route_b": gb,
                        "mean_window_at_zero": a["by_m"][str(m)]["mean_window"],
                        "fixed_denominator_gain": a["by_m"][str(m)]["fixed_gain"],
                        "short_correction": a["by_m"][str(m)]["short_correction"],
                        "gaussian_form_gain": a["by_m"][str(m)]["gaussian_gain"],
                        "correspondence": corr, "verdict": verdict,
                    })
                print(f"  {layer_name:8s} {detector.label:14s} {family_name:12s} "
                      f"ARL={a['arl']['mean']:8.2f} "
                      f"[{time.time() - started:5.1f}s]", flush=True)
    return {"cells": cells}


def run_fd_ladder(protocol: dict) -> dict:
    """Independent step-size diagnostic on the pre-named cells.

    Route B already reports its two constituent steps.  This adds a third,
    finer step on two named cells so that the assumed ``O(h^2)`` law behind the
    Richardson combination is tested rather than assumed.
    """
    m_grid = tuple(protocol["m_grid"])
    rows = []
    for layer_name, kind, threshold, family_name in protocol["fd_ladder_cells"]:
        layer = protocol["layers"][layer_name]
        result = route_b(
            family=REGISTRY[family_name], detector=Detector(kind, threshold),
            m_grid=m_grid, batches=layer["route_b"]["batches"],
            paths=layer["route_b"]["paths"],
            seed=protocol["master_seeds"]["fd_ladder"],
            fd_steps=tuple(protocol["fd_ladder_fine"]),
            max_steps=layer["max_steps"],
        )
        for m in m_grid:
            rows.append({
                "layer": layer_name, "detector": Detector(kind, threshold).label,
                "family": family_name, "m": m,
                "fd_steps": protocol["fd_ladder_fine"],
                "richardson": result["by_m"][str(m)]["gamma"],
                "per_step": result["by_m"][str(m)]["per_step"],
            })
    return {"rows": rows}


def main() -> None:
    # an alternate protocol path is accepted so that the focused test suite can
    # exercise every code path on a tiny grid without touching the frozen one
    protocol_path = (
        Path(sys.argv[1]) if len(sys.argv) > 1
        else CAMPAIGN / "configs" / "P4_PROTOCOL.json"
    )
    protocol = json.loads(protocol_path.read_text())
    started = time.time()

    print("== Route Q: deterministic quadrature reference ==", flush=True)
    q = run_route_q(protocol)
    print(f"   all_pass={q['all_pass']}", flush=True)

    print("== Route N: deterministic-stopping neutrality control ==", flush=True)
    n = run_route_n(protocol)
    print(f"   all_pass={n['all_pass']}", flush=True)

    print("== Routes A and B: frozen detector recursions ==", flush=True)
    mc = run_monte_carlo(protocol)

    print("== finite-difference ladder ==", flush=True)
    ladder = run_fd_ladder(protocol)

    payload = {
        "schema": "rebaseguard.p4-correspondence.v1",
        "protocol_sha256": sha256(protocol_path),
        "elapsed_seconds": time.time() - started,
        "route_q": q,
        "route_n": n,
        "monte_carlo": mc,
        "fd_ladder": ladder,
    }
    out = Path(sys.argv[2]) if len(sys.argv) > 2 \
        else CAMPAIGN / "results" / "correspondence.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {out} in {payload['elapsed_seconds']:.1f}s")


if __name__ == "__main__":
    main()
