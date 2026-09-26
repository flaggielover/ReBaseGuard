"""K1R5 focused tests: freeze binding, scope, predecessors, bound qualification evidence."""
import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CFG, CP = NS / "config", NS.parent
R = []
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()       # noqa: E731
j = lambda p: json.loads(Path(p).read_text())                            # noqa: E731


def check(n, f):
    try:
        f(); R.append("PASS"); print(f"  PASS  {n}")
    except AssertionError as e:
        R.append("FAIL"); print(f"  FAIL  {n}: {e}")


def test_A_checkpoint():
    cp = j(CFG / "CHECKPOINT.json")
    assert sha(CFG / "CHECKPOINT.json") == (CFG / "CHECKPOINT_HASH").read_text().strip()
    assert all(sha(CFG / n) == h for n, h in cp["frozen_artifacts"].items())
    assert cp["wrapper_sha256"] == sha(NS / "driver/k1r5_cusum_entry.py")
    assert cp["bridge_indices"] == [1000, 1001] and cp["production_started"] is False


def test_B_scope_inherited_from_k1r4():
    cp = j(CFG / "CHECKPOINT.json")["inherited"]
    k4 = j(CP / "p5y_k1r4_bridge_successor/config/CHECKPOINT.json")["inherited"]
    assert cp["m_universe"] == k4["m_universe"] and cp["precision_bits"] == k4["precision_bits"]
    assert cp["target"] == k4["target"] and cp["cost_cap_cpu_h"] == k4["cost_cap_cpu_h"] == 150.0
    assert cp["domain"] == k4["cusum_domain"]


def test_C_k1r4_untouched():
    k = CP / "p5y_k1r4_bridge_successor/config"
    assert sha(k / "CHECKPOINT.json") == (k / "CHECKPOINT_HASH").read_text().strip() == \
        "9091cb0d5db6cc0a8d233f1667bea78bc69be676b2672f2e47506c453d2a33f0"
    assert sha(k / "SOURCE_MANIFEST.json") == "505b96015ef3afdda6046851f1a429709935c472bdf609f2e9163f8d0ca5cbb5"


def test_D_identity_not_aux4():
    i = j(CFG / "PRODUCER_IDENTITY.json")
    assert i["aux4_identity_reused"] is False and i["producer_manifest_hash"] == sha(CFG / "PRODUCER_MANIFEST.json")
    m = j(CFG / "PRODUCER_MANIFEST.json")
    assert len(m["files"]) == 59 and m["inherited_kernel"]["verified_unchanged"] is True


def test_E_qualification_evidence():
    q = j(NS / "evidence/QUALIFICATION_K1R5.json")
    assert q["verdict"] == "PASS" and q["gates_passed"] == q["gates_total"] == 12
    assert q["negatives_passed"] == q["negatives_total"] == 12
    assert q["cusum_can_run_concurrently_with_k1r4_sr"] is True and q["decisive_computation"] is False
    assert q["checkpoint_sha256"] == (CFG / "CHECKPOINT_HASH").read_text().strip()


def main() -> int:
    for n, f in sorted((k, v) for k, v in globals().items() if k.startswith("test_")):
        check(n.replace("test_", ""), f)
    print(f"\n{R.count('PASS')}/{len(R)} tests passed")
    return 0 if R.count("PASS") == len(R) else 1


if __name__ == "__main__":
    sys.exit(main())
