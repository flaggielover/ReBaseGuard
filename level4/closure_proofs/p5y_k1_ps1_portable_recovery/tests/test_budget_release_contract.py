"""Focused tests: the budget release-call-site contract binds the LAUNCHER THAT RUNS.

The genuine refusal was 'budget.release(dkey) not found exactly once'. Cause was NOT lost
release semantics: produce_entry bound the launcher by module name, so it resolved the
FROZEN production_launcher.py (3 sites) instead of the recovery ps1_cellseq_launcher.py
(4 sites). The assertion is unchanged; it now scans the correct file.
"""
import ast
import sys
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "ops"))
import ledger_ops as LO  # noqa: E402

DRV = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod-gen2/level4/closure_proofs/"
           "p5y_k1_ps1_production/driver")
RECOVERY = DRV / "ps1_cellseq_launcher.py"
FROZEN = DRV / "production_launcher.py"


def stripped(p):
    return [l.strip() for l in Path(p).read_text().splitlines()]


# 1. accepted for the correct semantic reason
def test_recovery_launcher_has_every_release_site_exactly_once():
    s = stripped(RECOVERY)
    for site in LO.RELEASE_SITES:
        assert s.count(site) == 1, f"{site!r} appears {s.count(site)}x"


def test_frozen_launcher_lacks_the_drain_site_which_is_why_it_refused():
    s = stripped(FROZEN)
    assert s.count("budget.release(dkey)") == 0
    assert s.count("budget.release(key); continue") == 1
    assert s.count("budget.release(k)") == 1


def test_produce_entry_binds_the_recovery_launcher():
    src = (NS / "ops" / "produce_entry.py").read_text()
    assert "import ps1_cellseq_launcher as PL" in src
    assert "import production_launcher as PL" not in src
    assert "is not the bound one under" in src, "the driver-dir bind check must survive"


# 2 / 3. mutations must fail
def _counts_ok(text):
    s = [l.strip() for l in text.splitlines()]
    return all(s.count(site) == 1 for site in LO.RELEASE_SITES)


def _drop_line(src, site):
    out = []
    dropped = False
    for l in src.splitlines():
        if not dropped and l.strip() == site:
            dropped = True
            continue
        out.append(l)
    assert dropped, f"{site!r} not present to drop"
    return "\n".join(out) + "\n"


def _dup_line(src, site):
    out = []
    done = False
    for l in src.splitlines():
        out.append(l)
        if not done and l.strip() == site:
            out.append(l)
            done = True
    assert done, f"{site!r} not present to duplicate"
    return "\n".join(out) + "\n"


@pytest.mark.parametrize("site", sorted(LO.RELEASE_SITES))
def test_removing_any_release_path_fails_the_contract(site):
    src = RECOVERY.read_text()
    assert _counts_ok(src)
    assert not _counts_ok(_drop_line(src, site)), f"dropping {site!r} must refuse"


@pytest.mark.parametrize("site", sorted(LO.RELEASE_SITES))
def test_duplicating_any_release_path_fails_the_contract(site):
    src = RECOVERY.read_text()
    assert not _counts_ok(_dup_line(src, site)), f"duplicating {site!r} must refuse"


# exactly-once structure
def test_all_releases_are_lexically_in_run_production_cells():
    tree = ast.parse(RECOVERY.read_text())
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        rel = [d for d in ast.walk(fn) if isinstance(d, ast.Call)
               and isinstance(d.func, ast.Attribute) and d.func.attr == "release"]
        if rel:
            assert fn.name == "run_production_cells", \
                f"{fn.name} holds a release; frame-name classification would break"
            assert len(rel) == 4


def test_reap_markers_commits_but_never_releases():
    tree = ast.parse(RECOVERY.read_text())
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "_reap_markers")
    attrs = [d.func.attr for d in ast.walk(fn) if isinstance(d, ast.Call)
             and isinstance(d.func, ast.Attribute) and d.func.attr in ("release", "commit")]
    assert attrs == ["commit"]


def test_commit_pops_the_reservation_atomically():
    """budget.commit(inflight.pop(cell), ...) -- the key leaves inflight as it commits,
    so no later release path can touch it."""
    assert "budget.commit(inflight.pop(cell), actual, _sealed)" in RECOVERY.read_text()


# 9. generation-1 untouched
def test_generation1_ledger_byte_identical():
    import hashlib
    p = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod/level4/closure_proofs/"
             "p5y_k1_ps1_production/production/PRODUCTION_LEDGER.json")
    assert hashlib.sha256(p.read_bytes()).hexdigest() == \
        "0557bc229c3fcdb10cb0dd0b5836fa62a6b0e6c2512656e6ec7e49294b4d6cab"
