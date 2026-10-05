"""Extend tests/test_r2h_fsprobe.py with the SF1-A cases (F14, F15, M06) and labels s1a / pre_s1a / pre_s1.

usage: patch_fsprobe_tests.py <path to test_r2h_fsprobe.py>
"""
import sys
from pathlib import Path

p = Path(sys.argv[1])
s = p.read_text()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:80], s.count(old))
    s = s.replace(old, new)


# docstring
rep('''M01-M05  integration: the real main() / host_rerun() in the replica, run in a child process:''',
    '''F14-F15  SF1-A unit tests: a ledger that cannot be opened for appending (F14), a missing ledger (F15).
M01-M06  integration: the real main() / host_rerun() in the replica, run in a child process:''')
rep('''         M05 host_rerun with hard links unsupported: refused before HOST RERUN START.
Label s1: every test must pass.''',
    '''         M05 host_rerun with hard links unsupported: refused before HOST RERUN START.
         M06 (SF1-A) a ledger that cannot be appended to (the fault is injected both in the runner's os.open and
             in the ledger writer's Path.open): refused before Q-HOST, the attempt directory and RUN START.
Labels: s1a (the SF1-A runner): every test must pass.  pre_s1a (S1 runner without SF1-A): F01-F13 and M01-M05 pass,
F14, F15 and M06 fail (they discriminate; M06 records the attempt being consumed).  pre_s1 (before S1): see below.
Label s1 (historical, before SF1-A existed): every S1 test must pass.''')
rep('UNIT = [f"F{i:02d}" for i in range(1, 14)]\nINTEG = ["M01", "M02", "M03", "M04", "M05"]',
    'UNIT = [f"F{i:02d}" for i in range(1, 14)]\nINTEG = ["M01", "M02", "M03", "M04", "M05"]\n'
    'SF1A = ["F14", "F15", "M06"]                                       # the SF1-A cases')
# fault: a ledger that cannot be opened for appending
rep('''    def open(self, path, flags, mode=0o777, **kw):
        if "no_excl" in self.faults''',
    '''    def open(self, path, flags, mode=0o777, **kw):
        if ("ledger_noappend" in self.faults and str(path).endswith(".jsonl") and flags & self.real.O_APPEND
                and flags & (self.real.O_WRONLY | self.real.O_RDWR)):
            raise PermissionError(errno.EACCES, "Permission denied (injected: ledger not appendable)")
        if "no_excl" in self.faults''')
# unit cases
rep('''    case("F13", expect("F13", {"enospc"}, "write", errno.ENOSPC))''',
    '''    case("F13", expect("F13", {"enospc"}, "write", errno.ENOSPC))
    case("F14", expect("F14", {"ledger_noappend"}, "ledger appendability", errno.EACCES))

    def f15():
        saved15 = Q.E.Q.EXPOSURE_LEDGER
        Q.E.Q.EXPOSURE_LEDGER = led_dir / "MISSING_LEDGER.jsonl"
        try:
            d, out, _ = probe("f15")
        finally:
            Q.E.Q.EXPOSURE_LEDGER = saved15
        assert any("ledger appendability (MISSING_LEDGER.jsonl" in p and f"errno {errno.ENOENT}" in p for p in out), out
        assert left(d) == [], f"the probe left {left(d)}"
        assert not (led_dir / "MISSING_LEDGER.jsonl").exists(), "the probe created a ledger"

    case("F15", f15)''')
# child: M06 faults in os and in the ledger writer
rep('''    faults = {"M02": {"no_link"}, "M03": {"no_dir_fsync"}, "M05": {"no_link"}}.get(case, set())
    Q.os = Faulty(real_os, faults)''',
    '''    faults = {"M02": {"no_link"}, "M03": {"no_dir_fsync"}, "M05": {"no_link"},
              "M06": {"ledger_noappend"}}.get(case, set())
    Q.os = Faulty(real_os, faults)
    if case == "M06":                       # the same fault for the ledger writer (pathlib, outside the runner's os)
        import pathlib
        real_path_open = pathlib.Path.open

        def path_open(self, mode="r", *a, **kw):
            if self.name.endswith(".jsonl") and self.parent.name == "ledger" and any(c in mode for c in "aw+"):
                raise PermissionError(errno.EACCES, "Permission denied (injected: ledger not appendable)")
            return real_path_open(self, mode, *a, **kw)
        pathlib.Path.open = path_open''')
# integration M06
rep('''                          and not res["M05"]["probe_left"])
    reset()
    return res''',
    '''                          and not res["M05"]["probe_left"])
    # M06 (SF1-A): a ledger that cannot be appended to -> refused before Q-HOST, the attempt directory and RUN START
    reset()
    before = ledger.read_bytes()
    r = run("M06")
    refusal = [l for l in r.stdout.splitlines() if "REFUSED" in l]
    res["M06"] = {"rc": r.returncode, "refusal": refusal[:1], "preflight_called": "PREFLIGHT_CALLED" in r.stdout,
                  "attempt_dir": (qdir / "attempt_1").exists(), "run_start_lines": starts(),
                  "qualification_entries": sorted(p.name for p in qdir.iterdir()) if qdir.exists() else None,
                  "ledger_unchanged": ledger.read_bytes() == before, "probe_left": probe_left(),
                  "stderr_tail": r.stderr[-400:]}
    res["M06"]["pass"] = (r.returncode == 2 and bool(refusal) and "filesystem probe (S1)" in refusal[0]
                          and "ledger appendability" in refusal[0] and not res["M06"]["preflight_called"]
                          and not res["M06"]["attempt_dir"] and starts() == 0 and res["M06"]["ledger_unchanged"]
                          and res["M06"]["qualification_entries"] == [] and not res["M06"]["probe_left"])
    reset()
    return res''')
# expectations
rep('''    if a.label == "s1":
        ok = all(v["pass"] for v in results.values())
        expectation = "every test passes"
    else:''',
    '''    s1_ids = UNIT + INTEG
    if a.label == "s1a":
        ok = all(v["pass"] for v in results.values())
        expectation = "every test passes (S1 and SF1-A)"
    elif a.label == "pre_s1a":
        ok = all(results[k]["pass"] for k in s1_ids) and all(not results[k]["pass"] for k in SF1A)
        expectation = ("the S1 tests pass and the SF1-A tests fail on the runner without SF1-A: the SF1-A tests "
                       "discriminate")
    elif a.label == "s1":
        ok = all(results[k]["pass"] for k in s1_ids)
        expectation = "every S1 test passes"
    else:''')
p.write_text(s)
print("patched")
