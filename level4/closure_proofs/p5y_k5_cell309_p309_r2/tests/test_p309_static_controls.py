"""r2 delta review C10 (and C6): negative controls for QC12 T11-T14, as the D5 tests are for T4/T6/T7/T8.

  python3 tests/test_p309_static_controls.py   -> evidence/fc6/STATIC_CONTROLS.json; exit 0 iff every control holds

The namespace's code/, tests/, verify/ and config/ are copied into a TEST directory under P309_SCRATCH_ROOT.  Each
control applies one literal mutation to that copy (a missing anchor is a FAIL, never a silent pass), runs the static
check's t11-t14 there in-process, and passes iff the check named for it fails; the copy is then restored.  The
unmutated copy must pass all four.  Nothing is written outside the scratch copy and the evidence file; nothing runs
from the copy.
"""
from __future__ import annotations

import datetime
import json
import shutil
import sys
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FNS / "code"))
import p309_env as E  # noqa: E402
import p309_static_check as SC  # noqa: E402

R = {}
QC11_BASE = '    head, _mode = sandbox_base()                 # r2 P6: F after the freeze, HEAD before it (never "HEAD" blindly)\n'
R1_BASE = ('    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True,\n'
           '                          check=True).stdout.strip()\n')
MAIN_PRE = ('    try:\n'
            '        qh = qhost_preflight(("official", "drill"))         # r2 P10: before the attempt directory and RUN START\n'
            '    except (H.HostError, OSError, ValueError, KeyError) as exc:\n'
            '        print(f"QUALIFICATION REFUSED: Q-HOST: {exc}")\n'
            '        return 2\n'
            '    ATT["dir"] = QDIR / "attempt_1"\n'
            '    os.mkdir(ATT["dir"])                                      # exclusive\n')
MAIN_PRE_AFTER = ('    ATT["dir"] = QDIR / "attempt_1"\n'
                  '    os.mkdir(ATT["dir"])                                      # exclusive\n'
                  '    try:\n'
                  '        qh = qhost_preflight(("official", "drill"))\n'
                  '    except (H.HostError, OSError, ValueError, KeyError) as exc:\n'
                  '        print(f"QUALIFICATION REFUSED: Q-HOST: {exc}")\n'
                  '        return 2\n')
MAIN_MON = '    start_qhost_monitor(qh)                                   # r2 P10: continuous Q-HOST sampling (<= 60 s)\n'
MAIN_MIRROR = '    m = mirror(freeze)\n'

# (name, the check that must fail, file, old, new); an old text must occur exactly once
MUTANTS = [
    ("T11a_qc11_harness_reads_real_head", "T11", "tests/test_p309_exactly_once.py", QC11_BASE, R1_BASE),
    ("T11b_guard_harness_bypasses_sandbox_base", "T11", "tests/test_p309_guard.py",
     "    head, _mode = X.sandbox_base()", "    head, _mode = X.D.recorded_freeze(), \"post\""),
    ("T11c_verifier_sandbox_bypasses_its_base_rule", "T11", "verify/scoped_sandbox.py",
     "        self.base_commit, self.base_mode = sandbox_base_commit(src, self.record_rel)",
     "        self.base_commit, self.base_mode = src, \"pre\""),
    ("T12a_guard_forbids_only_r2", "T12", "code/p309_guard.py",
     "_FORBIDDEN_NAMESPACES = (_PROD_NAMESPACE, _PRIOR_NAMESPACE)", "_FORBIDDEN_NAMESPACES = (_PROD_NAMESPACE,)"),
    ("T12b_qc13_drops_the_namespace_check", "T12", "code/p309_qualify.py",
     "r.startswith(D.G._FORBIDDEN_NAMESPACES)", "r.startswith(D.G._PROD_NAMESPACE)"),
    ("T13a_recorded_freeze_changed", "T13", "code/p309_driver.py",
     '        raise Refusal("FREEZE_RECORD", "no freeze record")', '        raise Refusal("FREEZE_RECORD", "none")'),
    ("T13b_read_path_constant_changed", "T13", "code/p309_driver.py",
     'FREEZE_RECORD_REL = NS_REL + "/ledger/FREEZE_RECORD.json"', 'FREEZE_RECORD_REL = NS_REL + "/ledger/FREEZE.json"'),
    ("T14a_main_preflight_after_the_attempt", "T14", "code/p309_qualify.py", MAIN_PRE, MAIN_PRE_AFTER),
    ("T14b_main_refusal_after_the_attempt", "T14", "code/p309_qualify.py", MAIN_MON,
     "    if not qh:\n        return 2\n" + MAIN_MON),
    ("T14c_monitor_started_after_work", "T14", "code/p309_qualify.py", MAIN_MON + MAIN_MIRROR, MAIN_MIRROR + MAIN_MON),
    ("T14d_host_rerun_wrong_modes", "T14", "code/p309_qualify.py", 'qhost_preflight(("host-rerun",))',
     'qhost_preflight(("host-rerun", "official"))'),
    ("T14e_host_rerun_without_preflight", "T14", "code/p309_qualify.py",
     '        qh = qhost_preflight(("host-rerun",))', '        qh = {"cfg": {}}'),
    # follow-up V1: a raise or an exit between the attempt and the final return is a refusal after the attempt
    ("T14f_main_raise_after_the_attempt", "T14", "code/p309_qualify.py", MAIN_MON,
     "    if not qh:\n        raise SystemExit(2)\n" + MAIN_MON),
    ("T14g_main_sys_exit_after_the_attempt", "T14", "code/p309_qualify.py", MAIN_MON,
     "    if not qh:\n        sys.exit(2)\n" + MAIN_MON),
    ("T14h_host_rerun_os_exit_after_the_attempt", "T14", "code/p309_qualify.py",
     "    start_qhost_monitor(qh)                                   # r2 C7: continuous Q-HOST sampling (<= 60 s)\n",
     "    if not qh:\n        os._exit(2)\n"
     "    start_qhost_monitor(qh)                                   # r2 C7: continuous Q-HOST sampling (<= 60 s)\n"),
]


def t(name, ok, got=None):
    R[name] = {"pass": bool(ok), "got": got}
    print(f"[{'PASS' if ok else 'FAIL'}] {name}", flush=True)


def verdicts(root: Path, allow: dict = None) -> dict:
    d11, d12, d13, d14 = SC.t11(root), SC.t12(root, allow), SC.t13(root, allow), SC.t14(root)
    return {"T11": all(v for k, v in d11.items() if k != "stray"), "T12": all(d12.values()),
            "T13": all(v for k, v in d13.items() if k != "changed"), "T14": all(all(v.values()) for v in d14.values())}


def main() -> int:
    copy = E.scratch_dir("static_controls") / "fns_copy"
    if copy.exists():
        shutil.rmtree(copy)
    for sub in ("code", "tests", "verify", "config"):
        shutil.copytree(FNS / sub, copy / sub, ignore=shutil.ignore_patterns("__pycache__"))
    base = verdicts(copy)
    t("S00_unmutated_copy_passes_T11_T14", all(base.values()), base)
    for name, check, rel, old, new in MUTANTS:
        p = copy / rel
        src = p.read_text()
        if src.count(old) != 1:
            t(name, False, f"anchor found {src.count(old)} times in {rel}")
            continue
        p.write_text(src.replace(old, new))
        try:
            v = verdicts(copy)
        finally:
            p.write_text(src)
        t(name, v[check] is False, v)
    allow = json.loads(json.dumps(SC.ALLOW))                  # T12c: the r1 token removed from production_tokens
    import p309_guard as G
    r1 = G._PRIOR_NAMESPACE.rstrip("/")                      # r1's namespace, as the guard names it (no literal here)
    allow["production_tokens"] = [x for x in allow["production_tokens"] if x != r1]
    v = verdicts(copy, allow)
    t("T12c_production_tokens_lack_r1", v["T12"] is False and r1 in SC.ALLOW["production_tokens"], v)
    allow = json.loads(json.dumps(SC.ALLOW))                  # T13c: a constant pin removed from the config
    allow["production_read_path_constant_pins"]["entries"] = allow["production_read_path_constant_pins"]["entries"][1:]
    v = verdicts(copy, allow)
    t("T13c_constant_pin_missing", v["T13"] is False, v)
    t("S99_copy_restored", verdicts(copy) == base)
    shutil.rmtree(copy)
    return 0 if all(x["pass"] for x in R.values()) else 1


if __name__ == "__main__":
    E.log("tests/test_p309_static_controls.py", "r2 QC12 T11-T14 negative controls (C10)", klass="GOVERNANCE",
          notes="mutations only in a scratch copy; static (AST) checks only")
    rc = main()
    out = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "all_pass": rc == 0,
           "controls": len(R), "results": R}
    (E.evidence_dir("fc6") / "STATIC_CONTROLS.json").write_text(json.dumps(out, indent=1, sort_keys=True,
                                                                           default=str) + "\n")
    sys.exit(rc)
