"""Minimal proof-critical wrappers around FLINT/Arb real balls."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from flint import arb, ctx


@contextmanager
def workprec(bits: int) -> Iterator[None]:
    if bits < 64:
        raise ValueError("proof precision must be at least 64 bits")
    with ctx.workprec(bits):
        yield


def rational(numerator: int, denominator: int = 1) -> arb:
    if denominator == 0:
        raise ZeroDivisionError("zero denominator")
    return arb(numerator) / arb(denominator)


def gaussian_phi(x: arb) -> arb:
    two = arb(2)
    return (-(x * x) / two).exp() / (two * arb.pi()).sqrt()


def gaussian_cdf(x: arb) -> arb:
    return (arb(1) + (x / arb(2).sqrt()).erf()) / arb(2)


def gaussian_mass(lower: arb, upper: arb) -> arb:
    if not lower <= upper:
        raise ValueError("lower endpoint must not exceed upper endpoint")
    return gaussian_cdf(upper) - gaussian_cdf(lower)


def gaussian_first_moment(lower: arb, upper: arb) -> arb:
    if not lower <= upper:
        raise ValueError("lower endpoint must not exceed upper endpoint")
    return gaussian_phi(lower) - gaussian_phi(upper)


def gaussian_tail_second_moment(cutoff: arb, *, upper: bool) -> arb:
    density = gaussian_phi(cutoff)
    if upper:
        return cutoff * density + (arb(1) - gaussian_cdf(cutoff))
    return gaussian_cdf(cutoff) - cutoff * density


def ball_record(value: arb, *, digits: int = 80) -> dict[str, str]:
    """Return a parseable enclosing ball and redundant endpoint enclosures."""

    return {
        "ball": value.str(digits, radius=True),
        "lower_enclosure": value.lower().str(digits, radius=True),
        "upper_enclosure": value.upper().str(digits, radius=True),
    }

