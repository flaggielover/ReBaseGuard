"""QC05: two-sided exactness of the composition layers (envelope, Dv'-M, D14-M + Lemma DM, Lemma G, S_i, Lemma Lad,
pointwise U/L), primary (mb308_supply / mb308_stage1, pinned c1b assemble, frozen deflated_consume) against the
independent reconstruction F2 (mb_independent, pinned) and literal definitions, with planted mutants.

A test is TWO-SIDED: every S_i component must EQUAL the oracle exactly (Fractions). Each mutant must be REJECTED
(differ from the oracle on at least one set); the one-sided check S_i <= S_I1 is also evaluated to show which mutants
it would have missed. Every input is synthetic (seeded); no cell value is used.
"""
from __future__ import annotations

import random
from fractions import Fraction as F

SEED = 20260929
N_SETS = 300
FIELDS = ("A0", "A1", "A2")
D14 = ("A_bar", "tau", "D_lo", "C_T", "D1", "D2", "L1_up", "L2_up", "tau_a_lo", "C_R")
EPS = F(1, 2 ** 40)


def _rq(rng, lo, hi, den=1 << 12):
    return F(rng.randint(int(F(lo) * den), int(F(hi) * den)), den)


def synth_case(rng, n_blocks: int, bind: str | None = None) -> dict:
    """One synthetic cell: tiles, hulls, b_i, verified U_i (some None), RLR block records (some None), registries."""
    x_lo = _rq(rng, F(1, 4), 1)
    w = _rq(rng, F(1, 200), F(1, 100))
    blocks = []
    for i in range(n_blocks):
        lo, hi = x_lo + i * w, x_lo + (i + 1) * w
        s = 1 << 20
        hlo, hhi = F((lo * s).__floor__(), s), F((hi * s).__ceil__(), s)
        blocks.append({"index": i, "tile": (lo, hi), "hull": (hlo, hhi), "b": hlo})
    U = [None if rng.random() < 0.2 else _rq(rng, 2, 60) for _ in blocks]
    recs = []
    for b in blocks:
        if rng.random() < 0.15:
            recs.append(None)
            continue
        tlo = _rq(rng, 1, 20)
        tau = tlo * (1 + _rq(rng, 0, 1))
        r = {"tau_a_lo": tlo, "tau": tau, "D_lo": _rq(rng, F(1, 1000), 1), "A_bar": _rq(rng, 1, 80),
             "C_T": tau * (1 + _rq(rng, 0, 3)), "C_R": _rq(rng, 1, 80), "D1": _rq(rng, 0, 20), "D2": _rq(rng, 0, 200),
             "L1_up": _rq(rng, 1, 100)}
        r["L2_up"] = r["L1_up"] * (1 + _rq(rng, 0, 20))
        recs.append({k: f"{v.numerator}/{v.denominator}" for k, v in r.items()} |
                    {"status": "CERTIFIED", "_kind": "RLR_BLOCK", "_hull": [str(b["hull"][0]), str(b["hull"][1])]})
    regs = []
    for name in ("C1", "C2"):
        tau = _rq(rng, 1, 8)
        regs.append({"name": name, "values": {"Abar": _rq(rng, 1, 90), "tau": tau, "C_T": tau * (1 + _rq(rng, 0, 3)),
                                              "D_lo": _rq(rng, F(1, 100), 1), "D1": _rq(rng, 0, 5),
                                              "D2": _rq(rng, 0, 50)}})
    S = {"A0": _rq(rng, 1, 90), "A1": _rq(rng, 1, 5000), "A2": _rq(rng, 1, 10 ** 6)}
    if bind == "S_I1":
        S = {j: F(1, 10 ** 6) for j in FIELDS}
    elif bind in ("DvM_C1", "DvM_C2"):
        v = regs[0 if bind == "DvM_C1" else 1]["values"]
        v.update({"Abar": F(1), "C_T": v["tau"], "D1": F(0), "D2": F(0), "D_lo": F(10 ** 6)})
        S = {j: F(10 ** 12) for j in FIELDS}
        recs = [None for _ in recs]
    elif bind in ("D14M", "G"):
        S = {j: F(10 ** 12) for j in FIELDS}
        regs = []
        for r in recs:
            if r is not None and bind == "G":
                r["C_R"] = "1/1000"
            if r is not None and bind == "D14M":
                r.update({"A_bar": "1/1000", "C_R": "1000"})
    return {"blocks": blocks, "U": U, "recs": recs, "regs": regs, "S": S}


# ------------------------------------------------------------------ the oracle (F2 + literal definitions)
def oracle(IND, case: dict, k_dv: tuple, k_cert: tuple) -> list:
    Ub, cur = [], None
    for u in case["U"]:
        if u is not None and (cur is None or u < cur):
            cur = u
        Ub.append(cur)
    env = IND.envelope(case["U"], [b["b"] for b in case["blocks"]])
    assert [None if e is None else F(e) for e in env] == Ub, "F2 envelope differs from the literal definition"
    out = []
    for i, _ in enumerate(case["blocks"]):
        U = IND.INF if Ub[i] is None else Ub[i]
        mem = {"S_I1": tuple(case["S"][j] for j in FIELDS)}
        for s in case["regs"]:
            v = s["values"]
            mem["DvM_" + s["name"]] = IND.dv_prime_M({"A_bar": v["Abar"], "tau": v["tau"], "C_T": v["C_T"],
                                                      "D_lo": v["D_lo"], "D1": v["D1"], "D2": v["D2"]}, U, *k_dv)
        r = case["recs"][i]
        if r is not None:
            mem["D14M"] = IND.d14_M({k: F(r[k]) for k in D14}, U, *k_cert, True)
            mem["G"] = IND.lemma_g(F(r["C_R"]), *k_cert)
        bs = IND.block_supply(mem)
        out.append({"S": {j: bs[j] for j in FIELDS}, "attaining": bs["attaining"], "Ubar": Ub[i], "mem": mem})
    return out


# ------------------------------------------------------------------ mutants of the primary composition
def mutant_outputs(name: str, case: dict, IND, k_dv, k_cert, cp, SUP, con, IND7) -> list:
    """S_i of a MUTATED composition (each an alternative, wrong implementation)."""
    blocks, U = case["blocks"], case["U"]
    if name == "envelope_right_hand":
        Ub = [min([u for u in U[i:] if u is not None], default=None) for i in range(len(U))]
    elif name == "envelope_none":
        Ub = list(U)
    else:
        Ub, cur = [], None
        for u in U:
            if u is not None and (cur is None or u < cur):
                cur = u
            Ub.append(cur)
    res = []
    for i, _ in enumerate(blocks):
        ub = Ub[i]
        mem = {"S_I1": dict(case["S"])}
        for s in case["regs"]:
            v = dict(s["values"])
            ab = v["Abar"] if (ub is None or name == "abar_not_capped") else (
                ub if name == "abar_replaced" else min(v["Abar"], ub))
            args = (ab, v["tau"], v["C_T"], v["D_lo"], v["D1"], v["D2"])
            mem["DvM_" + s["name"]] = {j: con["DC"].atom_constants_r2(*args)[j] for j in FIELDS}
        r = case["recs"][i]
        if r is not None:
            rr = {k: F(r[k]) for k in D14}
            ab = rr["A_bar"] if (ub is None or name == "abar_not_capped") else (
                ub if name == "abar_replaced" else min(rr["A_bar"], ub))
            dlo = rr["D_lo"] if name == "no_DM_refresh" else max(rr["D_lo"], rr["tau_a_lo"] / ab)
            out = cp.assemble(dict(rr, A_bar=ab, D_lo=dlo))
            a0 = min(ab, rr["tau"] / dlo) if name == "A0_slot_without_C_R" else out["A0_SUPPLY"]
            mem["D14M"] = {"A0": a0, "A1": out["A1_SUPPLY"], "A2": out["A2_SUPPLY"]}
            mem["G"] = {"A0": out["G0"], "A1": out["G1"], "A2": out["G2"]}
        names = [n for n in mem if not (name == "no_S_I1" and n == "S_I1")]
        agg = max if name == "max_for_min" else min
        S = {j: agg(F(mem[n][j]) for n in names) for j in FIELDS}
        if name == "plus_2^-40":
            S = {j: v * (1 + EPS) for j, v in S.items()}
        if name == "minus_2^-40":
            S = {j: v * (1 - EPS) for j, v in S.items()}
        res.append((S, mem))
    return res


MUTANTS = ("no_S_I1", "max_for_min", "envelope_right_hand", "envelope_none", "abar_not_capped", "abar_replaced",
           "no_DM_refresh", "A0_slot_without_C_R", "plus_2^-40", "minus_2^-40")


def composition_test(SUP, S1M, S1, IND, IND7, cp, con, guard) -> dict:
    rng = random.Random(SEED)
    k_dv = (con["C2F"].K1_BOUND, con["C2F"].K2_BOUND)
    k_cert = (cp.KAPPA1, cp.KAPPA2)
    cases = [synth_case(rng, rng.randint(1, 12)) for _ in range(N_SETS)]
    plants = {b: synth_case(rng, 4, bind=b) for b in ("S_I1", "DvM_C1", "DvM_C2", "D14M", "G")}
    n_eq = n_blocks = 0
    bad = []
    mut = {m: {"sets_differing": 0, "passes_one_sided_somewhere": False} for m in MUTANTS}
    for ci, case in enumerate(cases + list(plants.values())):
        orc = oracle(IND, case, k_dv, k_cert)
        got = SUP.compose(case["blocks"], case["U"], case["recs"], case["S"], case["regs"], con, IND7, cp, IND, guard)
        if got["independent"]["status"] != "EQUAL":
            bad.append(ci)
        for i, b in enumerate(got["blocks"]):
            n_blocks += 1
            ok = all(b["_S"][j] == orc[i]["S"][j] for j in FIELDS) and \
                all(b["provenance"][j] in orc[i]["attaining"][j] for j in FIELDS)
            n_eq += ok
            if not ok:
                bad.append((ci, i))
        for m in MUTANTS:          # detection at the S_i level OR at the member level (two-sided per member)
            ms = mutant_outputs(m, case, IND, k_dv, k_cert, cp, SUP, con, IND7)
            s_diff = any(ms[i][0][j] != orc[i]["S"][j] for i in range(len(ms)) for j in FIELDS)
            m_diff = any(tuple(F(ms[i][1][n][j]) for j in FIELDS) != tuple(F(x) for x in orc[i]["mem"][n])
                         for i in range(len(ms)) for n in ms[i][1] if n in orc[i]["mem"])
            mut[m]["sets_differing"] += s_diff or m_diff
            mut[m]["sets_differing_at_S"] = mut[m].get("sets_differing_at_S", 0) + s_diff
            if s_diff and all(ms[i][0][j] <= case["S"][j] for i in range(len(ms)) for j in FIELDS):
                mut[m]["passes_one_sided_somewhere"] = True
    plant_prov = {}                     # the planted member attains the minimum (G can only tie with D14M: D14
    for bname, case in plants.items():  # already contains the min with G, so its provenance is D14M on a tie)
        got = SUP.compose(case["blocks"], case["U"], case["recs"], case["S"], case["regs"], con, IND7, cp, IND, guard)
        orc = oracle(IND, case, k_dv, k_cert)
        want = "D14M" if bname == "G" else bname
        plant_prov[bname] = all(bname in orc[b["index"]]["attaining"][j] and b["provenance"][j] == want
                                for b in got["blocks"] for j in ("A1", "A2")
                                if bname not in ("D14M", "G") or case["recs"][b["index"]] is not None)
    for m in mut.values():
        m["rejected"] = m["sets_differing"] > 0
    # refusals: pointwise inputs substituted for block ones; DM impossible direction; floats
    case = cases[0]
    rec = next((r for r in case["recs"] if r is not None), None)
    refusals = {}
    for label, patch in (("pointwise_record", {"_kind": "POINTWISE"}), ("wrong_hull", {"_hull": ["0/1", "1/1"]}),
                         ("not_certified", {"status": "NOT_CERTIFIED"})):
        try:
            SUP.d14m(cp, IND7, dict(rec, **patch), case["blocks"][case["recs"].index(rec)]["hull"], None)
            refusals[label] = False
        except SUP.SupplyRefusal:
            refusals[label] = True
    try:
        SUP.q(0.5)
        refusals["float_reaching_exact_layer"] = False
    except TypeError:
        refusals["float_reaching_exact_layer"] = True
    lad = ladder_test(S1, SUP, IND, IND7, cp, rng)
    pw = pointwise_test(S1M)
    ok = (n_eq == n_blocks and not bad and all(m["rejected"] for m in mut.values()) and all(plant_prov.values())
          and all(refusals.values()) and lad["pass"] and pw["pass"])
    return {"sets": len(cases) + len(plants), "blocks": n_blocks, "exact_equal": n_eq, "not_equal": bad[:10],
            "mutants": mut, "plants_provenance": plant_prov, "refusals": refusals, "ladder": lad,
            "pointwise": pw, "pass": ok}


def ladder_test(S1, SUP, IND, IND7, cp, rng) -> dict:
    """Lemma Lad: pinned rlr307_stage1.ladder_compose == rlr307_independent.ladder == F2 ladder (3-rung ladders)."""
    keys = IND7.UPPER_KEYS + IND7.LOWER_KEYS
    n_ok, n, n_mut = 0, 150, 0
    for _ in range(n):
        rungs = []
        for d in (4, 6, 8):
            r = {k: F(rng.randint(1, 10 ** 6), rng.randint(1, 10 ** 3)) for k in keys}
            rungs.append({k: f"{v.numerator}/{v.denominator}" for k, v in r.items()} | {"status": "CERTIFIED",
                                                                                         "degree": d})
        brec = S1.ladder_compose(cp, rungs)
        lad = IND7.ladder(rungs)
        n_ok += all(F(brec[k]) == lad[k] for k in keys) and SUP.f2_ladder_check(IND, rungs, brec)
        n_mut += max(F(r["tau"]) for r in rungs) != F(brec["tau"])      # mutant: an upper key composed by max
    return {"ladders": n, "equal": n_ok, "mutant_max_for_upper_rejected_on": n_mut,
            "pass": n_ok == n and n_mut > 0}


def pointwise_test(S1M) -> dict:
    """The amended D4/D5 rule (REVIEW_A0_CERTIFIER_R1 C2, coordinator notes 3 and 5): admission needs VERIFIED and an
    other-implementation lower rung below U; REFUTED or a cross-implementation L_other > U is INCONSISTENT; a
    same-implementation comparison is not an alarm; C1b uppers of degree > C1B_VERIFY_MAX_D are never admitted."""
    def c2(n, U, L, verdict="VERIFIED"):
        return {"rung": n, "status_U": "CERTIFIED", "status_L": "CERTIFIED", "record": {"U": U, "L": L},
                "verification": {"accepted": verdict == "VERIFIED", "verdict": verdict}}

    def c1(d, U, L):
        return {"rung": d, "status": "CERTIFIED", "record": {"U": U, "L": L}}

    ok = {"verdict": "VERIFIED", "accepted": True}
    r1 = S1M.pointwise([c2(20, "6", "2"), c2(40, "4", "3")], [c1(8, "5", "2"), c1(10, "9/2", "2")], {})
    r2 = S1M.pointwise([c2(20, "3", "2")], [c1(8, "5", "4")], {})
    r3 = S1M.pointwise([c2(20, "7", "6")], [c1(8, "5", "2")], {})
    r4 = S1M.pointwise([c2(20, "6", "2", "UNDECIDED")], [c1(8, "5", "2")], {})
    r5 = S1M.pointwise([c2(20, "6", "2", "REFUTED")], [c1(8, "5", "2")], {})
    r6 = S1M.pointwise([c2(20, "6", "2")], [], {})
    r7 = S1M.pointwise([c2(20, "6", "7/2")], [c1(8, "9", "2")], {})
    r8 = S1M.pointwise([c2(20, "6", "2")], [c1(4, "5", "2")], {4: ok})
    r9 = S1M.pointwise([c2(20, "6", "2")], [c1(4, "5", "2")], {4: {"verdict": "REFUTED", "accepted": False}})
    c1_d8 = [u for u in r1["uppers"] if u["impl"] == "C1B"]
    res = {"U_min_over_admitted_C2b": r1["status"] == "CERTIFIED" and r1["U"] == "4/1" and r1["U_rungs"] == ["C2B:N=40"],
           "C1b_d8_uppers_never_admitted": all(u["verdict"] == "NOT_INDEPENDENTLY_VERIFIED" and not u["verified"]
                                               for u in c1_d8) and len(c1_d8) == 2,
           "L_C1B_above_C2B_upper_inconsistent": r2["status"] == "INCONSISTENT" and r2["U"] is None,
           "L_C2B_above_C1B_upper_inconsistent": r3["status"] == "INCONSISTENT",
           "undecided_not_admitted": r4["status"] == "NOT_CERTIFIED" and r4["U"] is None,
           "c2b_refutation_inconsistent": r5["status"] == "INCONSISTENT" and r5["refuted_rungs"] == ["C2B:N=20"],
           "no_other_implementation_lower_alarm_unavailable": r6["status"] == "ALARM_UNAVAILABLE" and r6["U"] is None,
           "same_implementation_L_above_U_not_an_alarm": r7["status"] == "CERTIFIED" and r7["U"] == "6/1",
           "low_degree_c1b_admissible_when_verified": r8["status"] == "CERTIFIED" and r8["U"] == "5/1",
           "c1b_refutation_inconsistent": r9["status"] == "INCONSISTENT" and r9["refuted_rungs"] == ["C1B:d=4"],
           "alarm_sensitivity_recorded": any(u.get("alarm_sensitivity") == "2/1" for u in r1["uppers"])}
    res["pass"] = all(res.values())
    return res
