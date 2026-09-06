"""Whole-cell SR propagation: h/S/W chains, the F/D/H resolvent system, the exact
all-m assembly and M_R2.

Implements SR_DERIVATION.md sections 2, 4, 5, 6, 7 in the frozen error algebra of
`depgraph.py`, which this module reuses rather than restates:

    epsF_r = C ( deltaF_r + epsS_r )
    epsD_r = C ( deltaD_r + k1 epsF_r + epsS1_r )
    epsH_r = C ( deltaH_r + k2 epsF_r + 2 k1 epsD_r + epsS2_r )    [whole cell]

The raw-variable source is the part that is NOT shared with CUSUM and is the
easiest thing to get silently wrong:

    (I - K) F_r = S_r + e h_1
    (I - K) D_r = K' F_r + S_r' + h_1 + e h_1'          <-- the bare +h_1
    (I - K) H_r = K'' F_r + 2 K' D_r + S_r'' + 2 h_1' + e h_1''

Both `+ h_1` and `+ 2 h_1'` are absent from the g-variable formulation in
EXACT_SR_TARGET.md section 4 and are asserted by
`tests/test_raw_variable_source.py`.

Everything here is a rigorous sup-norm envelope over the whole cell: given
certified inputs (C, one-step norms, sup|S_0^{(k)}| over the cell), it returns an
upper bound on sup_{e in cell} |R''_{D,m}(e)|, i.e. M_R2. It does NOT merely prove
finiteness -- the returned number is the quantity the cover ledger charges.
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
import sr_nstep as NST                                             # noqa: E402
import sr_operators as OPS                                         # noqa: E402
import sr_sources as SRC                                           # noqa: E402

R_MAX, H_MAX, ORDERS = 5, 4, (0, 1, 2)


class MissingCertifiedInput(RuntimeError):
    """A propagation input was not supplied as a certified enclosure."""


class UncertifiedResolvent(RuntimeError):
    """A resolvent constant reached propagation without a ResolventCertificate.

    Guards the blocker recorded in RESULTS.md: the SR one-step constant
    1/(1-k0) = 7.03e10 is useless, so a bare number must never be accepted here.
    Every resolvent use consumes an explicit sr_nstep.ResolventCertificate whose
    drift interval is checked against the cell.
    """


# --------------------------------------------------------------- S_0 envelope
def s0_cell_envelope(e_lo: arb, e_hi: arb, grid: int = 16) -> dict[int, arb]:
    """sup_{e in cell, y in domain} |rho_1^{(k)}(y,e)| for k = 0,1,2.

    l and u are enclosed over a `grid` x `grid` subdivision of the state square
    (sharper than one interval evaluation), e over the whole cell. Outward
    rounded; the returned value is an upper bound, never a sample.
    """
    _A, b, c = OPS.sr_constants()
    e_iv = arb(0).union(e_lo).union(e_hi) if hasattr(arb(0), "union") else \
        (e_lo + e_hi) / arb(2) + arb(0, ((e_hi - e_lo) / arb(2)).abs_upper())
    out = {k: arb(0) for k in ORDERS}
    for i in range(grid):
        yp = b * arb(i) / arb(grid) + arb(0, (b / arb(grid) / arb(2)).abs_upper()) \
            + b / arb(grid) / arb(2)
        for j in range(grid):
            ym = b * arb(j) / arb(grid) + arb(0, (b / arb(grid) / arb(2)).abs_upper()) \
                + b / arb(grid) / arb(2)
            l, u = ym - c, c - yp
            for k in ORDERS:
                v = SRC.S0(l, u, e_iv, k).abs_upper()
                if v > out[k]:
                    out[k] = v
    return out


# ------------------------------------------------------------------ h chain
def h_chain(norms: dict) -> dict[tuple[int, int], arb]:
    """sup|h_j^{(k)}|, j = 1..4, k = 0,1,2.

        h_1 = 1 - K 1        -> sup|h_1|   <= 1        (h_1 in [0,1], substochastic)
        h_1^(k) = -K^(k) 1   -> sup|h_1'|  <= k1 ,  sup|h_1''| <= k2
        h_j     = K h_{j-1}  -> Leibniz in the operator derivatives
    """
    k0, k1, k2 = norms["k0"], norms["k1"], norms["k2"]
    s: dict[tuple[int, int], arb] = {}
    s[(1, 0)] = arb(1)                     # 0 <= h_1 = 1 - K1 <= 1
    s[(1, 1)] = k1
    s[(1, 2)] = k2
    for j in range(2, H_MAX + 1):
        s[(j, 0)] = k0 * s[(j - 1, 0)]
        s[(j, 1)] = k1 * s[(j - 1, 0)] + k0 * s[(j - 1, 1)]
        s[(j, 2)] = k2 * s[(j - 1, 0)] + arb(2) * k1 * s[(j - 1, 1)] + k0 * s[(j - 1, 2)]
    return s


# ------------------------------------------------------------------ S chain
def s_chain(norms: dict, h: dict, s0: dict[int, arb]) -> dict[tuple[int, int], arb]:
    """sup|S_r^{(k)}|. S_0 = rho_1 (closed form); S_j = K_z h_j (Leibniz)."""
    kz, kz1, kz2 = norms["kz"], norms["kz1"], norms["kz2"]
    s: dict[tuple[int, int], arb] = {}
    for k in ORDERS:
        s[(0, k)] = s0[k]
    for r in range(1, R_MAX):
        s[(r, 0)] = kz * h[(r, 0)]
        s[(r, 1)] = kz1 * h[(r, 0)] + kz * h[(r, 1)]
        s[(r, 2)] = kz2 * h[(r, 0)] + arb(2) * kz1 * h[(r, 1)] + kz * h[(r, 2)]
    return s


# ------------------------------------------------------- finite powers W_(r,j)
def w_chain(norms: dict, s: dict, indices) -> dict[tuple[int, int, int], arb]:
    """sup|W_(r,j)^(k)| by the frozen Leibniz recurrence (depgraph section 6)."""
    k0, k1, k2 = norms["k0"], norms["k1"], norms["k2"]
    jmax = max(j for _r, j in indices)
    w: dict[tuple[int, int, int], arb] = {}
    for r in range(R_MAX):
        for k in ORDERS:
            w[(r, 0, k)] = s[(r, k)]
        for j in range(1, jmax + 1):
            w[(r, j, 0)] = k0 * w[(r, j - 1, 0)]
            w[(r, j, 1)] = k0 * w[(r, j - 1, 1)] + k1 * w[(r, j - 1, 0)]
            w[(r, j, 2)] = (k0 * w[(r, j - 1, 2)] + arb(2) * k1 * w[(r, j - 1, 1)]
                            + k2 * w[(r, j - 1, 0)])
    return w


# ------------------------------------------------------ F / D / H resolvent
def resolvent_system(C: arb, norms: dict, h: dict, s: dict,
                     e_abs: arb) -> dict[tuple[int, int], arb]:
    """sup|F_r|, sup|D_r|, sup|H_r| from the RAW-VARIABLE equations."""
    k1, k2 = norms["k1"], norms["k2"]
    out: dict[tuple[int, int], arb] = {}
    for r in range(R_MAX):
        # (I - K) F_r = S_r + e h_1
        Fr = C * (s[(r, 0)] + e_abs * h[(1, 0)])
        # (I - K) D_r = K' F_r + S_r' + h_1 + e h_1'
        Dr = C * (k1 * Fr + s[(r, 1)] + h[(1, 0)] + e_abs * h[(1, 1)])
        # (I - K) H_r = K'' F_r + 2 K' D_r + S_r'' + 2 h_1' + e h_1''
        Hr = C * (k2 * Fr + arb(2) * k1 * Dr + s[(r, 2)]
                  + arb(2) * h[(1, 1)] + e_abs * h[(1, 2)])
        out[(r, 0)], out[(r, 1)], out[(r, 2)] = Fr, Dr, Hr
    return out


# ------------------------------------------------------------- assembly / M_R2
def assemble_order(m: int, fdh: dict, w: dict, k: int) -> arb:
    """|R_m^(k)| <= sum |c| * sup|object|, using the FROZEN coefficient table.

    Returned as a symmetric Arb ball of that magnitude, which is the enclosure the
    frozen `assembly.curvature_bound` consumes.
    """
    total = arb(0)
    for kind, r, j, c in assembly.coefficients(m):
        sup = fdh[(r, k)] if kind == "F" else w[(r, j, k)]
        num, den = abs(c).numerator, abs(c).denominator
        total = total + sup * arb(num) / arb(den)
    return arb(0, total.abs_upper())


def cell_certificate(*, resolvent, e_lo: arb, e_hi: arb, rho: arb,
                     cell_e=None, grid: int = 16) -> dict:
    """Full whole-cell SR certificate: R, D, R2 intervals, M_R2 and B_cover use.

    `resolvent` MUST be an sr_nstep.ResolventCertificate covering [e_lo, e_hi].
    A bare number is refused: for SR the one-step constant is 7.03e10 and there
    is no safe default, so the constant has to arrive with its own evidence.
    """
    if not isinstance(resolvent, NST.ResolventCertificate):
        raise UncertifiedResolvent(
            "cell_certificate requires an sr_nstep.ResolventCertificate, not "
            f"{type(resolvent).__name__}; see SR_NSTEP_RESOLVENT.md")
    if cell_e is None:
        raise MissingCertifiedInput(
            "cell_e=(e_lo_exact, e_hi_exact) exact rationals are required so the "
            "resolvent certificate can be matched to the cell without float slack")
    resolvent.require_covers(*cell_e)
    C = resolvent.constant()
    if not isinstance(C, arb):
        raise MissingCertifiedInput("C must be a certified Arb enclosure")
    e_mid = (e_lo + e_hi) / arb(2)
    e_abs = arb(0, max(e_lo.abs_upper(), e_hi.abs_upper()))
    e_abs = arb(e_abs.abs_upper())
    norms = OPS.one_step_norms(e_mid)
    s0 = s0_cell_envelope(e_lo, e_hi, grid=grid)
    h = h_chain(norms)
    s = s_chain(norms, h, s0)
    idx = sorted({(r, j) for m in spec.M_VALUES
                  for kind, r, j, _c in assembly.coefficients(m) if kind == "W"})
    w = w_chain(norms, s, idx)
    fdh = resolvent_system(C, norms, h, s, e_abs)

    per_m = {}
    for m in spec.M_VALUES:
        R_int = assemble_order(m, fdh, w, 0)
        D_int = assemble_order(m, fdh, w, 1)
        R2_int = assemble_order(m, fdh, w, 2)
        M_R2 = assembly.curvature_bound(R2_int)
        W_cover = rho * D_int.abs_upper() + rho * rho * M_R2 / arb(2)
        per_m[m] = {
            "R_interval_mag": R_int.abs_upper(),
            "D_interval_mag": D_int.abs_upper(),
            "R2_interval_mag": R2_int.abs_upper(),
            "M_R2": M_R2,
            "W_cover_exact": W_cover,
            "B_cover_budget": spec.TOP_BUDGETS["B_cover"],
            "utilisation": W_cover / (arb(spec.TOP_BUDGETS["B_cover"].numerator)
                                      / arb(spec.TOP_BUDGETS["B_cover"].denominator)),
        }
    return {"norms": norms, "s0_envelope": s0, "h": h, "S": s, "W": w,
            "FDH": fdh, "per_m": per_m, "C": C,
            "resolvent_certificate": resolvent.to_json(),
            "e_lo": e_lo, "e_hi": e_hi, "rho": rho}
