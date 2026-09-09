"""Result-free integration tests for THE authoritative production entry point.

No genuine production cell is ever executed: the one test that crosses the
result-bearing transition injects a stubbed scientific callable.
"""
import copy, hashlib, json, subprocess, sys
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
sys.path.insert(0, str(NS / "driver"))
import multihost as M                                              # noqa: E402
import executor_adapter as EA                                      # noqa: E402
import global_budget as GB                                         # noqa: E402
import integrated_sr_launcher as L                                 # noqa: E402

HEAD = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"]).decode().strip()
AWS_RT = "d49f043755ef658a60e3c4017022ddecf0642a087a6e5bb0c1f2aefbe9721191"
VUL_RT = "c7f9fc671664a1bcfef6d2d3d93d6cc865a2a241a869f2e93f94e6e00b6489d9"
SIX = {v: "1" for v in M.THREAD_CONTRACT_VARS}
AWS_SIBS = {c: [c, c + 16] for c in range(16)}
VUL_SIBS = {0: [0, 1], 2: [2, 3], 4: [4, 5], 6: [6, 7]}
AWS_CORES = list(range(16))
VUL_CORES = [0, 2, 4, 6]


@pytest.fixture
def auth():
    a = json.loads((NS / "config/LAUNCH_AUTHORIZATION.json").read_text())
    a["producer_commit"] = HEAD
    return a


def pf(auth, role, tmp_path, **kw):
    base = dict(role=role, env=SIX, repo=ROOT, ns=NS, root=ROOT,
                budget_path=tmp_path / "budget.json",
                live_hash=AWS_RT if role == "AWS" else VUL_RT,
                cores=AWS_CORES if role == "AWS" else VUL_CORES,
                siblings=AWS_SIBS if role == "AWS" else VUL_SIBS)
    base.update(kw)
    return L.preflight(auth, **base)


def stub_science(mods, cell_index):
    """Stands in for sr_propagate.cell_certificate. No genuine cell is computed."""
    return {"stub": True, "cell": cell_index}


# ---- 1-2: both roles reach the final pre-result gate ---------------------
@pytest.mark.parametrize("role,n", [("AWS", 247), ("VULTR", 69)])
def test_01_02_role_reaches_final_disabled_gate(auth, tmp_path, role, n):
    p = pf(auth, role, tmp_path)
    assert [t["gate"] for t in p["trace"]][-1] == "pending_cell_plan"
    assert all(t["status"] == "PASS" for t in p["trace"])
    assert len(p["owned"]) == n and len(p["pending"]) == n
    with pytest.raises(M.MultiHostRefusal, match="production_enabled is false"):
        L.gate_production_enabled(p["auth"])


# ---- 3-7: bound identity hashes ------------------------------------------
def test_03_wrong_producer_refuses(auth, tmp_path):
    bad = dict(auth, producer_commit="b" * 40)
    with pytest.raises(M.MultiHostRefusal):
        pf(bad, "AWS", tmp_path)


@pytest.mark.parametrize("field", ["protocol_sha256", "checkpoint_sha256",
                                   "evidence_manifest_sha256", "shard_manifest_sha256"])
def test_04_07_wrong_bound_hash_refuses(auth, tmp_path, field):
    bad = dict(auth); bad[field] = "0" * 64
    with pytest.raises(M.MultiHostRefusal):
        pf(bad, "AWS", tmp_path)


# ---- 8-10: runtime identity and thread contract --------------------------
def test_08_09_wrong_runtime_refuses(auth, tmp_path):
    with pytest.raises(M.MultiHostRefusal):
        pf(auth, "AWS", tmp_path, live_hash=VUL_RT)
    with pytest.raises(M.MultiHostRefusal):
        pf(auth, "VULTR", tmp_path, live_hash=AWS_RT)


def test_10_missing_thread_contract_refuses(auth, tmp_path):
    partial = dict(SIX); del partial["OMP_NUM_THREADS"]
    with pytest.raises(M.MultiHostRefusal, match="thread contract"):
        pf(auth, "AWS", tmp_path, env=partial)


# ---- 11-12: topology -----------------------------------------------------
def test_11_wrong_worker_count_refuses(auth, tmp_path):
    bad = copy.deepcopy(auth); bad["hosts"]["VULTR"]["workers"] = 8
    with pytest.raises(M.MultiHostRefusal):
        pf(bad, "VULTR", tmp_path, cores=[0, 2, 4, 6])


def test_12_wrong_core_topology_refuses(auth, tmp_path):
    with pytest.raises(M.MultiHostRefusal):
        pf(auth, "VULTR", tmp_path, cores=[0, 1, 2, 3],
           siblings={0: [0, 1], 1: [0, 1], 2: [2, 3], 3: [2, 3]})


# ---- 13-15: shard ownership ----------------------------------------------
def test_13_14_foreign_host_cell_refuses(auth, tmp_path):
    a = pf(auth, "AWS", tmp_path)
    v_cell = next(c for c, r in a["owners"].items() if r == "VULTR")
    with pytest.raises(M.MultiHostRefusal, match="foreign-host"):
        M.gate_cell_ownership("AWS", v_cell, a["owners"])
    a_cell = next(c for c, r in a["owners"].items() if r == "AWS")
    with pytest.raises(M.MultiHostRefusal, match="foreign-host"):
        M.gate_cell_ownership("VULTR", a_cell, a["owners"])


def test_15_duplicate_cell_refuses(auth, tmp_path):
    p = pf(auth, "AWS", tmp_path)
    cell = p["pending"][0]
    key = p["budget"].draw("AWS", cell, 1.0)
    with pytest.raises(GB.BudgetRefusal, match="already has an open reservation"):
        p["budget"].draw("AWS", cell, 1.0)
    p["budget"].commit(key, 0.5, {"cell_id": cell, "complete": True})
    with pytest.raises(GB.BudgetRefusal, match="already complete"):
        p["budget"].draw("AWS", cell, 1.0)


# ---- 16-18: accounting ---------------------------------------------------
def test_16_malformed_ledger_refuses(auth, tmp_path):
    b = tmp_path / "budget.json"
    b.write_text(json.dumps({"schema": "wrong"}) + "\n")
    with pytest.raises(GB.BudgetRefusal, match="schema mismatch"):
        pf(auth, "AWS", tmp_path)


def test_17_invalid_accounting_numeric_refuses(auth, tmp_path):
    p = pf(auth, "AWS", tmp_path)
    for bad in (float("nan"), float("inf"), -1.0, True, "1", None, 10 ** 400):
        with pytest.raises(M.MultiHostRefusal):
            p["budget"].draw("AWS", p["pending"][0], bad)


def test_18_global_cap_overrun_refuses(auth, tmp_path):
    p = pf(auth, "AWS", tmp_path)
    with pytest.raises(M.MultiHostRefusal, match="global cap exceeded"):
        p["budget"].draw("AWS", p["pending"][0], 5000.0)


# ---- 19-20: obsolete caps unreachable ------------------------------------
def test_19_20_obsolete_and_per_host_caps_unreachable():
    src = (NS / "driver/integrated_sr_launcher.py").read_text()
    src += (NS / "driver/global_budget.py").read_text()
    assert "1126" not in src and "1848" not in src
    assert not hasattr(M, "gate_per_host_reservation")
    assert M.GLOBAL_CPU_CAP == 4500.0 and M.PROTOCOL_BOUND_CPU_CAP == 4500.0


# ---- 21-22: scientific scope --------------------------------------------
@pytest.mark.parametrize("key,val", [("D", 12), ("Z", 21), ("precision_bits", 128),
                                     ("candidates", 45), ("contracts", 101),
                                     ("backend", "O6"), ("total_cells", 315)])
def test_21_scientific_scope_mutation_refuses(auth, tmp_path, key, val):
    bad = copy.deepcopy(auth); bad["scientific_scope"][key] = val
    with pytest.raises(M.MultiHostRefusal):
        pf(bad, "AWS", tmp_path)


def test_22_obligation_universe_mutation_refuses(auth, tmp_path):
    bad = copy.deepcopy(auth); bad["scientific_scope"]["obligations"] = 8848
    with pytest.raises(M.MultiHostRefusal):
        pf(bad, "AWS", tmp_path)


# ---- 23-25: the result-bearing transition --------------------------------
def test_23_production_disabled_refuses_the_transition(auth, tmp_path):
    p = pf(auth, "AWS", tmp_path)
    assert p["auth"]["production_enabled"] is False
    with pytest.raises(M.MultiHostRefusal, match="production_enabled is false"):
        L.execute_one_cell(p, p["pending"][0], science=stub_science)


def test_24_authorized_transition_reaches_the_real_executor_with_a_stub(auth, tmp_path):
    """Proves the post-authorization path is COMPLETE and executable: flipping
    only production_enabled reaches the real executor boundary. The scientific
    callable is stubbed, so no genuine production cell is computed."""
    enabled = copy.deepcopy(auth); enabled["production_enabled"] = True
    p = pf(enabled, "AWS", tmp_path)
    cell = p["pending"][0]
    out = L.execute_one_cell(p, cell, science=stub_science, reservation_cpu_h=1.0)
    assert out["cell_id"] == cell
    assert out["record"]["complete"] is True
    assert out["record"]["obligations_completed"] == 28
    assert out["cap"]["charged_cpu_h"] <= M.GLOBAL_CPU_CAP
    assert p["budget"].status()["completed_cells"] == [cell]


def test_25_scientific_adapter_identity_is_checked(auth, tmp_path):
    bad = dict(auth, scientific_adapter_hash="0" * 64)
    with pytest.raises(M.MultiHostRefusal, match="adapter hash"):
        pf(bad, "AWS", tmp_path)
    ident = EA.adapter_identity(ROOT)
    assert ident["SCIENTIFIC_ADAPTER_HASH"] == auth["scientific_adapter_hash"]
    assert len(ident["modules"]) == len(EA.BOUND_SCIENTIFIC_MODULES) + 1


# ---- 26-27: cell-atomic resume -------------------------------------------
def test_26_torn_cell_leaves_no_completed_cell(auth, tmp_path):
    enabled = copy.deepcopy(auth); enabled["production_enabled"] = True
    p = pf(enabled, "AWS", tmp_path)
    cell = p["pending"][0]

    def exploding(mods, idx):
        raise RuntimeError("scientific failure before finalisation")

    with pytest.raises(RuntimeError):
        L.execute_one_cell(p, cell, science=exploding, reservation_cpu_h=1.0)
    st = p["budget"].status()
    assert st["completed_cells"] == []                     # nothing finalised
    assert st["cap"]["charged_cpu_h"] == pytest.approx(
        1.15 * auth["governed_overhead_cpu_h"])            # reservation returned


def test_27_resume_recognises_only_finalised_cells(auth, tmp_path):
    enabled = copy.deepcopy(auth); enabled["production_enabled"] = True
    p = pf(enabled, "AWS", tmp_path)
    done = p["pending"][0]
    L.execute_one_cell(p, done, science=stub_science, reservation_cpu_h=1.0)
    p2 = pf(enabled, "AWS", tmp_path)
    assert done not in p2["pending"]
    assert len(p2["pending"]) == len(p["pending"]) - 1
    with pytest.raises(M.MultiHostRefusal):
        L.execute_one_cell(p2, done, science=stub_science, reservation_cpu_h=1.0)


# ---- 28-30: final assembly ----------------------------------------------
def _ledgers(auth, owners, n_aws=None, n_vul=None, dup=False):
    def rec(c, role):
        return {"cell_id": c, "role": role, "producer_commit": auth["producer_commit"],
                "checkpoint_sha256": auth["checkpoint_sha256"],
                "runtime_contract_hash": auth["runtime_contract_hashes"][role],
                "scientific_content_hash": "%064x" % c, "cpu_seconds": 3600.0,
                "obligations_completed": 28, "complete": True}
    aws = [c for c, r in sorted(owners.items()) if r == "AWS"]
    vul = [c for c, r in sorted(owners.items()) if r == "VULTR"]
    A = [rec(c, "AWS") for c in aws[:n_aws if n_aws is not None else len(aws)]]
    V = [rec(c, "VULTR") for c in vul[:n_vul if n_vul is not None else len(vul)]]
    if A:
        A[0]["obligations_completed"] = 29
    if dup:
        A.append(rec(aws[0], "AWS"))
        A[-1]["obligations_completed"] = 0
    return {"AWS": A, "VULTR": V}


def test_28_final_assembly_rejects_315(auth, tmp_path):
    p = pf(auth, "AWS", tmp_path)
    with pytest.raises(M.MultiHostRefusal):
        L.final_assembly(p, _ledgers(p["auth"], p["owners"], n_aws=246))


def test_29_final_assembly_rejects_duplicate(auth, tmp_path):
    p = pf(auth, "AWS", tmp_path)
    with pytest.raises(M.MultiHostRefusal):
        L.final_assembly(p, _ledgers(p["auth"], p["owners"], dup=True))


def test_30_final_assembly_admits_exact_316(auth, tmp_path):
    p = pf(auth, "AWS", tmp_path)
    out = L.final_assembly(p, _ledgers(p["auth"], p["owners"]))
    assert out["cells_completed"] == 316
    assert out["obligations_completed"] == 8849
    assert out["cap"]["charged_cpu_h"] <= M.GLOBAL_CPU_CAP


# ---- concurrency + non-authoritative legacy driver -----------------------
def test_concurrency_serialized_active_host_refuses_the_inactive_hosts_draw(auth, tmp_path):
    """Preflight succeeds on BOTH hosts (Phase 13), but only the active host may
    DRAW from the ONE global budget, so the two can never race."""
    assert auth["concurrency"]["mode"] == "SERIALIZED_ACTIVE_HOST"
    inactive = "VULTR" if auth["concurrency"]["active_host"] == "AWS" else "AWS"
    p = pf(auth, inactive, tmp_path)                       # preflight passes
    assert p["trace"][-2]["gate"] == "global_accounting_and_cap"
    conc = next(t for t in p["trace"] if t["gate"] == "concurrency_mode")
    assert conc["detail"]["admission_allowed_on_this_host"] is False
    enabled = copy.deepcopy(auth); enabled["production_enabled"] = True
    p2 = pf(enabled, inactive, tmp_path)
    with pytest.raises(M.MultiHostRefusal, match="not the active host"):
        L.execute_one_cell(p2, p2["pending"][0], science=stub_science,
                           reservation_cpu_h=1.0)


def test_role_cannot_be_spoofed_by_the_caller(auth):
    with pytest.raises(M.MultiHostRefusal):
        L.resolve_role(auth, sys_vendor="Google Compute Engine")
    assert L.resolve_role(auth, sys_vendor="Amazon EC2") == "AWS"
    assert L.resolve_role(auth, sys_vendor="Vultr") == "VULTR"


def test_gate_library_is_byte_identical_to_the_trusted_domain_predecessor():
    mine = hashlib.sha256((NS / "driver/multihost.py").read_bytes()).hexdigest()
    parent = hashlib.sha256((ROOT / "level4/closure_proofs"
                             "/p5y_k1_sr_multihost_trusted_domain_successor"
                             "/driver/multihost.py").read_bytes()).hexdigest()
    assert mine == parent, "the composed gate library must not diverge"
