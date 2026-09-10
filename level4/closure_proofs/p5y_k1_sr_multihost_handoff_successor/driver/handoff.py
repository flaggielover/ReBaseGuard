"""One-way authenticated AWS -> VULTR completion handoff.

The ONLY blocker this module addresses: AWS and Vultr keep separate host-local
ledgers, so Vultr has no authenticated way to learn that AWS finished its 247-cell
shard and to inherit the global accounting state. Without it Vultr always resolves
AWS as the active host and refuses its own 69 cells, making the 316-cell universe
unreachable.

Deliberately NOT introduced: any shared live coordinator, database, lock service,
RPC endpoint or dual-primary scheduler. The handoff is a single signed file that
moves one way, once.

Trust model
    - the Ed25519 private key exists only on AWS and is never committed;
    - the public key FINGERPRINT is frozen in the successor configuration;
    - the signature covers the exact canonical payload bytes;
    - the verifier RECOMPUTES completion and remaining budget from the cell sets
      and the frozen cap. It never trusts a self-asserted boolean such as
      aws_shard_complete, nor a self-asserted remaining_global_cpu_h.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import subprocess
import tempfile
import time
from pathlib import Path

HANDOFF_SCHEMA = "rebaseguard.p5y.k1.sr.multihost.handoff.v1"
TRANSITION_ID = "AWS_TO_VULTR"
TRANSITION_SEQUENCE = 1
SIGNATURE_ALGORITHM = "Ed25519"


class HandoffRefusal(RuntimeError):
    """The handoff was refused. Always fail closed."""


# ------------------------------------------------------------------ canonical
def canonical(payload: dict) -> bytes:
    """Deterministic serialisation. Any byte change invalidates the signature."""
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def payload_hash(payload: dict) -> str:
    return hashlib.sha256(canonical(payload)).hexdigest()


def _atomic_write(path: Path, data: bytes) -> None:
    """temp -> fsync -> rename, so a crash never leaves a partial artefact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dirfd = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


# -------------------------------------------------------------------- crypto
def _openssl(args, **kw):
    return subprocess.run(["openssl"] + args, capture_output=True, **kw)


def public_key_fingerprint(pubkey_pem: Path) -> str:
    """sha256 over the DER SubjectPublicKeyInfo. Stable across PEM whitespace."""
    r = _openssl(["pkey", "-pubin", "-in", str(pubkey_pem), "-outform", "DER"])
    if r.returncode != 0:
        raise HandoffRefusal(f"cannot read public key: {r.stderr.decode()[:200]}")
    return hashlib.sha256(r.stdout).hexdigest()


def sign(payload_bytes: bytes, privkey_pem: Path) -> bytes:
    if not Path(privkey_pem).exists():
        raise HandoffRefusal(
            f"signing key absent at {privkey_pem}; export refused (the private key "
            "exists only on AWS and is never committed)")
    with tempfile.TemporaryDirectory() as d:
        msg = Path(d) / "msg.bin"
        sig = Path(d) / "sig.bin"
        msg.write_bytes(payload_bytes)
        r = _openssl(["pkeyutl", "-sign", "-inkey", str(privkey_pem), "-rawin",
                      "-in", str(msg), "-out", str(sig)])
        if r.returncode != 0:
            raise HandoffRefusal(f"signing failed: {r.stderr.decode()[:200]}")
        return sig.read_bytes()


def verify(payload_bytes: bytes, signature: bytes, pubkey_pem: Path) -> bool:
    if not signature:
        raise HandoffRefusal("handoff carries no signature")
    with tempfile.TemporaryDirectory() as d:
        msg = Path(d) / "msg.bin"
        sig = Path(d) / "sig.bin"
        msg.write_bytes(payload_bytes)
        sig.write_bytes(signature)
        r = _openssl(["pkeyutl", "-verify", "-pubin", "-inkey", str(pubkey_pem),
                      "-rawin", "-in", str(msg), "-sigfile", str(sig)])
    if r.returncode != 0:
        raise HandoffRefusal(
            f"Ed25519 signature verification FAILED: {r.stderr.decode()[:160]}")
    return True


# ------------------------------------------------------- shared identity view
def campaign_identity(auth, ns: Path) -> dict:
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    return {
        "approved_launch_tag": auth["approved_launch_tag"],
        "producer_commit": auth["producer_commit"],
        "protocol_hash": auth["protocol_sha256"],
        "checkpoint_hash": auth["checkpoint_sha256"],
        "launch_authorization_hash": sha(ns / "config/LAUNCH_AUTHORIZATION.json"),
        "shard_hash": auth["shard_manifest_sha256"],
        "scientific_adapter_hash": auth["scientific_adapter_hash"],
        "integrated_source_manifest_hash": auth["integrated_source_manifest_sha256"],
        "global_cpu_cap": auth["global_cpu_cap"],
    }


def _refuse_on(what, fn, *args):
    """Fail CLOSED across an INJECTED trusted-domain gate.

    export_handoff/verify_handoff receive the frozen validators as CALLABLES, so
    the exception type they raise belongs to the caller, not to this boundary: a
    consumer wrapping the import in `except HandoffRefusal` would not catch a
    malformed accounting field, and a foreign exception would escape the handoff
    contract entirely. Any failure of an injected gate -- an explicit refusal, a
    coercion error, or an outright broken gate -- is normalised into
    HandoffRefusal, so a handoff can never be admitted through a gate that did
    not cleanly return. Nothing is swallowed: the original message is preserved
    for diagnosis and the original exception is chained as __cause__.
    """
    try:
        return fn(*args)
    except HandoffRefusal:
        raise
    except Exception as exc:
        raise HandoffRefusal(f"{what} refused by the trusted-domain gate: {exc}") from exc


def _validated_cost(value, what, validate_governed_cost):
    """Route every governed number through the frozen trusted-domain validator."""
    return _refuse_on(what, validate_governed_cost, value, what)


def _gated_cap(gate_global_cap, by_role, overhead):
    """Route the frozen ONE global CPU-h cap gate through the same boundary."""
    return _refuse_on("global CPU-h cap", gate_global_cap, by_role, overhead)


# ------------------------------------------------------------------- EXPORT
def export_handoff(*, auth, ns: Path, owners: dict, budget, approved_head: str,
                   privkey_pem: Path, out_path: Path, validate_governed_cost,
                   gate_global_cap, nonce: str = None) -> dict:
    """AWS side. Refuses unless the AWS shard is genuinely, completely finished."""
    aws_expected = sorted(c for c, r in owners.items() if r == "AWS")
    if len(aws_expected) != auth["hosts"]["AWS"]["cell_count"]:
        raise HandoffRefusal(
            f"AWS shard has {len(aws_expected)} cells != "
            f"{auth['hosts']['AWS']['cell_count']}")

    state = budget.raw_state()
    completed = sorted(int(c) for c in state.get("completed_cells", {}))
    aws_completed = sorted(c for c in completed if owners.get(c) == "AWS")
    foreign = [c for c in completed if owners.get(c) != "AWS"]
    if foreign:
        raise HandoffRefusal(f"AWS ledger contains non-AWS cells: {foreign[:5]}")
    if aws_completed != aws_expected:
        missing = sorted(set(aws_expected) - set(aws_completed))
        extra = sorted(set(aws_completed) - set(aws_expected))
        raise HandoffRefusal(
            f"AWS shard not complete: {len(aws_completed)}/{len(aws_expected)} "
            f"(missing {missing[:5]}, extra {extra[:5]})")
    open_res = state.get("open_reservations", {})
    if open_res:
        raise HandoffRefusal(f"AWS still has {len(open_res)} in-flight reservations")

    finalized = _validated_cost(state.get("committed_cpu_h_by_role", {}).get("AWS", 0.0),
                                "AWS finalized CPU-h", validate_governed_cost)
    cap = _gated_cap(gate_global_cap, {"AWS": finalized}, auth["governed_overhead_cpu_h"])
    remaining = _validated_cost(cap["cap"] - cap["charged_cpu_h"],
                                "remaining global CPU-h", validate_governed_cost)

    ledger_hash = hashlib.sha256(
        canonical({"completed": aws_completed,
                   "committed_cpu_h_by_role": state.get("committed_cpu_h_by_role", {})})
    ).hexdigest()
    result_manifest_hash = hashlib.sha256(canonical(
        {str(c): state["completed_cells"][str(c)].get("scientific_content_hash")
         for c in aws_completed})).hexdigest()

    payload = {
        "schema_version": HANDOFF_SCHEMA,
        "transition_id": TRANSITION_ID,
        "sequence": TRANSITION_SEQUENCE,
        "source_host": "AWS",
        "target_host": "VULTR",
        "approved_launch_head": approved_head,
        **campaign_identity(auth, ns),
        "aws_expected_cell_count": len(aws_expected),
        "aws_expected_cell_ids": aws_expected,
        "aws_completed_cell_count": len(aws_completed),
        "aws_completed_cell_ids": aws_completed,
        "aws_inflight_count": 0,
        "aws_shard_complete": True,          # ADVISORY ONLY: the verifier recomputes
        "aws_finalized_cpu_h": finalized,
        "aws_reserved_inflight_cpu_h": 0.0,
        "remaining_global_cpu_h": remaining,  # ADVISORY ONLY: the verifier recomputes
        "aws_ledger_hash": ledger_hash,
        "aws_result_manifest_hash": result_manifest_hash,
        "created_at": int(time.time()),
        "handoff_nonce": nonce or secrets.token_hex(16),
    }
    payload["handoff_payload_hash"] = payload_hash(
        {k: v for k, v in payload.items() if k != "handoff_payload_hash"})
    body = canonical(payload)
    sig = sign(body, privkey_pem)

    doc = {"payload": payload, "signature_b64":
           __import__("base64").b64encode(sig).decode(),
           "signature_algorithm": SIGNATURE_ALGORITHM}
    out_path = Path(out_path)
    if out_path.exists():                      # idempotent export
        prev = json.loads(out_path.read_text())
        if prev["payload"].get("handoff_payload_hash") == \
                payload["handoff_payload_hash"]:
            return {"status": "IDEMPOTENT_ALREADY_EXPORTED", "document": prev}
        prev_core = {k: v for k, v in prev["payload"].items()
                     if k not in ("created_at", "handoff_nonce", "handoff_payload_hash")}
        new_core = {k: v for k, v in payload.items()
                    if k not in ("created_at", "handoff_nonce", "handoff_payload_hash")}
        if prev_core != new_core:
            raise HandoffRefusal(
                "an INCONSISTENT handoff already exists at this path; refusing to "
                "overwrite a differing transition")
        return {"status": "IDEMPOTENT_ALREADY_EXPORTED", "document": prev}
    _atomic_write(out_path, (json.dumps(doc, indent=1, sort_keys=True) + "\n").encode())
    return {"status": "EXPORTED", "document": doc}


# ------------------------------------------------------------------- IMPORT
def verify_handoff(*, doc: dict, auth, ns: Path, owners: dict, approved_head: str,
                   pubkey_pem: Path, expected_fingerprint: str,
                   validate_governed_cost, gate_global_cap) -> dict:
    """VULTR side. Every gate recomputes; nothing self-asserted is trusted."""
    if not isinstance(doc, dict) or "payload" not in doc:
        raise HandoffRefusal("handoff document is malformed")
    payload = doc["payload"]
    import base64
    sig = base64.b64decode(doc.get("signature_b64") or "")

    fp = public_key_fingerprint(pubkey_pem)
    if fp != expected_fingerprint:
        raise HandoffRefusal(
            f"verification key fingerprint {fp} != frozen {expected_fingerprint}")
    if doc.get("signature_algorithm") != SIGNATURE_ALGORITHM:
        raise HandoffRefusal(f"unexpected signature algorithm "
                             f"{doc.get('signature_algorithm')!r}")
    verify(canonical(payload), sig, pubkey_pem)

    stated = payload.get("handoff_payload_hash")
    recomputed = payload_hash({k: v for k, v in payload.items()
                               if k != "handoff_payload_hash"})
    if stated != recomputed:
        raise HandoffRefusal("handoff_payload_hash does not match the payload")

    if payload.get("schema_version") != HANDOFF_SCHEMA:
        raise HandoffRefusal(f"unknown handoff schema {payload.get('schema_version')!r}")
    if payload.get("transition_id") != TRANSITION_ID:
        raise HandoffRefusal(f"wrong transition {payload.get('transition_id')!r}")
    if payload.get("sequence") != TRANSITION_SEQUENCE:
        raise HandoffRefusal(f"wrong sequence {payload.get('sequence')!r}")
    if payload.get("source_host") != "AWS" or payload.get("target_host") != "VULTR":
        raise HandoffRefusal(
            f"wrong direction {payload.get('source_host')} -> {payload.get('target_host')}")

    if payload.get("approved_launch_head") != approved_head:
        raise HandoffRefusal(
            f"handoff approved_launch_head {payload.get('approved_launch_head')} "
            f"!= {approved_head}")
    ident = campaign_identity(auth, ns)
    for k, want in ident.items():
        if payload.get(k) != want:
            raise HandoffRefusal(f"handoff {k} {payload.get(k)!r} != frozen {want!r}")

    aws_expected = sorted(c for c, r in owners.items() if r == "AWS")
    got_expected = payload.get("aws_expected_cell_ids")
    got_completed = payload.get("aws_completed_cell_ids")
    for name, ids in (("expected", got_expected), ("completed", got_completed)):
        if not isinstance(ids, list) or any(
                isinstance(c, bool) or not isinstance(c, int) for c in ids):
            raise HandoffRefusal(f"aws_{name}_cell_ids is not a list of ints")
        if len(set(ids)) != len(ids):
            raise HandoffRefusal(f"aws_{name}_cell_ids contains duplicates")
    if sorted(got_expected) != aws_expected:
        raise HandoffRefusal("aws_expected_cell_ids != the frozen AWS shard")
    foreign = [c for c in got_completed if owners.get(c) != "AWS"]
    if foreign:
        raise HandoffRefusal(f"completed list contains non-AWS cells: {foreign[:5]}")
    if sorted(got_completed) != aws_expected:
        missing = sorted(set(aws_expected) - set(got_completed))
        extra = sorted(set(got_completed) - set(aws_expected))
        raise HandoffRefusal(
            f"AWS completion RECOMPUTED as incomplete: "
            f"{len(got_completed)}/{len(aws_expected)} "
            f"(missing {missing[:5]}, extra {extra[:5]})")
    if payload.get("aws_expected_cell_count") != len(aws_expected) or \
            payload.get("aws_completed_cell_count") != len(aws_expected):
        raise HandoffRefusal("declared cell counts disagree with the cell sets")

    if payload.get("aws_inflight_count") != 0:
        raise HandoffRefusal(f"aws_inflight_count {payload.get('aws_inflight_count')!r} != 0")
    reserved = _validated_cost(payload.get("aws_reserved_inflight_cpu_h"),
                               "aws_reserved_inflight_cpu_h", validate_governed_cost)
    if reserved != 0.0:
        raise HandoffRefusal(f"reserved in-flight CPU-h {reserved} != 0")
    finalized = _validated_cost(payload.get("aws_finalized_cpu_h"),
                                "aws_finalized_cpu_h", validate_governed_cost)
    cap_now = _gated_cap(gate_global_cap, {"AWS": finalized}, auth["governed_overhead_cpu_h"])
    if cap_now["charged_cpu_h"] > cap_now["cap"]:
        raise HandoffRefusal("imported AWS cost already exceeds the global cap")
    remaining = cap_now["cap"] - cap_now["charged_cpu_h"]

    return {"verified": True, "payload": payload,
            "aws_completed_cell_ids": sorted(got_completed),
            "aws_finalized_cpu_h": finalized,
            "recomputed_remaining_global_cpu_h": remaining,
            "handoff_payload_hash": stated,
            "public_key_fingerprint": fp}


def consumed_record_path(ns: Path) -> Path:
    return Path(ns) / "evidence/handoff_consumed.json"


def apply_handoff(*, verified: dict, budget, ns: Path) -> dict:
    """Atomically consume the transition exactly once."""
    rec_path = consumed_record_path(ns)
    ph = verified["handoff_payload_hash"]
    if rec_path.exists():
        prev = json.loads(rec_path.read_text())
        if prev.get("handoff_payload_hash") == ph:
            return {"status": "IDEMPOTENT_ALREADY_APPLIED", "record": prev}
        raise HandoffRefusal(
            "a DIFFERENT transition with this sequence has already been consumed; "
            "replay or conflicting handoff refused")
    applied = budget.import_remote_completion(
        role="AWS", cell_ids=verified["aws_completed_cell_ids"],
        finalized_cpu_h=verified["aws_finalized_cpu_h"], payload_hash=ph)
    record = {"schema": HANDOFF_SCHEMA + ".consumed",
              "transition_id": TRANSITION_ID, "sequence": TRANSITION_SEQUENCE,
              "handoff_payload_hash": ph,
              "remote_cells": len(verified["aws_completed_cell_ids"]),
              "inherited_cpu_h": verified["aws_finalized_cpu_h"],
              "consumed_at": int(time.time())}
    _atomic_write(rec_path, (json.dumps(record, indent=1, sort_keys=True) + "\n").encode())
    return {"status": "APPLIED", "record": record, "budget": applied}
