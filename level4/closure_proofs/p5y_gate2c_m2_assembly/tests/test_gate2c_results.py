"""Post-outcome assertions for P5Y Gate-2C.  The measurement was ABORTED at the
frozen cap; these tests assert that the abort is recorded honestly and that no
adaptive repair was applied afterwards."""
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
R = HERE / "results"


def load(n="m2_assembly_abort.json"): return json.loads((R / n).read_text())


def test_decision_is_incomplete_external():
    assert load()["GATE2C_DECISION"] == "M2_ASSEMBLY_INCOMPLETE_EXTERNAL"


def test_cap_was_enforced_not_extended():
    d = load()
    assert d["cap_cpu_seconds"] == 720                      # 0.20 CPU-hours, frozen
    assert d["observed_cpu_seconds_at_kill"] >= 720
    assert d["stop_rule_fired"].startswith("S1")


def test_no_measurement_is_claimed():
    d = load()
    assert d["measurement_completed"] is False
    assert d["result_file_written"] is False
    assert d["timings_recorded"] is None
    assert not (R / "m2_assembly.json").exists(), "no measurement artifact may exist"


def test_ratio_is_reported_as_an_inference_not_a_measurement():
    d = load()["inferred_lower_bound_on_ratio_incremental"]
    assert d["value"].startswith(">=")
    assert "INFERENCE" in d["basis"] and "not a" in d["basis"]


def test_no_post_T2_code_mutation():
    """The frozen certifier must be byte-identical to its T1 hash: no adaptive
    repair may have been applied after the result-bearing run began."""
    man = json.loads((HERE / "GATE2C_SOURCE_MANIFEST.json").read_text())
    for f in ("m2_certifier.py", "m2_assembly.py", "GATE2C_PREREGISTRATION.md"):
        now = hashlib.sha256((HERE / f).read_bytes()).hexdigest()
        assert now == man["files"][f], f"{f} mutated after T1"
    assert load()["post_T2_code_mutation_check"]["unchanged_since_T1"] is True


def test_repair_is_designed_but_explicitly_not_applied():
    d = load()["identified_repair_NOT_APPLIED"]
    assert "hhat_1" in d["design"]
    assert d["expected_effect"].startswith("UNMEASURED")
    assert "not claimed" in d["expected_effect"].lower()


def test_cause_is_classified_with_measured_evidence():
    c = load()["cause"]
    assert c["classification"].startswith("IMPLEMENTATION_DEFECT")
    dg = c["measured_degrees"]
    assert dg["h_1"][0] == 121 and dg["F_0 candidate"][0] == 12
    assert dg["h_1"][0] / dg["F_0 candidate"][0] >= 10


def test_no_cost_band_was_updated():
    d = load()
    assert any("Gate-2B bands stand unchanged" in s
               for s in d["what_this_gate_did_NOT_establish"])


def test_no_correspondence_is_claimed():
    d = load()
    assert any("Monte Carlo" in s for s in d["what_this_gate_did_NOT_establish"])


def test_surviving_claims_are_algebraic_only():
    s = load()["what_survives"]
    assert any("R_2 = (1/2)[F_0(x0) + F_1(x0) + S_0^raw(x0)]" in x for x in s)
    assert any("ONE resolvent solve" in x for x in s)
    assert not any("ratio" in x.lower() or "cost" in x.lower() for x in s)


def test_anchor_contained_no_results():
    log = subprocess.run(["git", "log", "--format=%H %s", "-8"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip().split("\n")
    a = [l.split()[0] for l in log if "Gate-2C T0/T1" in l]
    assert a
    tree = subprocess.run(["git", "ls-tree", "-r", a[0], "--name-only"], cwd=ROOT,
                          capture_output=True, text=True).stdout
    assert "p5y_gate2c_m2_assembly/results/" not in tree


def test_prior_gates_and_protected_tree_untouched():
    diff = subprocess.run(["git", "diff", "--name-only", "c123b9b", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split("\n")
    bad = [x for x in diff if x.strip() and not x.startswith(
        ("level4/closure_proofs/p5y_micropilot_gate1/",
         "level4/closure_proofs/p5y_gate2a_sr_precision/",
         "level4/closure_proofs/p5y_gate2b_sr_cover/",
         "level4/closure_proofs/p5y_gate2c_m2_assembly/"))]
    assert not bad, f"protected paths modified: {bad}"
