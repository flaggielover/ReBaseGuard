"""Generic first-order stability classifier for the closed derivative theorems.

Every statement produced here is a consequence of the single imported identity

    lambda_{D,m}(rho) = F'_{rho,m}(0) = rho (1 - GammaTilde_{D,m}),

which is closed for the Gaussian two-sided CUSUM (Priority 1) and for the
reset symmetric two-chart Shiryaev-Roberts detector (Priority 2).  Nothing in
this module knows anything about a detector; it only performs the linearisation
algebra and the associated evidence bookkeeping.

The classification is first order and local.  It never asserts global
stability, nonlinear convergence, or uniqueness of a stationary law.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config import BOUNDARY_TOLERANCE, RHO_DOMAIN, Z95

CLASS_STABLE = "LOCALLY-STABLE"
CLASS_BOUNDARY = "BOUNDARY"
CLASS_UNSTABLE = "LOCALLY-UNSTABLE"

DYNAMICS = {
    CLASS_STABLE: "LOCALLY_ATTRACTING",
    CLASS_BOUNDARY: "FIRST_ORDER_BOUNDARY_INCONCLUSIVE",
    CLASS_UNSTABLE: "LOCALLY_REPELLING",
}

UNCERTAINTY_EXACT = "NOT_APPLICABLE_EXACT_INPUT"
UNCERTAINTY_ROBUST = "ROBUST_UNDER_95_INTERVAL"
UNCERTAINTY_SENSITIVE = "UNCERTAINTY_SENSITIVE_CROSSES_UNIT_MAGNITUDE"


def multiplier(rho: float, gamma: float) -> float:
    """The closed derivative identity itself."""
    return rho * (1.0 - gamma)


def classify_magnitude(magnitude: float,
                       tolerance: float = BOUNDARY_TOLERANCE) -> str:
    if abs(magnitude - 1.0) <= tolerance:
        return CLASS_BOUNDARY
    return CLASS_STABLE if magnitude < 1.0 else CLASS_UNSTABLE


def classify(rho: float, gamma: float,
             tolerance: float = BOUNDARY_TOLERANCE) -> str:
    return classify_magnitude(abs(multiplier(rho, gamma)), tolerance)


def gamma_regime(gamma: float) -> str:
    """Explicit audit of every GammaTilde regime, not only the observed one."""
    if gamma > 2.0:
        return "GAMMA_GT_2"
    if gamma == 2.0:
        return "GAMMA_EQ_2"
    if gamma > 1.0:
        return "ONE_LT_GAMMA_LT_2"
    if gamma == 1.0:
        return "GAMMA_EQ_1"
    if gamma >= 0.0:
        return "ZERO_LE_GAMMA_LT_1"
    return "GAMMA_LT_0"


def magnitude_interval(rho: float, gamma_lo: float,
                       gamma_hi: float) -> tuple[float, float]:
    """Exact image of ``[gamma_lo, gamma_hi]`` under ``rho|1-.|`` for rho>=0.

    ``|1-gamma|`` is not monotone, so the minimum is zero whenever the gain
    interval straddles one.  Taking endpoint minima blindly would understate
    the uncertainty exactly in the regime where it matters.
    """
    if rho < 0.0:
        raise ValueError("the admissible reuse fraction is nonnegative")
    if gamma_lo > gamma_hi:
        gamma_lo, gamma_hi = gamma_hi, gamma_lo
    ends = (abs(1.0 - gamma_lo), abs(1.0 - gamma_hi))
    low = 0.0 if gamma_lo <= 1.0 <= gamma_hi else min(ends)
    return rho * low, rho * max(ends)


def normal_interval(estimate: float, standard_error: float,
                    z: float = Z95) -> tuple[float, float]:
    return estimate - z * standard_error, estimate + z * standard_error


@dataclass(frozen=True)
class Boundary:
    """Critical reuse fraction derived from the linearisation, with audit."""

    gamma_regime: str
    rho_crit: float | None
    rho_crit_formula: str
    rho_crit_formula_applicable: bool
    rho_crit_se_delta: float | None
    rho_crit_interval: list[float | None] | None
    accessible_in_admissible_domain: bool
    admissible_interpretation: str


def boundary(gamma: float, gamma_se: float | None = None,
             gamma_interval: tuple[float, float] | None = None,
             tolerance: float = BOUNDARY_TOLERANCE) -> Boundary:
    """Derive the critical reuse fraction and audit every degenerate case."""
    lo_rho, hi_rho = RHO_DOMAIN
    regime = gamma_regime(gamma)
    distance = abs(1.0 - gamma)
    applicable = gamma > 1.0

    if distance == 0.0:
        return Boundary(
            gamma_regime=regime,
            rho_crit=None,
            rho_crit_formula="undefined: the multiplier is identically zero",
            rho_crit_formula_applicable=False,
            rho_crit_se_delta=None,
            rho_crit_interval=None,
            accessible_in_admissible_domain=False,
            admissible_interpretation=(
                "GammaTilde=1 makes lambda=0 for every rho, so the whole "
                "admissible domain is locally attracting and no boundary exists"
            ),
        )

    rho_crit = 1.0 / distance
    accessible = lo_rho <= rho_crit <= hi_rho + tolerance

    if applicable:
        formula = "rho_crit = 1/(GammaTilde-1)"
    else:
        formula = "rho_crit = 1/|1-GammaTilde| (the GammaTilde>1 form does not apply)"

    se = None
    interval: list[float | None] | None = None
    if gamma_se is not None and distance > 0.0:
        se = gamma_se / distance**2
    if gamma_interval is not None:
        g_lo, g_hi = sorted(gamma_interval)
        if g_lo > 1.0:
            interval = [1.0 / (g_hi - 1.0), 1.0 / (g_lo - 1.0)]
        elif g_hi < 1.0:
            interval = [1.0 / (1.0 - g_lo), 1.0 / (1.0 - g_hi)]
        else:
            interval = [min(1.0 / (g_hi - 1.0) if g_hi > 1.0 else float("inf"),
                            1.0 / (1.0 - g_lo) if g_lo < 1.0 else float("inf")),
                        None]
            if interval[0] == float("inf"):
                interval = [None, None]

    if accessible:
        interpretation = (
            f"the boundary lies inside the admissible domain [{lo_rho:g},{hi_rho:g}]: "
            f"rho<{rho_crit:.6f} is locally attracting and rho>{rho_crit:.6f} "
            "is locally repelling"
        )
    else:
        interpretation = (
            f"the boundary rho_crit={rho_crit:.6f} lies outside the admissible "
            f"domain [{lo_rho:g},{hi_rho:g}], so every admissible reuse fraction "
            "is locally attracting"
        )

    return Boundary(
        gamma_regime=regime,
        rho_crit=rho_crit,
        rho_crit_formula=formula,
        rho_crit_formula_applicable=applicable,
        rho_crit_se_delta=se,
        rho_crit_interval=interval,
        accessible_in_admissible_domain=accessible,
        admissible_interpretation=interpretation,
    )


def classify_cell(rho: float, gamma: float, *,
                  cell_evidence_class: str,
                  gamma_evidence_class: str,
                  gamma_se: float | None = None,
                  gamma_interval: tuple[float, float] | None = None,
                  gamma_exact: str | None = None,
                  tolerance: float = BOUNDARY_TOLERANCE) -> dict[str, Any]:
    """Full machine-readable record behind one plotted cell."""
    lam = multiplier(rho, gamma)
    magnitude = abs(lam)
    klass = classify_magnitude(magnitude, tolerance)

    record: dict[str, Any] = {
        "rho": rho,
        "rho_in_admissible_domain": RHO_DOMAIN[0] <= rho <= RHO_DOMAIN[1],
        "gamma_tilde": gamma,
        "gamma_tilde_exact": gamma_exact,
        "gamma_evidence_class": gamma_evidence_class,
        "lambda": lam,
        "abs_lambda": magnitude,
        "class": klass,
        "local_first_order_dynamics": DYNAMICS[klass],
        "evidence_class": cell_evidence_class,
        "gamma_regime": gamma_regime(gamma),
    }

    if gamma_interval is None:
        record["gamma_tilde_ci95"] = None
        record["lambda_ci95"] = None
        record["abs_lambda_interval"] = None
        record["class_at_interval_endpoints"] = None
        record["uncertainty_status"] = UNCERTAINTY_EXACT
        record["classification_reportable_as_robust"] = True
        record["gamma_tilde_se"] = None
        return record

    g_lo, g_hi = sorted(gamma_interval)
    lam_ends = sorted((multiplier(rho, g_lo), multiplier(rho, g_hi)))
    mag_lo, mag_hi = magnitude_interval(rho, g_lo, g_hi)
    class_lo = classify_magnitude(mag_lo, tolerance)
    class_hi = classify_magnitude(mag_hi, tolerance)
    sensitive = class_lo != class_hi or klass == CLASS_BOUNDARY

    record["gamma_tilde_se"] = gamma_se
    record["gamma_tilde_ci95"] = [g_lo, g_hi]
    record["lambda_ci95"] = list(lam_ends)
    record["abs_lambda_interval"] = [mag_lo, mag_hi]
    record["class_at_interval_endpoints"] = [class_lo, class_hi]
    record["uncertainty_status"] = (
        UNCERTAINTY_SENSITIVE if sensitive else UNCERTAINTY_ROBUST
    )
    record["classification_reportable_as_robust"] = not sensitive
    if sensitive:
        record["evidence_class"] = "INCONCLUSIVE"
    return record


def boundary_as_dict(value: Boundary) -> dict[str, Any]:
    return asdict(value)
