#!/usr/bin/env python3
"""Figures for Priority 4.

Three panels, each of which is a claim the campaign is willing to defend:
the correspondence between the two Monte Carlo routes, the gain and critical
reuse fraction across families, and the sign of the short-window correction.
Cells that the campaign refuses to classify are drawn as refused, not omitted.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

CAMPAIGN = Path(__file__).resolve().parents[1]
FIGURES = CAMPAIGN / "figures"
SUPPORTED = ("gaussian", "laplace", "logistic", "t3", "t1p5", "skewnormal4")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def figure_correspondence(cells: list[dict], path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    for ax, layer in zip(axes, ("reduced", "frozen")):
        rows = [c for c in cells if c["layer"] == layer
                and c["family_class"] == "THEOREM-SUPPORTED"]
        for detector, marker in (("cusum", "o"), ("sr", "s")):
            sub = [r for r in rows if r["detector_kind"] == detector]
            ax.errorbar(
                [r["route_a"]["mean"] for r in sub],
                [r["route_b"]["mean"] for r in sub],
                xerr=[r["route_a"]["se"] for r in sub],
                yerr=[r["route_b"]["se"] for r in sub],
                fmt=marker, ms=5, lw=0.9, alpha=0.85, label=detector.upper(),
            )
        lo = min([r["route_a"]["mean"] for r in rows] +
                 [r["route_b"]["mean"] for r in rows]) * 0.9
        hi = max([r["route_a"]["mean"] for r in rows] +
                 [r["route_b"]["mean"] for r in rows]) * 1.05
        ax.plot([lo, hi], [lo, hi], "k--", lw=0.8, label="identity")
        ax.set_xlabel(r"Route A:  $\Gamma = E_0[A_m \sum \psi(Z_t)]$")
        ax.set_ylabel(r"Route B:  $-g_m'(0)$  (CRN, Richardson)")
        ax.set_title(f"{layer} operating point")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.25)
    fig.suptitle("Score route against direct-map route, all theorem-supported cells")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def figure_gain_and_boundary(rows: list[dict], path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))
    frozen = [r for r in rows if r["layer"] == "frozen"]
    m_grid = sorted({r["m"] for r in frozen})
    width = 0.8 / max(len(SUPPORTED), 1)
    for ax, detector in zip(axes, ("cusum@5", "sr@520.886")):
        for i, family in enumerate(SUPPORTED):
            sub = sorted([r for r in frozen if r["family"] == family
                          and r["detector"] == detector], key=lambda r: r["m"])
            if not sub:
                continue
            xs = np.arange(len(m_grid)) + i * width - 0.4 + width / 2
            classified = [r["stability_status"] == "CLASSIFIED" for r in sub]
            bars = ax.bar(xs, [r["gamma"] for r in sub], width=width * 0.95,
                          yerr=[1.96 * r["gamma_se"] for r in sub],
                          label=family, alpha=0.9, capsize=2)
            for bar, ok in zip(bars, classified):
                if not ok:
                    bar.set_hatch("//")
                    bar.set_edgecolor("black")
        ax.axhline(1.0, color="k", lw=1.0, ls=":")
        ax.axhline(2.0, color="k", lw=0.8, ls="--")
        ax.set_xticks(np.arange(len(m_grid)))
        ax.set_xticklabels([f"m={m}" for m in m_grid])
        ax.set_ylabel(r"$\Gamma_{D,m,f}$")
        ax.set_title(detector)
        ax.grid(alpha=0.25, axis="y")
    axes[0].legend(fontsize=7, ncol=2)
    fig.suptitle(
        "Generalized gain at the frozen operating points.  Dotted line: neutral "
        "gain 1 (Corollary G2).  Dashed: gain 2, where the boundary reaches full "
        "reuse.  Hatched bars are cells the campaign refuses to classify "
        "(origin is not a fixed point)."
    )
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def figure_short_correction(rows: list[dict], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    frozen = [r for r in rows if r["layer"] == "frozen" and r["m"] == 5
              and r["family"] in SUPPORTED]
    labels, values, errors, colours = [], [], [], []
    for row in sorted(frozen, key=lambda r: (r["detector"], r["family"])):
        labels.append(f"{row['family']}\n{row['detector']}")
        values.append(row["expected_short_correction"])
        errors.append(1.96 * row["expected_short_correction_se"])
        colours.append("tab:blue" if row["family"] == "gaussian" else "tab:orange")
    ax.bar(range(len(values)), values, yerr=errors, color=colours, capsize=3)
    ax.axhline(0.0, color="k", lw=1.0)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=7, rotation=45, ha="right")
    ax.set_ylabel(r"$E_0[Q_5]$")
    ax.set_title(
        "Expected short-window correction at m=5.  Priority 1 proves this is "
        "nonnegative pathwise for the Gaussian score; Theorem G3 shows the sign "
        "is that of $T_\\tau S_\\tau$ in general."
    )
    ax.grid(alpha=0.25, axis="y")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    FIGURES.mkdir(exist_ok=True)
    corr = json.loads((CAMPAIGN / "results" / "correspondence.json").read_text())
    mapping = json.loads((CAMPAIGN / "results" / "stability_map.json").read_text())
    outputs = {
        "p4_route_correspondence.png":
            lambda p: figure_correspondence(corr["monte_carlo"]["cells"], p),
        "p4_generalized_gain.png":
            lambda p: figure_gain_and_boundary(mapping["rows"], p),
        "p4_short_window_correction.png":
            lambda p: figure_short_correction(mapping["rows"], p),
    }
    index = {}
    for name, builder in outputs.items():
        target = FIGURES / name
        builder(target)
        index[name] = {"sha256": sha256(target), "bytes": target.stat().st_size}
    (FIGURES / "figure_index.json").write_text(json.dumps(index, indent=2) + "\n")
    print(json.dumps(index, indent=2))


if __name__ == "__main__":
    main()
