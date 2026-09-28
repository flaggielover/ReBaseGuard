"""Cell-307 RLR campaign (r1) -- INDEPENDENT reconstruction of every composition layer above the certifier.

Written from THEOREM_RLR307 section 1 (not from `c1b_certpw.assemble` or `rlr307_stage1`). It imports no campaign or
certifier module; it takes exact inputs and returns exact outputs, so equality with the pinned path is a real
two-sided check (brief section 10). Shared surface with the pinned path: NONE of the code below; the only shared
objects are the certified inputs themselves and the two rational constants kappa1, kappa2, whose validity as upper
bounds is checked here independently (`kappa_check`, 60-digit decimal arithmetic).

Layers:
  L-A  block supply from certified inputs (declaration D14 as stated in THEOREM_RLR307 section 1)
  L-B  ladder composition over certified rungs (Lemma Lad)
  L-C  cell composition over blocks (Lemma H: worst block)
  L-D  consumed supply S_RLR = (A0_I1, min(A1_I1, A1_cell), min(A2_I1, A2_cell))
  L-E  Lemma Dv' r2 and Lemma G for the committed I1 members (THEOREM_AD section 4; THEOREM_TCT section 1)
"""
from __future__ import annotations

import decimal
from fractions import Fraction

UPPER_KEYS = ("C_R", "tau", "C_T", "A_bar", "tau_a_up", "S2_up", "TN_up", "D1", "D2", "L1_up", "L2_up")
LOWER_KEYS = ("tau_a_lo", "D_lo", "Lambda_lo")


def q(x) -> Fraction:
    if isinstance(x, float):
        raise TypeError("a float reached an exact layer")
    return Fraction(x)


def block_supply(inp: dict, kappa1, kappa2) -> dict:
    """L-A. inp: A_bar, tau, D_lo, C_T, D1, D2, L1_up, L2_up, tau_a_lo, C_R (exact)."""
    Ab, t, Dl, CT = q(inp["A_bar"]), q(inp["tau"]), q(inp["D_lo"]), q(inp["C_T"])
    D1, D2, L1, L2, tlo, CR = q(inp["D1"]), q(inp["D2"]), q(inp["L1_up"]), q(inp["L2_up"]), q(inp["tau_a_lo"]), q(inp["C_R"])
    k1, k2 = q(kappa1), q(kappa2)
    if not (Dl > 0 and tlo > 0):
        raise ValueError("D_lo and tau_a,lo must be positive")
    lam = t / Dl
    Aeff = Ab if Ab <= lam else lam
    d1, d2 = D1 / Dl, D2 / Dl
    rlr1, rlr2 = Aeff * (L1 / tlo), Aeff * (L2 / tlo)                 # ratio form
    nr1, nr2 = L1 / Dl, L2 / Dl                                         # non-ratio form
    dv1 = Aeff * (k1 * CT)                                              # Dv' factor, first order
    dv2 = Aeff * (2 * k1 * k1 * CT * CT + k2 * CT)                      # Dv' factor, second order
    c1 = min(rlr1, nr1, dv1)
    c2 = min(rlr2, nr2, dv2)
    g0, g1, g2 = CR, k1 * CR * CR, k2 * CR * CR + 2 * k1 * k1 * CR * CR * CR
    a1 = c1 + Aeff * d1
    a2 = c2 + 2 * c1 * d1 + Aeff * (2 * d1 * d1 + d2)
    return {"A0_SUPPLY": min(Aeff, g0), "A1_SUPPLY": min(a1, g1), "A2_SUPPLY": min(a2, g2),
            "G0": g0, "G1": g1, "G2": g2, "A_eff": Aeff,
            "binding_A1": "G" if g1 < a1 else ("RLR_ratio" if c1 == rlr1 else "RLR_nonratio" if c1 == nr1 else "Dv"),
            "binding_A2": "G" if g2 < a2 else ("RLR_ratio" if c2 == rlr2 else "RLR_nonratio" if c2 == nr2 else "Dv")}


def ladder(rungs: list) -> dict | None:
    """L-B. rungs: exact records of CERTIFIED rungs only (the caller filters by status)."""
    if not rungs:
        return None
    out = {k: min(q(r[k]) for r in rungs) for k in UPPER_KEYS}
    out.update({k: max(q(r[k]) for r in rungs) for k in LOWER_KEYS})
    return out


def cell(blocks: list) -> dict:
    """L-C. blocks: per-block supplies (exact); None marks an uncertified block."""
    if not blocks or any(b is None for b in blocks):
        return {"status": "CERTIFICATION_FAILED"}
    return {"status": "CERTIFIED", **{k: max(q(b[k]) for b in blocks) for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY")}}


def consumed(s_i1: dict, cell_rec: dict) -> dict:
    """L-D. A0 is the committed I1 value, unchanged; A1, A2 are componentwise minima."""
    return {"A0": q(s_i1["A0"]), "A1": min(q(s_i1["A1"]), q(cell_rec["A1_SUPPLY"])),
            "A2": min(q(s_i1["A2"]), q(cell_rec["A2_SUPPLY"]))}


def dv_prime_r2(Abar, tau, C, Dlo, D1, D2, k1, k2) -> dict:
    """L-E. THEOREM_AD Lemma Dv' (r2)."""
    Abar, tau, C, Dlo, D1, D2, k1, k2 = map(q, (Abar, tau, C, Dlo, D1, D2, k1, k2))
    eff = min(Abar, tau / Dlo)
    d1, d2 = D1 / Dlo, D2 / Dlo
    return {"A0": eff, "A1": eff * (k1 * C + d1),
            "A2": eff * (2 * k1 * k1 * C * C + k2 * C + 2 * k1 * C * d1 + 2 * d1 * d1 + d2)}


def lemma_g(C, k1, k2) -> dict:
    C, k1, k2 = q(C), q(k1), q(k2)
    return {"A0": C, "A1": k1 * C * C, "A2": k2 * C * C + 2 * k1 * k1 * C * C * C}


def componentwise_min(supplies: dict) -> dict:
    return {j: min(q(s[j]) for s in supplies.values()) for j in ("A0", "A1", "A2")}


def kappa_check(kappa1, kappa2) -> dict:
    """kappa1 >= E|Y| = sqrt(2/pi) and kappa2 >= E|Y^2 - 1| = 4 phi(1) = 4 exp(-1/2)/sqrt(2 pi), Y ~ N(0,1).
    Decimal arithmetic at 80 significant digits for EVERY operation (a local context; the first version of this
    function let `/`, `+` and `*` fall back to the default 28-digit context and reported a spurious 6e-28 deficit),
    with its own pi (Machin formula) and exp(-1/2) series. Truncation errors are < 1e-75, far below any margin."""
    with decimal.localcontext(decimal.Context(prec=80)):
        D = decimal.Decimal

        def arctan_inv(n: int):                   # arctan(1/n) by its alternating series
            x, n2, k, s, sign = D(1) / D(n), D(n) * D(n), 1, D(0), 1
            term = x
            while True:
                t = term / D(k)
                if t == 0 or t.adjusted() < -78:
                    break
                s = s + t if sign > 0 else s - t
                term, k, sign = term / n2, k + 2, -sign
            return s

        pi = 4 * (4 * arctan_inv(5) - arctan_inv(239))
        e_half, term, k = D(0), D(1), 0
        while term != 0 and term.adjusted() > -79:   # exp(-1/2)
            e_half += term
            k += 1
            term = term * D(-1) / (D(2) * D(k))
        k1_true = (D(2) / pi).sqrt()
        k2_true = 4 * e_half / (2 * pi).sqrt()
        k1, k2 = q(kappa1), q(kappa2)
        k1_dec, k2_dec = D(k1.numerator) / D(k1.denominator), D(k2.numerator) / D(k2.denominator)
        return {"kappa1_ge_sqrt_2_over_pi": k1_dec >= k1_true, "kappa2_ge_4phi1": k2_dec >= k2_true,
                "kappa1_margin": f"{k1_dec - k1_true:.6E}", "kappa2_margin": f"{k2_dec - k2_true:.6E}",
                "pi_check": str(pi)[:22], "precision_digits": 80}
