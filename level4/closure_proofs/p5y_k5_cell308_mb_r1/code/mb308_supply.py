"""Cell-308 MB campaign (r1) -- the primary composition of the block supplies (B4; design D6-D8, THEOREM_MB r1 s4-6).

For every tile E_i (hull B_i, pointwise drift b_i) the block triple S_i is the componentwise MINIMUM of the available
members (canonical order, used for provenance ties):
  S_I1    the committed cell-level supply (C2's adopted supply, reproduced by control C-A); admissible on E; never absent
  DvM_C1  Lemma Dv'-M on REGISTRY_C1's committed cell inputs (Abar, tau, C_T, D_lo, D1, D2) with
  DvM_C2  Abar' := min(Abar, Ubar_i), through the FROZEN deflated_consume.atom_constants_r2 (no D_lo refresh: the
          registries record no tau_a_lo); cross-checked exactly by c2_d5_forecast._atom_independent and
          rlr307_independent.dv_prime_r2
  D14M    declaration D14 on the RLR ladder record of B_i with Abar' = min(A_bar_B, Ubar_i) and Lemma DM
          D_lo' = max(D_lo_B, tau_a_lo_B / Abar'), through the PINNED c1b_certpw.assemble; A0 slot = A0_SUPPLY =
          min(Abar'_eff, C_R); cross-checked exactly by rlr307_independent.block_supply
  G       Lemma G with C_R of B_i (G0, G1, G2 of the same assembly; == rlr307_independent.lemma_g)
Ubar_i is the Lemma M-U envelope of the independently VERIFIED pointwise upper bounds at b_0 < ... < b_i (None = no
bound). A member that is missing (no RLR record; no verified U) only weakens S_i (D8). The D14M input record must be
an RLR BLOCK record on exactly B_i: a pointwise record (no tau / C_T / D_lo of its own) is refused (review N2).

The independent reconstruction (stream F2, `mb_independent`) is a HOOK: when present, every member, every S_i, the
envelope and the ladder must equal it EXACTLY (else IndependentCheckFailed).
"""
from __future__ import annotations

from fractions import Fraction as F

MEMBER_ORDER = ("S_I1", "DvM_C1", "DvM_C2", "D14M", "G")
FIELDS = ("A0", "A1", "A2")
REG_ARGS = ("Abar", "tau", "C_T", "D_lo", "D1", "D2")
D14_INPUTS = ("A_bar", "tau", "D_lo", "C_T", "D1", "D2", "L1_up", "L2_up", "tau_a_lo", "C_R")


class IndependentCheckFailed(RuntimeError):
    """A composition layer disagrees with an independent reconstruction."""


class SupplyRefusal(ValueError):
    """An input violates a premise of the composition (fail closed)."""


def q(x) -> F:
    if isinstance(x, (float, bool)):
        raise TypeError("a float reached an exact layer")
    return F(x)


def fs(x) -> str:
    x = F(x)
    return f"{x.numerator}/{x.denominator}"


def _min_opt(a, b):
    return a if b is None else (b if a is None else min(a, b))


# ------------------------------------------------------------------ members
def dvm(con: dict, IND7, reg: dict, Ubar) -> dict:
    """Lemma Dv'-M on committed registry cell inputs (frozen consumer arithmetic)."""
    v = {x: q(reg[x]) for x in REG_ARGS}
    if not (v["D_lo"] > 0 and v["tau"] >= 1 and v["C_T"] >= v["tau"] and v["Abar"] >= 1):
        raise SupplyRefusal("registry inputs fail validation")
    ab = v["Abar"] if Ubar is None else min(v["Abar"], q(Ubar))
    args = (ab, v["tau"], v["C_T"], v["D_lo"], v["D1"], v["D2"])
    frozen = con["DC"].atom_constants_r2(*args)
    got = {j: frozen[j] for j in FIELDS}
    if got != con["C2F"]._atom_independent(*args) or \
            got != IND7.dv_prime_r2(*args, con["C2F"].K1_BOUND, con["C2F"].K2_BOUND):
        raise IndependentCheckFailed("Dv'-M: frozen atom constants disagree with the independent recomputations")
    return {"triple": got, "Abar_prime": ab}


def d14m(cp, IND7, brec: dict, hull: tuple, Ubar) -> dict:
    """D14-M + Lemma DM on one RLR block record; returns the D14M and G members."""
    if brec is None:
        return {"D14M": None, "G": None}
    if brec.get("_kind") != "RLR_BLOCK" or brec.get("status") != "CERTIFIED" or \
            tuple(F(x) for x in brec.get("_hull", ())) != tuple(F(x) for x in hull):
        raise SupplyRefusal("D14-M needs a CERTIFIED RLR block record on exactly B_i (pointwise inputs refused)")
    r = {k: q(brec[k]) for k in D14_INPUTS}
    ab = r["A_bar"] if Ubar is None else min(r["A_bar"], q(Ubar))
    dlo = max(r["D_lo"], r["tau_a_lo"] / ab)                          # Lemma DM (declared composition change)
    if dlo < r["D_lo"]:
        raise SupplyRefusal("Lemma DM: D_lo' below the certifier's D_lo is impossible")
    rp = dict(r, A_bar=ab, D_lo=dlo)
    out = cp.assemble(dict(rp))
    ind = IND7.block_supply(rp, cp.KAPPA1, cp.KAPPA2)
    keys = ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY", "G0", "G1", "G2")
    if any(out[k] != ind[k] for k in keys):
        raise IndependentCheckFailed("D14-M: pinned assemble disagrees with rlr307_independent.block_supply")
    g = IND7.lemma_g(r["C_R"], cp.KAPPA1, cp.KAPPA2)
    if (out["G0"], out["G1"], out["G2"]) != (g["A0"], g["A1"], g["A2"]):
        raise IndependentCheckFailed("Lemma G disagrees with rlr307_independent.lemma_g")
    return {"D14M": {"A0": out["A0_SUPPLY"], "A1": out["A1_SUPPLY"], "A2": out["A2_SUPPLY"]},
            "G": {"A0": out["G0"], "A1": out["G1"], "A2": out["G2"]},
            "Abar_prime": ab, "D_lo_prime": dlo, "D_lo_cert": r["D_lo"]}


def block_supply(members: dict) -> dict:
    if members.get("S_I1") is None:
        raise SupplyRefusal("S_I1 must be present")
    names = [n for n in MEMBER_ORDER if members.get(n) is not None]
    out, prov = {}, {}
    for j in FIELDS:
        best = min(q(members[n][j]) for n in names)
        out[j] = best
        prov[j] = next(n for n in names if q(members[n][j]) == best)
    return {"S": out, "provenance": prov}


# ------------------------------------------------------------------ all blocks
def compose(blocks: list, U_list: list, rlr_recs: list, S_I1: dict, reg_sets: list, con: dict | None, IND7, cp,
            indep=None, guard=None) -> dict:
    """blocks: plan() records; U_list: verified U_i or None; rlr_recs: RLR block record or None per block; reg_sets:
    [{"name": "C1"/"C2", "values": {...}}] (empty in decoy mode). Returns per-block members, S_i and the envelope."""
    from mb308_stage1 import envelope
    Ub = envelope(U_list)
    out = []
    for i, b in enumerate(blocks):
        mem = {"S_I1": {j: q(S_I1[j]) for j in FIELDS}}
        detail = {"Ubar": None if Ub[i] is None else fs(Ub[i])}
        for s in reg_sets:
            d = dvm(con, IND7, s["values"], Ub[i])
            mem["DvM_" + s["name"]] = d["triple"]
            detail["Abar_prime_" + s["name"]] = fs(d["Abar_prime"])
        dm = d14m(cp, IND7, rlr_recs[i], b["hull"], Ub[i])
        mem["D14M"], mem["G"] = dm["D14M"], dm["G"]
        if dm["D14M"] is not None:
            detail.update({"Abar_prime_B": fs(dm["Abar_prime"]), "D_lo_prime": fs(dm["D_lo_prime"]),
                           "D_lo_cert": fs(dm["D_lo_cert"])})
        bs = block_supply(mem)
        out.append({"index": b["index"], "tile": [fs(b["tile"][0]), fs(b["tile"][1])],
                    "hull": [fs(b["hull"][0]), fs(b["hull"][1])], "b": fs(b["b"]),
                    "members": {n: (None if t is None else {j: fs(t[j]) for j in FIELDS}) for n, t in mem.items()},
                    "S": {j: fs(v) for j, v in bs["S"].items()}, "provenance": bs["provenance"], "detail": detail,
                    "_S": bs["S"], "_mem": mem})
    res = {"envelope": [None if u is None else fs(u) for u in Ub], "blocks": out,
           "independent": {"status": "HOOK_ABSENT"}}
    if indep is not None:
        band_guard = guard is None or guard.mode() != "TARGET"      # F2's research guard off only when ARMED
        res["independent"] = check_independent(indep, blocks, U_list, Ub, rlr_recs, reg_sets, out, con, cp, band_guard)
    return res


def _f2_reg(v: dict) -> dict:
    return {"A_bar": q(v["Abar"]), "tau": q(v["tau"]), "C_T": q(v["C_T"]), "D_lo": q(v["D_lo"]), "D1": q(v["D1"]),
            "D2": q(v["D2"])}


F2_LADDER_NAMES = {"S2_up": "S2hat_up", "TN_up": "T_N_up"}


def check_independent(IND, blocks, U_list, Ub, rlr_recs, reg_sets, out, con, cp, band_guard) -> dict:
    """Exact equality with stream F2 on every layer; raises IndependentCheckFailed on any difference."""
    inf = IND.INF
    env = IND.envelope(U_list, [b["b"] for b in blocks], research_band_guard=band_guard)
    if [None if e is None else F(e) for e in env] != Ub:
        raise IndependentCheckFailed("F2: envelope differs")
    n_checks = 1
    for i, b in enumerate(blocks):
        U = inf if Ub[i] is None else Ub[i]
        mem = out[i]["_mem"]
        for s in reg_sets:
            t = IND.dv_prime_M(_f2_reg(s["values"]), U, con["C2F"].K1_BOUND, con["C2F"].K2_BOUND, dlo_refresh=False)
            if tuple(t) != tuple(mem["DvM_" + s["name"]][j] for j in FIELDS):
                raise IndependentCheckFailed(f"F2: Dv'-M ({s['name']}) differs at block {i}")
            n_checks += 1
        if mem["D14M"] is not None:
            r = rlr_recs[i]
            t = IND.d14_M({k: q(r[k]) for k in D14_INPUTS}, U, cp.KAPPA1, cp.KAPPA2, True)
            if tuple(t) != tuple(mem["D14M"][j] for j in FIELDS):
                raise IndependentCheckFailed(f"F2: D14-M differs at block {i}")
            g = IND.lemma_g(q(r["C_R"]), cp.KAPPA1, cp.KAPPA2)
            if tuple(g) != tuple(mem["G"][j] for j in FIELDS):
                raise IndependentCheckFailed(f"F2: Lemma G differs at block {i}")
            n_checks += 2
        bs = IND.block_supply({n: (None if t is None else tuple(t[j] for j in FIELDS)) for n, t in mem.items()})
        for j in FIELDS:
            if bs[j] != out[i]["_S"][j] or out[i]["provenance"][j] not in bs["attaining"][j]:
                raise IndependentCheckFailed(f"F2: S_i differs at block {i} ({j})")
        n_checks += 1
    return {"status": "EQUAL", "checks": n_checks, "revision": getattr(IND, "MODULE_REVISION", None)}


def f2_ladder_check(IND, rung_records: list, brec: dict | None) -> bool:
    """Lemma Lad against F2's ladder (key names mapped; metadata dropped)."""
    keep = set(("C_R", "tau", "C_T", "A_bar", "tau_a_up", "S2_up", "TN_up", "D1", "D2", "L1_up", "L2_up",
                "tau_a_lo", "D_lo", "Lambda_lo"))
    rungs = [{F2_LADDER_NAMES.get(k, k): v for k, v in r.items() if k in keep} | {"status": r.get("status")}
             for r in rung_records]
    lad = IND.ladder(rungs)
    if lad is None or brec is None:
        return lad is None and brec is None
    return all(F(brec[k]) == lad[F2_LADDER_NAMES.get(k, k)] for k in keep if k in brec)
