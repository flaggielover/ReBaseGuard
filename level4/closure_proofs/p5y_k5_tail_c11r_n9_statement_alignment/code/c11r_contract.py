"""C11R round 4 -- THE FROZEN EXECUTION CONTRACT and the end-to-end identity chain (R3-1).

WHAT WAS WRONG (review round 3, blocker R3-1; erratum E25). Execution, seal and comparison were
linked only by the hash of c11r_runs.py and by the SELF-DECLARED `sha256` fields of the policy and
the statement table. The comparator took its "expected" certifier and producer hashes from the
seal commit's own tree, so a certifier edited, committed, used and reverted before the seal was
accepted; a policy edited in place with its sha256 field left alone passed authorization.

THE ROOT OF TRUST. config/C11R_CONTRACT.json, as committed at the REVIEWED commit A. A commit
cannot contain its own hash, so A is not written into the contract: the Phase 13 authorization
names A, the runner and the comparator are given A, and every boundary checks that the contract
(and every other frozen path) in the tree is byte-identical to its version at A and that no commit
after A touched any of them.

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

WHAT THE CHAIN DOES NOT COVER, stated exactly. (1) The runner's pre-flight hashes the files ON
DISK after the process has imported them: a deliberately malicious operator who swaps a module
between import and pre-flight, and restores it, is not detected by the pre-flight (the process
detector and the clean-tree and range checks bound, but do not close, that window). (2) A runs
artifact hand-written without running the frozen runner at all is detectable only by
re-executing the certifiers (see c11r_certificate). (3) The root of trust is the reviewed commit
as named by the user's Phase 13 authorization and supplied to the comparator; a wrong commit
supplied by the operator is refused only if its contract differs from the one the authorization
and the frozen paths carry.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_procs as PR
import c11r_schema as S

CONTRACT_SCHEMA = "C11R_CONTRACT/1"
QUAL_SCHEMA = "C11R_QUALIFICATION/4"
AUTH_SCHEMA = "C11R_AUTHORIZATION/4"
CONTRACT_REL = "config/C11R_CONTRACT.json"
GATE_REL = "config/N9R_GATE_C11R.json"
POLICY_REL = "config/C11R_POLICY.json"
STMT_REL = "evidence/table/C11R_N9_STATEMENTS.json"
COST_REL = "evidence/cost/C11R_COST.json"
QUAL_REL = "evidence/qualification/C11R_QUALIFICATION.json"
AUTH_REL = "config/C11R_AUTHORIZATION.json"
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
}
CODE_ROOTS = tuple(sorted(set(ROLES.values())))
REQUIRED_PREDICATES = {
    "G2": "c11r_certificate.py:reconstruct",
    "G8": "c11r_certificate.py:dispositions",
    "G10": "c11r_certificate.py:screen_order",
    "G18": "c11r_certificate.py:evaluate_target",
    "G19": "c11r_certificate.py:configuration_adherence",
    "G20": "c11r_contract.py:verify_run_identity",
}
HOST_KEYS = ("node", "machine", "cpu_brand", "ncpu", "python", "implementation")


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
        "contains_target_results": False,
    }


COMPARED_KEYS = ("schema", "scope", "roles", "code", "artifacts", "scientific_inputs", "schemas",
                 "configuration", "comparison_rule", "cost_host", "required_predicates",
                 "contains_target_results")


def frozen_paths(contract: dict) -> list[str]:
    """Every path whose bytes the reviewed commit fixes: the code closure, the bound artifacts and
    the namespace artifacts they declare as inputs, the contract itself and the gate."""
    declared = {inp for a in contract["artifacts"].values()
                for inp in a.get("declared_inputs", {}) if inp.startswith(C.NS_REL + "/")}
    return sorted(set(contract["code"]) | {ns_path(a["path"]) for a in contract["artifacts"].values()}
                  | declared | {ns_path(CONTRACT_REL), ns_path(GATE_REL)})


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


def verify_contract(repo=None) -> dict:
    """Recompute the contract from bytes and compare it with the committed one."""
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
    return {"problems": problems, "digest": digest, "contract": obj,
            "file_sha256": C.sha256_bytes(raw)}


def verify_frozen_at(repo, approved_commit: str, contract: dict) -> list[str]:
    """Every frozen path is byte-identical to its version at the approved commit, HEAD descends
    from it, no later commit touched a frozen path, and none has uncommitted changes."""
    p = []
    root = _root(repo)
    if not approved_commit or not C.git_ok_in(root, "cat-file", "-e", f"{approved_commit}^{{commit}}"):
        return [f"approved commit {approved_commit!r} does not exist in this repository"]
    if not C.git_ok_in(root, "merge-base", "--is-ancestor", approved_commit, "HEAD"):
        p.append("HEAD does not descend from the approved commit")
    paths = frozen_paths(contract)
    for rel in paths:
        at = C.git_object_at(approved_commit, rel, repo=root)
        now = C.content_free_id(root / rel)
        if at != now:
            p.append(f"frozen path {pathlib.PurePosixPath(rel).name} differs from the approved commit")
    touched = C.git_in(root, "log", "--format=%H", f"{approved_commit}..HEAD", "--", *paths)
    if touched:
        p.append(f"{len(touched.split())} commit(s) after the approved commit touched a frozen path "
                 f"(edited-then-reverted changes included)")
    dirty = C.git_in(root, "status", "--porcelain", "--", *paths)
    if dirty:
        p.append("a frozen path has uncommitted changes")
    return p


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


def verify_qualification(repo, q: dict | None, roots: dict, *, allow_fixture=False) -> dict:
    p = []
    if q is None:
        return {"problems": ["no qualification artifact"], "digest": None}
    digest = body_digest(q)
    if q.get("sha256") != digest:
        p.append("qualification: stored sha256 field does not equal the recomputed body digest")
    if q.get("schema") != QUAL_SCHEMA:
        p.append(f"qualification: schema {q.get('schema')!r}, expected {QUAL_SCHEMA!r}")
    b = q.get("bound", {})
    for key, want in (("execution_contract_sha256", roots.get("contract_digest")),
                      ("gate_sha256", roots.get("gate_digest")),
                      ("policy_sha256", roots.get("policy_digest")),
                      ("statements_sha256", roots.get("statements_digest"))):
        if b.get(key) != want:
            p.append(f"qualification: {key} belongs to another contract or tree")
    code = (roots.get("contract") or {}).get("code", {})
    qrel = next((r for r in code if r.endswith("/c11r_qualify.py")), None)
    qsha = code.get(qrel, {}).get("sha256") if qrel else None
    if b.get("qualifier_sha256") != qsha:
        p.append("qualification: produced by another qualifier than the bound one")
    if q.get("provenance", {}).get("producer_sha256") != qsha:
        p.append("qualification: provenance producer is not the bound qualifier")
    items = q.get("items", [])
    failed = [i.get("id") for i in items if not i.get("pass")]
    if not items:
        p.append("qualification: no items")
    if q.get("QUALIFICATION_CLASS") != "PASS":
        p.append(f"qualification: class {q.get('QUALIFICATION_CLASS')!r}")
    if failed or q.get("failed"):
        p.append(f"qualification: PASS claimed with failing items {failed or q.get('failed')}")
    env = q.get("environment", {}).get("host", {})
    if env != (roots.get("contract") or {}).get("cost_host"):
        p.append("qualification: environment is not the host the cost model was measured on")
    if env != current_host():
        p.append("qualification: environment is not this host")
    if q.get("fixture") and not allow_fixture:
        p.append("qualification: a synthetic fixture is not a qualification")
    return {"problems": p, "digest": digest}


# ---------------------------------------------------------------------------------------------
# authorization -- built only by a future Phase 13 on the user's instruction; never in this turn
# ---------------------------------------------------------------------------------------------
def _authorization_facts(repo, approved_commit: str, *, allow_fixture=False,
                         stage: str = "authorize") -> dict:
    """Recompute, independently, everything an authorization must bind. At stage "authorize"
    (Phase 13) and "run" (the runner's pre-flight) no runs or comparison artifact may exist yet;
    at stage "compare" (Phase 15) the runs artifact is the thing being checked."""
    roots = chain_roots(repo)
    p = list(roots["problems"])
    contract = roots.get("contract")
    if contract is not None:
        p += verify_frozen_at(repo, approved_commit, contract)
    q = load_artifact(repo, QUAL_REL) if artifact_exists(repo, QUAL_REL) else None
    qv = verify_qualification(repo, q, roots, allow_fixture=allow_fixture)
    p += qv["problems"]
    if stage in ("authorize", "run"):
        for rel, what in (("evidence/runs", "a runs artifact already exists"),
                          ("evidence/comparison", "a comparison already exists")):
            if (_root(repo) / C.NS_REL / rel).exists():
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
            "runner_sha256": runner, "head": head,
            "configuration": (contract or {}).get("configuration")}


def build_authorization(repo, *, approved_commit: str, operator: str, fixture=False) -> dict:
    """A Phase 13 authorization, bound to RECOMPUTED identities. Returns the record and the
    problems; it writes nothing. Refuses (problems non-empty) on any mismatch."""
    f = _authorization_facts(repo, approved_commit, allow_fixture=fixture)
    r = f["roots"]
    auth = {"schema": AUTH_SCHEMA, "guard": "ALLOW", "cell": C.TARGET_CELL,
            "approved_commit": approved_commit, "issued_at_head": f["head"],
            "execution_contract_sha256": r.get("contract_digest"),
            "gate_sha256": r.get("gate_digest"), "policy_sha256": r.get("policy_digest"),
            "statements_sha256": r.get("statements_digest"),
            "qualification_sha256": f["qualification_digest"],
            "runner_sha256": f["runner_sha256"], "configuration": f["configuration"],
            "operator": operator, "fixture": bool(fixture)}
    auth["sha256"] = body_digest(auth)
    return {"problems": f["problems"], "authorization": auth}


def verify_authorization(repo, a: dict | None, *, allow_fixture=False,
                         stage: str = "run") -> dict:
    if a is None:
        return {"problems": ["no authorization; guard is DENY"], "digest": None, "facts": None}
    p = []
    digest = body_digest(a)
    if a.get("sha256") != digest:
        p.append("authorization: stored sha256 field does not equal the recomputed body digest")
    if a.get("schema") != AUTH_SCHEMA:
        p.append(f"authorization: schema {a.get('schema')!r}")
    if a.get("guard") != "ALLOW" or a.get("cell") != C.TARGET_CELL:
        p.append("authorization: not an ALLOW for cell 306")
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
    return {"problems": p, "digest": digest, "facts": f}


# ---------------------------------------------------------------------------------------------
# the runner's pre-flight (defence in depth: it recomputes everything the authorization did)
# ---------------------------------------------------------------------------------------------
def runner_preflight(repo=None, *, allow_fixture=False, check_processes=True) -> dict:
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
    for rel, sha in prov.get("code_closure", {}).items():
        if rel in contract["code"] and contract["code"][rel]["sha256"] != sha:
            p.append(f"run: executed with another {pathlib.PurePosixPath(rel).name} than the bound one")
    cert_code = {pathlib.PurePosixPath(rel).name: rec["sha256"]
                 for rel, rec in contract["code"].items()}
    for cid, c in S.certificates(runs).items():
        mod = c.get("certifier", {}).get("module")
        if mod in cert_code and c["certifier"].get("module_sha256") != cert_code[mod]:
            p.append(f"run: certificate {cid} was made by another {mod} than the bound one")
    return p


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
