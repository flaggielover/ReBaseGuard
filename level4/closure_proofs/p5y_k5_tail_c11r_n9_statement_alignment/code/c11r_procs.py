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

WHAT IT DOES NOT CHECK, stated exactly: processes not visible to `ps` for this user; processes
on other hosts or in containers; campaign work run by a non-Python executable; an interpreter
renamed to something that is neither python-like nor inside a Python framework bundle; argv
tokens containing spaces (ps joins argv with spaces, and tokens are split on whitespace).
Foreign Python processes are COUNTED and reported, not treated as campaign workers.
"""
from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C

PY_BASENAME = re.compile(r"^python(\d+(\.\d+)*)?w?$", re.IGNORECASE)
CAMPAIGN_SCRIPT = re.compile(r"^(c11r?_[A-Za-z0-9_]+|taboo_certify)\.py$")
CAMPAIGN_MODULE = re.compile(r"^(c11r?_[A-Za-z0-9_]+|taboo_certify)$")
TARGET_SCRIPTS = frozenset({"c11r_runs.py", "c11r_compare.py", "c11r_qualify.py"})


def is_python_executable(exe: str) -> bool:
    if not exe:
        return False
    if PY_BASENAME.match(pathlib.PurePosixPath(exe).name):
        return True
    low = exe.lower()
    return "/python.framework/" in low or "/python.app/" in low


def campaign_role(args: str | None) -> str | None:
    """The campaign role an interpreter's argv implies, or None."""
    if not args:
        return None
    toks = args.split()
    for i, t in enumerate(toks[1:], start=1):
        base = pathlib.PurePosixPath(t).name
        if CAMPAIGN_SCRIPT.match(base):
            return "TARGET" if base in TARGET_SCRIPTS else "NON_TARGET_PRODUCER"
        if t == "-m" and i + 1 < len(toks) and CAMPAIGN_MODULE.match(toks[i + 1]):
            return "TARGET" if toks[i + 1] + ".py" in TARGET_SCRIPTS else "NON_TARGET_PRODUCER"
        if t == "-c":
            payload = " ".join(toks[i + 1:])
            if re.search(r"\b(c11r?_[a-z0-9_]+|taboo_certify)\b", payload):
                return "CAMPAIGN_ADHOC"
            return None
    return None


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
            role = campaign_role(r["args"])
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
    return rows, ancestor_chain(ppid, os.getpid())


WORKER_CLASSES = ("TARGET", "NON_TARGET_PRODUCER", "CAMPAIGN_ADHOC")


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
    marker = "c11r_live_detector_probe.py"
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)", marker])
    shell = subprocess.Popen(["/bin/sh", "-c", f"sleep 30; : {marker}"])
    try:
        seen = None
        for _ in range(20):
            w = campaign_workers()
            seen = [x for x in w["workers"] if x["pid"] == child.pid]
            if seen:
                break
            time.sleep(0.2)
        shell_seen = [x for x in campaign_workers()["workers"] if x["pid"] == shell.pid]
        self_seen = [x for x in campaign_workers()["workers"] if x["pid"] == os.getpid()]
    finally:
        child.kill()
        shell.kill()
        child.wait()
        shell.wait()
    gone = [x for x in campaign_workers()["workers"] if x["pid"] == child.pid]
    res = {"framework_child_with_campaign_argv_detected": bool(seen),
           "child_executable": seen[0]["exe"] if seen else None,
           "child_class": seen[0]["class"] if seen else None,
           "shell_mentioning_a_script_not_detected": not shell_seen,
           "detector_itself_not_detected": not self_seen,
           "exited_child_not_detected": not gone,
           "interpreter_under_test": sys.executable}
    res["ALL_PASS"] = all(v for k, v in res.items() if k.endswith(("detected", "_detected"))
                          and isinstance(v, bool))
    return res


def main() -> int:
    planted = planted_controls()
    live = live_controls()
    now = campaign_workers()
    ok = planted["ALL_PASS"] and live["ALL_PASS"]
    out = {"schema": "C11R_PROCESS_DETECTOR/2",
           "supersedes": "common.classified_processes (revision 1), blind to framework Python",
           "mechanism": now["mechanism"],
           "interpreter_identity": ("executable basename matching ^python(\\d+(\\.\\d+)*)?w?$ "
                                    "case-insensitively, or an executable inside a "
                                    "Python.framework / Python.app bundle"),
           "campaign_relevance": ("argv tokens only: a campaign script basename, -m campaign "
                                  "module, or a -c payload naming a campaign module"),
           "self_exclusion": "this process and its whole ppid ancestor chain",
           "not_checked": ["processes invisible to ps for this user", "other hosts/containers",
                           "campaign work run by a non-Python executable",
                           "interpreters renamed outside the recognised forms",
                           "argv tokens containing spaces"],
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
