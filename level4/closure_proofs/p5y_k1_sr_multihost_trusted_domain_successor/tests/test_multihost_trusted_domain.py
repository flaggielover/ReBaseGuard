"""Result-free fail-closed tests for the multi-host TRUSTED-NUMERIC-DOMAIN successor.

Adds the GLOBAL_CPU_CAP domain suite, the trusted-representation suite (only a
validator RETURN may enter governed arithmetic) and coercion-exception
normalisation, on top of the inherited accounting-integrity suite.

Inherits the cap-repair suite unchanged and adds the governed-accounting domain
suite (A-Q): no governed cost component may be NaN, +/-inf, negative or a bool,
and the aggregate is validated as well as its components.

Inherits the predecessor suite unchanged except for the prohibited per-host cap
test, which is replaced by the global-cap-only semantics suite (A-H).

Every invalid case MUST raise MultiHostRefusal. No test performs scientific
computation and no test emits a result-bearing SR cell.
"""
import copy
import json
import math
import sys
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "driver"))
import multihost as M                                              # noqa: E402

CKPT = json.loads((NS / "config/CHECKPOINT_HASH").read_text().strip() and
                  '"' + (NS / "config/CHECKPOINT_HASH").read_text().strip() + '"')
PRODUCER = "a" * 40
SHARD_SHA = json.loads((NS / "config/SHARD_MANIFEST_SHA256.json").read_text())["sha256"]

AWS_SIBS = {c: [c, c + 16] for c in range(16)}
VULTR_SIBS = {0: [0, 1], 1: [0, 1], 2: [2, 3], 3: [2, 3],
              4: [4, 5], 5: [4, 5], 6: [6, 7], 7: [6, 7]}


@pytest.fixture
def manifest():
    return json.loads((NS / "config/SHARD_MANIFEST.json").read_text())


@pytest.fixture
def owners(manifest):
    return M.gate_shards(manifest)


def record(cell, role, cpu_s, obligations=28, complete=True):
    return {"cell_id": cell, "role": role, "producer_commit": PRODUCER,
            "checkpoint_sha256": CKPT,
            "runtime_contract_hash": M.ROLES[role]["runtime_contract_hash"],
            "scientific_content_hash": "%064x" % cell,
            "cpu_seconds": cpu_s, "obligations_completed": obligations,
            "complete": complete}


@pytest.fixture
def ledgers(manifest):
    aws = [record(c, "AWS", 40000.0) for c in manifest["AWS"]["cells"]]
    vul = [record(c, "VULTR", 36000.0) for c in manifest["VULTR"]["cells"]]
    aws[0]["obligations_completed"] = 29          # the single far-field obligation
    return {"AWS": aws, "VULTR": vul}


# --------------------------------------------------------------- positive control
def test_valid_multihost_run_is_admitted(manifest, owners, ledgers):
    assert M.gate_role("AWS", "Amazon EC2") == "AWS"
    assert M.gate_role("VULTR", "Vultr") == "VULTR"
    M.gate_workers("AWS", 16, list(range(16)), AWS_SIBS)
    M.gate_workers("VULTR", 4, [0, 2, 4, 6], VULTR_SIBS)
    out = M.assemble_global_ledger(ledgers, owners, PRODUCER, CKPT)
    assert out["cells_completed"] == 316
    assert out["obligations_completed"] == 8849
    assert out["cap"]["charged_cpu_h"] <= M.GLOBAL_CPU_CAP
    M.verify_aggregate_ledger(out, out["aggregate_ledger_sha256"])


# ------------------------------------------------------------------ 1..16 refusals
def test_01_wrong_host_role():
    with pytest.raises(M.MultiHostRefusal):
        M.gate_role("AWS", "Vultr")
    with pytest.raises(M.MultiHostRefusal):
        M.detect_role("Google Compute Engine")


def test_02_wrong_runtime_hash():
    with pytest.raises(M.MultiHostRefusal):
        M.gate_runtime_hash("VULTR", M.ROLES["AWS"]["runtime_contract_hash"])


def test_03_wrong_worker_count():
    with pytest.raises(M.MultiHostRefusal):
        M.gate_workers("VULTR", 8, [0, 2, 4, 6], VULTR_SIBS)


def test_04_smt_misuse_is_refused():
    with pytest.raises(M.MultiHostRefusal):
        M.gate_workers("VULTR", 4, [0, 1, 2, 3], VULTR_SIBS)


def test_05_overlapping_shards(manifest):
    bad = copy.deepcopy(manifest)
    bad["VULTR"]["cells"] = bad["VULTR"]["cells"] + [bad["AWS"]["cells"][0]]
    with pytest.raises(M.MultiHostRefusal):
        M.gate_shards(bad)


def test_06_missing_cells(manifest):
    bad = copy.deepcopy(manifest)
    bad["AWS"]["cells"] = bad["AWS"]["cells"][:-1]
    with pytest.raises(M.MultiHostRefusal):
        M.gate_shards(bad)


def test_07_duplicate_ownership(manifest):
    bad = copy.deepcopy(manifest)
    bad["AWS"]["cells"] = bad["AWS"]["cells"] + [bad["AWS"]["cells"][0]]
    with pytest.raises(M.MultiHostRefusal):
        M.gate_shards(bad)


def test_08_wrong_shard_manifest():
    with pytest.raises(M.MultiHostRefusal):
        M.load_shard_manifest(NS / "config/SHARD_MANIFEST.json", "0" * 64)


def test_08b_authorised_shard_manifest_loads():
    man = M.load_shard_manifest(NS / "config/SHARD_MANIFEST.json", SHARD_SHA)
    assert man["cells_total"] == 316


def test_09_wrong_producer_commit():
    lm = json.loads((NS / "config/LAUNCH_MANIFEST.json").read_text())
    with pytest.raises(M.MultiHostRefusal):
        M.gate_producer_commit(lm, "b" * 40, CKPT, SHARD_SHA)


def test_10_foreign_host_cell(manifest, owners):
    aws_cell = manifest["AWS"]["cells"][0]
    with pytest.raises(M.MultiHostRefusal):
        M.gate_cell_ownership("VULTR", aws_cell, owners)


def test_11_cross_host_recomputation(manifest, owners, ledgers):
    bad = copy.deepcopy(ledgers)
    dup = manifest["AWS"]["cells"][0]
    bad["AWS"].append(record(dup, "AWS", 40000.0, obligations=0))
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(bad, owners, PRODUCER, CKPT)


def _ledgers_with(manifest, aws_cpu_s, vultr_cpu_s):
    """Ledgers over the frozen 247/69 shard at chosen per-cell CPU charges."""
    aws = [record(c, "AWS", aws_cpu_s) for c in manifest["AWS"]["cells"]]
    vul = [record(c, "VULTR", vultr_cpu_s) for c in manifest["VULTR"]["cells"]]
    aws[0]["obligations_completed"] = 29
    return {"AWS": aws, "VULTR": vul}


# ---- Codex counterexample, exactly as adjudicated -------------------------
def test_12_codex_counterexample_11_cpuh_vultr_cell(manifest, owners):
    """A single Vultr cell charged 11 CPU-h exceeds the former per-cell
    reservation of 10.217741 CPU-h. The predecessor's gate_per_host_reservation
    refused it (allowed = 10.217741 * 1 record). The governed campaign total is
    only ~249.6489 CPU-h, far under the ONE 4500 CPU-h cap, so it MUST be
    admitted. The repaired module has no such gate at all."""
    one = [record(manifest["VULTR"]["cells"][0], "VULTR", 11 * 3600.0)]
    assert not hasattr(M, "gate_per_host_reservation")
    acct = M.host_accounting("VULTR", one)                 # must NOT raise
    assert acct["cpu_h"] == pytest.approx(11.0)
    assert acct["projected_share_cpu_h"] == pytest.approx(10.217741105316279)
    assert acct["over_projected_share"] is True            # warning only
    assert acct["enforcement"] == "ACCOUNTING_ONLY"
    cap = M.gate_global_cap({"VULTR": 11.0, "AWS": 0.0})   # must NOT raise
    assert cap["charged_cpu_h"] == pytest.approx(249.6489, abs=1e-3)
    assert cap["charged_cpu_h"] <= M.GLOBAL_CPU_CAP


# ---- A. Vultr over its projected share, global under cap -> PASS ------------
def test_12A_vultr_over_projected_share_but_global_under_cap_passes(manifest, owners):
    """Vultr consumes 828 CPU-h against a 705.02 CPU-h projected share while AWS
    uses less than its own. Globally admissible, so it MUST pass."""
    led = _ledgers_with(manifest, aws_cpu_s=5.0 * 3600.0, vultr_cpu_s=12.0 * 3600.0)
    out = M.assemble_global_ledger(led, owners, PRODUCER, CKPT)
    acc = out["host_accounting"]
    assert acc["VULTR"]["over_projected_share"] is True
    assert acc["AWS"]["over_projected_share"] is False
    assert out["hosts_over_projected_share"] == ["VULTR"]
    assert out["cap"]["charged_cpu_h"] <= M.GLOBAL_CPU_CAP


# ---- B. AWS over its projected share, global under cap -> PASS --------------
def test_12B_aws_over_projected_share_but_global_under_cap_passes(manifest, owners):
    led = _ledgers_with(manifest, aws_cpu_s=13.0 * 3600.0, vultr_cpu_s=5.0 * 3600.0)
    out = M.assemble_global_ledger(led, owners, PRODUCER, CKPT)
    acc = out["host_accounting"]
    assert acc["AWS"]["over_projected_share"] is True
    assert acc["VULTR"]["over_projected_share"] is False
    assert out["hosts_over_projected_share"] == ["AWS"]
    assert out["cap"]["charged_cpu_h"] <= M.GLOBAL_CPU_CAP


# ---- C. BOTH hosts over their projected shares, aggregate under cap -> PASS --
def test_12C_both_hosts_over_projected_share_but_aggregate_under_cap_passes(manifest, owners):
    led = _ledgers_with(manifest, aws_cpu_s=11.8 * 3600.0, vultr_cpu_s=11.0 * 3600.0)
    out = M.assemble_global_ledger(led, owners, PRODUCER, CKPT)
    acc = out["host_accounting"]
    assert acc["AWS"]["over_projected_share"] and acc["VULTR"]["over_projected_share"]
    assert sorted(out["hosts_over_projected_share"]) == ["AWS", "VULTR"]
    assert out["cap"]["charged_cpu_h"] <= M.GLOBAL_CPU_CAP


# ---- D. aggregate comfortably below the cap -> PASS --------------------------
def test_12D_aggregate_below_cap_passes(manifest, owners):
    led = _ledgers_with(manifest, aws_cpu_s=11.0 * 3600.0, vultr_cpu_s=10.0 * 3600.0)
    out = M.assemble_global_ledger(led, owners, PRODUCER, CKPT)
    assert out["cap"]["charged_cpu_h"] < M.GLOBAL_CPU_CAP
    assert out["cap"]["headroom_cpu_h"] > 0


# ---- E. exactly at the frozen acceptance boundary: <= is admitted ------------
def _sr_hitting_cap_exactly():
    sr = M.GLOBAL_CPU_CAP / M.OVERHEAD_FACTOR
    for _ in range(256):
        charged = M.OVERHEAD_FACTOR * (sr + 0.0)
        if charged == M.GLOBAL_CPU_CAP:
            return sr
        sr = math.nextafter(sr, 0.0 if charged > M.GLOBAL_CPU_CAP else math.inf)
    raise AssertionError("no float lands exactly on the cap")


def test_12E_exactly_at_cap_follows_frozen_le_convention(manifest, owners):
    """The frozen convention is `charged > cap` refuses, so charged == cap is
    ADMITTED. That convention is preserved exactly."""
    sr = _sr_hitting_cap_exactly()
    assert M.OVERHEAD_FACTOR * sr == M.GLOBAL_CPU_CAP
    out = M.gate_global_cap({"AWS": sr}, governed_overhead_cpu_h=0.0)
    assert out["charged_cpu_h"] == M.GLOBAL_CPU_CAP
    assert out["headroom_cpu_h"] == 0.0
    assert out["enforcement"] == "GLOBAL_HARD_LIMIT"


# ---- F. aggregate above the cap -> FAIL CLOSED -------------------------------
def test_12F_above_cap_fails_closed(manifest, owners):
    sr = math.nextafter(_sr_hitting_cap_exactly(), math.inf)
    with pytest.raises(M.MultiHostRefusal):
        M.gate_global_cap({"AWS": sr}, governed_overhead_cpu_h=0.0)
    led = _ledgers_with(manifest, aws_cpu_s=15.0 * 3600.0, vultr_cpu_s=15.0 * 3600.0)
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(led, owners, PRODUCER, CKPT)


# ---- G. per-host accounting that does not reconcile -> FAIL CLOSED -----------
def test_12G_corrupted_host_accounting_fails_closed(manifest, owners, ledgers):
    accounts = {r: M.host_accounting(r, recs) for r, recs in ledgers.items()}
    assert M.reconcile_accounting(accounts, ledgers) > 0
    understated = copy.deepcopy(accounts)
    understated["VULTR"]["cpu_h"] = 0.0                  # hide real spend
    with pytest.raises(M.MultiHostRefusal):
        M.reconcile_accounting(understated, ledgers)
    miscounted = copy.deepcopy(accounts)
    miscounted["AWS"]["cells"] = 1
    with pytest.raises(M.MultiHostRefusal):
        M.reconcile_accounting(miscounted, ledgers)
    dropped = copy.deepcopy(accounts)
    del dropped["VULTR"]
    with pytest.raises(M.MultiHostRefusal):
        M.reconcile_accounting(dropped, ledgers)


# ---- H. duplicate / missing / non-physical cost entries -> FAIL CLOSED -------
def test_12H_duplicate_missing_and_nonphysical_costs_fail_closed(manifest, owners, ledgers):
    dup = copy.deepcopy(ledgers)
    dup["AWS"].append(record(manifest["AWS"]["cells"][0], "AWS", 1.0, obligations=0))
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(dup, owners, PRODUCER, CKPT)
    missing = copy.deepcopy(ledgers)
    missing["VULTR"].pop()
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(missing, owners, PRODUCER, CKPT)
    for bad_cost in (float("nan"), float("inf"), -1.0):
        bad = copy.deepcopy(ledgers)
        bad["AWS"][0]["cpu_seconds"] = bad_cost
        with pytest.raises(M.MultiHostRefusal):
            M.assemble_global_ledger(bad, owners, PRODUCER, CKPT)
    nanrole = {"AWS": float("nan"), "VULTR": 1.0}
    with pytest.raises(M.MultiHostRefusal):
        M.gate_global_cap(nanrole)


# ---- audit: the prohibited host hard limit is GONE, not softened -------------
def test_12I_host_hard_limit_is_removed_from_the_module():
    assert not hasattr(M, "gate_per_host_reservation"), \
        "the prohibited per-host hard limit must be removed, not retained"
    assert M.REMOVED_HOST_HARD_LIMITS == ("gate_per_host_reservation",)
    assert M.host_accounting("VULTR", [])["enforcement"] == "ACCOUNTING_ONLY"


def test_13_global_cap_violation():
    with pytest.raises(M.MultiHostRefusal):
        M.gate_global_cap({"AWS": 4000.0, "VULTR": 1000.0})


def test_13b_cap_is_not_per_host():
    """4500 is ONE global budget: two hosts at 2400 each must be refused."""
    with pytest.raises(M.MultiHostRefusal):
        M.gate_global_cap({"AWS": 2400.0, "VULTR": 2400.0})


def test_14_torn_cell_resume(owners, ledgers):
    bad = copy.deepcopy(ledgers)
    bad["AWS"][5]["complete"] = False
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(bad, owners, PRODUCER, CKPT)
    missing = copy.deepcopy(ledgers)
    del missing["AWS"][5]["scientific_content_hash"]
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(missing, owners, PRODUCER, CKPT)


def test_15_wrong_obligation_conservation(owners, ledgers):
    bad = copy.deepcopy(ledgers)
    bad["VULTR"][0]["obligations_completed"] = 27
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(bad, owners, PRODUCER, CKPT)


def test_16_corrupted_aggregate_ledger(owners, ledgers):
    out = M.assemble_global_ledger(ledgers, owners, PRODUCER, CKPT)
    with pytest.raises(M.MultiHostRefusal):
        M.verify_aggregate_ledger(out, "0" * 64)


def test_17_foreign_checkpoint_and_runtime_in_record(owners, ledgers):
    bad = copy.deepcopy(ledgers)
    bad["AWS"][0]["checkpoint_sha256"] = "c" * 64
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(bad, owners, PRODUCER, CKPT)
    bad2 = copy.deepcopy(ledgers)
    bad2["VULTR"][0]["runtime_contract_hash"] = M.ROLES["AWS"]["runtime_contract_hash"]
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(bad2, owners, PRODUCER, CKPT)


def test_09b_authorised_producer_commit_is_accepted():
    """Positive control: the binding must ADMIT the authorised checkout, so the
    refusal in test_09 is a real discrimination and not a blanket failure."""
    lm = json.loads((NS / "config/LAUNCH_MANIFEST.json").read_text())
    pc = lm["producer_commit"]
    assert M.gate_producer_commit(lm, pc, CKPT, SHARD_SHA) == pc


def test_09c_launch_manifest_must_stay_result_free():
    lm = json.loads((NS / "config/LAUNCH_MANIFEST.json").read_text())
    bad = dict(lm, result_bearing=True)
    with pytest.raises(M.MultiHostRefusal):
        M.gate_producer_commit(bad, bad["producer_commit"], CKPT, SHARD_SHA)
    bad2 = dict(lm, shard_manifest_sha256="0" * 64)
    with pytest.raises(M.MultiHostRefusal):
        M.gate_producer_commit(bad2, bad2["producer_commit"], CKPT, SHARD_SHA)



# ==========================================================================
# ACCOUNTING INTEGRITY (A-Q). Every case is result-free.
# ==========================================================================
INF = float("inf")
NAN = float("nan")


def _refusal(fn):
    with pytest.raises(M.MultiHostRefusal) as ei:
        fn()
    return str(ei.value)


# ---- governed_overhead_cpu_h domain: A-G ---------------------------------
def test_acc_A_nan_overhead_fails_closed():
    msg = _refusal(lambda: M.gate_global_cap({"AWS": 5000.0}, NAN))
    assert "governed_overhead_cpu_h" in msg and "not finite" in msg


def test_acc_B_pos_inf_overhead_fails_closed_as_invalid_not_incidentally():
    """+inf would also have tripped `charged > cap` by accident. It must be
    refused as an INVALID COMPONENT, before any arithmetic."""
    msg = _refusal(lambda: M.gate_global_cap({"AWS": 0.0}, INF))
    assert "governed_overhead_cpu_h" in msg and "not finite" in msg
    assert "global cap exceeded" not in msg


def test_acc_C_neg_inf_overhead_fails_closed():
    msg = _refusal(lambda: M.gate_global_cap({"AWS": 5000.0}, -INF))
    assert "governed_overhead_cpu_h" in msg and "not finite" in msg


def test_acc_D_negative_finite_overhead_fails_closed():
    msg = _refusal(lambda: M.gate_global_cap({"AWS": 5000.0}, -5000.0))
    assert "governed_overhead_cpu_h" in msg and "negative" in msg


def test_acc_E_negative_zero_overhead_is_admitted_and_cannot_reduce_the_total():
    """-0.0 satisfies `>= 0` under ordinary numeric semantics, so it is
    admitted. It is normalised to +0.0 and provably cannot reduce the
    aggregate: the charge equals the charge computed with +0.0."""
    neg = M.gate_global_cap({"AWS": 100.0}, -0.0)
    pos = M.gate_global_cap({"AWS": 100.0}, 0.0)
    assert neg["charged_cpu_h"] == pos["charged_cpu_h"]
    assert math.copysign(1.0, neg["governed_overhead_cpu_h"]) == 1.0   # +0.0, not -0.0
    assert neg["governed_overhead_cpu_h"] == 0.0
    assert M.validate_governed_cost(-0.0, "probe") == 0.0


def test_acc_F_zero_overhead_behaves_normally():
    out = M.gate_global_cap({"AWS": 100.0}, 0.0)
    assert out["charged_cpu_h"] == pytest.approx(1.15 * 100.0)


def test_acc_G_positive_finite_overhead_behaves_normally():
    out = M.gate_global_cap({"AWS": 100.0}, M.CUSUM_CPU_H)
    assert out["charged_cpu_h"] == pytest.approx(1.15 * (100.0 + 206.086))
    assert out["enforcement"] == "GLOBAL_HARD_LIMIT"


# ---- host / global components: H-K ---------------------------------------
@pytest.mark.parametrize("bad,tag", [(NAN, "not finite"), (INF, "not finite"),
                                     (-INF, "not finite"), (-100.0, "negative")])
def test_acc_HIJK_bad_host_components_fail_closed(bad, tag):
    msg = _refusal(lambda: M.gate_global_cap({"AWS": bad, "VULTR": 1.0}))
    assert "governed CPU-h for AWS" in msg and tag in msg


def test_acc_bool_and_nonnumeric_components_fail_closed():
    """bool is an int subclass: True would silently count as 1 CPU-h."""
    assert "bool" in _refusal(lambda: M.gate_global_cap({"AWS": True}))
    assert "bool" in _refusal(lambda: M.gate_global_cap({"AWS": 0.0}, True))
    assert "not numeric" in _refusal(lambda: M.gate_global_cap({"AWS": 0.0}, "206"))
    assert "not numeric" in _refusal(lambda: M.gate_global_cap({"AWS": None}))


def test_acc_aggregate_overflow_is_caught_even_when_components_are_valid():
    """Each addend is finite and non-negative, yet the SUM overflows to +inf,
    and (+inf) + (-inf) would be NaN. The aggregate is validated too."""
    msg = _refusal(lambda: M.gate_global_cap({"A": 1e308, "B": 1e308}, 0.0))
    assert "aggregate SR CPU-h" in msg and "not finite" in msg


def test_acc_subtractive_overhead_factor_is_refused():
    """A factor below 1 would silently reduce the governed total."""
    assert "subtractive" in _refusal(
        lambda: M.validate_governed_factor(0.5, "OVERHEAD_FACTOR"))
    assert "not finite" in _refusal(
        lambda: M.validate_governed_factor(NAN, "OVERHEAD_FACTOR"))
    assert M.validate_governed_factor(M.OVERHEAD_FACTOR, "OVERHEAD_FACTOR") == 1.15


# ---- cap boundary with a VALID aggregate: L-N -----------------------------
def test_acc_L_valid_aggregate_just_below_cap_passes():
    """One ulp below the boundary sr can still ROUND to exactly the cap, so step
    down until the product is genuinely below it, then assert admission."""
    sr = _sr_hitting_cap_exactly()
    for _ in range(64):
        sr = math.nextafter(sr, 0.0)
        if M.OVERHEAD_FACTOR * sr < M.GLOBAL_CPU_CAP:
            break
    else:
        raise AssertionError("no float below the cap found")
    out = M.gate_global_cap({"AWS": sr}, governed_overhead_cpu_h=0.0)
    assert out["charged_cpu_h"] < M.GLOBAL_CPU_CAP
    assert out["headroom_cpu_h"] > 0


def test_acc_M_valid_aggregate_exactly_at_cap_passes():
    sr = _sr_hitting_cap_exactly()
    out = M.gate_global_cap({"AWS": sr}, governed_overhead_cpu_h=0.0)
    assert out["charged_cpu_h"] == M.GLOBAL_CPU_CAP
    assert out["headroom_cpu_h"] == 0.0


def test_acc_N_valid_aggregate_just_above_cap_fails_closed():
    sr = math.nextafter(_sr_hitting_cap_exactly(), math.inf)
    assert "global cap exceeded" in _refusal(
        lambda: M.gate_global_cap({"AWS": sr}, governed_overhead_cpu_h=0.0))


# ---- over-cap SR combined with an invalid overhead: O-Q -------------------
def test_acc_O_over_cap_sr_with_negative_overhead_fails_on_the_overhead():
    msg = _refusal(lambda: M.gate_global_cap({"AWS": 9000.0}, -9000.0))
    assert "governed_overhead_cpu_h" in msg and "negative" in msg
    assert "global cap exceeded" not in msg


def test_acc_P_over_cap_sr_with_nan_overhead_fails_before_comparison():
    msg = _refusal(lambda: M.gate_global_cap({"AWS": 9000.0}, NAN))
    assert "governed_overhead_cpu_h" in msg and "not finite" in msg
    assert "global cap exceeded" not in msg


def test_acc_Q_over_cap_sr_with_neg_inf_overhead_fails_before_comparison():
    msg = _refusal(lambda: M.gate_global_cap({"AWS": 9000.0}, -INF))
    assert "governed_overhead_cpu_h" in msg and "not finite" in msg
    assert "global cap exceeded" not in msg


def test_acc_over_cap_sr_with_VALID_overhead_still_fails_on_the_cap():
    """Control: with a valid overhead the refusal must be the cap itself."""
    assert "global cap exceeded" in _refusal(
        lambda: M.gate_global_cap({"AWS": 9000.0}, 0.0))


# ---- the shared primitive is used by every accounting path ----------------
def test_acc_shared_primitive_governs_records_and_reconciliation(manifest, owners, ledgers):
    assert M.GOVERNED_COST_DOMAIN.startswith("finite real, >= 0")
    for bad in (NAN, INF, -INF, -1.0, True, "x", None):
        bad_led = copy.deepcopy(ledgers)
        bad_led["AWS"][0]["cpu_seconds"] = bad
        with pytest.raises(M.MultiHostRefusal):
            M.assemble_global_ledger(bad_led, owners, PRODUCER, CKPT)
    accounts = {r: M.host_accounting(r, recs) for r, recs in ledgers.items()}
    for bad in (NAN, INF, -INF, -1.0, True, "x", None):
        bad_acct = copy.deepcopy(accounts)
        bad_acct["VULTR"]["cpu_h"] = bad
        with pytest.raises(M.MultiHostRefusal):
            M.reconcile_accounting(bad_acct, ledgers)


def test_acc_full_ledger_still_admits_a_valid_campaign(manifest, owners, ledgers):
    """Regression: the hardening must not refuse a legitimate campaign."""
    out = M.assemble_global_ledger(ledgers, owners, PRODUCER, CKPT)
    assert out["cells_completed"] == 316
    assert out["obligations_completed"] == 8849
    assert out["cap"]["charged_cpu_h"] <= M.GLOBAL_CPU_CAP



# ==========================================================================
# TRUSTED NUMERIC DOMAIN. All result-free.
# ==========================================================================
from decimal import Decimal          # noqa: E402
from fractions import Fraction       # noqa: E402


class EvilInt(int):
    """int subclass that validates as its true magnitude but whose overloaded
    arithmetic tries to contribute zero to any sum."""
    def __add__(self, other): return 0
    def __radd__(self, other): return 0
    def __mul__(self, other): return 0
    def __rmul__(self, other): return 0


class FloatLike:
    """Implements __float__ but is neither int nor float."""
    def __float__(self): return 5000.0
    def __add__(self, other): return 0
    def __radd__(self, other): return 0


class Unrepresentable:
    def __float__(self): raise OverflowError("too large to represent")


# ---- A1: GLOBAL_CPU_CAP is itself a governed operand: D1-D10 -------------
@pytest.mark.parametrize("bad", [NAN, INF, -INF, -1.0, 0.0, True, False,
                                 "4500", None, 10 ** 400])
def test_td_D1_10_bad_global_cap_fails_closed(monkeypatch, bad):
    monkeypatch.setattr(M, "GLOBAL_CPU_CAP", bad)
    with pytest.raises(M.MultiHostRefusal):
        M.gate_global_cap({"AWS": 1.0}, 0.0)


def test_td_D10_valid_cap_behaves_normally():
    out = M.gate_global_cap({"AWS": 100.0}, 0.0)
    assert out["cap"] == 4500.0 and type(out["cap"]) is float
    assert out["headroom_cpu_h"] == 4500.0 - out["charged_cpu_h"]


def test_td_mutated_cap_cannot_admit_an_over_cap_campaign(monkeypatch):
    """The adjudicated mutation: a NaN or +inf cap previously admitted 5750."""
    for bad in (NAN, INF):
        monkeypatch.setattr(M, "GLOBAL_CPU_CAP", bad)
        with pytest.raises(M.MultiHostRefusal) as ei:
            M.gate_global_cap({"AWS": 5000.0}, 0.0)      # 5750 CPU-h charged
        assert "cap GLOBAL_CPU_CAP" in str(ei.value)


def test_td_cap_is_bound_to_the_protocol_value(monkeypatch):
    assert M.PROTOCOL_BOUND_CPU_CAP == 4500.0
    monkeypatch.setattr(M, "GLOBAL_CPU_CAP", 9000.0)     # finite, positive, but not bound
    assert "protocol binds" in _refusal(lambda: M.gate_global_cap({"AWS": 1.0}, 0.0))


# ---- A2: only validated RETURNS enter arithmetic: D11-D13 ---------------
def test_td_D11_malicious_int_subclass_contributes_its_true_magnitude():
    """Under the defect this validated as 5000 but summed as 0 and was ADMITTED.
    It must now charge 5000 CPU-h and trip the cap."""
    assert float(EvilInt(5000)) == 5000.0
    assert EvilInt(5000) + 0 == 0                       # the overload really is hostile
    msg = _refusal(lambda: M.gate_global_cap({"AWS": EvilInt(5000)}, 0.0))
    assert "global cap exceeded" in msg and "5750" in msg


def test_td_D11b_malicious_int_subclass_normalised_when_under_cap():
    out = M.gate_global_cap({"AWS": EvilInt(100)}, 0.0)
    assert out["charged_cpu_h"] == pytest.approx(115.0)
    assert out["validated_cpu_h_by_role"]["AWS"] == 100.0


def test_td_D12_float_like_object_is_refused_by_the_chosen_domain():
    """Policy: the trusted domain accepts only int/float instances. A
    __float__-only wrapper is refused rather than accepted-and-normalised."""
    assert "not numeric" in _refusal(lambda: M.gate_global_cap({"AWS": FloatLike()}, 0.0))
    assert "not numeric" in _refusal(lambda: M.validate_governed_cost(Decimal("5"), "d"))
    assert "not numeric" in _refusal(lambda: M.validate_governed_cost(Fraction(5, 1), "f"))


def test_td_D13_no_original_object_survives_into_the_summed_collection():
    evil = EvilInt(100)
    out = M.gate_global_cap({"AWS": evil, "VULTR": 1.0}, 0.0)
    vals = out["validated_cpu_h_by_role"]
    assert all(type(v) is float for v in vals.values()), vals
    assert not any(isinstance(v, EvilInt) for v in vals.values())
    assert vals["AWS"] is not evil
    assert type(out["overhead_factor"]) is float
    assert type(out["charged_cpu_h"]) is float
    assert type(out["sr_cpu_h"]) is float


def test_td_numpy_float_subclass_is_normalised_to_a_primitive():
    np = pytest.importorskip("numpy")
    out = M.gate_global_cap({"AWS": np.float64(100.0)}, 0.0)
    assert type(out["validated_cpu_h_by_role"]["AWS"]) is float
    assert out["charged_cpu_h"] == pytest.approx(115.0)
    with pytest.raises(M.MultiHostRefusal):
        M.gate_global_cap({"AWS": np.float64("nan")}, 0.0)


# ---- A3: coercion exceptions normalise to MultiHostRefusal: D14-D18 -----
def test_td_D14_huge_int_fails_closed_not_overflowerror():
    msg = _refusal(lambda: M.validate_governed_cost(10 ** 400, "huge"))
    assert "not representable" in msg and "OverflowError" in msg


@pytest.mark.parametrize("bad", [object(), Unrepresentable(), "12", None, [1], {"a": 1}])
def test_td_D15_18_malformed_inputs_fail_closed_as_MultiHostRefusal(bad):
    with pytest.raises(M.MultiHostRefusal):
        M.validate_governed_cost(bad, "malformed")
    with pytest.raises(M.MultiHostRefusal):
        M.gate_global_cap({"AWS": bad}, 0.0)
    with pytest.raises(M.MultiHostRefusal):
        M.gate_global_cap({"AWS": 1.0}, bad)


def test_td_no_raw_numeric_exception_escapes_any_admission_gate(manifest, owners, ledgers):
    """No TypeError / ValueError / OverflowError may cross an admission gate."""
    for bad in (10 ** 400, object(), "x", None, NAN, INF, -INF, -1.0, True):
        for call in (lambda b=bad: M.gate_global_cap({"AWS": b}, 0.0),
                     lambda b=bad: M.gate_global_cap({"AWS": 1.0}, b),
                     lambda b=bad: M.validate_governed_cost(b, "probe"),
                     lambda b=bad: M.validate_governed_factor(b, "probe"),
                     lambda b=bad: M.validate_governed_cap(b, "probe", expect=None)):
            with pytest.raises(M.MultiHostRefusal):
                call()
    bad_led = copy.deepcopy(ledgers)
    bad_led["AWS"][0]["cpu_seconds"] = 10 ** 400
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(bad_led, owners, PRODUCER, CKPT)


# ---- boundary with a validated cap: D19-D21 ------------------------------
def test_td_D19_below_cap_passes():
    sr = _sr_hitting_cap_exactly()
    for _ in range(64):
        sr = math.nextafter(sr, 0.0)
        if M.OVERHEAD_FACTOR * sr < M.GLOBAL_CPU_CAP:
            break
    out = M.gate_global_cap({"AWS": sr}, 0.0)
    assert out["charged_cpu_h"] < 4500.0 and out["headroom_cpu_h"] > 0


def test_td_D20_exactly_at_cap_passes():
    out = M.gate_global_cap({"AWS": _sr_hitting_cap_exactly()}, 0.0)
    assert out["charged_cpu_h"] == 4500.0 and out["headroom_cpu_h"] == 0.0


def test_td_D21_above_cap_fails_closed():
    sr = math.nextafter(_sr_hitting_cap_exactly(), math.inf)
    assert "global cap exceeded" in _refusal(lambda: M.gate_global_cap({"AWS": sr}, 0.0))


# ---- runtime-identity gate: the thread contract precedes the hash ---------
def test_td_thread_contract_gate_precedes_the_runtime_hash():
    """The reported Vultr 'drift' e8a9f671... was the frozen runtime measured
    WITHOUT the thread contract. This gate turns that into a precise refusal."""
    full = {v: "1" for v in M.THREAD_CONTRACT_VARS}
    assert M.gate_thread_contract(full)["thread_contract"] == "applied"
    missing = dict(full); del missing["OMP_NUM_THREADS"]
    msg = _refusal(lambda: M.gate_thread_contract(missing))
    assert "thread contract not applied" in msg and "OMP_NUM_THREADS" in msg
    wrong = dict(full); wrong["OPENBLAS_NUM_THREADS"] = "8"
    assert "OPENBLAS_NUM_THREADS" in _refusal(lambda: M.gate_thread_contract(wrong))
    assert _refusal(lambda: M.gate_thread_contract({})) .count("NUM_THREADS") >= 4
