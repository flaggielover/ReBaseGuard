"""Writes ONE activation object into a working tree (never commits, never pushes).

    python3 -B build_packet.py REPO amendment --draft amendment_draft.json
    python3 -B build_packet.py REPO authorization --authorized-by TEXT
    python3 -B build_packet.py REPO countersignature --from countersignature.json
    python3 -B build_packet.py REPO notice

Each object is derived from the frozen template or the reviewed draft, changing only the fields the frozen
architecture permits. Every JSON input is parsed with duplicate-key rejection. Prints the written path and sha256.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CP = "level4/closure_proofs/"
PROTO = CP + "p5y_k5_cusum_first_real_probe_protocol/"
EX = CP + "p5y_k5_cusum_real_point_executor/"
AMEND = PROTO + "protocol/EXECUTION_BINDING_AMENDMENT.json"
AUTH = PROTO + "protocol/AUTHORIZATION_ACTIVE.json"
TEMPLATE = PROTO + "protocol/AUTHORIZATION_TEMPLATE_R4.json"
CS = EX + "authorization/COUNTERSIGNATURE_ACTIVE.json"
CS_TEMPLATE = EX + "config/EXTERNAL_AUTHORIZATION_TEMPLATE.json"
LEDGER = PROTO + "ledger/ATTEMPT_LEDGER.jsonl"
FREEZE = "852b2d65c9332facd59771da7940ab429a7e2f2f"


def nodup(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise SystemExit(f"duplicate JSON keys: {keys}")
    return dict(pairs)


def load(p):
    return json.loads(Path(p).read_text(), object_pairs_hook=nodup)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def write_new(path: Path, data: bytes):
    if path.exists() or path.is_symlink():
        raise SystemExit(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print(path, sha(data))


ap = argparse.ArgumentParser()
ap.add_argument("repo")
ap.add_argument("what", choices=("amendment", "authorization", "countersignature", "notice"))
ap.add_argument("--draft")
ap.add_argument("--authorized-by")
ap.add_argument("--from", dest="src")
a = ap.parse_args()
R = Path(a.repo).resolve()

if a.what == "amendment":
    d = load(a.draft)
    review = R / d["independent_review"]
    lines = [l for l in review.read_text().splitlines()]
    verdicts = [l.split(":", 1)[1].strip() for l in lines if l.split(":", 1)[0].strip() == "REVIEW_VERDICT"]
    named = [l.split(":", 1)[1].strip() for l in lines if l.split(":", 1)[0].strip() == "REVIEWED_AMENDMENT_SOURCES_SHA256"]
    canon = sha(json.dumps(d["executor_sources_sha256"], sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode())
    if len(verdicts) != 1 or verdicts[0] not in ("PASS", "PASS_WITH_SCOPE_LIMITATION"):
        raise SystemExit(f"review verdict lines {verdicts}")
    if named != [canon]:
        raise SystemExit(f"review names sources {named}, the draft's canonical sources sha256 is {canon}")
    d["independent_review_sha256"] = sha(review.read_bytes())
    d["independent_review_verdict"] = verdicts[0]
    write_new(R / AMEND, (json.dumps(d, indent=1) + "\n").encode())

elif a.what == "authorization":
    t = load(R / TEMPLATE)
    am = (R / AMEND).read_bytes()
    if not a.authorized_by:
        raise SystemExit("--authorized-by required")
    auth = json.loads(json.dumps(t), object_pairs_hook=nodup)        # same key order as the template
    auth["EXECUTION_AUTHORIZED"] = True
    auth["PROTOCOL_FREEZE_COMMIT"] = FREEZE
    auth["AUTHORIZED_BY"] = a.authorized_by
    auth["AUTHORIZATION_UTC"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()   # ...+00:00
    auth["PRODUCER_R4_IDENTITY"]["executor_binding_sha256"] = sha(am)
    write_new(R / AUTH, (json.dumps(auth, indent=1) + "\n").encode())

elif a.what == "countersignature":
    t = load(R / CS_TEMPLATE)
    c = load(a.src)
    if set(c) != set(t) or set(c["countersigner"]) != set(t["countersigner"]):
        raise SystemExit("countersignature keys differ from the frozen template")
    for k in ("schema", "result_blind", "role", "activation_rule", "trust_model"):
        if c[k] != t[k]:
            raise SystemExit(f"countersignature field {k} differs from the frozen template")
    if type(c["attempt_slot"]) is not int or type(c["countersigner"]["utc"]) not in (int, float):
        raise SystemExit("attempt_slot must be an int and countersigner.utc a numeric epoch")
    write_new(R / CS, (json.dumps(c, indent=1) + "\n").encode())

else:
    auth = (R / AUTH).read_bytes()
    entry = {"event": "LAUNCH_NOTICE", "slot": "slot-1", "authorization_sha256": sha(auth),
             "utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat()}
    write_new(R / LEDGER, (json.dumps(entry, sort_keys=True) + "\n").encode())
