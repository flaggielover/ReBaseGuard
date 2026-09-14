"""Composite integrity audit and K4 composite attestation of the new-glibc successor. READ-ONLY, RESULT-AGNOSTIC.

  composite_audit       1  frozen prov_integrity.audit, unchanged, on the predecessor ledger
                        2  tolerates EXACTLY the bound stop (D_halt = the HOST_DRIFT stop) and the bound unsettled
                           supervisor run; any other predecessor issue refuses
                        3  all old pairs verified, exactly the carry-over cells, digest equal to the binding
                        4  frozen prov_integrity.audit, unchanged, on the successor ledger when it exists
                        5  disjointness, union exactly 0-325, one producer identity, qualification firewall
                        6  both provenance halves disclosed
                        state: COMPLETE (K4-ready) | INCOMPLETE (never K4-ready) | REFUSED
  build_composite_attestation   only from a COMPLETE audit: cells_verified 326, producer_checkpoint_sha256 = the
                        successor checkpoint (which binds the predecessor checkpoint); both halves disclosed
  export_composite      k4_records/ holds exactly one record per verified pair of either half

No K4 scientific assembly is run here. Obligation statuses are never read.
"""
from __future__ import annotations

import json
from pathlib import Path

import gs_schema as GS
import prov_integrity as PI
from prod_common import Refusal, atomic_write_bytes, atomic_write_json, canonical, sha256_bytes

HALF_KEYS = ("ledger_state_sha256", "genesis_entry_sha256", "authorization", "disposition")


def tolerance_for_production(binding: dict) -> dict:
    return {"stop": binding["predecessor"]["stop"], "unsettled_runs": [GS.UNSETTLED_RUN],
            "pairs_sha256": binding["integrity"]["frozen_audit"]["pairs_sha256"],
            "ledger_state_sha256": binding["ledger_state_sha256"],
            "genesis_entry_sha256": binding["journal"]["genesis_entry_sha256"],
            "carryover_cells": list(GS.OLD_CELLS)}


def predecessor_problems(rep: dict, tol: dict) -> list[str]:
    p = []
    issues = rep.get("issues") or {}
    extra = sorted(set(issues) - set(GS.TOLERATED_ISSUES))
    if extra:
        p.append(f"PREDECESSOR_ISSUE_NOT_TOLERATED: {extra}")
    if issues.get(GS.STOP_ISSUE) != [tol["stop"]] or (tol["stop"] or {}).get("reason") != "HOST_DRIFT":
        p.append("PREDECESSOR_STOP_NOT_THE_BOUND_HOST_DRIFT")
    if sorted(issues.get("D_unsettled_supervisor_runs") or []) != sorted(tol["unsettled_runs"]):
        p.append("PREDECESSOR_UNSETTLED_RUNS_NOT_THE_BOUND_RUN")
    if rep.get("disposition") != "HALTED":
        p.append(f"PREDECESSOR_DISPOSITION: {rep.get('disposition')}")
    cells = sorted(int(c) for c in rep.get("pairs") or {})
    if cells != sorted(tol["carryover_cells"]) or rep["A_completeness"]["sealed"] != len(tol["carryover_cells"]):
        p.append("PREDECESSOR_PAIRS_NOT_EXACTLY_THE_CARRYOVER_CELLS")
    if sha256_bytes(canonical(rep.get("pairs"))) != tol["pairs_sha256"]:
        p.append("PREDECESSOR_PAIRS_DIGEST_DIFFERS_FROM_BINDING")
    for k in ("ledger_state_sha256", "genesis_entry_sha256"):
        if rep.get(k) != tol[k]:
            p.append(f"PREDECESSOR_{k.upper()}_DIFFERS_FROM_BINDING")
    return p


def _half(rep: dict, cells_range, source: str, checkpoint_sha256: str) -> dict:
    return {"source": source, "cells": [cells_range[0], cells_range[-1]], "production_checkpoint_sha256": checkpoint_sha256,
            **{k: rep.get(k) for k in HALF_KEYS}, "verified_pairs": len(rep.get("pairs") or {}),
            "pairs": rep.get("pairs"), "integrity_audit_sha256": sha256_bytes(canonical(rep))}


def composite_audit(*, pred_spec, pred_authz, succ_spec, succ_authz, tolerance: dict, qualification_shas,
                    successor_ledger_exists: bool) -> dict:
    p = []
    pred_rep = PI.audit(pred_spec, pred_authz)
    p += predecessor_problems(pred_rep, tolerance)
    succ_rep = PI.audit(succ_spec, succ_authz) if successor_ledger_exists else None
    old = {int(c) for c in pred_rep["pairs"]}
    new = {int(c) for c in (succ_rep or {}).get("pairs", {})}
    if old & new:
        p.append(f"PARTITION_OVERLAP: {sorted(old & new)[:8]}")
    if not set(succ_spec.cell_indices) <= set(GS.NEW_CELLS) or set(succ_spec.cell_indices) & set(GS.OLD_CELLS):
        p.append("SUCCESSOR_UNIVERSE_CONTAINS_A_CARRYOVER_CELL")
    if pred_spec.identity != succ_spec.identity:
        p.append("PRODUCER_IDENTITY_DIFFERS_BETWEEN_HALVES")
    quals = set(qualification_shas)
    for half, rep in (("predecessor", pred_rep), ("successor", succ_rep or {})):
        reused = [c for c, v in (rep.get("pairs") or {}).items() if v["record_sha256"] in quals]
        if reused:
            p.append(f"QUALIFICATION_RECORD_REUSE: {half} {reused[:4]}")
    if succ_rep is not None:
        s_issues = succ_rep.get("issues") or {}
        if s_issues.get("B_pair_refused") or s_issues.get("C_unbound_envelope_files") or s_issues.get("C_evidence") \
                or s_issues.get("A_sealed_without_bound_envelope"):
            p.append(f"SUCCESSOR_PAIR_INTEGRITY: {sorted(s_issues)}")
    union_complete = (old | new) == set(range(GS.UNIVERSE))
    succ_ready = bool(succ_rep and succ_rep["INTEGRITY_READY_FOR_ADJUDICATION"])
    state = "REFUSED" if p else ("COMPLETE" if (union_complete and succ_ready) else "INCOMPLETE")
    rep = {"schema": GS.COMPOSITE_AUDIT_SCHEMA, "state": state, "K4_READY": state == "COMPLETE",
           "result_agnostic": True, "obligation_statuses_read": False, "problems": p,
           "carryover_rule": GS.CARRYOVER_RULE, "old_cells_verified": len(old), "new_cells_verified": len(new),
           "union_complete": union_complete, "successor_ledger_exists": successor_ledger_exists,
           "successor_integrity_ready": succ_ready,
           "producer_identity_hash": succ_spec.identity["producer_identity_hash"],
           "halves": {"predecessor": _half(pred_rep, GS.OLD_CELLS, "predecessor authorized campaign (terminal ledger, "
                                                                 "carried over, never recomputed)", pred_spec.checkpoint_sha256),
                      "successor": _half(succ_rep, GS.NEW_CELLS, "successor campaign (ledger born under the successor run "
                                                                 "authorization)", succ_spec.checkpoint_sha256)
                      if succ_rep is not None else None},
           "successor_issues": sorted((succ_rep or {}).get("issues") or {}),
           "tolerated_predecessor_issues": list(GS.TOLERATED_ISSUES)}
    return rep


def build_composite_attestation(rep: dict, *, successor_checkpoint_sha256: str, predecessor_checkpoint_sha256: str) -> dict:
    if rep.get("schema") != GS.COMPOSITE_AUDIT_SCHEMA or rep.get("state") != "COMPLETE" or rep.get("problems"):
        raise Refusal("ATTESTATION_REFUSED", f"composite audit is {rep.get('state')}: K4 coverage is not complete")
    halves = rep["halves"]
    if rep["old_cells_verified"] + rep["new_cells_verified"] != GS.UNIVERSE:
        raise Refusal("ATTESTATION_REFUSED", "verified cells do not cover exactly 0-325")
    return {"schema": "rebaseguard.p5y.k1.cusum-production.integrity-attestation.v1", "mode": "COMPOSITE",
            "cells_verified": rep["old_cells_verified"] + rep["new_cells_verified"],
            "all_scientific_hashes_verified": True, "k4_input_structure_verified": True, "k4_values_evaluated": False,
            "producer_identity_hash": rep["producer_identity_hash"],
            "producer_checkpoint_sha256": successor_checkpoint_sha256,
            "production_provenance": {
                "composite_rule": GS.CARRYOVER_RULE,
                "successor_checkpoint_binds_predecessor_checkpoint": predecessor_checkpoint_sha256,
                "cells_0_127": "sourced from the predecessor authorized campaign", "cells_128_325": "sourced from the successor campaign",
                "halves": halves, "composite_audit_sha256": sha256_bytes(canonical(rep)),
                "recomputation": "an adjudicator re-runs composite_audit on both ledgers and requires this attestation to "
                                 "recompute exactly"}}


def verify_composite_attestation(att: dict, rep: dict, **kw) -> None:
    if canonical(att) != canonical(build_composite_attestation(rep, **kw)):
        raise Refusal("ATTESTATION_REFUSED", "the composite attestation does not recompute from the composite audit")


def export_composite(rep: dict, *, pred_root, succ_root, out_dir) -> dict:
    if rep.get("state") != "COMPLETE":
        raise Refusal("EXPORT_REFUSED", f"composite audit is {rep.get('state')}")
    out = Path(out_dir)
    if out.exists() and any(out.iterdir()):
        raise Refusal("EXPORT_REFUSED", f"{out} is not empty")
    files = {}
    for half, root in (("predecessor", pred_root), ("successor", succ_root)):
        st = json.loads((Path(root) / "ledger.json").read_text())
        for cell, pair in rep["halves"][half]["pairs"].items():
            data = (Path(root) / st["attempts"][pair["attempt"]]["record"]).read_bytes()
            if sha256_bytes(data) != pair["record_sha256"]:
                raise Refusal("EXPORT_REFUSED", f"{half} cell {cell}: record bytes changed after the audit")
            atomic_write_bytes(out / f"k4_records/aux5_CUSUM_{cell}_256.json", data)
            files[f"k4_records/aux5_CUSUM_{cell}_256.json"] = pair["record_sha256"]
    manifest = {"schema": GS.COMPOSITE_AUDIT_SCHEMA + ".export", "files": files, "cells": len(files),
                "composite_audit_sha256": sha256_bytes(canonical(rep))}
    atomic_write_json(out / "COMPOSITE_EXPORT_MANIFEST.json", manifest)
    return manifest
