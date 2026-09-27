"""Producer of validation/NONTARGET_VALIDATION_INDEX.json (the machine-readable half of the validation report).

For every validation artifact: sha256, size, schema, class, producer; a shallow copy of its summary/verdict/control
fields; and a LEAK SCAN of the artifact's own content: every object carrying a CUSUM cell id in 305..309 or a drift
inside the quarantined band [6/5, 13/5] is listed. A planted negative control (an in-memory artifact with a target
cell and an in-band drift) must be flagged. Also counts ledger runs per producer script.
"""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(NS / "code"))
import ov_quarantine as Q  # noqa: E402

KEYS_SHALLOW = ("summary", "verdict", "verdicts", "checks", "all_sound", "P1_all_pass", "reproduction_gate",
                "coverage", "declared_rule", "declaration", "class", "producer", "negative_controls",
                "negative_control", "crosscheck")
BAND = (F(6, 5), F(13, 5))
TARGET_RANGE = range(305, 310)  # ov-quarantine: literal-ok the leak scanner must name the cells it searches for


def shallow(v, depth=0):
    if depth > 2:
        return "…"
    if isinstance(v, dict):
        return {k: shallow(x, depth + 1) for k, x in list(v.items())[:30]}
    if isinstance(v, list):
        return [shallow(x, depth + 1) for x in v[:12]] + (["…"] if len(v) > 12 else [])
    if isinstance(v, str) and len(v) > 200:
        return v[:200] + "…"
    return v


def as_frac(x):
    try:
        if isinstance(x, bool):
            return None
        if isinstance(x, (int, float)):
            return F(x)
        if isinstance(x, str) and len(x) < 60:
            return F(x)
    except (ValueError, ZeroDivisionError):
        return None
    return None


def leak_scan(obj, path="$", hits=None):
    hits = [] if hits is None else hits
    if isinstance(obj, dict):
        det = str(obj.get("detector", "CUSUM")).upper()
        m = obj.get("m")
        for key in ("cell", "k", "cell_index"):
            c = obj.get(key)
            if isinstance(c, int) and not isinstance(c, bool) and det == "CUSUM" and c in TARGET_RANGE \
                    and (m is None or m == 5):
                hits.append({"path": path, "kind": "TARGET_CELL", "value": c})
        for key in ("e", "e0", "drift", "e_lo", "e_hi", "x_lo", "x_hi"):
            if key in obj:
                v = as_frac(obj[key])
                if v is not None and (BAND[0] <= abs(v) <= BAND[1]):
                    hits.append({"path": path + "." + key, "kind": "DRIFT_IN_BAND", "value": str(obj[key])})
        for k, v in obj.items():
            if isinstance(k, str) and k.strip() in {"305", "306", "307", "308", "309"}:
                hits.append({"path": f"{path}.{k}", "kind": "TARGET_CELL_KEY", "value": k})
            leak_scan(v, f"{path}.{k}", hits)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            leak_scan(v, f"{path}[{i}]", hits)
    return hits


def main() -> None:
    ctrl = leak_scan({"rows": [{"detector": "CUSUM", "m": 5, "cell": 307, "e0": "7/4"}], "cells": {"308": {}}})  # ov-quarantine: literal-ok planted control
    ledger_runs = {}
    for line in Q.LEDGER.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            ledger_runs[r["script"]] = ledger_runs.get(r["script"], 0) + 1
    index = []
    for f in sorted(HERE.glob("*.json")):
        if f.name == "NONTARGET_VALIDATION_INDEX.json":
            continue
        raw = f.read_bytes()
        d = json.loads(raw)
        entry = {"file": f.name, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        if isinstance(d, dict):
            entry["schema"] = d.get("schema")
            entry["fields"] = {k: shallow(d[k]) for k in KEYS_SHALLOW if k in d}
        entry["leak_scan_hits"] = leak_scan(d)
        index.append(entry)
    out = {
        "schema": "OV_NONTARGET_VALIDATION_INDEX/1",
        "artifacts": index,
        "artifacts_count": len(index),
        "leak_scan_negative_control_flagged": sorted({h["kind"] for h in ctrl}) == ["DRIFT_IN_BAND", "TARGET_CELL", "TARGET_CELL_KEY"],
        "artifacts_with_leak_hits": [e["file"] for e in index if e["leak_scan_hits"]],
        "ledger_runs_by_script": ledger_runs,
    }
    (HERE / "NONTARGET_VALIDATION_INDEX.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("artifacts_count", "leak_scan_negative_control_flagged",
                                            "artifacts_with_leak_hits")}, indent=1))
    for e in index:
        if e["leak_scan_hits"]:
            print(e["file"], e["leak_scan_hits"][:3])


if __name__ == "__main__":
    main()
