"""Focused-suite fixtures.

These tests are IMPLEMENTATION CHECKS, not scientific adjudication.  Passing
them says the artifacts are internally consistent and the repaired algebra is
right; it says nothing about whether the science is correct.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

P9R = Path(__file__).resolve().parents[1]
ROOT = P9R.parents[2]
sys.path.insert(0, str(P9R / "src"))
sys.path.insert(0, str(P9R / "experiments"))

P9_NS = ROOT / "level4" / "closure_proofs" / "p9_final_synthesis"
P9_ADJ_COMMIT = "a3e3cabc30c4508b866736aeede54db17e5e1fcc"


def _load(rel: str):
    p = P9R / rel
    if not p.exists():
        pytest.skip(f"{rel} is a Checkpoint-B artifact and is absent")
    return json.loads(p.read_text())


@pytest.fixture(scope="session")
def p9r_root() -> Path:
    return P9R


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def sr_check():
    return _load("results/sr_recurrence_check.json")["payload"]


@pytest.fixture(scope="session")
def reproduction():
    return _load("results/reproduction.json")["payload"]


@pytest.fixture(scope="session")
def burnin():
    return _load("results/burnin_sensitivity.json")["payload"]


@pytest.fixture(scope="session")
def response_grid():
    return _load("results/response_grid.json")["payload"]


@pytest.fixture(scope="session")
def ledger():
    return _load("results/claim_ledger.json")["payload"]


@pytest.fixture(scope="session")
def ledger_rows(ledger):
    return {r["id"]: r for r in ledger["nodes"]}
