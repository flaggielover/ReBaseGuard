"""Mutation harness for the DEV-ONLY lx_platform tests (revision 2). Each mutant weakens one fail-closed property in a
temporary copy of lx_platform.py; the unchanged test suite must FAIL against every mutant ("killed"). A surviving
mutant means a property is untested. M01-M32 are the coordinator's; R01-R10 are review 59's mutants (reviews/
scratch_CLOUD_R1/reviewer_mutants.py), re-anchored to revision 2 with the same weakening. Target-free; nothing outside
a temporary directory is written.

usage: python3 tests/run_mutants.py [out.json]       (from streams/CLOUD_R1_LINUX_DEV)
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "lx_platform.py"

# (id, property weakened, [(old, new), ...]) -- each old text must occur exactly once
MUTANTS = [
    ("M01", "failed boot-id read treated as a reboot (DEAD)",
     [("    if cur is None:\n        return UNKNOWN\n", "    if cur is None:\n        return DEAD\n")]),
    ("M02", "unreadable /proc/<pid>/stat treated as DEAD",
     [("    if st is None:\n        return UNKNOWN\n    if st.get(\"state\")",
       "    if st is None:\n        return DEAD\n    if st.get(\"state\")")]),
    ("M03", "incomplete identity record reported ALIVE",
     [("    return ALIVE if complete else UNKNOWN", "    return ALIVE")]),
    ("M04", "zombie read as DEAD again (the withdrawn L-ID-1)",
     [('if st.get("state") in ("Z", "X"):\n        return UNKNOWN', 'if st.get("state") in ("Z", "X"):\n        return DEAD')]),
    ("M05", "pid reuse (other starttime) not detected",
     [('st["starttime"] != ident["starttime_ticks"]', 'False')]),
    ("M06", "no power supply exposed read as AC",
     [('    if not entries:\n        return "ABSENT"\n', '    if not entries:\n        return AC\n')]),
    ("M07", "unreadable cgroup limit skipped",
     [('        if lvl["limit"] is None:\n            return None\n', '        if lvl["limit"] is None:\n            continue\n')]),
    ("M08", "missing journal channel ignored in assess",
     [("    if not isinstance(journal_suspend_events, list):\n        reasons.append(\"AMBIGUOUS: L' journal unavailable\")",
       "    if not isinstance(journal_suspend_events, list):\n        pass")]),
    ("M09", "pause channel P removed", [("            if abs(dr - dm) > SLEEP_GAP_TOL_NS:", "            if False:")]),
    ("M10", "suspend (boottime - monotonic) ignored", [("            if db - dm > SLEEP_GAP_TOL_NS:", "            if False:")]),
    ("M11", "D-MEM-FREE gate silently passes",
     [('        "free_memory_ge_min": OPEN_DECISION,', '        "free_memory_ge_min": PASS,')]),
    ("M12", "attestation 'reviewed' not required",
     [('    if att.get("reviewed") is not True or att.get("accepted") is not True:',
       '    if att.get("accepted") is not True:')]),
    ("M13", "provider image updates pass without an attested token",
     [("    else:\n        upd_gate = UNKNOWN                                      # provider image updates not attested",
       "    else:\n        upd_gate = PASS")]),
    ("M14", "update vectors other than apt ignored",
     [("    shown_disabled = bool(apt_off and not timer and not snapd and not cloud and livepatch == [])",
       "    shown_disabled = bool(apt_off)")]),
    ("M15", "launched_by_systemd skips the MainPID check",
     [('rec.get("MainPID") == os.getpid()\n              and ', '')]),
    ("M16", "durable_write writes the target in place", [('    tmp = p.with_name(p.name + ".tmp")\n', "    tmp = p\n")]),
    ("M17", "unreadable pin counts as a match",
     [("    return [k for k in PIN_KEYS if unreadable(pins.get(k)) or got.get(k) != pins.get(k)]",
       "    return [k for k in PIN_KEYS if got.get(k) != pins.get(k)]")]),
    ("M18", "busy_processes uses lifetime ticks instead of the window",
     [("        used = ticks1 - prev[1] if prev is not None else ticks1", "        used = ticks1")]),
    ("M19", "empty cmdline (failed read) hashed as a command",
     [("    return hashlib.sha256(data).hexdigest() if data else None",
       "    return hashlib.sha256(data or b\"\").hexdigest() if data is not None else None")]),
    ("M20", "UNKNOWN gates not reported as blocking",
     [("    blocked = {k: v for k, v in gates.items() if v != PASS}",
       "    blocked = {k: v for k, v in gates.items() if v not in (PASS, UNKNOWN)}")]),
    ("M21", "headroom computed over levels with unreadable usage",
     [("            if not isinstance(use, int):\n                return None\n",
       "            if not isinstance(use, int):\n                continue\n")]),
    ("M22", "namespace mismatch ignored",
     [("        if ident.get(k) is not None and ns.get(k) != ident[k]:\n            return UNKNOWN",
       "        if False:\n            return UNKNOWN")]),
    ("M23", "unknown power-supply type skipped",
     [("        else:\n            return None\n    if discharging:", "        else:\n            continue\n    if discharging:")]),
    ("M24", "process born in the window not counted",
     [("        prev = t0.get((pid, start))\n",
       "        prev = t0.get((pid, start))\n        if prev is None:\n            continue\n")]),
    ("M25", "attestation file sha256 not verified", [("        if _sha(data) != want:", "        if False:")]),
    ("M26", "attestation not bound to the hardware identity",
     [('    if not cur.get("hardware_bound") or att.get("machine") != cur:', "    if False:")]),
    ("M27", "v2 root accepted as unlimited without attestation",
     [("            if not root_attested:\n                return None\n            continue", "            continue")]),
    ("M28", "effective_limit numeric without root attestation",
     [('    if not root_attested or not mem or "MemTotal" not in mem', '    if not mem or "MemTotal" not in mem')]),
    ("M29", "execute / resume pass the launch gate without a launch record",
     [('launched.get("pass") is True else FAIL\n    elif launched',
       'launched.get("pass") is True else (PASS if launched is None else FAIL)\n    elif launched')]),
    ("M30", "mapped shared objects (libm) not pinned",
     [('"python_sys_version", "mapped_objects", "dpkg_versions",', '"python_sys_version", "dpkg_versions",')]),
    ("M31", "incomplete /proc view accepted", [("or view_complete is not True ", "")]),
    ("M32", "own_pids may contain init", [(" or own_pids & {0, 1}", "")]),
    # ---- review 59's mutants, re-anchored to revision 2 (same weakening)
    ("R01", "unreadable Battery status skipped (a failed read can yield AC)",
     [("            if not st:\n                return None\n", "            if not st:\n                continue\n")]),
    ("R02", "host attestation accepted when the 'accepted' key is merely present (e.g. 'REJECTED')",
     [('att.get("accepted") is not True', '"accepted" not in att')]),
    ("R03", "durable_write never fsyncs the data", [("        os.fsync(fd)\n", "        pass\n")]),
    ("R04", "suspend / pause tolerance raised from 2 s to 25 s",
     [("SLEEP_GAP_TOL_NS = 2_000_000_000 ", "SLEEP_GAP_TOL_NS = 25_000_000_000")]),
    ("R05", "hidden name allow-list for the Cloud session controller in busy_processes",
     [("        if pid in own_pids or ppid in own_pids:\n",
       "        if pid in own_pids or ppid in own_pids or comm in (\"claude\", \"environment-man\", \"process_api\"):\n")]),
    ("R06", "package versions and glibc dropped from PIN_KEYS",
     [(' "dpkg_versions",\n', "\n"), ('"machine", "glibc")', '"machine")')]),
    ("R07", "stopped (T/t) and uninterruptible (D) tasks read as DEAD",
     [('    if st.get("state") in ("Z", "X"):\n        return UNKNOWN',
       '    if st.get("state") in ("T", "t", "D"):\n        return DEAD\n    if st.get("state") in ("Z", "X"):\n'
       '        return UNKNOWN')]),
    ("R08", "durable_write never fsyncs the directory after the rename", [("        os.fsync(dfd)\n", "        pass\n")]),
    ("R09", "maximum sample spacing raised from 180 s to 390 s", [("MAX_SAMPLE_GAP_S = 180 ", "MAX_SAMPLE_GAP_S = 390 ")]),
    ("R10", "assess checks power only at start and end, not at the samples",
     [('    power = [x.get("power") if isinstance(x, dict) else None for x in seq]',
       '    power = [x.get("power") if isinstance(x, dict) else None for x in (start, end)]')]),
]


def run_suite(env=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", str(HERE)], cwd=HERE.parent,
                          env=env, capture_output=True, text=True, timeout=900)


def main(out: str | None) -> int:
    src = SRC.read_text()
    rows = []
    for mid, what, edits in MUTANTS:
        mutated, ok = src, True
        for old, new in edits:
            if mutated.count(old) != 1:
                ok = False
                break
            mutated = mutated.replace(old, new)
        if not ok:
            rows.append({"id": mid, "property": what, "status": "NOT_APPLIED (anchor not unique)"})
            continue
        with tempfile.TemporaryDirectory() as d:
            Path(d, "lx_platform.py").write_text(mutated)
            p = run_suite(dict(os.environ, LX_PLATFORM_DIR=d, PYTHONDONTWRITEBYTECODE="1"))
            last = (p.stderr.strip().splitlines() or [""])[-1]
            rows.append({"id": mid, "property": what, "status": "KILLED" if p.returncode != 0 else "SURVIVED",
                         "suite_tail": last})
    base = run_suite(dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    rec = {"lx_platform_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
           "tests_sha256": hashlib.sha256((HERE / "test_lx_platform.py").read_bytes()).hexdigest(),
           "unmutated_suite": "PASS" if base.returncode == 0 else "FAIL",
           "unmutated_tail": (base.stderr.strip().splitlines() or [""])[-1],
           "killed": sum(r["status"] == "KILLED" for r in rows), "total": len(rows),
           "reviewer_mutants_killed": sum(r["status"] == "KILLED" for r in rows if r["id"].startswith("R")),
           "mutants": rows}
    text = json.dumps(rec, indent=1)
    print(text)
    if out:
        Path(out).write_text(text + "\n")
    return 0 if rec["unmutated_suite"] == "PASS" and rec["killed"] == rec["total"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
