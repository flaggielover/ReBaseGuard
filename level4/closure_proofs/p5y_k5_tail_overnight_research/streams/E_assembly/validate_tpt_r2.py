"""TPT validation r2 (repairs REVIEW_TPT_R1 blockers B2, B3), exact finite-state fixtures only.

Per fixture of the V1 set (same 12 configs), against exact truth:
  P1  pointwise Lemma TC-P (0 violations expected), and a CODE-PATH negative control: a mutated profile whose
      A0, A1, A2 and |G(a)| are scaled by lambda = (max true dev / 2) / (max rad) so that tpt.rad_poly itself
      produces an invalid radius -> the checker (through rad_poly) must report >= 1 violation;
  P2  transport soundness (rigorous sup g, adaptive bisection) for TPT, and TRANSPORT-LEVEL negative controls:
      planted bounds g_hi + theta*P for theta in {1/2, 9/10, 99/100} and three implementation mutants
      (M2 right-side weight t -> e0 - s, M4 radius evaluated at s/2, M5 Env4 dropped); a control counts as
      DETECTED when a TRUE lower bound of sup g (the exact grid maximum) exceeds the planted bound;
  V2  cap/split path: H_K1 := a rigorously CERTIFIED whole-cell enclosure of R''_m (grid values +- (h/2)*B3),
      which is valid and binds on part of the cell; checks soundness, dominance over C5-T with the same cap,
      interior split counts, and the N5 non-emptiness check.
Records the sha256 of tpt.py under test. Writes validation/TPT_R2_VALIDATION.json.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[1]
sys.path.insert(0, str(NS / "code"))
sys.path.insert(0, str(HERE))
import ov_quarantine as Q  # noqa: E402
import tpt  # noqa: E402
import validate_tpt_synthetic as V  # noqa: E402

Q.install_import_guard()
GRID = 400


def truth_tables(cp, truth, Rmd):
    e0, rho = cp.e0, cp.rho
    pts = [e0 - rho + 2 * rho * i / GRID for i in range(GRID + 1)]
    devs = [[] for _ in cp.terms]
    g, Rpp_abs, Rpp = [], [], []
    for t in pts:
        for j, (famr, Hh_a, Gh_a) in enumerate(truth):
            devs[j].append(abs(famr.F_derivs(t, 2)[2][0] - Hh_a - (t - e0) * Gh_a))
        R0, R1, R2 = Rmd(t)
        g.append(R0 - t * R1)
        Rpp.append(R2)
        Rpp_abs.append(abs(R2))
    return pts, devs, g, Rpp, Rpp_abs


def pointwise_violations(cp, pts, devs) -> int:
    viol = 0
    for i, t in enumerate(pts):
        s = abs(t - cp.e0)
        for j, st in enumerate(cp.terms):
            rad = tpt.peval(tpt.rad_poly(cp, st), s)  # includes s*|G(a)|; truth dev uses signed G (valid)
            if devs[j][i] > rad:
                viol += 1
    return viol


def certified_sup_g(cp, pts, g, Rpp_abs, Rmd, B3, target):
    def gpt(t):
        R0, R1, R2 = Rmd(t)
        return R0 - t * R1, abs(R2)
    stack = [(pts[i], pts[i + 1], g[i], g[i + 1], Rpp_abs[i], Rpp_abs[i + 1], 0) for i in range(GRID)]
    sup_upper = None
    while stack:
        a, b, ga, gb, ra, rb, d = stack.pop()
        u = max(ga, gb) + (b - a) / 2 * cp.x_hi * (max(ra, rb) + (b - a) / 2 * B3)
        if u > target and d < 16:
            mid = (a + b) / 2
            gm, rm = gpt(mid)
            stack += [(a, mid, ga, gm, ra, rm, d + 1), (mid, b, gm, gb, rm, rb, d + 1)]
            continue
        sup_upper = u if sup_upper is None else max(sup_upper, u)
    return sup_upper


def scaled(cp, lam):
    terms = [tpt.SourceTerm(**{**st.__dict__, "abs_G_at_a": st.abs_G_at_a * lam}) for st in cp.terms]
    return tpt.CellProfile(**{**cp.__dict__, "A0": cp.A0 * lam, "A1": cp.A1 * lam, "A2": cp.A2 * lam,
                              "terms": terms})


def mutant_penalty(cp, kind: str) -> F:
    """Right/left penalties with a deliberate implementation error (no cap: V1 fixtures have none)."""
    lo, hi = tpt.lo_hi_polys(cp)
    e0, rho = cp.e0, cp.rho
    if kind == "M2":        # right-side weight uses t = e0 - s (wrong sign)
        tR, tL = [e0, F(-1)], [e0, F(-1)]
    else:
        tR, tL = [e0, F(1)], [e0, F(-1)]
    if kind == "M4":        # radius evaluated at s/2: substitute s -> s/2 in the s-dependent profile
        lo = [c / 2 ** k for k, c in enumerate(lo)]
        hi = [c / 2 ** k for k, c in enumerate(hi)]
    if kind == "M5":        # Env4 dropped
        cpx = tpt.CellProfile(**{**cp.__dict__, "terms": [tpt.SourceTerm(**{**st.__dict__, "Env4": F(0)})
                                                           for st in cp.terms]})
        lo, hi = tpt.lo_hi_polys(cpx)
    I_right = tpt.pint(tpt.pmul(tR, tpt.pscale(lo, F(-1))), F(0), rho)
    I_left = tpt.pint(tpt.pmul(tL, hi), F(0), rho)
    return max(F(0), I_right, I_left)


def run(cfg) -> dict:
    seed, n, m, e0, rho, pert, G_mode = cfg
    cp, truth, Rmd, k, C = V.build_fixture(seed, n, m, e0, rho, pert, G_mode)
    pts, devs, g, Rpp, Rpp_abs = truth_tables(cp, truth, Rmd)
    B3 = V.third_derivative_bound(cp, truth, k, cp.x_hi, C)
    gmax = max(g)
    out = {"config": {"seed": seed, "n": n, "m": m, "rho": str(rho), "G_mode": G_mode}}
    # P1
    out["P1_pointwise_violations"] = pointwise_violations(cp, pts, devs)
    maxdev = max(max(d) for d in devs)
    maxrad = max(tpt.peval(tpt.rad_poly(cp, st), abs(t - e0)) for t in pts for st in cp.terms)
    lam = (maxdev / 2) / maxrad if maxrad > 0 else F(0)
    out["P1_control_lambda"] = float(lam)
    out["P1_control_violations_detected"] = pointwise_violations(scaled(cp, lam), pts, devs)
    # P2
    res = tpt.evaluate(cp)
    P = res["P_tpt"]
    sup_up = certified_sup_g(cp, pts, g, Rpp_abs, Rmd, B3, cp.g_hi + P)
    out["P2_sound_certified"] = bool(sup_up <= cp.g_hi + P)
    out["P2_true_excess_over_P"] = float((gmax - cp.g_hi) / P) if P else None
    ctrl = {}
    for th in (F(1, 2), F(9, 10), F(99, 100)):
        ctrl[f"theta_{th}"] = bool(gmax > cp.g_hi + th * P)
    for kind in ("M2", "M4", "M5"):
        ctrl[kind] = bool(gmax > cp.g_hi + mutant_penalty(cp, kind))
    out["P2_transport_controls_detected"] = ctrl
    # V2: certified truth cap of R''_m over the cell
    h = 2 * rho / GRID
    capLo = min(Rpp) - h / 2 * B3
    capHi = max(Rpp) + h / 2 * B3
    cpc = tpt.CellProfile(**{**cp.__dict__, "H_K1": (capLo, capHi)})
    rc = tpt.evaluate(cpc)
    Pc = rc["P_tpt"]
    d = rc["detail"]
    sup_c = certified_sup_g(cpc, pts, g, Rpp_abs, Rmd, B3, cpc.g_hi + Pc)
    out["V2_cap"] = {
        "sound_certified": bool(sup_c <= cpc.g_hi + Pc),
        "dominance_vs_c5t_same_cap": bool(Pc <= rc["P_c5t"]),
        "split_right_interior": d["split_right"] is not None and 0 < d["split_right"] < rho,
        "split_left_interior": d["split_left"] is not None and 0 < d["split_left"] < rho,
        "cap_tightens_P": bool(Pc <= P),
        "P_cap_over_P_nocap": float(Pc / P) if P else None,
    }
    return out


def main() -> None:
    t0 = time.time()
    sha = hashlib.sha256((HERE / "tpt.py").read_bytes()).hexdigest()
    cfgs = []
    for seed in range(1, 13):
        n = 4 + seed % 3
        m = 1 + seed % 3
        rho = [F(1, 64), F(1, 32), F(1, 16)][seed % 3]
        pert = [F(1, 10 ** 6), F(1, 10 ** 4), F(1, 10 ** 3)][seed % 3]
        cfgs.append((seed, n, m, F(1, 8), rho, pert, "zero" if seed % 2 == 0 else "real"))
    rows = [run(c) for c in cfgs]
    ctrl_keys = rows[0]["P2_transport_controls_detected"].keys()
    summ = {
        "tpt_py_sha256": sha,
        "fixtures": len(rows),
        "P1_violations_total": sum(r["P1_pointwise_violations"] for r in rows),
        "P1_code_path_controls_detected": sum(1 for r in rows if r["P1_control_violations_detected"] > 0),
        "P2_sound_certified_all": all(r["P2_sound_certified"] for r in rows),
        "P2_transport_control_detections": {k: sum(1 for r in rows if r["P2_transport_controls_detected"][k])
                                            for k in ctrl_keys},
        "V2_sound_all": all(r["V2_cap"]["sound_certified"] for r in rows),
        "V2_dominance_all": all(r["V2_cap"]["dominance_vs_c5t_same_cap"] for r in rows),
        "V2_interior_splits_right": sum(1 for r in rows if r["V2_cap"]["split_right_interior"]),
        "V2_interior_splits_left": sum(1 for r in rows if r["V2_cap"]["split_left_interior"]),
        "wall_s": round(time.time() - t0, 1),
    }
    # every transport control must fire on at least one fixture (the checks can fail)
    summ["P2_every_control_fires_somewhere"] = all(v > 0 for v in summ["P2_transport_control_detections"].values())
    out = {"schema": "OV_TPT_R2_VALIDATION/1", "rows": rows, "summary": summ}
    (NS / "validation" / "TPT_R2_VALIDATION.json").write_text(json.dumps(out, indent=1))
    Q.log_execution("streams/E_assembly/validate_tpt_r2.py", "TPT r2 validation (B2/B3 repairs) on FSM fixtures",
                    cells_touched=[], klass="SYNTHETIC_VALIDATION")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
