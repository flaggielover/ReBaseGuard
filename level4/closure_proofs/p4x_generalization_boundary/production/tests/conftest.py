from __future__ import annotations

import json
from pathlib import Path

import pytest

PROD = Path(__file__).resolve().parents[1]
BOUNDARY = PROD.parent
CLOSURE = BOUNDARY.parent
ROOT = CLOSURE.parents[1]
P4 = CLOSURE / "p4_theory_generalization"


def _load(name: str):
    path = PROD / "results" / name
    if not path.exists():
        pytest.skip(f"{name} not produced yet")
    return json.loads(path.read_text())


@pytest.fixture(scope="session")
def prod_dir() -> Path:
    return PROD


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def checkpoint() -> dict:
    return json.loads(
        (BOUNDARY / "checkpoint_a" / "results" / "checkpoint_a.json").read_text())


@pytest.fixture(scope="session")
def anchors() -> dict:
    return _load("anchors.json")


@pytest.fixture(scope="session")
def p1() -> dict:
    return _load("p1_zero_compute.json")


@pytest.fixture(scope="session")
def c6() -> dict:
    return _load("c6_lean_arb.json")


@pytest.fixture(scope="session")
def stage1() -> dict:
    return _load("c2_stage1.json")


@pytest.fixture(scope="session")
def stage2_plan() -> dict:
    return _load("c2_stage2_plan.json")


@pytest.fixture(scope="session")
def ledger() -> dict:
    return _load("c2_cell_ledger.json")


@pytest.fixture(scope="session")
def verdict() -> dict:
    return _load("production_results.json")


@pytest.fixture(scope="session")
def costs() -> dict:
    return _load("cost_ledger.json")


@pytest.fixture(scope="session")
def p4_correspondence() -> dict:
    return json.loads((P4 / "results" / "correspondence.json").read_text())
