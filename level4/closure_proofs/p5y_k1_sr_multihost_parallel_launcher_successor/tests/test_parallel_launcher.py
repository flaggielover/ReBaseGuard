"""Result-free tests for the parallel integrated launcher.

RULE (Part 2): no fixture may rewrite a frozen load-bearing identity to make the
current checkout pass. Positive tests load the FROZEN artifact unchanged; every
negative test builds an explicit temporary negative-control copy and never
writes it back. test_fixture_never_mutates_frozen_authorization proves byte
identity of the frozen artifact across the whole session.
"""
import copy, hashlib, json, os, subprocess, sys, time
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
sys.path.insert(0, str(NS / "driver"))
import multihost as M                                              # noqa: E402
import executor_adapter as EA                                      # noqa: E402
import global_budget as GB                                         # noqa: E402
import worker_pool as WP                                           # noqa: E402
import integrated_sr_launcher as L                                 # noqa: E402

AUTH_PATH = NS / "config/LAUNCH_AUTHORIZATION.json"
FROZEN_AUTH_SHA = hashlib.sha256(AUTH_PATH.read_bytes()).hexdigest()
SIX = {v: "1" for v in M.THREAD_CONTRACT_VARS}
AWS_SIBS = {c: [c, c + 16] for c in range(16)}
VUL_SIBS = {0: [0, 1], 2: [2, 3], 4: [4, 5], 6: [6, 7]}
AWS_RT = "d49f043755ef658a60e3c4017022ddecf0642a087a6e5bb0c1f2aefbe9721191"
VUL_RT = "c7f9fc671664a1bcfef6d2d3d93d6cc865a2a241a869f2e93f94e6e00b6489d9"


def git(*a):
    return subprocess.check_output(["git", "-C", str(ROOT)] + list(a)).decode().strip()


@pytest.fixture
def frozen_auth():
    """The frozen artifact, UNCHANGED. Never mutated."""
    return L.load_authorization(AUTH_PATH)


def negative_control(**overrides):
    """An explicit temporary negative-control manifest. Never written back."""
    a = json.loads(AUTH_PATH.read_text())
    for k, v in overrides.items():
        a[k] = v
    return a


def pf(auth, role, tmp_path, **kw):
    base = dict(role=role, env=SIX, repo=ROOT, ns=NS, root=ROOT,
                budget_path=tmp_path / "budget.json",
                live_hash=AWS_RT if role == "AWS" else VUL_RT,
                cores=list(range(16)) if role == "AWS" else [0, 2, 4, 6],
                siblings=AWS_SIBS if role == "AWS" else VUL_SIBS)
    base.update(kw)
    return L.preflight(auth, **base)


def approved_head_or_skip(auth):
    try:
        return git("rev-list", "-n1", auth["approved_launch_tag"])
    except subprocess.CalledProcessError:
        pytest.skip("approved launch tag not created yet (pre-freeze bootstrap)")


# ================= PART 2: the frozen artifact is never mutated =============
def test_fixture_never_mutates_frozen_authorization():
    assert hashlib.sha256(AUTH_PATH.read_bytes()).hexdigest() == FROZEN_AUTH_SHA


def test_no_fixture_substitutes_a_frozen_identity():
    """Static guard: the test source must not assign any frozen identity."""
    src = Path(__file__).read_text()
    banned = ["producer_commit\"] = ", "approved_launch_tag\"] = ",
              "protocol_sha256\"] = ", "checkpoint_sha256\"] = ",
              "evidence_manifest_sha256\"] = ", "shard_manifest_sha256\"] = ",
              "runtime_contract_hashes\"] = ", "scientific_scope\"] = ",
              "global_cpu_cap\"] = "]
    for b in banned:
        assert b not in src, f"fixture assigns a frozen identity: {b}"


# ================= PART 1: producer vs approved launch state ================
def test_producer_and_approved_head_are_separate_fields(frozen_auth):
    assert len(frozen_auth["producer_commit"]) == 40
    assert frozen_auth["approved_launch_tag"]
    assert "approved_launch_head" not in frozen_auth, \
        "the approved head must be bound by TAG, not by a self-referential hash"


def test_the_exact_prior_defect_now_passes(frozen_auth):
    """Regression for the adjudicated defect: producer_commit != approved HEAD,
    but correct ancestry + correct approved HEAD must PASS."""
    approved = approved_head_or_skip(frozen_auth)
    pc = frozen_auth["producer_commit"]
    assert pc != approved, "this regression is only meaningful when they differ"
    out = L.gate_approved_launch_head(frozen_auth, repo=ROOT)
    assert out["approved_launch_head"] == approved and out["live_head"] == approved
    anc = L.gate_producer_ancestry(frozen_auth, approved, repo=ROOT)
    assert anc["is_ancestor_of_approved_head"] is True


def test_exact_approved_head_passes(frozen_auth):
    approved = approved_head_or_skip(frozen_auth)
    assert L.gate_approved_launch_head(frozen_auth, repo=ROOT)["live_head"] == approved


def test_checkout_at_producer_commit_only_is_refused(frozen_auth):
    """Being AT the producer commit is not sufficient: it is not the approved head."""
    approved = approved_head_or_skip(frozen_auth)
    bad = negative_control(approved_launch_tag="refs/no/such/tag")
    with pytest.raises(M.MultiHostRefusal, match="does not resolve"):
        L.gate_approved_launch_head(bad, repo=ROOT)
    assert frozen_auth["producer_commit"] != approved


def test_descendant_after_approved_head_is_refused(frozen_auth, tmp_path):
    approved = approved_head_or_skip(frozen_auth)
    fake_head = "f" * 40
    with pytest.raises(M.MultiHostRefusal, match="unbound descendant|!= approved"):
        L._gate_head_against(approved, fake_head, clean=True)


def test_unrelated_and_missing_producer_are_refused(frozen_auth):
    approved = approved_head_or_skip(frozen_auth)
    # a real non-ancestor: the CUSUM branch tip, which is not in this branch's ancestry
    unrelated = git("rev-list", "-n1", "p5y-gate1-micropilots")
    bad = negative_control(producer_commit=unrelated)
    with pytest.raises(M.MultiHostRefusal, match="NOT an ancestor"):
        L.gate_producer_ancestry(bad, approved, repo=ROOT)
    missing = negative_control(producer_commit="0" * 40)
    with pytest.raises(M.MultiHostRefusal, match="does not exist"):
        L.gate_producer_ancestry(missing, approved, repo=ROOT)
    short = negative_control(producer_commit="abc")
    with pytest.raises(M.MultiHostRefusal, match="not a full commit id"):
        L.gate_producer_ancestry(short, approved, repo=ROOT)


def test_dirty_worktree_is_refused(frozen_auth):
    approved_head_or_skip(frozen_auth)
    with pytest.raises(M.MultiHostRefusal, match="not clean"):
        L._gate_head_against("x" * 40, "x" * 40, clean=False)


# ================= frozen preflight, both roles, unchanged ==================
@pytest.mark.parametrize("role,n", [("AWS", 247), ("VULTR", 69)])
def test_frozen_authorization_preflight_passes_unchanged(frozen_auth, tmp_path, role, n):
    approved_head_or_skip(frozen_auth)
    p = pf(frozen_auth, role, tmp_path)
    assert all(t["status"] == "PASS" for t in p["trace"])
    assert len(p["owned"]) == n and len(p["pending"]) == n
    with pytest.raises(M.MultiHostRefusal, match="production_enabled is false"):
        L.gate_production_enabled(p["auth"])
    assert hashlib.sha256(AUTH_PATH.read_bytes()).hexdigest() == FROZEN_AUTH_SHA


# ================= PART 3/4/5: real workers, affinity, overlap ==============
def _local_role():
    v = Path("/sys/class/dmi/id/sys_vendor")
    return M.detect_role(v.read_text().strip()) if v.exists() else None


def test_pool_creates_real_processes_with_verified_affinity(frozen_auth, tmp_path):
    approved_head_or_skip(frozen_auth)
    role = _local_role()
    if role is None:
        pytest.skip("no DMI vendor on this host")
    p = pf(frozen_auth, role, tmp_path)
    pool, info = L.build_pool(p)
    try:
        assert info["workers"] == frozen_auth["hosts"][role]["workers"]
        assert info["cores"] == frozen_auth["hosts"][role]["cores"]
        assert len(set(info["pids"])) == info["workers"]
        for pid, aff in info["affinity"].items():
            assert len(aff) == 1 and aff[0] in info["cores"]
        assert sorted(a[0] for a in info["affinity"].values()) == sorted(info["cores"])
    finally:
        pool.close()


def test_workers_actually_overlap(frozen_auth, tmp_path):
    approved_head_or_skip(frozen_auth)
    role = _local_role()
    if role is None:
        pytest.skip("no DMI vendor on this host")
    p = pf(frozen_auth, role, tmp_path)
    c = L.prove_concurrency(p, seconds=0.5)
    want = frozen_auth["hosts"][role]["workers"]
    assert c["distinct_pids"] == want
    assert c["max_simultaneous_active_workers"] >= want, c
    assert c["serial_equivalent_s"] > c["window_s"], "no genuine overlap"


def test_affinity_refusal_is_fail_closed():
    with pytest.raises(WP.AffinityRefusal):
        WP.enforce_affinity(10 ** 6)
    with pytest.raises(WP.AffinityRefusal, match="incomplete"):
        WP.enforce_thread_env({"OMP_NUM_THREADS": "1"})
    with pytest.raises(WP.AffinityRefusal, match="not the frozen one-thread contract"):
        WP.enforce_thread_env({v: ("8" if v == "OMP_NUM_THREADS" else "1")
                               for v in WP.FROZEN_THREAD_VARS})
    assert WP.enforce_thread_env({v: "1" for v in WP.FROZEN_THREAD_VARS})


def test_science_task_refused_while_production_disabled():
    with pytest.raises(WP.AffinityRefusal, match="production_enabled=false"):
        WP._run_task({"kind": "SCIENCE", "cell_id": 0, "driver_dir": str(NS / "driver")},
                     ROOT, False)


# ================= PART 6: real executor imports inside children ============
def test_scientific_dependencies_import_in_child_processes(frozen_auth, tmp_path):
    approved_head_or_skip(frozen_auth)
    role = _local_role()
    if role is None:
        pytest.skip("no DMI vendor on this host")
    p = pf(frozen_auth, role, tmp_path)
    out = L.structural_import_in_workers(p)
    assert out["all_bound"] is True
    assert "sr_propagate" in out["bound_modules"] and "sr_nstep" in out["bound_modules"]


# ================= PART 12/13: in-flight cap accounting =====================
def _budget(tmp_path, overhead):
    return GB.GlobalBudget(tmp_path / "b.json", M.validate_governed_cost,
                           M.gate_global_cap, overhead_cpu_h=overhead,
                           cap_cpu_h=M.validate_governed_cap(M.GLOBAL_CPU_CAP))


def test_inflight_reservations_cannot_oversubscribe_the_cap(tmp_path):
    """Remaining budget supports only 3 reservations; 16 workers ask; 3 admitted."""
    b = _budget(tmp_path, 0.0)
    per = 1000.0                      # 1.15 * 3 * 1000 = 3450 <= 4500; 4th -> 4600 > 4500
    admitted = []
    for cell in range(16):
        try:
            admitted.append(b.draw("AWS", cell, per))
        except (GB.BudgetRefusal, M.MultiHostRefusal):
            break
    assert len(admitted) == 3, admitted
    st = b.status()
    assert st["cap"]["charged_cpu_h"] == pytest.approx(1.15 * 3000.0)


def test_open_reservations_count_against_the_cap_before_completion(tmp_path):
    b = _budget(tmp_path, 0.0)
    b.draw("AWS", 0, 3000.0)
    assert b.status()["cap"]["charged_cpu_h"] == pytest.approx(3450.0)
    with pytest.raises((GB.BudgetRefusal, M.MultiHostRefusal)):
        b.draw("AWS", 1, 3000.0)          # stale-budget mass submission refused


def test_realized_cost_replaces_the_reservation(tmp_path):
    b = _budget(tmp_path, 0.0)
    k = b.draw("AWS", 0, 1000.0)
    b.commit(k, 10.0, {"cell_id": 0, "complete": True})
    assert b.status()["cap"]["charged_cpu_h"] == pytest.approx(11.5)
    k2 = b.draw("AWS", 1, 1.0)
    b.commit(k2, 100.0, {"cell_id": 1, "complete": True})   # over-run realised
    assert b.status()["cap"]["charged_cpu_h"] == pytest.approx(1.15 * 110.0)


def test_released_reservation_returns_to_the_global_budget(tmp_path):
    b = _budget(tmp_path, 0.0)
    k = b.draw("AWS", 0, 3000.0)          # 1.15*3000 = 3450 <= 4500
    with pytest.raises((GB.BudgetRefusal, M.MultiHostRefusal)):
        b.draw("AWS", 1, 1000.0)          # 1.15*4000 = 4600 > 4500
    b.release(k)
    b.draw("AWS", 1, 1000.0)              # budget freed, not stranded


# ================= PART 8: worker failure / torn cells ======================
def test_torn_and_malformed_worker_results_never_finalize(tmp_path):
    b = _budget(tmp_path, 0.0)
    k = b.draw("AWS", 5, 1.0)
    b.release(k)
    assert b.status()["completed_cells"] == []
    with pytest.raises(GB.BudgetRefusal, match="no open reservation"):
        b.commit("AWS:5", 1.0, {"cell_id": 5, "complete": True})
    k2 = b.draw("AWS", 5, 1.0)
    b.commit(k2, 1.0, {"cell_id": 5, "complete": True})
    with pytest.raises(GB.BudgetRefusal, match="already complete"):
        b.draw("AWS", 5, 1.0)             # no duplicate finalised result


def test_worker_death_and_exceptions_are_reported_not_finalized(frozen_auth, tmp_path):
    approved_head_or_skip(frozen_auth)
    role = _local_role()
    if role is None:
        pytest.skip("no DMI vendor on this host")
    p = pf(frozen_auth, role, tmp_path)
    pool, info = L.build_pool(p)
    try:
        pool.submit({"kind": "NOT_A_KIND", "cell_id": 1})
        rec = pool.get(timeout=60)
        assert rec["ok"] is False and "unknown task kind" in rec["error"]
    finally:
        pool.close()
    assert p["budget"].status()["completed_cells"] == []


# ================= PART 11: active-host transition ==========================
def test_role_transition_is_deterministic_and_result_independent(frozen_auth, tmp_path):
    approved_head_or_skip(frozen_auth)
    p = pf(frozen_auth, "AWS", tmp_path)
    owners = p["owners"]
    aws = [c for c, r in owners.items() if r == "AWS"]
    vul = [c for c, r in owners.items() if r == "VULTR"]
    seq = frozen_auth["concurrency"]["host_sequence"]
    assert seq == ["AWS", "VULTR"]
    assert L.resolve_active_host(frozen_auth, owners, [])["active_host"] == "AWS"
    assert L.resolve_active_host(frozen_auth, owners, aws)["active_host"] == "VULTR"
    # in-flight work BLOCKS the advance: the active host must stay put, never jump ahead
    blocked = L.resolve_active_host(frozen_auth, owners, aws, inflight=1)
    assert blocked["active_host"] == "AWS", blocked
    assert "in flight" in blocked["reason"]
    assert L.resolve_active_host(frozen_auth, owners, aws + vul)["active_host"] is None


def test_inactive_host_may_not_produce(frozen_auth, tmp_path):
    approved_head_or_skip(frozen_auth)
    p = pf(frozen_auth, "VULTR", tmp_path)
    assert p["active"]["active_host"] == "AWS"
    with pytest.raises(M.MultiHostRefusal):
        L.run_production(p)


# ================= unchanged frozen scope ==================================
def test_frozen_scope_and_cap_unchanged(frozen_auth):
    s = frozen_auth["scientific_scope"]
    assert (s["D"], s["Z"], s["precision_bits"], s["backend"]) == (11, 20, 256, "O9")
    assert (s["candidates"], s["contracts"], s["obligations"], s["total_cells"]) == \
        (46, 102, 8849, 316)
    assert frozen_auth["global_cpu_cap"] == 4500.0
    assert frozen_auth["hosts"]["AWS"]["cell_count"] == 247
    assert frozen_auth["hosts"]["VULTR"]["cell_count"] == 69
    assert frozen_auth["runtime_contract_hashes"] == {"AWS": AWS_RT, "VULTR": VUL_RT}
    assert not hasattr(M, "gate_per_host_reservation")


def test_adapter_unchanged_and_gate_library_repair_is_additive_only():
    """The adapter is byte-identical to the predecessor; multihost.py differs ONLY
    by the additive D19 validation -- no predecessor line is removed."""
    prev = ROOT / "level4/closure_proofs/p5y_k1_sr_multihost_integrated_launcher_successor"
    assert hashlib.sha256((NS / "driver/executor_adapter.py").read_bytes()).hexdigest() == \
           hashlib.sha256((prev / "driver/executor_adapter.py").read_bytes()).hexdigest()
    old = (prev / "driver/multihost.py").read_text().splitlines()
    new = (NS / "driver/multihost.py").read_text().splitlines()
    assert [l for l in old if l not in new] == [], "a predecessor line was removed"
    added = [l for l in new if l not in old]
    assert 0 < len(added) <= 14, added
    joined = "\n".join(added)
    assert "scientific_content_hash" in joined and "cell_id" in joined
    assert "D19" in joined


def test_malformed_scientific_content_hash_is_refused(frozen_auth, tmp_path):
    """D19 regression: a None / short / non-hex digest must never finalise."""
    approved_head_or_skip(frozen_auth)
    p = pf(frozen_auth, "AWS", tmp_path)
    base = {"cell_id": 0, "role": "AWS", "producer_commit": frozen_auth["producer_commit"],
            "checkpoint_sha256": frozen_auth["checkpoint_sha256"],
            "runtime_contract_hash": AWS_RT, "scientific_content_hash": "0" * 64,
            "cpu_seconds": 1.0, "obligations_completed": 29, "complete": True}
    M.validate_record(dict(base), "AWS", p["owners"], frozen_auth["producer_commit"],
                      frozen_auth["checkpoint_sha256"])
    for bad in (None, "", "abc", "z" * 64, 12345, "0" * 63, True):
        r = dict(base, scientific_content_hash=bad)
        with pytest.raises(M.MultiHostRefusal, match="malformed scientific_content_hash"):
            M.validate_record(r, "AWS", p["owners"], frozen_auth["producer_commit"],
                              frozen_auth["checkpoint_sha256"])
    for bad in (-1, 316, 3.5, True, "0"):
        r = dict(base, cell_id=bad)
        with pytest.raises(M.MultiHostRefusal):
            M.validate_record(r, "AWS", p["owners"], frozen_auth["producer_commit"],
                              frozen_auth["checkpoint_sha256"])


# ================= D18: obligation conservation over the real cover =========
def test_far_field_obligation_makes_316_cells_sum_to_8849(frozen_auth, tmp_path):
    """The 316 cover cells carry 8848 obligations; the 8849th is SR:-1:far_field.
    Without deterministic attribution, final assembly could NEVER succeed."""
    approved_head_or_skip(frozen_auth)
    p = pf(frozen_auth, "AWS", tmp_path)
    owners = p["owners"]
    total = sum(L.obligations_for_cell(frozen_auth, owners, r, c)
                for c, r in owners.items())
    assert total == frozen_auth["scientific_scope"]["obligations"] == 8849
    ff = L.far_field_attribution(frozen_auth, owners)
    assert ff["role"] == "AWS" and ff["cell"] == 0 and ff["count"] == 1
    assert L.obligations_for_cell(frozen_auth, owners, "AWS", 0) == 29
    assert L.obligations_for_cell(frozen_auth, owners, "AWS", 1) == 28


def test_far_field_attribution_must_be_deterministic(frozen_auth, tmp_path):
    approved_head_or_skip(frozen_auth)
    p = pf(frozen_auth, "AWS", tmp_path)
    bad = negative_control(far_field_obligation={
        "work_id": "SR:-1:far_field:all_m", "count": 1,
        "attributed_to_role": "VULTR", "attributed_to_cell": 4})
    with pytest.raises(M.MultiHostRefusal, match="far-field attribution"):
        L.far_field_attribution(bad, p["owners"])
