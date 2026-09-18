"""K5-B consumption adapter (authorization prerequisite E6; E6_SPEC.md).

Composition only, no new mathematics:

    CUSUM K1 records --(frozen k5_minimality.load_cells / record_path / rat)--> cells
                     --(frozen k5b_check.k5b_literal, once per m)--> per-m pass sets

Both frozen modules are executed from the exact bytes whose sha256 was checked against the pin. L_1 is the only
order-3 channel (L_k = None for k >= 2). Every problem raises AdapterRefusal; there is no partial result.

    python -B code/consumption_adapter.py consume [--records DIR] [--out RESULT.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import types
from fractions import Fraction
from pathlib import Path

SCHEMA = "rebaseguard.p5y.k5b.consumption-adapter.result.v1"
HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = "level4/closure_proofs/"
LOADER = CP + "p5y_k5_order3_readiness_audit/code/k5_minimality.py"
THEOREM = CP + "p5y_k5b_independent_countersignature/code/k5b_check.py"
PINS = {LOADER: "3a54f0fb290a9b8a07c861653d4399e6c588afdaef77ee51473f778c6c988885",
        THEOREM: "ddd54dc469375a2d64352782add8573231be07b94f7246dad83c4e55a2bf35a6"}
CELLS_JSON = CP + "p5y_k1_cover_ledger_successor/config/cells.json"
CELLS_SHA256 = "341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f"
MANIFEST = CP + "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json"
MANIFEST_SHA256 = "29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334"
HOST_RECORDS_DIR = "/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records"
UNIVERSE = (0, 309)
DETECTOR = "CUSUM"
MS = ("1", "2", "3", "5")
FIELDS = ("R_interval", "D_interval", "R2_interval")


class AdapterRefusal(Exception):
    """Fail closed: no consumption result exists."""


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def load_frozen(path: Path, pin: str, name: str) -> types.ModuleType:
    """Execute exactly the bytes whose sha256 equals the pin."""
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise AdapterRefusal(f"frozen component {name} unreadable: {exc}")
    if sha256_bytes(data) != pin:
        raise AdapterRefusal(f"frozen component {name} does not match its pin")
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    exec(compile(data, str(path), "exec"), mod.__dict__)
    return mod


def frozen_components(repo_root: Path = REPO) -> dict:
    return {"loader": load_frozen(Path(repo_root) / LOADER, PINS[LOADER], "k5_minimality"),
            "theorem": load_frozen(Path(repo_root) / THEOREM, PINS[THEOREM], "k5b_check"),
            "sha256": dict(PINS)}


def check_L1(L1) -> dict:
    if L1 is None:
        return {m: None for m in MS}
    if not isinstance(L1, dict) or set(L1) != set(MS):
        raise AdapterRefusal("L1 must be None or a dict keyed by exactly the m values 1, 2, 3, 5")
    for m, v in L1.items():
        if v is not None and type(v) is not Fraction:
            raise AdapterRefusal(f"L1[{m}] must be an exact Fraction or None")
    return {m: L1[m] for m in MS}


def exact(value, what: str) -> Fraction:
    if not isinstance(value, str):
        raise AdapterRefusal(f"{what} is not an exact rational string")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError):
        raise AdapterRefusal(f"{what} is not an exact rational string")


def bound_file(path: Path, pin: str, what: str) -> bytes:
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise AdapterRefusal(f"{what} unreadable: {exc}")
    if sha256_bytes(data) != pin:
        raise AdapterRefusal(f"{what} does not match its binding")
    return data


def read_records(KM, records_dir: Path, cover: list, manifest: dict) -> tuple[dict, dict]:
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise AdapterRefusal("manifest has no files map")
    root = Path(records_dir).resolve()
    records, hashes = {}, {}
    for c in cover:
        k = c["index"]
        path = KM.record_path(records_dir, DETECTOR, k)
        if path.is_symlink() or not path.is_file() or path.resolve().parent != root:
            raise AdapterRefusal(f"record {k} missing or not a regular file in the records directory")
        data = path.read_bytes()
        want = files.get(f"k4_records/{path.name}")
        if want is None or sha256_bytes(data) != want:
            raise AdapterRefusal(f"record {k} does not match its manifest entry")
        rec = json.loads(data)
        if rec.get("cell_index") != k or rec.get("detector") != DETECTOR:
            raise AdapterRefusal(f"record {k} does not identify itself as {DETECTOR} cell {k}")
        records[k], hashes[str(k)] = rec, want
    return records, hashes


def cells_for_m(KM, cover: list, records: dict, m: str, L1m) -> list[dict]:
    cells = []
    for c in cover:
        k = c["index"]
        r = records[k].get("m", {}).get(m)
        if not isinstance(r, dict):
            raise AdapterRefusal(f"record {k} has no entry for m = {m}")
        x_lo, x_hi, rho, e0 = KM.rat(c["left"]), KM.rat(c["right"]), KM.rat(c["rho"]), KM.rat(c["e0"])
        try:
            same = KM.rat(r["e0"]) == e0 and KM.rat(r["rho"]) == rho      # the loader's own geometry rule
        except (KeyError, TypeError, ValueError, ZeroDivisionError, IndexError):
            same = False
        if not same:
            raise AdapterRefusal(f"record {k} geometry does not match the frozen cover")
        pairs = {}
        for f in FIELDS:
            iv = r.get(f)
            if not isinstance(iv, dict):
                raise AdapterRefusal(f"record {k} m {m} has no {f}")
            pairs[f] = (exact(iv.get("lo"), f"record {k} m {m} {f}.lo"), exact(iv.get("hi"), f"record {k} m {m} {f}.hi"))
        cells.append({"x_lo": x_lo, "x_hi": x_hi, "rho": rho, "e0": e0,
                      "R": pairs["R_interval"], "D": pairs["D_interval"], "H": pairs["R2_interval"],
                      "M": exact(r.get("M_R2"), f"record {k} m {m} M_R2"),
                      "L": L1m if k == cover[0]["index"] else None})
    return cells


def row_json(rows: list[dict]) -> list[dict]:
    return [{key: (str(v) if isinstance(v, Fraction) else v) for key, v in r.items()} for r in rows]


def evaluate(records_dir, cells_json, manifest_path, *, manifest_sha256, cells_sha256, universe=UNIVERSE,
             L1=None, components=None) -> dict:
    comp = components or frozen_components()
    KM, KB = comp["loader"], comp["theorem"]
    L1 = check_L1(L1)
    bound_file(cells_json, cells_sha256, "cells.json")
    manifest = json.loads(bound_file(manifest_path, manifest_sha256, "record manifest"))
    try:
        cover = KM.load_cells(Path(cells_json), DETECTOR)
    except SystemExit as exc:
        raise AdapterRefusal(f"frozen loader refused the cover: {exc}")
    indices = [c["index"] for c in cover]
    if indices != list(range(universe[0], universe[1] + 1)):
        raise AdapterRefusal("the loader universe differs from the bound universe")
    records, hashes = read_records(KM, Path(records_dir), cover, manifest)
    per_m = {}
    for m in MS:
        cells = cells_for_m(KM, cover, records, m, L1[m])
        try:
            rows = KB.k5b_literal(cells)
        except Exception as exc:
            raise AdapterRefusal(f"k5b_literal refused m = {m}: {type(exc).__name__}: {exc}")
        if len(rows) != len(cover):
            raise AdapterRefusal("k5b_literal returned a row count different from the cell count")
        passed = [cover[i]["index"] for i, r in enumerate(rows) if r["pass"] is True]
        opened = [k for k in indices if k not in set(passed)]
        per_m[m] = {"pass": passed, "pass_ranges": KM.ranges(passed), "pass_count": len(passed),
                    "open_ranges": KM.ranges(opened), "open_count": len(opened),
                    "rows_sha256": sha256_bytes(canonical(row_json(rows)))}
    return {"schema": SCHEMA, "detector": DETECTOR, "universe": list(universe), "cell_count": len(cover),
            "m_values": list(MS), "L1": {m: (None if v is None else str(v)) for m, v in L1.items()},
            "L_k_ge_2": None, "per_m": per_m,
            "inputs": {"manifest_sha256": manifest_sha256, "cells_json_sha256": cells_sha256,
                       "records_sha256": sha256_bytes(canonical(hashes)), "record_count": len(hashes)},
            "components": comp["sha256"], "adapter_sha256": sha256_bytes(HERE.read_bytes())}


def consume(L1=None, *, records_dir=HOST_RECORDS_DIR, repo_root=REPO) -> dict:
    """The E6 binding: frozen pins, the pinned cover and manifest, CUSUM cells 0-309."""
    repo_root = Path(repo_root)
    return evaluate(Path(records_dir), repo_root / CELLS_JSON, repo_root / MANIFEST,
                    manifest_sha256=MANIFEST_SHA256, cells_sha256=CELLS_SHA256, universe=UNIVERSE,
                    L1=L1, components=frozen_components(repo_root))


def main() -> int:
    ap = argparse.ArgumentParser(description="K5-B consumption adapter (E6)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("consume")
    c.add_argument("--records", default=HOST_RECORDS_DIR)
    c.add_argument("--out")
    a = ap.parse_args()
    try:
        result = consume(None, records_dir=a.records)
    except AdapterRefusal as exc:
        print(f"ADAPTER_REFUSAL: {exc}", file=sys.stderr)
        return 3
    data = canonical(result)
    if a.out:
        Path(a.out).write_bytes(data + b"\n")
    sys.stdout.write(json.dumps({m: v["pass_ranges"] for m, v in result["per_m"].items()}) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
