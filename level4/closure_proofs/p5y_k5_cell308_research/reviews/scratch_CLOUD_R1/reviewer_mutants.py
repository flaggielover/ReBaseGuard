"""Reviewer mutants (brief 59). Each mutant is applied to a COPY of lx_platform.py (./base) in a temporary directory
under this scratch dir; the UNCHANGED repository test suite is run against it (LX_PLATFORM_DIR), with bytecode writing
disabled. Nothing in the repository is written. Usage: python3 -B reviewer_mutants.py"""
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
    ("R01", "unreadable Battery status skipped (a failed read can yield AC)",
     [("            if not st:\n                return None\n", "            if not st:\n                continue\n")]),
    ("R02", "host attestation accepted when the 'accepted' key is merely present (e.g. 'REJECTED')",
     [('and host_attestation.get("accepted")) else UNKNOWN', 'and "accepted" in host_attestation) else UNKNOWN')]),
    ("R03", "durable_write never fsyncs the data",
     [("        os.fsync(fd)\n", "        pass\n")]),
    ("R04", "suspend / pause tolerance raised from 2 s to 25 s",
     [("SLEEP_GAP_TOL_NS = 2_000_000_000 ", "SLEEP_GAP_TOL_NS = 25_000_000_000")]),
    ("R05", "hidden name allow-list for the Cloud session controller in busy_processes",
     [("        if pid in own_pids or ppid in own_pids:\n",
       "        if pid in own_pids or ppid in own_pids or comm in (\"claude\", \"environment-man\", \"process_api\"):\n")]),
    ("R06", "libpython_sha256 and glibc dropped from PIN_KEYS",
     [('"libpython", "libpython_sha256", "python_sys_version"', '"libpython", "python_sys_version"'),
      ('"os_version", "kernel_release", "machine", "glibc")', '"os_version", "kernel_release", "machine")')]),
    ("R07", "L-ID-1 widened: stopped (T/t) and uninterruptible (D) tasks read as DEAD",
     [('if st.get("state") in ("Z", "X"):', 'if st.get("state") in ("Z", "X", "T", "t", "D"):')]),
    ("R08", "durable_write never fsyncs the directory after the rename",
     [("        os.fsync(dfd)\n", "        pass\n")]),
    ("R09", "maximum sample spacing raised from 180 s to 390 s",
     [("MAX_SAMPLE_GAP_S = 180 ", "MAX_SAMPLE_GAP_S = 390 ")]),
    ("R10", "assess checks power only at start and end, not at the samples",
     [('    power = [x.get("power") if isinstance(x, dict) else None for x in seq]',
       '    power = [x.get("power") if isinstance(x, dict) else None for x in (start, end)]')]),
]


def run_suite(libdir):
    env = dict(os.environ, LX_PLATFORM_DIR=str(libdir), PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", str(TESTS)], cwd=TESTS.parent,
                       env=env, capture_output=True, text=True, timeout=600)
    return p.returncode, (p.stderr.strip().splitlines() or [""])[-1]


def main():
    src = SRC.read_text()
    rows = []
    for mid, what, edits in MUTANTS:
        new = src
        ok = True
        for old, rep in edits:
            if new.count(old) != 1:
                ok = False
                break
            new = new.replace(old, rep)
        if not ok:
            rows.append({"id": mid, "property": what, "status": "NOT_APPLIED"})
            continue
        diff = "".join(difflib.unified_diff(src.splitlines(True), new.splitlines(True), "lx_platform.py",
                                            f"lx_platform.py ({mid})", n=0))
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            Path(d, "lx_platform.py").write_text(new)
            rc, tail = run_suite(d)
        rows.append({"id": mid, "property": what, "status": "KILLED" if rc != 0 else "SURVIVED", "suite_tail": tail,
                     "diff": diff})
    rc, tail = run_suite(SRC.parent)
    print(json.dumps({"unmutated_suite": "PASS" if rc == 0 else "FAIL", "unmutated_tail": tail,
                      "killed": sum(r["status"] == "KILLED" for r in rows), "total": len(rows), "mutants": rows},
                     indent=1))


if __name__ == "__main__":
    main()
