"""Certified n-step SR resolvent bound, and the ResolventCertificate object that
every resolvent consumer must be handed.

Mathematics: SR_NSTEP_RESOLVENT.md.

    Lemma 1 (positivity)   ||T||_inf = ||T 1||_inf for positive T
    Lemma 2 (survival)     (K^n 1)(y) = P_y(tau > n)
    Theorem                (I-K)^{-1} = P_n (I - K^n)^{-1},
                           C_n = ||P_n 1||_inf / (1 - q_n)

so the whole certification reduces to ONE certified iteration

    s_0 = 1 ,   s_{j+1} = K_e s_j ,   q_n = sup s_n ,  ||P_n 1|| = sup sum_{j<n} s_j

WHOLE-DOMAIN COVERAGE, NOT A POINT GRID
---------------------------------------
`s_j` is carried as a piecewise-constant UPPER ENVELOPE over a P x P partition of
[0,b_SR]^2: `U_j[p] >= sup_{y in patch p} s_j(y)`. The step maps a whole patch x
a whole z-panel through the update, encloses the image as an interval box, and
takes the max of `U_j` over every patch that box can meet. No value is ever read
at a point, so no interpolation error can enter.

MONOTONICITY, USED ONLY WHERE PROVED
------------------------------------
Exactly two monotonicity facts are used, both elementary and both asserted in the
tests:
  * `softplus` is strictly increasing, so the image of an interval in `v` is the
    interval of the images -- this is what makes the box enclosure exact;
  * `v^+ = y^+ + z - 1/2` is increasing in both `y^+` and `z`, while
    `v^- = y^- - z - 1/2` is increasing in `y^-` and DECREASING in `z`, which is
    why the minus chart's box uses the swapped z endpoints.
No monotonicity of `s_j` in the state is assumed anywhere.

FREE STABILISER
---------------
`s_j` is a probability, so `0 <= s_j <= 1` for all `j` (Lemma 2). Every envelope
is intersected with `[0,1]`, which costs nothing and stops outward rounding from
compounding across steps.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict, dataclass, field
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
_PROOF = ROOT / "rebaseguard-proof/src"
for _p in (str(_PROOF), str(Path(__file__).resolve().parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flint import arb                                              # noqa: E402

import sr_operators as OPS                                         # noqa: E402
from sr_sources import Phi                                         # noqa: E402


class ResolventNotCertified(RuntimeError):
    """A resolvent constant was requested but no certificate establishes it."""


class OneStepFallbackRefused(RuntimeError):
    """Code attempted the useless 1/(1-k0) one-step constant outside diagnostics."""


class CellMismatch(RuntimeError):
    """A ResolventCertificate was applied to a drift interval it does not cover."""


# ------------------------------------------------------------------ certificate
@dataclass(frozen=True)
class ResolventCertificate:
    """Nested supporting evidence for ||(I - K_e)^{-1}|| on one drift interval.

    This is NOT a top-level K1 obligation and creates no new work ID: it is
    consumed inside the existing F / dF / curvature obligations of the cell whose
    drift interval it covers. It binds its own drift interval so a constant
    certified for one cell can never be silently reused on another.
    """
    n: int
    q_n: str                    # certified sup_y P_y(tau > n), decimal upper bound
    finite_sum_bound: str       # certified ||P_n 1||_inf
    C_n: str                    # ||(I-K)^{-1}|| bound (frozen C_upper, or n-step)
    e_lo: str                   # EXACT rational, e.g. "1/4"
    e_hi: str                   # EXACT rational, e.g. "3/10"
    domain: str                 # "[0,b_SR]^2"
    method: str                 # "interval-DP-upper-envelope"
    partition: int              # P
    z_panels: int
    bits: int
    producer_hash: str = ""
    source_hashes: dict = field(default_factory=dict)

    def constant(self) -> arb:
        return arb(self.C_n)

    def covers(self, e_lo, e_hi) -> bool:
        """Exact rational containment. No float or ball comparison is involved,
        so an equal-endpoint cell is accepted and a marginally wider one is not."""
        return F(self.e_lo) <= F(e_lo) and F(e_hi) <= F(self.e_hi)

    def require_covers(self, e_lo, e_hi) -> None:
        if not self.covers(e_lo, e_hi):
            raise CellMismatch(
                f"certificate covers [{self.e_lo},{self.e_hi}] but the cell is "
                f"[{F(e_lo)},{F(e_hi)}]")

    def to_json(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_frozen_cell(cell: dict) -> "ResolventCertificate":
        """THE AUTHORITATIVE SOURCE OF C: the frozen cover geometry's C_upper.

        `cusum_layer2.py:130` does exactly `self.C = F(cell["C_upper"])`, and
        `C_upper` is part of the frozen cell identity hashed into every record
        (`identity4.py`). It is cover geometry: frozen, per cell, and NOT
        recomputed by the producer. SR must consume it the same way.

        The n-step machinery in this module is therefore CORROBORATION, not the
        primary source -- see `corroborate`.
        """
        e_lo, e_hi = F(cell["left"][0]), F(cell["right"][0])
        return ResolventCertificate(
            n=0, q_n="0", finite_sum_bound="0", C_n=str(F(cell["C_upper"])),
            e_lo=str(e_lo), e_hi=str(e_hi), domain="[0,b_SR]^2",
            method="frozen-cover-geometry-C_upper",
            partition=0, z_panels=0, bits=256)

    def corroborate(self, other: "ResolventCertificate") -> dict:
        """Check an independently certified n-step UPPER bound against this one.

        Both quantities are UPPER bounds on the same norm, so the comparison is
        one-sided and the three outcomes are asymmetric:

          CORROBORATED  independent_C_n <= frozen_C_upper. A rigorous upper bound
                        sits below the frozen constant, so the frozen constant is
                        confirmed safe.
          INCONCLUSIVE  independent_C_n > frozen_C_upper. This is NOT evidence
                        against the frozen constant: a loose enclosure (coarse
                        partition, small n) exceeds it routinely. Refine and
                        retry.
          Falsifying `C_upper` is impossible from upper bounds alone; it would
          require a certified LOWER bound on ||(I-K)^{-1}|| exceeding it, which
          this method deliberately does not pretend to supply.

        Corroboration is NESTED auxiliary evidence. It never replaces or edits
        the frozen constant.
        """
        mine, theirs = F(self.C_n), F(other.C_n)
        corroborated = theirs <= mine
        return {"frozen_C_upper": str(mine), "independent_C_n": str(theirs),
                "status": "CORROBORATED" if corroborated else "INCONCLUSIVE",
                "note": ("independent rigorous upper bound sits below the frozen "
                         "constant" if corroborated else
                         "independent enclosure is looser than the frozen constant; "
                         "this is not evidence against it -- refine partition/n"),
                "ratio_independent_over_frozen": float(theirs / mine) if mine else None,
                "can_falsify_frozen": False,
                "method_frozen": self.method, "method_independent": other.method}


# ------------------------------------------------------------ certified step
def _decimal_upper(x: arb) -> str:
    """A plain decimal string that is provably >= x.

    Arb ball notation is not parseable as an exact rational, and the certificate
    fields must be comparable exactly. The float endpoint is nudged one ULP
    outward and printed with 17 significant digits, which round-trips that float
    exactly, so the stored decimal is >= the true value.
    """
    v = float(x.abs_upper().upper())
    return f"{math.nextafter(v, math.inf):.17g}"


def _softplus(u: arb) -> arb:
    """log(1+exp(u)), stable branch split, rigorous on balls. Strictly increasing."""
    if u.lower() >= 0:
        return u + (arb(1) + (-u).exp()).log()
    return (arb(1) + u.exp()).log()


def _panel_mass_upper(z_lo: arb, z_hi: arb, e: arb) -> arb:
    """Upper bound on int_{z_lo}^{z_hi} phi(z+e) dz (never negative)."""
    v = Phi(z_hi + e) - Phi(z_lo + e)
    up = v.abs_upper()
    return arb(up) if up > 0 else arb(0)


def certify(e_lo, e_hi, n: int, *, partition: int = 24,
            z_panels: int = 24, bits: int = 256) -> ResolventCertificate:
    """Certify (q_n, ||P_n 1||, C_n) for every drift in [e_lo, e_hi].

    `e_lo`, `e_hi` are EXACT rationals (Fraction, int, or a string like "1/4"),
    matching how the frozen spec stores drift endpoints. The drift enters only
    through phi(z+e); the panel mass is enclosed over the WHOLE drift interval,
    so the resulting constant is valid uniformly on the cell, which is what the
    whole-cell cover obligation needs.
    """
    fe_lo, fe_hi = F(e_lo), F(e_hi)
    if fe_hi < fe_lo:
        raise ValueError("empty drift interval")
    e_lo = arb(fe_lo.numerator) / arb(fe_lo.denominator)
    e_hi = arb(fe_hi.numerator) / arb(fe_hi.denominator)
    _A, b, c = OPS.sr_constants()
    P = partition
    h = b / arb(P)
    e_iv = (e_lo + e_hi) / arb(2) + arb(0, ((e_hi - e_lo) / arb(2)).abs_upper())

    # patch edges in the state variable
    edge = [b * arb(i) / arb(P) for i in range(P + 1)]

    # For each patch (i,j): l in [edge[j]-c, edge[j+1]-c], u in [c-edge[i+1], c-edge[i]]
    # widest continuation interval for the patch:
    z_lo_p = [[edge[j] - c for j in range(P)] for _i in range(P)]
    z_hi_p = [[c - edge[i] for _j in range(P)] for i in range(P)]

    U = [[arb(1) for _ in range(P)] for _ in range(P)]      # s_0 = 1
    CUM = [[arb(1) for _ in range(P)] for _ in range(P)]    # sum_{j<1} s_j
    q_hist = [arb(1)]

    for _step in range(n):
        Unew = [[arb(0) for _ in range(P)] for _ in range(P)]
        for i in range(P):
            for j in range(P):
                zl, zh = z_lo_p[i][j], z_hi_p[i][j]
                if not (zh - zl).lower() > 0:
                    Unew[i][j] = arb(0)
                    continue
                width = (zh - zl) / arb(z_panels)
                acc = arb(0)
                for k in range(z_panels):
                    pz_lo = zl + width * arb(k)
                    pz_hi = zl + width * arb(k + 1)
                    mass = _panel_mass_upper(pz_lo, pz_hi, e_iv)
                    if not mass > 0:
                        continue
                    # image box of patch x panel under the update (monotone)
                    vp_lo = edge[i] + pz_lo - arb(1) / arb(2)
                    vp_hi = edge[i + 1] + pz_hi - arb(1) / arb(2)
                    vm_lo = edge[j] - pz_hi - arb(1) / arb(2)
                    vm_hi = edge[j + 1] - pz_lo - arb(1) / arb(2)
                    yp_lo, yp_hi = _softplus(vp_lo), _softplus(vp_hi)
                    ym_lo, ym_hi = _softplus(vm_lo), _softplus(vm_hi)
                    ia = max(0, min(P - 1, int(float((yp_lo / h).lower()))))
                    ib = max(0, min(P - 1, int(float((yp_hi / h).upper())) ))
                    ja = max(0, min(P - 1, int(float((ym_lo / h).lower()))))
                    jb = max(0, min(P - 1, int(float((ym_hi / h).upper())) ))
                    best = arb(0)
                    for a in range(ia, ib + 1):
                        for bb in range(ja, jb + 1):
                            if U[a][bb] > best:
                                best = U[a][bb]
                    acc = acc + best * mass
                one = arb(1)
                Unew[i][j] = acc if (acc < one) else one       # s <= 1, free stabiliser
        U = Unew
        for i in range(P):
            for j in range(P):
                CUM[i][j] = CUM[i][j] + U[i][j]
        q_hist.append(max(U[i][j] for i in range(P) for j in range(P)))

    q_n = q_hist[-1]
    # ||P_n 1|| = sup_y sum_{j<n} s_j : CUM currently holds sum_{j<=n}; drop s_n
    Pn = arb(0)
    for i in range(P):
        for j in range(P):
            v = CUM[i][j] - U[i][j]
            if v > Pn:
                Pn = v
    if not (q_n < arb(1)):
        raise ResolventNotCertified(
            f"q_{n} = {q_n.str(12)} is not certified < 1; increase n")
    C_n = arb(Pn.abs_upper()) / (arb(1) - arb(q_n.abs_upper()))
    return ResolventCertificate(
        n=n, q_n=_decimal_upper(q_n), finite_sum_bound=_decimal_upper(Pn),
        C_n=_decimal_upper(C_n), e_lo=str(fe_lo), e_hi=str(fe_hi),
        domain="[0,b_SR]^2", method="interval-DP-upper-envelope",
        partition=partition, z_panels=z_panels, bits=bits)


def naive_one_step_constant(e: arb, *, diagnostics_only: bool = False) -> arb:
    """The useless 1/(1-k0). Refuses to run unless explicitly asked for diagnostics."""
    if not diagnostics_only:
        raise OneStepFallbackRefused(
            "1/(1-k0) is not a usable SR resolvent constant (k0 = 1 - 1.4e-11). "
            "Supply a ResolventCertificate from sr_nstep.certify().")
    return arb(1) / (arb(1) - OPS.one_step_norms(e)["k0"])


def load(path: Path) -> ResolventCertificate:
    return ResolventCertificate(**json.loads(Path(path).read_text()))
