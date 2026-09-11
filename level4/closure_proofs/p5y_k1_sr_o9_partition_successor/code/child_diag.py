"""Phases 3-4: NON-CERTIFYING rho-scaling and child-location diagnostic over the OLD cell-313 drift interval.

For N in {1,2,4,8,16,32} the old interval [L, R] is split into N equal exact-rational children. Each child is run
through the REAL frozen T4 machinery (ErrorDAG, sr_refine, assembly, ledger) with:
  * child geometry: exact child left/right, e0 = midpoint, rho = half-width; C_upper inherited from the parent cell
    (a proved bound for every e of the parent, hence of the child);
  * child candidates: the frozen T1 constructor at the child e0 (candidate sups and x0 values move with the child);
  * image-node x0 values at the child e0 from float Nystrom solves (5-point differences), parent midpoint radius;
  * delta_cell = delta_mid + rho_child * Env_child (the governed mean-value successor; no interval-e mode);
  * delta_mid: the PARENT T3 midpoint certificate used as a PROXY for the child's (not recomputed; no T2/T3 run).
Variant B = frozen certified norms and candidate sups.  Variant A = oracle-exact operator norms
(sup_y int|kernel|, attained at the reset state) and dense-sampled exact candidate sups.
The frozen T1/T4 functions are redirected in-process (T.frozen_cell for index 313, T4.norms_at, curv_mv.norms,
T4.cand_sup). That is acceptable ONLY because nothing here certifies; a certifying successor must wire cell
records explicitly (aux4 lesson).
"""
import copy
import hashlib
import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
import sr_o9_candidates as T
import sr_o9_equations as EQ
import t2_final_certifier as FC
import t4_cell as T4
import curv_mv as M
from flint import arb

NS = Path(__file__).resolve().parents[1]
PARENT = 313
XG, WG = np.polynomial.legendre.leggauss(48)
_FROZEN, _NORMS_AT, _MNORMS, _CANDSUP = T.frozen_cell, T4.norms_at, M.norms, T4.cand_sup
STATE = {"child": None, "oracle": False}
C_SR = math.log(4581762885148045 / 8796093022208) + 0.5


def frozen_cell_v(index):
    if index == PARENT and STATE["child"] is not None:
        return json.loads(json.dumps(STATE["child"]))
    return _FROZEN(index)


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


_nc = {}


def exact_norms(lo, hi):
    key = (round(lo, 14), round(hi, 14))
    if key not in _nc:
        grid = np.linspace(lo, hi, 9) if hi > lo else [lo]
        vals = [([integ_abs(he(i), -C_SR + e, C_SR + e) for i in range(5)],
                 [integ_abs(np.poly1d([1.0, -e]) * he(i), -C_SR + e, C_SR + e) for i in range(4)]) for e in grid]
        _nc[key] = ([max(v[0][i] for v in vals) * (1 + 1e-6) for i in range(5)],
                    [max(v[1][i] for v in vals) * (1 + 1e-6) for i in range(4)])
    return _nc[key]


def norms_at_v(e):
    base = _NORMS_AT(e)
    if not STATE["oracle"]:
        return base
    K, Kz = exact_norms(float(e.lower()), float(e.upper()))
    return {"k": [arb(K[i]) for i in range(3)], "kz": [arb(Kz[i]) for i in range(3)]}


def mnorms_v(e_lo, e_hi):
    base = _MNORMS(e_lo, e_hi)
    if not STATE["oracle"]:
        return base
    K, Kz = exact_norms(float(e_lo.lower()), float(e_hi.upper()))
    out = dict(base)
    out["K"] = {i: arb(K[i]) for i in range(4)}
    out["Kz"] = {i: arb(Kz[i]) for i in range(4)}
    return out


def cand_sup_v(mant):
    if not STATE["oracle"]:
        return _CANDSUP(mant)
    cf = np.array(mant, dtype=float) / 2.0 ** T.SCALE_BITS
    x = np.cos(np.linspace(0, np.pi, 601))
    V = np.polynomial.chebyshev.chebvander(x, cf.shape[0] - 1)
    return arb(float(np.abs(V @ cf @ V.T).max()) * (1 + 1e-3))


T.frozen_cell, T4.norms_at, M.norms, T4.cand_sup = frozen_cell_v, norms_at_v, mnorms_v, cand_sup_v


def child_record(Nc, k):
    p = _FROZEN(PARENT)
    L, R = Fr(p["left"][0]), Fr(p["right"][0])
    w = (R - L) / Nc
    lo, hi = L + k * w, L + (k + 1) * w
    enc = lambda x: [f"{x.numerator}/{x.denominator}", "0/1"]            # noqa: E731
    c = dict(p)
    c.update(left=enc(lo), right=enc(hi), e0=enc((lo + hi) / 2), rho=enc((hi - lo) / 2))
    return c


def objs(b, c, e):
    S = T.NodalSystem(b, c, e)
    M0, M1 = S.M[0], S.M[1]
    one = np.ones(S.A.shape[0])
    o = {"h:1": one - M0 @ one}
    for j in range(2, 5):
        o[f"h:{j}"] = M0 @ o[f"h:{j-1}"]
    o["S:0"] = S.s0raw - e * o["h:1"]
    for r in range(1, 5):
        o[f"S:{r}"] = M1 @ o[f"h:{r}"]
    for r in range(4):
        for j in range(1, 4 - r):
            o[f"W:{r},{j}"] = M0 @ (o[f"S:{r}"] if j == 1 else o[f"W:{r},{j-1}"])
    for r in range(5):
        o[f"F:{r}"] = np.linalg.solve(S.A, S.s0raw if r == 0 else o[f"S:{r}"] + e * o["h:1"])
    return o


def fd_x0(b, c, e, h=0.01):
    V = {q: objs(b, c, e + q * h) for q in (-2, -1, 0, 1, 2)}
    out = {}
    for name in V[0]:
        v = {q: V[q][name][0] for q in V}
        out[name] = [v[0], (-v[2] + 8 * v[1] - 8 * v[-1] + v[-2]) / (12 * h),
                     (-v[2] + 16 * v[1] - 30 * v[0] + 16 * v[-1] - v[-2]) / (12 * h * h)]
    return out


def image_value(vals, n):
    base, k = n.rsplit(":k", 1)
    key = "h:1" if base == "h1img" else base
    return vals[key][int(k)]


def R_true(vals, m, k):
    v = sum(vals[f"F:{r}"][k] for r in range(m)) / m
    for t in range(1, m):
        for r in range(t):
            key = f"S:{r}" if t - r - 1 == 0 else f"W:{r},{t-r-1}"
            v += (1.0 / t - 1.0 / m) * vals[key][k]
    return v


def child_view(t3, mant, hashes, rec, vals, SV):
    struct = M.struct_full()
    with T.scientific_precision():
        g = T.cell_geometry(rec)
        e0, rho = g["e0"], g["rho"]
        e_ball = e0 + arb(0, rho.abs_upper())
        nrm = M.norms(g["left"], g["right"])
        sups = {n: T4.cand_sup(m) for n, m in mant.items()}
        env = M.envelopes(struct, sups, nrm, e_ball, SV)
        rho_u = arb(rho.abs_upper())
        view = copy.deepcopy(t3)
        view["candidate_identity_list_sha256"] = [hashlib.sha256(T.canonical(sorted(hashes.items()))).hexdigest()]
        for n in FC.NODES:
            if n in EQ.IMAGE_NODES:
                old = T4.img_x0(t3["x0_images"]["mid"][n])
                val = image_value(vals, n)
                rad = float(old.rad()) + 1e-9 * max(1.0, abs(val))
                view["x0_images"]["mid"][n] = {"mid": M._enc(arb(val)), "rad": M._enc(arb(rad))}
                cb = arb(val) + arb(0, (arb(rad) + rho_u * env[n]).upper())
                view["x0_images"]["cell"][n] = {"mid": M._enc(arb(cb.mid())), "rad": M._enc(arb(cb.rad()))}
                continue
            dmid = Fr(t3["delta"]["mid"][n]["delta"])
            dmv = M.fr(T4.exact(dmid) + rho_u * env[n])
            view["delta"]["cell"][n] = dict(t3["delta"]["cell"][n], delta=f"{dmv.numerator}/{dmv.denominator}", delta_float=float(dmv))
    return view


def num(x):
    x = str(x)
    return float(x[1:].split(" ")[0]) if x.startswith("[") else float(Fr(x))


def main():
    T.check_threads()
    Nc, ks = int(sys.argv[1]), [int(x) for x in sys.argv[2].split(",")]
    t3 = json.loads((M.EV3 / f"t3/t3_c{PARENT}.json").read_text())
    SV = None
    for k in ks:
        rec = child_record(Nc, k)
        STATE["child"] = rec
        built = T.build_cell_candidates(PARENT)["scientific"]
        mant = {x["node"]: x["mantissas"] for x in built["candidates"]}
        hashes = {x["node"]: x["identity_hash"] for x in built["candidates"]}
        with T.scientific_precision():
            g = T.cell_geometry(rec)
            b, c, ef = T.nearest_double(g["b"]), T.nearest_double(g["c"]), T.nearest_double(g["e0"])
            rho = float(g["rho"].mid())
            SV = SV or {q: M.sup_He_phi(q) for q in range(4)}
        vals = fd_x0(b, c, ef)
        out = {"schema": "rebaseguard.p5y.k1.sr.o9.partition-child-diag.v1", "DIAGNOSTIC_ONLY": True, "N": Nc, "k": k,
               "child": {kk: rec[kk] for kk in ("left", "right", "e0", "rho")}, "e0_float": ef, "rho": rho, "variants": {}}
        out["ideal_true"] = {}
        for m in (1, 2, 3, 5):
            R1, R2 = R_true(vals, m, 1), R_true(vals, m, 2)
            out["ideal_true"][str(m)] = {"R1": R1, "R2": R2, "ratio_center": (rho * abs(R1) + rho * rho / 2 * abs(R2)) / 0.05}
        for var in ("B_certified", "A_oracle"):
            STATE["oracle"] = var == "A_oracle"
            view = child_view(t3, mant, hashes, rec, vals, SV)
            r4 = T4.t4(view)
            ref = {}
            for r, tr in r4["refinement"].items():
                i, s = tr["inputs"], tr["summary"]
                C, k1, k2 = num(i["C"]), num(i["k1"]), num(i["k2"])
                ref[r] = {"contraction": num(s["contraction"]), "eps_H_cell": num(s["eps_H_cell"]),
                          "C_deltaH": C * num(i["delta_H_cell"]), "C_k2_nF": C * k2 * num(s["eps_F_cell"]),
                          "C_2k1_nD_derivative": C * 2 * k1 * num(s["eps_D_cell"]), "C_S2_source": C * num(i["eps_S2_cell"])}
            out["variants"][var] = {
                "ratio": r4["B_cover_ratio"], "status": r4["all_m_status"],
                "M_R2": {m: float(T4.Fr(r4["m"][m]["M_R2"])) for m in r4["m"]},
                "D_mag": {m: float(T4.Fr(r4["m"][m]["D_interval_mag"])) for m in r4["m"]},
                "cover_children": {m: {kk: float(T4.Fr(v)) for kk, v in r4["m"][m]["cover"]["children"].items()} for m in r4["m"]},
                "refinement": ref, "max_contraction": max(v["contraction"] for v in ref.values()),
                "t4_sha": r4["t4_record_sha256"]}
        STATE["oracle"] = False
        (NS / f"evidence/diag/N{Nc}_k{k}.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
        print(Nc, k, {v: out["variants"][v]["ratio"] for v in out["variants"]}, flush=True)


if __name__ == "__main__":
    main()
