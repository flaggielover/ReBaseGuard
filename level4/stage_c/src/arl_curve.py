"""Stage C — the conditional cycle-length curve A(e) = E[tau | E_j = e].

Uses the FROZEN Stage A conditional simulator, which starts a fresh monitoring
cycle from an exact reference error and runs it to the exact frozen alarm rule.
No new detector code is involved.

Seeding: each grid point gets its OWN independent seed (no common random
numbers).  That is deliberate.  A(e) is consumed by an *integral*
(`ARL_decomp = E_pi[A]`), so independent errors across grid points average down,
whereas CRN would make them systematic.  CRN is the right choice for
differencing and the wrong choice here.
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from rebaseguard_level4.conditional import simulate_cycle_batch
from rebaseguard_level4.streams import STREAM_CONDITIONAL, STREAM_FRESH, ScalarStream

STAGE_C_STREAM = 41


def default_grid(fine_to: float = 1.5, fine_step: float = 0.02,
                 coarse_to: float = 5.0, coarse_step: float = 0.1) -> np.ndarray:
    """Symmetric grid, fine where A(e) is steep and coarse in the tails.

    A falls from ~465 at e = 0 to ~10 at |e| = 1, so a uniform grid would either
    waste points in the tail or under-resolve the drop.
    """
    fine = np.arange(0.0, fine_to + 1e-12, fine_step)
    coarse = np.arange(fine_to + coarse_step, coarse_to + 1e-12, coarse_step)
    half = np.concatenate([fine, coarse])
    return np.unique(np.concatenate([-half[::-1], half]))


def estimate_A(e_values: Sequence[float], *, n_paths: int, master_seed: int,
               batches: int = 10, verbose: bool = False) -> dict[str, Any]:
    """Estimate A(e) with an i.i.d. standard error at each grid point."""
    rows = []
    per_batch = n_paths // batches
    for i, e in enumerate(e_values):
        taus = np.empty(n_paths)
        batch_means = []
        for b in range(batches):
            key = (STAGE_C_STREAM, i, b)
            batch = simulate_cycle_batch(
                e=float(e), n_paths=per_batch, m=1,
                stream=ScalarStream(master_seed, STREAM_CONDITIONAL, *key),
                fresh_stream=ScalarStream(master_seed, STREAM_FRESH, *key))
            lo, hi = b * per_batch, (b + 1) * per_batch
            taus[lo:hi] = batch.tau
            batch_means.append(float(batch.tau.mean()))
        mean = float(taus.mean())
        se = float(taus.std(ddof=1) / np.sqrt(taus.size))
        rows.append({
            "e": float(e), "e_index": i, "A": mean, "A_se": se,
            "A_batch_means": batch_means,
            "median_tau": float(np.median(taus)),
            "sd_tau": float(taus.std(ddof=1)),
            "n_paths": n_paths,
            "seed_keys": [[master_seed, STREAM_CONDITIONAL, STAGE_C_STREAM, i, b]
                          for b in range(batches)],
        })
        if verbose:
            print(f"    e={e:+.3f}  A={mean:9.3f} +/- {se:7.3f}", flush=True)
    return {"master_seed": master_seed, "n_paths": n_paths,
            "batches": batches, "records": rows,
            "seeding": "independent per grid point (no CRN); A is integrated, "
                       "so independent errors average down"}


class ACurve:
    """Interpolator for A(e) with the tail behaviour handled explicitly."""

    def __init__(self, e: np.ndarray, a: np.ndarray, se: np.ndarray) -> None:
        order = np.argsort(e)
        self.e = np.asarray(e)[order]
        self.a = np.asarray(a)[order]
        self.se = np.asarray(se)[order]

    @classmethod
    def from_records(cls, records: Sequence[dict[str, Any]]) -> "ACurve":
        return cls(np.array([r["e"] for r in records]),
                   np.array([r["A"] for r in records]),
                   np.array([r["A_se"] for r in records]))

    def __call__(self, e: np.ndarray) -> np.ndarray:
        """Linear interpolation in log A, clamped to the grid endpoints.

        log-linear because A spans nearly two orders of magnitude across the
        grid; interpolating A itself on a steep exponential-looking decay
        systematically over-estimates between nodes.
        """
        e = np.asarray(e, dtype=float)
        clipped = np.clip(e, self.e[0], self.e[-1])
        return np.exp(np.interp(clipped, self.e, np.log(self.a)))

    def out_of_range_fraction(self, e: np.ndarray) -> float:
        e = np.asarray(e)
        return float(np.mean((e < self.e[0]) | (e > self.e[-1])))

    def symmetry_diagnostics(self) -> dict[str, Any]:
        """A(-e) = A(e) is expected from the proved arm-swap involution."""
        pairs = []
        lookup = {round(float(v), 10): i for i, v in enumerate(self.e)}
        for i, v in enumerate(self.e):
            if v <= 0:
                continue
            j = lookup.get(round(-float(v), 10))
            if j is None:
                continue
            gap = float(self.a[i] - self.a[j])
            gap_se = float(np.hypot(self.se[i], self.se[j]))
            pairs.append({"e": float(v), "A_plus": float(self.a[i]),
                          "A_minus": float(self.a[j]), "gap": gap,
                          "gap_se": gap_se,
                          "z": gap / gap_se if gap_se > 0 else float("nan")})
        z = np.array([p["z"] for p in pairs], dtype=float)
        z = z[np.isfinite(z)]
        return {"n_pairs": len(pairs), "pairs": pairs,
                "max_abs_z": float(np.max(np.abs(z))) if z.size else float("nan"),
                "mean_z": float(np.mean(z)) if z.size else float("nan")}

    def monotonicity_diagnostics(self) -> dict[str, Any]:
        """Test decrease in |e| WITHOUT assuming it holds globally."""
        pos = self.e >= 0
        e, a, se = self.e[pos], self.a[pos], self.se[pos]
        d = np.diff(a)
        d_se = np.hypot(se[1:], se[:-1])
        increases = [
            {"e_from": float(e[i]), "e_to": float(e[i + 1]),
             "delta_A": float(d[i]), "z": float(d[i] / d_se[i])}
            for i in range(d.size) if d[i] > 0
        ]
        significant = [r for r in increases if r["z"] > 3.0]
        return {
            "n_intervals": int(d.size),
            "n_increasing": len(increases),
            "n_significantly_increasing": len(significant),
            "significant_increases": significant,
            "monotone_decreasing_in_abs_e": len(significant) == 0,
            "note": "global monotonicity is tested, not assumed; any interval "
                    "where A increases by more than 3 sigma is reported",
        }
