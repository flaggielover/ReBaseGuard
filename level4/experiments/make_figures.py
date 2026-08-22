#!/usr/bin/env python
"""Regenerate every Level 4 figure from saved result files.

No figure in this project is produced or edited by hand.  This script takes the
campaign directory (Gate 4.1) and the findings JSON (Gate 4.2) and writes the
full figure set, together with a JSON index recording which result file each
figure was drawn from.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rebaseguard_level4 import analysis, figures, storage  # noqa: E402
from rebaseguard_level4.campaigns import RESULTS  # noqa: E402

FIGURES = Path(__file__).resolve().parents[1] / "figures"
LAGS = (1, 2, 3, 4, 5, 6, 7, 8)


def load_headline(campaign_dir: Path) -> list[dict]:
    return json.loads((campaign_dir / "campaign.summary.json").read_text())["headline"]


def load_cell_summary(campaign_dir: Path, cell_id: str) -> dict:
    return json.loads((campaign_dir / f"{cell_id}.summary.json").read_text())


def acf_curve(summary: dict, prefix: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    lags, point, err = [], [], []
    for lag in LAGS:
        est = summary["estimates"].get(f"{prefix}_lag{lag}")
        if est is None:
            continue
        lags.append(lag)
        point.append(est["point"])
        err.append(max(est["point"] - est["ci_low"], est["ci_high"] - est["point"]))
    return np.array(lags), np.array(point), np.array(err)


def gate41_figures(campaign_dir: Path, index: dict, tag: str = "") -> None:
    headline = load_headline(campaign_dir)
    ms = sorted({row["m"] for row in headline})
    focus_m = 1 if 1 in ms else ms[0]

    def cell(rho: float, m: int = focus_m) -> dict | None:
        for row in headline:
            if row["m"] == m and abs(row["rho"] - rho) < 1e-12:
                return row
        return None

    # Fig 1 — trajectories
    trajectories = {}
    raw_dir = RESULTS / "raw" / campaign_dir.name
    for rho, label in ((0.0, r"fresh  ($\rho=0$)"),
                       (0.05, r"$\rho=0.05$  (below $\rho_c$)"),
                       (0.1, r"$\rho=0.1$  (above $\rho_c$)"),
                       (1.0, r"full reuse  ($\rho=1$)")):
        path = raw_dir / f"cycles_m{focus_m}_rho{rho:g}.parquet"
        if not path.exists():
            continue
        data = storage.read_parquet(path)
        keep = (data["replicate"] == 0) & (~data["in_burn_in"].astype(bool))
        trajectories[label] = data["e_next"][keep]
    if trajectories:
        p = figures.fig_trajectories(trajectories, FIGURES / f"fig01_trajectories{tag}.png")
        index[p.name] = {"source": str(raw_dir), "replicate": 0, "m": focus_m}

    # Fig 2 — fresh vs reuse distributions
    samples = {}
    for rho, label in ((0.0, r"fresh ($\rho=0$)"),
                       (0.05, r"$\rho=0.05$"),
                       (0.25, r"$\rho=0.25$"),
                       (1.0, r"full reuse ($\rho=1$)")):
        path = raw_dir / f"cycles_m{focus_m}_rho{rho:g}.parquet"
        if not path.exists():
            continue
        data = storage.read_parquet(path)
        keep = ~data["in_burn_in"].astype(bool)
        samples[label] = data["e_next"][keep]
    if samples:
        p = figures.fig_reference_distributions(
            samples, FIGURES / f"fig02_reference_distributions{tag}.png")
        index[p.name] = {"source": str(raw_dir), "m": focus_m}

    # Fig 3 — alarm alternation
    p = figures.fig_metric_vs_rho(
        headline, "alternation_rate", r"$P(A_{j+1}\neq A_j)$",
        FIGURES / f"fig03_alarm_alternation{tag}.png",
        title="Alarm-direction alternation against reuse fraction",
        reference=0.5, reference_label="independent alarms (0.5)")
    index[p.name] = {"source": str(campaign_dir / "campaign.summary.json")}

    # Fig 4 — ACF
    curves_e, curves_d = {}, {}
    for rho, label in ((0.0, r"fresh ($\rho=0$)"), (0.25, r"$\rho=0.25$"),
                       (1.0, r"full reuse ($\rho=1$)")):
        row = cell(rho)
        if row is None:
            continue
        summary = load_cell_summary(campaign_dir, row["cell_id"])
        curves_e[label] = acf_curve(summary, "acf_e")
        curves_d[label] = acf_curve(summary, "acf_direction")
    if curves_e:
        p = figures.fig_acf(curves_e, FIGURES / f"fig04a_acf_reference_error{tag}.png",
                            title=r"Lagged autocorrelation of the reference error $E_j$",
                            ylabel=r"ACF of $E_j$")
        index[p.name] = {"source": str(campaign_dir)}
        p = figures.fig_acf(curves_d, FIGURES / f"fig04b_acf_alarm_direction{tag}.png",
                            title="Lagged autocorrelation of the alarm direction",
                            ylabel="ACF of alarm direction")
        index[p.name] = {"source": str(campaign_dir)}

    # Fig 5 — cycle ARL against rho
    p = figures.fig_metric_vs_rho(
        headline, "cycle_arl", "cycle ARL (mean stopping time)",
        FIGURES / f"fig05_cycle_arl{tag}.png",
        title=r"In-control cycle ARL against reuse fraction",
        reference=465.0, reference_label=r"oracle $ARL_0\approx465$ ($e\equiv0$)")
    index[p.name] = {"source": str(campaign_dir / "campaign.summary.json")}

    p = figures.fig_metric_vs_rho(
        headline, "sd_reference_error", r"$\mathrm{sd}(E_j)$",
        FIGURES / f"fig05b_reference_dispersion{tag}.png",
        title="Stationary reference-error dispersion against reuse fraction")
    index[p.name] = {"source": str(campaign_dir / "campaign.summary.json")}


def gate42_figures(findings: dict, index: dict) -> None:
    rho_values = [row["rho"] for row in findings["rho_transition"]["rows"]]
    coarse = findings["coarse_map"]["result"]["records"]
    near = findings["near_zero"]["result"]["records"]

    shown = [r for r in rho_values if r in (0.05, 0.1, 0.25, 0.5, 1.0)]
    p = figures.fig_conditional_map(
        coarse, FIGURES / "fig06_conditional_map.png", rho_values=shown,
        title=r"Conditional map $F_\rho(e)$ with the lines $y=e$ and $y=-e$")
    index[p.name] = {"source": findings["coarse_map"]["experiment_id"]}

    roots = [entry["refined"] for entry in findings["h_roots"]
             if entry.get("refined") and entry["rho"] == 1.0]
    p = figures.fig_h_function(
        coarse, FIGURES / "fig07_h_function.png", rho_values=shown, roots=roots,
        title=r"$H_\rho(e)=F_\rho(e)+e$; nonzero zeros are period-2 candidates")
    index[p.name] = {"source": findings["coarse_map"]["experiment_id"]}

    e = np.array([r["e"] for r in coarse])
    f = np.array([r["F_rho_1"] for r in coarse])
    s = np.array([r["F_rho_1_se"] for r in coarse])
    order = np.argsort(e)
    deriv = analysis.local_derivative(e[order], f[order], s[order], half_window=3)
    p = figures.fig_derivative(
        deriv["e"], deriv["derivative"], deriv["derivative_se"],
        FIGURES / "fig08_numerical_derivative.png",
        title=r"Numerical derivative $F'_{\rho=1}(e)$",
        marks={r"$1-\Gamma$ (score route)":
               findings["derivative_correspondence"]["score_change_of_measure"]["F1_prime_0"]})
    index[p.name] = {"source": findings["coarse_map"]["experiment_id"]}

    rows = findings["rho_transition"]["rows"]
    crit = findings["rho_transition"]["rho_c_from_direct"]
    cert = findings["rho_transition"]["rho_c_certified_enclosure"]["rho_c_enclosure"]
    p = figures.fig_stability_diagram(
        np.array([r["rho"] for r in rows]),
        np.array([r["F_rho_prime_0"] for r in rows]),
        np.array([r["F_rho_prime_0_se"] for r in rows]),
        FIGURES / "fig09_stability_diagram.png",
        rho_c=crit["rho_c"], rho_c_ci=tuple(crit["rho_c_ci95"]),
        certified_band=(cert[0], cert[1]))
    index[p.name] = {"source": findings["near_zero"]["experiment_id"]}

    corr = findings["derivative_correspondence"]
    fit = findings["near_zero"]["odd_polynomial_fit"]
    p = figures.fig_delta_scan(
        findings["near_zero"]["central_difference_scan"],
        FIGURES / "fig10_finite_difference_truncation.png",
        reference=corr["score_change_of_measure"]["F1_prime_0"],
        reference_se=corr["score_change_of_measure"]["se"],
        fitted=fit["derivative_at_zero"],
        fitted_se=fit["derivative_at_zero_se"])
    index[p.name] = {"source": findings["near_zero"]["experiment_id"]}

    p = figures.fig_conditional_map(
        near, FIGURES / "fig11_conditional_map_near_zero.png", rho_values=shown,
        title=r"Conditional map near $e=0$ (dense grid)")
    index[p.name] = {"source": findings["near_zero"]["experiment_id"]}


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    FIGURES.mkdir(parents=True, exist_ok=True)
    index: dict[str, dict] = {}
    for arg in argv[1:]:
        path = Path(arg)
        if path.is_dir():
            tag = "" if "full-" in path.name else f"_{path.name.split('-')[1]}"
            if "mgrid" in path.name:
                tag = "_mgrid"
            gate41_figures(path, index, tag=tag)
            print(f"Gate 4.1 figures from {path.name}")
        else:
            findings = json.loads(path.read_text())
            gate42_figures(findings, index)
            print(f"Gate 4.2 figures from {path.name}")
    storage.write_json(index, FIGURES / "figure_index.json")
    print(f"\n{len(index)} figures written to {FIGURES}")
    for name in sorted(index):
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
