"""Non-target validation of Theorem CV (certificate/verifier separation + two-sided sandwich).

DECLARED BEFORE ANY VERIFICATION RUN (rule, not similarity to a target):
  CUSUM part   drift block E = [3, 3 + 1/16], other-side point E' = {3}; six valid certificates found by the
               untrusted search (cv_search.py, certs/*.json); seven planted-invalid certificates built from them by
               the fixed rules P1-P7 below; BOTH verifiers (V_A exact-rational, V_B decimal) run on all 13.
               Pass iff: every valid certificate is ACCEPTED by both with IDENTICAL value strings, every planted one
               is REJECTED by both, and the float truth (mechanism Nystrom, Richardson) lies inside every certified
               sandwich interval.
  planted      P1 ARL_SUPER with f(a) below the ARL_SUB certified lower bound      (provably invalid, Theorem CV 2)
               P2 D_SUB with u(a) = 101/100 > 1 >= D                                 (provably invalid: D <= 1)
               P3 TABOO_SUPER with value_at_atom claim = f(a) - 1/1000               (claim tampering)
               P4 TABOO_SUPER with C_T_upper claim = f(a) - 1/1000 < sup f           (claim tampering)
               P5 ARL_SUPER shifted so that f(5) = -1/10 < 0                          (f >= 0 on R fails)
               P6 TABOO_SUB with f(a) above the TABOO_SUPER certified upper bound    (provably invalid)
               P7 D_SUPER with W(a) below the D_SUB certified lower bound             (provably invalid)
  refutation   claims X checked against certified [L, U]: an upper-bound constant X < L, or a lower-bound
               constant X > U, is REFUTED (Theorem CV part 3)
  synthetic    divided-difference lower bounds on sup|D'|, sup|D''| (Theorem CV part 2(b)) on exact finite-state
               drift families ov_fixtures.random_family(n=5, seed) for seeds 1..5, e in {0, 1/8, 1/4}, enclosure
               half-widths delta in {1e-9, 1e-3}; the bound must not exceed the exact sup over a 401-point grid; a
               planted D2 claim 0.9 x LB2 must be refuted.
R1 REPAIR (REVIEW_GLOBAL_INTEGRITY_R1 C-2, C-3, F5, F11), declared before the re-run:
  * the "refutation" list (C-2) and the "0.9 x LB2 refuted" count (C-3) were class (c)/(d): WITHDRAWN from the
    verdict (the refutation list is kept only as a labelled illustration);
  * NEW valid taboo-specific certificate TABOO_SUPER_T (Khat box LP at the point {3}; weight distinct from ARL_SUPER);
  * NEW planted P8 TABOO_SUPER_T scaled below the certified TABOO_SUB lower side (provably invalid: tau_a(3) >= L),
    P9 TABOO_SUB with C_T_lower claim = f(a) + 1/100 above the point maximum (C_T_lower rejection branch);
  * GATE: the upper Khat skip branch must fire (> 0 panels) in BOTH verifiers on TABOO_SUPER_T and the lower atom-union
    drop must fire on TABOO_SUB (instrumented counters);
  * REPORTED, not gated: TABOO_SUPER_T submitted with kind ARL_SUPER (a discrimination check, not provably invalid);
  * DD part (C-3 re-plant, class a): a planted INVALID enclosure u = d + 1/20 (claimed sub-solution) must be rejected
    by the exact sub-solution check in every family (guaranteed: u - Khat u - h1 = (1/20)(1 - Khat 1) > 0);
  * a Khat sub-solution search at {3} returned the ARL_SUB weight byte-for-byte (the atom drop does not bind there), so
    no distinct valid TABOO_SUB exists in this set; recorded, not counted.
Usage:  python3 -B cv_validate.py A | B | assemble
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[2]
sys.path.insert(0, str(NS / "code"))
sys.path.insert(0, str(HERE))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()
CERTS = HERE / "certs"
RUNS = HERE / "runs"
VALID = ("ARL_SUPER", "TABOO_SUPER", "D_SUB", "ARL_SUB", "TABOO_SUB", "D_SUPER", "TABOO_SUPER_T")
DISCRIM = ("X_TABOO_SUPER_T_as_ARL",)


def load_valid() -> dict:
    return {k: json.loads((CERTS / f"{k}.json").read_text()) for k in VALID}


def _scale(cert: dict, target_at_atom: Fr) -> dict:
    c = json.loads(json.dumps(cert))
    f0 = Fr(c["weight"]["0,0"])
    s = target_at_atom / f0
    c["weight"] = {k: str(Fr(v) * s) for k, v in c["weight"].items()}
    c["claims"]["value_at_atom"] = str(target_at_atom)
    return c


def planted(v: dict) -> dict:
    P = {}
    L_arl = Fr(v["ARL_SUB"]["claims"]["value_at_atom"])
    U_tab = Fr(v["TABOO_SUPER"]["claims"]["value_at_atom"])
    Dlo = Fr(v["D_SUB"]["claims"]["value_at_atom"])
    P["P1_ARL_SUPER_below_certified_lower"] = _scale(v["ARL_SUPER"], L_arl - Fr(1, 100))
    P["P2_D_SUB_above_one"] = _scale(v["D_SUB"], Fr(101, 100))
    c = json.loads(json.dumps(v["TABOO_SUPER"]))
    c["claims"]["value_at_atom"] = str(Fr(c["claims"]["value_at_atom"]) - Fr(1, 1000))
    P["P3_TABOO_SUPER_tampered_value"] = c
    c = json.loads(json.dumps(v["TABOO_SUPER"]))
    c["claims"]["C_T_upper"] = str(Fr(c["weight"]["0,0"]) - Fr(1, 1000))
    P["P4_TABOO_SUPER_C_T_claim_low"] = c
    c = json.loads(json.dumps(v["ARL_SUPER"]))
    f5 = sum(Fr(val) * Fr(5) ** int(k.split(",")[1]) for k, val in c["weight"].items())
    shift = f5 + Fr(1, 10)
    c["weight"]["0,0"] = str(Fr(c["weight"]["0,0"]) - shift)
    c["claims"]["value_at_atom"] = c["weight"]["0,0"]
    P["P5_ARL_SUPER_negative_on_R"] = c
    P["P6_TABOO_SUB_above_certified_upper"] = _scale(v["TABOO_SUB"], U_tab + Fr(1, 100))
    P["P7_D_SUPER_below_certified_lower"] = _scale(v["D_SUPER"], Dlo - Fr(1, 100))
    L_tau_pt = Fr(v["TABOO_SUB"]["claims"]["value_at_atom"])          # certified at the point {3}
    P["P8_TABOO_SUPER_T_below_certified_lower"] = _scale(v["TABOO_SUPER_T"], L_tau_pt - Fr(1, 100))
    for k, c in P.items():
        if "C_T_lower" in c.get("claims", {}):
            c["claims"]["C_T_lower"] = c["claims"]["value_at_atom"]
        if "C_T_upper" in c.get("claims", {}) and k != "P4_TABOO_SUPER_C_T_claim_low":
            c["claims"]["C_T_upper"] = str(max(Fr(c["claims"]["C_T_upper"]), Fr(c["claims"]["value_at_atom"])))
    c = json.loads(json.dumps(v["TABOO_SUB"]))
    c["claims"]["C_T_lower"] = str(Fr(c["claims"]["value_at_atom"]) + Fr(1, 100))   # above the point maximum f(a)
    P["P9_TABOO_SUB_C_T_lower_claim_high"] = c
    return P


def discrim(v: dict) -> dict:
    c = json.loads(json.dumps(v["TABOO_SUPER_T"]))
    c["kind"] = "ARL_SUPER"
    c["claims"].pop("C_T_upper", None)
    return {"X_TABOO_SUPER_T_as_ARL": c}


def run(which: str) -> None:
    mod = __import__("cv_verify_a" if which == "A" else "cv_verify_b")
    v = load_valid()
    P = planted(v)
    (CERTS / "planted").mkdir(exist_ok=True)
    for k, c in P.items():
        (CERTS / "planted" / f"{k}.json").write_text(json.dumps(c, indent=1, sort_keys=True) + "\n")
    RUNS.mkdir(exist_ok=True)
    res = {}
    for name, cert in list(v.items()) + list(P.items()) + list(discrim(v).items()):
        t0 = time.time()
        r = mod.verify(cert)
        r["seconds"] = time.time() - t0
        res[name] = r
        print(which, name, r["accepted"], r["reasons"], "%.1fs" % r["seconds"], flush=True)
        (RUNS / f"V_{which}.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    Q.log_execution(f"streams/A_306/common/cv_validate.py {which}",
                    f"Theorem CV verifier V_{which} on 6 valid + 7 planted certificates, drift block [3, 49/16]",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION", notes="rigorous verification, non-target")


# ------------------------------------------------------------------------------------------ synthetic DD part
def dd_synthetic() -> dict:
    import ov_fixtures as X
    out, fails = [], []
    for seed in range(1, 6):
        fam = X.random_family(5, seed)
        n = fam.n
        # Khat: column 0 (the atom) removed; source h1 = 1 - row sums of K (both polynomial in e)
        khp = [[([Fr(0)] if j == 0 else p) for j, p in enumerate(row)] for row in fam.kp]
        deg = max(len(p) for row in fam.kp for p in row)
        h1p = []
        for row in fam.kp:
            c = [Fr(0)] * deg
            for p in row:
                for t, a in enumerate(p):
                    c[t] -= a
            c[0] += 1
            h1p.append(c)
        dfam = X.DriftFamily(khp, h1p, (fam.e_lo, fam.e_hi))
        es = [Fr(0), Fr(1, 8), Fr(1, 4)]
        Dv = [dfam.F_derivs(e, 0)[0][0] for e in es]
        grid = [Fr(k, 1600) for k in range(401)]
        sup1 = max(abs(dfam.F_derivs(e, 1)[1][0]) for e in grid)
        sup2 = max(abs(dfam.F_derivs(e, 2)[2][0]) for e in grid)
        for delta in (Fr(1, 10 ** 9), Fr(1, 1000)):
            # certified enclosures: u = d - delta*1 is a sub-solution and W = d + delta*1 a supersolution exactly
            # (u - Khat u - h1 = -delta (1 - Khat 1) <= 0); checked, not assumed:
            ok_cert = True
            for e in es:
                d = dfam.F_derivs(e, 0)[0]
                Kh = dfam.K(e)
                h = dfam.S(e)
                for sgn in (-1, 1):
                    f = [x + sgn * delta for x in d]
                    Kf = [sum(a * b for a, b in zip(r, f)) for r in Kh]
                    res = [f[i] - Kf[i] - h[i] for i in range(n)]
                    if (sgn < 0 and max(res) > 0) or (sgn > 0 and min(res) < 0):
                        ok_cert = False
            # planted INVALID enclosure (class a): u = d + 1/20 claimed as a sub-solution at e = 1/8
            e_p = Fr(1, 8)
            d_p = dfam.F_derivs(e_p, 0)[0]
            Kh_p, h_p = dfam.K(e_p), dfam.S(e_p)
            u_p = [x + Fr(1, 20) for x in d_p]
            Ku_p = [sum(a * b for a, b in zip(r, u_p)) for r in Kh_p]
            planted_rejected = max(u_p[i] - Ku_p[i] - h_p[i] for i in range(n)) > 0
            lo = [x - delta for x in Dv]
            hi = [x + delta for x in Dv]
            hstep = Fr(1, 8)
            lb1 = max(max(Fr(0), max(lo[j] - hi[i], lo[i] - hi[j])) / (es[j] - es[i])
                      for i in range(3) for j in range(i + 1, 3))
            s2lo, s2hi = lo[0] - 2 * hi[1] + lo[2], hi[0] - 2 * lo[1] + hi[2]
            lb2 = (s2lo if s2lo > 0 else (-s2hi if s2hi < 0 else Fr(0))) / hstep ** 2
            rec = {"seed": seed, "delta": str(delta), "certificates_valid": ok_cert,
                   "LB1": float(lb1), "sup_grid_D1": float(sup1), "LB2": float(lb2), "sup_grid_D2": float(sup2),
                   "LB1_le_sup": lb1 <= sup1, "LB2_le_sup": lb2 <= sup2,
                   "planted_invalid_enclosure_rejected": planted_rejected,
                   "LB2_nonvacuous": lb2 > 0}
            if not (ok_cert and rec["LB1_le_sup"] and rec["LB2_le_sup"] and planted_rejected):
                fails.append(rec)
            out.append(rec)
    return {"records": out, "failures": fails,
            "planted_invalid_enclosures_rejected": sum(1 for r in out if r["planted_invalid_enclosure_rejected"]),
            "nonvacuous_LB2": sum(1 for r in out if r["LB2_nonvacuous"]),
            "vacuous_bounds": sum(1 for r in out if r["LB2"] == 0.0),
            "withdrawn": "planted_D2_claim_0.9LB2_refuted (class c, reduced to LB2 > 0)",
            "pass": not fails and all(r["planted_invalid_enclosure_rejected"] for r in out)}


def assemble() -> dict:
    A = json.loads((RUNS / "V_A.json").read_text())
    B = json.loads((RUNS / "V_B.json").read_text())
    v = load_valid()
    names_valid = list(VALID)
    names_pl = [k for k in A if k not in VALID and k not in DISCRIM]
    agree = {k: {"A": A[k]["accepted"], "B": B[k]["accepted"], "same_value": A[k]["value_at_atom"] == B[k]["value_at_atom"]}
             for k in A}
    valid_ok = all(A[k]["accepted"] and B[k]["accepted"] and A[k]["value_at_atom"] == B[k]["value_at_atom"]
                   for k in names_valid)
    planted_ok = all((not A[k]["accepted"]) and (not B[k]["accepted"]) for k in names_pl)
    # sandwich (certified), with the trivial facts D <= 1, tau_a >= 1, E_a[tau] >= 1
    L_arl, U_arl = Fr(v["ARL_SUB"]["claims"]["value_at_atom"]), Fr(v["ARL_SUPER"]["claims"]["value_at_atom"])
    L_tau, U_tau = Fr(v["TABOO_SUB"]["claims"]["value_at_atom"]), Fr(v["TABOO_SUPER"]["claims"]["value_at_atom"])
    L_ct, U_ct = Fr(v["TABOO_SUB"]["claims"]["C_T_lower"]), Fr(v["TABOO_SUPER"]["claims"]["C_T_upper"])
    L_d, U_d = Fr(v["D_SUB"]["claims"]["value_at_atom"]), min(Fr(v["D_SUPER"]["claims"]["value_at_atom"]), Fr(1))
    mech = json.loads((NS / "validation" / "A306_MECHANISM.json").read_text())
    tr = mech["per_drift"]["3"]["truth"]["richardson"]
    unc = mech["per_drift"]["3"]["truth"]["richardson_uncertainty"]
    blk = mech["per_drift"]["3"]["blocks"]["1/16"]
    sand = {
        "Abar* = sup_E E_a[tau]": {"L": float(L_arl), "U": float(U_arl), "truth_float": tr["v_a"], "unc": unc["v_a"]},
        "tau* = sup_E tau_a": {"L": float(L_tau), "U": float(U_tau), "truth_float": blk["truth_sup_t_a"], "unc": unc["t_a"]},
        "C* = sup_E ||Ghat_e||": {"L": float(L_ct), "U": float(U_ct), "truth_float": blk["truth_sup_sup_t"], "unc": unc["sup_t"]},
        "D* = inf_E D_e": {"L": float(L_d), "U": float(U_d), "truth_float": blk["truth_inf_D"], "unc": unc["D"]},
    }
    for s in sand.values():
        s["truth_inside"] = s["L"] - s["unc"] <= s["truth_float"] <= s["U"] + s["unc"]
        s["relative_width"] = (s["U"] - s["L"]) / s["truth_float"]
    # tau_a at the POINT {3}: taboo-specific upper side TABOO_SUPER_T, lower side TABOO_SUB (both at {3})
    U_tau_pt = Fr(v["TABOO_SUPER_T"]["claims"]["value_at_atom"])
    sand["tau_a(3) (point)"] = {"L": float(L_tau), "U": float(U_tau_pt), "truth_float": tr["t_a"], "unc": unc["t_a"]}
    for s_ in sand.values():
        s_["truth_inside"] = s_["L"] - s_["unc"] <= s_["truth_float"] <= s_["U"] + s_["unc"]
        s_["relative_width"] = (s_["U"] - s_["L"]) / s_["truth_float"]
    D_SUPER_vacuous = Fr(v["D_SUPER"]["claims"]["value_at_atom"]) > 1
    branch = {nm: {"V_A": A[nm]["khat_branch_counts"], "V_B": B[nm]["khat_branch_counts"]}
              for nm in ("TABOO_SUPER_T", "TABOO_SUB", "TABOO_SUPER")}
    branch_ok = (A["TABOO_SUPER_T"]["khat_branch_counts"]["upper_skips"] > 0
                 and B["TABOO_SUPER_T"]["khat_branch_counts"]["upper_skips"] > 0
                 and A["TABOO_SUB"]["khat_branch_counts"]["lower_drops"] > 0
                 and B["TABOO_SUB"]["khat_branch_counts"]["lower_drops"] > 0)
    distinct = v["TABOO_SUPER_T"]["weight"] != v["ARL_SUPER"]["weight"]
    disc = {k: {"A": A[k]["accepted"], "B": B[k]["accepted"]} for k in DISCRIM}
    # ILLUSTRATION ONLY (class c/d per REVIEW_GLOBAL_INTEGRITY_R1 C-2): not a control, not in the verdict
    refute = [
        {"claim": "Abar = L - 1/100 (upper-bound constant)", "refuted": L_arl - Fr(1, 100) < L_arl},
        {"claim": "Abar = U + 1/2", "refuted": U_arl + Fr(1, 2) < L_arl},
        {"claim": "D_lo = 1001/1000 (lower-bound constant)", "refuted": Fr(1001, 1000) > U_d},
        {"claim": "D_lo = L_d", "refuted": L_d > U_d},
    ]
    refute_ok = [r["refuted"] for r in refute] == [True, False, True, False]
    # bit-identity of the memoised sqrt(2 pi) in V_A
    import cv_verify_a as VA
    G = VA.G
    fresh = G.sqrt_two_pi.__wrapped__()
    memo = G.sqrt_two_pi()
    memo_ok = fresh.lo == memo.lo and fresh.hi == memo.hi
    dd = dd_synthetic()
    out = {"schema": "A306_CV_VALIDATION/1", "label": "NON-TARGET; rigorous verifiers V_A, V_B; float truth reference",
           "drift_block": ["3", "49/16"], "other_side_point": "3",
           "per_certificate": agree, "V_A": A, "V_B": B,
           "valid_all_accepted_by_both_with_identical_values": valid_ok,
           "planted_all_rejected_by_both": planted_ok,
           "sandwich": sand, "sandwich_all_contain_truth": all(s["truth_inside"] for s in sand.values()),
           "refutation_illustration_not_a_control": refute, "refutation_pattern_illustration": refute_ok,
           "taboo_branch_counts": branch, "taboo_branches_fired_in_both": branch_ok,
           "TABOO_SUPER_T_weight_distinct_from_ARL_SUPER": distinct,
           "discrimination_reported_not_gated": disc,
           "D_SUPER_vacuous_value_gt_1": D_SUPER_vacuous,
           "V_A_sqrt2pi_memo_bit_identical": memo_ok, "divided_difference_synthetic": dd,
           "coverage": {"certificates": len(A), "valid": len(names_valid), "planted": len(names_pl),
                        "boxes_per_certificate": A["ARL_SUPER"]["boxes"], "panels": 32,
                        "synthetic_families": 5, "synthetic_records": len(dd["records"])}}
    out["verdict"] = "PASS" if (valid_ok and planted_ok and out["sandwich_all_contain_truth"] and branch_ok
                                and distinct and memo_ok and dd["pass"]) else "FAIL"
    (NS / "validation" / "A306_CV_VALIDATION.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    Q.log_execution("streams/A_306/common/cv_validate.py assemble",
                    "Theorem CV: agreement of V_A/V_B, planted rejections, sandwich vs truth, synthetic DD bounds",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION", notes="non-target; synthetic fixtures")
    return out


if __name__ == "__main__":
    if sys.argv[1] in ("A", "B"):
        run(sys.argv[1])
    else:
        o = assemble()
        print(json.dumps({k: o[k] for k in ("verdict", "per_certificate", "taboo_branch_counts",
                                            "discrimination_reported_not_gated", "D_SUPER_vacuous_value_gt_1",
                                            "V_A_sqrt2pi_memo_bit_identical")}, indent=1))
        dd = o["divided_difference_synthetic"]
        print("DD:", dd["pass"], "planted enclosures rejected", dd["planted_invalid_enclosures_rejected"],
              "nonvacuous", dd["nonvacuous_LB2"], "vacuous", dd["vacuous_bounds"])
