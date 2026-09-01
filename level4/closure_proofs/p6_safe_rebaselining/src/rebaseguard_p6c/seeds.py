"""Deterministic seed derivation with enforced tuning/evaluation separation.

Every stream is a function of ``(family, detector, m, policy_id, cell_tag,
replicate_block)`` alone, so any single run is reproducible in isolation and no
two families can ever collide (FAILURE_MODE_REGISTER.md F9).
"""
from __future__ import annotations

import hashlib

import numpy as np

from . import SEED_FAMILIES

#: Entropy roots.  Distinct by construction; asserted in tests/test_seeds.py.
_FAMILY_ROOT = {
    "tune":   0x50365455_4E45,      # "P6TUNE"
    "eval":   0x50364556_414C,      # "P6EVAL"
    "replay": 0x50365245_504C,      # "P6REPL"
}


def _tag_to_int(tag: str) -> int:
    """Stable 64-bit digest of a free-form tag (hash() is salted per process)."""
    return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8], "big")


def seed_sequence(*, family: str, detector: str, m: int, policy_id: str,
                  cell_tag: str = "", block: int = 0) -> np.random.SeedSequence:
    """Return the ``SeedSequence`` for one (family, cell, policy, block)."""
    if family not in SEED_FAMILIES:
        raise ValueError(f"unknown seed family {family!r}; expected one of {SEED_FAMILIES}")
    return np.random.SeedSequence([
        _FAMILY_ROOT[family],
        _tag_to_int(detector),
        int(m),
        _tag_to_int(policy_id),
        _tag_to_int(cell_tag),
        int(block),
    ])


def generator(**kwargs) -> np.random.Generator:
    """``np.random.Generator`` for the stream identified by ``seed_sequence``."""
    return np.random.default_rng(seed_sequence(**kwargs))


def assert_disjoint(sample: int = 8, **kwargs) -> None:
    """Raise if any two seed families would produce the same stream head."""
    heads = {}
    for family in SEED_FAMILIES:
        rng = generator(family=family, **kwargs)
        heads[family] = tuple(rng.standard_normal(sample).tolist())
    if len(set(heads.values())) != len(SEED_FAMILIES):
        raise AssertionError(f"seed families collide: {heads}")
