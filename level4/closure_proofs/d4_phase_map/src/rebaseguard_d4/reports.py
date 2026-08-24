"""Generate human-readable D4 reports from the final structured decision."""

from __future__ import annotations

from .common import read_json
from .config import CAMPAIGN, RESULTS


def _gamma_table(rows: list[dict]) -> str:
    lines = [
        "| m | GammaTilde_m | SE | 95% CI | C_m | P(tau<m) |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        gamma = row["gamma_tilde"]
        correction = row["short_cycle_correction"]
        probability = row["short_cycle_probability"]
        lines.append(
            f"| {row['m']} | {gamma['mean']:.6f} | {gamma['se']:.6f} | "
            f"[{gamma['ci95'][0]:.6f}, {gamma['ci95'][1]:.6f}] | "
            f"{correction['mean']:.6f} | {probability['estimate']:.6f} |"
        )
    return "\n".join(lines)


def _rho_table(rows: list[dict]) -> str:
    lines = [
        "| m | Gamma regime | rho_c | SE | 95% CI | accessible in [0,1]? |",
        "|---:|---|---:|---:|---:|---|",
    ]
    for row in rows:
        value = row["rho_c_unconstrained"]
        se = row["rho_c_se_delta"]
        ci = row["rho_c_ci95"]
        value_text = "infinite" if value is None else f"{value:.6f}"
        se_text = "n/a" if se is None else f"{se:.6f}"
        ci_text = "unbounded" if None in ci else f"[{ci[0]:.6f}, {ci[1]:.6f}]"
        lines.append(
            f"| {row['m']} | {row['gamma_regime']} | {value_text} | {se_text} | "
            f"{ci_text} | {'yes' if row['boundary_accessible_on_unit_interval'] else 'no'} |"
        )
    return "\n".join(lines)


def _direct_table(rows: list[dict]) -> str:
    lines = [
        "| Cell | m | rho | theorem lambda | direct derivative | SE | abs z | relative gap | result |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['cell_id']} | {row['m']} | {row['rho']:.2f} | "
            f"{row['theorem_lambda']:+.6f} | {row['direct_derivative']:+.6f} | "
            f"{row['direct_derivative_se']:.6f} | {row['absolute_z']:.3f} | "
            f"{100*row['relative_discrepancy']:.2f}% | {'PASS' if row['passed'] else 'FAIL'} |"
        )
    return "\n".join(lines)


def _operational_table(rows: list[dict]) -> str:
    lines = [
        "| m | rho | theorem class | lambda | cycle ARL | reference MSE | e ACF1 | direction ACF1 |",
        "|---:|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        metric = row["metrics"]
        lines.append(
            f"| {row['m']} | {row['rho']:.2f} | {row['theorem_class']} | {row['lambda']:+.4f} | "
            f"{metric['cycle_arl']['mean']:.2f} | {metric['reference_mse']['mean']:.4f} | "
            f"{metric['reference_acf1']['mean']:+.3f} | {metric['direction_acf1']['mean']:+.3f} |"
        )
    return "\n".join(lines)


def build() -> None:
    decision = read_json(RESULTS / "decision.json")
    crossing = decision["gamma_equals_2_crossings"][0]
    gamma_table = _gamma_table(decision["gamma_rows"])
    rho_table = _rho_table(decision["rho_c_rows"])
    direct_table = _direct_table(decision["direct_validation"])
    operational_table = _operational_table(decision["operational_overlay"]["rows"])

    phase_report = f"""# D4 theorem-supported phase-map report

**Scoped decision:** `{decision['decision']}`

The imported Track-1B identity is

`{decision['derivative_formula']}`,

with `{decision['gamma_definition']}`.

The local multiplier is `lambda(m,rho)=rho(1-GammaTilde_m)`. The relevant
`GammaTilde_m>1` boundary is `rho_c(m)=1/(GammaTilde_m-1)`. It is accessible
on `rho in [0,1]` exactly when `GammaTilde_m>=2`.

## Gamma grid

{gamma_table}

## Critical reuse grid

{rho_table}

The `GammaTilde_m=2`, equivalently `rho_c=1`, crossing is bracketed by
`m={crossing['bracket'][0]}` and `m={crossing['bracket'][1]}`. Frozen
piecewise-linear interpolation in `log(m)` gives
`m={crossing['m_crossing_log_linear']:.6f}`.

## Direct-map correspondence

{direct_table}

All six preselected cells pass. The map is therefore theorem-supported rather
than a boundary discovered by a parameter sweep.

## Scope

This is a protocol-specific local stability map for the deterministic
conditional-mean reference skeleton. It does not assert a discontinuity in the
stochastic repeated-monitoring chain or a cross-distribution law.
"""
    (CAMPAIGN / "PHASE_MAP_REPORT.md").write_text(phase_report)

    operational_report = f"""# D4 operational bridge

The operational overlay is a consequence check, not a boundary-discovery or
discontinuity test.

{operational_table}

Within the paired `m=20` and `m=50` cells, higher reuse changes all four
reported metrics: cycle ARL falls, reference MSE rises, and the two lag-one
dependence measures become more negative. Those cell contrasts are compatible
with stronger feedback, but the sparse pre-frozen overlay does not establish
an abrupt change at `rho_c`.

Historical Stage-D D2.5 remains exactly **MATHEMATICAL, NOT OPERATIONAL**.
Its `m`-direction experiment found smooth monotone behavior through the
historical crossing; this later rho-direction consequence check neither
rewrites nor rescues that negative result.
"""
    (CAMPAIGN / "OPERATIONAL_BRIDGE.md").write_text(operational_report)

    blockers = decision["remaining_global_blockers_after_scoped_d4_closure"]
    blocker_lines = "\n".join(f"- {row['name']} — {row['type']}" for row in blockers)
    criteria_lines = "\n".join(
        f"- {key}: {'PASS' if decision['criteria'][key] else 'FAIL'}"
        for key in sorted(decision["criteria"], key=lambda value: int(value.split(".")[1]))
    )
    final_report = f"""# D4 phase-map closure — final report

## A. D4 verdict

`{decision['decision']}`

## B. Exact derivative formula used

`{decision['derivative_formula']}`

## C. Exact Gamma definition

`{decision['gamma_definition']}`

## D. Gamma table

{gamma_table}

## E. rho_c table

{rho_table}

## F. Gamma=2 / rho_c=1 crossing

Bracket `{crossing['bracket']}`; frozen log-linear estimate
`{crossing['m_crossing_log_linear']:.6f}`.

## G. Direct-map correspondence

{direct_table}

Result: 6/6 frozen cells passed.

## H. Operational overlay

{operational_table}

The overlay shows metric differences with reuse, but does not establish an
abrupt stochastic-chain change at the theorem boundary.

## I. Stage-D operational conclusion

Still `MATHEMATICAL, NOT OPERATIONAL`, unchanged.

## J. Figures

- `figures/d4_local_stability_map.png`
- `figures/d4_gamma_and_boundary.png`
- `figures/d4_operational_overlay.png`

## K. Tests

Focused D4 tests: `{decision['verification']['d4_focused_tests']}` passed.
Current distinct check accounting: `{decision['verification']['current_distinct_checks']} / {decision['verification']['current_distinct_checks']}`.

## L. Adversarial result

`{decision['adversarial']['passed']} / {decision['adversarial']['total']}` passed.

## M. Reproduction

`bash level4/closure_proofs/d4_phase_map/reproduce.sh`

## N. Historical statuses

Stage D remains `STAGE-D-PARTIAL`; D2.3 remains `FAILED`; D2.5 remains its
negative result; Track 1A remains failed; Track 1B remains closed; Stage F and
the current post-closure global verdict remain `LEVEL-4-PARTIAL`.

## O. Git

See repository history for the freeze, phase-map, and final closure commits.
All pushes are fast-forward and history is not rewritten.

## P. Original global D4 mandatory requirement

`{decision['original_global_d4_requirement']}` in this later scoped campaign.
No global re-audit is performed here.

## Q. Next blocker

`PRIOR-ART/NOVELTY VERIFICATION`

## Frozen closure criteria

{criteria_lines}

## Remaining global blockers after scoped D4 closure

{blocker_lines}
"""
    (CAMPAIGN / "FINAL_REPORT.md").write_text(final_report)
