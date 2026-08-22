"""Stage D figures. Every panel is generated from the confirmatory JSON only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                        # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
FIG = ROOT / "figures"


def load(n):
    p = RES / n
    return json.loads(p.read_text()) if p.exists() else None


def fig_a(d2):
    ms = [r["m"] for r in d2["rows"]]
    ga = [r["A"]["gamma_m"] for r in d2["rows"]]
    gb = [r["B"]["gamma_m"] for r in d2["rows"]]
    ea = [1.96 * r["A"]["se"] for r in d2["rows"]]
    br = d2["d2_2_bracket"]
    fig, ax = plt.subplots(figsize=(7, 4.6))
    ax.errorbar(ms, ga, yerr=ea, marker="o", lw=1.6, capsize=3,
                label=r"convention A (frozen): $w=\min(m,\tau)$")
    ax.plot(ms, gb, marker="s", ls="--", lw=1.3, alpha=.75,
            label=r"convention B (diagnostic): denominator $m$")
    ax.axhline(2.0, color="crimson", lw=1.2, ls=":",
               label=r"$\Gamma_m=2$  ($\rho_c=1$)")
    ax.axvspan(br["m_lo"], br["m_hi"], color="crimson", alpha=.10,
               label=fr"D2.2 bracket $m^*\in[{br['m_lo']},{br['m_hi']}]$")
    ax.axhline(d2["d2_4_asymptote"]["gamma_inf_A_E_Tsq_over_tau"],
               color="gray", lw=1, ls="-.",
               label=r"$\Gamma_\infty=E[T_\tau^2/\tau]$ (numerical)")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("stopped-window length $m$")
    ax.set_ylabel(r"$\Gamma_m$")
    ax.set_title(r"A — $\Gamma_m$ and the $\Gamma_m=2$ crossing (frozen CUSUM)")
    ax.legend(fontsize=7.5, loc="lower left"); ax.grid(alpha=.3, which="both")
    fig.tight_layout(); fig.savefig(FIG / "fig_A_gamma_m.png", dpi=160)
    plt.close(fig)


def fig_b(d2):
    lag = d2["d2_1_lag"]["gamma_first_10"]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.bar(range(len(lag)), lag, color="steelblue")
    ax.set_xlabel(r"lag $i$ (0 = terminal observation)")
    ax.set_ylabel(r"$\gamma_i=E[z_{\tau-i}\,\mathbf{1}\{i<\tau\}\,T_\tau]$")
    ax.set_title(r"B — lag decomposition; $\sum_i\gamma_i=E[T_\tau^2]=\mathrm{ARL}_0$"
                 f"  (ratio {d2['d2_1_lag']['wald_ratio_ETsq_over_arl0']:.5f})")
    ax.grid(alpha=.3, axis="y")
    fig.tight_layout(); fig.savefig(FIG / "fig_B_lag_decay.png", dpi=160)
    plt.close(fig)


def fig_c(d23):
    ms = [r["m"] for r in d23["rows"]]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4))
    tgt = [r["target_1_minus_gamma"] for r in d23["rows"]]
    a1.plot(ms, tgt, "k-", marker="o", label=r"$1-\Gamma_m$ (target)")
    for h, mk in (("0.1", "^"), ("0.05", "s"), ("0.025", "v")):
        a1.plot(ms, [r["by_step"][h]["deriv"] for r in d23["rows"]],
                marker=mk, ls="--", alpha=.8, label=fr"central diff, $h={h}$")
    a1.plot(ms, [r["richardson_diagnostic"] for r in d23["rows"]],
            marker="*", ls=":", color="crimson",
            label="Richardson (diagnostic only)")
    a1.set_xscale("log"); a1.set_xlabel("$m$"); a1.set_ylabel(r"$F'_{1,m}(0)$")
    a1.set_title("C1 — D2.3: FAILED at the primary step $h=0.05$")
    a1.legend(fontsize=7.5); a1.grid(alpha=.3)

    hs = np.array([0.025, 0.05, 0.1])
    for r in d23["rows"]:
        a2.loglog(hs, [abs(r["by_step"][str(h)]["discrepancy"]) for h in hs],
                  marker="o", alpha=.75, label=f"m={r['m']}")
    a2.loglog(hs, 80 * hs ** 2, "k--", lw=1.4, label=r"$O(h^2)$ reference")
    a2.set_xlabel("finite-difference step $h$")
    a2.set_ylabel(r"$|$discrepancy$|$")
    a2.set_title("C2 — discrepancy is $O(h^2)$: a truncation artifact,\n"
                 "the diagnosis, NOT a reversal of the failure")
    a2.legend(fontsize=7, ncol=2); a2.grid(alpha=.3, which="both")
    fig.tight_layout(); fig.savefig(FIG / "fig_C_derivative.png", dpi=160)
    plt.close(fig)


def fig_d(d25):
    rows = d25["rows"]
    ms = [r["m"] for r in rows]
    ms_ = d25["m_star_interp"]
    panels = [("cycle_arl", "in-control cycle ARL"),
              ("reference_mse", r"reference MSE $E[e^2]$"),
              ("e_acf1", r"lag-1 ACF of $e_j$"),
              ("direction_acf1", "lag-1 ACF of alarm direction")]
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.4))
    for ax, (k, lab) in zip(axes.flat, panels):
        v = [r[k]["mean"] for r in rows]
        e = [1.96 * r[k]["se"] for r in rows]
        ax.errorbar(ms, v, yerr=e, marker="o", capsize=3)
        ax.axvline(ms_, color="crimson", ls=":", lw=1.4, label=f"$m^*={ms_:.1f}$")
        ax.axvspan(*d25["m_star_bracket"], color="crimson", alpha=.10)
        ax.set_xlabel("$m$"); ax.set_ylabel(lab); ax.grid(alpha=.3)
        ax.legend(fontsize=7.5)
    ax = axes.flat[4]
    for sh in d25["shifts"]:
        ax.errorbar(ms, [r["R_delta"][str(sh)]["R"] for r in rows],
                    marker="o", capsize=3, label=fr"$\Delta={sh}$")
    ax.axvline(ms_, color="crimson", ls=":", lw=1.4)
    ax.axhline(1.0, color="gray", lw=1, ls="--")
    ax.set_xlabel("$m$"); ax.set_ylabel(r"$R_\Delta$"); ax.grid(alpha=.3)
    ax.legend(fontsize=7.5)
    axes.flat[5].axis("off")
    axes.flat[5].text(0.02, 0.5, d25.get("verdict_text", ""), fontsize=8.5,
                      va="center", wrap=True, transform=axes.flat[5].transAxes)
    fig.suptitle("D — monitoring bridge at $\\rho=1$: metrics across the "
                 "$\\Gamma_m=2$ crossing", y=.99)
    fig.tight_layout(); fig.savefig(FIG / "fig_D_bridge.png", dpi=160)
    plt.close(fig)


def fig_e(d3):
    rows = d3["rows"]
    names = [r["family"] for r in rows]
    x = np.arange(len(names))
    gp = [r["per_m"][0]["gamma_psi"] for r in rows]
    ep = [1.96 * r["per_m"][0]["se"] for r in rows]
    gn = [r["per_m"][0]["gamma_psi_normalised"] for r in rows]
    gt = [r["per_m"][0]["gamma_T_naive_DIAGNOSTIC_ONLY"] for r in rows]
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.bar(x - .26, gp, .26, yerr=ep, capsize=3, label=r"$\Gamma_\psi$ (frozen estimand)")
    ax.bar(x, gn, .26, label=r"$\Gamma_\psi/E[\psi']$ (stability-relevant, A5)")
    ax.bar(x + .26, gt, .26, color="lightgray", hatch="//", edgecolor="dimgray",
           label=r"naive $\Gamma_T$ — DIAGNOSTIC ONLY, not evidence")
    ax.axhline(2.0, color="crimson", ls=":", lw=1.4, label=r"threshold 2")
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=15)
    ax.set_ylabel(r"$\Gamma$ at $m=1$, ARL$_0$-matched")
    ax.set_title("E — D3: non-Gaussian families (numerical robustness only;\n"
                 "NOT distribution-free, NOT universal)")
    ax.legend(fontsize=7.5); ax.grid(alpha=.3, axis="y")
    fig.tight_layout(); fig.savefig(FIG / "fig_E_nongaussian.png", dpi=160)
    plt.close(fig)


def fig_f(d1, d14):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4))
    for k, lab in (("cusum", "CUSUM $h=5$"), ("sr", "SR $A$ (ARL$_0$-matched)")):
        a1.bar(lab, d1[k]["gamma"], yerr=1.96 * d1[k]["se"], capsize=4)
    a1.axhline(2.0, color="crimson", ls=":", label="threshold 2")
    a1.set_ylabel(r"$\Gamma$ at $m=1$")
    a1.set_title(f"F1 — D1.3 excess = {d1['d1_3']['difference']:+.4f} "
                 f"$\\pm$ {d1['d1_3']['se']:.4f}\n"
                 "two-detector replication, NOT detector-independence")
    a1.legend(fontsize=8); a1.grid(alpha=.3, axis="y")

    for k, mk in (("sr", "o"), ("cusum", "s")):
        sc = d14[k]["scan"]
        a2.errorbar([p["e"] for p in sc], [p["H"] for p in sc],
                    yerr=[1.96 * p["se"] for p in sc], marker=mk, capsize=2,
                    label=k.upper())
    a2.axhline(0, color="gray", lw=1)
    a2.axvspan(1.028724, 1.044724, color="seagreen", alpha=.18,
               label="Stage B certified enclosure")
    a2.set_xlabel("$e$"); a2.set_ylabel("$H(e)=F(e)+e$")
    a2.set_title("F2 — D1.4 period-2 candidate (Monte Carlo, NOT certified)")
    a2.legend(fontsize=8); a2.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(FIG / "fig_F_detectors.png", dpi=160)
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    made = []
    d2, d23, d25 = load("d2_gamma_m.json"), load("d2_3_derivative.json"), load("d2_5_bridge.json")
    d1, d14, d3 = load("d1_gamma.json"), load("d1_4_sr_map.json"), load("d3_nongaussian.json")
    if d2: fig_a(d2); fig_b(d2); made += ["fig_A_gamma_m.png", "fig_B_lag_decay.png"]
    if d23: fig_c(d23); made.append("fig_C_derivative.png")
    if d25: fig_d(d25); made.append("fig_D_bridge.png")
    if d3: fig_e(d3); made.append("fig_E_nongaussian.png")
    if d1 and d14: fig_f(d1, d14); made.append("fig_F_detectors.png")
    for m in made:
        print(f"  wrote figures/{m}")


if __name__ == "__main__":
    main()
