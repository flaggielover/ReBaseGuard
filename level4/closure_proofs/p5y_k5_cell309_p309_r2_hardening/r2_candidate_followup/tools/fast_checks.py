"""Fast r2 checks on a fresh scratch clone of one commit (result-free; nothing pushed; the clone has no remote).

usage: fast_checks.py <session repo> <commit> <work dir (new)> <out.json>
Runs, from the clone's r2 namespace with P309_SCRATCH_ROOT / P309_EVIDENCE_DIR / TMPDIR in the work dir:
  code/p309_static_check.py (QC12), tests/test_p309_static_controls.py (incl. T14a), code/p309_scan_pins.py --list,
  tests/test_p309_scan_allowance.py; then the generators in the real-freeze order and code/p309_placeholder_check.py
  (no placeholder marker in any frozen file, including the new governance supplement).
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

repo, commit, work, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
work.mkdir()
clone = work / "clone"
NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2"
subprocess.run(["git", "clone", "-q", "--no-local", "--no-checkout", str(repo), str(clone)], check=True)
subprocess.run(["git", "-C", str(clone), "checkout", "-q", commit], check=True)
env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTHON", "P309_"))}
env.update(P309_SCRATCH_ROOT=str(work / "scratch"), P309_EVIDENCE_DIR=str(work / "evidence"), TMPDIR=str(work / "tmp"))
for d in ("scratch", "evidence", "tmp"):
    (work / d).mkdir()
fns = clone / NS
steps = [("QC12_static_check", ["code/p309_static_check.py"]),
         ("static_controls", ["tests/test_p309_static_controls.py"]),
         ("scan_pins_list", ["code/p309_scan_pins.py", "--list"]),
         ("scan_allowance_test", ["tests/test_p309_scan_allowance.py"]),
         ("make_freeze_params", ["code/make_freeze_params.py"]),
         ("make_freeze_manifest", ["code/make_freeze_manifest.py"]),
         ("placeholder_check", ["code/p309_placeholder_check.py"]),
         ("manifest_check", ["code/make_freeze_manifest.py", "--check"])]
res = {"commit": subprocess.run(["git", "-C", str(clone), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
       "steps": {}}
for name, argv in steps:
    t0 = time.time()
    r = subprocess.run([sys.executable, "-B", *argv], cwd=str(fns), capture_output=True, text=True, env=env, timeout=3600)
    res["steps"][name] = {"rc": r.returncode, "wall_s": round(time.time() - t0, 1),
                          "tail": (r.stdout + r.stderr)[-1500:]}
    print(f"{name}: rc={r.returncode} ({res['steps'][name]['wall_s']} s)", flush=True)
res["all_rc0"] = all(s["rc"] == 0 for s in res["steps"].values())
out.write_text(json.dumps(res, indent=1) + "\n")
print("all rc 0:", res["all_rc0"])
