"""Stage E endpoints and the moving-block bootstrap.

The bootstrap unit differs by endpoint and is stated explicitly for each. A
large block does NOT by itself make an interval valid: with few events the
number of independent blocks becomes small, and every interval here is reported
together with `n_blocks_effective` so that weakness is visible rather than
hidden behind a plausible-looking CI.
"""
from __future__ import annotations

import numpy as np

BLOCK = 5
N_BOOT = 10_000
BOOT_SEED = 20261102
MIN_EFFECTIVE_BLOCKS = 5      # below this the interval is flagged UNRELIABLE


def _mb_indices(n: int, block: int, n_boot: int, rng) -> np.ndarray:
    """Moving-block bootstrap index matrix, (n_boot, n)."""
    if n <= 0:
        return np.zeros((n_boot, 0), dtype=np.int64)
    b = max(1, min(block, n))
    n_start = n - b + 1
    k = int(np.ceil(n / b))
    starts = rng.integers(0, n_start, size=(n_boot, k))
    idx = (starts[:, :, None] + np.arange(b)[None, None, :]).reshape(n_boot, -1)
    return idx[:, :n]


def block_bootstrap_mean(x, *, block: int = BLOCK, n_boot: int = N_BOOT,
                         seed: int = BOOT_SEED, unit: str = "") -> dict:
    x = np.asarray(x, dtype=float)
    n = x.size
    if n == 0:
        return {"mean": float("nan"), "ci": [float("nan")] * 2, "n": 0,
                "unit": unit, "block": block, "n_blocks_effective": 0,
                "reliable": False,
                "note": "no observations"}
    rng = np.random.default_rng(seed)
    draws = x[_mb_indices(n, block, n_boot, rng)].mean(axis=1)
    eff = int(np.ceil(n / max(1, min(block, n))))
    return {"mean": float(x.mean()), "sd": float(x.std(ddof=1)) if n > 1 else 0.0,
            "ci": [float(np.percentile(draws, 2.5)),
                   float(np.percentile(draws, 97.5))],
            "n": int(n), "unit": unit, "block": int(min(block, n)),
            "n_blocks_effective": eff,
            "reliable": bool(eff >= MIN_EFFECTIVE_BLOCKS),
            "note": ("" if eff >= MIN_EFFECTIVE_BLOCKS else
                     f"UNRELIABLE: only {eff} effective blocks; the interval is "
                     f"reported but must not be treated as calibrated")}


def block_bootstrap_ratio(num, den, *, block: int = BLOCK, n_boot: int = N_BOOT,
                          seed: int = BOOT_SEED, unit: str = "") -> dict:
    """Ratio of means where numerator and denominator come from DIFFERENT
    ordered sequences (e.g. injection-event delays over in-control cycle
    lengths). Each is resampled in blocks on its own index."""
    a, b = np.asarray(num, float), np.asarray(den, float)
    if a.size == 0 or b.size == 0:
        return {"ratio": float("nan"), "ci": [float("nan")] * 2,
                "n_num": int(a.size), "n_den": int(b.size), "unit": unit,
                "reliable": False, "note": "empty sequence"}
    rng = np.random.default_rng(seed)
    da = a[_mb_indices(a.size, block, n_boot, rng)].mean(axis=1)
    db = b[_mb_indices(b.size, block, n_boot, rng)].mean(axis=1)
    r = da / np.where(np.abs(db) < 1e-12, np.nan, db)
    ea = int(np.ceil(a.size / max(1, min(block, a.size))))
    eb = int(np.ceil(b.size / max(1, min(block, b.size))))
    eff = min(ea, eb)
    return {"ratio": float(a.mean() / b.mean()),
            "ci": [float(np.nanpercentile(r, 2.5)),
                   float(np.nanpercentile(r, 97.5))],
            "n_num": int(a.size), "n_den": int(b.size), "unit": unit,
            "block": int(block), "n_blocks_effective": eff,
            "reliable": bool(eff >= MIN_EFFECTIVE_BLOCKS),
            "note": ("" if eff >= MIN_EFFECTIVE_BLOCKS else
                     f"UNRELIABLE: only {eff} effective blocks")}


def block_bootstrap_diff(x, y, *, block: int = BLOCK, n_boot: int = N_BOOT,
                         seed: int = BOOT_SEED, unit: str = "") -> dict:
    """Difference of means of two independently resampled ordered sequences."""
    a, b = np.asarray(x, float), np.asarray(y, float)
    rng = np.random.default_rng(seed)
    da = a[_mb_indices(a.size, block, n_boot, rng)].mean(axis=1)
    db = b[_mb_indices(b.size, block, n_boot, rng)].mean(axis=1)
    d = da - db
    ea = int(np.ceil(a.size / max(1, min(block, a.size))))
    eb = int(np.ceil(b.size / max(1, min(block, b.size))))
    eff = min(ea, eb)
    ci = [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]
    return {"difference": float(a.mean() - b.mean()), "ci": ci,
            "excludes_zero": bool(ci[0] > 0 or ci[1] < 0),
            "n_x": int(a.size), "n_y": int(b.size), "unit": unit,
            "block": int(block), "n_blocks_effective": eff,
            "reliable": bool(eff >= MIN_EFFECTIVE_BLOCKS)}


# ------------------------------------------------------------- endpoints
def e2_reference_error(cycles) -> np.ndarray:
    """|R_j - local mean of the stream the cycle actually faced|, per cycle."""
    return np.array([abs(c.reference - c.local_mean) for c in cycles
                     if np.isfinite(c.local_mean)])


def e3_alert_burden(cycles, n_obs: int) -> float:
    """Alarms per 1000 observations on the UN-INJECTED stream.

    Named an alert BURDEN, never a false-alarm rate: the natural stream already
    contains concept drift, so it is not a stationary in-control process.
    """
    return 1000.0 * len(cycles) / n_obs if n_obs > 0 else float("nan")


def cycle_lengths(cycles) -> np.ndarray:
    return np.array([c.length for c in cycles], dtype=float)


def acf1(x) -> float:
    x = np.asarray(x, float)
    if x.size < 3:
        return float("nan")
    x = x - x.mean()
    d = float(x @ x)
    return float(x[:-1] @ x[1:] / d) if d > 0 else float("nan")
