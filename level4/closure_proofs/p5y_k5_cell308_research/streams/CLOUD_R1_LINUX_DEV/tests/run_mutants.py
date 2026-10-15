"""Strict, target-free mutation evidence for the combined Cell-308 development layer.

Retains Claude revision-5 M/R/X/N/Y/P/Z/Q properties. CDEX01-CDEX15 are origin-qualified
Codex property deltas (Y/P/F in its independent lineage); CDEX16 covers the combined
unknown-activity boundary; absent-blob refusal has separate regression tests. Historical totals are not validation of these bytes.
The unmutated suite runs first after removing inherited LX_PLATFORM_DIR. KILLED requires the
full baseline count, only AssertionError failures, and an explicit intended-property witness.
R5SYNC01-R5SYNC04 cover complete veto paths, failed veto evidence and unknown supervisor state.
RV01-RV17 carry Claude review 63's mutants W01-W07 (re-anchored where the code they targeted changed) and
weaken its H1/H3/H6/H7 repairs; P11, Z01, Z02, Z05 and Q06 are re-anchored with the same weakening.
RV18-RV28 carry review 64's surviving mutants (RW1-RW4, RW6) and weaken its K1, K4, K7 and K9 repairs; RV29-RV30
weaken the history-completeness guard restored after review 64 (shallow clones hide deleted rejections); RV31-RV42
carry review 65's mutants RX1-RX6 and weaken its L1, L3, L6 and L7 repairs; RV43-RV48 weaken review 66's M1-M4
repairs (RV39 is narrowed to the key refusal; the lazy-fetch block is RV45); RV49-RV51 weaken review 67's N1, N2 and
N4 repairs, and RV52-RV54 carry its surviving mutants RZ1, RZ4 and RZ5 (N5); RV55-RV58 carry review 68's mutants
RA1-RA4 and RV59-RV60 weaken its P1 repair (RV26 then also tolerates symlinks in the history scan); RV61-RV63 carry
review 69's RB1, RB2 and RB4 against the mode-reading ancestor check (S1, S2).
Every complete raw report, mutation anchor, and before/after input hash is retained.
No scientific evaluator is imported or executed. Explicit output paths receive the evidence.

usage: python3 tests/run_mutants.py [out.json]
"""
from __future__ import annotations

import ast
import datetime
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "lx_platform.py"

# Each original anchor must occur exactly once; each transformation must parse.
MUTANTS = [('M01',
  'failed boot-id read treated as a reboot (DEAD)',
  [('    if cur is None:\n        return UNKNOWN\n', '    if cur is None:\n        return DEAD\n')]),
 ('M02',
  'unreadable /proc/<pid>/stat treated as DEAD',
  [('    st = (stat or proc_stat)(pid)\n    if st is None:\n        return UNKNOWN\n',
    '    st = (stat or proc_stat)(pid)\n    if st is None:\n        return DEAD\n')]),
 ('M03',
  'incomplete identity record reported ALIVE',
  [('    return ALIVE if complete else UNKNOWN', '    return ALIVE')]),
 ('M04',
  'zombie read as DEAD again (the withdrawn L-ID-1)',
  [('if st.get("state") in ("Z", "X"):\n        return UNKNOWN',
    'if st.get("state") in ("Z", "X"):\n        return DEAD')]),
 ('M05', 'pid reuse (other starttime) not detected', [('st["starttime"] != ident["starttime_ticks"]', 'False')]),
 ('M06',
  'no power supply exposed read as AC',
  [('    if not entries:\n        return "ABSENT"\n', '    if not entries:\n        return AC\n')]),
 ('M07',
  'unreadable cgroup limit skipped',
  [('        if lvl["limit"] is None:\n            return None\n',
    '        if lvl["limit"] is None:\n            continue\n')]),
 ('M08',
  'missing journal channel ignored in assess',
  [('    elif not isinstance(journal_suspend_events, list):\n'
    '        reasons.append("AMBIGUOUS: L\' journal unavailable")',
    '    elif False:\n        pass')]),
 ('M09', 'pause channel P removed', [('            if abs(dr - dm) > SLEEP_GAP_TOL_NS:', '            if False:')]),
 ('M10',
  'suspend (boottime - monotonic) ignored',
  [('            if db - dm > SLEEP_GAP_TOL_NS:', '            if False:')]),
 ('M11',
  'D-MEM-FREE gate silently passes',
  [('        "free_memory_ge_min": OPEN_DECISION,', '        "free_memory_ge_min": PASS,')]),
 ('M12',
  "attestation 'reviewed' not required",
  [('    if rec.get("reviewed") is not True or rec.get("accepted") is not True:',
    '    if rec.get("accepted") is not True:')]),
 ('M13',
  'provider image updates pass without an attested token',
  [('        upd_gate = PASS if isinstance(att, dict) and att.get("provider_image_updates") == NO_IMAGE_CHANGE else '
    'UNKNOWN',
    '        upd_gate = PASS')]),
 ('M14',
  'update vectors other than apt ignored',
  [('    shown_disabled = bool(apt_off and not timer and not snapd and not cloud and livepatch == [])',
    '    shown_disabled = bool(apt_off)')]),
 ('M15',
  'launched_by_systemd skips the MainPID check',
  [('rec.get("MainPID") == os.getpid()\n              and ', '')]),
 ('M16', 'durable_write writes the target in place', [('    tmp = p.with_name(p.name + ".tmp")\n', '    tmp = p\n')]),
 ('M17',
  'unreadable pin counts as a match',
  [('    return [k for k in PIN_KEYS if unreadable(pins.get(k)) or got.get(k) != pins.get(k)]',
    '    return [k for k in PIN_KEYS if got.get(k) != pins.get(k)]')]),
 ('M18',
  'busy_processes uses lifetime ticks instead of the window',
  [('        used = ticks1 - prev[1] if prev is not None else ticks1', '        used = ticks1')]),
 ('M19',
  'empty cmdline (failed read) hashed as a command',
  [('    return hashlib.sha256(data).hexdigest() if data else None',
    '    return hashlib.sha256(data or b"").hexdigest() if data is not None else None')]),
 ('M20',
  'UNKNOWN gates not reported as blocking',
  [('    blocked = {k: v for k, v in gates.items() if v != PASS}',
    '    blocked = {k: v for k, v in gates.items() if v not in (PASS, UNKNOWN)}')]),
 ('M21',
  'headroom computed over levels with unreadable usage',
  [('            if not isinstance(use, int):\n                return None\n',
    '            if not isinstance(use, int):\n                continue\n')]),
 ('M22',
  'namespace mismatch ignored',
  [('        if type(ident.get(k)) is not int or ident[k] <= 0 or not isinstance(ns, dict) \\\n'
    '                or type(ns.get(k)) is not int or ns.get(k) != ident[k]:\n'
    '            return UNKNOWN',
    '        if False:\n            return UNKNOWN')]),
 ('M23',
  'unknown power-supply type skipped',
  [('        else:\n            return None\n    if discharging:',
    '        else:\n            continue\n    if discharging:')]),
 ('M24',
  'process born in the window not counted',
  [('        prev = t0.get((pid, start))\n',
    '        prev = t0.get((pid, start))\n        if prev is None:\n            continue\n')]),
 ('M25', 'attestation file sha256 not verified', [('    if _sha(data) != want:', '    if False:')]),
 ('M26',
  'attestation not bound to the hardware identity',
  [('    if not cur.get("hardware_bound") or rec.get("machine") != cur:', '    if False:')]),
 ('M27',
  'v2 root accepted as unlimited without attestation',
  [('            if root_attested is not True:\n                return None\n            continue',
    '            continue')]),
 ('M28',
  'effective_limit numeric without root attestation',
  [('    if root_attested is not True or not mem or "MemTotal" not in mem',
    '    if not mem or "MemTotal" not in mem')]),
 ('M29',
  'execute / resume pass the launch gate without a launch record',
  [('    if mode in ("execute", "resume") or launched is not None:', '    if launched is not None:')]),
 ('M30',
  'mapped shared objects (libm) not pinned',
  [('"python_sys_version", "mapped_objects", "dpkg_versions",', '"python_sys_version", "dpkg_versions",')]),
 ('M31', 'incomplete /proc view accepted', [('dt_s <= 0 or proc_view_complete() is not True:', 'dt_s <= 0:')]),
 ('M32', 'own may contain init', [('            or any(k[0] in (0, 1) for k in own):', '            or False:')]),
 ('R01',
  'unreadable Battery status skipped (a failed read can yield AC)',
  [('            elif st not in KNOWN_NOT_DISCHARGING:\n                return None',
    '            elif st not in KNOWN_NOT_DISCHARGING:\n                continue')]),
 ('R02',
  "host attestation accepted when the 'accepted' key is merely present (e.g. 'REJECTED')",
  [('rec.get("accepted") is not True', '"accepted" not in rec')]),
 ('R03', 'durable_write never fsyncs the data', [('        os.fsync(fd)\n', '        pass\n')]),
 ('R04',
  'suspend / pause tolerance raised from 2 s to 25 s',
  [('SLEEP_GAP_TOL_NS = 2_000_000_000 ', 'SLEEP_GAP_TOL_NS = 25_000_000_000')]),
 ('R05',
  'hidden name allow-list for the Cloud session controller in busy_processes',
  [('        if owned((pid, start), ppid, t1):\n            continue\n        prev',
    '        if (pid, start) in own or comm in ("claude", "environment-man", "process_api"):\n'
    '            continue\n'
    '        prev')]),
 ('R06',
  'package versions and glibc dropped from PIN_KEYS',
  [(' "dpkg_versions",\n', '\n'), ('"machine", "glibc")', '"machine")')]),
 ('R07',
  'stopped (T/t) and uninterruptible (D) tasks read as DEAD',
  [('    if st.get("state") in ("Z", "X"):\n        return UNKNOWN',
    '    if st.get("state") in ("T", "t", "D"):\n'
    '        return DEAD\n'
    '    if st.get("state") in ("Z", "X"):\n'
    '        return UNKNOWN')]),
 ('R08',
  'durable_write never fsyncs the directory after the rename',
  [('        os.fsync(dfd)\n', '        pass\n')]),
 ('R09',
  'maximum sample spacing raised from 180 s to 390 s',
  [('MAX_SAMPLE_GAP_S = 180 ', 'MAX_SAMPLE_GAP_S = 390 ')]),
 ('R10',
  'assess checks power only at start and end, not at the samples',
  [('    power = [x.get("power") if isinstance(x, dict) else None for x in seq]',
    '    power = [x.get("power") if isinstance(x, dict) else None for x in (start, end)]')]),
 ('X01',
  "/proc 'subset=' no longer refused",
  [('return not ("hidepid=" in opts or "subset=" in opts)', 'return not ("hidepid=" in opts)')]),
 ('X02',
  'no /proc mount line counts as a complete view',
  [('    if not candidates:\n        return None\n', '    if not candidates:\n        return True\n')]),
 ('X03', 'unreadable livepatch counts as none applied', [('livepatch == [])', 'livepatch in ([], None))')]),
 ('X04',
  "K' monotonic-ahead-of-boottime channel removed",
  [('                elif db - dm < -SLEEP_GAP_TOL_NS:\n'
    '                    reasons.append("AMBIGUOUS: K\' monotonic advanced more than boottime")\n',
    '')]),
 ('X05', 'durable_write read-back verification removed', [('    if got != want:', '    if False:')]),
 ('X06',
  'absent samples no longer AMBIGUOUS',
  [('    if not isinstance(samples, list):\n        reasons.append("AMBIGUOUS: samples absent")\n', '')]),
 ('X07',
  'a transient .scope accepted as the campaign unit',
  [('if last.startswith(prefix) and last.endswith(".service"):',
    'if last.startswith(prefix) and last.endswith((".service", ".scope")):')]),
 ('X08',
  "v1 'unlimited' sentinel lowered to 1 GiB",
  [('UNLIMITED_CGROUP_V1 = 2 ** 62 ', 'UNLIMITED_CGROUP_V1 = 2 ** 30 ')]),
 ('X09',
  'unknown interpreter package drops out of the pin',
  [('return (owner_query() or UNKNOWN_PACKAGE, f"libpython{v}-stdlib")',
    'return tuple(x for x in (owner_query(), f"libpython{v}-stdlib") if x)')]),
 ('N01',
  'D-HOST-LIFETIME treated as decided',
  [('    lifetime_open = "D-HOST-LIFETIME" not in decided', '    lifetime_open = False')]),
 ('N02',
  'attestation acceptance line not required',
  [('if f"{ACCEPTANCE_LINE}{sha}" in lines and verdicts == [ACCEPTANCE_VERDICT_LINE]:',
    'if verdicts == [ACCEPTANCE_VERDICT_LINE]:')]),
 ('N03',
  'attestation schema not checked',
  [('    if not isinstance(rec, dict) or rec.get("schema") != ATTESTATION_SCHEMA:',
    '    if not isinstance(rec, dict):')]),
 ('N04',
  'caller-asserted fields accepted in the attestation reference',
  [('set(ref) != {"path", "sha256"}', 'not {"path", "sha256"} <= set(ref)')]),
 ('N05',
  "attestation's root_cgroup_is_real not required",
  [('    if not why and (not isinstance(rec, dict) or rec.get("root_cgroup_is_real") is not True):',
    '    if False:')]),
 ('N06', 'nested PID namespace view accepted', [('    if ino != INIT_PID_NS:\n        return False\n', '')]),
 ('N07',
  'boot id not validated',
  [('_g(None if not isinstance(boot, str) or boot_id(boot) is None else True)',
    '_g(None if boot is None else True)')]),
 ('N08',
  'exited processes not reported',
  [('in t0.items():\n        if (pid, start) not in t1', 'in {}.items():\n        if (pid, start) not in t1')]),
 ('N09',
  'unreadable existing process skipped',
  [('            if Path(f"{proc_root}/{pid}").exists():\n                return None\n', '')]),
 ('N10',
  'campaign children exempt by pid alone',
  [('        return key in own or (ppid in own_start and (ppid, own_start[ppid]) in snapshot\n'
    '                              and key[1] >= own_start[ppid])',
    '        return key in own or ppid in own_start')]),
 ('N11',
  'unrecorded namespace lets pid evidence count (revision-2 behaviour)',
  [('        if type(ident.get(k)) is not int or ident[k] <= 0 or not isinstance(ns, dict) \\\n'
    '                or type(ns.get(k)) is not int or ns.get(k) != ident[k]:',
    '        if ident.get(k) is not None and (type(ident[k]) is not int or ident[k] <= 0\n'
    '                or not isinstance(ns, dict) or type(ns.get(k)) is not int or ns.get(k) != ident[k]):')]),
 ('N12',
  'pin without libm / libc / loader accepted',
  [('    if not all(any(n == r or n.startswith(r) for n in names) for r in REQUIRED_MAPPED):\n        return None',
    '    if False:\n        return None')]),
 ('N13',
  "launch record trusted on its 'pass' flag",
  [('    return bool(rec.get("systemd_pid1") is True and',
    '    return bool(rec.get("pass") is True) or bool(rec.get("systemd_pid1") is True and')]),
 ('N14',
  'unrecognised battery status read as not discharging',
  [('            elif st not in KNOWN_NOT_DISCHARGING:\n                return None',
    '            else:\n                pass')]),
 ('Y01',
  'any non-empty decided set opens D-HOST-LIFETIME',
  [('    lifetime_open = "D-HOST-LIFETIME" not in decided', '    lifetime_open = not decided')]),
 ('Y02',
  'exited children of a campaign pid exempt whatever their start',
  [('if (pid, start) not in t1 and not owned((pid, start), ppid, t0):',
    'if (pid, start) not in t1 and (pid, start) not in own and ppid not in own_start:')]),
 ('Y03',
  'acceptance token matched as a substring',
  [('if f"{ACCEPTANCE_LINE}{sha}" in lines and', 'if f"{ACCEPTANCE_LINE}{sha}" in "\\n".join(lines) and')]),
 ('Y04',
  'cgroup namespace reading hard-wired to initial',
  [('            "cgroup_ns_initial": ns_inode("cgroup") == INIT_CGROUP_NS,',
    '            "cgroup_ns_initial": True,')]),
 ('Y05',
  'attestation bound to /etc/machine-id only',
  [('    if not cur.get("hardware_bound") or rec.get("machine") != cur:',
    '    if not cur.get("hardware_bound") or (rec.get("machine") or {}).get("machine_id_sha256") != '
    'cur.get("machine_id_sha256"):')]),
 ('Y06',
  'loader no longer a required pin member',
  [('REQUIRED_MAPPED = ("libm.so.6", "libc.so.6", "ld-linux")', 'REQUIRED_MAPPED = ("libm.so.6", "libc.so.6")')]),
 ('Y07',
  'launch record unit type not checked',
  [('                and unit.endswith(".service") and isinstance(rec.get("invocation_id"), str)',
    '                and isinstance(rec.get("invocation_id"), str)')]),
 ('Y08',
  'merely truthy guest_updates_shown_disabled counts',
  [('    if not isinstance(upd, dict) or upd.get("guest_updates_shown_disabled") is not True:',
    '    if not isinstance(upd, dict) or not upd.get("guest_updates_shown_disabled"):')]),
 ('Y09',
  'cgroup_resources reads the leaf only',
  [('        for i in range(len(parts), -1, -1):\n'
    '            d = base.joinpath(*parts[:i])\n'
    '            rows.append(',
    '        for i in range(len(parts), len(parts) - 1, -1):\n'
    '            d = base.joinpath(*parts[:i])\n'
    '            rows.append(')]),
 ('P01',
  'acceptance committed with the attestation accepted (no order check)',
  [('    acc = [a for a in acc if _ordered(base, path, a, want)]', '    acc = acc')]),
 ('P02',
  'a rejecting review ignored',
  [('    if rej:\n        reasons.append', '    if False:\n        reasons.append')]),
 ('P03',
  'acceptance review outside the fixed name set accepted',
  [('if not (name.startswith(ACCEPTANCE_REVIEW_PREFIX) and name.endswith(".md")) or path in rej:',
    'if path in rej:')]),
 ('P04', 'verdict line not required', [('and verdicts == [ACCEPTANCE_VERDICT_LINE]:', ':')]),
 ('P05',
  'non-initial cgroup namespace does not block a number',
  [('    if ns_inode("cgroup") != INIT_CGROUP_NS:\n        why.append', '    if False:\n        why.append')]),
 ('P06',
  'root attestation without D-HOST-LIFETIME decided',
  [('    if "D-HOST-LIFETIME" not in _decided():\n        why.append', '    if False:\n        why.append')]),
 ('P07',
  'DECIDED not validated',
  [('    if not isinstance(DECIDED, frozenset) or not DECIDED <= frozenset(OPEN_DECISIONS):', '    if False:')]),
 ('P08',
  'passed launch record trusted instead of a fresh reading',
  [('        ok = launch_record_ok(fresh) and (launched is None or launched == fresh)',
    '        ok = launch_record_ok(launched if launched is not None else fresh)')]),
 ('P09',
  'MainPID type not checked',
  [('and isinstance(mp, int) and not isinstance(mp, bool) and mp == os.getpid()', 'and mp == os.getpid()')]),
 ('P10',
  'journal channel counted without a reviewed reader',
  [('    if not JOURNAL_READER_REVIEWED:\n        reasons.append', '    if False:\n        reasons.append')]),
 ('P11',
  'masked unit not recognised',
  [('    if first is not None and first.is_symlink() and os.path.realpath(first) == "/dev/null":\n'
    '        return False                                            # masked: no dependency can start it\n', '')]),
 ('P12',
  'unknown update-unit state counted as disabled',
  [('    timer = any(v is not False for v in units.values())',
    '    timer = any(v is True for v in units.values())')]),
 ('P13',
  'only the first unit root searched (file mode)',
  [('    for root in unit_roots:\n'
    '        r = Path(root)\n'
    '        if not r.exists():\n'
    '            continue\n'
    '        try:',
    '    for root in unit_roots[:1]:\n'
    '        r = Path(root)\n'
    '        if not r.exists():\n'
    '            continue\n'
    '        try:')]),
 ('P14',
  'identity record shape not validated',
  [('    if not _ident_shape_ok(ident):\n        return UNKNOWN',
    '    if not isinstance(ident, dict) or not ident.get("pid"):\n        return UNKNOWN')]),
 ('P15',
  'empty pin-point list accepted',
  [('    if not mods:\n        raise RuntimeError', '    if mods is None:\n        raise RuntimeError')]),
 ('Z01',
  'a rejecting review counts only if the negative word is on the same line as the sha',
  [('    return any(_NEGATIVE.search(ln) or _NEGATIVE_MORE.search(ln)\n'
    '               or (_VERDICT.match(ln) and ln != ACCEPTANCE_VERDICT_LINE) for ln in lines)',
    '    return any(_names_sha(ln, sha) and (_NEGATIVE.search(ln) or _NEGATIVE_MORE.search(ln)\n'
    '               or (_VERDICT.match(ln) and ln != ACCEPTANCE_VERDICT_LINE)) for ln in lines)')]),
 ('Z02',
  'update units enabled through a *.requires link are not seen',
  [('d.name.endswith((".wants", ".requires", ".upholds"))', 'd.name.endswith((".wants", ".upholds"))')]),
 ('Z03',
  'systemctl is-enabled: enabled-runtime / indirect / alias / linked read as disabled',
  [('        if st in ("enabled", "enabled-runtime", "static", "indirect", "alias", "linked", "linked-runtime"):\n'
    '            return True\n'
    '        if st in ("disabled", "masked", "masked-runtime"):',
    '        if st in ("enabled", "static"):\n'
    '            return True\n'
    '        if st in ("disabled", "masked", "masked-runtime", "enabled-runtime", "indirect", "alias", "linked", '
    '"linked-runtime"):')]),
 ('Z04',
  'a missing unit root ends the search (later roots never read)',
  [('        if not r.exists():\n            continue\n        try:',
    '        if not r.exists():\n            return False\n        try:')]),
 ('Z05',
  "accepting line's first commit looked up by path only (a git mv into the set resets it)",
  [('    line_commits = _commits(repo_root, pick, "HEAD")\n',
    '    line_commits = _commits(repo_root, pick, "HEAD", "--", acc_path)\n')]),
 ('Z06',
  'accepting line in the same commit as the attested blob counts as later',
  [('    if not earlier or not later or earlier == later:\n        return False',
    '    if not earlier or not later:\n        return False\n    if earlier == later:\n        return True')]),
 ('Z07',
  "a failed systemctl query (empty stdout) reads as 'disabled'",
  [('    return r.stdout.strip() or None\n\n\ndef _unit_files',
    '    return r.stdout.strip() or "disabled"\n\n\ndef _unit_files')]),
 ('Z08',
  'only an UNREADABLE cgroup namespace blocks root attestation (a non-initial one passes)',
  [('    if ns_inode("cgroup") != INIT_CGROUP_NS:\n        why.append',
    '    if ns_inode("cgroup") is None:\n        why.append')]),
 ('Z09',
  'launch gate evaluated only for execute / resume (a record passed in launcher mode is ignored)',
  [('    if mode in ("execute", "resume") or launched is not None:', '    if mode in ("execute", "resume"):')]),
 ('Z10',
  'an unreadable /proc view (None) treated as complete',
  [('dt_s <= 0 or proc_view_complete() is not True:', 'dt_s <= 0 or proc_view_complete() is False:')]),
 ('Z11',
  'a bool starttime in a record passes the shape check',
  [('        if v is not None and (not isinstance(v, int) or isinstance(v, bool) or v < 0):',
    '        if v is not None and (not isinstance(v, int) or v < 0):')]),
 ('Q01',
  'negative scan not recursive (a rejection in a review subdirectory ignored); on the combined source the '
  'history-wide veto scan is made non-recursive too, and the HEAD scan drops direct-child TREES only (review 64 '
  'K9 reads blobs with cat-file, so a listed subdirectory would refuse as unavailable evidence instead; review 65 '
  'L4: gitlinks stay in, as in the base; review 68 P1: the non-recursive history listing skips subdirectory TREES, '
  'which the base\'s recursive listing never shows, so the regular-file check still refuses symlinks and gitlinks)',
  [('every = _review_paths(_git(repo_root, "ls-tree", "-r", "-z", "--name-only", "HEAD", "--", '
    'ACCEPTANCE_REVIEW_DIR))',
    'every = _review_paths(_git(repo_root, "ls-tree", "-z", "--name-only", "HEAD", f"{ACCEPTANCE_REVIEW_DIR}/"))\n'
    '    every = every if every is None else [p for p in every\n'
    '                                         if _git(repo_root, "cat-file", "-t", f"HEAD:{p}") != b"tree\\n"]'),
   ('        listing = _git(repo_root, "ls-tree", "-r", "-z", c, "--", ACCEPTANCE_REVIEW_DIR)',
    '        listing = _git(repo_root, "ls-tree", "-z", c, f"{ACCEPTANCE_REVIEW_DIR}/")'),
   ('            if parts[0] not in (b"100644", b"100755"):          # review 68 P1',
    '            if parts[1] == b"tree":\n                continue\n'
    '            if parts[0] not in (b"100644", b"100755"):          # review 68 P1')]),
 ('Q02',
  'accepting set recursive (reviewer scratch can accept)',
  [('tree = _review_paths(_git(repo_root, "ls-tree", "-z", "--name-only", "HEAD", f"{ACCEPTANCE_REVIEW_DIR}/"))',
    'tree = _review_paths(_git(repo_root, "ls-tree", "-r", "-z", "--name-only", "HEAD", "--", '
    'ACCEPTANCE_REVIEW_DIR))')]),
 ('Q03',
  'negative words matched case-sensitively',
  [('_NEGATIVE = re.compile(r"reject|withdraw|not[ _-]?accepted|revoke", re.I)',
    '_NEGATIVE = re.compile(r"REJECT|WITHDRAW|NOT[ _-]?ACCEPTED|REVOKE")')]),
 ('Q04',
  'a second (conflicting) verdict line tolerated (review 64 K2: single site again; a duplicated accepting verdict '
  'line is the direct witness)',
  [('and verdicts == [ACCEPTANCE_VERDICT_LINE]:', 'and ACCEPTANCE_VERDICT_LINE in verdicts:')]),
 ('Q05',
  'accepting file suffix not required',
  [('(name.startswith(ACCEPTANCE_REVIEW_PREFIX) and name.endswith(".md"))',
    'name.startswith(ACCEPTANCE_REVIEW_PREFIX)')]),
 ('Q06',
  'attested commit found by path, not by blob (placeholder attestation filled later)',
  [('    blob_commits = _commits(repo_root, f"--find-object={blob}", "HEAD")\n',
    '    blob_commits = (_commits(repo_root, "HEAD", "--", att_path) or [])[-1:]\n')]),
 ('Q07',
  'systemctl is-active not consulted (a running but disabled update unit reads as off)',
  [('        act = _systemctl_is_active(unit)\n'
    '        if act in ("active", "activating", "reloading"):\n'
    '            return True\n',
    '        act = "inactive"\n')]),
 ('Q08',
  'is-enabled not-found read as disabled without checking the unit files',
  [('            return False if _unit_files(unit, unit_roots) is False else None', '            return False')]),
 ('Q09', 'dangling .wants / .requires link not counted', [('(e.is_symlink() or e.exists())', 'e.exists()')]),
 ('Q10', 'preflight power reading replaced by a constant AC', [('    power = power_source()  ', '    power = AC  ')]),
 ('Q11',
  'preflight free-disk reading replaced by a constant',
  [('    free = free_disk_bytes(repo_path)\n', '    free = 2 ** 40\n')]),
 ('Q12',
  'transient / generator roots dropped from the unit search path',
  [('"/run/systemd/transient",\n              "/run/systemd/generator.early", ', '\n              ')]),
 ('Q13',
  'host_exclusive reports only its first open decision',
  [('                                      for d in ((_GATE_DECISION[k],) if isinstance(_GATE_DECISION[k], str)\n'
    '                                                else _GATE_DECISION[k])})}',
    '                                      for d in ((_GATE_DECISION[k],) if isinstance(_GATE_DECISION[k], str)\n'
    '                                                else _GATE_DECISION[k][:1])})}')]),
 ('CDEX01',
  'Codex Y01: effective memory minimum omits the host MemTotal cap',
  [('    return min([mem["MemTotal"], *[v for v in vals[0] if isinstance(v, int)]])\n'
    '\n'
    '\n'
    'def visible_limit_upper_bound',
    '    return min([v for v in vals[0] if isinstance(v, int)])\n\n\ndef visible_limit_upper_bound')]),
 ('CDEX02',
  'Codex Y02: cgroup headroom uses the maximum instead of the minimum',
  [('    return min(hs) if hs else None', '    return max(hs) if hs else None')]),
 ('CDEX03',
  'Codex Y03: sample order is ignored (both sample-order and pairwise non-increase guards removed)',
  [('        if any(d < 0 for d in steps):\n'
    '            reasons.append("AMBIGUOUS: samples out of order")\n'
    '        elif not steps or max(steps) > MAX_SAMPLE_GAP_S * 10 ** 9:',
    '        if not steps or max(steps) > MAX_SAMPLE_GAP_S * 10 ** 9:'),
   ('            if dm <= 0 or db <= 0:', '            if False:')]),
 ('CDEX04',
  "Codex P01: campaign child ownership ignores the parent's observed starttime identity",
  [('ppid in own_start and (ppid, own_start[ppid]) in snapshot', 'ppid in own_start')]),
 ('CDEX05',
  'Codex P02: a malformed current boot id counts as positive identity evidence',
  [('(boot_id(current_boot) if isinstance(current_boot, str) else None)',
    '(current_boot if isinstance(current_boot, str) else None)')]),
 ('CDEX06',
  'Codex P03: matching malformed boot ids count as positive interval evidence',
  [('    if any(not isinstance(b, str) or boot_id(b) is None for b in boots):',
    '    if any(not b for b in boots):')]),
 ('CDEX07',
  'Codex P04: nonfinite CPU window duration is accepted',
  [('or isinstance(dt_s, bool) or abs(dt_s) > sys.float_info.max or not math.isfinite(dt_s)',
    'or isinstance(dt_s, bool) or abs(dt_s) > sys.float_info.max')]),
 ('CDEX08',
  'Codex P05: malformed NSpid entries count as a complete proc view',
  [('    if len(nspid) != 1 or not re.fullmatch(r"0*[1-9][0-9]*", nspid[0]):\n        return None\n', '')]),
 ('CDEX09',
  'Codex F01: clock-pair checks ignore intermediate observations and use only the endpoints',
  [('        pairs = list(zip(seq, seq[1:]))\n        if len(seq) > 2:\n            pairs.append((start, end))\n',
    '        pairs = [(start, end)]\n')]),
 ('CDEX10',
  'Codex F02: suspend counter checks ignore intermediate observations and use only the endpoints',
  [('    counts = [x.get("suspend_success") if isinstance(x, dict) else None for x in seq]',
    '    counts = [x.get("suspend_success") if isinstance(x, dict) else None for x in (start, end)]'),
   ('    if any(not isinstance(x, dict) or type(x.get("suspend_success")) is not int\n'
    '           or x["suspend_success"] < 0 for x in seq):',
    '    if any(not isinstance(x, dict) or type(x.get("suspend_success")) is not int\n'
    '           or x["suspend_success"] < 0 for x in (start, end)):')]),
 ('CDEX11',
  'Codex F03: malformed mount IDs and device numbers bypass numeric metadata validation',
  [('    if not re.fullmatch(r"0*[1-9][0-9]*", f[0]) or not re.fullmatch(r"0*[1-9][0-9]*", f[1]) \\\n'
    '            or not re.fullmatch(r"[0-9]+:[0-9]+", f[2]):\n'
    '        return None\n',
    '')]),
 ('CDEX12',
  'Codex F04: the first NSpid field is trusted when duplicate NSpid records disagree',
  [('    if len(nspid_fields) != 1:', '    if not nspid_fields:')]),
 ('CDEX13',
  'Codex F05: multiple starttime identities for one PID are accepted in a single CPU snapshot',
  [('        if len({key[0] for key in snapshot}) != len(snapshot):\n            return None\n', '')]),
 ('CDEX14',
  "Codex F06: payload adjoining NSpid's colon is discarded before validation",
  [('    nspid_fields = [ln.partition(":")[2].split() for ln in st.splitlines() if ln.startswith("NSpid:")]',
    '    nspid_fields = [ln.split()[1:] for ln in st.splitlines() if ln.startswith("NSpid:")]')]),
 ('CDEX15',
  'Codex F07: malformed attestation/reference paths escape as subprocess argument exceptions',
  [('                           stdin=subprocess.DEVNULL, env=_git_env())\n'
    '    except (OSError, subprocess.SubprocessError, ValueError, UnicodeError):\n        return None\n',
    '                           stdin=subprocess.DEVNULL, env=_git_env())\n'
    '    except (OSError, subprocess.SubprocessError):\n        return None\n')]),
 ('CDEX16',
  'Combined: unknown activity plus disabled state is not positive inactive evidence',
  [('            return False if act in ("inactive", "failed") else None', '            return False')]),
 ('R5SYNC01',
  'Combined R5 repair: complete negative-review scan includes nonASCII, tab and newline path names',
  [('    for path in every:\n',
    '    for path in (p for p in every if p.isascii() and "\\t" not in p and "\\n" not in p):\n')]),
 ('R5SYNC02',
  'Combined R5 repair: unavailable recursive listing cannot be replaced by an independent accepting read; '
  'on the combined source unavailable review history is ignored too, and the review-64 mode check tolerates a path '
  'missing from the (emptied) exact listing, since both would otherwise refuse the same way',
  [('    if history is None:\n        return [], ["UNAVAILABLE: review history unreadable, not UTF-8 or not regular files"]\n',
    '    if history is None:\n        history = []\n'),
   ('        if entries[path][:2] not in (("100644", "blob"), ("100755", "blob")):',
    '        if path in entries and entries[path][:2] not in (("100644", "blob"), ("100755", "blob")):'),
   ('    if tree is None or every is None:\n'
    '        return [], ["UNAVAILABLE: acceptance review listing unreadable or malformed"]\n',
    '    if tree is None:\n'
    '        return [], ["UNAVAILABLE: acceptance review listing unreadable or malformed"]\n'
    '    every = every or []\n'),
   ('        if path not in records:\n'
    '            return [], [f"UNAVAILABLE: accepting review absent from recursive listing: {path}"]\n'
    '        lines = records[path]\n',
    '        lines = records.get(path)\n'
    '        if lines is None:\n'
    '            data = _git(repo_root, "cat-file", "blob", f"HEAD:{path}") or b""\n'
    '            lines = data.decode("utf-8", errors="replace").splitlines()\n')]),
 ('R5SYNC03',
  'Combined R5 repair: unavailable recursive review blob cannot be skipped in the veto scan',
  [('        if data is None:\n            return [], [f"UNAVAILABLE: review blob unreadable: {path}"]\n',
    '        if data is None:\n            continue\n')]),
 ('R5SYNC04',
  'Combined R5 repair: unknown supervisor state cannot imply filesystem-only update inactivity',
  [('    if supervisor is not False:\n        return None\n', '')]),
 ('RV01',
  'Review 63 W01: only the newest accepting-line commit is ordered after the blob',
  [('    return all(_strictly_after(repo_root, b, c) for b in blob_commits for c in line_commits)',
    '    return all(_strictly_after(repo_root, b, c) for b in blob_commits for c in line_commits[:1])')]),
 ('RV02',
  'Review 63 W02: an upper-case cmdline digest passes the record shape check',
  [('re.fullmatch(r"[0-9a-f]{64}", c) is not None)', 're.fullmatch(r"[0-9a-fA-F]{64}", c) is not None)')]),
 ('RV03',
  'Review 63 W03 on the combined source: an upper-case boot id passes the record shape check and the recorded-boot '
  'check (the combined source re-validates it, so W03 alone is equivalent there)',
  [('    if b is not None and (not isinstance(b, str) or not _BOOT_ID.fullmatch(b)):',
    '    if b is not None and (not isinstance(b, str) or not _BOOT_ID.fullmatch(b.lower())):'),
   ('(not isinstance(recorded_boot, str) or boot_id(recorded_boot) is None):',
    '(not isinstance(recorded_boot, str) or boot_id(recorded_boot.lower()) is None):')]),
 ('RV04',
  'Review 63 W04: a dangling unit link in a root is not a unit file for not-found',
  [('        found |= f.is_symlink() or f.exists()', '        found |= f.exists()')]),
 ('RV05',
  'Review 63 W05: a unit root that is not a directory is skipped for not-found',
  [('        if not r.is_dir():\n            return None\n        f = r / unit\n        found',
    '        if not r.is_dir():\n            continue\n        f = r / unit\n        found')]),
 ('RV06',
  "Review 63 W06: 'revoke' is not a negative word",
  [('|not[ _-]?accepted|revoke", re.I)', '|not[ _-]?accepted", re.I)')]),
 ('RV07',
  'Review 63 W07: only the last root decides whether a unit file exists',
  [('        found |= f.is_symlink() or f.exists()', '        found = f.is_symlink() or f.exists()')]),
 ('RV08',
  'Review 63 H1: merge commits invisible to the blob / line order searches',
  [('               "--diff-merges=separate", *args)', '               *args)')]),
 ('RV09',
  'Review 63 H3: a rejection removed from HEAD no longer vetoes',
  [('    rej += [f"HISTORICAL: {path} (blob {oid[:12]})" for oid, path, lines in history if _vetoing(lines, sha)]\n',
    '')]),
 ('RV10',
  'Review 63 H3: unreadable review history counts as no historical rejection',
  [('    if history is None:\n        return [], ["UNAVAILABLE: review history unreadable, not UTF-8 or not regular files"]\n',
    '    if history is None:\n        history = []\n')]),
 ('RV11',
  'Review 63 H3: side branches simplified away from the historical review scan',
  [('    commits = _git(repo_root, "rev-list", "--full-history", "HEAD", "--", ACCEPTANCE_REVIEW_DIR)',
    '    commits = _git(repo_root, "rev-list", "HEAD", "--", ACCEPTANCE_REVIEW_DIR)')]),
 ('RV12',
  'Review 63 H3: only the exact lower-case full sha names the attestation',
  [('    return sha in line.lower() or any(sha.startswith(t.lower()) for t in _HEX_TOKEN.findall(line))',
    '    return sha in line')]),
 ('RV13',
  'Review 63 H3: refused / unaccepted / declined / needs revision / veto are not negative',
  [('    return any(_NEGATIVE.search(ln) or _NEGATIVE_MORE.search(ln)\n', '    return any(_NEGATIVE.search(ln)\n')]),
 ('RV14',
  'Review 63 H3: a verdict other than the accepting one in a review naming the sha is not a veto',
  [('               or (_VERDICT.match(ln) and ln != ACCEPTANCE_VERDICT_LINE) for ln in lines)',
    '               for ln in lines)')]),
 ('RV15',
  'Review 63 H7: only lines starting with verdict: are verdict lines',
  [('_VERDICT = re.compile(r"(?i:.*\\bverdict\\b)|\\s*[A-Z][A-Z0-9_]*\\s*:\\s*[A-Z][A-Z0-9_]*\\s*$")',
    '_VERDICT = re.compile(r"^\\s*verdict\\s*:", re.I)')]),
 ('RV16',
  'Review 63 H6: *.upholds links do not enable a unit',
  [('d.name.endswith((".wants", ".requires", ".upholds"))', 'd.name.endswith((".wants", ".requires"))')]),
 ('RV17',
  'Review 63 H6: a lower-precedence mask overrides a real higher-precedence unit file',
  [('        if first is None and (f.is_symlink() or f.exists()):',
    '        if f.is_symlink() and os.path.realpath(f) == "/dev/null":')]), ('RV18',
  'Review 64 RW1: an empty set of blob commits no longer refuses (all() over nothing)',
  [('    if not blob_commits or not line_commits:\n        return False\n',
    '    if not line_commits:\n        return False\n')]),
 ('RV19',
  'Review 64 RW2: a dangling highest-precedence unit link no longer shadows a lower mask',
  [('        if first is None and (f.is_symlink() or f.exists()):',
    '        if first is None and f.exists():')]),
 ('RV20',
  'Review 64 RW3: a non-UTF-8 historical review path is skipped',
  [('                seen.setdefault(parts[2].decode("ascii"), name.decode("utf-8", errors="strict"))\n'
    '            except UnicodeDecodeError:\n                return None\n',
    '                seen.setdefault(parts[2].decode("ascii"), name.decode("utf-8", errors="strict"))\n'
    '            except UnicodeDecodeError:\n                continue\n')]),
 ('RV21',
  'Review 64 RW4: the accepting verdict line may repeat',
  [('and verdicts == [ACCEPTANCE_VERDICT_LINE]:', 'and set(verdicts) == {ACCEPTANCE_VERDICT_LINE}:')]),
 ('RV22',
  'Review 64 RW6: accepting-line commits searched on the first-parent chain only',
  [('    line_commits = _commits(repo_root, pick, "HEAD")\n',
    '    line_commits = _commits(repo_root, pick, "--first-parent", "HEAD")\n')]),
 ('RV23',
  'Review 64 K1: the reading repository may hide the root / boundary commit (log.showRoot not forced)',
  [('_GIT_ISOLATION = ("--no-replace-objects", "-c", "log.showRoot=true",\n',
    '_GIT_ISOLATION = ("--no-replace-objects",\n')]),
 ('RV24',
  'Review 64 K1: a textconv driver may rewrite what the pickaxe searches',
  [('"--no-patch", "--no-textconv", "--no-ext-diff",', '"--no-patch", "--no-ext-diff",')]),
 ('RV25',
  'Review 64 K4: a full sha inside a longer hex run no longer names the attestation',
  [('    return sha in line.lower() or any(', '    return any(')]),
 ('RV26',
  'Review 64 K7 / review 68 P1: a symlink under the review directory counts, as an accepting review at HEAD and in '
  'the history scan (review 69 S3: the K7 HEAD mode check alone is unreachable since P1, so this witnesses the P1 '
  'symlink refusal, like RV59)',
  [('        if entries[path][:2] not in (("100644", "blob"), ("100755", "blob")):\n            continue',
    '        if entries[path][:2] not in (("100644", "blob"), ("100755", "blob"), ("120000", "blob")):\n'
    '            continue'),
   ('            if parts[0] not in (b"100644", b"100755"):          # review 68 P1',
    '            if parts[0] not in (b"100644", b"100755", b"120000"):  # review 68 P1')]),
 ('RV27',
  'Review 64 K9: review blobs read with git show (a range-like name is parsed as a revision range)',
  [('        data = _git(repo_root, "cat-file", "blob", f"HEAD:{path}")    # review 64 K9: never a revision range\n',
    '        data = _git(repo_root, "show", f"HEAD:{path}")\n')]),
 ('RV28',
  'Review 64 K9: an OSError reading a unit root escapes auto_update_settings',
  [('        except OSError:                                         # review 64 K9: e.g. a root listable, not searchable\n'
    '            units[u] = None',
    '        except ZeroDivisionError:\n            units[u] = None')]),
 ('RV29',
  'Review 64 follow-up: the history-completeness guard removed (a shallow clone hides a deleted rejection)',
  [('    if not _history_complete(repo_root):\n'
    '        return [], ["UNAVAILABLE: history completeness not established (shallow clone or unreadable)"]\n', '')]),
 ('RV30',
  'Review 64 follow-up: an unreadable completeness answer counts as complete history',
  [('    if _git(repo_root, "rev-parse", "--is-shallow-repository") != b"false\\n":',
    '    if _git(repo_root, "rev-parse", "--is-shallow-repository") == b"true\\n":')]),
 ('RV31',
  'Review 65 L1: no full fsck (a rewritten object hides a deleted rejection)',
  [('    return _git(repo_root, "fsck", "--full", "--strict", "--no-dangling", "--no-progress") is not None',
    '    return True')]),
 ('RV32',
  'Review 65 L1 / L6: repository-local fsck.* and promisor / partial-clone keys accepted',
  [('    if names is None or any(_LOCAL_CONFIG_REFUSED.match(n) for n in names.decode("utf-8", "replace").lower()\n'
    '                            .split("\\0") if n):',
    '    if names is None:')]),
 ('RV33',
  'Review 65 RX1: replace objects honoured by the reads',
  [('_GIT_ISOLATION = ("--no-replace-objects", "-c", "log.showRoot=true",\n',
    '_GIT_ISOLATION = ("-c", "log.showRoot=true",\n')]),
 ('RV34',
  'Review 65 RX2: info/grafts honoured by the reads',
  [('               GIT_GRAFT_FILE=os.devnull, GIT_NO_LAZY_FETCH="1")', '               GIT_NO_LAZY_FETCH="1")')]),
 ('RV35',
  'Review 65 RX5: the ancestry check runs without the isolation',
  [('["git", "-C", str(repo_root), *_GIT_ISOLATION, "merge-base", "--is-ancestor", earlier,\n'
    '                            later], capture_output=True, timeout=60, stdin=subprocess.DEVNULL, env=_git_env())',
    '["git", "-C", str(repo_root), "merge-base", "--is-ancestor", earlier,\n'
    '                            later], capture_output=True, timeout=60, stdin=subprocess.DEVNULL)')]),
 ('RV36',
  'Review 65 RX3: a glued full sha is named only in lower case',
  [('    return sha in line.lower() or any(', '    return sha in line or any(')]),
 ('RV37',
  'Review 65 RX4: only PermissionError from a unit root becomes unknown',
  [('        except OSError:                                         # review 64 K9: e.g. a root listable, not searchable',
    '        except PermissionError:')]),
 ('RV38',
  'Review 65 RX6: the exact-path listing need not cover every reviewed path',
  [('    if entries is None or set(entries) != set(every):', '    if entries is None:')]),
 ('RV39',
  'Review 65 L6: partial-clone / promisor keys accepted by the precondition (review 66 M4: the lazy-fetch block is '
  'RV45, a separate mutant)',
  [('_LOCAL_CONFIG_REFUSED = re.compile(r"fsck\\.|extensions\\.partialclone$|remote\\..*\\.(promisor|partialclonefilter)$")',
    '_LOCAL_CONFIG_REFUSED = re.compile(r"fsck\\.")')]),
 ('RV40',
  'Review 65 L3: the caller environment (GIT_DIR, object directories, ...) passes through to git',
  [('    env = {k: v for k, v in os.environ.items() if k in _GIT_ENV_KEEP}', '    env = dict(os.environ)')]),
 ('RV41',
  'Review 65 L7: the attested blob is resolved with rev-parse HEAD:<path> (range parsing)',
  [('    entry = (_tree_entries(repo_root, [att_path]) or {}).get(att_path)  # review 65 L7: never a revision range\n'
    '    blob = entry[2] if entry and entry[:2] in (("100644", "blob"), ("100755", "blob")) else ""\n',
    '    blob = (_git(repo_root, "rev-parse", f"HEAD:{att_path}") or b"").decode().strip()\n')]),
 ('RV42',
  'Review 65 L7: a deeply nested attestation raises out of attestation_valid',
  [('    except RecursionError:                                      # review 65 L7: deeply nested JSON\n'
    '        return None, ["attestation JSON nested too deeply"]\n', '')]), ('RV43',
  'Review 66 M1: the commit-graph (and its unverified changed-path Bloom filters) is read',
  [('                  "-c", "core.commitGraph=false",               # review 66 M1: no graph data (parents or Bloom filters)\n',
    '')]),
 ('RV44',
  'Review 66 M2: a repository-configured fsmonitor command may run (fsck reads the index)',
  [('                  "-c", "core.fsmonitor=false",                 # review 66 M2: no repository-configured fsmonitor\n',
    '')]),
 ('RV45',
  'Review 66 M4 (RY1): missing objects may be fetched lazily (GIT_NO_LAZY_FETCH dropped)',
  [('               GIT_GRAFT_FILE=os.devnull, GIT_NO_LAZY_FETCH="1")', '               GIT_GRAFT_FILE=os.devnull)')]),
 ('RV46',
  'Review 66 M4 (RY3): the attested entry need not be a regular file',
  [('    blob = entry[2] if entry and entry[:2] in (("100644", "blob"), ("100755", "blob")) else ""',
    '    blob = entry[2] if entry else ""')]),
 ('RV47',
  'Review 66 M4 (RY5): an unreadable configuration listing counts as clean',
  [('    if names is None or any(', '    if names is not None and any(')]),
 ('RV48',
  'Review 66 M3: configuration keys read from .git/config only (no includes, no worktree scope)',
  [('"config", "--includes", "--name-only", "--list", "-z")', '"config", "--local", "--name-only", "--list", "-z")')]),
 ('RV49',
  'Review 67 N1: fsck without --strict (warning-class tree names, e.g. fullPathname, pass the precondition)',
  [('"fsck", "--full", "--strict", "--no-dangling"', '"fsck", "--full", "--no-dangling"')]),
 ('RV50',
  'Review 67 N2: `git log` honours the repository\'s log.showSignature (a configured signature program runs)',
  [('                  "-c", "log.showSignature=false",              # review 67 N2: no signature program from `git log`\n',
    '')]),
 ('RV51',
  'Review 67 N4: the global attributes file under HOME is read',
  [('                  "-c", f"core.attributesFile={os.devnull}")    # review 67 N4: no global attributes file via HOME',
    '                  )')]),
 ('RV52',
  'Review 67 N5 (RZ1): the commit-graph\'s parent data is read (only changed-path Bloom filters off)',
  [('"-c", "core.commitGraph=false",               # review 66 M1', '"-c", "commitGraph.readChangedPaths=false",   # review 66 M1')]),
 ('RV53',
  'Review 67 N5 (RZ4): extensions.partialClone is not refused',
  [('re.compile(r"fsck\\.|extensions\\.partialclone$|remote', 're.compile(r"fsck\\.|remote')]),
 ('RV54',
  'Review 67 N5 (RZ5): promisor keys are refused only for a remote named origin',
  [('|remote\\..*\\.(promisor|partialclonefilter)$")', '|remote\\.origin\\.(promisor|partialclonefilter)$")')]),
 ('RV55',
  'Review 68 P3 (RA3): signature programs are off only for the --find-object search; the -S search honours the '
  'repository',
  [('                  "-c", "log.showSignature=false",              # review 67 N2: no signature program from `git log`\n',
    ''),
   ('    blob_commits = _commits(repo_root, f"--find-object={blob}", "HEAD")',
    '    blob_commits = _commits(repo_root, "--no-show-signature", f"--find-object={blob}", "HEAD")')]),
 ('RV56',
  'Review 68 P4 (RA2): strict fsck narrowed to the one tested message (fullPathname)',
  [('    return _git(repo_root, "fsck", "--full", "--strict", "--no-dangling", "--no-progress") is not None',
    '    return _git(repo_root, "-c", "fsck.fullPathname=error", "fsck", "--full", "--no-dangling", "--no-progress") '
    'is not None')]),
 ('RV57',
  'Review 68 P4 (RA4): the system attributes file is read (GIT_ATTR_NOSYSTEM dropped)',
  [('GIT_CONFIG_GLOBAL=os.devnull, GIT_ATTR_NOSYSTEM="1",', 'GIT_CONFIG_GLOBAL=os.devnull,')]),
 ('RV58',
  'Review 68 (RA1): the fsck-key refusal narrowed to fsck.skipList and fsck.missingEmail',
  [('re.compile(r"fsck\\.|extensions', 're.compile(r"fsck\\.(skiplist|missingemail)$|extensions')]),
 ('RV59',
  'Review 68 P1: a symlink or gitlink under the review directory in the history is read as its target text or '
  'skipped',
  [('            if parts[0] not in (b"100644", b"100755"):          # review 68 P1: a symlink or gitlink under the\n'
    '                return None                                     # directory is not a review file; unavailable\n',
    '            if parts[1] != b"blob":\n                continue\n')]),
 ('RV60',
  'Review 68 P1: the review directory or an ancestor may be a symlink (or other non-directory) in some commit',
  [('    if not _review_dir_is_a_directory(repo_root):', '    if False:')]),
 ('RV61',
  'Review 69 S2 (RB1): intermediate ancestors of the review directory are not checked',
  [('            if mode != b"40000":\n                return False\n            level.add(oid)\n',
    '            if mode != b"40000":\n                if depth in (0, len(parts) - 1):\n                    return False\n'
    '                continue\n            level.add(oid)\n')]),
 ('RV62',
  'Review 69 S2 (RB2): the ancestor check walks only the first-parent chain',
  [('    commits = _git(repo_root, "rev-list", "HEAD")', '    commits = _git(repo_root, "rev-list", "--first-parent", "HEAD")')]),
 ('RV63',
  'Review 69 S1 (RB4): a gitlink at the review directory or an ancestor is read as a directory (not descended)',
  [('            if mode != b"40000":\n                return False\n            level.add(oid)\n',
    '            if mode == b"160000":\n                continue\n'
    '            if mode != b"40000":\n                return False\n            level.add(oid)\n')])]

MUTANT_GROUP_SIZES = {"M": 32, "R": 10, "X": 9, "N": 14, "Y": 9, "P": 15, "Z": 11, "Q": 13, "CDEX": 16, "R5SYNC": 4, "RV": 63}

# A kill must include at least one named direct witness for the weakened property.
# These method names are unique across the full discovered suite. They are evidence
# attribution, not a selector: every baseline and mutant runs the entire suite.
PROPERTY_WITNESSES = {}
for _method, _ids in {
    "test_failed_readings_are_unknown_never_dead": "M01 M02",
    "test_unrecorded_fields": "M03",
    "test_zombie_is_never_proof_of_death": "M04",
    "test_positive_death_evidence": "M05",
    "test_power_classes": "M06",
    "test_partial_chain_never_numeric": "M07 M21",
    "test_missing_channels_never_clean": "M08",
    "test_pause_channel_is_ambiguous": "M09",
    "test_suspend_detected_just_above_tolerance": "M10",
    "test_all_favourable_still_blocked": "M11",
    "test_forged_or_unaccepted_attestations_refused": "M12 M26 R02 N03 Y05",
    "test_lifetime_gates_open_while_undecided": "M13 N01 Y01 Y08",
    "test_positive_evidence_only": "M14 X03",
    "test_launched_by_systemd_requires_everything": "M15 X07",
    "test_stale_tmp_is_a_named_state": "M16",
    "test_unreadable_pins_never_match": "M17",
    "test_window_not_lifetime_and_reuse_and_birth": "M18 M24",
    "test_empty_cmdline_is_a_failed_read": "M19",
    "test_unknowns_never_pass_and_are_reported": "M20 Q10 Q11 Q13",
    "test_namespace_mismatch_is_unknown": "M22",
    "test_failed_or_unknown_supplies_are_unknown": "M23 R01",
    "test_reference_digest_must_match_the_committed_file": "M25",
    "test_v2_root_and_memory_high": "M27 CDEX02",
    "test_v1_needs_root_attestation_for_a_number": "M28",
    "test_launch_gate_uses_a_fresh_reading": "M29 N13 P08 P09 Y07 Z09",
    "test_pin_set_covers_libm_libc_loader": "M30 R06",
    "test_view_is_read_not_assumed": "M31 Z10",
    "test_no_reading_or_unsafe_inputs_fail_closed": "M32",
    "test_fsyncs_file_then_directory": "R03 R08",
    "test_constants_equal_the_candidates": "R04 R09",
    "test_no_name_or_path_allowlist": "R05",
    "test_live_task_states_are_alive": "R07",
    "test_power_checked_at_every_sample": "R10",
    "test_proc_view": "X01 X02 N06",
    "test_monotonic_ahead_of_boottime_and_absent_samples": "X04 X06",
    "test_read_back_mismatch_is_detected": "X05",
    "test_large_v1_limit_is_a_limit": "X08",
    "test_unknown_interpreter_package_never_matches": "X09",
    "test_acceptance_is_found_not_named": "N02 P01 P02 P03 P04 Y03 Z01 Q01 Q02 Q03 Q04 Q05 RV21",
    "test_reference_rejects_extra_fields_even_if_otherwise_valid": "N04",
    "test_root_attestation_is_derived_never_asserted": "N05 P05 P06 Y04 Z08",
    "test_boot_id_must_be_valid": "N07",
    "test_exited_in_window_is_reported": "N08",
    "test_unreadable_existing_process_fails_the_snapshot": "N09",
    "test_reused_campaign_pid_does_not_exempt_children": "N10",
    "test_unrecorded_namespace_never_proves_death": "N11",
    "test_required_members_and_pin_point": "N12 P15 Y06",
    "test_unrecognised_battery_status_is_unknown": "N14",
    "test_exited_child_of_reused_campaign_pid_is_reported": "Y02",
    "test_cgroup_resources_whole_chain": "Y09",
    "test_decided_is_validated": "P07",
    "test_no_reviewed_journal_reader_never_clean": "P10",
    "test_file_mode_edge_cases": "Z02 Z04 Q09 Q12",
    "test_failed_systemctl_query_is_no_reading": "Z07",
    "test_unit_enabled_from_every_root": "P11 P12 P13",
    "test_malformed_records_prove_nothing": "P14 Z11",
    "test_systemctl_path_when_systemd_is_pid1": "Z03 Q07 Q08",
    "test_accepting_line_must_post_date_the_attested_blob": "Z05 Z06 Q06",
    "test_host_memtotal_caps_every_larger_cgroup_limit": "CDEX01",
    "test_reversed_sample_order_is_refused": "CDEX03",
    "test_missing_and_reused_parent_identity_cannot_exempt_child": "CDEX04",
    "test_current_boot_requires_a_recognized_string": "CDEX05",
    "test_interval_boot_schema_and_nonrecord_samples": "CDEX06",
    "test_duration_threshold_frequency_schemas": "CDEX07",
    "test_whole_colon_payload_and_ascii_schema": "CDEX08 CDEX14",
    "test_middle_clock_excursion_not_hidden_by_matching_endpoints": "CDEX09",
    "test_every_suspend_counter_and_reset_is_checked": "CDEX10",
    "test_mount_metadata_and_duplicate_mounts_refused": "CDEX11",
    "test_duplicate_fields_both_orders_and_identical_duplicates_refused": "CDEX12",
    "test_duplicate_pid_in_either_snapshot_or_own_set_is_refused": "CDEX13",
    "test_git_malformed_args_and_subprocess_failures_return_none": "CDEX15",
    "test_unavailable_or_unrecognized_activity_cannot_be_disabled": "CDEX16",
    "test_ascii_acceptance_control_and_nonascii_tab_newline_veto_paths": "R5SYNC01",
    "test_unavailable_recursive_listing_or_veto_blob_refuses_verification": "R5SYNC02 R5SYNC03",
    "test_supervisor_true_false_unknown_and_update_composition": "R5SYNC04",
    "test_review63_order_every_commit_merges_and_side_branches": "RV01 RV08",
    "test_review63_shape_rejects_uppercase_digest_and_boot_id": "RV02 RV03",
    "test_review63_not_found_unit_file_search_complete": "RV04 RV05 RV07",
    "test_review63_veto_words_and_references": "RV06 RV12 RV13 RV14",
    "test_review63_rejection_is_permanent": "RV09 RV10 RV11",
    "test_review63_verdict_like_lines_refuse_acceptance": "RV15",
    "test_review63_upholds_and_mask_precedence": "RV16 RV17",
    "test_review64_missing_blob_commits_refuse": "RV18",
    "test_review64_shallow_history_refuses_deleted_preboundary_rejection": "RV29 RV30",
    "test_review65_forged_graph_and_rewritten_object_refuse": "RV31 RV52",
    "test_review65_local_fsck_or_promisor_configuration_refuses": "RV32 RV53 RV54 RV58",
    "test_review65_replace_refs_and_grafts_are_ignored": "RV33 RV34 RV35",
    "test_review65_short_exact_listing_refuses": "RV38",
    "test_review65_partial_clone_runs_no_configured_command": "RV39",
    "test_review65_caller_git_environment_is_ignored": "RV40",
    "test_review65_range_like_attestation_path_and_deep_json": "RV41 RV42",
    "test_review66_forged_bloom_filter_is_never_read": "RV43",
    "test_review66_fsmonitor_command_never_runs": "RV44",
    "test_review66_lazy_fetch_blocked_even_past_the_precondition": "RV45",
    "test_review66_symlink_attestation_is_refused": "RV46",
    "test_review66_unreadable_configuration_listing_refuses": "RV47",
    "test_review66_configuration_in_includes_and_worktree_scope_refuses": "RV48",
    "test_review67_warning_class_tree_name_refuses": "RV49",
    "test_review67_signature_program_never_runs": "RV50 RV55",
    "test_review67_global_attributes_file_is_not_read": "RV51",
    "test_review68_non_directory_review_paths_refuse": "RV59 RV60",
    "test_review68_strict_fsck_and_forced_git_environment": "RV56 RV57",
    "test_review69_ancestor_entries_are_read_by_mode": "RV61 RV62 RV63",
    "test_review64_dangling_top_entry_shadows_lower_mask": "RV19",
    "test_review64_non_utf8_historical_review_path_refuses": "RV20",
    "test_review64_side_branch_acceptance_synced_and_merged_refuses": "RV22",
    "test_review64_order_ignores_reading_configuration": "RV23 RV24",
    "test_review64_sha_inside_longer_hex_run_still_names_it": "RV25 RV36",
    "test_review64_symlink_is_not_an_accepting_review": "RV26",
    "test_review64_range_like_review_names_do_not_block": "RV27",
    "test_review64_unreadable_unit_root_is_unknown_not_a_crash": "RV28 RV37",
}.items():
    for _mid in _ids.split():
        PROPERTY_WITNESSES.setdefault(_mid, []).append(_method)
del _method, _ids, _mid


def _text(value) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""


_RUNNER = r'''
import json, sys, traceback, unittest
from pathlib import Path

class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = []
        self.executed = []
    def startTest(self, test):
        self.executed.append(test.id())
        super().startTest(test)
    def record(self, kind, test, error, parent=None):
        self.events.append({"kind": kind, "test_id": test.id(),
                            "parent_test_id": (parent if parent is not None else test).id(),
                            "description": self.getDescription(test).splitlines()[0],
                            "exception_type": error[0].__module__ + "." + error[0].__qualname__,
                            "is_exact_assertion_error": error[0] is AssertionError,
                            "traceback_frames": [{"file": f.filename, "line": f.lineno, "function": f.name}
                                                 for f in traceback.extract_tb(error[2])]})
    def addFailure(self, test, error):
        self.record("failure", test, error)
        super().addFailure(test, error)
    def addError(self, test, error):
        self.record("error", test, error)
        super().addError(test, error)
    def addSubTest(self, test, subtest, error):
        if error is not None:
            self.record("failure" if issubclass(error[0], test.failureException) else "error", subtest, error, test)
        super().addSubTest(test, subtest, error)

sys.path.insert(0, sys.argv[1])
suite = (unittest.defaultTestLoader.loadTestsFromNames(sys.argv[3:]) if len(sys.argv) > 3
         else unittest.defaultTestLoader.discover(sys.argv[1]))
result = unittest.TextTestRunner(verbosity=2, resultclass=RecordedResult).run(suite)
metadata = {"schema": "CELL308_CONTROLLED_UNITTEST_RESULT_V1", "ran": result.testsRun,
            "successful": result.wasSuccessful(), "events": result.events,
            "executed_test_ids": result.executed,
            "skipped": len(result.skipped), "expected_failures": len(result.expectedFailures),
            "unexpected_successes": len(result.unexpectedSuccesses)}
Path(sys.argv[2]).write_text(json.dumps(metadata) + "\n")
sys.exit(0 if result.wasSuccessful() else 1)
'''


def _suite_record(command: list[str], env: dict, *, returncode: int | None, stdout: str, stderr: str,
                  elapsed_s: float, timed_out: bool = False, launch_error: str | None = None,
                  result_metadata: dict | None = None, result_metadata_raw: str | None = None) -> dict:
    """The controlled runner supplies exception types; raw reports must agree with its metadata."""
    counts = re.findall(r"^Ran (\d+) tests? in [0-9.]+s$", stderr, flags=re.MULTILINE)
    summaries = re.findall(r"^(?:OK(?: \([^\n]*\))?|FAILED \([^\n]*\))$", stderr, flags=re.MULTILINE)
    summary = summaries[0] if len(summaries) == 1 else None
    ran = int(counts[0]) if len(counts) == 1 else None
    tokens = re.findall(r"(failures|errors|skipped|expected failures|unexpected successes)=(\d+)", summary or "")
    tally = {name: int(value) for name, value in tokens}
    failures, errors, skipped = (tally.get(k, 0) for k in ("failures", "errors", "skipped"))
    failure_names = re.findall(r"^FAIL: (.+)$", stderr, flags=re.MULTILINE)
    error_names = re.findall(r"^ERROR: (.+)$", stderr, flags=re.MULTILINE)
    failure_blocks = re.findall(r"^FAIL: ([^\n]+)\n(.*?)(?=^={10,}$|^-{10,}\nRan |\Z)",
                                stderr, flags=re.MULTILINE | re.DOTALL)
    invalid = []
    assertion_names = []
    metadata_valid = (isinstance(result_metadata, dict)
                      and result_metadata.get("schema") == "CELL308_CONTROLLED_UNITTEST_RESULT_V1"
                      and type(result_metadata.get("ran")) is int
                      and type(result_metadata.get("successful")) is bool
                      and isinstance(result_metadata.get("events"), list)
                      and isinstance(result_metadata.get("executed_test_ids"), list)
                      and all(isinstance(test_id, str) and test_id for test_id in result_metadata["executed_test_ids"])
                      and all(type(result_metadata.get(k)) is int and result_metadata[k] >= 0
                              for k in ("skipped", "expected_failures", "unexpected_successes")))
    events = result_metadata["events"] if metadata_valid else []
    if any(not isinstance(event, dict) or event.get("kind") not in ("failure", "error")
           or any(not isinstance(event.get(k), str) or not event[k]
                  for k in ("test_id", "parent_test_id", "description", "exception_type"))
           or type(event.get("is_exact_assertion_error")) is not bool
           or not isinstance(event.get("traceback_frames"), list) or not event["traceback_frames"]
           or any(not isinstance(frame, dict) or type(frame.get("line")) is not int or frame["line"] <= 0
                  or any(not isinstance(frame.get(k), str) or not frame[k] for k in ("file", "function"))
                  for frame in event["traceback_frames"]) for event in events):
        metadata_valid = False
    if not metadata_valid:
        invalid.append("MISSING_OR_INVALID_CONTROLLED_RUNNER_METADATA")
    else:
        executed = result_metadata["executed_test_ids"]
        failed = [event for event in events if event["kind"] == "failure"]
        errored = [event for event in events if event["kind"] == "error"]
        if (result_metadata["ran"] != ran or len(executed) != ran
                or result_metadata["successful"] != (returncode == 0)
                or [event["description"] for event in failed] != failure_names
                or [event["description"] for event in errored] != error_names
                or len(failed) != failures or len(errored) != errors
                or result_metadata["skipped"] != skipped
                or result_metadata["expected_failures"] != tally.get("expected failures", 0)
                or result_metadata["unexpected_successes"] != tally.get("unexpected successes", 0)):
            invalid.append("CONTROLLED_METADATA_AND_REPORT_DISAGREE")
        if len(set(executed)) != len(executed):
            invalid.append("DUPLICATE_EXECUTED_TEST_ID")
        if any(event["parent_test_id"] not in executed for event in events):
            invalid.append("OUTCOME_WITHOUT_EXECUTED_PARENT_TEST")
        for event in events:
            identity = re.fullmatch(r"([^\s()]+) \(([^()\n]+)\)([^\n]*)", event["description"])
            if identity is None:
                invalid.append("OUTCOME_IDENTITY_AND_DESCRIPTION_DISAGREE")
                break
            method, owner, suffix = identity.groups()
            parent_id = owner if owner.endswith("." + method) else owner + "." + method
            if event["parent_test_id"] != parent_id or event["test_id"] != parent_id + suffix:
                invalid.append("OUTCOME_IDENTITY_AND_DESCRIPTION_DISAGREE")
                break
        if any(event["exception_type"] != "builtins.AssertionError" or not event["is_exact_assertion_error"]
               for event in failed):
            invalid.append("FAILURE_IS_NOT_ASSERTIONERROR")
        assertion_names = [event["description"] for event in failed
                           if event["exception_type"] == "builtins.AssertionError" and event["is_exact_assertion_error"]]
        if len({event["test_id"] for event in failed}) != len(failed):
            invalid.append("DUPLICATE_FAILURE_TEST_ID")
        if len(failed) != len(failure_blocks) or any(
                not any(f'  File "{frame["file"]}", line {frame["line"]}, in {frame["function"]}' in trace.splitlines()
                        for frame in event["traceback_frames"])
                for event, (_, trace) in zip(failed, failure_blocks)):
            invalid.append("CONTROLLED_TRACEBACK_AND_REPORT_DISAGREE")
    if len(set(failure_names)) != len(failure_names):
        invalid.append("DUPLICATE_FAILURE_DESCRIPTION")
    if timed_out:
        invalid.append("TIMEOUT")
    if launch_error:
        invalid.append("SUBPROCESS_LAUNCH_ERROR")
    if ran is None or ran <= 0 or summary is None:
        invalid.append("MISSING_OR_INVALID_UNITTEST_SUMMARY")
    if summary and summary != "OK":
        expected_summary = "FAILED (" + ", ".join(f"{name}={value}" for name, value in tokens) + ")"
        if summary != expected_summary or len(tokens) != len(tally):
            invalid.append("MALFORMED_UNITTEST_SUMMARY")
    if len(failure_names) != failures or len(error_names) != errors:
        invalid.append("OUTCOME_NAMES_DO_NOT_MATCH_SUMMARY")
    if (assertion_names != failure_names or len(failure_blocks) != failures
            or any(not re.search(r"^Traceback \(most recent call last\):$", trace, re.MULTILINE)
                   or not re.search(r'^  File "[^\n]+", line [0-9]+, in [^\n]+$', trace, re.MULTILINE)
                   or not re.search(r"^AssertionError(?::[^\n]*)?$", trace, re.MULTILINE)
                   for _, trace in failure_blocks)):
        invalid.append("FAILURE_WITHOUT_ASSERTIONERROR_TRACE")
    if errors:
        invalid.append("UNITTEST_ERRORS")
    if skipped or tally.get("expected failures", 0) or tally.get("unexpected successes", 0):
        invalid.append("NONASSERTION_OUTCOMES")
    combined = stdout + "\n" + stderr
    if "Exception ignored in:" in combined or re.search(r"\b[A-Za-z_]*Warning\b", combined):
        invalid.append("UNRAISABLE_OR_WARNING")
    if returncode not in (0, 1):
        invalid.append("NO_COHERENT_UNITTEST_EXIT")
    elif returncode == 0:
        if summary != "OK" or failures:
            invalid.append("EXIT_AND_SUMMARY_DISAGREE")
    elif summary is None or not summary.startswith("FAILED (") or not failures:
        invalid.append("EXIT_WITHOUT_ASSERTION_FAILURES")
    return {"command": command, "cwd": str(HERE.parent),
            "environment_controls": {k: env.get(k) for k in
                                     ("LX_PLATFORM_DIR", "PYTHONDONTWRITEBYTECODE", "PYTHONWARNINGS", "PYTHONHASHSEED")},
            "returncode": returncode, "elapsed_s": elapsed_s, "timed_out": timed_out,
            "launch_error": launch_error, "ran": ran, "summary": summary,
            "failures": failures, "errors": errors, "skipped": skipped,
            "failure_names": failure_names, "assertion_failure_names": assertion_names, "error_names": error_names,
            "controlled_runner_metadata": result_metadata,
            "controlled_runner_metadata_raw": result_metadata_raw,
            "invalid_reasons": invalid, "stdout": stdout, "stderr": stderr,
            "suite_tail": (stderr.strip().splitlines() or [""])[-1]}


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate runner metadata key")
        result[key] = value
    return result


def run_suite(env=None, *, timeout_s: float = 900) -> dict:
    clean_env = dict(os.environ if env is None else env)
    clean_env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONWARNINGS="error", PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory() as directory:
        metadata_path = Path(directory, "result.json")
        command = [sys.executable, "-B", "-W", "error", "-c", _RUNNER, str(HERE), str(metadata_path)]
        started = time.monotonic()
        try:
            p = subprocess.run(command, cwd=HERE.parent, env=clean_env, capture_output=True, text=True, timeout=timeout_s)
        except subprocess.TimeoutExpired as exc:
            return _suite_record(command, clean_env, returncode=None, stdout=_text(exc.stdout), stderr=_text(exc.stderr),
                                 elapsed_s=time.monotonic() - started, timed_out=True)
        except OSError as exc:
            return _suite_record(command, clean_env, returncode=None, stdout="", stderr="",
                                 elapsed_s=time.monotonic() - started, launch_error=f"{type(exc).__name__}: {exc}")
        raw_metadata = None
        try:
            raw_metadata = metadata_path.read_text()
            metadata = json.loads(raw_metadata, object_pairs_hook=_unique_json_object)
        except (OSError, ValueError, UnicodeError):
            metadata = None
        return _suite_record(command, clean_env, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr,
                             elapsed_s=time.monotonic() - started, result_metadata=metadata,
                             result_metadata_raw=raw_metadata)


def suite_passed(suite: dict) -> bool:
    return not suite["invalid_reasons"] and suite["returncode"] == 0


def classify_mutant(suite: dict, baseline: dict, witnesses: list[str]) -> tuple[str, list[str]]:
    if not suite_passed(baseline):
        return "ERROR", ["BASELINE_NOT_PASS"]
    reasons = list(suite["invalid_reasons"])
    if suite["ran"] != baseline["ran"]:
        reasons.append("TEST_COUNT_DIFFERS_FROM_BASELINE")
    suite_metadata = suite.get("controlled_runner_metadata")
    baseline_metadata = baseline.get("controlled_runner_metadata")
    suite_ids = suite_metadata.get("executed_test_ids") if isinstance(suite_metadata, dict) else None
    baseline_ids = baseline_metadata.get("executed_test_ids") if isinstance(baseline_metadata, dict) else None
    if suite_ids != baseline_ids:
        reasons.append("EXECUTED_TEST_IDS_DIFFER_FROM_BASELINE")
    failed_methods = {name.split(" ", 1)[0] for name in suite["assertion_failure_names"]}
    if suite["returncode"] != 0 and not failed_methods.intersection(witnesses):
        reasons.append("NO_INTENDED_PROPERTY_ASSERTION")
    if reasons:
        return "ERROR", reasons
    return ("SURVIVED", []) if suite["returncode"] == 0 else ("KILLED", [])


def apply_mutation(src: str, edits: list[tuple[str, str]]) -> tuple[str | None, list[int], str | None]:
    mutated, counts = src, []
    for old, new in edits:
        counts.append(mutated.count(old))
        if counts[-1] != 1:
            return None, counts, "ANCHOR_NOT_UNIQUE"
        mutated = mutated.replace(old, new)
    try:
        ast.parse(mutated)
    except SyntaxError as exc:
        return None, counts, f"MUTATED_SOURCE_SYNTAX_ERROR: line {exc.lineno}: {exc.msg}"
    return mutated, counts, None


def input_paths() -> list[Path]:
    """All development Python inputs plus the exact CI entry point; no namespace-wide scan."""
    return sorted([*HERE.parent.glob("*.py"), *HERE.glob("*.py"),
                   HERE.parents[5] / ".github/workflows/cell-308-r5-integration.yml"])


def input_hashes() -> dict[str, str]:
    root = HERE.parents[5]
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in input_paths()}


def expected_test_count() -> int:
    """Independent static discovery count guards against silently omitted test modules."""
    return sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
               for path in HERE.glob("test_*.py") for node in ast.walk(ast.parse(path.read_text())))


def validate_registry() -> set[str]:
    ids = [mid for mid, _, _ in MUTANTS]
    expected = {f"{prefix}{index:02d}" for prefix, count in MUTANT_GROUP_SIZES.items()
                for index in range(1, count + 1)}
    methods = {node.name for path in HERE.glob("test_*.py")
               for node in ast.walk(ast.parse(path.read_text())) if isinstance(node, ast.FunctionDef)}
    if len(ids) != len(set(ids)) or set(ids) != expected or set(PROPERTY_WITNESSES) != expected:
        raise ValueError("registry and property witnesses must contain exactly the expected unique IDs")
    if any(not names or not set(names) <= methods for names in PROPERTY_WITNESSES.values()):
        raise ValueError("each mutation must name existing intended-property test methods")
    return expected


def main(out: str | None) -> int:
    expected_ids = validate_registry()
    before = input_hashes()
    src = SRC.read_text()
    source_key = str(SRC.relative_to(HERE.parents[5]))
    if hashlib.sha256(src.encode()).hexdigest() != before[source_key]:
        raise RuntimeError("platform source changed while taking the input snapshot")
    clean_env = dict(os.environ)
    clean_env.pop("LX_PLATFORM_DIR", None)
    clean_env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONWARNINGS="error", PYTHONHASHSEED="0")
    # The first subprocess always uses the real combined source, never an inherited mutant directory.
    base = run_suite(clean_env)
    expected_tests = expected_test_count()
    if base["ran"] != expected_tests:
        base["invalid_reasons"].append("BASELINE_COUNT_DIFFERS_FROM_STATIC_TEST_METHODS")
    baseline_passed = suite_passed(base)
    rows = []
    for mid, what, edits in MUTANTS:
        row = {"id": mid, "origin": ("combined integration" if mid.startswith("R5SYNC") or mid == "CDEX16" else
                           "Codex" if mid.startswith("CDEX") else "Claude reviews 63-69" if mid.startswith("RV") else
                           "Claude revision 5"),
               "property": what, "intended_property_test_methods": PROPERTY_WITNESSES[mid],
               "edits": [{"old": old, "new": new} for old, new in edits]}
        mutated, counts, mutation_error = apply_mutation(src, edits)
        row["anchor_counts"] = counts
        if mutation_error:
            row.update(status="NOT_APPLIED", reasons=[mutation_error])
            rows.append(row)
            continue
        row["mutated_lx_platform_sha256"] = hashlib.sha256(mutated.encode()).hexdigest()
        if not baseline_passed:
            row.update(status="ERROR", reasons=["BASELINE_NOT_PASS"])
            rows.append(row)
            continue
        with tempfile.TemporaryDirectory() as d:
            Path(d, "lx_platform.py").write_text(mutated)
            suite = run_suite(dict(clean_env, LX_PLATFORM_DIR=d))
            status, reasons = classify_mutant(suite, base, PROPERTY_WITNESSES[mid])
            row.update(status=status, reasons=reasons, suite=suite, suite_tail=suite["suite_tail"])
            rows.append(row)
    after = input_hashes()
    complete = (len(rows) == len(expected_ids) and {row["id"] for row in rows} == expected_ids
                and all("suite" in row for row in rows))
    passed = baseline_passed and before == after and complete and all(row["status"] == "KILLED" for row in rows)
    executable = Path(os.path.realpath(sys.executable))
    rec = {"schema": "CLOUD_R1_LINUX_DEV_MUTATION_RUN_V3", "class": "SYNTHETIC_VALIDATION", "dev_only": True,
           "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "python": {"executable": sys.executable, "real_executable": str(executable),
                      "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
                      "version": sys.version, "implementation": platform.python_implementation()},
           "kernel": platform.release(), "machine": platform.machine(), "system": platform.system(),
           "source_commit": os.environ.get("GITHUB_SHA"), "input_sha256": before, "input_sha256_after": after,
           "inputs_unchanged": before == after, "full_registry_completed": complete,
           "expected_test_count": expected_tests, "unmutated_suite": "PASS" if baseline_passed else "ERROR",
           "baseline": base, "unmutated_tail": base["suite_tail"],
           "expected_mutants": len(expected_ids), "killed": sum(r["status"] == "KILLED" for r in rows),
           "total": len(rows), "status_counts": {status: sum(r["status"] == status for r in rows)
                                                   for status in ("KILLED", "SURVIVED", "ERROR", "NOT_APPLIED")},
           "new_target_evaluations": 0, "pass": passed, "mutants": rows}
    report = json.dumps(rec, indent=1)
    print(report)
    if out:
        Path(out).write_text(report + "\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
