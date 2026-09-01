"""The REPAIRED statistical procedure for P6R.

The independent adjudication of P6 recorded, as blocking defect 2, that the
preregistered statistical procedure was not executed: the original campaign
reported 4,000-resample percentile intervals where the preregistration named
10,000-resample BCa intervals with normal intervals beside them, ratios
bootstrapped as ratios, and Benjamini-Hochberg control over a declared family.

This module implements exactly that procedure, and ``tests/`` asserts each
element is actually executed rather than merely available:

* the resample count is **exactly** ``N_BOOT = 10_000``;
* **BCa** (bias-corrected and accelerated) intervals are computed, with a real
  jackknife acceleration -- closed form for ratios of means, an exact
  leave-one-out construction for ratios of quantiles;
* a **normal-approximation** interval is emitted beside every BCa interval;
* every ratio is resampled as a **ratio over replicate pairs** -- one index
  vector draws numerator and denominator together -- never as a post-hoc
  division of two independently bootstrapped means;
* **BH-FDR** adjusted p-values are emitted for each declared family;
* a tail estimate below the declared event floor is labelled
  ``INSUFFICIENT_TAIL_EVENTS`` and may not carry a resolved claim.

The statistical unit is the **replicate** throughout.  Where a statistic is
formed from cycles inside a replicate (the one-step risk of ``onestep.py``),
the bootstrap resamples **replicate clusters**, never cycles.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np
from scipy.stats import norm

#: Preregistered resample count.  Asserted exactly by tests/test_p6r_stats.py.
N_BOOT = 10_000
#: Chunk size for the resample loop; bounds peak memory, changes nothing.
_CHUNK = 250
#: Preregistered two-sided level.
ALPHA = 0.05
#: Preregistered tail-event floor per arm.
TAIL_EVENT_FLOOR = 200
#: Preregistered BH false-discovery rate.
BH_Q = 0.10

INCONCLUSIVE = "INCONCLUSIVE"
STATISTICALLY_RESOLVED = "STATISTICALLY_RESOLVED"
PRACTICALLY_MATERIAL = "PRACTICALLY_MATERIAL"
INSUFFICIENT_TAIL_EVENTS = "INSUFFICIENT_TAIL_EVENTS"


@dataclass(frozen=True, slots=True)
class Effect:
    """One paired relative effect, with everything the protocol requires."""
    metric: str
    statistic: str            # "ratio_of_means" | "ratio_of_quantiles"
    rel: float                # theta - 1, the relative effect
    bca_lo: float
    bca_hi: float
    normal_lo: float
    normal_hi: float
    boot_sd: float
    p_value: float
    n_pairs: int
    n_boot: int
    z0: float
    accel: float
    pair_corr: float
    verdict: str
    tail_flag: str | None = None
    n_events_method: int | None = None
    n_events_control: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# leave-one-out helpers (the real jackknife the BCa acceleration needs)
# ---------------------------------------------------------------------------

def loo_means(x: np.ndarray) -> np.ndarray:
    """Leave-one-out means, closed form."""
    x = np.asarray(x, float)
    n = x.size
    return (x.sum() - x) / (n - 1)


def loo_quantiles(x: np.ndarray, q: float) -> np.ndarray:
    """Exact leave-one-out quantiles, in the original index order.

    ``numpy``'s default 'linear' method places the quantile of an ``n-1``
    sample at position ``h = (n-2) q`` of the sorted values.  Deleting the
    element of sorted rank ``r`` shifts the sorted array by one *after* ``r``,
    so the two order statistics that bracket ``h`` are known in closed form and
    the whole vector is computable in ``O(n log n)`` once.
    """
    x = np.asarray(x, float)
    n = x.size
    if n < 3:
        raise ValueError("leave-one-out quantiles need n >= 3")
    order = np.argsort(x, kind="stable")
    xs = x[order]
    h = (n - 2) * float(q)
    lo = int(np.floor(h))
    g = h - lo
    hi = min(lo + 1, n - 2)
    r = np.arange(n)
    # y[j] = xs[j] for j < r, xs[j+1] for j >= r
    v_lo = np.where(lo < r, xs[lo], xs[min(lo + 1, n - 1)])
    v_hi = np.where(hi < r, xs[hi], xs[min(hi + 1, n - 1)])
    out_sorted = v_lo + g * (v_hi - v_lo)
    out = np.empty(n, float)
    out[order] = out_sorted
    return out


# ---------------------------------------------------------------------------
# the core BCa engine
# ---------------------------------------------------------------------------

def _bca_from_parts(theta_hat, boot, jack, alpha=ALPHA):
    """BCa endpoints from the point estimate, resamples and jackknife values."""
    b = np.asarray(boot, float)
    n_b = b.size
    frac = float((b < theta_hat).sum()) / n_b
    frac = min(max(frac, 0.5 / n_b), 1.0 - 0.5 / n_b)
    z0 = float(norm.ppf(frac))
    jack = np.asarray(jack, float)
    jbar = jack.mean()
    d = jbar - jack
    den = 6.0 * (float((d ** 2).sum()) ** 1.5)
    accel = float((d ** 3).sum() / den) if den > 0 else 0.0
    out = []
    for z in (norm.ppf(alpha / 2.0), norm.ppf(1.0 - alpha / 2.0)):
        adj = z0 + (z0 + z) / (1.0 - accel * (z0 + z))
        out.append(float(np.quantile(b, float(np.clip(norm.cdf(adj), 0.0, 1.0)))))
    return out[0], out[1], z0, accel


def _boot_indices(rng, n, n_boot=N_BOOT, chunk=_CHUNK):
    """Yield chunks of paired replicate indices.  One draw serves BOTH arms."""
    done = 0
    while done < n_boot:
        k = min(chunk, n_boot - done)
        yield rng.integers(0, n, size=(k, n))
        done += k


def _percentile_p(boot, null=1.0):
    """Two-sided percentile bootstrap p-value for ``theta = null``."""
    b = np.asarray(boot, float)
    n_b = b.size
    below = float((b <= null).sum()) / n_b
    above = float((b >= null).sum()) / n_b
    return float(min(1.0, 2.0 * min(below, above) + 1.0 / n_b))


def paired_ratio_of_means(a, b, *, metric: str, materiality: float = 0.10,
                          seed: int = 0, n_boot: int = N_BOOT,
                          alpha: float = ALPHA) -> Effect:
    """Paired relative effect ``mean(a)/mean(b) - 1``, BCa + normal + p.

    ``a`` and ``b`` are per-replicate values for the method and the control,
    aligned by replicate.  The resample draws one index vector and applies it
    to **both** arms, so the numerator and denominator move together.
    """
    a = np.asarray(a, float).ravel()
    b = np.asarray(b, float).ravel()
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("paired_ratio_of_means needs two equal-length 1-D arrays")
    n = a.size
    theta_hat = float(a.mean() / b.mean())
    rng = np.random.default_rng(seed)
    parts = []
    for idx in _boot_indices(rng, n, n_boot):
        parts.append(a[idx].mean(axis=1) / b[idx].mean(axis=1))
    boot = np.concatenate(parts)
    assert boot.size == n_boot
    jack = loo_means(a) / loo_means(b)
    lo, hi, z0, accel = _bca_from_parts(theta_hat, boot, jack, alpha)
    sd = float(boot.std(ddof=1))
    z = float(norm.ppf(1.0 - alpha / 2.0))
    nlo, nhi = theta_hat - z * sd, theta_hat + z * sd
    p = _percentile_p(boot, 1.0)
    corr = float(np.corrcoef(a, b)[0, 1]) if a.std() > 0 and b.std() > 0 else float("nan")
    rel = theta_hat - 1.0
    verdict = (INCONCLUSIVE if lo <= 1.0 <= hi else
               PRACTICALLY_MATERIAL if abs(rel) >= materiality else
               STATISTICALLY_RESOLVED)
    return Effect(metric=metric, statistic="ratio_of_means", rel=rel,
                  bca_lo=lo - 1.0, bca_hi=hi - 1.0,
                  normal_lo=nlo - 1.0, normal_hi=nhi - 1.0, boot_sd=sd,
                  p_value=p, n_pairs=n, n_boot=int(boot.size), z0=z0,
                  accel=accel, pair_corr=corr, verdict=verdict)


def paired_ratio_of_quantiles(a, b, q: float, *, metric: str,
                              materiality: float = 0.10, seed: int = 0,
                              n_boot: int = N_BOOT, alpha: float = ALPHA) -> Effect:
    """Paired relative effect ``quantile_q(a)/quantile_q(b) - 1``, BCa + normal."""
    a = np.asarray(a, float).ravel()
    b = np.asarray(b, float).ravel()
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("paired_ratio_of_quantiles needs two equal-length 1-D arrays")
    n = a.size
    theta_hat = float(np.quantile(a, q) / np.quantile(b, q))
    rng = np.random.default_rng(seed)
    parts = []
    for idx in _boot_indices(rng, n, n_boot):
        parts.append(np.quantile(a[idx], q, axis=1) / np.quantile(b[idx], q, axis=1))
    boot = np.concatenate(parts)
    assert boot.size == n_boot
    jack = loo_quantiles(a, q) / loo_quantiles(b, q)
    lo, hi, z0, accel = _bca_from_parts(theta_hat, boot, jack, alpha)
    sd = float(boot.std(ddof=1))
    z = float(norm.ppf(1.0 - alpha / 2.0))
    p = _percentile_p(boot, 1.0)
    corr = float(np.corrcoef(a, b)[0, 1]) if a.std() > 0 and b.std() > 0 else float("nan")
    rel = theta_hat - 1.0
    verdict = (INCONCLUSIVE if lo <= 1.0 <= hi else
               PRACTICALLY_MATERIAL if abs(rel) >= materiality else
               STATISTICALLY_RESOLVED)
    return Effect(metric=metric, statistic="ratio_of_quantiles", rel=rel,
                  bca_lo=lo - 1.0, bca_hi=hi - 1.0,
                  normal_lo=theta_hat - z * sd - 1.0,
                  normal_hi=theta_hat + z * sd - 1.0, boot_sd=sd,
                  p_value=p, n_pairs=n, n_boot=int(boot.size), z0=z0,
                  accel=accel, pair_corr=corr, verdict=verdict)


def paired_ratio_of_ratios(a_num, a_den, b_num, b_den, *, metric: str,
                           materiality: float = 0.10, seed: int = 0,
                           n_boot: int = N_BOOT, alpha: float = ALPHA) -> Effect:
    """Relative effect on a RATIO statistic (e.g. ``Coll = E tau_2 / E tau_1``).

    The ratio is bootstrapped **as a ratio**: one replicate index vector draws
    all four component arrays together, and the ratio is re-formed inside each
    resample.  It is never a post-hoc division of separately bootstrapped means.
    """
    arrs = [np.asarray(x, float).ravel() for x in (a_num, a_den, b_num, b_den)]
    n = arrs[0].size
    if any(x.size != n for x in arrs):
        raise ValueError("all four arrays must be aligned by replicate")
    an, ad, bn, bd = arrs
    theta_hat = float((an.mean() / ad.mean()) / (bn.mean() / bd.mean()))
    rng = np.random.default_rng(seed)
    parts = []
    for idx in _boot_indices(rng, n, n_boot):
        ra = an[idx].mean(axis=1) / ad[idx].mean(axis=1)
        rb = bn[idx].mean(axis=1) / bd[idx].mean(axis=1)
        parts.append(ra / rb)
    boot = np.concatenate(parts)
    assert boot.size == n_boot
    jack = ((loo_means(an) / loo_means(ad)) / (loo_means(bn) / loo_means(bd)))
    lo, hi, z0, accel = _bca_from_parts(theta_hat, boot, jack, alpha)
    sd = float(boot.std(ddof=1))
    z = float(norm.ppf(1.0 - alpha / 2.0))
    p = _percentile_p(boot, 1.0)
    rel = theta_hat - 1.0
    verdict = (INCONCLUSIVE if lo <= 1.0 <= hi else
               PRACTICALLY_MATERIAL if abs(rel) >= materiality else
               STATISTICALLY_RESOLVED)
    return Effect(metric=metric, statistic="ratio_of_ratios", rel=rel,
                  bca_lo=lo - 1.0, bca_hi=hi - 1.0,
                  normal_lo=theta_hat - z * sd - 1.0,
                  normal_hi=theta_hat + z * sd - 1.0, boot_sd=sd,
                  p_value=p, n_pairs=n, n_boot=int(boot.size), z0=z0,
                  accel=accel, pair_corr=float("nan"), verdict=verdict)


def tail_gate(n_events_method: int, n_events_control: int,
              floor: int = TAIL_EVENT_FLOOR) -> str | None:
    """``INSUFFICIENT_TAIL_EVENTS`` unless BOTH arms clear the declared floor."""
    return (INSUFFICIENT_TAIL_EVENTS
            if min(int(n_events_method), int(n_events_control)) < floor else None)


def apply_tail_gate(effect: Effect, n_events_method: int,
                    n_events_control: int, floor: int = TAIL_EVENT_FLOOR) -> Effect:
    """Attach the floor verdict; a sub-floor cell can carry NO resolved claim."""
    flag = tail_gate(n_events_method, n_events_control, floor)
    verdict = INSUFFICIENT_TAIL_EVENTS if flag else effect.verdict
    d = effect.to_dict()
    d.update(verdict=verdict, tail_flag=flag,
             n_events_method=int(n_events_method),
             n_events_control=int(n_events_control))
    return Effect(**d)


def benjamini_hochberg(pvals, q: float = BH_Q):
    """BH step-up.  Returns ``(reject, adjusted_p)``, both aligned to input."""
    p = np.asarray(pvals, float)
    n = p.size
    order = np.argsort(p)
    ranked = p[order]
    adj_sorted = np.minimum.accumulate((ranked * n / np.arange(1, n + 1))[::-1])[::-1]
    adj_sorted = np.clip(adj_sorted, 0.0, 1.0)
    adj = np.empty(n, float)
    adj[order] = adj_sorted
    return adj <= q, adj


def bh_family(effects: dict, q: float = BH_Q) -> dict:
    """Apply BH over a declared family of ``Effect``s, keyed by metric name.

    Sub-floor tail estimates are EXCLUDED from the family and reported as
    ``INSUFFICIENT_TAIL_EVENTS``: they carry no claim, so they neither consume
    nor receive false-discovery budget.
    """
    keys = [k for k, e in effects.items()
            if e.verdict != INSUFFICIENT_TAIL_EVENTS]
    excluded = [k for k in effects if k not in keys]
    if not keys:
        return {"q": q, "family": [], "excluded_insufficient_tail": excluded,
                "reject": {}, "p_adjusted": {}, "n_tests": 0}
    rej, adj = benjamini_hochberg([effects[k].p_value for k in keys], q)
    return {"q": q, "family": keys, "excluded_insufficient_tail": excluded,
            "n_tests": len(keys),
            "reject": {k: bool(r) for k, r in zip(keys, rej)},
            "p_adjusted": {k: float(v) for k, v in zip(keys, adj)}}


def cluster_bootstrap_ratio(num_by_rep, den_by_rep, *, seed: int = 0,
                            n_boot: int = N_BOOT, alpha: float = ALPHA) -> dict:
    """Replicate-cluster bootstrap of ``sum(num)/sum(den)`` over clusters.

    Used by ``onestep.py``: the one-step risk is a mean over *cycles*, and
    cycles inside a replicate are dependent, so the resampling unit is the
    replicate cluster and each cluster contributes its own cycle sum and count.
    """
    num = np.asarray(num_by_rep, float).ravel()
    den = np.asarray(den_by_rep, float).ravel()
    n = num.size
    theta = float(num.sum() / den.sum())
    rng = np.random.default_rng(seed)
    parts = []
    for idx in _boot_indices(rng, n, n_boot):
        parts.append(num[idx].sum(axis=1) / den[idx].sum(axis=1))
    boot = np.concatenate(parts)
    jack = (num.sum() - num) / (den.sum() - den)
    lo, hi, z0, accel = _bca_from_parts(theta, boot, jack, alpha)
    sd = float(boot.std(ddof=1))
    z = float(norm.ppf(1.0 - alpha / 2.0))
    return {"estimate": theta, "bca_lo": lo, "bca_hi": hi,
            "normal_lo": theta - z * sd, "normal_hi": theta + z * sd,
            "boot_sd": sd, "n_clusters": int(n), "n_boot": int(boot.size),
            "z0": z0, "accel": accel}


def paired_ratio_across_blocks(a_num, b_num, a_den, b_den, *, metric: str,
                               materiality: float = 0.10, seed: int = 0,
                               n_boot: int = N_BOOT, alpha: float = ALPHA) -> Effect:
    """Relative effect on ``(num/den)`` where numerator and denominator come
    from **different, independent** simulation blocks.

    Used for ``Rdelta = Dmean / Arl0``: the delay arm and the in-control arm are
    separate runs with different replicate counts, so no single replicate index
    pairs them.  The resample therefore draws **two** index vectors -- one for
    the delay block, one for the in-control block -- and applies each to BOTH
    policies, so the comparison stays paired across policies while the two
    blocks stay independent, which is what they are.  The ratio is still
    re-formed inside every resample and is never a post-hoc division.
    """
    an, bn = (np.asarray(x, float).ravel() for x in (a_num, b_num))
    ad, bd = (np.asarray(x, float).ravel() for x in (a_den, b_den))
    if an.shape != bn.shape or ad.shape != bd.shape:
        raise ValueError("policies must be aligned within each block")
    n_num, n_den = an.size, ad.size
    theta_hat = float((an.mean() / ad.mean()) / (bn.mean() / bd.mean()))
    rng = np.random.default_rng(seed)
    parts = []
    done = 0
    while done < n_boot:
        c = min(_CHUNK, n_boot - done)
        i_n = rng.integers(0, n_num, size=(c, n_num))
        i_d = rng.integers(0, n_den, size=(c, n_den))
        ra = an[i_n].mean(axis=1) / ad[i_d].mean(axis=1)
        rb = bn[i_n].mean(axis=1) / bd[i_d].mean(axis=1)
        parts.append(ra / rb)
        done += c
    boot = np.concatenate(parts)
    assert boot.size == n_boot
    # jackknife over the SHORTER block (the one that dominates the variance is
    # reported; the acceleration is a second-order correction either way)
    if n_den <= n_num:
        jack = ((an.mean() / loo_means(ad)) / (bn.mean() / loo_means(bd)))
    else:
        jack = ((loo_means(an) / ad.mean()) / (loo_means(bn) / bd.mean()))
    lo, hi, z0, accel = _bca_from_parts(theta_hat, boot, jack, alpha)
    sd = float(boot.std(ddof=1))
    z = float(norm.ppf(1.0 - alpha / 2.0))
    p = _percentile_p(boot, 1.0)
    rel = theta_hat - 1.0
    verdict = (INCONCLUSIVE if lo <= 1.0 <= hi else
               PRACTICALLY_MATERIAL if abs(rel) >= materiality else
               STATISTICALLY_RESOLVED)
    return Effect(metric=metric, statistic="ratio_across_blocks", rel=rel,
                  bca_lo=lo - 1.0, bca_hi=hi - 1.0,
                  normal_lo=theta_hat - z * sd - 1.0,
                  normal_hi=theta_hat + z * sd - 1.0, boot_sd=sd,
                  p_value=p, n_pairs=int(min(n_num, n_den)),
                  n_boot=int(boot.size), z0=z0, accel=accel,
                  pair_corr=float("nan"), verdict=verdict)
