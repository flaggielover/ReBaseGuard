"""Exact additive attribution of SR whole-cell width to its primitive sources.

Every bound in `sr_propagate` is a sum of products with NON-NEGATIVE coefficients,
so each output is exactly a sum of contributions, each traceable to the additive
source term where it entered and to the number of resolvent factors `C` it picked
up on the way. This module carries that decomposition alongside the arithmetic
instead of reconstructing it afterwards, so the attribution is exact by
construction: `sum(contributions) == the bound`, asserted in the tests.

A contribution is keyed by (origin, c_power):

    origin   the additive term where the quantity entered the chain, e.g.
             "S_r"        the source object              (source uncertainty)
             "S_r'" "S_r''"  its e-derivatives           (derivative source)
             "e*h_1"      the raw-variable drift term    (raw-variable source)
             "h_1"        the bare +h_1 in the D equation
             "2*h_1'"     the order-2 analogue in the H equation
    c_power  how many resolvent factors multiply it (1, 2 or 3)

`c_power` is the amplification depth, and it is what the midpoint refinement
attacks: a contribution at `c_power = k` costs `C^k`, and refinement replaces the
tower for the midpoint VALUE while leaving only the cell-radius VARIATION at that
depth.

Nothing here is a certificate. It is exact bookkeeping of the existing bound.
"""
from __future__ import annotations

import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
IMPL = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code"
SPECC = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor/code"
for _p in (str(IMPL), str(SPECC), str(Path(__file__).resolve().parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flint import arb                                              # noqa: E402

import assembly                                                    # noqa: E402
import spec                                                        # noqa: E402
import sr_operators as OPS                                         # noqa: E402
import sr_propagate as P                                           # noqa: E402

R_MAX = 5


class Attributed:
    """A non-negative bound carrying its exact additive decomposition."""

    __slots__ = ("parts",)

    def __init__(self, parts: dict | None = None):
        self.parts: dict[tuple[str, int], arb] = dict(parts or {})

    @staticmethod
    def leaf(origin: str, value: arb, c_power: int = 0) -> "Attributed":
        return Attributed({(origin, c_power): value})

    def total(self) -> arb:
        t = arb(0)
        for v in self.parts.values():
            t = t + v
        return t

    def __add__(self, other: "Attributed") -> "Attributed":
        out = dict(self.parts)
        for k, v in other.parts.items():
            out[k] = out.get(k, arb(0)) + v
        return Attributed(out)

    def scale(self, factor: arb) -> "Attributed":
        return Attributed({k: v * factor for k, v in self.parts.items()})

    def amplify(self, factor: arb) -> "Attributed":
        """Multiply by the resolvent constant, incrementing the amplification depth."""
        return Attributed({(o, p + 1): v * factor for (o, p), v in self.parts.items()})


def attributed_cell(cell: dict, *, grid: int = 8) -> dict:
    """Reproduce sr_propagate's bounds for one frozen cell, with attribution."""
    lo, hi = F(cell["left"][0]), F(cell["right"][0])
    rho = abs(F(cell["rho"][0]))
    C = arb(F(cell["C_upper"]).numerator) / arb(F(cell["C_upper"]).denominator)
    e_lo = arb(lo.numerator) / arb(lo.denominator)
    e_hi = arb(hi.numerator) / arb(hi.denominator)
    e_mid = (e_lo + e_hi) / arb(2)
    e_abs = arb(max(e_lo.abs_upper(), e_hi.abs_upper()))

    norms = OPS.one_step_norms(e_mid)
    k1, k2 = norms["k1"], norms["k2"]
    s0 = P.s0_cell_envelope(e_lo, e_hi, grid=grid)
    h = P.h_chain(norms)
    s = P.s_chain(norms, h, s0)
    idx = sorted({(r, j) for m in spec.M_VALUES
                  for kind, r, j, _c in assembly.coefficients(m) if kind == "W"})
    w = P.w_chain(norms, s, idx)

    # ---- resolvent system, with attribution
    A: dict[tuple[int, int], Attributed] = {}
    for r in range(R_MAX):
        src_F = (Attributed.leaf("S_r  (source uncertainty)", s[(r, 0)])
                 + Attributed.leaf("e*h_1  (raw-variable drift)", e_abs * h[(1, 0)]))
        Fr = src_F.amplify(C)
        src_D = (Fr.scale(k1)
                 + Attributed.leaf("S_r'  (derivative source)", s[(r, 1)])
                 + Attributed.leaf("h_1  (bare raw-variable term)", h[(1, 0)])
                 + Attributed.leaf("e*h_1'  (drift x reward deriv)", e_abs * h[(1, 1)]))
        Dr = src_D.amplify(C)
        src_H = (Fr.scale(k2) + Dr.scale(arb(2) * k1)
                 + Attributed.leaf("S_r''  (2nd derivative source)", s[(r, 2)])
                 + Attributed.leaf("2*h_1'  (order-2 raw term)", arb(2) * h[(1, 1)])
                 + Attributed.leaf("e*h_1''  (drift x 2nd reward deriv)",
                                   e_abs * h[(1, 2)]))
        Hr = src_H.amplify(C)
        A[(r, 0)], A[(r, 1)], A[(r, 2)] = Fr, Dr, Hr

    # ---- assembly (exact frozen rational coefficients)
    per_m = {}
    for m in spec.M_VALUES:
        out = {}
        for k in (0, 1, 2):
            acc = Attributed()
            for kind, r, j, c in assembly.coefficients(m):
                coef = arb(abs(c).numerator) / arb(abs(c).denominator)
                if kind == "F":
                    acc = acc + A[(r, k)].scale(coef)
                else:
                    acc = acc + Attributed.leaf(
                        "W_(r,j)  (finite kernel powers)", w[(r, j, k)] * coef)
            out[k] = acc
        per_m[m] = out

    return {"cell": int(cell["index"]), "rho": rho, "C_upper": F(cell["C_upper"]),
            "e_lo": lo, "e_hi": hi, "per_m": per_m, "norms": norms}


def cover_decomposition(cell: dict, m: int = 2, *, grid: int = 8) -> dict:
    """Rank the sources of `W_cover = rho|D| + rho^2 M_R2/2` for one cell."""
    a = attributed_cell(cell, grid=grid)
    rho = arb(a["rho"].numerator) / arb(a["rho"].denominator)
    D, R2 = a["per_m"][m][1], a["per_m"][m][2]
    lin = D.scale(rho)                                  # rho * |D|
    curv = R2.scale(rho * rho / arb(2))                 # rho^2 * M_R2 / 2
    total = lin + curv
    budget = spec.TOP_BUDGETS["B_cover"]
    B = arb(budget.numerator) / arb(budget.denominator)

    ranked = sorted(((o, p, v) for (o, p), v in total.parts.items()),
                    key=lambda t: -float(t[2].abs_upper().mid()))
    tot = total.total()
    by_power: dict[int, arb] = {}
    for (_o, p), v in total.parts.items():
        by_power[p] = by_power.get(p, arb(0)) + v
    return {
        "cell": a["cell"], "m": m, "rho": a["rho"], "C_upper": a["C_upper"],
        "linear_term": lin.total(), "curvature_term": curv.total(),
        "W_cover": tot, "utilisation": tot / B,
        "linear_over_curvature": lin.total() / curv.total(),
        "ranked": [(o, p, v, float((v / tot).mid())) for o, p, v in ranked],
        "by_c_power": {p: (v, float((v / tot).mid())) for p, v in sorted(by_power.items())},
    }


NOT_INSTRUMENTED = (
    "candidate approximation error",
    "patch-local truncation error",
    "z-panel / Gaussian moment tail",
    "exact-dyadic rounding of candidates",
)
"""Width sources that do NOT yet exist in this layer.

The current chain is a sup-norm envelope: it has no patch-resolved candidate, so
these four sources are structurally absent rather than measured as zero. They
enter with the Phase-8 patch-resolved layer and are listed here so the ranked
table cannot be mistaken for a complete accounting of the eventual certifier.
"""
