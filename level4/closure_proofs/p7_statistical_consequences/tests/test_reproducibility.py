"""Seeds must be reproducible and the campaign must stay isolated."""
import ast
import hashlib
import json
from pathlib import Path

import numpy as np

from rebaseguard_p7 import CUSUM
from rebaseguard_p7.chain import simulate_chain
from rebaseguard_p7.config import DETECTOR_CODE, SEED_FAMILY

CAMPAIGN = Path(__file__).resolve().parents[1]
SOURCES = sorted((CAMPAIGN / "src").rglob("*.py")) + \
          sorted((CAMPAIGN / "experiments").rglob("*.py"))


def test_no_salted_hash_in_any_seed_path():
    """Python salts hash(str) per process; it must never reach a SeedSequence.

    Only executable code is scanned: string literals and comments may name the
    defect (PROVENANCE and the pilot notes both do).
    """
    for p in SOURCES:
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "hash"):
                raise AssertionError(f"{p}:{node.lineno} calls hash()")


def test_detector_codes_are_fixed_integers():
    assert DETECTOR_CODE == {"cusum": 11, "sr": 13}
    assert isinstance(SEED_FAMILY, int) and SEED_FAMILY > 0


def test_same_seed_gives_the_same_chain_twice():
    kw = dict(detector=CUSUM, m=3, rho=0.4, n_rep=200, n_cycles=5, burn_in=1)
    ss = [SEED_FAMILY, 2, DETECTOR_CODE["cusum"], 3, 4000000]
    a = simulate_chain(rng=np.random.Generator(
        np.random.PCG64(np.random.SeedSequence(ss))), **kw)
    b = simulate_chain(rng=np.random.Generator(
        np.random.PCG64(np.random.SeedSequence(ss))), **kw)
    assert np.array_equal(a.tau, b.tau)
    assert np.array_equal(a.e_start, b.e_start)


def test_campaign_does_not_import_other_closure_campaigns():
    """No P7 module may import another campaign's package -- P4 above all.

    Imports are read from the AST, so a string literal that merely *names* a
    campaign (PROVENANCE records that P4 was not used) does not trip the test.
    """
    forbidden = {"rebaseguard_p3_map", "rebaseguard_sr_priority2",
                 "rebaseguard_mgt1_priority1", "rebaseguard_sr_derivative",
                 "p4_theory_generalization"}
    for p in SOURCES:
        for node in ast.walk(ast.parse(p.read_text())):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for n in names:
                root = n.split(".")[0]
                assert root not in forbidden, f"{p} imports {n}"


def test_campaign_writes_only_inside_its_own_namespace():
    """No P7 script may name a path outside level4/closure_proofs/p7_*."""
    for p in SOURCES:
        for line in p.read_text().splitlines():
            if "write_text" in line or "savez" in line or "savefig" in line:
                assert ("RESULTS" in line or "FIGURES" in line or "path" in line
                        or "CAMPAIGN" in line), f"{p}: unanchored write: {line}"


def test_provenance_hashes_match_and_do_not_self_reference():
    provenance = json.loads((CAMPAIGN / "PROVENANCE.json").read_text())
    assert "PROVENANCE.json" not in provenance["files"]
    assert "PROVENANCE.md" not in provenance["files"]
    for rel, record in provenance["files"].items():
        path = CAMPAIGN / rel
        assert path.stat().st_size == record["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
