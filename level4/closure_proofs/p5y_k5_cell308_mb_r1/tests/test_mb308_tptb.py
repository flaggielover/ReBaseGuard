"""QC07 (formal part): the Stage-2 entry mb308_consumer.stage2 on MANUFACTURED TC-T bundles (stream ASSEMBLY's
decoy_gen, pinned, label DECOY, geometries outside the band), with planted defects. Decoys only.

  T1  block-triple patterns const / decreasing-to-the-right / increasing / random / drop-after-e0: stage2 passes,
      F2's P_lo <= P_B(primary) exactly, P_B <= P_frozen(S_I1)
  T2  DECREASING-constant regime (coordinator note 2): right-side constants fall after e0, so the right running
      integral rises then falls; the ENDPOINT-ONLY rule max(0, I_right(rho), I_left(rho)) (computed from the primary's
      own penalty_blocked record) must be DETECTED on every case where it differs from P_B (it falls below F2's
      P_lo); at least MIN_RISE_FALL such cases must exist (non-vacuous)
  T3  P_B x (1 - 2^-40) must fail the exact soundness comparison P_lo <= P (whenever P_lo > 0)
  T4  C5 plant (e0 of the cover moved by 10^-9): Stop C5_CELL_IDENTITY
  T5  C6 plant (the K1 cap moved above the centre, tiny block constants): Stop C6_EMPTY_BAND, and F2 refuses the
      same input (consistent refusal)
  T6  reproduction plant (committed H_exact altered by 2^-40): Stop REPRODUCTION_FAILED
  T7  tiling plant (a gap between two tiles): refused
  T8  tripwires: inside `tripwires(..., "target")` penalty_closed / penalty_c5t raise, penalty_blocked does not;
      in "control" mode penalty_blocked raises too; all restored on exit
Every comparison is exact (no tolerance enters a gate).
"""
from __future__ import annotations

import copy
from fractions import Fraction as F

FIELDS = ("A0", "A1", "A2")
SEED = 20260930
MIN_RISE_FALL = 3
GEOMS = [(F(1, 2), F(1, 50)), (F(3), F(1, 32)), (F(1), F(1, 40)), (F(7, 2), F(1, 25))]


def bundles(DG, n_per_geom: int = 6) -> list:
    out = []
    saved = DG.GEOMS
    try:
        for gi, geom in enumerate(GEOMS):
            DG.GEOMS = [geom]
            for k in range(n_per_geom):
                regime = ("taylor", "mixed", "midpoint")[k % 3]
                cap = ("cut", "cut_both", "loose")[(k // 3) % 3]
                sign = 1 if k % 2 == 0 else -1
                out.append(DG.make_decoy(100 * gi + k, SEED, regime, sign, cap, 0))
    finally:
        DG.GEOMS = saved
    return out


def tiles(x_lo: F, x_hi: F, n: int) -> list:
    w = (x_hi - x_lo) / n
    return [(x_lo + i * w, x_lo + (i + 1) * w) for i in range(n)]


def triples(bundle: dict, pattern: str, n: int = 6, rng_seed: int = 0) -> list:
    S = {j: F(bundle["supply"][j]) for j in FIELDS}
    e0, rho = F(bundle["cover"]["e0"]), F(bundle["cover"]["rho"])
    ts = tiles(e0 - rho, e0 + rho, n)
    out = []
    for i, (a, b) in enumerate(ts):
        if pattern == "const":
            u = F(1)
        elif pattern == "decreasing":
            u = F(1, 2 ** (3 * i))
        elif pattern == "increasing":
            u = F(1, 2 ** (3 * (n - 1 - i)))
        elif pattern == "drop_after_e0":
            u = F(1) if a < e0 else F(1, 1000)
        elif pattern == "fall_right":            # constants fall after the first right tile (rise-then-fall right)
            u = F(1) if a <= e0 else F(1, 1000)
        elif pattern == "fall_left":             # mirror: constants fall beyond the first left tile
            u = F(1) if b >= e0 else F(1, 1000)
        else:
            u = F((7 * i + rng_seed) % 11 + 1, 12)
        out.append((a, b, {j: S[j] * u for j in FIELDS}))
    return out


def _stage2(CON, asm, guard, indep, bundle, trip):
    try:
        return CON.stage2(asm, guard, bundle, trip, indep), None
    except CON.Stop as exc:
        return None, exc.code
    except asm["TB"].Stop as exc:
        return None, "TB:" + exc.code
    except CON.IndependentCheckFailed as exc:
        return None, "INDEPENDENT:" + str(exc)[:80]


def endpoint_only(CON, asm, bundle, trip) -> tuple:
    """(P_B, endpoint-only value) from the primary's own penalty_blocked record, outside any tripwire (decoys)."""
    core = CON.repro_core(asm, bundle)
    TPT = asm["TPT"]
    rb = TPT.penalty_blocked(core["cp"], [TPT.Block(e_lo=a, e_hi=b, A0=t["A0"], A1=t["A1"], A2=t["A2"])
                                          for a, b, t in trip])
    return rb["P_star_B"], max(F(0), rb["I_right_full"], rb["I_left_full"])


def run(CON, asm, guard, indep, DG) -> dict:
    if guard.mode() != "DECOY" or indep is None:
        return {"pass": False, "reason": "needs DECOY mode and the F2 module"}
    bs = bundles(DG)
    res = {"T1_cases": 0, "T1_ok": 0, "T2_rise_fall_cases": 0, "T2_detected": 0, "T3_cases": 0, "T3_detected": 0}
    fails = []
    for bi, bundle in enumerate(bs):
        for pat in ("const", "decreasing", "increasing", "drop_after_e0", "fall_right", "fall_left", "random"):
            trip = triples(bundle, pat, rng_seed=bi)
            st2, err = _stage2(CON, asm, guard, indep, bundle, trip)
            res["T1_cases"] += 1
            if st2 is None:
                fails.append((bi, pat, err))
                continue
            f2lo, P_B = F(st2["F2"]["P_lo"]), F(st2["values"]["P_B_primary"])
            ok = f2lo <= P_B <= F(st2["values"]["P_frozen_S_I1"]) and all(
                g.get("pass") is True for g in st2["gates"].values())
            res["T1_ok"] += ok
            if not ok:
                fails.append((bi, pat, "T1"))
            if f2lo > 0:
                res["T3_cases"] += 1
                res["T3_detected"] += not (f2lo <= P_B * (1 - F(1, 2 ** 40)))
            if pat in ("decreasing", "increasing", "drop_after_e0", "fall_right", "fall_left"):
                pb, ep = endpoint_only(CON, asm, bundle, trip)
                if pb != P_B:
                    fails.append((bi, pat, "primary P_B not reproduced"))
                if ep != P_B:
                    res["T2_rise_fall_cases"] += 1
                    res["T2_detected"] += ep < f2lo
    for bi, bundle in enumerate(bs):                         # T2 by construction: a small centre, a wide cap
        for side in ("R", "L"):
            pb_, trip = _rise_fall_bundle(CON, asm, bundle, side)
            st2, err = _stage2(CON, asm, guard, indep, pb_, trip)
            if st2 is None:
                fails.append((bi, "rise_fall_" + side, err))
                continue
            f2lo, P_B = F(st2["F2"]["P_lo"]), F(st2["values"]["P_B_primary"])
            pb, ep = endpoint_only(CON, asm, pb_, trip)
            if pb != P_B or not f2lo <= P_B:
                fails.append((bi, "rise_fall_" + side, "T2"))
            if ep != P_B:
                res["T2_rise_fall_cases"] += 1
                res["T2_detected"] += ep < f2lo
    res["T9_r0_order3_binding_cases"] = 0                    # stream F3 note: make the r = 0 adopted bound bind
    for bi, bundle in enumerate(bs[:8]):
        v = copy.deepcopy(bundle)
        s3 = F(v["meas"]["sup_S0"][3])
        v["aux"]["candidate_suprema"]["Sclosed:0:3"] = str(s3 / 10)
        v["aux"]["midpoint_eps"]["Sclosed:3"] = str(s3 / 1000)
        v.pop("committed", None)
        S = tuple(F(v["supply"][j]) for j in FIELDS)
        binds = asm["F3"].tuple_tct(v["meas"], v["aux"], S)["towers"]["sigma3"][0] < s3
        st2, err = _stage2(CON, asm, guard, indep, v, triples(v, "decreasing"))
        if st2 is None or not binds or st2["gates"]["G-R3b"]["pass"] is not True:
            fails.append((bi, "r0_order3", err or "not binding / G-R3b"))
        else:
            res["T9_r0_order3_binding_cases"] += 1
    res["T1_failures"] = fails[:10]
    base = bs[0]
    res["T4_C5_plant"] = _stage2(CON, asm, guard, indep, _plant_c5(base), triples(base, "const"))[1] == \
        "C5_CELL_IDENTITY"
    c6_bundle, c6_trip = _plant_c6(CON, asm, base)
    res["T5_C6_plant"] = _stage2(CON, asm, guard, indep, c6_bundle, c6_trip)[1] == "C6_EMPTY_BAND"
    res["T5_F2_refuses_same_input"] = _f2_refuses_c6(CON, asm, indep, c6_bundle, c6_trip)
    pl = copy.deepcopy(base)
    pl["committed"]["H_exact"][0] = str(F(pl["committed"]["H_exact"][0]) * (1 + F(1, 2 ** 40)))
    res["T6_reproduction_plant"] = _stage2(CON, asm, guard, indep, pl, triples(base, "const"))[1] == \
        "REPRODUCTION_FAILED"
    gap = triples(base, "const")
    gap[1] = (gap[1][0] + F(1, 10 ** 9), gap[1][1], gap[1][2])
    res["T7_tiling_plant"] = _stage2(CON, asm, guard, indep, base, gap)[1] is not None
    res["T8_tripwires"] = _tripwire_test(CON, asm, indep, base)
    res["T10_G_R3b_common_mode_plant"] = _common_mode_plant(CON, asm, guard, indep, base)
    res["pass"] = (res["T1_ok"] == res["T1_cases"] and not fails and res["T2_rise_fall_cases"] >= MIN_RISE_FALL
                   and res["T2_detected"] == res["T2_rise_fall_cases"] and res["T3_cases"] > 0
                   and res["T3_detected"] == res["T3_cases"] and res["T4_C5_plant"] and res["T5_C6_plant"]
                   and res["T5_F2_refuses_same_input"] and res["T6_reproduction_plant"] and res["T7_tiling_plant"]
                   and res["T8_tripwires"] and res["T9_r0_order3_binding_cases"] == 8
                   and res["T10_G_R3b_common_mode_plant"])
    return res


def _rise_fall_bundle(CON, asm, b: dict, side: str) -> tuple:
    """A manufactured bundle whose band centre is small against the radius (|C| = rad(0)/10, sign chosen so that the
    far tiles of `side` make the integrand negative), a cap that never binds, and 12 tiles: constants S on the tiles
    of `side` except the outermost one, S/1000 elsewhere. The running integral of `side` then rises and falls, so its
    maximum sits at an INTERIOR piece end (THEOREM_MB r1 C4); the other side stays small."""
    TB = asm["TB"]
    p = copy.deepcopy(b)
    p.pop("committed", None)
    p["adopted_m5"]["R2_interval"] = {"lo": "-1000000", "hi": "1000000"}
    p["adopted_m5"]["M_R2"] = "1000000"
    core = CON.repro_core(asm, p)
    S, ext = core["S"], core["ext"]
    rad0 = sum(TB.rad_at(t, S, F(0)) for t in ext["terms"]) / len(ext["terms"])
    w = rad0 / 1000
    if side == "R":
        h = rad0 / 10 - ext["W"][0] + w                  # C_lo = W.lo + h - w = +rad0/10
    else:
        h = -rad0 / 10 - ext["W"][1] - w                 # C_hi = W.hi + h + w = -rad0/10
    for r in p["meas"]["r"].values():
        r["H_at_a"] = [str(h - w), str(h + w)]
    e0, rho = F(p["cover"]["e0"]), F(p["cover"]["rho"])
    ts = tiles(e0 - rho, e0 + rho, 12)
    Sd = {j: F(p["supply"][j]) for j in FIELDS}
    trip = []
    for i, (a, c) in enumerate(ts):
        big = (side == "R" and 6 <= i <= 10) or (side == "L" and 1 <= i <= 5)
        trip.append((a, c, {j: Sd[j] * (F(1) if big else F(1, 1000)) for j in FIELDS}))
    return p, trip


def _common_mode_plant(CON, asm, guard, indep, b: dict) -> bool:
    """Stream F3's finding: a shape error present in BOTH the frozen extraction (and the frozen per-r object) and
    tptb_tail.rederive_tuple that preserves rad_r(rho) for the CELL constants passes every primary gate (G-R1..G-R4,
    G-CF, the profile at rho, P_frozen); only G-R3b catches it. Plant (test only, restored afterwards): fH -> fH - d,
    fG -> fG + dG with A0 dp2 + 2 A1 dp1 + A2 dp0 = 0 at s = rho, applied to the captured tuple, to the frozen per-r
    object's f_G and to rederive_tuple. stage2 must stop with INDEPENDENT (G-R3b)."""
    TB = asm["TB"]
    S = tuple(F(b["supply"][j]) for j in FIELDS)
    rho = F(b["cover"]["rho"])

    def delta(t):
        d = t["fH"] / 4
        dG = d * (S[0] + 2 * S[1] * rho + S[2] * rho ** 2 / 2) / (S[0] * rho + S[1] * rho ** 2 + S[2] * rho ** 3 / 6)
        return d, dG

    orig_direct, orig_extract, orig_red = TB.C2.direct, TB._extract, TB.rederive_tuple

    def direct_m(*a, **k):
        res = orig_direct(*a, **k)
        for r, t in enumerate(_last["terms"]):
            res["obj"][r]["f_G"] = res["obj"][r]["f_G"] + delta(t)[1]
        return res

    _last = {"terms": []}

    def ext_m(cap, meas):
        e = orig_extract(cap, meas)
        for t in e["terms"]:
            d, dG = delta(t)
            t["fH"], t["fG"] = t["fH"] - d, t["fG"] + dG
        return e

    def red_m(meas, aux):
        out = orig_red(meas, aux)
        for t in out.values():
            d, dG = delta(t)
            t["fH"], t["fG"] = t["fH"] - d, t["fG"] + dG
        return out

    # the frozen per-r object needs the ORIGINAL fH to compute the same shift: take it from an unplanted extraction
    core0 = CON.repro_core(asm, b)
    _last["terms"] = [dict(t) for t in core0["ext"]["terms"]]
    TB.C2.direct, TB._extract, TB.rederive_tuple = direct_m, ext_m, red_m
    try:
        st2, err = _stage2(CON, asm, guard, indep, b, triples(b, "decreasing"))
    finally:
        TB.C2.direct, TB._extract, TB.rederive_tuple = orig_direct, orig_extract, orig_red
    return st2 is None and str(err).startswith("INDEPENDENT") and "G-R3b" in str(err)


def _plant_c5(b: dict) -> dict:
    p = copy.deepcopy(b)
    p["cover"]["e0"] = str(F(p["cover"]["e0"]) + F(1, 10 ** 9))
    return p


def _plant_c6(CON, asm, b: dict) -> tuple:
    """Move the K1 cap R2 strictly above the band centre (drop the committed record, which no longer applies) and use
    tiny block constants: the capped band is empty at a piece's inner end while the cell band at s = 0 is not."""
    TB = asm["TB"]
    p = copy.deepcopy(b)
    p.pop("committed", None)
    core = CON.repro_core(asm, p)
    S = core["S"]
    lo0, hi0 = TB.band_at(core["ext"], S, F(0), None)
    _, hi_tiny = TB.band_at(core["ext"], tuple(x / 10 ** 6 for x in S), F(0), None)
    r2lo, r2hi = (hi_tiny + hi0) / 2, hi0 + (hi0 - lo0)      # above every tiny-constant band, below hi0 (N5 holds)
    p["adopted_m5"]["R2_interval"] = {"lo": str(r2lo), "hi": str(r2hi)}
    p["adopted_m5"]["M_R2"] = str(max(abs(r2lo), abs(r2hi)))
    trip = triples(p, "const")
    trip = [(a, c, {j: t[j] / 10 ** 6 for j in FIELDS}) for a, c, t in trip]
    return p, trip


def _f2_refuses_c6(CON, asm, indep, p, trip) -> bool:
    core = CON.repro_core(asm, p)
    try:
        indep.tptb(CON.f2_profile(core), [{"lo": a, "hi": c, **t} for a, c, t in trip])
        return False
    except indep.Refusal as exc:
        return "C6" in str(exc)


def _tripwire_test(CON, asm, indep, b) -> bool:
    TPT = asm["TPT"]
    orig = (TPT.penalty_closed, TPT.penalty_c5t, TPT.penalty_blocked)
    core = CON.repro_core(asm, b)
    out = []
    with CON.tripwires(asm, indep, "target"):
        for fn in (TPT.penalty_closed, TPT.penalty_c5t):
            try:
                fn(core["cp"])
                out.append(False)
            except CON.TripwireFired:
                out.append(True)
        out.append(TPT.penalty_blocked is orig[2])
    with CON.tripwires(asm, indep, "control"):
        try:
            TPT.penalty_blocked(core["cp"], [])
            out.append(False)
        except CON.TripwireFired:
            out.append(True)
    out.append((TPT.penalty_closed, TPT.penalty_c5t, TPT.penalty_blocked) == orig)
    return all(out)
