"""Generate D4 figures exclusively from final JSON artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402

from .common import read_json, sha256, write_json
from .config import CAMPAIGN, RESULTS, RHO_SAFE

FIGURES = CAMPAIGN / "figures"
PHASE_INPUT = RESULTS / "phase_map.json"
OPERATIONAL_INPUT = RESULTS / "operational_overlay.json"
DIRECT_INPUT = RESULTS / "direct_validation.json"


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        path,
        dpi=180,
        bbox_inches="tight",
        metadata={"Software": "ReBaseGuard D4"},
    )
    plt.close(fig)


def _interpolated_gamma(phase: dict, m_dense: np.ndarray) -> np.ndarray:
    m = np.asarray([row["m"] for row in phase["gamma_rows"]], dtype=float)
    gamma = np.asarray(
        [row["gamma_tilde"]["mean"] for row in phase["gamma_rows"]], dtype=float
    )
    return np.interp(np.log(m_dense), np.log(m), gamma)


def phase_figure(phase: dict) -> Path:
    m_dense = np.geomspace(min(phase["m_grid"]), max(phase["m_grid"]), 600)
    rho_dense = np.linspace(0.0, 1.0, 500)
    gamma_dense = _interpolated_gamma(phase, m_dense)
    multiplier = rho_dense[:, None] * (1.0 - gamma_dense[None, :])
    stable = (np.abs(multiplier) < 1.0).astype(int)
    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    cmap = ListedColormap(["#c44e52", "#4c72b0"])
    ax.pcolormesh(m_dense, rho_dense, stable, shading="auto", cmap=cmap, vmin=0, vmax=1)
    rho_c = np.divide(
        1.0,
        np.abs(1.0 - gamma_dense),
        out=np.full_like(gamma_dense, np.nan),
        where=np.abs(1.0 - gamma_dense) > 0.0,
    )
    accessible = rho_c <= 1.0
    ax.plot(m_dense[accessible], rho_c[accessible], color="black", lw=2.3,
            label=r"theorem boundary $\rho_c(m)$")
    ax.axhline(1.0, color="#222222", ls="--", lw=1.1, label=r"$\rho=1$")
    ax.axhline(RHO_SAFE, color="#55a868", ls=":", lw=2.0,
               label=f"Stage-C safe rho={RHO_SAFE:.6f}")
    ax.set_xscale("log")
    ax.set_xlim(m_dense.min(), m_dense.max())
    ax.set_ylim(0.0, 1.0)
    ax.set_xlabel("Stopped-window length m")
    ax.set_ylabel("Reuse fraction rho")
    ax.set_title("Local deterministic reference-map stability")
    ax.text(2.1, 0.82, "LOCALLY UNSTABLE", color="white", weight="bold")
    ax.text(95, 0.46, "LOCALLY STABLE", color="white", weight="bold",
            horizontalalignment="center")
    ax.legend(loc="lower right", framealpha=0.95)
    ax.grid(alpha=0.15, which="both")
    path = FIGURES / "d4_local_stability_map.png"
    _save(fig, path)
    return path


def gamma_figure(phase: dict) -> Path:
    m = np.asarray([row["m"] for row in phase["gamma_rows"]], dtype=float)
    gamma = np.asarray([row["gamma_tilde"]["mean"] for row in phase["gamma_rows"]])
    gamma_lo = np.asarray([row["gamma_tilde"]["ci95"][0] for row in phase["gamma_rows"]])
    gamma_hi = np.asarray([row["gamma_tilde"]["ci95"][1] for row in phase["gamma_rows"]])
    rho_c = np.asarray([
        np.nan if row["rho_c_unconstrained"] is None else row["rho_c_unconstrained"]
        for row in phase["boundary_rows"]
    ])
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.5))
    axes[0].fill_between(m, gamma_lo, gamma_hi, color="#4c72b0", alpha=0.22,
                         label="95% batch CI")
    axes[0].plot(m, gamma, "o-", color="#4c72b0", label="GammaTilde_m")
    axes[0].axhline(2.0, color="black", ls="--", label="GammaTilde_m=2")
    axes[0].set_xscale("log")
    axes[0].set_xlabel("m")
    axes[0].set_ylabel("GammaTilde_m")
    axes[0].set_title("Exact Stage-D convention-A gain")
    axes[0].legend()
    axes[0].grid(alpha=0.2, which="both")

    axes[1].plot(m, rho_c, "o-", color="#8172b2", label="unconstrained rho_c")
    axes[1].axhline(1.0, color="black", ls="--", label="full reuse")
    axes[1].axhline(RHO_SAFE, color="#55a868", ls=":", lw=2,
                    label="Stage-C safe rho")
    axes[1].set_xscale("log")
    axes[1].set_xlabel("m")
    axes[1].set_ylabel("rho_c(m)")
    axes[1].set_ylim(0.0, max(2.2, float(np.nanmax(rho_c)) * 1.05))
    axes[1].set_title("Theorem-derived critical reuse")
    axes[1].legend()
    axes[1].grid(alpha=0.2, which="both")
    fig.suptitle("D4 gain and local stability boundary")
    path = FIGURES / "d4_gamma_and_boundary.png"
    _save(fig, path)
    return path


def operational_figure(operational: dict) -> Path:
    rows = operational["rows"]
    labels = [f"m={row['m']}\nrho={row['rho']:.1f}" for row in rows]
    colors = [
        "#4c72b0" if row["theorem_class"] == "LOCALLY-STABLE" else "#c44e52"
        for row in rows
    ]
    definitions = (
        ("cycle_arl", "Cycle ARL"),
        ("reference_mse", "Reference MSE"),
        ("reference_acf1", "Reference ACF1"),
        ("direction_acf1", "Alarm-direction ACF1"),
    )
    x = np.arange(len(rows))
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.0), sharex=True)
    for ax, (metric, title) in zip(axes.flat, definitions):
        means = np.asarray([row["metrics"][metric]["mean"] for row in rows])
        ses = np.asarray([row["metrics"][metric]["se"] for row in rows])
        ax.bar(x, means, color=colors, alpha=0.9)
        ax.errorbar(x, means, yerr=1.959963984540054 * ses, fmt="none",
                    ecolor="black", capsize=3, lw=1)
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.2)
    for ax in axes[1]:
        ax.set_xticks(x, labels)
    fig.suptitle("Operational consequence overlay (not a transition test)")
    path = FIGURES / "d4_operational_overlay.png"
    _save(fig, path)
    return path


def build() -> dict:
    phase = read_json(PHASE_INPUT)
    operational = read_json(OPERATIONAL_INPUT)
    direct = read_json(DIRECT_INPUT)
    if not phase["valid"] or not operational["valid"] or not direct["valid"]:
        raise RuntimeError("final numerical JSON must be valid before figures")
    paths = [phase_figure(phase), gamma_figure(phase), operational_figure(operational)]
    index = {
        "schema": "rebaseguard.d4-figure-index.v1",
        "source_policy": "figures generated from final JSON only",
        "inputs": {
            str(PHASE_INPUT.relative_to(CAMPAIGN)): sha256(PHASE_INPUT),
            str(OPERATIONAL_INPUT.relative_to(CAMPAIGN)): sha256(OPERATIONAL_INPUT),
            str(DIRECT_INPUT.relative_to(CAMPAIGN)): sha256(DIRECT_INPUT),
        },
        "figures": {
            str(path.relative_to(CAMPAIGN)): sha256(path) for path in paths
        },
        "valid": True,
    }
    write_json(FIGURES / "figure_index.json", index)
    return index


if __name__ == "__main__":
    sys.exit(0 if build()["valid"] else 1)
