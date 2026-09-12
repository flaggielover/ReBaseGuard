"""P4ZR touches nothing it is not allowed to touch."""
import json
import subprocess
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parent.parent
CP = NS.parent
REPO = CP.parent.parent

#: trees that must be byte-identical to their P4ZB-tip state.
PROTECTED = {
    "level4/closure_proofs/p4_theory_generalization":
        "eede90383da44c250871b1bb97d12045c897c8d9",
    "level4/closure_proofs/p4z_location_family_feasibility":
        "4f4f5209ea6b9b15ed8c8e0e3f83355007c00e18",
    "level4/closure_proofs/p4za_fullscope_closure":
        "478edf02e28a451ae2ea1d830777e049735c28dd",
}

PARENT = "p4zb-skewnormal4-k7"
OWN_NAMESPACE = "level4/closure_proofs/p4zr_rng_provenance_repair/"


def git(*a):
    return subprocess.run(("git", "-C", str(REPO)) + a,
                          capture_output=True, text=True, check=True).stdout.strip()


def test_frozen_scientific_trees_are_byte_identical():
    for path, want in PROTECTED.items():
        assert git("rev-parse", f"HEAD:{path}") == want, f"{path} changed"


def test_p4zb_tree_is_byte_identical_to_its_own_branch_tip():
    path = "level4/closure_proofs/p4zb_skewnormal4_k7"
    assert git("rev-parse", f"HEAD:{path}") == git("rev-parse", f"{PARENT}:{path}")


def test_p4zr_touches_no_path_outside_its_own_namespace():
    """Committed diff against the parent tip, and the live working tree.

    The working-tree half matters before the repair is committed, when the
    committed diff is still empty.
    """
    changed = [p for p in git("diff", "--name-only", PARENT, "HEAD").splitlines() if p]
    working = [line[3:].strip().strip('"')
               for line in git("status", "--porcelain").splitlines() if line]
    outside = [p for p in changed + working
               if p and not p.startswith(OWN_NAMESPACE)]
    assert not outside, f"P4ZR modified protected paths: {sorted(set(outside))}"


def test_historical_p4_verdict_is_still_partial():
    d = json.loads((CP / "p4_theory_generalization" / "results"
                    / "closure_decision.json").read_text())
    assert d["verdict"] == "PARTIAL"


def test_no_scientific_result_artifact_changed():
    """Every result-bearing artifact the successor line adjudicated on."""
    results = [
        CP / "p4z_location_family_feasibility" / "production" / "adjudication.json",
        CP / "p4z_location_family_feasibility" / "results" / "successor_closure.json",
        CP / "p4za_fullscope_closure" / "production" / "adjudication_p4za.json",
        CP / "p4za_fullscope_closure" / "results" / "p4za_successor_closure.json",
        CP / "p4zb_skewnormal4_k7" / "production" / "adjudication_p4zb.json",
        CP / "p4zb_skewnormal4_k7" / "results" / "p4zb_successor_closure.json",
        CP / "p4zb_skewnormal4_k7" / "results" / "final_coverage.json",
    ]
    for p in results:
        rel = p.relative_to(REPO).as_posix()
        assert git("rev-parse", f"HEAD:{rel}") == git("rev-parse", f"{PARENT}:{rel}"), \
            f"{rel} changed"


def test_the_defective_historical_scripts_are_preserved_unedited():
    """The defect must stay visible in the artifacts that contain it."""
    for rel in ("level4/closure_proofs/p4z_location_family_feasibility/micropilots/run_micropilots.py",
                "level4/closure_proofs/p4z_location_family_feasibility/micropilots/run_fd_ladder.py",
                "level4/closure_proofs/p4za_fullscope_closure/audit/calibrate_ladder.py"):
        assert git("rev-parse", f"HEAD:{rel}") == git("rev-parse", f"{PARENT}:{rel}")


#: verdicts this repair is not permitted to assert.
BANNED_VERDICTS = ("P4Z = CLOSED", "P4Z_CLOSED", "P4ZB_CLOSED",
                   "P4_SCIENTIFIC_LINE = CLOSED", "CLOSED_BY_LATER_SUCCESSOR",
                   "P4 = CLOSED")
#: a line may name a banned verdict only to deny or defer it.
NEGATORS = ("not ", "no ", "never", "neither", "nothing", "does not",
            "outstanding", "cannot", "unless", "declares no", "asserts no")


def test_machine_readable_artifacts_assert_no_closure():
    """Strict: the JSON a reader parses must not contain a banned verdict."""
    for p in sorted((NS / "results").rglob("*.json")):
        text = p.read_text()
        for phrase in BANNED_VERDICTS:
            assert phrase not in text, f"{p.name} contains {phrase!r}"


def test_prose_names_a_closure_verdict_only_to_deny_or_defer_it():
    for p in sorted(NS.rglob("*.md")):
        for n, line in enumerate(p.read_text().splitlines(), 1):
            for phrase in BANNED_VERDICTS:
                if phrase in line:
                    low = line.lower()
                    assert any(t in low for t in NEGATORS), (
                        f"{p.name}:{n} names {phrase!r} without denying it: "
                        f"{line.strip()}")
