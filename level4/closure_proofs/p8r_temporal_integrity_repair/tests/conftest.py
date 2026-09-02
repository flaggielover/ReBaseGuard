import json
import sys
from pathlib import Path

import pytest

P8R = Path(__file__).resolve().parents[1]
ROOT = P8R.parents[2]
sys.path.insert(0, str(P8R / "src"))
sys.path.insert(0, str(P8R / "experiments"))
sys.path.insert(0, str(P8R / "scripts"))


@pytest.fixture(scope="session")
def p8r():
    return P8R


@pytest.fixture(scope="session")
def repo_root():
    return ROOT


def payload_or_skip(rel: str):
    """Load a result payload, or skip.

    Every result-dependent test in this suite is written so that it *passes
    vacuously before production and fails loudly if the artifact exists and is
    wrong*.  That is deliberate: the whole suite must be committable at the
    temporal anchor, when no production result exists yet, and must then police
    the same properties once results arrive.
    """
    p = P8R / rel
    if not p.exists():
        pytest.skip(f"{rel} not produced yet (pre-anchor state)")
    doc = json.loads(p.read_text())
    return doc["payload"] if "payload" in doc else doc
