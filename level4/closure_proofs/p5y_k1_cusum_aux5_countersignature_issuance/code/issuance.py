"""Countersignature issuance protocol for the CUSUM Aux5 production-provenance successor. NON-CERTIFYING.

The frozen successor entrypoint (prov_entry.py preflight, P01-P10) is the LAUNCH gate. Its P07 only verifies that an
independent countersignature already exists, validates and is committed. Using that same predicate to decide whether
a reviewer may ISSUE the countersignature is circular. This module separates the two predicates and changes nothing
in the frozen successor: it imports the entrypoint read-only, adds no file to any bound or executor-globbed directory,
and never creates a countersignature.

  python issuance.py review-preflight --out F   Phase A: READY_FOR_COUNTERSIGNATURE | REVIEW_PASS_COUNTERSIGNED | BLOCKED
  python issuance.py launch-preflight --out F   Phase B: READY_TO_LAUNCH_PRODUCTION | NOT_READY

Phase A never yields a launch state. Phase B requires the unmodified frozen preflight to be READY (P01-P10 including
P07) AND the issuance bindings of a committed, reviewer-authored countersignature to verify. Exit 0 / 30.

r2 (runtime-root semantics). "Not started" is the frozen lifecycle's pre-genesis state, not path absence: the keeper
and CampaignLock.acquire create the runtime root before any preflight, and prod_ledger.Ledger.inspect is FRESH for a
root holding only PRE_GENESIS_FILES. classify_runtime_root accepts exactly that residue, fails closed on anything else,
and the countersignature binds the reaper evidence present at signing so it cannot be lost or rewritten before genesis.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
SUCC_NS = NS.parent / "p5y_k1_cusum_aux5_production_provenance_successor"
sys.path.insert(0, str(SUCC_NS / "code"))

import prov_schema as S                                                                 # noqa: E402
import prod_ledger as L                                                                 # noqa: E402
from prod_common import ROOT, Refusal, canonical, sha256_bytes, sha256_file             # noqa: E402
from prov_authorization import load_authorization, verify_countersignature              # noqa: E402
from prov_spec import (AUTHORIZATION, AUTHORIZATION_HASH, CHECKPOINT, COUNTERSIGNATURE,  # noqa: E402
                       FREEZE_RECORD, PRODUCTION_RUNTIME_ROOT)

ISSUANCE_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.countersignature-issuance.v2"
REVIEW_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.countersignature-review-preflight.v2"
LAUNCH_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.countersignature-launch-preflight.v2"

FROZEN_CHECKS = ("P01_checkpoint_and_freeze", "P02_bound_sources", "P03_predecessor_frozen_and_fenced",
                 "P04_inherited_sections_unchanged", "P05_provenance_schemas", "P06_run_authorization",
                 "P07_independent_countersignature", "P08_synthetic_acceptance", "P09_run_state", "P10_host_idle")
SIGNATURE_GATE = "P07_independent_countersignature"
SIGNATURE_ABSENT_CODE = "COUNTERSIGNATURE_MISSING"

REVIEW_READY = "READY_FOR_COUNTERSIGNATURE"
REVIEW_PASS_SIGNED = "REVIEW_PASS_COUNTERSIGNED"
BLOCKED = "BLOCKED"
REVIEW_STATES = (REVIEW_READY, REVIEW_PASS_SIGNED, BLOCKED)
LAUNCH_READY = "READY_TO_LAUNCH_PRODUCTION"
NOT_READY = "NOT_READY"
LAUNCH_STATES = (LAUNCH_READY, NOT_READY)
HISTORICAL_VERDICT = "BLOCKED_BY_COUNTERSIGNATURE_ISSUANCE_DEADLOCK"
EXIT_REFUSED = 30

AUTH_COMMIT = "9719cba2263c553bb134167504fb3f6fac60670f"
FREEZE_COMMIT = "292e432efaa2c43c185a62812be649031b8f42e1"
CAP_CPU_H = 300
USEC_PER_CPU_H = 3600 * 10**6
UNIVERSE_CELLS = 326

# Frozen lifecycle facts (prod_ledger.PRE_GENESIS_FILES, Paths, checkpoint lifecycle.exit_codes.REFUSED).
FROZEN_PRE_GENESIS_FILES = ("campaign.lock", "campaign.owner.json", "reaper.jsonl")
GENESIS_FILES = ("ledger.json", "journal.jsonl")
FROZEN_REFUSED_EXIT = 30
ROOT_ABSENT, ROOT_PRE_GENESIS, ROOT_STARTED, ROOT_CORRUPTED = "ABSENT", "PRE_GENESIS", "PRODUCTION_STARTED", "CORRUPTED"
ACCEPTABLE_ROOT_STATES = (ROOT_ABSENT, ROOT_PRE_GENESIS)
RESIDUE_KEYS = ("state", "entries", "reaper_sha256", "reaper_size", "reaper_record_ids", "overhead_usec")

SUCC_REL = str(SUCC_NS.relative_to(ROOT))
NS_REL = str(NS.relative_to(ROOT))
COUNTERSIGNATURE_REL = str(COUNTERSIGNATURE.relative_to(ROOT))
# Paths that may not change between the reviewed tip and the launch HEAD (the countersignature itself excepted).
WATCHED_PREFIXES = (f"{SUCC_REL}/code", f"{SUCC_REL}/config", f"{SUCC_REL}/tests", f"{SUCC_REL}/evidence",
                    f"{NS_REL}/code", f"{NS_REL}/tests")
REQUIRED_STATEMENTS = {"production_result_existed_at_signing": False, "aws_resource_touched": False,
                       "result_bearing_compute_during_review": False}


# ====================================================================== runtime root (pre-genesis vs started)
def _reaper_problems(data: bytes, out: dict) -> list[str]:
    """Every line must be a frozen-verifiable reaper record of a pre-genesis kind: a keeper exit, or a supervisor the
    keeper reaped with the frozen REFUSED exit code. Unreadable lines are refused here because the frozen read_reaper
    skips them silently, which would lose their CPU charge."""
    problems, ids, total = [], [], 0
    if data and not data.endswith(b"\n"):
        problems.append("REAPER_TORN_TAIL: reaper.jsonl does not end with a complete line")
    for i, line in enumerate(x for x in data.decode("utf-8", errors="replace").splitlines() if x.strip()):
        try:
            rec = json.loads(line)
            body = {k: v for k, v in rec.items() if k != "record_id"}
            ok = rec.get("schema") == L.REAPER_SCHEMA and rec.get("record_id") == sha256_bytes(canonical(body))
        except (ValueError, AttributeError):
            ok = False
        if not ok:
            problems.append(f"REAPER_CORRUPT: line {i} is not a verifiable reaper record")
            continue
        cpu = rec.get("cpu_usec")
        if not (isinstance(cpu, int) and not isinstance(cpu, bool) and cpu >= 0):
            problems.append(f"REAPER_CORRUPT: line {i} cpu_usec {cpu!r}")
            continue
        keeper = rec.get("kind") == "KEEPER_EXIT" and rec.get("is_supervisor") is False
        refused = (rec.get("kind") == "CHILD_REAPED" and rec.get("is_supervisor") is True and rec.get("exited") is True
                   and rec.get("exit_code") == FROZEN_REFUSED_EXIT)
        if not (keeper or refused):
            problems.append(f"REAPER_RECORD_NOT_PRE_GENESIS: line {i} kind {rec.get('kind')} supervisor "
                            f"{rec.get('is_supervisor')} exit {rec.get('exit_code')} signal {rec.get('signal')}")
            continue
        if rec["record_id"] in ids:
            problems.append(f"REAPER_DUPLICATE_RECORD: line {i}")
            continue
        ids.append(rec["record_id"])
        total += cpu
    out["reaper_record_ids"], out["overhead_usec"] = ids, total
    return problems


def classify_runtime_root(root, *, lock_state: str, bound_host: str) -> dict:
    """ABSENT | PRE_GENESIS | PRODUCTION_STARTED | CORRUPTED. Read-only. Only ABSENT and PRE_GENESIS are acceptable.

    PRODUCTION_STARTED iff a genesis artifact (ledger.json or journal.jsonl) exists: every reservation, admission,
    seal, provenance binding and overhead charge is a journalled transition after GENESIS. Any other entry outside
    the frozen PRE_GENESIS_FILES, a non-regular file, a held lock, an invalid owner or a reaper record that is not a
    refused launch or keeper exit is CORRUPTED (the frozen Ledger.inspect refuses such a root as well)."""
    root = Path(root)
    out = {"state": ROOT_CORRUPTED, "problems": [], "entries": [], "lock_state": lock_state, "reaper_sha256": None,
           "reaper_size": 0, "reaper_record_ids": [], "overhead_usec": 0}
    p = out["problems"]
    if tuple(L.PRE_GENESIS_FILES) != FROZEN_PRE_GENESIS_FILES:
        p.append(f"FROZEN_PRE_GENESIS_FILES_DRIFT: {L.PRE_GENESIS_FILES}")
        return out
    if not os.path.lexists(root):
        out["state"] = ROOT_ABSENT
        return out
    if root.is_symlink() or not root.is_dir():
        p.append("ROOT_NOT_A_DIRECTORY")
        return out
    out["entries"] = entries = sorted(x.name for x in root.iterdir())
    begun = [n for n in entries if n in GENESIS_FILES]
    if begun:
        out["state"] = ROOT_STARTED
        p.append(f"PRODUCTION_STARTED: genesis artifacts present {begun}")
        return out
    unknown = [n for n in entries if n not in FROZEN_PRE_GENESIS_FILES]
    if unknown:
        p.append(f"NOT_PRE_GENESIS: entries outside the frozen PRE_GENESIS_FILES {unknown[:6]}")
    for n in entries:
        if n in FROZEN_PRE_GENESIS_FILES and ((root / n).is_symlink() or not (root / n).is_file()):
            p.append(f"NOT_A_REGULAR_FILE: {n}")
    if lock_state != "FREE":
        p.append(f"CAMPAIGN_LOCK_{lock_state}: the campaign lock is not free")
    lock, owner, reaper = (root / n for n in FROZEN_PRE_GENESIS_FILES)
    if lock.is_file() and not lock.is_symlink() and lock.stat().st_size != 0:
        p.append("CAMPAIGN_LOCK_NOT_EMPTY")
    if owner.is_file() and not owner.is_symlink():
        try:
            o = json.loads(owner.read_text())
        except ValueError:
            o = None
        if not isinstance(o, dict) or o.get("host", bound_host) != bound_host:
            p.append("CAMPAIGN_OWNER_INVALID")
    if reaper.is_file() and not reaper.is_symlink():
        data = reaper.read_bytes()
        out["reaper_sha256"], out["reaper_size"] = sha256_bytes(data), len(data)
        p += _reaper_problems(data, out)
    if not p:
        out["state"] = ROOT_PRE_GENESIS
    return out


def residue_summary(rr) -> dict:
    rr = rr if isinstance(rr, dict) else {}
    return {k: rr.get(k) for k in RESIDUE_KEYS}


def residue_preserved(signed, live: dict, live_reaper: bytes) -> list[str]:
    """The pre-genesis evidence bound at signing must still be present, byte-for-byte, as a prefix of the live reaper.
    Later refused launches may only append further verifiable pre-genesis records (checked by the classifier)."""
    if not isinstance(signed, dict) or signed.get("state") not in ACCEPTABLE_ROOT_STATES:
        return ["RESIDUE: the countersignature binds no acceptable pre-genesis residue"]
    if live.get("state") not in ACCEPTABLE_ROOT_STATES:
        return [f"RESIDUE: live runtime root is {live.get('state')}"]
    if signed["state"] == ROOT_ABSENT:
        return []
    p = []
    size = signed.get("reaper_size")
    if live.get("state") != ROOT_PRE_GENESIS or not isinstance(size, int) or len(live_reaper) < size \
            or sha256_bytes(live_reaper[:size]) != signed.get("reaper_sha256"):
        p.append("RESIDUE_LOST_OR_REWRITTEN: the reaper evidence bound at signing is not a prefix of the live reaper")
    if not set(signed.get("reaper_record_ids") or []) <= set(live.get("reaper_record_ids") or []):
        p.append("RESIDUE_LOST_OR_REWRITTEN: a reaper record bound at signing is missing")
    return p


# ====================================================================== pure decisions
def _in_order(report: dict) -> bool:
    return tuple(c.get("check") for c in report.get("checks", [])) == FROZEN_CHECKS


def review_eligibility(report: dict) -> dict:
    """Phase A predicate over a frozen P01-P10 report. P07 is exempt ONLY when it fails for absence."""
    checks = {c.get("check"): c for c in report.get("checks", [])}
    problems = [] if _in_order(report) else ["the report does not carry exactly the frozen checks P01-P10 in order"]
    for name in FROZEN_CHECKS:
        c = checks.get(name) or {}
        if name != SIGNATURE_GATE and c.get("status") != "PASS":
            problems.append(f"{name}: {c.get('code', 'ABSENT')}")
    sig = checks.get(SIGNATURE_GATE) or {}
    if problems:
        state = BLOCKED
    elif sig.get("status") == "FAIL" and sig.get("code") == SIGNATURE_ABSENT_CODE:
        state = REVIEW_READY
    elif sig.get("status") == "PASS":
        state = REVIEW_PASS_SIGNED
    else:
        problems.append(f"{SIGNATURE_GATE}: {sig.get('code', 'ABSENT')} (a present but invalid countersignature is not "
                        "an absent one)")
        state = BLOCKED
    return {"state": state, "exempt_gate": SIGNATURE_GATE, "exempt_only_with_code": SIGNATURE_ABSENT_CODE,
            "problems": problems, "launch_authorized": False}


def signing_guard(facts: dict) -> list[str]:
    """Nothing of production may have started: the runtime root is ABSENT or exactly PRE_GENESIS."""
    problems = []
    rr = facts.get("runtime_root")
    if not isinstance(rr, dict) or rr.get("state") not in ACCEPTABLE_ROOT_STATES or rr.get("problems"):
        rr = rr if isinstance(rr, dict) else {}
        problems.append(f"PRODUCTION_ROOT_NOT_PRE_GENESIS: {rr.get('state')} {(rr.get('problems') or [])[:4]}")
    elif facts.get("production_root_exists") is not (rr["state"] == ROOT_PRE_GENESIS):
        problems.append("PRODUCTION_ROOT_FACTS_INCONSISTENT")
    if facts.get("production_processes"):
        problems.append(f"PRODUCTION_PROCESS_PRESENT: {facts['production_processes'][:4]}")
    if facts.get("result_bearing_cells") != 0:
        problems.append(f"RESULT_BEARING_CELLS_PRESENT: {facts.get('result_bearing_cells')}")
    if facts.get("predecessor_ledger_exists") is not False:
        problems.append("PREDECESSOR_LEDGER_PRESENT")
    if facts.get("checkout_clean") is not True:
        problems.append("CHECKOUT_DIRTY: tracked files differ from HEAD")
    return problems


def review_decision(report: dict, facts: dict, temporal_problems: list[str]) -> dict:
    elig = review_eligibility(report)
    guard = signing_guard(facts)
    state = elig["state"]
    if state == REVIEW_READY and (guard or temporal_problems):
        state = BLOCKED
    return {"state": state, "signing_permitted": state == REVIEW_READY, "launch_authorized": False,
            "eligibility": elig, "signing_guard_problems": guard, "temporal_problems": list(temporal_problems)}


def launch_eligibility(report: dict, binding_problems: list[str], facts: dict) -> dict:
    """Phase B predicate: the unmodified frozen preflight READY plus verified issuance bindings plus not started."""
    problems = []
    if report.get("ready") is not True or not _in_order(report) or any(c.get("status") != "PASS" for c in report["checks"]):
        problems.append("the frozen preflight P01-P10 is not READY: "
                        f"{[(c.get('check'), c.get('code')) for c in report.get('checks', []) if c.get('status') != 'PASS']}")
    problems += list(binding_problems)
    problems += signing_guard(facts)
    return {"state": LAUNCH_READY if not problems else NOT_READY, "problems": problems}


def check_issuance_binding(cs: dict, *, auth: dict, auth_sha: str, checkpoint_sha: str, freeze_sha: str, git,
                           watched=WATCHED_PREFIXES) -> list[str]:
    """Bindings a countersignature must carry beyond what frozen P07 checks. Returns problems (empty == PASS)."""
    p = []
    iss = cs.get("issuance")
    if not isinstance(iss, dict) or iss.get("schema") != ISSUANCE_SCHEMA:
        return [f"ISSUANCE_BLOCK: missing, or not schema {ISSUANCE_SCHEMA} (a countersignature issued under older "
                "issuance semantics is stale)"]
    for key, want in (("authorization_sha256", auth_sha), ("production_checkpoint_sha256", checkpoint_sha),
                      ("freeze_record_sha256", freeze_sha), ("production_run_id", auth["production_run_id"])):
        if cs.get(key) != want:
            p.append(f"BINDING: {key} differs from the live object")
    if cs.get("verdict") != S.APPROVED or cs.get("mode") != "PRODUCTION" or cs.get("synthetic") is not False:
        p.append("BINDING: verdict / mode / synthetic")
    if auth.get("production_checkpoint_sha256") != checkpoint_sha:
        p.append("BINDING: the live authorization binds another checkpoint")
    for key, want in (("authorization_commit", AUTH_COMMIT), ("freeze_commit", FREEZE_COMMIT),
                      ("authorization_id", auth["authorization_id"]), ("ledger_id", auth["ledger"]["ledger_id"]),
                      ("runtime_root", auth["ledger"]["runtime_root"]), ("producer", auth["producer"]),
                      ("host", auth["host"]), ("runtime_contract_hash", auth["runtime"]["runtime_contract_hash"]),
                      ("universe", auth["universe"])):
        if iss.get(key) != want:
            p.append(f"BINDING: issuance.{key} differs from the authorization")
    if (auth["universe"].get("cells") != UNIVERSE_CELLS or (iss.get("universe") or {}).get("cells") != UNIVERSE_CELLS):
        p.append("BINDING: universe is not the 326-cell universe")
    cap = iss.get("cap") or {}
    if not (cap.get("cap_cpu_h") == CAP_CPU_H and cap.get("cap_usec") == CAP_CPU_H * USEC_PER_CPU_H
            == auth["cap"]["cap_usec"]):
        p.append("BINDING: cap is not the authorized 300 CPU-h")
    if iss.get("review_verdict") != "PASS" or iss.get("review_state") != REVIEW_READY:
        p.append("REVIEW: verdict is not PASS / READY_FOR_COUNTERSIGNATURE")
    for key, want in REQUIRED_STATEMENTS.items():
        if (iss.get("statements") or {}).get(key) is not want:
            p.append(f"STATEMENT: {key} must be {want}")

    head, tip = git.head(), iss.get("reviewed_tip", "")
    if not git.is_ancestor(FREEZE_COMMIT, tip):
        p.append("STALE_REVIEWER_BASE: the reviewed tip does not contain the freeze commit")
    if not git.is_ancestor(tip, head):
        p.append("STALE_REVIEWER_BASE: HEAD does not descend from the reviewed tip")
    drift = sorted(x for x in git.changed_paths(tip, head, list(watched)) if x != COUNTERSIGNATURE_REL)
    if drift:
        p.append(f"MUTATED_SINCE_REVIEW: {drift[:6]}")

    ev = iss.get("review_evidence") or {}
    raw = git.show(ev.get("commit", ""), ev.get("path", "")) if ev.get("commit") and ev.get("path") else None
    if raw is None or not git.is_ancestor(ev.get("commit", ""), head) or not git.is_ancestor(tip, ev.get("commit", "")):
        return p + ["REVIEW_EVIDENCE: not committed between the reviewed tip and HEAD"]
    if sha256_bytes(raw) != ev.get("sha256"):
        return p + ["REVIEW_EVIDENCE: sha256 differs from the committed evidence"]
    rec = json.loads(raw)
    d = rec.get("decision") or {}
    if (rec.get("schema") != REVIEW_SCHEMA or d.get("state") != REVIEW_READY or rec.get("head") != tip
            or rec.get("authorization_sha256") != auth_sha or rec.get("provenance_checkpoint_sha256") != checkpoint_sha
            or rec.get("freeze_record_sha256") != freeze_sha):
        p.append("REVIEW_EVIDENCE: not a READY_FOR_COUNTERSIGNATURE review of these objects at the reviewed tip")
    facts = rec.get("facts") or {}
    if signing_guard(facts):
        p.append("REVIEW_EVIDENCE: production state was not pre-genesis at review time")
    if iss.get("pre_genesis_residue") != residue_summary(facts.get("runtime_root")):
        p.append("REVIEW_EVIDENCE: issuance.pre_genesis_residue is not the residue recorded by the review")
    return p


# ====================================================================== live facts (host)
class Git:
    def _run(self, *args) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True)

    def head(self) -> str:
        return self._run("rev-parse", "HEAD").stdout.decode().strip()

    def is_ancestor(self, a: str, b: str) -> bool:
        return bool(a) and bool(b) and self._run("merge-base", "--is-ancestor", a, b).returncode == 0

    def changed_paths(self, a: str, b: str, paths: list[str]) -> list[str]:
        r = self._run("diff", "--name-only", a, b, "--", *paths)
        return r.stdout.decode().split() if r.returncode == 0 else ["<git diff failed>"]

    def show(self, commit: str, path: str):
        r = self._run("show", f"{commit}:{path}")
        return r.stdout if r.returncode == 0 else None

    def commit_time(self, commit: str) -> int:
        return int(self._run("log", "-1", "--format=%ct", commit).stdout.decode().strip() or 0)

    def clean(self) -> bool:
        r = self._run("status", "--porcelain", "--untracked-files=no")
        return r.returncode == 0 and not r.stdout.strip()


def _lock_state(root: Path) -> str:
    if not (root / "campaign.lock").is_file():
        return "FREE"
    try:
        return L.CampaignLock(root).probe()
    except OSError as exc:
        return f"UNPROBEABLE_{type(exc).__name__}"


def host_facts(git: Git, bound_host: str) -> dict:
    import prov_entry as PENT
    from prod_common import processes_matching
    root = Path(PRODUCTION_RUNTIME_ROOT)
    rr = classify_runtime_root(root, lock_state=_lock_state(root) if root.is_dir() else "FREE", bound_host=bound_host)
    cells = {e.name for e in root.glob("provenance/*/CUSUM_*.envelope.json")} if root.is_dir() else set()
    return {"host_name": os.uname().nodename, "production_runtime_root": str(root),
            "production_root_exists": os.path.lexists(root), "runtime_root": rr,
            "production_processes": [p for p in processes_matching(PENT.MARKERS) if p["pid"] != os.getpid()],
            "result_bearing_cells": len(cells),
            "predecessor_ledger_exists": (Path(S.PREDECESSOR["runtime_root"]) / "ledger.json").exists(),
            "checkout_clean": git.clean(), "countersignature_present": COUNTERSIGNATURE.exists()}


def temporal_checks(git: Git, *, auth_sha: str, checkpoint_sha: str, freeze_sha: str) -> list[str]:
    p = []
    head = git.head()
    if not (git.is_ancestor(AUTH_COMMIT, FREEZE_COMMIT) and git.is_ancestor(FREEZE_COMMIT, head)):
        p.append("ANCESTRY: authorization commit -> freeze commit -> HEAD does not hold")
    for commit, path, want in ((AUTH_COMMIT, str(AUTHORIZATION.relative_to(ROOT)), auth_sha),
                               (FREEZE_COMMIT, str(FREEZE_RECORD.relative_to(ROOT)), freeze_sha),
                               (FREEZE_COMMIT, str(CHECKPOINT.relative_to(ROOT)), checkpoint_sha)):
        raw = git.show(commit, path)
        if raw is None or sha256_bytes(raw) != want:
            p.append(f"PREDATES: {path} at {commit[:12]} is not the live object")
    ta, tf = git.commit_time(AUTH_COMMIT), git.commit_time(FREEZE_COMMIT)
    if not (0 < ta <= tf <= time.time()):
        p.append("PREDATES: authorization / freeze commit times are not ordered before now")
    return p


def _live_hashes() -> dict:
    _auth, asha = load_authorization(AUTHORIZATION, AUTHORIZATION_HASH)
    return {"authorization_sha256": asha, "provenance_checkpoint_sha256": sha256_file(CHECKPOINT),
            "freeze_record_sha256": sha256_file(FREEZE_RECORD)}


def _base(schema: str, git: Git, report: dict) -> dict:
    return {"schema": schema, "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "head": git.head(),
            **_live_hashes(), "issuance_code_sha256": sha256_file(Path(__file__)),
            "frozen_preflight": report, "production_launched": False, "historical_verdict": HISTORICAL_VERDICT}


def review_preflight() -> dict:
    import prov_entry as PENT
    git = Git()
    auth, _asha = load_authorization(AUTHORIZATION, AUTHORIZATION_HASH)
    report = PENT.preflight()
    facts = host_facts(git, auth["host"]["host_name"])
    h = _live_hashes()
    temporal = temporal_checks(git, auth_sha=h["authorization_sha256"], checkpoint_sha=h["provenance_checkpoint_sha256"],
                               freeze_sha=h["freeze_record_sha256"])
    return {**_base(REVIEW_SCHEMA, git, report), "facts": facts, "decision": review_decision(report, facts, temporal)}


def launch_preflight() -> dict:
    import prov_entry as PENT
    git = Git()
    report = PENT.preflight()
    auth, asha = load_authorization(AUTHORIZATION, AUTHORIZATION_HASH)
    facts = host_facts(git, auth["host"]["host_name"])
    h = _live_hashes()
    try:
        cs, cs_sha = verify_countersignature(COUNTERSIGNATURE, auth=auth, auth_sha=asha, freeze_record_sha256=h["freeze_record_sha256"])
        binding = check_issuance_binding(cs, auth=auth, auth_sha=asha, checkpoint_sha=h["provenance_checkpoint_sha256"],
                                         freeze_sha=h["freeze_record_sha256"], git=git)
        reaper = Path(PRODUCTION_RUNTIME_ROOT) / "reaper.jsonl"
        live_reaper = reaper.read_bytes() if facts["runtime_root"]["state"] == ROOT_PRE_GENESIS and reaper.is_file() else b""
        binding += residue_preserved((cs.get("issuance") or {}).get("pre_genesis_residue"), facts["runtime_root"], live_reaper)
    except Refusal as r:
        cs_sha, binding = None, [f"{r.code}: {r.detail}"]
    return {**_base(LAUNCH_SCHEMA, git, report), "facts": facts, "countersignature_sha256": cs_sha,
            "issuance_binding_problems": binding, "decision": launch_eligibility(report, binding, facts)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CUSUM Aux5 countersignature issuance protocol (read-only)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("review-preflight", "launch-preflight"):
        sub.add_parser(name).add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rep = review_preflight() if a.cmd == "review-preflight" else launch_preflight()
    Path(a.out).write_text(json.dumps(rep, indent=1, sort_keys=True, default=str) + "\n")
    for c in rep["frozen_preflight"]["checks"]:
        print(f"  {c['status']:4s}  {c['check']}" + ("" if c["status"] == "PASS" else f"   [{c.get('code')}]"))
    rr = rep["facts"]["runtime_root"]
    print(f"RUNTIME_ROOT = {rr['state']}  entries {rr['entries']}  reaper {rr['reaper_sha256']}  "
          f"pre-genesis overhead {rr['overhead_usec']} usec  problems {rr['problems']}")
    d = rep["decision"]
    print(json.dumps({k: v for k, v in d.items() if k != "eligibility"}, indent=1, default=str))
    label = "CUSUM_AUX5_COUNTERSIGNATURE_REVIEW" if a.cmd == "review-preflight" else "CUSUM_AUX5_LAUNCH"
    print(f"{label} = {d['state']}")
    ok = d["state"] == (REVIEW_READY if a.cmd == "review-preflight" else LAUNCH_READY)
    return 0 if ok else EXIT_REFUSED


if __name__ == "__main__":
    raise SystemExit(main())
