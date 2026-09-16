"""Exact-rational REFERENCE KERNEL for the signed order-3 error algebra of DESIGN.md.

NOT a producer. It certifies nothing about any detector. It implements, over Python Fractions and the sup (infinity)
norm, exactly the propagation and whole-cell rules the Arb producer must implement, so that those rules can be
qualified against manufactured systems whose true derivatives are known exactly (code/manufactured.py).

The model of one cell (every quantity is supplied by the caller):

    (I - K(e)) F_r(e) = S_r(e),          W_(r,0) = S_r,   W_(r,j) = K(e) W_(r,j-1)
    X_n := d_e^n X,   K_i := d_e^i K

    candidates  Fhat[r][n], n = 0..3     (n = 0 F, 1 D, 2 H, 3 the new order-3 rung)
                Shat[r][n], n = 0..3;   What[(r,j)][n], n = 0..3, j >= 1
    norms       C >= sup_cell ||(I-K(e))^-1||,   k[i] >= sup_cell ||K_i(e)||, i = 0..5
    sources     epsS[r][n] >= ||Shat_n - S_n(e0)||  (n <= 3),   TS[r][n] >= sup_cell ||S_n||  (n <= 4)
    operators   Kapply(i, v) = K_i(e0) v, exact

Rules (each is an upper bound on a distinct term of an exact identity; see DESIGN.md section 3):

    midpoint   eps_n  = C ( delta_n + sum_(i=1..n) C(n,i) k_i eps_(n-i) + epsS_n )
    tower      T_n    = C ( sum_(i=1..n) C(n,i) k_i T_(n-i) + TS_n )
    cascade    epsc_n = C ( delta_n + rho Env_n + sum_(i=1..n) C(n,i) k_i epsx_(n-i) + epsSx_n )
               Env_n  = k_1 ||Xhat_n|| + sum_(i=1..n) C(n,i) k_(i+1) ||Xhat_(n-i)||
    taylor     epst_n = eps_n + rho T_(n+1)
    cell       epsx_n = min(epsc_n, epst_n);   epsSx_n = epsS_n + rho TS_(n+1)
    W          the same with  (W_j)_n = sum_(i=0..n) C(n,i) K_i (W_(j-1))_(n-i)  and no resolvent factor
    assembly   R_m^(n) = sum_c c * X_n[origin];  radius = sum |c| eps   (frozen coefficient table)
    export     L = centre_3 - sum |c| epsx_3,   U = centre_3 + sum |c| epsx_3     (signed, exact)

`mutation` exists ONLY so the qualification can show each rule is load-bearing. The Arb producer carries no such
parameter; DESIGN.md section 6 forbids it.
"""
from __future__ import annotations

from fractions import Fraction as Fr
from math import comb

ORIGIN = 0
M_VALUES = (1, 2, 3, 5)
W_INDICES = tuple((r, j) for r in range(4) for j in range(1, 4 - r))
MUTATIONS = ("M1_ORDER3_LEIBNIZ_COEFF", "M2_DROP_K3_F", "M3_DROP_3K1_H", "M4_MIDPOINT_AS_CELL",
             "M6_TAYLOR_DROPS_TOWER", "M7_ASSEMBLY_DROPS_W", "M8_ASSEMBLY_COEFF_1_OVER_T", "M9_LOWER_BOUND_SIGN")


# ------------------------------------------------------------------ exact vector helpers
def norm(v) -> Fr:
    return max(abs(x) for x in v)


def add(u, v):
    return [a + b for a, b in zip(u, v, strict=True)]


def sub(u, v):
    return [a - b for a, b in zip(u, v, strict=True)]


def scale(c, v):
    return [c * a for a in v]


def coefficients(m: int, mutation: str | None = None) -> list[tuple[str, int, int, Fr]]:
    """Frozen all-m table: F_r with 1/m (r < m); W_(r, t-r-1) with 1/t - 1/m (1 <= t < m, r < t)."""
    rows = [("F", r, 0, Fr(1, m)) for r in range(m)]
    for t in range(1, m):
        for r in range(t):
            c = Fr(1, t) if mutation == "M8_ASSEMBLY_COEFF_1_OVER_T" else Fr(1, t) - Fr(1, m)
            rows.append(("W", r, t - r - 1, c))
    if mutation == "M7_ASSEMBLY_DROPS_W":
        rows = [x for x in rows if x[0] == "F"]
    return rows


def _binom(n: int, i: int, mutation: str | None) -> int:
    if mutation == "M1_ORDER3_LEIBNIZ_COEFF" and n == 3 and i in (1, 2):
        return 2
    return comb(n, i)


# ------------------------------------------------------------------ the kernel
def cell_order3(inp: dict, *, mutation: str | None = None) -> dict:
    """All midpoint and whole-cell bounds through order 3, and the signed per-m export."""
    if mutation is not None and mutation not in MUTATIONS:
        raise ValueError(mutation)
    rho, C, k = inp["rho"], inp["C"], inp["k"]
    Kap = inp["Kapply"]
    Fh, Sh, Wh = inp["Fhat"], inp["Shat"], inp["What"]
    epsS, TS = inp["epsS"], inp["TS"]
    no_rho = mutation == "M4_MIDPOINT_AS_CELL"
    rho_eff = Fr(0) if no_rho else rho

    out = {"eps_mid": {}, "eps_cell": {}, "cascade": {}, "taylor": {}, "tower": {}, "delta": {}}

    def src_cell(r, n):
        return epsS[r][n] + rho_eff * TS[r][n + 1]

    # ---- resolvent objects F_r, orders 0..3 (towers to order 4)
    for r in range(5):
        T = {}
        for n in range(5):
            acc = sum((comb(n, i) * k[i] * T[n - i] for i in range(1, n + 1)), Fr(0))
            T[n] = C * (acc + TS[r][n])
        eps, epsx = {}, {}
        for n in range(4):
            res = sub(Fh[r][n], Kap(0, Fh[r][n]))
            for i in range(1, n + 1):
                res = sub(res, scale(comb(n, i), Kap(i, Fh[r][n - i])))
            res = sub(res, Sh[r][n])
            delta = norm(res)
            dep = Fr(0)
            for i in range(1, n + 1):
                if n == 3 and i == 3 and mutation == "M2_DROP_K3_F":
                    continue
                if n == 3 and i == 1 and mutation == "M3_DROP_3K1_H":
                    continue
                dep += _binom(n, i, mutation) * k[i] * eps[n - i]
            eps[n] = C * (delta + dep + epsS[r][n])
            env = k[1] * norm(Fh[r][n]) + sum((comb(n, i) * k[i + 1] * norm(Fh[r][n - i])
                                               for i in range(1, n + 1)), Fr(0))
            depx = sum((_binom(n, i, mutation) * k[i] * epsx[n - i] for i in range(1, n + 1)
                        if not (n == 3 and ((i == 3 and mutation == "M2_DROP_K3_F")
                                            or (i == 1 and mutation == "M3_DROP_3K1_H")))), Fr(0))
            casc = C * (delta + rho_eff * env + depx + src_cell(r, n))
            tay = eps[n] + (Fr(0) if mutation == "M6_TAYLOR_DROPS_TOWER" else rho_eff) * T[n + 1]
            epsx[n] = min(casc, tay)
            key = ("F", r, n)
            out["delta"][key], out["eps_mid"][key], out["eps_cell"][key] = delta, eps[n], epsx[n]
            out["cascade"][key], out["taylor"][key] = casc, tay
        for n in range(5):
            out["tower"][("F", r, n)] = T[n]

    # ---- finite kernel powers W_(r,j), orders 0..3 (towers to order 4)
    for r in range(4):
        for n in range(5):
            out["tower"][("W", (r, 0), n)] = TS[r][n]
        for n in range(4):
            out["eps_mid"][("W", (r, 0), n)] = epsS[r][n]
            out["eps_cell"][("W", (r, 0), n)] = src_cell(r, n)
    for (r, j) in W_INDICES:
        prev = (lambda n, r=r, j=j: Sh[r][n]) if j == 1 else (lambda n, r=r, j=j: Wh[(r, j - 1)][n])
        for n in range(5):
            out["tower"][("W", (r, j), n)] = sum((comb(n, i) * k[i] * out["tower"][("W", (r, j - 1), n - i)]
                                                  for i in range(n + 1)), Fr(0))
        for n in range(4):
            res = list(Wh[(r, j)][n])
            for i in range(n + 1):
                res = sub(res, scale(comb(n, i), Kap(i, prev(n - i))))
            delta = norm(res)
            eps = delta + sum((comb(n, i) * k[i] * out["eps_mid"][("W", (r, j - 1), n - i)]
                               for i in range(n + 1)), Fr(0))
            env = sum((comb(n, i) * k[i + 1] * norm(prev(n - i)) for i in range(n + 1)), Fr(0))
            casc = delta + rho_eff * env + sum((comb(n, i) * k[i] * out["eps_cell"][("W", (r, j - 1), n - i)]
                                                for i in range(n + 1)), Fr(0))
            tay = eps + (Fr(0) if mutation == "M6_TAYLOR_DROPS_TOWER" else rho_eff) * \
                out["tower"][("W", (r, j), n + 1)]
            key = ("W", (r, j), n)
            out["delta"][key], out["eps_mid"][key], out["cascade"][key], out["taylor"][key] = delta, eps, casc, tay
            out["eps_cell"][key] = min(casc, tay)

    # ---- signed all-m assembly
    def cand(kind, r, j, n):
        if kind == "F":
            return Fh[r][n][ORIGIN]
        return Sh[r][n][ORIGIN] if j == 0 else Wh[(r, j)][n][ORIGIN]

    def key(kind, r, j, n):
        return ("F", r, n) if kind == "F" else ("W", (r, j), n)

    out["m"] = {}
    for m in M_VALUES:
        rec = {}
        for n in range(4):
            rows = coefficients(m, mutation)
            centre = sum((c * cand(kd, r, j, n) for kd, r, j, c in rows), Fr(0))
            rad_mid = sum((abs(c) * out["eps_mid"][key(kd, r, j, n)] for kd, r, j, c in rows), Fr(0))
            rad_cell = sum((abs(c) * out["eps_cell"][key(kd, r, j, n)] for kd, r, j, c in rows), Fr(0))
            rec[n] = {"centre": centre, "mid": (centre - rad_mid, centre + rad_mid),
                      "cell": (centre - rad_cell, centre + rad_cell)}
        lo, hi = rec[3]["cell"]
        if mutation == "M9_LOWER_BOUND_SIGN":
            lo = rec[3]["centre"] + (rec[3]["centre"] - lo)
        rec["export"] = {"L": lo, "U": hi}
        out["m"][m] = rec
    return out


def export_record(cell_id: str, e0: Fr, rho: Fr, result: dict) -> dict:
    """The signed order-3 export in the shape K5-B consumes: exact rational strings, per m."""
    return {"schema": "rebaseguard.p5y.k5.order3-export.v1", "cell": cell_id,
            "e0": str(e0), "rho": str(rho),
            "m": {str(m): {"R3_mid_interval": {"lo": str(v[3]["mid"][0]), "hi": str(v[3]["mid"][1])},
                           "R3_cell_lower_L": str(v["export"]["L"]),
                           "R3_cell_upper_U": str(v["export"]["U"]),
                           "sign_determinate": v["export"]["L"] > 0 or v["export"]["U"] < 0}
                  for m, v in sorted(result["m"].items())}}
