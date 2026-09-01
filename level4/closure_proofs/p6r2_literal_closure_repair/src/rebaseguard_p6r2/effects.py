"""Corrected paired-effect computation, with the zero-denominator guard AT SOURCE.

Everything about the bootstrap is inherited unchanged from P6R's ``stats_r``:
exactly 10,000 resamples, BCa with a real jackknife, a normal interval beside
every BCa interval, ratios resampled as ratios over replicate pairs, the
percentile p-value, the 200-event tail floor.  P6R2 changes two things and only
two:

1. **the zero-denominator guard runs before any bootstrap starts** (G6C/G12), so
   an undefined comparison can never acquire a finite verdict;
2. **``Rdelta`` uses the corrected two-block acceleration** (G6B).

Records are emitted in the P6R2 schema of ``undefined.py``: ``status``,
``relative_effect``, ``bca_interval``, ``normal_interval``, ``p_value``,
``p_adjusted``, ``verdict`` -- with JSON ``null`` wherever a number would be
undefined.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

_P6R_SRC = (Path(__file__).resolve().parents[3]
            / "p6r_safe_rebaselining_confirmation" / "src")
if str(_P6R_SRC) not in sys.path:
    sys.path.insert(0, str(_P6R_SRC))

from rebaseguard_p6r import stats_r as ST                     # noqa: E402

from . import twoblock as TB                                   # noqa: E402
from .undefined import (STATUS_OK, denominator_is_zero,        # noqa: E402
                        undefined_record)

MATERIALITY = 0.10
N_BOOT = ST.N_BOOT
ALPHA = ST.ALPHA
TAIL_EVENT_FLOOR = ST.TAIL_EVENT_FLOOR


def _verdict(lo, hi, rel, materiality):
    if lo <= 0.0 <= hi:
        return ST.INCONCLUSIVE
    return (ST.PRACTICALLY_MATERIAL if abs(rel) >= materiality
            else ST.STATISTICALLY_RESOLVED)


def _finite_record(metric, statistic, eff_dict, n_pairs, *, method_mean,
                   control_mean, pair_corr=None):
    rel = eff_dict["rel"]
    lo, hi = eff_dict["bca_lo"], eff_dict["bca_hi"]
    rec = {
        "metric": metric, "statistic": statistic, "status": STATUS_OK,
        "relative_effect": float(rel),
        "bca_interval": [float(lo), float(hi)],
        "normal_interval": [float(eff_dict["normal_lo"]),
                            float(eff_dict["normal_hi"])],
        "boot_sd": float(eff_dict["boot_sd"]),
        "p_value": float(eff_dict["p_value"]),
        "p_adjusted": None,                       # filled by the BH pass
        "verdict": _verdict(lo, hi, rel, MATERIALITY),
        "n_pairs": int(n_pairs), "n_boot": int(eff_dict["n_boot"]),
        "z0": float(eff_dict["z0"]), "accel": float(eff_dict["accel"]),
        "pair_corr": (None if pair_corr is None or not math.isfinite(pair_corr)
                      else float(pair_corr)),
        "tail_flag": None, "n_events_method": None, "n_events_control": None,
        "method_mean": float(method_mean), "control_mean": float(control_mean),
    }
    for k in ("relative_effect", "boot_sd", "p_value", "z0", "accel"):
        if rec[k] is not None and not math.isfinite(rec[k]):
            raise ValueError(f"defined record {metric!r} has non-finite {k}")
    for k in ("bca_interval", "normal_interval"):
        if not all(math.isfinite(v) for v in rec[k]):
            raise ValueError(f"defined record {metric!r} has non-finite {k}")
    return rec


def _corr(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if a.size < 2 or a.std() == 0 or b.std() == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def ratio_of_means(a, b, *, metric, seed=0, n_boot=N_BOOT):
    """Paired relative effect on means, undefined-guarded at source."""
    a = np.asarray(a, float).ravel(); b = np.asarray(b, float).ravel()
    if denominator_is_zero(b):
        return undefined_record(metric, "ratio_of_means", n_pairs=a.size,
                                method_mean=float(a.mean()) if a.size else None,
                                control_mean=0.0)
    e = ST.paired_ratio_of_means(a, b, metric=metric, materiality=MATERIALITY,
                                 seed=seed, n_boot=n_boot).to_dict()
    return _finite_record(metric, "ratio_of_means", e, a.size,
                          method_mean=a.mean(), control_mean=b.mean(),
                          pair_corr=_corr(a, b))


def ratio_of_quantiles(a, b, q, *, metric, seed=0, n_boot=N_BOOT):
    a = np.asarray(a, float).ravel(); b = np.asarray(b, float).ravel()
    qb = float(np.quantile(b, q)) if b.size else 0.0
    if qb == 0.0:
        return undefined_record(metric, "ratio_of_quantiles", n_pairs=a.size,
                                method_mean=float(np.quantile(a, q)) if a.size else None,
                                control_mean=0.0,
                                reason=(f"control arm quantile at q={q} is exactly "
                                        f"zero, so the ratio is undefined"))
    e = ST.paired_ratio_of_quantiles(a, b, q, metric=metric,
                                     materiality=MATERIALITY, seed=seed,
                                     n_boot=n_boot).to_dict()
    return _finite_record(metric, "ratio_of_quantiles", e, a.size,
                          method_mean=float(np.quantile(a, q)), control_mean=qb,
                          pair_corr=_corr(a, b))


def ratio_of_ratios(a_num, a_den, b_num, b_den, *, metric, seed=0, n_boot=N_BOOT):
    arrs = [np.asarray(x, float).ravel() for x in (a_num, a_den, b_num, b_den)]
    an, ad, bn, bd = arrs
    if float(bn.mean()) == 0.0 or float(bd.mean()) == 0.0 or float(ad.mean()) == 0.0:
        return undefined_record(metric, "ratio_of_ratios", n_pairs=an.size,
                                method_mean=None, control_mean=0.0,
                                reason="a component mean of the ratio is exactly zero")
    e = ST.paired_ratio_of_ratios(an, ad, bn, bd, metric=metric,
                                  materiality=MATERIALITY, seed=seed,
                                  n_boot=n_boot).to_dict()
    return _finite_record(metric, "ratio_of_ratios", e, an.size,
                          method_mean=float(an.mean() / ad.mean()),
                          control_mean=float(bn.mean() / bd.mean()))


def rdelta_two_block(a_num, b_num, a_den, b_den, *, metric="Rdelta", seed=0,
                     n_boot=N_BOOT):
    """Rdelta with the CORRECTED two-block BCa acceleration (G6B).

    ``a_num``/``b_num`` are the delay block (method/control); ``a_den``/``b_den``
    the in-control block.  The bootstrap estimand is unchanged from P6R.
    """
    an = np.asarray(a_num, float).ravel(); bn = np.asarray(b_num, float).ravel()
    ad = np.asarray(a_den, float).ravel(); bd = np.asarray(b_den, float).ravel()
    if float(bn.mean()) == 0.0 or float(bd.mean()) == 0.0 or float(ad.mean()) == 0.0:
        return undefined_record(metric, "rdelta_two_block_bca", n_pairs=an.size,
                                method_mean=None, control_mean=0.0,
                                reason="a component mean of Rdelta is exactly zero")
    r = TB.rdelta_bca(an, ad, bn, bd, n_boot=n_boot, alpha=ALPHA, seed=seed)
    rec = _finite_record(
        metric, "rdelta_two_block_bca",
        {"rel": r["rel"], "bca_lo": r["bca_lo"], "bca_hi": r["bca_hi"],
         "normal_lo": r["normal_lo"], "normal_hi": r["normal_hi"],
         "boot_sd": r["boot_sd"], "p_value": r["p_value"], "n_boot": r["n_boot"],
         "z0": r["z0"], "accel": r["accel_two_block"]},
        min(an.size, ad.size),
        method_mean=float(an.mean() / ad.mean()),
        control_mean=float(bn.mean() / bd.mean()))
    rec["two_block_diagnostics"] = {
        "accel_two_block": r["accel_two_block"],
        "accel_one_block_p6r_shortcut": r["accel_one_block_p6r_shortcut"],
        "bca_interval_one_block_p6r_shortcut": [
            r["bca_lo_one_block_p6r_shortcut"], r["bca_hi_one_block_p6r_shortcut"]],
        "n_block_a_delay": r["n_block_a"], "n_block_b_incontrol": r["n_block_b"],
    }
    return rec


def apply_tail_gate(rec: dict, n_events_method: int, n_events_control: int,
                    floor: int = TAIL_EVENT_FLOOR) -> dict:
    """Attach the event counts and the floor verdict.  Never upgrades a verdict."""
    rec = dict(rec)
    rec["n_events_method"] = int(n_events_method)
    rec["n_events_control"] = int(n_events_control)
    if rec["status"] != STATUS_OK:
        return rec                      # undefined stays undefined
    if min(int(n_events_method), int(n_events_control)) < floor:
        rec["tail_flag"] = ST.INSUFFICIENT_TAIL_EVENTS
        rec["verdict"] = ST.INSUFFICIENT_TAIL_EVENTS
    return rec
