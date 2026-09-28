"""Stream E (ASSEMBLY), task E4: negative controls THROUGH tptb_tail.evaluate_bundle (synthetic decoys only).

Every control is a pair: the VALID base decoy must return status OK, and the planted defect must return STOP with the
expected stop code (and, where stated, the expected failing gate while the named other gates still PASS). A control
counts as DETECTED only if both halves hold. The plants act at the point where the real defect would enter:
  * the input object (tiling, block constants, label m, M_R2, the K1 cap, committed record, supply);
  * the extracted per-r object right after capture (the G-R3 shape plant, Env4 dropped, m-weights);
  * the frozen call chain (a tampering proxy in place of the capturing proxy);
  * the transport implementation (planted tpt penalty with the sign of t flipped / a mirrored block lookup).
Writes validation/CONTROLS.json.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


DG = _load("c308E_decoy_gen", HERE.parent / "decoy_gen.py")
TB = sys.modules["c308E_tptb_tail"]
Q, TPT = TB.Q, TB.TPT
Q.install_import_guard()
OUT = HERE.parent / "validation" / "CONTROLS.json"


# ------------------------------------------------------------------ extraction plants
def plant_shape(ext):
    """G-R3 class: change (fF, fD, fH, fG, Env4) of every r along the null space of the s = rho Taylor map, so that
    p0(rho), p1(rho), p2(rho) -- hence rad(rho), the whole-cell enclosure and Gamma -- are unchanged, while the
    profile p_j(s) for s < rho is mis-shaped. With dfD = 0: dEnv4 = -3 d/(2 rho), dfH = -rho d/4,
    dfF = rho^3 d/48, dfG = d; here d = -fG/2."""
    rho = ext["rho"]
    for t in ext["terms"]:
        d = -t["fG"] / 2
        t["fG"] += d
        t["Env4"] += -3 * d / (2 * rho)
        t["fH"] += -rho * d / 4
        t["fF"] += rho ** 3 * d / 48


def plant_shape_unsound(ext):
    """as plant_shape with d = +fG/2: the interior profile shrinks (an UNSOUND mis-shape if it went ungated)."""
    rho = ext["rho"]
    for t in ext["terms"]:
        d = t["fG"] / 2
        t["fG"] += d
        t["Env4"] += -3 * d / (2 * rho)
        t["fH"] += -rho * d / 4
        t["fF"] += rho ** 3 * d / 48


def plant_env4_dropped(ext):
    for t in ext["terms"]:
        t["Env4"] = F(0)


def make_plant_m3(bundle):
    meas = bundle["meas"]

    def plant(ext):
        ext["terms"] = ext["terms"][:3]
        W = [F(0), F(0)]
        for kind, r, jj, c in TB.R.coefficients(3):
            if kind == "W":
                a, b = (F(v) for v in meas["W2"][f"{r}:{jj}"])
                W[0] += c * a
                W[1] += c * b
        ext["W"] = tuple(W)
        ext["m_rows"] = 3
    return plant


# ------------------------------------------------------------------ frozen-call-chain plant
class TamperingR(TB.CapturingR):
    """Scales the frozen radius result by 1/2 on its way back to the frozen tail_enclosure: the frozen path's own
    independent crosscheck (tct_rule.tail_enclosure_crosscheck, called inside c2_d5_forecast.direct) must refuse."""

    def __getattr__(self, name):
        w = super().__getattr__(name)
        if name != "radius":
            return w

        def half(*a, **kw):
            return w(*a, **kw) / 2
        return half


# ------------------------------------------------------------------ transport-implementation plants
def closed_with_t(cp, tR, tL):
    """tpt.penalty_closed's formula with the t-weight polynomials replaced (the planted defect); cap split as tpt."""
    lo, hi = TPT.lo_hi_polys(cp)
    rho = cp.rho
    sR = TPT._crossing(lo, cp.H_K1[0], rho, decreasing=True)
    sL = TPT._crossing(hi, cp.H_K1[1], rho, decreasing=False)
    negLo = TPT.pscale(lo, F(-1))
    I_R = TPT.pint(TPT.pmul(tR, negLo), F(0), rho) if sR is None else \
        TPT.pint(TPT.pmul(tR, negLo), F(0), sR) + TPT.pint(TPT.pscale(tR, -cp.H_K1[0]), sR, rho)
    I_L = TPT.pint(TPT.pmul(tL, hi), F(0), rho) if sL is None else \
        TPT.pint(TPT.pmul(tL, hi), F(0), sL) + TPT.pint(TPT.pscale(tL, cp.H_K1[1]), sL, rho)
    return {"P_star": max(F(0), I_R, I_L), "I_right": I_R, "I_left": I_L, "split_right": sR, "split_left": sL}


def pen_t_negated(cp):                       # t -> -t on both sides
    return closed_with_t(cp, [-cp.e0, F(-1)], [-cp.e0, F(1)])


def pen_t_mirrored_right(cp):                # right side weighted by t = e0 - s (validate_tpt_r2 mutant M2)
    return closed_with_t(cp, [cp.e0, F(-1)], [cp.e0, F(-1)])


def pen_t_mirrored_left(cp):                 # left side weighted by t = e0 + s
    return closed_with_t(cp, [cp.e0, F(1)], [cp.e0, F(1)])


def pen_blocked_mirrored(cp, blocks):        # block lookup at the mirror point t -> 2 e0 - t
    mir = [TPT.Block(e_lo=2 * cp.e0 - b.e_hi, e_hi=2 * cp.e0 - b.e_lo, A0=b.A0, A1=b.A1, A2=b.A2) for b in blocks]
    return TPT.penalty_blocked(cp, mir)


# ------------------------------------------------------------------ input-object plants
def blocks_gap(b):
    bl = b["blocks"]
    bl[1]["e_lo"] = str(F(bl[1]["e_lo"]) + (F(bl[1]["e_hi"]) - F(bl[1]["e_lo"])) / 3)


def blocks_overlap(b):
    bl = b["blocks"]
    bl[1]["e_lo"] = str(F(bl[1]["e_lo"]) - (F(bl[0]["e_hi"]) - F(bl[0]["e_lo"])) / 3)


def blocks_short(b):
    bl = b["blocks"]
    bl[-1]["e_hi"] = str(F(bl[-1]["e_hi"]) - (F(bl[-1]["e_hi"]) - F(bl[-1]["e_lo"])) / 5)


def blocks_beyond(b):
    bl = b["blocks"]
    bl[-1]["e_hi"] = str(F(bl[-1]["e_hi"]) + F(1, 10 ** 6))


def blocks_above(b):
    S, _ = TB.supply_from(b, b["meas"])
    b["blocks"][0]["A0"] = str(S[0] * F(11, 10))


def label_m3(b):
    b["label"]["m"] = 3


def m_r2_below_mag(b):
    """the adopted M_R2 below mag(H_final): the frozen consumer then uses M = M_R2 < mag(H_final) (G-R4, N7)."""
    lo, hi = (F(v) for v in b["committed"]["H_exact"])
    R2 = (F(b["adopted_m5"]["R2_interval"]["lo"]), F(b["adopted_m5"]["R2_interval"]["hi"]))
    a, c = max(R2[0], lo), min(R2[1], hi)
    M0 = max(abs(a), abs(c)) * F(99, 100)
    b["adopted_m5"]["M_R2"] = str(M0)
    # keep the decoy's committed record consistent with the planted input, so that ONLY G-R4 can see the defect
    e0, rho = F(b["cover"]["e0"]), F(b["cover"]["rho"])
    g_hi = F(b["adopted_m5"]["R_interval"]["hi"]) - e0 * F(b["adopted_m5"]["D_interval"]["lo"])
    b["committed"]["M_after_exact"] = str(M0)
    b["committed"]["Gamma_exact"] = str(g_hi + rho * (e0 + rho) * M0)


def cap_empty_at_s0(b):
    """K1 cap strictly between the profile's rho-end and its s = 0 value on the lower side: H_final is non-empty but
    the capped band is empty at s = 0 (tpt N5)."""
    S, _ = TB.supply_from(b, b["meas"])
    tup = TB.rederive_tuple(b["meas"], b["aux"])
    W = [F(0), F(0)]
    for kind, r, jj, c in TB.R.coefficients(5):
        if kind == "W":
            x, y = (F(v) for v in b["meas"]["W2"][f"{r}:{jj}"])
            W[0] += c * x
            W[1] += c * y
    ext = {"terms": [tup[r] for r in range(5)], "W": tuple(W), "rho": F(b["meas"]["rho"])}
    lo_r, _ = TB.band_at(ext, S, ext["rho"], None)
    lo_0, _ = TB.band_at(ext, S, F(0), None)
    b["adopted_m5"]["R2_interval"] = {"lo": str(lo_r - 1), "hi": str(lo_0 - (lo_0 - lo_r) / 2)}
    b["adopted_m5"]["M_R2"] = str(max(abs(lo_r - 1), abs(lo_0 - (lo_0 - lo_r) / 2)))
    b.pop("committed", None)


def geometry_mirror(b):
    """sign flip of t in the geometry: the whole cell mirrored to negative drift (x_lo < 0 side)."""
    for d in (b["cover"], b["meas"]):
        e0, rho = F(d["e0"]), F(d["rho"])
        d["e0"], d["left"], d["right"] = str(-e0), str(-e0 - rho), str(-e0 + rho)
    for bl in b.get("blocks") or []:
        bl["e_lo"], bl["e_hi"] = str(-F(bl["e_hi"])), str(-F(bl["e_lo"]))
    b.pop("committed", None)


def committed_H(b):
    b["committed"]["H_exact"][0] = str(F(b["committed"]["H_exact"][0]) - F(1, 10 ** 12))


def committed_Gamma(b):
    b["committed"]["Gamma_exact"] = str(F(b["committed"]["Gamma_exact"]) + F(1, 10 ** 12))


def committed_per_r(b):
    c = b["committed"]["per_r"]["2"]
    c["fG"] = str(F(c["fG"]) * F(1001, 1000))


def supply_inconsistent(b):
    S, _ = TB.supply_from(b, b["meas"])
    b["supply"] = {"A0": str(S[0]), "A1": str(S[1]), "A2": str(S[2] * F(1001, 1000))}


def label_quarantined(b):
    b["label"] = {"detector": "CUSUM", "m": 5, "cell": min(Q.TARGET_CELLS)}


def label_adjacent(b):
    b["label"] = {"detector": "CUSUM", "m": 5, "cell": min(Q.ADJACENT_CELLS)}


def geometry_in_band(b):
    for d in (b["cover"], b["meas"]):
        e0, rho = F(2), F(d["rho"])
        d["e0"], d["left"], d["right"] = str(e0), str(e0 - rho), str(e0 + rho)


# ------------------------------------------------------------------ the control table
def controls(ds):
    right = next(b for b in ds if b["decoy_meta"]["lower_end_binds"] and b["decoy_meta"]["nblocks"] >= 3
                 and b["decoy_meta"]["cap_mode"] == "loose")
    left = next(b for b in ds if not b["decoy_meta"]["lower_end_binds"] and b["decoy_meta"]["nblocks"] >= 3)
    src = next(b for b in ds if b["decoy_meta"]["with_supply_sources"] and b["decoy_meta"]["nblocks"] >= 2)
    mid = next(b for b in ds if b["decoy_meta"]["regime"] == "midpoint" and b["decoy_meta"]["nblocks"] >= 2)
    return [
        # name, base, input plant, eval kwargs, expected stop code, gate expectations
        ("GR3_shape_preserving_rad_rho", right, None, {"mutate": plant_shape}, "REPRODUCTION_FAILED",
         {"fail": ["G-R3"], "pass": ["G-R1", "G-R2"]}),
        ("GR3_shape_preserving_rad_rho_midpoint_regime", mid, None, {"mutate": plant_shape}, "REPRODUCTION_FAILED",
         {"fail": ["G-R3"], "pass": ["G-R1", "G-R2"]}),
        ("GR3_shape_unsound_direction", right, None, {"mutate": plant_shape_unsound}, "REPRODUCTION_FAILED",
         {"fail": ["G-R3"], "pass": ["G-R1", "G-R2"]}),
        ("GR3_shape_unsound_direction_midpoint_regime", mid, None, {"mutate": plant_shape_unsound},
         "REPRODUCTION_FAILED", {"fail": ["G-R3"], "pass": ["G-R1", "G-R2"]}),
        ("env4_dropped", right, None, {"mutate": plant_env4_dropped}, "REPRODUCTION_FAILED",
         {"fail": ["G-R1", "G-R3"]}),
        ("tiling_gap", right, blocks_gap, {}, "BLOCKS_REFUSED", {}),
        ("tiling_overlap", right, blocks_overlap, {}, "BLOCKS_REFUSED", {}),
        ("tiling_short_of_x_hi", right, blocks_short, {}, "BLOCKS_REFUSED", {}),
        ("tiling_beyond_x_hi", right, blocks_beyond, {}, "BLOCKS_REFUSED", {}),
        ("block_constant_above_cell_supply", right, blocks_above, {}, "BLOCKS_REFUSED", {}),
        ("wrong_m_label", right, label_m3, {}, "INPUT_REFUSED", {}),
        ("wrong_m_extraction_weights", right, None, {"mutate": "m3"}, "REPRODUCTION_FAILED",
         {"fail": ["G-R1", "G-R3"]}),
        ("M_consumed_ne_mag_H_final_input", right, m_r2_below_mag, {}, "REPRODUCTION_FAILED",
         {"fail": ["G-R4"], "pass": ["G-R1", "G-R2", "G-R3"]}),
        ("M_consumed_ne_mag_H_final_extraction", left, None, {"mutate": "M"}, "REPRODUCTION_FAILED",
         {"fail": ["G-R4"], "pass": ["G-R1", "G-R2", "G-R3"]}),
        ("empty_intersection_at_s0", right, cap_empty_at_s0, {}, "REPRODUCTION_FAILED", {"fail": ["G-R4"]}),
        ("sign_flip_t_negated", right, None, {"tpt_override": {"penalty_closed": pen_t_negated}},
         "TRANSPORT_CHECK_FAILED", {"fail": ["G-T1"]}),
        ("sign_flip_t_negated_left_binding", left, None, {"tpt_override": {"penalty_closed": pen_t_negated}},
         "TRANSPORT_CHECK_FAILED", {"fail": ["G-T1"]}),
        ("sign_flip_t_mirrored_right", right, None, {"tpt_override": {"penalty_closed": pen_t_mirrored_right}},
         "TRANSPORT_CHECK_FAILED", {"fail": ["G-T1"]}),
        ("sign_flip_t_mirrored_left", left, None, {"tpt_override": {"penalty_closed": pen_t_mirrored_left}},
         "TRANSPORT_CHECK_FAILED", {"fail": ["G-T1"]}),
        ("sign_flip_block_lookup_mirrored", right, None, {"tpt_override": {"penalty_blocked": pen_blocked_mirrored}},
         "TRANSPORT_CHECK_FAILED", {"fail": ["G-T2"]}),
        ("sign_flip_geometry_mirrored", right, geometry_mirror, {}, "INPUT_REFUSED", {}),
        ("frozen_chain_tampered_radius", right, None, {"proxy_factory": TamperingR}, "FROZEN_PATH_REFUSED", {}),
        ("committed_H_mismatch", right, committed_H, {}, "REPRODUCTION_FAILED", {"fail": ["G-R1"]}),
        ("committed_Gamma_mismatch", right, committed_Gamma, {}, "REPRODUCTION_FAILED", {"fail": ["G-R2"]}),
        ("committed_per_r_mismatch", right, committed_per_r, {}, "REPRODUCTION_FAILED", {"fail": ["G-R3"]}),
        ("supply_differs_from_frozen_combine", src, supply_inconsistent, {}, "INPUT_REFUSED", {}),
        ("label_quarantined_target", right, label_quarantined, {}, "GUARD_REFUSED", {}),
        ("label_quarantined_adjacent", right, label_adjacent, {}, "GUARD_REFUSED", {}),
        ("geometry_in_drift_band", right, geometry_in_band, {}, "GUARD_REFUSED", {}),
    ]


def _gate_status(res, name):
    g = res["gates"].get(name)
    return None if g is None else g.get("pass")


def run_control(name, base, plant, kw, expected, gexp) -> dict:
    valid = TB.evaluate_bundle(copy.deepcopy(base))
    b = copy.deepcopy(base)
    if plant is not None:
        plant(b)
    kw = dict(kw)
    if kw.get("mutate") == "m3":
        kw["mutate"] = make_plant_m3(b)
    elif kw.get("mutate") == "M":
        mag = F(valid["gates"]["G-R4"]["mag_H_final"])

        def plant_M(ext, mag=mag):
            ext["M_consumed_override"] = mag * F(99, 100)
        kw["mutate"] = plant_M
    seen = {}
    if name.startswith("GR3_shape"):             # keep the mutated object to show the gate is load-bearing
        inner = kw["mutate"]

        def keep(ext, inner=inner):
            inner(ext)
            seen["ext"] = copy.deepcopy(ext)
        kw["mutate"] = keep
    res = TB.evaluate_bundle(b, **kw)
    consequence = None
    if "ext" in seen and valid["status"] == "OK":
        ext = seen["ext"]
        S = tuple(F(valid["supply"][j]) for j in TB.FIELDS)
        cap = tuple(F(v) for v in valid["values"]["H_final"])
        P_mut = TB.independent_penalty(ext, [(ext["x_lo"], ext["x_hi"], S)], cap)["P_hi"]
        P_ok = F(valid["values"]["P_tpt"])
        consequence = {"note": "decoy only: TPT penalty the mis-shaped tuple would give if G-R3 were absent",
                       "P_tpt_valid": float(P_ok), "P_tpt_mis_shaped_independent": float(P_mut),
                       "ratio": float(P_mut / P_ok) if P_ok else None,
                       "mis_shaped_has_negative_coefficient": any(t[x] < 0 for t in ext["terms"] for x in TB.TUPLE)}
    gate_obs = {g: _gate_status(res, g) for g in ("G-R1", "G-R2", "G-R3", "G-R4", "G-T1", "G-T2", "G-D")}
    gates_ok = all(gate_obs.get(g) is False for g in gexp.get("fail", [])) and \
        all(gate_obs.get(g) is True for g in gexp.get("pass", []))
    detected = valid["status"] == "OK" and res["status"] == "STOP" and res.get("stop_code") == expected and gates_ok
    return {"control": name, "base_decoy": base["decoy_meta"]["index"], "valid_status": valid["status"],
            "planted_status": res["status"], "expected_code": expected, "observed_code": res.get("stop_code"),
            "observed_reason": res.get("stop_reason"), "gate_expectation": gexp, "gates_observed": gate_obs,
            "gate_expectation_met": gates_ok, "DETECTED": detected, "ungated_consequence": consequence}


def main() -> None:
    t0 = time.time()
    ds = DG.decoy_set()
    rows = [run_control(*c) for c in controls(ds)]
    summ = {"controls": len(rows), "detected": sum(1 for r in rows if r["DETECTED"]),
            "all_detected": all(r["DETECTED"] for r in rows),
            "valid_halves_ok": all(r["valid_status"] == "OK" for r in rows),
            "not_detected": [r["control"] for r in rows if not r["DETECTED"]],
            "tptb_tail_sha256": TB.sha256_file(HERE.parent / "tptb_tail.py"),
            "controls_sha256": TB.sha256_file(HERE),
            "wall_s": round(time.time() - t0, 1)}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"schema": "C308_STREAM_E_CONTROLS/1", "class": "SYNTHETIC_VALIDATION",
                               "summary": summ, "rows": rows}, indent=1, default=str))
    Q.log_event("streams/ASSEMBLY/controls.py", "E4: negative controls through tptb_tail on decoys",
                klass="SYNTHETIC_VALIDATION", agent="streamE",
                notes="guard controls use Q.TARGET_CELLS / ADJACENT_CELLS labels on DECOY data; refused before any load")
    print(json.dumps(summ, indent=1))
    for r in rows:
        print(f"{r['control']:48s} valid={r['valid_status']:4s} planted={r['planted_status']:4s} "
              f"code={r['observed_code']} DETECTED={r['DETECTED']}")


if __name__ == "__main__":
    main()
