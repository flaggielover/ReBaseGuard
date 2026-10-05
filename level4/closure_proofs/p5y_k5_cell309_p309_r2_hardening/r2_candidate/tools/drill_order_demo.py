"""F-DRILL-ORDER demonstration (result-free, scratch clones only).

usage: drill_order_demo.py <session repo> <r2 commit> <work dir (new)> <out.json>

For each order -- the r2 drill's current order (manifest, params, placeholder) and the corrected order (params,
manifest, placeholder) -- in a fresh no-local clone of the r2 commit: run r2's own unmodified generators exactly as
make_topology does (python -B <script>, cwd = clone), then run the check the qualification runner makes before any
launch (`make_freeze_manifest.py --check`), and report the manifest's pin count and whether it pins the parameter
file freeze/P309_FREEZE.json.  Also reports what r1's real recorded freeze manifest pins.  Nothing is committed or
pushed; no target code is imported or run.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

repo, commit, work, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2"
R1NS = "level4/closure_proofs/p5y_k5_cell309_p309_r1"
work.mkdir(parents=False)
ORDERS = {"current_r2": ["make_freeze_manifest.py", "make_freeze_params.py", "p309_placeholder_check.py"],
          "corrected": ["make_freeze_params.py", "make_freeze_manifest.py", "p309_placeholder_check.py"]}


def sh(*a, cwd=None, env=None):
    return subprocess.run(list(a), cwd=cwd, capture_output=True, text=True, env=env)


res = {"r2_commit": commit, "orders": {}}
for name, order in ORDERS.items():
    clone = work / name
    assert sh("git", "clone", "-q", "--no-local", "--no-checkout", str(repo), str(clone)).returncode == 0
    assert sh("git", "-C", str(clone), "checkout", "-q", commit).returncode == 0
    scratch = work / (name + "_scratch")
    scratch.mkdir()
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["P309_SCRATCH_ROOT"] = str(scratch)
    env["P309_EVIDENCE_DIR"] = str(scratch / "evidence")
    steps = []
    for script in order:
        r = sh(sys.executable, "-B", str(clone / NS / "code" / script), cwd=str(clone), env=env)
        steps.append({"script": script, "rc": r.returncode, "tail": (r.stdout + r.stderr)[-300:]})
    chk = sh(sys.executable, "-B", str(clone / NS / "code" / "make_freeze_manifest.py"), "--check", cwd=str(clone),
             env=env)
    man = json.loads((clone / NS / "freeze" / "P309_FREEZE_MANIFEST.json").read_text())
    pins = [p["path"] for p in man.get("pins", man.get("code_pins", []))] if isinstance(man.get("pins", None), list) \
        else None
    text = json.dumps(man)
    res["orders"][name] = {
        "order": order, "steps": steps,
        "manifest_check_rc": chk.returncode, "manifest_check_tail": (chk.stdout + chk.stderr)[-400:],
        "manifest_pins_params_file": (NS + "/freeze/P309_FREEZE.json") in text,
        "manifest_path_count": text.count('"path"'),
        "params_file_exists": (clone / NS / "freeze" / "P309_FREEZE.json").exists(),
    }
# r1's real freeze manifest (the recorded F of r1): does it pin the parameter file?
r1m = sh("git", "-C", str(repo), "show", f"{commit}:{R1NS}/freeze/P309_FREEZE_MANIFEST.json")
if r1m.returncode == 0:
    res["r1_real_manifest"] = {"pins_params_file": (R1NS + "/freeze/P309_FREEZE.json") in r1m.stdout,
                               "path_count": r1m.stdout.count('"path"'),
                               "sha256": hashlib.sha256(r1m.stdout.encode()).hexdigest()}
out.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
for k, v in res["orders"].items():
    print(k, [s["rc"] for s in v["steps"]], "check rc", v["manifest_check_rc"], "pins params", v["manifest_pins_params_file"],
          "paths", v["manifest_path_count"], "|", v["manifest_check_tail"].strip().splitlines()[-1:] )
print("r1", res.get("r1_real_manifest"))
