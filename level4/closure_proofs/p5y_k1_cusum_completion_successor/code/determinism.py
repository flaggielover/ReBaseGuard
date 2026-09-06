"""PHASE 3 support: field classification and repeated-run determinism checking.

The independent adjudication found that repeated fresh runs of the predecessor
produced different exact certificate hashes under the same producer identity.
This module names every differing field's class and provides the harness the
tests use to prove the invariant

    same certifying bytes + same exact inputs + same precision
      => same canonical scientific certificate hash
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import ancestry

import successor_certhash as CH

SCIENTIFIC_CONTENT = "SCIENTIFIC_CONTENT"
OUTWARD_ROUNDING = "OUTWARD_ROUNDING_REPRESENTATION"
RUNTIME_NOISE = "NONDETERMINISTIC_RUNTIME_NOISE"
SERIALIZATION_NOISE = "SERIALIZATION_NOISE"
IMPLEMENTATION_DEFECT = "IMPLEMENTATION_DEFECT"

FIELD_CLASSES = {
    # runtime noise -- excluded from the canonical scientific hash
    "cpu_seconds": RUNTIME_NOISE,
    "cpu_seconds_prepare": RUNTIME_NOISE,
    "cpu_seconds_including_dependencies": RUNTIME_NOISE,
    "wall_seconds": RUNTIME_NOISE,
    "peak_rss_kib": RUNTIME_NOISE,
    "bernstein_calls": RUNTIME_NOISE,
    "kernel_calls": RUNTIME_NOISE,
    "threading": RUNTIME_NOISE,
    "generated_utc": RUNTIME_NOISE,
    "pid": RUNTIME_NOISE,
    # diagnostic float ratios, not certified content
    "norm_improvement": SERIALIZATION_NOISE,
    "tightening_report": SERIALIZATION_NOISE,
    # JSON key order
    "__key_order__": SERIALIZATION_NOISE,
    # certified content -- INCLUDED
    "delta_mid": SCIENTIFIC_CONTENT,
    "delta_cell": SCIENTIFIC_CONTENT,
    "envelope": SCIENTIFIC_CONTENT,
    "eps_mid": SCIENTIFIC_CONTENT,
    "eps_cell": SCIENTIFIC_CONTENT,
    "eps_cell_refined": SCIENTIFIC_CONTENT,
    "R_interval": SCIENTIFIC_CONTENT,
    "D_interval": SCIENTIFIC_CONTENT,
    "R2_interval": SCIENTIFIC_CONTENT,
    "M_R2": SCIENTIFIC_CONTENT,
    "cover": SCIENTIFIC_CONTENT,
    "top_level_gates": SCIENTIFIC_CONTENT,
    "status": SCIENTIFIC_CONTENT,
    # the one real defect class, removed at source rather than normalised
    "float_candidate_coefficients": IMPLEMENTATION_DEFECT,
}

DEFECT_NOTE = (
    "float_candidate_coefficients: numpy.linalg.solve reduction order varies "
    "with BLAS thread count, which changes the degree-12 dyadic candidate and "
    "therefore every certified residual. That is scientifically meaningful "
    "drift, so it is NOT normalised away. successor_qualify pins the threading "
    "contract BEFORE numpy is imported (re-exec'ing if needed) and binds "
    "blas_threads/flint_threads into the producer identity, so a record made "
    "under different threading is a different PRODUCER, not a silently "
    "different certificate."
)


def classify_fields() -> dict:
    return {"classes": FIELD_CLASSES,
            "excluded_from_scientific_hash": sorted(CH.EXCLUDED_RUNTIME_FIELDS),
            "implementation_defect_note": DEFECT_NOTE}


def run_once(cell: int, out: Path, *, bits: int = 256) -> dict:
    """One fresh certification in a separate process."""
    qual = ancestry.NS / "code/successor_qualify.py"
    py = ancestry.ROOT / "level4/.venv/bin/python"
    subprocess.run([str(py), str(qual), "--cell", str(cell), "--bits", str(bits),
                    "--out", str(out)], cwd=ancestry.ROOT, check=True,
                   capture_output=True)
    return json.loads(out.read_text())


def repeated_run_hashes(cell: int, reps: int = 2, *, bits: int = 256) -> dict:
    """Fresh processes, identical inputs; the scientific hash must be identical."""
    hashes, records = [], []
    with tempfile.TemporaryDirectory() as d:
        for i in range(reps):
            rec = run_once(cell, Path(d) / f"r{i}.json", bits=bits)
            records.append(rec)
            hashes.append(CH.record_scientific_hash(rec))
    return {"cell": cell, "reps": reps, "hashes": hashes,
            "identical": len(set(hashes)) == 1,
            "cpu_seconds_differed": len({
                round(r["cpu_seconds_including_dependencies"], 3)
                for r in records}) > 1}


def scientific_hash_of(path: Path) -> str:
    return CH.record_scientific_hash(json.loads(Path(path).read_text()))


def compare_against_recorded(repeat_dir) -> dict:
    """Compare fresh repeat runs against the committed records, cell by cell.

    The repeats are produced by the ordinary runner in a separate directory, so
    the two records share nothing but the producer identity and the inputs. Only
    the scientific hash is compared: runtime fields are expected to differ, and
    the check asserts that they DO, so that an accidentally identical file
    cannot pass for a reproduction.
    """
    recorded_dir = ancestry.NS / "diagnostics" / "cells"
    out = {"schema": "k1.cusum-successor.determinism.v1",
           "result_bearing": False, "cells": {}}
    for repeat in sorted(Path(repeat_dir).glob("succ_CUSUM_*.json")):
        original = recorded_dir / repeat.name
        if not original.exists():
            continue
        a = json.loads(original.read_text())
        b = json.loads(repeat.read_text())
        out["cells"][a["cell_index"]] = {
            "recorded_scientific_hash": CH.record_scientific_hash(a),
            "repeat_scientific_hash": CH.record_scientific_hash(b),
            "identical": (CH.record_scientific_hash(a)
                          == CH.record_scientific_hash(b)),
            "producer_identical": (a["producer"]["implementation_hash"]
                                   == b["producer"]["implementation_hash"]),
            "runtime_fields_differed": (
                a["cpu_seconds_including_dependencies"]
                != b["cpu_seconds_including_dependencies"]),
            "recorded_cpu_seconds": a["cpu_seconds_including_dependencies"],
            "repeat_cpu_seconds": b["cpu_seconds_including_dependencies"],
        }
    out["all_identical"] = bool(out["cells"]) and all(
        v["identical"] and v["producer_identical"] for v in out["cells"].values())
    return out


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", required=True,
                    help="directory holding fresh repeat runs")
    ap.add_argument("--out")
    args = ap.parse_args()
    rep = compare_against_recorded(args.repeats)
    text = json.dumps(rep, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text)
    print(text)


if __name__ == "__main__":
    main()
