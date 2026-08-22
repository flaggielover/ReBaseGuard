"""Stage E tests: data ordering, split integrity, determinism, residual and
drift definitions, matched streams, leakage, protocol hash, decision rule and
claim guard."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
RES = ROOT / "results"
sys.path.insert(0, str(SRC))

from drift import delta_profile, inject, injection_grid       # noqa: E402
from loaders import LOADERS                                   # noqa: E402
from monitor import M_WINDOW, run_monitor                     # noqa: E402
from residuals import (                                       # noqa: E402
    MODEL_SPEC, build_stream, chronological_split, fit_ridge, predict,
)

PROTO_SHA = "974487019f57c7c319b3bfafcdc20497ab6fca86834ad0d2245a694296ef23cc"
TASKS = ("electricity", "air_quality", "bike_sharing")
CONF = {t: f"task_{t}_confirmatory.json" for t in TASKS}


def load(n):
    return json.loads((RES / n).read_text())


# --------------------------------------------------------- protocol integrity
def test_protocol_hash_unchanged():
    actual = hashlib.sha256((ROOT / "STAGE_E_PROTOCOL.md").read_bytes()).hexdigest()
    assert actual == PROTO_SHA


def test_protocol_hash_record_matches_file():
    assert load("protocol_hash.json")["sha256"] == PROTO_SHA


def test_stage_e_seeds_disjoint_from_prior_work():
    prior = {1234, 1729, 2024, 2026, 4242, 5150, 8080, 31337, 90210,
             20260820, 20260821, 20260822, 20260901, 20260902, 20260931,
             20261001, 20261002, 20261031}
    assert set(load("protocol_hash.json")["seeds"].values()).isdisjoint(prior)


# ------------------------------------------------------------- data ordering
def test_electricity_uses_row_order_not_the_nonmonotone_date():
    """Elec2's `date` has five backward jumps; row order is authoritative.
    This pins the decision so it cannot be silently reverted to sorting."""
    s = LOADERS["electricity"]()
    rows = []
    in_data = False
    for line in (ROOT / "data" / "_cache" / "electricity-normalized.arff").read_text().splitlines():
        t = line.strip()
        if not t:
            continue
        if t.lower().startswith("@data"):
            in_data = True
        elif in_data:
            rows.append(t.split(","))
    date = np.array([float(r[0]) for r in rows])
    assert not np.all(np.diff(date) >= 0), "date is monotone; the anomaly changed"
    assert int((np.diff(date) < 0).sum()) == 5
    assert s.X.shape[0] == len(rows)


def test_electricity_period_cycles_cleanly_in_row_order():
    rows, in_data = [], False
    for line in (ROOT / "data" / "_cache" / "electricity-normalized.arff").read_text().splitlines():
        t = line.strip()
        if not t:
            continue
        if t.lower().startswith("@data"):
            in_data = True
        elif in_data:
            rows.append(t.split(","))
    per = np.rint(np.array([float(r[2]) for r in rows]) * 47).astype(int)
    d = np.diff(per)
    assert np.all((d == 1) | ((per[:-1] == 47) & (per[1:] == 0)))


def test_bike_sharing_excludes_target_leaking_columns():
    s = LOADERS["bike_sharing"]()
    assert "casual" not in s.feature_names and "registered" not in s.feature_names


def test_air_quality_missing_code_rows_removed():
    s = LOADERS["air_quality"]()
    assert np.all(s.X > -200) and np.all(s.y > -200)
    assert s.X.shape[0] == 8991


@pytest.mark.parametrize("task", TASKS)
def test_loader_is_deterministic(task):
    a, b = LOADERS[task](), LOADERS[task]()
    assert np.array_equal(a.X, b.X) and np.array_equal(a.y, b.y)
    assert a.source_sha256 == b.source_sha256


@pytest.mark.parametrize("task", TASKS)
def test_loader_checksum_matches_manifest(task):
    assert LOADERS[task]().source_sha256 == load("data_manifest.json")["_streams"][task]["source_sha256"]


# ------------------------------------------------------------ split integrity
def test_split_is_chronological_contiguous_and_complete():
    sp = chronological_split(1000)
    assert sp.train.start == 0 and sp.train.stop == sp.calib.start
    assert sp.calib.stop == sp.eval.start and sp.eval.stop == 1000


@pytest.mark.parametrize("task", TASKS)
def test_recorded_split_is_contiguous(task):
    s = load(CONF[task])["split"]
    n = load(CONF[task])["n_total"]
    assert s["train"][0] == 0 and s["train"][1] == s["calib"][0]
    assert s["calib"][1] == s["eval"][0] and s["eval"][1] == n


# ------------------------------------------------------------- no leakage
@pytest.mark.parametrize("task", TASKS)
def test_threshold_calibrated_only_on_calibration_block(task):
    d = load(CONF[task])
    cb, s = d["calibration"]["calibration_block"], d["split"]
    assert cb[0] >= s["calib"][0] and cb[1] <= s["calib"][1]


@pytest.mark.parametrize("task", TASKS)
def test_injection_grid_lies_inside_the_evaluation_block(task):
    d = load(CONF[task])
    g, s = d["injection_grid"], d["split"]
    assert min(g) >= s["eval"][0] and max(g) < s["eval"][1]


def test_residual_scale_comes_from_the_reference_block_only():
    """Refitting the scale on the full stream must give a different number --
    otherwise the test could not detect a leak."""
    for task in TASKS:
        ms = build_stream(LOADERS[task]())
        full = float(ms.residual.std())
        assert ms.scale == pytest.approx(float(ms.residual[ms.split.train].std()))
        assert abs(full - ms.scale) > 1e-9


# --------------------------------------------------------- deterministic model
def test_ridge_is_deterministic_and_has_no_rng():
    rng = np.random.default_rng(0)
    X, y = rng.normal(size=(300, 4)), rng.normal(size=300)
    a, b = fit_ridge(X, y), fit_ridge(X, y)
    assert np.array_equal(a["beta"], b["beta"])


def test_ridge_recovers_a_known_linear_signal():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(4000, 3))
    y = 2.0 + 1.5 * X[:, 0] - 0.5 * X[:, 1]
    m = fit_ridge(X, y, lam=1e-8)
    assert np.allclose(predict(m, X), y, atol=1e-3)


@pytest.mark.parametrize("task", TASKS)
def test_model_spec_matches_the_recorded_run(task):
    assert load(CONF[task])["model_kind"] == MODEL_SPEC[task][0]


# ------------------------------------------------------------ drift injection
def test_step_drift_timing_and_magnitude_are_exact():
    d = delta_profile(100, 40, "STEP", 1.5)
    assert np.all(d[:40] == 0.0) and np.all(d[40:] == 1.5)


def test_gradual_drift_ramps_then_holds():
    d = delta_profile(600, 100, "GRAD", 1.0)
    assert d[99] == 0.0
    assert d[100 + 100] == pytest.approx(0.5, abs=1e-9)
    assert d[100 + 200] == pytest.approx(1.0)
    assert d[-1] == pytest.approx(1.0)


def test_recurring_drift_alternates_on_and_off():
    d = delta_profile(2000, 0, "RECUR", 1.0)
    assert np.all(d[:300] == 1.0) and np.all(d[300:600] == 0.0)
    assert np.all(d[600:900] == 1.0)


def test_in_control_condition_injects_nothing():
    assert np.all(delta_profile(500, 10, "IC", 1.0) == 0.0)


def test_injection_preserves_the_real_stream_apart_from_a_known_offset():
    r = np.random.default_rng(2).normal(size=500)
    out = inject(r, scale=2.0, t0=200, condition="STEP", magnitude=1.0)
    assert np.array_equal(out[:200], r[:200])
    assert np.allclose(out[200:] - r[200:], 2.0)


def test_injection_grid_is_deterministic_and_inside_bounds():
    a = injection_grid(1000, 500, 10, 20261101)
    b = injection_grid(1000, 500, 10, 20261101)
    assert np.array_equal(a, b)
    assert a.min() >= 500 + 100 and a.max() <= 500 + 900


# ------------------------------------------------------------- matched streams
@pytest.mark.parametrize("task", TASKS)
def test_policies_share_everything_except_rho(task):
    d = load(CONF[task])
    assert len(set(d["policies"].values())) == 4
    assert d["policies"]["P0_fresh"] == 0.0
    assert d["policies"]["P1_full_reuse"] == 1.0
    assert d["policies"]["P2_rebaseguard"] == 0.029796


def test_only_rho_changes_the_monitor_output():
    r = np.random.default_rng(3).normal(size=6000)
    kw = dict(scale=1.0, threshold=6.0, r0=0.0, start=0, stop=6000)
    a = run_monitor(r, rho=0.0, **kw)
    b = run_monitor(r, rho=1.0, **kw)
    assert [c.alarm for c in a.cycles] != [c.alarm for c in b.cycles]
    c = run_monitor(r, rho=0.0, **kw)
    assert [x.alarm for x in a.cycles] == [x.alarm for x in c.cycles]


def test_every_policy_consumes_the_fresh_settling_block():
    """No sample-efficiency claim is possible: the next cycle starts at
    alarm + 1 + m for EVERY rho, so fresh consumption is identical."""
    r = np.random.default_rng(4).normal(size=8000)
    for rho in (0.0, 0.029796, 1.0):
        run = run_monitor(r, scale=1.0, threshold=6.0, rho=rho, r0=0.0,
                          start=0, stop=8000)
        for prev, nxt in zip(run.cycles, run.cycles[1:]):
            assert nxt.start == prev.alarm + 1 + M_WINDOW


# --------------------------------------------------------- reproducibility
def test_monitor_is_deterministic():
    r = np.random.default_rng(5).normal(size=4000)
    kw = dict(scale=1.0, threshold=5.0, rho=0.3, r0=0.0, start=0, stop=4000)
    a, b = run_monitor(r, **kw), run_monitor(r, **kw)
    assert [c.alarm for c in a.cycles] == [c.alarm for c in b.cycles]
    assert [c.reference for c in a.cycles] == [c.reference for c in b.cycles]


# ------------------------------------------------------------- decision rule
def test_adversarial_suite_recorded_and_complete():
    a = load("adversarial.json")
    assert a["n_checks"] == 14


def test_decision_label_is_one_of_the_frozen_three():
    d = load("stage_e_decision.json")
    assert d["decision"] in {"STAGE-E-CLOSED-EXTERNAL-VALIDATION",
                             "STAGE-E-PARTIAL", "STAGE-E-FAILED"}


def test_task_A_and_B_do_not_count_and_task_C_is_partially_usable():
    d = load("stage_e_decision.json")
    per = d["per_task"]
    assert per["electricity"]["counts_toward_H_E5"] is False
    assert per["air_quality"]["counts_toward_H_E5"] is False
    assert per["bike_sharing"]["counts_toward_H_E5"] is False
    assert per["air_quality"]["power_class"] == "LOW-POWER"
    assert per["bike_sharing"]["usability"] == "PARTIALLY USABLE AFTER FREEZE"


def test_closure_was_unreachable_and_is_recorded_as_such():
    d = load("stage_e_decision.json")
    assert d["closure_mathematically_unreachable"] is True
    assert d["n_tasks_supporting_H_E5"] < 2


def test_task_C_E2_E3_marked_unreliable():
    d = load("stage_e_decision.json")
    u = d["per_task"]["bike_sharing"]["unreliable_endpoints"]
    assert "E2" in u and "E3" in u


def test_exploratory_policy_never_enters_a_hypothesis():
    d = load("stage_e_decision.json")
    blob = json.dumps(d["per_task"])
    for t in TASKS:
        for h in d["per_task"][t]["hypotheses"].values():
            assert "P3" not in json.dumps(h)
    assert "P3_moderate_EXPLORATORY" in d["exploratory_policy_excluded"]


# ---------------------------------------------------------------- claim guard
FORBIDDEN = ["production-proven", "industry-proven", "universally robust",
             "distribution-free", "detector-independent", "optimal",
             "real-world deployment validated", "sample savings",
             "data efficiency", "false-alarm rate"]


def _reports():
    return [ROOT.parent / "reports" / "STAGE_E_REPORT.md",
            ROOT.parent / "reports" / "STAGE_E_LEDGER.md"]


def _scannable(path: Path) -> str:
    """Strip the explicitly declared forbidden-phrase block: a section whose
    job is to list banned phrases must be allowed to contain them."""
    out, skip = [], False
    for line in path.read_text().splitlines():
        if line.startswith("#"):
            skip = "forbidden" in line.lower() or "ruled out" in line.lower()
        if not skip:
            out.append(line)
    return "\n".join(out).lower().replace("*", "").replace("`", "")


NEG = ("not ", "never", "no ", "❌", "rather than", "cannot", "must not",
       "ruled out", "unreachable", "does not")


@pytest.mark.parametrize("word", FORBIDDEN)
def test_forbidden_claim_only_appears_negated(word):
    for p in _reports():
        if not p.exists():
            continue
        txt = _scannable(p)
        for i in [m for m in range(len(txt)) if txt.startswith(word, m)]:
            w = txt[max(0, i - 130):i + len(word) + 60]
            assert any(n in w for n in NEG), (p.name, w)


def test_the_claim_guard_would_catch_an_affirmative_violation(tmp_path):
    bad = tmp_path / "STAGE_E_REPORT.md"
    bad.write_text("# X\n\nReBaseGuard is production-proven and optimal.\n")
    txt = _scannable(bad)
    i = txt.index("production-proven")
    assert not any(n in txt[max(0, i - 130):i + 60] for n in NEG)


def test_reports_declare_the_forbidden_block():
    for p in _reports():
        if p.exists():
            t = p.read_text().lower()
            assert "forbidden" in t or "ruled out" in t
