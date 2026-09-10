"""Focused, RESULT-FREE launch-readiness tests for the production authorization.

No genuine SR cell is executed anywhere in this file. Positive tests load the
FROZEN artifacts unchanged; every negative test builds an explicit temporary
negative control and never writes it back.
"""
import copy, hashlib, json, subprocess, sys
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
PREV = NS.parent / "p5y_k1_sr_multihost_handoff_successor"
ROOT = NS.parents[2]
sys.path.insert(0, str(NS / "driver"))
import multihost as M                                              # noqa: E402
import global_budget as GB                                         # noqa: E402
import integrated_sr_launcher as L                                 # noqa: E402
import worker_pool as WP                                           # noqa: E402
import production_launcher as PL                                   # noqa: E402
import production_provenance as PP                                 # noqa: E402

AUTH_PATH = NS / "config/LAUNCH_AUTHORIZATION.json"
FROZEN_AUTH_SHA = hashlib.sha256(AUTH_PATH.read_bytes()).hexdigest()
SIX = {v: "1" for v in M.THREAD_CONTRACT_VARS}
AWS_SIBS = {c: [c, c + 16] for c in range(16)}
VUL_SIBS = {0: [0, 1], 2: [2, 3], 4: [4, 5], 6: [6, 7]}
AWS_RT = "d49f043755ef658a60e3c4017022ddecf0642a087a6e5bb0c1f2aefbe9721191"
VUL_RT = "c7f9fc671664a1bcfef6d2d3d93d6cc865a2a241a869f2e93f94e6e00b6489d9"
AH = PL.authorization_hash()
ADAPTER = json.loads(AUTH_PATH.read_text())["scientific_adapter_hash"]


@pytest.fixture
def auth():
    return PL.load_production_authorization()


def negative_control(**overrides):
    a = json.loads(AUTH_PATH.read_text())
    a.update(overrides)
    return a


def pf(a, role, tmp_path, **kw):
    tag_or_skip(a)
    base = dict(role=role, env=SIX, repo=ROOT, ns=NS, root=ROOT,
                budget_path=tmp_path / "prod_ledger.json",
                live_hash=AWS_RT if role == "AWS" else VUL_RT,
                cores=list(range(16)) if role == "AWS" else [0, 2, 4, 6],
                siblings=AWS_SIBS if role == "AWS" else VUL_SIBS)
    base.update(kw)
    return PL.production_preflight(a, **base)


def tag_or_skip(a):
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-list", "-n1", a["approved_launch_tag"]]).decode().strip()
    except subprocess.CalledProcessError:
        pytest.skip("production launch tag not created yet (pre-freeze bootstrap)")


def genuine(cell, role, a, **over):
    rec = {"cell_id": cell, "role": role, "producer_commit": a["producer_commit"],
           "checkpoint_sha256": a["checkpoint_sha256"],
           "runtime_contract_hash": a["runtime_contract_hashes"][role],
           "scientific_content_hash": hashlib.sha256(f"cert-{cell}".encode()).hexdigest(),
           "cpu_seconds": 1.0, "obligations_completed": 28, "complete": True}
    rec.update(over)
    return PP.seal(rec, production_authorization_hash=AH, scientific_adapter_hash=ADAPTER,
                   certificate_digest=hashlib.sha256(f"c{cell}".encode()).hexdigest())


def phase8_synthetic(cell, role, a):
    """Byte-shaped exactly as the frozen synthetic scheduler writes it."""
    return {"cell_id": cell, "role": role, "producer_commit": a["producer_commit"],
            "checkpoint_sha256": a["inherited"]["checkpoint_sha256"],
            "runtime_contract_hash": a["runtime_contract_hashes"][role],
            "scientific_content_hash": "%064x" % cell, "cpu_seconds": 1.0,
            "obligations_completed": 28, "complete": True}


# ---- guard: the frozen artifact is never mutated by any test ---------------
def test_00_frozen_authorization_never_mutated():
    assert hashlib.sha256(AUTH_PATH.read_bytes()).hexdigest() == FROZEN_AUTH_SHA


# ---- H1 -------------------------------------------------------------------
def test_01_valid_authorization_reaches_READY_without_science(auth, tmp_path):
    p = pf(auth, "AWS", tmp_path)
    assert p["READY"] is True
    assert p["auth"]["production_enabled"] is True
    assert [t["status"] for t in p["trace"]] == ["PASS"] * len(p["trace"])
    gates = [t["gate"] for t in p["trace"]]
    for g in ("production_authorization", "production_campaign_scope",
              "production_result_namespace", "global_accounting_and_cap"):
        assert g in gates
    assert p["production"]["genuine_cells_completed"] == 0
    assert p["production"]["scope"] == {
        "total_cells": 316, "aws_cells": 247, "vultr_cells": 69, "obligations": 8849,
        "global_cpu_cap": 4500.0,
        "execution_order": ["AWS", "AUTHENTICATED_HANDOFF", "VULTR"]}
    assert len(p["pending"]) == 247
    L.gate_production_enabled(p["auth"])          # reachable, and NOT invoked


# ---- H2 -------------------------------------------------------------------
def test_02_missing_authorization_refuses_science(tmp_path):
    with pytest.raises(PL.ProductionRefusal, match="production authorization absent"):
        PL.load_production_authorization(path=tmp_path / "nope.json",
                                         hash_path=tmp_path / "nope.hash")
    prev_auth = L.load_authorization(
        PREV / "config/LAUNCH_AUTHORIZATION.json",
        expect_sha256=(PREV / "config/LAUNCH_AUTHORIZATION_HASH").read_text().strip())
    with pytest.raises(M.MultiHostRefusal, match="production_enabled is false"):
        L.gate_production_enabled(prev_auth)
    with pytest.raises(WP.AffinityRefusal, match="production_enabled=false"):
        WP._run_task({"kind": "SCIENCE", "cell_id": 0}, ROOT, False)


# ---- H3 -------------------------------------------------------------------
def test_03_tampered_authorization_refused(tmp_path):
    d = tmp_path / "t"; d.mkdir()
    body = json.loads(AUTH_PATH.read_text())
    body["global_cpu_cap"] = 99999.0
    p = d / "LAUNCH_AUTHORIZATION.json"
    p.write_text(json.dumps(body, indent=1, sort_keys=True) + "\n")
    (d / "H").write_text(FROZEN_AUTH_SHA + "\n")          # stale (correct) hash
    with pytest.raises(M.MultiHostRefusal, match="sha256"):
        PL.load_production_authorization(path=p, hash_path=d / "H")
    (d / "H").write_text(hashlib.sha256(p.read_bytes()).hexdigest() + "\n")
    a = PL.load_production_authorization(path=p, hash_path=d / "H")   # hash re-stamped
    owners = M.gate_shards(M.load_shard_manifest(NS / "config/SHARD_MANIFEST.json",
                                                 a["shard_manifest_sha256"]))
    with pytest.raises(PL.ProductionRefusal, match="global_cpu_cap drift"):
        PL.gate_campaign_scope(a, owners)                 # content gate still refuses


def test_03b_tampered_production_closure_refused(tmp_path):
    bad = negative_control(production_closure_sha256="0" * 64)
    d = tmp_path / "c"; d.mkdir()
    p = d / "a.json"; p.write_text(json.dumps(bad, indent=1, sort_keys=True) + "\n")
    (d / "H").write_text(hashlib.sha256(p.read_bytes()).hexdigest() + "\n")
    with pytest.raises(PL.ProductionRefusal, match="production closure"):
        PL.load_production_authorization(path=p, hash_path=d / "H")


# ---- H4 -------------------------------------------------------------------
def test_04_wrong_approved_head_refused(auth):
    approved = tag_or_skip(auth)
    with pytest.raises(M.MultiHostRefusal, match="unbound descendant|!= approved"):
        L._gate_head_against(approved, "f" * 40, clean=True)
    with pytest.raises(M.MultiHostRefusal, match="not clean"):
        L._gate_head_against(approved, approved, clean=False)
    assert L.gate_approved_launch_head(auth, repo=ROOT)["live_head"] == approved


def test_04b_authorization_binds_its_own_tag_not_the_parents(auth):
    assert auth["approved_launch_tag"] == "p5y-k1-sr-production-authorized-preresult"
    assert auth["parent"]["tag"] == "p5y-k1-sr-multihost-handoff-preresult"
    assert auth["approved_launch_tag"] != auth["parent"]["tag"]


# ---- H5 -------------------------------------------------------------------
def test_05_wrong_producer_refused(auth):
    approved = tag_or_skip(auth)
    for bad in ("0" * 40, "abc", None, 12345):
        with pytest.raises(M.MultiHostRefusal):
            L.gate_producer_ancestry(negative_control(producer_commit=bad), approved,
                                     repo=ROOT)
    out = L.gate_producer_ancestry(auth, approved, repo=ROOT)
    assert out["producer_commit"] == "e136c1a4b0ad0eeb31495f0689d80703e70deebe"
    assert out["is_ancestor_of_approved_head"] is True


# ---- H6 -------------------------------------------------------------------
def test_06_wrong_runtime_fingerprint_refused(auth):
    for role in ("AWS", "VULTR"):
        with pytest.raises(M.MultiHostRefusal):
            L.gate_runtime_identity(auth, role, live_hash="0" * 64, env=SIX)
    with pytest.raises(M.MultiHostRefusal, match="thread contract"):
        L.gate_runtime_identity(auth, "AWS", live_hash=AWS_RT, env={})


# ---- H7 -------------------------------------------------------------------
def test_07_wrong_host_role_refused(auth, tmp_path):
    with pytest.raises(M.MultiHostRefusal):
        L.resolve_role(auth, sys_vendor="Totally Unknown Vendor")
    p = pf(auth, "VULTR", tmp_path)
    assert p["active"]["active_host"] == "AWS"        # AWS is first in the frozen order
    with pytest.raises(M.MultiHostRefusal, match="not the active host"):
        PL.admit_cell(p, p["pending"][0])


# ---- H8 -------------------------------------------------------------------
def test_08_cell_outside_frozen_shard_refused(auth, tmp_path):
    p = pf(auth, "AWS", tmp_path)
    vultr_cell = next(c for c, r in p["owners"].items() if r == "VULTR")
    with pytest.raises(M.MultiHostRefusal):
        PL.admit_cell(p, vultr_cell)
    for bad in (-1, 316, 9999):
        with pytest.raises(M.MultiHostRefusal):
            PL.admit_cell(p, bad)


# ---- H9 -------------------------------------------------------------------
def test_09_duplicate_completed_cell_refused(auth, tmp_path):
    p = pf(auth, "AWS", tmp_path)
    cell = p["pending"][0]
    key = PL.admit_cell(p, cell)
    with pytest.raises(GB.BudgetRefusal, match="already has an open reservation"):
        PL.admit_cell(p, cell)
    p["budget"].commit(key, 0.001, genuine(cell, "AWS", auth, obligations_completed=29))
    with pytest.raises(GB.BudgetRefusal, match="already complete"):
        p["budget"].draw("AWS", cell, 1.0)


# ---- H10 ------------------------------------------------------------------
def test_10_budget_over_4500_refused(auth, tmp_path):
    p = pf(auth, "AWS", tmp_path)
    with pytest.raises((M.MultiHostRefusal, GB.BudgetRefusal), match="global cap exceeded"):
        PL.admit_cell(p, p["pending"][0], reservation_cpu_h=4500.0)
    assert p["budget"].status()["cap"]["charged_cpu_h"] <= 4500.0
    assert p["budget"].raw_state().get("open_reservations") == {}


# ---- H11 ------------------------------------------------------------------
@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf"), -1.0,
                                 "12.0", True, 10 ** 400, complex(1, 1), [1.0]])
def test_11_hostile_accounting_input_refused(auth, tmp_path, bad):
    p = pf(auth, "AWS", tmp_path)
    with pytest.raises((M.MultiHostRefusal, GB.BudgetRefusal, TypeError, ValueError,
                        OverflowError)):
        PL.admit_cell(p, p["pending"][0], reservation_cpu_h=bad)
    assert p["budget"].raw_state().get("open_reservations") == {}


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf"), -1.0,
                                 "12.0", None, True, 10 ** 400])
def test_11b_hostile_value_reaching_the_validator_is_refused(bad):
    """None is admit_cell's default SENTINEL, not a value; reaching the trusted
    domain it is refused like every other hostile input."""
    with pytest.raises((M.MultiHostRefusal, TypeError, ValueError, OverflowError)):
        M.validate_governed_cost(bad, "cell reservation")


def test_11c_none_reservation_uses_the_authorised_default(auth, tmp_path):
    p = pf(auth, "AWS", tmp_path)
    cell = p["pending"][0]
    PL.admit_cell(p, cell, reservation_cpu_h=None)
    res = p["budget"].raw_state()["open_reservations"][f"AWS:{cell}"]
    assert res["reserved_cpu_h"] == auth["hosts"]["AWS"]["per_cell_reservation_cpu_h"]


# ---- H12 ------------------------------------------------------------------
def test_12_phase8_synthetic_record_refused_by_production_assembly(auth, tmp_path):
    p = pf(auth, "AWS", tmp_path)
    owners = p["owners"]
    syn = phase8_synthetic(0, "AWS", auth)
    # the FROZEN validator still admits it -- that is exactly the gap being closed
    M.validate_record(syn, "AWS", owners, auth["producer_commit"],
                      auth["inherited"]["checkpoint_sha256"])
    with pytest.raises(PP.ProvenanceRefusal, match="NO production provenance"):
        PP.verify(syn, production_authorization_hash=AH, scientific_adapter_hash=ADAPTER)
    ledgers = {"AWS": [phase8_synthetic(c, "AWS", auth) for c, r in sorted(owners.items())
                       if r == "AWS"],
               "VULTR": [phase8_synthetic(c, "VULTR", auth) for c, r in sorted(owners.items())
                         if r == "VULTR"]}
    with pytest.raises(PP.ProvenanceRefusal):
        PL.assemble_production_campaign(p, ledgers)


def test_12b_synthetic_stand_in_hash_refused_even_if_provenance_is_forged(auth):
    """A stand-in content hash is refused on its own, before any binding check."""
    rec = {"cell_id": 7, "role": "AWS", "producer_commit": auth["producer_commit"],
           "checkpoint_sha256": auth["checkpoint_sha256"],
           "runtime_contract_hash": AWS_RT,
           "scientific_content_hash": PP.synthetic_stand_in(7),
           "cpu_seconds": 1.0, "obligations_completed": 28, "complete": True}
    sealed = PP.seal(rec, production_authorization_hash=AH, scientific_adapter_hash=ADAPTER,
                     certificate_digest=hashlib.sha256(b"c7").hexdigest())
    with pytest.raises(PP.ProvenanceRefusal, match="synthetic stand-in"):
        PP.verify(sealed, production_authorization_hash=AH, scientific_adapter_hash=ADAPTER)


def test_12c_record_from_a_foreign_authorization_refused(auth):
    """TEMPORAL FIREWALL: a record sealed under any other authorization is refused."""
    rec = genuine(3, "AWS", auth)
    rec[PP.PROVENANCE_FIELD]["production_authorization_hash"] = "0" * 64
    with pytest.raises(PP.ProvenanceRefusal, match="not produced under this authorization"):
        PP.verify(rec, production_authorization_hash=AH, scientific_adapter_hash=ADAPTER)


def test_12d_field_swapped_or_copied_record_refused(auth):
    for mut in ({"cell_id": 4}, {"role": "VULTR"}, {"cpu_seconds": 99.0,
                                                    "scientific_content_hash": "a" * 64}):
        rec = genuine(3, "AWS", auth)
        rec.update(mut)
        if "cpu_seconds" in mut or "role" in mut or "cell_id" in mut:
            with pytest.raises(PP.ProvenanceRefusal):
                PP.verify(rec, production_authorization_hash=AH,
                          scientific_adapter_hash=ADAPTER)


def test_12e_a_genuine_record_is_accepted(auth):
    assert PP.verify(genuine(3, "AWS", auth), production_authorization_hash=AH,
                     scientific_adapter_hash=ADAPTER)["task_kind"] == "SCIENCE"


# ---- H13 ------------------------------------------------------------------
@pytest.mark.parametrize("strip", ["production_provenance", "task_kind", "synthetic",
                                   "binding", "certificate_digest", "schema"])
def test_13_record_lacking_genuine_provenance_refused(auth, strip):
    rec = genuine(5, "AWS", auth)
    if strip == "production_provenance":
        rec.pop(strip)
    else:
        rec[PP.PROVENANCE_FIELD].pop(strip, None)
    with pytest.raises(PP.ProvenanceRefusal):
        PP.verify(rec, production_authorization_hash=AH, scientific_adapter_hash=ADAPTER)


def test_13b_synthetic_marked_record_refused(auth):
    rec = genuine(5, "AWS", auth)
    rec[PP.PROVENANCE_FIELD]["synthetic"] = True
    with pytest.raises(PP.ProvenanceRefusal):
        PP.verify(rec, production_authorization_hash=AH, scientific_adapter_hash=ADAPTER)
    rec = genuine(5, "AWS", auth)
    rec[PP.PROVENANCE_FIELD]["task_kind"] = "SYNTHETIC_SPIN"
    with pytest.raises(PP.ProvenanceRefusal, match="is not SCIENCE"):
        PP.verify(rec, production_authorization_hash=AH, scientific_adapter_hash=ADAPTER)


# ---- H14 ------------------------------------------------------------------
def test_14_imported_aws_cost_is_preserved_on_vultr(auth, tmp_path):
    """Section D end-to-end, under the PRODUCTION authorization."""
    b = GB.GlobalBudget(tmp_path / "v.json", M.validate_governed_cost, M.gate_global_cap,
                        overhead_cpu_h=auth["governed_overhead_cpu_h"], cap_cpu_h=4500.0)
    owners = M.gate_shards(M.load_shard_manifest(NS / "config/SHARD_MANIFEST.json",
                                                 auth["shard_manifest_sha256"]))
    aws = sorted(c for c, r in owners.items() if r == "AWS")
    COST = 1000.0
    b.import_remote_completion(role="AWS", cell_ids=aws, finalized_cpu_h=COST,
                               payload_hash="a" * 64)
    st = b.status()
    assert len(st["remote_completed_cells"]) == 247
    assert st["cap"]["sr_cpu_h"] == COST                      # not reset, not omitted
    assert abs(st["cap"]["charged_cpu_h"] - 1.15 * (COST + auth["governed_overhead_cpu_h"])) < 1e-9
    b.import_remote_completion(role="AWS", cell_ids=aws, finalized_cpu_h=COST,
                               payload_hash="a" * 64)
    assert b.status()["cap"]["sr_cpu_h"] == COST              # not double counted
    with pytest.raises(GB.BudgetRefusal):
        b.import_remote_completion(role="AWS", cell_ids=aws, finalized_cpu_h=1.0,
                                   payload_hash="b" * 64)
    assert L.resolve_active_host(auth, owners, sorted(
        set(st["completed_cells"]) | set(st["remote_completed_cells"])))["active_host"] == "VULTR"


# ---- H15 ------------------------------------------------------------------
def test_15_production_output_cannot_collide_with_evidence(auth):
    ok = PL.gate_production_result_path(PL.PRODUCTION_DIR / "cells" / "0000.json")
    assert str(ok).startswith(str((NS / "production").resolve()))
    for bad in (NS / "evidence/handoff_verification_vultr.json",
                NS / "evidence/EVIDENCE_MANIFEST.json",
                NS / "diagnostics/x.json", NS / "phase8/x.json",
                NS / "config/LAUNCH_AUTHORIZATION.json",
                NS.parent / "p5y_k1_sr_multihost_handoff_successor/evidence/x.json",
                Path("/tmp/x.json")):
        with pytest.raises(PL.ProductionRefusal):
            PL.gate_production_result_path(bad)
    with pytest.raises(PL.ProductionRefusal, match="over evidence"):
        PL.gate_no_evidence_collision([NS / "evidence/handoff_consumed.json"])
    assert auth["production_result_namespace"] == "production/"


# ---- H16 ------------------------------------------------------------------
def test_16_production_remained_off_zero_genuine_cells():
    assert not (NS / "production/PRODUCTION_LEDGER.json").exists()
    assert not (NS / "production/cells").exists()
    assert sorted(p.name for p in (NS / "production").iterdir()) == ["README.md"]
    assert json.loads((NS / "config/protocol.json").read_text())[
        "genuine_sr_production_cells_at_freeze"] == 0


# ---- preservation of the predecessor and of frozen scope -------------------
@pytest.mark.parametrize("rel", [
    "driver/executor_adapter.py", "driver/global_budget.py", "driver/handoff.py",
    "driver/integrated_sr_launcher.py", "driver/multihost.py", "driver/worker_pool.py",
    "config/SHARD_MANIFEST.json", "config/SHARD_MANIFEST_SHA256.json",
    "config/handoff_pubkey.pem", "config/HANDOFF_PUBKEY_FINGERPRINT",
    "evidence/scientific_adapter_identity.json"])
def test_17_carried_forward_files_are_byte_identical(rel):
    if not (PREV / rel).exists():
        # The predecessor carries this file only in a working directory, never in
        # git: the repository-wide `*.pem` secrets rule excluded it from every
        # predecessor commit. That is the disclosed clean-checkout defect. This
        # namespace tracks its own copy (test_21) and binds it to the frozen
        # fingerprint (test_23), so identity is still proven -- just not by
        # comparison against a file a clean checkout does not have.
        pytest.skip(f"{rel} is not tracked in the predecessor (disclosed *.pem defect); "
                    "identity is proven by test_21 and test_23 instead")
    assert hashlib.sha256((NS / rel).read_bytes()).hexdigest() == \
           hashlib.sha256((PREV / rel).read_bytes()).hexdigest()


def test_18_frozen_scope_cap_and_shard_unchanged(auth):
    s = auth["scientific_scope"]
    assert (s["total_cells"], s["obligations"]) == (316, 8849)
    assert (s["D"], s["Z"], s["precision_bits"], s["backend"]) == (11, 20, 256, "O9")
    assert (s["candidates"], s["contracts"]) == (46, 102)
    assert auth["global_cpu_cap"] == 4500.0 == M.GLOBAL_CPU_CAP
    assert auth["hosts"]["AWS"]["cell_count"] == 247
    assert auth["hosts"]["VULTR"]["cell_count"] == 69
    assert auth["hosts"]["AWS"]["workers"] == 16
    assert auth["hosts"]["VULTR"]["workers"] == 4
    assert auth["hosts"]["VULTR"]["cores"] == [0, 2, 4, 6]
    assert not any("cap" in k for h in auth["hosts"].values() for k in h)
    assert not hasattr(M, "gate_per_host_reservation")
    prev = json.loads((PREV / "config/LAUNCH_AUTHORIZATION.json").read_text())
    assert auth["scientific_scope"] == prev["scientific_scope"]
    assert auth["runtime_contract_hashes"] == prev["runtime_contract_hashes"]
    assert auth["hosts"] == prev["hosts"]
    assert auth["far_field_obligation"] == prev["far_field_obligation"]
    assert auth["shard_manifest_sha256"] == prev["shard_manifest_sha256"]
    assert auth["scientific_adapter_hash"] == prev["scientific_adapter_hash"]
    # no stale wall-clock projection is bound as an execution requirement
    assert not any(t in k.lower() for k in auth
                   for t in ("hour", "wall_clock", "wallclock", "eta", "runtime_hours"))
    assert "stale_runtime_projection_177h" in auth["excluded_bindings"]
    assert auth["excluded_bindings"]["stale_runtime_projection_177h"].startswith("NOT BOUND")
    assert auth["cap_policy"]["per_host_hard_caps_present"] is False


def test_19_execution_order_is_the_adjudicated_sequence(auth, tmp_path):
    assert auth["execution_order"] == ["AWS", "AUTHENTICATED_HANDOFF", "VULTR"]
    assert auth["concurrency"]["host_sequence"] == ["AWS", "VULTR"]
    assert auth["concurrency"]["mode"] == "SERIALIZED_ACTIVE_HOST"
    assert auth["concurrency"]["coordinator_endpoint"] is None
    p = pf(auth, "AWS", tmp_path)
    owners = p["owners"]
    aws = [c for c, r in owners.items() if r == "AWS"]
    assert L.resolve_active_host(auth, owners, [])["active_host"] == "AWS"
    assert L.resolve_active_host(auth, owners, aws, inflight=1)["active_host"] == "AWS"
    assert L.resolve_active_host(auth, owners, aws)["active_host"] == "VULTR"


def test_20_obligation_conservation_and_far_field(auth, tmp_path):
    p = pf(auth, "AWS", tmp_path)
    owners = p["owners"]
    assert sum(L.obligations_for_cell(auth, owners, r, c)
               for c, r in owners.items()) == 8849
    ff = L.far_field_attribution(auth, owners)
    assert ff["work_id"] == "SR:-1:far_field:all_m" and ff["count"] == 1
    assert (ff["role"], ff["cell"]) == ("AWS", 0)


# ---- clean-checkout launchability -----------------------------------------
def test_21_every_closure_file_is_tracked_at_the_approved_tag(auth):
    """A clean checkout of the approved launch tag must be able to LAUNCH.

    Regression for a real, load-bearing defect: the repository-wide `*.pem`
    secrets rule silently excluded config/handoff_pubkey.pem -- a PUBLIC key and
    a mandatory member of SOURCE_CLOSURE -- from the commit. A clean checkout
    could then neither compute INTEGRATED_SOURCE_MANIFEST_HASH (so VULTR, whose
    producer binding is SOURCE_MANIFEST, could never pass preflight) nor verify
    the authenticated AWS -> VULTR handoff. Nothing in the frozen gate chain
    detected it, because every host tested so far already had the file on disk.
    """
    tag = tag_or_skip(auth)
    prefix = f"level4/closure_proofs/{NS.name}/"
    tracked = set(subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", tag, "--", prefix]
    ).decode().split())
    required = set(L.SOURCE_CLOSURE) | set(PL.PRODUCTION_CLOSURE) | {
        "config/LAUNCH_AUTHORIZATION.json", "config/LAUNCH_AUTHORIZATION_HASH",
        "evidence/INTEGRATED_SOURCE_MANIFEST.json"}
    missing = sorted(r for r in required if prefix + r not in tracked)
    assert not missing, (
        f"a clean checkout of {tag} could not launch: {missing} are not tracked")


def test_22_no_private_key_is_committed():
    prefix = f"level4/closure_proofs/{NS.name}/"
    tracked = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", "HEAD", "--", prefix]
    ).decode().split()
    # assembled at runtime so this test's own source is not a match
    marker = ("-----BEGIN ", "PRIVATE KEY-----")
    needle = (marker[0] + marker[1]).encode()
    for rel in tracked:
        assert needle not in (ROOT / rel).read_bytes(), f"{rel} contains a private key"
    pem = (NS / "config/handoff_pubkey.pem").read_text()
    assert pem.startswith(marker[0] + "PUBLIC KEY-----")


def test_23_committed_pubkey_matches_the_frozen_fingerprint(auth):
    import handoff as H
    fp = H.public_key_fingerprint(NS / "config/handoff_pubkey.pem")
    assert fp == (NS / "config/HANDOFF_PUBKEY_FINGERPRINT").read_text().strip()
    assert fp == auth["handoff"]["public_key_fingerprint"]
