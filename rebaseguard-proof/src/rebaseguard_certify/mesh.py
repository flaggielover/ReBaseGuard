"""Deterministic tensor candidates with exact dyadic serialization."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class TensorCandidate:
    values: np.ndarray
    h: float

    def __post_init__(self) -> None:
        array = np.asarray(self.values, dtype=float)
        if array.ndim != 2 or array.shape[0] != array.shape[1] or array.shape[0] < 2:
            raise ValueError("values must be a square nodal array")
        self.values = array

    @property
    def intervals(self) -> int:
        return self.values.shape[0] - 1

    @property
    def spacing(self) -> float:
        return self.h / self.intervals

    def evaluate(self, plus: float, minus: float) -> float:
        p = min(max(float(plus), 0.0), self.h)
        m = min(max(float(minus), 0.0), self.h)
        p_scaled = p / self.spacing
        m_scaled = m / self.spacing
        i = min(int(p_scaled), self.intervals - 1)
        j = min(int(m_scaled), self.intervals - 1)
        x = p_scaled - i
        y = m_scaled - j
        block = self.values[i : i + 2, j : j + 2]
        return float(
            (1.0 - x) * (1.0 - y) * block[0, 0]
            + x * (1.0 - y) * block[1, 0]
            + (1.0 - x) * y * block[0, 1]
            + x * y * block[1, 1]
        )

    def to_dyadic(self, *, scale_bits: int) -> dict[str, object]:
        if scale_bits < 1 or scale_bits > 52:
            raise ValueError("scale_bits must be between 1 and 52")
        scale = 1 << scale_bits
        numerators = np.rint(self.values * scale).astype(np.int64)
        return {
            "schema": "rebaseguard.tensor-candidate.v1",
            "h_num": int(round(self.h * 2)),
            "h_den": 2,
            "intervals": self.intervals,
            "scale_bits": scale_bits,
            "numerators": numerators.tolist(),
        }

    @classmethod
    def from_dyadic(cls, payload: dict[str, object]) -> "TensorCandidate":
        scale_bits = int(payload["scale_bits"])
        values = np.asarray(payload["numerators"], dtype=np.int64).astype(float) / (
            1 << scale_bits
        )
        h = int(payload["h_num"]) / int(payload["h_den"])
        return cls(values, h)

