"""Corrected BCa acceleration for the two-block ``Rdelta`` functional (G6B).

The adjudication found that P6R's bootstrap **resampling** across the two
independent blocks was conceptually correct, but that the jackknife feeding the
BCa acceleration deleted observations from **only the shorter block**.  That is
not the jackknife of the complete two-sample functional.

**The estimand and the bootstrap are unchanged.**  Only the acceleration is
repaired.

The functional
--------------

``Rdelta`` compares a method and a control on a ratio whose numerator and
denominator come from *different, independent* simulation blocks:

    block A  the delay run,       n_A replicates:  a_num (method), b_num (control)
    block B  the in-control run,  n_B replicates:  a_den (method), b_den (control)

    theta = ( mean(a_num) / mean(a_den) ) / ( mean(b_num) / mean(b_den) )
          = ( mean(a_num) * mean(b_den) ) / ( mean(a_den) * mean(b_num) )

Both policies are observed on the *same* replicates within each block, so a
resample draws one index vector per block and applies it to both policies:
paired across policies, independent across blocks.

The acceleration
----------------

For a statistic of several independent samples the BCa acceleration uses the
empirical influence values of **all** samples (Efron 1987; Efron & Tibshirani
1993, multi-sample bootstrap).  With the block-wise jackknife replicates

    theta_(s,i)  = theta with replicate i deleted from block s, the other intact
    U_(s,i)      = (n_s - 1) * ( mean_i theta_(s,i) - theta_(s,i) )

the acceleration is

    accel = (1/6) * [ sum_s n_s^-3 sum_i U_(s,i)^3 ]
                  / [ sum_s n_s^-2 sum_i U_(s,i)^2 ]^(3/2)

This **reduces exactly** to the classical single-sample formula
``sum d^3 / (6 (sum d^2)^(3/2))`` when one block carries no influence, which
``tests/`` asserts.  Both leave-one-out families have closed forms, so the whole
computation is ``O(n_A + n_B)`` rather than ``O((n_A + n_B) * cost(theta))``.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import norm


def rdelta_theta(a_num, a_den, b_num, b_den) -> float:
    """The Rdelta functional, from the four block arrays."""
    return float((np.mean(a_num) / np.mean(a_den))
                 / (np.mean(b_num) / np.mean(b_den)))


def jackknife_block_a(a_num, a_den, b_num, b_den) -> np.ndarray:
    """``theta`` with each block-A replicate deleted, block B intact (closed form).

    Deleting replicate ``i`` from the delay block changes ``mean(a_num)`` and
    ``mean(b_num)``; the common ``1/(n_A - 1)`` cancels inside their ratio.
    """
    an = np.asarray(a_num, float); bn = np.asarray(b_num, float)
    ad_m = float(np.mean(a_den)); bd_m = float(np.mean(b_den))
    s_an, s_bn = an.sum(), bn.sum()
    return ((s_an - an) / (s_bn - bn)) * (bd_m / ad_m)


def jackknife_block_b(a_num, a_den, b_num, b_den) -> np.ndarray:
    """``theta`` with each block-B replicate deleted, block A intact (closed form)."""
    ad = np.asarray(a_den, float); bd = np.asarray(b_den, float)
    an_m = float(np.mean(a_num)); bn_m = float(np.mean(b_num))
    s_ad, s_bd = ad.sum(), bd.sum()
    return (an_m / bn_m) * ((s_bd - bd) / (s_ad - ad))


def brute_force_jackknives(a_num, a_den, b_num, b_den):
    """Literal leave-one-out recomputation.  Reference for the closed forms."""
    an = np.asarray(a_num, float); ad = np.asarray(a_den, float)
    bn = np.asarray(b_num, float); bd = np.asarray(b_den, float)
    ja = np.array([rdelta_theta(np.delete(an, i), ad, np.delete(bn, i), bd)
                   for i in range(an.size)])
    jb = np.array([rdelta_theta(an, np.delete(ad, j), bn, np.delete(bd, j))
                   for j in range(ad.size)])
    return ja, jb


def two_block_acceleration(jack_a, jack_b) -> float:
    """Multi-sample BCa acceleration from both blocks' jackknife replicates."""
    num = 0.0
    den = 0.0
    for jack in (jack_a, jack_b):
        j = np.asarray(jack, float)
        n = j.size
        if n < 2:
            continue
        u = (n - 1.0) * (j.mean() - j)          # centred within the block
        num += float((u ** 3).sum()) / n ** 3
        den += float((u ** 2).sum()) / n ** 2
    return float(num / (6.0 * den ** 1.5)) if den > 0 else 0.0


def one_block_acceleration(jack) -> float:
    """The P6R shortcut, kept so tests can show the two differ when they should."""
    j = np.asarray(jack, float)
    d = j.mean() - j
    den = 6.0 * (float((d ** 2).sum()) ** 1.5)
    return float((d ** 3).sum() / den) if den > 0 else 0.0


def bca_endpoints(theta_hat: float, boot: np.ndarray, accel: float,
                  alpha: float = 0.05):
    """BCa endpoints given the point estimate, the resamples and an acceleration."""
    b = np.asarray(boot, float)
    n_b = b.size
    frac = float((b < theta_hat).sum()) / n_b
    frac = min(max(frac, 0.5 / n_b), 1.0 - 0.5 / n_b)
    z0 = float(norm.ppf(frac))
    out = []
    for z in (norm.ppf(alpha / 2.0), norm.ppf(1.0 - alpha / 2.0)):
        adj = z0 + (z0 + z) / (1.0 - accel * (z0 + z))
        out.append(float(np.quantile(b, float(np.clip(norm.cdf(adj), 0.0, 1.0)))))
    return out[0], out[1], z0


def rdelta_bca(a_num, a_den, b_num, b_den, *, n_boot: int = 10_000,
               alpha: float = 0.05, seed: int = 0, chunk: int = 250) -> dict:
    """Corrected two-block BCa for Rdelta.  Bootstrap estimand unchanged."""
    an = np.asarray(a_num, float).ravel(); ad = np.asarray(a_den, float).ravel()
    bn = np.asarray(b_num, float).ravel(); bd = np.asarray(b_den, float).ravel()
    if an.shape != bn.shape or ad.shape != bd.shape:
        raise ValueError("policies must be aligned within each block")
    n_a, n_b_ = an.size, ad.size
    theta_hat = rdelta_theta(an, ad, bn, bd)

    rng = np.random.default_rng(seed)
    parts, done = [], 0
    while done < n_boot:
        c = min(chunk, n_boot - done)
        i_a = rng.integers(0, n_a, size=(c, n_a))
        i_b = rng.integers(0, n_b_, size=(c, n_b_))
        ra = an[i_a].mean(axis=1) / ad[i_b].mean(axis=1)
        rb = bn[i_a].mean(axis=1) / bd[i_b].mean(axis=1)
        parts.append(ra / rb)
        done += c
    boot = np.concatenate(parts)

    ja = jackknife_block_a(an, ad, bn, bd)
    jb = jackknife_block_b(an, ad, bn, bd)
    accel_two = two_block_acceleration(ja, jb)
    accel_one = one_block_acceleration(jb if n_b_ <= n_a else ja)   # the P6R shortcut

    lo, hi, z0 = bca_endpoints(theta_hat, boot, accel_two, alpha)
    lo1, hi1, _ = bca_endpoints(theta_hat, boot, accel_one, alpha)
    sd = float(boot.std(ddof=1))
    z = float(norm.ppf(1.0 - alpha / 2.0))
    n_bt = boot.size
    below = float((boot <= 1.0).sum()) / n_bt
    above = float((boot >= 1.0).sum()) / n_bt
    p = float(min(1.0, 2.0 * min(below, above) + 1.0 / n_bt))
    return {
        "theta": theta_hat, "rel": theta_hat - 1.0,
        "bca_lo": lo - 1.0, "bca_hi": hi - 1.0,
        "normal_lo": theta_hat - z * sd - 1.0,
        "normal_hi": theta_hat + z * sd - 1.0,
        "boot_sd": sd, "p_value": p, "z0": z0,
        "accel_two_block": accel_two, "accel_one_block_p6r_shortcut": accel_one,
        "bca_lo_one_block_p6r_shortcut": lo1 - 1.0,
        "bca_hi_one_block_p6r_shortcut": hi1 - 1.0,
        "n_block_a": int(n_a), "n_block_b": int(n_b_), "n_boot": int(n_bt),
    }
