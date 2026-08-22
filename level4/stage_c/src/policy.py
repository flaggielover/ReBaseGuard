"""Stage C — the ReBaseGuard stability-aware reuse policy.

The policy is a *definition*, fixed before any Stage C evaluation was run.  It
is derived only from frozen Level 1-3 / Stage A theory and never from Stage C
outcomes, and in particular never from the Stage B root e* (see
`tests/test_policy.py::test_policy_does_not_depend_on_stage_b_root`).

Frozen inputs
-------------
Level 2C proves, unconditionally, the mixed-reuse linearity  F_rho = rho * F_1
and the score identity  F_1'(0) = 1 - Gamma.  Hence

    F'_rho(0) = rho (1 - Gamma) ,      |F'_rho(0)| = rho (Gamma - 1)   (Gamma > 1)

and the fixed point e = 0 of the deterministic conditional-mean map is locally
linearly stable iff rho < rho_c = 1/(Gamma - 1).

The policy
----------
Choose a safety margin delta in (0,1) and require

    |F'_rho(0)| <= 1 - delta        i.e.       rho <= (1 - delta) / (Gamma - 1)

which gives, after clipping to [0,1],

    rho_safe(delta) = clip( (1 - delta) / (Gamma - 1), 0, 1 ) .

Two versions, and the difference matters
----------------------------------------
`POINT` substitutes the Monte Carlo point estimate Gamma_hat.  Its stability
statement is only as good as that estimate: it is a *heuristic*, and calling it
certified would be false.

`CONSERVATIVE` substitutes the upper end of the frozen certified enclosure of
Gamma.  Because |F'_rho(0)| = rho (Gamma - 1) is increasing in Gamma, using
Gamma_upper gives the worst case over everything the certificate admits, so the
guarantee |F'_rho(0)| <= 1 - delta holds for the TRUE Gamma.  That statement is
genuinely certified -- but only the *local linear stability* statement, and only
for the deterministic map.  It is not a statement about the noisy recursion.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

# Frozen Level 1-3 certified enclosure of Gamma = E_0[Z_tau T_tau]
# (rebaseguard-proof/proofs/certificate.json; closure/04_ARB_CERTIFICATE.md).
GAMMA_CERT_LOW = 3.9243482005828971281857775466050952672958374023437500
GAMMA_CERT_HIGH = 27.849382127546703280529527546605095267295837402343750

# Stage A Gate 4.2 pooled score-route estimate (Monte Carlo, NOT certified).
GAMMA_POINT = 15.885729
GAMMA_POINT_SE = 0.020165

POINT = "point"
CONSERVATIVE = "conservative"


@dataclass(frozen=True, slots=True)
class PolicyResult:
    variant: str
    delta: float
    gamma_used: float
    rho: float
    clipped: bool
    slope_at_zero: float          # F'_rho(0) with the Gamma actually used
    guarantee: str
    evidence_class: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def critical_rho(gamma: float) -> float:
    """rho_c = 1/(Gamma - 1), the local linear stability boundary."""
    if gamma <= 1.0:
        raise ValueError(
            f"Gamma must exceed 1 for a finite critical reuse fraction; got {gamma}"
        )
    return 1.0 / (gamma - 1.0)


def rho_safe(delta: float, *, variant: str = CONSERVATIVE,
             gamma_point: float = GAMMA_POINT,
             gamma_cert_high: float = GAMMA_CERT_HIGH) -> PolicyResult:
    """The ReBaseGuard reuse fraction for safety margin ``delta``."""
    if not 0.0 < delta < 1.0:
        raise ValueError(f"delta must lie strictly in (0,1); got {delta}")
    if variant == POINT:
        gamma = gamma_point
        guarantee = ("heuristic: |F'_rho(0)| <= 1-delta holds if the Monte "
                     "Carlo point estimate of Gamma is exact")
        evidence = "NEW-NUMERICAL (point estimate; NOT certified)"
    elif variant == CONSERVATIVE:
        gamma = gamma_cert_high
        guarantee = ("certified: |F'_rho(0)| <= 1-delta for the TRUE Gamma, "
                     "because |F'_rho(0)| = rho(Gamma-1) is increasing in Gamma "
                     "and Gamma <= Gamma_upper is a frozen certified enclosure")
        evidence = ("RIGOROUS-CERTIFIED for LOCAL LINEAR STABILITY of the "
                    "DETERMINISTIC map only")
    else:
        raise ValueError(f"unknown policy variant {variant!r}")

    raw = (1.0 - delta) / (gamma - 1.0)
    rho = min(max(raw, 0.0), 1.0)
    return PolicyResult(
        variant=variant, delta=delta, gamma_used=gamma, rho=rho,
        clipped=(rho != raw), slope_at_zero=rho * (1.0 - gamma),
        guarantee=guarantee, evidence_class=evidence,
    )


def policy_table(deltas=(0.05, 0.1, 0.2, 0.5)) -> list[dict[str, Any]]:
    rows = []
    for d in deltas:
        for variant in (POINT, CONSERVATIVE):
            rows.append(rho_safe(d, variant=variant).as_dict())
    return rows
