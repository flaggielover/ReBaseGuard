"""Exactly 18 adversarial cases for the isolated post-closure re-audit."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest


AUDIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AUDIT / "src"))

from adversarial import evaluate_checks  # noqa: E402


CHECK_IDS = [f"R{index}" for index in range(1, 19)]


@pytest.mark.parametrize("check_id", CHECK_IDS)
def test_post_closure_adversarial_check(check_id: str) -> None:
    checks = {item["id"]: item for item in evaluate_checks()}
    assert list(checks) == CHECK_IDS
    assert checks[check_id]["passed"], checks[check_id]
