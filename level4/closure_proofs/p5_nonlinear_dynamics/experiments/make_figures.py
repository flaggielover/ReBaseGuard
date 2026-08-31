#!/usr/bin/env python3
"""P5 figures."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                   # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p5 import RESULTS, FIGURES                       # noqa: E402

plt.rcParams.update({"figure.dpi": 130, "font.size": 8,
                     "axes.grid": True, "grid.alpha": 0.25})


def pooled(det, m):
    acc = {}
    for f in ("nonlinear_map.json", "nonlinear_map_rep.json", "map_tail.json"):
        d = json.loads((RESULTS / f).read_text())
        for r in d["rows"]:
            if r["detector"] != det:
                continue
            q = [q for q in r["per_m"] if q["m"] == m][0]
            acc.setdefault(round(r["e"], 6), []).append(
                (q["R"], q["R_se"], q["S"]))
    xs = np.array(sorted(acc))
    R = np.array([float(np.average([v[0] for v in acc[x]],
                                   weights=[1 / v[1] ** 2 for v in acc[x]]))
                  for x in xs])
    se = np.array([float(np.sqrt(1 / sum(1 / v[1] ** 2 for v in acc[x])))
                   for x in xs])
    S = np.array([float(np.mean([v[2] for v in acc[x]])) for x in xs])
    return xs, R, se, S


def fig_map():
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.2))
    for det, ls in (("cusum", "-"), ("sr", "--")):
        for m, c in ((1, "C0"), (3, "C1"), (5, "C2")):
            x, R, se, S = pooled(det, m)
            lab = f"{det.upper()} m={m}"
            ax[0].plot(x, R, ls, color=c, lw=1.2, label=lab)
            ax[0].fill_between(x, R - 1.96 * se, R + 1.96 * se, color=c,
                               alpha=0.25, lw=0)
            k = np.abs(x) <= 0.12
            ax[1].plot(x[k], R[k], ls, color=c, lw=1.2)
            p = x > 0
            ax[2].semilogy(x[p], -R[p] / x[p], ls, color=c, lw=1.2)
    a3 = json.loads((RESULTS / "map_analysis.json").read_text())
    for c in a3["cells"]:
        if c["m"] == 1 and c["detector"] == "cusum":
            xx = np.linspace(-0.12, 0.12, 5)
            ax[1].plot(xx, c["p3_one_minus_gamma"] * xx, ":k", lw=1.0,
                       label="P3 tangent $(1-\\tilde\\Gamma)e$")
    ax[2].axhline(1.0, color="k", ls=":", lw=1)
    ax[2].text(0.011, 1.15, "$1/\\rho=1$ (full reuse)", fontsize=7)
    ax[0].set(xlabel="entering reference error $e$", ylabel="$R(e)=E[\\bar R\\,|\\,e]$",
              title="(a) the fixed map: saturation and total forgetting",
              xlim=(-12, 12))
    ax[1].set(xlabel="$e$", ylabel="$R(e)$",
              title="(b) linear core recovers the P3 multiplier")
    ax[2].set(xlabel="$e>0$", ylabel="secant gain $s(e)=-R(e)/e$",
              title="(c) $s$ decreasing: 2-cycles solve $s(e^*)=1/\\rho$",
              xscale="log", xlim=(0.004, 6))
    ax[0].legend(fontsize=6, ncol=2)
    ax[1].legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(FIGURES / "p5_nonlinear_map.png")
    plt.close(fig)


def fig_bifurcation():
    ch = json.loads((RESULTS / "chain_analysis.json").read_text())["cells"]
    an = json.loads((RESULTS / "map_analysis.json").read_text())["cells"]
    sk = json.loads((RESULTS / "skeleton_scan.json").read_text())["cells"]
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.2))
    for det, m, c in (("cusum", 1, "C0"), ("cusum", 5, "C2"), ("sr", 1, "C3")):
        s = [x for x in sk if x["detector"] == det and x["m"] == m][0]["rows"]
        rr = np.array([r["rho"] for r in s])
        aa = np.array([r["amp_max"] for r in s])
        ax[0].plot(rr, aa, color=c, lw=1.3, label=f"{det.upper()} m={m} skeleton $e^*$")
        ax[0].plot(rr, -aa, color=c, lw=1.3)
        rows = sorted([r for r in ch if r["detector"] == det and r["m"] == m],
                      key=lambda r: r["rho"])
        x = np.array([r["rho"] for r in rows])
        q = np.array([r["q95"] for r in rows])
        ax[0].plot(x, q, color=c, ls=":", lw=1.0,
                   label=f"{det.upper()} m={m} chain $q_{{95}}(|e|)$")
        ax[0].plot(x, -q, color=c, ls=":", lw=1.0)
        rc = rows[0]["rho_crit"]
        ax[0].axvline(rc, color=c, ls="--", lw=0.7, alpha=0.6)
        b = [x for x in an if x["detector"] == det and x["m"] == m][0]["branch"]
        bb = [q for q in b if q["exists"]]
        ax[1].plot([q["rho"] for q in bb], [q["snr"] for q in bb], color=c,
                   marker="o", ms=2.5, lw=1.2, label=f"{det.upper()} m={m}")
        ax[2].errorbar(x, [r["rms"] for r in rows],
                       yerr=[1.96 * r["rms_se"] for r in rows], color=c,
                       lw=1.2, ms=2.5, marker="o", label=f"{det.upper()} m={m}")
        ax[2].axvline(rc, color=c, ls="--", lw=0.7, alpha=0.6)
    ax[1].axhline(1.0, color="k", ls=":", lw=1)
    ax[0].set(xlabel="reuse fraction $\\rho$", ylabel="reference error",
              title="(a) flip bifurcation at $\\rho_c$, buried in the chain",
              xlim=(0, 1))
    ax[1].set(xlabel="$\\rho$", ylabel="$e^*/\\sqrt{V(e^*)}$",
              title="(b) skeleton signal-to-noise never exceeds ~2",
              xlim=(0, 1), ylim=(0, 2.6))
    ax[2].set(xlabel="$\\rho$", ylabel="stationary RMS$(e)$",
              title="(c) dispersion law: smooth, no feature at $\\rho_c$",
              xlim=(0, 1))
    for a in ax:
        a.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(FIGURES / "p5_bifurcation_and_dispersion.png")
    plt.close(fig)


def fig_density():
    d = json.loads((RESULTS / "density.json").read_text())
    cells = [("cusum", 1), ("cusum", 3), ("sr", 5)]
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.3))
    for k, (det, m) in enumerate(cells):
        for rho, c in ((0.3, "C0"), (0.5, "C1"), (0.8, "C3"), (1.0, "C4")):
            r = [x for x in d["rows"] if x["detector"] == det
                 and x["m"] == m and abs(x["rho"] - rho) < 1e-9]
            if not r:
                continue
            r = r[0]
            x = np.array(r["centers"]); y = np.array(r["density"])
            se = np.array(r["density_se"])
            ax[k].plot(x, y, color=c, lw=1.1, label=f"$\\rho$={rho}")
            ax[k].fill_between(x, y - 1.96 * se, y + 1.96 * se, color=c,
                               alpha=0.25, lw=0)
            if np.isfinite(r["e_star"]):
                for sgn in (1, -1):
                    ax[k].axvline(sgn * r["e_star"], color=c, ls="--", lw=0.7,
                                  alpha=0.6)
        ax[k].set(xlabel="stationary reference error $e$", ylabel="density",
                  xlim=(-3, 3),
                  title=f"{det.upper()} m={m}\ndashed = skeleton 2-cycle $\\pm e^*$")
        ax[k].legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(FIGURES / "p5_stationary_density.png")
    plt.close(fig)


def fig_crossover():
    rows = []
    for f in ("density.json", "density_crossover.json"):
        if (RESULTS / f).exists():
            rows += json.loads((RESULTS / f).read_text())["rows"]
    fig, ax = plt.subplots(figsize=(4.6, 3.3))
    for (det, m), c in ((("cusum", 1), "C0"), (("cusum", 3), "C1"),
                        (("sr", 1), "C3"), (("sr", 5), "C2")):
        r = sorted([x for x in rows if x["detector"] == det and x["m"] == m],
                   key=lambda x: x["rho"])
        if len(r) < 3:
            continue
        ax.errorbar([x["rho"] for x in r], [x["contrast_mean"] for x in r],
                    yerr=[1.96 * x["contrast_se"] for x in r], color=c,
                    marker="o", ms=3, lw=1.2, label=f"{det.upper()} m={m}")
    ax.axhline(0.0, color="k", lw=1, ls=":")
    ax.set(xlabel="reuse fraction $\\rho$",
           ylabel="density$(\\pm e^*)$ - density$(0)$",
           title="bimodality onset: mass moves onto the\n2-cycle only far above $\\rho_c$ ($\\approx 0.06-0.11$)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGURES / "p5_bimodality_onset.png")
    plt.close(fig)


if __name__ == "__main__":
    FIGURES.mkdir(exist_ok=True)
    fig_map()
    print("p5_nonlinear_map.png")
    if (RESULTS / "chain_analysis.json").exists():
        fig_bifurcation(); print("p5_bifurcation_and_dispersion.png")
        fig_density(); print("p5_stationary_density.png")
        fig_crossover(); print("p5_bimodality_onset.png")
