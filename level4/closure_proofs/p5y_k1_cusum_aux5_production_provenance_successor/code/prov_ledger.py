"""Authorization-bound ledger genesis and envelope binding, on top of the unchanged predecessor ledger. NON-CERTIFYING.

  genesis        refused without a verified authorization + countersignature; the state carries
                 `production_authorization` and journal entry 0 carries the same block
  seal           unchanged predecessor semantics (record verified, read-only, SEALED entry)
  envelope       immediately after the seal: derive the envelope, write it read-only, verify the pair, then one
                 PROVENANCE_BOUND transition records the envelope path and sha256 on the attempt. A crash between
                 SEALED and PROVENANCE_BOUND leaves a sealed-but-unbound attempt, which is NOT a production result; the
                 next supervisor derives the same envelope and binds it before any admission.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import prov_schema as S
import prod_ledger as L
from prod_common import Refusal, atomic_write_bytes, atomic_write_json, fsync_dir, sha256_bytes, sha256_file
from prov_envelope import build_envelope, envelope_rel, verify_pair


class ProvenanceLedger(L.Ledger):
    def __init__(self, spec, lock, run_id=None, *, authz):
        super().__init__(spec, lock, run_id=run_id)
        if authz is None:
            raise Refusal("NO_PRE_RESULT_AUTHORIZATION", "a production ledger is never opened without an authorization")
        self.authz = authz

    def _genesis(self) -> None:
        """The predecessor genesis, plus the authorization block in the state AND in journal entry 0."""
        spec, p = self.spec, self.p
        extra = sorted(x.name for x in p.root.iterdir() if x.name not in L.PRE_GENESIS_FILES) if p.root.exists() else []
        if extra:
            raise Refusal("STALE_INCOMPATIBLE_RUN_STATE", f"runtime root holds {extra[:6]} but no ledger")
        block = dict(self.authz.block)
        st = {"schema": L.LEDGER_SCHEMA, "mode": spec.mode, "checkpoint_sha256": spec.checkpoint_sha256,
              "campaign_id": spec.campaign_id,
              "cap": {"cap_usec": spec.cap_usec, "reservation_usec": spec.reservation_usec, "invariant": L.INVARIANT},
              "cells": {str(i): {"status": "PENDING", "attempt": None, "infra_tears": 0} for i in spec.cell_indices},
              "attempts": {}, "supervisor_runs": {}, "overhead_charges": {},
              "committed_usec": dict.fromkeys(L.BUCKETS, 0),
              "accounting_exclusions": spec.accounting_exclusions,
              "first_admission_wall": None, "halt": None, "disposition": "OPEN", "budget_exhaustion": None,
              "production_authorization": block,
              "seq": 0, "prev_state_sha256": None,
              "last_event": {"event": "GENESIS", "detail": {"production_authorization": block}, "t_wall": time.time()}}
        L.validate_state(st, spec)
        atomic_write_json(p.ledger, st)
        self.state = st
        self._last = self._append_journal(None, st, "GENESIS", {"checkpoint_sha256": spec.checkpoint_sha256,
                                                                 "production_authorization": block})


def op_bind_provenance(st: dict, aid: str, rel: str, sha: str) -> None:
    a = st["attempts"][aid]
    if a["status"] != "SEALED":
        raise Refusal("LEDGER_LINKAGE", f"attempt {aid} is {a['status']}; only a sealed attempt binds an envelope")
    if a.get("provenance") is not None:
        raise Refusal("DUPLICATE_ENVELOPE", f"attempt {aid} already binds envelope {a['provenance']['envelope_sha256'][:16]}")
    others = [x for x, y in st["attempts"].items() if y.get("provenance") and y["cell"] == a["cell"] and x != aid]
    if others:
        raise Refusal("DUPLICATE_ENVELOPE", f"cell {a['cell']} already has a bound envelope ({others})")
    a["provenance"] = {"schema": S.ENVELOPE_SCHEMA, "envelope": rel, "envelope_sha256": sha}


def unbound_sealed(st: dict) -> list:
    return sorted(aid for aid, a in st["attempts"].items() if a["status"] == "SEALED" and not a.get("provenance"))


def verify_bound_envelopes(spec, st: dict) -> int:
    """Structural invariants of the provenance extension; bound envelope bytes must be unchanged."""
    n, per_cell = 0, {}
    for aid, a in sorted(st["attempts"].items()):
        prov = a.get("provenance")
        if prov is None:
            continue
        if a["status"] != "SEALED" or prov.get("envelope") != envelope_rel(aid, a["cell"]):
            raise Refusal("LEDGER_LINKAGE", f"attempt {aid} binds provenance but is {a['status']}")
        per_cell.setdefault(a["cell"], []).append(aid)
        path = Path(spec.root) / prov["envelope"]
        if not path.exists() or sha256_file(path) != prov["envelope_sha256"]:
            raise Refusal("ENVELOPE_EVIDENCE_CORRUPT", f"cell {a['cell']}: bound envelope missing or its bytes changed")
        n += 1
    dup = {c: v for c, v in per_cell.items() if len(v) > 1}
    if dup:
        raise Refusal("DUPLICATE_ENVELOPE", f"cells with more than one bound envelope: {dup}")
    return n


def bind_envelope(led, authz, aid: str) -> dict:
    spec, st = led.spec, led.state
    a = st["attempts"][aid]
    if a.get("provenance"):
        return a["provenance"]
    entries = L.Ledger.read_journal(led.p.journal)[0]
    record = Path(spec.root) / a["record"]
    env = build_envelope(spec=spec, authz=authz, st=st, entries=entries, aid=aid, record_bytes=record.read_bytes())
    data = (json.dumps(env, indent=1, sort_keys=True) + "\n").encode()
    rel = envelope_rel(aid, a["cell"])
    path = Path(spec.root) / rel
    if not path.exists() or path.read_bytes() != data:            # absent, or an unbound crash residue
        atomic_write_bytes(path, data)
    os.chmod(path, 0o444)
    fsync_dir(path.parent)
    verify_pair(spec=spec, authz=authz, st=st, entries=entries, record_path=record, envelope_path=path,
                require_bound=False)
    sha = sha256_bytes(data)
    led.txn(S.PROVENANCE_EVENT, lambda s: op_bind_provenance(s, aid, rel, sha),
            {"attempt": aid, "cell": a["cell"], "envelope_sha256": sha})
    return led.state["attempts"][aid]["provenance"]
