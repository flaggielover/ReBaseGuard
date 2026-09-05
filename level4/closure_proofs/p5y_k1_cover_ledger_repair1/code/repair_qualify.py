"""Regression runner for repair1. NOT production, NOT a new scientific campaign.

Re-certifies a small set of already-reviewed CUSUM obligations through the
REPAIRED path so the independently accepted components can be re-checked:

    CUSUM_M_R2_SOUND, CUSUM_ALL_M_ASSEMBLY_SOUND, PRECISION_DIAGNOSTIC

Cell 325 is deliberately NOT re-run and NOT attacked: its state remains
CURRENT_CERTIFICATE_FAILURE_ONLY.

usage: repair_qualify.py --cell 221 [--bits 256] [--scope full|m1] --out FILE
"""
from __future__ import annotations

import argparse
import json
import resource
import time
from pathlib import Path

import prior                                                    # noqa: F401

import propagate                                                # noqa: E402
import spec                                                     # noqa: E402
from intervals import pin_single_thread, workprec               # noqa: E402

import repair_check                                             # noqa: E402
import repair_layer2                                            # noqa: E402
import repair_scoped                                            # noqa: E402
import repair_universe as RU                                    # noqa: E402

FORBIDDEN_CELLS = {325}          # cell 325 is out of scope for this repair


def run_cell(index: int, *, bits: int = spec.PRODUCTION_BITS,
             scope: str = "full") -> dict:
    if spec.PRODUCTION_ENABLED:
        raise RuntimeError("PRODUCTION_ENABLED must remain false")
    if index in FORBIDDEN_CELLS:
        raise SystemExit(
            f"cell {index} is CURRENT_CERTIFICATE_FAILURE_ONLY and is explicitly "
            "out of scope for this repair")
    threading = pin_single_thread()
    cell = next(c for c in spec.CELLS
                if c["detector"] == "CUSUM" and c["index"] == index)
    t0 = time.process_time()
    with workprec(bits):
        cert = repair_layer2.RepairedCellCertifier(cell, bits=bits).prepare()
        t_prep = time.process_time() - t0
        if scope == "m1":
            record = repair_scoped.cell_obligation_m1(cert)
        else:
            record = propagate.cell_obligations(cert)
        charge = repair_check.require_single_charge(cert, cert.residuals)
    record.update({
        "repair": "repair1",
        "repairs": ["single_S0_charge", "exact_resume_identity"],
        "s0_charge_audit": charge,
        "cpu_seconds_including_dependencies": time.process_time() - t0,
        "cpu_seconds_prepare": t_prep,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "precision_bits": bits,
        "threading": threading,
        "production_run": False,
        "result_bearing": False,
        "scientific_certification_of_full_cover": False,
        # A full-cell run discharges the four assembly obligations of that
        # cell, not one "all_m" unit (no such obligation exists in the frozen
        # universe). Stamp each real obligation identity.
        "identity": {
            "|".join(str(x) for x in u): RU.canonical_identity(
                u, backend_hash=RU.reviewed.implementation_hash(),
                impl_hash=RU.reviewed.implementation_hash(),
                precision_bits=bits)
            for u in ([("CUSUM", index, "assembly", "1")] if scope == "m1"
                      else [("CUSUM", index, "assembly", str(m))
                            for m in spec.M_VALUES])},
    })
    return record


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", type=int, required=True)
    ap.add_argument("--bits", type=int, default=spec.PRODUCTION_BITS)
    ap.add_argument("--scope", choices=("full", "m1"), default="full")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rec = run_cell(args.cell, bits=args.bits, scope=args.scope)
    Path(args.out).write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"cell": args.cell, "bits": args.bits, "scope": args.scope,
                      "cpu_s": rec["cpu_seconds_including_dependencies"],
                      "charged_once": rec["s0_charge_audit"][
                          "all_charged_exactly_once"]}))


if __name__ == "__main__":
    main()
