"""Self-test of the packet's two read-only tools (scratch only).
usage: run_selftest.py <T dir with clone/ = a fresh clone of origin r2 at 501f48cb> <tools dir> <fixture script> <out.json>
Every case starts from a pristine copy of the clone.  Expected outcomes are fixed in EXPECT before anything runs."""
import json, os, shutil, subprocess, sys

T, tools, fx, out = sys.argv[1:5]
clone, pristine = os.path.join(T, "clone"), os.path.join(T, "pristine")
shutil.rmtree(pristine, ignore_errors=True)
shutil.copytree(clone, pristine, symlinks=True)
PY = sys.executable
EXPECT = {
    "prelaunch_container": {"failed": ["C25_no_p309_unit_loaded"]},          # no systemd in this container
    "prelaunch_no_remote": {"failed": ["C13_origin_r2_is_501f48cb", "C14_no_protected_ref_on_origin",
                                       "C25_no_p309_unit_loaded"]},
    "prelaunch_dirty": {"failed": ["C04_clone_clean_incl_untracked", "C16_scratch_empty", "C25_no_p309_unit_loaded"]},
    "drill_pass": {"classification": "PASS", "failed": []},
    "drill_fail_gate": {"classification": "FAIL"},
    "drill_extra_file": {"classification": "FAIL", "must_fail": ["V22_clone_changes_only_this_drill"]},
    "drill_incident": {"classification": "INCIDENT"},
    "drill_interrupted": {"classification": "INTERRUPTED"},
    "drill_corrupt_report": {"classification": "FAIL", "must_fail": ["V02_schema_tier_pass"]},
}


def fresh():
    shutil.rmtree(clone)
    shutil.copytree(pristine, clone, symlinks=True)
    for d in ("run", "check"):
        shutil.rmtree(os.path.join(T, d), ignore_errors=True)


def run(argv):
    p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return p.returncode, json.loads(p.stdout) if p.stdout.strip().startswith("{") else {"raw": p.stdout + p.stderr}


res = {}
pre = [PY, "-B", os.path.join(tools, "prelaunch_readonly_check_8d.py"), "--clone", clone, "--host-config",
       os.path.join(T, "host_config.json"), "--scratch", os.path.join(T, "run"), "--check-record",
       os.path.join(T, "check", "launch_x.json"), "--verdict", os.path.join(T, "verdict.json")]
for case, extra, dirty in (("prelaunch_container", ["--remote"], False), ("prelaunch_no_remote", [], False),
                           ("prelaunch_dirty", ["--remote"], True)):
    fresh()
    subprocess.run([PY, "-B", fx, T, "prelaunch"], check=True)
    if dirty:
        open(os.path.join(clone, "stray_untracked"), "w").write("x\n")
        open(os.path.join(T, "run", "leftover"), "w").write("x\n")
    st0 = subprocess.run(["git", "-C", clone, "status", "--porcelain", "--untracked-files=all"], stdout=subprocess.PIPE,
                         universal_newlines=True).stdout
    rc, d = run(pre + extra)
    st1 = subprocess.run(["git", "-C", clone, "status", "--porcelain", "--untracked-files=all"], stdout=subprocess.PIPE,
                         universal_newlines=True).stdout
    failed = sorted(k for k, v in d.get("checks", {}).items() if not v)
    res[case] = {"rc": rc, "n_checks": len(d.get("checks", {})), "failed": failed, "clone_unchanged_by_tool": st0 == st1,
                 "ok": failed == EXPECT[case]["failed"] and st0 == st1 and rc == 1}
for case in ("drill_pass", "drill_fail_gate", "drill_extra_file", "drill_incident", "drill_interrupted",
             "drill_corrupt_report"):
    fresh()
    subprocess.run([PY, "-B", fx, T, "drill_pass" if case == "drill_corrupt_report" else case, "--fake-imds"],
                   check=True, stdout=subprocess.DEVNULL)
    if case == "drill_corrupt_report":                 # a torn report: the validator must classify, not crash
        rp = os.path.join(clone, "level4/closure_proofs/p5y_k5_cell309_p309_r2/evidence/drill/20261012T080102Z",
                          "DRILL_REPORT.json")
        open(rp, "w").write(open(rp).read()[:500])
    st0 = subprocess.run(["git", "-C", clone, "status", "--porcelain", "--untracked-files=all"], stdout=subprocess.PIPE,
                         universal_newlines=True).stdout
    rc, d = run([PY, "-B", os.path.join(tools, "validate_worker_drill_8d.py"), "--clone", clone, "--stamp",
                 "20261012T080102Z", "--launch-record", os.path.join(T, "launch_rec.json"), "--verdict",
                 os.path.join(T, "verdict.json"), "--prelaunch", os.path.join(T, "prelaunch_pass.json")])
    st1 = subprocess.run(["git", "-C", clone, "status", "--porcelain", "--untracked-files=all"], stdout=subprocess.PIPE,
                         universal_newlines=True).stdout
    e = EXPECT[case]
    ok = d.get("classification") == e["classification"] and st0 == st1 and (rc == 0) == (e["classification"] == "PASS")
    if "failed" in e:
        ok = ok and d.get("failed") == e["failed"]
    if "must_fail" in e:
        ok = ok and all(k in (d.get("failed") or []) for k in e["must_fail"])
    res[case] = {"rc": rc, "classification": d.get("classification"), "n_checks": len(d.get("checks", {})),
                 "failed": d.get("failed"), "incident": d.get("incident"), "clone_unchanged_by_tool": st0 == st1,
                 "ok": ok}
fresh()
summary = {"schema": "P309_R2_PACKET_TOOL_SELFTEST/1", "expect": EXPECT, "results": res,
           "all_ok": all(v["ok"] for v in res.values()),
           "note": "run in the coordinating Cloud Session on a fresh clone of origin r2 (501f48cb); the drill cases use "
                   "synthetic worker-shaped fixtures built from the committed cloud-tier report 20261002T052554Z; "
                   "nothing here is host evidence"}
open(out, "w").write(json.dumps(summary, indent=1, sort_keys=True) + "\n")
print(json.dumps({k: (v["ok"], v.get("classification"), v["failed"]) for k, v in res.items()}, indent=1), "\nall_ok:",
      summary["all_ok"])
