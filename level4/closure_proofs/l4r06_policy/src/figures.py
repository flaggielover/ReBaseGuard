#!/usr/bin/env python3
"""Generate every L4R-06 figure from scientific_findings.json only."""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from config import FIGURES, RESULTS, canonical_json

SOURCE = RESULTS / "scientific_findings.json"
NAMES = (
    "figure_a_policy.png",
    "figure_b_reference_distortion.png",
    "figure_c_operational_consequence.png",
    "figure_d_noninferiority.png",
    "figure_e_joint_criteria.png",
)


def _save(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=150, metadata={"Software": "ReBaseGuard L4R-06"})
    plt.close(fig)


def generate(source: Path = SOURCE, output: Path = FIGURES) -> dict[str, Any]:
    data = json.loads(source.read_text())
    output.mkdir(parents=True, exist_ok=True)
    actions = data["policy"]["actions"]
    ms = np.array([row["m"] for row in actions])
    rho = np.array([row["rho"] for row in actions])
    bound = np.array([row["multiplier_bound"] for row in actions])

    fig, ax = plt.subplots(figsize=(6.4, 4.1))
    ax.plot(ms, rho, "o-", label=r"$\rho_{P3}$")
    ax.plot(ms, bound, "s--", label=r"uncertainty-aware $\rho/\rho_{c,L95}$")
    ax.axhline(0.8, color="0.35", lw=1, ls=":", label="frozen 0.8 bound")
    ax.set(xlabel="terminal-window regime m", ylabel="policy action / multiplier bound",
           title="A. Frozen stability-aware P3 action")
    ax.set_ylim(0, 1.08); ax.grid(alpha=.25); ax.legend(fontsize=8)
    _save(fig, output / NAMES[0])

    summaries = data["all_cell_summaries"]
    colors = {"P0": "#333333", "P1": "#d62728", "P2": "#1f77b4", "P3": "#2ca02c"}
    fig, ax = plt.subplots(figsize=(6.4, 4.1))
    for policy in ("P0", "P1", "P2", "P3"):
        rows = [r for r in summaries if r["policy"] == policy and r["shift"] == 0.0]
        rows.sort(key=lambda r: r["m"])
        ax.plot([r["m"] for r in rows], [r["reference_mse"] for r in rows],
                "o-", label=policy, color=colors[policy])
    ax.set(xlabel="m", ylabel=r"in-control $E[e^2]$", title="B. Reference-state distortion")
    ax.grid(alpha=.25); ax.legend(ncol=4, fontsize=8)
    _save(fig, output / NAMES[1])

    fig, ax = plt.subplots(figsize=(6.4, 4.1))
    for policy in ("P0", "P1", "P2", "P3"):
        rows = [r for r in summaries if r["policy"] == policy and r["shift"] == 0.0]
        rows.sort(key=lambda r: r["m"])
        ax.plot([r["m"] for r in rows], [r["cycle_arl"] for r in rows],
                "o-", label=policy, color=colors[policy])
    ax.set(xlabel="m", ylabel="in-control cycle ARL (higher = fewer false alerts)",
           title="C. Operational false-alert consequence")
    ax.grid(alpha=.25); ax.legend(ncol=4, fontsize=8)
    _save(fig, output / NAMES[2])

    fig, ax = plt.subplots(figsize=(6.8, 4.3))
    response = data["H6-4"]["family"]["rows"]
    for m in ms:
        rows = [r for r in response if r["m"] == int(m)]
        rows.sort(key=lambda r: r["shift"])
        ax.plot([r["shift"] for r in rows],
                [r["simultaneous_upper95"] for r in rows], "o-", label=f"m={m}")
    ax.axhline(.10, color="#d62728", ls="--", label="primary epsilon=0.10")
    ax.axhline(.05, color="0.45", ls=":", label="secondary epsilon=0.05")
    ax.set(xlabel=r"shift $\Delta$", ylabel=r"simultaneous upper 95%: $R(P3)-R(P0)$",
           title="D. P3 versus fresh normalized-response non-inferiority")
    ax.grid(alpha=.25); ax.legend(fontsize=8, ncol=3)
    _save(fig, output / NAMES[3])

    labels = ["H6-1", "H6-2", "H6-3", "H6-4", "Abs. safety", "H6-5"]
    statuses = [data[x]["status"] for x in ("H6-1", "H6-2", "H6-3", "H6-4")]
    statuses += [data["absolute_delay_safety"]["status"], data["H6-5"]["status"]]
    values = [1 if s == "PASS" else 0 for s in statuses]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    bars = ax.bar(labels, values, color=["#2ca02c" if v else "#d62728" for v in values])
    for bar, status in zip(bars, statuses, strict=True):
        ax.text(bar.get_x() + bar.get_width()/2, .5, status, ha="center", va="center",
                rotation=90, color="white", fontweight="bold")
    ax.set(ylim=(0, 1.05), ylabel="frozen gate", title="E. Joint L4R-06 criterion summary")
    ax.set_yticks([0, 1], ["FAIL", "PASS"]); ax.grid(axis="y", alpha=.25)
    _save(fig, output / NAMES[4])

    files = {name: hashlib.sha256((output / name).read_bytes()).hexdigest() for name in NAMES}
    return {
        "schema": "rebaseguard.l4r06-figure-manifest.v1",
        "source": "results/scientific_findings.json",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory(prefix="l4r06-figures-") as tmp:
            got = generate(output=Path(tmp))
        expected_path = RESULTS / "figure_manifest.json"
        if not expected_path.exists() or json.loads(expected_path.read_text()) != got:
            print("L4R-06 figures are not byte-stable")
            return 1
        print("L4R-06 figures: byte-stable")
        return 0
    manifest = generate()
    (RESULTS / "figure_manifest.json").write_text(canonical_json(manifest))
    print(f"generated {len(NAMES)} figures from {manifest['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
