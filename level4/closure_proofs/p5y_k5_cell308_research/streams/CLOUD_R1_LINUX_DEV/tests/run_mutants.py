"""Mutation harness for the DEV-ONLY lx_platform tests. Each mutant weakens one fail-closed property in a temporary
copy of lx_platform.py. A KILLED case must run the baseline's full test count and report assertion failures with no
errors or skips. Import failures, malformed reports, timeouts and other invalid runs are ERROR, never kills.
M01-M32 are the coordinator's; R01-R10 are review 59's mutants and X01-X09 are review 60's surviving mutants, each
re-anchored with the same weakening; N01-N14 weaken the revision-3 repairs. Y01-Y03 are review 61's fresh semantic
mutants; P01-P05 cover its discovered regressions. F01-F05 weaken review 62's bounded follow-up repairs; F06 restores review 63's payload-dropping defect; F07 weakens review 64's malformed-path refusal.
Y03 removes both the sample-order and pairwise non-increase rejection routes for the same ordering property.
The baseline runs first with an inherited
LX_PLATFORM_DIR removed. Every suite subprocess uses strict ResourceWarning handling and keeps its complete output.
Target-free; repository results are written only when an explicit output argument is supplied.

usage: python3 tests/run_mutants.py [out.json]       (from streams/CLOUD_R1_LINUX_DEV)
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

# (id, property weakened, [(old, new), ...]) -- each old text must occur exactly once
MUTANTS = [
    ("M01", "failed boot-id read treated as a reboot (DEAD)",
     [("    if cur is None:\n        return UNKNOWN\n", "    if cur is None:\n        return DEAD\n")]),
    ("M02", "unreadable /proc/<pid>/stat treated as DEAD",
     [("    st = (stat or proc_stat)(pid)\n    if st is None:\n        return UNKNOWN\n",
       "    st = (stat or proc_stat)(pid)\n    if st is None:\n        return DEAD\n")]),
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
     [("        if type(ident.get(k)) is not int or ident[k] <= 0 or not isinstance(ns, dict) \\\n"
       "                or type(ns.get(k)) is not int or ns.get(k) != ident[k]:\n            return UNKNOWN",
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
    ("M31", "incomplete /proc view accepted", [("dt_s <= 0 or view_complete is not True:", "dt_s <= 0:")]),
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
     [("        if owned((pid, start), ppid, t1):\n            continue\n        prev",
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
     [('    if not candidates:\n        return None\n', '    if not candidates:\n        return True\n')]),
    ("X03", "unreadable livepatch counts as none applied", [("livepatch == [])", "livepatch in ([], None))")]),
    ("X04", "K' monotonic-ahead-of-boottime channel removed",
     [("                elif db - dm < -SLEEP_GAP_TOL_NS:\n                    reasons.append(\"AMBIGUOUS: K' monotonic advanced more "
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
     [('    if review is None or f"{ACCEPTANCE_LINE}{want}".encode() not in review.splitlines():', "    if False:")]),
    ("N03", "attestation schema not checked",
     [('    if not isinstance(rec, dict) or rec.get("schema") != ATTESTATION_SCHEMA:', "    if not isinstance(rec, dict):")]),
    ("N04", "caller-asserted fields accepted in the attestation reference",
     [('set(ref) != {"path", "sha256"}', 'not {"path", "sha256"} <= set(ref)')]),
    ("N05", "root attestation truthy again",
     [("    root_attested = root_attested is True\n", ""),
      ('    if root_attested is not True or not mem or "MemTotal" not in mem', '    if not root_attested or not mem or "MemTotal" not in mem'),
      ("    if root_attested is not True:\n        return None\n    vals", "    if not root_attested:\n        return None\n    vals")]),
    ("N06", "nested PID namespace view accepted", [("    if ino != INIT_PID_NS:\n        return False\n", "")]),
    ("N07", "boot id not validated", [("_g(None if not isinstance(boot, str) or boot_id(boot) is None else True)",
                                       "_g(None if boot is None else True)")]),
    ("N08", "exited processes not reported", [("in t0.items():\n        if (pid, start) not in t1", "in {}.items():\n        if (pid, start) not in t1")]),
    ("N09", "unreadable existing process skipped",
     [('            if Path(f"{proc_root}/{pid}").exists():\n                return None\n', "")]),
    ("N10", "campaign children exempt by pid alone",
     [("        return key in own or (ppid in own_start and (ppid, own_start[ppid]) in snapshot\n"
       "                              and key[1] >= own_start[ppid])",
       "        return key in own or ppid in own_start")]),
    ("N11", "unrecorded namespace lets pid evidence count (revision-2 behaviour)",
     [("        if type(ident.get(k)) is not int or ident[k] <= 0 or not isinstance(ns, dict) \\\n"
       "                or type(ns.get(k)) is not int or ns.get(k) != ident[k]:",
       "        if ident.get(k) is not None and (type(ident[k]) is not int or ident[k] <= 0\n"
       "                or not isinstance(ns, dict) or type(ns.get(k)) is not int or ns.get(k) != ident[k]):")]),
    ("N12", "pin without libm / libc / loader accepted",
     [("    if not all(any(n == r or n.startswith(r) for n in names) for r in REQUIRED_MAPPED):\n        return None",
       "    if False:\n        return None")]),
    ("N13", "launch record trusted on its 'pass' flag",
     [('    return bool(rec.get("systemd_pid1") is True and', '    return bool(rec.get("pass") is True) or bool(rec.get("systemd_pid1") is True and')]),
    ("N14", "unrecognised battery status read as not discharging",
     [("            elif st not in KNOWN_NOT_DISCHARGING:\n                return None", "            else:\n                pass")]),
    # ---- review 61's semantic coverage mutants (Y) and discovered regressions (P)
    ("Y01", "effective memory minimum omits the host MemTotal cap",
     [("    return min([mem[\"MemTotal\"], *[v for v in vals[0] if isinstance(v, int)]])\n\n\n"
       "def visible_limit_upper_bound",
       "    return min([v for v in vals[0] if isinstance(v, int)])\n\n\n"
       "def visible_limit_upper_bound")]),
    ("Y02", "cgroup headroom uses the maximum instead of the minimum",
     [("    return min(hs) if hs else None", "    return max(hs) if hs else None")]),
    ("Y03", "sample order is ignored (both sample-order and pairwise non-increase guards removed)",
     [('        if any(d < 0 for d in steps):\n            reasons.append("AMBIGUOUS: samples out of order")\n'
       '        elif not steps or max(steps) > MAX_SAMPLE_GAP_S * 10 ** 9:',
       '        if not steps or max(steps) > MAX_SAMPLE_GAP_S * 10 ** 9:'),
      ('            if dm <= 0 or db <= 0:', '            if False:')]),
    ("P01", "campaign child ownership ignores the parent's observed starttime identity",
     [("ppid in own_start and (ppid, own_start[ppid]) in snapshot", "ppid in own_start")]),
    ("P02", "a malformed current boot id counts as positive identity evidence",
     [('(boot_id(current_boot) if isinstance(current_boot, str) else None)',
       '(current_boot if isinstance(current_boot, str) else None)')]),
    ("P03", "matching malformed boot ids count as positive interval evidence",
     [('    if any(not isinstance(b, str) or boot_id(b) is None for b in boots):',
       '    if any(not b for b in boots):')]),
    ("P04", "nonfinite CPU window duration is accepted",
     [('or isinstance(dt_s, bool) or not math.isfinite(dt_s) or dt_s <= 0',
       'or isinstance(dt_s, bool) or dt_s <= 0')]),
    ("P05", "malformed NSpid entries count as a complete proc view",
     [('    if len(nspid) != 1 or not re.fullmatch(r"0*[1-9][0-9]*", nspid[0]):\n        return None\n', '')]),
    # ---- review 62's bounded intermediate-reading and ambiguity repairs
    ("F01", "clock-pair checks ignore intermediate observations and use only the endpoints",
     [('        pairs = list(zip(seq, seq[1:]))\n        if len(seq) > 2:\n            pairs.append((start, end))\n',
       '        pairs = [(start, end)]\n')]),
    ("F02", "suspend counter checks ignore intermediate observations and use only the endpoints",
     [('    counts = [x.get("suspend_success") if isinstance(x, dict) else None for x in seq]',
       '    counts = [x.get("suspend_success") if isinstance(x, dict) else None for x in (start, end)]'),
      ('    if any(not isinstance(x, dict) or type(x.get("suspend_success")) is not int\n'
       '           or x["suspend_success"] < 0 for x in seq):',
       '    if any(not isinstance(x, dict) or type(x.get("suspend_success")) is not int\n'
       '           or x["suspend_success"] < 0 for x in (start, end)):')]),
    ("F03", "malformed mount IDs and device numbers bypass numeric metadata validation",
     [('    if not re.fullmatch(r"0*[1-9][0-9]*", f[0]) or not re.fullmatch(r"0*[1-9][0-9]*", f[1]) \\\n'
       '            or not re.fullmatch(r"[0-9]+:[0-9]+", f[2]):\n        return None\n', '')]),
    ("F04", "the first NSpid field is trusted when duplicate NSpid records disagree",
     [('    if len(nspid_fields) != 1:', '    if not nspid_fields:')]),
    ("F05", "multiple starttime identities for one PID are accepted in a single CPU snapshot",
     [('        if len({key[0] for key in snapshot}) != len(snapshot):\n            return None\n', '')]),
    ("F06", "payload adjoining NSpid's colon is discarded before validation",
     [('    nspid_fields = [ln.partition(":")[2].split() for ln in st.splitlines() if ln.startswith("NSpid:")]',
       '    nspid_fields = [ln.split()[1:] for ln in st.splitlines() if ln.startswith("NSpid:")]')]),
    ("F07", "malformed attestation/reference paths escape as subprocess argument exceptions",
     [('    except (OSError, subprocess.SubprocessError, ValueError, UnicodeError):',
       '    except (OSError, subprocess.SubprocessError):')]),
]

MUTANT_GROUP_SIZES = {"M": 32, "R": 10, "X": 9, "N": 14, "Y": 3, "P": 5, "F": 7}


def _text(value) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""


def _suite_record(command: list[str], env: dict, *, returncode: int | None, stdout: str, stderr: str,
                  elapsed_s: float, timed_out: bool = False, launch_error: str | None = None) -> dict:
    """Keep the raw report and fail closed when its summary and named outcomes do not agree."""
    counts = re.findall(r"^Ran (\d+) tests? in [0-9.]+s$", stderr, flags=re.MULTILINE)
    summaries = re.findall(r"^(?:OK(?: \([^\n]*\))?|FAILED \([^\n]*\))$", stderr, flags=re.MULTILINE)
    summary = summaries[-1] if len(summaries) == 1 else None
    ran = int(counts[0]) if len(counts) == 1 else None
    tally = dict((name, int(value)) for name, value in re.findall(
        r"(failures|errors|skipped|expected failures|unexpected successes)=(\d+)", summary or ""))
    failures = tally.get("failures", 0)
    errors = tally.get("errors", 0)
    skipped = tally.get("skipped", 0)
    failure_names = re.findall(r"^FAIL: (.+)$", stderr, flags=re.MULTILINE)
    error_names = re.findall(r"^ERROR: (.+)$", stderr, flags=re.MULTILINE)
    invalid = []
    if timed_out:
        invalid.append("TIMEOUT")
    if launch_error:
        invalid.append("SUBPROCESS_LAUNCH_ERROR")
    if ran is None or ran <= 0 or summary is None:
        invalid.append("MISSING_OR_INVALID_UNITTEST_SUMMARY")
    if len(failure_names) != failures or len(error_names) != errors:
        invalid.append("OUTCOME_NAMES_DO_NOT_MATCH_SUMMARY")
    if errors:
        invalid.append("UNITTEST_ERRORS")
    if skipped or tally.get("expected failures", 0) or tally.get("unexpected successes", 0):
        invalid.append("NONASSERTION_OUTCOMES")
    if "Exception ignored in:" in stderr or "ResourceWarning:" in stderr:
        invalid.append("UNRAISABLE_OR_RESOURCE_WARNING")
    if returncode is None or returncode < 0:
        invalid.append("NO_NORMAL_EXIT")
    elif returncode == 0:
        if summary != "OK" or failures:
            invalid.append("EXIT_AND_SUMMARY_DISAGREE")
    elif summary is None or not summary.startswith("FAILED (") or not failures:
        invalid.append("EXIT_WITHOUT_ASSERTION_FAILURES")
    return {"command": command, "cwd": str(HERE.parent),
            "environment_controls": {"LX_PLATFORM_DIR": env.get("LX_PLATFORM_DIR"),
                                     "PYTHONDONTWRITEBYTECODE": env.get("PYTHONDONTWRITEBYTECODE")},
            "returncode": returncode, "elapsed_s": elapsed_s, "timed_out": timed_out,
            "launch_error": launch_error, "ran": ran, "summary": summary,
            "failures": failures, "errors": errors, "skipped": skipped,
            "failure_names": failure_names, "error_names": error_names,
            "invalid_reasons": invalid, "stdout": stdout, "stderr": stderr,
            "suite_tail": (stderr.strip().splitlines() or [""])[-1]}


def run_suite(env=None, *, timeout_s: float = 900) -> dict:
    command = [sys.executable, "-B", "-W", "error::ResourceWarning", "-m", "unittest", "discover",
               "-s", str(HERE), "-v"]
    clean_env = dict(os.environ if env is None else env)
    clean_env["PYTHONDONTWRITEBYTECODE"] = "1"
    started = time.monotonic()
    try:
        p = subprocess.run(command, cwd=HERE.parent, env=clean_env, capture_output=True, text=True,
                           timeout=timeout_s)
    except subprocess.TimeoutExpired as exc:
        return _suite_record(command, clean_env, returncode=None, stdout=_text(exc.stdout), stderr=_text(exc.stderr),
                             elapsed_s=time.monotonic() - started, timed_out=True)
    except OSError as exc:
        return _suite_record(command, clean_env, returncode=None, stdout="", stderr="",
                             elapsed_s=time.monotonic() - started, launch_error=f"{type(exc).__name__}: {exc}")
    return _suite_record(command, clean_env, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr,
                         elapsed_s=time.monotonic() - started)


def suite_passed(suite: dict) -> bool:
    return not suite["invalid_reasons"] and suite["returncode"] == 0


def classify_mutant(suite: dict, baseline: dict) -> tuple[str, list[str]]:
    if not suite_passed(baseline):
        return "ERROR", ["BASELINE_NOT_PASS"]
    reasons = list(suite["invalid_reasons"])
    if suite["ran"] != baseline["ran"]:
        reasons.append("TEST_COUNT_DIFFERS_FROM_BASELINE")
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


def input_hashes() -> dict[str, str]:
    return {str(path.relative_to(HERE.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (SRC, HERE.parent / "lx_inventory.py", HERE.parent / "lx_verified.py",
                         HERE / "test_lx_platform.py", HERE / "test_lx_verified.py", Path(__file__).resolve())}


def main(out: str | None) -> int:
    before = input_hashes()
    src = SRC.read_text()
    if hashlib.sha256(src.encode()).hexdigest() != before["lx_platform.py"]:
        raise RuntimeError("platform source changed while taking the input snapshot")
    clean_env = dict(os.environ)
    clean_env.pop("LX_PLATFORM_DIR", None)
    clean_env["PYTHONDONTWRITEBYTECODE"] = "1"
    base = run_suite(clean_env)
    baseline_passed = suite_passed(base)
    ids = [mid for mid, _, _ in MUTANTS]
    expected_ids = {f"{prefix}{index:02d}" for prefix, count in MUTANT_GROUP_SIZES.items()
                    for index in range(1, count + 1)}
    if len(ids) != len(set(ids)) or set(ids) != expected_ids:
        raise ValueError("mutation registry must contain exactly the expected unique IDs")
    rows = []
    for mid, what, edits in MUTANTS:
        row = {"id": mid, "property": what}
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
            status, reasons = classify_mutant(suite, base)
            row.update(status=status, reasons=reasons, suite=suite, suite_tail=suite["suite_tail"])
            rows.append(row)
    after = input_hashes()
    rec = {"schema": "CLOUD_R1_LINUX_DEV_MUTATION_RUN_V2", "class": "SYNTHETIC_VALIDATION", "dev_only": True,
           "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "python": {"executable": sys.executable, "real_executable": os.path.realpath(sys.executable),
                      "version": sys.version, "implementation": platform.python_implementation()},
           "kernel": platform.release(), "machine": platform.machine(), "system": platform.system(),
           "input_sha256": before, "input_sha256_after": after, "inputs_unchanged": before == after,
           "lx_platform_sha256": before["lx_platform.py"],
           "tests_sha256": before["tests/test_lx_platform.py"],
           "harness_sha256": before["tests/run_mutants.py"],
           "unmutated_suite": "PASS" if baseline_passed else "ERROR", "baseline": base,
           "unmutated_tail": base["suite_tail"],
           "expected_mutants": len(expected_ids),
           "killed": sum(r["status"] == "KILLED" for r in rows), "total": len(rows),
           "status_counts": {status: sum(r["status"] == status for r in rows)
                             for status in ("KILLED", "SURVIVED", "ERROR", "NOT_APPLIED")},
           "reviewer_mutants_killed": sum(r["status"] == "KILLED" for r in rows if r["id"].startswith("R")),
           "review60_mutants_killed": sum(r["status"] == "KILLED" for r in rows if r["id"].startswith("X")),
           "review61_mutants_killed": sum(r["status"] == "KILLED" for r in rows if r["id"].startswith("Y")),
           "regression_mutants_killed": sum(r["status"] == "KILLED" for r in rows if r["id"].startswith("P")),
           "new_target_evaluations": 0,
           "mutants": rows}
    text = json.dumps(rec, indent=1)
    print(text)
    if out:
        Path(out).write_text(text + "\n")
    return 0 if baseline_passed and rec["inputs_unchanged"] and rec["killed"] == rec["total"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
