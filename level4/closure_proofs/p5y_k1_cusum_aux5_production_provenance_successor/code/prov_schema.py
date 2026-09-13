"""Frozen identifiers and normative texts of the CUSUM Aux5 production-provenance successor. NON-CERTIFYING.

Importing this module puts the predecessor lifecycle modules (p5y_k1_cusum_aux5_production_checkpoint/code) on
sys.path AFTER this namespace's own code directory. They are reused in place, byte-identical and hash-bound; no
predecessor file is edited.
"""
from __future__ import annotations

import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
PRED_NS = NS.parent / "p5y_k1_cusum_aux5_production_checkpoint"
for _p in (str(NS / "code"), str(PRED_NS / "code")):
    if _p not in sys.path:
        sys.path.append(_p)

CHECKPOINT_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.production-provenance-checkpoint.v1"
ENVELOPE_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.production-provenance-envelope.v1"
ENVELOPE_KIND = "CUSUM_AUX5_PRODUCTION_PROVENANCE_ENVELOPE"
AUTH_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.production-run-authorization.v1"
COUNTERSIGN_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.production-countersignature.v1"
LEDGER_ID_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.ledger-identity.v1"
AUDIT_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.production-integrity-audit.v1"
PAIR_EXPORT_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.production-pair-export.v1"
FREEZE_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.production-provenance-freeze-record.v1"
ACCEPTANCE_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.production-provenance-acceptance.v1"
PREFLIGHT_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.production-provenance-preflight.v1"
K4_ATTESTATION_SCHEMA = "rebaseguard.p5y.k1.cusum-production.integrity-attestation.v1"

AUTH_STATUS = "PRE_RESULT_AUTHORIZATION_AWAITING_INDEPENDENT_COUNTERSIGNATURE"
APPROVED = "APPROVED_FOR_PRODUCTION_LAUNCH"
PROVENANCE_EVENT = "PROVENANCE_BOUND"
SEAL_EVENTS = ("SEALED", "RECONCILED_SEALED")

PREDECESSOR = {
    "namespace": "level4/closure_proofs/p5y_k1_cusum_aux5_production_checkpoint",
    "checkpoint_sha256": "4026f296bd7b32bea24a0f73422f4fc8df1f0c1d04aea952ee7ed0f5313c3c5c",
    "freeze_commit": "532c880ee8edacf322f8c57660b0a7e71e729c40",
    "readiness_record_commit": "264e9d37a3af961ede7da32073db1787d6568087",
    "status": "BLOCKED_ON_PRODUCTION_STATUS_SEMANTICS",
    "runtime_root": "/root/work/postk1-runs/cusum-aux5-production",
}
FENCE_MARKER = "BLOCKED_ON_PRODUCTION_STATUS_SEMANTICS"

IDENTITY_KEYS = ("producer_manifest_hash", "runtime_contract_hash", "producer_identity_hash",
                 "implementation_hash_kind", "producer_manifest_path", "producer_manifest_schema",
                 "producer_manifest_version", "campaign")

# Emitted by the frozen Aux5 certifier inside the scientific hash; identical in qualification and production.
CERTIFIER_CONSTANT_FLAGS = {"production_run": False, "result_bearing": False,
                            "scientific_certification_of_full_cover": False}

COMPOSITE_RULE = (
    "A CUSUM Aux5 production result is the PAIR (scientific record, valid production provenance envelope). Neither "
    "object alone is production-authorized, result-bearing or disposition-bearing. An envelope is valid only if it "
    "recomputes exactly from: the sealed record bytes; a production ledger whose GENESIS names the pre-result run "
    "authorization and its independent countersignature; that ledger's RESERVED -> RUNNING -> SEAL journal entries for "
    "the attempt; the frozen producer, checkpoint, cell geometry and host; and the ledger's PROVENANCE_BOUND entry "
    "naming the envelope sha256.")

FLAG_SEMANTICS = (
    "production_run=false, result_bearing=false and scientific_certification_of_full_cover=false inside the scientific "
    "record are constants of the frozen, qualified Aux5 certifier: identical in qualification and production, inside "
    "the scientific hash, never rewritten. They state that a scientific record BY ITSELF authorizes nothing, which the "
    "composite rule also requires. They are not the production disposition and are never read as one. The PS1 "
    "precedent is the same: its T3/T4/T5 science artifacts carry no production flag and acquire production status "
    "only through a sealed production cell record whose production_provenance binds the pre-result launch "
    "authorization, and that authorization object itself declares result_bearing=false.")

# envelope section -> refusal code when the section does not recompute (checked in this order)
SECTION_CODES = (
    ("producer", "PRODUCER_MISMATCH"), ("checkpoint", "CHECKPOINT_MISMATCH"),
    ("authorization", "AUTHORIZATION_MISMATCH"), ("cell", "CELL_MISMATCH"),
    ("scientific_record", "RECORD_MISMATCH"), ("ledger", "LEDGER_LINKAGE"),
    ("host_runtime", "HOST_RUNTIME_MISMATCH"), ("cpu_accounting", "CPU_ACCOUNTING_MISMATCH"),
    ("qualification", "QUALIFICATION_DISTINCTION_MISMATCH"),
)

ENVELOPE_FIELDS = {
    "schema": "ENVELOPE_SCHEMA", "kind": "ENVELOPE_KIND", "task_kind": "SCIENCE", "synthetic": "bool (False in production)",
    "mode": "PRODUCTION | SYNTHETIC", "composite_rule": "COMPOSITE_RULE", "record_flag_semantics": "FLAG_SEMANTICS",
    "cell": ["detector", "cell_index", "geometry {index,e0,rho,left,right,C_upper}", "geometry_row_sha256",
             "cells_table_sha256", "m_values"],
    "scientific_record": ["path", "sha256", "record_schema", "precision_bits", "scientific_content_hash",
                          "auxiliary_evidence_hash", "certificate_digest", "certificate_count",
                          "certifier_constant_flags_observed"],
    "producer": list(IDENTITY_KEYS),
    "checkpoint": ["production_checkpoint_sha256", "predecessor_checkpoint_sha256", "predecessor_status"],
    "authorization": ["authorization_sha256", "authorization_id", "production_run_id", "ledger_id",
                      "countersignature_sha256", "executor_hash"],
    "ledger": ["ledger_id", "attempt_id", "supervisor_run_id", "genesis_entry_sha256",
               "reservation {seq,event,entry_sha256,t_wall}", "running {..}", "seal {..}"],
    "host_runtime": ["host_name", "machine_id_sha256", "runtime_contract_hash", "boot_id", "core", "pid"],
    "cpu_accounting": ["charge_usec", "charge_evidence", "bucket", "reference"],
    "qualification": ["is_qualification_record", "record_sha256_in_qualification_set", "qualification_record_sha256"],
    "binding_sha256": "sha256(canonical(envelope without binding_sha256))",
}


def envelope_schema_document() -> dict:
    return {"schema": "rebaseguard.p5y.k1.cusum-aux5.envelope-schema-document.v1", "envelope_schema": ENVELOPE_SCHEMA,
            "envelope_kind": ENVELOPE_KIND, "fields": ENVELOPE_FIELDS, "section_refusal_codes": dict(SECTION_CODES),
            "composite_rule": COMPOSITE_RULE, "record_flag_semantics": FLAG_SEMANTICS,
            "certifier_constant_flags": CERTIFIER_CONSTANT_FLAGS, "binding_event": PROVENANCE_EVENT,
            "seal_events": list(SEAL_EVENTS),
            "object_sha256": "the envelope FILE sha256 is bound outside the envelope: in the ledger attempt's provenance "
                             "(PROVENANCE_BOUND journal entry), the integrity audit and the K4 attestation",
            "immutability": "an envelope is read-only once bound; a second envelope for a bound attempt or cell is "
                            "refused (DUPLICATE_ENVELOPE); an unbound crash residue is regenerated from the ledger",
            "path": "provenance/<attempt id>/CUSUM_<cell:04d>.envelope.json under the production runtime root"}
