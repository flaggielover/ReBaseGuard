#!/usr/bin/env python3
"""Turn the raw correspondence run into the Priority-4 map, tables and reports.

The classification rules are Priority 3's, unchanged.  Two things are added,
both of which restrict rather than widen the claim:

* a cell is classified only if the campaign's own evidence says the origin is a
  fixed point.  For an asymmetric family `E_0[A_m] != 0`, there is no fixed
  point at the origin, and the cell is reported as `FIXED-POINT-NOT-AT-ORIGIN`
  instead of being given a stability label it has not earned;
* a cell whose family is `OUTSIDE-ASSUMPTIONS` is never classified at all.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
Z95 = 1.959963984540054
RHO_GRID = (0.0, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0)

#: Threshold for the origin-is-a-fixed-point check.
#:
#: For a symmetric family with a reflection-equivariant detector, Theorem G4
#: *proves* `E_0[A_m] = 0`; it is not an empirical question, and a 95% test
#: would reject roughly one symmetric cell in twenty by pure chance.  The
#: numerical check is therefore a **falsification** test with a deliberately
#: wide threshold: it exists to catch a gross violation such as an asymmetric
#: family, where the measured `E_0[A_1]` is of order one against a standard
#: error of order 1e-3, i.e. hundreds of standard errors.  Six standard errors
#: separates those two situations by an enormous margin in both directions.
#:
#: Fixed before any result of this campaign was generated.
ORIGIN_FALSIFICATION_Z = 6.0


def interval(estimate: dict) -> tuple[float, float]:
    return (estimate["mean"] - Z95 * estimate["se"],
            estimate["mean"] + Z95 * estimate["se"])


def classify(rho: float, gamma: float, lo: float, hi: float) -> dict:
    distance = abs(1.0 - gamma)
    magnitude = rho * distance
    endpoints = sorted({rho * abs(1.0 - lo), rho * abs(1.0 - hi)})
    contains_one = lo <= 1.0 <= hi
    band_lo = 0.0 if contains_one else endpoints[0]
    band_hi = endpoints[-1]
    if magnitude < 1.0:
        label = "LOCALLY-STABLE"
    elif magnitude > 1.0:
        label = "LOCALLY-UNSTABLE"
    else:
        label = "BOUNDARY"
    robust = not (band_lo <= 1.0 <= band_hi)
    return {
        "rho": rho, "abs_multiplier": magnitude,
        "abs_multiplier_interval": [band_lo, band_hi],
        "class": label,
        "evidence_class": "THEOREM-SUPPORTED-MONTE-CARLO-GAIN" if robust
        else "INCONCLUSIVE",
        "classification_reportable_as_robust": robust,
    }


def build_map(payload: dict, protocol: dict) -> dict:
    rows = []
    for cell in payload["monte_carlo"]["cells"]:
        gamma = cell["route_a"]
        lo, hi = interval(gamma)
        window = cell["mean_window_at_zero"]
        origin_z = (
            abs(window["mean"]) / window["se"] if window["se"] > 0
            else (0.0 if window["mean"] == 0.0 else math.inf)
        )
        origin_is_fixed = origin_z <= ORIGIN_FALSIFICATION_Z
        base = {
            "layer": cell["layer"], "detector": cell["detector"],
            "family": cell["family"], "family_class": cell["family_class"],
            "m": cell["m"], "arl": cell["arl"]["mean"],
            "gamma": gamma["mean"], "gamma_se": gamma["se"],
            "gamma_ci95": [lo, hi],
            "gamma_evidence_class": "EMPIRICAL_ONLY",
            "route_b_gamma": cell["route_b"]["mean"],
            "route_b_se": cell["route_b"]["se"],
            "correspondence": cell["correspondence"],
            "correspondence_verdict": cell["verdict"],
            "mean_window_at_zero": window["mean"],
            "mean_window_at_zero_se": window["se"],
            "mean_window_at_zero_z": origin_z,
            "origin_falsification_z_threshold": ORIGIN_FALSIFICATION_Z,
            "origin_is_fixed_point": bool(origin_is_fixed),
            "expected_short_correction": cell["short_correction"]["mean"],
            "expected_short_correction_se": cell["short_correction"]["se"],
            "fixed_denominator_gain": cell["fixed_denominator_gain"]["mean"],
            "gaussian_form_gain": cell["gaussian_form_gain"]["mean"],
        }
        if cell["family_class"] != "THEOREM-SUPPORTED":
            base["stability_status"] = "NOT-CLASSIFIED-OUTSIDE-ASSUMPTIONS"
            base["critical_rho"] = None
            base["cells"] = []
        elif not origin_is_fixed:
            base["stability_status"] = "FIXED-POINT-NOT-AT-ORIGIN"
            base["critical_rho"] = None
            base["cells"] = []
        else:
            distance = abs(1.0 - gamma["mean"])
            base["stability_status"] = "CLASSIFIED"
            base["critical_rho"] = (1.0 / distance) if distance > 0 else None
            base["critical_rho_se"] = (
                gamma["se"] / distance ** 2 if distance > 0 else None
            )
            base["cells"] = [
                classify(rho, gamma["mean"], lo, hi) for rho in RHO_GRID
            ]
        rows.append(base)
    return {
        "schema": "rebaseguard.p4-stability-map.v1",
        "classification_rule": "Priority-3 first-order rule, unchanged: "
                               "|lambda| = rho |1 - Gamma|, rho_c = 1/|1-Gamma|",
        "rho_grid": list(RHO_GRID),
        "m_grid": protocol["m_grid"],
        "z95": Z95,
        "rows": rows,
    }


def write_csv(mapping: dict, path: Path) -> None:
    fields = ["layer", "detector", "family", "family_class", "m", "arl",
              "gamma", "gamma_se", "route_b_gamma", "route_b_se",
              "correspondence_verdict", "mean_window_at_zero",
              "origin_is_fixed_point", "expected_short_correction",
              "fixed_denominator_gain", "gaussian_form_gain",
              "stability_status", "critical_rho"]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        for row in mapping["rows"]:
            flat = dict(row)
            flat["correspondence_verdict"] = row["correspondence_verdict"]
            writer.writerow(flat)


def markdown_table(rows: list[dict], columns: list[tuple[str, str]]) -> str:
    head = "| " + " | ".join(title for title, _ in columns) + " |"
    rule = "|" + "|".join("---" for _ in columns) + "|"
    body = []
    for row in rows:
        body.append("| " + " | ".join(fmt(row) for _, fmt in columns) + " |")
    return "\n".join([head, rule, *body])


def main() -> None:
    payload = json.loads((CAMPAIGN / "results" / "correspondence.json").read_text())
    protocol = json.loads((CAMPAIGN / "configs" / "P4_PROTOCOL.json").read_text())
    mapping = build_map(payload, protocol)
    (CAMPAIGN / "results" / "stability_map.json").write_text(
        json.dumps(mapping, indent=2) + "\n"
    )
    write_csv(mapping, CAMPAIGN / "results" / "stability_map.csv")

    # ---------------- NUMERICAL_CORRESPONDENCE.md ----------------
    q = payload["route_q"]
    lines: list[str] = []
    lines.append("# Numerical correspondence\n")
    lines.append(
        "Four independent routes.  Route Q and Route N have known or "
        "deterministically computed answers and therefore *test* the "
        "implementation; Routes A and B are two Monte Carlo estimates of the "
        "same quantity under the frozen detector recursions and therefore test "
        "the theorem.  Every table states its own evidence class.\n"
    )
    lines.append("## 1. Route Q -- deterministic quadrature, memoryless detector\n")
    lines.append(
        "No sampling error.  Both sides of Theorem G1 are evaluated by adaptive "
        "quadrature for the detector `tau = inf{t : |Z_t| >= c}` with "
        f"`c = {q['c']}`, including the truncated window, the random "
        "denominator and the `tau < m` branch.  This is **not** the frozen "
        "operating point and is never reported as evidence about it.\n"
    )
    lines.append(markdown_table(q["rows"], [
        ("family", lambda r: r["family"]),
        ("m", lambda r: str(r["m"])),
        ("`Gamma` (score side)", lambda r: f"{r['gamma_score_route']:.10f}"),
        ("`-g_m'(0)` (map side)", lambda r: f"{r['negative_map_derivative']:.10f}"),
        ("relative", lambda r: f"{r['relative_discrepancy']:.2e}"),
        ("result", lambda r: "PASS" if r["pass"] else "FAIL"),
    ]))
    uc = q["uniform_counterexample"]
    lines.append(
        f"\nAll Route-Q cells pass: **{q['all_pass']}**.\n\n"
        "The uniform family is the deliberate negative control.  Its a.e. "
        "interior score is identically zero, so the score side is exactly "
        f"`{uc['gamma_score_route']}`, while the exact map slope is "
        f"`-{uc['negative_map_derivative_exact']:.6f}` "
        f"(quadrature: `-{uc['negative_map_derivative_quadrature']:.6f}`).  "
        "The identity is **false** there, as `PROOF.md` Section 9 proves.\n"
    )
    cf = q["laplace_closed_form"]
    lines.append(
        "The Laplace cell additionally has a closed form with an unbounded "
        f"horizon: `Gamma_1 = (c+b)/b = {cf['gain']:.10f}` and "
        f"`{cf['map']}`.  It is interval-certified in "
        "`certificates/certificate.json`.\n"
    )

    lines.append("## 2. Route N -- neutrality control\n")
    lines.append(
        "Corollary G2 says a deterministic stopping rule has gain exactly one "
        "for **every** regular location family and every window length.  This "
        "exercises the score, the window average and the random denominator "
        "against a known answer, and it is the control that a sign or "
        "normalisation error in any family would break.\n"
    )
    worst = max(payload["route_n"]["rows"], key=lambda r: r["z_against_one"])
    lines.append(
        f"All {len(payload['route_n']['rows'])} cells pass "
        f"(`all_pass = {payload['route_n']['all_pass']}`); the largest "
        f"deviation from one is `{worst['family']}`, "
        f"`tau = {worst['deterministic_tau']}`, `m = {worst['m']}`: "
        f"`Gamma = {worst['gamma']:.5f} +- {worst['se']:.5f}`, "
        f"`|z| = {worst['z_against_one']:.2f}`.\n"
    )

    lines.append("## 3. Routes A and B under the frozen detector recursions\n")
    lines.append(
        "Route A evaluates `Gamma = E_0[A_m sum psi(Z_t)]`.  Route B is a "
        "common-random-number central difference of the conditional-mean map "
        "with per-batch Richardson extrapolation; it uses no likelihood, no "
        "score and no change of measure.  The frozen gate is the 3% relative "
        "discrepancy limit inherited from the Track-3 location-family "
        "campaign, with `|z| <= 4` as the secondary criterion.\n"
    )
    for layer in ("reduced", "frozen"):
        rows = [c for c in payload["monte_carlo"]["cells"] if c["layer"] == layer]
        if not rows:
            continue
        detectors = sorted({c["detector"] for c in rows})
        lines.append(f"### 3.{1 if layer == 'reduced' else 2} `{layer}` layer "
                     f"({', '.join(detectors)})\n")
        lines.append(markdown_table(rows, [
            ("detector", lambda r: r["detector"]),
            ("family", lambda r: r["family"]),
            ("class", lambda r: r["family_class"].replace("THEOREM-SUPPORTED", "TS")
                                                 .replace("OUTSIDE-ASSUMPTIONS", "OA")),
            ("m", lambda r: str(r["m"])),
            ("ARL", lambda r: f"{r['arl']['mean']:.1f}"),
            ("Route A", lambda r: f"{r['route_a']['mean']:.4f} ± {r['route_a']['se']:.4f}"),
            ("Route B", lambda r: f"{r['route_b']['mean']:.4f} ± {r['route_b']['se']:.4f}"),
            ("relative", lambda r: f"{r['correspondence']['relative_discrepancy']*100:.3f}%"),
            ("\\|z\\|", lambda r: f"{r['correspondence']['z']:.2f}"),
            ("verdict", lambda r: r["verdict"]),
        ]))
        lines.append("")

    lines.append("## 4. Finite-difference step diagnostic\n")
    lines.append(
        "A central difference is `O(h^2)` accurate.  Route B therefore runs two "
        "steps on the same batches and reports the Richardson combination; this "
        "table adds an independent finer pair on the pre-named cells so the "
        "`O(h^2)` law is checked rather than assumed.\n"
    )
    lines.append(markdown_table(payload["fd_ladder"]["rows"], [
        ("layer", lambda r: r["layer"]),
        ("detector", lambda r: r["detector"]),
        ("family", lambda r: r["family"]),
        ("m", lambda r: str(r["m"])),
        ("coarse step", lambda r: f"{list(r['per_step'].values())[0]['gamma']['mean']:.4f}"),
        ("fine step", lambda r: f"{list(r['per_step'].values())[1]['gamma']['mean']:.4f}"),
        ("Richardson", lambda r: f"{r['richardson']['mean']:.4f} ± {r['richardson']['se']:.4f}"),
    ]))

    lines.append("\n## 5. Consistency with the closed Gaussian gains\n")
    lines.append(
        "Priority 4 re-implements the frozen CUSUM and SR from scratch.  Its "
        "Gaussian cells are therefore an independent check on the closed "
        "Priority-1 and Priority-2 Monte Carlo values.  They are a consistency "
        "check only: Priority 4 does **not** re-derive, replace or update any "
        "frozen number.\n"
    )
    reference = protocol["frozen_reference_values"]
    consistency = []
    for cell in payload["monte_carlo"]["cells"]:
        if cell["layer"] != "frozen" or cell["family"] != "gaussian":
            continue
        key = "cusum_gaussian" if cell["detector_kind"] == "cusum" else "sr_gaussian"
        frozen = reference[key][str(cell["m"])]
        se = cell["route_a"]["se"]
        consistency.append({
            "detector": cell["detector"], "m": cell["m"],
            "frozen": frozen, "p4": cell["route_a"]["mean"], "se": se,
            "z": abs(cell["route_a"]["mean"] - frozen) / se if se > 0 else math.inf,
        })
    lines.append(markdown_table(consistency, [
        ("detector", lambda r: r["detector"]),
        ("m", lambda r: str(r["m"])),
        ("closed P1/P2 gain", lambda r: f"{r['frozen']:.4f}"),
        ("P4 independent Route A", lambda r: f"{r['p4']:.4f} ± {r['se']:.4f}"),
        ("\\|z\\|", lambda r: f"{r['z']:.2f}"),
    ]))

    lines.append("\n## 6. Structural diagnostics\n")
    lines.append(
        "The expected short-window correction `E_0[Q_m]` is the quantity "
        "Priority 1 proves nonnegative for the Gaussian score.  Theorem G3 "
        "shows the pathwise sign is exactly the sign of `T_tau S_tau`, so for "
        "a bounded score it need not be nonnegative.  The `m = 1` column is "
        "structurally zero (the short event is empty).\n"
    )
    short_rows = [c for c in payload["monte_carlo"]["cells"]
                  if c["m"] == 5 and c["family_class"] == "THEOREM-SUPPORTED"]
    lines.append(markdown_table(short_rows, [
        ("layer", lambda r: r["layer"]),
        ("detector", lambda r: r["detector"]),
        ("family", lambda r: r["family"]),
        ("`E[Q_5]`", lambda r: f"{r['short_correction']['mean']:.5f} ± "
                               f"{r['short_correction']['se']:.5f}"),
        ("`E[A_5 S]`", lambda r: f"{r['route_a']['mean']:.4f}"),
        ("`E[B_5 S]`", lambda r: f"{r['fixed_denominator_gain']['mean']:.4f}"),
        ("Gaussian form `E[A_5 T]`", lambda r: f"{r['gaussian_form_gain']['mean']:.4f}"),
    ]))
    lines.append(
        "\nThe last column is what the *Gaussian* formula would report if it "
        "were applied unchanged to a non-Gaussian family.  Where it differs "
        "from `E[A_m S]`, using the closed Gaussian estimand off its model "
        "would give the wrong gain and hence the wrong critical reuse "
        "fraction.\n"
    )

    lines.append("## 7. Origin as a fixed point\n")
    lines.append(
        "Theorem G4 needs an even density and a reflection-equivariant "
        "detector, and then *proves* `E_0[A_m] = 0`.  The numbers below are a "
        "falsification check, not an estimate of something unknown: a "
        "symmetric cell should sit within a few standard errors of zero, and a "
        "family that violates the hypothesis should miss by orders of "
        f"magnitude.  The classifier refuses to classify any cell beyond "
        f"{ORIGIN_FALSIFICATION_Z:g} standard errors.\n"
    )
    fp = [c for c in payload["monte_carlo"]["cells"] if c["m"] == 1
          and c["family_class"] == "THEOREM-SUPPORTED" and c["layer"] == "frozen"]
    lines.append(markdown_table(fp, [
        ("detector", lambda r: r["detector"]),
        ("family", lambda r: r["family"]),
        ("`E_0[A_1]`", lambda r: f"{r['mean_window_at_zero']['mean']:+.5f} ± "
                                 f"{r['mean_window_at_zero']['se']:.5f}"),
        ("\\|z\\|", lambda r: (
            f"{abs(r['mean_window_at_zero']['mean'])/r['mean_window_at_zero']['se']:.1f}"
            if r["mean_window_at_zero"]["se"] > 0 else "n/a")),
    ]))
    (CAMPAIGN / "NUMERICAL_CORRESPONDENCE.md").write_text("\n".join(lines) + "\n")
    print("wrote results/stability_map.json, results/stability_map.csv, "
          "NUMERICAL_CORRESPONDENCE.md")


if __name__ == "__main__":
    main()
