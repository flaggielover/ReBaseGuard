"""Re-certification runner with drift-aware norms, full Repair2 provenance.

NOT production. Certifies one frozen cell through the validated Repair1 science
plus the sharper certified operator norms, then binds the Repair2 producer and
source-certificate provenance to the result.

usage: final_qualify.py --cell 325 [--bits 256] --out FILE
"""
from __future__ import annotations

import argparse
import json
import resource
import time
from pathlib import Path

import base                                                     # noqa: F401

import propagate                                                # noqa: E402
import spec                                                     # noqa: E402
from intervals import pin_single_thread, workprec               # noqa: E402
from repair_check import require_single_charge                  # noqa: E402

import certhash                                                 # noqa: E402
import producer                                                 # noqa: E402
import provenance                                               # noqa: E402
import repair2_universe as RU2                                  # noqa: E402

import sharp_certifier                                          # noqa: E402


def run_cell(index: int, *, detector: str = "CUSUM",
             bits: int = spec.PRODUCTION_BITS) -> dict:
    if spec.PRODUCTION_ENABLED:
        raise RuntimeError("PRODUCTION_ENABLED must remain false")
    threading = pin_single_thread()
    cell = next(c for c in spec.CELLS
                if c["detector"] == detector and c["index"] == index)
    t0 = time.process_time()
    w0 = time.time()
    with workprec(bits):
        cert = sharp_certifier.SharpCellCertifier(cell, bits=bits).prepare()
        t_prep = time.process_time() - t0
        record = propagate.cell_obligations(cert)
        charge = require_single_charge(cert, cert.residuals)

    ctx = RU2.context(precision_bits=bits)
    producer.verify_loaded_modules_covered(strict=False)
    certificates = provenance.build_cell_certificates(record, **ctx)
    chain = provenance.verify_cell(record, certificates=certificates, **ctx)

    record.update({
        "campaign": "p5y_k1_final_completion",
        "changes": ["drift_aware_operator_norms"],
        "inherits": ["repair1:single_S0_charge", "repair1:exact_resume_identity",
                     "repair2:producer_binding", "repair2:source_certificate_binding"],
        "s0_charge_audit": charge,
        "norm_improvement": cert.norm_improvement(),
        "producer": {
            "implementation_hash": ctx["producer_hash"],
            "implementation_hash_kind": RU2.IDENTITY_KIND,
            "backend_hash": ctx["backend_hash"],
            "reviewed_parent_hash": producer.parent_hash(),
            "note": ("this record is produced by the final-completion "
                     "certifier, whose modules are NOT in the Repair2 producer "
                     "manifest; the stamped hash is Repair2's and is recorded "
                     "for lineage only, not as this record's producer identity"),
        },
        "certificates": {uid: {"certificate_hash": certhash.certificate_hash(c),
                               "identity": c["identity"], "status": c["status"]}
                         for uid, c in sorted(certificates.items())},
        "provenance_chain": chain,
        "cpu_seconds_including_dependencies": time.process_time() - t0,
        "wall_seconds": time.time() - w0,
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
    ap.add_argument("--detector", default="CUSUM")
    ap.add_argument("--bits", type=int, default=spec.PRODUCTION_BITS)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rec = run_cell(args.cell, detector=args.detector, bits=args.bits)
    Path(args.out).write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    print(json.dumps({
        "cell": args.cell, "bits": args.bits,
        "cpu_s": rec["cpu_seconds_including_dependencies"],
        "wall_s": rec["wall_seconds"],
        "peak_rss_mib": rec["peak_rss_kib"] / 1024,
        "statuses": {m: L["status"] for m, L in sorted(rec["m"].items())},
        "cover_util": {m: round(L["cover"]["utilization"] * 100, 4)
                       for m, L in sorted(rec["m"].items())},
        "chain_verified": rec["provenance_chain"]["all_verified"]}))


if __name__ == "__main__":
    main()
