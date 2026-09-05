"""Outward-rounded interval helpers over Arb balls.

Arb balls are rigorous: every operation encloses the true result. This module
adds only (a) exact-rational injection, (b) exact-rational scaling that keeps
containment, (c) exact dyadic export so a record never stores a bare float,
and (d) the frozen `outward_upper` used by the cover ledger.

No function here converts a certified quantity to a Python float on a proof
path. `float(...)` appears only in explicitly named diagnostic helpers.
"""
from __future__ import annotations

import sys
from fractions import Fraction as F
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
_PROOF_SRC = _ROOT / "rebaseguard-proof" / "src"
if str(_PROOF_SRC) not in sys.path:
    sys.path.insert(0, str(_PROOF_SRC))

from flint import arb                                             # noqa: E402
from rebaseguard_certify.arb_backend import workprec              # noqa: E402

__all__ = ["workprec", "exact", "lower_fraction", "upper_fraction", "mag_fraction",
           "outward_upper", "ball_of", "scale_exact", "record", "as_float_diagnostic",
           "contains", "hull", "tight_upper"]


def pin_single_thread() -> dict:
    """One FLINT/BLAS thread per worker.

    The frozen memory policy sets `oversubscription_allowed: false`, and CPU
    accounting uses process_time(), which sums every thread. Leaving FLINT or
    OpenBLAS multi-threaded both violates the policy and silently inflates the
    measured CPU seconds (observed: 156% CPU and 15 threads per worker).
    """
    import os
    import flint
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS"):
        os.environ.setdefault(var, "1")
    flint.ctx.threads = 1
    return {"flint_threads": flint.ctx.threads,
            "env": {v: os.environ.get(v) for v in ("OMP_NUM_THREADS",
                                                   "OPENBLAS_NUM_THREADS")}}


def exact(value) -> arb:
    """Exact rational -> arb. Division of two exact integers is outward rounded."""
    q = F(value)
    return arb(q.numerator) / arb(q.denominator)


def tight_upper(x: arb) -> arb:
    """A RADIUS-ZERO Arb >= |x|.

    Certified scalar bounds must be exact upper endpoints, not balls: Arb's
    order comparisons are certified, so `ball >= ball` is False whenever the
    radius is positive, even for the same object. Every delta, envelope,
    operator norm and eps node in this namespace is normalised through here so
    that gate comparisons are decidable and monotone. Enclosures that genuinely
    carry two-sided information (R_interval, D_interval, R2_interval) are NOT
    normalised; they stay balls.
    """
    return x.abs_upper()


def lower_fraction(x: arb) -> F:
    q = x.lower().fmpq()
    return F(int(q.p), int(q.q))


def upper_fraction(x: arb) -> F:
    q = x.upper().fmpq()
    return F(int(q.p), int(q.q))


def mag_fraction(x: arb) -> F:
    """mag(X) = max(|lo|, |hi|) as an exact rational upper bound."""
    q = x.abs_upper().upper().fmpq()
    return F(int(q.p), int(q.q))


def outward_upper(x: arb, *, bits: int = 256) -> F:
    """Frozen cover-ledger export: an exact dyadic rational >= sup(x).

    Rounds up onto the 2^-bits dyadic grid, so the exported scalar is never
    smaller than the certified upper endpoint. Any rounding introduced here is
    part of the cover charge (cover_arithmetic), per ERROR_ALGEBRA section 5.
    """
    hi = upper_fraction(x)
    scale = 1 << bits
    return F(-((-hi.numerator * scale) // hi.denominator), scale)


def ball_of(lo, hi) -> arb:
    """Smallest arb ball containing the exact rational interval [lo, hi]."""
    a, b = exact(lo), exact(hi)
    if not a <= b:
        raise ValueError("reversed interval")
    return a.union(b)


def scale_exact(x: arb, coefficient) -> arb:
    """Multiply an enclosure by an exact rational, keeping containment."""
    return x * exact(coefficient)


def contains(outer: arb, inner: arb) -> bool:
    return bool(outer.contains(inner))


def hull(*balls: arb) -> arb:
    out = balls[0]
    for b in balls[1:]:
        out = out.union(b)
    return out


def record(x: arb) -> dict:
    """Record-schema conformant interval: exact rational endpoints, no float."""
    lo, hi = lower_fraction(x), upper_fraction(x)
    return {"lo": f"{lo.numerator}/{lo.denominator}",
            "hi": f"{hi.numerator}/{hi.denominator}",
            "mag": str(mag_fraction(x)),
            "encoding": "outward exact rational endpoints"}


def as_float_diagnostic(x: arb) -> float:
    """DIAGNOSTIC ONLY. Never a certificate; never used in a gate comparison."""
    return float(x.mid())
