"""Certification runner for the CUSUM completion successor. NOT production.

DETERMINISM CONTRACT (Phase 3)
------------------------------
The float candidate solve goes through `numpy.linalg.solve`. If BLAS runs
multi-threaded its reduction order varies between runs, the degree-12 dyadic
candidate changes, and every certified residual changes with it. Setting the
thread environment inside the process is TOO LATE -- OpenBLAS sizes its pool at
import. So this module pins the environment and, if it was not already pinned,
RE-EXECS itself before numpy can be imported. The contract is then bound into
the producer identity, so a record made under different threading is a different
producer rather than a silently different certificate.

usage: successor_qualify.py --cell 321 [--bits 256] --out FILE
"""
from __future__ import annotations

import os
import sys

_PINNED = {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
           "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"}

if os.environ.get("K1_THREADS_PINNED") != "1":
    # Re-exec with a deterministic threading contract BEFORE numpy loads.
    env = dict(os.environ)
    env.update(_PINNED)
    env["K1_THREADS_PINNED"] = "1"
    os.execve(sys.executable, [sys.executable] + sys.argv, env)

import argparse                                                 # noqa: E402
import json                                                     # noqa: E402
import resource                                                 # noqa: E402
import time                                                     # noqa: E402
from pathlib import Path                                        # noqa: E402

import ancestry                                                 # noqa: F401,E402

import propagate                                                # noqa: E402
import provenance as repair2_provenance                         # noqa: E402
import spec                                                     # noqa: E402
from intervals import workprec                                  # noqa: E402
from repair_check import require_single_charge                  # noqa: E402
from repair_universe import dependencies_of                     # noqa: E402

import order2                                                   # noqa: E402
import refine2                                                  # noqa: E402
import successor_certhash as CH                                 # noqa: E402
import successor_producer as SP                                 # noqa: E402
import successor_universe as SU                                 # noqa: E402


def pin_flint() -> dict:
    import flint
    flint.ctx.threads = 1
    return {"flint_threads": flint.ctx.threads,
            "blas_threads": os.environ.get("OPENBLAS_NUM_THREADS"),
            "pinned_before_numpy_import": True}


def build_certificates(record: dict, ctx: dict) -> dict:
    """Bottom-up chain under THIS successor's producer identity."""
    detector, index = record["detector"], record["cell_index"]
    ms = [int(m) for m in record["m"]]
    order = repair2_provenance.cell_units(detector, index, m_values=ms)
    certs: dict = {}
    for unit in order:
        sources = SU.expected_source_hashes(unit, certs)
        ident = SU.canonical_identity(unit, source_certificate_hashes=sources,
                                      **ctx)
        certs[SU.unit_id(unit)] = CH.build_certificate(unit, ident, record)
    return certs


def verify_chain(record: dict, certs: dict, ctx: dict) -> dict:
    """Recursive verification against the certificates actually on hand."""
    seen: set = set()

    def walk(unit):
        uid = SU.unit_id(unit)
        if uid in seen:
            return
        cert = certs[uid]
        deps = dependencies_of(unit)
        declared = cert["identity"]["source_certificate_hashes"]
        if not deps and declared != {}:
            raise SU.ProvenanceRejected(f"{uid}: leaf must have an empty map")
        if deps and not declared:
            raise SU.ProvenanceRejected(f"{uid}: non-leaf presented an empty map")
        for dep in deps:
            walk(dep)
        SU.admit_resume_record(cert["identity"], unit,
                               dependency_certificates=certs, **ctx)
        seen.add(uid)

    ms = [int(m) for m in record["m"]]
    roots = [(record["detector"], record["cell_index"], "assembly", str(m))
             for m in ms]
    for r in roots:
        walk(r)
    leaves = [u for u in repair2_provenance.cell_units(
        record["detector"], record["cell_index"], m_values=ms)
        if not dependencies_of(u)]
    return {"obligations": len(certs), "units_verified": len(seen),
            "all_verified": len(seen) == len(certs),
            "leaf_units": [SU.unit_id(u) for u in leaves],
            "leaf_maps_empty": all(
                certs[SU.unit_id(u)]["identity"]["source_certificate_hashes"] == {}
                for u in leaves)}


def run_cell(index: int, *, detector: str = "CUSUM",
             bits: int = spec.PRODUCTION_BITS) -> dict:
    if spec.PRODUCTION_ENABLED:
        raise RuntimeError("PRODUCTION_ENABLED must remain false")
    threading = pin_flint()
    # `propagate` is reviewed and unedited; its whole-cell refinement dependency
    # is substituted explicitly here and stamped into the record below.
    refinement = refine2.install()
    cell = next(c for c in spec.CELLS
                if c["detector"] == detector and c["index"] == index)
    t0, w0 = time.process_time(), time.time()
    with workprec(bits):
        cert = order2.Order2Certifier(cell, bits=bits).prepare()
        t_prep = time.process_time() - t0
        record = propagate.cell_obligations(cert)
        charge = require_single_charge(cert, cert.residuals)
        tightening = cert.tightening_report()

    ctx = SU.context(precision_bits=bits)
    SP.verify_loaded_modules_covered(strict=False)
    certificates = build_certificates(record, ctx)
    chain = verify_chain(record, certificates, ctx)

    record.update({
        "campaign": "p5y_k1_cusum_completion_successor",
        "changes": ["drift_aware_operator_norms(inherited, SOUND)",
                    "second_order_taylor_in_e_order2_chain",
                    "drift_aware_closed_form_source_suprema",
                    "second_order_taylor_in_e_whole_cell_D_and_F",
                    "new_producer_identity"],
        "whole_cell_refinement_module": {
            "module": "refine2", "tightening": refinement,
            "substitutes": "refine (reviewed, unedited)"},
        "s0_charge_audit": charge,
        "tightening_report": tightening,
        "producer": {
            "implementation_hash": ctx["producer_hash"],
            "implementation_hash_kind": SU.IDENTITY_KIND,
            "backend_hash": ctx["backend_hash"],
            "rejected_lineages": SP.rejected_producer_hashes(),
            "manifest_file_count": len(SP.producer_manifest()["files"]),
        },
        "certificates": {uid: {"certificate_hash": CH.certificate_hash(c),
                               "identity": c["identity"], "status": c["status"]}
                         for uid, c in sorted(certificates.items())},
        "provenance_chain": chain,
        "scientific_content_hash": None,     # filled below, after stripping
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
    record["scientific_content_hash"] = CH.record_scientific_hash(record)
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
        "cpu_s": round(rec["cpu_seconds_including_dependencies"], 1),
        "peak_rss_mib": round(rec["peak_rss_kib"] / 1024, 1),
        "statuses": {m: L["status"] for m, L in sorted(rec["m"].items())},
        "cover_util": {m: round(L["cover"]["utilization"] * 100, 3)
                       for m, L in sorted(rec["m"].items())},
        "M_R2": {m: float(__import__("fractions").Fraction(L["M_R2"]))
                 for m, L in sorted(rec["m"].items())},
        "chain": rec["provenance_chain"]["all_verified"],
        "sci_hash": rec["scientific_content_hash"][:16]}))


if __name__ == "__main__":
    main()
