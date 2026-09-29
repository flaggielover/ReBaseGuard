"""SRK consumer interface (THEOREM_SRK section 3-4): exact replacement of the order-0 channel term A0*p2.

Inputs per source index r (all exact rationals, fields named as in the frozen tct_rule / theorem TC):
  sF, sD, sH          certified candidate sups
  fF, fD, fH          midpoint premises
  fG                  the frozen order-3 surrogate AS IMPLEMENTED (3k1 sH + 3k2 sD + k3 sF + sigma3 + eps3)
  Env4                the frozen order-4 envelope AS IMPLEMENTED
  sigma3, eps3, sigma4
  rho, A0, A1, A2
and the cell-level SRK certificate values Gamma[1..4] (Gamma_i >= sup_{e in C} (R_e kbar_i^C)(a)).

rad_srk = A0 fH + rho B3 + rho^2/2 B4 + 2 A1 p1 + A2 p0, with
  B3 = min(A0 fG,   A0 (sigma3 + eps3) + 3 sH G1 + 3 sD G2 + sF G3)
  B4 = min(A0 Env4, A0 sigma4 + 6 sH G2 + 4 (sD + rho sH) G3 + (sF + rho sD + rho^2 sH / 2) G4)
Never larger than rad_tct = A0 p2 + 2 A1 p1 + A2 p0 (min construction).  A missing Gamma_i (None) means +infinity.
"""
from __future__ import annotations

from fractions import Fraction as F

REQUIRED = ("sF", "sD", "sH", "fF", "fD", "fH", "fG", "Env4", "sigma3", "eps3", "sigma4", "rho", "A0", "A1", "A2")


class AssemblyRefusal(ValueError):
    pass


def _fr(x) -> F:
    if isinstance(x, bool) or x is None:
        raise AssemblyRefusal(f"not a rational: {x!r}")
    if isinstance(x, float):
        raise AssemblyRefusal("floats are refused (exact rationals only)")
    return F(x)


def validate(fields: dict, gamma: dict) -> tuple:
    missing = [k for k in REQUIRED if k not in fields]
    if missing:
        raise AssemblyRefusal(f"missing fields {missing}")
    f = {k: _fr(fields[k]) for k in REQUIRED}
    neg = [k for k, v in f.items() if v < 0]
    if neg:
        raise AssemblyRefusal(f"negative fields {neg}")
    if f["rho"] <= 0:
        raise AssemblyRefusal("rho must be > 0")
    g = {}
    for i in (1, 2, 3, 4):
        v = gamma.get(i, gamma.get(str(i)))
        if v is None:
            g[i] = None
        else:
            v = _fr(v)
            if v < 0:
                raise AssemblyRefusal(f"negative Gamma_{i}")
            g[i] = v
    return f, g


def p_terms(f: dict) -> tuple:
    rho = f["rho"]
    p2 = f["fH"] + rho * f["fG"] + rho ** 2 * f["Env4"] / 2
    p1 = f["fD"] + rho * f["fH"] + rho ** 2 * f["fG"] / 2 + rho ** 3 * f["Env4"] / 6
    p0 = f["fF"] + rho * f["fD"] + rho ** 2 * f["fH"] / 2 + rho ** 3 * f["fG"] / 6 + rho ** 4 * f["Env4"] / 24
    return p0, p1, p2


def rad_tct(fields: dict) -> F:
    f, _ = validate(fields, {})
    p0, p1, p2 = p_terms(f)
    return f["A0"] * p2 + 2 * f["A1"] * p1 + f["A2"] * p0


def srk_coefficients(f: dict, g: dict) -> tuple:
    """(B3, B4, B3_srk_raw, B4_srk_raw, which3, which4)."""
    A0, rho = f["A0"], f["rho"]
    old3, old4 = A0 * f["fG"], A0 * f["Env4"]
    if None in (g[1], g[2], g[3]):
        new3 = None
    else:
        new3 = A0 * (f["sigma3"] + f["eps3"]) + 3 * f["sH"] * g[1] + 3 * f["sD"] * g[2] + f["sF"] * g[3]
    if None in (g[2], g[3], g[4]):
        new4 = None
    else:
        new4 = (A0 * f["sigma4"] + 6 * f["sH"] * g[2] + 4 * (f["sD"] + rho * f["sH"]) * g[3]
                + (f["sF"] + rho * f["sD"] + rho ** 2 * f["sH"] / 2) * g[4])
    B3 = old3 if new3 is None or new3 >= old3 else new3
    B4 = old4 if new4 is None or new4 >= old4 else new4
    return B3, B4, new3, new4, ("SRK" if B3 != old3 else "TCT"), ("SRK" if B4 != old4 else "TCT")


def rad_srk(fields: dict, gamma: dict) -> dict:
    f, g = validate(fields, gamma)
    p0, p1, p2 = p_terms(f)
    B3, B4, n3, n4, w3, w4 = srk_coefficients(f, g)
    rho = f["rho"]
    rad = f["A0"] * f["fH"] + rho * B3 + rho ** 2 / 2 * B4 + 2 * f["A1"] * p1 + f["A2"] * p0
    base = f["A0"] * p2 + 2 * f["A1"] * p1 + f["A2"] * p0
    assert rad <= base
    return {"rad_srk": rad, "rad_tct": base, "B3": B3, "B4": B4, "B3_srk_raw": n3, "B4_srk_raw": n4,
            "branch3": w3, "branch4": w4}
