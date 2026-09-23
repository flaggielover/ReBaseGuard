"""C11R -- the mutation suite, revision 4.

REVISION 4 (review round 3, N-3; erratum E30). Revision 3 claimed this module "defines no guard".
That was inaccurate: M01, M02, M07, M08, M10 and M12 were decided by logic local to this suite, and
M10 (a changed factor-2 threshold) had no production detector at all. Now:
  * M10 calls the PRODUCTION check c11r_compare.comparison_rule_problems, which the comparator
    runs on the chain before any quarantine access; M01/M02 call the production import rule
    c11r_qualify.forbidden_imports; M36 calls the real runner pre-flight;
  * every row carries `detector_kind`: PRODUCTION_GUARD (a production function refuses a mutated
    input), PRODUCTION_SCIENCE (a production certifier or screen refuses a mutated candidate),
    SUITE_LOCAL_PROPERTY (the suite checks a mathematical property of the reviewed machinery on
    NT against a planted wrong value) or SUITE_LOCAL_AUDIT (a scope or record audit). Only the
    PRODUCTION_* rows demonstrate production enforcement, and the artifact says so.
The end-to-end identity chain (R3-1) is exercised by code/c11r_chain.py, not here.

REVISION 3 (preserved below): it mutated PRODUCTION INPUTS for the run-artifact guards.

WHAT WAS WRONG IN REVISION 2 (review round 2, B-4; erratum E17). Its value-trace, screen-order and
disposition checks were functions defined HERE -- test-only copies of rules the production path
never ran -- so a mutant "detected" by them proved nothing about the gate, the runner or the
comparator. Its run-artifact mutants edited target STATEMENTS that the runner wrote itself, which
the template-built comparator then read back (erratum E16).

THE RULES NOW
  * Every detector is a PRODUCTION function: c11r_certificate.reconstruct / evaluate_run /
    screen_order / dispositions / configuration_adherence, c11r_compare.run_comparison,
    c11r_schema.validate_runs / seal_problems / forbidden_payload, c11r_equiv.compare,
    c11r_status.freshness / contradictions, c11r_gate.scan_for_result_language /
    scan_source_for_result_language, c11r_runs.preflight, c11r_firewall. This module
    builds inputs, mutates them, and calls those functions. It defines no guard.
  * Run artifacts are built by c11r_runs.assemble from certificates made by
    c11r_certificate.make_certificate -- the runner's own emission path -- with SYNTHETIC values.
  * Every mutant records the producer, verifier and input hashes, the exact path and value it
    mutated, and three outcomes: the MUTANT must be flagged, the CLEAN control accepted, and
    (where meaningful) an UNRELATED mutation must NOT be flagged. A false positive on either
    control marks the detector DETECTOR_BROKEN, which counts against the suite like a survivor.
  * The thirteen ADVERSARIAL CERTIFICATE CONTROLS (review round 2, B-3) run end to end through
    c11r_compare.run_comparison, and statement equivalence is reported separately from numerical
    agreement.
  * Numerical mutants run on the NON-TARGET block NT = [5/2, 5/2 + 108337/1250000] only.
  * UNDETERMINED is never a pass. MUTATION_CLASS = PASS requires every mutant DETECTED and every
    adversarial control caught.
"""
from __future__ import annotations

import ast
import copy
import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_boxdata as BD
import c11r_certificate as CV
import c11r_common as C
import c11r_compare as K
import c11r_contract as CT
import c11r_equiv as EQ
import c11r_firewall as FW
import c11r_gate as GA
import c11r_idrift as I
import c11r_qualify as Q
import c11r_runs as R
import c11r_schema as S
import c11r_status as ST

X, G = I.X, I.G
W = F(108337, 1250000)
NT = I.Blk(F(5, 2), F(5, 2) + W)
CODE = C.NS / "code"
RES: list[dict] = []
ADV: list[dict] = []
KIND = {
    "PRODUCTION_GUARD": ("M01", "M02", "M03", "M10", "M13", "M14", "M16", "M17", "M18", "M19",
                         "M20", "M21", "M22", "M23", "M25", "M26", "M27", "M28", "M30", "M31",
                         "M34", "M35", "M36", "M37", "M38", "M39"),
    "PRODUCTION_SCIENCE": ("M15", "M32", "M33"),
    "SUITE_LOCAL_PROPERTY": ("M04", "M05", "M06", "M09", "M18b", "M24", "M29"),
    "SUITE_LOCAL_AUDIT": ("M07", "M08", "M11", "M12"),
}
KIND_OF = {m: k for k, ms in KIND.items() for m in ms}
FAKE_MAGS = {"Abar": F(10), "tau": F(10), "C_T": F(10), "D_lo": F(1, 2), "D1": F(10),
             "D2": F(10)}                                    # synthetic, deliberately round
CELL_307_BLOCK = ("17885921/10000000", "1882413/1000000")    # a label from r5 geometry; no computation


def _sha(mod: str) -> str:
    return C.sha256_file(CODE / mod) if (CODE / mod).exists() else C.sha256_file(
        C.C11 / "code" / mod)


def record(mid, name, *, verifier, producer=None, input_artifact=None, mutated_path,
           mutated_value, mutant_flagged, clean_flagged, unrelated_flagged=None, detail=None,
           **extra):
    if clean_flagged or unrelated_flagged:
        outcome = "DETECTOR_BROKEN"
    elif mutant_flagged:
        outcome = "DETECTED"
    else:
        outcome = "SURVIVED"
    row = {"id": mid, "name": name, "outcome": outcome,
           "detector_kind": KIND_OF.get(mid, "UNCLASSIFIED"),
           "mutated_path": mutated_path, "mutated_value": repr(mutated_value)[:160],
           "mutant_flagged": bool(mutant_flagged), "clean_control_flagged": bool(clean_flagged),
           "unrelated_mutation_flagged": None if unrelated_flagged is None
           else bool(unrelated_flagged),
           "verifier": verifier, "verifier_sha256": _sha(verifier),
           "producer": producer, "producer_sha256": _sha(producer) if producer else None,
           "input_artifact": input_artifact,
           "input_sha256": (C.sha256_file(C.NS / input_artifact) if input_artifact else None),
           "detail": detail}
    row.update(extra)
    RES.append(row)


def redigest(cert: dict) -> dict:
    """Make a mutated certificate internally CONSISTENT again, so only the semantic check can
    catch it -- the harder forgery."""
    cert["input_digest"] = CV.input_digest(cert["weight"], cert["inputs"], cert["certifier"])
    return cert


def main() -> int:
    stmt = C.load_allowlisted("evidence/table/C11R_N9_STATEMENTS.json")
    policy = C.load_allowlisted("config/C11R_POLICY.json")
    gate = C.load_allowlisted("config/N9R_GATE_C11R.json")
    val = C.load_allowlisted("evidence/validation/C11R_VALIDATION.json")
    fw_art = C.load_allowlisted("evidence/firewall/C11R_FIREWALL.json")
    RUNS_IN = "evidence/table/C11R_N9_STATEMENTS.json"
    e_lo, e_hi = stmt["drift_domain"]["e_lo"], stmt["drift_domain"]["e_hi"]
    mid = str((F(e_lo) + F(e_hi)) / 2)
    ME = {"module": "c11r_runs.py", "sha256": C.sha256_file(CODE / "c11r_runs.py")}
    EXP = CV.certifier_hashes()

    def build(certs=None, deductions=None):
        return R.assemble(policy=policy, stmt=stmt, certs=certs or K.synthetic_certs(stmt, policy),
                          stop_reason=None, extra={"timings_seconds": {"x": 0.0}},
                          deductions=deductions)

    def compare(runs, deductions=None, exp=None):
        return K.run_comparison(runs, stmt, FAKE_MAGS, policy,
                                expected_certifier_sha=exp or EXP, runs_producer=ME,
                                deductions=deductions)

    def guards(runs, deductions=None):
        return CV.evaluate_run(runs, policy, expected_certifier_sha=EXP, runs_producer=ME,
                               deductions=deductions)

    base = build()
    base_cmp = compare(base)
    base_cls = base_cmp["classes"]
    unrel = copy.deepcopy(base)
    unrel["timings_seconds"] = {"x": 1.0}                     # a mutation no guard should see
    unrel_cls = compare(unrel)["classes"]

    def run_mutant(mid_, name, target, mutate, *, expect=("INVALID", "DISAGREES"), deductions=None,
                   exp=None, path, value, verifier="c11r_compare.py"):
        m = copy.deepcopy(base)
        mutate(m)
        res = compare(m, deductions=deductions, exp=exp)
        record(mid_, name, verifier=verifier, producer="c11r_runs.py", input_artifact=RUNS_IN,
               mutated_path=path, mutated_value=value,
               mutant_flagged=res["classes"][target] in expect and res["N9_VERDICT"] != "N9_CLOSED",
               clean_flagged=base_cls[target] in ("INVALID", "DISAGREES"),
               unrelated_flagged=unrel_cls[target] != base_cls[target],
               detail={"clean_class": base_cls[target], "mutant_class": res["classes"][target],
                       "mutant_verdict": res["N9_VERDICT"],
                       "mutant_statement": res["per_target"][target].get("statement")})
        return res

    # ============================ independence and backend =================================
    scan = Q.import_scan()                         # the production rule over the real closure
    planted = "import taboo_certify\nfrom opnorms import kernel_norm\n"
    record("M01", "hidden import of the original certifier's load-bearing graph",
           verifier="c11r_qualify.py", mutated_path="<synthetic module source>",
           mutated_value=planted, mutant_flagged=bool(Q.forbidden_imports(planted)["graph"]),
           clean_flagged=bool(scan["forbidden_graph_hits"]),
           unrelated_flagged=bool(Q.forbidden_imports("import json\n")["graph"]),
           detail={"modules_in_closure": scan["modules"]})
    planted = "import numpy as np\nfrom flint import arb\n"
    record("M02", "the original's arithmetic backend", verifier="c11r_qualify.py",
           mutated_path="<synthetic module source>", mutated_value=planted,
           mutant_flagged=bool(Q.forbidden_imports(planted)["backend"]),
           clean_flagged=bool(scan["forbidden_backend_hits"]),
           unrelated_flagged=bool(Q.forbidden_imports("import fractions\n")["backend"]))
    fwc = FW.run_controls()
    record("M03", "reading original magnitudes, review prose or the runs artifact by any PLANTED "
                  "path (a heuristic: known misses are recorded in the firewall artifact)",
           verifier="c11r_firewall.py", input_artifact="evidence/firewall/C11R_FIREWALL.json",
           mutated_path=f"<{len(FW.POSITIVE)} planted module sources>",
           mutated_value=sorted(FW.POSITIVE),
           mutant_flagged=fwc["all_positives_flagged"],
           clean_flagged=(not fwc["no_negative_flagged"]) or fw_art["FIREWALL_CLASS"] != "PASS",
           detail={"real_tree_class": fw_art["FIREWALL_CLASS"],
                   "offenders": fw_art["offenders"],
                   "negatives_clean": fwc["no_negative_flagged"]})

    # ============================ reviewed machinery on NT =================================
    w = {(0, 0): F(12), (0, 1): F(-3, 2)}
    bx = (F(0), F(1), F(0), F(1))
    pts = [(bx[0], bx[2]), (bx[1], bx[3]), ((bx[0] + bx[1]) / 2, (bx[2] + bx[3]) / 2),
           (bx[0], bx[3]), (bx[1], bx[2])]
    with BD.PhiCache():
        pw = {pt: I.kernel_apply_iv(w, *pt, NT) for pt in pts}
        real_ub = I.kernel_box_upper_iv(w, *bx, NT, 16).hi
    mid_pt = ((bx[0] + bx[1]) / 2, (bx[2] + bx[3]) / 2)
    planted_ub = pw[mid_pt].hi
    record("M04", "a box bound that does not dominate the pointwise kernel (midpoint-for-box)",
           verifier="c11r_idrift.py", mutated_path="kernel_box_upper_iv -> kernel at box centre",
           mutated_value=float(planted_ub),
           mutant_flagged=any(planted_ub < v.hi for v in pw.values()),
           clean_flagged=any(real_ub < v.hi for v in pw.values()),
           detail={"block": "NON-TARGET", "real_bound": float(real_ub)})
    wv = X.poly_eval_iv(w, G.Iv(bx[0], bx[1]), G.Iv(bx[2], bx[3]))
    with BD.PhiCache():
        kv = I.kernel_box_upper_iv(w, *bx, NT, 16)
    real_L = wv.lo - 1 - kv.hi
    reversed_L = wv.hi - 1 - kv.lo
    pw_L = min(X.poly_eval_iv(w, G.Iv(p, p), G.Iv(m, m)).hi - 1 - v.lo for (p, m), v in pw.items())
    record("M05", "lower/upper reversal in the supersolution margin", verifier="c11r_idrift.py",
           mutated_path="L_lo = w.lo - 1 - Kw.hi  ->  w.hi - 1 - Kw.lo",
           mutated_value=float(reversed_L),
           mutant_flagged=reversed_L > pw_L, clean_flagged=real_L > pw_L,
           detail={"real_margin": float(real_L), "pointwise_min": float(pw_L)})
    one = {(0, 0): F(1)}
    with BD.PhiCache():
        full = I.kernel_apply_iv(one, F(0), F(0), NT)
        hat = I.kernel_apply_iv(one, F(0), F(0), NT, atom_removed=True)
        atom = I.atom_contribution_iv(one, F(0), F(0), NT)
        shifted = I.shifted_moments_iv(-I.K + F(1, 4), I.K, NT, 0)[0]
    sep = lambda a, b: max(a.lo - b.hi, b.lo - a.hi)             # noqa: E731
    record("M06", "wrong atom window", verifier="c11r_idrift.py",
           mutated_path="atom window [m-K, K-p] -> [m-K+1/4, K-p]", mutated_value="(0,0)",
           mutant_flagged=sep(full, hat + shifted) > 0, clean_flagged=sep(full, hat + atom) > 0,
           detail={"block": "NON-TARGET"})
    import re
    txt = C.read_code("level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/"
                      "cusum_layer1.py")
    kf = F(re.search(r"K_FROZEN\s*=\s*([0-9.]+)", txt).group(1))
    hf = F(re.search(r"H_FROZEN\s*=\s*([0-9.]+)", txt).group(1))
    record("M07", "wrong frozen model constants", verifier="c11r_mutations.py",
           mutated_path="K", mutated_value="1/3",
           mutant_flagged=F(1, 3) != kf, clean_flagged=(I.K != kf or I.H != hf
                                                        or I.CC != kf + hf),
           detail={"frozen_K": str(kf), "frozen_H": str(hf)})

    def rigorous(iv):
        return isinstance(iv.lo, F) and isinstance(iv.hi, F) and iv.lo <= iv.hi

    class FloatIv:
        lo = hi = 0.5
    record("M08", "interval arithmetic collapsed to floating point", verifier="c11r_mutations.py",
           mutated_path="Iv endpoints", mutated_value="float",
           mutant_flagged=not rigorous(FloatIv), clean_flagged=not rigorous(full))
    PT = I.Blk(F(5, 2), F(5, 2))
    k1 = I.kernel_apply_iv(one, F(0), F(0), PT)
    rhs = G.Iv(1, 1) - I.alarm_prob_iv(F(0), F(0), PT)
    off = G.Iv(rhs.lo + F(1, 10 ** 6), rhs.hi + F(1, 10 ** 6))
    record("M09", "the kernel/alarm identity holding only approximately",
           verifier="c11r_mutations.py", mutated_path="1 - h1 at (0,0), e = 5/2",
           mutated_value="shifted by 1e-6",
           mutant_flagged=sep(k1, off) > 0, clean_flagged=sep(k1, rhs) > 0,
           detail={"enclosure_width": float(k1.hi - k1.lo)})

    # ============================ governance ================================================
    contract = CT.load_artifact(C.REPO, CT.CONTRACT_REL)
    planted_stmt = copy.deepcopy(stmt)
    planted_stmt["comparison_semantics_frozen_before_results"]["factor"] = 3
    unrelated_stmt = copy.deepcopy(stmt)
    unrelated_stmt["note"] = "a field outside the comparison rule"
    record("M10", "an agreement threshold changed after the freeze",
           verifier="c11r_compare.py", input_artifact="config/C11R_CONTRACT.json",
           mutated_path="$.comparison_semantics_frozen_before_results.factor", mutated_value=3,
           mutant_flagged=bool(K.comparison_rule_problems(planted_stmt, gate, contract)),
           clean_flagged=bool(K.comparison_rule_problems(stmt, gate, contract)),
           unrelated_flagged=bool(K.comparison_rule_problems(unrelated_stmt, gate, contract)),
           detail={"production_check": "c11r_compare.comparison_rule_problems, run by "
                                       "verify_chain before any quarantine access"})

    def weaker_verdict(runs):
        certified = [t for t in S.targets(runs).values() if t["status"] != "NOT_CERTIFIED"]
        return "N9_CLOSED" if len(certified) == 6 else "AGREEMENT_INSUFFICIENT"
    record("M11", "N9 declared closed on a weaker criterion (NOT_IMPLEMENTED counted as pass)",
           verifier="c11r_compare.py", producer="c11r_runs.py",
           mutated_path="verdict rule", mutated_value="count NOT_IMPLEMENTED as satisfied",
           mutant_flagged=weaker_verdict(base) == "N9_CLOSED",
           clean_flagged=base_cmp["N9_VERDICT"] == "N9_CLOSED",
           detail={"real_verdict_on_base": base_cmp["N9_VERDICT"]})

    def scope_problems(paths):
        return [p for p in paths if "COVERAGE_MAP_R6" in p.upper() or
                "p5y_k5_tail_c11r_n9_statement_alignment" not in p]
    changed = [f for f in C.git("diff", "--name-only", f"{C.C11_HEAD}..HEAD").splitlines() if f]
    record("M12", "adoption, coverage change or r6 smuggled in", verifier="c11r_mutations.py",
           mutated_path="changed files", mutated_value="+ K5_COVERAGE_MAP_R6.json",
           mutant_flagged=bool(scope_problems(changed + ["x/K5_COVERAGE_MAP_R6.json"])),
           clean_flagged=bool(scope_problems(changed)),
           detail={"files_changed_since_C11": len(changed)})

    # ============================ certificate-level mutants ================================
    run_mutant("M13", "a whole-kernel (K_e) certificate cited for the atom-removed tau", "tau",
               lambda r: r["targets"]["tau"].update(certificate_id="F_K"),
               path="$.targets.tau.certificate_id", value="F_K")

    def set_block(cid, blk):
        def f(r):
            r["certificates"][cid]["inputs"]["drift_block"] = list(blk)
            redigest(r["certificates"][cid])
        return f
    run_mutant("M16", "a scalar drift substituted for the block (C11's development drift)",
               "Abar", set_block("F_K", ("18355/10000", "18355/10000")),
               path="$.certificates.F_K.inputs.drift_block", value="[18355/10000] x 2")
    run_mutant("M17", "the midpoint substituted for uniform drift", "Abar",
               set_block("F_K", (mid, mid)), path="$.certificates.F_K.inputs.drift_block",
               value="[mid, mid]")
    run_mutant("M18", "endpoints only", "Abar", set_block("F_K", (e_lo, e_lo)),
               path="$.certificates.F_K.inputs.drift_block", value="[e_lo, e_lo]")
    z = -(NT.lo + NT.hi) / 2
    lo_e, hi_e = G.phi(z + NT.lo), G.phi(z + NT.hi)
    hull_hi = max(lo_e.hi, hi_e.hi)
    true_iv = I._phi_pair(z + NT.lo, z + NT.hi)
    interior = G.phi(F(0)).lo
    record("M18b", "an endpoint hull without an extremum theorem misses the interior maximum",
           verifier="c11r_idrift.py", mutated_path="_phi_pair -> hull of endpoint values",
           mutated_value=float(hull_hi), mutant_flagged=interior > hull_hi,
           clean_flagged=interior > true_iv.hi,
           detail={"block": "NON-TARGET", "phi(0)": float(interior),
                   "endpoint_hull_hi": float(hull_hi), "interval_hi": float(true_iv.hi)})
    run_mutant("M19", "K_e substituted for Khat_e in the certifier's reported kernel", "tau",
               lambda r: r["certificates"]["F_H"]["certifier_result"].update(kernel="K_e"),
               path="$.certificates.F_H.certifier_result.kernel", value="K_e")
    run_mutant("M20", "tau's certificate cited for Abar", "Abar",
               lambda r: r["targets"]["Abar"].update(certificate_id="F_H",
                                                     value=r["targets"]["tau"]["value"]),
               path="$.targets.Abar.certificate_id", value="F_H")
    run_mutant("M21", "Abar's certificate cited for tau, with Abar's value", "tau",
               lambda r: r["targets"]["tau"].update(certificate_id="F_K",
                                                    value=r["targets"]["Abar"]["value"]),
               path="$.targets.tau.certificate_id", value="F_K")
    run_mutant("M22", "cell 307's block substituted for cell 306's", "Abar",
               set_block("F_K", CELL_307_BLOCK), path="$.certificates.F_K.inputs.drift_block",
               value=list(CELL_307_BLOCK))
    m = copy.deepcopy(base)
    del m["targets"]["D2"]
    record("M23", "fewer than the six constants", verifier="c11r_schema.py",
           producer="c11r_runs.py", mutated_path="$.targets.D2", mutated_value="<deleted>",
           mutant_flagged=bool(S.validate_runs(m, check_provenance=False)),
           clean_flagged=bool(S.validate_runs(base, check_provenance=False)),
           unrelated_flagged=bool(S.validate_runs(unrel, check_provenance=False)))
    record("M24", "the atom contribution's sign flipped", verifier="c11r_idrift.py",
           mutated_path="Khat_e + atom -> Khat_e - atom", mutated_value="(0,0) on NT",
           mutant_flagged=sep(full, hat - atom) > 0, clean_flagged=sep(full, hat + atom) > 0)
    run_mutant("M25", "the drift interval narrowed", "Abar", set_block("F_K", (e_lo, mid)),
               path="$.certificates.F_K.inputs.drift_block", value="[e_lo, mid]")

    # M14 -- value trace (production: c11r_certificate.evaluate_target inside evaluate_run)
    m = copy.deepcopy(base)
    m["targets"]["Abar"]["value"] = str(F(base["targets"]["Abar"]["value"]) - F(1, 10))
    record("M14", "a reported value that its certificate did not produce",
           verifier="c11r_certificate.py", producer="c11r_runs.py", input_artifact=RUNS_IN,
           mutated_path="$.targets.Abar.value", mutated_value="value - 1/10",
           mutant_flagged=not guards(m)["value_trace"]["PASS"],
           clean_flagged=not guards(base)["value_trace"]["PASS"],
           unrelated_flagged=not guards(unrel)["value_trace"]["PASS"])
    with BD.PhiCache():
        bad = I.pointwise_refute_iv({(0, 0): F(5)}, NT, n=5)
        good = I.pointwise_refute_iv({(0, 0): F(5000)}, NT, n=5)
    record("M15", "a pointwise-infeasible member not refuted", verifier="c11r_idrift.py",
           mutated_path="candidate", mutated_value="w = 5 (infeasible) vs w = 5000",
           mutant_flagged=bad["POINTWISE_REFUTED"], clean_flagged=good["POINTWISE_REFUTED"],
           detail={"block": "NON-TARGET", "bad": bad["min_L_upper_bound"],
                   "good": good["min_L_upper_bound"]})

    # M26 -- the seal: ordering (pure) and typed (production schema)
    sealbits = {k: bool(K.verify_seal_bytes(*a)) for k, a in (
        ("never_committed", (b"x", None, False)), ("edited", (b"n", b"o", False)),
        ("uncommitted", (b"x", b"x", True)), ("sealed", (b"x", b"x", False)))}
    typed = {
        "false_seal_accepted": not S.seal_problems(base),
        "true_seal_rejected": bool(S.seal_problems(dict(base, seal=dict(
            base["seal"], contains_original_magnitudes=True)))),
        "unrelated_text_with_the_word_accepted": not S.seal_problems(dict(
            base, note="these magnitudes and original_value words are prose")),
        "real_payload_key_rejected": bool(S.seal_problems(dict(
            base, targets=dict(base["targets"], Abar=dict(base["targets"]["Abar"],
                                                          original_value="1/1"))))),
    }
    prov = copy.deepcopy(base)
    prov["provenance"] = C.provenance(CODE / "c11r_runs.py")
    prov["sha256"] = C.sha256_obj({k: v for k, v in prov.items() if k != "sha256"})
    stripped = copy.deepcopy(prov)
    del stripped["provenance"]
    record("M26", "comparison performed before the independent output is sealed",
           verifier="c11r_compare.py", producer="c11r_runs.py",
           mutated_path="$.provenance (and: uncommitted / edited / never committed / true seal)",
           mutated_value="<removed>",
           mutant_flagged=(bool(S.validate_runs(stripped)) and sealbits["never_committed"]
                           and sealbits["edited"] and sealbits["uncommitted"]
                           and typed["true_seal_rejected"] and typed["real_payload_key_rejected"]),
           clean_flagged=(bool(S.validate_runs(prov)) or sealbits["sealed"]
                          or not typed["false_seal_accepted"]),
           unrelated_flagged=not typed["unrelated_text_with_the_word_accepted"],
           detail={"typed_seal_controls": typed, "ordering_controls": sealbits,
                   "note": ("the real seal path (c11r_compare.verify_seal) reads the runs "
                            "artifact, so only the comparator may call it; the firewall forbids "
                            "it here")})
    probe = copy.deepcopy(gate)
    probe["predicates"]["G_probe"] = "this is the criterion C11R must and does fail"
    unrel_gate = copy.deepcopy(gate)
    unrel_gate["predicates"]["G_probe"] = "a predicate that states a test and no outcome"
    record("M27", "the prospective gate contains result-dependent language",
           verifier="c11r_gate.py", input_artifact="config/N9R_GATE_C11R.json",
           mutated_path="$.predicates.G_probe", mutated_value=probe["predicates"]["G_probe"],
           mutant_flagged=bool(GA.scan_for_result_language(probe)),
           clean_flagged=bool(GA.scan_for_result_language(gate)),
           unrelated_flagged=bool(GA.scan_for_result_language(unrel_gate)))

    # M28 -- G10 (production: c11r_certificate.screen_order; the comparator acts on it)
    m = copy.deepcopy(base)
    m["certificates"]["F_K"]["screen_classification"] = "POINTWISE_INFEASIBLE"
    withheld = copy.deepcopy(base)
    withheld["certificates"]["F_K"].update(screen_classification="POINTWISE_INFEASIBLE",
                                           sent_to_certification=False)
    withheld["certificates"]["F_K"]["certifier_result"].update(certified=False)
    record("M28", "a pointwise-refuted member still sent to certification",
           verifier="c11r_certificate.py", producer="c11r_runs.py", input_artifact=RUNS_IN,
           mutated_path="$.certificates.F_K.screen_classification (sent True)",
           mutated_value="POINTWISE_INFEASIBLE",
           mutant_flagged=(not guards(m)["G10"]["PASS"]
                           and compare(m)["N9_VERDICT"] == "EXECUTION_INVALID"),
           clean_flagged=not guards(base)["G10"]["PASS"] or not guards(withheld)["G10"]["PASS"],
           unrelated_flagged=not guards(unrel)["G10"]["PASS"],
           detail={"refuted_and_withheld_is_accepted": guards(withheld)["G10"]["PASS"]})

    v6 = next(c for c in val["checks"] if c["id"] == "V6")
    e = F(5, 2)
    a = X.kernel_apply({(0, 0): F(99, 10), (0, 1): F(-3, 2)}, F(3), F(1), e)
    b = I.kernel_apply_iv({(0, 0): F(99, 10), (0, 1): F(-3, 2)}, F(3), F(1), I.Blk(e, e))
    widened = G.Iv(b.lo, b.hi + F(1, 2 ** 320))
    record("M29", "the interval layer silently widening instead of collapsing onto C11",
           verifier="c11r_idrift.py", input_artifact="evidence/validation/C11R_VALIDATION.json",
           mutated_path="kernel_apply_iv result .hi", mutated_value="+ 2^-320",
           mutant_flagged=(a.lo, a.hi) != (widened.lo, widened.hi),
           clean_flagged=(a.lo, a.hi) != (b.lo, b.hi),
           cites_v6_mismatch_count=v6["detail"]["mismatch_count"],
           detail={"scalar": "5/2 (non-target)", "v6_pass": v6["pass"]})

    st_ok = {"x": 1, "provenance": {"producer": "p.py", "producer_sha256": "a",
                                    "code_closure": {}, "inputs": {}}}
    st_ok["sha256"] = C.sha256_obj({k: v for k, v in st_ok.items() if k != "sha256"})
    record("M30", "stale evidence (producer changed after the artifact was written)",
           verifier="c11r_status.py", mutated_path="producer sha256", mutated_value="changed",
           mutant_flagged=ST.freshness(st_ok, lambda r: "CHANGED")["state"] == "STALE",
           clean_flagged=ST.freshness(st_ok, lambda r: "a")["state"] != "FRESH")
    A_real = {"validation": val, "mutations": {"mutants": [{"id": "M29",
                                                          "cites_v6_mismatch_count":
                                                          v6["detail"]["mismatch_count"]}],
                                               "MUTATION_CLASS": "PASS"}}
    A_bad = copy.deepcopy(A_real)
    A_bad["mutations"]["mutants"][0]["cites_v6_mismatch_count"] = 9
    record("M31", "validation 0 mismatches beside a mutation record citing 9 (the E4 defect)",
           verifier="c11r_status.py", mutated_path="$.mutants[M29].cites_v6_mismatch_count",
           mutated_value=9, mutant_flagged=bool(ST.contradictions(A_bad)),
           clean_flagged=bool(ST.contradictions(A_real)))

    with BD.PhiCache():
        rows = [BD.box_upper_coeffs(*b_, NT, 8) for b_ in X.cover(2)]
    s = BD.select_upper(rows, "K", grid=1000, b_max=F(4), mu=F(1, 2 ** 60))
    low = min(BD.factored_upper_margin(r, "K", s["A"] - F(1, 1000), s["B"]) for r in rows)
    record("M32", "a selector returning a member below its minimal feasible A",
           verifier="c11r_boxdata.py", mutated_path="selected A", mutated_value="A - 1/1000",
           mutant_flagged=low < F(1, 2 ** 60), clean_flagged=s["min_factored_margin"] < F(1, 2 ** 60),
           detail={"block": "NON-TARGET", "config": [2, 8], "A": str(s["A"]), "B": str(s["B"])})
    with BD.PhiCache():
        lrows = [BD.box_lower_coeffs(*b_, NT, 8) for b_ in X.cover(2)]
        sl = BD.select_lower(lrows, grid=1000, beta_max=F(1), mu=F(1, 2 ** 60))
        u_ok = {(0, 0): sl["alpha"], (0, 1): sl["beta"]}
        u_bad = {(0, 0): sl["alpha"] + F(1, 10), (0, 1): sl["beta"]}
        c_ok = BD.subsolution_margin_iv(u_ok, NT, 2, 8)
        c_bad = BD.subsolution_margin_iv(u_bad, NT, 2, 8)
    record("M33", "an inflated sub-solution accepted as a lower bound", verifier="c11r_boxdata.py",
           mutated_path="alpha", mutated_value="alpha + 1/10",
           mutant_flagged=not c_bad["certified"], clean_flagged=not c_ok["certified"],
           detail={"block": "NON-TARGET", "alpha": str(sl["alpha"])})

    planted_pol = copy.deepcopy(policy)
    planted_pol["magnitudes"] = {"tau": "planted"}
    unrel_pol = copy.deepcopy(policy)
    unrel_pol["note"] = "the word magnitudes in prose is not a payload key"
    record("M34", "the policy carrying an original-magnitude payload",
           verifier="c11r_schema.py", input_artifact="config/C11R_POLICY.json",
           mutated_path="$.magnitudes", mutated_value={"tau": "planted"},
           mutant_flagged=bool(S.forbidden_payload(planted_pol)),
           clean_flagged=bool(S.forbidden_payload(policy))
           or policy["references_original_magnitudes"] is not False,
           unrelated_flagged=bool(S.forbidden_payload(unrel_pol)))

    cmp_src = C.read_code(f"{C.NS_REL}/code/c11r_compare.py")
    planted_src = 'MSG = "agreement is established with statements equal to the original"\n'
    quoting_doc = ('"""Revision 1 carried \'agreement is established\' before any run."""\n'
                   'x = 1\n')
    record("M35", "a pre-written scientific conclusion in the comparator's output prose",
           verifier="c11r_gate.py", mutated_path="<synthetic comparator source>",
           mutated_value=planted_src,
           mutant_flagged=bool(GA.scan_source_for_result_language(planted_src)),
           clean_flagged=bool(GA.scan_source_for_result_language(cmp_src)),
           unrelated_flagged=bool(GA.scan_source_for_result_language(quoting_doc)))

    chain = C.load_allowlisted("evidence/chain/C11R_CHAIN_CONTROLS.json")
    real_pf = R.preflight(C.REPO, check_processes=False)
    valid_synthetic = next((r for r in chain["controls"] if r["id"] == "R3T"), {})
    record("M36", "target execution without a bound Phase 13 authorization",
           verifier="c11r_runs.py", input_artifact="evidence/chain/C11R_CHAIN_CONTROLS.json",
           mutated_path="config/C11R_AUTHORIZATION.json", mutated_value="<absent>",
           mutant_flagged=bool(real_pf["problems"]),
           clean_flagged=not valid_synthetic.get("pass", False),
           detail={"real_tree_preflight": real_pf["problems"][:3],
                   "clean_control": "chain control R3T: a fully bound synthetic chain is "
                                    "accepted by the same pre-flight",
                   "wrong_contract_and_tamper_controls": "chain controls R3B-R3S"})
    run_mutant("M37", "D1 claimed from a supersolution certificate, which cannot bound it", "D1",
               lambda r: r["targets"].update(D1=S.target("D1", status="CERTIFIED", value=F(3),
                                                         reason=None, certificate_id="F_K")),
               path="$.targets.D1", value="CERTIFIED via F_K")
    m = copy.deepcopy(base)
    m["targets"]["Abar"] = S.target("Abar", status="NOT_IMPLEMENTED", value=None, reason="planted",
                                    certificate_id=None)
    record("M38", "a constant the policy implements marked NOT_IMPLEMENTED (G8)",
           verifier="c11r_certificate.py", producer="c11r_runs.py",
           input_artifact="config/C11R_POLICY.json", mutated_path="$.targets.Abar.status",
           mutated_value="NOT_IMPLEMENTED",
           mutant_flagged=(not guards(m)["G8"]["PASS"]
                           and compare(m)["N9_VERDICT"] == "EXECUTION_INVALID"),
           clean_flagged=not guards(base)["G8"]["PASS"],
           unrelated_flagged=not guards(unrel)["G8"]["PASS"])
    other = copy.deepcopy(policy)
    other["configuration"]["chosen"] = dict(policy["configuration"]["chosen"],
                                            panels=policy["configuration"]["chosen"]["panels"] * 2)
    m = build(K.synthetic_certs(stmt, other))
    record("M39", "certificates made at another configuration than the frozen one (G19)",
           verifier="c11r_certificate.py", producer="c11r_runs.py",
           input_artifact="config/C11R_POLICY.json", mutated_path="$.certificates.*.inputs.panels",
           mutated_value="2 x frozen panels",
           mutant_flagged=(not guards(m)["G19"]["PASS"]
                           and compare(m)["N9_VERDICT"] == "EXECUTION_INVALID"),
           clean_flagged=not guards(base)["G19"]["PASS"],
           unrelated_flagged=not guards(unrel)["G19"]["PASS"])

    # ============================ the thirteen adversarial certificate controls ============
    def adv(aid, attack, target, mutate, *, deductions=None, exp=None, note=None):
        mm = copy.deepcopy(base)
        mutate(mm)
        res = compare(mm, deductions=deductions, exp=exp)
        cls = res["classes"][target]
        caught = cls in ("INVALID", "DISAGREES") and res["N9_VERDICT"] != "N9_CLOSED"
        ADV.append({"id": aid, "attack": attack, "target": target,
                    "clean_class": base_cls[target], "mutant_class": cls,
                    "verdict": res["N9_VERDICT"], "caught": caught,
                    "statement_result": res["per_target"][target].get("statement"),
                    "numeric_result": res["per_target"][target].get("numeric"),
                    "unrelated_mutation_changes_class": unrel_cls[target] != base_cls[target],
                    "note": note})

    def forge_certified_with_negative_margin(r):
        r["certificates"]["F_K"]["certifier_result"].update(margin_lower_bound="-1/1000")
    adv("ADV01", "forged certificate: certified=True over a negative margin", "Abar",
        forge_certified_with_negative_margin)
    adv("ADV02", "value halved after certification", "Abar",
        lambda r: r["targets"]["Abar"].update(value=str(F(r["targets"]["Abar"]["value"]) / 2)))
    adv("ADV03", "K_e certificate relabelled Khat_e (reported kernel)", "Abar",
        lambda r: r["certificates"]["F_K"]["certifier_result"].update(kernel="Khat_e"),
        note=("a CONSISTENT relabel -- the atom-removal argument changed too and the digest "
              "recomputed -- is a record indistinguishable from a real Khat_e run; only "
              "re-execution detects it. See c11r_certificate, 'what reconstruction cannot see'."))
    adv("ADV04", "Khat_e certificate relabelled K_e (reported kernel)", "tau",
        lambda r: r["certificates"]["F_H"]["certifier_result"].update(kernel="K_e"))
    adv("ADV05a", "direction swapped: the LOWER-bound target cites an UPPER-bound certificate",
        "D_lo", lambda r: r["targets"]["D_lo"].update(certificate_id="F_H",
                                                      value=r["targets"]["tau"]["value"]))
    flipped = copy.deepcopy(CV.DEDUCTIONS)
    flipped[("c11r_boxdata.py", "subsolution_margin_iv", "Khat_e")]["direction"] = "UPPER_BOUND"
    adv("ADV05b", "direction swapped in the deduction: a sub-solution read as an UPPER bound",
        "D_lo", lambda r: None, deductions=flipped)
    adv("ADV06", "cell 306 -> cell 307 (consistent re-digested certificate)", "Abar",
        set_block("F_K", CELL_307_BLOCK))
    adv("ADV07", "reachable set changed: the certificate's cover is not the certified one",
        "tau", lambda r: r["certificates"]["F_H"].update(
            cover={"function": "c11_certifier.cover_without_axes",
                   "depth": r["certificates"]["F_H"]["inputs"]["depth"]}))
    adv("ADV08", "aggregation swapped: an UPPER bound aggregated by MIN over sub-blocks", "Abar",
        lambda r: r["certificates"]["F_K"].update(aggregation="min_over_sub_blocks"))
    adv("ADV09", "the D_lo sub-solution relabelled as D1", "D1",
        lambda r: r["targets"].update(D1=S.target("D1", status="CERTIFIED",
                                                  value=F(r["targets"]["D_lo"]["value"]),
                                                  reason=None, certificate_id="F_D")))
    conditional = copy.deepcopy(CV.DEDUCTIONS)
    conditional[("c11r_derivative.py", "derivative_propagation", "Khat_e")].update(
        implemented=True, family="w = A - B*m", kind=CV.SUPER,
        yields={"D1": "w_at_atom"})                       # a TEST-ONLY implemented route

    def add_conditional(premises):
        def f(r):
            c = copy.deepcopy(r["certificates"]["F_H"])
            c.update(certificate_id="F_DV", premises=sorted(premises))
            c["certifier"] = {"module": "c11r_derivative.py", "function": "derivative_propagation",
                              "module_sha256": "t"}
            redigest(c)
            r["certificates"]["F_DV"] = c
            r["targets"]["D1"] = S.target("D1", status="CERTIFIED", value=F(c["weight"]["0,0"]),
                                          reason=None, certificate_id="F_DV")
        return f
    exp_t = dict(EXP, **{"c11r_derivative.py": "t"})
    adv("ADV10", "missing dependency: a conditional derivation omits one premise", "D1",
        add_conditional(["C_T_independent"]), deductions=conditional, exp=exp_t)
    adv("ADV11a", "candidate function changed after certification (digest not recomputed)",
        "Abar", lambda r: r["certificates"]["F_K"]["weight"].update({"0,0": "20"}))
    adv("ADV11b", "candidate function changed and re-digested; the value no longer traces",
        "Abar", lambda r: redigest(r["certificates"]["F_K"]) if r["certificates"]["F_K"][
            "weight"].update({"0,0": "20"}) is None else None)
    adv("ADV12a", "certifier hash changed (re-digested)", "Abar",
        lambda r: redigest(r["certificates"]["F_K"]) if r["certificates"]["F_K"][
            "certifier"].update(module_sha256="0" * 64) is None else None)
    adv("ADV12b", "the certifier that ran is not the one bound at the seal", "Abar",
        lambda r: None, exp=dict(EXP, **{"c11r_idrift.py": "1" * 64}))
    adv("ADV13", "conditional derivation presented as unconditional (no premises declared)",
        "D1", add_conditional([]), deductions=conditional, exp=exp_t)
    # the separation of STATEMENT EQUIVALENCE from NUMERICAL AGREEMENT
    far = compare(build(K.synthetic_certs(stmt, policy, A_K=F(25))))
    separation = {
        "statement_status_clean": base_cmp["per_target"]["Abar"]["statement"]["STATUS"],
        "statement_status_far": far["per_target"]["Abar"]["statement"]["STATUS"],
        "numeric_clean": base_cmp["per_target"]["Abar"]["numeric"]["class"],
        "numeric_far": far["per_target"]["Abar"]["numeric"]["class"]}
    separation["pass"] = (separation["statement_status_clean"] == separation[
        "statement_status_far"] == "EQUIVALENT" and separation["numeric_clean"]
        != separation["numeric_far"])
    adv_ok = all(r["caught"] and not r["unrelated_mutation_changes_class"] for r in ADV) \
        and base_cmp["N9_VERDICT"] != "N9_CLOSED" and separation["pass"]

    ks = K.self_test(stmt, policy)
    es = EQ.self_test(stmt)
    bad = [r["id"] for r in RES if r["outcome"] != "DETECTED"]
    adv_missed = [r["id"] for r in ADV if not r["caught"]]
    out = {"schema": "C11R_MUTATIONS/4",
           "supersedes": ("C11R_MUTATIONS/2 at affdf8a3, whose value-trace, screen-order and "
                          "disposition detectors were test-only copies (erratum E17)); "
                          "C11R_MUTATIONS/3 at eaca931e, which overstated that it defined no "
                          "guard (erratum E30)"),
           "rules": ["every detector is a production function; this module defines no guard",
                     "run artifacts built by c11r_runs.assemble from c11r_certificate certificates",
                     "each mutant: mutant flagged AND clean accepted AND unrelated not flagged",
                     "numerical mutants on the NON-TARGET block only",
                     "UNDETERMINED is never a pass"],
           "base_artifact_classes_on_synthetic_magnitudes": base_cls,
           "base_verdict_on_synthetic_magnitudes": base_cmp["N9_VERDICT"],
           "mutants": RES,
           "detector_kinds": {k: sum(1 for r in RES if r["detector_kind"] == k) for k in KIND},
           "what_demonstrates_production_enforcement": ("only rows with detector_kind "
                                                        "PRODUCTION_GUARD or PRODUCTION_SCIENCE"),
           "adversarial_controls": ADV,
           "adversarial_controls_missed": adv_missed,
           "statement_vs_number_separation": separation,
           "comparator_self_test": {"PASS": ks["PASS"], "cases": len(ks["cases"]),
                                    "used_real_magnitudes": ks["used_real_magnitudes"]},
           "equivalence_self_test": {"PASS": es["PASS"], "cases": len(es["cases"])},
           "not_detected": bad,
           "MUTATION_CLASS": "PASS" if (not bad and adv_ok and ks["PASS"] and es["PASS"])
           else "REFUSE"}
    sh = C.write_evidence(C.NS / "evidence" / "mutations" / "C11R_MUTATIONS.json", out,
                          producer=__file__)
    for r in RES:
        print(f"  {r['outcome']:15s} {r['id']:5s} {r['name'][:78]}")
    print("\nadversarial certificate controls:")
    for r in ADV:
        print(f"  {'caught ' if r['caught'] else 'MISSED '} {r['id']:7s} {r['attack'][:62]:62s} "
              f"{r['clean_class']:>10s} -> {r['mutant_class']:9s} {r['verdict']}")
    print(f"\nseparation (same proposition, different value): {separation}")
    print(f"comparator self-test {ks['PASS']} ({len(ks['cases'])} cases); equivalence self-test "
          f"{es['PASS']} ({len(es['cases'])} cases)")
    print(f"MUTATION_CLASS = {out['MUTATION_CLASS']}   not detected: {bad}   adversarial missed: "
          f"{adv_missed}")
    print(f"wrote evidence/mutations/C11R_MUTATIONS.json sha256 {sh[:16]}...")
    return 0 if out["MUTATION_CLASS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
