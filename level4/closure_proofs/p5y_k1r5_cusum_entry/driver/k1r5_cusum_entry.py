"""P5Y-K1R5 CUSUM bridge production entry. THIN WRAPPER - ORCHESTRATION ONLY.

The frozen aux4 runner qualify4.run_cell is a qualification harness: it resolves cells from
the frozen 326-cell spec.CELLS, refuses when spec.PRODUCTION_ENABLED, and binds aux4's own
producer identity and TCB gate. It is NOT edited and NOT called here. Instead certify()
re-executes run_cell's frozen statement block VERBATIM (tests/test_k1r5.py proves AST
identity) on a K1R4 bridge cell dict, binding the K1R5 producer identity through the
unchanged identity4 scheme and K1R5's own TCB gate. No scientific branch, threshold,
formula or numerical routine is copied or rewritten: every one is called, not defined.
"""
import copy
import hashlib
import json
import os
import resource
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CFG = NS / "config"
REPO = Path("/home/ubuntu/work/ReBaseGuard")
AUX4 = REPO / "level4/closure_proofs/p5y_k1_cusum_aux4_fullcover/code"
K1R4 = NS.parent / "p5y_k1r4_bridge_successor"
K1R4_TABLE = K1R4 / "config/CUSUM_BRIDGE_CELL_TABLE.json"
BRIDGE_INDICES = (1000, 1001)
HISTORICAL_INDICES = range(0, 326)
CAMPAIGN = "p5y_k1r5_cusum_entry"
MARKER_SCHEMA = "rebaseguard.p5y.k1r5.cusum-cell-done-marker.v1"

sys.path.insert(0, str(AUX4))
import qualify4 as Q4                     # noqa: E402  frozen; pins threads at import; run_cell never called
from qualify4 import (H, ID, aux_certifier, aux_propagate, aux_refine, refine2,  # noqa: E402
                      require_single_charge, scipy_guard, spec, workprec)
pin_flint, _aux_record = Q4.pin_flint, Q4._aux_record
build_certificates, verify_chain = Q4.build_certificates, Q4.verify_chain


class CusumBridgeRefused(RuntimeError):
    pass


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def canonical(o) -> bytes:
    return (json.dumps(o, sort_keys=True, separators=(",", ":")) + "\n").encode()


def check_schema(cell: dict) -> None:
    """The consumed schema, frozen in config/RESULT_SCHEMA.json (inputs)."""
    for f in ("left", "right", "e0", "rho", "C_evaluation"):
        v = cell.get(f)
        if not (isinstance(v, list) and len(v) == 2 and all(isinstance(x, str) for x in v)
                and Fr(v[1]) == 0):
            raise CusumBridgeRefused(f"{f}: affine [p, '0/1'] pair required (K1R2 schema defect)")
    if not isinstance(cell.get("C_upper"), str):
        raise CusumBridgeRefused("C_upper: plain rational string required")
    L, R, E, P = (Fr(cell[f][0]) for f in ("left", "right", "e0", "rho"))
    if E != (L + R) / 2 or P != (R - L) / 2 or not R > L:
        raise CusumBridgeRefused("e0/rho are not the exact midpoint/half-width")


def bridge_cell(index) -> dict:
    if isinstance(index, int) and index in HISTORICAL_INDICES:
        raise CusumBridgeRefused(f"historical CUSUM cell {index} is inherited evidence, never new work")
    if index not in BRIDGE_INDICES:
        raise CusumBridgeRefused(f"cell {index!r} is not a K1R5 CUSUM bridge cell")
    want = json.loads((K1R4 / "config/CHECKPOINT.json").read_text())["frozen_artifacts"][
        "CUSUM_BRIDGE_CELL_TABLE.json"]
    if _sha(K1R4_TABLE) != want:
        raise CusumBridgeRefused("K1R4 CUSUM bridge table does not match its frozen hash")
    hits = [c for c in json.loads(K1R4_TABLE.read_text())["cells"] if c["index"] == index]
    if len(hits) != 1:
        raise CusumBridgeRefused(f"cell {index} missing from the frozen K1R4 table")
    cell = copy.deepcopy(hits[0])
    check_schema(cell)
    return cell


def producer_context(bits: int) -> dict:
    m = json.loads((CFG / "PRODUCER_MANIFEST.json").read_text())
    ident = json.loads((CFG / "PRODUCER_IDENTITY.json").read_text())
    if _sha(CFG / "PRODUCER_MANIFEST.json") != ident["producer_manifest_hash"]:
        raise CusumBridgeRefused("K1R5 producer manifest does not match its identity")
    return {"producer_manifest_hash": ident["producer_manifest_hash"],
            "producer_manifest_schema": m["schema"], "producer_manifest_path": str(CFG / "PRODUCER_MANIFEST.json"),
            "producer_manifest_version": m["manifest_version"],
            "runtime_contract_hash": ident["runtime_contract_hash"],
            "producer_identity_hash": ident["producer_identity_hash"], "precision_bits": bits}


def verify_tcb(stage: str) -> dict:
    """K1R5's own exact-path TCB gate (aux4's manifest_v2 gate covers aux4's TCB, not this one)."""
    files = json.loads((CFG / "PRODUCER_MANIFEST.json").read_text())["files"]
    roots = (str(REPO) + "/", str(NS.parents[2]) + "/")
    loaded, bad = 0, []
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if not f or not f.endswith(".py"):
            continue
        f = str(Path(f).resolve())
        if not f.startswith(roots) or "/site-packages/" in f:
            continue
        loaded += 1
        if files.get(f) != _sha(f):
            bad.append(f)
    if bad:
        raise CusumBridgeRefused(f"{stage} TCB gate: modules outside/unequal to the manifest: {bad[:3]}")
    return {"stage": stage, "loaded_repository_modules": loaded, "tcb_size": len(files)}


# ============================================================ the frozen statement block
# Statements from `threading = pin_flint()` through `chain = verify_chain(...)` are the
# frozen qualify4.run_cell text, verbatim, EXCEPT exactly two lines, both orchestration:
#   * the cell comes in as an argument (run_cell's `cell = next(c for c in spec.CELLS ...)`)
#   * ctx is the K1R5 producer context (run_cell's `ctx = ID.context(precision_bits=bits)`)
# tests/test_k1r5.py compares the two blocks statement-by-statement with ast.dump.
def certify(cell: dict, bits: int) -> dict:
    threading = pin_flint()
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

        ctx = producer_context(bits)
        certificates = build_certificates(record, ctx, aux_hash)
        chain = verify_chain(record, certificates, ctx, aux_hash)
    return {"record": record, "guard": guard, "ctx": ctx, "certificates": certificates,
            "chain": chain, "charge": charge, "tightening": tightening, "aux_hash": aux_hash,
            "threading": threading, "t0": t0, "w0": w0, "t_prep": t_prep, "cpu_aux": cpu_aux}


# ================================================================== orchestration
def assemble(index: int, out: dict, bits: int) -> dict:
    record, ctx, certificates = out["record"], out["ctx"], out["certificates"]
    record.update({
        "campaign": CAMPAIGN,
        "changes": ["drift_aware_operator_norms(inherited, SOUND)",
                    "second_order_taylor_in_e_order2_chain(inherited)",
                    "second_order_taylor_in_e_whole_cell_D_and_F(inherited)",
                    "auxiliary_third_derivative_node_bound(inherited, SOUND)",
                    "exact_path_tcb_no_basename_exemptions",
                    "complete_runtime_and_backend_binding",
                    "schema_driven_scientific_hash_v2",
                    "final_fail_closed_gate_after_scientific_hash",
                    "k1r5_bridge_cell_entry(orchestration only; kernel unchanged)"],
        "s0_charge_audit": out["charge"],
        "tightening_report": out["tightening"],
        "auxiliary_evidence_hash": out["aux_hash"],
        **{k: v for k, v in ctx.items() if k != "precision_bits"},
        "implementation_hash_kind": ID.IDENTITY_KIND,
        "obligation_universe_total": spec.TOTAL_UNITS,
        "producer": {**ctx, "implementation_hash_kind": ID.IDENTITY_KIND,
                     "rejected_identities": ID.rejected_producer_identities(),
                     "identity_scheme": "identity4 manifest-bound scheme, bound to the K1R5 manifest"},
        "certificates": {uid: {"certificate_hash": H.certificate_hash(c),
                               "identity": c["identity"], "status": c["status"]}
                         for uid, c in sorted(certificates.items())},
        "provenance_chain": out["chain"],
        "cpu_seconds_including_dependencies": time.process_time() - out["t0"],
        "cpu_seconds_auxiliary": out["cpu_aux"],
        "wall_seconds": time.time() - out["w0"],
        "cpu_seconds_prepare": out["t_prep"],
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "precision_bits": bits,
        "threading": out["threading"],
        "production_run": True,
        "result_bearing": False,
        "scientific_certification_of_full_cover": False,
        "universe": ID.universe_unchanged(),
        "k1r5_bridge": {"index": index, "k1r4_table_sha256": _sha(K1R4_TABLE),
                        "k1r4_checkpoint_sha256": (K1R4 / "config/CHECKPOINT_HASH").read_text().strip(),
                        "k1r5_checkpoint_sha256": (CFG / "CHECKPOINT_HASH").read_text().strip()},
    })
    record["scientific_content_hash"] = H.record_scientific_hash(record)
    gate = verify_tcb("final")
    record["scipy_guard"] = out["guard"].require_clean()
    record["producer"]["final_gate"] = {**gate, "ran_after_scientific_hash": True}
    record["scientific_content_hash"] = H.record_scientific_hash(record)
    verify_tcb("final-reverify")
    return record


def atomic_write(path: Path, data: bytes) -> None:
    tmp = path.with_name(".tmp-" + path.name)
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def seal(ev: Path, index: int, record: dict, task_id: str) -> dict:
    """Per-cell, collision-free: the evidence directory must not exist beforehand."""
    ev.mkdir(parents=True, exist_ok=False)
    rec_bytes = canonical(record)
    rp = ev / f"k1r5_CUSUM_{index}_256.json"
    atomic_write(rp, rec_bytes)
    marker = {"marker_schema": MARKER_SCHEMA, "cell_id": index, "task_id": task_id,
              "record_file": rp.name, "record_sha256": hashlib.sha256(rec_bytes).hexdigest(),
              "scientific_content_hash": record["scientific_content_hash"],
              "producer_identity_hash": record["producer_identity_hash"],
              "k1r5_checkpoint_sha256": record["k1r5_bridge"]["k1r5_checkpoint_sha256"],
              "cpu_seconds": record["cpu_seconds_including_dependencies"],
              "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    atomic_write(ev / f"cell_done_{index}.json", canonical(marker))
    return marker


def run_cell(index: int, evidence_dir, task_id: str, bits: int = 256) -> dict:
    """GENUINE PRODUCTION. Never called during qualification."""
    if os.environ.get("K1_THREADS_PINNED") != "1" or any(
            os.environ.get(v) != "1" for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                                                "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")):
        raise CusumBridgeRefused("frozen thread contract not in force")
    if bits != spec.PRODUCTION_BITS:
        raise CusumBridgeRefused(f"precision {bits} != frozen {spec.PRODUCTION_BITS}")
    ev = Path(evidence_dir)
    if ev.exists():
        raise CusumBridgeRefused(f"evidence directory {ev} already exists")
    cell = bridge_cell(index)
    verify_tcb("initial")
    record = assemble(index, certify(cell, bits), bits)
    return seal(ev, index, record, task_id)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="K1R5 CUSUM bridge production entry")
    ap.add_argument("--cell", type=int, required=True, choices=BRIDGE_INDICES)
    ap.add_argument("--evidence-dir", required=True)
    ap.add_argument("--task-id", required=True)
    a = ap.parse_args(argv)
    print(json.dumps(run_cell(a.cell, a.evidence_dir, a.task_id), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
