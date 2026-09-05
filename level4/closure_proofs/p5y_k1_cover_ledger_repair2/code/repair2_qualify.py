"""Repair2 regression runner: certify, then bind real provenance to the result.

The science is Repair1's, unchanged. Repair2 adds only the evidence binding:
after the cell is certified, the full certificate chain is built bottom-up and
verified, and every emitted identity carries the Repair2 producer hash and the
hashes of the actual dependency certificates.

NOT production. Cell 325 is refused by construction, exactly as in Repair1.

usage: repair2_qualify.py --cell 221 [--bits 256] [--scope full|m1] --out FILE
"""
from __future__ import annotations

import argparse
import json
import resource
import time
from pathlib import Path

import prior2                                                   # noqa: F401

import propagate                                                # noqa: E402
import spec                                                     # noqa: E402
from intervals import pin_single_thread, workprec               # noqa: E402
from repair_check import require_single_charge                  # noqa: E402
from repair_layer2 import RepairedCellCertifier                 # noqa: E402
import repair_scoped                                            # noqa: E402

import certhash                                                 # noqa: E402
import producer                                                 # noqa: E402
import provenance                                               # noqa: E402
import repair2_universe as RU2                                  # noqa: E402

FORBIDDEN_CELLS = {325}


def run_cell(index: int, *, bits: int = spec.PRODUCTION_BITS,
             scope: str = "full") -> dict:
    if spec.PRODUCTION_ENABLED:
        raise RuntimeError("PRODUCTION_ENABLED must remain false")
    if index in FORBIDDEN_CELLS:
        raise SystemExit(
            f"cell {index} is CURRENT_CERTIFICATE_FAILURE_ONLY and is out of "
            "scope for this repair")
    threading = pin_single_thread()
    cell = next(c for c in spec.CELLS
                if c["detector"] == "CUSUM" and c["index"] == index)
    t0 = time.process_time()
    with workprec(bits):
        cert = RepairedCellCertifier(cell, bits=bits).prepare()
        t_prep = time.process_time() - t0
        record = (repair_scoped.cell_obligation_m1(cert) if scope == "m1"
                  else propagate.cell_obligations(cert))
        charge = require_single_charge(cert, cert.residuals)

    # --- Repair2: bind the evidence -------------------------------------
    ctx = RU2.context(precision_bits=bits)
    manifest = producer.producer_manifest()
    producer.verify_loaded_modules_covered()
    if scope == "m1":
        # The m=1 SCOPED path is a precision diagnostic, not an obligation
        # discharge: the frozen dependency bundle for this cell is never
        # computed, so no certificate may be issued for the m=1 assembly.
        certificates = {}
        chain = {"status": "NOT_A_CERTIFICATE", "obligations": 0,
                 "all_verified": False,
                 "reason": ("m=1 scoped diagnostic: the frozen dependency "
                            "bundle was not computed, so this run discharges "
                            "no obligation and issues no certificate")}
    else:
        certificates = provenance.build_cell_certificates(record, **ctx)
        chain = provenance.verify_cell(record, certificates=certificates, **ctx)

    record.update({
        "repair": "repair2",
        "repairs": ["producer_implementation_hash", "source_certificate_hashes"],
        "inherits": ["repair1:single_S0_charge",
                     "repair1:exact_resume_identity"],
        "s0_charge_audit": charge,
        "producer": {
            "implementation_hash": ctx["producer_hash"],
            "implementation_hash_kind": RU2.IDENTITY_KIND,
            "backend_hash": ctx["backend_hash"],
            "reviewed_parent_hash": producer.parent_hash(),
            "distinct_from_parent":
                ctx["producer_hash"] != producer.parent_hash(),
            "manifest": manifest,
        },
        "certificates": {uid: {
            "certificate_hash": certhash.certificate_hash(c),
            "identity": c["identity"], "status": c["status"]}
            for uid, c in sorted(certificates.items())},
        "provenance_chain": chain,
        "cpu_seconds_including_dependencies": time.process_time() - t0,
        "cpu_seconds_prepare": t_prep,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "precision_bits": bits,
        "threading": threading,
        "production_run": False,
        "result_bearing": False,
        "scientific_certification_of_full_cover": False,
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
    print(json.dumps({
        "cell": args.cell, "bits": args.bits, "scope": args.scope,
        "cpu_s": rec["cpu_seconds_including_dependencies"],
        "charged_once": rec["s0_charge_audit"]["all_charged_exactly_once"],
        "obligations": rec["provenance_chain"]["obligations"],
        "chain_verified": rec["provenance_chain"]["all_verified"],
        "producer_hash": rec["producer"]["implementation_hash"][:16] + "..."}))


if __name__ == "__main__":
    main()
