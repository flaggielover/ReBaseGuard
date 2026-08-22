"""Stage E figures. Generated from results/*.json ONLY -- no re-simulation.

Every panel carries the reliability status of the endpoint it draws, so an
UNRELIABLE or LOW-POWER quantity cannot be read as if it were a valid estimate.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                        # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
FIG = ROOT / "figures"

TASKS = [("electricity", "Task A - Electricity/Elec2", "usable"),
         ("air_quality", "Task B - UCI Air Quality", "LOW-POWER"),
         ("bike_sharing", "Task C - UCI Bike Sharing", "E2/E3 UNRELIABLE")]
POLS = ["P0_fresh", "P1_full_reuse", "P2_rebaseguard", "P3_moderate_EXPLORATORY"]
LAB = {"P0_fresh": "P0 fresh", "P1_full_reuse": "P1 full reuse",
       "P2_rebaseguard": "P2 ReBaseGuard", "P3_moderate_EXPLORATORY": "P3 expl.*"}
COL = {"P0_fresh": "#4C72B0", "P1_full_reuse": "#C44E52",
       "P2_rebaseguard": "#55A868", "P3_moderate_EXPLORATORY": "#B0B0B0"}


def load(n):
    p = RES / n
    return json.loads(p.read_text()) if p.exists() else None


def fig1_e1():
    """E1 baseline-normalised response, all tasks, all policies."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    for ax, (t, title, flag) in zip(axes, TASKS):
        a = load(f"task_{t}_confirmatory_analysis.json")
        if a is None:
            continue
        conds = list(a["E1"])
        x = np.arange(len(conds))
        w = 0.2
        for i, p in enumerate(POLS):
            v = [a["E1"][c][p]["R_delta"] for c in conds]
            lo = [a["E1"][c][p]["R_delta"] - a["E1"][c][p]["ci"][0] for c in conds]
            hi = [a["E1"][c][p]["ci"][1] - a["E1"][c][p]["R_delta"] for c in conds]
            ax.bar(x + (i - 1.5) * w, v, w, yerr=[lo, hi], capsize=2,
                   color=COL[p], label=LAB[p],
                   hatch="//" if p.endswith("EXPLORATORY") else None)
        ax.axhline(1.0, color="gray", lw=1, ls="--")
        ax.set_xticks(x)
        ax.set_xticklabels([c.replace("_", "\n") for c in conds], fontsize=7.5)
        ax.set_ylabel(r"$R_\Delta$  (lower = faster)")
        blocks = a["E1"][conds[0]]["P0_fresh"]["n_blocks_effective"]
        ax.set_title(f"{title}\nE1 USABLE, {blocks} eff. blocks", fontsize=9)
        ax.grid(alpha=.3, axis="y")
    axes[0].legend(fontsize=7)
    fig.suptitle("Stage E — E1 baseline-normalised detection response "
                 "(matched-wait denominator).  *P3 EXPLORATORY, excluded from closure",
                 y=1.02, fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "fig1_E1_response.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def fig2_noninferiority():
    """H-E3: upper 95% excess of P2 over P0 against both frozen margins."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    for ax, (t, title, flag) in zip(axes, TASKS):
        a = load(f"task_{t}_confirmatory_analysis.json")
        if a is None:
            continue
        h3 = a["H_E3_non_inferiority"]
        conds = list(h3)
        y = np.arange(len(conds))
        up = [h3[c]["upper95_excess"] for c in conds]
        pt = [h3[c]["excess_over_fresh"] for c in conds]
        cols = ["#55A868" if h3[c]["non_inferior_eps_0.10"] else "#C44E52"
                for c in conds]
        ax.barh(y, up, color=cols, alpha=.85, label="upper 95% excess")
        ax.plot(pt, y, "ko", ms=5, label="point estimate")
        ax.axvline(0.10, color="darkorange", ls="--", lw=1.4,
                   label=r"$\epsilon=0.10$ (primary)")
        ax.axvline(0.05, color="purple", ls=":", lw=1.4,
                   label=r"$\epsilon=0.05$ (secondary)")
        ax.axvline(0.0, color="gray", lw=1)
        ax.set_yticks(y)
        ax.set_yticklabels(conds, fontsize=8)
        ax.set_xlabel(r"excess of $R_\Delta$(P2) over $R_\Delta$(P0)")
        ax.set_title(f"{title}", fontsize=9)
        ax.grid(alpha=.3, axis="x")
    axes[0].legend(fontsize=6.5, loc="lower right")
    fig.suptitle("Stage E — H-E3 non-inferiority of ReBaseGuard vs fresh. "
                 "Green = PASS at $\\epsilon=0.10$. "
                 "Failure to demonstrate non-inferiority is NOT inferiority.",
                 y=1.03, fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "fig2_noninferiority.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def fig3_reference_error():
    """E2 reference-state error, with reliability status stamped on each panel."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    for ax, (t, title, flag) in zip(axes, TASKS):
        a = load(f"task_{t}_confirmatory_analysis.json")
        if a is None:
            continue
        vals = [a["E2"][p]["mean"] for p in POLS]
        rel = [a["E2"][p]["reliable"] for p in POLS]
        blk = [a["E2"][p]["n_blocks_effective"] for p in POLS]
        lo = [a["E2"][p]["mean"] - a["E2"][p]["ci"][0] for p in POLS]
        hi = [a["E2"][p]["ci"][1] - a["E2"][p]["mean"] for p in POLS]
        x = np.arange(len(POLS))
        for i, p in enumerate(POLS):
            if rel[i]:
                ax.bar(x[i], vals[i], .62, yerr=[[lo[i]], [hi[i]]], capsize=3,
                       color=COL[p],
                       hatch="//" if p.endswith("EXPLORATORY") else None)
            else:
                ax.bar(x[i], vals[i], .62, color=COL[p], alpha=.45,
                       edgecolor="black", linestyle=":", linewidth=1.4,
                       hatch="xx")
        ax.set_xticks(x)
        ax.set_xticklabels([LAB[p] for p in POLS], rotation=18, fontsize=7.5)
        ax.set_ylabel(r"$E_2 = |R_j - $ local mean$|$")
        allrel = all(rel[:3])
        status = ("E2 USABLE" if allrel and min(blk[:3]) > 5 else
                  "E2 LOW-POWER (at floor)" if allrel else
                  "E2 UNRELIABLE — below floor")
        ax.set_title(f"{title}\n{status}  (blocks {blk})", fontsize=9)
        ax.grid(alpha=.3, axis="y")
    fig.suptitle("Stage E — E2 reference-state error. Hatched/faded bars are "
                 "BELOW the pre-specified effective-block floor and their "
                 "intervals are not valid inferential evidence.",
                 y=1.03, fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "fig3_reference_error.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def fig4_delay():
    """E4 absolute detection delay beside E1, as the protocol requires."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    for ax, (t, title, flag) in zip(axes, TASKS):
        a = load(f"task_{t}_confirmatory_analysis.json")
        if a is None:
            continue
        conds = list(a["E1"])
        x = np.arange(len(conds))
        for p in POLS:
            v = [a["E1"][c][p]["E4_delay"] for c in conds]
            ax.plot(x, v, marker="o", color=COL[p], label=LAB[p],
                    ls="--" if p.endswith("EXPLORATORY") else "-")
        ax.set_xticks(x)
        ax.set_xticklabels([c.replace("_", "\n") for c in conds], fontsize=7.5)
        ax.set_ylabel("E4 absolute delay (observations)")
        ax.set_title(f"{title}\nE4 USABLE", fontsize=9)
        ax.grid(alpha=.3)
    axes[0].legend(fontsize=7)
    fig.suptitle("Stage E — E4 absolute detection delay. A short raw delay is "
                 "not better discrimination if the policy also alarms rapidly "
                 "without drift (see E2/E3).", y=1.03, fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "fig4_delay.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    made = []
    for fn, name in ((fig1_e1, "fig1_E1_response.png"),
                     (fig2_noninferiority, "fig2_noninferiority.png"),
                     (fig3_reference_error, "fig3_reference_error.png"),
                     (fig4_delay, "fig4_delay.png")):
        try:
            fn()
            made.append(name)
            print(f"  wrote figures/{name}")
        except Exception as exc:            # a missing task must not kill the rest
            print(f"  SKIPPED {name}: {exc}")
    return made


if __name__ == "__main__":
    main()
