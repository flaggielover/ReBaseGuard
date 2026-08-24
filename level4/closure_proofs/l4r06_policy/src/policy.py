"""Uncertainty-aware P3 policy reconstructed from protected D4 evidence."""
from __future__ import annotations

from dataclasses import asdict, dataclass

from config import P2_RHO, REGIMES, ROOT, SAFETY_FACTOR, read_json


@dataclass(frozen=True, slots=True)
class PolicyAction:
    m: int
    rho_c_lower95: float
    safety_factor: float
    uncapped_allowance: float
    rho: float
    saturated: bool
    multiplier_bound: float

    def as_dict(self) -> dict:
        return asdict(self)


def d4_lower_bounds() -> dict[int, float]:
    decision = read_json(ROOT / "level4/closure_proofs/d4_phase_map/results/decision.json")
    return {
        int(row["m"]): float(row["rho_c_ci95"][0])
        for row in decision["rho_c_rows"]
    }


def p3_action(m: int) -> PolicyAction:
    if m not in REGIMES:
        raise ValueError(f"m={m} is outside frozen regimes {REGIMES}")
    lower = d4_lower_bounds()[m]
    allowance = SAFETY_FACTOR * lower
    rho = min(1.0, allowance)
    return PolicyAction(
        m=m,
        rho_c_lower95=lower,
        safety_factor=SAFETY_FACTOR,
        uncapped_allowance=allowance,
        rho=rho,
        saturated=allowance >= 1.0,
        multiplier_bound=rho / lower,
    )


def policies(m: int) -> dict[str, float]:
    return {"P0": 0.0, "P1": 1.0, "P2": P2_RHO, "P3": p3_action(m).rho}


def policy_table() -> list[dict]:
    return [p3_action(m).as_dict() for m in REGIMES]
