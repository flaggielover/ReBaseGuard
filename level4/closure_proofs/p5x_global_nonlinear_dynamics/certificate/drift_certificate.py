"""P5X certified enclosure of R_{CUSUM,m=1}(e) on one e-cell.

Proof-critical.  Reuses, unmodified and by import, the audited Level-1..3
continuum-residual machinery of ``rebaseguard_certify`` (polynomial algebra,
kernel panel splitting, Bernstein continuum range bound over the reachable set,
Arb backend).  Nothing in ``rebaseguard-proof`` is written to.

What is new here, and only this:

* the killed kernel at drift ``e``, written in the innovation variable
  ``zeta = z + e`` so that the Gaussian weight is the *plain* ``phi(zeta)`` of
  the audited Gamma certificate and the whole drift dependence sits in three
  affine constants.  ``e`` is carried as an Arb ball covering the whole cell;
* the absorbing reward ``rho_{1,e}(x) = E[z ; alarm from x]`` of P5X-T1;
* a single second-kind equation ``g = K_e g + rho_{1,e}`` (the Gamma
  certificate solved a coupled pair, and paid two factors of the resolvent);
* a drift-explicit block-forcing resolvent bound, proved from scratch, so that
  no constant is transported from ``e = 0`` and PROOF_OBLIGATIONS L4's unproved
  monotonicity clause (DEFECT_REGISTER D3) is not needed.

R_{CUSUM,1}(e) = e + g(x_0; e)  by PROOF.md L1.7 with m = 1.
"""
from __future__ import annotations

import math
import sys
from math import factorial
from pathlib import Path

import numpy as np
from flint import arb
from scipy.special import ndtr

_PROOF_SRC = Path(__file__).resolve().parents[4] / "rebaseguard-proof" / "src"
if str(_PROOF_SRC) not in sys.path:
    sys.path.insert(0, str(_PROOF_SRC))

from rebaseguard_certify.arb_backend import (          # noqa: E402
    ball_record, gaussian_cdf, rational, workprec,
)
from rebaseguard_certify.polynomial import (           # noqa: E402
    BiPoly, bi_add, bi_eval, bi_mul, bi_scale, chebyshev_payload_to_power,
)
from rebaseguard_certify.residual import (             # noqa: E402
    _cdf_at_affine, _integrate_z, _max_abs_on_reachable, _multiply_by_phi,
    _phi_coefficients, _series_at_affine, _chebyshev_sup,
)
from rebaseguard_certify.polynomial import (           # noqa: E402
    TriPoly, tri_add, tri_mul, tri_pow,
)
from rebaseguard_certify.spectral_candidate import (   # noqa: E402
    SpectralCandidate, _barycentric_weights, _basis,
)

K_FROZEN = 0.5
H_FROZEN = 5.0
C_CUSUM = H_FROZEN + K_FROZEN          # 11/2


# --------------------------------------------------------------------------
# 1. candidate (NOT proof evidence)
# --------------------------------------------------------------------------
def solve_candidate(*, drift: float, degree: int = 12, quadrature_order: int = 400,
                    k: float = K_FROZEN, h: float = H_FROZEN) -> SpectralCandidate:
    """Chebyshev collocation candidate for g = K_e g + rho_1e at e = ``drift``."""
    count = degree + 1
    x = np.cos(np.pi * np.arange(count) / degree)
    nodes = 0.5 * h * (1.0 - x)
    bary = _barycentric_weights(degree)
    gnodes, gweights = np.polynomial.legendre.leggauss(quadrature_order)
    dim = count * count
    kernel = np.zeros((dim, dim))
    reward = np.zeros(dim)
    norm = math.sqrt(2.0 * math.pi)
    for i, p in enumerate(nodes):
        for j, m in enumerate(nodes):
            row = i * count + j
            ell = m - h - k
            upper = h + k - p
            mid = 0.5 * (ell + upper)
            rad = 0.5 * (upper - ell)
            for node, weight in zip(gnodes, gweights, strict=True):
                z = mid + rad * node
                dens = rad * weight * math.exp(-0.5 * (z + drift) ** 2) / norm
                wp = _basis(max(0.0, p + z - k), nodes, bary)
                wm = _basis(max(0.0, m - z - k), nodes, bary)
                kernel[row] += dens * np.outer(wp, wm).ravel()
            au = upper + drift
            al = ell + drift
            reward[row] = (
                math.exp(-0.5 * au * au) / norm - math.exp(-0.5 * al * al) / norm
                - drift * (1.0 - ndtr(au) + ndtr(al))
            )
    values = np.linalg.solve(np.eye(dim) - kernel, reward).reshape(count, count)
    return SpectralCandidate(values, h)


# --------------------------------------------------------------------------
# 2. the killed kernel at drift e, in the innovation variable zeta = z + e
# --------------------------------------------------------------------------
# Writing zeta = z + e turns the Gaussian weight back into the *plain* phi(zeta)
# whose Maclaurin series is even and is exactly the one the audited Gamma
# certificate uses, and pushes the whole drift dependence into three affine
# constants.  This is a change of integration variable, not a change of the
# mathematics: the alternative (expanding phi(z+e) in powers of z) is
# algebraically equivalent but numerically catastrophic, because it fills in the
# odd powers and destroys the cancellation structure that keeps the Bernstein
# range bound tight -- see STOP_GATE.md section 5.
#
#   q_plus  = p + zeta - (1/2 + e)      q_minus = m - zeta - (1/2 - e)
#   panels break at  alpha = (1/2 + e) - p  and  beta = (m - 1/2) + e
#   continuation is  zeta in ( m - 11/2 + e , 11/2 - p + e )


def _substitute_candidate(candidate: BiPoly, mode: str, e: arb) -> TriPoly:
    """Candidate composed with q(x, zeta - e); variables are (p, m, zeta)."""
    zero: TriPoly = {(0, 0, 0): arb(0)}
    active_plus: TriPoly = {
        (1, 0, 0): arb(1), (0, 0, 1): arb(1), (0, 0, 0): -(rational(1, 2) + e),
    }
    active_minus: TriPoly = {
        (0, 1, 0): arb(1), (0, 0, 1): -arb(1), (0, 0, 0): -(rational(1, 2) - e),
    }
    q_plus = active_plus if mode in {"up", "both"} else zero
    q_minus = active_minus if mode in {"down", "both"} else zero
    max_i = max(i for i, _ in candidate)
    max_j = max(j for _, j in candidate)
    plus_powers = [tri_pow(q_plus, i) for i in range(max_i + 1)]
    minus_powers = [tri_pow(q_minus, j) for j in range(max_j + 1)]
    result: TriPoly = {}
    for (i, j), coefficient in candidate.items():
        if mode in {"down", "origin"} and i > 0:
            continue
        if mode in {"up", "origin"} and j > 0:
            continue
        term = tri_mul(plus_powers[i], minus_powers[j])
        result = tri_add(result, {key: value * coefficient for key, value in term.items()})
    return result


def _kernel_piece(candidate: BiPoly, mode: str, lower: BiPoly, upper: BiPoly,
                  phi_coefficients: list[arb], e: arb, *, z_weight: int) -> BiPoly:
    substituted = _substitute_candidate(candidate, mode, e)
    integrand = _multiply_by_phi(substituted, phi_coefficients, z_weight)
    return _integrate_z(integrand, lower, upper)


def kernel_polynomials(candidate: BiPoly, phi_coefficients: list[arb], e: arb,
                       *, z_weight: int = 0) -> tuple[BiPoly, BiPoly]:
    """(K_e candidate) as a polynomial, on the p+m<=1 and p+m>=1 regimes."""
    p: BiPoly = {(1, 0): arb(1)}
    m: BiPoly = {(0, 1): arb(1)}
    ell = bi_add(m, {(0, 0): -rational(11, 2) + e})
    beta = bi_add(m, {(0, 0): -rational(1, 2) + e})
    alpha = bi_add(bi_scale(p, -arb(1)), {(0, 0): rational(1, 2) + e})
    upper = bi_add(bi_scale(p, -arb(1)), {(0, 0): rational(11, 2) + e})

    low = _kernel_piece(candidate, "down", ell, beta, phi_coefficients, e, z_weight=z_weight)
    low = bi_add(low, _kernel_piece(candidate, "origin", beta, alpha, phi_coefficients, e, z_weight=z_weight))
    low = bi_add(low, _kernel_piece(candidate, "up", alpha, upper, phi_coefficients, e, z_weight=z_weight))

    high = _kernel_piece(candidate, "down", ell, alpha, phi_coefficients, e, z_weight=z_weight)
    high = bi_add(high, _kernel_piece(candidate, "both", alpha, beta, phi_coefficients, e, z_weight=z_weight))
    high = bi_add(high, _kernel_piece(candidate, "up", beta, upper, phi_coefficients, e, z_weight=z_weight))
    return low, high


def phi_truncation_error(order: int, max_abs_argument: arb) -> arb:
    """Uniform Lagrange remainder of the phi Maclaurin truncation on |zeta| <= arg."""
    u_max = max_abs_argument * max_abs_argument / arb(2)
    return (u_max ** (order + 1)) / (
        arb(factorial(order + 1)) * (arb(2) * arb.pi()).sqrt()
    )


# --------------------------------------------------------------------------
# 3. absorbing reward rho_{1,e} as a bivariate polynomial in (p, m)
# --------------------------------------------------------------------------
def reward_rho1(plain_phi_coefficients: list[arb], e_ball: arb) -> BiPoly:
    p: BiPoly = {(1, 0): arb(1)}
    m: BiPoly = {(0, 1): arb(1)}
    upper_plus_e = bi_add(bi_scale(p, -arb(1)), {(0, 0): rational(11, 2) + e_ball})
    ell_plus_e = bi_add(m, {(0, 0): -rational(11, 2) + e_ball})
    phi_u = _series_at_affine(plain_phi_coefficients, upper_plus_e)
    phi_l = _series_at_affine(plain_phi_coefficients, ell_plus_e)
    cdf_u = _cdf_at_affine(plain_phi_coefficients, upper_plus_e)
    cdf_l = _cdf_at_affine(plain_phi_coefficients, ell_plus_e)
    bracket = bi_add({(0, 0): arb(1)}, bi_add(bi_scale(cdf_u, -arb(1)), cdf_l))
    return bi_add(bi_add(phi_u, bi_scale(phi_l, -arb(1))), bi_scale(bracket, -e_ball))


# --------------------------------------------------------------------------
# 4. drift-explicit block-forcing resolvent bound
# --------------------------------------------------------------------------
def resolvent_bound(e_ball: arb, *, n_max: int = 60, k: float = K_FROZEN,
                    h: float = H_FROZEN) -> tuple[arb, int, arb]:
    """||(I-K_e)^{-1}||_inf <= n / q_n(e), minimised over n in {1..n_max}.

    From any live state, S+_n >= S+_0 + G_n - n k >= G_n - n k, so
    {G_n >= h + n k} forces a plus-arm alarm within n steps; symmetrically for
    the minus arm.  The two events are disjoint.  Under drift -e,
    G_n ~ N(-n e, n), giving
        q_n(e) = Phi(-(h+nk)/sqrt(n) - e sqrt(n)) + Phi(-(h+nk)/sqrt(n) + e sqrt(n)).
    Evaluated on the e-ball and read at its lower endpoint, so the bound holds
    for every e in the cell.  No monotonicity in e is used.
    """
    best: tuple[arb, int, arb] | None = None
    for n in range(1, n_max + 1):
        sqrt_n = arb(n).sqrt()
        base = (arb(h) + arb(n) * arb(k)) / sqrt_n
        q_n = gaussian_cdf(-base - e_ball * sqrt_n) + gaussian_cdf(-base + e_ball * sqrt_n)
        q_lo = q_n.lower()
        if not q_lo > 0:
            continue
        bound = arb(n) / q_lo
        if best is None or bound.upper() < best[0].upper():
            best = (bound, n, q_lo)
    if best is None:
        raise ArithmeticError("no valid resolvent block length")
    return best


# --------------------------------------------------------------------------
# 5. the certified single-cell enclosure
# --------------------------------------------------------------------------
def certify_cell(*, e_lo: float, e_hi: float, degree: int = 12,
                 quadrature_order: int = 400, scale_bits: int = 50,
                 phi_order: int = 50, subdivision_depth: int = 3,
                 bits: int = 256, resolvent_n_max: int = 60,
                 diagnostic_radius: float | None = None) -> dict:
    """Certified enclosure of R_{CUSUM,1} over [e_lo, e_hi].

    ``diagnostic_radius`` is **diagnostics only** and must be ``None`` for the
    stop-gate: it replaces the e-ball radius (e.g. by 0, collapsing the cell to
    its midpoint) so that the failure mode can be attributed.  A run with it set
    is not a certified enclosure of a cell and is labelled as such.
    """
    if not 0.0 <= e_lo < e_hi:
        raise ValueError("cell must satisfy 0 <= e_lo < e_hi")
    e_mid = 0.5 * (e_lo + e_hi)
    candidate = solve_candidate(drift=e_mid, degree=degree,
                                quadrature_order=quadrature_order)
    payload = candidate.to_chebyshev_dyadic(scale_bits=scale_bits)

    with workprec(bits):
        e_mid_q = rational(round(e_mid * 10**6), 10**6)
        if diagnostic_radius is None:
            e_rad_q = rational(round((e_hi - e_lo) * 10**6), 2 * 10**6)
        else:
            e_rad_q = rational(round(diagnostic_radius * 10**12), 10**12)
        e_ball = arb(e_mid_q, e_rad_q)
        if diagnostic_radius is None and not (
                e_ball.lower() <= arb(e_lo) and e_ball.upper() >= arb(e_hi)):
            raise ArithmeticError("e ball does not cover the declared cell")
        g_hat = chebyshev_payload_to_power(payload)
        plain = _phi_coefficients(phi_order)
        k_low, k_high = kernel_polynomials(g_hat, plain, e_ball, z_weight=0)
        reward = reward_rho1(plain, e_ball)
        res_low = bi_add(bi_add(g_hat, bi_scale(k_low, -arb(1))),
                         bi_scale(reward, -arb(1)))
        res_high = bi_add(bi_add(g_hat, bi_scale(k_high, -arb(1))),
                          bi_scale(reward, -arb(1)))
        poly_residual, coverage = _max_abs_on_reachable(
            res_low, res_high, subdivision_depth=subdivision_depth)

        e_hi_arb = arb(rational(round(e_hi * 10**6), 10**6))
        max_argument = rational(11, 2) + e_hi_arb
        phi_error = phi_truncation_error(phi_order, max_argument)
        sup_g = _chebyshev_sup(payload)
        allowance = (arb(11) * sup_g + arb(2)
                     + arb(2) * e_hi_arb * (rational(11, 2) + e_hi_arb))
        delta = poly_residual + allowance * phi_error
        if not delta > 0:
            raise ArithmeticError("invalid residual bound")

        resolvent, block_n, q_n = resolvent_bound(e_ball, n_max=resolvent_n_max)
        propagated = resolvent * delta
        g_at_origin = bi_eval(g_hat, arb(0), arb(0))
        g_enclosure = g_at_origin + arb(0, propagated.upper())
        r_enclosure = e_ball + g_enclosure
        half_width = r_enclosure.rad()

        return {
            "schema": "rebaseguard.p5x.single-cell-enclosure.v1",
            "target": "R_{CUSUM,m=1}(e) on the closed cell",
            "detector": "cusum",
            "m": 1,
            "e_cell": [e_lo, e_hi],
            "diagnostic_radius": diagnostic_radius,
            "is_certified_cell_enclosure": diagnostic_radius is None,
            "model": {"k_num": 1, "k_den": 2, "h_num": 5, "h_den": 1},
            "precision_bits": bits,
            "candidate": {
                "role": "EXACT DYADIC CANDIDATE ONLY; NOT PROOF EVIDENCE",
                "degree": degree, "quadrature_order": quadrature_order,
                "scale_bits": scale_bits,
                "g_hat_origin": ball_record(g_at_origin),
                "sup_abs_chebyshev": ball_record(sup_g),
            },
            "phi_taylor_order": phi_order,
            "phi_uniform_error": ball_record(phi_error),
            "phi_truncation_allowance": ball_record(allowance),
            "polynomial_residual": ball_record(poly_residual),
            "delta": ball_record(delta),
            "resolvent": {
                "method": "drift-explicit block forcing, proved in STOP_GATE_SPEC.md",
                "block_length_n": block_n,
                "q_n_lower": ball_record(q_n),
                "bound": ball_record(resolvent),
                "imported_constant": False,
                "monotonicity_in_e_used": False,
            },
            "propagated_error": ball_record(propagated),
            "g_enclosure": ball_record(g_enclosure),
            "R_enclosure": ball_record(r_enclosure),
            "R_enclosure_lower": float(r_enclosure.lower()),
            "R_enclosure_upper": float(r_enclosure.upper()),
            "interval_width": float(r_enclosure.upper() - r_enclosure.lower()),
            "achieved_half_width": float(half_width),
            "coverage": {**coverage,
                         "parameterization": "p=r*t, m=r*(1-t)",
                         "pieces": ["0<=r<=1", "1<=r<=4", "axis tails 4<=r<=5"],
                         "reachable_continuum_complete": True,
                         "sampled_grid_used": False,
                         "gaussian_tail_truncation": "none"},
        }
