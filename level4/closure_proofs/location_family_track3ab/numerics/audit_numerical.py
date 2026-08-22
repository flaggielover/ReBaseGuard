#!/usr/bin/env python3
"""Independently reconstruct the frozen Track-3A gate from checkpoints."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]
RESULTS = CAMPAIGN / "results"
BATCHES = 192
MASTER_SEED = 2026082317
H = (0.05, 0.025, 0.0125)
PRIMARY = 2
RELATIVE_LIMIT = 0.03
Z_LIMIT = 3.0
HISTORICAL_ARL = 465.891191


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mean_se(values: list[float]) -> tuple[float, float]:
    data = np.asarray(values, dtype=float)
    return float(data.mean()), float(data.std(ddof=1) / math.sqrt(data.size))


def compare(x: tuple[float, float], y: tuple[float, float]) -> dict:
    mean_abs = (abs(x[0]) + abs(y[0])) / 2.0
    relative = abs(x[0] - y[0]) / mean_abs
    z = abs(x[0] - y[0]) / math.hypot(x[1], y[1])
    return {
        "x": x[0],
        "x_se": x[1],
        "y": y[0],
        "y_se": y[1],
        "relative": relative,
        "absolute_z": z,
        "pass": relative <= RELATIVE_LIMIT and z <= Z_LIMIT,
    }


def load(route: str, replication: int) -> list[dict]:
    directory = RESULTS / "checkpoints" / f"route_{route}_replication_{replication}"
    rows = []
    protocol_hash = json.loads((RESULTS / "protocol_hash.json").read_text())["sha256"]
    expected_paths = 200_000 if route == "a" else 25_000
    route_code = 10 if route == "a" else 20
    for batch in range(BATCHES):
        path = directory / f"batch_{batch:03d}.json"
        row = json.loads(path.read_text())
        assert row["route"] == route.upper()
        assert row["replication"] == replication
        assert row["batch"] == batch
        assert row["seed_key"] == [MASTER_SEED, route_code, replication, batch]
        assert row["paths"] == expected_paths
        assert row["protocol_sha256"] == protocol_hash
        rows.append(row)
    return rows


def main() -> None:
    protocol = json.loads((RESULTS / "protocol_hash.json").read_text())
    assert sha256(CAMPAIGN / "PROTOCOL.md") == protocol["sha256"]
    sources = json.loads((RESULTS / "source_manifest.json").read_text())
    assert all(sha256(REPO / relative) == expected for relative, expected in sources["sha256"].items())
    historical = json.loads((RESULTS / "historical_manifest.json").read_text())
    assert all(sha256(REPO / relative) == expected for relative, expected in historical["sha256"].items())

    a_rows = [load("a", replication) for replication in (1, 2)]
    b_rows = [load("b", replication) for replication in (1, 2)]
    route_a = [mean_se([1.0 - row["gamma_f"] for row in rows]) for rows in a_rows]
    route_b = [mean_se([row["paired_derivatives"][PRIMARY] for row in rows]) for rows in b_rows]

    max_map_error = 0.0
    for rows in b_rows:
        for row in rows:
            for index, h in enumerate(H):
                maps = row["maps"]
                reconstructed = (maps[2 * index + 1] - maps[2 * index]) / (2.0 * h)
                max_map_error = max(max_map_error, abs(reconstructed - row["paired_derivatives"][index]))

    rep_correspondence = [compare(route_a[index], route_b[index]) for index in range(2)]
    a_replication = compare(route_a[0], route_a[1])
    b_replication = compare(route_b[0], route_b[1])
    pooled_a = mean_se([1.0 - row["gamma_f"] for rows in a_rows for row in rows])
    pooled_b = mean_se([row["paired_derivatives"][PRIMARY] for rows in b_rows for row in rows])
    pooled = compare(pooled_a, pooled_b)
    arls = [float(np.mean([row["arl"] for row in rows])) for rows in a_rows]
    arl_pass = all(abs(arl - HISTORICAL_ARL) / HISTORICAL_ARL <= 0.02 for arl in arls)
    zero_ties = all(
        row["ties"] == 0 and row["simultaneous_crossings"] == 0
        for route_rows in (a_rows, b_rows)
        for rows in route_rows
        for row in rows
    )

    all_primary = (
        all(cell["pass"] for cell in rep_correspondence)
        and a_replication["pass"]
        and b_replication["pass"]
        and pooled["pass"]
        and arl_pass
        and zero_ties
        and max_map_error <= 2e-12
    )
    audit = {
        "schema": "rebaseguard.location-family-track3ab.numerical-audit.v1",
        "checkpoint_count": 4 * BATCHES,
        "route_a": [{"mean": x[0], "se": x[1]} for x in route_a],
        "route_b": [{"mean": x[0], "se": x[1]} for x in route_b],
        "per_replication_correspondence": rep_correspondence,
        "route_a_replication": a_replication,
        "route_b_replication": b_replication,
        "pooled": pooled,
        "arls": arls,
        "arl_pass": arl_pass,
        "zero_ties": zero_ties,
        "max_map_identity_error": max_map_error,
        "all_primary_pass": all_primary,
        "status": "T3A-NUMERICAL-PASS" if all_primary else "AUDIT-FAIL",
    }
    decision = json.loads((RESULTS / "numerical_decision.json").read_text())
    assert audit["status"] == decision["status"] == "T3A-NUMERICAL-PASS"
    assert decision["lean_authorized"] is True
    (RESULTS / "numerical_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print("independent checkpoint audit: T3A-NUMERICAL-PASS")


if __name__ == "__main__":
    main()
