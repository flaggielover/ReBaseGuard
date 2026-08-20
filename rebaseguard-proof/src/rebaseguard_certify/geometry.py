"""Reachable-state geometry and reflection operations."""

from __future__ import annotations

from rebaseguard_certify.model import State


def reflect(state: State) -> State:
    return State(state.minus, state.plus)


def in_reachable_closure(
    state: State, k: float, h: float, tolerance: float = 1e-12
) -> bool:
    p, m = state.plus, state.minus
    if p < -tolerance or m < -tolerance or p > h + tolerance or m > h + tolerance:
        return False
    if p <= tolerance or m <= tolerance:
        return True
    return p + m <= h - 2.0 * k + tolerance

