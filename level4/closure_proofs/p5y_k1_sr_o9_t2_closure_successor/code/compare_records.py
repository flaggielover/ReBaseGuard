"""Leaf-by-leaf comparison of complete records under the FROZEN aux4 field classification
(p5y_k1_cusum_aux4_fullcover/code/schema.py: INCIDENTAL_PATHS whitelist, unknown = SCIENTIFIC)."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

CP = Path(__file__).resolve().parents[2]
SCHEMA_PATH = CP / "p5y_k1_cusum_aux4_fullcover/code/schema.py"
_spec = importlib.util.spec_from_file_location("aux4_schema", SCHEMA_PATH)
schema = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(schema)


def compare(a: dict, b: dict) -> dict:
    la, lb = dict(schema.walk(a)), dict(schema.walk(b))
    paths = sorted(set(la) | set(lb))
    moved = [p for p in paths if la.get(p, "<absent>") != lb.get(p, "<absent>")]
    cls = {schema.SCIENTIFIC: 0, schema.PROVENANCE: 0, schema.INCIDENTAL: 0}
    for p in moved:
        cls[schema.classify(p)] += 1
    counts = {schema.SCIENTIFIC: 0, schema.PROVENANCE: 0, schema.INCIDENTAL: 0}
    for p in paths:
        counts[schema.classify(p)] += 1
    return {"leaves": len(paths), "leaf_classes": counts, "moved": len(moved), "moved_by_class": cls,
            "moved_non_incidental": [p for p in moved if schema.classify(p) != schema.INCIDENTAL],
            "moved_incidental": [p for p in moved if schema.classify(p) == schema.INCIDENTAL]}


def main():
    mode, out = sys.argv[1], sys.argv[2]
    pairs = [x.split("=") for x in sys.argv[3:]]
    res = {"schema_file": str(SCHEMA_PATH.relative_to(CP)),
           "schema_sha256": hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest(), "mode": mode, "pairs": []}
    for pa, pb in pairs:
        a, b = json.loads(Path(pa).read_text()), json.loads(Path(pb).read_text())
        c = compare(a, b)
        c.update({"a": str(Path(pa).relative_to(CP)), "b": str(Path(pb).relative_to(CP)),
                  "scientific_hash_equal": a["scientific_hash"] == b["scientific_hash"],
                  "scientific_bytes_equal": json.dumps(a["scientific"], sort_keys=True) == json.dumps(b["scientific"], sort_keys=True)})
        res["pairs"].append(c)
    res["zero_scientific_leaves_moved"] = all(p["moved_by_class"][schema.SCIENTIFIC] == 0
                                              and p["moved_by_class"][schema.PROVENANCE] == 0 for p in res["pairs"])
    res["all_scientific_identical"] = all(p["scientific_bytes_equal"] and p["scientific_hash_equal"] for p in res["pairs"])
    Path(out).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"mode": mode, "pairs": len(res["pairs"]), "zero_scientific_leaves_moved": res["zero_scientific_leaves_moved"],
                      "all_scientific_identical": res["all_scientific_identical"],
                      "per_pair": [(p["b"].split("/")[-1], p["leaves"], p["moved"], p["moved_by_class"]) for p in res["pairs"]]}, indent=1))


if __name__ == "__main__":
    main()
