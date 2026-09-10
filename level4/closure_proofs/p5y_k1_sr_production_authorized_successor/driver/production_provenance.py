"""The genuine-vs-synthetic provenance firewall for P5Y K1 SR production.

THE GAP THIS CLOSES
    The frozen record schema (multihost.CELL_RECORD_REQUIRED_FIELDS) makes a
    genuine science record and a Phase-8 synthetic stand-in STRUCTURALLY
    IDENTICAL: both carry a well-formed 64-hex `scientific_content_hash`, so
    `validate_record` admits either and `assemble_global_ledger` will happily
    assemble a wholly synthetic 316-cell / 8849-obligation campaign. That was
    acceptable while `production_enabled=false` closed every result-bearing
    path. It is NOT acceptable once production is authorised.

WHAT A GENUINE RECORD MUST CARRY
    An additive `production_provenance` block that a synthetic path cannot
    produce. Nothing frozen is modified: this is a strictly ADDITIVE field on
    top of the frozen record, and the frozen validators still run first.

THE FOUR INDEPENDENT LAYERS
    1. TEMPORAL   `production_authorization_hash` must equal the live production
                  authorization. Every Phase-8 synthetic record was produced
                  BEFORE that authorization existed, so none can carry it. This
                  is the load-bearing layer and it is not forgeable after the
                  fact by anything that already exists.
    2. CHECKPOINT The production authorization binds a NEW checkpoint identity,
                  so the FROZEN `validate_record` -- unmodified -- already
                  rejects any record bound to the predecessor checkpoint. Phase-8
                  records carry the predecessor checkpoint.
    3. KIND       `task_kind == "SCIENCE"` and `synthetic is False`. The
                  synthetic path stamps SYNTHETIC_SPIN / synthetic=True, and the
                  known Phase-8 stand-in form '%064x' % cell_id is rejected
                  outright as a scientific content hash.
    4. BINDING    A canonical digest over the whole provenance tuple, so a record
                  cannot be part-copied or field-swapped between cells or hosts.

HONEST LIMIT
    `binding` is a canonical SHA-256 digest, not an unforgeable signature. It
    defends against misfiling, replay across cells/hosts, truncation and
    accidental admission of control artifacts -- which is the stated threat.
    It does not defend against an attacker who already has write access to the
    production ledger; that is out of scope for this campaign and is stated
    rather than papered over.
"""
from __future__ import annotations

import hashlib
import json

PROVENANCE_SCHEMA = "rebaseguard.p5y.k1.sr.production.provenance.v1"
GENUINE_TASK_KIND = "SCIENCE"
SYNTHETIC_TASK_KINDS = ("SYNTHETIC_SPIN", "STRUCTURAL_IMPORT")
PROVENANCE_FIELD = "production_provenance"


class ProvenanceRefusal(RuntimeError):
    """A record was refused by the production provenance firewall. Fail closed."""


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def _hex64(v) -> bool:
    return (isinstance(v, str) and len(v) == 64
            and all(c in "0123456789abcdef" for c in v.lower()))


def synthetic_stand_in(cell_id: int) -> str:
    """The exact stand-in the frozen synthetic scheduler writes. Never genuine."""
    return "%064x" % cell_id


def binding_digest(*, cell_id, role, producer_commit, checkpoint_sha256,
                   runtime_contract_hash, scientific_content_hash,
                   production_authorization_hash, scientific_adapter_hash,
                   certificate_digest, task_kind, synthetic) -> str:
    return hashlib.sha256(canonical({
        "schema": PROVENANCE_SCHEMA, "cell_id": cell_id, "role": role,
        "producer_commit": producer_commit, "checkpoint_sha256": checkpoint_sha256,
        "runtime_contract_hash": runtime_contract_hash,
        "scientific_content_hash": scientific_content_hash,
        "production_authorization_hash": production_authorization_hash,
        "scientific_adapter_hash": scientific_adapter_hash,
        "certificate_digest": certificate_digest,
        "task_kind": task_kind, "synthetic": synthetic})).hexdigest()


def seal(record: dict, *, production_authorization_hash: str,
         scientific_adapter_hash: str, certificate_digest: str) -> dict:
    """Stamp a GENUINE production record. Called only on the SCIENCE path."""
    for name, v in (("production_authorization_hash", production_authorization_hash),
                    ("scientific_adapter_hash", scientific_adapter_hash),
                    ("certificate_digest", certificate_digest)):
        if not _hex64(v):
            raise ProvenanceRefusal(f"{name} is not a 64-hex digest: {v!r}")
    if certificate_digest == synthetic_stand_in(record["cell_id"]):
        raise ProvenanceRefusal(
            f"certificate_digest for cell {record['cell_id']} is the synthetic stand-in")
    prov = {"schema": PROVENANCE_SCHEMA, "task_kind": GENUINE_TASK_KIND,
            "synthetic": False,
            "production_authorization_hash": production_authorization_hash,
            "scientific_adapter_hash": scientific_adapter_hash,
            "certificate_digest": certificate_digest}
    prov["binding"] = binding_digest(
        cell_id=record["cell_id"], role=record["role"],
        producer_commit=record["producer_commit"],
        checkpoint_sha256=record["checkpoint_sha256"],
        runtime_contract_hash=record["runtime_contract_hash"],
        scientific_content_hash=record["scientific_content_hash"],
        production_authorization_hash=production_authorization_hash,
        scientific_adapter_hash=scientific_adapter_hash,
        certificate_digest=certificate_digest,
        task_kind=GENUINE_TASK_KIND, synthetic=False)
    out = dict(record)
    out[PROVENANCE_FIELD] = prov
    return out


def verify(record: dict, *, production_authorization_hash: str,
           scientific_adapter_hash: str) -> dict:
    """Refuse anything that is not a GENUINE production record. Fail closed."""
    if not isinstance(record, dict):
        raise ProvenanceRefusal("production record is not a mapping")
    cid = record.get("cell_id")
    prov = record.get(PROVENANCE_FIELD)
    if prov is None:
        raise ProvenanceRefusal(
            f"cell {cid!r}: record carries NO production provenance; it is a "
            "control/synthetic artifact and is refused by the production assembler")
    if not isinstance(prov, dict):
        raise ProvenanceRefusal(f"cell {cid!r}: production provenance is not a mapping")
    if prov.get("schema") != PROVENANCE_SCHEMA:
        raise ProvenanceRefusal(f"cell {cid!r}: unknown provenance schema "
                                f"{prov.get('schema')!r}")
    # LAYER 3 -- kind
    if prov.get("task_kind") != GENUINE_TASK_KIND:
        raise ProvenanceRefusal(
            f"cell {cid!r}: task_kind {prov.get('task_kind')!r} is not "
            f"{GENUINE_TASK_KIND}; synthetic work never becomes a production result")
    if prov.get("synthetic") is not False:
        raise ProvenanceRefusal(f"cell {cid!r}: record is marked synthetic")
    sch = record.get("scientific_content_hash")
    if not _hex64(sch):
        raise ProvenanceRefusal(f"cell {cid!r}: malformed scientific_content_hash")
    if isinstance(cid, int) and not isinstance(cid, bool) \
            and sch == synthetic_stand_in(cid):
        raise ProvenanceRefusal(
            f"cell {cid}: scientific_content_hash is the frozen synthetic stand-in "
            f"'%064x' % cell_id; this is a Phase-8 control record")
    # LAYER 1 -- temporal
    if prov.get("production_authorization_hash") != production_authorization_hash:
        raise ProvenanceRefusal(
            f"cell {cid!r}: production_authorization_hash "
            f"{prov.get('production_authorization_hash')!r} != the live production "
            f"authorization {production_authorization_hash}; the record was not "
            "produced under this authorization")
    if prov.get("scientific_adapter_hash") != scientific_adapter_hash:
        raise ProvenanceRefusal(
            f"cell {cid!r}: scientific_adapter_hash is not the authorised adapter")
    cd = prov.get("certificate_digest")
    if not _hex64(cd):
        raise ProvenanceRefusal(f"cell {cid!r}: malformed certificate_digest")
    if isinstance(cid, int) and not isinstance(cid, bool) \
            and cd == synthetic_stand_in(cid):
        raise ProvenanceRefusal(f"cell {cid}: certificate_digest is the synthetic stand-in")
    # LAYER 4 -- binding
    want = binding_digest(
        cell_id=cid, role=record.get("role"),
        producer_commit=record.get("producer_commit"),
        checkpoint_sha256=record.get("checkpoint_sha256"),
        runtime_contract_hash=record.get("runtime_contract_hash"),
        scientific_content_hash=sch,
        production_authorization_hash=prov.get("production_authorization_hash"),
        scientific_adapter_hash=prov.get("scientific_adapter_hash"),
        certificate_digest=cd, task_kind=prov.get("task_kind"),
        synthetic=prov.get("synthetic"))
    if prov.get("binding") != want:
        raise ProvenanceRefusal(
            f"cell {cid!r}: provenance binding does not recompute; the record was "
            "altered, field-swapped or copied from another cell/host")
    return prov
