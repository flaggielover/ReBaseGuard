"""Stage C figures.

Visual convention, applied consistently:

* **solid black**       Monte Carlo estimate from this stage
* **shaded grey band**  a CERTIFIED quantity carried in from Level 1-3
                        (the enclosure of rho_c implied by the Gamma certificate)
* **dash-dot line**     the ReBaseGuard policy location (a DEFINITION, fixed
                        before evaluation)
* **open marker**       the ORACLE point (post-hoc, not a proposed method)

Nothing certified is ever drawn in the same style as something estimated.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

PROOF_ROLE = ("Monte Carlo unless marked certified; the certified band is the "
              "frozen Level 1-3 Gamma enclosure")

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 200, "savefig.bbox": "tight",
    "font.size": 9, "axes.grid": True, "grid.alpha": 0.25,
    "grid.linewidth": 0.5, "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "lines.linewidth": 1.3, "errorbar.capsize": 2.0,
})

RHO_C_POINT = 0.067178
RHO_C_CERT = (0.037245, 0.341957)


def _finish(fig, path: Path, caption: str) -> Path:
    fig.text(0.005, 0.002, f"{PROOF_ROLE}. {caption}", fontsize=6, alpha=0.65,
             ha="left", va="bottom")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return path


def _stability_annotations(ax, rbg_rho: float, rbg_label: str,
                           oracle_rho: float | None = None,
                           oracle_y: float | None = None) -> None:
    ax.axvspan(RHO_C_CERT[0], RHO_C_CERT[1], color="0.55", alpha=0.15, lw=0,
               label=r"certified $\rho_c$ enclosure")
    ax.axvline(RHO_C_POINT, ls=":", lw=1.0, color="0.35",
               label=rf"$\rho_c$ point est. = {RHO_C_POINT:.4f}")
    ax.axvline(rbg_rho, ls="-.", lw=1.2, color="0.15", label=rbg_label)
    if oracle_rho is not None and oracle_y is not None:
        ax.plot([oracle_rho], [oracle_y], marker="o", ms=8, mfc="none",
                mec="0.1", mew=1.4, ls="none", label="ORACLE (post-hoc)")


def fig_metric_vs_rho(rows: Sequence[dict], metric: str, ylabel: str,
                      path: Path, *, title: str, rbg_rho: float,
                      rbg_label: str, ci_key: str | None = None,
                      oracle_rho: float | None = None,
                      reference: float | None = None,
                      reference_label: str | None = None,
                      logx: bool = True) -> Path:
    rows = sorted(rows, key=lambda r: r["rho"])
    x = np.array([r["rho"] for r in rows])
    y = np.array([r[metric] for r in rows])
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    oracle_y = None
    if oracle_rho is not None:
        j = int(np.argmin(np.abs(x - oracle_rho)))
        oracle_y = float(y[j])
    _stability_annotations(ax, rbg_rho, rbg_label, oracle_rho, oracle_y)
    if reference is not None:
        ax.axhline(reference, ls="--", lw=0.9, color="0.45",
                   label=reference_label or "reference")
    if ci_key and ci_key in rows[0]:
        lo = np.array([r[ci_key][0] for r in rows])
        hi = np.array([r[ci_key][1] for r in rows])
        ax.errorbar(x, y, yerr=np.vstack([y - lo, hi - y]), marker="o", ms=3.5,
                    color="0.1", label="Monte Carlo estimate")
    else:
        ax.plot(x, y, marker="o", ms=3.5, color="0.1",
                label="Monte Carlo estimate")
    if logx:
        ax.set_xscale("symlog", linthresh=0.01)
    ax.set_xlabel(r"reuse fraction $\rho$")
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=10)
    ax.legend(fontsize=7, ncol=2)
    return _finish(fig, path, "error bars are 95% percentile bootstrap over "
                              "replicates (the statistical unit)")


def fig_detection(rows: Sequence[dict], shifts: Sequence[float], path: Path, *,
                  rbg_rho: float, rbg_label: str) -> Path:
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    _stability_annotations(ax, rbg_rho, rbg_label)
    for shift in shifts:
        sel = sorted([r for r in rows if abs(r["shift"] - shift) < 1e-12],
                     key=lambda r: r["rho"])
        if not sel:
            continue
        x = np.array([r["rho"] for r in sel])
        y = np.array([r["delay_mean"] for r in sel])
        e = np.array([r["delay_se"] for r in sel])
        label = (r"in control ($\Delta=0$)" if shift == 0
                 else rf"$\Delta={shift:g}$")
        ax.errorbar(x, y, yerr=1.96 * e, marker="o", ms=3.0, label=label)
    ax.set_xscale("symlog", linthresh=0.01)
    ax.set_yscale("log")
    ax.set_xlabel(r"reuse fraction $\rho$")
    ax.set_ylabel("mean detection delay (observations)")
    ax.set_title("Detection delay against reuse fraction", fontsize=10)
    ax.legend(fontsize=7, ncol=2)
    return _finish(fig, path, "the top curve is the in-control control arm; "
                              "delay must be read jointly with ARL, never alone")


def fig_pareto(rows: Sequence[dict], delays: Sequence[dict], path: Path, *,
               shift: float, rbg_rho: float, oracle_rho: float,
               front: Sequence[int]) -> Path:
    rows = sorted(rows, key=lambda r: r["rho"])
    arl = np.array([r["cycle_arl"] for r in rows])
    x = np.array([r["rho"] for r in rows])
    d = []
    for r in rows:
        m = [q for q in delays
             if abs(q["rho"] - r["rho"]) < 1e-9 and abs(q["shift"] - shift) < 1e-12]
        d.append(m[0]["delay_mean"] if m else np.nan)
    d = np.array(d)
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    sc = ax.scatter(arl, d, c=np.log10(np.maximum(x, 1e-3)), cmap="viridis",
                    s=34, zorder=3)
    for i, r in enumerate(rows):
        if r["rho"] in (0.0, 1.0) or abs(r["rho"] - rbg_rho) < 1e-9 \
                or abs(r["rho"] - oracle_rho) < 1e-9:
            ax.annotate(rf"$\rho$={r['rho']:g}", (arl[i], d[i]),
                        textcoords="offset points", xytext=(6, 4), fontsize=7)
    if front:
        ax.plot(arl[list(front)], d[list(front)], ls="--", lw=1.0, color="0.3",
                zorder=2, label="Pareto front (high ARL, low delay)")
    j = int(np.argmin(np.abs(x - rbg_rho)))
    ax.plot([arl[j]], [d[j]], marker="D", ms=9, mfc="none", mec="0.05", mew=1.6,
            ls="none", label="ReBaseGuard (defined a priori)")
    k = int(np.argmin(np.abs(x - oracle_rho)))
    ax.plot([arl[k]], [d[k]], marker="o", ms=10, mfc="none", mec="0.35",
            mew=1.4, ls="none", label="ORACLE (post-hoc)")
    fig.colorbar(sc, ax=ax, label=r"$\log_{10}\rho$")
    ax.set_xlabel("in-control cycle ARL (higher is better)")
    ax.set_ylabel(rf"mean detection delay at $\Delta={shift:g}$ (lower is better)")
    ax.set_title("Reuse-performance frontier", fontsize=10)
    ax.legend(fontsize=7, loc="best")
    return _finish(fig, path, "a point is better if it is further right and "
                              "further down; the oracle is a yardstick, not a method")


def fig_stationary_densities(cells: dict[float, dict], path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    for rho, cell in sorted(cells.items()):
        h = cell["e_hist"]
        edges = np.array(h["edges"])
        counts = np.array(h["counts"], dtype=float)
        centres = 0.5 * (edges[1:] + edges[:-1])
        width = edges[1] - edges[0]
        dens = counts / (counts.sum() * width)
        ax.plot(centres, dens, lw=1.2, label=rf"$\rho={rho:g}$")
    ax.set_xlim(-4, 4)
    ax.set_xlabel(r"stationary reference error $e$")
    ax.set_ylabel("empirical density")
    ax.set_title("Stationary reference distribution by reuse fraction",
                 fontsize=10)
    ax.legend(fontsize=7, ncol=2)
    return _finish(fig, path, "empirical (numerical) stationary distribution; "
                              "no claim of rigorous bimodality or of a unique "
                              "invariant law is made")


def fig_a_curve(records: Sequence[dict], path: Path) -> Path:
    e = np.array([r["e"] for r in records])
    a = np.array([r["A"] for r in records])
    se = np.array([r["A_se"] for r in records])
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.errorbar(e, a, yerr=1.96 * se, marker="o", ms=2.2, color="0.1", lw=1.0)
    ax.set_yscale("log")
    ax.set_xlabel(r"reference error $e$")
    ax.set_ylabel(r"$A(e)=\mathbb{E}[\tau\mid E_j=e]$")
    ax.set_title(r"Conditional cycle length $A(e)$", fontsize=10)
    ax.axhline(a[np.argmin(np.abs(e))], ls=":", lw=0.9, color="0.4",
               label=rf"$A(0)={a[np.argmin(np.abs(e))]:.1f}$")
    ax.legend(fontsize=7)
    return _finish(fig, path, "symmetry and monotonicity in |e| are TESTED, "
                              "not assumed; see the report")


def fig_decomposition(rows: Sequence[dict], path: Path, *, rbg_rho: float,
                      rbg_label: str) -> Path:
    rows = sorted(rows, key=lambda r: r["rho"])
    x = np.array([r["rho"] for r in rows])
    gap = np.array([r["arl_paired_gap"] for r in rows])
    lo = np.array([r["arl_paired_gap_ci"][0] for r in rows])
    hi = np.array([r["arl_paired_gap_ci"][1] for r in rows])
    fig, axes = plt.subplots(2, 1, figsize=(6.4, 5.2), sharex=True,
                             height_ratios=[2, 1])
    ax = axes[0]
    ax.plot(x, [r["cycle_arl"] for r in rows], marker="o", ms=3.5, color="0.1",
            label=r"direct  $\overline{\tau}$")
    ax.plot(x, [r["arl_decomposition"] for r in rows], marker="s", ms=3.5,
            ls="--", color="0.45", label=r"decomposition  $\mathbb{E}_\pi[A(e)]$")
    ax.axvline(rbg_rho, ls="-.", lw=1.2, color="0.15", label=rbg_label)
    ax.set_ylabel("in-control cycle ARL")
    ax.set_title("Direct ARL vs stationary decomposition", fontsize=10)
    ax.legend(fontsize=7)
    ax2 = axes[1]
    ax2.axhline(0.0, color="0.5", lw=0.8)
    ax2.errorbar(x, gap, yerr=np.vstack([gap - lo, hi - gap]), marker="o",
                 ms=3.5, color="0.1")
    ax2.set_xscale("symlog", linthresh=0.01)
    ax2.set_xlabel(r"reuse fraction $\rho$")
    ax2.set_ylabel("paired gap")
    return _finish(fig, path, "the gap is a PAIRED replicate-level contrast: "
                              "both routes use the same cycles")


def fig_stability_boundary(rows: Sequence[dict], path: Path, *,
                           policy_rows: Sequence[dict]) -> Path:
    rows = sorted(rows, key=lambda r: r["rho"])
    x = np.array([r["rho"] for r in rows])
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.axvspan(RHO_C_CERT[0], RHO_C_CERT[1], color="0.55", alpha=0.15, lw=0,
               label=r"certified $\rho_c$ enclosure (Level 1-3)")
    ax.axvline(RHO_C_POINT, ls=":", lw=1.0, color="0.35",
               label=rf"$\rho_c$ point est. = {RHO_C_POINT:.4f}")
    slope = x * (1.0 - 15.885729)
    ax.plot(x, np.abs(slope), marker="o", ms=3.0, color="0.1",
            label=r"$|F'_\rho(0)| = \rho(\Gamma-1)$ (point $\Gamma$)")
    ax.plot(x, x * (27.849382 - 1.0), ls="--", lw=1.0, color="0.4",
            label=r"worst case over the certified $\Gamma$")
    ax.axhline(1.0, ls="-", lw=1.0, color="0.2",
               label=r"local stability boundary $|F'_\rho(0)|=1$")
    for row in policy_rows:
        if row["delta"] != 0.2:
            continue
        style = "-." if row["variant"] == "conservative" else (0, (4, 2))
        ax.axvline(row["rho"], ls=style, lw=1.2, color="0.15",
                   label=f"ReBaseGuard {row['variant']} "
                         rf"($\delta=0.2$, $\rho={row['rho']:.4f}$)")
    ax.set_xscale("symlog", linthresh=0.01)
    ax.set_yscale("log")
    ax.set_ylim(1e-3, 1e2)
    ax.set_xlabel(r"reuse fraction $\rho$")
    ax.set_ylabel(r"$|F'_\rho(0)|$")
    ax.set_title("Local stability boundary and the ReBaseGuard policy",
                 fontsize=10)
    ax.legend(fontsize=6.5, loc="upper left")
    return _finish(fig, path, "the certified band is wide because the frozen "
                              "Gamma enclosure is wide; the conservative policy "
                              "is safe across ALL of it")
