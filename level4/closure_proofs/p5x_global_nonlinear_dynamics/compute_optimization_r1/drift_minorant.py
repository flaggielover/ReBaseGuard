"""P5X Compute Optimization R1 — drift-explicit monotone resolvent minorant.

Proof-critical.  This module changes ONE thing: the rigorous upper bound used
for ``||(I - K_e)^{-1}||_inf``.  It changes no operator, no reward, no kernel,
no state space, no stopping convention, no estimand and no enclosure semantics.
See ``NEUTRALITY_AUDIT.md`` and ``PROOF.md`` in this directory.

Why it matters for cost.  In R-A' the sub-cell half-width is the frozen formula
``h = 1/(4 a C)``, so the number of sub-cells -- and hence the whole runtime --
is *directly proportional to C*.  R-A' used the drift-explicit **block-forcing**
bound, which is rigorous but crude: it asks for a run of n innovations whose sum
alone clears ``h + nk``, ignoring everything the chain does in between.

The replacement is the **one-sided monotone Bellman minorant** already certified
at ``e = 0`` in ``rebaseguard_certify.contraction`` (claim N-01 of
``closure/04_ARB_CERTIFICATE.md``), made drift-explicit.  Under drift ``-e`` with
``e > 0`` the *minus* arm has increment ``-z - k ~ N(|e| - k, 1)``, so the whole
drift dependence is the substitution ``k -> k - |e|`` in the transition and
reward arguments.  One-sided crossing forces two-sided absorption, so

    q_n := inf_x P_x(tau <= n)  >=  H_n(0)  >=  lower_n[0] ,
    ||(I - K_e)^{-1}||_inf  <=  min_t  t / lower_t[0] .

Rigour rests on two elementary facts, both proved in ``PROOF.md``:
  (M1) H_t(x) is nondecreasing in the starting state x  -- so left cell
       endpoints give a genuine step-function lower envelope, not a sample;
  (M2) H_t(0; e) is nondecreasing in |e| for the aligned arm -- so evaluating at
       the smallest |e| of the cell is valid for the whole cell.
(M2) is a pathwise coupling statement about a ONE-SIDED random walk with
stochastically ordered increments.  It is NOT the unproved global claim
``sup_e E[tau|e] = E[tau|0]`` recorded as open in P5, and nothing here uses that.
"""
from __future__ import annotations

import sys
from pathlib import Path

from flint import arb, arb_mat

_PROOF_SRC = Path(__file__).resolve().parents[5] / "rebaseguard-proof" / "src"
if str(_PROOF_SRC) not in sys.path:
    sys.path.insert(0, str(_PROOF_SRC))

from rebaseguard_certify.arb_backend import (          # noqa: E402
    ball_record, gaussian_cdf, rational, workprec,
)

K_FROZEN = rational(1, 2)
H_FROZEN = arb(5)


def drift_monotone_resolvent(*, e_num: int, e_den: int, cells: int = 100,
                             n_max: int = 250, bits: int = 192) -> dict:
    """Rigorous upper bound on ||(I-K_e)^{-1}||_inf at the *worst* drift |e|.

    ``e_num/e_den`` must be the SMALLEST |e| of the cell (M2 makes that the
    worst case).  Returns the bound and the full audit trail.
    """
    if cells < 2 or n_max < 1:
        raise ValueError("invalid discretisation")
    with workprec(bits):
        e = rational(e_num, e_den)
        if not e >= 0:
            raise ValueError("pass |e|")
        shift = K_FROZEN - e                      # increment ~ N(|e| - k, 1)
        spacing = H_FROZEN / arb(cells)
        transition = arb_mat(cells, cells)
        reward = arb_mat(cells, 1)
        one = arb(1)
        for i in range(cells):
            state = H_FROZEN * arb(i) / arb(cells)          # LEFT endpoint (M1)
            transition[i, 0] = gaussian_cdf(spacing + shift - state)
            for j in range(1, cells):
                lo = H_FROZEN * arb(j) / arb(cells) + shift - state
                hi = H_FROZEN * arb(j + 1) / arb(cells) + shift - state
                transition[i, j] = gaussian_cdf(hi) - gaussian_cdf(lo)
            reward[i, 0] = gaussian_cdf(state - shift - H_FROZEN)
            total = reward[i, 0]
            for j in range(cells):
                total += transition[i, j]
            if not total.contains(one):
                raise ArithmeticError(f"row {i} failed probability mass balance")

        values = arb_mat(cells, 1)
        best = None
        trail = []
        for t in range(1, n_max + 1):
            values = reward + transition * values
            lower = values[0, 0].lower()
            if not lower > 0:
                continue
            bound = arb(t) / lower
            if best is None or bound.upper() < best[0].upper():
                best = (bound, t, arb(lower))
            if t in (1, 2, 5, 10, 25, 50, 100, 250):
                trail.append({"t": t, "H_t_lower": ball_record(arb(lower)),
                              "t_over_H": ball_record(arb(t) / lower)})
        if best is None:
            raise ArithmeticError("no positive hitting lower bound")
        bound, t_star, h_star = best
        return {
            "schema": "rebaseguard.p5x.opt-r1.drift-monotone-resolvent.v1",
            "method": "one-sided monotone Bellman lower envelope, drift-explicit",
            "e_rational": f"{e_num}/{e_den}",
            "e_float": e_num / e_den,
            "arm": "minus (aligned with the drift)",
            "increment_law": "N(|e| - k, 1)",
            "cells": cells, "n_max": n_max, "precision_bits": bits,
            "t_star": t_star,
            "H_t_star_lower": ball_record(h_star),
            "resolvent_bound": ball_record(bound),
            "resolvent_bound_upper_float": float(bound.upper()),
            "sampled_grid_used": False,
            "monotonicity_used": ["M1 state-monotone envelope (proved)",
                                  "M2 drift-monotone one-sided walk (proved)"],
            "empirical_monotonicity_used": False,
            "mass_balance": "every Arb row enclosure contains 1",
            "trail": trail,
        }


def block_forcing_resolvent(*, e_num: int, e_den: int, n_max: int = 60,
                            bits: int = 192) -> dict:
    """The R-A' baseline bound, recomputed here only for side-by-side reporting."""
    with workprec(bits):
        e = rational(e_num, e_den)
        best = None
        for n in range(1, n_max + 1):
            sqrt_n = arb(n).sqrt()
            base = (H_FROZEN + arb(n) * K_FROZEN) / sqrt_n
            q_n = gaussian_cdf(-base - e * sqrt_n) + gaussian_cdf(-base + e * sqrt_n)
            q_lo = q_n.lower()
            if not q_lo > 0:
                continue
            bound = arb(n) / q_lo
            if best is None or bound.upper() < best[0].upper():
                best = (bound, n, arb(q_lo))
        bound, n_star, q = best
        return {"method": "block forcing (R-A' baseline)",
                "e_rational": f"{e_num}/{e_den}", "n_star": n_star,
                "q_n_lower": ball_record(q), "resolvent_bound": ball_record(bound),
                "resolvent_bound_upper_float": float(bound.upper())}
