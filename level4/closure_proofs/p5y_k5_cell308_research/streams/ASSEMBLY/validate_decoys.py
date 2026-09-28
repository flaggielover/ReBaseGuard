"""Stream E (ASSEMBLY), task E3: validation of tptb_tail.py on manufactured TC-T-shaped decoys (synthetic only).

Per decoy (decoy_gen.decoy_set: 3 radius regimes x 2 centre signs x 3 cap modes, 1-6 blocks):
  V-G   every gate of tptb_tail passes (G-R1..G-R4, G-T1, G-T2 incl. an interior grid scan of the running integral,
        G-D, and G-CF where the binding-regime closed form applies);
  V-D   dominance  P_B <= P_TPT <= P_C5T <= P_frozen  (also a gate);
  V-S1  relaxed extremal witness of the BLOCK band (R'' = L_B right of e0, U_B left; measurable, inside the band):
        its sup g - g_hi lies in the independent certified bracket [P_lo, P_hi]; P_B >= P_hi certifies
        P_B >= sup g (soundness) and P_B - P_lo <= tol shows the bound is attained in the relaxed class (sharpness);
  V-S2  C^2 test functions: R''(t) = c + a u + b u^2 (u = t - e0), certified to lie inside the block band and the
        consumed cap (piecewise monotone bounds), g(e0) = g_hi (worst case); certified UPPER bound of sup g by
        adaptive bisection with an exact Lipschitz bound (V1/V2 methodology of validate_tpt_r2.py) must be
        <= g_hi + P_B; a tightness ratio (grid max - g_hi) / P_B is recorded;
  V-C   transport-level controls through the same code path: (i) planted bounds g_hi + theta P_B, theta in
        {1/2, 9/10, 99/100, 999/1000}, DETECTED when the certified lower bound P_lo of the witness sup exceeds them;
        (ii) tpt.penalty_blocked fed block constants scaled by 1/2 (an invalid band): DETECTED when the valid band's
        witness lower bound exceeds the planted P.
Determinism: the canonical exact output is recomputed in a second process and its sha256 must be identical.
Writes validation/DECOY_VALIDATION.json (under this stream's directory).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import subprocess
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
Q = TB.Q
Q.install_import_guard()
OUT = HERE.parent / "validation" / "DECOY_VALIDATION.json"
THETAS = (F(1, 2), F(9, 10), F(99, 100), F(999, 1000))


def rebuild_ext(bundle: dict, res: dict) -> tuple:
    """The extracted object as tptb_tail consumed it (exact strings -> Fractions)."""
    v = res["values"]
    e0, rho = F(v["e0"]), F(v["rho"])
    terms = [{x: F(t[x]) for x in TB.TUPLE + ("abs_G",)} | {"H_at_a": tuple(F(y) for y in t["H_at_a"])}
             for t in res["extracted_tuple"]]
    ext = {"terms": terms, "W": tuple(F(y) for y in res["W_sum"]), "e0": e0, "rho": rho, "x_lo": e0 - rho,
           "x_hi": e0 + rho}
    S = tuple(F(res["supply"][j]) for j in TB.FIELDS)
    cap = tuple(F(y) for y in v["H_final"])
    bl = TB.check_blocks(bundle["blocks"], ext["x_lo"], ext["x_hi"], S) if bundle.get("blocks") \
        else [(ext["x_lo"], ext["x_hi"], S)]
    return ext, S, cap, bl, F(v["g_hi"])


# ------------------------------------------------------------------ V-S2: C^2 polynomial test functions
def _sub_bounds(ext, bl, cap, N=16):
    """per (side, sub-interval [u1, u2] in s): (L at u1, U at u1) = (sup L, inf U) on the sub-interval."""
    rows = []
    for side in ("R", "L"):
        for sa, sb, A in TB._pieces(ext, bl, side):
            for i in range(N):
                u1, u2 = sa + (sb - sa) * i / N, sa + (sb - sa) * (i + 1) / N
                Lb, Ub = TB.band_at(ext, A, u1, cap)
                rows.append((side, u1, u2, Lb, Ub))
    return rows


def _quad_range(c, a, b, u1, u2):
    vals = [c + a * u1 + b * u1 ** 2, c + a * u2 + b * u2 ** 2]
    if b != 0:
        v = -a / (2 * b)
        if u1 < v < u2:
            vals.append(c + a * v + b * v ** 2)
    return min(vals), max(vals)


def contained(rows, c, a, b) -> bool:
    for side, u1, u2, Lb, Ub in rows:
        aa = a if side == "R" else -a          # f as a function of s: c + a u + b u^2 with u = +-s
        mn, mx = _quad_range(c, aa, b, u1, u2)
        if mn < Lb or mx > Ub:
            return False
    return True


def g_poly(ext, g0, c, a, b):
    e0 = ext["e0"]

    def g(u):          # g(e0 + u) = g0 - int_0^u (e0 + v) f(v) dv,  f(v) = c + a v + b v^2
        return g0 - (e0 * c * u + (c + e0 * a) * u ** 2 / 2 + (a + e0 * b) * u ** 3 / 3 + b * u ** 4 / 4)
    return g


def certified_sup(ext, g, c, a, b, target, depth_max=40, n0=64):
    rho, e0 = ext["rho"], ext["e0"]
    stack = [(-rho + 2 * rho * i / n0, -rho + 2 * rho * (i + 1) / n0, 0) for i in range(n0)]
    sup_up, sup_lo = None, None
    while stack:
        u1, u2, d = stack.pop()
        g1, g2 = g(u1), g(u2)
        sup_lo = max(g1, g2) if sup_lo is None else max(sup_lo, g1, g2)
        Um = max(abs(u1), abs(u2))
        lip = (e0 + Um) * (abs(c) + abs(a) * Um + abs(b) * Um ** 2)
        bound = max(g1, g2) + (u2 - u1) / 2 * lip
        if bound > target and d < depth_max:
            mid = (u1 + u2) / 2
            stack += [(u1, mid, d + 1), (mid, u2, d + 1)]
            continue
        sup_up = bound if sup_up is None else max(sup_up, bound)
    return sup_up, sup_lo


def poly_tests(ext, bl, cap, g_hi, P_B, rng, n=6) -> list:
    m = len(ext["terms"])
    C_lo = ext["W"][0] + sum(t["H_at_a"][0] for t in ext["terms"]) / m
    C_hi = ext["W"][1] + sum(t["H_at_a"][1] for t in ext["terms"]) / m
    c_lo, c_hi = max(C_lo, cap[0]), min(C_hi, cap[1])
    rows = _sub_bounds(ext, bl, cap)
    rho = ext["rho"]
    width = max(r[4] - r[3] for r in rows)
    out = []
    for i in range(n):
        c = c_lo + (c_hi - c_lo) * F(rng.randint(0, 1000), 1000)
        a0 = width / rho * F(rng.randint(-1000, 1000), 1000)
        b0 = width / rho ** 2 * F(rng.randint(-1000, 1000), 1000)
        if not contained(rows, c, F(0), F(0)):
            out.append({"skipped": "constant not inside the band"})
            continue
        lo_l, hi_l = F(0), F(1)
        while contained(rows, c, a0 * hi_l, b0 * hi_l) and hi_l < 2 ** 20:
            hi_l *= 2
        for _ in range(24):                    # largest scale keeping the function certified inside the band
            mid = (lo_l + hi_l) / 2
            if contained(rows, c, a0 * mid, b0 * mid):
                lo_l = mid
            else:
                hi_l = mid
        a, b = a0 * lo_l, b0 * lo_l
        g = g_poly(ext, g_hi, c, a, b)
        target = g_hi + P_B
        sup_up, sup_lo = certified_sup(ext, g, c, a, b, target)
        out.append({"sound_certified": sup_up <= target,
                    "tightness_grid": float((sup_lo - g_hi) / P_B) if P_B else None,
                    "c": str(c), "a": str(a), "b": str(b)})
    return out


# ------------------------------------------------------------------ one decoy
def run_decoy(bundle: dict) -> dict:
    meta = bundle["decoy_meta"]
    res = TB.evaluate_bundle(bundle, grid_per_piece=6)
    row = {"meta": meta, "status": res["status"]}
    if res["status"] != "OK":
        row.update(stop_code=res.get("stop_code"), stop_reason=res.get("stop_reason"))
        return row
    g = res["gates"]
    row["gates"] = {k: v.get("pass") for k, v in g.items()}
    row["gate_detail"] = {"G-T1_exact_equal": g["G-T1"]["exact_equal"], "G-T2_exact_equal": g["G-T2"]["exact_equal"],
                          "G-T1_certified_ge_true_sup": g["G-T1"]["certified_ge_true_sup"],
                          "G-T2_certified_ge_true_sup": g["G-T2"]["certified_ge_true_sup"],
                          "G-T1_interior_scan": g["G-T1"].get("interior_scan_le_P"),
                          "G-T2_interior_scan": g["G-T2"].get("interior_scan_le_P"),
                          "G-R3_committed_checked": g["G-R3"]["committed_per_r_checked"],
                          "G-CF_applies": g["G-CF"]["applies"]}
    v = res["values"]
    row["values"] = v
    P_B, P_t, P_c, P_f = (F(v[k]) for k in ("P_B", "P_tpt", "P_c5t", "P_frozen"))
    row["dominance"] = P_B <= P_t <= P_c <= P_f
    row["ratios_decoy_only"] = {"PB_over_Ptpt": float(P_B / P_t) if P_t else None,
                                "Ptpt_over_Pc5t": float(P_t / P_c) if P_c else None,
                                "Pc5t_over_Pfrozen": float(P_c / P_f) if P_f else None}
    ext, S, cap, bl, g_hi = rebuild_ext(bundle, res)
    # V-S1 witness
    ind = TB.independent_penalty(ext, bl, cap)
    tol = TB.split_tolerance(ext, S, cap, 2 * len(TB.bl_pieces_hint(ext, bl)))
    row["V-S1_witness"] = {"P_lo": str(ind["P_lo"]), "P_hi": str(ind["P_hi"]),
                           "sound_certified": P_B >= ind["P_hi"], "attained_within_tol": P_B - ind["P_lo"] <= tol,
                           "tol": str(tol)}
    # V-S2 polynomial C^2 functions
    rng = random.Random(7919 * (meta["index"] + 1))
    pt = poly_tests(ext, bl, cap, g_hi, P_B, rng)
    row["V-S2_poly"] = {"n": len(pt), "n_sound": sum(1 for x in pt if x.get("sound_certified")),
                        "n_skipped": sum(1 for x in pt if "skipped" in x),
                        "tightness_max": max((x["tightness_grid"] for x in pt if x.get("tightness_grid") is not None),
                                             default=None),
                        "rows": pt}
    # V-C controls
    row["V-C_theta_detected"] = {str(th): ind["P_lo"] > th * P_B for th in THETAS} if P_B > 0 else None
    terms = [TB.TPT.SourceTerm(H_at_a=t["H_at_a"], abs_G_at_a=t["abs_G"], fF=t["fF"], fD=t["fD"], fH=t["fH"],
                               fG=t["fG"], Env4=t["Env4"]) for t in ext["terms"]]
    cp = TB.TPT.CellProfile(detector="DECOY", m=5, cell=meta["index"] + 9000, e0=ext["e0"], rho=ext["rho"],
                            g_hi=g_hi, A0=S[0], A1=S[1], A2=S[2], terms=terms, W=ext["W"], H_K1=cap)
    bad = [TB.TPT.Block(e_lo=a, e_hi=b, A0=A[0] / 2, A1=A[1] / 2, A2=A[2] / 2) for (a, b, A) in bl]
    P_bad = TB.TPT.penalty_blocked(cp, bad)["P_star_B"]
    row["V-C_invalid_constants"] = {"P_planted": float(P_bad), "detected": ind["P_lo"] > P_bad}
    return row


def canonical(rows) -> bytes:
    keep = [{"meta": r["meta"], "status": r["status"], "values": r.get("values"), "gates": r.get("gates"),
             "V-S1": r.get("V-S1_witness"), "V-S2": [x.get("c", "") + x.get("a", "") + x.get("b", "")
                                                     for x in r.get("V-S2_poly", {}).get("rows", [])]}
            for r in rows]
    return json.dumps(keep, sort_keys=True).encode()


def main() -> None:
    t0 = time.time()
    rows = [run_decoy(b) for b in DG.decoy_set()]
    can = canonical(rows)
    sha = hashlib.sha256(can).hexdigest()
    if "--canonical-only" in sys.argv:
        print(sha)
        return
    p2 = subprocess.run([sys.executable, "-I", "-B", str(HERE), "--canonical-only"], capture_output=True, text=True)
    sha2 = p2.stdout.strip().splitlines()[-1] if p2.stdout.strip() else "none"
    ok = [r for r in rows if r["status"] == "OK"]
    summ = {
        "decoys": len(rows), "status_ok": len(ok),
        "all_gates_pass": all(all(x is not False for x in r["gates"].values()) for r in ok),
        "G-CF_applied": sum(1 for r in ok if r["gate_detail"]["G-CF_applies"]),
        "dominance_all": all(r["dominance"] for r in ok),
        "G-T_exact_equal_count": sum(1 for r in ok if r["gate_detail"]["G-T2_exact_equal"]),
        "V-S1_sound_certified": sum(1 for r in ok if r["V-S1_witness"]["sound_certified"]),
        "V-S1_attained_within_tol": sum(1 for r in ok if r["V-S1_witness"]["attained_within_tol"]),
        "V-S2_functions": sum(r["V-S2_poly"]["n"] - r["V-S2_poly"]["n_skipped"] for r in ok),
        "V-S2_sound_certified": sum(r["V-S2_poly"]["n_sound"] for r in ok),
        "V-S2_tightness_max_over_decoys": max(r["V-S2_poly"]["tightness_max"] or 0 for r in ok),
        "V-C_theta_detected": {str(th): sum(1 for r in ok if r["V-C_theta_detected"]
                                            and r["V-C_theta_detected"][str(th)]) for th in THETAS},
        "V-C_invalid_constants_detected": sum(1 for r in ok if r["V-C_invalid_constants"]["detected"]),
        "regimes_realized": sorted({(r["meta"]["regime"], r["meta"]["centre_sign_realized"], r["meta"]["cap_mode"])
                                    for r in ok}),
        "radius_taylor_share_by_regime": {reg: [min(r["meta"]["radius_decomposition"]["taylor_share"] for r in ok
                                                    if r["meta"]["regime"] == reg),
                                                max(r["meta"]["radius_decomposition"]["taylor_share"] for r in ok
                                                    if r["meta"]["regime"] == reg)]
                                          for reg in ("taylor", "midpoint", "mixed")},
        "ratio_ranges_decoy_only": {k: [min(r["ratios_decoy_only"][k] for r in ok),
                                        max(r["ratios_decoy_only"][k] for r in ok)]
                                    for k in ("PB_over_Ptpt", "Ptpt_over_Pc5t", "Pc5t_over_Pfrozen")},
        "determinism": {"sha256_process_1": sha, "sha256_process_2": sha2, "identical": sha == sha2},
        "loader_record": TB.FP.record(),
        "tptb_tail_sha256": TB.sha256_file(HERE.parent / "tptb_tail.py"),
        "decoy_gen_sha256": TB.sha256_file(HERE.parent / "decoy_gen.py"),
        "wall_s": round(time.time() - t0, 1),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"schema": "C308_STREAM_E_DECOY_VALIDATION/1", "class": "SYNTHETIC_VALIDATION",
                               "summary": summ, "rows": rows}, indent=1, default=str))
    Q.log_event("streams/ASSEMBLY/validate_decoys.py",
                "E3: tptb_tail gates, dominance, witness/C2 soundness, controls and determinism on 18 TC-T-shaped decoys",
                klass="SYNTHETIC_VALIDATION", agent="streamE",
                notes="decoy labels DECOY 9000+, geometries outside the band; no CUSUM cell, no tail figure")
    print(json.dumps({k: v for k, v in summ.items() if k != "loader_record"}, indent=1, default=str))


if __name__ == "__main__":
    main()
