"""T2 NEGATIVE CONTROL for the K1 binding checkpoint.

Validation harness, NOT part of the frozen rule set: it is deliberately
excluded from manifests/source_manifest.json, so it cannot alter
CHECKPOINT_HASH and cannot be mistaken for a binding rule.

It builds a sandbox (real copy of this namespace, symlinks for every sibling,
inside the repo so `git -C` still discovers the object database), applies one
deliberate checkpoint violation at a time, and asserts the design-validation
suite FAILS each time. A gate that never fails is not a gate -- the Gate-2D
defect was exactly an acceptance precondition that was computed but never
branched on.

Executes no certified numerics. Non-result-bearing.
"""
import json, pathlib, shutil, subprocess, sys, tempfile

SRC = pathlib.Path("/Users/suzhe/ReBaseGuard/level4/closure_proofs/p5y_k1_binding_campaign")

def mut_m(ns):        # narrow the frozen m set
    p = ns/"CHECKPOINT.json"; d = json.loads(p.read_text())
    d["scope"]["m_values"] = [1,2,3]; p.write_text(json.dumps(d, indent=1))

def mut_self_award(ns):
    p = ns/"config/final_verdict_spec.json"; d = json.loads(p.read_text())
    d["verdicts"]["K1_CLOSED"]["producer_may_self_award"] = True
    p.write_text(json.dumps(d, indent=1))

def mut_close_p5(ns):
    p = ns/"config/final_verdict_spec.json"; d = json.loads(p.read_text())
    d["downstream_effects"]["if_K1_CLOSED"]["auto_close_P5"] = True
    p.write_text(json.dumps(d, indent=1))

def mut_cap(ns):      # adopt the programme worst as the cap
    p = ns/"CHECKPOINT.json"; d = json.loads(p.read_text())
    d["cpu"]["model"]["bands_cpu_hours"]["hard_cpu_cap"] = 4597
    d["cpu"]["HARD_CPU_CAP_CPU_HOURS"] = 4597
    p.write_text(json.dumps(d, indent=1))

def mut_untighten(ns):  # revert the m=1 budget tightening to Gate-2E's m=2 value
    p = ns/"config/budget_ledger.json"; d = json.loads(p.read_text())
    d["reference_cell"]["w_panel_max"] = d["reference_cell"]["gate2e_w_panel_max"]
    d["reference_cell"]["tightening_factor_vs_gate2e"] = 1.0
    p.write_text(json.dumps(d, indent=1))

def mut_assembly(ns):   # corrupt one m=5 assembly coefficient
    p = ns/"config/production_dag.json"; d = json.loads(p.read_text())
    d["assembly"]["per_m"]["5"]["finite"]["K^3 S_0"] = "1/21"
    p.write_text(json.dumps(d, indent=1))

def mut_redistribute(ns):
    p = ns/"config/budget_ledger.json"; d = json.loads(p.read_text())
    d["redistribution_allowed"] = True; p.write_text(json.dumps(d, indent=1))

def mut_production(ns):  # a result-bearing artifact appears
    (ns/"results/cells_sr.jsonl").write_text('{"cell":0,"R":1.9}\n')

def mut_escalate(ns):
    p = ns/"config/precision_policy.json"; d = json.loads(p.read_text())
    d["PRECISION_ESCALATION_ALLOWED"] = True; p.write_text(json.dumps(d, indent=1))

def mut_hash(ns):        # forge the checkpoint hash
    p = ns/"manifests/CHECKPOINT_HASH.json"; d = json.loads(p.read_text())
    d["CHECKPOINT_HASH"] = "0"*64; p.write_text(json.dumps(d, indent=1))

def mut_reinterpret(ns): # rewrite a failed gate as a pass
    p = ns/"CHECKPOINT.json"; d = json.loads(p.read_text())
    d["inherited_state"]["P5Y_GATE2E"] = "SR_METRIC_PASS"
    p.write_text(json.dumps(d, indent=1))

def mut_ceiling(ns):     # revert to the pilot-era complexity ceiling
    p = ns/"config/complexity_guard.json"; d = json.loads(p.read_text())
    d["PRODUCTION_COMPLEXITY_CEILING"] = 100000; p.write_text(json.dumps(d, indent=1))

MUTS = [("narrow the frozen m set", mut_m),
        ("producer self-awards K1_CLOSED", mut_self_award),
        ("K1_CLOSED auto-closes P5", mut_close_p5),
        ("adopt programme worst 4597 as the cap", mut_cap),
        ("revert the m=1 budget tightening", mut_untighten),
        ("corrupt an m=5 assembly coefficient", mut_assembly),
        ("allow budget redistribution", mut_redistribute),
        ("a production result exists at T2", mut_production),
        ("allow precision escalation", mut_escalate),
        ("forge the checkpoint hash", mut_hash),
        ("reinterpret Gate-2E as PASS", mut_reinterpret),
        ("revert to the pilot-era ceiling 100000", mut_ceiling)]

def run(ns):
    r = subprocess.run([sys.executable, str(ns/"tests/test_k1_checkpoint_design.py")],
                       capture_output=True, text=True)
    return r.returncode

REPO = pathlib.Path("/Users/suzhe/ReBaseGuard")
SANDBOX = REPO / ".negctl_tmp"      # inside the repo so `git -C` discovers it

def make_sandbox(dst: pathlib.Path):
    """Real copy of the campaign namespace; symlinks for every sibling."""
    cp = dst / "level4" / "closure_proofs"
    cp.mkdir(parents=True, exist_ok=True)
    for child in SRC.parent.iterdir():
        if child.name == SRC.name:
            continue
        (cp / child.name).symlink_to(child)
    shutil.copytree(SRC, cp / SRC.name)
    return cp / SRC.name

shutil.rmtree(SANDBOX, ignore_errors=True)
SANDBOX.mkdir()
ns0 = make_sandbox(SANDBOX / "base")
ok = run(ns0)
print(f"{'baseline (unmutated)':48s} rc={ok}  " +
      ("PASS as expected" if ok == 0 else "BASELINE BROKEN"))
allgood = ok == 0
for i, (name, fn) in enumerate(MUTS):
    ns = make_sandbox(SANDBOX / f"m{i}")
    fn(ns)
    rc = run(ns)
    caught = rc != 0
    allgood &= caught
    print(f"{name:48s} rc={rc}  " + ("CAUGHT" if caught else "*** NOT CAUGHT ***"))
shutil.rmtree(SANDBOX, ignore_errors=True)
print("\nNEGATIVE CONTROL:",
      "PASS -- every violation is detected" if allgood else "FAIL")
sys.exit(0 if allgood else 1)
