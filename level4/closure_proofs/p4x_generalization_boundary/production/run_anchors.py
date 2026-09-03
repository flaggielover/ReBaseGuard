#!/usr/bin/env python3
"""P4X production PHASE P0 -- frozen anchor reproduction.

Before any production path is drawn, re-run the FROZEN Priority-4 estimators
with the FROZEN seeds, batch counts and path counts, and compare against the
values recorded in the frozen correspondence artifact.

A match validates, in one stroke: the Route-A score estimator, the Route-B CRN
central difference, the Richardson h = 0.05/0.025 semantics, the Philox RNG
addressing, the detector parameters, the window and random-denominator
semantics, the inclusion of the alarm-causing increment, and the family
parameterisation.

Any mismatch is classified and production STOPS.
"""

from __future__ import annotations

import hashlib
import json
import resource
import sys
import time
from pathlib import Path

PROD = Path(__file__).resolve().parent
BOUNDARY = PROD.parent
CLOSURE = BOUNDARY.parent
P4 = CLOSURE / "p4_theory_generalization"
sys.path.insert(0, str(P4 / "src"))
sys.path.insert(0, str(P4 / "numerics"))

from rebaseguard_p4_general.detectors import Detector  # noqa: E402
from rebaseguard_p4_general.families import REGISTRY  # noqa: E402
from rebaseguard_p4_general.estimators import route_a, route_b  # noqa: E402
from rebaseguard_p4_general.quadrature import *  # noqa: E402,F401,F403

#: relative tolerance for a reproduced anchor.  Bitwise equality is the
#: expectation; this allows only last-place floating-point drift from a
#: different numpy build, and anything larger is classified as drift.
ANCHOR_RTOL = 1e-12

#: Anchor set: cheap, plus the load-bearing frozen SR/Gaussian cell that the
#: Gaussian-consistency obligation depends on, plus the heavy-tail family.
ANCHORS = (
    ("reduced", "cusum", 2.0, "gaussian"),
    ("frozen", "cusum", 5.0, "t1p5"),
    ("frozen", "sr", 520.886133602749, "gaussian"),
)


def name_offset(name: str) -> int:
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % 9973


def cpu() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def classify(field: str, expected: float, got: float) -> str:
    """Classify an anchor mismatch per the production charter."""
    if expected == 0:
        return "A6_OTHER"
    rel = abs(got - expected) / abs(expected)
    if rel < 1e-9:
        return "A6_OTHER"          # sub-ulp; not a real mismatch
    # a systematically different stream reproduces the right magnitude with a
    # different realisation; a convention error moves the estimand itself
    return "A2_RNG_DRIFT" if rel < 0.5 else "A4_CONVENTION_DRIFT"


def main() -> None:
    protocol = json.loads((P4 / "configs" / "P4_PROTOCOL.json").read_text())
    corr = json.loads((P4 / "results" / "correspondence.json").read_text())
    cells = corr["monte_carlo"]["cells"]
    m_grid = tuple(protocol["m_grid"])
    seeds = protocol["master_seeds"]

    rows = []
    mismatches = []
    c0, w0 = cpu(), time.perf_counter()

    for layer_name, kind, threshold, family_name in ANCHORS:
        layer = protocol["layers"][layer_name]
        detector = Detector(kind, threshold)
        family = REGISTRY[family_name]
        label = f"{layer_name}/{detector.label}/{family_name}"
        off = name_offset(family_name)

        t0, cc0 = time.perf_counter(), cpu()
        a = route_a(
            family=family, detector=detector, m_grid=m_grid,
            batches=layer["route_a"]["batches"], paths=layer["route_a"]["paths"],
            seed=seeds[f"route_a_{layer_name}"] + off,
            max_steps=layer["max_steps"],
        )
        b = route_b(
            family=family, detector=detector, m_grid=m_grid,
            batches=layer["route_b"]["batches"], paths=layer["route_b"]["paths"],
            seed=seeds[f"route_b_{layer_name}"] + off,
            fd_steps=tuple(protocol["fd_steps"]),
            max_steps=layer["max_steps"],
        )
        elapsed, used = time.perf_counter() - t0, cpu() - cc0

        for m in m_grid:
            hist = next(c for c in cells
                        if (c["layer"], c["detector"], c["family"], c["m"])
                        == (layer_name, detector.label, family_name, m))
            for route, produced in (("route_a", a), ("route_b", b)):
                got = produced["by_m"][str(m)]["gamma"]
                exp = hist[route]
                for field in ("mean", "se"):
                    e, g = exp[field], got[field]
                    ok = abs(g - e) <= ANCHOR_RTOL * abs(e)
                    row = {
                        "config": label, "m": m, "route": route, "field": field,
                        "historical": e, "reproduced": g,
                        "relative_difference": (abs(g - e) / abs(e)) if e else None,
                        "match": bool(ok),
                    }
                    if not ok:
                        row["classification"] = classify(field, e, g)
                        mismatches.append(row)
                    rows.append(row)
                assert exp["paths"] == got["paths"], (label, m, route)

        print(f"{label:34s} reproduced in {elapsed:7.1f}s wall / {used:7.1f}s cpu "
              f"({'ALL MATCH' if not mismatches else str(len(mismatches)) + ' MISMATCH'})")

    # Route Q: deterministic quadrature, no sampling error at all.
    rq = corr["route_q"]
    route_q_anchor = {
        "recorded_all_pass": rq["all_pass"],
        "recorded_rows": len(rq["rows"]),
        "recorded_uniform_identity_holds": rq["uniform_counterexample"]["identity_holds"],
        "recorded_worst_relative": max(
            abs(r.get("relative_discrepancy", 0.0)) for r in rq["rows"]),
    }
    route_n_anchor = {
        "recorded_all_pass": corr["route_n"]["all_pass"],
        "recorded_rows": len(corr["route_n"]["rows"]),
    }

    total_cpu, total_wall = cpu() - c0, time.perf_counter() - w0
    payload = {
        "schema": "rebaseguard.p4x-production-anchors.v1",
        "phase": "P0_ANCHOR_REPRODUCTION",
        "checkpoint_commit": "756bf687cfe8e7d08f3fadea3daac504ea0330ac",
        "anchor_rtol": ANCHOR_RTOL,
        "anchors_attempted": [f"{l}/{Detector(k, t).label}/{f}"
                              for l, k, t, f in ANCHORS],
        "comparisons": len(rows),
        "mismatches": mismatches,
        "all_anchors_reproduced": not mismatches,
        "route_q_recorded": route_q_anchor,
        "route_n_recorded": route_n_anchor,
        "semantics_validated_by_exact_reproduction": [
            "Route-A frozen score estimator",
            "Route-B frozen CRN central difference",
            "Richardson per-block combination at h = 0.05 / 0.025",
            "Philox RNG addressing (seed, batch, step) with 2^64 stream stride",
            "detector parameters k=1/2, h=5, A=520.886133602749",
            "window semantics w = min(m, tau) with random denominator",
            "inclusion of the alarm-causing increment",
            "family parameterisation and per-family seed offset",
        ],
        "rows": rows,
        "cpu_seconds": total_cpu,
        "wall_seconds": total_wall,
        "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1 << 20),
    }
    out = PROD / "results" / "anchors.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")

    print(f"\ncomparisons {len(rows)}   mismatches {len(mismatches)}")
    print(f"CPU {total_cpu:.1f}s   wall {total_wall:.1f}s")
    print(f"ALL_ANCHORS_REPRODUCED = {not mismatches}")
    print(f"-> {out}")
    if mismatches:
        print("\nSTOP: load-bearing anchor(s) not reproduced")
        for m in mismatches[:10]:
            print("  ", json.dumps(m))
        sys.exit(2)


if __name__ == "__main__":
    main()
