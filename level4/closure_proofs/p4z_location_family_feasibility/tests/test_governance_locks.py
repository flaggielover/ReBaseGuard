"""Locks on the frozen inputs, the checkpoint, and the historical record.

Every test here is a comparison against a constant that was frozen before any
P4Z number existed.  None of them is a measurement.
"""
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parent.parent
REPO = NS.parent.parent.parent
P4 = NS.parent / "p4_theory_generalization"
CHECKPOINT = json.loads((NS / "configs" / "checkpoint_p4z.json").read_text())
CONTRACT = json.loads((NS / "configs" / "estimand_contract.json").read_text())


def _git(*args: str) -> str:
    return subprocess.run(("git", "-C", str(REPO)) + args,
                          capture_output=True, text=True, check=True).stdout.strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- theorem / estimand lock -------------------------------------------------

def test_the_inherited_p4_tree_is_untouched():
    """The whole historical P4 namespace, by git object."""
    got = _git("rev-parse", "HEAD:level4/closure_proofs/p4_theory_generalization")
    assert got == CHECKPOINT["theorem"]["tree_object"]


@pytest.mark.parametrize("name,key", [
    ("THEOREM.md", "theorem_md_blob"),
    ("PROOF.md", "proof_md_blob"),
    ("configs/P4_PROTOCOL.json", "protocol_blob"),
])
def test_load_bearing_p4_documents_are_untouched(name, key):
    got = _git("rev-parse",
               f"HEAD:level4/closure_proofs/p4_theory_generalization/{name}")
    assert got == CHECKPOINT["theorem"][key]


def test_p4_protocol_content_hash_matches_the_p4_manifest():
    """P4Z binds the protocol by content, as P4's own manifest does."""
    manifest = json.loads((P4 / "manifest.json").read_text())
    declared = manifest["frozen_new_inputs"]["protocol_sha256"]
    assert declared == CHECKPOINT["theorem"]["protocol_sha256"]
    assert _sha256(P4 / "configs" / "P4_PROTOCOL.json") == declared


def test_the_estimand_is_the_frozen_G1a_object():
    assert CONTRACT["estimand"]["definition"] == "E_0[ A_m * S_tau^psi ]"
    assert CONTRACT["estimand"]["theorem"].startswith("G1a")
    theorem = (P4 / "THEOREM.md").read_text()
    assert "Gamma_{D,m,f} := E_0[A_m S_tau^psi]" in theorem


# --- exact thresholds unchanged ---------------------------------------------

def test_every_scientific_threshold_is_the_frozen_one():
    protocol = json.loads((P4 / "configs" / "P4_PROTOCOL.json").read_text())
    gates = protocol["gates"]
    frozen = CHECKPOINT["gate_thresholds_unchanged"]
    assert frozen["correspondence_relative_limit"] == gates["correspondence_relative_limit"] == 0.03
    assert frozen["correspondence_z_limit"] == gates["correspondence_z_limit"] == 4.0
    assert frozen["route_q_tolerance_relative"] == protocol["route_q"]["tolerance_relative"] == 1e-6
    assert frozen["neutrality_tolerance_z"] == protocol["neutrality_control"]["tolerance_z"] == 4.0
    assert frozen["fd_steps"] == protocol["fd_steps"] == [0.05, 0.025]
    assert frozen["m_grid"] == protocol["m_grid"] == [1, 2, 3, 5]
    assert frozen["any_threshold_relaxed_by_p4z"] is False


def test_r_star_is_the_forced_value_and_the_p4z_target_is_tighter():
    r_star = CHECKPOINT["gate_thresholds_unchanged"]["r_star"]
    assert abs(1.96 * (2 ** 0.5) * r_star - 0.03) < 1e-8
    feas = json.loads((NS / "results" / "estimator_feasibility.json").read_text())
    target = feas["design"]["target_relative_se_per_route"]
    assert target < r_star, "the P4Z design target must be tighter than r*"


# --- old estimator exclusion -------------------------------------------------

def test_the_historical_routes_are_rejected_with_a_named_cause():
    names = {r["name"]: r["cause"] for r in CHECKPOINT["estimators"]["rejected"]}
    assert "historical Route A" in names and "F-01" in names["historical Route A"]
    assert "historical Route B" in names and "F-02" in names["historical Route B"]
    for method in ("reflection-antithetic", "Corollary-G2 control variate",
                   "coarse finite-difference step", "fine finite-difference step"):
        assert method in names


def test_no_p4z_estimator_module_imports_the_historical_estimators():
    """The frozen detectors, families and simulator are inherited; the frozen
    ESTIMATORS are not, and must not be reachable from P4Z's own routes."""
    for name in ("analytic.py", "rbscore.py", "rbmap.py"):
        src = (NS / "src" / "rebaseguard_p4z" / name).read_text()
        assert "route_a" not in src
        assert "route_b(" not in src
        assert "rebaseguard_p4_general.estimators" not in src


# --- producer / scientific hash ---------------------------------------------

@pytest.mark.parametrize("key,rel", [
    ("primary", "src/rebaseguard_p4z/rbscore.py"),
    ("fallback", "src/rebaseguard_p4z/rbmap.py"),
    ("analytic_contract", "src/rebaseguard_p4z/analytic.py"),
    ("package_init", "src/rebaseguard_p4z/__init__.py"),
])
def test_producer_source_hashes_match_the_checkpoint(key, rel):
    assert _sha256(NS / rel) == CHECKPOINT["estimators"][key]["sha256"]


def test_estimand_contract_hash_matches_the_checkpoint():
    assert (_sha256(NS / "configs" / "estimand_contract.json")
            == CHECKPOINT["estimand"]["contract_sha256"])


def test_no_broad_swallowed_exception_in_the_producer():
    for name in ("analytic.py", "rbscore.py", "rbmap.py", "__init__.py"):
        src = (NS / "src" / "rebaseguard_p4z" / name).read_text()
        assert "except Exception" not in src
        assert "except:" not in src


# --- stopping budget / path budget -------------------------------------------

def test_the_stopping_rule_is_non_adaptive_and_repairs_the_named_findings():
    rule = CHECKPOINT["stopping_rule"]
    assert rule["adaptive"] is False
    assert rule["top_ups_permitted"] == 0
    assert rule["precision_trigger"] == "none"
    assert rule["post_hoc_extension"] == "not permitted"
    assert set(rule["repairs_findings"]) == {"F-04", "F-05"}


def test_the_projected_budget_fits_inside_the_cap():
    b = CHECKPOINT["budget"]
    assert b["projected_total_cpu_hours"] <= b["total_cpu_cap_hours"]
    feas = json.loads((NS / "results" / "estimator_feasibility.json").read_text())
    # the CPU projection is a measured rate, so it is pinned to the committed
    # feasibility artifact rather than to a bit-exact constant
    assert abs(feas["totals"]["total_cpu_hours"]
               - b["projected_total_cpu_hours"]) < 0.01
    for row in feas["plan"]:
        cpu = (row["route_a_cpu_seconds"] + row["route_b_cpu_seconds"]) / 3600.0
        assert cpu <= b["per_configuration_cpu_cap_hours"], row["configuration"]


def test_every_planned_configuration_uses_the_frozen_block_count():
    feas = json.loads((NS / "results" / "estimator_feasibility.json").read_text())
    for row in feas["plan"]:
        assert row["blocks"] == CHECKPOINT["budget"]["blocks_per_route"] == 200
        assert row["route_a_paths"] == row["blocks"] * row["block_paths"]


# --- kill-gate logic ---------------------------------------------------------

def test_kill_gates_are_complete_and_blind_to_the_science():
    gates = CHECKPOINT["kill_gates"]
    assert [g["id"] for g in gates] == [f"K{i}" for i in range(1, 10)]
    forbidden = ("discrepancy", "z >", "close to passing", "would close",
                 "pass", "fail rate")
    for g in gates:
        text = (g["condition"] + " " + g["when"]).lower()
        for word in forbidden:
            assert word not in text, (g["id"], word)


def test_every_kill_gate_action_is_abort_kill_stop_or_inconclusive():
    for g in CHECKPOINT["kill_gates"]:
        action = g["action"].upper()
        assert any(k in action for k in
                   ("ABORT", "KILL", "STOP", "INCONCLUSIVE", "BUDGET_EXCLUDED"))
        assert "PASS" not in action


# --- gate logic --------------------------------------------------------------

def test_the_gate_has_exactly_three_outcomes_and_no_almost_pass():
    rule = CHECKPOINT["uncertainty_rule"]
    assert rule["almost_pass"] == "does not exist"
    for key in ("pass", "fail", "inconclusive"):
        assert rule[key]
    assert "0.03" in rule["pass"] and "4.0" in rule["pass"]


def test_route_b_uncertainty_includes_the_truncation_residual():
    rule = CHECKPOINT["uncertainty_rule"]
    assert "T_B" in rule["se_b"]
    assert "rounded outward" in rule["T_B"]


def test_no_multiple_comparison_correction_is_introduced_or_removed():
    assert "none applied and none removed" in \
        CHECKPOINT["uncertainty_rule"]["multiple_comparison_correction"]


# --- seed determinism / resume identity --------------------------------------

def test_seed_policy_forbids_schedule_dependent_inputs():
    policy = CHECKPOINT["seed_policy"]
    assert policy["disjoint_from_historical_p4_p4x_seeds"] is True
    protocol = json.loads((P4 / "configs" / "P4_PROTOCOL.json").read_text())
    historical = set(protocol["master_seeds"].values())
    for key, value in policy.items():
        if isinstance(value, int):
            assert value not in historical, key
    for banned in ("worker id", "pid", "shard index", "schedule", "wall clock"):
        assert banned in policy["forbidden_seed_inputs"]


def test_the_stream_rule_is_the_inherited_one():
    from rebaseguard_p4_general.simulate import STREAM_STRIDE, stream_counter
    assert STREAM_STRIDE == 1 << 64
    assert stream_counter(3, 7) == ((3 << 32) | 7) * (1 << 64)
    assert "((batch << 32) | step) * 2**64" in \
        CHECKPOINT["seed_policy"]["stream_rule"]


# --- historical namespaces untouched -----------------------------------------

def test_p4z_touches_no_historical_namespace():
    changed = _git("diff", "--name-only", "p5y-gate1-micropilots", "HEAD")
    for path in filter(None, changed.splitlines()):
        assert path.startswith(
            "level4/closure_proofs/p4z_location_family_feasibility/"), path


def test_p4_verdict_is_still_partial_and_p4z_claims_nothing_more():
    decision = json.loads(
        (P4 / "results" / "closure_decision.json").read_text())
    assert decision["verdict"] == "PARTIAL"
    assert CHECKPOINT["immutable_history"]["P4_ORIGINAL_VERDICT"] == "PARTIAL"
    for claim in ("historical P4 repaired", "P4 CLOSED", "P5Y CLOSED",
                  "Level-4 CLOSED", "production ready",
                  "the P4Z gate will pass"):
        assert claim in CHECKPOINT["claims_explicitly_not_made"]


#: The commit at which the feasibility checkpoint was frozen.  Its claims were
#: true then and are asserted against that commit, not against the working tree,
#: so that promoting the Mac to a result-bearing host cannot quietly erase them.
FEASIBILITY_CHECKPOINT_COMMIT = "d46fc6846303946a717dffac71c4755e94194067"


def test_the_feasibility_checkpoint_shipped_no_production_driver():
    """True at d46fc68 and asserted there.  The driver that exists now was
    authorised by a later commit, and the checkpoint still says so."""
    listing = _git("ls-tree", "-r", "--name-only",
                   FEASIBILITY_CHECKPOINT_COMMIT,
                   "level4/closure_proofs/p4z_location_family_feasibility/")
    assert listing, "the feasibility checkpoint commit must be reachable"
    assert not any("/production/" in line for line in listing.splitlines())
    assert CHECKPOINT["full_run_command"]["authorised_by_this_checkpoint"] is False
    assert CHECKPOINT["production_run_launched"] is False
    assert CHECKPOINT["scientific_results_produced"] is False


#: Governance INPUTS and run state.  These are contracts and plans, bound by
#: hash in the producer manifest; "result bearing" is a property of outputs, so
#: they do not carry the flag.  The set is enumerated here so that a new schema
#: cannot join it silently.
GOVERNANCE_SCHEMAS = frozenset({
    "rebaseguard.p4z-campaign-plan.v1",
    "rebaseguard.p4z-mac-runtime-contract.v1",
    "rebaseguard.p4z-stage0-freeze.v1",
    "rebaseguard.p4z-run-state.v1",
    "rebaseguard.p4z-checkpoint.v1",
    "rebaseguard.p4z-estimand-contract.v1",
    "rebaseguard.p4z-producer-manifest.v1",
})


def test_every_output_artifact_declares_whether_it_is_result_bearing():
    """No OUTPUT may be ambiguous about its own status; inputs are exempt, and
    the exempt set is enumerated so nothing joins it silently."""
    roots = [NS / "results", NS / "micropilots" / "diagnostics",
             NS / "production", NS / "configs"]
    seen = 0
    for root in roots:
        if not root.exists():
            continue
        for path in root.glob("*.json"):
            doc = json.loads(path.read_text())
            schema = doc.get("schema")
            if schema is None or schema in GOVERNANCE_SCHEMAS:
                continue
            assert "result_bearing" in doc, f"{path} does not declare its status"
            seen += 1
    assert seen > 0


def test_no_unenumerated_schema_escapes_the_result_bearing_requirement():
    """Every governance schema actually present must be in the enumerated set."""
    for root in (NS / "production", NS / "configs"):
        for path in root.glob("*.json"):
            schema = json.loads(path.read_text()).get("schema")
            if schema and "result_bearing" not in json.loads(path.read_text()):
                assert schema in GOVERNANCE_SCHEMAS, (
                    f"{path} carries neither a result_bearing flag nor a "
                    "recognised governance schema")


def test_the_feasibility_phase_artifacts_remain_non_result_bearing():
    """Nothing produced during the feasibility phase may be relabelled."""
    for root in (NS / "results", NS / "micropilots" / "diagnostics"):
        for path in root.glob("*.json"):
            doc = json.loads(path.read_text())
            if path.name == "lean_audit.json":
                continue          # produced in the production phase
            assert doc.get("result_bearing") is False, path


def test_result_bearing_artifacts_live_only_under_production_or_are_declared():
    """A result-bearing artifact must say so and must not sit among the
    feasibility outputs unannounced."""
    for path in (NS / "production").rglob("*.json"):
        doc = json.loads(path.read_text())
        if doc.get("schema", "").startswith("rebaseguard.p4z-block"):
            assert doc["result_bearing"] is True, path
