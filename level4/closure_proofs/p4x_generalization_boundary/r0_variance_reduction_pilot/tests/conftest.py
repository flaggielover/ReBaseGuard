from __future__ import annotations

import json
from pathlib import Path

import pytest

PILOT = Path(__file__).resolve().parents[1]
BOUNDARY = PILOT.parent
CLOSURE_PROOFS = BOUNDARY.parent
ROOT = CLOSURE_PROOFS.parents[1]
P4 = CLOSURE_PROOFS / "p4_theory_generalization"


def _load(name: str):
    path = PILOT / "results" / name
    if not path.exists():
        pytest.skip(f"{name} not generated yet; run the pilot")
    return json.loads(path.read_text())


@pytest.fixture(scope="session")
def pilot_dir() -> Path:
    return PILOT


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def sizing() -> dict:
    return _load("sizing.json")


@pytest.fixture(scope="session")
def pilot() -> dict:
    return _load("pilot.json")


@pytest.fixture(scope="session")
def cut23() -> dict:
    return _load("cut2_cut3_cost.json")


@pytest.fixture(scope="session")
def policy() -> dict:
    return _load("precision_policy.json")


@pytest.fixture(scope="session")
def p4_correspondence() -> dict:
    return json.loads((P4 / "results" / "correspondence.json").read_text())


@pytest.fixture(scope="session")
def p4_protocol() -> dict:
    return json.loads((P4 / "configs" / "P4_PROTOCOL.json").read_text())


@pytest.fixture(scope="session")
def audit_results() -> dict:
    path = (BOUNDARY / "feasibility_and_scope_audit" / "results"
            / "audit_results.json")
    return json.loads(path.read_text())
