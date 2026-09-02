"""Estimators, uncertainty and the preregistered gate arithmetic.
P8R provenance: byte-for-byte the P8 module `.../rebaseguard_p8/analysis.py` apart from this note.  Estimator/uncertainty changes required by P8R live in `experiments/`, not here.
"""
from __future__ import annotations

import numpy as np

Z95 = 1.959963984540054


def batch_mean_se(batch_values: np.ndarray) -> tuple[float, float, int]:
    v = np.asarray(batch_values, float)
    return float(v.mean()), float(v.std(ddof=1) / np.sqrt(v.size)), int(v.size)


def combined_z(a: float, sa: float, b: float, sb: float) -> float:
    s = float(np.sqrt(sa ** 2 + sb ** 2))
    return float((a - b) / s) if s > 0 else float("inf")


def rho_c_from_gamma(g: float, se: float) -> dict:
    """P3 A3: ``rho_c = 1/|1-Gamma|``, with the exact monotone image of the CI."""
    d = abs(1.0 - g)
    lo_g, hi_g = g - Z95 * se, g + Z95 * se
    ds = [abs(1.0 - x) for x in (lo_g, hi_g)]
    if lo_g <= 1.0 <= hi_g:
        ds.append(0.0)
    dmin, dmax = min(ds), max(ds)
    return {
        "gamma": g, "gamma_se": se, "gamma_ci95": [lo_g, hi_g],
        "d": d, "rho_c": (1.0 / d) if d > 0 else None,
        "rho_c_interval": [(1.0 / dmax) if dmax > 0 else None,
                           (1.0 / dmin) if dmin > 0 else None],
        "regime": _regime(g),
        "accessible_in_admissible_domain": bool(d > 0 and 1.0 / d <= 1.0),
        "lower_bound_exceeds_2": bool(lo_g > 2.0),
    }


def _regime(g: float) -> str:
    """P3 THEOREM.md section 5 regime audit, applied without assuming one."""
    if g > 2.0:
        return "GAMMA_GT_2"
    if g == 2.0:
        return "GAMMA_EQ_2"
    if 1.0 < g < 2.0:
        return "GAMMA_BETWEEN_1_AND_2"
    if g == 1.0:
        return "GAMMA_EQ_1_NO_BOUNDARY"
    if 0.0 < g < 1.0:
        return "GAMMA_BETWEEN_0_AND_1"
    if g == 0.0:
        return "GAMMA_EQ_0"
    return "GAMMA_LT_0"


def ratio_se(a: float, sa: float, b: float, sb: float,
             cov: float = 0.0) -> float:
    """Delta-method SE of ``a/b``."""
    if b == 0:
        return float("inf")
    r = a / b
    var = (sa / b) ** 2 + (a * sb / b ** 2) ** 2 - 2.0 * a * cov / b ** 3
    return float(abs(r) * 0.0 + np.sqrt(max(var, 0.0)))


def cochran_q(values: np.ndarray, ses: np.ndarray) -> dict:
    """Inverse-variance homogeneity test.  DESCRIPTIVE ONLY (protocol section 8)."""
    from scipy import stats
    v = np.asarray(values, float)
    s = np.asarray(ses, float)
    w = 1.0 / np.maximum(s, 1e-300) ** 2
    mu = float((w * v).sum() / w.sum())
    q = float((w * (v - mu) ** 2).sum())
    df = int(v.size - 1)
    return {"pooled": mu, "Q": q, "df": df,
            "p": float(stats.chi2.sf(q, df)) if df > 0 else None,
            "I2": float(max(0.0, (q - df) / q)) if q > 0 else 0.0}


def bh_fdr(pvalues, q: float = 0.10):
    """Benjamini-Hochberg; returns the boolean reject vector."""
    p = np.asarray(pvalues, float)
    n = p.size
    order = np.argsort(p)
    thresh = q * (np.arange(1, n + 1) / n)
    passed = p[order] <= thresh
    k = np.nonzero(passed)[0]
    out = np.zeros(n, bool)
    if k.size:
        out[order[: k[-1] + 1]] = True
    return out


def spread(values) -> float:
    """``max/min - 1`` over positive values (the gate G4 statistic)."""
    v = np.asarray(values, float)
    if np.any(v <= 0):
        return float("inf")
    return float(v.max() / v.min() - 1.0)


def p7_boundary_rates(ladder, values, metric: str) -> dict:
    """P7's boundary criterion arithmetic, restated verbatim.

    ``rate = |d log|metric|| / d log(rho/rho_c)`` per bracket for every metric
    except ``e_acf1``, which uses the absolute difference.  The boundary
    brackets are ``0.8-1.0`` and ``1.0-1.25``.  Source:
    ``p7/experiments/make_report.py::boundary_verdict``.
    """
    xs = np.log(np.asarray(ladder, float))
    ys = np.asarray(values, float)
    if metric == "e_acf1":
        rates = np.abs(np.diff(ys) / np.diff(xs))
    else:
        rates = np.abs(np.diff(np.log(np.abs(ys))) / np.diff(xs))
    labels = [f"{ladder[i]}-{ladder[i+1]}" for i in range(len(ladder) - 1)]
    bi = [i for i, lab in enumerate(labels) if lab in ("0.8-1.0", "1.0-1.25")]
    if not bi:
        raise ValueError("ladder does not contain the P7 boundary brackets")
    bmax = float(rates[bi].max())
    others = np.delete(rates, bi)
    return {"boundary_rate": bmax, "max_rate_elsewhere": float(others.max()),
            "argmax_bracket": labels[int(np.argmax(rates))],
            "peaks_at_boundary": bool(bmax > others.max()),
            "rates": {lab: float(r) for lab, r in zip(labels, rates)}}


def p7_boundary_rate_uncertainty(ladder, values, ses) -> dict:
    """Replicate-level uncertainty on P7's per-bracket rates.

    P7's criterion is a bare ``max`` over brackets with **no** uncertainty
    margin, so it can flip on Monte Carlo noise.  This companion computes, for a
    metric with replicate-level standard errors, the standard error of each
    bracket rate by the delta method and reports how many standard errors the
    boundary rate exceeds the largest rate elsewhere.

    DESCRIPTIVE ONLY.  It is reported beside gate ``G7`` and never replaces it:
    the gate is evaluated exactly as P7 wrote it.
    """
    xs = np.log(np.asarray(ladder, float))
    y = np.asarray(values, float)
    s = np.asarray(ses, float)
    dx = np.diff(xs)
    rates = np.abs(np.diff(np.log(np.abs(y))) / dx)
    rel = s / np.abs(y)
    rate_se = np.sqrt(rel[:-1] ** 2 + rel[1:] ** 2) / np.abs(dx)
    labels = [f"{ladder[i]}-{ladder[i+1]}" for i in range(len(ladder) - 1)]
    bi = [i for i, lab in enumerate(labels) if lab in ("0.8-1.0", "1.0-1.25")]
    b = int(bi[int(np.argmax(rates[bi]))])
    others = [i for i in range(rates.size) if i not in bi]
    o = int(others[int(np.argmax(rates[others]))])
    diff = float(rates[b] - rates[o])
    diff_se = float(np.sqrt(rate_se[b] ** 2 + rate_se[o] ** 2))
    return {"boundary_bracket": labels[b], "boundary_rate": float(rates[b]),
            "boundary_rate_se": float(rate_se[b]),
            "best_elsewhere_bracket": labels[o],
            "best_elsewhere_rate": float(rates[o]),
            "best_elsewhere_rate_se": float(rate_se[o]),
            "difference": diff, "difference_se": diff_se,
            "difference_in_se": (diff / diff_se) if diff_se > 0 else None,
            "resolved_at_2se": bool(diff_se > 0 and diff > 2.0 * diff_se)}
