"""Analysis of the Gate 4.2 conditional map: derivatives, roots, candidates.

Derivative estimation
---------------------
A plain central difference of an estimated map carries an O(delta^2)
*truncation* bias, ``D(delta) = F'(0) + a3 delta^2 + O(delta^4)``, and for this
map ``a3`` is large (order 300), so a naive central difference at delta = 0.05
is biased by about 0.7 -- many Monte Carlo standard errors.  Reporting that as a
disagreement with the Level 1-3 identity would be a numerical artefact, not a
scientific finding.  The primary estimator is therefore a weighted least-squares
fit of an **odd** polynomial ``a1 e + a3 e^3 + a5 e^5`` to the estimated map on a
symmetric window around zero, with ``a1 = F'(0)``.  Oddness is not assumed for
convenience: it is a proved symmetry of the model, and ``symmetry_diagnostics``
tests it against the data rather than imposing it silently.

Vocabulary discipline
---------------------
Nothing in this module produces a proof.  Roots of ``H_rho(e) = F_rho(e) + e``
are *candidate* period-2 points of the deterministic map ``F_rho``.  The actual
recursion is ``E_{j+1} = F_rho(E_j) + noise``; a deterministic 2-cycle of
``F_rho`` is neither necessary nor sufficient for bimodality of the invariant
law of that noisy recursion, and this module never says otherwise.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

Z95 = 1.959963984540054


# ------------------------------------------------------------- derivatives --

def odd_polynomial_fit(
    e: np.ndarray,
    f: np.ndarray,
    se: np.ndarray,
    *,
    max_abs_e: float,
    n_terms: int = 3,
) -> dict[str, Any]:
    """WLS fit of ``sum_{i<n_terms} a_{2i+1} e^{2i+1}`` on ``|e| <= max_abs_e``."""
    mask = np.abs(e) <= max_abs_e + 1e-12
    x, y, s = e[mask], f[mask], se[mask]
    if x.size < n_terms + 1:
        raise ValueError(
            f"need > {n_terms} grid points with |e| <= {max_abs_e}, got {x.size}"
        )
    powers = [2 * i + 1 for i in range(n_terms)]
    design = np.vstack([x ** p for p in powers]).T
    if np.linalg.cond(design) > 1e10:
        raise np.linalg.LinAlgError(
            f"design matrix for n_terms={n_terms} on |e| <= {max_abs_e} is "
            f"ill-conditioned (cond > 1e10)"
        )
    w = np.where(s > 0, 1.0 / np.maximum(s, 1e-300) ** 2, 0.0)
    sw = np.sqrt(w)
    aw = design * sw[:, None]
    yw = y * sw
    coef, *_ = np.linalg.lstsq(aw, yw, rcond=None)
    cov = np.linalg.inv(aw.T @ aw)
    resid = y - design @ coef
    dof = max(x.size - n_terms, 1)
    chi2 = float(np.sum(w * resid ** 2))
    return {
        "powers": powers,
        "coefficients": coef.tolist(),
        "coefficient_se": np.sqrt(np.diag(cov)).tolist(),
        "derivative_at_zero": float(coef[0]),
        "derivative_at_zero_se": float(np.sqrt(cov[0, 0])),
        "derivative_at_zero_ci95": [
            float(coef[0] - Z95 * np.sqrt(cov[0, 0])),
            float(coef[0] + Z95 * np.sqrt(cov[0, 0])),
        ],
        "n_points": int(x.size),
        "max_abs_e": float(max_abs_e),
        "chi2": chi2,
        "dof": dof,
        "chi2_per_dof": chi2 / dof,
        "max_abs_standardised_residual": float(
            np.max(np.abs(resid) / np.maximum(s, 1e-300))
        ),
    }


def central_difference_scan(
    e: np.ndarray, f: np.ndarray, se: np.ndarray, deltas: Sequence[float]
) -> list[dict[str, Any]]:
    """``D(delta)`` for each delta, to *exhibit* the O(delta^2) truncation law."""
    lookup = {round(float(v), 10): (float(f[i]), float(se[i]))
              for i, v in enumerate(e)}
    out = []
    for d in deltas:
        hi = lookup.get(round(float(d), 10))
        lo = lookup.get(round(float(-d), 10))
        if hi is None or lo is None:
            continue
        value = (hi[0] - lo[0]) / (2.0 * d)
        err = float(np.hypot(hi[1], lo[1]) / (2.0 * d))
        out.append({"delta": float(d), "D": value, "se": err})
    return out


def local_derivative(
    e: np.ndarray, f: np.ndarray, se: np.ndarray, *, half_window: int = 3
) -> dict[str, np.ndarray]:
    """Numerical ``F'(e)`` by a local weighted quadratic fit at every grid point."""
    order = np.argsort(e)
    x, y, s = e[order], f[order], se[order]
    n = x.size
    slope = np.full(n, np.nan)
    slope_se = np.full(n, np.nan)
    for i in range(n):
        lo = max(0, i - half_window)
        hi = min(n, i + half_window + 1)
        if hi - lo < 3:
            continue
        dx = x[lo:hi] - x[i]
        design = np.vstack([np.ones_like(dx), dx, dx ** 2]).T
        w = np.where(s[lo:hi] > 0, 1.0 / s[lo:hi] ** 2, 0.0)
        sw = np.sqrt(w)
        aw = design * sw[:, None]
        try:
            coef, *_ = np.linalg.lstsq(aw, y[lo:hi] * sw, rcond=None)
            cov = np.linalg.inv(aw.T @ aw)
        except np.linalg.LinAlgError:
            continue
        slope[i] = coef[1]
        slope_se[i] = np.sqrt(cov[1, 1])
    return {"e": x, "derivative": slope, "derivative_se": slope_se}


# --------------------------------------------------------------- symmetry --

def symmetry_diagnostics(
    e: np.ndarray, f: np.ndarray, se: np.ndarray
) -> dict[str, Any]:
    """Test the proved oddness ``F(-e) = -F(e)`` against the estimated map."""
    lookup = {round(float(v), 10): i for i, v in enumerate(e)}
    pairs = []
    for i, value in enumerate(e):
        if value <= 0:
            continue
        j = lookup.get(round(float(-value), 10))
        if j is None:
            continue
        asym = float(f[i] + f[j])                       # 0 under oddness
        asym_se = float(np.hypot(se[i], se[j]))
        pairs.append({
            "e": float(value),
            "F_plus": float(f[i]),
            "F_minus": float(f[j]),
            "asymmetry": asym,
            "asymmetry_se": asym_se,
            "z": asym / asym_se if asym_se > 0 else float("nan"),
        })
    z = np.array([p["z"] for p in pairs], dtype=float)
    z = z[np.isfinite(z)]
    return {
        "n_pairs": len(pairs),
        "pairs": pairs,
        "max_abs_z": float(np.max(np.abs(z))) if z.size else float("nan"),
        "mean_z": float(np.mean(z)) if z.size else float("nan"),
        "chi2": float(np.sum(z ** 2)) if z.size else float("nan"),
        "chi2_per_dof": float(np.sum(z ** 2) / z.size) if z.size else float("nan"),
        "interpretation": "oddness is a proved symmetry of the model; large |z| "
                          "indicates an estimator or implementation defect, not "
                          "a property of the model",
    }


# ------------------------------------------------------------- H_rho roots --

@dataclass(frozen=True, slots=True)
class RootCandidate:
    rho: float
    e_star: float
    e_star_se: float
    bracket: tuple[float, float]
    h_residual: float
    h_residual_se: float
    derivative: float
    derivative_se: float
    multiplier: float
    multiplier_se: float
    classification: str
    notes: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "rho": self.rho,
            "e_star": self.e_star,
            "e_star_se": self.e_star_se,
            "e_star_ci95": [self.e_star - Z95 * self.e_star_se,
                            self.e_star + Z95 * self.e_star_se],
            "bracket": list(self.bracket),
            "H_residual_at_e_star": self.h_residual,
            "H_residual_se": self.h_residual_se,
            "F_prime_at_e_star": self.derivative,
            "F_prime_at_e_star_se": self.derivative_se,
            "two_cycle_multiplier": self.multiplier,
            "two_cycle_multiplier_se": self.multiplier_se,
            "classification": self.classification,
            "notes": self.notes,
            "meaning": "candidate period-2 point of the DETERMINISTIC map "
                       "F_rho; the actual recursion is E_{j+1}=F_rho(E_j)+noise "
                       "and no claim about its invariant law is made here",
        }


def h_function(e: np.ndarray, f_rho: np.ndarray) -> np.ndarray:
    """``H_rho(e) = F_rho(e) + e``.  Nonzero roots are period-2 candidates."""
    return f_rho + e


def find_h_crossings(
    e: np.ndarray,
    f_rho: np.ndarray,
    se: np.ndarray,
    *,
    rho: float,
    derivative: dict[str, np.ndarray] | None = None,
    min_abs_e: float = 1e-6,
    min_z: float = 3.0,
) -> dict[str, list]:
    """Screen sign changes of ``H_rho`` on the positive half-grid.

    A bare sign change is not evidence of a crossing.  Near ``e = 0`` the map
    satisfies ``H_rho(e) ~ (1 - rho|F_1'(0)|) e``, which is tiny for small
    ``rho``, so Monte Carlo noise alone manufactures sign changes there.  A
    crossing is accepted only if the grid carries a point on each side whose
    ``H`` is itself at least ``min_z`` standard errors from zero **and** of the
    matching sign.  Rejected crossings are returned rather than dropped, so a
    reader can see what was screened out and why.
    """
    order = np.argsort(e)
    x, y, s = e[order], h_function(e[order], f_rho[order]), se[order]
    positive = np.flatnonzero(x > min_abs_e)
    accepted: list[RootCandidate] = []
    rejected: list[dict[str, Any]] = []
    if positive.size < 2:
        return {"accepted": accepted, "rejected": rejected}
    start = int(positive[0])

    def _support(lo: int, hi: int, sign: float) -> float:
        """Largest |H|/se among indices [lo, hi) whose sign matches ``sign``."""
        best = 0.0
        for j in range(lo, hi):
            if s[j] <= 0 or np.sign(y[j]) != sign:
                continue
            best = max(best, abs(y[j]) / s[j])
        return best

    for i in range(start, x.size - 1):
        y0, y1 = y[i], y[i + 1]
        if y0 == 0.0 or np.sign(y0) == np.sign(y1):
            continue
        span = y1 - y0
        if span == 0.0:
            continue
        t = -y0 / span
        root = float(x[i] + t * (x[i + 1] - x[i]))
        # y0 != 0 is guaranteed above; derive the right-hand sign from it so
        # that a grid point landing exactly on the root does not starve the
        # right-hand support test.
        left_sign = float(np.sign(y0))
        left_z = _support(start, i + 1, left_sign)
        right_z = _support(i + 1, x.size, -left_sign)
        info = {
            "rho": rho, "e_star_interpolated": root,
            "bracket": [float(x[i]), float(x[i + 1])],
            "left_support_z": left_z, "right_support_z": right_z,
            "min_z": min_z,
        }
        if root <= min_abs_e:
            info["reason"] = "interpolated root is not separated from e = 0"
            rejected.append(info)
            continue
        if left_z < min_z or right_z < min_z:
            info["reason"] = (
                f"no significant H of the required sign on both sides "
                f"(left {left_z:.2f}z, right {right_z:.2f}z, need {min_z}z); "
                f"consistent with noise around H == 0"
            )
            rejected.append(info)
            continue
        slope = span / (x[i + 1] - x[i])
        root_se = float(np.hypot((1 - t) * s[i], t * s[i + 1]) / abs(slope))
        fprime, fprime_se = _interpolate_derivative(derivative, root)
        accepted.append(RootCandidate(
            rho=rho, e_star=root, e_star_se=root_se,
            bracket=(float(x[i]), float(x[i + 1])),
            h_residual=0.0,
            h_residual_se=float(np.hypot(s[i], s[i + 1]) / 2.0),
            derivative=fprime, derivative_se=fprime_se,
            multiplier=fprime ** 2, multiplier_se=abs(2.0 * fprime) * fprime_se,
            classification="UNCLASSIFIED", notes=[],
        ))
    return {"accepted": accepted, "rejected": rejected}


def find_h_roots(
    e: np.ndarray,
    f_rho: np.ndarray,
    se: np.ndarray,
    *,
    rho: float,
    derivative: dict[str, np.ndarray] | None = None,
    min_abs_e: float = 1e-6,
    min_z: float = 3.0,
) -> list[RootCandidate]:
    """Accepted (screened) nonzero roots of ``H_rho``; see ``find_h_crossings``."""
    return find_h_crossings(e, f_rho, se, rho=rho, derivative=derivative,
                            min_abs_e=min_abs_e, min_z=min_z)["accepted"]


def _interpolate_derivative(
    derivative: dict[str, np.ndarray] | None, at: float
) -> tuple[float, float]:
    if derivative is None:
        return float("nan"), float("nan")
    x = derivative["e"]
    d = derivative["derivative"]
    ds = derivative["derivative_se"]
    good = np.isfinite(d)
    if good.sum() < 2:
        return float("nan"), float("nan")
    return (float(np.interp(at, x[good], d[good])),
            float(np.interp(at, x[good], ds[good])))


def classify_candidate(
    candidate: RootCandidate,
    *,
    h_residual_direct: float | None = None,
    h_residual_direct_se: float | None = None,
    symmetry_z: float | None = None,
    grid_sensitivity: float | None = None,
    mc_sensitivity: float | None = None,
    seed_replication_delta: float | None = None,
    tolerance_sigma: float = 3.0,
) -> RootCandidate:
    """Assign one of NO-/WEAK-/STRONG-CANDIDATE or NUMERICALLY-INCONSISTENT.

    * STRONG  -- ``e*`` is resolved to better than 10% of its own value, the
      direct high-precision ``H`` residual at ``e*`` is consistent with zero,
      the symmetry check passes, and independent seeds, a refined grid and a
      larger Monte Carlo sample all move ``e*`` by less than its own CI width.
    * WEAK    -- a sign change is present but at least one robustness check is
      marginal.
    * NUMERICALLY-INCONSISTENT -- checks actively disagree with each other.
    * NO-CANDIDATE is returned by the caller when no sign change exists at all.
    """
    notes: list[str] = []
    inconsistent = False
    weak = False

    rel = candidate.e_star_se / abs(candidate.e_star) if candidate.e_star else np.inf
    if rel > 0.10:
        weak = True
        notes.append(f"e* resolved to only {rel:.1%} relative precision")

    if h_residual_direct is not None and h_residual_direct_se:
        z = abs(h_residual_direct) / h_residual_direct_se
        notes.append(f"direct H(e*) residual z = {z:.2f}")
        if z > tolerance_sigma:
            inconsistent = True
            notes.append("direct residual at e* is inconsistent with zero")
        elif z > 2.0:
            weak = True

    if symmetry_z is not None:
        notes.append(f"symmetry |z| = {abs(symmetry_z):.2f}")
        if abs(symmetry_z) > tolerance_sigma:
            inconsistent = True
            notes.append("odd-symmetry check failed at e*")

    ci_width = 2.0 * Z95 * candidate.e_star_se
    for label, value in (("grid", grid_sensitivity),
                         ("Monte Carlo sample", mc_sensitivity),
                         ("independent seed", seed_replication_delta)):
        if value is None:
            notes.append(f"{label} sensitivity not measured")
            weak = True
            continue
        notes.append(f"{label} shift in e* = {value:+.5f} (CI width {ci_width:.5f})")
        if ci_width > 0 and abs(value) > 2.0 * ci_width:
            inconsistent = True
            notes.append(f"{label} shift exceeds twice the CI width")
        elif ci_width > 0 and abs(value) > ci_width:
            weak = True

    if inconsistent:
        label = "NUMERICALLY-INCONSISTENT"
    elif weak:
        label = "WEAK-CANDIDATE"
    else:
        label = "STRONG-CANDIDATE"
    return RootCandidate(
        rho=candidate.rho, e_star=candidate.e_star, e_star_se=candidate.e_star_se,
        bracket=candidate.bracket, h_residual=(h_residual_direct
                                               if h_residual_direct is not None
                                               else candidate.h_residual),
        h_residual_se=(h_residual_direct_se if h_residual_direct_se is not None
                       else candidate.h_residual_se),
        derivative=candidate.derivative, derivative_se=candidate.derivative_se,
        multiplier=candidate.multiplier, multiplier_se=candidate.multiplier_se,
        classification=label, notes=notes,
    )


# ------------------------------------------------------------- critical rho --

def critical_rho(f1_prime_0: float, f1_prime_0_se: float) -> dict[str, Any]:
    """``rho_c = 1/|F_1'(0)|`` with a delta-method interval.

    Local linear stability of the fixed point at 0 holds iff ``rho < rho_c``.
    This is a *local* threshold statement about the deterministic linearisation;
    it is not a claim about a global bifurcation of the noisy recursion.
    """
    magnitude = abs(f1_prime_0)
    rho_c = 1.0 / magnitude
    se = f1_prime_0_se / magnitude ** 2
    return {
        "F1_prime_0": f1_prime_0,
        "F1_prime_0_se": f1_prime_0_se,
        "rho_c": rho_c,
        "rho_c_se": se,
        "rho_c_ci95": [rho_c - Z95 * se, rho_c + Z95 * se],
        "definition": "rho_c = 1/|F_1'(0)|; local linear stability iff rho < rho_c",
        "scope": "LOCAL linear stability of the deterministic linearisation only",
    }


def rho_c_from_gamma_interval(gamma_low: float, gamma_high: float) -> dict[str, Any]:
    """``rho_c`` interval implied by a certified enclosure of ``Gamma``.

    ``F_1'(0) = 1 - Gamma`` so ``|F_1'(0)| = Gamma - 1`` whenever ``Gamma > 1``,
    and ``rho_c = 1/(Gamma - 1)`` is decreasing in ``Gamma``.
    """
    if gamma_low <= 1.0:
        raise ValueError("certified Gamma enclosure must lie above 1")
    return {
        "gamma_enclosure": [gamma_low, gamma_high],
        "F1_prime_0_enclosure": [1.0 - gamma_high, 1.0 - gamma_low],
        "rho_c_enclosure": [1.0 / (gamma_high - 1.0), 1.0 / (gamma_low - 1.0)],
        "source": "derived from the frozen Level 1-3 certificate; the arithmetic "
                  "here is exact but is performed in float, so treat the printed "
                  "endpoints as slightly-rounded, not outward-rounded",
    }


# ------------------------------------------------- batch-level derivative --

def odd_polynomial_fit_batched(
    e: np.ndarray,
    batch_means: np.ndarray,
    *,
    max_abs_e: float,
    n_terms: int = 3,
) -> dict[str, Any]:
    """Fit the odd polynomial once per batch and pool the resulting ``a1``.

    Why this and not the pooled weighted fit: under common random numbers the
    grid points share their driving noise, so the residuals of a pooled fit are
    correlated and its reported standard error is not valid.  Each *batch*,
    however, is an independent replicate of the whole map, so fitting per batch
    and taking the spread of ``a1`` across batches gives an uncertainty that
    needs no assumption about the correlation structure at all.

    ``batch_means`` has shape ``(n_batches, n_grid)`` and must be aligned with
    ``e``.
    """
    mask = np.abs(e) <= max_abs_e + 1e-12
    if int(mask.sum()) < n_terms + 1:
        raise ValueError(
            f"need > {n_terms} grid points with |e| <= {max_abs_e}, "
            f"got {int(mask.sum())}"
        )
    powers = [2 * i + 1 for i in range(n_terms)]
    design = np.vstack([e[mask] ** p for p in powers]).T
    # A high-order odd polynomial on a short symmetric window is badly
    # conditioned; without this guard lstsq silently returns the lower-order
    # solution and the order-selection rule then sees a zero shift and declares
    # convergence on a fit that never happened.
    if np.linalg.cond(design) > 1e10:
        raise np.linalg.LinAlgError(
            f"design matrix for n_terms={n_terms} on |e| <= {max_abs_e} is "
            f"ill-conditioned (cond > 1e10)"
        )
    coefs = np.array([
        np.linalg.lstsq(design, row[mask], rcond=None)[0]
        for row in batch_means
    ])
    a1 = coefs[:, 0]
    n = a1.size
    se = float(np.std(a1, ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    return {
        "max_abs_e": float(max_abs_e),
        "n_terms": n_terms,
        "n_points": int(mask.sum()),
        "n_batches": int(n),
        "derivative_at_zero": float(a1.mean()),
        "derivative_at_zero_se": se,
        "derivative_at_zero_ci95": [float(a1.mean() - Z95 * se),
                                    float(a1.mean() + Z95 * se)],
        "per_batch_a1": a1.tolist(),
        "mean_coefficients": coefs.mean(axis=0).tolist(),
        "uncertainty_method": "spread of per-batch fits (valid under common "
                              "random numbers)",
    }


def select_derivative_fit(
    e: np.ndarray,
    batch_means: np.ndarray,
    se: np.ndarray,
    *,
    windows: Sequence[float],
    max_terms: int = 5,
    tolerance_se: float = 1.0,
) -> dict[str, Any]:
    """Choose the fit window and polynomial order by a pre-specified rule.

    The rule, fixed before looking at the answer:

    1. For each window, find the smallest order ``n >= 2`` whose ``a1`` differs
       from the order-``n+1`` fit by at most ``tolerance_se`` standard errors of
       the larger fit.  That order is *converged*: adding another odd term no
       longer moves the answer by more than noise.
    2. Among windows that admit a converged order, take the one whose converged
       fit has the smallest standard error.

    The full scan is returned alongside the selection so that a reader can see
    every fit that was considered, including the ones the rule rejected.  The
    pooled weighted fit is reported too, for its chi-square, which is what
    exposes an under-specified order.
    """
    scan: list[dict[str, Any]] = []
    for window in windows:
        fits: dict[int, dict[str, Any]] = {}
        for n_terms in range(2, max_terms + 1):
            try:
                batched = odd_polynomial_fit_batched(
                    e, batch_means, max_abs_e=window, n_terms=n_terms)
            except (ValueError, np.linalg.LinAlgError):
                continue
            try:
                pooled = odd_polynomial_fit(
                    e, batch_means.mean(axis=0), se, max_abs_e=window,
                    n_terms=n_terms)
                batched["chi2_per_dof"] = pooled["chi2_per_dof"]
                batched["pooled_se"] = pooled["derivative_at_zero_se"]
            except (ValueError, np.linalg.LinAlgError):
                batched["chi2_per_dof"] = float("nan")
                batched["pooled_se"] = float("nan")
            fits[n_terms] = batched
        for n_terms, fit in fits.items():
            nxt = fits.get(n_terms + 1)
            if nxt is None:
                fit["order_shift"] = None
                fit["order_shift_in_se"] = None
                fit["converged"] = False
                continue
            shift = nxt["derivative_at_zero"] - fit["derivative_at_zero"]
            ref = nxt["derivative_at_zero_se"]
            fit["order_shift"] = float(shift)
            fit["order_shift_in_se"] = (float(abs(shift) / ref) if ref > 0
                                        else float("inf"))
            fit["converged"] = bool(fit["order_shift_in_se"] <= tolerance_se)
        scan.extend(fits.values())

    converged = [f for f in scan if f.get("converged")]
    selected = (min(converged, key=lambda f: f["derivative_at_zero_se"])
                if converged else None)
    return {
        "rule": (f"smallest order whose a1 moves by <= {tolerance_se} s.e. when "
                 f"one more odd term is added; then the window with the "
                 f"smallest s.e. among converged fits"),
        "windows": [float(w) for w in windows],
        "max_terms": max_terms,
        "scan": scan,
        "selected": selected,
        "n_converged": len(converged),
    }
