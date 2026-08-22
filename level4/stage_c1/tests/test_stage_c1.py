"""Stage C.1: metric correctness, seed independence, and immutability of Stage C."""

from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import numpy as np
import pytest

import campaign_c1
import metric
import policy
from campaign_c1 import SEED_ADVERSARIAL, SEED_CONFIRM, SEED_SMOKE, SHIFTS, rho_rbg
from detection import DetectionConfig, simulate_detection
from metric import estimate_R, estimate_difference, mean_of_ratios, ratio_of_means
from rebaseguard_level4.multicycle import MultiCycleConfig, simulate_multicycle
from rebaseguard_level4.streams import STREAM_OBS, generator

ROOT = Path(__file__).resolve().parents[3]
STAGE_C1 = ROOT / "level4" / "stage_c1"

# Every seed used anywhere before Stage C.1.
PRIOR_SEEDS = {1234, 1729, 2024, 2026, 4242, 5150, 8080, 31337, 90210,
               20260820, 20260821, 20260822}


# ----------------------------------------------------------- protocol frozen --

def test_protocol_hash_matches_the_frozen_record():
    """The protocol must not have changed since it was frozen."""
    rec = json.loads((STAGE_C1 / "results" / "protocol_hash.json").read_text())
    actual = hashlib.sha256(
        (STAGE_C1 / "STAGE_C1_PROTOCOL.md").read_bytes()).hexdigest()
    assert actual == rec["sha256"], (
        "STAGE_C1_PROTOCOL.md changed after it was frozen; that is exactly what "
        "the hash exists to prevent")
    assert rec["epsilon"] == 0.05
    assert rec["shifts"] == [0.25, 0.5, 1.0, 1.5]


def test_frozen_margin_and_shifts_are_used_everywhere():
    import run_analysis_c1
    assert run_analysis_c1.EPSILON == 0.05
    assert tuple(SHIFTS) == (0.25, 0.5, 1.0, 1.5)


# ------------------------------------------------------------ seed disjointness --

@pytest.mark.parametrize("seed", [SEED_SMOKE, SEED_CONFIRM, SEED_ADVERSARIAL])
def test_stage_c1_seeds_are_new(seed):
    assert seed not in PRIOR_SEEDS, f"seed {seed} was already used by an earlier stage"


@pytest.mark.parametrize("seed", [SEED_CONFIRM, SEED_ADVERSARIAL])
def test_stage_c1_streams_do_not_overlap_stage_c(seed):
    """Different master seeds must give genuinely different draws."""
    for row in (0, 1, 7, 99):
        a = generator(20260821, STREAM_OBS, row).standard_normal(500)
        b = generator(seed, STREAM_OBS, row).standard_normal(500)
        assert not np.allclose(a, b)
        assert abs(float(np.corrcoef(a, b)[0, 1])) < 0.2


def test_confirmatory_and_adversarial_seeds_differ():
    a = generator(SEED_CONFIRM, STREAM_OBS, 0).standard_normal(500)
    b = generator(SEED_ADVERSARIAL, STREAM_OBS, 0).standard_normal(500)
    assert not np.allclose(a, b)


def test_runner_refuses_a_previously_used_seed():
    import run_confirmatory
    with pytest.raises(SystemExit, match="overlaps"):
        run_confirmatory.main(["x", "--seed", "20260821"])


# ---------------------------------------------------------------- the policy --

def test_rho_is_taken_verbatim_from_stage_c():
    assert rho_rbg() == policy.rho_safe(0.2, variant=policy.CONSERVATIVE).rho
    assert rho_rbg() == pytest.approx(0.02979584394902044, abs=1e-15)


def test_stage_c1_cannot_reach_the_policy_definition():
    """No Stage C.1 identifier or outcome may appear in the policy module."""
    src = inspect.getsource(policy)
    for token in ("stage_c1", "confirmatory", "R_delta", "20260901",
                  "20260902", "non_inferior", "epsilon"):
        assert token not in src, f"policy.py references {token!r}"


def test_rho_is_not_recomputed_by_stage_c1():
    """campaign_c1 must import rho, never re-derive it."""
    src = inspect.getsource(campaign_c1)
    assert "import policy" in src
    assert "GAMMA" not in src, "Stage C.1 must not re-derive rho from Gamma"


# ----------------------------------------------------- simulator is unmodified --

@pytest.mark.parametrize("rho", [0.0, 0.02979584394902044, 1.0])
def test_detection_simulator_still_reproduces_stage_a_at_zero_shift(rho):
    cfg = DetectionConfig(n_replicates=6, burn_in=5, n_cycles_after=15,
                          rho=rho, shift=0.0, master_seed=31337)
    got = simulate_detection(cfg)
    want = simulate_multicycle(MultiCycleConfig(
        n_replicates=6, n_cycles=20, burn_in=0, rho=rho, m=1, master_seed=31337))
    assert np.array_equal(got.tau, want.tau)
    assert np.array_equal(got.e_next, want.e_next)


def test_many_events_structure_does_not_change_the_measured_quantity():
    """K events per replicate is a variance device, not a different experiment."""
    few = campaign_c1.arm(rho=0.0, shift=0.5, n_replicates=1500, n_events=1,
                          burn_in=200, cycles_between=15, master_seed=SEED_SMOKE)
    many = campaign_c1.arm(rho=0.0, shift=0.5, n_replicates=150, n_events=60,
                           burn_in=200, cycles_between=15, master_seed=SEED_SMOKE)
    d = np.array(few["per_replicate_mean_delay"])
    se = d.std(ddof=1) / np.sqrt(d.size)
    assert abs(few["grand_mean_delay"] - many["grand_mean_delay"]) < 4 * se


# -------------------------------------------------------------- the metric --

def test_R_recovers_a_known_ratio():
    rng = np.random.default_rng(3)
    den = rng.gamma(20, 4, 300)
    num = den * 0.6
    e = estimate_R(num, den, name="t", seed=SEED_SMOKE, index=0, n_boot=1500)
    assert e.point == pytest.approx(0.6, abs=1e-9)


def test_R_uses_its_own_denominator():
    """Sanity check F, as arithmetic: swapping denominators must change R."""
    rng = np.random.default_rng(5)
    den_a, den_b = rng.gamma(20, 4, 200), rng.gamma(20, 8, 200)
    num = den_a * 0.7
    own = estimate_R(num, den_a, name="a", seed=1, index=0, n_boot=500).point
    foreign = estimate_R(num, den_b, name="b", seed=1, index=1, n_boot=500).point
    assert own == pytest.approx(0.7, abs=1e-9)
    assert abs(foreign - 0.7) > 0.2


def test_paired_difference_of_identical_arms_is_exactly_zero():
    rng = np.random.default_rng(7)
    num, den = rng.gamma(10, 3, 150), rng.gamma(10, 3, 150)
    d = estimate_difference(num, den, num, den, name="d", seed=1, index=0,
                            n_boot=800)
    assert d.point == 0.0 and d.ci_low == 0.0 and d.ci_high == 0.0


def test_pairing_is_tighter_than_no_pairing():
    rng = np.random.default_rng(11)
    common = rng.gamma(20, 4, 300)
    a_num, a_den = common * 0.60, common
    b_num, b_den = common * 0.62, common
    paired = estimate_difference(a_num, a_den, b_num, b_den, name="p", seed=1,
                                 index=0, n_boot=1500)
    assert paired.se < 1e-6
    assert paired.point == pytest.approx(-0.02, abs=1e-9)


def test_estimator_variants_differ_but_agree_closely_on_tame_data():
    rng = np.random.default_rng(13)
    den = rng.gamma(40, 2, 400)
    num = den * 0.8 + rng.normal(0, 1, 400)
    assert ratio_of_means(num, den) != mean_of_ratios(num, den)
    assert ratio_of_means(num, den) == pytest.approx(mean_of_ratios(num, den),
                                                     abs=0.01)


def test_misaligned_arrays_are_rejected():
    with pytest.raises(ValueError):
        estimate_R(np.zeros(5), np.zeros(6), name="x", seed=1, index=0)
    with pytest.raises(ValueError):
        estimate_difference(np.zeros(5), np.zeros(5), np.zeros(6), np.zeros(6),
                            name="x", seed=1, index=0)


# ------------------------------------------------- Stage C remains immutable --

def test_stage_c_decision_is_untouched():
    f = json.loads((ROOT / "level4/stage_c/results/findings.json").read_text())
    assert f["decision"] == "STAGE-C-PARTIAL"
    assert f["decision_basis"]["failed"] == ["C6"]


def test_stage_c_c6_is_still_recorded_as_failed():
    txt = (ROOT / "level4/reports/STAGE_C_METHOD_REPORT.md").read_text()
    assert "STAGE-C-PARTIAL" in txt
    assert "**FAIL**" in txt
    for forbidden in ("C6 actually passed", "C6 was corrected",
                      "C6 now passes"):
        assert forbidden not in txt


NEVER_ALLOWED = (
    # so specific that even a negated mention would confuse the record
    "c6 actually passed", "c6 was corrected", "c6 now passes", "supersedes c6",
    "c6 is superseded", "c6 passes after all",
)

NEGATED_ONLY = (
    # permitted ONLY as an explicit disclaimer
    "universally better", "is optimal", "sample efficiency",
    "rigorous certified", "rigorously certified",
)

NEGATIONS = ("not", "no ", "never", "cannot", "without", "neither", "nor ",
             "excluded", "prohibited", "makes no")


def _normalise(text: str) -> str:
    """Formatting must not let a phrase -- or a negation -- slip past the guard.

    Three defects found while building this guard, each fixed here:
      * "sample efficiency" was searched for while the report wrote
        "sample-efficiency", so a real violation would have gone unnoticed;
      * markdown emphasis broke the negation match, because "**no**" does not
        contain the substring "no ";
      * backticks around inline code did the same.
    Stripping hyphens, underscores, asterisks and backticks removes all three,
    and it also means an author cannot hide a violation behind formatting.
    """
    out = text.lower()
    for ch in ("-", "_", "*", "`"):
        out = out.replace(ch, " " if ch in "-_" else "")
    return out


def test_stage_c1_report_never_claims_c6_passed():
    p = ROOT / "level4/reports/STAGE_C1_CONFIRMATORY_REPORT.md"
    if not p.exists():
        pytest.skip("report not generated yet")
    txt = _normalise(p.read_text())
    for phrase in NEVER_ALLOWED:
        assert _normalise(phrase) not in txt, phrase


def test_stage_c1_report_uses_forbidden_claims_only_as_disclaimers():
    """These phrases may appear, but only inside an explicit denial."""
    p = ROOT / "level4/reports/STAGE_C1_CONFIRMATORY_REPORT.md"
    if not p.exists():
        pytest.skip("report not generated yet")
    txt = _normalise(p.read_text())
    for phrase in NEGATED_ONLY:
        needle = _normalise(phrase)
        start = 0
        while (i := txt.find(needle, start)) != -1:
            # look BOTH ways: "no X claim is well posed" and "X is not well
            # posed" are equally disclaimers, and a backward-only window
            # rejects the second while accepting neither more nor less abuse.
            window = txt[max(0, i - 120):i] + " " + txt[i + len(needle):
                                                        i + len(needle) + 60]
            assert any(n in window for n in NEGATIONS), (
                f"{phrase!r} appears without a nearby negation: "
                f"...{txt[max(0, i - 120):i + len(needle) + 60]}...")
            start = i + len(needle)


def _guard_flags(text: str) -> list[str]:
    """Re-implementation of the guard, used to test the guard itself."""
    txt = _normalise(text)
    flagged = []
    for phrase in NEGATED_ONLY:
        needle = _normalise(phrase)
        i = txt.find(needle)
        if i == -1:
            continue
        window = txt[max(0, i - 120):i] + " " + txt[i + len(needle):
                                                    i + len(needle) + 60]
        if not any(n in window for n in NEGATIONS):
            flagged.append(phrase)
    return flagged


@pytest.mark.parametrize("bad", [
    "Stage C.1 shows ReBaseGuard is universally better.",
    "ReBaseGuard improves sample-efficiency by a wide margin.",
    "The chosen rho is optimal for every shift.",
    "This result is rigorously certified by the confirmatory campaign.",
])
def test_guard_catches_affirmative_violations(bad):
    """A guard that never fires is worthless; these must all be caught."""
    assert _guard_flags(bad), f"guard missed: {bad!r}"


@pytest.mark.parametrize("ok", [
    "It does not mean ReBaseGuard is universally better.",
    "No sample-efficiency claim is made here.",
    "The policy is not optimal, and optimality is not claimed.",
    "Nothing here is rigorously certified.",
])
def test_guard_allows_genuine_disclaimers(ok):
    assert not _guard_flags(ok), f"guard wrongly fired on: {ok!r}"


def test_guard_is_not_defeated_by_markdown_emphasis():
    """**no** must still read as a negation, and **better** still as a claim."""
    assert not _guard_flags("Here **no** sample-efficiency claim is made.")
    assert not _guard_flags("It is **not** universally better.")
    assert _guard_flags("It is **universally better** in every regime.")


def test_guard_is_insensitive_to_hyphenation():
    """The first version missed 'sample-efficiency' while checking for a space."""
    assert _guard_flags("We improve sample efficiency.")
    assert _guard_flags("We improve sample-efficiency.")
    assert _guard_flags("We improve sample_efficiency.")
