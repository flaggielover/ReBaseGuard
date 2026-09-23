"""C11R Phase 15 -- the sealed comparison. Revision 4 (R3-1; B-1, B-3, B-4 kept).

ONE OF EXACTLY TWO MODULES PERMITTED TO LOAD AN ORIGINAL MAGNITUDE, and it does so only through
the `loader` that `execute_comparison` calls AFTER the seal and the whole identity chain verify.

THE ROOT OF TRUST (round 4, erratum E25). Revision 3 took the certifier and producer hashes it
"expected" from the seal commit's own tree, so a certifier edited, committed, used and reverted
before the seal was accepted. Now the operator supplies the APPROVED commit A (the one the review
passed); the frozen execution contract at A is the authority, and nothing is taken from the tree
being checked without being recomputed and compared with it.

ORDER OF OPERATIONS IN `execute_comparison`:
  1  the SEAL: the runs artifact is committed by exactly one commit and never touched again, the
     file on disk is that commit's blob with no uncommitted change, its canonical body hashes to
     its stored sha256, and it passes c11r_schema.validate_runs (typed seal fields: erratum E15);
  2  the CHAIN (c11r_contract): the authorization names A; the execution contract recomputed from
     bytes; every frozen path byte-identical to A and untouched by every later commit; the gate,
     the qualification and the authorization verified against the recomputed identities; the run's
     execution_identity, code closure, certifier hashes, runner and configuration equal to them
     (predicate G20); the comparison rule's factor equal to this module's and to the gate's.
     ANY failure -> EXECUTION_INVALID, and the quarantine is NOT opened;
  3  every production guard (c11r_certificate.evaluate_run) with the certifier hashes the FROZEN
     CONTRACT fixes: reconstruction; value tracing, G8, G10, G19;
  4  only then the ORIGINAL statements (semantics) and the ORIGINAL magnitudes (the quarantine,
     first checked against the content-free id the statement table recorded for it);
  4  per target: STATEMENT EQUIVALENCE first (the reconstructed proposition against the original),
     then, only for an equivalent-or-stronger statement, NUMERICAL AGREEMENT. The two results are
     recorded separately and never conflated;
  5  the N9 classification by a frozen precedence, and only then any prose.

NOTHING HERE IS A PRE-WRITTEN CONCLUSION: every sentence is rendered from computed fields.

REACHABILITY, stated per path rather than claimed wholesale (erratum E19). In production, D1 and D2
are NOT_IMPLEMENTED, so N9_CLOSED is unreachable by scope. INVALID, INDEPENDENCE_VIOLATION and
EXECUTION_INVALID are reachable from genuine artifacts whose certificates do not establish what
their targets claim. DISAGREES requires an independent bound on an original quantity in the
OPPOSITE direction; no implemented certifier produces one, so it is reachable only through a
deduction no production certifier has, and the self-test exercises it that way.
"""
from __future__ import annotations

import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_certificate as CV
import c11r_common as C
import c11r_contract as CT
import c11r_equiv as EQ
import c11r_schema as S

RUNS_REL = "evidence/runs/C11R_RUNS.json"
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
    if root.resolve() == C.REPO.resolve() and C.running_program() != "c11r_compare.py":
        raise PermissionError("the real runs artifact is read only by c11r_compare.py as Phase 15")


def verify_seal(repo=None) -> dict:
    """The seal, recomputed: the runs artifact was committed by exactly one commit, is unchanged
    since, and its canonical body hashes to its stored sha256. Nothing is trusted."""
    import json
    root = pathlib.Path(repo) if repo is not None else C.REPO
    _real_repository_guard(root)
    path = root / C.NS_REL / RUNS_REL
    rel = f"{C.NS_REL}/{RUNS_REL}"
    disk = path.read_bytes() if path.exists() else None
    commits = C.git_in(root, "log", "--format=%H", "--", rel).splitlines() if disk else []
    seal_commit = commits[-1] if commits else None
    committed = C.blob_at_in(root, seal_commit, rel) if seal_commit else None
    dirty = bool(C.git_in(root, "status", "--porcelain", "--", rel)) if disk is not None else False
    problems = verify_seal_bytes(disk, committed, dirty)
    if len(commits) > 1:
        problems.append(f"the runs artifact was changed after it was sealed ({len(commits)} "
                        f"commits touch it)")
    runs = None
    if disk is not None:
        runs = json.loads(disk)
        problems += S.validate_runs(runs)
        if runs.get("sha256") != CT.body_digest(runs):
            problems.append("the runs artifact's stored sha256 does not equal its recomputed "
                            "canonical body digest")
    return {"problems": problems, "seal_commit": seal_commit, "runs": runs,
            "runs_file_sha256": C.sha256_bytes(disk) if disk else None}


def verify_chain(repo, runs: dict, seal_commit: str, *, approved_commit: str,
                 allow_fixture: bool = False) -> dict:
    """contract -> gate -> qualification -> authorization -> run -> seal, all recomputed."""
    root = pathlib.Path(repo) if repo is not None else C.REPO
    a = CT.load_artifact(repo, CT.AUTH_REL) if CT.artifact_exists(repo, CT.AUTH_REL) else None
    av = CT.verify_authorization(repo, a, allow_fixture=allow_fixture, stage="compare")
    p = list(av["problems"])
    if a is not None and a.get("approved_commit") != approved_commit:
        p.append("the authorization names another approved commit than the operator supplied")
    facts = av.get("facts")
    contract = (facts or {}).get("roots", {}).get("contract") if facts else None
    if facts and contract is not None:
        p += CT.verify_run_identity(runs, facts, av["digest"])
        if seal_commit and not C.git_ok_in(root, "merge-base", "--is-ancestor", approved_commit,
                                           seal_commit):
            p.append("the seal commit does not descend from the approved commit")
        for rel in (CT.AUTH_REL, CT.QUAL_REL):
            if not C.git_in(root, "log", "--format=%H", "-1", "--", f"{C.NS_REL}/{rel}"):
                p.append(f"{rel} was never committed")
        stmt = CT.load_artifact(repo, CT.STMT_REL)
        p += comparison_rule_problems(stmt, facts["roots"].get("gate") or {}, contract)
    elif not p:
        p.append("the chain could not be reconstructed")
    return {"problems": p, "contract": contract, "facts": facts}


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


def execute_comparison(repo=None, *, approved_commit: str, loader, allow_fixture: bool = False) -> dict:
    """The whole Phase 15 path. The loader -- the ONLY access to original magnitudes -- is called
    only after the seal and the chain verify; otherwise the verdict is EXECUTION_INVALID and the
    quarantine is never opened."""
    seal = verify_seal(repo)
    problems = list(seal["problems"])
    chain = None
    if not problems:
        chain = verify_chain(repo, seal["runs"], seal["seal_commit"],
                             approved_commit=approved_commit, allow_fixture=allow_fixture)
        problems += chain["problems"]
    if problems:
        return {"N9_VERDICT": "EXECUTION_INVALID", "identity_problems": problems,
                "loader_called": False, "seal": {k: seal[k] for k in ("seal_commit",
                                                                       "runs_file_sha256")}}
    contract, facts = chain["contract"], chain["facts"]
    stmt = CT.load_artifact(repo, CT.STMT_REL)
    policy = CT.load_artifact(repo, CT.POLICY_REL)
    mags = loader(stmt)                                   # only now, only here
    result = run_comparison(seal["runs"], stmt, mags, policy,
                            expected_certifier_sha=CT.expected_certifier_sha(contract),
                            runs_producer={"module": "c11r_runs.py",
                                           "sha256": facts["runner_sha256"]})
    result["loader_called"] = True
    result["identity_problems"] = []
    result["seal"] = {k: seal[k] for k in ("seal_commit", "runs_file_sha256")}
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


def run_comparison(runs: dict, stmt_table: dict, mags: dict, policy: dict, *,
                   expected_certifier_sha: dict, runs_producer: dict,
                   deductions: dict | None = None) -> dict:
    """Everything after the seal, as a pure function. main() and the self-tests both call it."""
    ev = CV.evaluate_run(runs, policy, expected_certifier_sha=expected_certifier_sha,
                         runs_producer=runs_producer, deductions=deductions)
    per, violations = {}, []
    for k in S.SIX_CONSTANTS:
        t = S.targets(runs)[k]
        et = ev["targets"][k]
        orig_st = EQ.original_statement(stmt_table, k)
        rec = {"target_status": t["status"], "independent_value": t.get("value"),
               "original_value": str(mags[k])}
        if t["status"] != "CERTIFIED":
            rec.update(statement={"STATUS": "NO_INDEPENDENT_STATEMENT"}, numeric=None,
                       CLASS="INSUFFICIENT", why=f"no certified value (status {t['status']})")
        elif not et["ok"]:
            if et.get("independence"):
                violations.append(k)
            rec.update(statement={"STATUS": "NOT_PROVED", "reasons": et["problems"]},
                       numeric=None, CLASS="INVALID",
                       why=f"the cited certificate does not prove this value: {et['problems']}")
        else:
            cmp = EQ.compare(orig_st, et["proposition"])
            if cmp.get("independence_violation"):
                violations.append(k)
            rec["statement"] = cmp
            if cmp["STATUS"] not in ("EQUIVALENT", "STRONGER"):
                rec.update(numeric=None, CLASS="INVALID",
                           why=f"statement {cmp['STATUS']}; the number is not compared")
            else:
                v, o = F(t["value"]), mags[k]
                num = classify_numeric(orig_st["direction"], v, o)
                rec["numeric"] = {"class": num, "ratio": str(v / o),
                                  "direction": orig_st["direction"], "factor": FACTOR}
                if v == o:
                    rec.update(CLASS="INVALID", why="the independent value equals the original "
                                                     "EXACTLY -- copied, not certified")
                else:
                    rec.update(CLASS=num, why=f"statement {cmp['STATUS']}; {num} at ratio "
                                              f"{float(v / o):.6f}")
        per[k] = rec

    # DISAGREES: an independent bound whose quantity the original bounds from the other side
    orig_by_q = {v["quantity"]: (kk, v["direction"])
                 for kk, v in stmt_table["original_statements"].items()}
    pairs = []
    for cid, r in ev["reconstructed"].items():
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
    guards_ok = ev["G8"]["PASS"] and ev["G10"]["PASS"] and ev["G19"]["PASS"]
    if violations:
        verdict = "INDEPENDENCE_VIOLATION"
    elif any(c == "DISAGREES" for c in classes.values()):
        verdict = "SCIENTIFIC_DISAGREEMENT"
    elif any(c == "INVALID" for c in classes.values()) or not guards_ok:
        verdict = "EXECUTION_INVALID"
    elif all(c in ("AGREES", "STRONGER") for c in classes.values()):
        verdict = "N9_CLOSED"
    else:
        verdict = "AGREEMENT_INSUFFICIENT"
    return {"per_target": per, "classes": classes, "opposite_direction_pairs": pairs,
            "independence_violations": violations,
            "guards": {"G8": ev["G8"], "G10": ev["G10"], "G19": ev["G19"],
                       "value_trace": ev["value_trace"]},
            "N9_VERDICT": verdict, "precedence": list(PRECEDENCE)}


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
    certs["F_X"] = extra_cert
    r_dis = R.assemble(policy=policy, stmt=stmt_table, certs=certs, stop_reason=None, extra={},
                       deductions=dd)
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
def main(approved_commit: str) -> int:
    """Phase 15, on the user's instruction, with the approved commit the review passed."""
    result = execute_comparison(C.REPO, approved_commit=approved_commit,
                                loader=load_original_magnitudes)
    out = {"schema": "C11R_COMPARISON/4", "approved_commit": approved_commit,
           "result": result,
           "rendered": render(result) if result.get("loader_called") else
           [f"EXECUTION_INVALID -- {p}" for p in result["identity_problems"]]}
    s_ = C.write_evidence(C.NS / "evidence" / "comparison" / "C11R_COMPARISON.json", out,
                          producer=__file__)
    for line in out["rendered"]:
        print(line)
    print(f"wrote evidence/comparison/C11R_COMPARISON.json sha256 {s_[:16]}...")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--approved-commit":
        raise SystemExit(main(sys.argv[2]))
    print("c11r_compare.py runs only as Phase 15, after a sealed run, with --approved-commit <sha>")
    raise SystemExit(2)
