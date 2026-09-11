"""Phase 2 (contribution graph) and Phase 3 (ORACLE-TIGHT NORMS, NON-CERTIFYING DIAGNOSTIC) for cell 313.

Exact operator norms (sup over the state y of the |kernel| integral; the widest continuation interval is at the reset
state y0 = (0,0), [l, u] = [-c_SR, c_SR], so the sup is attained there):
    ||K^(i)_e||   = int_{-c+e}^{c+e} |He_i(w)| phi(w) dw
    ||K_z^(i)_e|| = int_{-c+e}^{c+e} |w - e| |He_i(w)| phi(w) dw          (z = w - e)
The oracle evaluates these in double precision (Gauss-Legendre between sign changes), at e0 for the midpoint DAG and
maximised over a dense e-grid of the parent cell for the cell DAG, mean-value envelope and refinement, with 1e-6
relative padding. It is a DIAGNOSTIC ONLY: sampled values are never used as proof.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import sr_o9_candidates as T
import t4_cell as T4
import curv_mv as M
from flint import arb

NS = Path(__file__).resolve().parents[1]
CELL = int(sys.argv[1]) if len(sys.argv) > 1 else 313
C_SR = math.log(4581762885148045 / 8796093022208) + 0.5
XG, WG = np.polynomial.legendre.leggauss(48)
PAD = 1 + 1e-6
ORIG_NORMS_AT, ORIG_M_NORMS, ORIG_CAND_SUP = T4.norms_at, M.norms, T4.cand_sup
SEL, CANDSUP = set(), [False]
_cache = {}


def he(n):
    a, b = np.poly1d([1.0]), np.poly1d([1.0, 0.0])
    if n == 0:
        return a
    for k in range(1, n):
        a, b = b, np.poly1d([1.0, 0.0]) * b - k * a
    return b


def integ_abs(P, a, b):
    rts = [r.real for r in np.roots(P.coeffs) if abs(r.imag) < 1e-12 and a < r.real < b] if P.order > 0 else []
    pts = sorted([a, b] + rts)
    tot = 0.0
    for lo, hi in zip(pts[:-1], pts[1:]):
        ed = np.linspace(lo, hi, 25)
        for l, h in zip(ed[:-1], ed[1:]):
            x = 0.5 * (h - l) * XG + 0.5 * (h + l)
            tot += abs(float(np.sum(WG * P(x) * np.exp(-x * x / 2))) / math.sqrt(2 * math.pi) * 0.5 * (h - l))
    return tot


def point(e):
    a, b = -C_SR + e, C_SR + e
    return ([integ_abs(he(i), a, b) for i in range(5)],
            [integ_abs(np.poly1d([1.0, -e]) * he(i), a, b) for i in range(4)])


def cell_sup(lo, hi, n=81):
    key = ("cell", round(lo, 15), round(hi, 15))
    if key not in _cache:
        grid = np.linspace(lo, hi, n)
        vals = [point(x) for x in grid]
        K = [max(v[0][i] for v in vals) for i in range(5)]
        Kz = [max(v[1][i] for v in vals) for i in range(4)]
        argK = [float(grid[int(np.argmax([v[0][i] for v in vals]))]) for i in range(5)]
        argKz = [float(grid[int(np.argmax([v[1][i] for v in vals]))]) for i in range(4)]
        _cache[key] = (K, Kz, argK, argKz)
    return _cache[key]


def norms_at_v(e):
    base = ORIG_NORMS_AT(e)
    if not SEL:
        return base
    if float(e.rad()) < 1e-30:
        K, Kz = point(float(e.mid()))
    else:
        K, Kz, _, _ = cell_sup(float(e.lower()), float(e.upper()))
    return {"k": [arb(K[i] * PAD) if f"K{i}" in SEL else base["k"][i] for i in range(3)],
            "kz": [arb(Kz[i] * PAD) if f"Kz{i}" in SEL else base["kz"][i] for i in range(3)]}


def m_norms_v(e_lo, e_hi):
    base = ORIG_M_NORMS(e_lo, e_hi)
    if not SEL:
        return base
    K, Kz, _, _ = cell_sup(float(e_lo.lower()), float(e_hi.upper()))
    out = dict(base)
    out["K"] = {i: (arb(K[i] * PAD) if f"K{i}" in SEL else base["K"][i]) for i in range(4)}
    out["Kz"] = {i: (arb(Kz[i] * PAD) if f"Kz{i}" in SEL else base["Kz"][i]) for i in range(4)}
    return out


def cand_sup_v(mant):
    if not CANDSUP[0]:
        return ORIG_CAND_SUP(mant)
    cf = np.array(mant, dtype=float) / 2.0 ** T.SCALE_BITS
    x = np.cos(np.linspace(0, np.pi, 601))
    V = np.polynomial.chebyshev.chebvander(x, cf.shape[0] - 1)
    return arb(float(np.abs(V @ cf @ V.T).max()) * (1 + 1e-3))


T4.norms_at, M.norms, T4.cand_sup = norms_at_v, m_norms_v, cand_sup_v


def run(sel, cand=False, SV=None):
    SEL.clear(); SEL.update(sel); CANDSUP[0] = cand
    view, SV = M.build_view(CELL, SV)
    r4 = T4.t4(view)
    out = {"ratio": {m: r4["B_cover_ratio"][m] for m in ("1", "2", "3", "5")},
           "M_R2": {m: float(T4.Fr(r4["m"][m]["M_R2"])) for m in ("1", "2", "3", "5")},
           "D_mag": {m: float(T4.Fr(r4["m"][m]["D_interval_mag"])) for m in ("1", "2", "3", "5")},
           "status": r4["all_m_status"], "t4_sha": r4["t4_record_sha256"]}
    return out, view, r4, SV


def breakdown(view, r4, SV):
    """Phase-2 contribution graph at the baseline (original certified norms)."""
    SEL.clear(); CANDSUP[0] = False
    built = T.build_cell_candidates(CELL)["scientific"]
    mant = {x["node"]: x["mantissas"] for x in built["candidates"]}
    struct = M.struct_full()
    graph = {"env": {}, "cell_dag": {}, "refinement": {}, "R2_terms": {}, "cover": {}}
    with T.scientific_precision():
        g = T.cell_geometry(T.frozen_cell(CELL))
        e_ball = g["e0"] + arb(0, g["rho"].abs_upper())
        nrm = M.norms(g["left"], g["right"])
        sups = {n: T4.cand_sup(m) for n, m in mant.items()}
        rho = float(g["rho"].abs_upper())
        for n in [x for x in struct if x.endswith("k2") or x.startswith("h:") or x.startswith("S:")]:
            terms, const, src = struct[n]
            rows = []
            for (c, kind, i), p in sorted(terms.items()):
                S = 1.0 if c == "const:1" else float(sups[c])
                dp = M.dpoly(p)
                if dp:
                    v = float(M.psup(dp, e_ball)) * float(nrm[kind][i]) * S
                    rows.append({"term": f"d/de coef * {kind}{i} * sup({c})", "norm_id": f"{kind}{i}", "value": v})
                v = float(M.psup(p, e_ball)) * float(nrm[kind][i + 1]) * S
                rows.append({"term": f"|coef| * {kind}{i+1} * sup({c})", "norm_id": f"{kind}{i+1}", "sup": S,
                             "norm": float(nrm[kind][i + 1]), "value": v})
            for kind, p in src:
                q = M.SRC_ORDER[kind]
                rows.append({"term": f"closed form d/de {kind}", "norm_id": None, "value": float(M.psup(p, e_ball)) * float(SV[q + 1])})
            tot = sum(r["value"] for r in rows)
            byn = {}
            for r in rows:
                byn[r["norm_id"] or "closed_form"] = byn.get(r["norm_id"] or "closed_form", 0.0) + r["value"]
            graph["env"][n] = {"Env": tot, "rho_Env": rho * tot, "by_norm_id": byn, "terms": rows}
        struct4 = T4.op_structure()
        nb = T4.norms_at(e_ball)
        ncell = {"K": [float(x) for x in nb["k"]], "Kz": [float(x) for x in nb["kz"]]}
        eps = {k: float(T4.Fr(v)) for k, v in r4["eps_cell"].items()}
        for n, terms in struct4.items():
            rows = []
            for (c, kind, i), p in sorted(terms.items()):
                if c == "const:1" or c == n:
                    continue
                nv = ncell[kind][i]
                rows.append({"src": c, "op": f"{kind}{i}", "coef": str(p.get(0)), "norm": nv, "eps_src": eps.get(c),
                             "contribution": abs(float(p.get(0, 0))) * nv * (eps.get(c) or 0.0)})
            if rows:
                graph["cell_dag"][n] = rows
        graph["cell_dag_eps"] = eps
        graph["cell_dag_norms"] = ncell
    graph["refinement"] = r4["refinement"]
    for m in ("1", "2", "3", "5"):
        L = r4["m"][m]
        graph["cover"][m] = {k: float(T4.Fr(v)) for k, v in L["cover"]["children"].items()}
        graph["R2_terms"][m] = {}
        for kd, r, j, cf in T4.assembly.coefficients(int(m)):
            rec = r4["x0_enclosures"]["H"][r] if kd == "F" else r4["x0_enclosures"]["W"][2][f"{r},{j}"]
            lo, hi = T4.Fr(rec["lo"]), T4.Fr(rec["hi"])
            graph["R2_terms"][m][f"H_{r}" if kd == "F" else f"W''_{r},{j}"] = {
                "coef": str(cf), "abs_coef_times_radius": float(abs(cf) * (hi - lo) / 2), "abs_coef_times_mid": float(abs(cf) * abs(hi + lo) / 2)}
    return graph


def main():
    T.check_threads()
    res = {}
    base, view, r4, SV = run(set())
    res["base"] = base
    graph = breakdown(view, r4, SV)
    ids = ["K0", "K1", "K2", "K3", "Kz0", "Kz1", "Kz2", "Kz3"]
    for i in ids:
        res[i] = run({i}, SV=SV)[0]
    res["K_all"] = run({"K0", "K1", "K2", "K3"}, SV=SV)[0]
    res["Kz_all"] = run({"Kz0", "Kz1", "Kz2", "Kz3"}, SV=SV)[0]
    res["ALL_NORMS"] = run(set(ids), SV=SV)[0]
    res["CANDSUP_only__beyond_norm_scope"] = run(set(), cand=True, SV=SV)[0]
    res["ALL_NORMS_plus_CANDSUP__beyond_norm_scope"] = run(set(ids), cand=True, SV=SV)[0]
    with T.scientific_precision():
        g = T.cell_geometry(T.frozen_cell(CELL))
        K, Kz, argK, argKz = cell_sup(float(g["left"].lower()), float(g["right"].upper()))
        Kp, Kzp = point(float(g["e0"].mid()))
        SEL.clear()
        old_env = ORIG_M_NORMS(g["left"], g["right"])
        old_mid = ORIG_NORMS_AT(g["e0"])
        old_cell = ORIG_NORMS_AT(g["e0"] + arb(0, g["rho"].abs_upper()))
    table = []
    for fam, idx in [("K", i) for i in range(4)] + [("Kz", i) for i in range(4)]:
        nid = f"{fam}{idx}"
        o = K[idx] if fam == "K" else Kz[idx]
        row = {"norm_id": nid, "operator": ("K^(%d)" % idx) if fam == "K" else ("K_z^(%d)" % idx),
               "env_old_bound_cell": float(old_env[fam][idx]), "oracle_cell_sup": o,
               "oracle_argmax_e": (argK if fam == "K" else argKz)[idx], "old_over_oracle_env": float(old_env[fam][idx]) / o}
        if idx <= 2:
            kk = "k" if fam == "K" else "kz"
            row.update({"dag_old_cell": float(old_cell[kk][idx]), "dag_old_mid": float(old_mid[kk][idx]),
                        "oracle_mid_e0": (Kp[idx] if fam == "K" else Kzp[idx]),
                        "old_over_oracle_dag_cell": float(old_cell[kk][idx]) / o})
        row["removable_share_B_cover"] = {m: 1 - res[nid]["ratio"][m] / base["ratio"][m] for m in ("1", "2", "3", "5")}
        row["removable_share_M_R2"] = {m: 1 - res[nid]["M_R2"][m] / base["M_R2"][m] for m in ("1", "2", "3", "5")}
        table.append(row)
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.opnorm-oracle.v1", "cell": CELL, "DIAGNOSTIC_ONLY": True,
           "variants": res, "norm_table": table, "contribution_graph": graph,
           "ALL_NORMS_closes_m2_m3_m5": all(res["ALL_NORMS"]["ratio"][m] <= 1 for m in ("2", "3", "5"))}
    (NS / f"evidence/phase23_oracle_c{CELL}.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    for k, v in res.items():
        print(f"{k:45s} ratio " + " ".join(f"m{m}={v['ratio'][m]:.4g}" for m in ("1", "2", "3", "5")) + "  M_R2 m5 %.4g" % v["M_R2"]["5"])
    for r in table:
        print(f"{r['norm_id']:4s} env old {r['env_old_bound_cell']:.4g} oracle {r['oracle_cell_sup']:.4g} (x{r['old_over_oracle_env']:.3f}) "
              + (f"dag cell {r.get('dag_old_cell', 0):.4g} (x{r.get('old_over_oracle_dag_cell', 0):.3f}) " if 'dag_old_cell' in r else "")
              + "removable M_R2 m5 %.1f%%" % (100 * r["removable_share_M_R2"]["5"]))
    print("ALL_NORMS closes 313 m=2,3,5:", out["ALL_NORMS_closes_m2_m3_m5"])


if __name__ == "__main__":
    main()
