"""C8 shared helpers: committed-fact readers, canonical JSON, process identity.

C8 is a FEASIBILITY / ROUTE-SELECTION campaign. It computes NO new scientific values. Everything here
either reads a committed artifact or performs exact arithmetic over values already committed.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parent
CLOSURE = NS.parent
REPO = CLOSURE.parent.parent

C2 = CLOSURE / "p5y_k5_tail_c2_closure"
C4 = CLOSURE / "p5y_k5_tail_c4_exhaustion"
C5 = CLOSURE / "p5y_k5_tail_c5_exhaustion"
C6 = CLOSURE / "p5y_k5_tail_c6_evidence_recovery"
C7 = CLOSURE / "p5y_k5_tail_c7_e2_lambda309"

R5_PATH = "level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
C7_HEAD = "df4ec1791a5aa837a1e3dca26f9a1a329f283a9f"
C7_GATE_SHA = "9f7083b9ef45f48ede9addcc8374005187785c789cf7a24403bed2e519d4a604"
MODEL = CLOSURE / "p5y_k1_cover_ledger_implementation" / "code" / "cusum_layer1.py"
MODEL_SHA = "efcc0f36632632577a24c4ddf1a7c2c3579d471cdba5a752dd72c708667cdc79"

OPEN_CELLS = (306, 307, 308, 309)


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True,
                          check=True).stdout.strip()


def git_grep(pattern: str, *paths: str) -> list[str]:
    """`git grep -l` over HEAD, tolerating exit 1.

    git grep exits 1 when NOTHING matches. For an absence check -- "no guard ALLOW anywhere" -- that
    is the PASSING case, so treating a non-zero exit as an error would make the check crash exactly
    when it should succeed. Exit codes >1 are real failures and still raise.
    """
    r = subprocess.run(["git", "-C", str(REPO), "grep", "-l", "-E", pattern, "HEAD", "--", *paths],
                       capture_output=True, text=True)
    if r.returncode > 1:
        raise RuntimeError(f"git grep failed ({r.returncode}): {r.stderr[:200]}")
    return [ln for ln in r.stdout.strip().splitlines() if ln]


def git_ok(*a: str) -> bool:
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).returncode == 0


def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sha256_obj(o) -> str:
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load(p: pathlib.Path):
    return json.loads(p.read_text())


def write_evidence(p: pathlib.Path, obj: dict) -> str:
    body = {k: v for k, v in obj.items() if k != "sha256"}
    body["sha256"] = sha256_obj(body)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(body, indent=1, sort_keys=True) + "\n")
    return body["sha256"]


# -------------------------------------------------------------------------------------------------
# Process identity. C7's post-mortem found a waiter whose termination depended on grepping a
# TRUNCATED log, and a process audit that matched its own diagnostic command line. Both are banned.
# A worker is identified by its EXECUTABLE (ps -o comm), never by a command line that merely contains
# a string.
# -------------------------------------------------------------------------------------------------

def live_interpreters(names=("python3", "python", "python3.13", "python3.12")) -> list[dict]:
    """Processes whose EXECUTABLE basename is a Python interpreter, excluding this process and every
    ancestor of it, so a diagnostic can never match itself."""
    import os
    out = subprocess.run(["ps", "-eo", "pid=,ppid=,comm="], capture_output=True, text=True).stdout
    table = {}
    for ln in out.splitlines():
        parts = ln.split(None, 2)
        if len(parts) == 3:
            table[int(parts[0])] = (int(parts[1]), parts[2].strip())
    self_chain, cur = set(), os.getpid()
    for _ in range(64):
        self_chain.add(cur)
        if cur not in table or cur <= 1:
            break
        cur = table[cur][0]
    res = []
    for pid, (ppid, comm) in table.items():
        if pid in self_chain or pathlib.PurePath(comm).name not in names:
            continue
        res.append({"pid": pid, "ppid": ppid, "executable": comm})
    return res


def campaign_workers() -> dict:
    """Classify each live interpreter as a ReBaseGuard campaign worker or a foreign process.

    Executable identity alone is not enough -- an unrelated agent may also run `python`. Three
    INDEPENDENT signals are recorded per process, and a process counts as a campaign worker only if
    at least one positively ties it to this repository. A process is never classified by a command
    line that merely mentions a path, and this function cannot match itself because
    live_interpreters() removes the whole self ancestry chain.
    """
    procs = []
    for pr in live_interpreters():
        pid = pr["pid"]
        argv = subprocess.run(["ps", "-o", "args=", "-p", str(pid)],
                              capture_output=True, text=True).stdout.strip()
        cwd = ""
        lz = subprocess.run(["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"],
                            capture_output=True, text=True)
        for ln in lz.stdout.splitlines():
            if ln.startswith("n"):
                cwd = ln[1:]
        exe_in_repo = "ReBaseGuard" in pr["executable"]
        cwd_in_repo = "ReBaseGuard" in cwd
        argv_campaign = any(tok in argv for tok in ("c8_", "c7_", "c6_", "c5_", "c4_",
                                                    "closure_proofs"))
        procs.append({**pr, "cwd": cwd, "argv_head": argv[:120],
                      "signal_executable_in_repo": exe_in_repo,
                      "signal_cwd_in_repo": cwd_in_repo,
                      "signal_argv_references_campaign": argv_campaign,
                      "classified": ("CAMPAIGN_WORKER"
                                     if (exe_in_repo or cwd_in_repo or argv_campaign)
                                     else "FOREIGN_UNRELATED")})
    return {"interpreters": procs,
            "campaign_workers": [p for p in procs if p["classified"] == "CAMPAIGN_WORKER"],
            "foreign": [p for p in procs if p["classified"] == "FOREIGN_UNRELATED"]}


def toolchain_present() -> dict:
    """A real absence check: importlib resolution, not a claim."""
    import importlib.util as u
    return {m: (u.find_spec(m) is not None) for m in
            ("numpy", "scipy", "flint", "mpmath", "sympy", "gmpy2")}


# -------------------------------------------------------------------------------------------------
# Committed-fact readers
# -------------------------------------------------------------------------------------------------

def r5_map() -> dict:
    return json.loads(git("show", f"HEAD:{R5_PATH}"))


def r5_open_by_verdict(m: str = "5") -> list[int]:
    """Reconstruct the open set from PER-CELL verdicts, not from the summary ranges."""
    return sorted(c["cell"] for c in r5_map()["per_m"][m]["cells"] if c.get("verdict") == "OPEN")


def c7_certificate() -> dict:
    return load(C7 / "evidence" / "certificate" / "C7_CERTIFICATE.json")


def c4_cells() -> dict:
    return load(C4 / "evidence" / "certificate" / "C4_CERTIFICATE.json")["cells"]


def c5_forecast() -> dict:
    return load(C5 / "evidence" / "forecast" / "C5_FORECAST.json")
