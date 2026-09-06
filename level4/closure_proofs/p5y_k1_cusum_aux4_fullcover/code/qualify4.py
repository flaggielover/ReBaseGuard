"""Aux4 certification runner. NOT production.

GATE ORDER -- THE POINT OF THIS NAMESPACE
-----------------------------------------
    1. pin threads (before numpy loads) or refuse
    2. initial_gate()        cheap early failure, authorises nothing
    3. SciPy guard ON
    4. all science: residuals, auxiliary evidence, propagation, ledger
    5. assemble the auxiliary record and its hash
    6. build and verify the certificate chain
    7. assemble the record and compute the scientific hash
    8. final_gate()          <-- authorises the certificate. Runs LAST.
    9. atomic write

Aux3 ran its last check between (4) and (5), leaving the lazy import, the
certificate construction and the hash unguarded. Everything after step 8 here is
a file write.

RESUMABILITY
------------
`--out` is written atomically: a temporary file in the same directory, fsynced,
then `os.replace`. A record already present and admissible under the CURRENT
producer identity is left alone; anything else is recomputed. A crashed run
therefore resumes without inheriting a partial or foreign record.

usage: qualify4.py --cell 321 [--bits 256] --out FILE [--skip-if-current]
"""
from __future__ import annotations

import os
import sys

_PINNED = {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
           "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"}


class ThreadingContractViolated(RuntimeError):
    """numpy was imported before the thread environment could be pinned."""


def pin_threads() -> None:
    if "numpy" in sys.modules and os.environ.get("K1_THREADS_PINNED") != "1":
        return                      # cannot pin retroactively; run_cell refuses
    os.environ.update(_PINNED)
    os.environ["K1_THREADS_PINNED"] = "1"


pin_threads()

import argparse                                                 # noqa: E402
import json                                                     # noqa: E402
import resource                                                 # noqa: E402
import tempfile                                                 # noqa: E402
import time                                                     # noqa: E402
from pathlib import Path                                        # noqa: E402

import ancestry4                                                # noqa: F401,E402

import certhash as repair2_certhash                             # noqa: E402
import provenance as repair2_provenance                         # noqa: E402
import spec                                                     # noqa: E402
from intervals import mag_fraction, workprec                    # noqa: E402
from repair_check import require_single_charge                  # noqa: E402

import refine2                                                  # noqa: E402
import aux_certifier                                            # noqa: E402
import aux_propagate                                            # noqa: E402
import aux_refine                                               # noqa: E402

import hash_v2 as H                                             # noqa: E402
import identity4 as ID                                          # noqa: E402
import manifest_v2                                              # noqa: E402
import scipy_guard                                              # noqa: E402


def pin_flint() -> dict:
    import flint
    flint.ctx.threads = 1
    return {"flint_threads": flint.ctx.threads,
            "blas_threads": os.environ.get("OPENBLAS_NUM_THREADS"),
            "pinned_before_numpy_import": os.environ.get("K1_THREADS_PINNED") == "1"}


def build_certificates(record: dict, ctx: dict, aux_hash: str) -> dict:
    detector, index = record["detector"], record["cell_index"]
    ms = [int(m) for m in record["m"]]
    order = repair2_provenance.cell_units(detector, index, m_values=ms)
    certs: dict = {}
    for unit in order:
        sources = ID.expected_source_hashes(unit, certs)
        ident = ID.canonical_identity(unit, source_certificate_hashes=sources,
                                      auxiliary_evidence_hash=aux_hash, **ctx)
        certs[ID.unit_id(unit)] = {
            "identity": ident,
            "certified": _certified_content(unit, record),
            "status": _obligation_status(unit, record)}
    return certs


def _certified_content(unit: tuple, record: dict) -> dict:
    return repair2_certhash.certified_content(unit, record)


def _obligation_status(unit: tuple, record: dict) -> str:
    return repair2_certhash.obligation_status(unit, record)


def verify_chain(record: dict, certs: dict, ctx: dict, aux_hash: str) -> dict:
    seen: set = set()

    def walk(unit):
        uid = ID.unit_id(unit)
        if uid in seen:
            return
        seen.add(uid)
        for dep in ID.dependencies_of(unit):
            walk(dep)
        ID.admit_resume_record(certs[uid]["identity"], unit,
                               dependency_certificates=certs,
                               auxiliary_evidence_hash=aux_hash, **ctx)

    detector, index = record["detector"], record["cell_index"]
    ms = [int(m) for m in record["m"]]
    units = repair2_provenance.cell_units(detector, index, m_values=ms)
    for unit in units:
        walk(unit)
    leaves = [u for u in units if not ID.dependencies_of(u)]
    return {"all_verified": True,
            "obligations": len(units),
            "units_verified": len(seen),
            "leaf_units": [ID.unit_id(u) for u in leaves],
            "leaf_maps_empty": all(
                certs[ID.unit_id(u)]["identity"]["source_certificate_hashes"] == {}
                for u in leaves),
            "auxiliary_evidence_bound": all(
                certs[ID.unit_id(u)]["identity"]["auxiliary_evidence_hash"] == aux_hash
                for u in units)}


def _aux_record(cert, aux, aux_mid) -> dict:
    """The nested auxiliary evidence. Every field here is hashed by schema V2."""
    return {
        "kind": aux_certifier.AUX_KIND,
        "order": aux_certifier.AUX_ORDER,
        "hermite_weight": cert.aux_weight,
        "ownership": ID.AUXILIARY_OWNERSHIP,
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


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def record_is_current(path: Path) -> bool:
    """True if `path` already holds an Aux4 record under the CURRENT identity."""
    if not path.exists():
        return False
    try:
        rec = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return False
    ident = manifest_v2.identity()
    return (rec.get("producer", {}).get("producer_identity_hash")
            == ident["producer_identity_hash"]
            and rec.get("scientific_content_hash")
            == H.record_scientific_hash(rec))


def run_cell(index: int, *, detector: str = "CUSUM",
             bits: int = spec.PRODUCTION_BITS) -> dict:
    if spec.PRODUCTION_ENABLED:
        raise RuntimeError("PRODUCTION_ENABLED must remain false")
    if os.environ.get("K1_THREADS_PINNED") != "1":
        raise ThreadingContractViolated(
            "numpy was imported before the thread environment was pinned; "
            "run this module as a script, or pin the environment first")

    manifest_v2.initial_gate()          # cheap early failure; authorises nothing

    threading = pin_flint()
    cell = next(c for c in spec.CELLS
                if c["detector"] == detector and c["index"] == index)
    t0, w0 = time.process_time(), time.time()

    guard = scipy_guard.ScipyGuard()
    with guard:
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
                return aux_refine.AuxiliaryRefinement(c, mid_nodes, aux_mid)

            record = aux_propagate.cell_obligations(
                cert,
                whole_cell_refinement=refine2.refine,
                node_refinement_factory=make_backend)
            charge = require_single_charge(cert, cert.residuals)
            tightening = cert.tightening_report()

        record["auxiliary_evidence"] = _aux_record(cert, aux, holder["aux_mid"])
        aux_hash = H.auxiliary_evidence_hash(record)

        ctx = ID.context(precision_bits=bits)
        certificates = build_certificates(record, ctx, aux_hash)
        chain = verify_chain(record, certificates, ctx, aux_hash)

        record.update({
            "campaign": "p5y_k1_cusum_aux4_fullcover",
            "changes": ["drift_aware_operator_norms(inherited, SOUND)",
                        "second_order_taylor_in_e_order2_chain(inherited)",
                        "second_order_taylor_in_e_whole_cell_D_and_F(inherited)",
                        "auxiliary_third_derivative_node_bound(inherited, SOUND)",
                        "exact_path_tcb_no_basename_exemptions",
                        "complete_runtime_and_backend_binding",
                        "schema_driven_scientific_hash_v2",
                        "final_fail_closed_gate_after_scientific_hash"],
            "s0_charge_audit": charge,
            "tightening_report": tightening,
            "auxiliary_evidence_hash": aux_hash,
            **{k: v for k, v in ctx.items() if k != "precision_bits"},
            "implementation_hash_kind": ID.IDENTITY_KIND,
            "obligation_universe_total": spec.TOTAL_UNITS,
            "producer": {**ctx,
                         "implementation_hash_kind": ID.IDENTITY_KIND,
                         "rejected_identities": ID.rejected_producer_identities()},
            "certificates": {uid: {"certificate_hash": H.certificate_hash(c),
                                   "identity": c["identity"], "status": c["status"]}
                             for uid, c in sorted(certificates.items())},
            "provenance_chain": chain,
            "cpu_seconds_including_dependencies": time.process_time() - t0,
            "cpu_seconds_auxiliary": cpu_aux,
            "wall_seconds": time.time() - w0,
            "cpu_seconds_prepare": t_prep,
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "precision_bits": bits,
            "threading": threading,
            "production_run": False,
            "result_bearing": False,
            "scientific_certification_of_full_cover": False,
            "universe": ID.universe_unchanged(),
        })
        record["scientific_content_hash"] = H.record_scientific_hash(record)

    # ---- THE GATE THAT AUTHORISES THIS CERTIFICATE. Nothing precedes the write.
    gate = manifest_v2.final_gate(scipy_guard=guard)
    record["scipy_guard"] = gate["scipy_guard"]
    record["producer"]["runtime"] = gate["runtime"]
    record["producer"]["final_gate"] = {
        "stage": gate["stage"],
        "loaded_repository_modules": gate["loaded_repository_modules"],
        "tcb_size": gate["tcb_size"],
        "ran_after_scientific_hash": True}
    # the gate added provenance fields; rebind the hash over the complete record
    record["scientific_content_hash"] = H.record_scientific_hash(record)
    manifest_v2.final_gate(scipy_guard=guard)      # and re-verify after rebinding
    return record


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", type=int, required=True)
    ap.add_argument("--detector", default="CUSUM")
    ap.add_argument("--bits", type=int, default=spec.PRODUCTION_BITS)
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip-if-current", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    if args.skip_if_current and record_is_current(out):
        print(json.dumps({"cell": args.cell, "skipped": "already current"}))
        return
    rec = run_cell(args.cell, detector=args.detector, bits=args.bits)
    atomic_write(out, json.dumps(rec, indent=1, sort_keys=True) + "\n")
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
        "scipy_free": rec["scipy_guard"]["scipy_free"],
        "chain": rec["provenance_chain"]["all_verified"],
        "sci_hash": rec["scientific_content_hash"][:16]}))


if __name__ == "__main__":
    main()
