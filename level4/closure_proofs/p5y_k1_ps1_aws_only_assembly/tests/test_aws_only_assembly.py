"""AWS-only assembly successor: checks A-L.

Every genuine artifact is READ-ONLY here. Failure cases mutate a COPY of the ledger and
the sealed cell files under a temp tree (tests/fixtures.py); evidence is only ever read.
"""
import json
import shutil
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "driver"))
sys.path.insert(0, str(NS / "tests"))
import fixtures as F          # noqa: E402
import ps1_assembly as A      # noqa: E402

GEN1_EV = "/home/ubuntu/rbg-runtime/p5y_k1_ps1_production/evidence"
GEN2_EV = "/home/ubuntu/rbg-runtime/p5y_k1_ps1_generation2/evidence"
FIRST16 = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60]
RESULTS = []


def check(name, fn):
    tmp = None
    try:
        tmp = F.tmpdir()
        fn(tmp)
        RESULTS.append((name, "PASS", ""))
        print(f"  PASS  {name}")
    except AssertionError as e:
        RESULTS.append((name, "FAIL", str(e)[:160]))
        print(f"  FAIL  {name}: {e}")
    except Exception as e:                      # noqa: BLE001
        RESULTS.append((name, "ERROR", f"{type(e).__name__}: {str(e)[:150]}"))
        print(f"  ERROR {name}: {type(e).__name__}: {str(e)[:150]}")
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)


def refuses(acfg, *needles):
    try:
        A.preflight(acfg)
    except A.AssemblyRefusal as e:
        msg = str(e)
        for n in needles:
            assert n.lower() in msg.lower(), f"refusal {msg!r} does not mention {n!r}"
        return msg
    raise AssertionError("expected an AssemblyRefusal, got none")


# ---------------------------------------------------------------- A, K, L, F
def test_A_complete_shard_accepted(tmp):
    rep = A.preflight(F.build(tmp))
    assert rep["route"] == A.ROUTE_AWS_ONLY, rep["route"]
    assert rep["cells_completed"] == 369 and rep["pending"] == 0
    assert rep["obligations_completed"] == 10332
    assert rep["far_field"]["units"] == 1 and rep["far_field"]["global_obligations"] == 10333
    assert rep["ledger_state"]["torn_attempts"] == {}
    assert rep["campaign_lock"] == "FREE"
    assert rep["cap"]["cap_refusal"] is None and rep["cap"]["charged_cpu_h"] < 6600


def test_K_evidence_split_unchanged(tmp):
    rep = A.preflight(F.build(tmp))
    split = rep["evidence_split"]
    assert split.get(GEN1_EV) == 16, split
    assert split.get(GEN2_EV) == 353, split
    ledger = json.loads(Path("/home/ubuntu/work/ReBaseGuard-ps1-prod-gen2/level4/"
                             "closure_proofs/p5y_k1_ps1_production/production/"
                             "PRODUCTION_LEDGER.json").read_text())
    hist = sorted(int(c) for c, r in ledger["completed_cells"].items()
                  if r["evidence"]["t5"]["path"].startswith(GEN1_EV))
    assert hist == FIRST16, hist
    for c in FIRST16:
        rec = ledger["completed_cells"][str(c)]
        assert rec["task_id"].startswith("20260912T154659Z-277931"), rec["task_id"]
        assert rec["production_provenance"]["production_authorization_hash"] == \
            "fc7cb93465916c3a7842066701b0e11fb6799bfdfc7fff55073a3f6e4cfc03ef"


def test_L_executor_manifest_unchanged(tmp):
    acfg = F.build(tmp)
    rep = A.preflight(acfg)
    assert rep["executor"]["files"] == 39 and rep["executor"]["drift"] == []
    assert rep["executor"]["integrated_source_manifest_sha256"] == \
        "13ba2ecd1c8afdaafb3463233f246716f599dd935c5b3722f4074327d8eec5fd"
    I = A.load_inputs(acfg)
    try:
        A.gate_executor_manifest(I["auth"], "/home/ubuntu")
    except A.AssemblyRefusal as e:
        assert "drift" in str(e).lower()
    else:
        raise AssertionError("executor drift was not detected")


def test_F_imported_cpu_counted_exactly_once(tmp):
    rep = A.preflight(F.build(tmp))
    a = rep["accounting"]
    total = (a["scientific_record_cpu_h"] + a["settlement_or_operational_cpu_h"]
             + a["imported_predecessor_cpu_h"])
    assert abs(a["committed_cpu_h"] - total) <= A.ACCOUNTING_TOL, a
    assert abs(a["identity_residual_cpu_h"]) <= A.ACCOUNTING_TOL
    twice = total + a["imported_predecessor_cpu_h"]
    assert abs(a["committed_cpu_h"] - twice) > A.ACCOUNTING_TOL, "import counted twice"
    assert a["imported_predecessor_cpu_h"] == 92.32
    assert 0.0 <= a["imported_predecessor_cpu_h"] - a["predecessor_measured_cpu_h"] <= 0.01


# ------------------------------------------------------- B, C, D, E, G, H, I, J
def test_B_incomplete_shard_rejected(tmp):
    def drop(ledger, cells):
        ledger["completed_cells"].pop("123")
        (cells / "0123.json").unlink()
    refuses(F.build(tmp, ledger_edit=drop), "coverage incomplete", "368/369")


def test_C_duplicate_or_missing_cell_rejected(tmp):
    def dup(ledger, cells):
        ledger["completed_cells"]["7"] = dict(ledger["completed_cells"]["6"])
        shutil.copyfile(cells / "0006.json", cells / "0007.json")
    refuses(F.build(tmp, ledger_edit=dup), "duplicate")
    tmp2 = F.tmpdir()
    try:
        def missing(ledger, cells):
            ledger["completed_cells"].pop("0")
        refuses(F.build(tmp2, ledger_edit=missing), "coverage incomplete", "missing")
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)


def test_D_open_state_rejected(tmp):
    def reservation(ledger, cells):
        ledger["open_reservations"] = {"AWS:12": {"cpu_h": 13.0}}
    refuses(F.build(tmp, ledger_edit=reservation), "open reservation")
    for edit, needle in (
        (lambda l, c: l["operational_lifecycle"]["runs"]
         .__setitem__("20260913T112316Z-1062b6ce",
                      {**l["operational_lifecycle"]["runs"]["20260913T112316Z-1062b6ce"],
                       "status": "OPEN"}), "unsettled"),
        (lambda l, c: l["operational_lifecycle"].__setitem__(
            "halt", {"reason": "RETRY_LIMIT", "cells": [1]}), "halted"),
        (lambda l, c: l.__setitem__("remote_completed_cells", {"5": {}}), "remote"),
    ):
        t = F.tmpdir()
        try:
            refuses(F.build(t, ledger_edit=edit), needle)
        finally:
            shutil.rmtree(t, ignore_errors=True)


def test_E_hash_mismatch_rejected(tmp):
    def flip(ledger, cells):
        rec = ledger["completed_cells"]["200"]
        bad = ("b" if rec["scientific_content_hash"][0] != "b" else "c") \
            + rec["scientific_content_hash"][1:]
        rec["scientific_content_hash"] = bad
        p = cells / "0200.json"
        d = json.loads(p.read_text())
        d["scientific_content_hash"] = bad
        p.write_text(json.dumps(d, sort_keys=True) + "\n")
    refuses(F.build(tmp, ledger_edit=flip), "ProvenanceRefusal", "binding does not recompute")

    def swap_evidence(ledger, cells):
        rec = ledger["completed_cells"]["201"]
        rec["evidence"]["t3"]["sha256"] = "0" * 64
        p = cells / "0201.json"
        d = json.loads(p.read_text())
        d["evidence"]["t3"]["sha256"] = "0" * 64
        p.write_text(json.dumps(d, sort_keys=True) + "\n")
    t = F.tmpdir()
    try:
        refuses(F.build(t, ledger_edit=swap_evidence), "evidence t3 does not match its sealed sha256")
    finally:
        shutil.rmtree(t, ignore_errors=True)


def test_G_imported_cpu_altered_or_missing_fails_closed(tmp):
    refuses(F.build(tmp, transition_edit=lambda t: t["accounting_import"].__setitem__(
        "predecessor_science_cpu_h", 50.0)), "imported CPU disagreement")
    for edit, needle in (
        (lambda t: t.pop("accounting_import"), "declares no imported predecessor CPU"),
        (lambda t: t["accounting_import"].__setitem__("seeded_into_generation_2_as", "elsewhere"),
         "does not seed the import"),
    ):
        d = F.tmpdir()
        try:
            refuses(F.build(d, transition_edit=edit), needle)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def strip_import(ledger, cells):      # committed without the seed: identity must break
        ledger["committed_cpu_h_by_role"]["AWS"] -= 92.32
    d = F.tmpdir()
    try:
        refuses(F.build(d, ledger_edit=strip_import), "does not reconcile")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_H_cap_violation_fails_closed(tmp):
    BURN = 4_000_000.0                     # CPU-seconds, ~1111 CPU-h over the cap
    def inflate(ledger, cells):
        rec = ledger["completed_cells"]["300"]
        rec["cpu_seconds"] += BURN
        p = cells / "0300.json"
        d = json.loads(p.read_text())
        d["cpu_seconds"] = rec["cpu_seconds"]
        p.write_text(json.dumps(d, sort_keys=True) + "\n")
        ledger["committed_cpu_h_by_role"]["AWS"] += BURN / 3600.0
    refuses(F.build(tmp, ledger_edit=inflate), "global cap exceeded")


def test_I_multi_host_still_requires_authenticated_handoff(tmp):
    def to_multihost(a):
        a["topology"] = "B_AWS_VULTR"
        a["handoff"] = {"public_key_fingerprint": "ab" * 16, "status": "REQUIRED"}
    def shard_multi(s):
        s["topology"] = "B_AWS_VULTR"
        s["AWS"]["cells"] = s["AWS"]["cells"][:300]
        s["VULTR"] = {"cells": list(range(300, 369))}
    acfg = F.build(tmp, auth_edit=to_multihost, shard_edit=shard_multi)
    I = A.load_inputs(acfg)
    assert A.select_route(I["auth"], I["shard"]) == A.ROUTE_MULTI_HOST
    refuses(acfg, "MULTI_HOST", "prodctl.py assemble --role VULTR")
    # the frozen two-host implementation is untouched and still VULTR-only
    ops = Path("/home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/"
               "p5y_k1_ps1_portable_recovery")
    sys.path.insert(0, str(ops / "ops"))
    import prodctl                                        # noqa: E402
    from opscommon import OpsRefusal                       # noqa: E402
    try:
        prodctl._assemble({}, "AWS", None, None)
    except OpsRefusal as e:
        assert "VULTR" in str(e), e
    else:
        raise AssertionError("frozen assemble accepted a non-VULTR role")
    man = json.loads((ops / "config/OPS_SOURCE_MANIFEST.json").read_text())["files"]
    assert A.sha256_file(ops / "ops/prodctl.py") == man["ops/prodctl.py"], "frozen prodctl changed"


def test_J_unknown_or_inconsistent_topology_fails_closed(tmp):
    refuses(F.build(tmp, auth_edit=lambda a: a.__setitem__("topology", "Z_MYSTERY"),
                    shard_edit=lambda s: s.__setitem__("topology", "Z_MYSTERY")),
            "unknown or inconsistent topology")
    for auth_edit, shard_edit, needle in (
        (lambda a: a.__setitem__("topology", "A_AWS_ONLY"),
         lambda s: s.__setitem__("topology", "B_AWS_VULTR"), "topology disagreement"),
        (lambda a: a.__setitem__("handoff",
                                 {"public_key_fingerprint": "cd" * 16, "status": "REQUIRED"}),
         None, "carries handoff material"),
        (None, lambda s: s.__setitem__("VULTR", {"cells": [1, 2, 3]}), "owned off-AWS"),
    ):
        d = F.tmpdir()
        try:
            refuses(F.build(d, auth_edit=auth_edit, shard_edit=shard_edit), needle)
        finally:
            shutil.rmtree(d, ignore_errors=True)


def main() -> int:
    print("PS1 AWS-only assembly successor: checks A-L")
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_")):
        check(name.replace("test_", ""), fn)
    bad = [r for r in RESULTS if r[1] != "PASS"]
    print(f"\n{len(RESULTS) - len(bad)}/{len(RESULTS)} checks passed")
    for r in bad:
        print("  ", r)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
