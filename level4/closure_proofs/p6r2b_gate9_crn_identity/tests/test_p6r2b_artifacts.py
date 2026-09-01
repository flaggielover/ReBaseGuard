"""The regenerated Gate-9 artifacts, plus provenance and regression."""
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
CLOSURE = NS.parent
ROOT = NS.parents[2]
RES = NS / "results"
CELLS8 = ("cusum_m1", "cusum_m2", "cusum_m3", "cusum_m5",
          "sr_m1", "sr_m2", "sr_m3", "sr_m5")
P6_NAMESPACES = tuple(f"level4/closure_proofs/{n}/" for n in (
    "p6_safe_rebaselining", "p6_safe_rebaselining_predesign",
    "p6r_safe_rebaselining_confirmation", "p6r2_literal_closure_repair",
    "p6r2b_gate9_crn_identity"))


def _j(name):
    p = RES / name
    if not p.exists():
        pytest.skip(f"{name} not produced yet")
    return json.loads(p.read_text())


# --- strict JSON ------------------------------------------------------------

@pytest.mark.parametrize("name", ("p6r2b_crn_identity.json",
                                  "p6r2b_crn_sensitivity.json"))
def test_artifacts_are_strict_json(name):
    p = RES / name
    if not p.exists():
        pytest.skip("not produced yet")
    raw = p.read_text()
    for tok in ("NaN", "Infinity", "-Infinity"):
        assert tok not in raw
    json.loads(raw, parse_constant=lambda c: (_ for _ in ()).throw(
        AssertionError(f"non-standard constant {c!r}")))


# --- identity artifact ------------------------------------------------------

def test_identity_artifact_reports_primitive_identity_in_every_cell():
    d = _j("p6r2b_crn_identity.json")
    assert set(d["cells"]) == set(CELLS8)
    assert d["all_cells_primitive_identity"] is True
    for k, c in d["cells"].items():
        assert c["primitive_stream_identity"] is True, k
        assert c["endogenous_path_identity"] == "NOT_REQUIRED", k
        assert c["max_abs_difference_monitor"] == 0.0, k
        assert c["max_abs_difference_fresh"] == 0.0, k
        assert c["max_abs_difference_overflow"] in (None, 0.0), k
        assert c["primitive_field_digests_match"] is True, k
        assert c["n_primitive_monitor_draws_compared"] > 1_000_000, k
        assert c["n_fresh_draws_compared"] > 0, k


def test_identity_artifact_compares_deep_overflow_addresses():
    """The exact P6R2 failure region must be covered by real comparisons."""
    d = _j("p6r2b_crn_identity.json")
    for k, c in d["cells"].items():
        assert c["n_overflow_draws_compared"] > 0, k
        assert c["deepest_observation_index_compared"] >= 2047, k
        deep = [p for p in c["ladder_checkpoints"]
                if p["past_first_block"] and p["n_comparisons"]]
        assert deep, k
        assert all(p["max_abs_diff"] == 0.0 for p in deep), k
        assert c["max_block_index_touched"] >= 4, k       # t > 2047 was reached


def test_identity_artifact_does_not_claim_whole_path_equality():
    d = _j("p6r2b_crn_identity.json")
    blob = json.dumps(d)
    assert "all_paths_identical" not in blob
    assert "exogenous primitive random field" in d["cells"][CELLS8[0]]["statement"]
    assert "endogenous trajectories may diverge" in d["cells"][CELLS8[0]]["statement"]


def test_endogenous_divergence_is_recorded_not_suppressed():
    """Divergence must be measured and reported, never forced to zero."""
    d = _j("p6r2b_crn_identity.json")
    total = sum(sum(c["endogenous_tau_divergences_vs_baseline"].values())
                for c in d["cells"].values())
    assert total > 0, "no endogenous divergence at all is implausible"
    for c in d["cells"].values():
        assert c["endogenous_tau_divergences_vs_baseline"]["baseline"] == 0
        assert c["endogenous_entering_state_divergences_vs_baseline"]["baseline"] == 0


def test_address_exclusions_are_declared_in_the_artifact():
    d = _j("p6r2b_crn_identity.json")
    for banned in ("policy_id", "sensitivity_variant", "s1_multiplier",
                   "live_set_position", "stopping_time", "branch_order",
                   "n_previously_consumed_draws"):
        assert banned in d["address_excludes"]


# --- sensitivity artifact ---------------------------------------------------

def test_sensitivity_keeps_the_shipped_constants_and_does_not_recalibrate():
    aud = json.loads((CLOSURE / "p6r_safe_rebaselining_confirmation" / "precommit"
                      / "calibration_audit.json").read_text())
    s = _j("p6r2b_crn_sensitivity.json")
    assert s["saw_m_recalibrated"] is False
    assert s["shipped_constants_changed"] is False
    assert s["n_rep"] == 1500 and s["n_cycles"] == 60 and s["burn_in"] == 15
    assert tuple(s["variants"]) == ("baseline", "s1_x0.5", "s1_x2.0", "s1_eq_s0")
    for k, c in aud["cells"].items():
        sh = s["cells"][k]["shipped"]
        for f in ("g0", "g1", "s0", "s1"):
            assert sh[f] == c[f], (k, f)
        assert s["cells"][k]["variants"]["baseline"]["s1_used"] == c["s1"]


def test_calibration_limitations_are_carried_forward_unchanged():
    aud = json.loads((CLOSURE / "p6r_safe_rebaselining_confirmation" / "precommit"
                      / "calibration_audit.json").read_text())
    s = _j("p6r2b_crn_sensitivity.json")
    cf = s["calibration_summary_carried_forward"]
    assert cf["all_converged"] is False and cf["n_converged"] == 6
    assert set(cf["non_converged_cells"]) == {"cusum_m2", "sr_m3"}
    assert cf["final_refit_is_a_verified_fixed_point"] is False
    assert s["does_not_claim"].startswith("This experiment does NOT prove")
    for k, c in aud["cells"].items():
        f = s["cells"][k]["calibration_facts_carried_forward"]
        assert f["converged"] == c["converged"]
        assert f["n_obs_behind_s1"] == c["n_obs_behind_s1"]
        assert f["s1_is_fallback_equal_to_s0"] == c["s1_is_fallback_equal_to_s0"]
        assert f["final_refit_followed_by_another_fixed_point_update"] is False


def test_cells_where_s1_cannot_fire_are_explained_and_move_exactly_zero():
    s = _j("p6r2b_crn_sensitivity.json")
    for k, c in s["cells"].items():
        if not c["s1_can_fire_under_observed_trajectories"]:
            assert c["n_cycles_where_s1_can_fire_tau_lt_m"] == 0, k
            assert c["why_if_not"] and "tau < m" in c["why_if_not"], k
            for mm in ("rho_mean", "rms", "arl0"):
                assert c["max_abs_relative_change"][mm] == 0.0, (k, mm)
        else:
            assert c["why_if_not"] is None, k


# --- provenance and regression ---------------------------------------------

def test_frozen_inputs_are_byte_identical():
    fr = json.loads((NS / "precommit" / "frozen_inputs.json").read_text())
    bad = [rel for rel, w in fr["files"].items()
           if hashlib.sha256((CLOSURE / rel).read_bytes()).hexdigest() != w["sha256"]]
    assert not bad, bad
    assert fr["head_matches"] is True


def test_no_historical_artifact_was_modified():
    """P6, P6R and P6R2 are evidence.  P6R2b may only touch its OWN namespace.

    (P6R2b's own modules were iterated between the pre-repair anchor and the
    result checkpoint -- a bad negative-cycle key and an over-expensive field
    hash were fixed before any result was generated.  That is inside its
    namespace and is recorded in GATE9_REPAIR_REPORT.md.)
    """
    out = subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    changed = [f for f in out.splitlines() if f.strip()]
    own = "level4/closure_proofs/p6r2b_gate9_crn_identity/"
    historical = [f for f in changed if not f.startswith(own)]
    assert not historical, f"historical artifacts modified: {historical}"


def test_historical_p6r_and_p6r2_manifests_still_verify():
    man = json.loads((CLOSURE / "p6r_safe_rebaselining_confirmation" / "precommit"
                      / "historical_p6_manifest.json").read_text())
    bad = [rel for rel, want in man["files"].items()
           if hashlib.sha256((CLOSURE / rel).read_bytes()).hexdigest() != want]
    assert not bad, bad
    fr = json.loads((CLOSURE / "p6r2_literal_closure_repair" / "precommit"
                     / "frozen_inputs.json").read_text())
    bad2 = [rel for rel, w in fr["files"].items()
            if hashlib.sha256((CLOSURE / rel).read_bytes()).hexdigest() != w["sha256"]]
    assert not bad2, bad2


def test_p6r2b_writes_only_into_its_own_namespace():
    out = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    off = [l for l in out.splitlines() if l.strip() and not l[3:].strip().startswith(
        "level4/closure_proofs/p6r2b_gate9_crn_identity/")]
    assert not off, off


def test_p6r2b_reruns_only_the_gate9_sensitivity():
    """No primary experiment may be re-executed from this namespace."""
    for f in (NS / "experiments").rglob("*.py"):
        t = f.read_text()
        for banned in ("run_delay", "run_incontrol", "calibrate_saw",
                       "tune_selection", "select_rho", "paired_ratio_of_means"):
            assert banned not in t, f"{f.name} touches {banned}"


def test_p6r2b_does_not_reimplement_the_scientific_object():
    names = {f.name for f in (NS / "src" / "rebaseguard_p6r2b").glob("*.py")}
    for forbidden in ("saw.py", "policy.py", "calibrate.py", "select.py",
                      "effects.py", "twoblock.py", "families.py"):
        assert forbidden not in names, forbidden


def test_the_frozen_detector_step_is_imported_not_reimplemented():
    from rebaseguard_p6r2b import simulate as SM
    import inspect
    src = inspect.getsource(SM)
    assert "from rebaseguard_p7.detectors import make_step" in src
    assert "def cusum_update" not in src and "logaddexp" not in src
