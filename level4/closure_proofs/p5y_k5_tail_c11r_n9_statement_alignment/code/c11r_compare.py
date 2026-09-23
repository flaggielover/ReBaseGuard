"""C11R Phase 15 -- the sealed comparison. Revision 3 (blockers B-1, B-3, B-4).

ONE OF EXACTLY TWO MODULES PERMITTED TO LOAD AN ORIGINAL MAGNITUDE, and it does so only inside
`load_original_magnitudes`, which only `main` calls, and only after `verify_seal` has passed.

ORDER OF OPERATIONS IN `main`:
  1  the SEAL: the runs artifact is committed, the file on disk is the committed blob, it has no
     uncommitted change, it passes c11r_schema.validate_runs -- which checks the seal on TYPED
     fields (round 2 scanned the artifact's text for "magnitudes" and so refused every genuine
     artifact, whose schema key is "contains_original_magnitudes": erratum E15) -- and its producer
     hash equals c11r_runs.py as committed at the seal;
  2  every production guard (c11r_certificate.evaluate_run) with the certifier hashes AS COMMITTED
     AT THE SEAL: each certificate is RECONSTRUCTED into what it proves; value tracing, G8 and G10;
  3  only then the ORIGINAL statements (semantics) and the ORIGINAL magnitudes (the quarantine,
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


def verify_seal() -> dict:
    import json
    path = C.NS / RUNS_REL
    rel = str(path.relative_to(C.REPO))
    disk = path.read_bytes() if path.exists() else None
    commits = C.git("log", "--format=%H", "--", rel).splitlines() if disk is not None else []
    seal_commit = commits[-1] if commits else None
    committed = C.blob_at(seal_commit, rel) if seal_commit else None
    dirty = bool(C.git("status", "--porcelain", "--", rel)) if disk is not None else False
    problems = verify_seal_bytes(disk, committed, dirty)
    runs, runs_producer = None, None
    if not problems:
        runs = json.loads(disk)
        problems += S.validate_runs(runs)               # typed seal + structure, schema-owned
        code = str((C.NS / "code" / "c11r_runs.py").relative_to(C.REPO))
        at_seal = C.sha256_bytes(C.blob_at(seal_commit, code))
        if runs.get("provenance", {}).get("producer_sha256") != at_seal:
            problems.append("producer hash differs from c11r_runs.py as committed at the seal")
        runs_producer = {"module": "c11r_runs.py", "sha256": at_seal}
    return {"problems": problems, "seal_commit": seal_commit, "runs": runs,
            "runs_producer": runs_producer,
            "runs_sha256": C.sha256_bytes(disk) if disk else None}


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
                   margin_lower_bound=F(1, 1000) if cert_ok else F(-1, 1000), boxes=363, **extra)
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
def main() -> int:
    seal = verify_seal()
    if seal["problems"]:
        print("REFUSE: the independent outputs are not sealed, so no original value is loaded.")
        for p in seal["problems"]:
            print(f"  - {p}")
        return 2
    runs = seal["runs"]
    stmt_table = C.load_allowlisted("evidence/table/C11R_N9_STATEMENTS.json")
    policy = C.load_allowlisted("config/C11R_POLICY.json")
    exp = CV.certifier_hashes(seal["seal_commit"])
    mags = load_original_magnitudes(stmt_table)          # only now, only here
    result = run_comparison(runs, stmt_table, mags, policy, expected_certifier_sha=exp,
                            runs_producer=seal["runs_producer"])
    out = {"schema": "C11R_COMPARISON/3",
           "seal": {"commit": seal["seal_commit"], "runs_sha256": seal["runs_sha256"]},
           "comparison_rule_source": {"artifact": "evidence/table/C11R_N9_STATEMENTS.json",
                                      "sha256": stmt_table["sha256"]},
           "result": result, "rendered": render(result)}
    s = C.write_evidence(C.NS / "evidence" / "comparison" / "C11R_COMPARISON.json", out,
                         producer=__file__)
    for line in out["rendered"]:
        print(line)
    print(f"wrote evidence/comparison/C11R_COMPARISON.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
