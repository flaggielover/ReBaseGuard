from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

CAMPAIGN = Path(__file__).resolve().parents[1]
ROOT = CAMPAIGN.parents[2]

sys.path.insert(0, str(CAMPAIGN / "src"))
sys.path.insert(0, str(ROOT / "level4" / "src"))


def _load(name: str):
    path = CAMPAIGN / "results" / name
    if not path.exists():
        pytest.skip(f"{name} not generated yet; run reproduce.sh")
    return json.loads(path.read_text())


@pytest.fixture(scope="session")
def campaign() -> Path:
    return CAMPAIGN


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def protocol() -> dict:
    return json.loads((CAMPAIGN / "configs" / "P4_PROTOCOL.json").read_text())


@pytest.fixture(scope="session")
def manifest() -> dict:
    return json.loads((CAMPAIGN / "manifest.json").read_text())


@pytest.fixture(scope="session")
def correspondence() -> dict:
    return _load("correspondence.json")


@pytest.fixture(scope="session")
def stability_map() -> dict:
    return _load("stability_map.json")


@pytest.fixture(scope="session")
def closure() -> dict:
    return _load("closure_decision.json")


@pytest.fixture(scope="session")
def certificate() -> dict:
    path = CAMPAIGN / "certificates" / "certificate.json"
    if not path.exists():
        pytest.skip("certificate not generated yet; run reproduce.sh")
    return json.loads(path.read_text())
