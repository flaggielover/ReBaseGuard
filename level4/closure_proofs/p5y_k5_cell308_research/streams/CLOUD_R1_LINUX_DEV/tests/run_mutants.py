"""Mutation harness for the DEV-ONLY lx_platform tests (revision 5). Each mutant weakens one fail-closed property in a
temporary copy of lx_platform.py; the unchanged test suite must FAIL against every mutant ("killed"). A surviving
mutant means a property is untested. M01-M32 are the coordinator's; R01-R10 are review 59's mutants (reviews/
scratch_CLOUD_R1/reviewer_mutants.py) and X01-X09 review 60's surviving mutants (reviews/scratch_CLOUD_R1_DELTA/
reviewer60_mutants.py), each re-anchored to revision 3 with the same weakening; N01-N12 weaken the revision-3 repairs
of review 60's findings; Y01-Y09 are review 61's mutants (reviews/scratch_CLOUD_R1_DELTA2/reviewer61_mutants.py.txt)
re-anchored to revision 4, and P01-P15 weaken the revision-4 repairs of review 61's findings; Z01-Z11 are review 62's
mutants (reviews/scratch_CLOUD_R1_DELTA3/reviewer62_mutants.py.txt) re-anchored to revision 5, and Q01-Q13 weaken the
revision-5 repairs of review 62's findings. Target-free; nothing outside a temporary directory is written.

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
     [("    elif not isinstance(journal_suspend_events, list):\n        reasons.append(\"AMBIGUOUS: L' journal unavailable\")",
       "    elif False:\n        pass")]),
    ("M09", "pause channel P removed", [("            if abs(dr - dm) > SLEEP_GAP_TOL_NS:", "            if False:")]),
    ("M10", "suspend (boottime - monotonic) ignored", [("            if db - dm > SLEEP_GAP_TOL_NS:", "            if False:")]),
    ("M11", "D-MEM-FREE gate silently passes",
     [('        "free_memory_ge_min": OPEN_DECISION,', '        "free_memory_ge_min": PASS,')]),
    ("M12", "attestation 'reviewed' not required",
     [('    if rec.get("reviewed") is not True or rec.get("accepted") is not True:',
       '    if rec.get("accepted") is not True:')]),
    ("M13", "provider image updates pass without an attested token",
     [('        upd_gate = PASS if isinstance(att, dict) and att.get("provider_image_updates") == NO_IMAGE_CHANGE else UNKNOWN',
       "        upd_gate = PASS")]),
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
     [("        if ident.get(k) is None or ns.get(k) != ident[k]:\n            return UNKNOWN",
       "        if False:\n            return UNKNOWN")]),
    ("M23", "unknown power-supply type skipped",
     [("        else:\n            return None\n    if discharging:", "        else:\n            continue\n    if discharging:")]),
    ("M24", "process born in the window not counted",
     [("        prev = t0.get((pid, start))\n",
       "        prev = t0.get((pid, start))\n        if prev is None:\n            continue\n")]),
    ("M25", "attestation file sha256 not verified", [("    if _sha(data) != want:", "    if False:")]),
    ("M26", "attestation not bound to the hardware identity",
     [('    if not cur.get("hardware_bound") or rec.get("machine") != cur:', "    if False:")]),
    ("M27", "v2 root accepted as unlimited without attestation",
     [("            if root_attested is not True:\n                return None\n            continue", "            continue")]),
    ("M28", "effective_limit numeric without root attestation",
     [('    if root_attested is not True or not mem or "MemTotal" not in mem', '    if not mem or "MemTotal" not in mem')]),
    ("M29", "execute / resume pass the launch gate without a launch record",
     [('    if mode in ("execute", "resume") or launched is not None:', '    if launched is not None:')]),
    ("M30", "mapped shared objects (libm) not pinned",
     [('"python_sys_version", "mapped_objects", "dpkg_versions",', '"python_sys_version", "dpkg_versions",')]),
    ("M31", "incomplete /proc view accepted", [("dt_s <= 0 or proc_view_complete() is not True:", "dt_s <= 0:")]),
    ("M32", "own may contain init", [("            or any(k[0] in (0, 1) for k in own):", "            or False:")]),
    # ---- review 59's mutants, re-anchored to revision 2 (same weakening)
    ("R01", "unreadable Battery status skipped (a failed read can yield AC)",
     [("            elif st not in KNOWN_NOT_DISCHARGING:\n                return None",
       "            elif st not in KNOWN_NOT_DISCHARGING:\n                continue")]),
    ("R02", "host attestation accepted when the 'accepted' key is merely present (e.g. 'REJECTED')",
     [('rec.get("accepted") is not True', '"accepted" not in rec')]),
    ("R03", "durable_write never fsyncs the data", [("        os.fsync(fd)\n", "        pass\n")]),
    ("R04", "suspend / pause tolerance raised from 2 s to 25 s",
     [("SLEEP_GAP_TOL_NS = 2_000_000_000 ", "SLEEP_GAP_TOL_NS = 25_000_000_000")]),
    ("R05", "hidden name allow-list for the Cloud session controller in busy_processes",
     [("        if (pid, start) in own or (ppid in own_start and start >= own_start[ppid]):\n            continue\n        prev",
       "        if (pid, start) in own or comm in (\"claude\", \"environment-man\", \"process_api\"):\n            continue\n"
       "        prev")]),
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
    # ---- review 60's surviving mutants, re-anchored to revision 3
    ("X01", "/proc 'subset=' no longer refused",
     [('return not ("hidepid=" in opts or "subset=" in opts)', 'return not ("hidepid=" in opts)')]),
    ("X02", "no /proc mount line counts as a complete view",
     [('            return not ("hidepid=" in opts or "subset=" in opts)\n    return None',
       '            return not ("hidepid=" in opts or "subset=" in opts)\n    return True')]),
    ("X03", "unreadable livepatch counts as none applied", [("livepatch == [])", "livepatch in ([], None))")]),
    ("X04", "K' monotonic-ahead-of-boottime channel removed",
     [("            elif db - dm < -SLEEP_GAP_TOL_NS:\n                reasons.append(\"AMBIGUOUS: K' monotonic advanced more "
       "than boottime\")\n", "")]),
    ("X05", "durable_write read-back verification removed", [("    if got != want:", "    if False:")]),
    ("X06", "absent samples no longer AMBIGUOUS",
     [('    if not isinstance(samples, list):\n        reasons.append("AMBIGUOUS: samples absent")\n', "")]),
    ("X07", "a transient .scope accepted as the campaign unit",
     [('if last.startswith(prefix) and last.endswith(".service"):',
       'if last.startswith(prefix) and last.endswith((".service", ".scope")):')]),
    ("X08", "v1 'unlimited' sentinel lowered to 1 GiB", [("UNLIMITED_CGROUP_V1 = 2 ** 62 ", "UNLIMITED_CGROUP_V1 = 2 ** 30 ")]),
    ("X09", "unknown interpreter package drops out of the pin",
     [('return (owner_query() or UNKNOWN_PACKAGE, f"libpython{v}-stdlib")',
       'return tuple(x for x in (owner_query(), f"libpython{v}-stdlib") if x)')]),
    # ---- weakenings of the revision-3 repairs (review 60 findings)
    ("N01", "D-HOST-LIFETIME treated as decided", [('    lifetime_open = "D-HOST-LIFETIME" not in decided',
                                                    "    lifetime_open = False")]),
    ("N02", "attestation acceptance line not required",
     [('if f"{ACCEPTANCE_LINE}{sha}" in lines and verdicts == [ACCEPTANCE_VERDICT_LINE]:',
       "if verdicts == [ACCEPTANCE_VERDICT_LINE]:")]),
    ("N03", "attestation schema not checked",
     [('    if not isinstance(rec, dict) or rec.get("schema") != ATTESTATION_SCHEMA:', "    if not isinstance(rec, dict):")]),
    ("N04", "caller-asserted fields accepted in the attestation reference",
     [('set(ref) != {"path", "sha256"}', 'not {"path", "sha256"} <= set(ref)')]),
    ("N05", "attestation's root_cgroup_is_real not required",
     [('    if not why and (not isinstance(rec, dict) or rec.get("root_cgroup_is_real") is not True):', "    if False:")]),
    ("N06", "nested PID namespace view accepted", [("    if ino != INIT_PID_NS:\n        return False\n", "")]),
    ("N07", "boot id not validated", [("_g(None if not isinstance(boot, str) or boot_id(boot) is None else True)",
                                       "_g(None if boot is None else True)")]),
    ("N08", "exited processes not reported", [("in t0.items():\n        if (pid, start) not in t1", "in {}.items():\n        if (pid, start) not in t1")]),
    ("N09", "unreadable existing process skipped",
     [('            if Path(f"{proc_root}/{pid}").exists():\n                return None\n', "")]),
    ("N10", "campaign children exempt by pid alone",
     [("        if (pid, start) in own or (ppid in own_start and start >= own_start[ppid]):",
       "        if (pid, start) in own or ppid in own_start:")]),
    ("N11", "unrecorded namespace lets pid evidence count (revision-2 behaviour)",
     [("        if ident.get(k) is None or ns.get(k) != ident[k]:", "        if ident.get(k) is not None and ns.get(k) != ident[k]:")]),
    ("N12", "pin without libm / libc / loader accepted",
     [("    if not all(any(n == r or n.startswith(r) for n in names) for r in REQUIRED_MAPPED):\n        return None",
       "    if False:\n        return None")]),
    ("N13", "launch record trusted on its 'pass' flag",
     [('    return bool(rec.get("systemd_pid1") is True and', '    return bool(rec.get("pass") is True) or bool(rec.get("systemd_pid1") is True and')]),
    ("N14", "unrecognised battery status read as not discharging",
     [("            elif st not in KNOWN_NOT_DISCHARGING:\n                return None", "            else:\n                pass")]),
    # ---- review 61's mutants, re-anchored to revision 4
    ("Y01", "any non-empty decided set opens D-HOST-LIFETIME",
     [('    lifetime_open = "D-HOST-LIFETIME" not in decided', "    lifetime_open = not decided")]),
    ("Y02", "exited children of a campaign pid exempt whatever their start",
     [("if (pid, start) not in t1 and (pid, start) not in own and not (ppid in own_start and start >= own_start[ppid]):",
       "if (pid, start) not in t1 and (pid, start) not in own and not (ppid in own_start):")]),
    ("Y03", "acceptance token matched as a substring",
     [('if f"{ACCEPTANCE_LINE}{sha}" in lines and', 'if f"{ACCEPTANCE_LINE}{sha}" in "\\n".join(lines) and')]),
    ("Y04", "cgroup namespace reading hard-wired to initial",
     [('            "cgroup_ns_initial": ns_inode("cgroup") == INIT_CGROUP_NS,', '            "cgroup_ns_initial": True,')]),
    ("Y05", "attestation bound to /etc/machine-id only",
     [('    if not cur.get("hardware_bound") or rec.get("machine") != cur:',
       '    if not cur.get("hardware_bound") or (rec.get("machine") or {}).get("machine_id_sha256") != '
       'cur.get("machine_id_sha256"):')]),
    ("Y06", "loader no longer a required pin member",
     [('REQUIRED_MAPPED = ("libm.so.6", "libc.so.6", "ld-linux")', 'REQUIRED_MAPPED = ("libm.so.6", "libc.so.6")')]),
    ("Y07", "launch record unit type not checked",
     [('                and unit.endswith(".service") and isinstance(rec.get("invocation_id"), str)',
       '                and isinstance(rec.get("invocation_id"), str)')]),
    ("Y08", "merely truthy guest_updates_shown_disabled counts",
     [('    if not isinstance(upd, dict) or upd.get("guest_updates_shown_disabled") is not True:',
       '    if not isinstance(upd, dict) or not upd.get("guest_updates_shown_disabled"):')]),
    ("Y09", "cgroup_resources reads the leaf only",
     [("        for i in range(len(parts), -1, -1):\n            d = base.joinpath(*parts[:i])\n            rows.append(",
       "        for i in range(len(parts), len(parts) - 1, -1):\n            d = base.joinpath(*parts[:i])\n            rows.append(")]),
    # ---- weakenings of the revision-4 repairs (review 61 findings)
    ("P01", "acceptance committed with the attestation accepted (no order check)",
     [("    acc = [a for a in acc if _ordered(base, path, a, want)]", "    acc = acc")]),
    ("P02", "a rejecting review ignored", [("    if rej:\n        reasons.append", "    if False:\n        reasons.append")]),
    ("P03", "acceptance review outside the fixed name set accepted",
     [('if not (name.startswith(ACCEPTANCE_REVIEW_PREFIX) and name.endswith(".md")) or path in rej:',
       "if path in rej:")]),
    ("P04", "verdict line not required", [("and verdicts == [ACCEPTANCE_VERDICT_LINE]:", ":")]),
    ("P05", "non-initial cgroup namespace does not block a number",
     [('    if ns_inode("cgroup") != INIT_CGROUP_NS:\n        why.append', "    if False:\n        why.append")]),
    ("P06", "root attestation without D-HOST-LIFETIME decided",
     [('    if "D-HOST-LIFETIME" not in _decided():\n        why.append', "    if False:\n        why.append")]),
    ("P07", "DECIDED not validated",
     [("    if not isinstance(DECIDED, frozenset) or not DECIDED <= frozenset(OPEN_DECISIONS):", "    if False:")]),
    ("P08", "passed launch record trusted instead of a fresh reading",
     [("        ok = launch_record_ok(fresh) and (launched is None or launched == fresh)",
       "        ok = launch_record_ok(launched if launched is not None else fresh)")]),
    ("P09", "MainPID type not checked",
     [("and isinstance(mp, int) and not isinstance(mp, bool) and mp == os.getpid()", "and mp == os.getpid()")]),
    ("P10", "journal channel counted without a reviewed reader",
     [("    if not JOURNAL_READER_REVIEWED:\n        reasons.append", "    if False:\n        reasons.append")]),
    ("P11", "masked unit not recognised",
     [('        if f.is_symlink() and os.path.realpath(f) == "/dev/null":\n            return False\n', "")]),
    ("P12", "unknown update-unit state counted as disabled",
     [("    timer = any(v is not False for v in units.values())", "    timer = any(v is True for v in units.values())")]),
    ("P13", "only the first unit root searched (file mode)",
     [("    for root in unit_roots:\n        r = Path(root)\n        if not r.exists():\n            continue\n        try:",
       "    for root in unit_roots[:1]:\n        r = Path(root)\n        if not r.exists():\n            continue\n        try:")]),
    ("P14", "identity record shape not validated",
     [("    if not _ident_shape_ok(ident):\n        return UNKNOWN", '    if not isinstance(ident, dict) or not ident.get("pid"):\n        return UNKNOWN')]),
    ("P15", "empty pin-point list accepted",
     [("    if not mods:\n        raise RuntimeError", "    if mods is None:\n        raise RuntimeError")]),
    # ---- review 62's mutants (reviews/scratch_CLOUD_R1_DELTA3/reviewer62_mutants.py.txt), re-anchored to revision 5;
    # Z05 / Z06 targeted _added_in, which revision 5 removed: Z05 / Z06 here are the same weakenings of its successor
    # (_ordered): the line's first commit looked up by path (a rename defeats it), and an equal commit counted as later
    ("Z01", "a rejecting review counts only if the negative word is on the same line as the sha",
     [("        if any(sha in ln for ln in lines) and any(_NEGATIVE.search(ln) for ln in lines):",
       "        if any(sha in ln and _NEGATIVE.search(ln) for ln in lines):")]),
    ("Z02", "update units enabled through a *.requires link are not seen",
     [('d.name.endswith((".wants", ".requires"))', 'd.name.endswith(".wants")')]),
    ("Z03", "systemctl is-enabled: enabled-runtime / indirect / alias / linked read as disabled",
     [('        if st in ("enabled", "enabled-runtime", "static", "indirect", "alias", "linked", "linked-runtime"):\n'
       '            return True\n        if st in ("disabled", "masked", "masked-runtime"):',
       '        if st in ("enabled", "static"):\n            return True\n'
       '        if st in ("disabled", "masked", "masked-runtime", "enabled-runtime", "indirect", "alias", "linked", '
       '"linked-runtime"):')]),
    ("Z04", "a missing unit root ends the search (later roots never read)",
     [("        if not r.exists():\n            continue\n        try:", "        if not r.exists():\n            return False\n        try:")]),
    ("Z05", "accepting line's first commit looked up by path only (a git mv into the set resets it)",
     [('line_commit = _first_commit(repo_root, f"-S{ACCEPTANCE_LINE}{sha}", "HEAD")',
       'line_commit = _first_commit(repo_root, f"-S{ACCEPTANCE_LINE}{sha}", "HEAD", "--", acc_path)')]),
    ("Z06", "accepting line in the same commit as the attested blob counts as later",
     [("    if not earlier or not later or earlier == later:\n        return False",
       "    if not earlier or not later:\n        return False\n    if earlier == later:\n        return True")]),
    ("Z07", "a failed systemctl query (empty stdout) reads as 'disabled'",
     [("    return r.stdout.strip() or None\n\n\ndef _unit_files", "    return r.stdout.strip() or \"disabled\"\n\n\ndef _unit_files")]),
    ("Z08", "only an UNREADABLE cgroup namespace blocks root attestation (a non-initial one passes)",
     [('    if ns_inode("cgroup") != INIT_CGROUP_NS:\n        why.append', '    if ns_inode("cgroup") is None:\n        why.append')]),
    ("Z09", "launch gate evaluated only for execute / resume (a record passed in launcher mode is ignored)",
     [('    if mode in ("execute", "resume") or launched is not None:', '    if mode in ("execute", "resume"):')]),
    ("Z10", "an unreadable /proc view (None) treated as complete",
     [("dt_s <= 0 or proc_view_complete() is not True:", "dt_s <= 0 or proc_view_complete() is False:")]),
    ("Z11", "a bool starttime in a record passes the shape check",
     [('        if v is not None and (not isinstance(v, int) or isinstance(v, bool) or v < 0):',
       '        if v is not None and (not isinstance(v, int) or v < 0):')]),
    # ---- weakenings of the revision-5 repairs (review 62 findings)
    ("Q01", "negative scan not recursive (a rejection in a review subdirectory ignored)",
     [('every = _git(repo_root, "ls-tree", "-r", "--name-only", "HEAD", "--", ACCEPTANCE_REVIEW_DIR)',
       'every = _git(repo_root, "ls-tree", "--name-only", "HEAD", f"{ACCEPTANCE_REVIEW_DIR}/")')]),
    ("Q02", "accepting set recursive (reviewer scratch can accept)",
     [('tree = _git(repo_root, "ls-tree", "--name-only", "HEAD", f"{ACCEPTANCE_REVIEW_DIR}/")',
       'tree = _git(repo_root, "ls-tree", "-r", "--name-only", "HEAD", "--", ACCEPTANCE_REVIEW_DIR)')]),
    ("Q03", "negative words matched case-sensitively",
     [('_NEGATIVE = re.compile(r"reject|withdraw|not[ _-]?accepted|revoke", re.I)',
       '_NEGATIVE = re.compile(r"REJECT|WITHDRAW|NOT[ _-]?ACCEPTED|REVOKE")')]),
    ("Q04", "a second (conflicting) verdict line tolerated",
     [("and verdicts == [ACCEPTANCE_VERDICT_LINE]:", "and ACCEPTANCE_VERDICT_LINE in verdicts:")]),
    ("Q05", "accepting file suffix not required",
     [('(name.startswith(ACCEPTANCE_REVIEW_PREFIX) and name.endswith(".md"))', "name.startswith(ACCEPTANCE_REVIEW_PREFIX)")]),
    ("Q06", "attested commit found by path, not by blob (placeholder attestation filled later)",
     [('att_commit = _first_commit(repo_root, f"--find-object={blob}", "HEAD")',
       'att_commit = _first_commit(repo_root, "HEAD", "--", att_path)')]),
    ("Q07", "systemctl is-active not consulted (a running but disabled update unit reads as off)",
     [('        act = _systemctl_is_active(unit)\n        if act in ("active", "activating", "reloading"):\n'
       '            return True\n', "")]),
    ("Q08", "is-enabled not-found read as disabled without checking the unit files",
     [("            return False if _unit_files(unit, unit_roots) is False else None", "            return False")]),
    ("Q09", "dangling .wants / .requires link not counted",
     [("(e.is_symlink() or e.exists())", "e.exists()")]),
    ("Q10", "preflight power reading replaced by a constant AC",
     [("    power = power_source()  ", "    power = AC  ")]),
    ("Q11", "preflight free-disk reading replaced by a constant",
     [("    free = free_disk_bytes(repo_path)\n", "    free = 2 ** 40\n")]),
    ("Q12", "transient / generator roots dropped from the unit search path",
     [('"/run/systemd/transient",\n              "/run/systemd/generator.early", ', '\n              ')]),
    ("Q13", "host_exclusive reports only its first open decision",
     [('                                      for d in ((_GATE_DECISION[k],) if isinstance(_GATE_DECISION[k], str)\n'
       '                                                else _GATE_DECISION[k])})}',
       '                                      for d in ((_GATE_DECISION[k],) if isinstance(_GATE_DECISION[k], str)\n'
       '                                                else _GATE_DECISION[k][:1])})}')]),
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
           "review60_mutants_killed": sum(r["status"] == "KILLED" for r in rows if r["id"].startswith("X")),
           "review61_mutants_killed": sum(r["status"] == "KILLED" for r in rows if r["id"].startswith("Y")),
           "review62_mutants_killed": sum(r["status"] == "KILLED" for r in rows if r["id"].startswith("Z")),
           "mutants": rows}
    text = json.dumps(rec, indent=1)
    print(text)
    if out:
        Path(out).write_text(text + "\n")
    return 0 if rec["unmutated_suite"] == "PASS" and rec["killed"] == rec["total"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
