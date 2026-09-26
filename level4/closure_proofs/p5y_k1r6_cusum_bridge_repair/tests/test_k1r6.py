"""K1R6 focused tests: freeze binding, generated-stage reproducibility, scope, predecessors, bound qualification."""
import hashlib
import json
import subprocess
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


def test_A_checkpoint_binds_config_and_stages():
    cp = j(CFG / "CHECKPOINT.json")
    assert sha(CFG / "CHECKPOINT.json") == (CFG / "CHECKPOINT_HASH").read_text().strip()
    assert all(sha(CFG / n) == h for n, h in cp["frozen_artifacts"].items()), "config drift"
    assert all(sha(NS / "driver" / n) == h for n, h in cp["stages"].items()), "stage drift"
    assert cp["bridge_indices"] == [1000, 1001] and cp["production_started"] is False
    assert cp["previous_consumed_unsealed_cpu_h"] == 0.61


def test_B_generated_stages_reproduce():
    r = subprocess.run([sys.executable, str(NS / "code/make_k1r6_stages.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_C_scope_inherited_unchanged():
    cp = j(CFG / "CHECKPOINT.json")["inherited"]
    k5 = j(CP / "p5y_k1r5_cusum_entry/config/CHECKPOINT.json")["inherited"]
    assert cp == k5, "domain / m universe / precision / target / b_cover / cap must equal K1R5 (= K1R4)"
    assert cp["cost_cap_cpu_h"] == 150.0 and cp["m_universe"] == [1, 2, 3, 5] and cp["precision_bits"] == 256


def test_D_predecessors_untouched():
    k4, k5 = CP / "p5y_k1r4_bridge_successor/config", CP / "p5y_k1r5_cusum_entry/config"
    assert sha(k4 / "CHECKPOINT.json") == (k4 / "CHECKPOINT_HASH").read_text().strip() == \
        "9091cb0d5db6cc0a8d233f1667bea78bc69be676b2672f2e47506c453d2a33f0"
    assert sha(k5 / "CHECKPOINT.json") == (k5 / "CHECKPOINT_HASH").read_text().strip() == \
        "8cc6e877d20dac618b24bf9b2eb66ce08c8d6cce58e3cfb9ba1dc0527056b215"
    wt = NS.parents[2]
    for rev, d in (("d9e8f1185c04ee8beb339efff091a073e6ebc21d", "p5y_k1r4_bridge_successor"),
                   ("0cd4e8dd36615971745eb37c00197d735723cc82", "p5y_k1r5_cusum_entry")):
        out = subprocess.run(["git", "-C", str(wt), "diff", "--stat", rev, "--", str(CP / d)], capture_output=True, text=True).stdout
        assert out == "", f"{d} differs from its freeze"


def test_E_identity_provenance_declared():
    p = j(CFG / "IDENTITY_PROVENANCE.json")
    assert p["CELL_PROVENANCE"]["sha256"] == p["value_rebound"]["cells_sha256"] == \
        j(CP / "p5y_k1r4_bridge_successor/config/CHECKPOINT.json")["frozen_artifacts"]["CUSUM_BRIDGE_CELL_TABLE.json"]
    assert set(p["SCIENTIFIC_REGIME_PROVENANCE"]["identity_fields"]) >= {"checkpoint_hash", "obligation_universe_total"}
    assert "NOT claim" in p["SCIENTIFIC_REGIME_PROVENANCE"]["meaning"]


def test_F_qualification_bound_and_complete():
    q = j(NS / "evidence/QUALIFICATION_K1R6.json")
    assert q["verdict"] == "PASS" and q["gates_passed"] == q["gates_total"] == 18
    assert q["controls_passed"] == q["controls_total"] == 25
    assert q["bridge_post_science_acceptance"] == "2/2" and q["post_science_replay"]["NON_GENUINE"] is True
    assert q["genuine_bridge_computation"] is False
    assert q["checkpoint_sha256"] == (CFG / "CHECKPOINT_HASH").read_text().strip()
    names = {c["control"].split()[0] for c in q["controls"]}
    assert {f"G{i}" for i in range(1, 9)} <= names, "Part G controls 1-8 must all be present"
    assert {f"F{i}" for i in range(2, 12)} <= names, "Part F identity controls must all be present"


def test_G_no_genuine_evidence():
    ev = [p.name for p in (NS / "evidence").iterdir() if p.name.startswith(("k1r6_CUSUM", "cell_done"))]
    assert ev == [], ev


if __name__ == "__main__":
    for name, fn in sorted((k, v) for k, v in dict(globals()).items() if k.startswith("test_")):
        check(name, fn)
    print(f"{R.count('PASS')}/{len(R)} tests")
    sys.exit(0 if R.count("PASS") == len(R) else 1)
