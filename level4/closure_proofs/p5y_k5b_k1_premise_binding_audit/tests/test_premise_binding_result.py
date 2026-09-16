"""The r1 result verifies, the frozen plan is untouched, and the consistency rules refuse over-claims."""
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))
import verify_premise_binding as V  # noqa: E402

LIVE = V.build()
RESULT = json.loads(V.RESULT.read_text())


def _refused(mut_result=None, mut_live=None):
    r, l = copy.deepcopy(RESULT), copy.deepcopy(LIVE)
    if mut_result:
        mut_result(r)
    if mut_live:
        mut_live(l)
    if mut_live:
        r["recomputed"] = l          # isolate the rule under test from the section-equality check
    return V.consistency_problems(r, l) != []


def test_result_verifies():
    assert V.consistency_problems(RESULT, LIVE) == []


def test_plan_and_its_test_unchanged_since_publication():
    for rel in ("config/AUDIT_PLAN.json", "README.md", "tests/test_plan.py"):
        blob = subprocess.run(["git", "-C", str(V.REPO), "show",
                               f"9d136827:level4/closure_proofs/p5y_k5b_k1_premise_binding_audit/{rel}"],
                              capture_output=True, check=True).stdout
        assert blob == (NS / rel).read_bytes(), rel
    assert not (NS / "evidence").exists()


def test_headline_verdicts():
    v = RESULT["verdicts"]
    assert v["CUSUM_K5B_K1_PREMISE_BINDING"] == "PASS_WITH_NOTES"
    assert (v["PB2"], v["PB3"], v["PB4_FUNCTION_IDENTITY"], v["PB5_WHOLE_CELL_R2"], v["PB6_R2_ENDPOINT_GATE"]) == \
        ("BOUND_WITH_NOTE", "BOUND", "BOUND", "BOUND", "BOUND_WITH_NOTE")
    assert RESULT["NEW_K5_BLOCKER_CREATED"] == "NO" and RESULT["B3_REOPENED"] == "NO"
    assert RESULT["SR_PREMISE_BINDING"] == "UNDETERMINED_PENDING_PS1"
    assert not any(RESULT["non_claims"].values())


def test_record_copies_are_the_closed_export_bytes():
    export = json.loads((V.REPO / V.CP / "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/"
                                         "COMPOSITE_EXPORT_MANIFEST.json").read_text())["files"]
    for i in (0, 309):
        raw = (NS / f"result_r1/records/aux5_CUSUM_{i}_256.json").read_bytes()
        assert hashlib.sha256(raw).hexdigest() == export[f"k4_records/aux5_CUSUM_{i}_256.json"]
        assert hashlib.sha256(raw + b" ").hexdigest() != export[f"k4_records/aux5_CUSUM_{i}_256.json"]


def test_refusals():
    cases = {
        "overall PASS with notes present": (lambda r: r["verdicts"].update(CUSUM_K5B_K1_PREMISE_BINDING="PASS"), None),
        "B3 reopened": (lambda r: r.update(B3_REOPENED="YES"), None),
        "SR extrapolated": (lambda r: r.update(SR_PREMISE_BINDING="BOUND"), None),
        "committed section tampered": (lambda r: r["recomputed"]["geometry"].update(cells_containing_2=[308]), None),
        "PB6 bound but recheck fails": (None, lambda l: l["pb6_recheck"]["m"]["5"].update(
            exact_lower_bound_gt_minus_2=False)),
        "PB6 bound but gate failed": (None, lambda l: l["pb6_recheck"]["m"]["1"].update(target_gate_status="FAIL")),
        "PB3 consistency PASS but check fails": (None, lambda l: l["pb3_external_consistency"]["m"]["2"].update(
            contains_recorded_estimate=False)),
        "manifest mismatch": (None, lambda l: l["manifest_v3"].update(bound_file_mismatches=["x.py"])),
        "identity does not reproduce": (None, lambda l: l["manifest_v3"].update(equals_closure_producer_identity=False)),
        "record not bound": (None, lambda l: l["records"]["309"].update(scientific_content_hash_recomputes=False)),
        "cover gap": (None, lambda l: l["geometry"].update(problems=["contiguity 17"])),
    }
    assert [name for name, (mr, ml) in cases.items() if not _refused(mr, ml)] == []


def test_cli():
    p = subprocess.run([sys.executable, "-B", str(NS / "code/verify_premise_binding.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0 and "PREMISE_BINDING_RESULT_VERIFIED" in p.stdout


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
