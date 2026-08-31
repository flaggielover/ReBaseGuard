"""Publication figures, generated only from the final Priority-3 JSON.

Two rules are enforced mechanically rather than by convention:

* every plotted cell must reproduce a stored machine-readable record, and
* ``m`` is drawn as a discrete categorical axis, because ``GammaTilde_m`` is
  known only at the four supported window lengths.  ``rho`` is the only
  continuously varying axis, and it is the only one filled continuously.
"""

from __future__ import annotations

from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from .classifier import classify
from .common import read_json, sha256, write_json
from .config import BOUNDARY_TOLERANCE, FIGURES, M_GRID, RESULTS, RHO_GRID

ATTRACT = "#4c72b0"
REPEL = "#c44e52"
UNCERTAIN = "#dd8452"
CERTIFIED = "#55a868"
BOUNDARY_LINE = "#101010"

DENSE_RHO = 1201


def _save(fig: plt.Figure, name: str) -> str:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / name
    fig.savefig(path, dpi=200, bbox_inches="tight",
                metadata={"Software": "ReBaseGuard Level-4 Priority 3"})
    plt.close(fig)
    return f"figures/{name}"


def _rows(payload: dict[str, Any], layer_id: str) -> dict[int, dict[str, Any]]:
    return {row["m"]: row for row in payload["boundary_rows"]
            if row["layer"] == layer_id}


def _traceability(payload: dict[str, Any]) -> dict[str, Any]:
    """Every grid cell drawn must equal the stored classification."""
    mismatches = []
    for cell in payload["cells"]:
        recomputed = classify(cell["rho"], cell["gamma_tilde"], BOUNDARY_TOLERANCE)
        if recomputed != cell["class"]:
            mismatches.append({"layer": cell["layer"], "m": cell["m"],
                               "rho": cell["rho"], "stored": cell["class"],
                               "recomputed": recomputed})
    return {"checked_cells": len(payload["cells"]),
            "mismatches": mismatches,
            "every_plotted_cell_traceable": not mismatches}


def _fill_panel(ax, payload, layer, rho_lo, rho_hi, annotate):
    rows = _rows(payload, layer["id"])
    certified = layer["gamma_evidence_class"] == "EXACT_SYMBOLIC"
    rho_dense = np.linspace(rho_lo, rho_hi, DENSE_RHO)
    half = 0.42
    for index, m in enumerate(M_GRID):
        row = rows[m]
        magnitude = np.abs(rho_dense * (1.0 - row["gamma_tilde"]))
        ax.imshow(
            np.where(magnitude < 1.0, 0, 1).reshape(-1, 1),
            extent=(index - half, index + half, rho_lo, rho_hi),
            origin="lower", aspect="auto", interpolation="nearest",
            cmap=matplotlib.colors.ListedColormap([ATTRACT, REPEL]),
            vmin=0, vmax=1,
        )
        band = row["uncertainty_band"]
        if band and band.get("bounded"):
            lo, hi = max(rho_lo, band["rho_lo"]), min(rho_hi, band["rho_hi"])
            if hi > lo:
                ax.fill_between([index - half, index + half], lo, hi,
                                color=UNCERTAIN, alpha=1.0, lw=0.7,
                                edgecolor=UNCERTAIN)
        rho_c = row["rho_crit"]
        if rho_c is not None and rho_lo <= rho_c <= rho_hi:
            ax.plot([index - half, index + half], [rho_c, rho_c],
                    color=BOUNDARY_LINE, lw=1.8, solid_capstyle="butt")
        if annotate and rho_c is not None:
            text = (f"${row['rho_crit_exact']}$" if certified
                    else f"{rho_c:.4f}")
            ax.annotate(text, (index, 1.012), xycoords=("data", "axes fraction"),
                        ha="center", va="bottom", fontsize=8.5,
                        color=BOUNDARY_LINE)
    ax.set_xticks(range(len(M_GRID)))
    ax.set_xticklabels([str(m) for m in M_GRID])
    ax.set_xlim(-0.5, len(M_GRID) - 0.5)
    ax.set_ylim(rho_lo, rho_hi)


def stability_map_figure(payload: dict[str, Any]) -> str:
    layers = payload["layers"]
    fig, axes = plt.subplots(2, len(layers), figsize=(4.0 * len(layers), 8.6))

    for column, layer in enumerate(layers):
        rows = _rows(payload, layer["id"])
        _fill_panel(axes[0][column], payload, layer, 0.0, 1.0, annotate=False)
        badge = ("exact gain, interval-certified"
                 if layer["gamma_evidence_class"] == "EXACT_SYMBOLIC"
                 else "Monte Carlo gain, theorem-supported")
        axes[0][column].set_title(f"{layer['detector_short']}\n{badge}",
                                  fontsize=10.5)

        criticals = [rows[m]["rho_crit"] for m in M_GRID
                     if rows[m]["rho_crit"] is not None]
        span = max(criticals) - min(criticals)
        pad = max(0.25 * span, 0.02 * max(criticals))
        lo = max(0.0, min(criticals) - pad)
        hi = min(1.0, max(criticals) + pad)
        _fill_panel(axes[1][column], payload, layer, lo, hi, annotate=True)
        axes[1][column].set_xlabel("window length $m$ (discrete)")

    axes[0][0].set_ylabel(r"reuse fraction $\rho$ over the whole domain $[0,1]$")
    axes[1][0].set_ylabel(r"$\rho$, zoomed on the boundary")
    for column in range(1, len(layers)):
        axes[0][column].set_yticklabels([])

    handles = [
        Patch(color=ATTRACT, label=r"locally attracting  $|\lambda|<1$"),
        Patch(color=REPEL, label=r"locally repelling  $|\lambda|>1$"),
        Line2D([0], [0], color=BOUNDARY_LINE, lw=1.8,
               label=r"first-order boundary  $|\lambda|=1$"),
        Patch(color=UNCERTAIN,
              label="95% gain interval permits either class"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False,
               bbox_to_anchor=(0.5, 0.008), fontsize=10)
    fig.suptitle(
        "Level-4 Priority 3: local stability of the reference fixed point "
        r"under $\lambda_{D,m}(\rho)=\rho\,(1-\widetilde\Gamma_{D,m})$",
        fontsize=13, y=0.985,
    )
    fig.text(0.5, 0.487,
             "lower row: same map zoomed on each detector's own boundary; "
             r"numbers above each column are $\rho_c$",
             ha="center", fontsize=9, color="#444444")
    fig.text(0.5, 0.062,
             "Columns are separate window lengths and no gain is interpolated "
             r"between them. Only $\rho$ varies continuously.",
             ha="center", fontsize=9, color="#444444")
    fig.subplots_adjust(hspace=0.44, wspace=0.30, top=0.90, bottom=0.14)
    return _save(fig, "p3_cross_detector_stability_map.png")


def boundary_figure(payload: dict[str, Any]) -> str:
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    styles = {
        "GAUSSIAN_CUSUM_FROZEN": ("o", ATTRACT, "CUSUM (empirical gain)"),
        "GAUSSIAN_SR_FROZEN": ("s", REPEL, "SR (empirical gain)"),
        "FINITE_SUPPORT_CUSUM_WITNESS": ("^", CERTIFIED,
                                         "CUSUM witness (certified)"),
        "FINITE_SUPPORT_SR_WITNESS": ("v", "#8172b2",
                                      "SR witness (certified)"),
    }
    positions = {m: i for i, m in enumerate(M_GRID)}
    for layer in payload["layers"]:
        rows = _rows(payload, layer["id"])
        marker, color, label = styles[layer["id"]]
        x = [positions[m] for m in M_GRID]
        y = [rows[m]["rho_crit"] for m in M_GRID]
        err = None
        interval = [rows[m]["rho_crit_interval"] for m in M_GRID]
        if all(item is not None for item in interval):
            lower = [y[i] - interval[i][0] for i in range(len(y))]
            upper = [interval[i][1] - y[i] for i in range(len(y))]
            err = np.array([lower, upper])
        ax.errorbar(x, y, yerr=err, fmt=marker, color=color, label=label,
                    capsize=3.5, lw=1.6, ms=6.5)
    ax.set_yscale("log")
    ax.set_xticks(list(positions.values()))
    ax.set_xticklabels([str(m) for m in M_GRID])
    ax.set_xlabel("window length $m$ (discrete)")
    ax.set_ylabel(r"critical reuse fraction $\rho_c=1/(\widetilde\Gamma-1)$")
    ax.axhline(1.0, color="#222222", ls="--", lw=1.1,
               label=r"$\rho=1$ (full reuse)")
    ax.set_title("Theorem-derived critical reuse fraction by detector family")
    ax.grid(alpha=0.2, which="both")
    ax.legend(loc="center left", fontsize=9, framealpha=0.95)
    fig.text(0.5, -0.02,
             "Error bars are 95% intervals transformed from the recorded batch "
             "standard errors; certified rows are exact rationals and carry none.",
             ha="center", fontsize=8.5, color="#444444")
    return _save(fig, "p3_critical_reuse_by_detector.png")


def evidence_figure(payload: dict[str, Any]) -> str:
    layers = payload["layers"]
    labels, matrix, texture = [], [], []
    codes = {"LOCALLY-STABLE": 0, "LOCALLY-UNSTABLE": 1, "BOUNDARY": 2}
    for layer in layers:
        for m in M_GRID:
            labels.append(f"{layer['detector_short']}  m={m}")
            row, tex = [], []
            for rho in RHO_GRID:
                cell = next(c for c in payload["cells"]
                            if c["layer"] == layer["id"] and c["m"] == m
                            and c["rho"] == rho)
                row.append(codes[cell["class"]])
                tex.append(not cell["classification_reportable_as_robust"])
            matrix.append(row)
            texture.append(tex)
    grid = np.asarray(matrix)
    marks = np.asarray(texture)

    fig, ax = plt.subplots(figsize=(11.4, 6.6))
    cmap = matplotlib.colors.ListedColormap([ATTRACT, REPEL, BOUNDARY_LINE])
    ax.imshow(grid, cmap=cmap, vmin=0, vmax=2, aspect="auto",
              interpolation="nearest")
    ys, xs = np.nonzero(marks)
    ax.scatter(xs, ys, marker="x", s=42, color=UNCERTAIN, lw=1.8,
               label="not reportable as robust")
    ax.set_xticks(range(len(RHO_GRID)))
    ax.set_xticklabels([f"{r:g}" for r in RHO_GRID], rotation=90, fontsize=8.5)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8.5)
    for edge in range(len(M_GRID), len(labels), len(M_GRID)):
        ax.axhline(edge - 0.5, color="white", lw=2.2)
    ax.set_xlabel(r"reuse fraction $\rho$ on the candidate-declared fixed grid")
    ax.set_title("Priority-3 evidence grid: one square per machine-readable cell")
    handles = [
        Patch(color=ATTRACT, label="locally attracting"),
        Patch(color=REPEL, label="locally repelling"),
        Patch(color=BOUNDARY_LINE, label="first-order boundary (inconclusive)"),
        Line2D([0], [0], marker="x", color=UNCERTAIN, lw=0, ms=8,
               label="95% interval crosses $|\\lambda|=1$"),
    ]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.01, 1.0),
              fontsize=9, frameon=False)
    fig.text(0.5, -0.03,
             "Top two blocks use empirical Gaussian gains; bottom two use "
             "exact finite-support witness gains.",
             ha="center", fontsize=8.5, color="#444444")
    return _save(fig, "p3_evidence_grid.png")


def build() -> dict[str, Any]:
    payload = read_json(RESULTS / "stability_map.json")
    if not payload["valid"]:
        raise RuntimeError("refusing to plot an invalid stability map")
    trace = _traceability(payload)
    if not trace["every_plotted_cell_traceable"]:
        raise RuntimeError(f"untraceable plotted cells: {trace['mismatches']}")

    produced = [
        stability_map_figure(payload),
        boundary_figure(payload),
        evidence_figure(payload),
    ]
    index = {
        "schema": "rebaseguard.p3-figure-index.v1",
        "source_policy": "figures generated from final Priority-3 JSON only",
        "inputs": {
            "results/stability_map.json": sha256(RESULTS / "stability_map.json"),
            "results/provenance.json": sha256(RESULTS / "provenance.json"),
        },
        "figures": {name: sha256(FIGURES.parent / name) for name in produced},
        "traceability": trace,
        "m_axis": "discrete categorical; GammaTilde is never interpolated across m",
        "rho_axis": "continuous on the admissible domain [0,1]",
        "valid": True,
    }
    write_json(FIGURES / "figure_index.json", index)
    return index
