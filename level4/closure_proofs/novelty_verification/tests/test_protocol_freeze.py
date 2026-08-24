import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "level4/closure_proofs/novelty_verification"


def digest_tree(root: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    files = [
        p for p in sorted(root.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    ]
    for path in files:
        rel = path.relative_to(ROOT).as_posix().encode()
        data = path.read_bytes()
        digest.update(len(rel).to_bytes(8, "big"))
        digest.update(rel)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return len(files), digest.hexdigest()


def test_protocol_hash_freeze():
    frozen = json.loads((BASE / "results/protocol_hash.json").read_text())
    chunks = []
    for name, expected in frozen["files"].items():
        data = (BASE / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected
        chunks.append(data)
    assert hashlib.sha256(b"".join(chunks)).hexdigest() == frozen["combined_sha256"]


def test_protected_history_hashes():
    frozen = json.loads((BASE / "results/historical_hashes.json").read_text())
    for name, expected in frozen["roots"].items():
        count, digest = digest_tree(ROOT / name)
        assert count == expected["files"]
        assert digest == expected["sha256"]


def test_primary_query_count_and_families():
    strategy = (BASE / "SEARCH_STRATEGY.md").read_text()
    assert sum(line.startswith(tuple(f"{n}. " for n in range(1, 5))) for line in strategy.splitlines()) == 36
    for family in "ABCDEFGHI":
        assert f"## 7{family}" in strategy


def test_historical_audit_preserves_gap():
    audit = " ".join((BASE / "HISTORICAL_PROVENANCE_AUDIT.md").read_text().split())
    assert "no standalone, paper-level novelty or prior-art review" in audit
    assert "UNRESOLVED HISTORICAL REFERENCE" in audit
    assert "LEVEL-4-PARTIAL" in audit
