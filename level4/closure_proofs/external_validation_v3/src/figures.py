#!/usr/bin/env python3
"""Generate all five V3 figures from results/summary.json only."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap


BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "results/summary.json"
FIGURES = BASE / "figures"
COLORS = {"Stage E": "#6b7280", "V2": "#d97706", "V3": "#2563eb"}


def save(fig, name: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / name, dpi=160, bbox_inches="tight",
                metadata={"Software": "ReBaseGuard external validation V3"})
    plt.close(fig)


def support_value(label: str) -> float:
    return 1.0 if label == "SUPPORTED" else 0.0 if label == "NOT_SUPPORTED" else np.nan


def support_figure(rows: list[dict], field: str, title: str, name: str) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 5.8), constrained_layout=True)
    y = np.arange(len(rows))
    values = np.asarray([support_value(row[field]) for row in rows])
    colors = [COLORS[row["campaign"]] for row in rows]
    ax.scatter(np.nan_to_num(values, nan=0.5), y, s=110, c=colors, edgecolor="white", linewidth=0.8)
    for index, value in enumerate(values):
        text = "YES" if value == 1 else "NO" if value == 0 else "UNEVALUABLE"
        ax.text((0.96 if value == 1 else 0.04 if value == 0 else 0.54), index, text,
                ha="right" if value == 1 else "left",
                va="center", fontsize=9, fontweight="bold")
    ax.set_yticks(y, [f"{row['campaign']} · {row['display']}" for row in rows])
    ax.set_xticks([0, 1], ["Not supported", "Supported"])
    ax.set_xlim(-0.12, 1.12)
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.grid(axis="x", color="#d1d5db", linewidth=0.8)
    ax.set_title(title, fontweight="bold", pad=14)
    ax.set_xlabel("Task-level frozen decision; estimates are not pooled")
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    save(fig, name)


def figure_c(summary: dict) -> None:
    tasks = summary["tasks"]
    conditions = ["STEP_0.5", "STEP_1.0", "STEP_2.0", "GRADUAL_1.0", "RECURRING_1.0"]
    labels = ["Step 0.5", "Step 1", "Step 2", "Gradual", "Recurring"]
    fig, ax = plt.subplots(figsize=(10.5, 5.8), constrained_layout=True)
    x = np.arange(len(conditions))
    offsets = {"metropt": -0.12, "retail": 0.12}
    names = {"metropt": "MetroPT-3", "retail": "Online Retail II"}
    colors = {"metropt": "#2563eb", "retail": "#059669"}
    for task in ("metropt", "retail"):
        rows = tasks[task]["analysis"]["H3_3"]["conditions"]
        point = np.asarray([rows[key]["excess"] for key in conditions])
        lower = np.asarray([rows[key]["lower99_excess"] for key in conditions])
        upper = np.asarray([rows[key]["upper99_excess"] for key in conditions])
        ax.errorbar(x + offsets[task], point, yerr=[point - lower, upper - point],
                    fmt="o", capsize=4, color=colors[task], label=names[task], linewidth=1.5)
    ax.axhline(0.10, color="#dc2626", linestyle="--", linewidth=1.4, label="Primary margin +0.10")
    ax.axhline(0.05, color="#9ca3af", linestyle=":", linewidth=1.2, label="Secondary +0.05")
    ax.axhline(0, color="#111827", linewidth=0.8)
    ax.set_xticks(x, labels)
    ax.set_ylabel("P2/P0 normalized-response excess")
    ax.set_title("P2 simultaneous non-inferiority by intervention", fontweight="bold", pad=14)
    ax.legend(ncol=2, frameon=False)
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "figure_c_p2_noninferiority.png")


def figure_d(rows: list[dict]) -> None:
    fields = ["reference_distortion", "operational_consequence", "p2_safety", "joint_support"]
    columns = ["Reference\ndistortion", "Operational\nconsequence", "P2 safety /\nnon-inferiority", "Joint\nsupport"]
    matrix = []
    labels = []
    for row in rows:
        values = []
        for field in fields:
            value = row[field]
            if isinstance(value, bool):
                values.append(1 if value else 0)
            else:
                values.append(1 if value == "SUPPORTED" else 0 if value == "NOT_SUPPORTED" else -1)
        matrix.append(values)
        labels.append(f"{row['campaign']} · {row['display']}")
    matrix = np.asarray(matrix)
    fig, ax = plt.subplots(figsize=(10.5, 6.4), constrained_layout=True)
    ax.imshow(matrix, cmap=ListedColormap(["#d1d5db", "#fecaca", "#bbf7d0"]), vmin=-1, vmax=1,
              aspect="auto")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, "NA" if matrix[i, j] < 0 else "YES" if matrix[i, j] else "NO",
                    ha="center", va="center", fontweight="bold", fontsize=9)
    ax.set_xticks(np.arange(len(columns)), columns)
    ax.set_yticks(np.arange(len(labels)), labels)
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
    ax.set_title("Task-level joint-support matrix", fontweight="bold", pad=18)
    ax.set_xticks(np.arange(-0.5, len(columns), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(labels), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)
    save(fig, "figure_d_joint_support_matrix.png")


def figure_e(rows: list[dict]) -> None:
    fig, ax = plt.subplots(figsize=(11, 5.8), constrained_layout=True)
    x = np.arange(len(rows))
    values = [row["minimum_effective_blocks"] for row in rows]
    colors = [COLORS[row["campaign"]] for row in rows]
    bars = ax.bar(x, values, color=colors, width=0.7)
    ax.bar_label(bars, padding=3, fontsize=9)
    ax.axhline(30, color="#9ca3af", linestyle=":", linewidth=1.2)
    ax.axhline(40, color="#dc2626", linestyle="--", linewidth=1.3)
    ax.text(-0.4, 30.35, "Recommended minimum 30", color="#6b7280",
            ha="left", va="bottom", fontsize=9)
    ax.text(-0.4, 40.35, "V3 frozen floor 40", color="#b91c1c",
            ha="left", va="bottom", fontsize=9)
    ax.set_xticks(x, [f"{row['campaign']}\n{row['display']}" for row in rows], rotation=25, ha="right")
    ax.set_ylabel("Minimum effective blocks across closure endpoints")
    ax.set_title("Power and effective-block comparison", fontweight="bold", pad=14)
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "figure_e_effective_blocks.png")


def main() -> int:
    summary = json.loads(SOURCE.read_text())
    rows = summary["cross_campaign_tasks"]
    support_figure(rows, "reference_distortion",
                   "Cross-campaign reference-distortion support",
                   "figure_a_cross_campaign_reference_distortion.png")
    support_figure(rows, "operational_consequence",
                   "Cross-campaign operational-consequence support",
                   "figure_b_operational_consequences.png")
    figure_c(summary)
    figure_d(rows)
    figure_e(rows)
    print("figures: 5 generated from results/summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
