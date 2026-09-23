"""C11R shared helpers. Narrow repair successor to C11: can the independent certifier prove THE
SAME STATEMENT N9 requires, for cell 306, over the frozen drift block. No adoption, no
coverage change, no r6, no alpha, no C2 floor replacement.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parent
CLOSURE = NS.parent
REPO = CLOSURE.parent.parent

C2 = CLOSURE / "p5y_k5_tail_c2_closure"
C7 = CLOSURE / "p5y_k5_tail_c7_e2_lambda309"
C9 = CLOSURE / "p5y_k5_tail_c9_e1_cell307"
C10 = CLOSURE / "p5y_k5_tail_c10_governance_provenance"
C11 = CLOSURE / "p5y_k5_tail_c11_n9_independent_certifier"
AD = CLOSURE / "p5y_k5_perron_deflated_resolvent"

C11_HEAD = "440bcd9183f4f883428cba41d47aa7780fd681c4"
REMOTE_MAIN_EXPECTED = "1cb453826313c189f0bdafd5b84120c1edb74da9"
R5_PATH = "level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
ORIGINAL_CERTIFIER = "level4/closure_proofs/p5y_k5_perron_deflated_resolvent/code/taboo_certify.py"
OPEN_CELLS = (306, 307, 308, 309)
TARGET_CELL = 306
SIX_CONSTANTS = ("C_T", "tau", "Abar", "D_lo", "D1", "D2")


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True,
                          check=True).stdout.strip()


def git_ok(*a: str) -> bool:
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).returncode == 0


def git_grep(pattern: str, *paths: str) -> list[str]:
    r = subprocess.run(["git", "-C", str(REPO), "grep", "-l", "-E", pattern, "HEAD", "--", *paths],
                       capture_output=True, text=True)
    if r.returncode > 1:
        raise RuntimeError(f"git grep failed: {r.stderr[:200]}")
    return [x for x in r.stdout.strip().splitlines() if x]


def blob_at(commit: str, path: str) -> bytes:
    return subprocess.run(["git", "-C", str(REPO), "show", f"{commit}:{path}"],
                          capture_output=True, check=True).stdout


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sha256_obj(o) -> str:
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


# ---------------------------------------------------------------------------------------------
# PROVENANCE (repair E, erratum E4). The first freeze carried a mutation artifact produced by
# older code than the validation artifact beside it, and nothing recorded which code produced
# either, so the contradiction could not be traced from the evidence. Every artifact now binds:
#   * the sha256 of its producer module,
#   * the sha256 of every campaign module the producer imports, transitively,
#   * the sha256 of every artifact it read through load().
# code/c11r_status.py recomputes all of them and refuses on any mismatch.
# ---------------------------------------------------------------------------------------------
CODE_DIRS = (HERE, C11 / "code", C7 / "code")
_READS: dict[str, str] = {}


def _rel(p: pathlib.Path) -> str:
    return str(pathlib.Path(p).resolve().relative_to(REPO))


def load(p: pathlib.Path):
    """Load a JSON artifact, and record what was read so the writer can bind it."""
    p = pathlib.Path(p)
    raw = p.read_bytes()
    _READS[_rel(p)] = sha256_bytes(raw)
    return json.loads(raw)


def _resolve_module(name: str) -> pathlib.Path | None:
    for d in CODE_DIRS:
        cand = d / f"{name}.py"
        if cand.exists():
            return cand
    return None


def code_closure(producer: pathlib.Path) -> dict[str, str]:
    """sha256 of the producer and of every campaign module it imports, transitively."""
    import ast
    seen: dict[str, str] = {}
    stack = [pathlib.Path(producer).resolve()]
    while stack:
        f = stack.pop()
        rel = _rel(f)
        if rel in seen:
            continue
        seen[rel] = sha256_file(f)
        for n in ast.walk(ast.parse(f.read_text())):
            names = []
            if isinstance(n, ast.Import):
                names = [a.name.split(".")[0] for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                names = [n.module.split(".")[0]]
            for nm in names:
                r = _resolve_module(nm)
                if r is not None:
                    stack.append(r.resolve())
    return dict(sorted(seen.items()))


def provenance(producer) -> dict:
    prod = pathlib.Path(producer).resolve()
    return {"producer": _rel(prod),
            "producer_sha256": sha256_file(prod),
            "code_closure": code_closure(prod),
            "inputs": dict(sorted(_READS.items()))}


def write_evidence(p: pathlib.Path, obj: dict, *, producer) -> str:
    """Write an artifact bound to the code and inputs that produced it.

    `producer` is MANDATORY. An artifact that cannot say which code made it is exactly the kind
    that let a REFUSE mutation record sit unnoticed beside a PASS validation (erratum E4).
    """
    if not producer:
        raise ValueError("write_evidence requires the producer module path")
    body = {k: v for k, v in obj.items() if k not in ("sha256", "provenance")}
    body["provenance"] = provenance(producer)
    body["sha256"] = sha256_obj(body)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(body, indent=1, sort_keys=True) + "\n")
    return body["sha256"]


def r5_map() -> dict:
    return json.loads(git("show", f"HEAD:{R5_PATH}"))


def r5_open_by_verdict(m: str = "5") -> list[int]:
    return sorted(c["cell"] for c in r5_map()["per_m"][m]["cells"] if c.get("verdict") == "OPEN")


def classified_processes(interp=("python3", "python", "python3.14", "python3.12", "python3.11")) -> dict:
    """Executable identity, whole self-ancestry removed. Never pgrep -f or ps|grep alone."""
    import os
    out = subprocess.run(["ps", "-eo", "pid=,ppid=,comm="], capture_output=True, text=True).stdout
    table = {}
    for ln in out.splitlines():
        parts = ln.split(None, 2)
        if len(parts) == 3:
            table[int(parts[0])] = (int(parts[1]), parts[2].strip())
    chain, cur = set(), os.getpid()
    for _ in range(64):
        chain.add(cur)
        if cur not in table or cur <= 1:
            break
        cur = table[cur][0]
    rows = []
    for pid, (ppid, comm) in table.items():
        if pid in chain or pathlib.PurePath(comm).name not in interp:
            continue
        argv = subprocess.run(["ps", "-o", "args=", "-p", str(pid)],
                              capture_output=True, text=True).stdout.strip()
        cwd = ""
        for ln in subprocess.run(["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"],
                                 capture_output=True, text=True).stdout.splitlines():
            if ln.startswith("n"):
                cwd = ln[1:]
        sig = {"executable_in_repo": "ReBaseGuard" in comm, "cwd_in_repo": "ReBaseGuard" in cwd,
               "argv_references_campaign": any(t in argv for t in
                                               ("c11r_", "c11_", "taboo_certify", "closure_proofs"))}
        rows.append({"pid": pid, "ppid": ppid, "executable": comm, "cwd": cwd, "signals": sig,
                     "classified": "CAMPAIGN_WORKER" if any(sig.values()) else "FOREIGN_UNRELATED"})
    return {"interpreters": rows,
            "campaign_workers": [r for r in rows if r["classified"] == "CAMPAIGN_WORKER"],
            "foreign": [r for r in rows if r["classified"] == "FOREIGN_UNRELATED"]}


def toolchain_present() -> dict:
    import importlib.util as u
    return {m: (u.find_spec(m) is not None) for m in
            ("numpy", "scipy", "flint", "mpmath", "sympy", "gmpy2")}
