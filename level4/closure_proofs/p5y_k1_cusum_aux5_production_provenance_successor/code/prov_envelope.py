"""The per-record production provenance envelope and the composite (record + envelope) verifier. NON-CERTIFYING.

An envelope is fully DERIVED: every field is recomputed from the sealed record bytes, the ledger state, the ledger's
hash-chained journal, the verified authorization, and the frozen specification. `verify_pair` rebuilds it and requires
byte-for-byte section equality, so an envelope cannot be edited, swapped to another cell, replayed from another
run/ledger/checkpoint, or attached to different scientific bytes without a named refusal.
"""
from __future__ import annotations

import json
from pathlib import Path

import prov_schema as S
import prod_cells
import prod_ledger as L
from prod_common import Refusal, canonical, sha256_bytes
from prod_sealer import RECORD_SCHEMA, verify_record


def envelope_rel(aid: str, cell: int) -> str:
    return f"provenance/{aid}/CUSUM_{cell:04d}.envelope.json"


def certificate_digest(rec: dict) -> str:
    certs = rec.get("certificates") or {}
    return sha256_bytes(canonical({uid: c.get("certificate_hash") for uid, c in sorted(certs.items())}))


def check_genesis(st: dict, entries: list, authz) -> None:
    """The ledger must have been BORN under this authorization: state block and journal entry 0 both name it."""
    if st.get("production_authorization") != authz.block:
        raise Refusal("NO_PRE_RESULT_AUTHORIZATION", "the ledger state is not bound to this pre-result run authorization")
    if (not entries or entries[0].get("seq") != 0 or entries[0].get("event") != "GENESIS"
            or (entries[0].get("detail") or {}).get("production_authorization") != authz.block):
        raise Refusal("NO_PRE_RESULT_AUTHORIZATION", "the ledger GENESIS entry does not name this authorization; the "
                                                     "ledger was not created under a pre-result authorization")


def ledger_linkage(entries: list, st: dict, aid: str) -> dict:
    a = st["attempts"][aid]
    cell = a["cell"]
    mine = sorted(x for x, y in st["attempts"].items() if y["cell"] == cell)
    reserved = [e for e in entries if e["event"] == "RESERVED" and (e.get("detail") or {}).get("cell") == cell]
    running = [e for e in entries if e["event"] == "RUNNING" and (e.get("detail") or {}).get("attempt") == aid]
    sealed = [e for e in entries if e["event"] in S.SEAL_EVENTS and (e.get("detail") or {}).get("attempt") == aid]
    if len(reserved) != len(mine) or len(running) != 1 or len(sealed) != 1:
        raise Refusal("LEDGER_LINKAGE", f"attempt {aid}: {len(reserved)} reservations for {len(mine)} attempts, "
                                        f"{len(running)} start entries, {len(sealed)} seal entries")
    r = reserved[mine.index(aid)]
    if not (0 < r["seq"] < running[0]["seq"] < sealed[0]["seq"]):
        raise Refusal("LEDGER_LINKAGE", f"attempt {aid}: reservation, start and seal are out of order")

    def ent(e):
        return {"seq": e["seq"], "event": e["event"], "entry_sha256": e["entry_sha256"], "t_wall": e["t_wall"]}
    return {"genesis_entry_sha256": entries[0]["entry_sha256"], "reservation": ent(r), "running": ent(running[0]),
            "seal": ent(sealed[0])}


def build_envelope(*, spec, authz, st: dict, entries: list, aid: str, record_bytes: bytes) -> dict:
    a = st["attempts"].get(aid)
    if a is None or a["status"] != "SEALED":
        raise Refusal("LEDGER_LINKAGE", f"attempt {aid} is not a SEALED attempt of this ledger")
    cell = a["cell"]
    rec = json.loads(record_bytes)
    rsha = sha256_bytes(record_bytes)
    geo = spec.cells[cell]
    env = {
        "schema": S.ENVELOPE_SCHEMA, "kind": S.ENVELOPE_KIND, "task_kind": "SCIENCE", "synthetic": spec.synthetic,
        "mode": spec.mode, "composite_rule": S.COMPOSITE_RULE, "record_flag_semantics": S.FLAG_SEMANTICS,
        "cell": {"detector": "CUSUM", "cell_index": cell, "geometry": geo, "geometry_row_sha256": sha256_bytes(canonical(geo)),
                 "cells_table_sha256": prod_cells.CELLS_SHA256, "m_values": list(prod_cells.M_VALUES)},
        "scientific_record": {"path": a["record"], "sha256": rsha, "record_schema": RECORD_SCHEMA,
                              "precision_bits": spec.precision_bits,
                              "scientific_content_hash": rec.get("scientific_content_hash"),
                              "auxiliary_evidence_hash": rec.get("auxiliary_evidence_hash"),
                              "certificate_digest": certificate_digest(rec),
                              "certificate_count": len(rec.get("certificates") or {}),
                              "certifier_constant_flags_observed": {k: rec.get(k, "<absent>") for k in S.CERTIFIER_CONSTANT_FLAGS}},
        "producer": {k: spec.identity[k] for k in S.IDENTITY_KEYS},
        "checkpoint": {"production_checkpoint_sha256": spec.checkpoint_sha256,
                       "predecessor_checkpoint_sha256": authz.auth["predecessor_checkpoint"]["checkpoint_sha256"],
                       "predecessor_status": authz.auth["predecessor_checkpoint"]["status"]},
        "authorization": {**authz.block, "executor_hash": authz.auth["executor_sources"]["EXECUTOR_HASH"]},
        "ledger": {"ledger_id": authz.block["ledger_id"], "attempt_id": aid, "supervisor_run_id": a["run_id"],
                   **ledger_linkage(entries, st, aid)},
        "host_runtime": {"host_name": authz.auth["host"].get("host_name"),
                         "machine_id_sha256": authz.auth["host"].get("machine_id_sha256"),
                         "runtime_contract_hash": spec.identity["runtime_contract_hash"], "boot_id": a["boot_id"],
                         "core": a["core"], "pid": a["pid"]},
        "cpu_accounting": {"charge_usec": a["charge_usec"], "charge_evidence": a["charge_evidence"], "bucket": "science",
                           "reference": f"ledger attempts[{aid}].charge_usec, fixed by the seal entry"},
        "qualification": {"is_qualification_record": False,
                          "record_sha256_in_qualification_set": rsha in spec.qualification_record_sha256,
                          "qualification_record_sha256": sorted(spec.qualification_record_sha256)},
    }
    env["binding_sha256"] = sha256_bytes(canonical(env))
    return env


def verify_pair(*, spec, authz, st: dict, entries: list, record_path, envelope_path, require_bound: bool = True) -> dict:
    """THE composite production verifier. Returns the verified pair identity or raises a named Refusal."""
    record_path, envelope_path = Path(record_path), Path(envelope_path)
    if not record_path.exists():
        raise Refusal("PAIR_INCOMPLETE", f"scientific record {record_path.name} is absent: an envelope alone is not a "
                                         "production result")
    if not envelope_path.exists():
        raise Refusal("PAIR_INCOMPLETE", f"provenance envelope for {record_path.name} is absent: a scientific record "
                                         "alone is not a production result")
    raw_env = envelope_path.read_bytes()
    try:
        env = json.loads(raw_env)
    except ValueError as exc:
        raise Refusal("ENVELOPE_UNPARSEABLE", str(exc)[:200]) from exc
    if not isinstance(env, dict) or env.get("schema") != S.ENVELOPE_SCHEMA or env.get("kind") != S.ENVELOPE_KIND:
        raise Refusal("ENVELOPE_SCHEMA", "not a production provenance envelope")
    body = {k: v for k, v in env.items() if k != "binding_sha256"}
    if env.get("binding_sha256") != sha256_bytes(canonical(body)):
        raise Refusal("ENVELOPE_BINDING", "binding_sha256 does not recompute: the envelope was edited")
    if env.get("task_kind") != "SCIENCE" or env.get("synthetic") is not spec.synthetic or env.get("mode") != spec.mode:
        raise Refusal("ENVELOPE_KIND", "task kind / synthetic / mode does not match this campaign")
    L.validate_state(st, spec)
    check_genesis(st, entries, authz)
    raw_rec = record_path.read_bytes()
    rsha = sha256_bytes(raw_rec)
    if rsha in spec.qualification_record_sha256:
        raise Refusal("QUALIFICATION_RECORD_REUSE", "a qualification record never becomes a production result")
    aid = (env.get("ledger") or {}).get("attempt_id")
    a = st["attempts"].get(aid)
    if a is None:
        raise Refusal("LEDGER_LINKAGE", f"attempt {aid!r} is not in this ledger")
    cell = a["cell"]
    if a["status"] != "SEALED" or st["cells"][str(cell)]["attempt"] != aid:
        raise Refusal("LEDGER_LINKAGE", f"attempt {aid} is {a['status']}, not cell {cell}'s single sealed attempt")
    if rsha != a["seal"]["record_sha256"]:
        raise Refusal("RECORD_MISMATCH", "the scientific record bytes are not the bytes sealed for this attempt")
    facts = verify_record(record_path, cell=cell, spec=spec)
    rec = json.loads(raw_rec)
    for k, v in S.CERTIFIER_CONSTANT_FLAGS.items():
        if k not in rec or rec[k] is not v:
            raise Refusal("RECORD_FLAGS", f"{k}={rec.get(k, '<absent>')!r} is not the frozen certifier constant {v!r}")
    expected = build_envelope(spec=spec, authz=authz, st=st, entries=entries, aid=aid, record_bytes=raw_rec)
    for section, code in S.SECTION_CODES:
        if env.get(section) != expected[section]:
            raise Refusal(code, f"envelope section {section!r} does not recompute from the record, ledger and authorization")
    if canonical(env) != canonical(expected):
        raise Refusal("ENVELOPE_MISMATCH", "envelope does not recompute exactly")
    esha = sha256_bytes(raw_env)
    if require_bound:
        prov = a.get("provenance") or {}
        if prov.get("envelope_sha256") != esha or prov.get("envelope") != envelope_rel(aid, cell):
            raise Refusal("ENVELOPE_NOT_BOUND_TO_LEDGER", f"cell {cell}: this envelope is not the one the ledger bound")
    return {"cell": cell, "attempt": aid, "record_sha256": rsha, "envelope_sha256": esha,
            "scientific_content_hash": facts["scientific_content_hash"]}
