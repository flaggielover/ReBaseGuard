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
from prod_common import ROOT, Refusal, sha256_bytes, sha256_file                        # noqa: E402
from prov_authorization import load_authorization, verify_countersignature              # noqa: E402
from prov_spec import (AUTHORIZATION, AUTHORIZATION_HASH, CHECKPOINT, COUNTERSIGNATURE,  # noqa: E402
                       FREEZE_RECORD, PRODUCTION_RUNTIME_ROOT)

ISSUANCE_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.countersignature-issuance.v1"
REVIEW_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.countersignature-review-preflight.v1"
LAUNCH_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.countersignature-launch-preflight.v1"

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

SUCC_REL = str(SUCC_NS.relative_to(ROOT))
NS_REL = str(NS.relative_to(ROOT))
COUNTERSIGNATURE_REL = str(COUNTERSIGNATURE.relative_to(ROOT))
# Paths that may not change between the reviewed tip and the launch HEAD (the countersignature itself excepted).
WATCHED_PREFIXES = (f"{SUCC_REL}/code", f"{SUCC_REL}/config", f"{SUCC_REL}/tests", f"{SUCC_REL}/evidence",
                    f"{NS_REL}/code", f"{NS_REL}/tests")
REQUIRED_STATEMENTS = {"production_result_existed_at_signing": False, "aws_resource_touched": False,
                       "result_bearing_compute_during_review": False}


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
    """Temporal preconditions at the moment of signing: nothing of production may exist yet."""
    problems = []
    if facts.get("production_root_exists") is not False:
        problems.append("PRODUCTION_ALREADY_STARTED: the successor production runtime root exists")
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
    problems += [p for p in signing_guard(facts)]
    return {"state": LAUNCH_READY if not problems else NOT_READY, "problems": problems}


def check_issuance_binding(cs: dict, *, auth: dict, auth_sha: str, checkpoint_sha: str, freeze_sha: str, git,
                           watched=WATCHED_PREFIXES) -> list[str]:
    """Bindings a countersignature must carry beyond what frozen P07 checks. Returns problems (empty == PASS)."""
    p = []
    iss = cs.get("issuance")
    if not isinstance(iss, dict) or iss.get("schema") != ISSUANCE_SCHEMA:
        return ["ISSUANCE_BLOCK: missing or wrong schema"]
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
    if signing_guard(rec.get("facts") or {}):
        p.append("REVIEW_EVIDENCE: production state was not pristine at review time")
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


def host_facts(git: Git) -> dict:
    import prov_entry as PENT
    from prod_common import processes_matching
    root = Path(PRODUCTION_RUNTIME_ROOT)
    cells = {e.name for e in root.glob("provenance/*/CUSUM_*.envelope.json")} if root.exists() else set()
    return {"host_name": os.uname().nodename, "production_runtime_root": str(root),
            "production_root_exists": root.exists(),
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
    report = PENT.preflight()
    facts = host_facts(git)
    h = _live_hashes()
    temporal = temporal_checks(git, auth_sha=h["authorization_sha256"], checkpoint_sha=h["provenance_checkpoint_sha256"],
                               freeze_sha=h["freeze_record_sha256"])
    return {**_base(REVIEW_SCHEMA, git, report), "facts": facts, "decision": review_decision(report, facts, temporal)}


def launch_preflight() -> dict:
    import prov_entry as PENT
    git = Git()
    report = PENT.preflight()
    facts = host_facts(git)
    auth, asha = load_authorization(AUTHORIZATION, AUTHORIZATION_HASH)
    h = _live_hashes()
    try:
        cs, cs_sha = verify_countersignature(COUNTERSIGNATURE, auth=auth, auth_sha=asha, freeze_record_sha256=h["freeze_record_sha256"])
        binding = check_issuance_binding(cs, auth=auth, auth_sha=asha, checkpoint_sha=h["provenance_checkpoint_sha256"],
                                         freeze_sha=h["freeze_record_sha256"], git=git)
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
    d = rep["decision"]
    print(json.dumps({k: v for k, v in d.items() if k != "eligibility"}, indent=1, default=str))
    label = "CUSUM_AUX5_COUNTERSIGNATURE_REVIEW" if a.cmd == "review-preflight" else "CUSUM_AUX5_LAUNCH"
    print(f"{label} = {d['state']}")
    ok = d["state"] == (REVIEW_READY if a.cmd == "review-preflight" else LAUNCH_READY)
    return 0 if ok else EXIT_REFUSED


if __name__ == "__main__":
    raise SystemExit(main())
