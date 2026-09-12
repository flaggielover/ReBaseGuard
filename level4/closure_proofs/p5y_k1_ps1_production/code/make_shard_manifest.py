"""Deterministic PS1 shard manifest: every successor cell of the frozen PS1 table exactly once. Topology A (AWS only):
AWS owns all 369 cells; the VULTR role is present (the frozen shard gate requires both roles) and owns none. Cell
groups (the production unit of one pool worker) are consecutive successor indices in blocks of 4; the terminal cell
forms its own group. Groups only order and batch the work; each cell is admitted, accounted, verified and sealed
individually."""
import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
TABLE = NS.parent / "p5y_k1_sr_o9_partition_successor/config/successor_cells.json"
GROUP = 4


def build():
    t = json.loads(TABLE.read_text())
    ids = [c["index"] for c in t["cells"]]
    assert ids == list(range(t["n_cells"])) and t["n_cells"] == 369
    body = ids[:-1]
    groups = [body[i:i + GROUP] for i in range(0, len(body), GROUP)] + [[ids[-1]]]
    flat = [c for g in groups for c in g]
    assert flat == ids
    return {"schema": "rebaseguard.p5y.k1.ps1.shard-manifest.v1", "cells_total": len(ids), "topology": "A_AWS_ONLY",
            "AWS": {"cells": ids}, "VULTR": {"cells": []}, "groups": groups, "group_size": GROUP,
            "successor_cells_sha256": hashlib.sha256(TABLE.read_bytes()).hexdigest()}


if __name__ == "__main__":
    m = build()
    b = (json.dumps(m, indent=1, sort_keys=True) + "\n").encode()
    (NS / "config/SHARD_MANIFEST.json").write_bytes(b)
    print("groups", len(m["groups"]), "sha256", hashlib.sha256(b).hexdigest())
