"""QC05 / QC09: two-sided exactness tests of every composition layer above the certifier (brief sections 9, 10).

Implementation under test (IUT): the pinned `c1b_certpw.assemble` (block supply), `rlr307_stage1.ladder_compose` and
`cell_compose`, and `rlr307_driver.s_rlr`. Oracle: `rlr307_independent` (written from THEOREM_RLR307, sharing no code).

A test is TWO-SIDED: every component of the IUT must EQUAL the oracle exactly (Fractions). A one-sided bound
(IUT <= min of the supplies) is also evaluated, only to show which mutants it would have missed.

Mutants (each must be REJECTED by the equality clause):
  historical (overnight D18): no_min, no_G (too large); supply_half, drop_A2_cross, drop_A1_delta, G_no_cubic (too small)
  composition: ladder_max_for_upper, ladder_min_for_lower, cell_min, A0_replaced, no_min_with_I1, max_for_min
"""
from __future__ import annotations

import glob
import json
import random
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
OV_VALIDATION = REPO / "level4/closure_proofs/p5y_k5_tail_overnight_research/validation"
INPUT_KEYS = ("A_bar", "tau", "D_lo", "C_T", "D1", "D2", "L1_up", "L2_up", "tau_a_lo", "C_R")
SUPPLY_KEYS = ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY", "G0", "G1", "G2")
SEED = 20260928
N_RANDOM = 2000


def _ex(v):
    return F(v["exact"]) if isinstance(v, dict) and "exact" in v else (F(v) if isinstance(v, str) else v)


# ------------------------------------------------------------------ mutants of the IUT (block supply)
def _terms(inp, k1, k2):
    Ab, t, Dl, CT = (F(inp[k]) for k in ("A_bar", "tau", "D_lo", "C_T"))
    D1, D2, L1, L2, tlo, CR = (F(inp[k]) for k in ("D1", "D2", "L1_up", "L2_up", "tau_a_lo", "C_R"))
    Ae = min(Ab, t / Dl)
    d1, d2 = D1 / Dl, D2 / Dl
    c1 = min(Ae * L1 / tlo, L1 / Dl, Ae * k1 * CT)
    c2 = min(Ae * L2 / tlo, L2 / Dl, Ae * (2 * k1 * k1 * CT * CT + k2 * CT))
    q1 = min(Ae * L1 / tlo, L1 / Dl)
    q2 = min(Ae * L2 / tlo, L2 / Dl)
    return Ae, d1, d2, c1, c2, q1, q2, CR


def mutants(cp, k1, k2):
    def no_min(inp):
        r = cp.assemble({k: F(inp[k]) for k in INPUT_KEYS}, use_min=False)
        return {k: r[k] for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY")}

    def no_G(inp):
        Ae, d1, d2, c1, c2, *_ = _terms(inp, k1, k2)
        return {"A0_SUPPLY": Ae, "A1_SUPPLY": c1 + Ae * d1, "A2_SUPPLY": c2 + 2 * c1 * d1 + Ae * (2 * d1 * d1 + d2)}

    def supply_half(inp):
        r = cp.assemble({k: F(inp[k]) for k in INPUT_KEYS})
        return {k: r[k] / 2 for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY")}

    def _with(inp, a1f, a2f, g2f=None):
        Ae, d1, d2, c1, c2, _, _, CR = _terms(inp, k1, k2)
        g1 = k1 * CR * CR
        g2 = g2f(CR) if g2f else k2 * CR * CR + 2 * k1 * k1 * CR ** 3
        return {"A0_SUPPLY": min(Ae, CR), "A1_SUPPLY": min(a1f(Ae, d1, d2, c1, c2), g1),
                "A2_SUPPLY": min(a2f(Ae, d1, d2, c1, c2), g2)}

    def drop_A2_cross(inp):
        return _with(inp, lambda Ae, d1, d2, c1, c2: c1 + Ae * d1, lambda Ae, d1, d2, c1, c2: c2 + Ae * (2 * d1 * d1 + d2))

    def drop_A1_delta(inp):
        return _with(inp, lambda Ae, d1, d2, c1, c2: c1,
                     lambda Ae, d1, d2, c1, c2: c2 + 2 * c1 * d1 + Ae * (2 * d1 * d1 + d2))

    def G_no_cubic(inp):
        return _with(inp, lambda Ae, d1, d2, c1, c2: c1 + Ae * d1,
                     lambda Ae, d1, d2, c1, c2: c2 + 2 * c1 * d1 + Ae * (2 * d1 * d1 + d2), lambda CR: k2 * CR * CR)

    return {"no_min": (no_min, "too_large"), "no_G": (no_G, "too_large"), "supply_half": (supply_half, "too_small"),
            "drop_A2_cross": (drop_A2_cross, "too_small"), "drop_A1_delta": (drop_A1_delta, "too_small"),
            "G_no_cubic": (G_no_cubic, "too_small")}


def one_sided_bound(inp, k1, k2) -> dict:
    """min(raw RLR, Dv', G) per component: the pre-R3 one-sided test's bound."""
    Ae, d1, d2, _, _, q1, q2, CR = _terms(inp, k1, k2)
    CT = F(inp["C_T"])
    rlr1, rlr2 = q1 + Ae * d1, q2 + 2 * q1 * d1 + Ae * (2 * d1 * d1 + d2)
    dv1 = Ae * (k1 * CT + d1)
    dv2 = Ae * (2 * k1 * k1 * CT * CT + k2 * CT + 2 * k1 * CT * d1 + 2 * d1 * d1 + d2)
    g1, g2 = k1 * CR * CR, k2 * CR * CR + 2 * k1 * k1 * CR ** 3
    return {"A1_SUPPLY": min(rlr1, dv1, g1), "A2_SUPPLY": min(rlr2, dv2, g2), "A0_SUPPLY": min(Ae, CR)}


# ------------------------------------------------------------------ input sets
def committed_sets() -> list:
    out = []
    for f in sorted(glob.glob(str(OV_VALIDATION / "C1B_R2_PW_*.json"))):
        d = json.loads(Path(f).read_bytes())
        for i, r in enumerate(d.get("records", [])):
            if r.get("status") == "CERTIFIED" and all(isinstance(r.get(k), dict) for k in INPUT_KEYS):
                out.append({"name": f"{Path(f).name}#rung{i}", "inp": {k: _ex(r[k]) for k in INPUT_KEYS},
                            "committed": {k: _ex(r[k]) for k in SUPPLY_KEYS if isinstance(r.get(k), dict)}})
        lm = d.get("ladder_min") or {}
        if all(isinstance(lm.get(k), dict) for k in INPUT_KEYS):
            out.append({"name": f"{Path(f).name}#ladder_min", "inp": {k: _ex(lm[k]) for k in INPUT_KEYS},
                        "committed": {k: _ex(lm[k]) for k in SUPPLY_KEYS if isinstance(lm.get(k), dict)}})
    return out


def decoy_sets(decoy_stage1: dict | None) -> list:
    out = []
    for b in (decoy_stage1 or {}).get("blocks", []):
        for r in b["rungs"]:
            if r.get("kind") == "RUNG_RETURNED" and r.get("status") == "CERTIFIED":
                rec = r["record"]
                out.append({"name": f"decoy block {b['index']} d{rec['degree']}",
                            "inp": {k: F(rec[k]) for k in INPUT_KEYS},
                            "committed": {k: F(rec[k]) for k in SUPPLY_KEYS}})
    return out


def planted_sets(k1) -> list:
    base = {"A_bar": F(40), "tau": F(10), "D_lo": F(1, 4), "C_T": F(20), "D1": F(3, 2), "D2": F(16),
            "L1_up": F(30), "L2_up": F(200), "tau_a_lo": F(9), "C_R": F(40)}
    ratio = dict(base, A_bar=F(9, 2) * 4, tau=F(40), C_R=F(10 ** 6))        # A_eff = A_bar < tau_a,lo/D_lo -> ratio < non-ratio
    ratio["L1_up"] = ratio["tau_a_lo"] * k1 * ratio["C_T"] / 4
    nonratio = dict(base, A_bar=F(10 ** 6), tau=F(36), C_T=F(10 ** 4), C_R=F(10 ** 6))   # tau = 4 tau_a,lo
    dv = dict(base, L1_up=F(10 ** 7), L2_up=F(10 ** 9), C_R=F(10 ** 6))
    g = dict(base, C_R=F(3, 2))
    mixed = dict(base, C_R=F(12), L1_up=F(10 ** 5))
    return [{"name": n, "inp": s, "expect": e} for n, s, e in (("plant_ratio_binding", ratio, "RLR_ratio"),
                                                               ("plant_nonratio_binding", nonratio, "RLR_nonratio"),
                                                               ("plant_Dv_binding", dv, "Dv"),
                                                               ("plant_G_binding", g, "G"),
                                                               ("plant_mixed", mixed, None))]


def random_sets(n: int = N_RANDOM, seed: int = SEED) -> list:
    rng = random.Random(seed)

    def rq(lo, hi, den=1 << 12):
        return F(rng.randint(int(lo * den), int(hi * den)), den)

    out = []
    for i in range(n):
        tlo = rq(1, 20)
        tau = tlo * (1 + rq(0, 1))
        s = {"tau_a_lo": tlo, "tau": tau, "D_lo": rq(F(1, 1000), 1), "A_bar": rq(1, 500), "C_T": tau * (1 + rq(0, 3)),
             "C_R": rq(1, 500), "D1": rq(0, 20), "D2": rq(0, 200), "L1_up": rq(1, 100)}
        s["L2_up"] = s["L1_up"] * (1 + rq(0, 20))
        out.append({"name": f"random{i}", "inp": s})
    return out


# ------------------------------------------------------------------ the tests
def assembly_test(cp, IND, decoy_stage1: dict | None) -> dict:
    k1, k2 = cp.KAPPA1, cp.KAPPA2
    sets = committed_sets() + decoy_sets(decoy_stage1) + planted_sets(k1) + random_sets()
    n_eq, bad, committed_repro, plants = 0, [], {"checked": 0, "equal": 0}, {}
    for s in sets:
        iut = cp.assemble({k: F(s["inp"][k]) for k in INPUT_KEYS})
        orc = IND.block_supply(s["inp"], k1, k2)
        eq = all(iut[k] == orc[k] for k in SUPPLY_KEYS)
        n_eq += eq
        if not eq:
            bad.append(s["name"])
        if s.get("committed"):
            committed_repro["checked"] += 1
            committed_repro["equal"] += all(s["committed"][k] == iut[k] for k in s["committed"])
        if "expect" in s:
            plants[s["name"]] = {"equal": eq, "binding_A1": orc["binding_A1"], "expected": s["expect"],
                                 "as_expected": s["expect"] is None or orc["binding_A1"] == s["expect"]}
    mres = {}
    for name, (fn, kind) in mutants(cp, k1, k2).items():
        n_diff, n_onesided_ok = 0, 0
        for s in sets:
            m = fn(s["inp"])
            orc = IND.block_supply(s["inp"], k1, k2)
            n_diff += any(m[k] != orc[k] for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY"))
            ob = one_sided_bound(s["inp"], k1, k2)
            n_onesided_ok += all(m[k] <= ob[k] and m[k] > 0 for k in ("A1_SUPPLY", "A2_SUPPLY"))
        mres[name] = {"kind": kind, "rejected": n_diff > 0, "sets_differing": n_diff, "sets": len(sets),
                      "passes_one_sided_bound_on": n_onesided_ok}
    float_raises = False
    try:
        IND.block_supply(dict(sets[0]["inp"], tau=float(sets[0]["inp"]["tau"])), k1, k2)
    except TypeError:
        float_raises = True
    hist_rejected = sum(1 for m in mres.values() if m["rejected"])
    return {"sets": len(sets), "exact_equal": n_eq, "not_equal": bad[:10], "committed_reproduction": committed_repro,
            "plants": plants, "mutants": mres, "historical_mutants_rejected": f"{hist_rejected}/6",
            "too_small_mutants_pass_one_sided_somewhere": {n: m["passes_one_sided_bound_on"] > 0 for n, m in mres.items()
                                                           if m["kind"] == "too_small"},
            "float_reaching_exact_layer_raises": float_raises,
            "pass": n_eq == len(sets) and hist_rejected == 6 and all(p["as_expected"] and p["equal"] for p in plants.values())
            and committed_repro["equal"] == committed_repro["checked"] and float_raises}


def composition_test(cp, IND, S1, D, decoy_stage1: dict) -> dict:
    """Ladder, cell and S_RLR layers, on the decoy rungs, with mutants."""
    rng = random.Random(SEED + 1)
    blocks = decoy_stage1["blocks"]
    cert = [[r["record"] for r in b["rungs"] if r.get("kind") == "RUNG_RETURNED" and r.get("status") == "CERTIFIED"]
            for b in blocks]
    res = {"ladder_equal": 0, "blocks": len(blocks)}
    for rungs in cert:
        brec = S1.ladder_compose(cp, rungs)
        lad = IND.ladder(rungs)
        isup = IND.block_supply(lad, cp.KAPPA1, cp.KAPPA2)
        res["ladder_equal"] += all(F(brec[k]) == lad[k] for k in IND.UPPER_KEYS + IND.LOWER_KEYS) and all(
            F(brec[k]) == isup[k] for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY"))
    brecs = [S1.ladder_compose(cp, r) for r in cert]
    cell = S1.cell_compose(brecs)
    icell = IND.cell([IND.block_supply(IND.ladder(r), cp.KAPPA1, cp.KAPPA2) for r in cert])
    res["cell_equal"] = all(F(cell[k + "_max"]) == icell[k] for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY"))

    def mut_ladder(rungs, which):
        out = IND.ladder(rungs)
        if which == "ladder_max_for_upper":
            out["tau"] = max(F(r["tau"]) for r in rungs)
        else:
            out["D_lo"] = min(F(r["D_lo"]) for r in rungs)
        return out

    # multi-rung ladders: the decoy blocks' own rungs plus 200 synthetic 3-rung ladders (so rejection power never
    # depends on the decoy data having several certified rungs per block)
    synth = []
    for _ in range(200):
        rungs = []
        for _d in range(3):
            r = {k: F(rng.randint(1, 10 ** 6), rng.randint(1, 10 ** 3)) for k in IND.UPPER_KEYS + IND.LOWER_KEYS}
            rungs.append(r)
        synth.append(rungs)
    multi = [r for r in cert if len(r) > 1] + synth
    lm = {}
    for which in ("ladder_max_for_upper", "ladder_min_for_lower"):
        lm[which] = {"rejected": any(mut_ladder(r, which) != IND.ladder(r) for r in multi),
                     "ladders_tested": len(multi), "decoy_multi_rung_blocks": len(multi) - len(synth)}
    synth_equal = 0                                  # the IUT ladder on synthetic multi-rung ladders, exact
    for r in synth:
        brec = S1.ladder_compose(cp, [dict({k: S1.fs(v) for k, v in x.items()}, status="CERTIFIED", degree=i)
                                      for i, x in enumerate(r)])
        lad = IND.ladder(r)
        isup = IND.block_supply(lad, cp.KAPPA1, cp.KAPPA2)
        synth_equal += all(F(brec[k]) == lad[k] for k in IND.UPPER_KEYS + IND.LOWER_KEYS) and all(
            F(brec[k]) == isup[k] for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY"))
    res["synthetic_ladder_equal"] = f"{synth_equal}/{len(synth)}"
    cm_min = {k: min(F(b[k]) for b in brecs) for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY")}
    lm["cell_min"] = {"rejected": any(cm_min[k] != icell[k] for k in cm_min)}        # no vacuous pass: needs >= 2 distinct blocks
    # S_RLR on synthetic I1 supplies around the decoy cell values (both orders of every min)
    n_eq, rej = 0, {"A0_replaced": 0, "no_min_with_I1": 0, "max_for_min": 0}
    for _ in range(500):
        s_i1 = {j: F(cell[j + "_SUPPLY_max"]) * F(rng.randint(1, 4000), 2000) for j in ("A0", "A1", "A2")}
        want = IND.consumed(s_i1, {"A1_SUPPLY": cell["A1_SUPPLY_max"], "A2_SUPPLY": cell["A2_SUPPLY_max"]})
        got = D.s_rlr(s_i1, cell)
        n_eq += got == want
        a0r = dict(got, A0=min(s_i1["A0"], F(cell["A0_SUPPLY_max"])))
        nomin = dict(got, A1=F(cell["A1_SUPPLY_max"]), A2=F(cell["A2_SUPPLY_max"]))
        mx = dict(got, A1=max(s_i1["A1"], F(cell["A1_SUPPLY_max"])), A2=max(s_i1["A2"], F(cell["A2_SUPPLY_max"])))
        rej["A0_replaced"] += a0r != want
        rej["no_min_with_I1"] += nomin != want
        rej["max_for_min"] += mx != want
    for k, v in rej.items():
        lm[k] = {"rejected": v > 0, "sets_differing": v}
    a0_unchanged = D.s_rlr({"A0": F(7), "A1": F(1), "A2": F(1)}, cell)["A0"] == F(7)
    res.update({"s_rlr_equal": f"{n_eq}/500", "A0_never_changed": a0_unchanged, "composition_mutants": lm,
                "pass": res["ladder_equal"] == len(blocks) and res["cell_equal"] and n_eq == 500 and a0_unchanged
                and synth_equal == len(synth)
                and all(m["rejected"] for m in lm.values())})
    return res
