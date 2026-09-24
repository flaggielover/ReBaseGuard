"""C11R Phase 15 -- the sealed comparison. Revision 7 (N6-3, N6-5; R5-1, N5-2, N5-7, E45; R4-1,
N4-5, N4-8 kept).

REVISION 7 (review 6; errata E50, E52). N6-3: round 6 wrote the comparison artifact even when the
chain refused BEFORE the loader; `phase15` is now ONE transaction -- verify, load iff every step
passed, compute, write exactly once -- and a refusal writes NOTHING (c11r_contract.
COMPARISON_TRANSACTION states the retry rule). N6-5: every step is typed; a directory, a symlink or
malformed JSON where the runs artifact belongs refuses with a reason instead of raising.

ONE OF EXACTLY TWO MODULES PERMITTED TO LOAD AN ORIGINAL MAGNITUDE, and it does so only through
the `loader` that `execute_comparison` calls AFTER every verification step has passed.

THE ROOT OF TRUST (round 4, erratum E25). The operator supplies the APPROVED commit A (the one the
review passed); the frozen execution contract AS COMMITTED AT A is the authority, and nothing is
taken from the tree being checked without being recomputed and compared with it.

REVISION 5. Review round 4 found (R4-1) that the seal was located with `git log -- <runs path>`,
whose default history simplification hides a run committed and discarded on a merged side
branch, and (N4-5) that the magnitude loader ran BEFORE the G8/G10/G19 guards were evaluated,
and (N4-8) that a demoted target never reached the verdict. Now:

THE ORDER IN `execute_comparison` (STEPS; each recorded, in order, with its problems):
   1  approved commit   -- A is a full, self-naming 40-hex commit id (round 6, N5-7), the
                           authorization names A, HEAD descends from A, A carries a contract;
   2  complete history  -- c11r_contract.frozen_state (tree identity AND history purity over
                           EVERY commit reachable after A; replace objects disabled; grafts and
                           shallow history refused) and protocol_history (no comparison, no
                           discarded run, qualification and authorization introduced once and
                           in order before the seal) and the LIFECYCLE (round 6, R5-1): SEALED,
                           execution permission DENY/EXECUTION_COMPLETED bound to THIS run's
                           recomputed digest, the authorization untouched, nothing at the
                           comparison output path (N5-2);
   3  contract          -- recomputed from bytes; equal to the contract at A;
   4  gate              -- bound to that contract, the policy and the statement table;
   5  qualification     -- the typed Q1-Q18 schema, bound to the contract and to A;
   6  authorization     -- every identity recomputed (stage "compare");
   7  run               -- the run's schema, stored digest, execution identity and code closure
                           (G20);
   8  seal              -- exactly one sealing commit in complete history, the file is its blob,
                           no uncommitted change;
   9  G8, 10 G10, 11 G19 -- the production guards, with the certifier hashes the FROZEN contract
                           fixes;
  12  other predicates  -- value tracing (including the demotion check), reconstruction,
                           independence, STATEMENT equivalence, the loaded-module identity and the
                           frozen comparison rule;
  13  ONLY THEN the loader (the original magnitudes; the quarantine, first checked against the
      content-free id the statement table recorded);
  14  numerical agreement per statement-equivalent target, the opposite-direction check, and the
      N9 classification by the frozen precedence; only then any prose.
ANY failure in 1-12 -> EXECUTION_INVALID (INDEPENDENCE_VIOLATION when the chain verified and a
certificate uses the original's graph), and the loader is NOT called; the chain controls prove it
with a loader spy for each refusal class. Such a refusal is REPORTED, never written (revision 7).

NOTHING HERE IS A PRE-WRITTEN CONCLUSION: every sentence is rendered from computed fields.

REACHABILITY, stated per path rather than claimed wholesale (erratum E19). In production, D1 and D2
are NOT_IMPLEMENTED, so N9_CLOSED is unreachable by scope. INVALID, INDEPENDENCE_VIOLATION and
EXECUTION_INVALID are reachable from genuine artifacts whose certificates do not establish what
their targets claim. DISAGREES requires an independent bound on an original quantity in the
OPPOSITE direction; no implemented certifier produces one, so it is reachable only through a
deduction no production certifier has -- and, since revision 7, through a certificate beyond the
frozen F_K, F_H, F_D, which the run step refuses (N6-4) -- and the self-test exercises it that way,
on the pure classification functions.
"""
# --- C11R PRE-IMPORT BARRIER (review 6, R6-1): the first statement, before any other import ---
import os as _os
import sys as _sys


def _c11r_preimport_barrier():
    """Refuse to start while a campaign code directory holds anything a standard-library import
    could resolve to. Only `os` and `sys` are used: the interpreter loaded both before this
    script's directory was put on sys.path (c11r_contract.PREIMPORT_BARRIER)."""
    here = _os.path.dirname(_os.path.realpath(__file__))
    closure = _os.path.dirname(_os.path.dirname(here))
    bad = []
    for d in (here, _os.path.join(closure, "p5y_k5_tail_c11_n9_independent_certifier", "code"),
              _os.path.join(closure, "p5y_k5_tail_c7_e2_lambda309", "code")):
        if _os.path.islink(d) or not _os.path.isdir(d):
            bad.append(d)
            continue
        for e in sorted(_os.listdir(d)):
            p = _os.path.join(d, e)
            if e == "__pycache__" and _os.path.isdir(p) and not _os.path.islink(p):
                continue
            if (not e.endswith(".py") or _os.path.islink(p) or not _os.path.isfile(p)
                    or e[:-3] in _sys.stdlib_module_names or e[:-3] in _sys.builtin_module_names):
                bad.append(_os.path.basename(_os.path.dirname(d)) + "/code/" + e)
    if bad:
        raise SystemExit("REFUSE (pre-import barrier, review 6 R6-1): a campaign code directory "
                         "holds an entry a standard-library import could resolve to: "
                         + ", ".join(bad))


_c11r_preimport_barrier()
# --- end of the pre-import barrier ---

import os
import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_certificate as CV
import c11r_common as C
import c11r_contract as CT
import c11r_equiv as EQ
import c11r_schema as S

RUNS_REL = CT.RUNS_REL
FACTOR = 2
PRECEDENCE = ("INDEPENDENCE_VIOLATION", "SCIENTIFIC_DISAGREEMENT", "EXECUTION_INVALID",
              "N9_CLOSED", "AGREEMENT_INSUFFICIENT")


# ---------------------------------------------------------------------------------------------
# 1. the seal
# ---------------------------------------------------------------------------------------------
def verify_seal_bytes(disk: bytes | None, committed: bytes | None, dirty: bool) -> list[str]:
    """The ORDERING part of the seal, testable without any runs artifact existing."""
    p = []
    if disk is None:
        p.append("no runs artifact on disk")
    if committed is None:
        p.append("the runs artifact was never committed, so no ordering can be established")
    if disk is not None and committed is not None and disk != committed:
        p.append("the file on disk differs from the committed blob")
    if dirty:
        p.append("the runs artifact has uncommitted changes")
    return p


def _real_repository_guard(root: pathlib.Path) -> None:
    """The REAL runs artifact carries prospective target values: in the real repository it is
    read only by this module run as Phase 15. Any other program may exercise the seal and chain
    checks only on a synthetic repository (the chain controls do)."""
    if root.resolve() == C.REPO.resolve() and C.running_reader() != "c11r_compare.py":
        raise PermissionError("the real runs artifact is read only by c11r_compare.py as Phase 15")


def verify_seal(repo=None, *, approved_commit: str) -> dict:
    """The seal, recomputed over COMPLETE reachable history (review 4, R4-1): the runs artifact
    was introduced by exactly ONE commit after the approved commit (the seal), no reachable
    commit holds any other runs content (a replaced, hidden or discarded run on any branch), the
    file on disk is the sealed blob with no uncommitted change, and its canonical body hashes to
    its stored sha256. Nothing is trusted."""
    root = pathlib.Path(repo) if repo is not None else C.REPO
    _real_repository_guard(root)
    rel = f"{C.NS_REL}/{RUNS_REL}"
    runs, disk, shape = read_runs(root)                   # typed shape (N6-5), read once
    hist = CT.protocol_history(repo, approved_commit, "compare")
    intro = hist["introducers"].get("runs", [])
    seal_commit = intro[0] if len(intro) == 1 else None
    committed = C.blob_at_in(root, seal_commit, rel) if seal_commit else None
    dirty = bool(C.git_in(root, "status", "--porcelain", "--", rel)) if disk is not None else False
    problems = shape + verify_seal_bytes(disk, committed, dirty)
    if len(intro) > 1:
        problems.append(f"the runs artifact was introduced by {len(intro)} commits: an earlier "
                        f"seal exists in reachable history")
    other = hist["foreign"].get("runs", [])
    if other:
        problems.append(f"the runs artifact was changed after it was sealed, or another run was "
                        f"committed and discarded ({len(other)} reachable commits hold other "
                        f"runs content)")
    if runs is not None:
        problems += S.validate_runs(runs)
        if runs.get("sha256") != CT.body_digest(runs):
            problems.append("the runs artifact's stored sha256 does not equal its recomputed "
                            "canonical body digest")
    return {"problems": problems, "seal_commit": seal_commit, "runs": runs,
            "runs_file_sha256": C.sha256_bytes(disk) if disk else None}


def comparison_rule_problems(stmt: dict, gate: dict, contract: dict) -> list[str]:
    """The agreement rule this comparator applies must be the FROZEN one (review 3, N-3/N-6):
    its factor equals the statement table's, the contract's and the gate's, and the gate's rule
    is the table's. A threshold changed after the freeze is EXECUTION_INVALID."""
    p = []
    rule = stmt.get("comparison_semantics_frozen_before_results", {})
    if rule.get("factor") != FACTOR or contract.get("comparison_rule", {}).get("factor") != FACTOR:
        p.append(f"the frozen comparison factor {rule.get('factor')} is not this "
                 f"comparator's {FACTOR}")
    if contract.get("comparison_rule", {}).get("rule_sha256") != C.sha256_obj(rule):
        p.append("the statement table's comparison rule is not the one the contract froze")
    if gate.get("comparison_rule") != rule:
        p.append("the gate's comparison rule is not the statement table's")
    return p


# ---------------------------------------------------------------------------------------------
# 2. THE ORDER (review round 4, N4-5). Every step below runs BEFORE the magnitude loader, in this
#    order; the loader is called only when ALL of them pass. A step whose prerequisite failed is
#    recorded as not evaluated. Nothing before step 13 reads the quarantine.
# ---------------------------------------------------------------------------------------------
STEPS = ("approved commit", "complete frozen history", "contract", "gate", "qualification",
         "authorization", "run", "seal", "G8", "G10", "G19",
         "other execution-integrity predicates")


def read_runs(root: pathlib.Path) -> tuple[dict | None, bytes | None, list[str]]:
    """The runs artifact, read ONCE, with its SHAPE refused by a typed reason (review 6, N6-3 and
    N6-5): a directory, a symlink (inside, outside, dangling, a loop), unreadable or malformed
    JSON never raises."""
    import json
    path = root / C.NS_REL / RUNS_REL
    k = C.path_kind(path, inside=root)
    if k == "ABSENT":
        return None, None, []
    if k != "FILE":
        return None, None, [f"the runs artifact path is {CT.KIND_TEXT[k]}"]
    try:
        raw = path.read_bytes()
        obj = json.loads(raw)
    except (OSError, ValueError) as e:
        return None, None, [f"the runs artifact is not readable JSON ({type(e).__name__})"]
    if not isinstance(obj, dict):
        return None, raw, ["the runs artifact is not a JSON object"]
    return obj, raw, []


def execute_comparison(repo=None, *, approved_commit: str, loader, allow_fixture: bool = False) -> dict:
    """The whole Phase 15 path. Steps 1-12 (STEPS) verify; step 13 -- the loader, the ONLY
    access to original magnitudes -- runs only when all twelve pass; step 14 classifies. A step
    that cannot be evaluated on the tree in front of it REFUSES with a typed reason (review 6,
    N6-5): no path through steps 1-12 raises."""
    root = pathlib.Path(repo) if repo is not None else C.REPO
    _real_repository_guard(root)
    steps, seen = [], []

    def step(name, problems, evaluated=True):
        new = [x for x in problems if x not in seen]
        seen.extend(new)
        steps.append({"step": len(steps) + 1, "name": name, "evaluated": evaluated,
                      "problems": new, "pass": bool(evaluated and not new)})
        assert steps[-1]["name"] == STEPS[len(steps) - 1]

    def attempt(where, fn, default=None):
        try:
            return fn(), []
        except CT.TYPED_ERRORS as e:
            return default, [CT.not_evaluable(where, e)]

    a, p = attempt("authorization artifact", lambda: CT.load_artifact(repo, CT.AUTH_REL)
                   if CT.artifact_exists(repo, CT.AUTH_REL) else None)
    # 1 approved commit -- a full, self-naming commit id (review 5, N5-7), never a movable ref
    bad, q = attempt("approved commit", lambda: CT.approved_commit_problems(repo, approved_commit),
                     ["the approved commit could not be checked"])
    p += bad + q
    a_exists = not (bad or q)
    if a is None:
        p.append("no authorization artifact")
    elif a.get("approved_commit") != approved_commit:
        p.append("the authorization names another approved commit than the operator supplied")
    if a_exists and not C.git_ok_in(root, "merge-base", "--is-ancestor", approved_commit, "HEAD"):
        p.append("HEAD does not descend from the approved commit")
    frozen, q = attempt("approved commit", lambda: CT.contract_at(repo, approved_commit)
                        if a_exists else None)
    p += q
    if a_exists and frozen is None:
        p.append("the approved commit carries no execution contract")
    step("approved commit", p)
    # the run artifact is read HERE (the comparator is its only reader) so that its recomputed
    # digest can be checked against the DENY/EXECUTION_COMPLETED record in step 2; its SHAPE is
    # refused with a typed reason (N6-3, N6-5)
    runs, _, runs_problems = read_runs(root)
    # 2 complete frozen history, protocol history, and the LIFECYCLE: SEALED, execution
    #   permission DENY/EXECUTION_COMPLETED bound to THIS run, the authorization untouched, and no
    #   comparison file already at the output path (review 5, R5-1, N5-2)
    if frozen is not None:
        def history():
            fs = CT.frozen_state(repo, approved_commit)
            ph = CT.protocol_history(repo, approved_commit, "compare")
            lc = CT.lifecycle_problems(repo, approved_commit, "compare",
                                       allow_fixture=allow_fixture,
                                       runs_sha256=CT.body_digest(runs) if runs is not None
                                       else None)
            return fs["ancestry"] + fs["tree_identity"] + fs["history_purity"] + ph["problems"] + lc
        hp, q = attempt("complete frozen history", history, [])
        step("complete frozen history", runs_problems + hp + q)
    else:
        step("complete frozen history", [], evaluated=False)
    # 3 contract, 4 gate -- recomputed from bytes; the tree's contract must BE the frozen one
    cv = CT.verify_contract(repo)                         # typed by construction (N6-5)
    p = list(cv["problems"])
    if frozen is not None and cv["contract"] is not None and cv["contract"] != frozen:
        p.append("the contract in the tree is not the contract at the approved commit")
    step("contract", p)
    roots, q = attempt("gate", lambda: CT.chain_roots(repo) if cv["contract"] is not None
                       else None)
    step("gate", [x for x in (roots or {}).get("problems", []) if x.startswith("gate")] + q,
         evaluated=roots is not None or bool(q))
    # 5 qualification
    if roots is not None:
        qv, q = attempt("qualification", lambda: CT.verify_qualification(
            repo, CT.load_artifact(repo, CT.QUAL_REL) if CT.artifact_exists(repo, CT.QUAL_REL)
            else None, roots, approved_commit=approved_commit, allow_fixture=allow_fixture),
            {"problems": []})
        step("qualification", qv["problems"] + q)
    else:
        step("qualification", [], evaluated=False)
    # 6 authorization (it recomputes everything above again, independently; only NEW problems
    #   are listed here)
    av, q = attempt("authorization", lambda: CT.verify_authorization(
        repo, a, allow_fixture=allow_fixture, stage="compare"),
        {"problems": [], "digest": None, "facts": None})
    step("authorization", av["problems"] + q)
    facts = av.get("facts")
    contract = frozen if frozen is not None else (facts or {}).get("roots", {}).get("contract")
    # 7 run -- the run artifact's own integrity and its execution identity (G20)
    if runs is not None and facts and contract is not None:
        def run_checks():
            r = S.validate_runs(runs)
            if runs.get("sha256") != CT.body_digest(runs):
                r.append("the runs artifact's stored sha256 does not equal its recomputed "
                         "canonical body digest")
            return r + CT.verify_run_identity(runs, facts, av["digest"])
        rp, q = attempt("run", run_checks, [])
        step("run", rp + q)
    else:
        step("run", ["no runs artifact"] if runs is None else [], evaluated=runs is None)
    # 8 seal
    if a_exists:
        seal, q = attempt("seal", lambda: verify_seal(repo, approved_commit=approved_commit),
                          {"problems": [], "seal_commit": None, "runs_file_sha256": None})
        seal["problems"] = seal["problems"] + q
    else:
        seal = {"problems": ["no approved commit to seal against"], "seal_commit": None,
                "runs_file_sha256": None}
    step("seal", seal["problems"])
    chain_ok = all(s_["pass"] for s_ in steps)
    pre = None
    if chain_ok:
        def guards_and_predicates():
            stmt_ = CT.load_artifact(repo, CT.STMT_REL)
            policy = CT.load_artifact(repo, CT.POLICY_REL)
            pre_ = pre_numeric(runs, stmt_, policy,
                               expected_certifier_sha=CT.expected_certifier_sha(contract),
                               runs_producer={"module": "c11r_runs.py",
                                              "sha256": facts["runner_sha256"]})
            g = pre_["guards"]
            other = [f"value trace: {k}: {v}" for k, v in g["value_trace"]["violations"].items()]
            other += [f"{k}: {pre_['per'][k]['why']}" for k in S.SIX_CONSTANTS
                      if pre_["per"][k]["CLASS"] == "INVALID"]
            other += [f"independence violation: {k}" for k in pre_["violations"]]
            other += CT.verify_loaded_modules(contract, role="comparator")["problems"]
            other += CT.code_dir_shadows(contract, repo)
            other += comparison_rule_problems(stmt_, facts["roots"].get("gate") or {}, contract)
            return stmt_, pre_, other
        res, q = attempt("guards and predicates", guards_and_predicates)
        if res is None:
            for name in STEPS[len(steps):]:
                step(name, q if name == STEPS[-1] else [], evaluated=name == STEPS[-1])
        else:
            stmt, pre, other = res
            g = pre["guards"]
            step("G8", [f"G8: {x}" for x in g["G8"]["violations"]])
            step("G10", [f"G10: {x}" for x in g["G10"]["violations"]])
            step("G19", [f"G19: {x}" for x in g["G19"]["violations"]])
            step("other execution-integrity predicates", other)
    else:
        for name in STEPS[len(steps):]:
            step(name, [], evaluated=False)
    problems = [x for s_ in steps for x in s_["problems"]]
    out = {"steps": steps, "seal": {k: seal.get(k) for k in ("seal_commit", "runs_file_sha256")}}
    if problems or not all(s_["pass"] for s_ in steps):
        verdict = ("INDEPENDENCE_VIOLATION" if chain_ok and pre and pre["violations"]
                   else "EXECUTION_INVALID")
        refused = next(s_ for s_ in steps if not s_["pass"])
        out.update(N9_VERDICT=verdict, identity_problems=problems or ["a step was not evaluated"],
                   loader_called=False, refused_at_step=refused["step"],
                   refused_at=refused["name"])
        return out
    mags = loader(stmt)                                   # 13: only now, only here
    result = numeric_phase(pre, stmt, mags)               # 14
    result.update(out, loader_called=True, identity_problems=[], refused_at_step=None,
                  refused_at=None)
    return result


# ---------------------------------------------------------------------------------------------
# 3. the ONLY magnitude load in the campaign outside the extractor
# ---------------------------------------------------------------------------------------------
def load_original_magnitudes(stmt_table: dict) -> dict:
    qpath = C.NS / C.QUARANTINE_REL
    recorded = stmt_table.get("quarantine", {}).get("content_free_id")
    now = C.content_free_id(qpath)
    if not recorded or now != recorded:
        raise SystemExit("REFUSE: the quarantine is not the one the statement table recorded")
    with C.sanctioned_protected_access("load the originals after the chain and guards verify"):
        q = C.load(qpath)
    return {k: F(v["value"]) for k, v in q["magnitudes"].items()}


# ---------------------------------------------------------------------------------------------
# 4. classification -- pure functions of their arguments
# ---------------------------------------------------------------------------------------------
def classify_numeric(direction: str, indep: F, orig: F, factor: int = FACTOR) -> str:
    if direction == "UPPER_BOUND":
        if indep <= orig:
            return "STRONGER"
        return "AGREES" if indep <= factor * orig else "INSUFFICIENT"
    if direction == "LOWER_BOUND":
        if indep >= orig:
            return "STRONGER"
        return "AGREES" if indep * factor >= orig else "INSUFFICIENT"
    raise ValueError(f"unknown direction {direction!r}")


def pre_numeric(runs: dict, stmt_table: dict, policy: dict, *, expected_certifier_sha: dict,
                runs_producer: dict, deductions: dict | None = None) -> dict:
    """Everything that needs NO original magnitude: every production guard, reconstruction, value
    tracing (including the demotion check), independence and STATEMENT equivalence. A target is
    INVALID here when its certificate does not prove what it claims -- or when a target reported
    NOT_CERTIFIED is in fact proved by its certificate (demoted; review 4, N4-8)."""
    ev = CV.evaluate_run(runs, policy, expected_certifier_sha=expected_certifier_sha,
                         runs_producer=runs_producer, deductions=deductions)
    per, violations = {}, []
    for k in S.SIX_CONSTANTS:
        t = S.targets(runs)[k]
        et = ev["targets"][k]
        orig_st = EQ.original_statement(stmt_table, k)
        rec = {"target_status": t["status"], "independent_value": t.get("value"),
               "direction": orig_st["direction"]}
        if et["ok"] is False:                  # a bad certified claim, or a demoted target
            if et.get("independence"):
                violations.append(k)
            rec.update(statement={"STATUS": "NOT_PROVED", "reasons": et["problems"]},
                       numeric=None, CLASS="INVALID",
                       why=f"the target does not trace to its certificate: {et['problems']}")
        elif t["status"] != "CERTIFIED":
            rec.update(statement={"STATUS": "NO_INDEPENDENT_STATEMENT"}, numeric=None,
                       CLASS="INSUFFICIENT", why=f"no certified value (status {t['status']})")
        else:
            cmp = EQ.compare(orig_st, et["proposition"])
            if cmp.get("independence_violation"):
                violations.append(k)
            rec["statement"] = cmp
            if cmp["STATUS"] not in ("EQUIVALENT", "STRONGER"):
                rec.update(numeric=None, CLASS="INVALID",
                           why=f"statement {cmp['STATUS']}; the number is not compared")
            else:
                rec.update(CLASS=None, why="awaiting the numerical comparison")
        per[k] = rec
    guards = {"G8": ev["G8"], "G10": ev["G10"], "G19": ev["G19"], "value_trace": ev["value_trace"]}
    return {"ev": ev, "per": per, "violations": violations, "guards": guards,
            "guards_ok": all(g["PASS"] for g in guards.values())}


def numeric_phase(pre: dict, stmt_table: dict, mags: dict) -> dict:
    """Step 14: numerical agreement for the statement-equivalent targets, the opposite-direction
    check, and the N9 classification by the frozen precedence."""
    import copy
    per = copy.deepcopy(pre["per"])
    for k in S.SIX_CONSTANTS:
        rec = per[k]
        rec["original_value"] = str(mags[k])
        if rec["CLASS"] is None:
            v, o = F(rec["independent_value"]), mags[k]
            num = classify_numeric(rec["direction"], v, o)
            rec["numeric"] = {"class": num, "ratio": str(v / o), "direction": rec["direction"],
                              "factor": FACTOR}
            if v == o:
                rec.update(CLASS="INVALID", why="the independent value equals the original "
                                                 "EXACTLY -- copied, not certified")
            else:
                rec.update(CLASS=num, why=f"statement {rec['statement']['STATUS']}; {num} at "
                                          f"ratio {float(v / o):.6f}")

    # DISAGREES: an independent bound whose quantity the original bounds from the other side
    orig_by_q = {v["quantity"]: (kk, v["direction"])
                 for kk, v in stmt_table["original_statements"].items()}
    pairs = []
    for cid, r in pre["ev"]["reconstructed"].items():
        for const, prop in r["propositions"].items():
            hit = orig_by_q.get(prop["quantity"])
            if hit and hit[1] != prop["direction"]:
                iv, ov = r["values"][const], mags[hit[0]]
                dis = iv < ov if prop["direction"] == "UPPER_BOUND" else iv > ov
                pairs.append({"certificate": cid, "quantity": prop["quantity"],
                              "original": hit[0], "independent_direction": prop["direction"],
                              "disagrees": dis})
                if dis:
                    per[hit[0]].update(CLASS="DISAGREES",
                                       why=f"certificate {cid}'s {prop['direction']} excludes the "
                                           f"original's {hit[1]}")
    classes = {k: v["CLASS"] for k, v in per.items()}
    # guards_ok includes the VALUE TRACE (and so the demotion check): review 4, N4-8
    if pre["violations"]:
        verdict = "INDEPENDENCE_VIOLATION"
    elif any(c == "DISAGREES" for c in classes.values()):
        verdict = "SCIENTIFIC_DISAGREEMENT"
    elif any(c == "INVALID" for c in classes.values()) or not pre["guards_ok"]:
        verdict = "EXECUTION_INVALID"
    elif all(c in ("AGREES", "STRONGER") for c in classes.values()):
        verdict = "N9_CLOSED"
    else:
        verdict = "AGREEMENT_INSUFFICIENT"
    return {"per_target": per, "classes": classes, "opposite_direction_pairs": pairs,
            "independence_violations": pre["violations"], "guards": pre["guards"],
            "N9_VERDICT": verdict, "precedence": list(PRECEDENCE)}


def run_comparison(runs: dict, stmt_table: dict, mags: dict, policy: dict, *,
                   expected_certifier_sha: dict, runs_producer: dict,
                   deductions: dict | None = None) -> dict:
    """Steps 9-14 as ONE pure function of their arguments (the self-tests and the mutation suite
    call it; execute_comparison calls the two halves with the loader between them)."""
    pre = pre_numeric(runs, stmt_table, policy, expected_certifier_sha=expected_certifier_sha,
                      runs_producer=runs_producer, deductions=deductions)
    return numeric_phase(pre, stmt_table, mags)


def render(result: dict) -> list[str]:
    """Prose, rendered ONLY from computed fields, after classification."""
    lines = [f"{k}: {result['per_target'][k]['CLASS']} -- {result['per_target'][k]['why']}"
             for k in S.SIX_CONSTANTS]
    counts = {}
    for c in result["classes"].values():
        counts[c] = counts.get(c, 0) + 1
    lines.append(f"class counts: {dict(sorted(counts.items()))}")
    lines.append(f"G8 {result['guards']['G8']['PASS']}; G10 {result['guards']['G10']['PASS']}; "
                 f"G19 {result['guards']['G19']['PASS']}; "
                 f"value trace {result['guards']['value_trace']['PASS']}")
    lines.append(f"opposite-direction pairs found: {len(result['opposite_direction_pairs'])}")
    lines.append(f"N9 classification by frozen precedence {result['precedence']}: "
                 f"{result['N9_VERDICT']}")
    return lines


# ---------------------------------------------------------------------------------------------
# self-test -- SYNTHETIC certificates and SYNTHETIC magnitudes; never loads the quarantine
# ---------------------------------------------------------------------------------------------
def synthetic_certs(stmt_table: dict, policy: dict, *, A_K=F(1111, 100), A_H=F(999, 100),
                    alpha=F(3, 5), kernel_H="Khat_e", certified_K=True) -> dict:
    """SYNTHETIC certificates at the frozen configuration. Values deliberately round; no
    certifier ran. Used only by self-tests and the mutation suite."""
    d = stmt_table["drift_domain"]
    E = (d["e_lo"], d["e_hi"])
    ch = policy["configuration"]["chosen"]

    def mk(cid, fam, w, ar, mod, fn, kern, cert_ok, extra):
        res = dict(kernel=kern, certified=cert_ok,
                   margin_lower_bound=F(1, 1000) if cert_ok else F(-1, 1000),
                   boxes=len(CV.X.cover(ch["depth"])), **extra)
        return CV.make_certificate(cid=cid, family=fam, w=w, drift_block=E, depth=ch["depth"],
                                   panels=ch["panels"],
                                   atom_removed=ar, certifier_module=mod, certifier_function=fn,
                                   result=res, screen="POINTWISE_FEASIBLE", sent=True, seconds=0.0)
    return {"F_K": mk("F_K", "w = A - B*m", {(0, 0): A_K, (0, 1): F(-3, 2)}, False,
                      "c11r_idrift.py", "supersolution_margin_iv", "K_e", certified_K,
                      {"w_min_lower_bound": F(1)}),
            "F_H": mk("F_H", "w = A - B*m", {(0, 0): A_H, (0, 1): F(-3, 2)}, kernel_H == "Khat_e",
                      "c11r_idrift.py", "supersolution_margin_iv", kernel_H, True,
                      {"w_min_lower_bound": F(1)}),
            "F_D": mk("F_D", "u = alpha + beta*m", {(0, 0): alpha, (0, 1): F(1, 20)}, True,
                      "c11r_boxdata.py", "subsolution_margin_iv", "Khat_e", True,
                      {"h_min_lower_bound": F(1, 10000), "u_nonnegative": True})}


def self_test(stmt_table: dict, policy: dict) -> dict:
    """Every branch of run_comparison on synthetic inputs. Loads no real magnitude."""
    import copy
    import c11r_runs as R
    fake = {"Abar": F(10), "tau": F(10), "C_T": F(10), "D_lo": F(1, 2), "D1": F(10),
            "D2": F(10)}                                     # synthetic, deliberately round
    me = {"module": "c11r_runs.py", "sha256": C.sha256_file(C.HERE / "c11r_runs.py")}
    exp = CV.certifier_hashes()
    cases = []

    def run(certs, deductions=None, mutate=None):
        r = R.assemble(policy=policy, stmt=stmt_table, certs=certs, stop_reason=None, extra={},
                       deductions=deductions)
        if mutate:
            mutate(r)
        return run_comparison(r, stmt_table, fake, policy, expected_certifier_sha=exp,
                              runs_producer=me, deductions=deductions)

    def case(label, res, expect_verdict, expect=None):
        ok = res["N9_VERDICT"] == expect_verdict and all(
            res["classes"][k] == v for k, v in (expect or {}).items())
        cases.append({"case": label, "verdict": res["N9_VERDICT"], "classes": res["classes"],
                      "expected_verdict": expect_verdict, "ok": ok, "render": render(res)})

    honest = run(synthetic_certs(stmt_table, policy))
    case("honest certificates; D1, D2 not implemented", honest, "AGREEMENT_INSUFFICIENT",
         {"Abar": "AGREES", "tau": "STRONGER", "C_T": "STRONGER", "D_lo": "STRONGER",
          "D1": "INSUFFICIENT"})
    # SEPARATION: a different value under the SAME legitimately proved proposition
    far = run(synthetic_certs(stmt_table, policy, A_K=F(25)))
    sep = (honest["per_target"]["Abar"]["statement"]["STATUS"]
           == far["per_target"]["Abar"]["statement"]["STATUS"] == "EQUIVALENT")
    cases.append({"case": "same proposition, different value: statement unchanged, number moves",
                  "verdict": far["N9_VERDICT"], "classes": far["classes"],
                  "expected_verdict": "Abar statement EQUIVALENT both times; numeric AGREES -> "
                                      "INSUFFICIENT",
                  "ok": sep and honest["classes"]["Abar"] == "AGREES"
                  and far["classes"]["Abar"] == "INSUFFICIENT", "render": render(far)})
    case("a K_e certificate cited for tau is refused, not EQUIVALENT",
         run(synthetic_certs(stmt_table, policy), mutate=lambda r: r["targets"]["tau"].update(
             certificate_id="F_K")), "EXECUTION_INVALID", {"tau": "INVALID"})
    case("a value halved after certification is refused (value trace)",
         run(synthetic_certs(stmt_table, policy), mutate=lambda r: r["targets"]["Abar"].update(
             value=str(F(r["targets"]["Abar"]["value"]) / 2))), "EXECUTION_INVALID",
         {"Abar": "INVALID"})
    case("an independent value EQUAL to the original is refused as copied",
         run(synthetic_certs(stmt_table, policy, alpha=fake["D_lo"])), "EXECUTION_INVALID",
         {"D_lo": "INVALID"})
    case("an original-graph certifier is an INDEPENDENCE_VIOLATION",
         run(synthetic_certs(stmt_table, policy), mutate=lambda r: r["certificates"]["F_K"][
             "certifier"].update(module="taboo_certify.py")), "INDEPENDENCE_VIOLATION")
    # G19 in isolation: certificates internally CONSISTENT, but made at another configuration
    other = copy.deepcopy(policy)
    other["configuration"]["chosen"] = dict(policy["configuration"]["chosen"],
                                            depth=policy["configuration"]["chosen"]["depth"] + 1)
    g19 = run(synthetic_certs(stmt_table, other))
    case("consistent certificates at another depth than the frozen one: G19 -> EXECUTION_INVALID",
         g19, "EXECUTION_INVALID",
         {"Abar": "AGREES", "tau": "STRONGER", "C_T": "STRONGER", "D_lo": "STRONGER"})
    case("a target demoted to NOT_CERTIFIED although its certificate proves it (review 4, N4-8)",
         run(synthetic_certs(stmt_table, policy), mutate=lambda r: r["targets"]["Abar"].update(
             status="NOT_CERTIFIED")), "EXECUTION_INVALID", {"Abar": "INVALID"})
    case("a G10 violation makes the run EXECUTION_INVALID",
         run(synthetic_certs(stmt_table, policy), mutate=lambda r: r["certificates"]["F_D"].update(
             screen_classification="POINTWISE_INFEASIBLE")), "EXECUTION_INVALID")
    # DISAGREES: only through a deduction no production certifier has
    dd = dict(CV.DEDUCTIONS)
    dd[("c11r_testonly.py", "d_upper", "Khat_e")] = {
        "kind": CV.SUPER, "route": "independent_supersolution", "direction": "UPPER_BOUND",
        "family": "w = A - B*m", "premises": (), "implemented": True, "inequality": "test only",
        "yields": {"D_lo": "w_at_atom"}}
    certs = synthetic_certs(stmt_table, policy)
    extra_cert = copy.deepcopy(certs["F_K"])
    extra_cert["certificate_id"] = "F_X"
    extra_cert["certifier"] = {"module": "c11r_testonly.py", "function": "d_upper",
                               "module_sha256": "t"}
    extra_cert["certifier_result"]["kernel"] = "Khat_e"
    extra_cert["inputs"]["atom_removed_argument"] = True
    extra_cert["weight"] = CV.weight_json({(0, 0): F(1, 10), (0, 1): F(0)})
    extra_cert["input_digest"] = CV.input_digest(extra_cert["weight"], extra_cert["inputs"],
                                                 extra_cert["certifier"])
    # the frozen runner emits exactly F_K, F_H, F_D (review 6, N6-4: emit_runs refuses anything
    # else, and the comparator's run step refuses it too); the test-only certificate is therefore
    # added AFTER emission, to exercise the pure classification below
    r_dis = R.assemble(policy=policy, stmt=stmt_table, certs=certs, stop_reason=None, extra={},
                       deductions=dd)
    r_dis["certificates"]["F_X"] = extra_cert
    res_dis = run_comparison(r_dis, stmt_table, fake, policy,
                             expected_certifier_sha=dict(exp, **{"c11r_testonly.py": "t"}),
                             runs_producer=me, deductions=dd)
    case("an independent UPPER bound below the original LOWER bound DISAGREES", res_dis,
         "SCIENTIFIC_DISAGREEMENT", {"D_lo": "DISAGREES"})

    seal = {
        "absent": verify_seal_bytes(None, None, False),
        "never_committed": verify_seal_bytes(b"x", None, False),
        "edited_after_commit": verify_seal_bytes(b"new", b"old", False),
        "uncommitted_change": verify_seal_bytes(b"x", b"x", True),
        "sealed": verify_seal_bytes(b"x", b"x", False),
    }
    base = R.assemble(policy=policy, stmt=stmt_table, certs=synthetic_certs(stmt_table, policy),
                      stop_reason=None, extra={})
    typed = {
        "producer_built_false_seal_accepted": not S.seal_problems(base),
        "true_seal_rejected": bool(S.seal_problems(dict(base, seal=dict(
            base["seal"], contains_original_magnitudes=True)))),
        "unrelated_text_with_the_word_accepted": not S.seal_problems(dict(
            base, note="these magnitudes and original_value words are prose")),
        "real_payload_key_rejected": bool(S.seal_problems(dict(
            base, targets=dict(base["targets"], Abar=dict(base["targets"]["Abar"],
                                                          original_value="1/1"))))),
    }
    seal_ok = (all(seal[k] for k in ("absent", "never_committed", "edited_after_commit",
                                     "uncommitted_change")) and not seal["sealed"]
               and all(typed.values()))
    return {"cases": cases, "seal_ordering_controls": seal, "seal_typed_controls": typed,
            "seal_controls_ok": seal_ok,
            "renders_depend_on_inputs": len({tuple(c["render"]) for c in cases}) == len(cases),
            "used_real_magnitudes": False,
            "PASS": all(c["ok"] for c in cases) and seal_ok}


# ---------------------------------------------------------------------------------------------
def write_comparison(repo, out: dict) -> str:
    """Write the comparison artifact ONCE (erratum E45). The output path must not exist -- not
    even as a symlink or an untracked leftover (review 5, N5-2) -- and it is created exclusively
    ('x'), so nothing written in between can be overwritten or adopted. C11R_COMPARISON.json is a
    PROTECTED name: round 5's open-guard revision refused this very write outside the sanctioned
    context, which the round-5 comparator never entered, so its final write would have failed
    after the magnitudes were loaded. The write is now done inside the context, by the reader."""
    import json
    path = (pathlib.Path(repo) if repo is not None else C.REPO) / C.NS_REL / CT.COMPARISON_REL
    if os.path.lexists(path):
        raise SystemExit("REFUSE: a file already exists at the comparison output path")
    body = C.evidence_body(out, producer=__file__)
    path.parent.mkdir(parents=True, exist_ok=True)
    with C.sanctioned_protected_access("write the comparison artifact, once"):
        with open(path, "x") as fh:
            fh.write(json.dumps(body, indent=1, sort_keys=True) + "\n")
    return body["sha256"]


# THE TRANSACTION (review 6, N6-3; c11r_contract.COMPARISON_TRANSACTION). Round 6's main()
# wrote the comparison artifact even when the chain refused BEFORE the loader, so a harmless cause
# (a Finder .DS_Store in evidence/runs) left an EXECUTION_INVALID file that made every later
# comparison refuse. Now: verify -> load iff every step passed -> compute -> write ONCE. Nothing is
# written on any other path; the refusal is printed, typed, with its own exit code.
EXIT = {"COMPARED": 0, "REFUSED_BEFORE_LOAD": 3, "POST_LOAD_FAILURE": 4}


def phase15(repo=None, *, approved_commit: str, loader, allow_fixture: bool = False,
            writer=None) -> dict:
    """Phase 15 as ONE transaction. Returns the outcome, the lines to print and whether the
    comparison artifact was written; the artifact is written (by `writer`, default
    write_comparison) only after the loader ran AND the classification completed."""
    writer = writer or write_comparison
    entered = {"loader": False}

    def counted(stmt):
        entered["loader"] = True
        return loader(stmt)
    try:
        result = execute_comparison(repo, approved_commit=approved_commit, loader=counted,
                                    allow_fixture=allow_fixture)
    except BaseException as e:
        if not entered["loader"]:
            raise                                       # steps 1-12 are typed: not expected
        return {"outcome": "POST_LOAD_FAILURE", "written": False, "result": None,
                "lines": [f"POST_LOAD_FAILURE -- the loader was entered (the original "
                          f"magnitudes may have been read) and the comparison did not complete "
                          f"({type(e).__name__}); NOTHING was written. Do not run the comparator "
                          f"again without the user's instruction (COMPARISON_TRANSACTION)."]}
    if not result.get("loader_called"):
        return {"outcome": "REFUSED_BEFORE_LOAD", "written": False, "result": result,
                "lines": [f"REFUSED before the loader at step {result['refused_at_step']} "
                          f"({result['refused_at']}); NOTHING was written, the state stays "
                          f"SEALED, and once the cause is removed the comparator may be run "
                          f"again (COMPARISON_TRANSACTION):"]
                + [f"  - {p}" for p in result["identity_problems"]]}
    out = {"schema": "C11R_COMPARISON/6", "approved_commit": approved_commit, "result": result,
           "rendered": render(result)}
    try:
        digest = writer(repo, out)
    except BaseException as e:
        return {"outcome": "POST_LOAD_FAILURE", "written": False, "result": None,
                "lines": [f"POST_LOAD_FAILURE -- the comparison was computed but could not be "
                          f"written ({type(e).__name__}: {str(e)[:120]}); do not run the "
                          f"comparator again without the user's instruction."]}
    return {"outcome": "COMPARED", "written": True, "result": result, "sha256": digest,
            "lines": out["rendered"] + [f"wrote {CT.COMPARISON_REL} sha256 {digest[:16]}..."]}


def main(approved_commit: str) -> int:
    """Phase 15, on the user's instruction, with the approved commit the review passed."""
    r = phase15(C.REPO, approved_commit=approved_commit, loader=load_original_magnitudes)
    for line in r["lines"]:
        print(line)
    return EXIT[r["outcome"]]


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--approved-commit":
        raise SystemExit(main(sys.argv[2]))
    print("c11r_compare.py runs only as Phase 15, after a sealed run, with --approved-commit <sha>")
    raise SystemExit(2)
