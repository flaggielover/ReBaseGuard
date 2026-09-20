"""Critical order-3 candidate ratio s_G/s_H per tail cell, under any named atom-constant supply.

WHY THIS FILE EXISTS. Campaign C2 published critical ratios in
`evidence/phase_d5/C2_ROBUSTNESS_AND_R_ATTRIBUTION.json` and quoted them in `phase_r/R_STAGE_DESIGN.md` and
`phase_d/D_STAGE_DECISION.md`, but the script that produced them was an uncommitted scratch file. The pre-freeze
review reproduced the numbers independently and, doing so, found that the column those documents labelled "under C1
constants" is not C1 at all: it is Campaign B's Lemma-G column. This module is the committed producer. It computes
the ratio under every supply BY NAME, so the labels cannot drift again, and it REFUSES unless it reproduces two
independently published anchors bit-exactly:

  * the Lemma-G column must equal Campaign B's `TAIL_FORECAST_R2.critical_sup_G_over_sup_H_ratio`;
  * the C2 column must equal C2's own published `critical_sG_over_sH`.

Those two anchors are what license the C1 column, which nothing else in the programme has ever computed.

Everything read here is committed evidence: no K1 record store, no compute host, no new real scientific address, no
order-3 field of any measurement. It runs from a fresh clone on any machine with stdlib Python.

    python3 -B c2_critical_ratio.py --out OUT.json
"""
import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
CP = HERE.parents[4] / "level4/closure_proofs"
B_NS = CP / "p5y_k5_m5_tail_closure"
C1_NS = CP / "p5y_k5_tail_operator_registry"
LF_NS = CP / "p5y_k5_lower_front_order3"
TAIL = (305, 306, 307, 308, 309)

# The two published anchors this module must reproduce before any of its own output is trusted.
B_FORECAST = B_NS / "evidence/forecast_r2/TAIL_FORECAST_R2.json"
C2_AUX = NS / "evidence/phase_d5/C2_ROBUSTNESS_AND_R_ATTRIBUTION.json"


def lower_front_model(fc) -> tuple[dict, int]:
    """The adopted Campaign-A order-3 evidence model, per Taylor index r.

    For each r SEPARATELY, the worst (largest) value observed across the adopted lower-front cells of
      * ag = |Ghat(a)| / sup_G  -- the centre-motion fraction, whose adopted max is the 0.681 the design quotes,
      * dg = delta_G            -- the certified order-3 residual,
      * gh = sup_G / sup_H      -- the ratio itself. Its adopted spread, reported separately, is the min-to-max
                                   over every (cell, r) pair, NOT a per-r maximum; that is the 34.8-80.5 range the
                                   R-stage design compares against.
    'Per-r worst', not 'worst over all r': each r keeps its own maximum. One maximum across all r is a different,
    slightly more pessimistic model that reproduces neither published anchor.
    """
    acc = {r: {"ag": [], "dg": [], "gh": []} for r in range(5)}
    paths = sorted(LF_NS.glob("evidence/tc_r1/cells/TC_CELL_*.json"))
    if not paths:
        raise SystemExit("adopted lower-front order-3 evidence not found")
    for p in paths:
        d = json.loads(p.read_bytes())
        for r in range(5):
            o = d["r"][str(r)]
            g, h = F(o["sup"]["G"]), F(o["sup"]["H"])
            acc[r]["gh"].append(g / h)
            acc[r]["ag"].append(F(o["abs_G_at_a"]) / g)
            acc[r]["dg"].append(F(o["delta_G"]))
    flat = [x for r in range(5) for x in acc[r]["gh"]]
    return ({r: {n + "_max": max(v) for n, v in acc[r].items()} for r in range(5)}, len(paths),
            (min(flat), max(flat)))


def gamma_with(T, R, meas, aux, A, ad, cov, KM, order3) -> F:
    """The frozen K5-B direct clause Gamma, evaluated with a PROPOSED order-3 candidate.

    Same form as `c2_d5_forecast.direct`, which this module reuses verbatim for every order-3-free number. It is
    written out separately because `direct` pins order3 = None, and that is not merely a default: with no candidate
    proposed, theorem TC-T bounds the whole order-3 term by the (P2') source quantity 3k1*s_H + 3k2*s_D + k3*s_F +
    sigma3. A proposed candidate replaces that with its own certified residual delta_G. The two therefore do NOT
    agree in the limit ratio -> 0 -- a zero-supremum candidate still carries delta_G -- and an earlier draft of this
    module asserted that they did. They are tied to published anchors in `main` instead.
    """
    lo, hi, _ = T.tail_enclosure(R, meas, aux, A, 5, order3)
    if (lo, hi) != T.tail_enclosure_crosscheck(meas, aux, A, 5, order3):
        raise SystemExit("theorem TC-T crosscheck disagrees under a proposed order-3 candidate")
    H = (F(ad["R2_interval"]["lo"]), F(ad["R2_interval"]["hi"]))
    M0 = F(ad["M_R2"])
    a, b = max(H[0], lo), min(H[1], hi)
    M = M0 if a > b else min(M0, max(abs(a), abs(b)))
    e0, rho, x_hi = (KM.rat(cov[t]) for t in ("e0", "rho", "right"))
    return (F(ad["R_interval"]["hi"]) - e0 * F(ad["D_interval"]["lo"])) + rho * x_hi * M


def critical_ratio(T, R, meas, aux, A, ad, cov, KM, lf: dict):
    """Largest s_G/s_H at which a REAL order-3 candidate still passes the frozen direct test on this cell.

    The candidate pays its supremum through the (P3) envelope Env4 and its value at the atom through the centre
    motion rho*|Ghat(a)| -- which is exactly what invalidated Campaign B's route T2. Exact rational bisection; the
    value returned is the last certified-PASSING endpoint, so it never overstates.
    """
    def ok(ratio: F) -> bool:
        o3 = {}
        for r in range(5):
            sG = ratio * F(meas["r"][str(r)]["sup"]["H"])
            o3[str(r)] = {"sup_G": str(sG), "abs_G_at_a": str(lf[r]["ag_max"] * sG),
                          "delta_G": str(lf[r]["dg_max"])}
        return gamma_with(T, R, meas, aux, A, ad, cov, KM, o3) < 0

    if not ok(F(0)):
        return None
    lo_r, hi_r = F(0), F(500)
    if ok(hi_r):
        return float("inf")
    for _ in range(50):
        mid = (lo_r + hi_r) / 2
        if ok(mid):
            lo_r = mid
        else:
            hi_r = mid
    return float(lo_r)


def operator_mixed(c1b: dict, c2b: dict) -> dict:
    """The componentwise best OPERATOR tuple across the C1 and C2 registries.

    NOT a C2 result and NOT eligible under the frozen C2 gate, which pre-registers the minimum over A0/A1/A2 across
    SUPPLIES, not over the six operator constants. Computed here only to quantify pre-freeze review Note 11: both
    registries certify the same six quantities uniformly over the same cell, so the componentwise best of the two
    satisfies all six Lemma Dv' hypotheses simultaneously and is a sound supply that a SUCCESSOR may pre-register.
    See `phase_d/D_PRIME_OPPORTUNITY.md`.
    """
    def g(b, f):
        v = b[f]
        return F(v) if isinstance(v, str) else F(str(v))
    return {"Abar": min(g(c1b, "Abar"), g(c2b, "Abar")), "tau": min(g(c1b, "tau"), g(c2b, "tau")),
            "C_T": min(g(c1b, "C_T"), g(c2b, "C_T")), "D_lo": max(g(c1b, "D_lo"), g(c2b, "D_lo")),
            "D1": min(g(c1b, "D1"), g(c2b, "D1")), "D2": min(g(c1b, "D2"), g(c2b, "D2"))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    fc = __import__("importlib.util", fromlist=["util"])
    spec = fc.spec_from_file_location("c2_d5_forecast_lib", HERE.parent / "c2_d5_forecast.py")
    FC = fc.module_from_spec(spec)
    sys.modules["c2_d5_forecast_lib"] = FC
    spec.loader.exec_module(FC)          # its GATE_SHA check runs at call time, not import time

    B = FC.load(B_NS / "code/tail_forecast_r2.py", "b_tail_forecast_r2")
    T = sys.modules["tct_rule"]
    R = T.load_frozen("tc_rule", T.FROZEN["tc_rule"][1])
    DC = FC.load(FC.AD_NS / "code/deflated_consume.py", "ad_dc", FC.DC_SHA)
    KM = B

    adopted = json.loads((B_NS / "evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json").read_bytes())["cells"]
    cells = json.loads((CP / "p5y_k1_cover_ledger_successor/config/cells.json").read_bytes())
    cover = {c["index"]: c for c in cells if c["detector"] == "CUSUM"}   # index collides across detectors
    c1b = {b["cell"]: b for b in json.loads((C1_NS / "evidence/registry_c1/REGISTRY_C1.json").read_bytes())["blocks"]}
    c2b = {b["cell"]: b for b in json.loads((NS / "evidence/registry_c2/REGISTRY_C2.json").read_bytes())["blocks"]}
    lf, n_lf, gh_span = lower_front_model(FC)

    meas, aux = {}, {}
    for k in TAIL:
        d = json.loads((B_NS / f"evidence/measurement_r1/TCT_INPUTS_{k}.json").read_bytes())
        if d["cell"] != k or not d["identity_gate"]["identical"] or d["order3_fields_present"]:
            raise SystemExit(f"measurement {k} is not a gated order-3-free replay")
        d["C_upper"] = adopted[str(k)]["C_upper"]
        meas[k], aux[k] = d, adopted[str(k)]["auxiliary_evidence"]

    def dv(b):
        return DC.atom_constants_r2(*(F(str(b[x])) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2")))

    out = {"supplies": {}, "anchors": {}, "lower_front_cells": n_lf,
           "lower_front_ratio_range": [float(gh_span[0]), float(gh_span[1])]}
    supplies_per_cell = {}
    for k in TAIL:
        kn = {i: F(meas[k]["norms"]["k"][i]) for i in range(5)}
        S = {"G": T.atom_constants_generic(F(meas[k]["C_upper"]), kn[1], kn[2]),
             "C1": dv(c1b[k]), "C2": dv(c2b[k])}
        S["min_G_C1"] = FC.combine({n: S[n] for n in ("G", "C1")})[0]      # what existed when C1 stopped
        S["D4_gate_rule"] = FC.combine({n: S[n] for n in ("G", "C1", "C2")})[0]
        S["operator_mixed"] = dv(operator_mixed(c1b[k], c2b[k]))
        supplies_per_cell[k] = S

    for name in ("G", "C1", "C2", "min_G_C1", "D4_gate_rule", "operator_mixed"):
        row = {}
        for k in TAIL:
            A = supplies_per_cell[k][name]
            ad, cov = adopted[str(k)]["m"]["5"], cover[k]
            d0 = FC.direct(T, R, meas[k], aux[k], A, ad, cov, KM)
            perfect = {str(r): {"sup_G": "0", "abs_G_at_a": "0", "delta_G": "0"} for r in range(5)}
            req = FC.requirement(T, R, meas[k], aux[k], A, ad, cov, KM)
            gap = None if req is None else max(F(0), req - 1)
            row[str(k)] = {"critical_sG_over_sH": critical_ratio(T, R, meas[k], aux[k], A, ad, cov, KM, lf),
                           "Gamma": float(d0["Gamma"]), "closes": d0["pass"],
                           "Gamma_perfect_order3": float(gamma_with(T, R, meas[k], aux[k], A, ad, cov, KM, perfect)),
                           "requirement": float(req) if req is not None else None,
                           "requirement_exact": None if req is None else str(req),
                           "gap_above_1": None if gap is None else float(gap),
                           "A": {j: float(A[j]) for j in ("A0", "A1", "A2")}}
        out["supplies"][name] = row

    # ---- refuse unless both published anchors reproduce bit-exactly -------------------------------------------
    bref = json.loads(B_FORECAST.read_bytes())["critical_sup_G_over_sup_H_ratio"]
    mine_g = {k: out["supplies"]["G"][k]["critical_sG_over_sH"] for k in bref}
    if mine_g != {k: bref[k] for k in bref}:
        raise SystemExit(f"Lemma-G column does not reproduce Campaign B: {mine_g} vs {bref}")
    c2ref = json.loads(C2_AUX.read_bytes())
    for field in ("critical_sG_over_sH", "Gamma", "Gamma_perfect_order3"):
        mine = {k: out["supplies"]["C2"][k][field] for k in c2ref}
        theirs = {k: c2ref[k][field] for k in c2ref}
        if mine != theirs:
            raise SystemExit(f"C2 column does not reproduce published {field}: {mine} vs {theirs}")
    out["anchors"] = {"campaign_B_lemma_G_critical_ratio": "reproduced bit-exactly",
                      "campaign_C2_critical_ratio_Gamma_and_attribution": "reproduced bit-exactly"}

    Path(a.out).write_text(json.dumps(out, sort_keys=True, indent=1) + "\n")
    for name in out["supplies"]:
        print(name, {k: round(v["critical_sG_over_sH"], 5) if v["critical_sG_over_sH"] else v["critical_sG_over_sH"]
                     for k, v in out["supplies"][name].items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
