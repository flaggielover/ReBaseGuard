#!/usr/bin/env python3
"""Generate the four required figures from results/summary.json only."""
from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from config import BASE, POLICIES, PRIMARY_TASKS

LABELS = {"household": "Household", "metro": "Metro", "beijing": "Beijing",
          "P0_fresh": "P0 fresh", "P1_full_reuse": "P1 full", "P2_rebaseguard": "P2 RBG"}
COLORS = {"P0_fresh": "#4c78a8", "P1_full_reuse": "#e45756", "P2_rebaseguard": "#54a24b"}


def _save(fig, name: str, rect=(0, 0, 1, 1)):
    fig.tight_layout(rect=rect)
    fig.savefig(BASE / f"figures/{name}", dpi=160,
                metadata={"Software": "ReBaseGuard external validation V2"})
    plt.close(fig)


def reference_distortion(summary):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    x = np.arange(len(PRIMARY_TASKS)); width = 0.24
    for index, policy in enumerate(POLICIES):
        rows = [summary["tasks"][task]["E2"][policy] for task in PRIMARY_TASKS]
        y = np.array([row["mean"] for row in rows])
        err = np.array([[row["mean"] - row["ci95"][0] for row in rows],
                        [row["ci95"][1] - row["mean"] for row in rows]])
        ax.bar(x + (index - 1) * width, y, width, label=LABELS[policy],
               color=COLORS[policy], yerr=err, capsize=3)
    ax.set_xticks(x, [LABELS[t] for t in PRIMARY_TASKS])
    ax.set_ylabel("Reference distortion (train-SD units)")
    ax.set_title("A. Natural-stream reference distortion")
    ax.legend(frameon=False, ncols=3)
    _save(fig, "figure_a_reference_distortion.png")


def normalized_response(summary):
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2), sharey=True)
    conditions = ["STEP_0.5", "STEP_1.0", "STEP_2.0", "GRADUAL_1.0", "RECURRING_1.0"]
    labels = ["S0.5", "S1", "S2", "Grad", "Recur"]
    for ax, task in zip(axes, PRIMARY_TASKS):
        x = np.arange(len(conditions))
        for policy in POLICIES:
            rows = [summary["tasks"][task]["E1"][condition][policy] for condition in conditions]
            y = np.array([row["ratio"] for row in rows])
            lo = np.array([row["ci95"][0] for row in rows]); hi = np.array([row["ci95"][1] for row in rows])
            ax.errorbar(x, y, yerr=np.vstack([y - lo, hi - y]), marker="o",
                        capsize=2, label=LABELS[policy], color=COLORS[policy])
        ax.set_xticks(x, labels, rotation=35)
        ax.set_title(LABELS[task])
        ax.axhline(1, color="0.5", lw=1)
    axes[0].set_ylabel("E1 normalized response (matched wait)")
    handles, labels_ = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels_, frameon=False, ncols=3, loc="upper center",
               bbox_to_anchor=(0.5, 0.91))
    fig.suptitle("B. Baseline-normalized intervention response", y=0.99)
    _save(fig, "figure_b_normalized_response.png", rect=(0, 0, 1, 0.84))


def delay_burden(summary):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6))
    x = np.arange(len(PRIMARY_TASKS)); width = 0.24
    for index, policy in enumerate(POLICIES):
        e4 = [summary["tasks"][task]["E4"]["STEP_1.0"][policy]["hours"] for task in PRIMARY_TASKS]
        e3 = [summary["tasks"][task]["E3"][policy]["mean"] for task in PRIMARY_TASKS]
        axes[0].bar(x + (index - 1) * width, e4, width, color=COLORS[policy], label=LABELS[policy])
        axes[1].bar(x + (index - 1) * width, e3, width, color=COLORS[policy], label=LABELS[policy])
    for ax in axes:
        ax.set_xticks(x, [LABELS[t] for t in PRIMARY_TASKS])
    axes[0].set_title("Medium-step absolute delay")
    axes[0].set_ylabel("Hours (capped)")
    axes[1].set_title("Natural-stream alert burden")
    axes[1].set_ylabel("Alarms per 1,000 observations")
    handles, labels_ = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels_, frameon=False, ncols=3, loc="upper center",
               bbox_to_anchor=(0.5, 0.90))
    fig.suptitle("C. Absolute delay and alert burden", y=0.99)
    _save(fig, "figure_c_delay_alert_burden.png", rect=(0, 0, 1, 0.82))


def support(summary):
    matrix = np.array([[summary["tasks"][task][f"H2_{index}"]["supported"]
                        for index in range(1, 5)] for task in PRIMARY_TASKS], int)
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    image = ax.imshow(matrix, cmap=matplotlib.colors.ListedColormap(["#d9d9d9", "#54a24b"]),
                      vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(4), ["H2-1", "H2-2", "H2-3", "H2-4"])
    ax.set_yticks(range(3), [LABELS[t] for t in PRIMARY_TASKS])
    for row in range(3):
        for col in range(4):
            ax.text(col, row, "SUPPORTED" if matrix[row, col] else "NOT SUPPORTED",
                    ha="center", va="center", fontsize=8)
    ax.set_title("D. Frozen task-level mechanism decisions")
    _save(fig, "figure_d_task_support.png")


def main() -> int:
    summary = json.loads((BASE / "results/summary.json").read_text())
    (BASE / "figures").mkdir(exist_ok=True)
    reference_distortion(summary)
    normalized_response(summary)
    delay_burden(summary)
    support(summary)
    print("figures: 4 generated from results/summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
