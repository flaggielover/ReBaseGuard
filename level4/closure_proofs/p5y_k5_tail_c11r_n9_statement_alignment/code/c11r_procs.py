"""C11R -- the campaign-process detector, revision 2 (review round 3, N-2; errata E26, E27).

WHAT WAS WRONG. Revision 1 (common.classified_processes) accepted an interpreter only if the
basename of its executable was exactly one of python3, python, python3.14, python3.12, python3.11.
On the recorded host every campaign process runs under a framework build whose executable is
.../Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python -- basename
"Python", capital P. So the detector never saw a campaign process at all, and every claim that
rested on it -- the cost artifact's "sequential" fields, B0_14, the regeneration pre-flight --
was vacuous.

HOW THIS ONE WORKS (macOS has no /proc; the platform-native mechanism is `ps`):
  1  SNAPSHOT. `ps -axww -o pid=,ppid=,comm=` gives every visible process with its executable
     path; `ps -axww -o pid=,args=` gives its argument string. A PID in the first listing and
     not the second exited in between and is classified VANISHED.
  2  INTERPRETER IDENTITY, from the executable path, case-insensitively: a basename of the form
     python / python3 / python3.14 (any case, optional trailing w), or any executable inside a
     Python.framework / Python.app bundle. This covers system, Homebrew, venv and framework
     builds, including the capital-P framework executable.
  3  CAMPAIGN RELEVANCE, from argv TOKENS only -- never from the command string of a shell: a
     token whose basename is a campaign script (c11r_*.py, c11_*.py, taboo_certify.py), a
     `-m c11r_...` module, or a `-c` payload that names a campaign module. The role is TARGET for
     c11r_runs.py, c11r_compare.py and c11r_qualify.py (execution-phase entry points), otherwise
     NON_TARGET_PRODUCER, or CAMPAIGN_ADHOC for a `-c` payload.
  4  SELF-EXCLUSION, explicit: this process and every ancestor up the ppid chain (the driver
     that launched it, and the shells above) are EXCLUDED_SELF_CHAIN, whatever their argv says.
     A shell is never a worker: only interpreter processes are classified, so a shell whose
     command string mentions a campaign script cannot match (the `pgrep -f` self-match trap).

REVISION 3 (review round 4, N4-6; erratum E36). Revision 2 decided relevance from a campaign SCRIPT
name only, so a WRAPPER script importing campaign modules -- the form every ad-hoc probe and both
reviewers' non-target rehearsals took -- was FOREIGN_PYTHON, and so were `-Bc payload`,
`-cpayload` and `-Bm module`. Now, for an interpreter process:
  * option clusters are parsed (`-Bc`, `-cimport ...`, `-Bm mod`, `-W`/`-X` arguments skipped);
  * an argv token naming the campaign namespace or a campaign module anywhere (a wrapper given
    the code directory as an argument) is CAMPAIGN_WRAPPER;
  * the SCRIPT'S OWN SOURCE is read (a .py file, resolved against the process's working
    directory, at most 1 MB) and an import of a campaign module, an import_module of one, or the
    namespace name makes it CAMPAIGN_WRAPPER.

WHAT IT DOES NOT CHECK, stated exactly: processes not visible to `ps` for this user; processes
on other hosts or in containers; campaign work run by a non-Python executable; an interpreter
renamed to something that is neither python-like nor inside a Python framework bundle; argv
tokens containing spaces (ps joins argv with spaces, and tokens are split on whitespace); an
interpreter reading its program from STDIN or run interactively; a wrapper whose campaign import
is INDIRECT (through a third module, or code built at run time); a script this user cannot read.
Foreign Python processes are COUNTED and reported, not treated as campaign workers. The detector
gates CONCURRENCY (cost measurement, pre-flight, B0, regeneration), not identity: it cannot prove
that no competing computation ran, only that none it can recognise did.
"""
from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C

PY_BASENAME = re.compile(r"^python(\d+(\.\d+)*)?w?$", re.IGNORECASE)
CAMPAIGN_SCRIPT = re.compile(r"^(c11r?_[A-Za-z0-9_]+|taboo_certify)\.py$")
CAMPAIGN_MODULE = re.compile(r"^(c11r?_[A-Za-z0-9_]+|taboo_certify)$")
CAMPAIGN_TOKEN = re.compile(r"(\bc11r?_[a-z0-9_]+|\btaboo_certify\b|"
                            r"p5y_k5_tail_c11r_n9_statement_alignment)", re.IGNORECASE)
CAMPAIGN_IMPORT = re.compile(r"(^|[\s;])(import|from)\s+(c11r?_[A-Za-z0-9_]+|taboo_certify)\b|"
                             r"import_module\(\s*['\"](c11r?_|taboo_certify)|"
                             r"p5y_k5_tail_c11r_n9_statement_alignment", re.MULTILINE)
TARGET_SCRIPTS = frozenset({"c11r_runs.py", "c11r_compare.py", "c11r_qualify.py"})
OPTIONS_WITH_ARGUMENT = frozenset("WXQ")


def is_python_executable(exe: str) -> bool:
    if not exe:
        return False
    if PY_BASENAME.match(pathlib.PurePosixPath(exe).name):
        return True
    low = exe.lower()
    return "/python.framework/" in low or "/python.app/" in low


def _module_role(mod: str) -> str | None:
    if CAMPAIGN_MODULE.match(mod):
        return "TARGET" if mod + ".py" in TARGET_SCRIPTS else "NON_TARGET_PRODUCER"
    return None


def campaign_role(args: str | None, script_source: str | None = None) -> str | None:
    """The campaign role an interpreter's argv (and, for a wrapper, its script) implies."""
    if not args:
        return None
    toks = args.split()
    i = 1
    while i < len(toks):
        t = toks[i]
        if t.startswith("-") and not t.startswith("--") and len(t) > 1:
            letters = t[1:]
            for j, ch in enumerate(letters):
                rest = letters[j + 1:]
                if ch == "c":                              # -c, -Bc, -cpayload
                    # everything after -c is the payload (ps joins argv, so an attached payload
                    # with spaces arrives as several tokens)
                    payload = " ".join(([rest] if rest else []) + toks[i + 1:])
                    return "CAMPAIGN_ADHOC" if CAMPAIGN_TOKEN.search(payload) else None
                if ch == "m":                              # -m, -Bm, -mmodule
                    mod = rest if rest else (toks[i + 1] if i + 1 < len(toks) else "")
                    return _module_role(mod) or (
                        "CAMPAIGN_WRAPPER" if CAMPAIGN_TOKEN.search(" ".join(toks[i:])) else None)
                if ch in OPTIONS_WITH_ARGUMENT:
                    if not rest:
                        i += 1                             # its argument is the next token
                    break
            i += 1
            continue
        if t == "-":
            return None                                    # program on stdin: undetectable
        base = pathlib.PurePosixPath(t).name               # the script
        if CAMPAIGN_SCRIPT.match(base):
            return "TARGET" if base in TARGET_SCRIPTS else "NON_TARGET_PRODUCER"
        if any(CAMPAIGN_TOKEN.search(x) for x in toks[i:]):
            return "CAMPAIGN_WRAPPER"                      # names the campaign in its arguments
        if script_source and CAMPAIGN_IMPORT.search(script_source):
            return "CAMPAIGN_WRAPPER"                      # imports campaign code
        return None
    return None                                            # interactive: undetectable


def classify(rows: list[dict], self_chain: set[int]) -> list[dict]:
    """Pure: classify a process snapshot. Each row: pid, ppid, exe, args (None = vanished)."""
    out = []
    for r in rows:
        if r["pid"] in self_chain:
            cls = "EXCLUDED_SELF_CHAIN"
        elif r.get("args") is None:
            cls = "VANISHED"
        elif not is_python_executable(r["exe"]):
            cls = "NOT_AN_INTERPRETER"
        else:
            role = campaign_role(r["args"], r.get("script_source"))
            cls = role if role else "FOREIGN_PYTHON"
        out.append({**r, "class": cls})
    return out


def ancestor_chain(table: dict[int, int], pid: int) -> set[int]:
    chain, cur = set(), pid
    for _ in range(128):
        chain.add(cur)
        if cur not in table or cur <= 1:
            break
        cur = table[cur]
    return chain


def snapshot() -> tuple[list[dict], set[int]]:
    a = subprocess.run(["ps", "-axww", "-o", "pid=,ppid=,comm="], capture_output=True,
                       text=True).stdout
    b = subprocess.run(["ps", "-axww", "-o", "pid=,args="], capture_output=True, text=True).stdout
    args = {}
    for ln in b.splitlines():
        parts = ln.strip().split(None, 1)
        if parts and parts[0].isdigit():
            args[int(parts[0])] = parts[1] if len(parts) > 1 else ""
    rows, ppid = [], {}
    for ln in a.splitlines():
        parts = ln.strip().split(None, 2)
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            pid, pp = int(parts[0]), int(parts[1])
            ppid[pid] = pp
            rows.append({"pid": pid, "ppid": pp, "exe": parts[2] if len(parts) > 2 else "",
                         "args": args.get(pid)})
    chain = ancestor_chain(ppid, os.getpid())
    for r in rows:
        if r["pid"] not in chain and is_python_executable(r["exe"]) and r["args"]:
            r["script_source"] = script_source_of(r["pid"], r["args"])
    return rows, chain


def _process_cwd(pid: int) -> str | None:
    out = subprocess.run(["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"], capture_output=True,
                         text=True).stdout
    for ln in out.splitlines():
        if ln.startswith("n"):
            return ln[1:]
    return None


def script_source_of(pid: int, args: str) -> str | None:
    """The source of the script an interpreter runs (a .py file, <= 1 MB), for wrapper detection.
    Python source only: data files are never read here."""
    toks = args.split()
    i = 1
    while i < len(toks):
        t = toks[i]
        if t.startswith("-") and len(t) > 1:
            if any(ch in "cm" for ch in t[1:]):
                return None
            if t[1:] and t[-1] in OPTIONS_WITH_ARGUMENT and len(t) == 2:
                i += 1
            i += 1
            continue
        if not t.endswith(".py"):
            return None
        path = pathlib.Path(t)
        if not path.is_absolute():
            cwd = _process_cwd(pid)
            if cwd is None:
                return None
            path = pathlib.Path(cwd) / path
        try:
            if path.stat().st_size > 1 << 20:
                return None
            return path.with_suffix(".py").read_text(errors="replace")
        except OSError:
            return None
    return None


WORKER_CLASSES = ("TARGET", "NON_TARGET_PRODUCER", "CAMPAIGN_ADHOC", "CAMPAIGN_WRAPPER")
# ONE source for the revision: the cost artifact records DETECTOR_LABEL and the policy refuses a
# cost artifact certified sequential by any other revision (review 4 found a stale label class)
DETECTOR_REVISION = 3
DETECTOR_LABEL = f"code/c11r_procs.py (revision {DETECTOR_REVISION})"


def campaign_workers() -> dict:
    """Live: every campaign-relevant interpreter other than this process and its ancestors."""
    rows, chain = snapshot()
    cl = classify(rows, chain)
    return {"mechanism": "ps -axww (pid, ppid, comm) + (pid, args); no /proc on this platform",
            "processes_seen": len(cl),
            "interpreters_seen": sum(1 for r in cl if is_python_executable(r["exe"])),
            "workers": [{k: r[k] for k in ("pid", "exe", "args", "class")} for r in cl
                        if r["class"] in WORKER_CLASSES],
            "foreign_python": sum(1 for r in cl if r["class"] == "FOREIGN_PYTHON"),
            "self_chain": sorted(chain)}


# ---------------------------------------------------------------------------------------------
# controls
# ---------------------------------------------------------------------------------------------
FW_PY = "/Library/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python"
PLANTED = [
    ("python", {"pid": 101, "ppid": 1, "exe": "/usr/bin/python",
                "args": "python code/c11r_cost.py"}, "NON_TARGET_PRODUCER"),
    ("Python_capital", {"pid": 102, "ppid": 1, "exe": "Python",
                        "args": "Python -B code/c11r_validate.py"}, "NON_TARGET_PRODUCER"),
    ("python3", {"pid": 103, "ppid": 1, "exe": "/opt/homebrew/bin/python3",
                 "args": "python3 -B code/c11r_policy.py"}, "NON_TARGET_PRODUCER"),
    ("venv_python", {"pid": 104, "ppid": 1, "exe": "/Users/x/venv/bin/python",
                     "args": "/Users/x/venv/bin/python c11r_mutations.py"},
     "NON_TARGET_PRODUCER"),
    ("framework_build_Python", {"pid": 105, "ppid": 1, "exe": FW_PY,
                                "args": f"{FW_PY} -B code/c11r_cost.py"}, "NON_TARGET_PRODUCER"),
    ("target_worker_argv", {"pid": 106, "ppid": 1, "exe": FW_PY,
                            "args": f"{FW_PY} -B code/c11r_runs.py"}, "TARGET"),
    ("non_target_producer_argv", {"pid": 107, "ppid": 1, "exe": "python3.14",
                                  "args": "python3.14 code/c11r_b0.py"}, "NON_TARGET_PRODUCER"),
    ("adhoc_dash_c", {"pid": 108, "ppid": 1, "exe": FW_PY,
                      "args": f"{FW_PY} -B -c import c11r_boxdata as BD"}, "CAMPAIGN_ADHOC"),
    ("unrelated_shell_mentioning_a_script", {
        "pid": 109, "ppid": 1, "exe": "/bin/zsh",
        "args": "/bin/zsh -c eval 'python3 -B code/c11r_regen.py'"}, "NOT_AN_INTERPRETER"),
    ("foreign_python", {"pid": 110, "ppid": 1, "exe": "/usr/bin/python3",
                        "args": "python3 -m http.server"}, "FOREIGN_PYTHON"),
    ("stale_pid", {"pid": 111, "ppid": 1, "exe": FW_PY, "args": None}, "VANISHED"),
    ("current_detector_process", {"pid": 200, "ppid": 199, "exe": FW_PY,
                                  "args": f"{FW_PY} -B code/c11r_procs.py"},
     "EXCLUDED_SELF_CHAIN"),
    ("parent_shell", {"pid": 199, "ppid": 1, "exe": "/bin/zsh",
                      "args": "/bin/zsh -c python3 -B code/c11r_procs.py"},
     "EXCLUDED_SELF_CHAIN"),
    # review round 4, N4-6: the PD controls
    ("PD1_direct_script", {"pid": 301, "ppid": 1, "exe": FW_PY,
                           "args": f"{FW_PY} -B code/c11r_policy.py"}, "NON_TARGET_PRODUCER"),
    ("PD2_framework_build_Python", {"pid": 302, "ppid": 1, "exe": FW_PY,
                                    "args": f"{FW_PY} code/c11r_cost.py"}, "NON_TARGET_PRODUCER"),
    ("PD3_wrapper_script_importing_campaign", {
        "pid": 303, "ppid": 1, "exe": FW_PY, "args": f"{FW_PY} -B /tmp/nt_calib.py 5 32",
        "script_source": "import sys\nsys.path.insert(0, sys.argv[1])\nimport c11r_policy as P\n"},
     "CAMPAIGN_WRAPPER"),
    ("PD3b_wrapper_given_the_code_directory", {
        "pid": 304, "ppid": 1, "exe": FW_PY,
        "args": f"{FW_PY} -B probe.py /x/p5y_k5_tail_c11r_n9_statement_alignment/code 5 32"},
     "CAMPAIGN_WRAPPER"),
    ("PD4_dash_c_import", {"pid": 305, "ppid": 1, "exe": FW_PY,
                           "args": f"{FW_PY} -c import c11r_boxdata"}, "CAMPAIGN_ADHOC"),
    ("PD5_dash_Bc_import", {"pid": 306, "ppid": 1, "exe": FW_PY,
                            "args": f"{FW_PY} -Bc import c11r_boxdata as BD"}, "CAMPAIGN_ADHOC"),
    ("PD5b_dash_c_attached_payload", {"pid": 307, "ppid": 1, "exe": FW_PY,
                                      "args": f"{FW_PY} -cimport c11r_idrift"}, "CAMPAIGN_ADHOC"),
    ("PD5c_dash_Bm_module", {"pid": 308, "ppid": 1, "exe": FW_PY,
                             "args": f"{FW_PY} -Bm c11r_runs"}, "TARGET"),
    ("PD6_unrelated_Python", {"pid": 309, "ppid": 1, "exe": FW_PY,
                              "args": f"{FW_PY} -m pip list",
                              "script_source": None}, "FOREIGN_PYTHON"),
    ("PD6b_unrelated_wrapper_script", {"pid": 310, "ppid": 1, "exe": FW_PY,
                                       "args": f"{FW_PY} server.py --port 8000",
                                       "script_source": "import http.server\n"},
     "FOREIGN_PYTHON"),
    ("PD7_current_process", {"pid": 200, "ppid": 199, "exe": FW_PY,
                             "args": f"{FW_PY} -B code/c11r_chain.py"}, "EXCLUDED_SELF_CHAIN"),
    ("PD8_parent_process", {"pid": 199, "ppid": 1, "exe": FW_PY,
                            "args": f"{FW_PY} -B code/c11r_regen.py"}, "EXCLUDED_SELF_CHAIN"),
    ("PD9_vanished_pid", {"pid": 311, "ppid": 1, "exe": FW_PY, "args": None}, "VANISHED"),
    ("PD10_shell_with_the_name_in_diagnostic_text", {
        "pid": 312, "ppid": 1, "exe": "/bin/zsh",
        "args": "/bin/zsh -c echo c11r_runs.py finished; tail log"}, "NOT_AN_INTERPRETER"),
    ("stdin_program_undetectable_by_design", {"pid": 313, "ppid": 1, "exe": FW_PY,
                                              "args": f"{FW_PY} -"}, "FOREIGN_PYTHON"),
]


def planted_controls() -> dict:
    rows = [r for _n, r, _e in PLANTED]
    got = {r["pid"]: r["class"] for r in classify(rows, self_chain={200, 199, 1})}
    res = {name: {"expected": exp, "got": got[r["pid"]], "pass": got[r["pid"]] == exp}
           for name, r, exp in PLANTED}
    return {"cases": res, "ALL_PASS": all(v["pass"] for v in res.values())}


def live_controls() -> dict:
    """On THIS host: a real framework-build child with campaign argv must be seen; a shell whose
    command string mentions a campaign script must not; after the child exits it must be gone."""
    import tempfile
    marker = "c11r_live_detector_probe.py"
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="c11r_procs_"))
    wrapper = tmp / "nt_wrapper_probe.py"
    wrapper.write_text("import time\nif False:\n    import c11r_boxdata\ntime.sleep(30)\n")
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)", marker])
    shell = subprocess.Popen(["/bin/sh", "-c", f"sleep 30; : {marker}"])
    wrap = subprocess.Popen([sys.executable, "-B", str(wrapper)])
    bc = subprocess.Popen([sys.executable, "-Bc", "import time; time.sleep(30); x = 'c11r_live'"])
    try:
        seen = None
        for _ in range(20):
            w = campaign_workers()
            seen = [x for x in w["workers"] if x["pid"] == child.pid]
            if seen:
                break
            time.sleep(0.2)
        w2 = campaign_workers()["workers"]
        shell_seen = [x for x in w2 if x["pid"] == shell.pid]
        self_seen = [x for x in w2 if x["pid"] == os.getpid()]
        wrap_seen = [x for x in w2 if x["pid"] == wrap.pid]
        bc_seen = [x for x in w2 if x["pid"] == bc.pid]
    finally:
        for proc in (child, shell, wrap, bc):
            proc.kill()
            proc.wait()
        shutil.rmtree(tmp, ignore_errors=True)
    gone = [x for x in campaign_workers()["workers"] if x["pid"] == child.pid]
    res = {"framework_child_with_campaign_argv_detected": bool(seen),
           "child_executable": seen[0]["exe"] if seen else None,
           "child_class": seen[0]["class"] if seen else None,
           "shell_mentioning_a_script_not_detected": not shell_seen,
           "detector_itself_not_detected": not self_seen,
           "exited_child_not_detected": not gone,
           "wrapper_script_importing_campaign_detected": bool(wrap_seen)
           and wrap_seen[0]["class"] == "CAMPAIGN_WRAPPER",
           "dash_Bc_child_detected": bool(bc_seen) and bc_seen[0]["class"] == "CAMPAIGN_ADHOC",
           "interpreter_under_test": sys.executable}
    res["ALL_PASS"] = all(v for k, v in res.items() if k.endswith(("detected", "_detected"))
                          and isinstance(v, bool))
    return res


def main() -> int:
    planted = planted_controls()
    live = live_controls()
    now = campaign_workers()
    ok = planted["ALL_PASS"] and live["ALL_PASS"]
    out = {"schema": f"C11R_PROCESS_DETECTOR/{DETECTOR_REVISION}",
           "supersedes": ("revision 2 (bd00c1f6), blind to wrapper scripts and to -Bc / -cpayload "
                          "(review round 4, N4-6); revision 1 (common.classified_processes), blind "
                          "to framework Python"),
           "mechanism": now["mechanism"],
           "interpreter_identity": ("executable basename matching ^python(\\d+(\\.\\d+)*)?w?$ "
                                    "case-insensitively, or an executable inside a "
                                    "Python.framework / Python.app bundle"),
           "campaign_relevance": ("argv (option clusters parsed): a campaign script basename, "
                                  "a -m campaign module, a -c payload naming the campaign, any "
                                  "argument naming the campaign namespace or a campaign module, "
                                  "or a script whose own source imports campaign code"),
           "self_exclusion": "this process and its whole ppid ancestor chain",
           "not_checked": ["processes invisible to ps for this user", "other hosts/containers",
                           "campaign work run by a non-Python executable",
                           "interpreters renamed outside the recognised forms",
                           "argv tokens containing spaces",
                           "a program read from stdin, or an interactive interpreter",
                           "a wrapper whose campaign import is indirect (through another module, "
                           "or code built at run time)", "a script this user cannot read"],
           "what_it_gates": ("concurrency only (cost measurement, runner pre-flight, B0, "
                             "regeneration); it cannot prove no competing computation ran"),
           "planted_controls": planted,
           "live_controls_on_this_host": live,
           "snapshot_at_write": {k: now[k] for k in ("processes_seen", "interpreters_seen",
                                                     "foreign_python")},
           "campaign_workers_at_write": now["workers"],
           "DETECTOR_CLASS": "PASS" if ok and not now["workers"] else "REFUSE"}
    s = C.write_evidence(C.NS / "evidence" / "procs" / "C11R_PROCESS_DETECTOR.json", out,
                         producer=__file__)
    for k, v in planted["cases"].items():
        print(f"  {'ok  ' if v['pass'] else 'FAIL'} {k:38s} -> {v['got']}")
    print(f"  live: {live}")
    print(f"  campaign workers now: {now['workers']}")
    print(f"DETECTOR_CLASS = {out['DETECTOR_CLASS']}")
    print(f"wrote evidence/procs/C11R_PROCESS_DETECTOR.json sha256 {s[:16]}...")
    return 0 if out["DETECTOR_CLASS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
