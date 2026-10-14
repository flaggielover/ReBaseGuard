"""Mutation harness for the DEV-ONLY lx_platform tests: each mutant weakens one fail-closed property in a temporary
copy of lx_platform.py; the unchanged test suite must FAIL against every mutant ("killed"). A surviving mutant means
a property is untested. Target-free; nothing outside a temporary directory is written.

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

# (id, property weakened, old text, new text) -- each old text must occur exactly once
MUTANTS = [
    ("M01", "failed boot-id read treated as a reboot (DEAD)",
     "    if cur is None:\n        return UNKNOWN\n", "    if cur is None:\n        return DEAD\n"),
    ("M02", "unreadable /proc/<pid>/stat treated as DEAD",
     "    if st is None:\n        return UNKNOWN\n    if st.get(\"state\")", "    if st is None:\n        return DEAD\n    if st.get(\"state\")"),
    ("M03", "incomplete identity record reported ALIVE",
     "    return ALIVE if complete else UNKNOWN", "    return ALIVE"),
    ("M04", "zombie not recognised as dead",
     'if st.get("state") in ("Z", "X"):', 'if st.get("state") in ("X",):'),
    ("M05", "pid reuse (other starttime) not detected",
     'st["starttime"] != ident["starttime_ticks"]', 'False'),
    ("M06", "no power supply exposed read as AC",
     '        return "ABSENT"\n', '        return AC\n'),
    ("M07", "unreadable cgroup ancestor treated as unlimited",
     "        if lim is None:\n            return None\n", "        if lim is None:\n            continue\n"),
    ("M08", "missing journal channel ignored in assess",
     "    if not isinstance(journal_suspend_events, list):\n        reasons.append(\"AMBIGUOUS: L' journal unavailable\")",
     "    if not isinstance(journal_suspend_events, list):\n        pass"),
    ("M09", "pause channel P removed",
     "            if abs(dr - dm) > SLEEP_GAP_TOL_NS:", "            if False:"),
    ("M10", "suspend (boottime - monotonic) ignored",
     "            if db - dm > SLEEP_GAP_TOL_NS:", "            if False:"),
    ("M11", "D-MEM-FREE gate silently passes",
     '        "free_memory_ge_min": OPEN_DECISION,', '        "free_memory_ge_min": PASS,'),
    ("M12", "unreviewed host attestation accepted",
     'host_attestation.get("reviewed")\n                                           and ', ''),
    ("M13", "provider image updates UNKNOWN ignored",
     '(UNKNOWN if upd.get("provider_image_updates") == UNKNOWN else PASS)', 'PASS'),
    ("M14", "missing update setting counts as disabled",
     "    enabled = not (files is not None and not timer\n                   and (vals.get(\"Enable\") == \"0\" or vals.get(\"Unattended-Upgrade\") == \"0\"))",
     "    enabled = vals.get(\"Unattended-Upgrade\") == \"1\" or timer"),
    ("M15", "launched_by_systemd skips the MainPID check",
     'rec.get("MainPID") == os.getpid()\n              and ', ''),
    ("M16", "durable_write without fsync / tmp+rename (in-place write)",
     "    tmp = p.with_name(p.name + \".tmp\")\n", "    tmp = p\n"),
    ("M17", "unreadable pin counts as a match",
     'return [k for k in PIN_KEYS if pins.get(k) is None or got.get(k) != pins.get(k)]',
     'return [k for k in PIN_KEYS if got.get(k) != pins.get(k)]'),
    ("M18", "busy_processes uses lifetime ticks instead of the window",
     "        pct = 100.0 * (ticks1 - prev[1]) / hz / dt_s", "        pct = 100.0 * ticks1 / hz / dt_s"),
    ("M19", "empty cmdline (failed read) hashed as a command",
     "    return hashlib.sha256(data).hexdigest() if data else None",
     "    return hashlib.sha256(data or b\"\").hexdigest() if data is not None else None"),
    ("M20", "preflight pass ignores non-PASS gates of state UNKNOWN",
     "    blocked = {k: v for k, v in gates.items() if v != PASS}",
     "    blocked = {k: v for k, v in gates.items() if v not in (PASS, UNKNOWN)}"),
]


def main(out: str | None) -> int:
    src = SRC.read_text()
    rows = []
    for mid, what, old, new in MUTANTS:
        if src.count(old) != 1:
            rows.append({"id": mid, "property": what, "status": "NOT_APPLIED (anchor not unique)"})
            continue
        with tempfile.TemporaryDirectory() as d:
            Path(d, "lx_platform.py").write_text(src.replace(old, new))
            env = dict(os.environ, LX_PLATFORM_DIR=d)
            p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(HERE)], cwd=HERE.parent,
                               env=env, capture_output=True, text=True, timeout=600)
            last = (p.stderr.strip().splitlines() or [""])[-1]
            rows.append({"id": mid, "property": what, "status": "KILLED" if p.returncode != 0 else "SURVIVED",
                         "suite_tail": last})
    base = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(HERE)], cwd=HERE.parent,
                          capture_output=True, text=True, timeout=600)
    rec = {"lx_platform_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
           "tests_sha256": hashlib.sha256((HERE / "test_lx_platform.py").read_bytes()).hexdigest(),
           "unmutated_suite": "PASS" if base.returncode == 0 else "FAIL",
           "unmutated_tail": (base.stderr.strip().splitlines() or [""])[-1],
           "killed": sum(r["status"] == "KILLED" for r in rows), "total": len(rows), "mutants": rows}
    text = json.dumps(rec, indent=1)
    print(text)
    if out:
        Path(out).write_text(text + "\n")
    return 0 if rec["unmutated_suite"] == "PASS" and rec["killed"] == rec["total"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
