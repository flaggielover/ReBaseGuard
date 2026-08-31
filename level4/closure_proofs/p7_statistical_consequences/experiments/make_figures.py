"""P7 figures.  Deterministic from results/; no simulation."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                        # noqa: E402
import numpy as np                                                      # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p7.analysis import ResponseCurves, h_grid, load_curves  # noqa: E402
from rebaseguard_p7.config import DETECTORS, FIGURES, M_GRID, RESULTS    # noqa: E402

COL = {1: "#1b6ca8", 2: "#2e9e5b", 3: "#d98324", 5: "#b23a48"}


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    res = json.loads((RESULTS / "consequences.json").read_text())
    cells = res["cells"]
    raw = load_curves()["curves"]
    curves = {d: ResponseCurves(raw[d], M_GRID) for d in DETECTORS}

    def series(d, m, key):
        rows = sorted((c for c in cells if c["detector"] == d and c["m"] == m),
                      key=lambda c: c["rho_over_rhoc"])
        rows = [c for c in rows if c["rho"] > 0]
        return (np.array([c["rho_over_rhoc"] for c in rows]),
                np.array([key(c) for c in rows]))

    # --- A: ARL and reference dispersion against the P3 boundary -----------
    fig, ax = plt.subplots(2, 2, figsize=(11, 7.5), sharex=True)
    for j, d in enumerate(DETECTORS):
        A0 = res["curve_summary"][d]["A0"]
        for m in M_GRID:
            x, y = series(d, m, lambda c: c["arl"])
            fresh = [c for c in cells if c["detector"] == d and c["m"] == m
                     and c["rho"] == 0.0][0]["arl"]
            ax[0, j].plot(x, y / fresh, "o-", color=COL[m], ms=3.5, lw=1.3,
                          label=f"m={m}")
            ax[0, j].axhline(A0 / fresh, color=COL[m], ls=":", lw=0.7, alpha=0.35)
            x, y = series(d, m, lambda c: c["ref_mse"])
            ax[1, j].plot(x, y / fresh * fresh, "o-", color=COL[m], ms=3.5, lw=1.3)
        for a in (ax[0, j], ax[1, j]):
            a.axvline(1.0, color="k", ls="--", lw=1.1)
            a.set_xscale("log")
            a.grid(alpha=0.25, lw=0.5)
        ax[0, j].set_title(f"{d.upper()}")
        ax[0, j].axhline(1.0, color="0.4", lw=0.8)
        ax[1, j].set_xlabel(r"$\rho/\rho_c$  (P3 boundary at 1, dashed)")
    ax[0, 0].set_ylabel("chain $ARL_0$ / fresh-control $ARL_0$")
    ax[1, 0].set_ylabel(r"reference MSE $E_\pi[e^2]$")
    ax[0, 0].legend(fontsize=8, ncol=2)
    fig.suptitle("No localised feature at the P3 critical reuse fraction",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGURES / "p7_arl_and_dispersion_vs_boundary.png", dpi=160)
    plt.close(fig)

    # --- B: the mechanism -- the stopping-selection bias -------------------
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for j, d in enumerate(DETECTORS):
        c = curves[d]
        for m in M_GRID:
            ax[j].plot(c.x, h_grid(c, m), "o-", color=COL[m], ms=3, lw=1.2,
                       label=f"$h_{{{m}}}$")
            gt = c.gamma_tilde[m]
            xx = np.linspace(0, 0.35, 50)
            ax[j].plot(xx, -(gt - 1) * xx, color=COL[m], ls="--", lw=0.9,
                       alpha=0.8)
        rl = res["curve_summary"][d]["linearisation_radius"]["1"]
        ax[j].axvline(rl, color="k", ls=":", lw=1.0)
        ax[j].annotate(r"$r_{\rm lin}$", (rl, -1.7), fontsize=8)
        ax[j].set_xlim(0, 1.0)
        ax[j].set_ylim(-1.8, 0.05)
        ax[j].set_xlabel("reference error $e$")
        ax[j].set_title(f"{d.upper()}: selection bias $h_m$ vs its P3 tangent")
        ax[j].grid(alpha=0.25, lw=0.5)
    ax[0].set_ylabel(r"$h_m(e)=E_e[(1/w)\sum \epsilon_{\tau-r}]$")
    ax[0].legend(fontsize=8, ncol=2)
    fig.suptitle("The P3 multiplier is $\\rho\\,h_m'(0)$; $h_m$ saturates "
                 "far inside the operating range", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGURES / "p7_selection_bias_mechanism.png", dpi=160)
    plt.close(fig)

    # --- C: finite-cycle decay of the calibration promise ------------------
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.0), sharey=True)
    idx = {(c["detector"], c["m"], round(c["rho"], 10)): c for c in cells}
    for j, d in enumerate(DETECTORS):
        A0 = res["curve_summary"][d]["A0"]
        for m in M_GRID:
            for rho, ls in ((0.0, ":"), (1.0, "-")):
                ca = np.array(idx[(d, m, rho)]["cycle_arl"])
                ax[j].plot(np.arange(1, ca.size + 1), ca / A0, ls, color=COL[m],
                           lw=1.3, label=f"m={m}, rho={rho:g}")
        ax[j].axhline(1.0, color="k", lw=0.8)
        ax[j].set_xlim(1, 20)
        ax[j].set_xlabel("cycle index $j$ (chain started at $e_0=0$)")
        ax[j].set_title(d.upper())
        ax[j].grid(alpha=0.25, lw=0.5)
    ax[0].set_ylabel("$ARL_j$ / nominal $A(0)$")
    ax[0].legend(fontsize=7, ncol=2)
    fig.suptitle("The calibrated in-control ARL survives one cycle",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGURES / "p7_finite_cycle_decay.png", dpi=160)
    plt.close(fig)

    # --- D: effective multiplier vs the P3 multiplier ----------------------
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for j, d in enumerate(DETECTORS):
        for m in M_GRID:
            x, y = series(d, m, lambda c: c["e_acf1"])
            _, p = series(d, m, lambda c: c["acf1_predicted_from_gamma_eff"])
            _, q = series(d, m, lambda c: c["acf1_predicted_from_p3_lambda"])
            ax[j].plot(x, y, "o", color=COL[m], ms=4, label=f"m={m} measured")
            ax[j].plot(x, p, "-", color=COL[m], lw=1.1)
            ax[j].plot(x, q, "--", color=COL[m], lw=0.8, alpha=0.6)
        ax[j].axhline(-1.0, color="k", lw=0.9)
        ax[j].axvline(1.0, color="k", ls="--", lw=1.0)
        ax[j].set_xscale("log")
        ax[j].set_yscale("symlog", linthresh=1.0)
        ax[j].set_xlabel(r"$\rho/\rho_c$")
        ax[j].set_title(f"{d.upper()}")
        ax[j].grid(alpha=0.25, lw=0.5)
    ax[0].set_ylabel(r"$ACF_1(e)$")
    ax[0].legend(fontsize=7, ncol=2)
    fig.suptitle("Measured $ACF_1$ (points) matches "
                 r"$\rho(1-\Gamma_{\rm eff})$ (solid); the P3 multiplier "
                 r"$\rho(1-\tilde\Gamma)$ (dashed) overshoots by 5-20x",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(FIGURES / "p7_effective_multiplier.png", dpi=160)
    plt.close(fig)

    index = sorted(p.name for p in FIGURES.glob("*.png"))
    (FIGURES / "figure_index.json").write_text(json.dumps(index, indent=1))
    print("wrote", len(index), "figures")


if __name__ == "__main__":
    main()
