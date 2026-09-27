"""Exact-truth validation of theorem TPT-B (block-resolved profile transport) on finite-state drift families.

For each fixture of validate_tpt_synthetic (same seeds/configs), the cell is split into nb sub-blocks.
Each sub-block gets its OWN certified Lemma-G constants (C_b >= sup_{e in block} ||R_e||, k_i over the block).
Checks:
  B1 pointwise: |F_r''(t)(a) - H_r(a) - (t-e0) G_r(a)| <= rad_r(|t-e0|; A of the block containing t), exact, on a grid;
  B2 transport: rigorous sup_C g <= g_hi + P*_B (adaptive bisection as in V1);
  B3 dominance: P*_B <= P_tpt(cell constants = componentwise max over blocks) <= P_c5t;
  B4 negative control (r2, code path): block constants scaled so that rad_at itself is invalid -> violation;
  B5 transport controls: planted g_hi + theta*P*_B, detected when the exact grid max of g exceeds it.
Writes validation/TPTB_SYNTHETIC.json.
"""
from __future__ import annotations

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


def block_constants(fam, e_lo: F, e_hi: F) -> tuple:
    c, h = (e_lo + e_hi) / 2, (e_hi - e_lo) / 2
    C = V.sup_R_bound(fam, c, h)
    k1, k2 = V.sup_Ki(fam, 1, e_hi), V.sup_Ki(fam, 2, e_hi)
    return C, k1 * C * C, k2 * C * C + 2 * k1 ** 2 * C ** 3


def run_fixture(cfg: tuple, nb: int, grid: int = 400) -> dict:
    seed, n, m, e0, rho, pert, G_mode = cfg
    cp, truth, Rmd, k, C = V.build_fixture(seed, n, m, e0, rho, pert, G_mode)
    fam = X_family = truth[0][0]
    edges = [cp.x_lo + 2 * rho * i / nb for i in range(nb + 1)]
    blocks = [tpt.Block(a, b, *block_constants(X_family, a, b)) for a, b in zip(edges, edges[1:])]
    # cell-level comparator: componentwise max over blocks (a valid cell-uniform supply)
    cell = tpt.CellProfile(**{**cp.__dict__, "A0": max(b.A0 for b in blocks),
                              "A1": max(b.A1 for b in blocks), "A2": max(b.A2 for b in blocks)})
    resB = tpt.penalty_blocked(cell, blocks)
    res_cell = tpt.evaluate(cell)

    def blk_of(t):
        return [b for b in blocks if b.e_lo <= t <= b.e_hi]

    def rad_at(st, t, scale=F(1)):
        s = abs(t - e0)
        vals = []
        for b in blk_of(t):
            A = (b.A0 * scale, b.A1 * scale, b.A2 * scale)
            lo, _ = tpt._lo_hi_with(tpt.CellProfile(**{**cell.__dict__, "terms": [st], "m": 1, "W": (F(0), F(0))}), A)
            # lo(s) = H.lo - rad(s) - s|G| for a single term with W = 0: recover rad(s) + s|G|
            vals.append(st.H_at_a[0] - tpt.peval(lo, s) - s * st.abs_G_at_a)
        return min(vals)  # any containing block is valid; the tightest is the claim under test

    pts = [e0 - rho + 2 * rho * i / grid for i in range(grid + 1)]
    viol = 0
    gvals, Rpp = [], []
    devs = [[] for _ in cell.terms]
    for t in pts:
        for j, ((famr, Hh_a, Gh_a), st) in enumerate(zip(truth, cell.terms)):
            dev = abs(famr.F_derivs(t, 2)[2][0] - Hh_a - (t - e0) * Gh_a)
            devs[j].append(dev)
            if dev > rad_at(st, t):
                viol += 1
        R0, R1, R2 = Rmd(t)
        gvals.append(R0 - t * R1)
        Rpp.append(abs(R2))
    # negative control r2 (REVIEW_TPT_R1 B2): a CODE-PATH plant. Block constants are scaled by
    # lam = (max true dev / 2) / (max rad_at), so rad_at -> tpt._lo_hi_with itself yields an invalid radius;
    # the same comparison must then report >= 1 violation. (r1's control, a count over the truth list only,
    # was a tautology and is withdrawn.)
    maxdev = max(max(d) for d in devs)
    maxrad = max(rad_at(st, t) for t in pts for st in cell.terms)
    lam = (maxdev / 2) / maxrad if maxrad > 0 else F(0)
    viol_nc = sum(1 for i, t in enumerate(pts) for j, st in enumerate(cell.terms) if devs[j][i] > rad_at(st, t, lam))
    theta_detect = {str(th): bool(max(gvals) > cell.g_hi + th * resB["P_star_B"])
                    for th in (F(1, 2), F(9, 10), F(99, 100))}
    B3 = V.third_derivative_bound(cell, truth, k, cell.x_hi, C)
    target = cell.g_hi + resB["P_star_B"]

    def gpt(t):
        R0, R1, R2 = Rmd(t)
        return R0 - t * R1, abs(R2)

    stack = [(pts[i], pts[i + 1], gvals[i], gvals[i + 1], Rpp[i], Rpp[i + 1], 0) for i in range(grid)]
    sup_upper = None
    while stack:
        a, b, ga, gb, ra, rb, d = stack.pop()
        u = max(ga, gb) + (b - a) / 2 * cell.x_hi * (max(ra, rb) + (b - a) / 2 * B3)
        if u > target and d < 16:
            mid = (a + b) / 2
            gm, rm = gpt(mid)
            stack += [(a, mid, ga, gm, ra, rm, d + 1), (mid, b, gm, gb, rm, rb, d + 1)]
            continue
        sup_upper = u if sup_upper is None else max(sup_upper, u)
    return {
        "config": {"seed": seed, "n": n, "m": m, "rho": str(rho), "G_mode": G_mode, "blocks": nb},
        "B1_pointwise_violations": viol,
        "B2_sound_certified": bool(sup_upper <= target),
        "B3_PB_le_Ptpt": bool(resB["P_star_B"] <= res_cell["P_tpt"]),
        "B3_Ptpt_le_Pc5t": bool(res_cell["P_tpt"] <= res_cell["P_c5t"]),
        "B4_negative_control_violations": viol_nc,
        "B5_transport_theta_controls_detected": theta_detect,
        "P_B": float(resB["P_star_B"]), "P_tpt_cellmax": float(res_cell["P_tpt"]),
        "P_c5t_cellmax": float(res_cell["P_c5t"]),
        "PB_over_Ptpt": float(resB["P_star_B"] / res_cell["P_tpt"]) if res_cell["P_tpt"] else None,
        "A0_block_range": [float(min(b.A0 for b in blocks)), float(max(b.A0 for b in blocks))],
    }


def main() -> None:
    t0 = time.time()
    cfgs = []
    for seed in range(1, 13):
        n = 4 + seed % 3
        m = 1 + seed % 3
        rho = [F(1, 64), F(1, 32), F(1, 16)][seed % 3]
        pert = [F(1, 10 ** 6), F(1, 10 ** 4), F(1, 10 ** 3)][seed % 3]
        cfgs.append((seed, n, m, F(1, 8), rho, pert, "zero" if seed % 2 == 0 else "real"))
    rows = [run_fixture(c, nb) for c in cfgs for nb in (2, 4)]
    summ = {
        "fixtures": len(rows),
        "B1_violations_total": sum(r["B1_pointwise_violations"] for r in rows),
        "B2_all_sound": all(r["B2_sound_certified"] for r in rows),
        "B3_all_dominated": all(r["B3_PB_le_Ptpt"] and r["B3_Ptpt_le_Pc5t"] for r in rows),
        "B4_controls_detected": sum(1 for r in rows if r["B4_negative_control_violations"] > 0),
        "B5_theta_detections": {k: sum(1 for r in rows if r["B5_transport_theta_controls_detected"][k])
                                for k in rows[0]["B5_transport_theta_controls_detected"]},
        "tpt_py_sha256": __import__("hashlib").sha256((HERE / "tpt.py").read_bytes()).hexdigest(),
        "PB_over_Ptpt_range": [min(r["PB_over_Ptpt"] for r in rows), max(r["PB_over_Ptpt"] for r in rows)],
        "wall_s": round(time.time() - t0, 1),
    }
    out = {"schema": "OV_TPTB_SYNTHETIC/1", "rows": rows, "summary": summ}
    (NS / "validation" / "TPTB_SYNTHETIC.json").write_text(json.dumps(out, indent=1))
    Q.log_execution("streams/E_assembly/validate_tptb_synthetic.py", "TPT-B exact-truth validation on FSM fixtures",
                    cells_touched=[], klass="SYNTHETIC_VALIDATION")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
