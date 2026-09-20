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

Nothing here evaluates a model quantity; every input is an adopted certified bound.
"""
from __future__ import annotations

import hashlib
import types
from fractions import Fraction as F
from math import comb
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


# ------------------------------------------------------------------ (P3') the true-object tower
def h_tower(k: dict, sup_S0: dict, h3: dict | None = None) -> dict:
    """||h_j^(n)|| for j = 1..4, n = 0..4.

    Frozen premises (theorem TC P3): ||h_1|| <= 1, h_1' = -S_0 exactly so ||h_1^(n)|| <= sup||S_0^(n-1)||,
    ||h_j|| <= 1, ||h_j^(n)|| <= sum_i C(n,i) k_i ||h_(j-1)^(n-i)||.
    `h3[j]`, when given, is an adopted Aux3 bound of ||h_j'''|| (candidate supremum + certified midpoint error); the
    minimum of the two valid bounds is used, and the order-4 recursion is then seeded with the refined lower orders.
    """
    t = {}
    for n in range(5):
        t[(1, n)] = F(1) if n == 0 else sup_S0[n - 1]
    if h3:
        t[(1, 3)] = min(t[(1, 3)], h3[1])
    for j in range(2, 5):
        t[(j, 0)] = F(1)
        for n in (1, 2, 3):
            v = sum((comb(n, i) * k[i] * t[(j - 1, n - i)] for i in range(n + 1)), F(0))
            t[(j, n)] = min(v, h3[j]) if (n == 3 and h3) else v
        t[(j, 4)] = sum((comb(4, i) * k[i] * t[(j - 1, 4 - i)] for i in range(5)), F(0))
    return t


def sigma_source(n: int, r: int, j: dict, tower: dict, sup_S0: dict, adopted: F | None = None) -> F:
    """Upper bound of ||S_r^(n)||: the frozen closed form for r = 0, else the frozen J/h Leibniz tower intersected
    with the adopted Aux3 order-3 source bound (candidate supremum + certified midpoint source error) when n = 3."""
    if r == 0:
        return sup_S0[n]
    v = sum((comb(n, i) * j[i] * tower[(r, n - i)] for i in range(n + 1)), F(0))
    return min(v, adopted) if (n == 3 and adopted is not None) else v


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
def tail_object(R, meas_r: dict, k: dict, rho: F, A: dict, sigma3: F, sigma4: F) -> dict:
    """One object's theorem-TC quantities with the zero order-3 candidate, through the FROZEN tc_rule functions."""
    sF, sD, sH = (F(meas_r["sup"][x]) for x in ("F", "D", "H"))
    dG = fG_zero_candidate(k, sF, sD, sH, sigma3)
    fF = F(meas_r["delta_F"]) + F(meas_r["eps_src"][0])
    fD = F(meas_r["delta_D"]) + F(meas_r["eps_src"][1])
    fH = F(meas_r["delta_H"]) + F(meas_r["eps_src"][2])
    fG = dG + F(meas_r["eps_src"][3])
    e4 = R.env4(sF, sD, sH, F(0), k, sigma4, rho)
    p = R.taylor_bounds(fF, fD, fH, fG, e4, rho)
    rad = R.radius(A, p)
    return {"delta_G": dG, "fG": fG, "env4": e4, "p": p, "rad": rad,
            "half": R.object_half_width(rho, F(0), rad)}


def tail_enclosure(R, meas: dict, aux: dict, A: dict, m: int) -> tuple[F, F, dict]:
    """The theorem-TCT whole-cell enclosure of R''_m on one tail cell (exact interval), frozen-rule path."""
    if m not in M_VALUES:
        raise TCTRefusal(f"m = {m} outside the frozen scope")
    rho = F(meas["rho"])
    k = {i: F(meas["norms"]["k"][i]) for i in range(5)}
    j = {i: F(meas["norms"]["j"][i]) for i in range(5)}
    s0 = {n: F(meas["sup_S0"][n]) for n in range(5)}
    h3 = {jj: F(aux["candidate_suprema"][f"h:{jj}:3"]) + F(aux["midpoint_eps"][f"h:{jj}:3"]) for jj in range(1, 5)}
    tw = h_tower(k, s0, h3)
    obj = {}
    for r in range(5):
        a3 = None if r == 0 else F(aux["candidate_suprema"][f"S:{r}:3"]) + F(aux["midpoint_eps"][f"S:{r}:3"])
        s3 = sigma_source(3, r, j, tw, s0, a3)
        s4 = sigma_source(4, r, j, tw, s0)
        obj[r] = tail_object(R, meas["r"][str(r)], k, rho, A, s3, s4)
        obj[r]["sigma3"], obj[r]["sigma4"] = s3, s4
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


# ------------------------------------------------------------------ independent second path (imports no tc_rule)
def tail_enclosure_crosscheck(meas: dict, aux: dict, A: dict, m: int) -> tuple[F, F]:
    """Independent re-derivation from THEOREM_TCT.md in generic form: the Taylor sums, the P3' envelope written as
    sum_i C(4,i) k_i sup|t|<=rho ||Ftilde^(4-i)(t)|| with Ftilde''' = 0, the resolvent expansion
    rad = sum_i C(2,i) A_i p_(2-i), and the assembly table re-derived from c(m,t) = 1/t - 1/m."""
    from math import factorial
    rho = F(meas["rho"])
    k = [F(x) for x in meas["norms"]["k"]]
    j = {i: F(meas["norms"]["j"][i]) for i in range(5)}
    s0 = {n: F(meas["sup_S0"][n]) for n in range(5)}
    h3 = {jj: F(aux["candidate_suprema"][f"h:{jj}:3"]) + F(aux["midpoint_eps"][f"h:{jj}:3"]) for jj in range(1, 5)}
    tw = h_tower(k={i: k[i] for i in range(5)}, sup_S0=s0, h3=h3)
    Av = [F(A["A0"]), F(A["A1"]), F(A["A2"])]

    def sup_deriv(s, n):                          # sup_|t|<=rho ||Ftilde^(n)(t)||, s = [sF, sD, sH] and s_G = 0
        return sum((s[l] * rho ** (l - n) / factorial(l - n) for l in range(n, 3)), F(0))

    halves = {}
    for r in range(5):
        o = meas["r"][str(r)]
        s = [F(o["sup"][x]) for x in ("F", "D", "H")]
        a3 = None if r == 0 else F(aux["candidate_suprema"][f"S:{r}:3"]) + F(aux["midpoint_eps"][f"S:{r}:3"])
        s3 = sigma_source(3, r, j, tw, s0, a3)
        s4 = sigma_source(4, r, j, tw, s0)
        f = [F(o["delta_F"]) + F(o["eps_src"][0]), F(o["delta_D"]) + F(o["eps_src"][1]),
             F(o["delta_H"]) + F(o["eps_src"][2]),
             k[3] * s[0] + 3 * k[2] * s[1] + 3 * k[1] * s[2] + s3 + F(o["eps_src"][3])]
        env = s4 + sum((comb(4, i) * k[i] * sup_deriv(s, 4 - i) for i in range(1, 5)), F(0))
        p = [sum((f[i] * rho ** (i - n) / factorial(i - n) for i in range(n, 4)), F(0))
             + rho ** (4 - n) / factorial(4 - n) * env for n in range(3)]
        halves[r] = sum((comb(2, i) * Av[i] * p[2 - i] for i in range(3)), F(0))     # |Ghat(a)| = 0
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
    frozen propagate/assembly composes it, and require the rebuild to be CONTAINED in the record interval with a
    relative endpoint agreement within `tol`. (Containment, not equality: the record's enclosure adds its eps as an
    outward-rounded Arb radius, so it is very slightly wider.) A wrong H_at_a or W2 moves an endpoint by O(0.01-1)."""
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
        rows[str(m)] = {"contained": bool(contained), "relative_endpoint_gap": float(rel),
                        "rebuilt": [str(lo), str(hi)], "record": [str(w[0]), str(w[1])]}
    ok = all(v["contained"] for v in rows.values()) and worst <= tol
    return {"pass": bool(ok), "worst_relative_gap": float(worst), "tolerance": float(tol), "per_m": rows}
