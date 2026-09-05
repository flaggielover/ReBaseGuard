"""CUSUM raw-variable production kernel: h_j, S_r, F_r, dF_r and R/R' assembly.

RAW VARIABLE ONLY. The unknown is F = R itself, with reward phi(u+e) - phi(l+e).
The old g-variable system (unknown g = R - e, reward carrying the -e(1-Phi+Phi)
term) certifies a DIFFERENT formulation and is never on this production path;
`ra_certifier.certify_at_exact_drift` is admissible only as a correspondence
reference, and a test enforces that.

Layer 1 (float) builds every object by collocation on the frozen Chebyshev grid.
Layer 2 rounds each to a degree-12 exact-dyadic Chebyshev candidate and certifies
its defect symbolically. EVERY argument handed to `_kernel_polynomials` is such a
candidate -- feeding a high-degree exact series there is what blew the Gate-2C
cost budget.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RA_DIR = ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics/certified_method_repair_ra"
G1 = ROOT / "level4/closure_proofs/p5y_micropilot_gate1"
for _p in (str(RA_DIR), str(G1), str(ROOT / "rebaseguard-proof" / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np                                                    # noqa: E402
from flint import arb                                                 # noqa: E402
import ra_certifier as RA                                             # noqa: E402
import raw_certifier as RAW                                           # noqa: E402
from rebaseguard_certify.arb_backend import rational, workprec        # noqa: E402
from rebaseguard_certify.polynomial import (                          # noqa: E402
    bi_add, bi_eval, bi_scale, chebyshev_payload_to_power)
from rebaseguard_certify.residual import (                             # noqa: E402
    _chebyshev_sup, _kernel_polynomials)
from rebaseguard_certify.spectral_candidate import (                   # noqa: E402
    SpectralCandidate, _barycentric_weights, _basis)

_R2 = ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r2"
if str(_R2) not in sys.path:
    sys.path.insert(0, str(_R2))
from fast_range import max_abs_on_reachable_fast                      # noqa: E402

C = RA.C_CUSUM
K_ = RA.K_FROZEN
H_ = RA.H_FROZEN
DEGREE = RA.DEGREE
QUAD = RA.QUADRATURE
SCALE_BITS = RA.SCALE_BITS
TAYLOR_N = RA.TAYLOR_N
BITS = RA.BITS

H_OBJECTS = ["h_1", "h_2", "h_3", "h_4"]
S_OBJECTS = [f"S_{r}" for r in range(5)]
F_OBJECTS = [f"F_{r}" for r in range(5)]
DF_OBJECTS = [f"dF_{r}" for r in range(5)]
ALL_OBJECTS = H_OBJECTS + S_OBJECTS + F_OBJECTS + DF_OBJECTS


# ============================================================ LAYER 1 (float)
def collocation(drift: float, degree: int = DEGREE, quad: int = QUAD):
    """Frozen collocation grid plus the three discrete operators.

    K   : (K_e f)(x)      survival integral, weight phi(z+e)
    Kz  : (K_{z,e} f)(x)  the same with an extra factor z
    dK  : d/de of K       weight factor -(z+e)
    dKz : d/de of Kz      weight factor -z(z+e)
    """
    n = degree + 1
    x = np.cos(np.pi * np.arange(n) / degree)
    nodes = 0.5 * H_ * (1.0 - x)
    bary = _barycentric_weights(degree)
    gn, gw = np.polynomial.legendre.leggauss(quad)
    dim = n * n
    K = np.zeros((dim, dim)); Kz = np.zeros((dim, dim))
    dK = np.zeros((dim, dim)); dKz = np.zeros((dim, dim))
    h1 = np.zeros(dim); S0 = np.zeros(dim); dS0 = np.zeros(dim)
    norm = math.sqrt(2.0 * math.pi)

    def Phi(t):
        return 0.5 * (1.0 + math.erf(t / math.sqrt(2.0)))

    for i, p in enumerate(nodes):
        for j, m in enumerate(nodes):
            row = i * n + j
            ell, upper = m - C, C - p
            mid, rad = 0.5 * (ell + upper), 0.5 * (upper - ell)
            for node, weight in zip(gn, gw, strict=True):
                z = mid + rad * node
                y = z + drift
                dens = rad * weight * math.exp(-0.5 * y * y) / norm
                wp = _basis(max(0.0, p + z - K_), nodes, bary)
                wm = _basis(max(0.0, m - z - K_), nodes, bary)
                interp = np.outer(wp, wm).ravel()
                K[row] += dens * interp
                Kz[row] += z * dens * interp
                dK[row] += (-y) * dens * interp
                dKz[row] += (-y) * z * dens * interp
            au, al = upper + drift, ell + drift
            pu = math.exp(-0.5 * au * au) / norm
            pl = math.exp(-0.5 * al * al) / norm
            h1[row] = 1.0 - Phi(au) + Phi(al)              # h_1 = P(tau = 1)
            S0[row] = pu - pl                              # S_0^raw, alarm-event reward
            dS0[row] = -au * pu + al * pl                  # d_e S_0
    return dict(nodes=nodes, n=n, K=K, Kz=Kz, dK=dK, dKz=dKz,
                h1=h1, S0=S0, dS0=dS0, drift=drift)


def build_objects(co: dict) -> dict:
    """Every raw-variable object at the collocation nodes, from the frozen DAG."""
    K, Kz, dK, dKz = co["K"], co["Kz"], co["dK"], co["dKz"]
    e = co["drift"]
    dim = K.shape[0]
    h = {1: co["h1"]}
    dh = {1: -co["S0"]}                                    # exact identity d_e h_1 = -S_0
    for j in range(2, 5):
        h[j] = K @ h[j - 1]
        dh[j] = dK @ h[j - 1] + K @ dh[j - 1]
    S = {0: co["S0"]}
    dS = {0: co["dS0"]}
    for r in range(1, 5):
        S[r] = Kz @ h[r] + e * (K @ h[r])
        dS[r] = (dKz @ h[r] + Kz @ dh[r]
                 + (K @ h[r]) + e * (dK @ h[r] + K @ dh[r]))
    op = np.eye(dim) - K
    F, dF = {}, {}
    for r in range(5):
        F[r] = np.linalg.solve(op, S[r])
        dF[r] = np.linalg.solve(op, dK @ F[r] + dS[r])
    return {"h": h, "dh": dh, "S": S, "dS": dS, "F": F, "dF": dF,
            "cond": float(np.linalg.cond(op))}


# ---------------------------------------------------------- frozen assembly
def assemble(obj: dict, co: dict, m: int) -> tuple[float, float]:
    """Exact frozen assembly of R_m and R'_m at x0 = (0,0).

    Window convention w = min(m, tau), inclusive stopping, Stage-D convention A:
    the random denominator is preserved by the (1/t - 1/m) coefficients, which
    come from the frozen general formula, not from a min-dwell rewrite.
    """
    from fractions import Fraction
    n = co["n"]
    i0 = 0                                                  # x0 = (0,0) is node (0,0)
    K = co["K"]; dK = co["dK"]
    F, dF, S, dS = obj["F"], obj["dF"], obj["S"], obj["dS"]
    R = sum(Fraction(1, m) * F[r][i0] for r in range(m))
    dR = sum(Fraction(1, m) * dF[r][i0] for r in range(m))
    R = float(R); dR = float(dR)
    for t in range(1, m):
        c = float(Fraction(1, t) - Fraction(1, m))
        for r in range(t):
            p = t - r - 1
            v, dv = S[r], dS[r]
            for _ in range(p):
                dv = dK @ v + K @ dv
                v = K @ v
            R += c * v[i0]
            dR += c * dv[i0]
    return R, dR


# ============================================================ LAYER 2 (certified)
def _dyadic_candidate(values: np.ndarray, n: int):
    """Degree-12 exact-dyadic Chebyshev candidate -- the frozen representation."""
    return SpectralCandidate(values.reshape(n, n), H_).to_chebyshev_dyadic(
        scale_bits=SCALE_BITS)


def certify_object(name: str, obj: dict, co: dict, *, order: int = TAYLOR_N,
                   bits: int = BITS) -> dict:
    """Certified defect of one raw-variable object, symbolically.

    Every BiPoly passed to `_kernel_polynomials` is a degree-12 exact-dyadic
    candidate (the frozen Gate-2C lesson).
    """
    n = co["n"]
    e_num, e_den = co["e_rational"]
    kind = name.split("_")[0]
    idx = int(name.split("_")[1])
    with workprec(bits):
        e = rational(e_num, e_den)
        b = RA.phi_taylor_coefficients(order, e)
        db = RA.derivative_coefficients(b)
        eps_z = RA.taylor_remainder(order, rational(11, 2))
        eps_reward = RA.taylor_remainder(order, rational(5, 2))
        reward_allow = arb(2) * eps_reward * (arb(1) + rational(5, 2))

        def cand(vals):
            pay = _dyadic_candidate(vals, n)
            return chebyshev_payload_to_power(pay), _chebyshev_sup(pay)

        if kind == "h":
            if idx == 1:                                    # closed form: exact
                (_, cdf_u), (_, cdf_l), _, _ = RA._recentred_sites(order, e)
                poly = bi_add({(0, 0): arb(1)},
                              bi_add(bi_scale(cdf_u, -arb(1)), cdf_l))
                return _pack(name, poly, arb(0), arb(0), "closed form", e_num, e_den)
            hh, sup = cand(obj["h"][idx])
            pv, sup_p = cand(obj["h"][idx - 1])
            lo, hi = _kernel_polynomials(pv, b, z_weight=0)
            res_lo = bi_add(hh, bi_scale(lo, -arb(1)))
            res_hi = bi_add(hh, bi_scale(hi, -arb(1)))
            extra = arb(11) * sup_p * eps_z
        elif kind == "S":
            if idx == 0:
                return _pack(name, RAW.reward_rho1_raw(order, e), arb(0), arb(0),
                             "closed form", e_num, e_den)
            ss, sup = cand(obj["S"][idx])
            pv, sup_p = cand(obj["h"][idx])
            zlo, zhi = _kernel_polynomials(pv, b, z_weight=1)
            klo, khi = _kernel_polynomials(pv, b, z_weight=0)
            rhs_lo = bi_add(zlo, bi_scale(klo, e))
            rhs_hi = bi_add(zhi, bi_scale(khi, e))
            res_lo = bi_add(ss, bi_scale(rhs_lo, -arb(1)))
            res_hi = bi_add(ss, bi_scale(rhs_hi, -arb(1)))
            extra = arb(11) * sup_p * eps_z * (arb(1) + rational(11, 2))
        elif kind == "F":
            ff, sup = cand(obj["F"][idx])
            lo, hi = _kernel_polynomials(ff, b, z_weight=0)
            # The source is the S_r CANDIDATE polynomial, not its residual.
            # (Feeding the residual here inflated the F_r defect by ~4000x and
            #  was caught by the frozen budget test.)
            if idx == 0:
                src = RAW.reward_rho1_raw(order, e)          # closed form, exact
            else:
                src, _ = cand(obj["S"][idx])
            res_lo = bi_add(bi_add(ff, bi_scale(lo, -arb(1))), bi_scale(src, -arb(1)))
            res_hi = bi_add(bi_add(ff, bi_scale(hi, -arb(1))), bi_scale(src, -arb(1)))
            extra = arb(11) * sup * eps_z + reward_allow
        elif kind == "dF":
            dd, sup_d = cand(obj["dF"][idx])
            ff, sup = cand(obj["F"][idx])
            lo, hi = _kernel_polynomials(dd, b, z_weight=0)
            dlo, dhi = _kernel_polynomials(ff, db, z_weight=0)
            dsrc = _dS_poly(idx, obj, co, order, e, b, db)
            res_lo = bi_add(bi_add(dd, bi_scale(lo, -arb(1))),
                            bi_add(bi_scale(dlo, -arb(1)), bi_scale(dsrc, -arb(1))))
            res_hi = bi_add(bi_add(dd, bi_scale(hi, -arb(1))),
                            bi_add(bi_scale(dhi, -arb(1)), bi_scale(dsrc, -arb(1))))
            extra = (arb(11) * sup_d * eps_z + arb(11) * sup * arb(order + 1) * eps_z
                     + reward_allow * (arb(1) + rational(11, 2)))
        else:
            raise ValueError(name)

        poly, coverage = max_abs_on_reachable_fast(res_lo, res_hi, subdivision_depth=0)
        return _pack(name, res_lo, poly, extra, "certified defect", e_num, e_den,
                     coverage=coverage)


def _dS_poly(idx, obj, co, order, e, b, db):
    """d_e S_r as a BiPoly. For r = 0 this is the exact raw derivative reward."""
    if idx == 0:
        return RAW.reward_drho1_raw(order, e)
    n = co["n"]
    hv, _ = chebyshev_payload_to_power(_dyadic_candidate(obj["h"][idx], n)), None
    dhv = chebyshev_payload_to_power(_dyadic_candidate(obj["dh"][idx], n))
    zlo, _ = _kernel_polynomials(hv, db, z_weight=1)
    zdlo, _ = _kernel_polynomials(dhv, b, z_weight=1)
    klo, _ = _kernel_polynomials(hv, b, z_weight=0)
    kdlo, _ = _kernel_polynomials(dhv, b, z_weight=0)
    dklo, _ = _kernel_polynomials(hv, db, z_weight=0)
    out = bi_add(zlo, zdlo)
    out = bi_add(out, klo)
    out = bi_add(out, bi_scale(bi_add(dklo, kdlo), e))
    return out


def _pack(name, poly, residual, extra, how, e_num, e_den, coverage=None):
    tot = residual + extra if not isinstance(residual, str) else residual
    return {"object": name, "e_rational": f"{e_num}/{e_den}", "how": how,
            "poly": poly, "equation_defect": float(residual),
            "truncation_and_tail": float(extra),
            "total_certified_error": float(tot),
            "coverage": coverage}
