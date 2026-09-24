"""C11R rounds 4-8 -- THE FROZEN EXECUTION CONTRACT and the end-to-end identity chain.

ROUND 8 (review round 7; errata E56-E60). N7-1/N7-2: a boundary program runs only in an interpreter
started exactly as c11r_launch.py starts it (LAUNCH_POLICY, bound in the contract; L0) -- checked
by the pre-import barrier BEFORE any other import and again at every boundary
(launch_policy_problems); the launcher itself is started isolated by the kernel. N7-1 also: the
cache check models the interpreter's actual hash-based .pyc mode. N7-3: the barrier's rule is a
POSITIVE campaign-prefix rule (no standard-library enumeration), and the loaded-module snapshot is
taken after the check's own imports. Contract schema C11R_CONTRACT/5.

ROUND 7 (review round 6; errata E49-E55). R6-1: module identity is now keyed on LOCATION -- any
module loaded from a campaign code directory must be an approved, byte-verified source whatever
its name; origins must agree; nothing but those directories and the interpreter may precede the
standard library on sys.path; the code directories must hold exactly the inventory the contract
binds (`code_directories`, `frozen_code`, `module_identity`); and the boundary programs start
behind PREIMPORT_BARRIER. N6-2: protocol_history also checks every ref, stash and reflog entry of
the repository, and the lifecycle's claim is scoped (LIFECYCLE_SCOPE). N6-3: the comparison is
one transaction (COMPARISON_TRANSACTION). N6-5: every boundary refuses with a typed reason instead
of raising (TYPED_ERRORS, bound_path_problems). Contract schema C11R_CONTRACT/4.

ROUND 6 (review round 5; errata E39-E48). R5-1: execution PERMISSION was the authorization file
itself, so "guard DENY" after the run could only mean deleting the evidence the comparator needs;
the permission is now a separate record with a typed, forward-only LIFECYCLE (derived by
`lifecycle`, bound in the contract, required per boundary by STAGE_STATE). R5-2: loaded-module
identity is keyed on module NAMES and ORIGINS, load-bearing modules must be source-backed, each
boundary's import-time closure must be present, and code_dir_shadows refuses any file carrying a
contract module's import name. Also: every git call through c11r_common.git_run (replace
objects disabled; grafts and shallow history refused), the approved commit must be a full
self-naming id, the frozen path list bound at A is the one checked and includes all campaign
code, protocol directories may hold only their canonical file, and a qualification is stated to
be an attestation (QUALIFICATION_PROVES).

ROUND 5 (review round 4; errata E32-E36, E38). Blocker R4-1: the "untouched by every later commit"
check used `git log A..HEAD -- <paths>`, whose default history simplification hides a side branch
that edited, used and reverted a frozen file and was then merged. Now history is COMPLETE:
`frozen_state` enumerates every commit reachable after A with `git rev-list` (no pathspec, so no
simplification) and requires each to hold every frozen path in exactly A's state (HISTORY PURITY),
separately from TREE IDENTITY (the bytes now); `protocol_history` does the same for the runs,
comparison, authorization and qualification artifacts, and fixes their order (N4-10). Also: the
frozen path set now includes every pre-result artifact and the quarantine and is bound in the
contract; the qualification has a TYPED Q1-Q18 schema whose disposition is recomputed (N4-4);
`verify_loaded_modules` and `code_dir_shadows` check what a process actually imported (N4-3);
the gate is cross-checked against the contract's policy and statement table, and the run's code
closure must equal the runner's (N4-1).

THE ROOT OF TRUST. config/C11R_CONTRACT.json, as committed at the REVIEWED commit A. A commit
cannot contain its own hash, so A is not written into the contract: the Phase 13 authorization
names A, the runner and the comparator are given A, and every boundary checks that the contract
(and every other frozen path) in the tree is byte-identical to its version at A and that EVERY
commit reachable after A holds each of them in exactly that state.

WHAT THE CONTRACT BINDS, by CONTENT (sha256 of the bytes and the git blob id), never by name:
  * code: the transitive import closure of every load-bearing module (gate, policy, statement
    table, qualifier, runner, reconstruction, both certifiers, interval drift, guards, run schema,
    comparator, equivalence, cost, process detector, and this module), each with its role;
  * artifacts: the policy, the statement table and the cost artifact -- file digest, canonical
    body digest, stored sha256 field, schema, producer and producer digest, declared inputs;
  * scientific inputs: the registry the statement table was extracted from, by content-free id;
  * schemas: runs, qualification, authorization;
  * the selected configuration and the resource-cap policy (depth, panels, cap, RSS cap, safety
    factor), and the frozen comparison rule;
  * the predicates execution depends on, each with its production evaluator (G2, G8, G10, G18,
    G19, G20), which the gate must carry verbatim.
It carries no target result.

RECOMPUTE, NEVER TRUST. Every verifier here rebuilds the identities from actual bytes and compares
them with what was recorded. A stored `sha256` field is evidence; acceptance requires that the
canonical body hashes to it AND that the recomputed identity equals the contract's.

THE CHAIN. contract -> gate -> qualification -> authorization -> runner -> run -> seal ->
comparator. `verify_contract`, `verify_gate`, `verify_frozen_at`, `verify_qualification`,
`build_authorization` / `verify_authorization`, `runner_preflight` and `verify_run_identity` are the
production checks; c11r_qualify, c11r_runs and c11r_compare call them, and the chain controls
(code/c11r_chain.py) call the same functions on synthetic repositories.

Every function takes the repository root `repo`, so the controls can run the real checks against
a synthetic git repository; production passes the real one. This module reads only allowlisted
artifacts and Python source; it never reads the runs artifact (the comparator passes it in).

WHAT THE CHAIN DOES NOT COVER, stated exactly. (1) History is what is REACHABLE from HEAD and, for
the protocol artifacts, from any ref, stash or reflog entry of this repository (round 7, N6-2): a
run never committed, made in another clone, or reachable from nothing (deleted refs, expired
reflogs) is invisible to git; the protocol, the runner's pre-flight and the process detector bound
that, they do not prove its absence (LIFECYCLE_SCOPE).
(2) The loaded-module check establishes what the import system loaded, from which file, when it
runs, and what the code directories hold when a boundary program starts and when it is checked
(MODULE_IDENTITY_POLICY); a file placed after the pre-import barrier and removed before the check,
code run through exec/eval, a module that rewrites its own metadata or deletes its file once
executing, and in-memory patching of a module or of this verifier are NOT detected -- arbitrary
malicious runtime modification is out of scope. (3) A runs artifact
hand-written without running the frozen runner at all is detectable only by re-executing the
certifiers (see c11r_certificate). (4) The root of trust is the reviewed commit as named by the
user's Phase 13 authorization and supplied to the comparator; a wrong commit supplied by the
operator is refused only if its contract differs from the one the authorization and the frozen
paths carry.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_launch as L
import c11r_procs as PR
import c11r_schema as S

CONTRACT_SCHEMA = "C11R_CONTRACT/5"
QUAL_SCHEMA = "C11R_QUALIFICATION/5"
AUTH_SCHEMA = "C11R_AUTHORIZATION/5"
PERMISSION_SCHEMA = "C11R_EXECUTION_PERMISSION/1"
CONTRACT_REL = "config/C11R_CONTRACT.json"
GATE_REL = "config/N9R_GATE_C11R.json"
POLICY_REL = "config/C11R_POLICY.json"
STMT_REL = "evidence/table/C11R_N9_STATEMENTS.json"
COST_REL = "evidence/cost/C11R_COST.json"
QUAL_REL = "evidence/qualification/C11R_QUALIFICATION.json"
AUTH_REL = "config/C11R_AUTHORIZATION.json"
PERMISSION_REL = "config/C11R_EXECUTION_PERMISSION.json"
RUNS_REL = "evidence/runs/C11R_RUNS.json"
COMPARISON_REL = "evidence/comparison/C11R_COMPARISON.json"
BOUND_ARTIFACTS = {"policy": POLICY_REL, "statements": STMT_REL, "cost": COST_REL}
REGISTRY_REL = "level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json"
ROLES = {
    "gate_producer": "c11r_gate.py", "policy_producer": "c11r_policy.py",
    "statement_table_producer": "c11r_table.py", "qualifier": "c11r_qualify.py",
    "runner": "c11r_runs.py", "certificate_reconstruction": "c11r_certificate.py",
    "production_guards": "c11r_certificate.py", "supersolution_certifier": "c11r_idrift.py",
    "interval_drift": "c11r_idrift.py", "subsolution_certifier": "c11r_boxdata.py",
    "run_schema": "c11r_schema.py", "comparator": "c11r_compare.py",
    "statement_equivalence": "c11r_equiv.py", "execution_contract": "c11r_contract.py",
    "cost_producer": "c11r_cost.py", "process_detector": "c11r_procs.py",
    "launcher": "c11r_launch.py",
}
CODE_ROOTS = tuple(sorted(set(ROLES.values())))
REQUIRED_PREDICATES = {
    "G2": "c11r_certificate.py:reconstruct",
    "G8": "c11r_certificate.py:dispositions",
    "G10": "c11r_certificate.py:screen_order",
    "G18": "c11r_certificate.py:evaluate_target",
    "G19": "c11r_certificate.py:configuration_adherence",
    "G20": "c11r_contract.py:verify_run_identity",
    "G21": "c11r_contract.py:lifecycle",
}
HOST_KEYS = ("node", "machine", "cpu_brand", "ncpu", "python", "implementation")
# THE QUALIFICATION SCHEMA (review round 4, N4-4): exactly these items, each exactly once, each
# PASS or FAIL, each bound to the same contract, approved commit and qualifier. An item not in
# this table REFUSES the qualification (the frozen rule for unknown items). The overall
# disposition is RECOMPUTED from the items; a stored class is never trusted.
QUAL_ITEMS = {
    "Q1": "the execution contract and the gate verify from bytes",
    "Q2": "every frozen path equals the approved commit in the tree and in all reachable history",
    "Q3": "the frozen policy re-derives its configuration from the committed evidence",
    "Q4": "the certifiers and every loaded load-bearing module are the contract's",
    "Q5": "no forbidden import graph and no forbidden backend in the code closure",
    "Q6": "the original certifier's backend is absent from this environment",
    "Q7": "VALIDATION_CLASS = PASS",
    "Q8": "MUTATION_CLASS = PASS",
    "Q9": "FIREWALL_CLASS = PASS (a defence-in-depth heuristic)",
    "Q10": "LEAK_CLASS = PASS",
    "Q11": "the status verifier, RUN now, reports CONSISTENT",
    "Q12": "the equivalence comparator's self-test passes",
    "Q13": "scalar collapse re-exercised at the NON-TARGET scalar 5/2",
    "Q14": "K_e = Khat_e + atom re-exercised on NT",
    "Q15": "the chain controls pass",
    "Q16": "this host is the host the cost model was measured on",
    "Q17": "guard prerequisites: gate DENY, lifecycle FROZEN (no authorization, no execution "
           "permission, no runs), no campaign worker",
    "Q18": "disk space for the run",
}
# WHAT A QUALIFICATION PROVES, exactly (review 5, N5-1): it is an ATTESTATION record. Its typed
# schema proves the record's shape, its bindings (contract, approved commit, qualifier code, host)
# and that every required item is recorded PASS -- NOT that each check was executed: a record
# built by the production builder from eighteen PASS items passes it. The facts behind Q1, Q2,
# Q16 and Q17 are re-derived independently at authorization, pre-flight and comparison; the
# others rest on the operator running the frozen qualifier as the protocol prescribes.
QUALIFICATION_PROVES = ("shape, bindings and recorded statuses of an attestation; not the "
                        "execution of its checks (Q1, Q2, Q16, Q17 facts are re-derived at every "
                        "later boundary; the rest rest on the operator running the frozen "
                        "qualifier)")
QUAL_ITEM_STATUSES = ("PASS", "FAIL")
QUAL_UNKNOWN_ITEM_RULE = "REFUSE"
# The protocol artifacts whose appearance in ANY reachable commit is governed (review 4, R4-1).
PROTOCOL_PATHS = {"runs": RUNS_REL, "comparison": COMPARISON_REL,
                  "authorization": AUTH_REL, "qualification": QUAL_REL,
                  "permission": PERMISSION_REL}
# Directories that may hold ONLY their canonical protocol file (review 5, N5-12): a run or a
# comparison committed under another file name there is refused too.
PROTOCOL_DIRS = {"evidence/runs": ("C11R_RUNS.json",),
                 "evidence/comparison": ("C11R_COMPARISON.json",),
                 "evidence/qualification": ("C11R_QUALIFICATION.json",)}

# ---------------------------------------------------------------------------------------------
# THE EXECUTION LIFECYCLE (review round 5, blocker R5-1; erratum E39). Round 5 coupled two things
# in ONE file: the authorization was both the PERMISSION to execute and the HISTORICAL EVIDENCE
# the comparator verifies, and "guard DENY" could only mean deleting it -- so the runner's own
# closing instruction ("set the guard back to DENY") destroyed the evidence and made a valid run
# EXECUTION_INVALID, irrecoverably. They are now separate:
#   * the GATE's guard is frozen at A and always DENY: the approval gate never permits anything;
#   * the AUTHORIZATION (config/C11R_AUTHORIZATION.json) is immutable evidence: introduced ONCE,
#     never modified or removed;
#   * the EXECUTION PERMISSION (config/C11R_EXECUTION_PERMISSION.json) is the only switch, with
#     typed, forward-only transitions, each record bound to the authorization and to the record
#     before it; DENY never touches the authorization.
# The state is DERIVED from committed and on-disk facts by `lifecycle`, never stored.
# ---------------------------------------------------------------------------------------------
PERMISSION_TRANSITIONS = {"GRANT": "ALLOW", "EXECUTION_STARTED": "DENY",
                          "EXECUTION_COMPLETED": "DENY", "REVOKED_BEFORE_EXECUTION": "DENY"}
LIFECYCLE_STATES = ("FROZEN", "QUALIFIED", "AUTHORIZED", "EXECUTING", "EXECUTED_UNSEALED",
                    "SEALED", "COMPARED", "ABANDONED", "REVOKED_BEFORE_EXECUTION", "MALFORMED")
LIFECYCLE = [
    {"from": "FROZEN", "to": "QUALIFIED", "actor": "Phase 12: c11r_launch.py qualify",
     "event": "the qualification is written and committed", "writes": [QUAL_REL],
     "execution_permission_after": None},
    {"from": "QUALIFIED", "to": "AUTHORIZED",
     "actor": "Phase 13: build_authorization (authorization + permission GRANT)",
     "event": "the authorization AND the execution permission GRANT are committed in ONE commit",
     "writes": [AUTH_REL, PERMISSION_REL], "execution_permission_after": "ALLOW"},
    {"from": "AUTHORIZED", "to": "EXECUTING",
     "actor": "Phase 14: c11r_launch.py run -> c11r_runs.begin_execution",
     "event": "after the pre-flight passes and BEFORE any science, the runner replaces the "
              "permission on disk with DENY/EXECUTION_STARTED (not committed)",
     "writes": [PERMISSION_REL], "execution_permission_after": "DENY"},
    {"from": "EXECUTING", "to": "EXECUTED_UNSEALED",
     "actor": "Phase 14: c11r_runs.finish_execution",
     "event": "the runner writes the runs artifact and DENY/EXECUTION_COMPLETED bound to its "
              "digest (not committed)", "writes": [RUNS_REL, PERMISSION_REL],
     "execution_permission_after": "DENY"},
    {"from": "EXECUTED_UNSEALED", "to": "SEALED", "actor": "operator",
     "event": "the runs artifact and the DENY/EXECUTION_COMPLETED record are committed in ONE "
              "commit -- the seal; the authorization is not touched", "writes": [],
     "execution_permission_after": "DENY"},
    {"from": "SEALED", "to": "COMPARED", "actor": "Phase 15: c11r_launch.py compare",
     "event": "the comparator verifies under execution permission DENY and, only when every "
              "step passed and the comparison completed, writes the comparison exactly once "
              "(a refusal writes nothing and the state stays SEALED: COMPARISON_TRANSACTION)",
     "writes": [COMPARISON_REL], "execution_permission_after": "DENY"},
    {"from": "AUTHORIZED", "to": "REVOKED_BEFORE_EXECUTION", "actor": "operator (terminal)",
     "event": "a DENY/REVOKED_BEFORE_EXECUTION record is committed; nothing runs under A",
     "writes": [PERMISSION_REL], "execution_permission_after": "DENY"},
    {"from": "EXECUTING", "to": "ABANDONED", "actor": "operator (terminal)",
     "event": "an interrupted execution's DENY/EXECUTION_STARTED record is committed; nothing "
              "further runs or compares under A", "writes": [], "execution_permission_after": "DENY"},
]
# the state each production boundary requires; no boundary ever requires execution permission
# ALLOW except the runner's pre-flight
STAGE_STATE = {"authorize": "QUALIFIED", "run": "AUTHORIZED", "compare": "SEALED"}
# WHAT THE LIFECYCLE PROVES, and where (review 6, N6-2). Round 6's runner printed "nothing
# re-enables execution under this approved commit"; the reviewer re-executed on a SIBLING branch
# forked at the authorization, and after restoring the GRANT over an uncommitted
# EXECUTION_STARTED. protocol_history now also checks every commit reachable from ANY ref, from
# HEAD or from any reflog entry (the sibling branch is refused); the rest is stated, not claimed.
LIFECYCLE_SCOPE = (
    "Within this repository -- HEAD's complete history after the approved commit, and every "
    "commit reachable from any ref, from HEAD or from any reflog entry -- no valid forward "
    "transition re-enables execution: a runs artifact, a permission record other than the GRANT, "
    "or a comparison anywhere there refuses a new pre-flight (c11r_contract.protocol_history). "
    "NOT covered, and not claimed: an execution never committed (a process interrupted after "
    "EXECUTION_STARTED whose record is discarded and the GRANT restored from git leaves no trace "
    "-- the protocol requires committing that record instead: INTERRUPTED_EXECUTION), an "
    "execution in another clone of the repository, and commits reachable from nothing (deleted "
    "refs, expired reflogs, dangling objects).")
INTERRUPTED_EXECUTION = (
    f"if the runner stops before it prints its NEXT steps, commit {C.NS_REL}/{PERMISSION_REL} "
    f"exactly as it is on disk (DENY/EXECUTION_STARTED): the state becomes ABANDONED (terminal). "
    f"Restoring the GRANT from git instead erases the only record of the attempt and is outside "
    f"the protocol.")
# THE COMPARISON TRANSACTION (review 6, N6-3). Round 6's comparator wrote its artifact even when
# it refused before the loader, so a harmless cause (a Finder .DS_Store in evidence/runs) left an
# EXECUTION_INVALID file that made every later comparison refuse.
COMPARISON_TRANSACTION = (
    "verify steps 1-12 -> load the original magnitudes IF AND ONLY IF all pass -> compute -> "
    "write the comparison artifact exactly once (exclusive create). A refusal before the loader "
    "writes NOTHING and leaves the state SEALED; once its cause is removed -- without changing any "
    "frozen path or protocol record -- the comparator may be run again: a pre-load refusal saw no "
    "magnitude. A failure after the loader was entered writes nothing either and is reported as "
    "POST_LOAD_FAILURE; the magnitudes have then been read, so the comparator is not run again "
    "without the user's instruction.")


# ---------------------------------------------------------------------------------------------
# canonical identity
# ---------------------------------------------------------------------------------------------
def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def body_digest(obj: dict) -> str:
    """sha256 of the canonical body without its own sha256 field -- what write_evidence stores."""
    return C.sha256_bytes(canon({k: v for k, v in obj.items() if k != "sha256"}))


def _root(repo) -> pathlib.Path:
    return pathlib.Path(repo) if repo is not None else C.REPO


def artifact_bytes(repo, rel: str) -> bytes:
    """Bytes of an ALLOWLISTED artifact of this namespace in `repo`. Nothing else is read here."""
    for allowed in C.ALLOWED_NS_INPUTS:
        if allowed == rel:
            return (_root(repo) / C.NS_REL / allowed).read_bytes()
    raise ValueError(f"{rel!r} is not an allowlisted artifact")


def artifact_exists(repo, rel: str) -> bool:
    return (_root(repo) / C.NS_REL / rel).exists()


def load_artifact(repo, rel: str) -> dict:
    return json.loads(artifact_bytes(repo, rel))


def code_bytes(repo, rel: str) -> bytes:
    """Bytes of a Python module by repo-relative path (forced to .py)."""
    if not rel.endswith(".py"):
        raise ValueError(f"{rel!r} is not Python source")
    return (_root(repo) / rel).with_suffix(".py").read_bytes()


def closure_paths() -> list[str]:
    """The transitive import closure of every load-bearing root, from the real tree's graph."""
    paths: set[str] = set()
    for root in CODE_ROOTS:
        paths |= set(C.code_closure(C.HERE / root))
    return sorted(paths)


def code_identity(repo, rel: str) -> dict:
    p = _root(repo) / rel
    if not p.exists():
        return {"sha256": None, "git_blob": None}
    return {"sha256": C.sha256_bytes(code_bytes(repo, rel)), "git_blob": C.content_free_id(p)}


def artifact_identity(repo, rel: str) -> dict:
    if not artifact_exists(repo, rel):
        return {"path": rel, "present": False}
    raw = artifact_bytes(repo, rel)
    obj = json.loads(raw)
    prov = obj.get("provenance", {})
    return {"path": rel, "present": True, "file_sha256": C.sha256_bytes(raw),
            "body_sha256": body_digest(obj), "stored_sha256": obj.get("sha256"),
            "schema": obj.get("schema"), "producer": prov.get("producer"),
            "producer_sha256": prov.get("producer_sha256"),
            "declared_inputs": prov.get("inputs", {}),
            "git_blob": C.content_free_id(_root(repo) / C.NS_REL / rel)}


def ns_path(rel: str) -> str:
    return f"{C.NS_REL}/{rel}"


# ---------------------------------------------------------------------------------------------
# the contract
# ---------------------------------------------------------------------------------------------
def contract_body(repo=None) -> dict:
    """Everything the contract binds, recomputed from the bytes in `repo`."""
    body = _contract_body(repo)
    body["frozen_paths"] = frozen_paths(body)
    # review 6, R6-1: every approved source, and the exact inventory of the code directories
    body["frozen_code"] = frozen_code(repo, body["code"])
    body["code_directories"] = code_directories(repo)
    body["module_identity"] = dict(MODULE_IDENTITY_POLICY)
    body["launch_policy"] = dict(LAUNCH_POLICY)             # review 7, N7-1 / N7-2 (L0)
    return body


def _contract_body(repo=None) -> dict:
    paths = closure_paths()
    code = {rel: code_identity(repo, rel) for rel in paths}
    arts = {name: artifact_identity(repo, rel) for name, rel in BOUND_ARTIFACTS.items()}
    policy = load_artifact(repo, POLICY_REL)
    stmt = load_artifact(repo, STMT_REL)
    cost = load_artifact(repo, COST_REL)
    cfg = policy["configuration"]
    rule = stmt["comparison_semantics_frozen_before_results"]
    d = stmt["drift_domain"]
    by_name = {pathlib.PurePosixPath(rel).name: rel for rel in paths}
    return {
        "schema": CONTRACT_SCHEMA,
        "scope": {"campaign": "C11R", "cell": C.TARGET_CELL, "constants": list(C.SIX_CONSTANTS),
                  "drift_block": [d["e_lo"], d["e_hi"]],
                  "implemented": list(policy["target_scope"]["implementable_under_this_policy"]),
                  "not_implemented": ["D1", "D2"]},
        "approved_commit": ("NOT RECORDED HERE: a commit cannot contain its own hash. The Phase 13 "
                            "authorization names the reviewed commit A; every boundary checks "
                            "this file and every frozen path against A."),
        "roles": {role: by_name.get(mod) for role, mod in sorted(ROLES.items())},
        "code": code,
        "artifacts": arts,
        "scientific_inputs": {
            "registry_c2_for_the_statement_table": {
                "path": REGISTRY_REL,
                "content_free_id": C.content_free_id(_root(repo) / REGISTRY_REL),
                "note": "identity only; its content is never read outside the sanctioned reader"},
            "statement_table_drift_block": [d["e_lo"], d["e_hi"]]},
        "schemas": {"runs": S.RUNS_SCHEMA, "qualification": QUAL_SCHEMA,
                    "authorization": AUTH_SCHEMA, "contract": CONTRACT_SCHEMA},
        "configuration": {"depth": cfg["chosen"]["depth"], "panels": cfg["chosen"]["panels"],
                          "cap_seconds": cfg["cap_seconds"], "cap_rss_mb": cfg["cap_rss_mb"],
                          "safety_factor": cfg["safety_factor"],
                          "rule": cfg["rule"]},
        "comparison_rule": {"factor": rule.get("factor"), "rule_sha256": C.sha256_obj(rule)},
        "cost_host": {k: cost["host"].get(k) for k in HOST_KEYS},
        "required_predicates": dict(REQUIRED_PREDICATES),
        "qualification_items": dict(QUAL_ITEMS),
        "qualification_unknown_item_rule": QUAL_UNKNOWN_ITEM_RULE,
        "qualification_proves": QUALIFICATION_PROVES,
        "protocol_paths": {k: ns_path(v) for k, v in sorted(PROTOCOL_PATHS.items())},
        "protocol_dirs": {ns_path(k): list(v) for k, v in sorted(PROTOCOL_DIRS.items())},
        "lifecycle": {"states": list(LIFECYCLE_STATES), "transitions": LIFECYCLE,
                      "permission_schema": PERMISSION_SCHEMA,
                      "permission_transitions": dict(PERMISSION_TRANSITIONS),
                      "stage_state": dict(STAGE_STATE),
                      "authorization_is": "immutable evidence, introduced once, never modified "
                                          "or removed",
                      "gate_guard_is": "frozen at the approved commit, always DENY",
                      "scope": LIFECYCLE_SCOPE, "interrupted_execution": INTERRUPTED_EXECUTION,
                      "comparison_transaction": COMPARISON_TRANSACTION},
        "contains_target_results": False,
    }


COMPARED_KEYS = ("schema", "scope", "roles", "code", "artifacts", "scientific_inputs", "schemas",
                 "configuration", "comparison_rule", "cost_host", "required_predicates",
                 "qualification_items", "qualification_unknown_item_rule",
                 "qualification_proves", "protocol_paths", "protocol_dirs", "lifecycle",
                 "frozen_paths", "frozen_code", "code_directories", "module_identity",
                 "launch_policy", "contains_target_results")


def namespace_code() -> list[str]:
    """EVERY Python file of this campaign's code directory (review 5, N5-8): the producers of
    frozen artifacts and the status verifier Q11 runs are frozen too, not only the closure."""
    return sorted(f"{C.NS_REL}/code/{f.name}" for f in C.HERE.glob("*.py"))


def frozen_paths(contract: dict) -> list[str]:
    """Every path whose bytes the reviewed commit fixes: the code closure, EVERY Python file of
    the campaign's code directory, the bound artifacts and the namespace artifacts they declare
    as inputs, EVERY pre-result artifact (the qualifier reads them: review 4, N4-4), the
    quarantine (by object id only), the contract itself and the gate. The contract BINDS this
    list; the history checks use the list bound at the approved commit (review 5, N5-6)."""
    declared = {inp for a in contract["artifacts"].values()
                for inp in a.get("declared_inputs", {}) if inp.startswith(C.NS_REL + "/")}
    return sorted(set(contract["code"]) | set(namespace_code())
                  | {ns_path(a["path"]) for a in contract["artifacts"].values()}
                  | declared | {ns_path(r) for r in C.PRE_RESULT_ARTIFACTS}
                  | {ns_path(C.QUARANTINE_REL), ns_path(CONTRACT_REL), ns_path(GATE_REL)})


def verify_artifact_record(repo, name: str, rec: dict, code: dict) -> list[str]:
    p = []
    if not rec.get("present"):
        return [f"{name}: artifact absent"]
    if rec["stored_sha256"] != rec["body_sha256"]:
        p.append(f"{name}: stored sha256 field does not equal the recomputed body digest")
    prod = rec.get("producer")
    if prod not in code:
        p.append(f"{name}: producer {prod} is not in the bound code closure")
    elif code[prod]["sha256"] != rec.get("producer_sha256"):
        p.append(f"{name}: produced by other code than the bound {pathlib.PurePosixPath(prod).name}")
    for inp, dig in rec.get("declared_inputs", {}).items():
        short = inp[len(C.NS_REL) + 1:] if inp.startswith(C.NS_REL + "/") else None
        if short is not None and short in C.ALLOWED_NS_INPUTS:
            now = (C.sha256_bytes(artifact_bytes(repo, short))
                   if artifact_exists(repo, short) else None)
            if now != dig:
                p.append(f"{name}: declared input {pathlib.PurePosixPath(inp).name} changed")
    return p


# TYPED REFUSALS (review 6, N6-5): a load-bearing check that cannot be evaluated on the tree in
# front of it -- a symlink resolving outside the repository, a dangling one, a loop, a directory
# where a file belongs, unreadable JSON -- REFUSES with a typed reason; it never raises.
TYPED_ERRORS = (OSError, ValueError, KeyError, TypeError, AttributeError, RuntimeError,
                subprocess.CalledProcessError)


def not_evaluable(where: str, e: BaseException) -> str:
    return (f"{where}: refused -- not evaluable on this tree ({type(e).__name__}: "
            f"{str(e)[:160]})")


def bound_path_problems(repo, contract: dict | None) -> list[str]:
    """Path SHAPES, from lstat (review 6, N6-5): every code path of the contract is a regular
    FILE; every frozen path and protocol path is ABSENT or a regular FILE; every protocol directory
    is ABSENT or a real DIRECTORY. Never a symlink (inside, outside, dangling, a loop) or anything
    else -- each named with its kind instead of an exception."""
    root = _root(repo)
    if not isinstance(contract, dict):
        return []
    code = set(contract.get("code") or {}) | set(contract.get("frozen_code") or {})
    paths = sorted(set(contract.get("frozen_paths") or []) | code
                   | {ns_path(v) for v in PROTOCOL_PATHS.values()})
    p = []
    for rel in paths:
        k = C.path_kind(root / rel, inside=root)
        if k == "FILE" or (k == "ABSENT" and rel not in code):
            continue
        p.append(f"paths: {pathlib.PurePosixPath(rel).name} is {KIND_TEXT[k]}")
    for d in sorted(PROTOCOL_DIRS):
        k = C.path_kind(root / C.NS_REL / d, inside=root)
        if k not in ("ABSENT", "DIRECTORY"):
            p.append(f"paths: the protocol directory {d} is {KIND_TEXT[k]}")
    return p


def verify_contract(repo=None) -> dict:
    """Recompute the contract from bytes and compare it with the committed one; a tree on which
    that cannot be done is REFUSED with a typed reason (N6-5)."""
    try:
        return _verify_contract(repo)
    except TYPED_ERRORS as e:
        try:
            committed = load_artifact(repo, CONTRACT_REL)
        except TYPED_ERRORS:
            committed = None
        return {"problems": [not_evaluable("contract", e)] + bound_path_problems(repo, committed),
                "digest": None, "contract": None}


def _verify_contract(repo=None) -> dict:
    problems = []
    if not artifact_exists(repo, CONTRACT_REL):
        return {"problems": ["no execution contract"], "digest": None, "contract": None}
    raw = artifact_bytes(repo, CONTRACT_REL)
    obj = json.loads(raw)
    digest = body_digest(obj)
    if obj.get("sha256") != digest:
        problems.append("contract: stored sha256 field does not equal the recomputed body digest")
    now = contract_body(repo)
    for k in COMPARED_KEYS:
        if obj.get(k) != now.get(k):
            if k == "code":
                diff = sorted(rel for rel in set(obj.get("code", {})) | set(now["code"])
                              if obj.get("code", {}).get(rel) != now["code"].get(rel))
                problems.append(f"contract: code identity differs for "
                                f"{[pathlib.PurePosixPath(x).name for x in diff]}")
            elif k == "artifacts":
                diff = sorted(a for a in set(obj.get("artifacts", {})) | set(now["artifacts"])
                              if obj.get("artifacts", {}).get(a) != now["artifacts"].get(a))
                problems.append(f"contract: artifact identity differs for {diff}")
            else:
                problems.append(f"contract: {k} differs from the recomputed value")
    for name, rec in now["artifacts"].items():
        problems += verify_artifact_record(repo, name, rec, now["code"])
    prov = obj.get("provenance", {})
    me = now["code"].get(prov.get("producer"), {})
    if not me or me.get("sha256") != prov.get("producer_sha256"):
        problems.append("contract: produced by other code than the bound c11r_contract.py")
    problems += bound_path_problems(repo, obj)                 # N6-5
    problems += preimport_barrier_problems(repo)               # R6-1 (B)
    return {"problems": problems, "digest": digest, "contract": obj,
            "file_sha256": C.sha256_bytes(raw)}


# ---------------------------------------------------------------------------------------------
# COMPLETE reachable history (review round 4, blocker R4-1)
# ---------------------------------------------------------------------------------------------
# WHAT WAS WRONG. `git log A..HEAD -- <paths>` applies git's default history simplification: a
# merge whose tree equals one parent's (TREESAME) is followed down that parent only, so a side
# branch that edited a frozen file, used it and reverted it -- then merged with --no-ff -- was
# never listed. The seal check (`git log -- <runs path>`) had the same hole.
# THE METHOD NOW. No path-limited traversal anywhere. `git rev-list` WITHOUT a pathspec lists
# every commit reachable from HEAD and not from A -- side branches, merge commits and every
# parent of an octopus merge included; nothing is simplified. For EVERY such commit, the object
# id of EVERY frozen path is read with one `git cat-file --batch-check` (ids only, no content)
# and compared with A's. This is a STATE check, stronger than a per-parent-edge diff: it refuses
# any commit that ever held a frozen path in another state, whichever edge introduced it, and it
# needs no rename or TREESAME rule. Commits NOT reachable from HEAD (reset-away commits, unmerged
# branches, stashes, reflog-only objects) are outside history and are not examined; that is a
# stated limit, not a claim.
def _batch_ids(repo, pairs: list[tuple[str, str]]) -> dict[tuple[str, str], str | None]:
    """Object id of `commit:path` for many pairs in ONE git process; None when absent."""
    if not pairs:
        return {}
    r = C.git_run(_root(repo), "cat-file", "--batch-check=%(objectname) %(objecttype)",
                  input="".join(f"{c}:{path}\n" for c, path in pairs))
    lines = r.stdout.splitlines()
    if len(lines) != len(pairs):
        raise RuntimeError("git cat-file answered a different number of queries than it was asked")
    out = {}
    for pair, ln in zip(pairs, lines):
        parts = ln.split()
        if len(parts) == 2 and parts[1] in ("blob", "tree", "commit"):
            out[pair] = "gitobj:" + parts[0] + ("" if parts[1] == "blob" else f":{parts[1]}")
        else:
            out[pair] = None                     # "<query> missing": the path is absent there
    return out


def reachable_since(repo, approved_commit: str) -> list[str]:
    """EVERY commit reachable from HEAD and not from the approved commit (no pathspec, so no
    history simplification)."""
    return [x for x in C.git_in(_root(repo), "rev-list", f"{approved_commit}..HEAD").split() if x]


def parent_map(repo, approved_commit: str) -> dict[str, list[str]]:
    """commit -> parents, for every commit reachable after the approved one (one git call)."""
    out = {}
    for ln in C.git_in(_root(repo), "rev-list", "--parents", f"{approved_commit}..HEAD").splitlines():
        ids = ln.split()
        if ids:
            out[ids[0]] = ids[1:]
    return out


def contract_at(repo, commit: str) -> dict | None:
    """The execution contract AS COMMITTED at `commit` -- the root of trust when `commit` is the
    approved commit. None when that commit carries no contract."""
    rel = ns_path(CONTRACT_REL)
    if C.git_object_at(commit, rel, repo=_root(repo)) is None:
        return None
    return json.loads(C.blob_at_in(_root(repo), commit, rel))


FULL_OID = re.compile(r"[0-9a-f]{40}")


def approved_commit_problems(repo, approved_commit) -> list[str]:
    """The root of trust is an IMMUTABLE commit id (review 5, N5-7): a full 40-hex object id that
    names a commit and that `rev-parse --verify` maps to itself -- never a tag, a branch, an
    abbreviation or a revision expression, whose target can move."""
    if not isinstance(approved_commit, str) or not FULL_OID.fullmatch(approved_commit):
        return [f"approved commit {approved_commit!r} is not a full 40-hex commit id (a tag, "
                f"branch, abbreviation or expression can move)"]
    r = C.git_run(_root(repo), "rev-parse", "--verify", "--quiet", f"{approved_commit}^{{commit}}",
                  check=False)
    if r.returncode != 0:
        return [f"approved commit {approved_commit!r} does not exist in this repository"]
    if r.stdout.strip() != approved_commit:
        return [f"approved commit {approved_commit!r} does not name itself"]
    return []


def frozen_state(repo, approved_commit: str) -> dict:
    """Three SEPARATE properties, each required (review 4, R4-1):
      ANCESTRY        -- HEAD descends from the approved commit;
      TREE IDENTITY   -- the bytes NOW equal the approved bytes (every frozen path, and no
                         uncommitted change to any of them);
      HISTORY PURITY  -- EVERY commit reachable after the approved commit holds every frozen
                         path in exactly the approved state; an edit that was used and reverted
                         -- on any branch, merged in any way -- is refused although the tree is
                         identical again."""
    root = _root(repo)
    out = {"ancestry": [], "tree_identity": [], "history_purity": [], "commits_checked": 0,
           "paths_checked": 0, "method": "rev-list A..HEAD (no pathspec, replace objects "
                                         "disabled) + cat-file state check"}
    integ = C.history_integrity(root)
    out["ancestry"] += integ["problems"]
    out["replace_refs_ignored"] = integ["replace_refs_ignored"]
    bad = approved_commit_problems(repo, approved_commit)
    if bad:
        out["ancestry"] += bad
        return out
    if not C.git_ok_in(root, "merge-base", "--is-ancestor", approved_commit, "HEAD"):
        out["ancestry"].append("HEAD does not descend from the approved commit")
    contract = contract_at(repo, approved_commit)       # the frozen path set is A's, not the tree's
    if contract is None:
        out["ancestry"].append("the approved commit carries no execution contract")
        return out
    paths = contract.get("frozen_paths")
    if not isinstance(paths, list) or not paths:
        out["ancestry"].append("the approved contract binds no frozen path set")
        return out
    out["paths_checked"] = len(paths)
    approved = {rel: v for (_, rel), v in
                _batch_ids(repo, [(approved_commit, rel) for rel in paths]).items()}
    for rel in paths:
        if approved.get(rel) != C.content_free_id(root / rel):
            out["tree_identity"].append(f"tree identity: frozen path "
                                        f"{pathlib.PurePosixPath(rel).name} differs from the "
                                        f"approved commit")
    if C.git_in(root, "status", "--porcelain", "--untracked-files=all", "--", *paths):
        out["tree_identity"].append("tree identity: a frozen path has uncommitted changes")
    commits = reachable_since(repo, approved_commit)
    out["commits_checked"] = len(commits)
    ids = _batch_ids(repo, [(c, rel) for c in commits for rel in paths])
    for c in commits:
        bad = sorted({pathlib.PurePosixPath(rel).name for rel in paths
                      if ids[(c, rel)] != approved.get(rel)})
        if bad:
            out["history_purity"].append(f"history purity: commit {c[:12]} touched a frozen path: "
                                         f"it holds {bad} in a state other than the approved "
                                         f"commit's")
    # TOPOLOGY POLICY (review 5, N5-5), stated: this is a STATE check over every reachable
    # commit not reachable from A, so merging ANY branch that forked before A (main, for one)
    # after the approval is refused -- its commits hold pre-A states of frozen paths. The
    # protocol needs no such merge; a new freeze is the path to integrate other history.
    return out


def protocol_artifacts_anywhere(repo=None) -> dict:
    """Every commit reachable from ANY ref, from HEAD or from any reflog entry that holds a
    protocol artifact (runs, comparison, authorization, qualification, execution permission) or
    ANY file under a protocol directory -- the PRE-RESULT state check. Enumerated with `rev-list
    --all --reflog` (no pathspec, replace objects disabled) and one cat-file batch. Dangling
    objects referenced by nothing are outside every history and are not examined."""
    names = {k: ns_path(v) for k, v in PROTOCOL_PATHS.items()}
    dirs = {d: ns_path(d) for d in PROTOCOL_DIRS}
    commits = sorted(set(C.git_in(_root(repo), "rev-list", "--all", "--reflog", "HEAD").split()))
    ids = _batch_ids(repo, [(c, rel) for c in commits
                            for rel in list(names.values()) + list(dirs.values())])
    holders = {k: sorted(c for c in commits if ids[(c, rel)] is not None)
               for k, rel in sorted(names.items())}
    holders.update({f"dir:{d}": sorted(c for c in commits if ids[(c, rel)] is not None)
                    for d, rel in sorted(dirs.items())})
    return {"commits_checked": len(commits), "holders": holders,
            "history_integrity": C.history_integrity(_root(repo))}


def verify_frozen_at(repo, approved_commit: str) -> list[str]:
    st = frozen_state(repo, approved_commit)
    return st["ancestry"] + st["tree_identity"] + st["history_purity"]


def artifact_at(repo, commit: str, rel: str) -> dict | None:
    """An ALLOWLISTED artifact as committed at `commit` (None when absent there)."""
    if rel not in C.ALLOWED_NS_INPUTS:
        raise ValueError(f"{rel!r} is not an allowlisted artifact")
    if C.git_object_at(commit, ns_path(rel), repo=_root(repo)) is None:
        return None
    return json.loads(C.blob_at_in(_root(repo), commit, ns_path(rel)))


def _unexpected_protocol_files(repo, commit: str) -> list[str]:
    out = C.git_in(_root(repo), "ls-tree", "-r", "--name-only", "--full-tree", commit, "--",
                   *[ns_path(d) for d in PROTOCOL_DIRS])
    bad = []
    for path in out.splitlines():
        d, _, name = path.rpartition("/")
        allowed = PROTOCOL_DIRS.get(d[len(C.NS_REL) + 1:] if d.startswith(C.NS_REL + "/") else d)
        if allowed is None or name not in allowed:
            bad.append(path)
    return bad


def protocol_history(repo, approved_commit: str, stage: str) -> dict:
    """The protocol artifacts across COMPLETE reachable history (review 4, R4-1 and N4-10;
    review 5, R5-1 and N5-12).
      at A           : no protocol artifact exists at the approved commit;
      protocol dirs  : evidence/runs, evidence/comparison and evidence/qualification hold only
                       their canonical file in every commit (a run renamed there is refused);
      comparison     : in NO commit after A, at any stage (a prior comparison saw the values);
      runs           : stage authorize/run -- in no commit (a prior, discarded execution);
                       stage compare -- only the sealed content, introduced by ONE commit;
      authorization  : stage authorize -- in no commit; later -- only the current content,
                       introduced ONCE, never modified or removed (immutable evidence);
      qualification  : only the current content, introduced once, committed at HEAD;
      permission     : stage authorize -- in no commit; stage run -- only the GRANT, introduced
                       in the SAME commit as the authorization; stage compare -- only the GRANT
                       and the final DENY/EXECUTION_COMPLETED record, the latter introduced in the
                       SAME commit as the runs artifact (the seal), every commit holding the runs
                       artifact holds it too, and no commit after it holds the GRANT again.
    ORDER (stage compare): qualification introducer <= authorization introducer < seal. An
    "introducer" is a commit holding the content none of whose parents holds it."""
    root = _root(repo)
    names = {k: ns_path(v) for k, v in PROTOCOL_PATHS.items()}
    kinds = sorted(names)
    parents = parent_map(repo, approved_commit)
    commits = list(parents)
    extra = sorted({q for ps in parents.values() for q in ps} - set(commits))
    ids = _batch_ids(repo, [(c, names[k]) for c in commits + extra + [approved_commit, "HEAD"]
                            for k in kinds])
    current = {k: C.content_free_id(root / names[k]) for k in kinds}
    p, intro, foreign = [], {}, {k: [] for k in kinds}
    for k in kinds:
        if ids[(approved_commit, names[k])] is not None:
            p.append(f"protocol history: the approved commit already holds a {k} artifact")
    for c in commits + [approved_commit]:
        for path in _unexpected_protocol_files(repo, c):
            p.append(f"protocol history: commit {c[:12]} holds an unexpected file under a "
                     f"protocol directory: {path}")
    # on disk: names only, tracked, untracked and ignored alike (git ls-files --others lists
    # ignored files too when no exclude option is given)
    for path in C.git_in(root, "ls-files", "--cached", "--others", "--",
                         *[ns_path(d) for d in PROTOCOL_DIRS]).splitlines():
        d, _, name = path.rpartition("/")
        rel_d = d[len(C.NS_REL) + 1:] if d.startswith(C.NS_REL + "/") else d
        if name not in PROTOCOL_DIRS.get(rel_d, ()):
            p.append(f"protocol history: an unexpected file under a protocol directory on disk: "
                     f"{path}")
    # the GRANT is the permission content committed together with the authorization
    auth_intro = [c for c in commits if ids[(c, names["authorization"])] is not None
                  and ids[(c, names["authorization"])] == current["authorization"]
                  and not any(ids.get((q, names["authorization"])) == current["authorization"]
                              for q in parents[c])] if current["authorization"] else []
    grant_id = ids[(auth_intro[0], names["permission"])] if len(auth_intro) == 1 else None
    final_perm = ids[("HEAD", names["permission"])] if stage == "compare" else None
    for c in commits:
        held = {k for k in kinds if ids[(c, names[k])] is not None}
        if "comparison" in held:
            p.append(f"protocol history: commit {c[:12]} holds a comparison artifact (a prior "
                     f"comparison)")
        if "runs" in held and stage in ("authorize", "run"):
            p.append(f"protocol history: commit {c[:12]} holds a runs artifact (a prior "
                     f"execution)")
        if "authorization" in held and stage == "authorize":
            p.append(f"protocol history: commit {c[:12]} holds an authorization (a prior one)")
        if "permission" in held and stage == "authorize":
            p.append(f"protocol history: commit {c[:12]} holds an execution permission (a prior "
                     f"one)")
        for k in ("runs", "authorization", "qualification"):
            if k in held and ids[(c, names[k])] != current[k]:
                foreign[k].append(c)
                p.append(f"protocol history: commit {c[:12]} holds a {k} artifact other than the "
                         f"current one (a discarded or replaced {k})")
        if "permission" in held and stage in ("run", "compare") and \
                ids[(c, names["permission"])] not in {grant_id, final_perm} - {None}:
            foreign["permission"].append(c)
            p.append(f"protocol history: commit {c[:12]} holds an execution permission other than "
                     f"the GRANT and the final record (a discarded or replaced permission)")
        if "runs" in held and stage == "compare" and (final_perm is None or final_perm == grant_id
                                                      or ids[(c, names["permission"])] != final_perm):
            p.append(f"protocol history: commit {c[:12]} holds the runs artifact without the "
                     f"DENY/EXECUTION_COMPLETED permission record")
    for k in ("runs", "authorization", "qualification"):
        if current[k] is None:
            intro[k] = []
            continue
        intro[k] = [c for c in commits if ids[(c, names[k])] == current[k]
                    and not any(ids.get((q, names[k])) == current[k] for q in parents[c])]
        if len(intro[k]) > 1:
            p.append(f"protocol history: the {k} artifact was introduced by {len(intro[k])} "
                     f"commits")
    # the permission records' introducers
    def introducers(blob):
        return [c for c in commits if blob is not None and ids[(c, names["permission"])] == blob
                and not any(ids.get((q, names["permission"])) == blob for q in parents[c])]
    intro["permission_grant"] = introducers(grant_id)
    intro["permission_final"] = introducers(final_perm) if final_perm != grant_id else []
    if stage in ("run", "compare"):
        if grant_id is None:
            p.append("protocol history: no execution permission GRANT was committed together with "
                     "the authorization")
        elif intro["permission_grant"] != auth_intro:
            p.append("protocol history: the execution permission GRANT was not introduced once, "
                     "in the authorization's commit")
    need = {"authorize": ("qualification",), "run": ("qualification", "authorization", "permission"),
            "compare": ("qualification", "authorization", "runs", "permission")}[stage]
    for k in need:
        if current[k] is not None and ids[("HEAD", names[k])] != current[k]:
            p.append(f"protocol history: the {k} artifact is not committed at HEAD")
    if stage == "compare":
        if final_perm is not None and final_perm == grant_id:
            p.append("protocol history: execution permission at HEAD is still the GRANT (ALLOW): "
                     "comparison requires DENY/EXECUTION_COMPLETED, never ALLOW")
        if len(intro["runs"]) != 1:
            p.append("protocol history: the runs artifact has no single sealing commit")
        else:
            seal = intro["runs"][0]
            for k in ("qualification", "authorization"):
                if len(intro[k]) != 1 or intro[k][0] == seal or not C.git_ok_in(
                        root, "merge-base", "--is-ancestor", intro[k][0], seal):
                    p.append(f"protocol history: the {k} was not committed before the seal")
            if len(intro["qualification"]) == 1 and len(intro["authorization"]) == 1 and \
                    not C.git_ok_in(root, "merge-base", "--is-ancestor",
                                    intro["qualification"][0], intro["authorization"][0]):
                p.append("protocol history: the authorization was committed before the "
                         "qualification it binds")
            if final_perm is None or final_perm == grant_id or intro["permission_final"] != [seal]:
                p.append("protocol history: the DENY/EXECUTION_COMPLETED permission record was "
                         "not introduced in the sealing commit")
            elif grant_id is not None:
                for c in commits:
                    if ids[(c, names["permission"])] == grant_id and C.git_ok_in(
                            root, "merge-base", "--is-ancestor", seal, c):
                        p.append(f"protocol history: commit {c[:12]} restores the execution "
                                 f"permission GRANT after the seal")
    elsewhere = _protocol_elsewhere(repo, stage, current, grant_id, final_perm)
    p += elsewhere["problems"]
    return {"problems": p, "introducers": intro, "foreign": foreign,
            "commits_checked": len(commits), "repository_commits_checked": elsewhere["commits"]}


ELSEWHERE_WHY = {"runs": "a prior or parallel execution",
                 "permission": "an execution started, completed or revoked there",
                 "comparison": "a prior comparison",
                 "authorization": "another authorization"}


def _protocol_elsewhere(repo, stage: str, current: dict, grant_id, final_perm) -> dict:
    """REPOSITORY-WIDE (review 6, N6-2): every commit reachable from ANY ref, from HEAD or from any
    reflog entry -- a sibling branch forked at the authorization commit, a tag, a stash, a reset --
    may hold a runs, permission, comparison or authorization artifact only as the stage admits:
      authorize -- none of them;
      run       -- the current authorization and its GRANT only (no run, no DENY, no comparison);
      compare   -- the current authorization, the GRANT, the final EXECUTION_COMPLETED record and
                   the sealed runs content only; no comparison.
    Commits reachable from nothing (deleted refs, expired reflogs) and other clones are outside
    this repository's refs: LIFECYCLE_SCOPE states it."""
    names = {k: ns_path(PROTOCOL_PATHS[k]) for k in ELSEWHERE_WHY}
    every = sorted(set(C.git_in(_root(repo), "rev-list", "--all", "--reflog", "HEAD").split()))
    ids = _batch_ids(repo, [(c, names[k]) for c in every for k in names])
    admitted = {"authorize": {"runs": set(), "permission": set(), "comparison": set(),
                              "authorization": set()},
                "run": {"runs": set(), "permission": {grant_id}, "comparison": set(),
                        "authorization": {current.get("authorization")}},
                "compare": {"runs": {current.get("runs")}, "permission": {grant_id, final_perm},
                            "comparison": set(), "authorization": {current.get("authorization")}}
                }[stage]
    p = []
    for k in names:
        ok = admitted[k] - {None}
        extra = sorted(c for c in every if ids[(c, names[k])] is not None
                       and ids[(c, names[k])] not in ok)
        if extra:
            p.append(f"protocol lineage: {len(extra)} commit(s) of this repository -- other "
                     f"branches, tags, stashes and reflog entries included -- hold a {k} artifact "
                     f"that stage {stage} does not admit (e.g. {extra[0][:12]}): "
                     f"{ELSEWHERE_WHY[k]}")
    return {"problems": p, "commits": len(every)}


def verify_gate(repo, contract_digest: str, contract: dict) -> dict:
    p = []
    if not artifact_exists(repo, GATE_REL):
        return {"problems": ["no gate"], "digest": None}
    gate = load_artifact(repo, GATE_REL)
    digest = body_digest(gate)
    if gate.get("sha256") != digest:
        p.append("gate: stored sha256 field does not equal the recomputed body digest")
    if gate.get("execution_contract_sha256") != contract_digest:
        p.append("gate: bound to another execution contract")
    if gate.get("guard") != "DENY":
        p.append(f"gate: guard is {gate.get('guard')!r}, not DENY")
    arts = contract["artifacts"]
    if gate.get("statements_sha256") != arts["statements"].get("body_sha256") or \
            gate.get("policy_sha256") != arts["policy"].get("body_sha256"):
        p.append("gate: bound to another policy or statement table than the contract's (review 4, "
                 "N4-1)")
    ev = gate.get("predicate_evaluators", {})
    for pid, fn in contract["required_predicates"].items():
        if ev.get(pid) != fn:
            p.append(f"gate: predicate {pid} is not bound to its production evaluator {fn}")
        if not any(k.startswith(pid + "_") for k in gate.get("predicates", {})):
            p.append(f"gate: predicate {pid} is not stated")
    prov = gate.get("provenance", {})
    g = contract["code"].get(prov.get("producer"), {})
    if not g or g.get("sha256") != prov.get("producer_sha256"):
        p.append("gate: produced by other code than the bound c11r_gate.py")
    return {"problems": p, "digest": digest, "gate": gate}


# ---------------------------------------------------------------------------------------------
# qualification
# ---------------------------------------------------------------------------------------------
def current_host() -> dict:
    import c11r_cost as K
    h = K.host_identity()
    return {k: h.get(k) for k in HOST_KEYS}


def chain_roots(repo=None) -> dict:
    """contract + gate, verified; the policy and statement digests they fix."""
    cv = verify_contract(repo)
    out = {"problems": list(cv["problems"]), "contract_digest": cv["digest"],
           "contract": cv["contract"]}
    if cv["contract"] is None:
        return out
    gv = verify_gate(repo, cv["digest"], cv["contract"])
    out["problems"] += gv["problems"]
    out["gate_digest"] = gv["digest"]
    out["gate"] = gv.get("gate")
    arts = cv["contract"]["artifacts"]
    out["policy_digest"] = arts["policy"].get("body_sha256")
    out["statements_digest"] = arts["statements"].get("body_sha256")
    return out


def qualifier_sha(roots: dict) -> str | None:
    code = (roots.get("contract") or {}).get("code", {})
    qrel = next((r for r in code if r.endswith("/c11r_qualify.py")), None)
    return code.get(qrel, {}).get("sha256") if qrel else None


def item_binding(roots: dict, approved_commit: str | None) -> dict:
    """What EVERY qualification item must carry: the same contract, approved commit, qualifier."""
    return {"execution_contract_sha256": roots.get("contract_digest"),
            "approved_commit": approved_commit, "qualifier_sha256": qualifier_sha(roots)}


def qualification_disposition(items, binding: dict) -> dict:
    """THE TYPED SCHEMA (review 4, N4-4), applied to the item list. The overall disposition is
    DERIVED here, mechanically: PASS only when exactly the items Q1-Q18 are present, each once,
    each with its canonical name, an allowed status and the same binding, and every status is
    PASS. Nothing stored in the artifact (a class, a failed list) is consulted."""
    p = []
    if not isinstance(items, list):
        return {"disposition": "FAIL", "problems": ["qualification: items is not a list"],
                "failing": [], "missing": list(QUAL_ITEMS), "duplicates": [], "unknown": []}
    ids = [i.get("id") if isinstance(i, dict) else None for i in items]
    if None in ids:
        p.append("qualification: an item is not a record with an id")
    missing = [k for k in QUAL_ITEMS if k not in ids]
    duplicates = sorted({x for x in ids if x is not None and ids.count(x) > 1}, key=str)
    unknown = sorted({x for x in ids if x is not None and x not in QUAL_ITEMS}, key=str)
    if missing:
        p.append(f"qualification: required item(s) missing: {missing}")
    if duplicates:
        p.append(f"qualification: duplicate item(s): {duplicates}")
    if unknown:
        p.append(f"qualification: unknown item(s) {unknown} -- the frozen schema rule is "
                 f"{QUAL_UNKNOWN_ITEM_RULE}")
    failing = []
    for i in items:
        if not isinstance(i, dict) or i.get("id") not in QUAL_ITEMS:
            continue
        iid = i["id"]
        if i.get("name") != QUAL_ITEMS[iid]:
            p.append(f"qualification: item {iid} does not carry its canonical name")
        if i.get("status") not in QUAL_ITEM_STATUSES:
            p.append(f"qualification: item {iid} has status {i.get('status')!r}, not one of "
                     f"{list(QUAL_ITEM_STATUSES)}")
        b = i.get("bound") or {}
        for key, want in binding.items():
            if b.get(key) != want:
                p.append(f"qualification: item {iid} is bound to another {key}")
        if i.get("status") != "PASS":
            failing.append(iid)
    if failing:
        p.append(f"qualification: failing item(s) {failing}")
    return {"disposition": "PASS" if not p else "FAIL", "problems": p, "failing": failing,
            "missing": missing, "duplicates": duplicates, "unknown": unknown}


def verify_qualification(repo, q: dict | None, roots: dict, *, approved_commit: str | None = None,
                         allow_fixture=False) -> dict:
    p = []
    if q is None:
        return {"problems": ["no qualification artifact"], "digest": None, "disposition": None}
    digest = body_digest(q)
    if q.get("sha256") != digest:
        p.append("qualification: stored sha256 field does not equal the recomputed body digest")
    if q.get("schema") != QUAL_SCHEMA:
        p.append(f"qualification: schema {q.get('schema')!r}, expected {QUAL_SCHEMA!r}")
    b = q.get("bound", {})
    for key, want in (("execution_contract_sha256", roots.get("contract_digest")),
                      ("gate_sha256", roots.get("gate_digest")),
                      ("policy_sha256", roots.get("policy_digest")),
                      ("statements_sha256", roots.get("statements_digest")),
                      ("approved_commit", approved_commit)):
        if b.get(key) != want:
            p.append(f"qualification: {key} belongs to another contract or tree")
    qsha = qualifier_sha(roots)
    if b.get("qualifier_sha256") != qsha:
        p.append("qualification: produced by another qualifier than the bound one")
    if q.get("provenance", {}).get("producer_sha256") != qsha:
        p.append("qualification: provenance producer is not the bound qualifier")
    d = qualification_disposition(q.get("items"), item_binding(roots, approved_commit))
    p += d["problems"]
    if q.get("QUALIFICATION_CLASS") != d["disposition"]:
        p.append(f"qualification: stored class {q.get('QUALIFICATION_CLASS')!r} is not the "
                 f"recomputed disposition {d['disposition']!r}")
    env = q.get("environment", {}).get("host", {})
    if env != (roots.get("contract") or {}).get("cost_host"):
        p.append("qualification: environment is not the host the cost model was measured on")
    if env != current_host():
        p.append("qualification: environment is not this host")
    if q.get("fixture") and not allow_fixture:
        p.append("qualification: a synthetic fixture is not a qualification")
    return {"problems": p, "digest": digest, "disposition": d["disposition"]}


# ---------------------------------------------------------------------------------------------
# WHAT WAS ACTUALLY LOADED (review round 4, N4-3; review round 5, R5-2 -- erratum E40; review
# round 6, R6-1 -- erratum E49)
# ---------------------------------------------------------------------------------------------
# The contract binds source files by path and content; a process can nevertheless import a
# DIFFERENT file under the same module name (a stray copy earlier on sys.path, a symlink, a copy
# in another checkout, a zip, a SOURCELESS .pyc, a package directory, an extension, a hook).
# Round 5 selected the modules to check by the BASENAME of `__file__`, so any contract module
# loaded from a file not named `<stem>.py` silently left the check (R5-2). Round 6 keyed the check
# on the contract's module NAMES (import stems) and on the ORIGIN of every loaded module:
#   * every entry of sys.modules whose name, or whose origin's import name, is a contract stem --
#     and __main__ when its file is one -- is examined; a module can no longer drop out;
#   * FROZEN POLICY: a load-bearing module must be SOURCE-BACKED (the exact SourceFileLoader).
#     Sourceless bytecode, extensions, zips, namespace packages and hook loaders are refused;
#   * __file__, __spec__.origin and the loader's path must ALL resolve (realpath) to exactly
#     <execution root>/<contract path>, which itself contains no symlink below the root;
#   * the bytes of that file hash to the contract's sha256;
#   * a cached bytecode file that CPython's loader would ACCEPT for that source (a timestamp
#     header matching its mtime and size, or an unchecked hash-based header) must EQUAL the
#     compilation of the verified source; a stale cache the loader ignores is not a finding;
#   * every module the boundary's program imports at module level (its import-time closure) must
#     be present and verified (PRESENCE);
#   * PYTHONPATH is unset and assertions are not stripped (-O).
# ROUND 7 (review 6, R6-1). Round 6 examined only CONTRACT-NAMED modules and refused statically
# only contract-named entries and untracked *.py. The campaign itself puts its code directories
# AHEAD of the standard library on sys.path (the script's own directory; c11r_idrift and
# c11_certifier insert C11's and C7's), so a sourceless `fractions.pyc` there -- the arithmetic of
# every certifier and of the comparator's classification -- ran with every check green. The rules
# now start from LOCATION, not from names:
#   (L1) CAMPAIGN-DIRECTORY CLOSURE: a loaded module ANY of whose origins (__file__,
#        __spec__.origin, the loader's path, a package's search locations; lexically or by
#        realpath) lies inside a campaign code directory of the execution root must be an
#        APPROVED SOURCE, source-backed, loaded from exactly that regular file under its own
#        name -- whatever the name, standard-library-looking or not. APPROVED = a file whose bytes
#        the contract binds: the load-bearing closure (`code`) and the campaign's other frozen
#        Python files (`frozen_code`: producers, harnesses, the status verifier), both verified
#        byte for byte. Tracked but unbound files of the predecessors' code directories are NOT
#        approved;
#   (L2) ORIGIN AGREEMENT: for EVERY loaded module, __file__, __spec__.origin and the loader's
#        path, where they are filesystem paths, name one file;
#   (L3) IMPORT-PATH PRECEDENCE: every sys.path entry inside the repository is a campaign code
#        directory, and every entry that precedes the standard library is a campaign code
#        directory or lies inside the interpreter's own installation -- so a standard-library
#        name can be resolved ahead of the standard library only in a campaign code directory,
#        which (S) and (B) cover and (L1) examines when it is loaded (review 7, N7-3: a module a
#        boundary check itself imports is loaded before the snapshot is taken);
#   (S)  STATIC INVENTORY (code_dir_shadows): each campaign code directory holds EXACTLY the
#        entries the contract froze (`code_directories`: tracked, regular *.py files) and at most a
#        real `__pycache__` whose entries are regular files named <inventory stem>.<cache
#        tag>[.opt-N].pyc (CPython reads that directory only for a source it has already found).
#        Anything else -- a .pyc, an extension, a zip or egg, a package or namespace directory, a
#        symlink, metadata, an unexpected or untracked .py, a COMMITTED addition -- is refused by
#        name and kind. (A standard-library or built-in name is ALSO reported, as defence in depth
#        only: `sys.stdlib_module_names` is not complete -- review 7, N7-3,
#        `_sysconfigdata__darwin_darwin` -- and no rule depends on it.)
#   (B)  PRE-IMPORT BARRIER: the three boundary programs (c11r_runs, c11r_compare, c11r_qualify)
#        execute PREIMPORT_BARRIER as their first statement, before any other import (they no
#        longer begin with `from __future__ import annotations`, itself an import resolved through
#        sys.path). Using only `os`, `sys` and the built-in `_imp`, it refuses to start while a
#        campaign code directory holds anything but __pycache__ and regular, lower-case *.py files
#        carrying that DIRECTORY'S CAMPAIGN PREFIX (c11r_, c11_, c7_) -- a POSITIVE rule that no
#        standard-library, third-party or start-up module name can satisfy, so it depends on no
#        enumeration of the standard library (review 7, N7-3). A shadow must be ABSENT WHEN THE
#        PROGRAM STARTS, not merely detected after it has run.
# ROUND 8 (review 7, N7-1 and N7-2). (L0) THE LAUNCH POLICY: a boundary program runs only in an
# interpreter started exactly as c11r_launch.py starts it -- the frozen executable, isolated and
# without site (-I -S: no PYTHON* variable is honoured, no user site, no .pth hook, the script's
# directory is not on sys.path), DEFAULT hash-based .pyc checking (`--check-hash-based-pycs never`
# executes a forged checked cache: N7-1), no pycache prefix, no warning options, only the frozen -X
# option, and an EXPLICIT environment (the frozen name allowlist, PATH frozen). The barrier checks
# it when the file runs as a program, BEFORE any other import; runner_preflight, comparator step 12
# and Q4 check it again (launch_policy_problems). The launcher is started isolated by the KERNEL
# (its first line), so the environment never acts before a campaign statement on the supported
# path; a direct start is refused by the barrier before any campaign import, but what the
# interpreter executed at its own start-up has then already run (LAUNCH_POLICY.not_covered).
# SCOPE, exactly: what the code directories hold when a boundary program starts and when it is
# checked, and what the import system loaded, from which file, at the moment of the check. A file
# placed between the barrier and the import that uses it and removed before the check, code
# executed through exec/eval, a module that -- once executing -- rewrites its own metadata or
# deletes its file, and in-memory patching of a loaded module or of this verifier are arbitrary
# malicious runtime modification: NOT covered.
SOURCE_BACKED = "SOURCE"
STDLIB_NAMES = frozenset(sys.stdlib_module_names) | frozenset(sys.builtin_module_names)
SOURCE_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\.py")
CACHE_NAME = re.compile(r"(?P<stem>[A-Za-z_][A-Za-z0-9_]*)\.[A-Za-z0-9_-]+(\.opt-[12])?\.pyc")
BOUNDARY_PROGRAMS = ("c11r_runs.py", "c11r_compare.py", "c11r_qualify.py")
KIND_TEXT = {"ABSENT": "missing", "FILE": "a regular file", "DIRECTORY": "a directory",
             "SYMLINK_INSIDE": "a symlink (resolving inside the repository)",
             "SYMLINK_OUTSIDE": "a symlink resolving OUTSIDE the repository",
             "SYMLINK_DANGLING": "a dangling symlink", "SYMLINK_LOOP": "a symlink loop",
             "OTHER": "not a regular file or directory"}
MODULE_IDENTITY_POLICY = {
    "approved_sources": "the contract's `code` (load-bearing closure) and `frozen_code` (every "
                        "other Python file of the campaign's code directory), byte-verified",
    "campaign_directory_closure": "a loaded module with ANY origin inside a campaign code "
                                  "directory must be an approved source, source-backed, loaded "
                                  "from exactly that regular file under its own name; refused "
                                  "whatever its name (L1)",
    "origin_agreement": "__file__, __spec__.origin and the loader's path name one file, for every "
                        "loaded module (L2)",
    "import_path_precedence": "repository directories on sys.path are campaign code directories; "
                              "entries ahead of the standard library are campaign code "
                              "directories or inside the interpreter's installation (L3)",
    "code_directory_inventory": "exactly the frozen regular, tracked *.py entries and at most a "
                                "real __pycache__ (S); a standard-library or built-in name is "
                                "reported too, as defence in depth only (the enumeration is not "
                                "complete: review 7, N7-3)",
    "cache_policy": "__pycache__ holds only regular files named <inventory stem>.<cache tag>"
                    "[.opt-N].pyc; a cache CPython would accept must equal the compilation of "
                    "its verified source; a stale cache is ignored by CPython and not a finding",
    "preimport_barrier": "the boundary programs, run as programs, refuse to start unless the "
                         "launch policy holds (L0), and always refuse while a code directory "
                         "holds anything but __pycache__ and regular lower-case *.py files "
                         "carrying the directory's campaign prefix (B; no standard-library "
                         "enumeration involved)",
    "launch_policy": "c11r_launch.py, started isolated by the kernel, execs the program under "
                     "LAUNCH_POLICY; the barrier, runner_preflight, comparator step 12 and Q4 "
                     "verify it (L0)",
    "not_covered": "a file placed after the barrier and removed before the check; exec/eval; a "
                   "module that rewrites its own metadata or deletes its file once executing; "
                   "in-memory patching -- arbitrary malicious runtime modification"}

# (L0) THE LAUNCH POLICY, bound in the contract: c11r_launch.py's constants ARE the policy.
CODE_DIR_PREFIXES = {f"{C.NS_REL}/code": "c11r_",
                     str((C.C11 / "code").relative_to(C.REPO)): "c11_",
                     str((C.C7 / "code").relative_to(C.REPO)): "c7_"}
LAUNCH_POLICY = {
    "launcher": f"{C.NS_REL}/code/c11r_launch.py",
    "launcher_first_line": f"#!{L.FROZEN_INTERPRETER} -IS",
    "interpreter": L.FROZEN_INTERPRETER,
    "child_flags": list(L.CHILD_FLAGS),
    "required": "isolated (-I: environment ignored, no user site, safe path) and no site (-S); "
                "optimize 0; check_hash_based_pycs 'default'; no pycache prefix; no warning "
                "options; -X options only " + repr(L.ALLOWED_XOPTIONS),
    "environment_allowed": list(L.ENV_ALLOWED), "path": L.FROZEN_PATH,
    "launcher_refuses_prefixes": list(L.ENV_REFUSED_PREFIXES),
    "code_directory_prefixes": dict(CODE_DIR_PREFIXES),
    "not_covered": "a boundary program started some other way is refused by its barrier before any "
                   "campaign import, but what the interpreter itself executed at start-up (a "
                   "sitecustomize or user-site .pth hook, a forged cache of a start-up stdlib "
                   "module under PYTHONPYCACHEPREFIX) has then already run; native code injected "
                   "by the dynamic linker (DYLD_*, refused by the launcher) acts before any "
                   "Python; the interpreter binary and its standard library are the host's"}


def launch_policy_problems() -> list[str]:
    """(L0): THIS process was started as c11r_launch.py starts a boundary program -- the frozen
    interpreter policy and the explicit environment (review 7, N7-1, N7-2)."""
    import _imp
    p = L.interpreter_problems(sys.flags, _imp.check_hash_based_pycs, sys.pycache_prefix,
                               sys._xoptions, sys.warnoptions, sys.executable)
    extra = sorted(k for k in os.environ if k not in L.ENV_ALLOWED)
    if extra:
        p.append(f"the environment carries names outside the frozen allowlist {extra}")
    if os.environ.get("PATH") != L.FROZEN_PATH:
        p.append("PATH is not the frozen one")
    return [f"launch policy: {x}" for x in p]


# The block every boundary program executes FIRST (after its docstring). Its text is canonical,
# generated from the launch policy's constants: preimport_barrier_problems() requires it verbatim,
# first, in all three programs.
_BARRIER_TEMPLATE = """# --- C11R PRE-IMPORT BARRIER (reviews 6-7: R6-1, N7-1, N7-2, N7-3): the first statement ---
import os as _os
import sys as _sys
import _imp as _c11r_imp


def _c11r_preimport_barrier():
    \"\"\"Run as a PROGRAM, refuse to start unless the interpreter was started as c11r_launch.py
    starts it (isolated, no site, default hash-based .pyc checking, the frozen interpreter, the
    explicit environment); always refuse while a campaign code directory holds anything but
    __pycache__ and regular lower-case *.py files carrying its campaign prefix. Only `os`, `sys`
    and the built-in `_imp` are used: nothing here is resolved through sys.path
    (c11r_contract.PREIMPORT_BARRIER, generated from c11r_launch.py).\"\"\"
    bad = []
    if __name__ == "__main__":
        f = _sys.flags
        if not (f.isolated and f.ignore_environment and f.no_user_site and f.safe_path
                and f.no_site):
            bad.append("not started isolated and without site (-I -S): use c11r_launch.py")
        if f.optimize:
            bad.append("assertions stripped (-O)")
        if _c11r_imp.check_hash_based_pycs != "default":
            bad.append("hash-based .pyc policy " + repr(_c11r_imp.check_hash_based_pycs))
        if _sys.pycache_prefix is not None:
            bad.append("a pycache prefix is set")
        if _sys._xoptions and dict(_sys._xoptions) != @XOPTIONS@:
            bad.append("-X options other than the frozen ones")
        if _sys.warnoptions:
            bad.append("warning options are set")
        if _os.path.realpath(_sys.executable) != _os.path.realpath(@INTERPRETER@):
            bad.append("not the frozen interpreter")
        extra = sorted(k for k in _os.environ if k not in @ENV_ALLOWED@)
        if extra:
            bad.append("environment names outside the frozen allowlist: " + ", ".join(extra))
        if _os.environ.get("PATH") != @PATH@:
            bad.append("PATH is not the frozen one")
    here = _os.path.dirname(_os.path.realpath(__file__))
    closure = _os.path.dirname(_os.path.dirname(here))
    for d, prefix in ((here, "c11r_"), (_os.path.join(closure, @C11@, "code"), "c11_"),
                      (_os.path.join(closure, @C7@, "code"), "c7_")):
        if _os.path.islink(d) or not _os.path.isdir(d):
            bad.append(d)
            continue
        for e in sorted(_os.listdir(d)):
            p = _os.path.join(d, e)
            if e == "__pycache__" and _os.path.isdir(p) and not _os.path.islink(p):
                continue
            stem = e[:-3]
            if not (e.endswith(".py") and stem.startswith(prefix) and stem.isascii()
                    and stem.replace("_", "").isalnum() and stem == stem.lower()
                    and _os.path.isfile(p) and not _os.path.islink(p)):
                bad.append(_os.path.basename(_os.path.dirname(d)) + "/code/" + e)
    if bad:
        raise SystemExit("REFUSE (pre-import barrier, reviews 6-7): " + "; ".join(bad))


_c11r_preimport_barrier()
# --- end of the pre-import barrier ---
"""
PREIMPORT_BARRIER = (_BARRIER_TEMPLATE
                     .replace("@XOPTIONS@", repr(dict(L.ALLOWED_XOPTIONS)))
                     .replace("@INTERPRETER@", repr(L.FROZEN_INTERPRETER))
                     .replace("@ENV_ALLOWED@", repr(tuple(L.ENV_ALLOWED)))
                     .replace("@PATH@", repr(L.FROZEN_PATH))
                     .replace("@C11@", repr(C.C11.name))
                     .replace("@C7@", repr(C.C7.name)))


def preimport_barrier_problems(repo=None) -> list[str]:
    """(B, L0): each boundary program starts with PREIMPORT_BARRIER verbatim, immediately after its
    docstring, and imports nothing from __future__ (such an import must come first and is
    resolved through sys.path); the launcher's first line starts the frozen interpreter with
    -IS; every inventory entry carries its directory's campaign prefix."""
    import ast
    p = []
    try:
        first = code_bytes(repo, LAUNCH_POLICY["launcher"]).decode().splitlines()[0]
    except (OSError, ValueError, IndexError):
        first = None
    if first != LAUNCH_POLICY["launcher_first_line"]:
        p.append("launch policy: c11r_launch.py does not start with the frozen interpreter line")
    inv = code_directories(repo)
    for rel_d, prefix in CODE_DIR_PREFIXES.items():
        off = [e for e in inv.get(rel_d, []) if not (e.startswith(prefix) and e == e.lower())]
        if off:
            p.append(f"pre-import barrier: {off} in {rel_d} do not carry the campaign prefix "
                     f"{prefix!r}")
    for name in BOUNDARY_PROGRAMS:
        rel = f"{C.NS_REL}/code/{name}"
        try:
            src = code_bytes(repo, rel).decode()
            tree = ast.parse(src)
        except (OSError, ValueError, SyntaxError) as e:
            p.append(f"pre-import barrier: {name} is not readable Python source ({type(e).__name__})")
            continue
        doc = tree.body[0] if tree.body and isinstance(tree.body[0], ast.Expr) \
            and isinstance(getattr(tree.body[0], "value", None), ast.Constant) else None
        after = "\n".join(src.splitlines()[doc.end_lineno:]).lstrip("\n") if doc else src
        if not after.startswith(PREIMPORT_BARRIER):
            p.append(f"pre-import barrier: {name} does not begin with the canonical pre-import "
                     f"barrier immediately after its docstring")
        if any(isinstance(n, ast.ImportFrom) and n.module == "__future__" for n in ast.walk(tree)):
            p.append(f"pre-import barrier: {name} imports from __future__ (an import resolved "
                     f"through sys.path before the barrier could run)")
    return p


def import_time_closure(root_name: str) -> set[str]:
    """The contract stems a program imports at MODULE LEVEL, transitively (the modules that are
    necessarily loaded once the program has started) -- mechanically, from the source."""
    import ast
    seen, stack = set(), [root_name]
    while stack:
        name = stack.pop()
        if name in seen:
            continue
        seen.add(name)
        path = C._resolve_module(name)
        if path is None:
            continue
        for n in ast.parse(C.read_code(C._rel(path))).body:
            names = []
            if isinstance(n, ast.Import):
                names = [a.name.split(".")[0] for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                names = [n.module.split(".")[0]]
            stack += [x for x in names if C._resolve_module(x) is not None]
    return seen


LOAD_ROLES = {"runner": "c11r_runs", "comparator": "c11r_compare", "qualifier": "c11r_qualify"}


def module_kind(m) -> tuple[str, str]:
    """(kind, loader type name) of a loaded module, from its spec (or __loader__)."""
    import importlib.machinery as M
    spec = getattr(m, "__spec__", None)
    loader = getattr(spec, "loader", None) if spec is not None else getattr(m, "__loader__", None)
    t = type(loader)
    if t is M.SourceFileLoader:
        kind = SOURCE_BACKED
    elif t is M.SourcelessFileLoader:
        kind = "SOURCELESS_BYTECODE"
    elif t is M.ExtensionFileLoader:
        kind = "EXTENSION"
    elif loader is None or t.__name__ == "NamespaceLoader":
        kind = "NAMESPACE_OR_UNKNOWN"
    elif t.__name__ == "zipimporter":
        kind = "ZIP"
    else:
        kind = "OTHER_LOADER"
    return kind, t.__name__


def _origins(m) -> list[str]:
    spec = getattr(m, "__spec__", None)
    loader = getattr(spec, "loader", None) if spec is not None else getattr(m, "__loader__", None)
    out = [getattr(m, "__file__", None), getattr(spec, "origin", None),
           getattr(loader, "path", None)]
    return [x for x in out if isinstance(x, str) and x]


def _file_origins(m) -> list[str]:
    """The origins that are FILESYSTEM PATHS ('frozen' and 'built-in' are not)."""
    return [x for x in _origins(m) if os.sep in x]


def _search_locations(m) -> list[str]:
    """A package's search locations -- a namespace package has nothing else."""
    spec = getattr(m, "__spec__", None)
    locs = getattr(spec, "submodule_search_locations", None) if spec is not None else \
        getattr(m, "__path__", None)
    try:
        return [x for x in list(locs or []) if isinstance(x, str) and x]
    except TypeError:
        return []


def _import_name_of_file(path: str) -> str:
    """The import name a file or directory provides: `x.py`, `x.pyc`, `x.cpython-314-darwin.so`
    and `x/__init__.py` all provide `x`."""
    pp = pathlib.PurePosixPath(path)
    if pp.name.startswith("__init__."):
        return pp.parent.name
    return pp.name.split(".")[0]


def _pyc_matches_source(cached: str | None, source: bytes, filename: str) -> bool | None:
    """The cached bytecode CPython's source loader WOULD ACCEPT for this source, compared with the
    compilation of the verified source. None when there is no such cache: no file, another magic
    number, a timestamp header whose mtime or size does not match the source file (the loader
    then recompiles from source and ignores the cache), or a checked hash-based header whose
    source hash does not match. An UNCHECKED hash-based cache, or a timestamp cache whose header
    matches, is what the loader executes, so its code object must equal the source's."""
    import _imp
    import importlib.util as U
    import marshal
    if not cached or not os.path.exists(cached):
        return None
    try:
        data = pathlib.Path(cached).read_bytes()
        if len(data) < 16 or data[:4] != U.MAGIC_NUMBER:
            return None
        flags = int.from_bytes(data[4:8], "little")
        if flags & 0b1:                                   # hash-based
            # the loader validates the source hash in mode 'always', and in 'default' only for a
            # CHECKED cache; in mode 'never' it validates nothing (review 7, N7-1)
            mode = _imp.check_hash_based_pycs
            validated = mode == "always" or (mode == "default" and flags & 0b10)
            if validated and data[8:16] != U.source_hash(source):
                return None                               # validated, stale: recompiled
        else:                                             # timestamp-based
            st = os.stat(filename)
            if (int.from_bytes(data[8:12], "little") != (int(st.st_mtime) & 0xFFFFFFFF)
                    or int.from_bytes(data[12:16], "little") != (st.st_size & 0xFFFFFFFF)):
                return None                               # stale: the loader ignores it
        loaded = marshal.loads(data[16:])
        fresh = compile(source, filename, "exec", dont_inherit=True, optimize=sys.flags.optimize)
        return loaded == fresh
    except Exception:
        return False


def code_dir_rels() -> list[str]:
    """The campaign code directories (the ones the campaign puts on sys.path), repo-relative."""
    return sorted(str(pathlib.Path(d).relative_to(C.REPO)) for d in C.CODE_DIRS)


def code_directories(repo=None) -> dict[str, list[str]]:
    """The INVENTORY of each campaign code directory (review 6, R6-1): the regular *.py files it
    holds. The contract binds it at the approved commit; code_dir_shadows refuses anything else."""
    root = _root(repo)
    out = {}
    for rel_d in code_dir_rels():
        here = root / rel_d
        names = []
        if C.path_kind(here, inside=root) == "DIRECTORY":
            names = [e for e in sorted(os.listdir(here)) if SOURCE_NAME.fullmatch(e)
                     and C.path_kind(here / e, inside=root) == "FILE"]
        out[rel_d] = names
    return out


def frozen_code(repo=None, code: dict | None = None) -> dict[str, str | None]:
    """sha256 of every Python file of the campaign's code directory OUTSIDE the load-bearing
    closure (producers, harnesses, the status verifier): approved sources for (L1)."""
    code = code if code is not None else {}
    return {rel: code_identity(repo, rel)["sha256"] for rel in namespace_code() if rel not in code}


def approved_sources(contract: dict) -> dict[str, str | None]:
    out = {rel: rec.get("sha256") for rel, rec in contract.get("code", {}).items()}
    out.update(contract.get("frozen_code") or {})
    return out


def _cache_dir_problems(path: pathlib.Path, where: str, allowed: set, root) -> list[str]:
    k = C.path_kind(path, inside=root)
    if k != "DIRECTORY":
        return [f"code directories: __pycache__ in {where} is {KIND_TEXT[k]}, not a real "
                f"directory"]
    stems = {e[:-3] for e in allowed}
    p = []
    for e in sorted(os.listdir(path)):
        m = CACHE_NAME.fullmatch(e)
        ek = C.path_kind(path / e, inside=root)
        if ek != "FILE" or m is None or m.group("stem") not in stems:
            p.append(f"code directories: __pycache__/{e} in {where} is not a cache of one of the "
                     f"directory's inventory sources ({KIND_TEXT[ek]}): the frozen cache policy "
                     f"admits only regular <stem>.<cache tag>[.opt-N].pyc files")
    return p


def code_dir_shadows(contract: dict, repo=None) -> list[str]:
    """STATIC (S) -- review 4, N4-3; review 5, R5-2; review 6, R6-1. Every entry of each campaign
    code directory is listed from the FILESYSTEM (tracked, untracked and ignored alike, lstat,
    never following a link) and compared with the inventory the contract froze. Refused, each by
    name and kind: a symlink, a directory (package or namespace package), anything that is not a
    regular *.py file (.pyc, extension, zip, egg, metadata), an entry carrying a standard-library
    or built-in module name, an entry carrying a contract module's import name away from its
    contract path, an entry not in the frozen inventory (a COMMITTED addition included), an
    untracked source, a missing inventory entry, and a __pycache__ that is not a real directory
    of regular caches of the directory's own sources."""
    root = _root(repo)
    stems = {pathlib.PurePosixPath(rel).stem: rel for rel in contract["code"]}
    inv = contract.get("code_directories")
    if not isinstance(inv, dict) or sorted(inv) != code_dir_rels():
        return ["code directories: the contract binds no inventory of the campaign code "
                "directories"]
    p, untracked = [], []
    for rel_d in code_dir_rels():
        here = root / rel_d
        where = f"{pathlib.PurePosixPath(rel_d).parent.name}/code"
        k = C.path_kind(here, inside=root)
        if k != "DIRECTORY":
            p.append(f"code directories: {where} is {KIND_TEXT[k]}, not a directory")
            continue
        allowed = set(inv.get(rel_d) or [])
        tracked = set(C.git_in(root, "ls-files", "--", f"{rel_d}/").splitlines())
        entries = sorted(os.listdir(here))
        for e in entries:
            path = here / e
            k = C.path_kind(path, inside=root)
            if e == "__pycache__":
                p += _cache_dir_problems(here / "__pycache__", where, allowed, root)
                continue
            name = e if k == "DIRECTORY" else _import_name_of_file(e)
            if k.startswith("SYMLINK"):
                p.append(f"code directories: {e} in {where} is {KIND_TEXT[k]}: a campaign code "
                         f"directory holds no symlink")
            elif k == "DIRECTORY":
                p.append(f"code directories: {e}/ in {where} is a directory (a package or "
                         f"namespace package): a campaign code directory holds no package")
            elif k != "FILE":
                p.append(f"code directories: {e} in {where} is {KIND_TEXT[k]}")
            elif not SOURCE_NAME.fullmatch(e):
                p.append(f"code directories: {e} in {where} is not Python source: sourceless "
                         f"bytecode, extensions, archives and import metadata are refused")
            elif f"{rel_d}/{e}" not in tracked:
                untracked.append(e)
            if name in STDLIB_NAMES:
                p.append(f"code directories: {e} in {where} carries the standard-library import "
                         f"name {name!r}")
            if name in stems and f"{rel_d}/{e}" != stems[name]:
                p.append(f"code directories: {e} in {where} carries the import name of contract "
                         f"module {name}")
            if e not in allowed:
                p.append(f"code directories: {e} in {where} is not in the directory inventory "
                         f"the contract froze")
        for e in sorted(allowed - set(entries)):
            p.append(f"code directories: {e}, in the frozen inventory of {where}, is missing")
    if untracked:
        p.append(f"code directories: untracked Python source {sorted(untracked)}")
    return p


def _parent_resolved(path: str) -> str:
    """The path with its DIRECTORIES resolved and its last component kept: a symlinked file keeps
    its own name (so it is judged where it sits), a symlinked parent (/var -> /private/var) does
    not move it."""
    a = os.path.abspath(path)
    return os.path.join(os.path.realpath(os.path.dirname(a)), os.path.basename(a))


def _in_dirs(path: str, dirs) -> bool:
    """Inside one of `dirs` ((lexical, real) pairs) -- lexically, with its parents resolved, or by
    realpath: a module reached through a symlink in a code directory is inside it, and so is one
    whose file lies there under another name."""
    forms = (os.path.abspath(path), _parent_resolved(path), os.path.realpath(path))
    return any(x == d or x.startswith(d + os.sep) for x in forms for pair in dirs for d in pair)


def _where_in_dirs(path: str, dirs) -> str:
    """`<campaign>/code/<path inside the code directory>`, for messages."""
    for form in (os.path.abspath(path), _parent_resolved(path), os.path.realpath(path)):
        for pair in dirs:
            for d in pair:
                if form.startswith(d + os.sep):
                    return f"{pathlib.PurePosixPath(d).parent.name}/code/{form[len(d) + 1:]}"
    return pathlib.PurePosixPath(path).name


def _import_path_problems(dirs, lex_root: pathlib.Path) -> list[str]:
    """(L3): which directories can supply a module ahead of the standard library."""
    import sysconfig
    paths = sysconfig.get_paths()
    std = {os.path.realpath(paths[k]) for k in ("stdlib", "platstdlib") if paths.get(k)}
    prefixes = {os.path.realpath(x) for x in (sys.base_prefix, sys.prefix, sys.base_exec_prefix,
                                              sys.exec_prefix)}
    code_real = {real for _, real in dirs}
    repo_real = os.path.realpath(lex_root)
    p, seen_std = [], False
    for entry in sys.path:
        real = os.path.realpath(entry or os.getcwd())
        if real in std:
            seen_std = True
            continue
        if real in code_real:
            continue
        name = pathlib.PurePosixPath(real).name
        if real == repo_real or real.startswith(repo_real + os.sep):
            p.append(f"loaded modules: sys.path holds a repository directory that is not a "
                     f"campaign code directory ({name})")
        elif not seen_std and not any(real == x or real.startswith(x + os.sep) for x in prefixes):
            p.append(f"loaded modules: sys.path entry {name!r} precedes the standard library and "
                     f"is neither a campaign code directory nor part of the interpreter "
                     f"(review 6, R6-1)")
    if not seen_std:
        p.append("loaded modules: the standard library is not on sys.path")
    return p


def _campaign_module_problems(key: str, m, files: list[str], locs: list[str], dirs,
                              approved: dict, contract_code: dict,
                              lex_root: pathlib.Path) -> list[str]:
    """(L1) for one module with an origin inside a campaign code directory."""
    inside = [o for o in files + locs if _in_dirs(o, dirs)]
    where = _where_in_dirs(inside[0], dirs)
    files = [o for o in files if _in_dirs(o, dirs)] + [o for o in files if not _in_dirs(o, dirs)]
    if not files:
        return [f"loaded modules: module {key!r} is a namespace package inside a campaign code "
                f"directory ({where}): refused whatever its name (review 6, R6-1)"]
    rel = None
    for form in (_parent_resolved(files[0]), os.path.realpath(files[0])):
        r = os.path.relpath(form, os.path.realpath(lex_root))
        if not r.startswith(".."):
            rel = str(pathlib.PurePosixPath(r))
            break
    if rel is None or rel not in approved:
        return [f"loaded modules: module {key!r} was loaded from {where}, inside a campaign code "
                f"directory, which is not an approved contract source (review 6, R6-1)"]
    p = []
    kind, loader_type = module_kind(m)
    if kind != SOURCE_BACKED:
        p.append(f"loaded modules: module {key!r} from {where} is {kind} ({loader_type}): a module "
                 f"of a campaign code directory must be loaded from its source by the standard "
                 f"source loader")
    real_root = pathlib.Path(os.path.realpath(lex_root))
    k = C.path_kind(real_root / rel, inside=real_root)
    if k != "FILE":
        p.append(f"loaded modules: module {key!r} from {where} is reached through {KIND_TEXT[k]}")
    if key != "__main__" and key.rsplit(".", 1)[-1] != pathlib.PurePosixPath(rel).stem:
        p.append(f"loaded modules: {where} is loaded under another module name, {key!r}")
    if rel not in contract_code:                         # frozen, not load-bearing: bytes here
        try:
            src = code_bytes(real_root, rel)
        except OSError:
            src = None
        if src is None or C.sha256_bytes(src) != approved[rel]:
            p.append(f"loaded modules: module {key!r} from {where} is not the approved bytes")
        elif _pyc_matches_source(getattr(m, "__cached__", None), src,
                                 str(real_root / rel)) is False:
            p.append(f"loaded modules: module {key!r} from {where} has cached bytecode that is "
                     f"not the compilation of its verified source")
    return p


def verify_loaded_modules(contract: dict, exec_root=None, modules: dict | None = None,
                          role: str | None = None) -> dict:
    """What THIS process loaded: (L1) every module with an origin inside a campaign code
    directory is an approved source; every loaded module that IS, by name or by origin, a
    contract module is verified; (L2) origins agree; (L3) the import path; and, for a boundary
    `role`, every module its program imports at module level is present."""
    root = pathlib.Path(os.path.realpath(exec_root or C.REPO))
    lex_root = pathlib.Path(os.path.abspath(exec_root or C.REPO))
    dirs = [(os.path.abspath(lex_root / d), os.path.realpath(lex_root / d))
            for d in code_dir_rels()]
    # (L3) FIRST: it imports sysconfig and its platform data module; the snapshot below must
    # include whatever this check itself caused to be loaded (review 7, N7-3)
    path_problems = _import_path_problems(dirs, lex_root)
    mods = dict(sys.modules if modules is None else modules)
    stems = {pathlib.PurePosixPath(rel).stem: rel for rel in contract["code"]}
    approved = approved_sources(contract)
    inv = contract.get("code_directories")
    p, checked, origin_seen, campaign = [], set(), {}, []
    if not isinstance(inv, dict) or sorted(inv) != code_dir_rels():
        p.append("loaded modules: the contract binds no inventory of the campaign code "
                 "directories")
    if os.environ.get("PYTHONPATH"):
        p.append("loaded modules: PYTHONPATH is set; the import path is not the contract's")
    if sys.flags.optimize:
        p.append("loaded modules: assertions are stripped (-O)")
    p += path_problems
    for key, m in sorted(mods.items(), key=lambda kv: kv[0]):
        if m is None:
            continue
        origins = _origins(m)
        files = _file_origins(m)
        locs = _search_locations(m)
        if len({os.path.realpath(o) for o in files}) > 1:                          # (L2)
            p.append(f"loaded modules: module {key!r}: its __file__, __spec__.origin and loader "
                     f"path disagree "
                     f"({sorted({pathlib.PurePosixPath(o).name for o in files})}): one module, "
                     f"one file")
        if any(_in_dirs(o, dirs) for o in files + locs):                            # (L1)
            campaign.append(key)
            p += _campaign_module_problems(key, m, files, locs, dirs, approved,
                                           contract["code"], lex_root)
        by_origin = {_import_name_of_file(o) for o in origins} & set(stems)
        by_key = {key.rsplit(".", 1)[-1]} & set(stems) if key != "__main__" else set()
        for stem in sorted(by_origin | by_key):
            rel = stems[stem]
            name = pathlib.PurePosixPath(rel).name
            where = f"{name} (as module {key!r})"
            checked.add(stem)
            expected = root / rel
            kind, loader_type = module_kind(m)
            if kind != SOURCE_BACKED:
                p.append(f"loaded modules: {where} is {kind} ({loader_type}, origin "
                         f"{pathlib.PurePosixPath(origins[0]).name if origins else None}): a "
                         f"load-bearing module must be loaded from its source file by the "
                         f"standard source loader -- sourceless bytecode, archives, extensions "
                         f"and hook loaders are refused")
                continue
            if os.path.realpath(expected) != str(expected):
                p.append(f"loaded modules: the contract path of {name} is reached through a symlink")
            reals = {os.path.realpath(o) for o in origins}
            if not origins or reals != {str(expected)}:
                p.append(f"loaded modules: {where} was loaded from another file than "
                         f"<execution root>/{rel}")
                continue
            if origin_seen.setdefault(stem, id(m)) != id(m) and key != "__main__":
                p.append(f"loaded modules: {name} is loaded twice, as different module objects")
            src = code_bytes(root, rel)                # the file just shown to BE root/rel
            if C.sha256_bytes(src) != contract["code"][rel]["sha256"]:
                p.append(f"loaded modules: {where} is not the contract's bytes")
            pyc = _pyc_matches_source(getattr(m, "__cached__", None), src, str(expected))
            if pyc is False:
                p.append(f"loaded modules: {where} has cached bytecode that is not the compilation "
                         f"of its verified source")
    required = set()
    if role is not None:
        required = import_time_closure(LOAD_ROLES[role]) & set(stems)
        for stem in sorted(required - checked):
            p.append(f"loaded modules: {pathlib.PurePosixPath(stems[stem]).name} is required at the "
                     f"{role} boundary but is not loaded")
    return {"problems": p, "checked": sorted(pathlib.PurePosixPath(stems[s]).name for s in checked),
            "required": sorted(pathlib.PurePosixPath(stems[s]).name for s in required),
            "modules_examined": len(mods), "campaign_origin_modules": sorted(campaign),
            "approved_sources": len(approved), "execution_root": str(root)}


# ---------------------------------------------------------------------------------------------
# the execution lifecycle (review 5, R5-1): permission records and the DERIVED state
# ---------------------------------------------------------------------------------------------
def permission_record(transition: str, *, approved_commit: str, authorization_sha256: str,
                      grant_sha256: str | None = None, runs_sha256: str | None = None,
                      fixture: bool = False) -> dict:
    """ONE builder for every execution-permission record. GRANT (ALLOW) binds the
    authorization; every DENY record also binds the GRANT it ends, and EXECUTION_COMPLETED the
    runs artifact's body digest. The authorization itself is never rewritten."""
    if transition not in PERMISSION_TRANSITIONS:
        raise ValueError(f"unknown permission transition {transition!r}")
    rec = {"schema": PERMISSION_SCHEMA, "cell": C.TARGET_CELL, "approved_commit": approved_commit,
           "transition": transition, "execution_permission": PERMISSION_TRANSITIONS[transition],
           "authorization_sha256": authorization_sha256, "grant_sha256": grant_sha256,
           "runs_sha256": runs_sha256, "fixture": bool(fixture)}
    rec["sha256"] = body_digest(rec)
    return rec


def write_record(repo, rel: str, obj: dict) -> None:
    """Write a protocol record (authorization or permission) exactly as the verifiers read it."""
    if rel not in (AUTH_REL, PERMISSION_REL):
        raise ValueError(f"{rel!r} is not a protocol record")
    path = _root(repo) / C.NS_REL / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")


def validate_permission(rec: dict | None, *, approved_commit, authorization_sha256,
                        grant_sha256=None, runs_sha256=None, allow_fixture=False) -> list[str]:
    """The TYPED rule for one permission record: schema, cell, approved commit, transition and
    its permission value, the bindings each transition requires, the stored digest."""
    if rec is None:
        return ["permission: no record"]
    p = []
    t = rec.get("transition")
    if rec.get("schema") != PERMISSION_SCHEMA:
        p.append(f"permission: schema {rec.get('schema')!r}")
    if rec.get("sha256") != body_digest(rec):
        p.append("permission: stored sha256 field does not equal the recomputed body digest")
    if t not in PERMISSION_TRANSITIONS:
        return p + [f"permission: unknown transition {t!r}"]
    if rec.get("execution_permission") != PERMISSION_TRANSITIONS[t]:
        p.append(f"permission: transition {t} carries execution_permission "
                 f"{rec.get('execution_permission')!r}")
    if rec.get("cell") != C.TARGET_CELL or rec.get("approved_commit") != approved_commit:
        p.append("permission: bound to another cell or approved commit")
    if rec.get("authorization_sha256") != authorization_sha256:
        p.append("permission: bound to another authorization")
    if t == "GRANT":
        if rec.get("grant_sha256") is not None or rec.get("runs_sha256") is not None:
            p.append("permission: a GRANT binds no earlier record and no run")
    else:
        if rec.get("grant_sha256") != grant_sha256:
            p.append(f"permission: {t} does not end the committed GRANT")
        if t == "EXECUTION_COMPLETED":
            if runs_sha256 is not None and rec.get("runs_sha256") != runs_sha256:
                p.append("permission: EXECUTION_COMPLETED is bound to another runs artifact")
        elif rec.get("runs_sha256") is not None:
            p.append(f"permission: {t} binds a run")
    if rec.get("fixture") and not allow_fixture:
        p.append("permission: a synthetic fixture is not a permission")
    return p


def _protocol_facts(repo) -> dict:
    """Ids only: what each protocol path holds on disk and at HEAD (no content is read)."""
    root = _root(repo)
    f = {}
    for k, rel in PROTOCOL_PATHS.items():
        path = root / C.NS_REL / rel
        head = C.git_object_at("HEAD", ns_path(rel), repo=root)
        disk = C.content_free_id(path) if path.exists() and not path.is_symlink() else None
        f[k] = {"lexists": os.path.lexists(path), "symlink": path.is_symlink(), "disk": disk,
                "head": head, "committed": disk is not None and disk == head}
    return f


def _grant_at_authorization(repo, approved_commit: str, auth_blob: str | None) -> dict | None:
    """The permission GRANT as committed in the commit that introduced the authorization."""
    if not auth_blob:
        return None
    parents = parent_map(repo, approved_commit)
    names = [ns_path(AUTH_REL)]
    ids = _batch_ids(repo, [(c, n) for c in list(parents) + sorted({q for ps in parents.values()
                                                                     for q in ps}) for n in names])
    intro = [c for c in parents if ids[(c, names[0])] == auth_blob
             and not any(ids.get((q, names[0])) == auth_blob for q in parents[c])]
    return artifact_at(repo, intro[0], PERMISSION_REL) if len(intro) == 1 else None


def lifecycle(repo, approved_commit: str, *, runs_sha256: str | None = None,
              allow_fixture: bool = False) -> dict:
    """The execution lifecycle state, DERIVED from what is committed and what is on disk -- never
    stored. Every record present is validated by its typed rule; any combination the transition
    table does not produce is MALFORMED. `runs_sha256` (the comparator's recomputed runs body
    digest) is needed to check the EXECUTION_COMPLETED binding; without it that binding is
    reported unchecked."""
    f = _protocol_facts(repo)
    present = {k: v["lexists"] or v["head"] is not None for k, v in f.items()}
    held = {k for k, v in present.items() if v}
    pr = []
    for k, v in f.items():
        if v["symlink"]:
            pr.append(f"lifecycle: the {k} path is a symlink")
    cmpf = f["comparison"]
    if cmpf["lexists"] and not cmpf["committed"]:
        pr.append("lifecycle: a comparison file already exists at the comparison output path and "
                  "is not committed (untracked, modified or foreign): a stale comparison may not "
                  "masquerade as the current one")
    disk_rec = load_artifact(repo, PERMISSION_REL) if f["permission"]["disk"] else None
    head_rec = artifact_at(repo, "HEAD", PERMISSION_REL) if f["permission"]["head"] else None
    t_disk = (disk_rec or {}).get("transition")
    t_head = (head_rec or {}).get("transition")
    base = {"qualification", "authorization", "permission"}
    committed = lambda *ks: all(f[k]["committed"] for k in ks)
    state = "MALFORMED"
    if not held:
        state = "FROZEN"
    elif held == {"qualification"} and committed("qualification"):
        state = "QUALIFIED"
    elif held == base and committed("qualification", "authorization"):
        if committed("permission") and t_head == "GRANT":
            state = "AUTHORIZED"
        elif t_head == "GRANT" and t_disk == "EXECUTION_STARTED":
            state = "EXECUTING"
        elif committed("permission") and t_head == "EXECUTION_STARTED":
            state = "ABANDONED"
        elif committed("permission") and t_head == "REVOKED_BEFORE_EXECUTION":
            state = "REVOKED_BEFORE_EXECUTION"
    elif held == base | {"runs"} and committed("qualification", "authorization"):
        if t_head == "GRANT" and t_disk == "EXECUTION_COMPLETED" and f["runs"]["disk"] \
                and f["runs"]["head"] is None:
            state = "EXECUTED_UNSEALED"
        elif committed("permission", "runs") and t_head == "EXECUTION_COMPLETED":
            state = "SEALED"
    elif held == base | {"runs", "comparison"} and committed(*PROTOCOL_PATHS) and \
            t_head == "EXECUTION_COMPLETED":
        state = "COMPARED"
    if state == "MALFORMED":
        pr.append(f"lifecycle: the protocol files present ({sorted(held)}; permission at HEAD "
                  f"{t_head}, on disk {t_disk}) are no state of the frozen transition table")
    auth = load_artifact(repo, AUTH_REL) if f["authorization"]["disk"] else None
    auth_digest = body_digest(auth) if auth else None
    grant = head_rec if t_head == "GRANT" else _grant_at_authorization(
        repo, approved_commit, f["authorization"]["head"])
    grant_digest = body_digest(grant) if grant else None
    if "permission" in held:
        if grant is None:
            pr.append("lifecycle: no execution permission GRANT was committed with the "
                      "authorization")
        else:
            pr += [f"lifecycle: GRANT {x}" for x in validate_permission(
                grant, approved_commit=approved_commit, authorization_sha256=auth_digest,
                allow_fixture=allow_fixture)]
            if grant.get("transition") != "GRANT":
                pr.append("lifecycle: the permission committed with the authorization is not a "
                          "GRANT")
        for where, rec in (("at HEAD", head_rec), ("on disk", disk_rec)):
            if rec is not None and rec is not grant and rec.get("transition") != "GRANT":
                pr += [f"lifecycle: permission {where}: {x}" for x in validate_permission(
                    rec, approved_commit=approved_commit, authorization_sha256=auth_digest,
                    grant_sha256=grant_digest, runs_sha256=runs_sha256,
                    allow_fixture=allow_fixture)]
    return {"state": state, "problems": pr, "held": sorted(held),
            "permission_at_head": t_head, "permission_on_disk": t_disk,
            "execution_permission": (disk_rec or {}).get("execution_permission", "DENY"),
            "runs_binding_checked": runs_sha256 is not None,
            "authorization_sha256": auth_digest, "grant_sha256": grant_digest}


def lifecycle_problems(repo, approved_commit: str, stage: str, *, runs_sha256=None,
                       allow_fixture=False) -> list[str]:
    lc = lifecycle(repo, approved_commit, runs_sha256=runs_sha256, allow_fixture=allow_fixture)
    p = list(lc["problems"])
    if lc["state"] != STAGE_STATE[stage]:
        p.append(f"lifecycle: the state is {lc['state']}; stage {stage} requires "
                 f"{STAGE_STATE[stage]}")
    return p


# ---------------------------------------------------------------------------------------------
# authorization -- built only by a future Phase 13 on the user's instruction; never in this turn
# ---------------------------------------------------------------------------------------------
def _authorization_facts(repo, approved_commit: str, *, allow_fixture=False,
                         stage: str = "authorize") -> dict:
    """Recompute, independently, everything an authorization must bind, and require the
    lifecycle state the stage needs (STAGE_STATE). At stage "authorize" (Phase 13) and "run"
    (the runner's pre-flight) no runs or comparison artifact may exist yet; at stage "compare"
    (Phase 15) the runs artifact is the thing being checked."""
    roots = chain_roots(repo)
    p = list(roots["problems"])
    contract = roots.get("contract")
    history = {"problems": [], "introducers": {}, "commits_checked": 0}
    p += approved_commit_problems(repo, approved_commit)
    if contract is not None:
        p += [x for x in verify_frozen_at(repo, approved_commit) if x not in p]
        if not approved_commit_problems(repo, approved_commit):
            history = protocol_history(repo, approved_commit, stage)
            p += history["problems"]
            p += lifecycle_problems(repo, approved_commit, stage, allow_fixture=allow_fixture)
    q = load_artifact(repo, QUAL_REL) if artifact_exists(repo, QUAL_REL) else None
    qv = verify_qualification(repo, q, roots, approved_commit=approved_commit,
                              allow_fixture=allow_fixture)
    p += qv["problems"]
    if stage in ("authorize", "run"):
        for rel, what in (("evidence/runs", "a runs artifact already exists"),
                          ("evidence/comparison", "a comparison already exists")):
            if os.path.lexists(_root(repo) / C.NS_REL / rel):
                p.append(what)
    runner = None
    if contract is not None:
        policy = load_artifact(repo, POLICY_REL)
        ch = policy["configuration"]["chosen"]
        cfg = contract["configuration"]
        if (ch["depth"], ch["panels"]) != (cfg["depth"], cfg["panels"]):
            p.append("the policy's selected configuration is not the contract's")
        rrel = next((r for r in contract["code"] if r.endswith("/c11r_runs.py")), None)
        runner = code_identity(repo, rrel)["sha256"] if rrel else None
        if runner != contract["code"].get(rrel, {}).get("sha256"):
            p.append("the runner is not the bound c11r_runs.py")
    head = C.git_in(_root(repo), "rev-parse", "HEAD")
    return {"problems": p, "roots": roots, "qualification_digest": qv["digest"],
            "runner_sha256": runner, "head": head, "protocol_history": history,
            "configuration": (contract or {}).get("configuration")}


def build_authorization(repo, *, approved_commit: str, operator: str, fixture=False) -> dict:
    """A Phase 13 authorization, bound to RECOMPUTED identities, and the execution permission
    GRANT that goes with it (review 5, R5-1: the authorization is immutable EVIDENCE; the GRANT
    is the switch). Returns both records and the problems; it writes nothing. The two are to be
    committed together, in ONE commit. Refuses (problems non-empty) on any mismatch."""
    f = _authorization_facts(repo, approved_commit, allow_fixture=fixture)
    r = f["roots"]
    auth = {"schema": AUTH_SCHEMA, "authorizes": "ONE_EXECUTION", "cell": C.TARGET_CELL,
            "approved_commit": approved_commit, "issued_at_head": f["head"],
            "execution_contract_sha256": r.get("contract_digest"),
            "gate_sha256": r.get("gate_digest"), "policy_sha256": r.get("policy_digest"),
            "statements_sha256": r.get("statements_digest"),
            "qualification_sha256": f["qualification_digest"],
            "runner_sha256": f["runner_sha256"], "configuration": f["configuration"],
            "operator": operator, "fixture": bool(fixture)}
    auth["sha256"] = body_digest(auth)
    grant = permission_record("GRANT", approved_commit=approved_commit,
                              authorization_sha256=auth["sha256"], fixture=fixture)
    return {"problems": f["problems"], "authorization": auth, "permission": grant}


def verify_authorization(repo, a: dict | None, *, allow_fixture=False,
                         stage: str = "run") -> dict:
    if a is None:
        return {"problems": ["no authorization artifact"], "digest": None, "facts": None}
    p = []
    digest = body_digest(a)
    if a.get("sha256") != digest:
        p.append("authorization: stored sha256 field does not equal the recomputed body digest")
    if a.get("schema") != AUTH_SCHEMA:
        p.append(f"authorization: schema {a.get('schema')!r}")
    if a.get("authorizes") != "ONE_EXECUTION" or a.get("cell") != C.TARGET_CELL or "guard" in a:
        p.append("authorization: does not authorize ONE execution for cell 306 (an authorization "
                 "carries no guard: execution permission is a separate record)")
    if a.get("fixture") and not allow_fixture:
        p.append("authorization: a synthetic fixture is not an authorization")
    f = _authorization_facts(repo, a.get("approved_commit"), allow_fixture=allow_fixture,
                             stage=stage)
    p += f["problems"]
    r = f["roots"]
    for key, want in (("execution_contract_sha256", r.get("contract_digest")),
                      ("gate_sha256", r.get("gate_digest")),
                      ("policy_sha256", r.get("policy_digest")),
                      ("statements_sha256", r.get("statements_digest")),
                      ("qualification_sha256", f["qualification_digest"]),
                      ("runner_sha256", f["runner_sha256"]),
                      ("configuration", f["configuration"])):
        if a.get(key) != want:
            p.append(f"authorization: {key} does not match the recomputed value")
    p += _issue_order(repo, a, f)
    return {"problems": p, "digest": digest, "facts": f}


def _issue_order(repo, a: dict, facts: dict) -> list[str]:
    """COMMIT ORDERING (review 4, N4-10): the authorization was issued at a commit that descends
    from the approved commit and from the commit introducing the qualification it binds, and is
    itself an ancestor of HEAD; the authorization is introduced after that issue point."""
    root = _root(repo)
    p = []
    issued = a.get("issued_at_head")
    approved = a.get("approved_commit")
    if not issued or not C.git_ok_in(root, "cat-file", "-e", f"{issued}^{{commit}}"):
        return ["authorization: issued_at_head is not a commit of this repository"]
    if not approved or not C.git_ok_in(root, "merge-base", "--is-ancestor", approved, issued):
        p.append("authorization: issued at a commit that does not descend from the approved commit")
    if not C.git_ok_in(root, "merge-base", "--is-ancestor", issued, "HEAD"):
        p.append("authorization: issued at a commit that is not in HEAD's history")
    intro = (facts.get("protocol_history") or {}).get("introducers", {})
    q = intro.get("qualification") or []
    if len(q) == 1 and not C.git_ok_in(root, "merge-base", "--is-ancestor", q[0], issued):
        p.append("authorization: issued before the qualification it binds was committed")
    au = intro.get("authorization") or []
    if len(au) == 1 and not C.git_ok_in(root, "merge-base", "--is-ancestor", issued, au[0]):
        p.append("authorization: committed before the commit it claims to be issued at")
    return p


# ---------------------------------------------------------------------------------------------
# the runner's pre-flight (defence in depth: it recomputes everything the authorization did)
# ---------------------------------------------------------------------------------------------
def runner_preflight(repo=None, *, allow_fixture=False, check_processes=True) -> dict:
    """The runner's pre-flight; a tree on which it cannot be evaluated is REFUSED with a typed
    reason, never an exception (review 6, N6-5)."""
    try:
        return _runner_preflight(repo, allow_fixture=allow_fixture,
                                 check_processes=check_processes)
    except TYPED_ERRORS as e:
        try:
            committed = load_artifact(repo, CONTRACT_REL)
        except TYPED_ERRORS:
            committed = None
        return {"problems": [not_evaluable("runner pre-flight", e)]
                + [f"runner pre-flight: {x}" for x in bound_path_problems(repo, committed)],
                "identity": None}


def _runner_preflight(repo=None, *, allow_fixture=False, check_processes=True) -> dict:
    a = load_artifact(repo, AUTH_REL) if artifact_exists(repo, AUTH_REL) else None
    av = verify_authorization(repo, a, allow_fixture=allow_fixture)
    p = list(av["problems"])
    ident = None
    f = av.get("facts")
    if f and f["roots"].get("contract") is not None:
        contract = f["roots"]["contract"]
        for rel, rec in contract["code"].items():
            if code_identity(repo, rel) != rec:
                p.append(f"runner pre-flight: {pathlib.PurePosixPath(rel).name} is not the bound "
                         f"version")
        # what THIS process actually imported (N4-3, R5-2): the code executing is the real
        # checkout's, source-backed, and every module the runner imports at module level is there
        p += [f"runner pre-flight: {x}"
              for x in verify_loaded_modules(contract, role="runner")["problems"]]
        p += [f"runner pre-flight: {x}" for x in launch_policy_problems()]    # L0 (N7-1, N7-2)
        p += [f"runner pre-flight: {x}" for x in code_dir_shadows(contract, repo)]
        if (_root(repo) / C.NS_REL / "evidence" / "runs").exists():
            p.append("runner pre-flight: a runs artifact already exists")
        if check_processes:
            w = PR.campaign_workers()["workers"]
            if w:
                p.append(f"runner pre-flight: other campaign workers are running: {w}")
        ident = {"approved_commit": a.get("approved_commit") if a else None,
                 "execution_contract_sha256": f["roots"]["contract_digest"],
                 "gate_sha256": f["roots"].get("gate_digest"),
                 "qualification_sha256": f["qualification_digest"],
                 "authorization_sha256": av["digest"],
                 "policy_sha256": f["roots"].get("policy_digest"),
                 "statements_sha256": f["roots"].get("statements_digest"),
                 "runner_sha256": f["runner_sha256"],
                 "configuration": f["configuration"],
                 "code_sha256": {rel: rec["sha256"] for rel, rec in contract["code"].items()}}
    return {"problems": p, "identity": ident}


# ---------------------------------------------------------------------------------------------
# the run artifact's identity, checked against the RECOMPUTED chain (predicate G20)
# ---------------------------------------------------------------------------------------------
def verify_run_identity(runs: dict, facts: dict, auth_digest: str | None) -> list[str]:
    """The run was produced under exactly this contract, gate, qualification, authorization,
    policy, statement table, runner, code and configuration -- all recomputed, none trusted."""
    p = []
    r = facts["roots"]
    contract = r["contract"]
    ident = runs.get("execution_identity") or {}
    want = {"execution_contract_sha256": r["contract_digest"],
            "gate_sha256": r.get("gate_digest"),
            "qualification_sha256": facts["qualification_digest"],
            "authorization_sha256": auth_digest,
            "policy_sha256": r.get("policy_digest"),
            "statements_sha256": r.get("statements_digest"),
            "runner_sha256": facts["runner_sha256"],
            "configuration": facts["configuration"],
            "code_sha256": {rel: rec["sha256"] for rel, rec in contract["code"].items()}}
    for k, v in want.items():
        if ident.get(k) != v:
            p.append(f"run: execution_identity.{k} does not match the recomputed chain")
    if runs.get("policy_sha256") != r.get("policy_digest") or \
            runs.get("statements_sha256") != r.get("statements_digest"):
        p.append("run: policy/statement digests are not the frozen ones")
    if list(runs.get("drift_block", [])) != contract["scope"]["drift_block"]:
        p.append("run: drift block is not the contract's")
    prov = runs.get("provenance", {})
    if prov.get("producer_sha256") != facts["runner_sha256"]:
        p.append("run: produced by another runner than the bound c11r_runs.py")
    # N4-1: the run's recorded code closure is EXACTLY the runner's closure, every file at the
    # contract's hash -- a missing, extra or foreign module refuses, not only a changed one.
    closure = prov.get("code_closure", {})
    want_set = runner_closure(contract)
    if set(closure) != want_set:
        p.append(f"run: recorded code closure is not the runner's closure (missing "
                 f"{sorted(pathlib.PurePosixPath(x).name for x in want_set - set(closure))}, "
                 f"extra {sorted(pathlib.PurePosixPath(x).name for x in set(closure) - want_set)})")
    for rel, sha in closure.items():
        if rel in contract["code"] and contract["code"][rel]["sha256"] != sha:
            p.append(f"run: executed with another {pathlib.PurePosixPath(rel).name} than the bound one")
    cert_code = {pathlib.PurePosixPath(rel).name: rec["sha256"]
                 for rel, rec in contract["code"].items()}
    for cid, c in S.certificates(runs).items():
        mod = c.get("certifier", {}).get("module")
        if mod in cert_code and c["certifier"].get("module_sha256") != cert_code[mod]:
            p.append(f"run: certificate {cid} was made by another {mod} than the bound one")
    return p


def runner_closure(contract: dict) -> set[str]:
    """The runner's transitive import closure, as bound: every member must be a contract file."""
    got = set(C.code_closure(C.HERE / "c11r_runs.py"))
    return got if got <= set(contract["code"]) else got | {"<outside the contract>"}


def expected_certifier_sha(contract: dict) -> dict:
    """The certifier hashes a certificate must carry -- from the FROZEN contract, never the tree."""
    import c11r_certificate as CV
    names = {pathlib.PurePosixPath(rel).name: rec["sha256"] for rel, rec in contract["code"].items()}
    return {m: names.get(m) for m in CV.CERTIFIER_MODULES}


def main() -> int:
    for rel in BOUND_ARTIFACTS.values():
        C.load_allowlisted(rel)                  # recorded as inputs for status freshness
    body = contract_body(C.REPO)
    problems = []
    for name, rec in body["artifacts"].items():
        problems += verify_artifact_record(C.REPO, name, rec, body["code"])
    if problems:
        print("REFUSE: the bound artifacts are not self-consistent:")
        for x in problems:
            print(f"  - {x}")
        return 1
    s = C.write_evidence(C.NS / CONTRACT_REL, body, producer=__file__)
    check = verify_contract(C.REPO)
    print(f"contract binds {len(body['code'])} code files, {len(body['artifacts'])} artifacts, "
          f"configuration D{body['configuration']['depth']}/P{body['configuration']['panels']}")
    print(f"re-verification after write: {check['problems'] or 'no problems'}")
    print(f"wrote {CONTRACT_REL} sha256 {s[:16]}...")
    return 0 if not check["problems"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
