"""Numerical-stability follow-up to d309_hermite.py H3: Taylor-form (centred) range bounds for the certified composite sup.
NON-TARGET DRIFTS ONLY ({1/4, 3}); guard_drift at every entry point.

Finding being addressed (validation/D309_HERMITE_NONTARGET.json, H3): the naive monomial interval evaluation of a
degree-9 test polynomial on image boxes of width ~0.37 is vacuous (certified upper ~10^4 x the grid lower bound), while it
is 1.5-4x for low-degree test functions.  Cause: the monomial expansion of y(1 - (y/L)^2)^4 about m = 0 has large
cancelling coefficients (dependency problem).  Remedy tested here (declared before this run): expand each w_i exactly
about the image-box centre and bound the non-constant part by sum |a_ij| r_p^i r_m^j (Taylor/centred form, exact
rationals); expand the combined Hermite weight sum_i c_i (-1)^i He_i(z+e) about the panel centre when the triple uses one
function for every order (so the weight cancellation is kept); depth 4 and 5 box covers, panel width 1/16.
Writes validation/D309_HERMITE_TF_NONTARGET.json.
"""
from __future__ import annotations

import json
import math
import sys
import time
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d309_hermite as H  # noqa: E402

D, Q, G, C11 = H.D, H.Q, H.G, H.C11

DECLARED_RULE = ("Triples (w_quad, w_lin, w_const) and (w_bump, w_bump, w_bump) as in d309_hermite H3; drifts {1/4, 3}; "
                 "Taylor-form image-box bounds; depth 4 for both triples, depth 5 for the bump triple; panel 1/16. "
                 "Soundness: certified upper >= grid lower (grid of d309_hermite H2). Fixed before this run.")


def shift2(w: dict, cp: F, cm: F) -> dict:
    """coefficients of w(cp + dp, cm + dm) in (dp, dm)."""
    out: dict = {}
    for (i, j), c in w.items():
        for a in range(i + 1):
            ca = c * math.comb(i, a) * cp ** (i - a)
            if ca == 0:
                continue
            for b in range(j + 1):
                v = ca * math.comb(j, b) * cm ** (j - b)
                if v:
                    out[(a, b)] = out.get((a, b), F(0)) + v
    return out


def tf_range2(w: dict, P: tuple, M: tuple) -> G.Iv:
    cp, cm = (P[0] + P[1]) / 2, (M[0] + M[1]) / 2
    rp, rm = (P[1] - P[0]) / 2, (M[1] - M[0]) / 2
    s = shift2(w, cp, cm)
    c0 = s.get((0, 0), F(0))
    rest = sum((abs(v) * rp ** a * rm ** b for (a, b), v in s.items() if (a, b) != (0, 0)), F(0))
    return G.Iv(c0 - rest, c0 + rest)


def tf_range1(poly: list, lo: F, hi: F) -> G.Iv:
    c = (lo + hi) / 2
    r = (hi - lo) / 2
    t = D.p_taylor(poly, c)
    rest = sum((abs(t[k]) * r ** k for k in range(1, len(t))), F(0))
    return G.Iv(t[0] - rest, t[0] + rest)


def box_upper_tf(triple: list, box: tuple, e: F, panel: F) -> G.Iv:
    a, b, c, d = box
    zlo, zhi = c - H.CC, H.CC - a
    ilo, ihi = d - H.CC, H.CC - b
    cuts = {zlo, zhi, ilo, ihi}
    k = math.floor(zlo / panel)
    while k * panel < zhi:
        if zlo < k * panel < zhi:
            cuts.add(k * panel)
        k += 1
    cuts = sorted(x for x in cuts if zlo <= x <= zhi)
    same_w = all(t[2] is triple[0][2] for t in triple)
    weights = [D.p_scale(D.p_taylor(H.HE[i], e), F(coef) * (-1) ** i) for coef, i, _ in triple]
    if same_w:
        comb = [F(0)]
        for wpoly in weights:
            comb = D.p_add(comb, wpoly)
        groups = [(triple[0][2], comb)]
    else:
        groups = [(t[2], wp) for t, wp in zip(triple, weights)]
    tot = G.Iv(0)
    for z0, z1 in zip(cuts, cuts[1:]):
        P = (max(F(0), a + z0 - H.KK), max(F(0), b + z1 - H.KK))
        M = (max(F(0), c - z1 - H.KK), max(F(0), d - z0 - H.KK))
        q = G.Iv(0)
        for w, wp in groups:
            q = q + tf_range2(w, P, M) * tf_range1(wp, z0, z1)
        mass = H.Phi(z1 + e) - H.Phi(z0 + e)
        contrib = q * mass
        if not (ilo <= z0 and z1 <= ihi):
            contrib = G.Iv(min(F(0), contrib.lo), max(F(0), contrib.hi))
        tot = tot + contrib
    return tot


def main() -> None:
    t0 = time.time()
    W = H.test_polys()
    prev = json.loads((D.NS / "validation" / "D309_HERMITE_NONTARGET.json").read_text())
    naive = {(r["e"], tuple(r["triple"])): r for r in prev["H3"]}
    grid = [(F(x, 2), F(y, 2)) for x in range(11) for y in range(11) if H.in_reach(F(x, 2), F(y, 2))]
    out = {"schema": "OV_D309_HERMITE_TF_NONTARGET/1", "declared_rule": DECLARED_RULE, "runs": []}
    for e in (F(1, 4), F(3)):
        Q.guard_drift(e)
        for names, depths in ((("w_quad", "w_lin", "w_const"), (4,)), (("w_bump", "w_bump", "w_bump"), (4, 5))):
            fn, dn, hn = names
            trip = [(F(3), 1, W[hn]), (F(3), 2, W[dn]), (F(1), 3, W[fn])]
            glo = F(0)
            for (p, m) in grid:
                v = sum((G.Iv(cf) * H.Ki_apply(w, p, m, e, i) for cf, i, w in trip), G.Iv(0))
                glo = max(glo, min(abs(v.lo), abs(v.hi)) if v.lo * v.hi > 0 else F(0))
            for depth in depths:
                ts = time.time()
                best = F(0)
                boxes = C11.cover(depth)
                for box in boxes:
                    iv = box_upper_tf(trip, box, e, F(1, 16))
                    best = max(best, abs(iv.lo), abs(iv.hi))
                nv = naive.get((str(e), names))
                out["runs"].append({
                    "e": str(e), "triple": list(names), "depth": depth, "boxes": len(boxes),
                    "certified_upper_tf": float(best), "grid_lower": float(glo),
                    "sound": bool(best >= glo), "upper_over_grid_lower": float(best / glo),
                    "surrogate_ideal_lower": nv["surrogate_ideal_lower"] if nv else None,
                    "upper_over_surrogate": float(best) / nv["surrogate_ideal_lower"] if nv else None,
                    "naive_depth4_upper": nv["certified_upper"] if nv else None,
                    "nc_planted_detected": bool(not (glo * F(99, 100) >= glo)),
                    "wall_s": round(time.time() - ts, 1)})
                print(out["runs"][-1], flush=True)
    out["summary"] = {"sound_all": all(r["sound"] for r in out["runs"]),
                      "nc_detected": sum(r["nc_planted_detected"] for r in out["runs"]),
                      "wall_s": round(time.time() - t0, 1)}
    (D.NS / "validation" / "D309_HERMITE_TF_NONTARGET.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    Q.log_execution("streams/D_309/code/d309_hermite_tf.py",
                    "Taylor-form certified composite sup (numerical-stability follow-up), drifts {1/4, 3} only",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION")
    print(json.dumps(out["summary"], indent=1))


if __name__ == "__main__":
    main()
