from __future__ import annotations

import ast
from pathlib import Path

import numpy as np

from rebaseguard_mgt1_priority1.cusum import H, K

CAMPAIGN = Path(__file__).resolve().parents[1]


def test_new_numerics_have_no_historical_scientific_import() -> None:
    sources = [CAMPAIGN / "src/rebaseguard_mgt1_priority1/cusum.py",
               CAMPAIGN / "numerics/run_correspondence.py"]
    forbidden = ("stage_d", "rebaseguard_mgt1a", "rebaseguard_mgt1b")
    for source in sources:
        tree = ast.parse(source.read_text())
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
        assert not any(any(token in name for token in forbidden) for name in imports)


def test_frozen_constants_and_one_step_semantics() -> None:
    assert K == 0.5 and H == 5.0
    plus = np.array([0.0, 4.9, 0.2])
    minus = np.array([0.0, 0.1, 4.8])
    z = np.array([1.0, 0.6, -0.8])
    new_plus = np.maximum(0.0, plus + z - K)
    new_minus = np.maximum(0.0, minus - z - K)
    assert np.array_equal(new_plus >= H, [False, True, False])
    assert np.array_equal(new_minus >= H, [False, False, True])


def test_lean_does_not_import_track1b() -> None:
    source = (CAMPAIGN / "lean/MGtOneClosure.lean").read_text()
    assert "Track1B" not in source
    assert "sorry" not in source and "admit" not in source
