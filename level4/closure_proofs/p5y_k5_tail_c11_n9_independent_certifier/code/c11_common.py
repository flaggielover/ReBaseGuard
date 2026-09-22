"""C11 shared helpers. Governance-enabling verification campaign: close N9 by building a SECOND,
independently implemented certifier. No adoption, no coverage change, no r6.
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
AD = CLOSURE / "p5y_k5_perron_deflated_resolvent"

C10_HEAD = "ec969db1fcd1f5f5249fa2864a81c0cb284fa66e"
R5_PATH = "level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
ORIGINAL_CERTIFIER = "level4/closure_proofs/p5y_k5_perron_deflated_resolvent/code/taboo_certify.py"
OPEN_CELLS = (306, 307, 308, 309)


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


def load(p: pathlib.Path):
    return json.loads(p.read_text())


def write_evidence(p: pathlib.Path, obj: dict) -> str:
    body = {k: v for k, v in obj.items() if k != "sha256"}
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
                                               ("c11_", "c10_", "taboo_certify", "closure_proofs"))}
        rows.append({"pid": pid, "ppid": ppid, "executable": comm, "cwd": cwd, "signals": sig,
                     "classified": "CAMPAIGN_WORKER" if any(sig.values()) else "FOREIGN_UNRELATED"})
    return {"interpreters": rows,
            "campaign_workers": [r for r in rows if r["classified"] == "CAMPAIGN_WORKER"],
            "foreign": [r for r in rows if r["classified"] == "FOREIGN_UNRELATED"]}


def toolchain_present() -> dict:
    import importlib.util as u
    return {m: (u.find_spec(m) is not None) for m in
            ("numpy", "scipy", "flint", "mpmath", "sympy", "gmpy2")}
