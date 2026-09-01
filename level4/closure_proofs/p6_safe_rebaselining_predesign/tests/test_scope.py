"""Nothing outside the P6 pre-design namespace may be written."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
# Widened when the full P6 campaign opened its own namespace: the assertion's
# semantics -- "P6 writes stay inside P6" -- are unchanged.  Recorded in
# p6_safe_rebaselining/P5_TO_P6_DEPENDENCY_AUDIT.md section 5.
NS = ("level4/closure_proofs/p6_safe_rebaselining_predesign/",
      "level4/closure_proofs/p6_safe_rebaselining/")
#: The worktree state recorded BEFORE the pre-design began.  Anything in it is
#: not ours; anything new outside NS is.
BASELINE = Path(__file__).resolve().parents[1] / "results" / "worktree_baseline.txt"


def test_worktree_scope_is_predesign_only():
    baseline = set(BASELINE.read_text().splitlines())
    out = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    offenders = [line for line in out.splitlines()
                 if line not in baseline
                 and not any(line[3:].strip().startswith(ns) for ns in NS)]
    assert not offenders, f"writes outside the P6 namespace: {offenders}"


def test_baseline_records_the_pre_existing_dirty_state():
    """Documents what was already modified when P6 started (not P6's doing)."""
    baseline = BASELINE.read_text()
    assert " M README.md" in baseline
    assert "p5_nonlinear_dynamics" in baseline


def test_predesign_does_not_import_p5():
    """P6 must not depend on an unadjudicated campaign (ledger section 5)."""
    src = Path(__file__).resolve().parents[1] / "src"
    hits = [f for f in src.rglob("*.py") if "rebaseguard_p5" in f.read_text()]
    assert not hits, f"P6 harness imports P5: {hits}"
