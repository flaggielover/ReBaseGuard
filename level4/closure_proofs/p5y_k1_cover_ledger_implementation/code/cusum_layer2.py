"""Layer 2: certified CUSUM raw-variable residuals, whole-cell envelopes and the
complete order-0/1/2 dependency propagation.

Two distinct certified quantities are produced for every DAG object:

  delta_mid   the certified residual AT THE EXACT CELL MIDPOINT e0.
              Used for R_interval (order 0) and D_interval (order 1), which
              ERROR_ALGEBRA section 4 evaluates at e0.

  delta_cell  a certified UNIFORM bound over the whole declared cell.
              Used for the curvature obligation, which section 3 requires to be
              uniform on the cell, "not the midpoint versions".

WHY delta_cell IS NOT COMPUTED BY SUBSTITUTING AN INTERVAL e
------------------------------------------------------------
Substituting an Arb ball for e directly into the frozen recentred-Hermite /
Bernstein residual machinery is rigorous but numerically useless: the frozen
order-120 series is evaluated against z-powers up to (11/2)^121, and the
cancellation that makes the point residual ~1e-6 is destroyed by any interval
width. Measured on this host, cell 0 (rho = 2.5e-4) gives a point residual of
3.69e-06 and an interval-e residual of 1.46e+42; cell 325 gives 1.96e-05 and
2.29e+60. That construction cannot certify anything.

The construction used instead is the mean-value extension, which ERROR_ALGEBRA
section 1-3 explicitly authorises ("Use certified operator norm bounds j_k over
the whole cell; rigorous whole-line absolute Gaussian moments are admissible"):

    r(x;e) - r(x;e0) = int_{e0}^{e} d_s r(x;s) ds,   |e - e0| <= rho
    =>  sup_{x, e in cell} |r(x;e)| <= sup_x |r(x;e0)| + rho * Env

where Env is a certified e-UNIFORM bound on sup_x |d_e r(x;e)|. Because every
candidate is a state-only dyadic polynomial constant in e over the cell, d_e r
consists only of differentiated OPERATORS applied to fixed candidates, so Env is
a finite sum of (certified operator norm) * (certified candidate sup norm) --
whole-line Gaussian moments, never sampled, never a finite difference.

This is a whole-cell certificate: it bounds the residual simultaneously at every
e in the cell, not at sampled points.

TRUNCATION ALLOWANCES
---------------------
The frozen recentred series truncate phi at order N = TAYLOR_N. For derivative
order i the Lagrange remainder of the degree-(N-i) Taylor polynomial of phi^(i)
is bounded by (N+1)^i * eps_z with eps_z = taylor_remainder(N, 11/2), because

    Cramer_sup(phi^(N+1)) * R^(N-i+1)/(N-i+1)!  =  eps_z * (N+1)!/((N+1-i)! R^i)
                                               <= eps_z * (N+1)^i     for R >= 1.

i = 1 reproduces the frozen `(order+1)*eps_z` allowance exactly; i = 2 is the new
case and is bounded by the same rule. No precision or degree escalation.
"""
from __future__ import annotations

import sys
from fractions import Fraction as F
from math import comb
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
for _p in (str(_ROOT / "rebaseguard-proof/src"),
           str(_ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics/certified_method_repair_ra"),
           str(_ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r2"),
           str(_ROOT / "level4/closure_proofs/p5y_micropilot_gate1")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flint import arb                                                    # noqa: E402
import ra_certifier as RA                                                # noqa: E402
from rebaseguard_certify.polynomial import (                             # noqa: E402
    bi_add, bi_eval, bi_mul, bi_scale, chebyshev_payload_to_power)
from rebaseguard_certify.residual import _chebyshev_sup, _kernel_polynomials  # noqa: E402
from fast_range import max_abs_on_reachable_fast                         # noqa: E402

import cusum_layer1 as L1                                                # noqa: E402
import opnorms                                                           # noqa: E402
import spec                                                              # noqa: E402
from intervals import exact, tight_upper, workprec                       # noqa: E402

TAYLOR_N = RA.TAYLOR_N            # frozen 120
SUBDIVISION_DEPTH = 0             # frozen: the CUSUM raw kernel uses depth 0
Z_RANGE = arb(11)                 # length of the z integration window
Z_HALF = arb(11) / arb(2)
REWARD_RADIUS = F(5, 2)           # recentred site radius

ZERO: dict = {}


class Pair:
    """A (low branch, high branch) enclosure pair from _kernel_polynomials.

    Both branches are certified; the residual sup is the max over both, exactly
    as the frozen CUSUM kernel does. Linear operations act on both branches.
    """

    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        self.lo = lo
        self.hi = lo if hi is None else hi

    def __add__(self, other):
        o = other if isinstance(other, Pair) else Pair(other)
        return Pair(bi_add(self.lo, o.lo), bi_add(self.hi, o.hi))

    def __sub__(self, other):
        o = other if isinstance(other, Pair) else Pair(other)
        return Pair(bi_add(self.lo, bi_scale(o.lo, -arb(1))),
                    bi_add(self.hi, bi_scale(o.hi, -arb(1))))

    def scale(self, c):
        return Pair(bi_scale(self.lo, c), bi_scale(self.hi, c))


class CellCertifier:
    """All certified CUSUM evidence for one frozen cover cell."""

    def __init__(self, cell: dict, *, bits: int = spec.PRODUCTION_BITS,
                 order: int = TAYLOR_N, depth: int = SUBDIVISION_DEPTH):
        if cell["detector"] != "CUSUM":
            raise NotImplementedError(
                "no raw-variable DAG exists for SR; see IMPLEMENTATION_STATUS.md")
        self.cell = cell
        self.bits = bits
        self.order = order
        self.depth = depth
        self.e0 = F(cell["e0"][0])
        self.rho = F(cell["rho"][0])
        self.left = F(cell["left"][0])
        self.right = F(cell["right"][0])
        self.C = F(cell["C_upper"])
        self.e_max = max(abs(self.left), abs(self.right))
        self.bernstein_calls = 0
        self.kernel_calls = 0
        self.kernel_cpu = 0.0
        self._cache: dict = {}

    def _begin(self) -> None:
        """Mark the start of one object's construction, for per-class costing."""
        import time as _time
        self._mark = (_time.process_time(), self.kernel_calls,
                      self.bernstein_calls, self.kernel_cpu)

    # ---------------------------------------------------------------- setup
    def prepare(self):
        co = L1.collocation(float(self.e0))
        self.obj = L1.build_objects(co)
        self.n = co["n"]
        self.co = co
        e = exact(self.e0)
        self.e = e
        self.norms = opnorms.table(exact(self.e_max))
        self.b = [RA.phi_taylor_coefficients(self.order, e)]
        for _ in range(3):
            self.b.append(RA.derivative_coefficients(self.b[-1]))
        self.eps_z = RA.taylor_remainder(self.order, exact(F(11, 2)))
        self.eps_r = RA.taylor_remainder(self.order, exact(REWARD_RADIUS))
        (self.phi_u, self.cdf_u), (self.phi_l, self.cdf_l), self.arg_u, self.arg_l = \
            RA._recentred_sites(self.order, e)
        self._closed_forms()
        self._candidates()
        return self

    def eps_zi(self, i: int) -> arb:
        """Certified truncation allowance for the order-i phi coefficient list."""
        return (arb(self.order + 1) ** i) * self.eps_z

    def _closed_forms(self):
        """Exact closed forms for h_1^(k) and S_0^(k), and their sup bounds."""
        one = {(0, 0): arb(1)}
        s0 = bi_add(self.phi_u, bi_scale(self.phi_l, -arb(1)))
        s1 = bi_add(bi_scale(bi_mul(self.arg_u, self.phi_u), -arb(1)),
                    bi_mul(self.arg_l, self.phi_l))
        au2 = bi_add(bi_mul(self.arg_u, self.arg_u), {(0, 0): -arb(1)})
        al2 = bi_add(bi_mul(self.arg_l, self.arg_l), {(0, 0): -arb(1)})
        s2 = bi_add(bi_mul(au2, self.phi_u), bi_scale(bi_mul(al2, self.phi_l), -arb(1)))
        self.S0_closed = {0: s0, 1: s1, 2: s2}
        h1 = bi_add(one, bi_add(bi_scale(self.cdf_u, -arb(1)), self.cdf_l))
        self.h1_closed = {0: h1, 1: bi_scale(s0, -arb(1)), 2: bi_scale(s1, -arb(1))}
        # Reward-series truncation allowances (radius 5/2 recentred sites).
        A = Z_HALF + exact(self.e_max)                     # |u+e|, |l+e| bound
        self.reward_allow = {
            0: arb(2) * self.eps_r,
            1: arb(2) * A * self.eps_r,
            2: arb(2) * (A * A + arb(1)) * self.eps_r,
        }
        self.h1_allow = {0: arb(2) * exact(REWARD_RADIUS) * self.eps_r,
                         1: self.reward_allow[0], 2: self.reward_allow[1]}
        # Certified sup bounds for the closed forms (analytic, e-uniform).
        self.sup_S0 = {k: opnorms.sup_source_derivative(k) for k in range(3)}
        self.sup_h1 = {0: arb(1), 1: self.sup_S0[0], 2: self.sup_S0[1]}

    def _cand(self, values):
        pay = L1.dyadic_candidate(values, self.n)
        return chebyshev_payload_to_power(pay), _chebyshev_sup(pay)

    def _candidates(self):
        o = self.obj
        self.P, self.sup = {}, {}
        for j in range(2, 5):
            for k in range(3):
                self.P["h", j, k], self.sup["h", j, k] = self._cand(o["h"][j, k])
        # h_1^(k) needs a degree-12 candidate because it is an ARGUMENT of K_i
        # (in the h_2 residual) and of J_i (in the S_1 residual). Handing the
        # degree-120 closed-form series to _kernel_polynomials is the frozen
        # Gate-2C failure mode. The closed form is retained separately so the
        # candidate can be certified against it.
        for k in range(3):
            self.P["hclosed", 1, k] = self.h1_closed[k]
            self.sup["hclosed", 1, k] = self.sup_h1[k]
            self.P["h", 1, k], self.sup["h", 1, k] = self._cand(o["h"][1, k])
        for r in range(1, 5):
            for k in range(3):
                self.P["S", r, k], self.sup["S", r, k] = self._cand(o["S"][r, k])
        # S_0 has BOTH a closed form (exact source for the F/D/H equations) and a
        # degree-12 candidate (so the finite-power chain never feeds a degree-120
        # series to _kernel_polynomials -- the frozen Gate-2C lesson).
        for k in range(3):
            self.P["Sclosed", 0, k] = self.S0_closed[k]
            self.sup["Sclosed", 0, k] = self.sup_S0[k]
            self.P["S", 0, k], self.sup["S", 0, k] = self._cand(o["S"][0, k])
        for r in range(5):
            self.P["F", r, 0], self.sup["F", r, 0] = self._cand(o["F"][r])
            self.P["D", r, 0], self.sup["D", r, 0] = self._cand(o["D"][r])
            self.P["H", r, 0], self.sup["H", r, 0] = self._cand(o["H"][r])
        for (r, j) in L1.W_INDICES:
            for k in range(3):
                self.P["W", (r, j), k], self.sup["W", (r, j), k] = \
                    self._cand(o["W"][r, j, k])
        for r in range(4):
            for k in range(3):
                self.P["W", (r, 0), k] = self.P["S", r, k]
                self.sup["W", (r, 0), k] = self.sup["S", r, k]

    # ------------------------------------------------------------- operators
    def K(self, poly, i: int) -> Pair:
        """Certified enclosure of K_i f = int f(q) phi^(i)(z+e) dz."""
        key = (id(poly), i, 0)
        if key not in self._cache:
            import time as _time
            t0 = _time.process_time()
            self.kernel_calls += 1
            lo, hi = _kernel_polynomials(poly, self.b[i], z_weight=0)
            self.kernel_cpu += _time.process_time() - t0
            self._cache[key] = Pair(lo, hi)
        return self._cache[key]

    def Kz(self, poly, i: int) -> Pair:
        """Certified enclosure of Kz_i f = int f(q) z phi^(i)(z+e) dz."""
        key = (id(poly), i, 1)
        if key not in self._cache:
            import time as _time
            t0 = _time.process_time()
            self.kernel_calls += 1
            lo, hi = _kernel_polynomials(poly, self.b[i], z_weight=1)
            self.kernel_cpu += _time.process_time() - t0
            self._cache[key] = Pair(lo, hi)
        return self._cache[key]

    def J(self, poly, i: int) -> Pair:
        """J_i = Kz_i + e K_i + i K_(i-1), the exact Leibniz expansion of J_e."""
        out = self.Kz(poly, i) + self.K(poly, i).scale(self.e)
        if i >= 1:
            out = out + self.K(poly, i - 1).scale(arb(i))
        return out

    def _J_trunc(self, i: int, sup: arb) -> arb:
        """Truncation allowance for one J_i application to a candidate."""
        out = Z_RANGE * Z_HALF * sup * self.eps_zi(i) \
            + exact(self.e_max) * Z_RANGE * sup * self.eps_zi(i)
        if i >= 1:
            out = out + arb(i) * Z_RANGE * sup * self.eps_zi(i - 1)
        return out

    # ------------------------------------------------------------- residuals
    def _range(self, pair: Pair) -> arb:
        self.bernstein_calls += 1
        value, _ = max_abs_on_reachable_fast(pair.lo, pair.hi,
                                             subdivision_depth=self.depth)
        return tight_upper(value)

    def certify(self, name: str, residual: Pair, extra: arb, envelope: arb) -> dict:
        """One certified object: midpoint residual, whole-cell envelope, both deltas."""
        import time as _time
        t0, k0, b0, _ = getattr(self, "_mark",
                                (_time.process_time(), self.kernel_calls,
                                 self.bernstein_calls, self.kernel_cpu))
        poly = self._range(residual)
        extra = tight_upper(extra)
        envelope = tight_upper(envelope)
        delta_mid = tight_upper(poly + extra)
        delta_cell = tight_upper(delta_mid + exact(self.rho) * envelope)
        if not delta_mid >= 0 or not delta_cell >= delta_mid:
            raise ArithmeticError(f"invalid certified residual for {name}")
        return {"object": name, "polynomial_residual": poly, "truncation_allowance": extra,
                "delta_mid": delta_mid, "envelope": envelope, "delta_cell": delta_cell,
                "cpu_seconds": _time.process_time() - t0,
                "bernstein_calls": self.bernstein_calls - b0,
                "kernel_calls": self.kernel_calls - k0}

    def all_residuals(self) -> dict:
        """Every certified local residual required by the frozen DAG."""
        out = {}
        k_ = self.norms["k"]
        j_ = self.norms["j"]

        # --- h_1^(k) and S_0^(k): closed forms evaluated AT e0.
        # They carry no equation defect, but they are fixed functions of x while
        # the TRUE objects move with e, so the whole-cell bound needs the same
        # mean-value envelope as every other object:
        #     h_1^(k+1) = -S_0^(k)  and  d_e S_0^(k) = S_0^(k+1),
        # bounded e-uniformly by 2 sup|phi^(k)| and 2 sup|phi^(k+1)|.
        for k in range(3):
            # h_1^(k): degree-12 candidate certified against the exact closed
            # form, with the same mean-value envelope sup|h_1^(k+1)| = 2 sup|phi^(k)|.
            self._begin()
            res = Pair(self.P["h", 1, k]) - Pair(self.P["hclosed", 1, k])
            out[f"h_1:{k}"] = self.certify(
                f"h_1:{k}", res, self.h1_allow[k],
                opnorms.sup_source_derivative(k))
            allow0 = tight_upper(self.reward_allow[k])
            env0 = opnorms.sup_source_derivative(k + 1)
            out[f"Sclosed_{k}"] = {
                "object": f"Sclosed_{k}", "polynomial_residual": arb(0),
                "truncation_allowance": allow0, "delta_mid": allow0,
                "envelope": env0,
                "delta_cell": tight_upper(allow0 + exact(self.rho) * env0),
                "closed_form": True, "cpu_seconds": 0.0,
                "bernstein_calls": 0, "kernel_calls": 0}

        # --- h_j^(k) = sum_i C(k,i) K_i h_(j-1)^(k-i)
        for j in range(2, 5):
            for k in range(3):
                self._begin()
                res = Pair(self.P["h", j, k])
                extra = arb(0)
                env = arb(0)
                for i in range(k + 1):
                    c = arb(comb(k, i))
                    src = self.P["h", j - 1, k - i]
                    s = self.sup["h", j - 1, k - i]
                    res = res - self.K(src, i).scale(c)
                    extra = extra + c * Z_RANGE * s * self.eps_zi(i)
                    env = env + c * k_[i + 1] * s
                out[f"h_{j}:{k}"] = self.certify(f"h_{j}:{k}", res, extra, env)

        # --- S_0^(k) degree-12 candidate against the exact closed form
        for k in range(3):
            self._begin()
            res = Pair(self.P["S", 0, k]) - Pair(self.P["Sclosed", 0, k])
            out[f"S_0:{k}"] = self.certify(
                f"S_0:{k}", res, self.reward_allow[k],
                opnorms.sup_source_derivative(k + 1))

        # --- S_r^(k) = sum_i C(k,i) J_i h_r^(k-i)
        for r in range(1, 5):
            for k in range(3):
                self._begin()
                res = Pair(self.P["S", r, k])
                extra = arb(0)
                env = arb(0)
                for i in range(k + 1):
                    c = arb(comb(k, i))
                    src = self.P["h", r, k - i]
                    s = self.sup["h", r, k - i]
                    res = res - self.J(src, i).scale(c)
                    extra = extra + c * self._J_trunc(i, s)
                    env = env + c * j_[i + 1] * s
                out[f"S_{r}:{k}"] = self.certify(f"S_{r}:{k}", res, extra, env)

        # --- F_r = K F_r + S_r
        for r in range(5):
            self._begin()
            src = self.P["Sclosed", 0, 0] if r == 0 else self.P["S", r, 0]
            res = Pair(self.P["F", r, 0]) - self.K(self.P["F", r, 0], 0) - Pair(src)
            s = self.sup["F", r, 0]
            extra = Z_RANGE * s * self.eps_zi(0)
            env = k_[1] * s
            if r == 0:
                extra = extra + self.reward_allow[0]
                # NO source term in env: the residual uses the FIXED closed-form
                # Sclosed_0, whose e-variation is carried once by epsS (its own
                # envelope). Adding it here too would double charge it.
            out[f"F_{r}"] = self.certify(f"F_{r}", res, extra, env)

        # --- D_r = K D_r + K_1 F_r + S_r'
        for r in range(5):
            self._begin()
            src = self.P["Sclosed", 0, 1] if r == 0 else self.P["S", r, 1]
            res = (Pair(self.P["D", r, 0]) - self.K(self.P["D", r, 0], 0)
                   - self.K(self.P["F", r, 0], 1) - Pair(src))
            sd, sf = self.sup["D", r, 0], self.sup["F", r, 0]
            extra = Z_RANGE * sd * self.eps_zi(0) + Z_RANGE * sf * self.eps_zi(1)
            env = k_[1] * sd + k_[2] * sf
            if r == 0:
                extra = extra + self.reward_allow[1]
                # see F_r: source e-variation is owned by epsS(Sclosed_1) alone.
            out[f"dF_{r}"] = self.certify(f"dF_{r}", res, extra, env)

        # --- H_r = K H_r + K_2 F_r + 2 K_1 D_r + S_r''   (curvature equation)
        for r in range(5):
            self._begin()
            src = self.P["Sclosed", 0, 2] if r == 0 else self.P["S", r, 2]
            res = (Pair(self.P["H", r, 0]) - self.K(self.P["H", r, 0], 0)
                   - self.K(self.P["F", r, 0], 2)
                   - self.K(self.P["D", r, 0], 1).scale(arb(2)) - Pair(src))
            sh, sd, sf = self.sup["H", r, 0], self.sup["D", r, 0], self.sup["F", r, 0]
            extra = (Z_RANGE * sh * self.eps_zi(0) + Z_RANGE * sf * self.eps_zi(2)
                     + arb(2) * Z_RANGE * sd * self.eps_zi(1))
            env = k_[1] * sh + k_[3] * sf + arb(2) * k_[2] * sd
            if r == 0:
                extra = extra + self.reward_allow[2]
                # see F_r: source e-variation is owned by epsS(Sclosed_2) alone.
            out[f"H_{r}"] = self.certify(f"H_{r}", res, extra, env)

        # --- W_(r,j+1)^(k) = sum_i C(k,i) K_i W_(r,j)^(k-i)
        for (r, j) in L1.W_INDICES:
            for k in range(3):
                self._begin()
                res = Pair(self.P["W", (r, j), k])
                extra = arb(0)
                env = arb(0)
                for i in range(k + 1):
                    c = arb(comb(k, i))
                    src = self.P["W", (r, j - 1), k - i]
                    s = self.sup["W", (r, j - 1), k - i]
                    res = res - self.K(src, i).scale(c)
                    extra = extra + c * Z_RANGE * s * self.eps_zi(i)
                    env = env + c * k_[i + 1] * s
                out[f"W_{r}_{j}:{k}"] = self.certify(f"W_{r}_{j}:{k}", res, extra, env)
        self.residuals = out
        return out

    # ------------------------------------------------------------ point values
    def origin(self, key) -> arb:
        """Candidate value at x0 = (0,0); the certified centre of an enclosure."""
        return bi_eval(self.P[key], arb(0), arb(0))
