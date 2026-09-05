"""Representative qualification runner. NOT production, and it cannot become one.

Executes the complete frozen cover ledger for a small representative set of
cells and writes a NON-RESULT-BEARING diagnostic JSON. Every output is stamped
`production_run: false` and `result_bearing: false`. The runner refuses to
process the whole cover: `require_production()` in the frozen reference algebra
is the only gate that could authorise that, and it always raises.

usage:  python qualify.py --detector CUSUM --cell 42 [--bits 256] --out FILE
        python qualify.py --representatives --out DIR
"""
from __future__ import annotations

import argparse
import json
import resource
import sys
import time
from fractions import Fraction as F
from pathlib import Path

import spec
import universe
from intervals import pin_single_thread, workprec

NS = Path(__file__).resolve().parents[1]

# Frozen representative anchors (diagnostics/REPRESENTATIVES.md). The anchor
# SELECTS a cell; the expansion point is always that cell's exact midpoint.
ANCHORS = (F(0), F(1, 10), F(1, 4), F(1), F(27, 5), F(11, 2))
ANCHOR_ROLE = {
    F(0): "near-zero; the historical 244% dF_0 near-zero difficulty",
    F(1, 10): "near-zero interior",
    F(1, 4): "interior",
    F(1): "interior",
    F(27, 5): "far interior, approaching the far-field handoff",
    F(11, 2): "splice-adjacent: the exact CUSUM terminal 11/2",
}

MAX_REPRESENTATIVE_CELLS = 12


def anchor_cells(detector: str = "CUSUM") -> list[tuple[F, dict]]:
    cells = spec.cells_for(detector)
    out = []
    for a in ANCHORS:
        for c in cells:
            left, right = F(c["left"][0]), F(c["right"][0])
            if left <= a < right or (a == right and c["index"] == len(cells) - 1):
                out.append((a, c))
                break
        else:
            raise LookupError(f"no cell contains anchor {a}")
    return out


def run_cell(detector: str, index: int, *, bits: int = spec.PRODUCTION_BITS,
             scope: str = "full") -> dict:
    threading = pin_single_thread()
    if spec.PRODUCTION_ENABLED:
        raise RuntimeError("PRODUCTION_ENABLED must remain false")
    cell = next(c for c in spec.CELLS
                if c["detector"] == detector and c["index"] == index)
    if detector != "CUSUM":
        return {"detector": detector, "cell_index": index,
                "status": "NOT_IMPLEMENTED",
                "failure_class": "SR_RAW_DAG_NOT_IMPLEMENTED",
                "certificate_status": (
                    "no raw-variable SR DAG exists in the repository: Task1R "
                    "certified the F_0 class only, on one patch at one drift, in "
                    "a different (softplus Taylor-model) formulation. h/S/F/dF "
                    "for r>=1, the derivative and curvature chains, and the "
                    "interval-e whole-cell envelopes are all unimplemented."),
                "result_bearing": False, "production_run": False}
    import cusum_layer2 as L2
    import propagate
    import scoped
    t0 = time.process_time()
    with workprec(bits):
        cert = L2.CellCertifier(cell, bits=bits).prepare()
        t_prep = time.process_time() - t0
        record = (scoped.cell_obligation_m1(cert) if scope == "m1"
                  else propagate.cell_obligations(cert))
    record["cpu_seconds_including_dependencies"] = time.process_time() - t0
    record["cpu_seconds_prepare"] = t_prep
    record["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    record["precision_bits"] = bits
    record["threading"] = threading
    record["production_run"] = False
    record["result_bearing"] = False
    record["scientific_certification_of_full_cover"] = False
    record["identity"] = universe.unit_identity(
        (detector, index, "assembly", "all_m"),
        backend_hash=universe.implementation_hash(),
        precision_bits=bits)
    return record


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--detector", default="CUSUM")
    ap.add_argument("--cell", type=int)
    ap.add_argument("--bits", type=int, default=spec.PRODUCTION_BITS)
    ap.add_argument("--representatives", action="store_true")
    ap.add_argument("--scope", choices=("full", "m1"), default="full")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if args.representatives:
        cells = anchor_cells(args.detector)
        if len(cells) > MAX_REPRESENTATIVE_CELLS:
            raise SystemExit("representative set too large; this is not production")
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        for anchor, cell in cells:
            rec = run_cell(args.detector, cell["index"], bits=args.bits)
            rec["anchor"] = str(anchor)
            rec["anchor_role"] = ANCHOR_ROLE[anchor]
            (out / f"{args.detector}_{cell['index']}_{args.bits}.json").write_text(
                json.dumps(rec, indent=1, sort_keys=True) + "\n")
        return

    if args.cell is None:
        raise SystemExit("--cell or --representatives required")
    rec = run_cell(args.detector, args.cell, bits=args.bits, scope=args.scope)
    for anchor, cell in anchor_cells(args.detector) if args.detector == "CUSUM" else []:
        if cell["index"] == args.cell:
            rec["anchor"] = str(anchor)
            rec["anchor_role"] = ANCHOR_ROLE[anchor]
    Path(args.out).write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"detector": args.detector, "cell": args.cell,
                      "bits": args.bits,
                      "cpu_s": rec.get("cpu_seconds_including_dependencies"),
                      "status": rec.get("status", "COMPUTED")}))


if __name__ == "__main__":
    sys.exit(main())
