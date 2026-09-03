from __future__ import annotations

import json
from pathlib import Path

import pytest

CHECKPOINT = Path(__file__).resolve().parents[1]
BOUNDARY = CHECKPOINT.parent
CLOSURE = BOUNDARY.parent
ROOT = CLOSURE.parents[1]
P4 = CLOSURE / "p4_theory_generalization"
R0 = BOUNDARY / "r0_variance_reduction_pilot"


@pytest.fixture(scope="session")
def checkpoint_dir() -> Path:
    return CHECKPOINT


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def manifest() -> dict:
    return json.loads((CHECKPOINT / "results" / "checkpoint_a.json").read_text())


@pytest.fixture(scope="session")
def doc() -> str:
    return (CHECKPOINT / "CHECKPOINT_A.md").read_text()


@pytest.fixture(scope="session")
def doc_flat(doc) -> str:
    """The document with all runs of whitespace collapsed to single spaces.

    Markdown hard-wraps prose, so a phrase that is contiguous when read can
    straddle a newline in the file.  Substring checks on prose use this view;
    checks on fenced constant blocks use the raw text.
    """
    return " ".join(doc.split())


@pytest.fixture(scope="session")
def p4_protocol() -> dict:
    return json.loads((P4 / "configs" / "P4_PROTOCOL.json").read_text())


@pytest.fixture(scope="session")
def p4_correspondence() -> dict:
    return json.loads((P4 / "results" / "correspondence.json").read_text())


@pytest.fixture(scope="session")
def p4_closure() -> dict:
    return json.loads((P4 / "results" / "closure_decision.json").read_text())


@pytest.fixture(scope="session")
def r0_tail_sweep() -> dict:
    return json.loads((R0 / "results" / "tail_sweep.json").read_text())
