from __future__ import annotations

import json
from pathlib import Path

import pytest

AUDIT = Path(__file__).resolve().parents[1]
CLOSURE_PROOFS = AUDIT.parents[1]
ROOT = CLOSURE_PROOFS.parents[1]
P4 = CLOSURE_PROOFS / "p4_theory_generalization"


@pytest.fixture(scope="session")
def audit() -> Path:
    return AUDIT


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def p4() -> Path:
    return P4


@pytest.fixture(scope="session")
def results() -> dict:
    return json.loads((AUDIT / "results" / "audit_results.json").read_text())


@pytest.fixture(scope="session")
def p4_closure() -> dict:
    return json.loads((P4 / "results" / "closure_decision.json").read_text())


@pytest.fixture(scope="session")
def p4_protocol() -> dict:
    return json.loads((P4 / "configs" / "P4_PROTOCOL.json").read_text())


@pytest.fixture(scope="session")
def p4_correspondence() -> dict:
    return json.loads((P4 / "results" / "correspondence.json").read_text())


@pytest.fixture(scope="session")
def p9r_ledger() -> dict:
    path = (CLOSURE_PROOFS / "p9r_final_synthesis_repair" / "results"
            / "claim_ledger.json")
    return json.loads(path.read_text())["payload"]
