"""Deterministic replay: fresh-process re-execution compared leaf-by-leaf under the FROZEN aux4 classifier.

  patches : re-run a deterministic subset of T3 patch records in a fresh process and compare every leaf
  pipeline: re-run T3 aggregation, T4 and T5 from the same inputs and compare the complete records
Only INCIDENTAL_RUNTIME leaves (frozen whitelist) may move.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

CP = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("aux4_schema", CP / "p5y_k1_cusum_aux4_fullcover/code/schema.py")
schema = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(schema)


def diff(a, b):
    la, lb = dict(schema.walk(a)), dict(schema.walk(b))
    moved = [p for p in sorted(set(la) | set(lb)) if la.get(p, "<absent>") != lb.get(p, "<absent>")]
    by = {schema.SCIENTIFIC: [], schema.PROVENANCE: [], schema.INCIDENTAL: []}
    for p in moved:
        by[schema.classify(p)].append(p)
    return {"leaves": len(set(la) | set(lb)), "moved": len(moved),
            "moved_by_class": {k: len(v) for k, v in by.items()},
            "moved_non_incidental": by[schema.SCIENTIFIC] + by[schema.PROVENANCE], "moved_incidental": by[schema.INCIDENTAL]}


def patches(original_glob, replay_file, cell):
    orig = {}
    import glob
    for f in glob.glob(original_glob):
        for line in Path(f).read_text().splitlines():
            r = json.loads(line)
            if r["cell"] == cell:
                orig[tuple(r["patch"])] = r
    rows = []
    for line in Path(replay_file).read_text().splitlines():
        r = json.loads(line)
        d = diff(orig[tuple(r["patch"])], r)
        rows.append({"patch": r["patch"], **d})
    return rows


def files(pairs):
    rows = []
    for a, b in pairs:
        A, B = json.loads(Path(a).read_text()), json.loads(Path(b).read_text())
        d = diff(A, B)
        rows.append({"a": Path(a).name, "b": Path(b).name, "bytes_equal": Path(a).read_bytes() == Path(b).read_bytes(),
                     "sha_a": hashlib.sha256(Path(a).read_bytes()).hexdigest(), **d})
    return rows


def main():
    mode, out = sys.argv[1], sys.argv[2]
    if mode == "patches":
        rows = patches(sys.argv[3], sys.argv[4], int(sys.argv[5]))
    else:
        rows = files([x.split("=") for x in sys.argv[3:]])
    res = {"mode": mode, "schema_sha256": hashlib.sha256((CP / "p5y_k1_cusum_aux4_fullcover/code/schema.py").read_bytes()).hexdigest(),
           "rows": rows, "total_moved_scientific": sum(r["moved_by_class"][schema.SCIENTIFIC] + r["moved_by_class"][schema.PROVENANCE] for r in rows),
           "total_moved_incidental": sum(r["moved_by_class"][schema.INCIDENTAL] for r in rows)}
    res["ZERO_SCIENTIFIC_LEAVES_MOVED"] = res["total_moved_scientific"] == 0
    Path(out).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: res[k] for k in ("mode", "total_moved_scientific", "total_moved_incidental", "ZERO_SCIENTIFIC_LEAVES_MOVED")}
                     | {"rows": [(r.get("patch") or r["b"], r["leaves"], r["moved"], r["moved_incidental"][:4]) for r in rows]}, indent=1))


if __name__ == "__main__":
    main()
