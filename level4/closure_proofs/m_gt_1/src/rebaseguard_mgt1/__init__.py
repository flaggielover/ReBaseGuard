"""Stage-D m>1 derivative closure-proof utilities."""

from .model import (
    M_GRID,
    gamma_components,
    mixed_update,
    predicted_derivative,
    truncated_window,
)

__all__ = [
    "M_GRID",
    "gamma_components",
    "mixed_update",
    "predicted_derivative",
    "truncated_window",
]
