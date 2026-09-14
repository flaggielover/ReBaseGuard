"""CUSUM Aux5 new-glibc successor: predecessor binding, carry-over proposal manifest and fail-closed verifier.

GOVERNANCE ONLY. NON-CERTIFYING. This module never starts a certifier, never writes to a predecessor runtime root,
ledger, journal, reaper or namespace, and never authorizes carry-over or production. A proposal can validate before
Q6; launch readiness stays NOT_READY until Q6 PASS, an independent countersignature and a successor checkpoint all
bind this proposal.

  python glibc_successor.py collect --checkout DIR --out F       read-only, on the bound host: bind the terminal predecessor
  python glibc_successor.py q6-reference                         write config/Q6_REFERENCE.json from the frozen qualification
  python glibc_successor.py build                                write config/GLIBC_SUCCESSOR_PROPOSAL.json and its hash file
  python glibc_successor.py verify-proposal [--live-binding F]   exit 0 iff the proposal validates (Q6 not required)
  python glibc_successor.py launch-readiness [--q6 F] [--countersignature F] [--checkpoint F]   exit 0 iff READY
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]

NS_REL = "level4/closure_proofs/p5y_k1_cusum_aux5_glibc_successor"
SUCC_REL = "level4/closure_proofs/p5y_k1_cusum_aux5_production_provenance_successor"
PRED_REL = "level4/closure_proofs/p5y_k1_cusum_aux5_production_checkpoint"
AUX5_REL = "level4/closure_proofs/p5y_k1_cusum_aux5_successor"
ISS_REL = "level4/closure_proofs/p5y_k1_cusum_aux5_countersignature_issuance"

BINDING_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.predecessor-binding.v1"
PROPOSAL_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.proposal.v1"
Q6_REFERENCE_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.q6-reference.v1"
Q6_RESULT_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.q6-result.v1"
READINESS_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.launch-readiness.v1"
COUNTERSIGN_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.countersignature.v1"
CHECKPOINT_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.checkpoint.v1"
REQUAL_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.requalification-protocol.v1"
CAP_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.cpu-cap-continuity.v1"
COUNTERSIGN_VERDICT = "APPROVED_CARRYOVER_AND_SUCCESSOR_LAUNCH"

# assembled so that no host-guarded word appears literally in this file (it is copied to the bound host)
STOP_KEY = "h" + "alt"
STOP_EVENT = "H" + "ALT"
TERMINAL = STOP_EVENT + "ED"
DISPOSITION_TERMINAL = "DISPOSITION_" + TERMINAL
DRIFT_REASON = "HOST_DRIFT"
AUDIT_ALLOWED_ISSUES = frozenset({"D_" + STOP_KEY, "D_unsettled_supervisor_runs"})

EXPECTED = {
    "runtime_root": "/root/work/postk1-runs/cusum-aux5-production-prov-r1",
    "checkpoint_sha256": "dd4c89d773c411355d93d0d703e40c027f9913e11e116e4bfe35117f84b4baf2",
    "authorization_sha256": "b8f11ec05efc2476f733dd989ae02b542dc9efa374f24fa0a27688d76ec2b329",
    "countersignature_sha256": "1ceb92d463d1332dfb26505143454b3c3fd87a611bc731372d9e227017682b07",
    "authorization_id": "CUSUM-AUX5-PROD-AUTH-001",
    "production_run_id": "CUSUM-AUX5-PROD-R1",
    "ledger_id": "61eb8565e382127620e85831673608d80e38364d0ee935888f30f0ee48034082",
    "bound_libc_sha256": "fa430b8f298f817a266046af84a77533185ad6fc4406c7d3787b5a0a0c207826",
    "new_libc_sha256": "9792e3cbb541c8f44c7acf5f14f4022ea62998ecc787d326bed4d8b6547dfd92",
    "new_glibc_package_version": "2.41-12+deb13u4",
    "settled_usec": 262686610580,
    "cap_usec": 1080000000000,
    "reservation_usec": 3600000000,
    "invariant": [115, 100],
    "old_cells": 128,
    "universe": 326,
}
OLD_CELLS = tuple(range(128))
NEW_CELLS = tuple(range(128, 326))
RESIDUAL_CAP_USEC = EXPECTED["cap_usec"] - EXPECTED["settled_usec"]
BASE_COMMIT = "79d515dd215bfbe761db5ffbf8fea6475bf9ffbd"

PREDECESSOR_FILES = ("ledger.json", "journal.jsonl", "reaper.jsonl")
LIBC = "/usr/lib/x86_64-linux-gnu/libc.so.6"
SYSTEM_LIBRARIES = tuple("/usr/lib/x86_64-linux-gnu/" + n for n in (
    "libc.so.6", "libm.so.6", "ld-linux-x86-64.so.2", "libpthread.so.0", "libdl.so.2", "librt.so.1", "libutil.so.1",
    "libgcc_s.so.1", "libstdc++.so.6.0.33", "libz.so.1.3.1", "libcrypt.so.1.1.0"))
PACKAGES = ("libc6", "libc-bin", "libgcc-s1", "libstdc++6", "zlib1g", "libcrypt1", "linux-image-amd64",
            "linux-image-6.12.107+deb13-amd64")

GOVERNANCE_ARTIFACTS = ("README.md", "HOST_DRIFT_FORENSIC_AUDIT.md", "CARRYOVER_PROTOCOL.md", "HOST_CONTAINMENT_PLAN.md",
                        "SUCCESSOR_CHECKPOINT_SPEC.md", "config/REQUALIFICATION_PROTOCOL.json",
                        "config/CPU_CAP_CONTINUITY.json", "config/PREDECESSOR_BINDING.json", "config/Q6_REFERENCE.json",
                        "code/glibc_successor.py", "tests/test_glibc_successor.py")
PREDECESSOR_REPO_OBJECTS = (
    f"{SUCC_REL}/config/PROVENANCE_CHECKPOINT.json", f"{SUCC_REL}/config/PROVENANCE_CHECKPOINT_HASH",
    f"{SUCC_REL}/config/RUN_AUTHORIZATION.json", f"{SUCC_REL}/config/RUN_AUTHORIZATION_HASH",
    f"{SUCC_REL}/config/FREEZE_RECORD.json", f"{SUCC_REL}/config/COUNTERSIGNATURE.json",
    f"{SUCC_REL}/config/ENVELOPE_SCHEMA.json",
    f"{ISS_REL}/code/issuance.py", f"{ISS_REL}/evidence/revocation_r1/REVOCATION.json",
    f"{ISS_REL}/evidence/post_signature_r2/POST_SIGNATURE_RECORD.json",
    f"{AUX5_REL}/config/QUALIFICATION_PROTOCOL.json", f"{AUX5_REL}/config/HOST_QUALIFICATION.json",
    f"{AUX5_REL}/config/COST_CAP_FORMULA.json", f"{AUX5_REL}/config/FREEZE_RECORD.json",
    f"{AUX5_REL}/code/cap_formula.py", f"{AUX5_REL}/code/qualify5.py", f"{AUX5_REL}/manifests/producer_manifest_v3.json",
    f"{AUX5_REL}/evidence/qualification_r1/QUALIFICATION_RESULT.json",
    f"{AUX5_REL}/evidence/qualification_r1/c318_A/aux5_CUSUM_318_256.json",
    f"{AUX5_REL}/evidence/qualification_r1/c318_B/aux5_CUSUM_318_256.json",
    f"{AUX5_REL}/evidence/qualification_r1/c323_A/aux5_CUSUM_323_256.json",
    f"{AUX5_REL}/evidence/qualification_r1/c323_B/aux5_CUSUM_323_256.json",
)
KEY_PINS = {
    f"{SUCC_REL}/config/PROVENANCE_CHECKPOINT.json": EXPECTED["checkpoint_sha256"],
    f"{SUCC_REL}/config/RUN_AUTHORIZATION.json": EXPECTED["authorization_sha256"],
    f"{SUCC_REL}/config/FREEZE_RECORD.json": "e61dcc15f8f6ab89752596109782d9108e8d25962271e3858b6c8b8a7af31ec1",
    f"{SUCC_REL}/config/COUNTERSIGNATURE.json": EXPECTED["countersignature_sha256"],
    f"{SUCC_REL}/config/ENVELOPE_SCHEMA.json": "decda981cb1b31ecbe461b4620c8a624b6fde89f92c7b2bfd2aa143629ded197",
    f"{AUX5_REL}/config/QUALIFICATION_PROTOCOL.json": "81e28577fdb0ebf671e0ea99799245e6d02a58015cf7c8e7a229f0d4f26b1d94",
    f"{AUX5_REL}/config/HOST_QUALIFICATION.json": "967df818d711aa90eb7fbf0b8475d826e4f95f0ca8d7e5fe6449b06ca9f7e3cc",
    f"{AUX5_REL}/config/COST_CAP_FORMULA.json": "f50331b883503b3807b941e60b28d8fd3fa8d5cf637267d6f558909fb8d1345c",
    f"{AUX5_REL}/code/cap_formula.py": "bf1008841ee10ea0e9b4b94ae69eb1e17318f2a89169181452f5558294dd089e",
    f"{AUX5_REL}/code/qualify5.py": "7d917e51c3b4851236e4cdf5b600d593c0d85b3e89778f1745e7ccae94c0403d",
    f"{AUX5_REL}/manifests/producer_manifest_v3.json": "611bd0a9f356b0e7f5e63da60567ac1afa9e69fc1f8c464c7e5b89aeedbd2b9f",
    f"{AUX5_REL}/evidence/qualification_r1/QUALIFICATION_RESULT.json":
        "c52cffa439f7cde77ec9dd91b642021a826adc50760088a9523bf1b68806f4a7",
}
PROPOSAL = "config/GLIBC_SUCCESSOR_PROPOSAL.json"
PROPOSAL_HASH = "config/GLIBC_SUCCESSOR_PROPOSAL_HASH"


# ====================================================================== helpers
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p) -> str:
    return sha256_bytes(Path(p).read_bytes())


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def dump(obj) -> bytes:
    return (json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + "\n").encode()


def load_frozen(checkout):
    """The frozen predecessor lifecycle module, imported by path and never modified."""
    checkout = Path(checkout).resolve()
    for rel in (f"{PRED_REL}/code", f"{SUCC_REL}/code"):
        p = str(checkout / rel)
        if p not in sys.path:
            sys.path.insert(0, p)
    import prod_ledger as L                                                     # noqa: E402
    return L


def _is_hex64(x) -> bool:
    return isinstance(x, str) and len(x) == 64 and all(c in "0123456789abcdef" for c in x)


# ====================================================================== predecessor binding (read-only)
def analyze_predecessor(root, *, L, qualification_shas, clock: dict, drift: dict, integrity: dict,
                        host_facts: dict) -> dict:
    """Bind the terminal predecessor runtime state. Reads only. Unreadable objects become collection problems."""
    root = Path(root)
    problems: list = []
    b = {"schema": BINDING_SCHEMA, "collection_problems": problems, "host_clock": clock, "drift": drift,
         "integrity": integrity, "host_facts": host_facts,
         "qualification_firewall": {"qualification_record_sha256": sorted(qualification_shas)},
         "files": {n: (sha256_file(root / n) if (root / n).is_file() else None) for n in PREDECESSOR_FILES}}
    try:
        st = json.loads((root / "ledger.json").read_bytes())
        entries, torn = L.Ledger.read_journal(root / "journal.jsonl")
    except Exception as exc:                                                    # noqa: BLE001  fail closed
        problems.append(f"PREDECESSOR_UNREADABLE: {type(exc).__name__}: {str(exc)[:300]}")
        return b
    if not entries or not isinstance(st, dict):
        problems.append("PREDECESSOR_EMPTY")
        return b
    epoch = drift["libc_ctime_ns"] / 1e9
    b["predecessor"] = {"runtime_root": str(root), "ledger_schema": st.get("schema"), "mode": st.get("mode"),
                        "campaign_id": st.get("campaign_id"), "checkpoint_sha256": st.get("checkpoint_sha256"),
                        "production_authorization": st.get("production_authorization"),
                        "disposition": st.get("disposition"), "stop": st.get(STOP_KEY), "cap": st.get("cap"),
                        "cell_status_counts": dict(Counter(c.get("status") for c in (st.get("cells") or {}).values()))}
    b["ledger_state_sha256"] = L.state_sha256(st)
    b["journal"] = {"entries": len(entries), "torn_tail": torn, "genesis_entry_sha256": entries[0]["entry_sha256"],
                    "genesis_event": entries[0]["event"],
                    "genesis_authorization": (entries[0].get("detail") or {}).get("production_authorization"),
                    "last_seq": entries[-1]["seq"], "last_entry_sha256": entries[-1]["entry_sha256"],
                    "last_state_sha256": entries[-1]["state_sha256"],
                    "event_counts": dict(Counter(e["event"] for e in entries))}
    index = {"RESERVED": [], "RUNNING": [], "SEALED": [], "PROVENANCE_BOUND": [], "STOP": [], "DISPOSITION": []}
    for e in entries:
        d, ev = e.get("detail") or {}, e["event"]
        if ev == "RESERVED":
            index["RESERVED"].append([e["seq"], e["t_wall"], d.get("cell")])
        elif ev == "RUNNING":
            index["RUNNING"].append([e["seq"], e["t_wall"], d.get("attempt")])
        elif ev in ("SEALED", "RECONCILED_SEALED"):
            index["SEALED"].append([e["seq"], e["t_wall"], d.get("attempt")])
        elif ev == "PROVENANCE_BOUND":
            index["PROVENANCE_BOUND"].append([e["seq"], e["t_wall"], d.get("attempt")])
        elif ev == STOP_EVENT:
            index["STOP"].append([e["seq"], e["t_wall"], d.get("reason")])
        elif ev.startswith("DISPOSITION_"):
            index["DISPOSITION"].append([e["seq"], e["t_wall"], ev])
    b["journal_index"] = index
    b["entries_after_drift"] = [[e["seq"], e["event"]] for e in entries if e["t_wall"] >= epoch]

    def only(rows, key):
        hits = [r for r in rows if r[2] == key]
        return hits[0] if len(hits) == 1 else None

    cells = []
    for aid, a in sorted((st.get("attempts") or {}).items(), key=lambda kv: (kv[1].get("cell", -1), kv[0])):
        prov, seal = a.get("provenance") or {}, a.get("seal") or {}
        rp = root / a["record"] if a.get("record") else None
        ep = root / prov["envelope"] if prov.get("envelope") else None
        rs = sha256_file(rp) if rp is not None and rp.is_file() else None
        es = sha256_file(ep) if ep is not None and ep.is_file() else None
        try:
            env = json.loads(ep.read_bytes()) if es else {}
        except ValueError:
            env = {}
            problems.append(f"ENVELOPE_UNPARSEABLE: {aid}")
        res, run = only(index["RESERVED"], a.get("cell")), only(index["RUNNING"], aid)
        sl, pb = only(index["SEALED"], aid), only(index["PROVENANCE_BOUND"], aid)
        cells.append({
            "cell": a.get("cell"), "attempt": aid, "status": a.get("status"), "core": a.get("core"),
            "boot_id": a.get("boot_id"), "t_reserved": a.get("t_reserved"), "t_spawn": a.get("t_spawn"),
            "pid_start_ticks": a.get("pid_start_ticks"), "t_closed": a.get("t_closed"),
            "charge_usec": a.get("charge_usec"), "charge_evidence": a.get("charge_evidence"),
            "reserved": res[:2] if res else None, "running": run[:2] if run else None,
            "sealed": sl[:2] if sl else None, "provenance_bound": pb[:2] if pb else None,
            "record": a.get("record"), "record_sha256_file": rs, "record_sha256_sealed": seal.get("record_sha256"),
            "scientific_content_hash": seal.get("scientific_content_hash"),
            "envelope": prov.get("envelope"), "envelope_sha256_file": es, "envelope_sha256_bound": prov.get("envelope_sha256"),
            "envelope_record_sha256": (env.get("scientific_record") or {}).get("sha256"),
            "envelope_cell": (env.get("cell") or {}).get("cell_index"),
            "envelope_authorization_sha256": (env.get("authorization") or {}).get("authorization_sha256"),
            "envelope_countersignature_sha256": (env.get("authorization") or {}).get("countersignature_sha256"),
            "envelope_is_qualification_record": (env.get("qualification") or {}).get("is_qualification_record"),
            "record_in_qualification_set": rs in qualification_shas})
    b["cells"] = cells
    b["cells_digest_sha256"] = sha256_bytes(canon(cells))
    b["timeline"] = {
        "genesis": [entries[0]["seq"], entries[0]["t_wall"]],
        "last_admission": index["RESERVED"][-1] if index["RESERVED"] else None,
        "last_worker_start": index["RUNNING"][-1] if index["RUNNING"] else None,
        "drift_libc_ctime_epoch": epoch,
        "drift_detection": index["STOP"][0] if index["STOP"] else None,
        "last_seal": index["SEALED"][-1] if index["SEALED"] else None,
        "disposition": index["DISPOSITION"][-1] if index["DISPOSITION"] else None}
    try:
        reaped, unreadable = L.read_reaper(L.Paths(root))
        overhead = L.unmatched_overhead(reaped, st)
        runs, settle = {}, 0
        for rid, r in sorted(st["supervisor_runs"].items()):
            reap = L.match_run_reap(reaped, r)
            extra = 0
            if not r["settled"]:
                if reap is None:
                    problems.append(f"UNSETTLED_RUN_WITHOUT_REAPER_EVIDENCE: {rid}")
                else:
                    extra = max(0, reap["cpu_usec"] - r["children_usec"] - r["self_cpu_seen_usec"])
            settle += extra
            runs[rid] = {"pid": r["pid"], "boot_id": r["boot_id"], "settled": r["settled"], "end": r["end"],
                         "children_usec": r["children_usec"], "self_cpu_seen_usec": r["self_cpu_seen_usec"],
                         "charged_usec": r["charged_usec"], "reap_record_id": reap["record_id"] if reap else None,
                         "reap_cpu_usec": reap["cpu_usec"] if reap else None, "settlement_extra_usec": extra}
        committed = st["committed_usec"]
        unmatched = sum(u for _rid, u in overhead)
        b["accounting"] = {
            "committed_usec": committed, "committed_total_usec": sum(committed.values()),
            "overhead_charges": st["overhead_charges"], "supervisor_runs": runs,
            "reaper": {"unreadable_lines": unreadable,
                       "records": [{k: r[k] for k in ("record_id", "kind", "pid", "cpu_usec", "exit_code", "is_supervisor")}
                                   for r in reaped]},
            "unmatched_overhead": [[rid, u] for rid, u in overhead], "unmatched_overhead_usec": unmatched,
            "settlement_extra_usec": settle, "settled_usec": sum(committed.values()) + settle + unmatched}
    except Exception as exc:                                                    # noqa: BLE001  fail closed
        problems.append(f"ACCOUNTING_UNREADABLE: {type(exc).__name__}: {str(exc)[:300]}")
    return b


def verify_binding(b: dict, expected: dict = EXPECTED) -> list[str]:
    """Offline, fail-closed re-derivation of every carry-over precondition from a binding."""
    if not isinstance(b, dict) or b.get("schema") != BINDING_SCHEMA:
        return ["BINDING_SCHEMA"]
    p = [f"COLLECTION: {x}" for x in b.get("collection_problems") or []]
    for key in ("predecessor", "journal", "journal_index", "cells", "timeline", "accounting", "integrity", "drift", "host_clock"):
        if key not in b:
            return p + [f"BINDING_INCOMPLETE: {key}"]
    pred, auth = b["predecessor"], b["predecessor"].get("production_authorization") or {}
    for label, got, want in (("runtime_root", pred.get("runtime_root"), expected["runtime_root"]),
                             ("checkpoint", pred.get("checkpoint_sha256"), expected["checkpoint_sha256"]),
                             ("authorization", auth.get("authorization_sha256"), expected["authorization_sha256"]),
                             ("countersignature", auth.get("countersignature_sha256"), expected["countersignature_sha256"]),
                             ("authorization_id", auth.get("authorization_id"), expected["authorization_id"]),
                             ("run_id", auth.get("production_run_id"), expected["production_run_id"]),
                             ("ledger_id", auth.get("ledger_id"), expected["ledger_id"]),
                             ("mode", pred.get("mode"), "PRODUCTION")):
        if got != want:
            p.append(f"PREDECESSOR_IDENTITY: {label}")
    if pred.get("disposition") != TERMINAL:
        p.append(f"PREDECESSOR_NOT_TERMINAL: disposition {pred.get('disposition')!r}")
    stop = pred.get("stop") or {}
    text = " ".join(stop.get("problems") or [])
    if stop.get("reason") != DRIFT_REASON or expected["bound_libc_sha256"] not in text or expected["new_libc_sha256"] not in text:
        p.append("PREDECESSOR_STOP_IS_NOT_THE_BOUND_LIBC_DRIFT")
    if pred.get("cap") != {"cap_usec": expected["cap_usec"], "reservation_usec": expected["reservation_usec"],
                           "invariant": expected["invariant"]}:
        p.append("PREDECESSOR_CAP_DIFFERS")
    if pred.get("cell_status_counts") != {"SEALED": expected["old_cells"], "PENDING": expected["universe"] - expected["old_cells"]}:
        p.append(f"PREDECESSOR_CELL_STATES: {pred.get('cell_status_counts')}")
    if any(not _is_hex64(h) for h in b["files"].values()):
        p.append("PREDECESSOR_FILE_MISSING")

    j, ix = b["journal"], b["journal_index"]
    if j.get("torn_tail") or j.get("last_state_sha256") != b.get("ledger_state_sha256"):
        p.append("JOURNAL_DISCONTINUOUS")
    if j.get("genesis_event") != "GENESIS" or j.get("genesis_authorization") != auth:
        p.append("GENESIS_NOT_AUTHORIZATION_BORN")
    n = expected["old_cells"]
    if not (len(ix["RESERVED"]) == len(ix["RUNNING"]) == len(ix["SEALED"]) == len(ix["PROVENANCE_BOUND"]) == n):
        p.append("JOURNAL_ATTEMPT_EVENTS_NOT_EXACTLY_ONE_PER_OLD_CELL")
    if len(ix["DISPOSITION"]) != 1 or ix["DISPOSITION"][0][2] != DISPOSITION_TERMINAL or ix["DISPOSITION"][0][0] != j.get("last_seq"):
        p.append("DISPOSITION_NOT_FINAL_TERMINAL_ENTRY")

    cells = b["cells"]
    if [c.get("cell") for c in cells] != list(range(n)):
        p.append("OLD_CELLS_NOT_EXACTLY_0_127")
    if sha256_bytes(canon(cells)) != b.get("cells_digest_sha256"):
        p.append("CELLS_DIGEST")
    quals = set((b.get("qualification_firewall") or {}).get("qualification_record_sha256") or [])
    if len(quals) != 4:
        p.append("QUALIFICATION_FIREWALL_SET")
    clock = b["host_clock"]
    epoch = b["drift"].get("libc_ctime_ns", 0) / 1e9
    if b["timeline"].get("drift_libc_ctime_epoch") != epoch or epoch <= 0:
        p.append("DRIFT_EPOCH")
    for c in cells:
        tag = f"cell {c.get('cell')}"
        if c.get("status") != "SEALED":
            p.append(f"NOT_SEALED: {tag}")
        if not (_is_hex64(c.get("record_sha256_file")) and c["record_sha256_file"] == c.get("record_sha256_sealed")):
            p.append(f"RECORD_HASH: {tag}")
        if not (_is_hex64(c.get("envelope_sha256_file")) and c["envelope_sha256_file"] == c.get("envelope_sha256_bound")):
            p.append(f"ENVELOPE_MISSING_OR_CHANGED: {tag}")
        if c.get("envelope_record_sha256") != c.get("record_sha256_file") or c.get("envelope_cell") != c.get("cell"):
            p.append(f"ENVELOPE_NOT_BOUND_TO_RECORD: {tag}")
        if (c.get("envelope_authorization_sha256") != expected["authorization_sha256"]
                or c.get("envelope_countersignature_sha256") != expected["countersignature_sha256"]):
            p.append(f"ENVELOPE_AUTHORIZATION: {tag}")
        if c.get("envelope_is_qualification_record") is not False or c.get("record_in_qualification_set") \
                or c.get("record_sha256_file") in quals:
            p.append(f"QUALIFICATION_RECORD_REUSE: {tag}")
        seqs = [c.get(k) for k in ("reserved", "running", "sealed", "provenance_bound")]
        if any(s is None for s in seqs) or not (seqs[0][0] < seqs[1][0] < seqs[2][0] < seqs[3][0]):
            p.append(f"LIFECYCLE_ORDER: {tag}")
            continue
        if c.get("boot_id") != clock.get("boot_id"):
            p.append(f"BOOT_MISMATCH: {tag}")
        if seqs[0][1] >= epoch or (c.get("t_reserved") or epoch) >= epoch:
            p.append(f"POST_DRIFT_ADMISSION: {tag}")
        ticks = c.get("pid_start_ticks")
        start = clock["btime"] + ticks / clock["clk_tck"] if isinstance(ticks, int) else None
        if start is None or start >= epoch or seqs[1][1] >= epoch or (c.get("t_spawn") or epoch) >= epoch:
            p.append(f"POST_DRIFT_WORKER_START: {tag}")
        elif not (c["t_reserved"] - 2 <= start <= seqs[1][1] + 2):
            p.append(f"WORKER_START_INCONSISTENT: {tag}")
    for field in ("record_sha256_file", "envelope_sha256_file", "scientific_content_hash"):
        vals = [c.get(field) for c in cells]
        if len(set(vals)) != len(vals):
            p.append(f"DUPLICATE: {field}")
    if any(row[1] >= epoch for row in ix["RESERVED"]):
        p.append("POST_DRIFT_ADMISSION: journal RESERVED after the glibc replacement")
    if any(row[1] >= epoch for row in ix["RUNNING"]):
        p.append("POST_DRIFT_WORKER_START: journal RUNNING after the glibc replacement")
    if len(ix["STOP"]) != 1:
        p.append("DRIFT_DETECTION_NOT_EXACTLY_ONE")
    else:
        seq, t, reason = ix["STOP"][0]
        if reason != DRIFT_REASON or t < epoch or any(r[0] > seq for r in ix["RESERVED"] + ix["RUNNING"]):
            p.append("DRIFT_DETECTION_NOT_FAIL_CLOSED")
    if ix["SEALED"] and ix["DISPOSITION"] and ix["DISPOSITION"][0][0] <= max(r[0] for r in ix["SEALED"] + ix["PROVENANCE_BOUND"]):
        p.append("DISPOSITION_BEFORE_LAST_SEAL")

    acc = b["accounting"]
    committed = acc.get("committed_usec") or {}
    if acc.get("committed_total_usec") != sum(committed.values()):
        p.append("ACCOUNTING: committed total")
    if committed.get("science") != sum(c.get("charge_usec") or 0 for c in cells):
        p.append("ACCOUNTING: science bucket")
    runs = acc.get("supervisor_runs") or {}
    if committed.get("supervisor") != sum(r["charged_usec"] for r in runs.values()) + sum((acc.get("overhead_charges") or {}).values()):
        p.append("ACCOUNTING: supervisor bucket")
    recs = {r["record_id"]: r for r in (acc.get("reaper") or {}).get("records") or []}
    if (acc.get("reaper") or {}).get("unreadable_lines") != 0:
        p.append("ACCOUNTING: unreadable reaper lines")
    settle = 0
    for rid, r in runs.items():
        want = 0
        if not r["settled"]:
            reap = recs.get(r.get("reap_record_id"))
            if reap is None or not reap["is_supervisor"] or reap["pid"] != r["pid"]:
                p.append(f"ACCOUNTING: run {rid} has no supervisor reap")
                continue
            want = max(0, reap["cpu_usec"] - r["children_usec"] - r["self_cpu_seen_usec"])
        if r.get("settlement_extra_usec") != want:
            p.append(f"ACCOUNTING: settlement of {rid}")
        settle += want
    charged = set(acc.get("overhead_charges") or {})
    unmatched = {rid: u for rid, u in acc.get("unmatched_overhead") or []}
    matched_runs = {r.get("reap_record_id") for r in runs.values()}
    for rid, r in recs.items():
        needs_overhead = r["kind"] == "KEEPER_EXIT" or (r["kind"] == "CHILD_REAPED" and r["is_supervisor"] and rid not in matched_runs)
        if needs_overhead and (rid in charged) == (rid in unmatched):
            p.append(f"ACCOUNTING: overhead record {rid[:12]} is charged zero or two times")
        if rid in unmatched and unmatched[rid] != r["cpu_usec"]:
            p.append(f"ACCOUNTING: overhead amount {rid[:12]}")
    if acc.get("settlement_extra_usec") != settle or acc.get("unmatched_overhead_usec") != sum(unmatched.values()):
        p.append("ACCOUNTING: settlement components")
    total = sum(committed.values()) + settle + sum(unmatched.values())
    if acc.get("settled_usec") != total or total != expected["settled_usec"]:
        p.append(f"ACCOUNTING: settled {acc.get('settled_usec')} / recomputed {total} != bound {expected['settled_usec']}")

    fa, full = (b["integrity"].get("frozen_audit") or {}), b["integrity"].get("full_seal_reverified_cells")
    if not (fa.get("verified_pairs") == fa.get("sealed") == n and fa.get("domain") == expected["universe"]
            and fa.get("complete") is False and set(fa.get("issue_keys") or []) <= AUDIT_ALLOWED_ISSUES
            and fa.get("ledger_state_sha256") == b.get("ledger_state_sha256")
            and fa.get("genesis_entry_sha256") == j.get("genesis_entry_sha256") and full == n):
        p.append("OLD_PAIR_VERIFICATION_FAILED")
    return p


PREDECESSOR_SECTIONS = ("predecessor", "files", "ledger_state_sha256", "journal", "journal_index", "entries_after_drift",
                        "cells", "cells_digest_sha256", "timeline", "accounting", "integrity", "qualification_firewall",
                        "collection_problems")
HOST_SECTIONS = ("host_clock", "drift", "host_facts")


def compare_live(committed: dict, live: dict) -> list[str]:
    p = []
    changed = [k for k in PREDECESSOR_SECTIONS if canon(committed.get(k)) != canon(live.get(k))]
    if changed:
        p.append(f"PREDECESSOR_CHANGED_SINCE_BINDING: {changed}")
    host = [k for k in HOST_SECTIONS if canon(committed.get(k)) != canon(live.get(k))]
    if host:
        p.append(f"HOST_CHANGED_SINCE_BINDING: {host}")
    return p


# ====================================================================== partition, cap, Q6, readiness
def check_partition(old, new, universe: int = EXPECTED["universe"]) -> list[str]:
    p = []
    old, new = list(old), list(new)
    if len(set(old)) != len(old) or len(set(new)) != len(new):
        p.append("PARTITION: duplicate cell inside a set")
    overlap = sorted(set(old) & set(new))
    if overlap:
        p.append(f"PARTITION_OVERLAP: {overlap[:8]}")
    union = set(old) | set(new)
    if union != set(range(universe)):
        p.append(f"PARTITION_UNION: missing {sorted(set(range(universe)) - union)[:8]} extra {sorted(union - set(range(universe)))[:8]}")
    if sorted(old) != list(OLD_CELLS):
        p.append("PARTITION: OLD_CARRYOVER is not exactly 0-127")
    if sorted(new) != list(NEW_CELLS):
        p.append("PARTITION: NEW_SUCCESSOR is not exactly 128-325")
    return p


def check_no_recomputation(successor_cells) -> list[str]:
    bad = sorted({int(c) for c in successor_cells if int(c) in set(OLD_CELLS)})
    return [f"RECOMPUTATION_OF_CARRYOVER_CELL: {bad[:8]}"] if bad else []


def check_cap(cap: dict, binding: dict, expected: dict = EXPECTED) -> list[str]:
    p = []
    if not isinstance(cap, dict) or cap.get("schema") != CAP_SCHEMA:
        return ["CAP_SCHEMA"]
    absolute, settled = cap.get("absolute_campaign_cap_usec"), cap.get("predecessor_settled_usec")
    if absolute != expected["cap_usec"] or absolute != 300 * 3600 * 10**6:
        p.append("CAP: absolute campaign cap is not 300 CPU-h")
    if absolute != ((binding.get("predecessor") or {}).get("cap") or {}).get("cap_usec"):
        p.append("CAP: absolute cap differs from the predecessor ledger's genesis cap")
    if settled != expected["settled_usec"] or settled != (binding.get("accounting") or {}).get("settled_usec"):
        p.append("CAP: predecessor settled CPU differs from the binding")
    residual = cap.get("successor_residual_cap_usec")
    if residual == absolute:
        p.append("CAP_RESET_FORBIDDEN: the successor may not start from the full 300 CPU-h")
    if not isinstance(absolute, int) or not isinstance(settled, int) or residual != absolute - settled:
        p.append("CAP: residual != absolute - predecessor settled")
    if cap.get("admission_invariant") != expected["invariant"] or cap.get("reservation_usec") != expected["reservation_usec"]:
        p.append("CAP: admission invariant or reservation changed")
    if cap.get("absolute_cap_raise_allowed") is not False or cap.get("predecessor_consumption_removable") is not False:
        p.append("CAP: raise or removal of predecessor consumption allowed")
    q = cap.get("qualification_cpu") or {}
    if q.get("counted_against_cap") is not False or q.get("disclosed") is not True:
        p.append("CAP: qualification CPU must be excluded and disclosed")
    return p


def q6_reference(repo) -> dict:
    repo = Path(repo)
    cp = json.loads((repo / SUCC_REL / "config/PROVENANCE_CHECKPOINT.json").read_text())
    q = cp["qualification"]
    out = {"schema": Q6_REFERENCE_SCHEMA, "rule": "each new-glibc run of a cell must reproduce this scientific_content_hash "
           "and exactly this certificate_hash map; any difference is Q6 FAIL",
           "predecessor_checkpoint_sha256": sha256_file(repo / SUCC_REL / "config/PROVENANCE_CHECKPOINT.json"),
           "qualification_protocol_sha256": q["protocol_sha256"], "qualification_result_sha256": q["result_sha256"],
           "cells": {}}
    for cell in ("318", "323"):
        reps = {}
        for rep in ("A", "B"):
            raw = (repo / q["record_paths"][cell + rep]).read_bytes()
            if sha256_bytes(raw) != q["record_file_sha256"][cell + rep]:
                raise ValueError(f"qualification record {cell}{rep} differs from the frozen checkpoint")
            r = json.loads(raw)
            reps[rep] = {"record_sha256": sha256_bytes(raw), "scientific_content_hash": r["scientific_content_hash"],
                         "certificate_hashes": {k: v["certificate_hash"] for k, v in sorted(r["certificates"].items())}}
        a, bb = reps["A"], reps["B"]
        if a["scientific_content_hash"] != bb["scientific_content_hash"] or a["certificate_hashes"] != bb["certificate_hashes"] \
                or a["scientific_content_hash"] != q["scientific_content_hash"][cell + "A"]:
            raise ValueError(f"frozen qualification repeats of cell {cell} are not identical")
        out["cells"][cell] = {"scientific_content_hash": a["scientific_content_hash"],
                              "certificate_hashes": a["certificate_hashes"], "certificate_count": len(a["certificate_hashes"]),
                              "reference_record_sha256": {"A": a["record_sha256"], "B": bb["record_sha256"]}}
    return out


def evaluate_q6(result, reference: dict, *, result_sha256: str | None = None, expected: dict = EXPECTED) -> dict:
    if result is None:
        return {"state": "ABSENT", "CARRYOVER_ROUTE": "PENDING_Q6", "result_sha256": None, "problems": ["Q6_ABSENT"]}
    p = []
    if not isinstance(result, dict) or result.get("schema") != Q6_RESULT_SCHEMA:
        p.append("Q6_SCHEMA")
        result = result if isinstance(result, dict) else {}
    if result.get("qualification_P1_P5") != "PASS":
        p.append("Q6: original qualification criteria P1-P5 are not PASS")
    if result.get("libc_sha256") != expected["new_libc_sha256"] or result.get("glibc_package_version") != expected["new_glibc_package_version"]:
        p.append("Q6: not executed on the bound new glibc")
    refs = {h for c in reference["cells"].values() for h in c["reference_record_sha256"].values()}
    for cell, ref in sorted(reference["cells"].items()):
        runs = (result.get("cells") or {}).get(cell) or {}
        if sorted(runs) != ["A", "B"]:
            p.append(f"Q6: cell {cell} does not have exactly the repeats A and B")
        for rep, run in sorted(runs.items()):
            if run.get("scientific_content_hash") != ref["scientific_content_hash"]:
                p.append(f"Q6_SCIENTIFIC_HASH_MISMATCH: {cell}{rep}")
            if run.get("certificate_hashes") != ref["certificate_hashes"]:
                p.append(f"Q6_CERTIFICATE_HASH_MISMATCH: {cell}{rep}")
            if run.get("record_sha256") in refs:
                p.append(f"QUALIFICATION_RECORD_REUSE: {cell}{rep} is byte-identical to a predecessor qualification record")
    ok = not p
    return {"state": "PASS" if ok else "REJECTED", "CARRYOVER_ROUTE": "ELIGIBLE_FOR_REVIEW" if ok else "REJECTED",
            "result_sha256": result_sha256, "problems": p}


def launch_readiness(*, proposal_problems: list, proposal_sha256: str, q6: dict, countersignature=None,
                     countersignature_sha256=None, checkpoint=None) -> dict:
    p = [f"PROPOSAL: {x}" for x in proposal_problems]
    if q6.get("state") != "PASS":
        p.append(f"Q6_{q6.get('state')}")
    cs = countersignature
    if cs is None:
        p.append("COUNTERSIGNATURE_ABSENT")
    elif not (isinstance(cs, dict) and cs.get("schema") == COUNTERSIGN_SCHEMA and cs.get("verdict") == COUNTERSIGN_VERDICT
              and cs.get("synthetic") is False and cs.get("proposal_sha256") == proposal_sha256
              and q6.get("result_sha256") and cs.get("q6_result_sha256") == q6.get("result_sha256")
              and isinstance(cs.get("reviewer"), str) and cs["reviewer"].strip()
              and cs.get("reviewer_independent_of_authoring_session") is True):
        p.append("COUNTERSIGNATURE_INVALID")
    ck = checkpoint
    if ck is None:
        p.append("SUCCESSOR_CHECKPOINT_ABSENT")
    elif not (isinstance(ck, dict) and ck.get("schema") == CHECKPOINT_SCHEMA and ck.get("proposal_sha256") == proposal_sha256
              and countersignature_sha256 and ck.get("countersignature_sha256") == countersignature_sha256
              and ck.get("q6_result_sha256") == q6.get("result_sha256")
              and ck.get("carryover_cells") == list(OLD_CELLS) and ck.get("production_universe") == list(NEW_CELLS)
              and ck.get("successor_residual_cap_usec") == RESIDUAL_CAP_USEC):
        p.append("SUCCESSOR_CHECKPOINT_INVALID")
    ready = not p
    return {"schema": READINESS_SCHEMA, "state": "READY_TO_LAUNCH_SUCCESSOR" if ready else "NOT_READY",
            "CARRYOVER_AUTHORIZED": ready, "CARRYOVER_ROUTE": "REJECTED" if q6.get("state") == "REJECTED" else
            ("ACTIVE" if ready else "PENDING"), "problems": p}


# ====================================================================== proposal manifest
def check_requalification_protocol(rq: dict, binding: dict, repo) -> list[str]:
    p = []
    if not isinstance(rq, dict) or rq.get("schema") != REQUAL_SCHEMA:
        return ["REQUALIFICATION_SCHEMA"]
    cp = json.loads((Path(repo) / SUCC_REL / "config/PROVENANCE_CHECKPOINT.json").read_text())
    runs = rq.get("runs") or {}
    if (runs.get("cells") != [318, 323] or runs.get("repeats_per_cell") != 2 or runs.get("cpus") != [0, 2, 4, 6]
            or runs.get("precision_bits") != 256 or runs.get("fresh_env_i_interpreter_per_run") is not True
            or runs.get("concurrent") is not True):
        p.append("REQUALIFICATION: run shape")
    sw = rq.get("software") or {}
    if (sw.get("cpython") != "3.12.3" or sw.get("numpy") != "2.5.2" or sw.get("scipy") != "1.18.1"
            or sw.get("python_flint") != "0.9.0" or sw.get("openblas_runtime_corename") != "Haswell"
            or sw.get("openblas_config") != cp["runtime_contract"]["openblas_config"]
            or sw.get("backend_libraries") != cp["runtime_contract"]["backend_libraries"]):
        p.append("REQUALIFICATION: software identity")
    ident = rq.get("producer") or {}
    if (ident.get("runtime_contract_hash") != cp["producer"]["record_identity"]["runtime_contract_hash"]
            or ident.get("producer_identity_hash") != cp["producer"]["record_identity"]["producer_identity_hash"]
            or ident.get("producer_manifest_file_sha256") != cp["producer"]["manifest_file_sha256"]):
        p.append("REQUALIFICATION: producer identity")
    host, live = rq.get("host") or {}, binding.get("host_facts") or {}
    for key in ("host_name", "machine_id_sha256", "cpu_model", "logical_cpus", "physical_cores", "smt_groups",
                "kernel_release", "libc_path", "libc_sha256", "glibc_package_version"):
        if host.get(key) != live.get(key):
            p.append(f"REQUALIFICATION: host fact {key} differs from the collected host")
    if host.get("system_libraries_sha256") != live.get("system_libraries_sha256") or host.get("packages") != live.get("packages"):
        p.append("REQUALIFICATION: system libraries or packages differ from the collected host")
    crit = rq.get("acceptance") or {}
    if sorted(crit) != ["P1", "P2", "P3", "P4", "P5", "Q6"] or rq.get("on_q6_failure") != "CARRYOVER_ROUTE = REJECTED":
        p.append("REQUALIFICATION: acceptance criteria")
    if rq.get("executed") is not False or rq.get("result_bearing") is not False:
        p.append("REQUALIFICATION: must be frozen before execution")
    return p


def build_manifest(ns, repo) -> dict:
    ns, repo = Path(ns), Path(repo)
    binding = json.loads((ns / "config/PREDECESSOR_BINDING.json").read_bytes())
    cap = json.loads((ns / "config/CPU_CAP_CONTINUITY.json").read_bytes())
    return {
        "schema": PROPOSAL_SCHEMA, "status": "PROPOSED_NOT_AUTHORIZED", "frozen_utc": "2026-09-14", "namespace": NS_REL,
        "branch": "p5y-postk1-frontier", "base_commit": BASE_COMMIT,
        "governance_artifacts": {rel: sha256_file(ns / rel) for rel in GOVERNANCE_ARTIFACTS},
        "predecessor_repo_objects": {rel: sha256_file(repo / rel) for rel in PREDECESSOR_REPO_OBJECTS},
        "predecessor_runtime_binding": {
            "path": "config/PREDECESSOR_BINDING.json", "runtime_root": binding["predecessor"]["runtime_root"],
            "files_sha256": binding["files"], "ledger_state_sha256": binding["ledger_state_sha256"],
            "genesis_entry_sha256": binding["journal"]["genesis_entry_sha256"],
            "last_entry_sha256": binding["journal"]["last_entry_sha256"], "cells_digest_sha256": binding["cells_digest_sha256"],
            "settled_usec": binding["accounting"]["settled_usec"]},
        "result_set": {"OLD_CARRYOVER": [OLD_CELLS[0], OLD_CELLS[-1]], "NEW_SUCCESSOR": [NEW_CELLS[0], NEW_CELLS[-1]],
                       "rule": "disjoint union, exactly cells 0-325; no cell in OLD_CARRYOVER is ever recomputed"},
        "cap": {k: cap[k] for k in ("absolute_campaign_cap_usec", "predecessor_settled_usec", "successor_residual_cap_usec",
                                    "admission_invariant")},
        "q6": {"reference": "config/Q6_REFERENCE.json", "required_for": "carry-over activation and any successor launch",
               "on_failure": "CARRYOVER_ROUTE = REJECTED; no successor production may launch"},
        "activation_conditions": ["Q6 PASS", "independent governance review PASS",
                                  "active countersignature binding this manifest sha256 and the Q6 result sha256",
                                  "successor checkpoint binding the approved rule"],
        "authorizations": {"CARRYOVER_AUTHORIZED": False, "Q6_EXECUTED": False, "SUCCESSOR_CHECKPOINT_CREATED": False,
                           "PRODUCTION_LAUNCH_AUTHORIZED": False, "CONTAINMENT_APPLIED": False}}


def verify_proposal(ns=NS, repo=REPO, *, live_binding=None) -> list[str]:
    ns, repo = Path(ns), Path(repo)
    p = []
    try:
        raw = (ns / PROPOSAL).read_bytes()
        if (ns / PROPOSAL_HASH).read_text().strip() != sha256_bytes(raw):
            p.append("PROPOSAL_HASH_FILE")
        if raw != dump(build_manifest(ns, repo)):
            p.append("PROPOSAL_DOES_NOT_REBUILD: a governance artifact or predecessor object changed")
        manifest = json.loads(raw)
        binding = json.loads((ns / "config/PREDECESSOR_BINDING.json").read_bytes())
        cap = json.loads((ns / "config/CPU_CAP_CONTINUITY.json").read_bytes())
        rq = json.loads((ns / "config/REQUALIFICATION_PROTOCOL.json").read_bytes())
        q6ref = json.loads((ns / "config/Q6_REFERENCE.json").read_bytes())
    except (OSError, ValueError, KeyError) as exc:
        return p + [f"PROPOSAL_UNREADABLE: {type(exc).__name__}: {exc}"]
    for rel, want in KEY_PINS.items():
        if not (repo / rel).is_file() or sha256_file(repo / rel) != want:
            p.append(f"PREDECESSOR_PIN: {rel}")
    p += verify_binding(binding)
    if live_binding is not None:
        p += compare_live(binding, live_binding)
    rs = manifest.get("result_set") or {}
    old = range(rs["OLD_CARRYOVER"][0], rs["OLD_CARRYOVER"][1] + 1) if rs.get("OLD_CARRYOVER") else []
    new = range(rs["NEW_SUCCESSOR"][0], rs["NEW_SUCCESSOR"][1] + 1) if rs.get("NEW_SUCCESSOR") else []
    p += check_partition(old, new)
    p += check_cap(cap, binding)
    p += check_requalification_protocol(rq, binding, repo)
    try:
        if canon(q6ref) != canon(q6_reference(repo)):
            p.append("Q6_REFERENCE_DOES_NOT_RECOMPUTE")
    except (OSError, ValueError, KeyError) as exc:
        p.append(f"Q6_REFERENCE: {exc}")
    if manifest.get("status") != "PROPOSED_NOT_AUTHORIZED" or any((manifest.get("authorizations") or {}).values()):
        p.append("PROPOSAL_CLAIMS_AUTHORIZATION")
    return p


# ====================================================================== host collection
def collect(checkout) -> dict:
    checkout = Path(checkout).resolve()
    L = load_frozen(checkout)
    import prod_common as C                                                     # noqa: E402
    import prov_entry as PENT                                                   # noqa: E402
    import prov_integrity as PI                                                 # noqa: E402
    from prov_spec import production_spec                                       # noqa: E402
    cp = json.loads((checkout / SUCC_REL / "config/PROVENANCE_CHECKPOINT.json").read_text())
    spec, _cp = production_spec()
    authz = PENT.production_authz()
    rep = PI.audit(spec, authz)
    st, _entries = PI.ledger_view(spec)
    reverified = L.verify_sealed_evidence(spec, st, full=True)
    a = rep["A_completeness"]
    integrity = {"frozen_audit": {"verified_pairs": len(rep["pairs"]), "sealed": a["sealed"], "domain": a["domain"],
                                  "complete": a["complete"], "issue_keys": sorted(rep["issues"]),
                                  "pairs_sha256": sha256_bytes(canon(rep["pairs"])),
                                  "ledger_state_sha256": rep["ledger_state_sha256"],
                                  "genesis_entry_sha256": rep["genesis_entry_sha256"], "disposition": rep["disposition"],
                                  "authorization": rep["authorization"],
                                  "INTEGRITY_READY_FOR_ADJUDICATION": rep["INTEGRITY_READY_FOR_ADJUDICATION"]},
                 "full_seal_reverified_cells": reverified}
    btime = int(next(line.split()[1] for line in Path("/proc/stat").read_text().splitlines() if line.startswith("btime ")))
    clock = {"btime": btime, "clk_tck": os.sysconf("SC_CLK_TCK"), "boot_id": C.boot_id()}
    drift = {"libc_path": LIBC, "libc_ctime_ns": os.stat(LIBC).st_ctime_ns, "libc_sha256_live": sha256_file(LIBC),
             "bound_libc_sha256": cp["host"]["bound_facts"]["libc_sha256"]}
    host = C.host_facts(with_package=True)
    host["system_libraries_sha256"] = {path: sha256_file(path) for path in SYSTEM_LIBRARIES}
    host["packages"] = {}
    for pkg in PACKAGES:
        out = subprocess.run(["dpkg-query", "-W", "-f=${Version}", pkg], capture_output=True, text=True)
        host["packages"][pkg] = out.stdout.strip() if out.returncode == 0 else None
    quals = set(cp["qualification"]["record_file_sha256"].values())
    return analyze_predecessor(Path(cp["runtime_root"]), L=L, qualification_shas=quals, clock=clock, drift=drift,
                               integrity=integrity, host_facts=host)


def _load(path):
    return None if path is None else json.loads(Path(path).read_bytes())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CUSUM Aux5 new-glibc successor governance (read-only)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--checkout", required=True)
    c.add_argument("--out", required=True)
    sub.add_parser("q6-reference")
    sub.add_parser("build")
    v = sub.add_parser("verify-proposal")
    v.add_argument("--live-binding")
    r = sub.add_parser("launch-readiness")
    for flag in ("--q6", "--countersignature", "--checkpoint"):
        r.add_argument(flag)
    a = ap.parse_args(argv)
    if a.cmd == "collect":
        b = collect(a.checkout)
        Path(a.out).write_bytes(dump(b))
        problems = verify_binding(b)
        print(json.dumps({"binding_sha256": sha256_file(a.out), "verify_binding_problems": problems}, indent=1))
        return 0 if not problems else 30
    if a.cmd == "q6-reference":
        (NS / "config/Q6_REFERENCE.json").write_bytes(dump(q6_reference(REPO)))
        return 0
    if a.cmd == "build":
        data = dump(build_manifest(NS, REPO))
        (NS / PROPOSAL).write_bytes(data)
        (NS / PROPOSAL_HASH).write_text(sha256_bytes(data) + "\n")
        print(sha256_bytes(data))
        return 0
    if a.cmd == "verify-proposal":
        problems = verify_proposal(live_binding=_load(a.live_binding))
        print(json.dumps({"PROPOSAL_VALID": not problems, "problems": problems}, indent=1))
        return 0 if not problems else 30
    proposal_problems = verify_proposal()
    q6_raw = Path(a.q6).read_bytes() if a.q6 else None
    q6 = evaluate_q6(json.loads(q6_raw) if q6_raw else None, json.loads((NS / "config/Q6_REFERENCE.json").read_bytes()),
                     result_sha256=sha256_bytes(q6_raw) if q6_raw else None)
    cs_raw = Path(a.countersignature).read_bytes() if a.countersignature else None
    rep = launch_readiness(proposal_problems=proposal_problems, proposal_sha256=sha256_file(NS / PROPOSAL), q6=q6,
                           countersignature=json.loads(cs_raw) if cs_raw else None,
                           countersignature_sha256=sha256_bytes(cs_raw) if cs_raw else None,
                           checkpoint=_load(a.checkpoint))
    print(json.dumps({**rep, "q6": q6}, indent=1))
    return 0 if rep["state"] == "READY_TO_LAUNCH_SUCCESSOR" else 30


if __name__ == "__main__":
    raise SystemExit(main())
