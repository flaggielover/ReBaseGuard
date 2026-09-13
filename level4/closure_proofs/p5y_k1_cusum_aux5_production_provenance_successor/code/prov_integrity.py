"""CUSUM production integrity audit, pair export and K4 attestation. READ-ONLY, RESULT-AGNOSTIC, NON-CERTIFYING.

The CUSUM analogue of the PS1 Lane C audit (p5y_k1_ps1_postk1_adjudication_tooling). It is the ONLY sanctioned
admission path from a production ledger to any downstream consumer (K1 adjudication, K4 assembly, coverage assembly,
closure reports): a cell counts only as a (scientific record, bound envelope) pair that `verify_pair` accepts.

  A  completeness: every frozen cell is a verified pair
  B  pair verification (record bytes, envelope recomputation, ledger binding, pre-result authorization)
  C  stray / unbound envelope files; sealed or envelope evidence drift
  D  open attempts, unsettled supervisor runs, halt
  Obligation statuses are never read.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import prov_schema as S
import prod_ledger as L
import prov_ledger as PL
from prod_common import Refusal, atomic_write_bytes, atomic_write_json, canonical, sha256_bytes
from prov_envelope import check_genesis, verify_pair


def ledger_view(spec) -> tuple[dict, list]:
    st, entries, _torn, relation = L.Ledger.read_and_relate(L.Paths(spec.root))
    if relation != "CONTINUOUS":
        raise Refusal("LEDGER_LINKAGE", f"ledger relation is {relation}; a supervisor must repair it before an audit")
    L.validate_state(st, spec)
    return st, entries


def audit(spec, authz) -> dict:
    st, entries = ledger_view(spec)
    check_genesis(st, entries, authz)
    root = Path(spec.root)
    issues: dict = defaultdict(list)
    pairs = {}
    sealed = {a["cell"]: aid for aid, a in st["attempts"].items() if a["status"] == "SEALED"}
    for cell, aid in sorted(sealed.items()):
        a = st["attempts"][aid]
        if not a.get("provenance"):
            issues["A_sealed_without_bound_envelope"].append(cell)
            continue
        try:
            pairs[cell] = verify_pair(spec=spec, authz=authz, st=st, entries=entries, record_path=root / a["record"],
                                      envelope_path=root / a["provenance"]["envelope"])
        except Refusal as r:
            issues["B_pair_refused"].append([cell, r.code, r.detail[:200]])
    bound = {a["provenance"]["envelope"] for a in st["attempts"].values() if a.get("provenance")}
    pdir = root / "provenance"
    files = sorted(str(x.relative_to(root)) for x in pdir.rglob("*") if x.is_file()) if pdir.exists() else []
    stray = [f for f in files if f not in bound]
    if stray:
        issues["C_unbound_envelope_files"].extend(stray)
    for fn in (L.verify_sealed_evidence, PL.verify_bound_envelopes):
        try:
            fn(spec, st)
        except Refusal as r:
            issues["C_evidence"].append(f"{r.code}: {r.detail}")
    open_attempts = sorted(aid for aid, a in st["attempts"].items() if a["status"] in L.OPEN)
    unsettled = sorted(r for r, x in st["supervisor_runs"].items() if not x["settled"])
    if open_attempts:
        issues["D_open_attempts"].extend(open_attempts)
    if unsettled:
        issues["D_unsettled_supervisor_runs"].extend(unsettled)
    if st["halt"] is not None:
        issues["D_halt"].append(st["halt"])
    domain = set(spec.cell_indices)
    return {"schema": S.AUDIT_SCHEMA, "mode": spec.mode, "result_agnostic": True, "obligation_statuses_read": False,
            "production_checkpoint_sha256": spec.checkpoint_sha256, "authorization": authz.block,
            "composite_rule": S.COMPOSITE_RULE, "ledger_state_sha256": L.state_sha256(st),
            "genesis_entry_sha256": entries[0]["entry_sha256"], "disposition": st["disposition"],
            "A_completeness": {"domain": len(domain), "sealed": len(sealed), "verified_pairs": len(pairs),
                               "complete": set(pairs) == domain},
            "pairs": {str(c): v for c, v in sorted(pairs.items())}, "issues": dict(issues),
            "INTEGRITY_READY_FOR_ADJUDICATION": set(pairs) == domain and not issues and st["disposition"] == "COMPLETE"}


def export_pairs(led, authz, out_dir) -> dict:
    """Copy every VERIFIED pair; the K4 records directory holds records only for verified pairs."""
    spec, st, out = led.spec, led.state, Path(out_dir)
    if out.exists() and any(out.iterdir()):
        raise Refusal("EXPORT_REFUSED", f"{out} is not empty")
    rep = audit(spec, authz)
    if rep["issues"].get("A_sealed_without_bound_envelope") or rep["issues"].get("B_pair_refused") \
            or rep["issues"].get("D_open_attempts") or rep["issues"].get("C_evidence"):
        raise Refusal("EXPORT_REFUSED", f"not every sealed cell is a verified pair: {sorted(rep['issues'])}")
    files = {}

    def put(rel: str, data: bytes) -> None:
        atomic_write_bytes(out / rel, data)
        files[rel] = sha256_bytes(data)

    root = Path(spec.root)
    put("ledger.json", led.p.ledger.read_bytes())
    put("journal.jsonl", led.p.journal.read_bytes())
    put("RUN_AUTHORIZATION.json", authz.auth_bytes)
    put("COUNTERSIGNATURE.json", authz.cs_bytes)
    for cell, pair in rep["pairs"].items():
        a = st["attempts"][pair["attempt"]]
        rec = (root / a["record"]).read_bytes()
        put(a["record"], rec)
        put(a["provenance"]["envelope"], (root / a["provenance"]["envelope"]).read_bytes())
        put(f"k4_records/aux5_CUSUM_{cell}_256.json", rec)
    manifest = {"schema": S.PAIR_EXPORT_SCHEMA, "mode": spec.mode, "production_checkpoint_sha256": spec.checkpoint_sha256,
                "authorization": authz.block, "composite_rule": S.COMPOSITE_RULE,
                "ledger_state_sha256": rep["ledger_state_sha256"], "integrity_audit_sha256": sha256_bytes(canonical(rep)),
                "pairs": rep["pairs"], "files": files, "k4_records_dir": "k4_records",
                "k4_records_rule": "a record appears in k4_records only if its (record, envelope) pair verified"}
    manifest["export_sha256"] = sha256_bytes(canonical(manifest))
    atomic_write_json(out / "PAIR_EXPORT_MANIFEST.json", manifest)
    return manifest


def build_k4_attestation(spec, authz, rep: dict) -> dict:
    if rep.get("schema") != S.AUDIT_SCHEMA or not rep.get("INTEGRITY_READY_FOR_ADJUDICATION"):
        raise Refusal("ATTESTATION_REFUSED", "the integrity audit is not ready: every cell must be a verified "
                                             "(record, envelope) pair of a COMPLETE, settled ledger")
    if sorted(int(c) for c in rep["pairs"]) != sorted(spec.cell_indices):
        raise Refusal("ATTESTATION_REFUSED", "verified pairs differ from the frozen cell universe")
    return {"schema": S.K4_ATTESTATION_SCHEMA, "mode": spec.mode, "cells_verified": len(rep["pairs"]),
            "all_scientific_hashes_verified": True, "k4_input_structure_verified": True, "k4_values_evaluated": False,
            "producer_identity_hash": spec.identity["producer_identity_hash"],
            "producer_checkpoint_sha256": spec.checkpoint_sha256,
            "production_provenance": {"composite_rule": S.COMPOSITE_RULE, "envelope_schema": S.ENVELOPE_SCHEMA,
                                      "pairs_verified": len(rep["pairs"]), "authorization": authz.block,
                                      "integrity_audit_sha256": sha256_bytes(canonical(rep)),
                                      "ledger_state_sha256": rep["ledger_state_sha256"],
                                      "genesis_entry_sha256": rep["genesis_entry_sha256"],
                                      "pairs": rep["pairs"],
                                      "recomputation": "an adjudicator re-runs prov_integrity.audit on the ledger and "
                                                       "requires this attestation to recompute exactly"}}


def verify_k4_attestation(att: dict, spec, authz) -> None:
    """Adjudication helper: the attestation must equal the one recomputed from the live ledger."""
    if canonical(att) != canonical(build_k4_attestation(spec, authz, audit(spec, authz))):
        raise Refusal("ATTESTATION_REFUSED", "the attestation does not recompute from the ledger and its pairs")
