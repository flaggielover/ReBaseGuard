"""Campaign C2, Phase D1: decompose the K5-B failure margin of tail cells 305-309 into its load-bearing certified
terms, and rank the dominant blockers. Diagnosis only - it proposes nothing and closes nothing.

Runs on committed evidence with stdlib Python alone (no python-flint, no remote host, no K1 record store), so a
reviewer or an adjudicator can re-run it. Inputs: Campaign B's measurement records and ADOPTED_TAIL_INPUTS.json,
Campaign C1's certified operator registry, and the frozen cover.

The theorem-TC-T radius of object r is

    rad_r = A0*p2 + 2*A1*p1 + A2*p0
    p2 = f_H + rho*f_G + rho^2*Env4/2
    p1 = f_D + rho*f_H + rho^2*f_G/2 + rho^3*Env4/6
    p0 = f_F + rho*f_D + rho^2*f_H/2 + rho^3*f_G/6 + rho^4*Env4/24

so it expands into twelve terms, which this tool reports individually and regroups by what a successor could
actually attack: the order-3 residual f_G, the (P3) envelope Env4, the order-2 residual f_H, and the rest.

    python3 -B c2_d1_blocker.py --out OUT.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import types
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = REPO / "level4/closure_proofs"
B_NS = CP / "p5y_k5_m5_tail_closure"
C1_NS = CP / "p5y_k5_tail_operator_registry"
AD_NS = CP / "p5y_k5_perron_deflated_resolvent"
TAIL = (305, 306, 307, 308, 309)
K1_BOUND = F(7978846, 10 ** 7)
K2_BOUND = F(9678830, 10 ** 7)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load(path: Path, name: str):
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)
    return mod


def rat(p) -> F:
    return F(p) if isinstance(p, str) else F(p[0]) + F(p[1])


class PremiseRefusal(Exception):
    """Lemma Dv' was asked for constants outside its own hypotheses."""


def atom_dv_prime(Abar, tau, C, Dlo, D1, D2) -> dict:
    # The pinned consumer `deflated_consume.atom_constants_r2` validates these premises and refuses an
    # inadmissible tuple; this local copy did not, and so would happily return constants for one. Pre-freeze
    # review r2 (notes 65/66) found the gap: the C_T row of the sensitivity table below perturbs C_T alone, and on
    # cells 307-309 a 10 % improvement drives C_T under tau, which is outside Lemma Dv'.
    # This guard enforces the four premise inequalities ONLY. It is deliberately NOT a claim of equivalence with
    # the pinned consumer, which additionally type-checks every input (non-Fraction or negative is refused) and
    # post-checks that no r2 constant exceeds its r1 counterpart. An earlier version of this comment said "the
    # guard is added so the two agree", which overclaimed; withdrawn on pre-freeze review r4.
    if not (Dlo > 0 and tau >= 1 and C >= tau and Abar >= 1):
        raise PremiseRefusal("constants violate tau >= 1, C >= tau, Dlo > 0, Abar >= 1")
    eff = Abar if Abar < tau / Dlo else tau / Dlo
    d1, d2 = D1 / Dlo, D2 / Dlo
    return {"A0": eff, "A1": eff * (K1_BOUND * C + d1),
            "A2": eff * (2 * K1_BOUND ** 2 * C ** 2 + K2_BOUND * C + 2 * K1_BOUND * C * d1 + 2 * d1 ** 2 + d2)}


def world():
    cover = {c["index"]: c for c in json.loads((CP / "p5y_k1_cover_ledger_successor/config/cells.json").read_bytes())
             if c["detector"] == "CUSUM"}
    reg = json.loads((C1_NS / "evidence/registry_c1/REGISTRY_C1.json").read_bytes())
    blocks = {b["cell"]: b for b in reg["blocks"]}
    adopted = json.loads((B_NS / "evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json").read_bytes())["cells"]
    meas = {k: json.loads((B_NS / f"evidence/measurement_r1/TCT_INPUTS_{k}.json").read_bytes()) for k in TAIL}
    return cover, blocks, adopted, meas


def direct_test(T, R, meas, aux, A, ad, cov):
    """(magnitude, M_after, Gamma, passes) for m = 5 under atom constants A."""
    lo, hi, obj = T.tail_enclosure(R, meas, aux, A, 5, None)
    H = (F(ad["R2_interval"]["lo"]), F(ad["R2_interval"]["hi"]))
    M0 = F(ad["M_R2"])
    a, b = max(H[0], lo), min(H[1], hi)
    M = M0 if a > b else min(M0, max(abs(a), abs(b)))
    e0, rho, x_hi = (rat(cov[t]) for t in ("e0", "rho", "right"))
    Gam = (F(ad["R_interval"]["hi"]) - e0 * F(ad["D_interval"]["lo"])) + rho * x_hi * M
    return max(abs(lo), abs(hi)), M, Gam, Gam < 0, obj


def requirement(T, R, meas, aux, A, ad, cov) -> F:
    """The uniform atom-constant reduction factor still required, by exact bisection (1 if it already passes)."""
    if direct_test(T, R, meas, aux, A, ad, cov)[3]:
        return F(1)
    lo_s, hi_s = F(1, 1000), F(1)
    if not direct_test(T, R, meas, aux, {j: A[j] * lo_s for j in A}, ad, cov)[3]:
        return None
    for _ in range(50):
        mid = (lo_s + hi_s) / 2
        if direct_test(T, R, meas, aux, {j: A[j] * mid for j in A}, ad, cov)[3]:
            lo_s = mid
        else:
            hi_s = mid
    return 1 / lo_s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cover, blocks, adopted, meas = world()
    T = load(B_NS / "code/tct_rule.py", "tct_rule")
    R = T.load_frozen("tc_rule", T.FROZEN["tc_rule"][1])
    out = {"schema": "rebaseguard.p5y.k5.tail-c2.d1-blocker.v1",
           "note": "diagnosis only; proposes nothing and closes nothing", "cells": {}}

    for k in TAIL:
        m, aux, ad, cov = meas[k], adopted[str(k)]["auxiliary_evidence"], adopted[str(k)]["m"]["5"], cover[k]
        b = blocks[k]
        op = {x: F(b[x]) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2")}
        A = atom_dv_prime(**{"Abar": op["Abar"], "tau": op["tau"], "C": op["C_T"],
                             "Dlo": op["D_lo"], "D1": op["D1"], "D2": op["D2"]})
        rho = F(m["rho"])
        kn = {i: F(m["norms"]["k"][i]) for i in range(5)}
        C_upper = rat(cov["C_upper"])
        mag, M, Gam, ok, obj = direct_test(T, R, m, aux, A, ad, cov)
        req = requirement(T, R, m, aux, A, ad, cov)

        # --- the twelve terms of the radius, per object, then averaged with the assembly weight 1/5
        terms = {n: F(0) for n in ("A0_fH", "A0_rho_fG", "A0_rho2_Env4", "A1_fD", "A1_rho_fH", "A1_rho2_fG",
                                   "A1_rho3_Env4", "A2_fF", "A2_rho_fD", "A2_rho2_fH", "A2_rho3_fG", "A2_rho4_Env4")}
        sub = {n: F(0) for n in ("fG_sigma3", "fG_candidate_sups", "fG_eps_src3", "Env4_sigma4", "Env4_cand")}
        rad_total = F(0)
        for r in range(5):
            o, q = m["r"][str(r)], obj[r]
            fF = F(o["delta_F"]) + F(o["eps_src"][0])
            fD = F(o["delta_D"]) + F(o["eps_src"][1])
            fH = F(o["delta_H"]) + F(o["eps_src"][2])
            fG, e4 = q["f_G"], q["env4"]
            sF, sD, sH = (F(o["sup"][x]) for x in ("F", "D", "H"))
            w = F(1, 5)
            terms["A0_fH"] += w * A["A0"] * fH
            terms["A0_rho_fG"] += w * A["A0"] * rho * fG
            terms["A0_rho2_Env4"] += w * A["A0"] * rho ** 2 * e4 / 2
            terms["A1_fD"] += w * 2 * A["A1"] * fD
            terms["A1_rho_fH"] += w * 2 * A["A1"] * rho * fH
            terms["A1_rho2_fG"] += w * 2 * A["A1"] * rho ** 2 * fG / 2
            terms["A1_rho3_Env4"] += w * 2 * A["A1"] * rho ** 3 * e4 / 6
            terms["A2_fF"] += w * A["A2"] * fF
            terms["A2_rho_fD"] += w * A["A2"] * rho * fD
            terms["A2_rho2_fH"] += w * A["A2"] * rho ** 2 * fH / 2
            terms["A2_rho3_fG"] += w * A["A2"] * rho ** 3 * fG / 6
            terms["A2_rho4_Env4"] += w * A["A2"] * rho ** 4 * e4 / 24
            rad_total += w * q["rad"]
            # what is inside f_G and Env4
            sub["fG_sigma3"] += w * q["sigma3"]
            sub["fG_candidate_sups"] += w * (3 * kn[1] * sH + 3 * kn[2] * sD + kn[3] * sF)
            sub["fG_eps_src3"] += w * F(o["eps_src"][3])
            sub["Env4_sigma4"] += w * q["sigma4"]
            sub["Env4_cand"] += w * (e4 - q["sigma4"])

        tot = sum(terms.values())
        grouped = {
            "order3_residual_fG": terms["A0_rho_fG"] + terms["A1_rho2_fG"] + terms["A2_rho3_fG"],
            "P3_envelope_Env4": terms["A0_rho2_Env4"] + terms["A1_rho3_Env4"] + terms["A2_rho4_Env4"],
            "order2_residual_fH": terms["A0_fH"] + terms["A1_rho_fH"] + terms["A2_rho2_fH"],
            "order1_residual_fD": terms["A1_fD"] + terms["A2_rho_fD"],
            "order0_residual_fF": terms["A2_fF"]}

        # --- sensitivity: the magnitude after a 10 % improvement in each certified operator input, one at a time
        sens = {}
        for name, better in (("D_lo", {"D_lo": op["D_lo"] * F(11, 10)}), ("D2", {"D2": op["D2"] * F(10, 11)}),
                             ("D1", {"D1": op["D1"] * F(10, 11)}), ("C_T", {"C_T": op["C_T"] * F(10, 11)}),
                             ("tau", {"tau": op["tau"] * F(10, 11)})):
            p, clamped = dict(op) | better, None
            if name == "D_lo" and p["D_lo"] > 1:
                p["D_lo"] = F(1)                     # D is a probability; it cannot exceed 1
                clamped = "D_lo capped at 1"
            if name == "C_T" and p["C_T"] < p["tau"]:
                # Lemma Dv' needs C >= tau, so a full 10 % improvement in C_T alone is simply NOT AVAILABLE on
                # this cell. The admissible best is C_T = tau, and that is what is reported. Reporting the
                # unclamped number would be an extrapolation outside the lemma's hypotheses -- which is what the
                # first published version of this table did on cells 307, 308 and 309.
                clamped = (f"a 10 % improvement is inadmissible here (C_T/1.1 = {float(p['C_T']):.6f} < tau = "
                           f"{float(p['tau']):.6f}); reported at the admissible best C_T = tau")
                p["C_T"] = p["tau"]
            A2_ = atom_dv_prime(Abar=p["Abar"], tau=p["tau"], C=p["C_T"], Dlo=p["D_lo"], D1=p["D1"], D2=p["D2"])
            mg = direct_test(T, R, m, aux, A2_, ad, cov)[0]
            # The fraction of the input actually moved. Nominally 1 - 1/1.1 = 9.0909 % for an upper bound and
            # 10 % for D_lo, but LESS wherever a clamp bound the perturbation -- so a clamped row is not a
            # like-for-like "10 % improvement" and must not be read against the unclamped columns as though it
            # were. Added on pre-freeze review r3, which pointed out that without it the C_T column silently
            # compares different-sized perturbations.
            eff = abs(p[name] - op[name]) / op[name]
            sens[name] = {"magnitude": float(mg), "delta_vs_base": float(mg - mag),
                          "relative_gain": float((mag - mg) / mag),
                          "effective_improvement": float(eff)}
            if name == "C_T":
                # Emitted for C_T ONLY, and this restriction is load-bearing. Per-unit normalisation is valid
                # for comparing the SAME input across cells -- which is the headroom question it exists to
                # answer, since the clamp gives 307/308/309 a smaller window than 305/306. It is INVALID across
                # different inputs: the div-1.1 convention is chosen so that both D_lo * 1.1 and tau / 1.1
                # divide A0 = tau/D_lo by exactly 1.1, which is precisely why their input fractions differ
                # (10 % against 9.0909 %). Dividing each gain by its own input fraction therefore discards the
                # symmetry the convention was chosen for, and inflates tau by 1.1 relative to D_lo -- enough to
                # REVERSE the D_lo > tau ordering on all five cells, which is the finding section 2 rests on.
                # An earlier version emitted this field on all five operator rows and did exactly that, in the
                # machine-readable artifact, uncaveated. Found by pre-freeze review r4.
                sens[name]["gain_per_unit_of_input_moved"] = float((mag - mg) / mag / eff) if eff else None
                sens[name]["per_unit_comparability"] = (
                    "same input across cells only; NOT comparable across different inputs, because the div-1.1 "
                    "convention equalises the effect on A0 = tau/D_lo rather than the input fraction")
            if clamped:
                sens[name]["admissibility_clamp"] = clamped
        for name, A_ in (("A0", {**A, "A0": A["A0"] * F(10, 11)}), ("A1", {**A, "A1": A["A1"] * F(10, 11)}),
                         ("A2", {**A, "A2": A["A2"] * F(10, 11)}),
                         ("A_all", {j: A[j] * F(10, 11) for j in A})):
            mg = direct_test(T, R, m, aux, A_, ad, cov)[0]
            sens[name] = {"magnitude": float(mg), "delta_vs_base": float(mg - mag),
                          "relative_gain": float((mag - mg) / mag)}
        # rho and C_upper are frozen cover facts, reported for completeness as elasticities of the enclosure
        sens["rho_frozen"] = {"value": float(rho), "note": "frozen cover geometry; not a C2 lever"}
        sens["C_upper_frozen"] = {"value": float(C_upper),
                                  "note": "frozen K1 block bound; feeds the Lemma G supply only"}

        # --- the R-stage attribution test, exactly as the gate pre-registers it
        floor = {}
        for r in range(5):
            o = dict(m["r"][str(r)])
            floor[str(r)] = o
        m_floor = dict(m, r={str(r): dict(m["r"][str(r)]) for r in range(5)})
        magf, Mf, Gamf, okf, _ = direct_test(T, R, m_floor, aux, A, ad, cov)
        # f_G is built inside tail_object from the measured sups and sigma3; the floor is reached by zeroing the
        # candidate-sup part and sigma3, leaving only eps_src[3] - done through a zero-candidate supply
        zero = {str(r): {"sup_G": "0", "abs_G_at_a": "0", "delta_G": "0",
                         "sup_F": m["r"][str(r)]["sup"]["F"], "sup_D": m["r"][str(r)]["sup"]["D"],
                         "sup_H": m["r"][str(r)]["sup"]["H"]} for r in range(5)}
        lo_f, hi_f, _ = T.tail_enclosure(R, m, aux, A, 5, zero)
        H = (F(ad["R2_interval"]["lo"]), F(ad["R2_interval"]["hi"]))
        M0 = F(ad["M_R2"])
        a_, b_ = max(H[0], lo_f), min(H[1], hi_f)
        Mfl = M0 if a_ > b_ else min(M0, max(abs(a_), abs(b_)))
        e0, rho_, x_hi = (rat(cov[t]) for t in ("e0", "rho", "right"))
        Gamfl = (F(ad["R_interval"]["hi"]) - e0 * F(ad["D_interval"]["lo"])) + rho_ * x_hi * Mfl
        out["cells"][str(k)] = {
            "closes_under_C1_constants": bool(ok),
            "magnitude": float(mag), "M_after": float(M), "M_needed": float(-(F(ad["R_interval"]["hi"])
                                                                              - e0 * F(ad["D_interval"]["lo"]))
                                                                            / (rho_ * x_hi)),
            "Gamma": float(Gam), "required_uniform_atom_constant_reduction": (float(req) if req else None),
            "gap_above_1": (float(req - 1) if req else None),
            "operator_constants": {x: float(op[x]) for x in op},
            "atom_constants": {j: float(A[j]) for j in A},
            "radius_mean_over_r": float(rad_total),
            "radius_terms": {n: {"value": float(v), "share": float(v / tot)} for n, v in terms.items()},
            "radius_grouped": {n: {"value": float(v), "share": float(v / tot)} for n, v in grouped.items()},
            "inside_fG": {n: float(v) for n, v in sub.items() if n.startswith("fG")},
            "inside_Env4": {n: float(v) for n, v in sub.items() if n.startswith("Env4")},
            "sensitivity_10pct_improvement": sens,
            "order3_attribution": {"magnitude_with_perfect_order3": float(max(abs(lo_f), abs(hi_f))),
                                   "M_after": float(Mfl), "Gamma": float(Gamfl), "closes": bool(Gamfl < 0)},
        }
        ranked = sorted(grouped.items(), key=lambda kv: -kv[1])
        out["cells"][str(k)]["DOMINANT_BLOCKER_1"] = {"term": ranked[0][0], "share": float(ranked[0][1] / tot)}
        out["cells"][str(k)]["DOMINANT_BLOCKER_2"] = {"term": ranked[1][0], "share": float(ranked[1][1] / tot)}
        out["cells"][str(k)]["DOMINANT_BLOCKER_3"] = {"term": ranked[2][0], "share": float(ranked[2][1] / tot)}

    data = json.dumps(out, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print(json.dumps({k: {"closes": v["closes_under_C1_constants"],
                          "req": v["required_uniform_atom_constant_reduction"],
                          "B1": v["DOMINANT_BLOCKER_1"], "B2": v["DOMINANT_BLOCKER_2"],
                          "order3_would_close": v["order3_attribution"]["closes"]}
                      for k, v in out["cells"].items()}, indent=1))
    print("sha256", sha(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
