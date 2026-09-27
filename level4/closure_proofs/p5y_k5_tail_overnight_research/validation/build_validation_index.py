"""Producer of validation/NONTARGET_VALIDATION_INDEX.json (the machine-readable half of the validation report).

For every validation artifact: sha256, size, schema, class, producer; a shallow copy of its summary/verdict/control
fields; and a LEAK SCAN of the artifact's own content: every object carrying a CUSUM cell id in 305..309 or a drift
inside the quarantined band [6/5, 13/5] is listed. A planted negative control (an in-memory artifact with a target
cell and an in-band drift) must be flagged. Also counts ledger runs per producer script.
"""
from __future__ import annotations

import hashlib
import json
import re
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


CELL_KEYS = {"cell", "cells", "k", "cell_index", "index", "cell_id", "cell_ids"}
DRIFT_KEYS = {"e", "e0", "drift", "drifts", "e_lo", "e_hi", "x_lo", "x_hi", "x0", "left", "right", "block", "blocks",
              "e_block", "e_range", "interval", "e_interval", "drift_block"}
TARGET_STR = {"305", "306", "307", "308", "309"}  # ov-quarantine: literal-ok the leak scanner must name the cells it searches for
_CELL_TXT = re.compile(r"\bcell[s]?\s*[:=#]?\s*(30[5-9])\b", re.I)
_E_TXT = re.compile(r"\be(?:0|_lo|_hi)?\s*[=:]\s*(-?\d+(?:\.\d+)?(?:/\d+)?)")


def _num_in_band(x) -> bool:
    v = as_frac(x)
    return v is not None and BAND[0] <= abs(v) <= BAND[1]


def _flat(v):
    if isinstance(v, list):
        for x in v:
            yield from _flat(x)
    else:
        yield v


def leak_scan(obj, path="$", hits=None, parent_detector="CUSUM"):
    hits = [] if hits is None else hits
    if isinstance(obj, dict):
        det = str(obj.get("detector", parent_detector)).upper()
        m = obj.get("m")
        for k, v in obj.items():
            kl = k.lower() if isinstance(k, str) else k
            if isinstance(k, str) and k.strip() in TARGET_STR:
                hits.append({"path": f"{path}.{k}", "kind": "TARGET_CELL_KEY", "value": k})
            if kl in CELL_KEYS and det == "CUSUM" and (m is None or m == 5):
                for x in _flat(v):
                    if isinstance(x, int) and not isinstance(x, bool) and x in TARGET_RANGE:
                        hits.append({"path": f"{path}.{k}", "kind": "TARGET_CELL", "value": x})
                    elif isinstance(x, str) and x.strip() in TARGET_STR:
                        hits.append({"path": f"{path}.{k}", "kind": "TARGET_CELL", "value": x})
            if kl in DRIFT_KEYS and not (kl in ("block", "blocks") and isinstance(v, int)):  # an int count, not a drift
                for x in _flat(v):
                    if _num_in_band(x):
                        hits.append({"path": f"{path}.{k}", "kind": "DRIFT_IN_BAND", "value": str(x)})
            leak_scan(v, f"{path}.{k}", hits, det)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            leak_scan(v, f"{path}[{i}]", hits, parent_detector)
    elif isinstance(obj, str):
        mc = _CELL_TXT.search(obj)
        if mc:
            hits.append({"path": path, "kind": "TARGET_CELL_TEXT", "value": obj[:80]})
        for me in _E_TXT.finditer(obj):
            if _num_in_band(me.group(1)):
                hits.append({"path": path, "kind": "DRIFT_IN_BAND_TEXT", "value": obj[:80]})
    return hits


CONTROL_SHAPES = {  # each planted shape must be flagged on its own (review F4)
    "int_cell": {"detector": "CUSUM", "m": 5, "cell": 307},
    "list_cells": {"cells": [306, 12]},
    "str_key": {"cells": {"308": {}}},
    "text_cell": {"note": "evaluated at cell 309"},
    "frac_drift": {"e0": "7/4"},
    "float_drift": {"e": 1.9},
    "list_drifts": {"drifts": [0.5, "9/5"]},
    "block": {"block": ["17/10", "9/5"]},
    "index_key": {"index": 306, "detector": "CUSUM"},
    "text_drift": {"note": "certified at e = 1.85"},
    "x0": {"x0": "37/20"},
}


def main() -> None:
    ctrl_by_shape = {name: bool(leak_scan(obj)) for name, obj in CONTROL_SHAPES.items()}
    benign = leak_scan({"cells": [11, 44], "e0": "1/2", "drifts": [0, 3], "note": "cell 12 at e = 1/4"})
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
        "leak_scan_controls_by_shape": ctrl_by_shape,
        "leak_scan_negative_control_flagged": all(ctrl_by_shape.values()),
        "leak_scan_benign_false_positives": benign,
        "artifacts_with_leak_hits": [e["file"] for e in index if e["leak_scan_hits"]],
        "ledger_runs_by_script": ledger_runs,
    }
    (HERE / "NONTARGET_VALIDATION_INDEX.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("artifacts_count", "leak_scan_negative_control_flagged",
                                            "leak_scan_controls_by_shape", "leak_scan_benign_false_positives",
                                            "artifacts_with_leak_hits")}, indent=1))
    for e in index:
        if e["leak_scan_hits"]:
            print(e["file"], e["leak_scan_hits"][:3])


if __name__ == "__main__":
    main()
