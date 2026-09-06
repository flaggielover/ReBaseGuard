"""Locks on the result-bearing production layer.

Every test compares against a frozen constant or asserts a fail-closed
behaviour.  None of them reads a scientific value.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parent.parent
REPO = NS.parent.parent.parent
sys.path.insert(0, str(NS / "production"))

import runtime_contract as rc  # noqa: E402
import scientific_hash as sh  # noqa: E402

PLAN = json.loads((NS / "production" / "campaign_plan.json").read_text())
CHECKPOINT = json.loads((NS / "configs" / "checkpoint_p4z.json").read_text())
STAGE0 = json.loads((NS / "production" / "stage0_freeze.json").read_text())
CONTRACT = json.loads((NS / "production" / "mac_runtime_contract.json").read_text())
PROBE = json.loads((NS / "production" / "worker_probe.json").read_text())
PROTOCOL = json.loads(
    (NS.parent / "p4_theory_generalization" / "configs" / "P4_PROTOCOL.json").read_text())


# --- host declaration --------------------------------------------------------

def test_the_campaign_is_declared_mac_only():
    d = CONTRACT["declaration"]
    assert d["P4Z_NUMERICAL_HOST"] == "LOCAL_MAC"
    assert d["AWS_CPU_USED_BY_P4Z"] == 0
    assert d["campaign_isolation"] == "MAC_ONLY"
    assert CONTRACT["role"] == "RESULT_BEARING_HOST"


def test_runtime_contract_is_self_consistent_and_matches_this_host():
    frozen = rc.verify(rc.CONTRACT_PATH)
    assert frozen["runtime_hash"] == rc.runtime_hash(frozen)


def test_runtime_contract_records_the_backend_that_actually_binds():
    backend = CONTRACT["numerical_backend"]
    if backend["blas_name"].lower() == "accelerate":
        assert backend["honours_omp_num_threads"] is False
        assert backend["thread_variable_that_binds"] == "VECLIB_MAXIMUM_THREADS"
    assert CONTRACT["threading_environment"]["VECLIB_MAXIMUM_THREADS"] == "1"
    assert CONTRACT["threading_environment"]["OMP_NUM_THREADS"] == "1"


def test_environment_enforcement_fails_closed(monkeypatch):
    monkeypatch.setenv("OMP_NUM_THREADS", "8")
    with pytest.raises(rc.RuntimeContractError, match="pinned threading"):
        rc.enforce_environment()


def test_runtime_verification_fails_closed_on_a_missing_contract(tmp_path):
    with pytest.raises(rc.RuntimeContractError, match="no frozen runtime contract"):
        rc.verify(tmp_path / "absent.json")


def test_runtime_verification_detects_a_tampered_contract(tmp_path):
    doc = json.loads(rc.CONTRACT_PATH.read_text())
    doc["machine"]["physical_cores"] = 999
    path = tmp_path / "tampered.json"
    path.write_text(json.dumps(doc))
    with pytest.raises(rc.RuntimeContractError, match="runtime_hash does not match"):
        rc.verify(path)


# --- worker / thread freeze --------------------------------------------------

def test_the_worker_configuration_was_frozen_before_stage0():
    decision = PROBE["frozen_decision"]
    assert decision["frozen_before_stage0"] is True
    assert decision["may_be_retuned_after_seeing_scientific_values"] is False
    assert decision["workers"] == 1 and decision["blas_threads"] == 1
    assert PLAN["execution"] == {"workers": 1, "blas_threads": 1}


def test_the_worker_choice_is_justified_by_the_measured_cpu_inflation():
    runs = {r["workers"]: r for r in PROBE["runs"]}
    assert runs[1]["cpu_inflation_vs_1_worker"] == 1.0
    assert runs[2]["cpu_inflation_vs_1_worker"] > 1.0
    assert runs[4]["cpu_inflation_vs_1_worker"] > runs[2]["cpu_inflation_vs_1_worker"]
    assert runs[1]["cpu_to_wall_ratio"] < 1.15, "the kernel must be single threaded"


# --- producer manifest / TCB -------------------------------------------------

def test_the_manifest_covers_every_scientific_module():
    manifest = sh.build_manifest()
    covered = set(manifest["entries"])
    for rel in sh.TCB_PATHS:
        assert rel in covered
    for module in sh.SCIENTIFIC_MODULES:
        tail = module.split(".")[-1] + ".py"
        assert any(p.endswith(tail) for p in covered), module


def test_manifest_verification_detects_a_changed_tcb_file():
    manifest = sh.build_manifest()
    victim = next(iter(manifest["entries"]))
    manifest["entries"][victim]["sha256"] = "0" * 64
    manifest["producer_hash"] = __import__("hashlib").sha256(
        json.dumps({k: v for k, v in manifest.items() if k != "producer_hash"},
                   indent=2, sort_keys=True).encode()).hexdigest()
    with pytest.raises(sh.ProducerGateError, match="changed mid-run"):
        sh.verify_manifest(manifest)


def test_manifest_verification_detects_a_forged_producer_hash():
    manifest = sh.build_manifest()
    manifest["producer_hash"] = "f" * 64
    with pytest.raises(sh.ProducerGateError, match="own hash does not match"):
        sh.verify_manifest(manifest)


def test_the_final_gate_refuses_a_module_that_was_never_imported():
    manifest = sh.build_manifest()
    saved = {name: sys.modules.pop(name, None) for name in sh.SCIENTIFIC_MODULES}
    try:
        with pytest.raises(sh.ProducerGateError, match="never imported"):
            sh.final_producer_gate(manifest)
    finally:
        for name, module in saved.items():
            if module is not None:
                sys.modules[name] = module


def test_the_final_gate_refuses_a_module_resolved_outside_the_manifest(tmp_path):
    """No basename exemption: a same-named file elsewhere is still refused."""
    import types  # noqa: PLC0415
    manifest = sh.build_manifest()
    decoy = tmp_path / "analytic.py"
    decoy.write_text("# not the real module\n")
    name = "rebaseguard_p4z.analytic"
    saved = sys.modules.get(name)
    sys.modules[name] = types.SimpleNamespace(__file__=str(decoy))
    try:
        with pytest.raises(sh.ProducerGateError, match="not in the producer manifest"):
            sh.final_producer_gate(manifest)
    finally:
        if saved is not None:
            sys.modules[name] = saved
        else:
            sys.modules.pop(name, None)


# --- scientific hashing ------------------------------------------------------

def test_scientific_hash_ignores_only_the_enumerated_non_scientific_fields():
    base = {"configuration": "x", "block_mean": {"1": 1.5}, "cpu_seconds": 3.0}
    faster = dict(base, cpu_seconds=99.0, wall_seconds=1.0, peak_rss_mb=7.0)
    assert sh.scientific_hash(base) == sh.scientific_hash(faster)


def test_scientific_hash_covers_a_field_nobody_enumerated():
    base = {"configuration": "x", "block_mean": {"1": 1.5}}
    extended = dict(base, some_field_added_later=0.25)
    assert sh.scientific_hash(base) != sh.scientific_hash(extended), (
        "exclusion-based hashing must hash unknown fields, not drop them")


def test_scientific_hash_changes_with_any_scientific_value():
    base = {"configuration": "x", "block_mean": {"1": 1.5}}
    moved = {"configuration": "x", "block_mean": {"1": 1.5000000001}}
    assert sh.scientific_hash(base) != sh.scientific_hash(moved)


def test_scientific_hash_fails_closed_on_an_uncanonicalisable_field():
    with pytest.raises(sh.ProducerGateError, match="unknown scientific field type"):
        sh.scientific_hash({"bad": {1, 2, 3}})


def test_scientific_hash_refuses_nan():
    with pytest.raises(ValueError):
        sh.scientific_hash({"x": float("nan")})


# --- plan / policy locks -----------------------------------------------------

def test_the_plan_is_derived_from_repository_state_not_from_a_prompt():
    assert "no value in this plan is taken from a prompt" in \
        PLAN["derived_from"]["note"]
    assert PLAN["scope"]["families_theorem_supported"] == sorted(
        n for n, s in PROTOCOL["families"].items()
        if s["class"] == "THEOREM-SUPPORTED")
    assert PLAN["scope"]["m_grid"] == PROTOCOL["m_grid"]
    assert PLAN["fd_steps"] == PROTOCOL["fd_steps"]


def test_the_unresolved_residue_matches_the_phase_0_reconstruction():
    residue = PLAN["unresolved_residue"]
    assert residue["count"] == 8
    assert sorted(residue["configurations"]) == [
        "frozen/cusum@5/t1p5", "frozen/cusum@5/t3",
        "frozen/sr@520.886/t1p5", "reduced/sr@20/t1p5"]


def test_the_block_policy_is_fixed_and_non_adaptive():
    policy = PLAN["fixed_policy"]
    assert policy["blocks_per_route_full"] == 200
    assert policy["adaptive"] is False
    assert policy["top_ups_permitted"] == 0
    assert policy["path_count_may_increase_during_run"] is False


def test_seeds_are_unique_and_disjoint_from_every_historical_p4_seed():
    seeds = []
    for cfg in PLAN["configurations"]:
        seeds += [cfg["seed_rb_score"], cfg["seed_rb_map"], cfg["seed_fd_ladder"]]
    assert len(set(seeds)) == len(seeds)
    assert not set(seeds) & set(PROTOCOL["master_seeds"].values())


def test_stage0_is_frozen_before_execution_and_blind_to_the_science():
    assert STAGE0["frozen_before_execution"] is True
    assert STAGE0["runs_the_production_driver"] is True
    assert STAGE0["separate_pilot_script"] is False
    assert set(STAGE0["stage0_verdict_rule"]) >= {
        "STAGE0_PASS", "STAGE0_INCONCLUSIVE", "STAGE0_KILLED"}
    assert STAGE0["stage0_verdict_rule"]["manual_override"] == "not permitted"
    for forbidden in ("the relative discrepancy between routes",
                      "the z statistic",
                      "whether a cell is close to passing"):
        assert forbidden in STAGE0["stage0_does_not_read"]
    for forbidden in ("alter any threshold", "trigger a top-up"):
        assert forbidden in STAGE0["what_stage0_may_not_do"]


def test_stage0_covers_every_configuration_carrying_an_unresolved_cell():
    covered = {row["configuration"] for row in STAGE0["design"]["mandatory_coverage"]}
    assert set(PLAN["unresolved_residue"]["configurations"]) <= covered


# --- resume identity ---------------------------------------------------------

def test_resume_identity_is_sensitive_to_every_binding_input():
    import run_p4z  # noqa: PLC0415
    base = ("PROD", "RUNTIME", "frozen/cusum@5/t1p5", "rb_score", 4090401, 3)
    ident = run_p4z.resume_identity(*base)
    for index in range(len(base)):
        changed = list(base)
        changed[index] = (changed[index] + 1 if isinstance(changed[index], int)
                          else str(changed[index]) + "x")
        assert run_p4z.resume_identity(*changed) != ident, index


# --- driver refusal behaviour ------------------------------------------------

def test_the_driver_refuses_a_dirty_scientific_tree(tmp_path):
    victim = REPO / sh.TCB_PATHS[0]
    original = victim.read_bytes()
    try:
        victim.write_bytes(original + b"\n# transient\n")
        with pytest.raises(sh.ProducerGateError, match="scientific source state is dirty"):
            sh.refuse_dirty_scientific_state()
    finally:
        victim.write_bytes(original)
    assert sh.refuse_dirty_scientific_state()


def test_the_driver_requires_a_stage_or_adjudicate_argument():
    out = subprocess.run(
        [sys.executable, str(NS / "production" / "run_p4z.py")],
        capture_output=True, text=True,
        env={"PATH": "/usr/bin:/bin", **{k: "1" for k in
             ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS")},
             "PYTHONHASHSEED": "0", "LC_ALL": "C"})
    assert out.returncode != 0
    assert "one of --stage or --adjudicate is required" in out.stderr


# --- bounded-survival formalisation ------------------------------------------

def test_the_lean_bounded_survival_file_exists_and_claims_the_right_lemmas():
    lean = (NS / "lean" / "BoundedSurvival.lean").read_text()
    for name in ("cusum_alarm_iff", "cusum_survival_bounded",
                 "cusum_live_residual_bounded", "sr_alarm_iff",
                 "sr_survival_bounded", "sr_live_residual_bounded",
                 "srChart_side_condition"):
        assert f"theorem {name}" in lean, name
    assert "sorry" not in lean
    audit = (NS / "lean" / "AxiomAudit.lean").read_text()
    assert "#print axioms P4Z.cusum_live_residual_bounded" in audit
    assert "#print axioms P4Z.sr_live_residual_bounded" in audit
