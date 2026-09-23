"""C11R Repair D -- the mutation suite, rebuilt (revision 2).

WHAT WAS WRONG (erratum E7). M26 read a key the runs producer never wrote and was guaranteed to
report SURVIVED; M28 read a path the producer never wrote and could never fire; M03 missed the
screen reading original magnitudes through the table; M29's control was a transcribed number. And
the committed mutation artifact was stale beside the validation it contradicted (erratum E4).

THE RULES NOW
  * Run-artifact mutants operate on artifacts built by c11r_runs.assemble -- the producer's own
    emission function -- read through c11r_schema's accessors. A path mismatch cannot arise.
  * Every mutant records the producer, verifier and input hashes, the exact JSON path and value it
    mutated, and three outcomes: the MUTANT must be flagged, the CLEAN control must be accepted,
    and (where meaningful) an UNRELATED mutation must NOT be flagged. A false positive on either
    control marks the detector DETECTOR_BROKEN, which counts against the suite like a survivor.
  * Numerical mutants run on the NON-TARGET block NT = [5/2, 5/2 + 108337/1250000] only.
  * UNDETERMINED is never a pass. MUTATION_CLASS = PASS requires every mutant DETECTED.
  * No count is transcribed: M29 cites the V6 mismatch count it READS from the validation
    artifact, and c11r_status cross-checks the two.
"""
from __future__ import annotations

import ast
import copy
import json
import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_boxdata as BD
import c11r_common as C
import c11r_compare as K
import c11r_equiv as EQ
import c11r_firewall as FW
import c11r_gate as GA
import c11r_idrift as I
import c11r_runs as R
import c11r_schema as S
import c11r_status as ST

X, G = I.X, I.G
W = F(108337, 1250000)
NT = I.Blk(F(5, 2), F(5, 2) + W)
CODE = C.NS / "code"
RES: list[dict] = []


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


def _set(obj, path: list, value):
    o = obj
    for k in path[:-1]:
        o = o[k]
    o[path[-1]] = value


# ---------------------------------------------------------------------------------------------
# the base artifact: built by the PRODUCER'S OWN emission function, with SYNTHETIC values
# ---------------------------------------------------------------------------------------------
def base_runs(policy: dict, stmt: dict) -> dict:
    e_lo, e_hi = F(stmt["drift_domain"]["e_lo"]), F(stmt["drift_domain"]["e_hi"])
    D = policy["configuration"]["chosen"]["depth"]
    P = policy["configuration"]["chosen"]["panels"]

    def cert(route, kernel, family, sel):
        return S.certificate(route=route, kernel=kernel, family=family,
                             screen_classification="POINTWISE_FEASIBLE", sent_to_box_pass=True,
                             ladder_level="single", depth=D, panels=P, boxes=0, selected=sel,
                             certified=True, margin_lower_bound="1/1000",
                             w_min_lower_bound="1", seconds=0.0)
    A_K, B_K, A_H, B_H = F(1111, 100), F(3, 2), F(999, 100), F(3, 2)   # synthetic
    al, be = F(1, 2), F(1, 20)                                           # synthetic
    certs = {"F_K": cert("independent_supersolution", "K_e", "w = A - B*m",
                         {"A": str(A_K), "B": str(B_K)}),
             "F_H": cert("independent_supersolution", "Khat_e", "w = A - B*m",
                         {"A": str(A_H), "B": str(B_H)}),
             "F_D": cert("independent_subsolution", "Khat_e", "u = alpha + beta*m",
                         {"alpha": str(al), "beta": str(be)})}
    selected = {"F_K": {"A": A_K, "B": B_K, "w": {(0, 0): A_K, (0, 1): -B_K},
                        "pointwise_A_min": F(5)},
                "F_H": {"A": A_H, "B": B_H, "w": {(0, 0): A_H, (0, 1): -B_H},
                        "pointwise_A_min": F(5)},
                "F_D": {"alpha": al, "beta": be}}
    return R.assemble(policy=policy, stmt=stmt, e_lo=e_lo, e_hi=e_hi, D=D, P=P, n_boxes=0,
                      certs=certs, selected=selected, stop_reason=None, timings={"x": 0.0},
                      total_seconds=0.0, peak_rss_mb=0.0)


FAKE_MAGS = {"Abar": F(10), "tau": F(10), "C_T": F(10), "D_lo": F(1, 2), "D1": F(10),
             "D2": F(10)}                                                # synthetic, deliberately


def trace_values(runs: dict) -> list[str]:
    """Each CERTIFIED target's value must be REPRODUCED from what its certificate selected.

    Abar and tau are w(atom) = A; D_lo is u(atom) = alpha; C_T is sup over the cover of the
    certified w, recomputed here exactly as the producer computes it (interval evaluation over
    X.cover at the run's depth), and required to match bit for bit. A tolerance would accept a
    value no certificate produced; this does not.
    """
    bad = []
    cm = S.certificates(runs)
    depth = runs["configuration"]["depth"]
    for k, t in S.targets(runs).items():
        if t["status"] != "CERTIFIED":
            continue
        sel = cm[t["certificate_id"]]["selected"] or {}
        if k == "D_lo":
            want = F(sel["alpha"]) if "alpha" in sel else None
        elif k == "C_T":
            w = {(0, 0): F(sel["A"]), (0, 1): -F(sel["B"])}
            want = max(X.poly_eval_iv(w, G.Iv(a, b), G.Iv(c, d)).hi
                       for (a, b, c, d) in X.cover(depth))
        else:
            want = F(sel["A"]) if "A" in sel else None
        if want is None or F(t["value"]) != want:
            bad.append(f"{k}: value {t['value']} is not reproduced from certificate {sel}")
    return bad


def refuted_but_sent(runs: dict) -> list[str]:
    return [cid for cid, c in S.certificates(runs).items()
            if S.cert_screen_class(c) == "POINTWISE_INFEASIBLE" and S.cert_sent_to_box_pass(c)]


def dispositions_consistent(runs: dict, policy: dict) -> list[str]:
    implementable = set(policy["target_scope"]["implementable_under_this_policy"])
    return [k for k, t in S.targets(runs).items()
            if t["status"] == "NOT_IMPLEMENTED" and k in implementable]


def imports_in(src: str) -> set[str]:
    roots = set()
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Import):
            roots |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
            roots.add(n.module.split(".")[0])
    return roots


RESULT_PHRASES = GA.RESULT_LANGUAGE + [r"\bagreement is established\b", r"\bno target is invalid\b",
                                       r"\bnone disagrees\b", r"\bwill agree\b"]


def result_phrases_in(src: str) -> list[str]:
    """Result-dependent phrases in strings that can reach OUTPUT.

    Docstrings are excluded: the defect class is pre-written OUTPUT prose, and the comparator's
    docstring legitimately QUOTES the revision-1 phrases in order to document their removal. The
    first version of this detector read that quotation as an assertion (the C10 lesson) and
    flagged the clean comparator.
    """
    import re
    tree = ast.parse(src)
    docs = FW._docstring_nodes(tree)
    hits = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs:
            for pat in RESULT_PHRASES:
                if re.search(pat, n.value, re.I):
                    hits.append(n.value[:60])
    return hits


def main() -> int:
    stmt = C.load(C.NS / "evidence" / "table" / "C11R_N9_STATEMENTS.json")
    policy = C.load(C.NS / "config" / "C11R_POLICY.json")
    gate = C.load(C.NS / "config" / "N9R_GATE_C11R.json")
    val = C.load(C.NS / "evidence" / "validation" / "C11R_VALIDATION.json")
    base = base_runs(policy, stmt)
    e_lo, e_hi = stmt["drift_domain"]["e_lo"], stmt["drift_domain"]["e_hi"]
    mid = str((F(e_lo) + F(e_hi)) / 2)
    RUNS_IN = "evidence/table/C11R_N9_STATEMENTS.json"

    def classes(r):
        return K.run_comparison(r, stmt, FAKE_MAGS)["classes"]

    base_cls = classes(base)

    def stmt_mutant(mid_, name, target, path_tail, value, expect_class="INVALID"):
        m = copy.deepcopy(base)
        _set(m, ["targets", target, "statement"] + path_tail, value)
        u = copy.deepcopy(base)
        u["timings_seconds"] = {"x": 1.0}                   # an unrelated mutation
        record(mid_, name, verifier="c11r_compare.py", producer="c11r_runs.py",
               input_artifact=RUNS_IN,
               mutated_path="$.targets." + target + ".statement." + ".".join(map(str, path_tail)),
               mutated_value=value,
               mutant_flagged=classes(m)[target] == expect_class,
               clean_flagged=base_cls[target] in ("INVALID", "DISAGREES"),
               unrelated_flagged=classes(u)[target] != base_cls[target],
               detail={"clean_class": base_cls[target], "mutant_class": classes(m)[target]})

    # ---------------- independence and backend -------------------------------------------
    closure = {}
    for m in sorted(CODE.glob("c11r_*.py")):
        closure.update(C.code_closure(m))
    roots = set()
    for rel in closure:
        roots |= imports_in((C.REPO / rel).read_text())
    forb = set(S.FORBIDDEN_PRODUCERS)
    planted = "import taboo_certify\nfrom opnorms import kernel_norm\n"
    record("M01", "hidden import of the original certifier's load-bearing graph",
           verifier="c11r_mutations.py", mutated_path="<synthetic module source>",
           mutated_value=planted, mutant_flagged=bool(imports_in(planted) & forb),
           clean_flagged=bool(roots & forb),
           detail={"modules_in_closure": len(closure), "imported_roots": sorted(roots)})
    backend = {"numpy", "flint", "scipy", "mpmath", "sympy", "gmpy2"}
    planted = "import numpy as np\nfrom flint import arb\n"
    record("M02", "the original's arithmetic backend", verifier="c11r_mutations.py",
           mutated_path="<synthetic module source>", mutated_value=planted,
           mutant_flagged=bool(imports_in(planted) & backend), clean_flagged=bool(roots & backend))
    fw = FW.run_controls()
    real_fw = C.load(C.NS / "evidence" / "firewall" / "C11R_FIREWALL.json")
    record("M03", "reading original magnitudes from ANY path (registry, quarantine, old table, "
                  "proxy function, subprocess, magnitude key)",
           verifier="c11r_firewall.py", input_artifact="evidence/firewall/C11R_FIREWALL.json",
           mutated_path="<8 planted module sources>", mutated_value=sorted(FW.POSITIVE),
           mutant_flagged=fw["all_positives_flagged"],
           clean_flagged=(not fw["no_negative_flagged"]) or real_fw["FIREWALL_CLASS"] != "PASS",
           detail={"real_tree_class": real_fw["FIREWALL_CLASS"],
                   "offenders": real_fw["offenders"]})

    # ---------------- soundness of the reviewed machinery (NT) ----------------------------
    w = {(0, 0): F(12), (0, 1): F(-3, 2)}
    bx = (F(0), F(1), F(0), F(1))
    pts = [(bx[0], bx[2]), (bx[1], bx[3]), ((bx[0] + bx[1]) / 2, (bx[2] + bx[3]) / 2),
           (bx[0], bx[3]), (bx[1], bx[2])]
    with BD.PhiCache():
        pw = {pt: I.kernel_apply_iv(w, *pt, NT) for pt in pts}
        real_ub = I.kernel_box_upper_iv(w, *bx, NT, 16).hi
    mid_pt = ((bx[0] + bx[1]) / 2, (bx[2] + bx[3]) / 2)
    planted_ub = pw[mid_pt].hi                                  # midpoint-for-whole-box
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
    reversed_L = wv.hi - 1 - kv.lo                              # lower/upper reversed
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
        shifted = I.shifted_moments_iv(-I.K + F(1, 4), I.K, NT, 0)[0]   # a shifted "atom"
    sep = lambda a, b: max(a.lo - b.hi, b.lo - a.hi)             # noqa: E731
    record("M06", "wrong atom window", verifier="c11r_idrift.py",
           mutated_path="atom window [m-K, K-p] -> [m-K+1/4, K-p]", mutated_value="(0,0)",
           mutant_flagged=sep(full, hat + shifted) > 0, clean_flagged=sep(full, hat + atom) > 0,
           detail={"block": "NON-TARGET"})

    import re
    txt = (C.REPO / "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/"
           "cusum_layer1.py").read_text()
    kf = F(re.search(r"K_FROZEN\s*=\s*([0-9.]+)", txt).group(1))
    hf = F(re.search(r"H_FROZEN\s*=\s*([0-9.]+)", txt).group(1))
    record("M07", "wrong frozen model constants", verifier="c11r_mutations.py",
           input_artifact=None, mutated_path="K", mutated_value="1/3",
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

    # at a SCALAR drift (non-target e = 5/2) both enclosures are ~1e-95 wide, so a 1e-6 shift is
    # detectable; over the whole block they are ~0.06 wide and would swallow it (the first
    # version of this mutant was set there and SURVIVED for exactly that reason)
    PT = I.Blk(F(5, 2), F(5, 2))
    k1 = I.kernel_apply_iv(one, F(0), F(0), PT)
    rhs = G.Iv(1, 1) - I.alarm_prob_iv(F(0), F(0), PT)
    off = G.Iv(rhs.lo + F(1, 10 ** 6), rhs.hi + F(1, 10 ** 6))
    record("M09", "the kernel/alarm identity holding only approximately",
           verifier="c11r_mutations.py", mutated_path="1 - h1 at (0,0), e = 5/2",
           mutated_value="shifted by 1e-6",
           mutant_flagged=sep(k1, off) > 0, clean_flagged=sep(k1, rhs) > 0,
           detail={"enclosure_width": float(k1.hi - k1.lo)})

    # ---------------- governance --------------------------------------------------------
    r1_gate = json.loads(C.blob_at("49b17ab4", str((C.NS / "config" / "N9R_GATE_C11R.json")
                                                   .relative_to(C.REPO))))
    now_rule = stmt["comparison_semantics_frozen_before_results"]
    planted_rule = copy.deepcopy(now_rule)
    planted_rule["factor"] = 3
    record("M10", "an agreement threshold changed after the fact", verifier="c11r_mutations.py",
           input_artifact="evidence/table/C11R_N9_STATEMENTS.json",
           mutated_path="$.comparison_semantics_frozen_before_results.factor", mutated_value=3,
           mutant_flagged=planted_rule != r1_gate["comparison_rule"],
           clean_flagged=now_rule != r1_gate["comparison_rule"],
           detail={"frozen_at": "49b17ab4 (revision-1 gate), before any independent result"})

    def weaker_verdict(runs):
        certified = [t for t in S.targets(runs).values() if t["status"] != "NOT_CERTIFIED"]
        return "N9_CLOSED" if len(certified) == 6 else "AGREEMENT_INSUFFICIENT"
    closed_by_real = K.run_comparison(base, stmt, FAKE_MAGS)["N9_VERDICT"] == "N9_CLOSED"
    record("M11", "N9 declared closed on a weaker criterion (NOT_IMPLEMENTED counted as pass)",
           verifier="c11r_compare.py", producer="c11r_runs.py",
           mutated_path="verdict rule", mutated_value="count NOT_IMPLEMENTED as satisfied",
           mutant_flagged=weaker_verdict(base) == "N9_CLOSED", clean_flagged=closed_by_real,
           detail={"real_verdict_on_base": K.run_comparison(base, stmt, FAKE_MAGS)["N9_VERDICT"]})

    def scope_problems(paths):
        return [p for p in paths if "COVERAGE_MAP_R6" in p.upper() or
                "p5y_k5_tail_c11r_n9_statement_alignment" not in p]
    changed = [f for f in C.git("diff", "--name-only", f"{C.C11_HEAD}..HEAD").splitlines() if f]
    record("M12", "adoption, coverage change or r6 smuggled in", verifier="c11r_mutations.py",
           mutated_path="changed files", mutated_value="+ K5_COVERAGE_MAP_R6.json",
           mutant_flagged=bool(scope_problems(changed + ["x/K5_COVERAGE_MAP_R6.json"])),
           clean_flagged=bool(scope_problems(changed)),
           detail={"files_changed_since_C11": len(changed)})

    stmt_mutant("M13", "a whole-kernel certificate read as the atom-removed tau", "tau",
                ["kernel"], "K_e")
    # M14 -- a value no certificate produced
    m = copy.deepcopy(base)
    _set(m, ["targets", "Abar", "value"], str(F(base["targets"]["Abar"]["value"]) - F(1, 10)))
    u = copy.deepcopy(base)
    u["timings_seconds"] = {"x": 2.0}
    record("M14", "a reported value that its certificate did not produce",
           verifier="c11r_mutations.py", producer="c11r_runs.py", input_artifact=RUNS_IN,
           mutated_path="$.targets.Abar.value", mutated_value="value - 1/10",
           mutant_flagged=bool(trace_values(m)), clean_flagged=bool(trace_values(base)),
           unrelated_flagged=bool(trace_values(u)))

    with BD.PhiCache():
        bad = I.pointwise_refute_iv({(0, 0): F(5)}, NT, n=5)
        good = I.pointwise_refute_iv({(0, 0): F(5000)}, NT, n=5)
    record("M15", "a pointwise-infeasible member not refuted", verifier="c11r_idrift.py",
           mutated_path="candidate", mutated_value="w = 5 (infeasible) vs w = 5000",
           mutant_flagged=bad["POINTWISE_REFUTED"], clean_flagged=good["POINTWISE_REFUTED"],
           detail={"block": "NON-TARGET", "bad": bad["min_L_upper_bound"],
                   "good": good["min_L_upper_bound"]})

    # ---------------- the campaign's required mutants M16-M28 ---------------------------
    stmt_mutant("M16", "a scalar drift substituted for the block (C11's e = 18355/10000)", "Abar",
                ["drift_domain"], ["18355/10000", "18355/10000"])
    stmt_mutant("M17", "the midpoint substituted for uniform drift", "Abar",
                ["drift_domain"], [mid, mid])
    stmt_mutant("M18", "endpoints only", "Abar", ["drift_domain"], [e_lo, e_lo])
    # and the mathematics behind M18: an endpoint hull misses an interior extremum of phi
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
    stmt_mutant("M19", "K_e substituted for Khat_e (kernel and convention)", "tau",
                ["kernel"], "K_e")
    abar_st = copy.deepcopy(base["targets"]["Abar"]["statement"])
    tau_st = copy.deepcopy(base["targets"]["tau"]["statement"])
    for mid_, name, tgt, repl in (("M20", "tau substituted for Abar", "Abar", tau_st),
                                  ("M21", "Abar substituted for tau", "tau", abar_st)):
        m = copy.deepcopy(base)
        m["targets"][tgt]["statement"] = repl
        record(mid_, name, verifier="c11r_compare.py", producer="c11r_runs.py",
               input_artifact=RUNS_IN, mutated_path=f"$.targets.{tgt}.statement",
               mutated_value=repl["constant"],
               mutant_flagged=classes(m)[tgt] == "INVALID",
               clean_flagged=base_cls[tgt] == "INVALID")
    stmt_mutant("M22", "cell 307 substituted for cell 306", "Abar", ["drift_domain"],
                ["17885921/10000000", "1882413/1000000"])
    m = copy.deepcopy(base)
    del m["targets"]["D2"]
    record("M23", "fewer than the six constants", verifier="c11r_schema.py",
           producer="c11r_runs.py", mutated_path="$.targets.D2", mutated_value="<deleted>",
           mutant_flagged=bool(S.validate_runs(m, check_provenance=False)),
           clean_flagged=bool(S.validate_runs(base, check_provenance=False)))
    record("M24", "the atom contribution's sign flipped", verifier="c11r_idrift.py",
           mutated_path="Khat_e + atom -> Khat_e - atom", mutated_value="(0,0) on NT",
           mutant_flagged=sep(full, hat - atom) > 0, clean_flagged=sep(full, hat + atom) > 0)
    stmt_mutant("M25", "the drift interval narrowed", "Abar", ["drift_domain"], [e_lo, mid])

    # M26 -- comparison before seal: the pure seal check, the real seal path, and a real-schema
    # artifact stripped of its provenance
    sealbits = {k: bool(K.verify_seal_bytes(*a)) for k, a in (
        ("never_committed", (b"x", None, False)), ("edited", (b"n", b"o", False)),
        ("uncommitted", (b"x", b"x", True)), ("sealed", (b"x", b"x", False)))}
    reads_before = set(C._READS)
    real = K.verify_seal()
    quarantine_read = any("ORIGINAL_MAGNITUDES" in k for k in set(C._READS) - reads_before)
    prov = copy.deepcopy(base)
    prov["provenance"] = C.provenance(CODE / "c11r_runs.py")
    prov["sha256"] = C.sha256_obj({k: v for k, v in prov.items() if k != "sha256"})
    stripped = copy.deepcopy(prov)
    del stripped["provenance"]
    record("M26", "comparison performed before the independent output is sealed",
           verifier="c11r_compare.py", producer="c11r_runs.py",
           mutated_path="$.provenance (and: uncommitted / edited / never committed)",
           mutated_value="<removed>",
           mutant_flagged=(bool(S.validate_runs(stripped)) and sealbits["never_committed"]
                           and sealbits["edited"] and sealbits["uncommitted"]),
           clean_flagged=bool(S.validate_runs(prov)) or sealbits["sealed"],
           detail={"real_tree_seal_problems": real["problems"],
                   "real_seal_path_refuses": bool(real["problems"]),
                   "quarantine_read_by_the_seal_check": quarantine_read})
    probe = copy.deepcopy(gate)
    probe["predicates"]["G_probe"] = "this is the criterion C11R must and does fail"
    record("M27", "the prospective gate contains result-dependent language",
           verifier="c11r_gate.py", input_artifact="config/N9R_GATE_C11R.json",
           mutated_path="$.predicates.G_probe", mutated_value=probe["predicates"]["G_probe"],
           mutant_flagged=bool(GA.scan_for_result_language(probe)),
           clean_flagged=bool(GA.scan_for_result_language(gate)))
    m = copy.deepcopy(base)
    _set(m, ["certificates", "F_K", "screen_classification"], "POINTWISE_INFEASIBLE")
    ok_ref = copy.deepcopy(m)
    _set(ok_ref, ["certificates", "F_K", "sent_to_box_pass"], False)
    u = copy.deepcopy(base)
    _set(u, ["certificates", "F_K", "margin_lower_bound"], "2/1000")
    record("M28", "a pointwise-refuted member still sent to certification",
           verifier="c11r_mutations.py", producer="c11r_runs.py", input_artifact=RUNS_IN,
           mutated_path="$.certificates.F_K.screen_classification (sent_to_box_pass True)",
           mutated_value="POINTWISE_INFEASIBLE", mutant_flagged=bool(refuted_but_sent(m)),
           clean_flagged=bool(refuted_but_sent(base)) or bool(refuted_but_sent(ok_ref)),
           unrelated_flagged=bool(refuted_but_sent(u)),
           detail={"refuted_and_withheld_is_accepted": not refuted_but_sent(ok_ref)})

    # M29 -- executed scalar collapse; the V6 count is READ, not transcribed
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

    # ---------------- revision-2 machinery -----------------------------------------------
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

    def has_mag_keys(o):
        found = []

        def walk(x):
            if isinstance(x, dict):
                for k2, v2 in x.items():
                    if k2 in FW.MAGNITUDE_KEYS:
                        found.append(k2)
                    walk(v2)
            elif isinstance(x, list):
                for v2 in x:
                    walk(v2)
        walk(o)
        return bool(found)
    record("M34", "the policy carrying an original magnitude", verifier="c11r_firewall.py",
           input_artifact="config/C11R_POLICY.json", mutated_path="$.magnitudes",
           mutated_value={"tau": "planted"}, mutant_flagged=has_mag_keys(planted_pol),
           clean_flagged=has_mag_keys(policy) or policy["references_original_magnitudes"])

    cmp_src = (CODE / "c11r_compare.py").read_text()
    planted_src = 'MSG = "agreement is established with statements equal to the original"\n'
    quoting_doc = ('"""Revision 1 carried \'agreement is established\' before any run."""\n'
                   'x = 1\n')
    record("M35", "a pre-written scientific conclusion in the comparator's output prose",
           verifier="c11r_mutations.py", mutated_path="<synthetic comparator source>",
           mutated_value=planted_src, mutant_flagged=bool(result_phrases_in(planted_src)),
           clean_flagged=bool(result_phrases_in(cmp_src)),
           unrelated_flagged=bool(result_phrases_in(quoting_doc)),
           detail={"hits_in_real_comparator_output_strings": result_phrases_in(cmp_src),
                   "a_docstring_quoting_the_phrase_is_not_flagged":
                       not result_phrases_in(quoting_doc)})

    self_sha = C.sha256_file(CODE / "c11r_runs.py")
    good_auth = {"guard": "ALLOW", "cell": 306, "policy_sha256": policy["sha256"],
                 "statements_sha256": stmt["sha256"], "runs_producer_sha256": self_sha}
    bad_auth = dict(good_auth, policy_sha256="0" * 64)
    real_block = R.authorised(policy, stmt)
    record("M36", "target execution without a bound Phase 13 authorization",
           verifier="c11r_runs.py", mutated_path="authorization.policy_sha256",
           mutated_value="0" * 16,
           mutant_flagged=bool(R.check_authorization(bad_auth, policy, stmt, self_sha))
           and bool(R.check_authorization(None, policy, stmt, self_sha)),
           clean_flagged=bool(R.check_authorization(good_auth, policy, stmt, self_sha)),
           detail={"real_tree_refuses": real_block})

    m = copy.deepcopy(base)
    m["targets"]["D1"] = S.target("D1", status="CERTIFIED", value=F(3),
                                  stmt=EQ.honest_independent("D1", (e_lo, e_hi),
                                                             "independent_supersolution"),
                                  reason=None, certificate_id="F_K")
    record("M37", "D1 claimed through a route that cannot bound a derivative",
           verifier="c11r_equiv.py", producer="c11r_runs.py", input_artifact=RUNS_IN,
           mutated_path="$.targets.D1", mutated_value="CERTIFIED via independent_supersolution",
           mutant_flagged=classes(m)["D1"] == "INVALID",
           clean_flagged=base_cls["D1"] == "INVALID")
    m = copy.deepcopy(base)
    m["targets"]["Abar"] = S.target("Abar", status="NOT_IMPLEMENTED", value=None, stmt=None,
                                    reason="planted", certificate_id=None)
    record("M38", "a constant the policy implements marked NOT_IMPLEMENTED (G8)",
           verifier="c11r_mutations.py", producer="c11r_runs.py",
           input_artifact="config/C11R_POLICY.json", mutated_path="$.targets.Abar.status",
           mutated_value="NOT_IMPLEMENTED", mutant_flagged=bool(dispositions_consistent(m, policy)),
           clean_flagged=bool(dispositions_consistent(base, policy)))

    # the comparator's and the equivalence checker's own self-tests, through their real code
    ks = K.self_test(stmt)
    es = EQ.self_test(stmt)

    bad = [r["id"] for r in RES if r["outcome"] != "DETECTED"]
    out = {"schema": "C11R_MUTATIONS/2",
           "supersedes": "C11R_MUTATIONS/1 (stale; REFUSE with M29 SURVIVED -- erratum E4)",
           "rules": ["run-artifact mutants use c11r_runs.assemble, the producer's own emission",
                     "each mutant: mutant flagged AND clean accepted AND unrelated not flagged",
                     "numerical mutants on the NON-TARGET block only",
                     "UNDETERMINED is never a pass"],
           "base_artifact_classes_on_synthetic_magnitudes": base_cls,
           "mutants": RES,
           "comparator_self_test": {"PASS": ks["PASS"], "cases": len(ks["cases"]),
                                    "used_real_magnitudes": ks["used_real_magnitudes"]},
           "equivalence_self_test": {"PASS": es["PASS"], "cases": len(es["cases"])},
           "not_detected": bad,
           "MUTATION_CLASS": "PASS" if not bad and ks["PASS"] and es["PASS"] else "REFUSE"}
    sh = C.write_evidence(C.NS / "evidence" / "mutations" / "C11R_MUTATIONS.json", out,
                          producer=__file__)
    for r in RES:
        print(f"  {r['outcome']:15s} {r['id']:5s} {r['name'][:78]}")
    print(f"\ncomparator self-test {ks['PASS']} ({len(ks['cases'])} cases); equivalence self-test "
          f"{es['PASS']} ({len(es['cases'])} cases)")
    print(f"MUTATION_CLASS = {out['MUTATION_CLASS']}   not detected: {bad}")
    print(f"wrote evidence/mutations/C11R_MUTATIONS.json sha256 {sh[:16]}...")
    return 0 if out["MUTATION_CLASS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
