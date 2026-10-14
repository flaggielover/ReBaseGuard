"""Reviewer mutants (brief 60) against a COPY of lx_platform.py revision 2 (./base, sha256 7561c364...). Each mutant
is written to a temporary directory under this scratch dir; the UNCHANGED repository suite is run against it via
LX_PLATFORM_DIR with -B. Nothing in the repository is written. Usage: python3 -B reviewer60_mutants.py"""
import difflib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "base" / "lx_platform.py"
TESTS = Path("/home/user/ReBaseGuard/level4/closure_proofs/p5y_k5_cell308_research/streams/CLOUD_R1_LINUX_DEV/tests")

MUTANTS = [
    ("X01", "proc_view_complete: /proc 'subset=' mount option no longer refused",
     [('return not ("hidepid=" in opts or "subset=" in opts)', 'return not ("hidepid=" in opts)')]),
    ("X02", "proc_view_complete: no /proc mount line found counts as a complete view",
     [("            return not (\"hidepid=\" in opts or \"subset=\" in opts)\n    return None\n",
       "            return not (\"hidepid=\" in opts or \"subset=\" in opts)\n    return True\n")]),
    ("X03", "auto_update_settings: an unreadable /sys/kernel/livepatch counts as 'no livepatch applied'",
     [("not cloud and livepatch == [])", "not cloud and livepatch in ([], None))")]),
    ("X04", "assess: K' 'monotonic advanced more than boottime' channel removed",
     [("            elif db - dm < -SLEEP_GAP_TOL_NS:\n                reasons.append(\"AMBIGUOUS: K' monotonic advanced more than boottime\")\n",
       "")]),
    ("X05", "durable_write: read-back verification removed",
     [("    if got != want:\n        raise OSError", "    if False:\n        raise OSError")]),
    ("X06", "assess: absent samples (None) no longer AMBIGUOUS",
     [("    if not isinstance(samples, list):\n        reasons.append(\"AMBIGUOUS: samples absent\")\n", "")]),
    ("X07", "launched_by_systemd: a transient .scope (e.g. systemd-run --scope from an agent session) accepted as the unit",
     [('if last.startswith(prefix) and last.endswith(".service"):',
       'if last.startswith(prefix) and last.endswith((".service", ".scope")):')]),
    ("X08", "v1 'unlimited' sentinel lowered to 1 GiB (real limits >= 1 GiB read as no limit)",
     [("UNLIMITED_CGROUP_V1 = 2 ** 62 ", "UNLIMITED_CGROUP_V1 = 2 ** 30 ")]),
    ("X09", "pins: an interpreter whose dpkg owner is unknown silently drops out of the package pin",
     [('    return (owner or "<unknown-interpreter-package>", f"libpython{v}-stdlib")',
       '    return tuple(x for x in (owner, f"libpython{v}-stdlib") if x)')]),
    ("X10", "identity_state: ESRCH proves death even when the reader's namespaces could not be read",
     [('    ns = current_ns if current_ns is not None else {"pidns": ns_inode("pid"), "timens": ns_inode("time")}\n'
       '    for k in ("pidns", "timens"):\n        if ident.get(k) is not None and ns.get(k) != ident[k]:\n',
       '    ns = current_ns if current_ns is not None else {"pidns": ns_inode("pid"), "timens": ns_inode("time")}\n'
       '    for k in ("pidns", "timens"):\n        if ident.get(k) is not None and ns.get(k) is not None and ns.get(k) != ident[k]:\n')]),
    ("X11", "power_source: Mains 'online' unreadable treated as offline (not UNKNOWN)",
     [('            if on not in ("0", "1"):\n                return None\n',
       '            if on not in ("0", "1"):\n                on = "0"\n')]),
    ("X12", "pin_mismatches: an EMPTY dict pin (no mapped objects / no packages) counts as readable",
     [("isinstance(v, dict) and (not v or any(x is None for x in v.values()))",
       "isinstance(v, dict) and any(x is None for x in v.values())")]),
]


def run_suite(libdir):
    env = dict(os.environ, LX_PLATFORM_DIR=str(libdir), PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", str(TESTS)], cwd=TESTS.parent,
                          env=env, capture_output=True, text=True, timeout=900)


def main():
    src = SRC.read_text()
    rows = []
    base = run_suite(SRC.parent)
    rows.append({"id": "BASE", "status": "PASS" if base.returncode == 0 else "FAIL",
                 "tail": base.stderr.strip().splitlines()[-1]})
    for mid, what, edits in MUTANTS:
        m, ok = src, True
        for old, new in edits:
            if m.count(old) != 1:
                ok = False
                break
            m = m.replace(old, new)
        if not ok:
            rows.append({"id": mid, "what": what, "status": "NOT_APPLIED"})
            continue
        diff = "".join(difflib.unified_diff(src.splitlines(True), m.splitlines(True), "rev2", mid, n=0))
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            Path(d, "lx_platform.py").write_text(m)
            p = run_suite(d)
        fails = [ln for ln in p.stderr.splitlines() if ln.startswith(("FAIL:", "ERROR:"))]
        rows.append({"id": mid, "what": what, "status": "KILLED" if p.returncode else "SURVIVED",
                     "tail": p.stderr.strip().splitlines()[-1], "failing": fails, "diff": diff})
    print(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
