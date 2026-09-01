import json, os, sys, pytest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))

@pytest.fixture(scope="session")
def root(): return ROOT

@pytest.fixture(scope="session")
def ledger(): return json.load(open(os.path.join(ROOT, "CLAIM_LEDGER.json")))

@pytest.fixture(scope="session")
def graph(): return json.load(open(os.path.join(ROOT, "THEOREM_DEPENDENCY_GRAPH.json")))

@pytest.fixture(scope="session")
def claims(ledger): return ledger["claims"]

@pytest.fixture(scope="session")
def byid(claims): return {c["id"]: c for c in claims}
