"""Frozen detector recursions, applied verbatim to non-Gaussian innovations.

Both recursions are copied from the closed campaigns and are *not* re-derived
for each family.  This is deliberate: the generalised theorem treats the
detector as a fixed measurable functional of the residual path, so changing the
innovation law must not change the recursion.  For a non-Gaussian family the
frozen Shiryaev--Roberts chart is therefore no longer that family's likelihood
ratio; it is simply a fixed path functional, which is all the theorem needs.

CUSUM   (Priority 1 / frozen model, ``closure/01_FROZEN_MODEL.md``)
    S+_t = max(0, S+_{t-1} + Z_t - k),  S-_t = max(0, S-_{t-1} - Z_t - k)
    alarm iff max(S+, S-) >= h, tested after the update, boundary inclusive.

SR      (Priority 2, ``sr_derivative_priority2/THEOREM.md`` Sec. 1)
    R+_t = (1 + R+_{t-1}) exp(Z_t - 1/2),  R-_t = (1 + R-_{t-1}) exp(-Z_t - 1/2)
    alarm iff max(R+, R-) >= A, tested after the update, boundary inclusive.

``deterministic`` is not a detector but the non-selective control ``tau = n``
used to test the neutrality corollary.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

K_FROZEN = 0.5
H_FROZEN = 5.0
A_FROZEN = 520.886133602749


@dataclass(frozen=True, slots=True)
class Detector:
    kind: str
    threshold: float

    @property
    def label(self) -> str:
        return f"{self.kind}@{self.threshold:g}"

    def new_state(self, n: int) -> tuple[np.ndarray, np.ndarray]:
        if self.kind == "sr":
            # the SR charts are carried as logarithms; the reset state R = 0
            # is log R = -inf, and logaddexp(0, -inf) = 0 reproduces
            # R_1 = exp(Z_1 - 1/2) exactly
            return np.full(n, -np.inf), np.full(n, -np.inf)
        return np.zeros(n), np.zeros(n)

    def step(
        self, up: np.ndarray, down: np.ndarray, z: np.ndarray, step_index: int
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """One frozen update returning ``(up, down, crossed)``."""
        if self.kind == "cusum":
            up = np.maximum(0.0, up + z - K_FROZEN)
            down = np.maximum(0.0, down - z - K_FROZEN)
            return up, down, (up >= self.threshold) | (down >= self.threshold)
        if self.kind == "sr":
            # log-domain to keep the chart finite for heavy-tailed innovations
            up = np.logaddexp(0.0, up) + z - 0.5
            down = np.logaddexp(0.0, down) - z - 0.5
            log_a = np.log(self.threshold)
            return up, down, (up >= log_a) | (down >= log_a)
        if self.kind == "threshold":
            # memoryless single-observation rule, used only as the exactly
            # computable validation detector
            return up, down, np.abs(z) >= self.threshold
        if self.kind == "deterministic":
            crossed = np.full(z.shape, step_index >= int(self.threshold))
            return up, down, crossed
        raise ValueError(f"unknown detector kind: {self.kind}")

    def forcing_increment(self) -> float:
        """A residual value that alarms in one step from every live state.

        CUSUM: ``Z >= h + k`` drives ``S+`` to at least ``h`` from ``S+ >= 0``.
        SR:    ``Z >= 1/2 + log A`` drives ``R+`` to at least ``A`` from
        ``R+ >= 0``.  Positive probability of this event, uniformly over a
        compact ``e`` neighbourhood, is what gives ``tau`` a geometric tail.
        """
        if self.kind == "cusum":
            return self.threshold + K_FROZEN
        if self.kind == "sr":
            return 0.5 + float(np.log(self.threshold))
        raise ValueError("the deterministic control has no forcing increment")
