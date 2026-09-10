"""Adversarial, result-free tests for the one-way authenticated AWS -> VULTR handoff.

No genuine SR science. Every negative case must fail CLOSED.
"""
import base64, copy, json, subprocess, sys
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
sys.path.insert(0, str(NS / "driver"))
import multihost as M                                              # noqa: E402
import global_budget as GB                                         # noqa: E402
import handoff as HO                                               # noqa: E402
import integrated_sr_launcher as L                                 # noqa: E402

AUTH_PATH = NS / "config/LAUNCH_AUTHORIZATION.json"
PUB = NS / "config/handoff_pubkey.pem"
PRIV = Path("/home/ubuntu/.rebaseguard/handoff_ed25519.pem")
FP = (NS / "config/HANDOFF_PUBKEY_FINGERPRINT").read_text().strip()


def git(*a):
    return subprocess.check_output(["git", "-C", str(ROOT)] + list(a)).decode().strip()


@pytest.fixture
def auth():
    return L.load_authorization(AUTH_PATH)


@pytest.fixture
def owners(auth):
    man = M.load_shard_manifest(NS / "config/SHARD_MANIFEST.json",
                               auth["shard_manifest_sha256"])
    return M.gate_shards(man)


@pytest.fixture
def approved(auth):
    try:
        return git("rev-list", "-n1", auth["approved_launch_tag"])
    except subprocess.CalledProcessError:
        pytest.skip("approved launch tag not created yet (pre-freeze bootstrap)")


def budget_at(p, auth):
    return GB.GlobalBudget(p, M.validate_governed_cost, M.gate_global_cap,
                           overhead_cpu_h=auth["governed_overhead_cpu_h"],
                           cap_cpu_h=4500.0)


def seed_aws_complete(tmp_path, auth, owners, per_cell_s=1.0):
    """A synthetic FINISHED AWS ledger. No science: structural records only."""
    b = budget_at(tmp_path / "aws.json", auth)
    for c in sorted(x for x, r in owners.items() if r == "AWS"):
        k = b.draw("AWS", c, 0.5)
        b.commit(k, per_cell_s / 3600.0,
                 {"cell_id": c, "role": "AWS",
                  "producer_commit": auth["producer_commit"],
                  "checkpoint_sha256": auth["checkpoint_sha256"],
                  "runtime_contract_hash": auth["runtime_contract_hashes"]["AWS"],
                  "scientific_content_hash": "%064x" % c,
                  "cpu_seconds": per_cell_s,
                  "obligations_completed": L.obligations_for_cell(auth, owners, "AWS", c),
                  "complete": True})
    return b


@pytest.fixture
def signed_doc(tmp_path, auth, owners, approved):
    if not PRIV.exists():
        pytest.skip("AWS signing key not present on this host")
    b = seed_aws_complete(tmp_path, auth, owners)
    out = HO.export_handoff(auth=auth, ns=NS, owners=owners, budget=b,
                            approved_head=approved, privkey_pem=PRIV,
                            out_path=tmp_path / "handoff.json",
                            validate_governed_cost=M.validate_governed_cost,
                            gate_global_cap=M.gate_global_cap)
    return out["document"]


def vfy(doc, auth, owners, approved, pub=PUB, fp=FP):
    return HO.verify_handoff(doc=doc, auth=auth, ns=NS, owners=owners,
                             approved_head=approved, pubkey_pem=pub,
                             expected_fingerprint=fp,
                             validate_governed_cost=M.validate_governed_cost,
                             gate_global_cap=M.gate_global_cap)


def resign(doc, payload):
    """Re-sign a MUTATED payload with the real key: isolates the semantic gates
    from the signature gate."""
    p = dict(payload)
    p.pop("handoff_payload_hash", None)
    p["handoff_payload_hash"] = HO.payload_hash(p)
    sig = HO.sign(HO.canonical(p), PRIV)
    return {"payload": p, "signature_b64": base64.b64encode(sig).decode(),
            "signature_algorithm": "Ed25519"}


# ===================== positive control ====================================
def test_valid_handoff_verifies(signed_doc, auth, owners, approved):
    v = vfy(signed_doc, auth, owners, approved)
    assert v["verified"] is True
    assert len(v["aws_completed_cell_ids"]) == 247
    assert v["aws_finalized_cpu_h"] > 0
    assert v["public_key_fingerprint"] == FP
    assert v["recomputed_remaining_global_cpu_h"] < 4500.0


# ===================== 1-3 signature / key =================================
def test_01_invalid_signature(signed_doc, auth, owners, approved):
    bad = copy.deepcopy(signed_doc)
    bad["payload"]["aws_finalized_cpu_h"] = 999.0        # tamper AFTER signing
    with pytest.raises(HO.HandoffRefusal, match="verification FAILED"):
        vfy(bad, auth, owners, approved)


def test_02_missing_signature(signed_doc, auth, owners, approved):
    bad = copy.deepcopy(signed_doc); bad["signature_b64"] = ""
    with pytest.raises(HO.HandoffRefusal, match="no signature"):
        vfy(bad, auth, owners, approved)


def test_03_wrong_public_key(signed_doc, auth, owners, approved, tmp_path):
    other_priv = tmp_path / "other.pem"; other_pub = tmp_path / "other.pub"
    subprocess.run(["openssl", "genpkey", "-algorithm", "ed25519", "-out",
                    str(other_priv)], check=True, capture_output=True)
    subprocess.run(["openssl", "pkey", "-in", str(other_priv), "-pubout", "-out",
                    str(other_pub)], check=True, capture_output=True)
    with pytest.raises(HO.HandoffRefusal, match="fingerprint"):
        vfy(signed_doc, auth, owners, approved, pub=other_pub)
    fp2 = HO.public_key_fingerprint(other_pub)
    with pytest.raises(HO.HandoffRefusal, match="verification FAILED"):
        vfy(signed_doc, auth, owners, approved, pub=other_pub, fp=fp2)


# ===================== 4-5 post-signing mutation ==========================
@pytest.mark.parametrize("field,val", [("aws_finalized_cpu_h", 1.0),
                                       ("aws_completed_cell_ids", [1, 2, 3])])
def test_04_05_mutation_after_signing(signed_doc, auth, owners, approved, field, val):
    bad = copy.deepcopy(signed_doc); bad["payload"][field] = val
    with pytest.raises(HO.HandoffRefusal, match="verification FAILED"):
        vfy(bad, auth, owners, approved)


# ===================== 6-11 cell-set integrity (re-signed) ================
def test_06_11_cell_set_defects(signed_doc, auth, owners, approved):
    p = signed_doc["payload"]
    aws = sorted(c for c, r in owners.items() if r == "AWS")
    vul = sorted(c for c, r in owners.items() if r == "VULTR")
    cases = {"missing_cell": aws[:-1],
             "extra_cell": aws + [max(aws) + 1000],
             "duplicate": aws[:-1] + [aws[0]],
             "vultr_inserted": aws[:-1] + [vul[0]],
             "only_246": aws[:246],
             "count_248": aws + [vul[0]]}
    for name, ids in cases.items():
        mp = dict(p); mp["aws_completed_cell_ids"] = ids
        mp["aws_completed_cell_count"] = len(ids)
        with pytest.raises(HO.HandoffRefusal):
            vfy(resign(signed_doc, mp), auth, owners, approved)


def test_expected_ids_must_equal_frozen_shard(signed_doc, auth, owners, approved):
    p = dict(signed_doc["payload"])
    p["aws_expected_cell_ids"] = p["aws_expected_cell_ids"][:-1]
    with pytest.raises(HO.HandoffRefusal):
        vfy(resign(signed_doc, p), auth, owners, approved)


# ===================== 12-17 accounting ===================================
@pytest.mark.parametrize("field,val,pat", [
    ("aws_inflight_count", 3, "inflight"),
    ("aws_reserved_inflight_cpu_h", 5.0, "!= 0"),
    ("aws_finalized_cpu_h", float("nan"), "not finite"),
    ("aws_finalized_cpu_h", float("inf"), "not finite"),
    ("aws_finalized_cpu_h", -1.0, "negative"),
    ("aws_finalized_cpu_h", 5000.0, "cap"),
    ("aws_finalized_cpu_h", True, "bool"),
    ("aws_finalized_cpu_h", "12", "not numeric"),
])
def test_12_17_accounting_defects(signed_doc, auth, owners, approved, field, val, pat):
    p = dict(signed_doc["payload"]); p[field] = val
    with pytest.raises(HO.HandoffRefusal, match=pat):
        vfy(resign(signed_doc, p), auth, owners, approved)


# ===================== 18-28 identity / transition ========================
@pytest.mark.parametrize("field,val", [
    ("approved_launch_head", "f" * 40),
    ("producer_commit", "b" * 40),
    ("protocol_hash", "0" * 64),
    ("checkpoint_hash", "0" * 64),
    ("launch_authorization_hash", "0" * 64),
    ("shard_hash", "0" * 64),
    ("scientific_adapter_hash", "0" * 64),
    ("integrated_source_manifest_hash", "0" * 64),
    ("approved_launch_tag", "some-other-tag"),
    ("global_cpu_cap", 9000.0),
    ("source_host", "VULTR"),
    ("target_host", "AWS"),
    ("transition_id", "VULTR_TO_AWS"),
    ("sequence", 2),
    ("schema_version", "something.else.v9"),
])
def test_18_28_identity_and_transition_defects(signed_doc, auth, owners, approved,
                                               field, val):
    p = dict(signed_doc["payload"]); p[field] = val
    with pytest.raises(HO.HandoffRefusal):
        vfy(resign(signed_doc, p), auth, owners, approved)


# ===================== 32-33 corrupted internal hashes ====================
def test_32_33_corrupted_internal_hashes(signed_doc, auth, owners, approved):
    bad = resign(signed_doc, dict(signed_doc["payload"]))
    bad["payload"]["handoff_payload_hash"] = "0" * 64
    with pytest.raises(HO.HandoffRefusal, match="verification FAILED|payload_hash"):
        vfy(bad, auth, owners, approved)
    for f in ("aws_ledger_hash", "aws_result_manifest_hash"):
        d = copy.deepcopy(signed_doc); d["payload"][f] = "0" * 64
        with pytest.raises(HO.HandoffRefusal, match="verification FAILED"):
            vfy(d, auth, owners, approved)


# ===================== 29-31 replay / conflict ============================
def test_29_31_replay_and_conflict(signed_doc, auth, owners, approved, tmp_path):
    ns = tmp_path / "vultr_ns"; (ns / "evidence").mkdir(parents=True)
    b = budget_at(tmp_path / "v.json", auth)
    v = vfy(signed_doc, auth, owners, approved)
    first = HO.apply_handoff(verified=v, budget=b, ns=ns)
    assert first["status"] == "APPLIED"
    again = HO.apply_handoff(verified=v, budget=b, ns=ns)
    assert again["status"] == "IDEMPOTENT_ALREADY_APPLIED"
    assert len(b.status()["remote_completed_cells"]) == 247
    p2 = dict(signed_doc["payload"]); p2["handoff_nonce"] = "deadbeef" * 4
    v2 = vfy(resign(signed_doc, p2), auth, owners, approved)
    with pytest.raises(HO.HandoffRefusal, match="already been consumed"):
        HO.apply_handoff(verified=v2, budget=b, ns=ns)
    assert len(b.status()["remote_completed_cells"]) == 247


def test_import_cannot_roll_accounting_backward(signed_doc, auth, owners, approved,
                                                tmp_path):
    ns = tmp_path / "ns"; (ns / "evidence").mkdir(parents=True)
    b = budget_at(tmp_path / "v.json", auth)
    v = vfy(signed_doc, auth, owners, approved)
    HO.apply_handoff(verified=v, budget=b, ns=ns)
    before = b.status()["cap"]["charged_cpu_h"]
    with pytest.raises(GB.BudgetRefusal, match="different remote handoff"):
        b.import_remote_completion(role="AWS", cell_ids=[1, 2], finalized_cpu_h=0.0,
                                   payload_hash="0" * 64)
    assert b.status()["cap"]["charged_cpu_h"] == before


# ===================== export-side gates ==================================
def test_export_refuses_incomplete_shard(tmp_path, auth, owners, approved):
    if not PRIV.exists():
        pytest.skip("no signing key")
    b = budget_at(tmp_path / "part.json", auth)
    for c in sorted(x for x, r in owners.items() if r == "AWS")[:10]:
        k = b.draw("AWS", c, 0.5)
        b.commit(k, 0.0002, {"cell_id": c, "role": "AWS",
                             "producer_commit": auth["producer_commit"],
                             "checkpoint_sha256": auth["checkpoint_sha256"],
                             "runtime_contract_hash": auth["runtime_contract_hashes"]["AWS"],
                             "scientific_content_hash": "%064x" % c, "cpu_seconds": 0.7,
                             "obligations_completed": 28, "complete": True})
    with pytest.raises(HO.HandoffRefusal, match="not complete"):
        HO.export_handoff(auth=auth, ns=NS, owners=owners, budget=b,
                          approved_head=approved, privkey_pem=PRIV,
                          out_path=tmp_path / "x.json",
                          validate_governed_cost=M.validate_governed_cost,
                          gate_global_cap=M.gate_global_cap)


def test_export_refuses_with_inflight(tmp_path, auth, owners, approved):
    if not PRIV.exists():
        pytest.skip("no signing key")
    b = seed_aws_complete(tmp_path, auth, owners)
    b.draw("AWS", sorted(x for x, r in owners.items() if r == "VULTR")[0], 0.5)
    with pytest.raises(HO.HandoffRefusal, match="in-flight"):
        HO.export_handoff(auth=auth, ns=NS, owners=owners, budget=b,
                          approved_head=approved, privkey_pem=PRIV,
                          out_path=tmp_path / "x.json",
                          validate_governed_cost=M.validate_governed_cost,
                          gate_global_cap=M.gate_global_cap)


def test_export_refuses_without_private_key(tmp_path, auth, owners, approved):
    b = seed_aws_complete(tmp_path, auth, owners)
    with pytest.raises(HO.HandoffRefusal, match="signing key absent"):
        HO.export_handoff(auth=auth, ns=NS, owners=owners, budget=b,
                          approved_head=approved, privkey_pem=tmp_path / "nope.pem",
                          out_path=tmp_path / "x.json",
                          validate_governed_cost=M.validate_governed_cost,
                          gate_global_cap=M.gate_global_cap)


def test_export_is_idempotent(tmp_path, auth, owners, approved):
    if not PRIV.exists():
        pytest.skip("no signing key")
    b = seed_aws_complete(tmp_path, auth, owners)
    kw = dict(auth=auth, ns=NS, owners=owners, budget=b, approved_head=approved,
              privkey_pem=PRIV, out_path=tmp_path / "h.json",
              validate_governed_cost=M.validate_governed_cost,
              gate_global_cap=M.gate_global_cap)
    a = HO.export_handoff(**kw); c = HO.export_handoff(**kw)
    assert a["status"] == "EXPORTED" and c["status"] == "IDEMPOTENT_ALREADY_EXPORTED"


def test_export_refuses_inconsistent_existing_handoff(tmp_path, auth, owners, approved):
    if not PRIV.exists():
        pytest.skip("no signing key")
    b = seed_aws_complete(tmp_path, auth, owners)
    out = tmp_path / "h.json"
    HO.export_handoff(auth=auth, ns=NS, owners=owners, budget=b, approved_head=approved,
                      privkey_pem=PRIV, out_path=out,
                      validate_governed_cost=M.validate_governed_cost,
                      gate_global_cap=M.gate_global_cap)
    d = json.loads(out.read_text()); d["payload"]["aws_finalized_cpu_h"] = 1.0
    out.write_text(json.dumps(d))
    with pytest.raises(HO.HandoffRefusal, match="INCONSISTENT"):
        HO.export_handoff(auth=auth, ns=NS, owners=owners, budget=b,
                          approved_head=approved, privkey_pem=PRIV, out_path=out,
                          validate_governed_cost=M.validate_governed_cost,
                          gate_global_cap=M.gate_global_cap)


# ===================== atomicity / anti-trust ==============================
def test_atomic_write_leaves_no_partial_file(tmp_path):
    p = tmp_path / "a" / "b.json"
    HO._atomic_write(p, b'{"x":1}\n')
    assert p.read_bytes() == b'{"x":1}\n'
    assert not list(p.parent.glob(".tmp-*")), "a temp file survived"


def test_verifier_does_not_trust_self_asserted_completion(signed_doc, auth, owners,
                                                          approved):
    """aws_shard_complete=true must NOT rescue a short cell list."""
    p = dict(signed_doc["payload"])
    p["aws_completed_cell_ids"] = p["aws_completed_cell_ids"][:100]
    p["aws_completed_cell_count"] = 100
    p["aws_shard_complete"] = True
    with pytest.raises(HO.HandoffRefusal, match="RECOMPUTED as incomplete"):
        vfy(resign(signed_doc, p), auth, owners, approved)


def test_verifier_recomputes_remaining_budget(signed_doc, auth, owners, approved):
    """A lying remaining_global_cpu_h is ignored: the verifier recomputes."""
    p = dict(signed_doc["payload"]); p["remaining_global_cpu_h"] = 4499.0
    v = vfy(resign(signed_doc, p), auth, owners, approved)
    assert v["recomputed_remaining_global_cpu_h"] != 4499.0
