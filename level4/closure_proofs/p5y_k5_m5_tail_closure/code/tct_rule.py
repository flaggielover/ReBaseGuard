"""Campaign B premise supply for theorem TC at the m = 5 tail (theorem/THEOREM_TCT.md). Pure functions, no I/O.

The frozen Campaign-A arithmetic (`tc_rule.py`, sha pinned) is reused unchanged; this module owns only the three
premise supplies the tail needs, none of which the lower front needed:

  Lemma G   atom constants from the frozen K1 block resolvent bound instead of the adopted operator registry
            (registry r1 certifies e in [0, 0.1147] only, the tail is e in [1.62, 2.10]):
                A0 = C,  A1 = k1 C^2,  A2 = k2 C^2 + 2 k1^2 C^3
  (P2')     the zero order-3 candidate Ghat := 0 (theorem TC lets Ghat be any FIXED function):
                f_G = k3 sF + 3 k2 sD + 3 k1 sH + sigma3 + eps_src[3],  s_G = 0,  |Ghat(a)| = 0
  (P3')     sigma3 / sigma4 from the ADOPTED Aux3 order-3 evidence (order-3 source candidate suprema and certified
            midpoint source errors, order-3 h-tower evidence) intersected with the frozen J/h Leibniz tower.

(P3') r1 -> r2 repair (review r1 note N1). The adopted Aux3 order-3 quantities are MIDPOINT bounds. sigma3 is a
midpoint premise (theorem TC (P2), at e0) and may use them directly. sigma4 is a WHOLE-CELL premise (theorem TC (P3),
every e in the cell) and may not: r1 substituted the midpoint bound into the order-3 slot of the tower and then ran
the order-4 recursion on it, which is unsound. r2 keeps two towers - a midpoint tower for sigma3 and a cell tower
whose order-3 slot carries the mean-value correction ||h_j'''(e)|| <= ||h_j'''(e0)|| + rho * sup_cell ||h_j''''||,
the order-4 bound being taken from the UNREFINED tower, which is cell-uniform by (P3).

Nothing here evaluates a model quantity; every input is an adopted certified bound.
"""
from __future__ import annotations

import hashlib
import types
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = "level4/closure_proofs/"
FROZEN = {
    "tc_rule": (CP + "p5y_k5_lower_front_order3/code/tc_rule.py",
                "8d402d11f6fc06ea2af88e3d3a01e376fefbe8ebacd8418f772116010e57afd5"),
    "tc_crosscheck": (CP + "p5y_k5_lower_front_order3/code/tc_crosscheck.py",
                      "1c72117f57197d7dfcf588447510fee43cdb37426ac5f7ca85892b0e10ad8938"),
}
M_VALUES = (1, 2, 3, 5)


class TCTRefusal(ValueError):
    pass


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_frozen(name: str, pin: str | None = None):
    """Execute a frozen Campaign-A module from its pinned bytes (never imported from the working tree by name)."""
    rel = FROZEN[name][0]
    raw = (REPO / rel).read_bytes()
    if pin is not None and sha(raw) != pin:
        raise TCTRefusal(f"{rel} does not match the pin {pin[:12]}")
    mod = types.ModuleType(name + "_frozen")
    mod.__file__ = str(REPO / rel)
    exec(compile(raw, mod.__file__, "exec"), mod.__dict__)
    return mod


# ------------------------------------------------------------------ Lemma G
def atom_constants_generic(C: F, k1: F, k2: F) -> dict:
    """Lemma G: |[R f](a)| <= C||f||, |[dR f](a)| <= k1 C^2 ||f||, |[d2R f](a)| <= (k2 C^2 + 2 k1^2 C^3)||f||.

    C is the frozen K1 block bound C_upper >= sup_cell ||(I - K_e)^-1||; k_i >= sup_cell ||K_i(e)|| are the frozen
    drift-aware norms. These are exactly the constants of the frozen generic K1 DAG rules
    eps(F) = C f_F, eps(D) = C(f_D + k1 eps(F)), eps(H) = C(f_H + k2 eps(F) + 2 k1 eps(D)) rewritten in the
    A-form A0 f_H + 2 A1 f_D + A2 f_F, so they need no operator registry.
    """
    for name, v in (("C", C), ("k1", k1), ("k2", k2)):
        if not isinstance(v, F) or v <= 0:
            raise TCTRefusal(f"{name} must be a positive Fraction")
    return {"A0": C, "A1": k1 * C ** 2, "A2": k2 * C ** 2 + 2 * k1 ** 2 * C ** 3}


# ------------------------------------------------------------------ (P3') the true-object towers
def pure_tower(k: dict, sup_S0: dict) -> dict:
    """The frozen theorem-TC (P3) tower, valid uniformly on the cell:
    ||h_1|| <= 1, h_1' = -S_0 exactly so ||h_1^(n)|| <= sup_cell||S_0^(n-1)||, ||h_j|| <= 1,
    ||h_j^(n)|| <= sum_i C(n,i) k_i ||h_(j-1)^(n-i)||."""
    t = {}
    for n in range(5):
        t[(1, n)] = F(1) if n == 0 else sup_S0[n - 1]
    for j in range(2, 5):
        t[(j, 0)] = F(1)
        for n in range(1, 5):
            t[(j, n)] = sum((comb(n, i) * k[i] * t[(j - 1, n - i)] for i in range(n + 1)), F(0))
    return t


def h_towers(k: dict, sup_S0: dict, h3_mid: dict | None = None, rho: F | None = None) -> tuple[dict, dict]:
    """(midpoint tower, cell tower).

    `h3_mid[j]`, when given, is an adopted Aux3 bound of ||h_j'''(e0)|| (order-3 candidate supremum + certified
    midpoint error). The MIDPOINT tower may take it as it stands. The CELL tower may not: it carries the mean-value
    correction ||h_j'''(e)|| <= ||h_j'''(e0)|| + rho * sup_cell||h_j''''||, with the order-4 bound taken from the
    unrefined tower (cell-uniform by (P3)), and then re-derives the order-4 entries from the corrected lower orders
    -- valid because the Leibniz recursion holds pointwise in e, so cell-uniform inputs give a cell-uniform output.
    """
    pure = pure_tower(k, sup_S0)
    mid, cell = dict(pure), dict(pure)
    if not h3_mid:
        return mid, cell
    if rho is None or not isinstance(rho, F) or rho < 0:
        raise TCTRefusal("the cell tower needs the cell half-width rho")
    for j in range(1, 5):
        mid[(j, 3)] = min(pure[(j, 3)], h3_mid[j])
        cell[(j, 3)] = min(pure[(j, 3)], h3_mid[j] + rho * pure[(j, 4)])
    for j in range(2, 5):
        cell[(j, 4)] = sum((comb(4, i) * k[i] * cell[(j - 1, 4 - i)] for i in range(5)), F(0))
        if cell[(j, 4)] > pure[(j, 4)]:                      # the refinement can only narrow; never widen
            cell[(j, 4)] = pure[(j, 4)]
    return mid, cell


def sigma_source(n: int, r: int, j: dict, tower: dict, sup_S0: dict, adopted: F | None = None) -> F:
    """Upper bound of ||S_r^(n)||: the frozen closed form for r = 0, else the frozen J/h Leibniz tower, in both
    cases intersected with the adopted Aux3 order-3 source bound (candidate supremum + certified midpoint source
    error) when n = 3. `tower` must be the MIDPOINT tower for n = 3 and the CELL tower for n = 4."""
    base = sup_S0[n] if r == 0 else sum((comb(n, i) * j[i] * tower[(r, n - i)] for i in range(n + 1)), F(0))
    return min(base, adopted) if (n == 3 and adopted is not None) else base


def sigmas(k: dict, j: dict, sup_S0: dict, rho: F, aux: dict) -> dict:
    """sigma3 (midpoint, theorem TC (P2)) and sigma4 (whole cell, theorem TC (P3)) for r = 0..4, from the frozen
    towers and the adopted Aux3 order-3 evidence. `aux` carries `candidate_suprema` and `midpoint_eps`."""
    cs, me = aux["candidate_suprema"], aux["midpoint_eps"]
    h3 = {jj: F(cs[f"h:{jj}:3"]) + F(me[f"h:{jj}:3"]) for jj in range(1, 5)}
    mid, cell = h_towers(k, sup_S0, h3, rho)
    out = {}
    for r in range(5):
        a3 = (F(cs["Sclosed:0:3"]) + F(me["Sclosed:3"])) if r == 0 else (F(cs[f"S:{r}:3"]) + F(me[f"S:{r}:3"]))
        out[r] = {"sigma3": sigma_source(3, r, j, mid, sup_S0, a3),
                  "sigma4": sigma_source(4, r, j, cell, sup_S0)}
    return out


# ------------------------------------------------------------------ (P2') the zero order-3 candidate
def fG_zero_candidate(k: dict, sF: F, sD: F, sH: F, sigma3: F) -> F:
    """With Ghat := 0 the frozen order-3 residual identity gives, at e0,
        phi'''(e0) = S'''(e0) + 3 K_1 Hhat + 3 K_2 Dhat + K_3 Fhat,
    so ||phi'''(e0)|| <= 3 k1 sH + 3 k2 sD + k3 sF + sigma3. (The source error is then added by the caller as
    eps_src[3], which is a valid extra allowance: the identity above already uses the TRUE source.)"""
    for name, v in (("sF", sF), ("sD", sD), ("sH", sH), ("sigma3", sigma3)):
        if not isinstance(v, F) or v < 0:
            raise TCTRefusal(f"{name} must be a nonnegative Fraction")
    return k[3] * sF + 3 * k[2] * sD + 3 * k[1] * sH + sigma3


# ------------------------------------------------------------------ the tail enclosure, frozen-rule path
def tail_object(R, meas_r: dict, k: dict, rho: F, A: dict, sigma3: F, sigma4: F, order3=None) -> dict:
    """One object's theorem-TC quantities through the FROZEN tc_rule functions, with (P3')'s sigma3/sigma4.

    `order3` is None for the zero candidate (P2'), or a dict {sup_G, abs_G_at_a, delta_G} for a route that proposes
    a real order-3 candidate. The SAME (P3') supply is used either way: (P3') is a statement about the source and is
    independent of the choice of Ghat (review r1 note N4)."""
    sF, sD, sH = (F(meas_r["sup"][x]) for x in ("F", "D", "H"))
    if order3 is None:
        sG, aG = F(0), F(0)
        residual_G = fG_zero_candidate(k, sF, sD, sH, sigma3)
    else:
        sG, aG, residual_G = (F(order3[x]) for x in ("sup_G", "abs_G_at_a", "delta_G"))
        sF = F(order3.get("sup_F", sF))
        sD = F(order3.get("sup_D", sD))
        sH = F(order3.get("sup_H", sH))
    fF = F(meas_r["delta_F"]) + F(meas_r["eps_src"][0])
    fD = F(meas_r["delta_D"]) + F(meas_r["eps_src"][1])
    fH = F(meas_r["delta_H"]) + F(meas_r["eps_src"][2])
    fG = residual_G + F(meas_r["eps_src"][3])
    e4 = R.env4(sF, sD, sH, sG, k, sigma4, rho)
    p = R.taylor_bounds(fF, fD, fH, fG, e4, rho)
    rad = R.radius(A, p)
    return {"order3_residual_bound": residual_G, "f_G": fG, "sup_G": sG, "abs_G_at_a": aG, "env4": e4, "p": p,
            "rad": rad, "half": R.object_half_width(rho, aG, rad)}


def tail_enclosure(R, meas: dict, aux: dict, A: dict, m: int, order3: dict | None = None) -> tuple[F, F, dict]:
    """The theorem-TC-T whole-cell enclosure of R''_m on one tail cell (exact interval), frozen-rule path.
    `order3`, when given, maps str(r) -> {sup_G, abs_G_at_a, delta_G[, sup_F, sup_D, sup_H]}."""
    if m not in M_VALUES:
        raise TCTRefusal(f"m = {m} outside the frozen scope")
    rho = F(meas["rho"])
    k = {i: F(meas["norms"]["k"][i]) for i in range(5)}
    j = {i: F(meas["norms"]["j"][i]) for i in range(5)}
    s0 = {n: F(meas["sup_S0"][n]) for n in range(5)}
    sig = sigmas(k, j, s0, rho, aux)
    obj = {}
    for r in range(5):
        obj[r] = tail_object(R, meas["r"][str(r)], k, rho, A, sig[r]["sigma3"], sig[r]["sigma4"],
                             None if order3 is None else order3[str(r)])
        obj[r].update(sig[r])
    lo = hi = F(0)
    for kind, r, jj, c in R.coefficients(m):
        if kind == "F":
            a, b = (F(x) for x in meas["r"][str(r)]["H_at_a"])
            if a > b:
                raise TCTRefusal("inverted centre interval")
            lo += c * (a - obj[r]["half"])
            hi += c * (b + obj[r]["half"])
        else:
            a, b = (F(x) for x in meas["W2"][f"{r}:{jj}"])
            if a > b or c < 0:
                raise TCTRefusal("inverted W enclosure or negative coefficient")
            lo += c * a
            hi += c * b
    return lo, hi, obj


# ------------------------------------------------------------------ independent second path
def tail_enclosure_crosscheck(meas: dict, aux: dict, A: dict, m: int, order3: dict | None = None) -> tuple[F, F]:
    """Independent re-derivation from THEOREM_TCT.md in generic form. It imports no tc_rule and, since review r1
    note N15, shares no function with the frozen-rule path above: the two towers, both sigmas, the Taylor sums, the
    (P3) envelope and the assembly table are all re-derived here."""
    rho = F(meas["rho"])
    k = [F(x) for x in meas["norms"]["k"]]
    jn = [F(x) for x in meas["norms"]["j"]]
    s0 = [F(x) for x in meas["sup_S0"]]
    cs, me = aux["candidate_suprema"], aux["midpoint_eps"]
    Av = [F(A["A0"]), F(A["A1"]), F(A["A2"])]

    # --- towers, re-derived (pure; then the midpoint and cell variants of the order-3 slot)
    P = {(1, n): (F(1) if n == 0 else s0[n - 1]) for n in range(5)}
    for jj in range(2, 5):
        P[(jj, 0)] = F(1)
        for n in range(1, 5):
            P[(jj, n)] = sum((comb(n, i) * k[i] * P[(jj - 1, n - i)] for i in range(n + 1)), F(0))
    MD, CL = dict(P), dict(P)
    for jj in range(1, 5):
        adopted = F(cs[f"h:{jj}:3"]) + F(me[f"h:{jj}:3"])
        MD[(jj, 3)] = adopted if adopted < P[(jj, 3)] else P[(jj, 3)]
        shifted = adopted + rho * P[(jj, 4)]
        CL[(jj, 3)] = shifted if shifted < P[(jj, 3)] else P[(jj, 3)]
    for jj in range(2, 5):
        v = sum((comb(4, i) * k[i] * CL[(jj - 1, 4 - i)] for i in range(5)), F(0))
        CL[(jj, 4)] = v if v < P[(jj, 4)] else P[(jj, 4)]

    def sig3(r):
        adopted = (F(cs["Sclosed:0:3"]) + F(me["Sclosed:3"])) if r == 0 else (F(cs[f"S:{r}:3"]) + F(me[f"S:{r}:3"]))
        base = s0[3] if r == 0 else sum((comb(3, i) * jn[i] * MD[(r, 3 - i)] for i in range(4)), F(0))
        return adopted if adopted < base else base

    def sig4(r):
        return s0[4] if r == 0 else sum((comb(4, i) * jn[i] * CL[(r, 4 - i)] for i in range(5)), F(0))

    def sup_deriv(s, n):                          # sup_|t|<=rho ||Ftilde^(n)(t)||, s = [sF, sD, sH, sG]
        return sum((s[l] * rho ** (l - n) / factorial(l - n) for l in range(n, 4)), F(0))

    halves = {}
    for r in range(5):
        o = meas["r"][str(r)]
        sF, sD, sH = (F(o["sup"][x]) for x in ("F", "D", "H"))
        if order3 is None:
            sG = aG = F(0)
            resG = k[3] * sF + 3 * k[2] * sD + 3 * k[1] * sH + sig3(r)
        else:
            q = order3[str(r)]
            sG, aG, resG = F(q["sup_G"]), F(q["abs_G_at_a"]), F(q["delta_G"])
            sF, sD, sH = F(q.get("sup_F", sF)), F(q.get("sup_D", sD)), F(q.get("sup_H", sH))
        s = [sF, sD, sH, sG]
        f = [F(o["delta_F"]) + F(o["eps_src"][0]), F(o["delta_D"]) + F(o["eps_src"][1]),
             F(o["delta_H"]) + F(o["eps_src"][2]), resG + F(o["eps_src"][3])]
        env = sig4(r) + sum((comb(4, i) * k[i] * sup_deriv(s, 4 - i) for i in range(1, 5)), F(0))
        p = [sum((f[i] * rho ** (i - n) / factorial(i - n) for i in range(n, 4)), F(0))
             + rho ** (4 - n) / factorial(4 - n) * env for n in range(3)]
        halves[r] = rho * aG + sum((comb(2, i) * Av[i] * p[2 - i] for i in range(3)), F(0))
    lo = hi = F(0)
    for r in range(m):
        a, b = (F(x) for x in meas["r"][str(r)]["H_at_a"])
        lo += (a - halves[r]) / m
        hi += (b + halves[r]) / m
    for t in range(1, m):
        for r in range(t):
            c = F(1, t) - F(1, m)
            a, b = (F(x) for x in meas["W2"][f"{r}:{t - r - 1}"])
            lo += c * a
            hi += c * b
    return lo, hi


# ------------------------------------------------------------------ derived identity gate
def derived_identity_gate(R, meas: dict, record: dict, tol: F = F(1, 10 ** 6)) -> dict:
    """H_at_a and W2 are replayed fields that the frozen producer's 262-field identity gate does not cover. Rebuild
    the ADOPTED record's R2_interval for every m from them and the record's own eps_cell_refined, exactly as the
    frozen propagate/assembly composes it, and require the rebuild to be CONTAINED in the record interval with both
    endpoints within `tol` of the record's. (Containment, not equality: the record's enclosure adds its eps as an
    outward-rounded Arb radius, so it is very slightly wider.) A wrong H_at_a or W2 moves an endpoint by O(0.01-1).

    The gap is normalised by max(1, |endpoint|), so it is a relative tolerance where |endpoint| >= 1 (the case on the
    whole tail, where |endpoint| >= 1.33) and an absolute one below that (review r1 note N9)."""
    er = record["eps_cell_refined"]
    rows, worst = {}, F(0)
    for m in M_VALUES:
        lo = hi = F(0)
        for kind, r, jj, c in R.coefficients(m):
            if kind == "F":
                a, b = (F(x) for x in meas["r"][str(r)]["H_at_a"])
                e = F(er[f"H:{r}"])
                lo += c * (a - e)
                hi += c * (b + e)
            else:
                a, b = (F(x) for x in meas["W2"][f"{r}:{jj}"])
                lo += c * a
                hi += c * b
        w = (F(record["m"][str(m)]["R2_interval"]["lo"]), F(record["m"][str(m)]["R2_interval"]["hi"]))
        contained = w[0] <= lo and hi <= w[1]
        rel = max(abs(lo - w[0]) / max(F(1), abs(w[0])), abs(hi - w[1]) / max(F(1), abs(w[1])))
        worst = max(worst, rel)
        rows[str(m)] = {"contained": bool(contained), "endpoint_gap_normalised": float(rel),
                        "rebuilt": [str(lo), str(hi)], "record": [str(w[0]), str(w[1])]}
    ok = all(v["contained"] for v in rows.values()) and worst <= tol
    return {"pass": bool(ok), "worst_endpoint_gap_normalised": float(worst), "tolerance": float(tol),
            "normalisation": "max(1, |endpoint|)", "per_m": rows}
