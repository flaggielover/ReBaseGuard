"""Publication-quality, scientifically neutral figures.

Every figure is regenerated from saved result files by a script; none is ever
edited by hand.  Styling is deliberately plain: no colour is used to imply a
verdict, uncertainty is always drawn, and the fresh (rho = 0) control appears in
every comparison where it exists.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

PROOF_ROLE = "Monte Carlo diagnostic — not proof evidence"

plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "font.size": 9,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.frameon": False,
    "lines.linewidth": 1.3,
    "errorbar.capsize": 2.0,
})


def _finish(fig: plt.Figure, path: Path, caption: str) -> Path:
    fig.text(0.005, 0.002, f"{PROOF_ROLE}. {caption}", fontsize=6, alpha=0.65,
             ha="left", va="bottom")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return path


def fig_trajectories(
    trajectories: dict[str, np.ndarray], path: Path, *, n_cycles: int = 120
) -> Path:
    """Figure 1 — multi-cycle reference trajectories, one panel per policy."""
    labels = list(trajectories)
    fig, axes = plt.subplots(len(labels), 1, figsize=(6.5, 1.5 * len(labels)),
                             sharex=True, sharey=True)
    axes = np.atleast_1d(axes)
    for ax, label in zip(axes, labels):
        series = trajectories[label][:n_cycles]
        ax.axhline(0.0, color="0.6", lw=0.7)
        ax.plot(np.arange(series.size), series, marker="o", ms=2.0,
                color="0.15")
        ax.set_ylabel("$E_j$")
        ax.set_title(label, fontsize=8, loc="left")
    axes[-1].set_xlabel("cycle index $j$")
    fig.suptitle("Reference-error trajectories across re-baselining cycles",
                 fontsize=10)
    return _finish(fig, path, "single replicate per panel; seeds in the manifest")


def fig_reference_distributions(
    samples: dict[str, np.ndarray], path: Path, *, bins: int = 121,
    span: float = 4.0
) -> Path:
    """Figure 2 — fresh vs reuse empirical reference distributions."""
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    edges = np.linspace(-span, span, bins)
    for label, values in samples.items():
        ax.hist(values, bins=edges, density=True, histtype="step",
                label=f"{label}  (n={values.size:,})")
    ax.set_xlabel("reference error $E_j$ (post burn-in)")
    ax.set_ylabel("empirical density")
    ax.legend(fontsize=7)
    ax.set_title("Empirical reference-error distribution by re-baselining policy",
                 fontsize=10)
    return _finish(fig, path,
                   "histograms are pooled over replicates; shape claims require "
                   "the replicate-level intervals, not this pool")


def fig_metric_vs_rho(
    rows: Sequence[dict[str, Any]], metric: str, ylabel: str, path: Path,
    *, title: str, reference: float | None = None,
    reference_label: str | None = None, logy: bool = False,
) -> Path:
    """Generic Figure — one metric against rho, one line per m, with 95% CIs."""
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    ms = sorted({row["m"] for row in rows})
    for m in ms:
        sel = sorted((r for r in rows if r["m"] == m), key=lambda r: r["rho"])
        x = np.array([r["rho"] for r in sel])
        y = np.array([r[metric] for r in sel])
        lo = np.array([r[f"{metric}_ci_low"] for r in sel])
        hi = np.array([r[f"{metric}_ci_high"] for r in sel])
        ax.errorbar(x, y, yerr=np.vstack([y - lo, hi - y]), marker="o", ms=3.5,
                    label=f"$m={m}$")
    if reference is not None:
        ax.axhline(reference, ls="--", lw=0.9, color="0.4",
                   label=reference_label or "reference")
    ax.set_xlabel(r"reuse fraction $\rho$")
    ax.set_ylabel(ylabel)
    if logy:
        ax.set_yscale("log")
    ax.legend(fontsize=7)
    ax.set_title(title, fontsize=10)
    return _finish(fig, path, "error bars are 95% percentile bootstrap over "
                              "replicates (the statistical unit)")


def fig_acf(
    curves: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]],
    path: Path, *, title: str, ylabel: str,
) -> Path:
    """Figure — lagged ACF with 95% intervals, one series per policy."""
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    ax.axhline(0.0, color="0.6", lw=0.7)
    for i, (label, (lags, point, err)) in enumerate(curves.items()):
        ax.errorbar(lags + 0.06 * i, point, yerr=err, marker="o", ms=3.5,
                    label=label)
    ax.set_xlabel("lag")
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=7)
    ax.set_title(title, fontsize=10)
    return _finish(fig, path, "95% bootstrap intervals over replicates")


def fig_conditional_map(
    records: Sequence[dict[str, Any]], path: Path, *,
    rho_values: Sequence[float], title: str,
) -> Path:
    """Figure — the F_rho(e) family against the two diagnostic lines y=e, y=-e."""
    e = np.array([r["e"] for r in records])
    order = np.argsort(e)
    e = e[order]
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.plot(e, e, ls=":", lw=0.9, color="0.45", label="$y=e$")
    ax.plot(e, -e, ls="--", lw=0.9, color="0.45", label="$y=-e$")
    for rho in rho_values:
        key = f"F_rho_{rho:g}"
        if key not in records[0]:
            continue
        y = np.array([r[key] for r in records])[order]
        s = np.array([r[f"{key}_se"] for r in records])[order]
        ax.plot(e, y, marker="o", ms=2.5, label=rf"$F_{{\rho={rho:g}}}(e)$")
        ax.fill_between(e, y - 1.96 * s, y + 1.96 * s, alpha=0.20, lw=0)
    ax.set_xlabel("$e$")
    ax.set_ylabel(r"$F_\rho(e)=\mathbb{E}[E_{j+1}\mid E_j=e]$")
    ax.legend(fontsize=7, ncol=2)
    ax.set_title(title, fontsize=10)
    return _finish(fig, path, "bands are pointwise 95% intervals; paths are "
                              "i.i.d. within a grid point")


def fig_h_function(
    records: Sequence[dict[str, Any]], path: Path, *,
    rho_values: Sequence[float], roots: Sequence[dict[str, Any]] = (),
    title: str = r"$H_\rho(e)=F_\rho(e)+e$",
) -> Path:
    """Figure — H_rho with its zero line and any located candidate roots."""
    e = np.array([r["e"] for r in records])
    order = np.argsort(e)
    e = e[order]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.axhline(0.0, color="0.5", lw=0.8)
    for rho in rho_values:
        key = f"F_rho_{rho:g}"
        if key not in records[0]:
            continue
        y = np.array([r[key] for r in records])[order] + e
        s = np.array([r[f"{key}_se"] for r in records])[order]
        ax.plot(e, y, marker="o", ms=2.5, label=rf"$\rho={rho:g}$")
        ax.fill_between(e, y - 1.96 * s, y + 1.96 * s, alpha=0.20, lw=0)
    for root in roots:
        ax.axvline(root["e_star"], color="0.25", ls="-.", lw=0.8)
        ax.axvspan(root["e_star_ci95"][0], root["e_star_ci95"][1],
                   color="0.25", alpha=0.12, lw=0)
    ax.set_xlabel("$e$")
    ax.set_ylabel(r"$H_\rho(e)$")
    ax.legend(fontsize=7, ncol=2)
    ax.set_title(title, fontsize=10)
    return _finish(fig, path, "nonzero zeros are period-2 candidates of the "
                              "deterministic map, not of the noisy recursion")


def fig_derivative(
    e: np.ndarray, derivative: np.ndarray, derivative_se: np.ndarray,
    path: Path, *, title: str, marks: dict[str, float] | None = None,
) -> Path:
    """Figure — numerical F'(e) with uncertainty and the |F'|=1 lines."""
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    good = np.isfinite(derivative)
    ax.axhline(0.0, color="0.6", lw=0.7)
    ax.axhline(-1.0, ls="--", lw=0.9, color="0.4")
    ax.axhline(1.0, ls="--", lw=0.9, color="0.4")
    ax.plot(e[good], derivative[good], marker="o", ms=2.5, color="0.15")
    ax.fill_between(e[good], (derivative - 1.96 * derivative_se)[good],
                    (derivative + 1.96 * derivative_se)[good], alpha=0.22,
                    lw=0, color="0.35")
    for label, value in (marks or {}).items():
        ax.axhline(value, ls=":", lw=1.0, color="0.2", label=label)
    ax.set_xlabel("$e$")
    ax.set_ylabel(r"$F'_\rho(e)$ (numerical)")
    if marks:
        ax.legend(fontsize=7)
    ax.set_title(title, fontsize=10)
    return _finish(fig, path, "local weighted quadratic fit; the shaded band is "
                              "Monte Carlo error only and excludes the O(h^2) "
                              "window truncation")


def fig_stability_diagram(
    rho: np.ndarray, slope: np.ndarray, slope_se: np.ndarray, path: Path, *,
    rho_c: float | None = None, rho_c_ci: tuple[float, float] | None = None,
    certified_band: tuple[float, float] | None = None,
    title: str = r"Local stability: $F'_\rho(0)$ against $\rho$",
) -> Path:
    """Figure — rho vs F'_rho(0), the |F'|=1 crossing, and the certified band."""
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.axhline(-1.0, ls="--", lw=1.0, color="0.35",
               label=r"$F'_\rho(0)=-1$ (local stability boundary)")
    if certified_band is not None:
        ax.axvspan(certified_band[0], certified_band[1], color="0.55",
                   alpha=0.15, lw=0,
                   label=r"$\rho_c$ implied by the certified $\Gamma$ enclosure")
    if rho_c is not None:
        ax.axvline(rho_c, ls="-.", lw=1.0, color="0.2",
                   label=rf"$\rho_c={rho_c:.4f}$ (this work)")
    if rho_c_ci is not None:
        ax.axvspan(rho_c_ci[0], rho_c_ci[1], color="0.2", alpha=0.18, lw=0)
    ax.errorbar(rho, slope, yerr=1.96 * slope_se, marker="o", ms=4,
                color="0.1", label=r"$F'_\rho(0)$ estimated")
    ax.set_xlabel(r"reuse fraction $\rho$")
    ax.set_ylabel(r"$F'_\rho(0)$")
    ax.legend(fontsize=7)
    ax.set_title(title, fontsize=10)
    return _finish(fig, path, "a local threshold crossing, not a global "
                              "bifurcation claim")


def fig_delta_scan(
    scan: Sequence[dict[str, Any]], path: Path, *, reference: float,
    reference_se: float, fitted: float, fitted_se: float,
) -> Path:
    """Figure — the O(delta^2) truncation law of the central difference.

    Included because the naive finite difference disagrees with the analytic
    route by many standard errors, and a reader is entitled to see that the
    disagreement is numerical rather than scientific.
    """
    d = np.array([row["delta"] for row in scan])
    y = np.array([row["D"] for row in scan])
    s = np.array([row["se"] for row in scan])
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    ax.axhspan(reference - 1.96 * reference_se, reference + 1.96 * reference_se,
               color="0.5", alpha=0.20, lw=0,
               label=r"score route $1-\Gamma$ (95%)")
    ax.axhline(reference, ls="--", lw=1.0, color="0.35")
    ax.errorbar(d ** 2, y, yerr=1.96 * s, marker="o", ms=4, color="0.1",
                label=r"central difference $D(\delta)$")
    ax.errorbar([0.0], [fitted], yerr=[1.96 * fitted_se], marker="s", ms=5,
                color="0.1", label="odd-polynomial fit at $\\delta=0$")
    ax.set_xlabel(r"$\delta^2$")
    ax.set_ylabel(r"$D(\delta)=[\hat F(\delta)-\hat F(-\delta)]/2\delta$")
    ax.legend(fontsize=7)
    ax.set_title(r"Finite-difference truncation is $O(\delta^2)$", fontsize=10)
    return _finish(fig, path, "linearity in delta^2 identifies the gap as "
                              "truncation bias, not model disagreement")
