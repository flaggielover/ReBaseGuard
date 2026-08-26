#!/usr/bin/env python3
"""Generate publication-facing ReBaseGuard figures from frozen evidence only.

This script performs presentation-only transformations. It imports no simulator,
downloads no data, and never writes into a scientific or historical namespace.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "figures" / "final"

INK = "#18212b"
MUTED = "#5d6975"
GRID = "#d8dee5"
BLUE = "#2f6690"
BLUE_LIGHT = "#d9e8f2"
GOLD = "#d39b2a"
GOLD_LIGHT = "#f5ead0"
ORANGE = "#c9662d"
PINK = "#a7556d"
OLIVE = "#738446"
PAPER = "#ffffff"
SOFT = "#f5f7f9"


FIGURES = [
    {
        "id": "Figure 1",
        "slug": "figure01_recursive_rebaselining",
        "title": "Stopping-selected recursive re-baselining",
        "purpose": "Define the cross-cycle feedback mechanism.",
        "sources": [
            "docs/research_synthesis/MAIN_THEOREM_ARCHITECTURE.md",
            "docs/research_synthesis/DEFINITIONS_AND_NOTATION.md",
        ],
        "transformation": "Explanatory vector diagram from the frozen synthesis narrative; no quantitative values.",
        "evidence": "INTERPRETATION / CONCEPTUAL DIAGRAM",
        "paper_section": "Sections 1–3",
        "limitation": "Diagram defines the mechanism; it is not empirical or proof evidence.",
    },
    {
        "id": "Figure 2",
        "slug": "figure02_derivative_instability",
        "title": "Stopped-selection derivative and local instability",
        "purpose": "Separate the Lean-checked derivative spine from the Arb-certified gain enclosure.",
        "sources": [
            "rebaseguard-proof/proofs/certificate.json",
            "docs/research_synthesis/MAIN_THEOREM_ARCHITECTURE.md",
        ],
        "transformation": "Exact interval transformation F'_1(0)=1-Gamma_CUSUM and evidence-flow diagram.",
        "evidence": "LEAN-CHECKED + ARB-CERTIFIED + HUMAN THEOREM BRIDGE",
        "paper_section": "Sections 4–5",
        "limitation": "Local deterministic fixed-point conclusion only; Lean does not certify the Gamma value.",
    },
    {
        "id": "Figure 3",
        "slug": "figure03_period2_skeleton",
        "title": "Certified period-two orbit of the deterministic skeleton",
        "purpose": "Show the rigorously certified symmetric deterministic orbit and multiplier.",
        "sources": ["level4/stage_b/certificate/period2_certificate.json"],
        "transformation": "Direct diagram of the certified root and multiplier intervals.",
        "evidence": "RIGOROUS NUMERICAL CERTIFICATE",
        "paper_section": "Section 5",
        "limitation": "No stochastic-chain period-two or invariant-law claim.",
    },
    {
        "id": "Figure 4",
        "slug": "figure04_m_rho_stability",
        "title": "Finite-window local-stability map",
        "purpose": "Show the D4 deterministic local boundary rho_c(m).",
        "sources": ["level4/closure_proofs/d4_phase_map/results/decision.json"],
        "transformation": "Log-m interpolation between frozen D4 grid values for display; plotted grid points remain visible.",
        "evidence": "HUMAN THEOREM CONSEQUENCE + CONFIRMATORY NUMERICAL",
        "paper_section": "Section 6",
        "limitation": "Mathematical deterministic local-stability boundary, not an observed operational phase transition.",
    },
    {
        "id": "Figure 5",
        "slug": "figure05_p3_policy",
        "title": "Frozen stability-aware P3 reuse policy",
        "purpose": "Compare P0, P1, fixed P2, and uncertainty-aware P3 at four frozen regimes.",
        "sources": ["level4/closure_proofs/l4r06_policy/results/scientific_findings.json"],
        "transformation": "Direct plot of frozen policy actions and lower-95%-boundary allowances.",
        "evidence": "METHOD DEFINITION + CONFIRMATORY NUMERICAL",
        "paper_section": "Section 7",
        "limitation": "P3 is scoped and not universally optimal; m=100 saturates at P1.",
    },
    {
        "id": "Figure 6",
        "slug": "figure06_policy_consequences",
        "title": "Reference-state and monitoring consequences",
        "purpose": "Show frozen reference-MSE and false-alert-burden improvements in active regimes.",
        "sources": ["level4/closure_proofs/l4r06_policy/results/scientific_findings.json"],
        "transformation": "Direct point and simultaneous lower-95%-bound display for H6-2 and H6-3.",
        "evidence": "CONFIRMATORY NUMERICAL",
        "paper_section": "Section 7",
        "limitation": "P2 has descriptive advantages at m=70 and m=100; P3=P1 at m=100; two secondary epsilon=0.05 conditions fail.",
    },
    {
        "id": "Figure 7",
        "slug": "figure07_external_validation",
        "title": "Semi-real external-validation synthesis",
        "purpose": "Retain every Stage E, V2, and V3 task while showing the non-pooled closure count.",
        "sources": [
            "level4/closure_proofs/external_validation_v3/CROSS_CAMPAIGN_AGGREGATION.md",
            "level4/closure_proofs/external_validation_v3/results/decision.json",
        ],
        "transformation": "Parse the frozen task table and render a task matrix plus campaign support counts.",
        "evidence": "SEMI-REAL EMPIRICAL",
        "paper_section": "Section 9",
        "limitation": "No pooled samples, production deployment, universal safety, or detector-independence claim.",
    },
    {
        "id": "Figure 8",
        "slug": "figure08_negative_crossing",
        "title": "Mathematical crossing without detected operational transition",
        "purpose": "Place the frozen mathematical crossing beside all four preselected operational metrics.",
        "sources": [
            "level4/stage_d/results/d2_5_bridge.json",
            "level4/closure_proofs/d4_phase_map/results/decision.json",
        ],
        "transformation": "Four small multiples of frozen tabulated means with Stage-D and D4 crossing bands.",
        "evidence": "NEGATIVE RESULT",
        "paper_section": "Section 10",
        "limitation": "Negative answer is limited to the frozen Gaussian CUSUM protocol, grid, shifts, and metrics.",
    },
]


def configure_matplotlib() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 14,
            "axes.labelsize": 10.5,
            "axes.edgecolor": INK,
            "axes.linewidth": 0.9,
            "axes.facecolor": PAPER,
            "figure.facecolor": PAPER,
            "grid.color": GRID,
            "grid.linewidth": 0.7,
            "grid.alpha": 0.75,
            "legend.frameon": False,
            "text.color": INK,
            "axes.labelcolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "svg.hashsalt": "rebaseguard-level4-closed",
            "savefig.facecolor": PAPER,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.12,
        }
    )


def load_json(relative: str) -> dict:
    with (ROOT / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def assert_frozen_state() -> None:
    decision = load_json("level4/final_level4_closure/results/final_decision.json")
    assert decision["current_verdict"] == "LEVEL-4-CLOSED"
    assert decision["current_counts"] == {"FAIL": 0, "OPEN": 0, "PARTIAL": 1, "PASS": 17}
    assert decision["mandatory_counts"] == {"FAIL": 0, "OPEN": 0, "PARTIAL": 0, "PASS": 16}
    assert decision["nonmandatory_partial_ids"] == ["L4R-13"]
    items = {row["id"]: row["status"] for row in decision["remaining_open_nonblockers"]}
    assert items["SR-ARB-CERTIFICATE"] == "OPEN"


def style_axis(ax: plt.Axes, *, grid_axis: str = "y") -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(True, axis=grid_axis)
    ax.set_axisbelow(True)


def panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(-0.08, 1.04, label, transform=ax.transAxes, fontsize=12, fontweight="bold", va="bottom")


def subtitle(fig: plt.Figure, text: str, y: float = 0.935) -> None:
    fig.text(0.5, y, text, ha="center", va="top", color=MUTED, fontsize=9.2)


def note(fig: plt.Figure, text: str) -> None:
    fig.text(0.01, 0.012, text, ha="left", va="bottom", color=MUTED, fontsize=8.2)


def save_figure(fig: plt.Figure, output: Path, slug: str) -> dict[str, str]:
    output.mkdir(parents=True, exist_ok=True)
    png = output / f"{slug}.png"
    svg = output / f"{slug}.svg"
    fig.savefig(
        png,
        dpi=220,
        metadata={"Software": "ReBaseGuard final figure pipeline"},
    )
    fig.savefig(
        svg,
        metadata={"Creator": "ReBaseGuard final figure pipeline", "Date": None},
    )
    # Matplotlib formats multiline SVG path data with trailing spaces. Normalize
    # generated presentation bytes so repository whitespace checks remain clean.
    svg_text = svg.read_text(encoding="utf-8")
    svg.write_text(
        "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)
    return {"png": sha256(png), "svg": sha256(svg)}


def draw_box(ax: plt.Axes, xy: tuple[float, float], width: float, height: float,
             title: str, body: str, *, face: str = SOFT, edge: str = BLUE) -> None:
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        linewidth=1.6,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(patch)
    ax.text(xy[0] + width / 2, xy[1] + height * 0.66, title, ha="center", va="center",
            fontsize=11, fontweight="bold")
    ax.text(xy[0] + width / 2, xy[1] + height * 0.30, body, ha="center", va="center",
            fontsize=8.8, color=MUTED, linespacing=1.25)


def arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float],
          *, color: str = INK, connectionstyle: str = "arc3,rad=0") -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=13,
            linewidth=1.5,
            color=color,
            connectionstyle=connectionstyle,
        )
    )


def figure01(output: Path) -> dict[str, str]:
    fig, ax = plt.subplots(figsize=(12, 5.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.suptitle("Stopping-selected recursive re-baselining", fontsize=16, fontweight="bold", y=0.98)
    subtitle(fig, "The next reference reuses observations selected by the alarm stopping time")

    boxes = [
        (0.03, "Reference", "$R_j$\nerror $e=R_j-\\mu$"),
        (0.23, "Monitor", "$Z_t=X_t-R_j$\nsequential detector"),
        (0.43, "Alarm", "$\\tau$ selected by\nstopping rule"),
        (0.63, "Reuse", "last $\\min(m,\\tau)$\nalarm-path residuals"),
        (0.83, "Update", "$R_{j+1}$\nreuse fraction $\\rho$"),
    ]
    for x, title, body in boxes:
        draw_box(ax, (x, 0.54), 0.145, 0.24, title, body,
                 face=BLUE_LIGHT if title in {"Alarm", "Reuse"} else SOFT,
                 edge=BLUE if title != "Alarm" else GOLD)
    for left, right in zip(boxes[:-1], boxes[1:]):
        arrow(ax, (left[0] + 0.145, 0.66), (right[0], 0.66))
    arrow(ax, (0.90, 0.53), (0.105, 0.49), color=ORANGE, connectionstyle="arc3,rad=-0.30")
    ax.text(0.50, 0.22, "recursive cross-cycle feedback", ha="center", va="center",
            fontsize=11, fontweight="bold", color=ORANGE)

    draw_box(ax, (0.27, 0.04), 0.46, 0.12, "Conditional-mean skeleton",
             "$F_{\\rho,m}(e)=\\mathbb{E}[e_{j+1}\\mid e_j=e]$  +  cycle noise in the observed recursion",
             face=GOLD_LIGHT, edge=GOLD)
    note(fig, "Conceptual diagram only. It defines the mechanism; it is not proof or empirical evidence.")
    return save_figure(fig, output, FIGURES[0]["slug"])


def figure02(output: Path) -> dict[str, str]:
    cert = load_json("rebaseguard-proof/proofs/certificate.json")
    gamma_lo = float(cert["Gamma_lower"])
    gamma_hi = float(cert["Gamma_upper"])
    slope_lo, slope_hi = 1.0 - gamma_hi, 1.0 - gamma_lo

    fig = plt.figure(figsize=(12, 6.2))
    grid = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.15], hspace=0.38, wspace=0.22)
    axes = [fig.add_subplot(grid[0, i]) for i in range(3)]
    fig.suptitle("Stopped-selection derivative and local instability", fontsize=16, fontweight="bold", y=0.985)
    subtitle(fig, "The formal derivative and rigorous numerical bound are separate evidence streams")

    cards = [
        ("Lean-checked spine", "$\\frac{d}{de}\\,\\mathbb{E}_e[Z_\\tau]\\vert_0$\n$=-\\mathbb{E}_0[Z_\\tau T_\\tau]$", BLUE_LIGHT, BLUE),
        ("Human model bridge", "$F'_\\rho(0)$\n$=\\rho(1-\\Gamma_{\\mathrm{CUSUM}})$", GOLD_LIGHT, GOLD),
        ("Arb-certified value", rf"$\Gamma_{{\mathrm{{CUSUM}}}}\in$" + "\n" + rf"$[{gamma_lo:.4f},\,{gamma_hi:.4f}]$", "#f3e3e8", PINK),
    ]
    for index, (title, body, face, edge) in enumerate(cards):
        ax = axes[index]
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        draw_box(ax, (0.05, 0.18), 0.90, 0.64, title, body, face=face, edge=edge)
    fig.text(0.345, 0.715, "+", fontsize=20, fontweight="bold", color=MUTED)
    fig.text(0.657, 0.715, "+", fontsize=20, fontweight="bold", color=MUTED)

    ax = fig.add_subplot(grid[1, :])
    style_axis(ax, grid_axis="x")
    ax.set_xlim(slope_lo - 1.2, 0.5)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xlabel("Certified enclosure for full-reuse local slope  $F'_1(0)=1-\\Gamma_{\\mathrm{CUSUM}}$")
    ax.axvline(-1, color=INK, linestyle="--", linewidth=1.3)
    ax.axvspan(slope_lo, slope_hi, facecolor=BLUE_LIGHT, edgecolor=BLUE, linewidth=1.5)
    ax.plot([slope_lo, slope_hi], [0.52, 0.52], color=BLUE, linewidth=4)
    ax.scatter([slope_lo, slope_hi], [0.52, 0.52], s=55, color=BLUE, edgecolor=INK, zorder=3)
    ax.text(-1, 0.84, "local stability threshold", ha="center", fontsize=9, color=MUTED)
    ax.text((slope_lo + slope_hi) / 2, 0.32,
            f"[{slope_lo:.3f}, {slope_hi:.3f}]  lies strictly below −1",
            ha="center", fontsize=10, fontweight="bold")
    ax.text(-0.8, 0.10, "locally stable\n$|F'_1(0)|<1$", ha="center", color=MUTED)
    ax.text((slope_lo - 1) / 2, 0.10, "locally repelling at zero", ha="center", color=BLUE, fontweight="bold")
    note(fig, "Scope: frozen Gaussian CUSUM, m=1, rho=1; local deterministic conditional-mean map only.")
    return save_figure(fig, output, FIGURES[1]["slug"])


def figure03(output: Path) -> dict[str, str]:
    theorem = load_json("level4/stage_b/certificate/period2_certificate.json")["theorem"]
    lo, hi = theorem["root_interval"]
    lam_lo, lam_hi = theorem["lambda2"]

    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-0.62, 0.72)
    ax.axis("off")
    fig.suptitle("Certified period-two orbit of the deterministic skeleton", fontsize=16, fontweight="bold", y=0.98)
    subtitle(fig, "Frozen CUSUM · m=1 · full reuse (rho=1)")

    for sign, x in [(-1, -(lo + hi) / 2), (1, (lo + hi) / 2)]:
        left = -hi if sign < 0 else lo
        width = hi - lo
        ax.add_patch(Rectangle((left, -0.12), width, 0.24, facecolor=BLUE_LIGHT,
                               edgecolor=BLUE, linewidth=2, hatch="//"))
        ax.scatter([x], [0], s=165, color=BLUE, edgecolor=INK, linewidth=1.2, zorder=4)
        ax.text(x, -0.24, "$-e_*$" if sign < 0 else "$+e_*$", ha="center",
                fontsize=12, fontweight="bold")
    arrow(ax, (-0.86, 0.11), (0.86, 0.11), color=ORANGE, connectionstyle="arc3,rad=-0.36")
    arrow(ax, (0.86, -0.11), (-0.86, -0.11), color=ORANGE, connectionstyle="arc3,rad=-0.36")
    ax.text(0, 0.50, "$F_1(-e_*)=+e_*$", ha="center", fontsize=11, color=ORANGE)
    ax.text(0, -0.48, "$F_1(+e_*)=-e_*$", ha="center", fontsize=11, color=ORANGE)
    ax.text(0, 0.14, rf"$e_*\in[{lo:.7f},\,{hi:.7f}]$", ha="center", fontsize=11,
            bbox={"boxstyle": "round,pad=0.35", "facecolor": SOFT, "edgecolor": GRID})
    ax.text(0, -0.04, rf"two-cycle multiplier $\lambda_2\in[{lam_lo:.5f},\,{lam_hi:.5f}]\subset(0,1)$",
            ha="center", fontsize=10, fontweight="bold")
    ax.text(0, 0.64, "unique nonzero root within the certified interval · locally attracting",
            ha="center", fontsize=9.5, color=MUTED)
    note(fig, "Deterministic conditional-mean skeleton only. No period-two or invariant-law theorem for the noisy stochastic chain.")
    return save_figure(fig, output, FIGURES[2]["slug"])


def figure04(output: Path) -> dict[str, str]:
    d4 = load_json("level4/closure_proofs/d4_phase_map/results/decision.json")
    rows = d4["rho_c_rows"]
    m = np.array([row["m"] for row in rows], dtype=float)
    rho_c = np.array([row["rho_c_unconstrained"] for row in rows], dtype=float)
    dense_m = np.geomspace(m.min(), m.max(), 500)
    dense_boundary = np.interp(np.log(dense_m), np.log(m), rho_c)

    fig, ax = plt.subplots(figsize=(11.5, 6.5))
    fig.suptitle("Finite-window local-stability map", fontsize=16, fontweight="bold", y=0.98)
    subtitle(fig, "$\\lambda(m,\\rho)=\\rho(1-\\widetilde{\\Gamma}_m)$ · D4 random-window convention")
    ax.set_xscale("log")
    ax.set_xlim(1, 250)
    ax.set_ylim(0, 1)
    ax.fill_between(dense_m, 0, np.minimum(dense_boundary, 1), color=BLUE_LIGHT,
                    edgecolor=BLUE, linewidth=0.6, label="locally stable")
    ax.fill_between(dense_m, np.minimum(dense_boundary, 1), 1, color=GOLD_LIGHT,
                    edgecolor=GOLD, linewidth=0.6, hatch="//", label="locally unstable")
    ax.plot(dense_m, dense_boundary, color=INK, linewidth=2.2, label="$\\rho_c(m)$")
    ax.scatter(m, np.minimum(rho_c, 1.03), s=35, facecolor=PAPER, edgecolor=INK,
               linewidth=1.1, zorder=4, label="frozen D4 grid")
    ax.axhline(1, color=MUTED, linestyle="--", linewidth=1.2)
    ax.axvspan(70, 72, color=PINK, alpha=0.22, linewidth=0)
    ax.text(71, 0.93, "full-reuse crossing\n$m\\in[70,72]$", ha="center", va="top",
            fontsize=9, color=PINK, fontweight="bold")
    ax.text(4, 0.73, "locally unstable", color=GOLD, fontsize=12, fontweight="bold")
    ax.text(80, 0.35, "locally stable", color=BLUE, fontsize=12, fontweight="bold")
    ax.set_xlabel("Reuse-window length $m$ (log scale)")
    ax.set_ylabel("Reuse fraction $\\rho$")
    style_axis(ax, grid_axis="both")
    ax.legend(loc="lower right", ncol=2, fontsize=8.8)
    note(fig, "Mathematical deterministic local-stability boundary; not an observed operational phase transition.")
    return save_figure(fig, output, FIGURES[3]["slug"])


def figure05(output: Path) -> dict[str, str]:
    findings = load_json("level4/closure_proofs/l4r06_policy/results/scientific_findings.json")
    actions = findings["policy"]["actions"]
    m = np.array([row["m"] for row in actions])
    p3 = np.array([row["rho"] for row in actions])
    allowance = np.array([row["uncapped_allowance"] for row in actions])
    p2 = 0.0297958439

    fig, ax = plt.subplots(figsize=(11.5, 6.2))
    fig.suptitle("Frozen stability-aware P3 reuse policy", fontsize=16, fontweight="bold", y=0.98)
    subtitle(fig, r"$\rho_{P3}(m)=\min(1,\,0.8\,\rho_{c,L95}(m))$ · four precommitted regimes")
    ax.plot(m, np.zeros_like(m), color=MUTED, linestyle=":", marker="o", markerfacecolor=PAPER,
            label="P0 fresh (rho=0)")
    ax.plot(m, np.ones_like(m), color=INK, linestyle="--", marker="s", markerfacecolor=PAPER,
            label="P1 full reuse (rho=1)")
    ax.plot(m, np.full_like(m, p2, dtype=float), color=OLIVE, linestyle="-.", marker="^",
            markerfacecolor=PAPER, label=f"P2 fixed (rho={p2:.4f})")
    ax.plot(m, p3, color=BLUE, linewidth=2.4, marker="D", markersize=7,
            label="P3 stability-aware")
    ax.plot(m, allowance, color=ORANGE, linewidth=1.5, linestyle=":", marker="x",
            label="uncapped 0.8 lower-95% allowance")
    for x, value in zip(m, p3):
        ax.annotate(f"{value:.3f}", (x, value), xytext=(0, 10), textcoords="offset points",
                    ha="center", fontsize=8.5, color=BLUE, fontweight="bold")
    ax.annotate("P3=P1 saturation", (100, 1), xytext=(-8, -35), textcoords="offset points",
                ha="right", fontsize=9, color=PINK,
                arrowprops={"arrowstyle": "->", "color": PINK, "linewidth": 1.2})
    ax.set_xticks(m, [str(int(value)) for value in m])
    ax.set_ylim(-0.04, 1.12)
    ax.set_xlabel("Reuse-window regime $m$")
    ax.set_ylabel("Reuse fraction $\\rho$")
    style_axis(ax)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.885),
               ncol=3, fontsize=8.5)
    fig.subplots_adjust(top=0.79)
    note(fig, "The 20% margin was frozen before outcomes. P3 is stability-aware, not universally optimal.")
    return save_figure(fig, output, FIGURES[4]["slug"])


def figure06(output: Path) -> dict[str, str]:
    findings = load_json("level4/closure_proofs/l4r06_policy/results/scientific_findings.json")
    mse = findings["H6-2"]["family"]["rows"]
    arl = findings["H6-3"]["family"]["rows"]

    fig, axes = plt.subplots(1, 2, figsize=(12, 6.1))
    fig.suptitle("Reference-state and monitoring consequences", fontsize=16, fontweight="bold", y=0.985)
    subtitle(fig, "Frozen simultaneous 95% lower bounds · active P3 regimes only")

    for ax, rows, title, xlabel, log_scale in [
        (axes[0], mse, "Reference MSE improvement", "MSE(P1) − MSE(P3)", True),
        (axes[1], arl, "False-alert burden improvement", "ARL0(P3) − ARL0(P1)", False),
    ]:
        y = np.arange(len(rows))
        point = np.array([row["point"] for row in rows])
        lower = np.array([row["simultaneous_lower95"] for row in rows])
        ax.hlines(y, lower, point, color=BLUE, linewidth=3)
        ax.scatter(point, y, s=60, color=BLUE, edgecolor=INK, zorder=3, label="point estimate")
        ax.scatter(lower, y, s=52, facecolor=PAPER, edgecolor=BLUE, linewidth=1.5,
                   zorder=3, label="simultaneous lower 95%")
        ax.set_yticks(y, [f"m={row['m']}" for row in rows])
        ax.invert_yaxis()
        if log_scale:
            ax.set_xscale("log")
            ax.text(0.02, 0.02, "log scale", transform=ax.transAxes, fontsize=8, color=MUTED)
        ax.set_xlabel(xlabel)
        ax.set_title(title, loc="left", fontweight="bold")
        style_axis(ax, grid_axis="x")
        for yy, value in zip(y, point):
            ax.annotate(f"{value:.3g}", (value, yy), xytext=(6, 0), textcoords="offset points",
                        va="center", fontsize=8.3)
    axes[0].legend(loc="lower right", fontsize=8.2)
    axes[1].text(0.98, 0.05, "m=100: P3=P1\n(no active contrast)", transform=axes[1].transAxes,
                 ha="right", va="bottom", fontsize=9, color=PINK,
                 bbox={"boxstyle": "round,pad=0.3", "facecolor": "#f3e3e8", "edgecolor": PINK})
    note(fig, "All active-regime simultaneous lower bounds are positive. P2 has descriptive advantages at m=70 and m=100; two secondary epsilon=0.05 conditions fail.")
    return save_figure(fig, output, FIGURES[5]["slug"])


def parse_external_table() -> list[dict[str, str]]:
    path = ROOT / "level4/closure_proofs/external_validation_v3/CROSS_CAMPAIGN_AGGREGATION.md"
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "Campaign" in line or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 9 or cells[0] not in {"Stage E", "V2", "V3"}:
            continue
        rows.append(
            {
                "campaign": cells[0],
                "task": cells[1],
                "reference": cells[4],
                "operational": cells[5],
                "safety": cells[6],
                "joint": cells[7],
                "counts": cells[8],
            }
        )
    assert len(rows) == 8
    return rows


def figure07(output: Path) -> dict[str, str]:
    rows = parse_external_table()
    decision = load_json("level4/closure_proofs/external_validation_v3/results/decision.json")
    metrics = ["reference", "operational", "safety", "joint"]
    labels = ["Reference\ndistortion", "Operational\nconsequence", "P2 safety", "Joint support"]
    code = {"NO": 0, "NA": 1, "YES": 2}
    matrix = np.array([[code[row[key]] for key in metrics] for row in rows])

    fig = plt.figure(figsize=(13, 7.3))
    grid = fig.add_gridspec(1, 2, width_ratios=[3.2, 1.25], wspace=0.30)
    ax = fig.add_subplot(grid[0, 0])
    ax2 = fig.add_subplot(grid[0, 1])
    fig.suptitle("Semi-real external-validation synthesis", fontsize=16, fontweight="bold", y=0.985)
    subtitle(fig, "Task-level evidence retained; campaign estimates and samples are not pooled")

    cmap = mpl.colors.ListedColormap([PAPER, GOLD_LIGHT, BLUE_LIGHT])
    ax.imshow(matrix, cmap=cmap, vmin=0, vmax=2, aspect="auto")
    ax.set_xticks(np.arange(4), labels)
    task_labels = [f"{row['campaign']} · {row['task']}" for row in rows]
    ax.set_yticks(np.arange(len(rows)), task_labels)
    ax.tick_params(axis="y", labelsize=8.8)
    for i, row in enumerate(rows):
        for j, key in enumerate(metrics):
            value = row[key]
            ax.text(j, i, "✓" if value == "YES" else ("—" if value == "NA" else "×"),
                    ha="center", va="center", fontsize=13,
                    color=BLUE if value == "YES" else (GOLD if value == "NA" else INK),
                    fontweight="bold")
    for boundary in [2.5, 5.5]:
        ax.axhline(boundary, color=INK, linewidth=1.4)
    ax.set_xticks(np.arange(-0.5, 4, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(rows), 1), minor=True)
    ax.grid(which="minor", color=GRID, linewidth=0.8)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_title("Frozen task-level support matrix", loc="left", fontweight="bold")

    campaigns = ["Stage E", "V2", "V3"]
    successes = [0, 1, 2]
    totals = [3, 3, 2]
    bars = ax2.barh(np.arange(3), totals, color=SOFT, edgecolor=INK, height=0.58)
    ax2.barh(np.arange(3), successes, color=BLUE_LIGHT, edgecolor=BLUE, height=0.58, hatch="//")
    ax2.set_yticks(np.arange(3), campaigns)
    ax2.invert_yaxis()
    ax2.set_xlim(0, 3.25)
    ax2.set_xticks([0, 1, 2, 3])
    ax2.set_xlabel("Joint-support tasks")
    ax2.set_title("Campaign decisions", loc="left", fontweight="bold")
    style_axis(ax2, grid_axis="x")
    for index, (success, total) in enumerate(zip(successes, totals)):
        ax2.text(total + 0.07, index, f"{success}/{total}", va="center", fontsize=10, fontweight="bold")
    ax2.text(0.5, -0.22,
             f"Cross-campaign: {decision['cross_campaign_success_count']} supporting tasks\n"
             f"Frozen requirement: {decision['cross_campaign_required']}",
             transform=ax2.transAxes, ha="center", va="top", fontsize=10,
             bbox={"boxstyle": "round,pad=0.4", "facecolor": GOLD_LIGHT, "edgecolor": GOLD})
    note(fig, "Semi-real/public sequential streams only. Negative Stage E and V2 tasks remain visible; P2 safety is regime-dependent.")
    return save_figure(fig, output, FIGURES[6]["slug"])


def figure08(output: Path) -> dict[str, str]:
    bridge = load_json("level4/stage_d/results/d2_5_bridge.json")
    d4 = load_json("level4/closure_proofs/d4_phase_map/results/decision.json")
    rows = bridge["rows"]
    m = np.array([row["m"] for row in rows], dtype=float)
    crossing = d4["gamma_equals_2_crossings"][0]["bracket"]
    metrics = [
        ("cycle_arl", "Cycle ARL", BLUE, "o"),
        ("reference_mse", "Reference MSE", ORANGE, "s"),
        ("e_acf1", "Reference-error ACF1", OLIVE, "^"),
        ("direction_acf1", "Alarm-direction ACF1", PINK, "D"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.2), sharex=True)
    fig.suptitle("Mathematical crossing without detected operational transition", fontsize=16,
                 fontweight="bold", y=0.985)
    subtitle(fig, "Frozen Stage-D monitoring metrics · 20,000 replicates · rho=1")
    for ax, (key, title, color, marker) in zip(axes.flat, metrics):
        values = np.array([row[key]["mean"] for row in rows])
        se = np.array([row[key]["se"] for row in rows])
        ax.axvspan(50, 75, color=GOLD_LIGHT, alpha=0.55, linewidth=0)
        ax.axvspan(crossing[0], crossing[1], color=PINK, alpha=0.23, linewidth=0)
        ax.errorbar(m, values, yerr=1.96 * se, color=color, marker=marker,
                    markerfacecolor=PAPER, markeredgecolor=color, linewidth=2,
                    capsize=2.5)
        ax.set_xscale("log")
        ax.set_title(title, loc="left", fontweight="bold")
        style_axis(ax, grid_axis="both")
        ax.text(0.97, 0.08, "monotone in log m", transform=ax.transAxes, ha="right",
                fontsize=8.5, color=MUTED)
    for ax in axes[1, :]:
        ax.set_xlabel("Reuse-window length $m$ (log scale)")
    axes[0, 0].text(0.03, 0.90, "Stage-D bracket [50,75]", transform=axes[0, 0].transAxes,
                    fontsize=8.5, color=GOLD)
    axes[0, 0].text(0.03, 0.80, "D4 bracket [70,72]", transform=axes[0, 0].transAxes,
                    fontsize=8.5, color=PINK)
    fig.subplots_adjust(bottom=0.14, hspace=0.28)
    fig.text(0.5, 0.060, "0/4 preselected metrics peak at the crossing · 4/4 are monotone in log m",
             ha="center", fontsize=11, fontweight="bold", color=INK)
    note(fig, "Negative result under the frozen Gaussian CUSUM protocol and monitored metrics; not a universal no-effect theorem.")
    return save_figure(fig, output, FIGURES[7]["slug"])


def provenance_markdown(manifest: dict) -> str:
    lines = [
        "# Final publication figures",
        "",
        "These eight figures are presentation-only derivatives of frozen ReBaseGuard evidence.",
        "They do not run simulations, download data, or modify scientific artifacts.",
        "",
        "Regenerate with:",
        "",
        "```bash",
        "level4/.venv/bin/python scripts/generate_final_figures.py",
        "```",
        "",
        "## Provenance",
        "",
        "| ID | Title | Evidence | Paper | PNG SHA-256 | SVG SHA-256 |",
        "|---|---|---|---|---|---|",
    ]
    for row in manifest["figures"]:
        lines.append(
            f"| {row['id']} | {row['title']} | {row['evidence']} | {row['paper_section']} | "
            f"`{row['outputs']['png']}` | `{row['outputs']['svg']}` |"
        )
    lines.extend(["", "## Figure details", ""])
    for row in manifest["figures"]:
        lines.extend(
            [
                f"### {row['id']} — {row['title']}",
                "",
                f"- **Purpose:** {row['purpose']}",
                f"- **Sources:** {', '.join(f'`{source}`' for source in row['sources'])}",
                f"- **Source SHA-256:** {', '.join(f'`{source}` `{digest}`' for source, digest in row['source_sha256'].items())}",
                f"- **Transformation:** {row['transformation']}",
                f"- **Evidence classification:** {row['evidence']}",
                f"- **Paper section:** {row['paper_section']}",
                f"- **Limitation:** {row['limitation']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Visual system",
            "",
            "All figures use DejaVu Sans, charcoal text, restrained blue/gold/orange/pink/olive roots,",
            "near-white backgrounds, quiet grids, shared line weights, and non-color encodings such as",
            "hatching, marker shape, open fills, direct labels, and line style. SVG is the vector master;",
            "PNG is exported at 220 dpi for GitHub rendering.",
            "",
            "The machine-readable companion is `figures/final/manifest.json`.",
            "",
        ]
    )
    return "\n".join(lines)


def generate(output: Path) -> dict:
    assert_frozen_state()
    configure_matplotlib()
    renderers = [figure01, figure02, figure03, figure04, figure05, figure06, figure07, figure08]
    manifest = {
        "schema": "rebaseguard.final-figures.v1",
        "generator": "scripts/generate_final_figures.py",
        "new_science_run": False,
        "network_used": False,
        "figures": [],
    }
    for metadata, renderer in zip(FIGURES, renderers):
        source_hashes = {source: sha256(ROOT / source) for source in metadata["sources"]}
        outputs = renderer(output)
        manifest["figures"].append({**metadata, "source_sha256": source_hashes, "outputs": outputs})
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "README.md").write_text(provenance_markdown(manifest), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    manifest = generate(output)
    print(f"generated {len(manifest['figures'])} figures in PNG+SVG at {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
