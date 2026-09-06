"""Certification runner for the aux3 successor. NOT production.

THREADING
---------
The float candidate solve goes through `numpy.linalg.solve`; multi-threaded BLAS
changes its reduction order, hence the dyadic candidate, hence every certified
residual. The environment must therefore be pinned BEFORE numpy is imported.
This module does not re-exec itself to achieve that -- the predecessor did, and
a process whose `argv[0]` is not a file (`python -c`, `python -m unittest`) died
in the attempt. Instead it pins the environment if numpy has not yet loaded, and
otherwise refuses to certify. Fail closed, no surprises, no re-exec.

WIRING
------
Everything is passed, nothing is patched:

    cert       = Aux3Certifier(cell).prepare()
    aux        = cert.aux_residuals()
    backend    = AuxiliaryRefinement(cert, mid_nodes, aux_mid)
    record     = aux_propagate.cell_obligations(
                     cert,
                     whole_cell_refinement=refine2.refine,   # inherited, SOUND
                     node_refinement_factory=make_backend)

GATE ORDER
----------
The committed manifest is required, and loaded-module coverage is checked
fail-closed, BEFORE any certificate is built and again after the science has run
(the second check catches a module imported lazily mid-run). Nothing is emitted
if either fails.

usage: aux_qualify.py --cell 321 [--bits 256] --out FILE
"""
from __future__ import annotations

import os
import sys

_PINNED = {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
           "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"}


class ThreadingContractViolated(RuntimeError):
    """numpy was imported before the thread environment could be pinned."""


def pin_threads() -> None:
    """Pin before numpy loads; if it already loaded unpinned, refuse later."""
    if "numpy" in sys.modules and os.environ.get("K1_THREADS_PINNED") != "1":
        return                      # cannot pin retroactively; run_cell refuses
    os.environ.update(_PINNED)
    os.environ["K1_THREADS_PINNED"] = "1"


pin_threads()

import argparse                                                 # noqa: E402
import json                                                     # noqa: E402
import resource                                                 # noqa: E402
import time                                                     # noqa: E402
from pathlib import Path                                        # noqa: E402

import ancestry                                                 # noqa: F401,E402

import provenance as repair2_provenance                         # noqa: E402
import spec                                                     # noqa: E402
from intervals import mag_fraction, workprec                    # noqa: E402
from repair_check import require_single_charge                  # noqa: E402

import refine2                                                  # noqa: E402

import aux_certhash as CH                                       # noqa: E402
import aux_certifier                                            # noqa: E402
import aux_propagate                                            # noqa: E402
import aux_refine                                               # noqa: E402
import aux_universe as SU                                       # noqa: E402
import manifest                                                 # noqa: E402


def pin_flint() -> dict:
    import flint
    flint.ctx.threads = 1
    return {"flint_threads": flint.ctx.threads,
            "blas_threads": os.environ.get("OPENBLAS_NUM_THREADS"),
            "pinned_before_numpy_import": os.environ.get("K1_THREADS_PINNED") == "1"}


def build_certificates(record: dict, ctx: dict, aux_hash: str) -> dict:
    """Bottom-up chain under this successor's resolvable producer identity."""
    detector, index = record["detector"], record["cell_index"]
    ms = [int(m) for m in record["m"]]
    order = repair2_provenance.cell_units(detector, index, m_values=ms)
    certs: dict = {}
    for unit in order:
        sources = SU.expected_source_hashes(unit, certs)
        ident = SU.canonical_identity(unit, source_certificate_hashes=sources,
                                      auxiliary_evidence_hash=aux_hash, **ctx)
        certs[SU.unit_id(unit)] = CH.build_certificate(unit, ident, record)
    return certs


def verify_chain(record: dict, certs: dict, ctx: dict, aux_hash: str) -> dict:
    """Recursive verification against the certificates actually on hand."""
    seen: set = set()

    def walk(unit):
        uid = SU.unit_id(unit)
        if uid in seen:
            return
        seen.add(uid)
        for dep in SU.dependencies_of(unit):
            walk(dep)
        SU.admit_resume_record(certs[uid]["identity"], unit,
                               dependency_certificates=certs,
                               auxiliary_evidence_hash=aux_hash, **ctx)

    detector, index = record["detector"], record["cell_index"]
    ms = [int(m) for m in record["m"]]
    units = repair2_provenance.cell_units(detector, index, m_values=ms)
    for unit in units:
        walk(unit)
    leaves = [u for u in units if not SU.dependencies_of(u)]
    return {"all_verified": True,
            "obligations": len(units),
            "units_verified": len(seen),
            "leaf_units": [SU.unit_id(u) for u in leaves],
            "leaf_maps_empty": all(
                certs[SU.unit_id(u)]["identity"]["source_certificate_hashes"] == {}
                for u in leaves),
            "auxiliary_evidence_bound": all(
                certs[SU.unit_id(u)]["identity"]["auxiliary_evidence_hash"] == aux_hash
                for u in units)}


def _aux_record(cert, aux, aux_mid) -> dict:
    return {
        "kind": aux_certifier.AUX_KIND,
        "order": aux_certifier.AUX_ORDER,
        "hermite_weight": cert.aux_weight,
        "ownership": SU.AUXILIARY_OWNERSHIP,
        "objects": {name: {"delta_mid": str(mag_fraction(v["delta_mid"])),
                           "polynomial_residual":
                               str(mag_fraction(v["polynomial_residual"])),
                           "truncation_allowance":
                               str(mag_fraction(v["truncation_allowance"])),
                           "envelope": str(mag_fraction(v["envelope"])),
                           "cpu_seconds": v.get("cpu_seconds", 0.0),
                           "bernstein_calls": v.get("bernstein_calls", 0),
                           "kernel_calls": v.get("kernel_calls", 0)}
                    for name, v in sorted(aux.items())},
        "candidate_suprema": {f"{f}:{i}:{o}": str(mag_fraction(v))
                              for (f, i, o), v in sorted(
                                  ((k, v) for k, v in cert.sup.items()
                                   if k[2] == aux_certifier.AUX_ORDER),
                                  key=lambda kv: str(kv[0]))},
        "midpoint_eps": {k: str(mag_fraction(v))
                         for k, v in sorted(aux_mid.items())
                         if k.endswith(":3")},
    }


def run_cell(index: int, *, detector: str = "CUSUM",
             bits: int = spec.PRODUCTION_BITS) -> dict:
    if spec.PRODUCTION_ENABLED:
        raise RuntimeError("PRODUCTION_ENABLED must remain false")
    if os.environ.get("K1_THREADS_PINNED") != "1":
        raise ThreadingContractViolated(
            "numpy was imported before the thread environment was pinned; "
            "run this module as a script, or set the pinned environment first")

    # --- fail-closed producer gate, BEFORE anything is certified
    gate = manifest.require()

    threading = pin_flint()
    cell = next(c for c in spec.CELLS
                if c["detector"] == detector and c["index"] == index)
    t0, w0 = time.process_time(), time.time()
    with workprec(bits):
        cert = aux_certifier.Aux3Certifier(cell, bits=bits).prepare()
        t_prep = time.process_time() - t0

        cert.all_residuals()
        t_aux = time.process_time()
        aux = cert.aux_residuals()
        cpu_aux = time.process_time() - t_aux

        holder = {}

        def make_backend(c, mid_nodes):
            aux_mid = aux_certifier.midpoint_order3_eps(c, mid_nodes)
            holder["aux_mid"] = aux_mid
            backend = aux_refine.AuxiliaryRefinement(c, mid_nodes, aux_mid)
            holder["backend"] = backend
            return backend

        record = aux_propagate.cell_obligations(
            cert,
            whole_cell_refinement=refine2.refine,
            node_refinement_factory=make_backend)
        charge = require_single_charge(cert, cert.residuals)
        tightening = cert.tightening_report()

    # --- fail-closed again: nothing was imported behind our back mid-run
    manifest.require()

    record["auxiliary_evidence"] = _aux_record(cert, aux, holder["aux_mid"])
    aux_hash = CH.auxiliary_evidence_hash(record)

    ctx = SU.context(precision_bits=bits)
    certificates = build_certificates(record, ctx, aux_hash)
    chain = verify_chain(record, certificates, ctx, aux_hash)

    record.update({
        "campaign": "p5y_k1_cusum_aux3_successor",
        "changes": ["drift_aware_operator_norms(inherited, SOUND)",
                    "second_order_taylor_in_e_order2_chain(inherited)",
                    "second_order_taylor_in_e_whole_cell_D_and_F(inherited, SOUND)",
                    "auxiliary_third_derivative_node_bound(new)",
                    "explicit_dependency_injection(no monkey-patching)",
                    "committed_immutable_producer_manifest"],
        "s0_charge_audit": charge,
        "tightening_report": tightening,
        "auxiliary_evidence_hash": aux_hash,
        "producer": {
            **SU.context(precision_bits=bits),
            "implementation_hash_kind": SU.IDENTITY_KIND,
            "manifest_file_count": gate["files"],
            "runtime": gate["runtime"],
            "loaded_module_coverage_strict": True,
            "rejected_identities": SU.rejected_producer_identities(),
        },
        "certificates": {uid: {"certificate_hash": CH.certificate_hash(c),
                               "identity": c["identity"], "status": c["status"]}
                         for uid, c in sorted(certificates.items())},
        "provenance_chain": chain,
        "scientific_content_hash": None,
        "cpu_seconds_including_dependencies": time.process_time() - t0,
        "cpu_seconds_auxiliary": cpu_aux,
        "wall_seconds": time.time() - w0,
        "cpu_seconds_prepare": t_prep,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "precision_bits": bits,
        "threading": threading,
        "scipy_imported_during_run": any(
            m.split(".")[0] == "scipy" for m in sys.modules),
        "scipy_called_during_run": False,
        "production_run": False,
        "result_bearing": False,
        "scientific_certification_of_full_cover": False,
        "universe": SU.universe_unchanged(),
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
    from fractions import Fraction as F
    print(json.dumps({
        "cell": args.cell, "bits": args.bits,
        "cpu_s": round(rec["cpu_seconds_including_dependencies"], 1),
        "cpu_aux_s": round(rec["cpu_seconds_auxiliary"], 1),
        "peak_rss_mib": round(rec["peak_rss_kib"] / 1024, 1),
        "statuses": {m: L["status"] for m, L in sorted(rec["m"].items())},
        "cover_util": {m: round(L["cover"]["utilization"] * 100, 3)
                       for m, L in sorted(rec["m"].items())},
        "M_R2": {m: float(F(L["M_R2"])) for m, L in sorted(rec["m"].items())},
        "nodes_tightened": rec["node_refinement"]["nodes_tightened"],
        "chain": rec["provenance_chain"]["all_verified"],
        "sci_hash": rec["scientific_content_hash"][:16]}))


if __name__ == "__main__":
    main()
