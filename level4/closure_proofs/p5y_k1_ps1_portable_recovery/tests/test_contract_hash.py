"""Focused regression tests for OPERATIONAL_CONTRACT_HASH_GENERATION_DEFECT.

Established rule (model A, as the frozen lifecycle adapter implements it):
  * OPERATIONAL_CONTRACT_HASH holds sha256 of the contract's RAW FILE BYTES
  * the hash lives OUTSIDE the hashed file -- the contract never embeds its own hash
  * opscommon.load_contract sets c["_sha256"] in memory only

The original defect hashed a canonical JSON body and then wrote that digest INTO the file,
which is self-referential and can never satisfy sha256(file bytes).
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
CONTRACT = NS / "config" / "OPERATIONAL_CONTRACT.json"
HASHFILE = NS / "config" / "OPERATIONAL_CONTRACT_HASH"
GEN = NS / "code" / "make_operational_contract.py"
ADAPTER = Path("/home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/"
               "p5y_k1_ps1_lifecycle_adapter")


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------------------------------------------------------- 1. the invariant holds
def test_hash_file_equals_sha256_of_raw_file_bytes():
    assert HASHFILE.read_text().strip() == sha(CONTRACT)


def test_contract_never_embeds_its_own_hash():
    c = json.loads(CONTRACT.read_text())
    assert "_sha256" not in c and "_contract_sha256" not in c, \
        "a self-referential hash field is unsatisfiable under sha256(file bytes)"


def test_matches_the_established_adapter_pattern():
    """The frozen adapter is the reference implementation of the rule."""
    a_contract = ADAPTER / "config" / "OPERATIONAL_CONTRACT.json"
    a_hash = ADAPTER / "config" / "OPERATIONAL_CONTRACT_HASH"
    if not a_contract.exists():
        pytest.skip("adapter not deployed on this checkout")
    assert a_hash.read_text().strip() == sha(a_contract)
    assert "_sha256" not in json.loads(a_contract.read_text())


# ------------------------------------------------------------------- 2. determinism
def test_regeneration_is_byte_identical():
    before, before_hash = CONTRACT.read_bytes(), HASHFILE.read_text()
    commit = json.loads(CONTRACT.read_text())["parent"]["commit"]
    r = subprocess.run([sys.executable, str(GEN), commit], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-400:]
    assert CONTRACT.read_bytes() == before, "generation must be deterministic"
    assert HASHFILE.read_text() == before_hash


# ------------------------------------------------------ 3/4. mutations must fail closed
def _load(tmp_path, contract_bytes, hash_text):
    """Exercise the real rule: sha256(raw bytes) vs the expected digest."""
    p = tmp_path / "OPERATIONAL_CONTRACT.json"
    p.write_bytes(contract_bytes)
    return hashlib.sha256(p.read_bytes()).hexdigest() == hash_text.strip()


def test_single_byte_mutation_is_refused(tmp_path):
    raw = CONTRACT.read_bytes()
    assert _load(tmp_path, raw, HASHFILE.read_text()), "unmutated must verify"
    i = raw.index(b'"schema"')
    mutated = raw[:i] + b'"schemb"' + raw[i + 8:]
    assert not _load(tmp_path, mutated, HASHFILE.read_text()), "one flipped byte must refuse"


def test_whitespace_only_mutation_is_refused(tmp_path):
    raw = CONTRACT.read_bytes()
    assert not _load(tmp_path, raw + b" ", HASHFILE.read_text())
    assert not _load(tmp_path, raw.replace(b"\n", b"\r\n", 1), HASHFILE.read_text())


def test_wrong_expected_hash_is_refused(tmp_path):
    raw = CONTRACT.read_bytes()
    assert not _load(tmp_path, raw, "0" * 64)
    assert not _load(tmp_path, raw, "87e11746ea7a3c0e4f308c375dfb93e7338b848c4391b422a665aab7a038cd70")


def test_the_original_defective_digest_no_longer_verifies(tmp_path):
    """The defective build's digest was computed over a canonical body, not the file."""
    c = json.loads(CONTRACT.read_text())
    body = hashlib.sha256(json.dumps(c, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert body != sha(CONTRACT), "body digest must not be mistaken for the file digest"
    assert not _load(tmp_path, CONTRACT.read_bytes(), body)


# ------------------------------------------------------- 5. no scientific drift
def test_no_scientific_source_changed():
    prod = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod")
    auth = json.loads((prod / "level4/closure_proofs/p5y_k1_ps1_production/config/"
                       "LAUNCH_AUTHORIZATION.json").read_text())
    wt = Path("/home/ubuntu/work/ReBaseGuard-sr-o9-t1")
    diff = [r for r in auth["executor_source_manifest"] if sha(prod / r) != sha(wt / r)]
    assert diff == [], f"scientific executor manifest drifted: {diff[:3]}"
    assert auth["scientific_adapter_hash"] == \
        "13ba2ecd1c8afdaafb3463233f246716f599dd935c5b3722f4074327d8eec5fd"
    assert auth["successor_cells_sha256"] == \
        "dfaced89653bd71a0bab4a61729407694768456b1e841f042df84c4544bfe349"


def test_historical_ledger_untouched():
    p = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod/level4/closure_proofs/"
             "p5y_k1_ps1_production/production/PRODUCTION_LEDGER.json")
    assert sha(p) == "0557bc229c3fcdb10cb0dd0b5836fa62a6b0e6c2512656e6ec7e49294b4d6cab"
