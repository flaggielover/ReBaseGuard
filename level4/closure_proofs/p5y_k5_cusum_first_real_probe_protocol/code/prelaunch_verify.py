"""READ-ONLY prelaunch verifier of the first governed real CUSUM signed-R''' probe. Fail closed.

    python3 -B code/prelaunch_verify.py [--authorization protocol/AUTHORIZATION_TEMPLATE.json] [--out report.json]

It never imports flint, never builds a certifier, never reads an operator and never writes outside --out. It prints
LAUNCH_PERMITTED (exit 0) only if every check passes, otherwise REFUSED (exit 3) with the FIRST failing check in the
frozen order as the primary reason; all checks are still evaluated and reported.

    P01 EXECUTION_AUTHORIZED is true
    P02 authorization object matches the frozen preregistration (protocol sha256, cell, m, precision, CPU, host, K1, producer)
    P03 temporal: PROTOCOL_FREEZE_COMMIT introduced the science file, the file is unchanged since, HEAD descends from it
    P04 protected hashes: R1-R4 pins (R4 protocol), preregistration references, this packet's manifest
    P05 executor binding: a qualified EXECUTION_BINDING_AMENDMENT.json pins the executor and leaves the science file unchanged
    P06 host runtime identity equals the frozen contract (live facts)
    P07 no conflicting real producer process (exact argv element match over /proc; own process tree excluded)
    P08 no finalized scientific record exists for any frozen address
    P09 CPU ceiling valid and equal to the preregistration
    P10 output namespace new or empty
    P11 no file in the output namespace predates the authorization
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
SCIENCE = NS / "protocol/SCIENCE_PREREGISTRATION.json"
BINDING = NS / "protocol/EXECUTION_BINDING.json"
AMENDMENT = NS / "protocol/EXECUTION_BINDING_AMENDMENT.json"
MANIFEST = NS / "protocol/PACKET_MANIFEST.json"
SCIENCE_SHA256_PINNED = "3d2eab4c3455a0a0075b65dceaca3e4db660edffe3784f6c36e51f3a38c5c2fb"
R4_PROTOCOL = REPO / "level4/closure_proofs/p5y_k5_cusum_order3_r4_tightening/config/QUALIFICATION_PROTOCOL_R4.json"
CONFLICTING_ARGV_BASENAMES = ("first_real_probe_executor.py", "cusum_order3.py", "qualify5.py", "gs_entry.py")
ORDER = ["P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09", "P10", "P11"]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


def _unset(obj) -> list[str]:
    s = json.dumps(obj)
    return ["SET_AT_ACTIVATION"] if "SET_AT_ACTIVATION" in s else []


def check_P01(auth, prereg):
    ok = auth.get("EXECUTION_AUTHORIZED") is True
    return ok, "EXECUTION_NOT_AUTHORIZED: EXECUTION_AUTHORIZED is not true" if not ok else "authorized"


def check_P02(auth, prereg):
    problems = []
    if auth.get("PROTOCOL_SHA256") != SCIENCE_SHA256_PINNED or sha(SCIENCE.read_bytes()) != SCIENCE_SHA256_PINNED:
        problems.append("protocol sha256 mismatch")
    for key, want in (("CELL_SET", [0]), ("M_SET", prereg["m_values"]["set"]), ("PRECISION_POLICY", prereg["precision_ladder"]),
                      ("CPU_CEILING", prereg["cpu_ceiling"]), ("K1_INPUT_IDENTITY", prereg["k1_input_identity"]),
                      ("POINT_E", "0/1"), ("THEOREM_CELL", "C_1")):
        if auth.get(key) != want:
            problems.append(f"{key} differs from the preregistration")
    if (auth.get("HOST_RUNTIME_IDENTITY") or {}).get("sha256") != prereg["host_runtime_identity_sha256"]:
        problems.append("host runtime identity differs")
    if (auth.get("PRODUCER_R4_IDENTITY") or {}).get("producer_identity_sha256") != prereg["producer_identity_sha256"]:
        problems.append("producer identity differs")
    problems += [f"unfilled field: {u}" for u in _unset(auth)]
    for key in ("AUTHORIZED_BY", "AUTHORIZATION_UTC", "AUTHORIZATION_COMMIT"):
        if not auth.get(key):
            problems.append(f"{key} missing")
    return not problems, "; ".join(problems) or "authorization matches the preregistration"


def check_P03(auth, prereg):
    rel = str(SCIENCE.relative_to(REPO))
    intro = git("log", "--diff-filter=A", "--format=%H", "--", rel).stdout.split()
    if len(intro) != 1:
        return False, f"science file introduced by {len(intro)} commits (expected exactly 1)"
    touched = git("log", "--format=%H", "--", rel).stdout.split()
    problems = []
    if touched != intro:
        problems.append("science file changed after its introducing commit")
    if auth.get("PROTOCOL_FREEZE_COMMIT") != intro[0]:
        problems.append(f"PROTOCOL_FREEZE_COMMIT != introducing commit {intro[0][:12]}")
    if git("merge-base", "--is-ancestor", intro[0], "HEAD").returncode != 0:
        problems.append("HEAD does not descend from the freeze commit")
    if git("status", "--porcelain", "--", str(NS.relative_to(REPO))).stdout.strip():
        problems.append("protocol namespace has uncommitted changes")
    return not problems, "; ".join(problems) or f"freeze commit {intro[0][:12]} verified"


def check_P04(auth, prereg):
    moved = []
    r4 = json.loads(R4_PROTOCOL.read_text())
    for key in ("r1_bound_sha256", "r2_bound_sha256", "r3_bound_sha256", "bound_code_sha256", "bound_config_sha256"):
        moved += [rel for rel, h in r4[key].items() if not (REPO / rel).exists() or sha((REPO / rel).read_bytes()) != h]
    if sha(R4_PROTOCOL.read_bytes()) != prereg["producer_identity"]["r4_protocol_sha256"]:
        moved.append("R4 protocol")
    for rel, h in prereg["references_sha256"].items():
        if not (REPO / rel).exists() or sha((REPO / rel).read_bytes()) != h:
            moved.append(rel)
    if not MANIFEST.exists():
        moved.append("PACKET_MANIFEST.json missing")
    else:
        for rel, h in json.loads(MANIFEST.read_text())["files"].items():
            if not (NS / rel).exists() or sha((NS / rel).read_bytes()) != h:
                moved.append(f"packet:{rel}")
    return not moved, f"moved: {moved[:8]}" if moved else "all protected hashes match"


def check_P05(auth, prereg):
    if not AMENDMENT.exists():
        status = json.loads(BINDING.read_text())["status"]
        return False, f"EXECUTOR_BINDING_PENDING: no EXECUTION_BINDING_AMENDMENT.json (binding status {status})"
    am = json.loads(AMENDMENT.read_text())
    problems = []
    if am.get("status") != "BOUND_QUALIFIED":
        problems.append(f"amendment status {am.get('status')}")
    if am.get("science_preregistration_sha256") != SCIENCE_SHA256_PINNED:
        problems.append("amendment names another science file")
    for rel, h in (am.get("executor_sources_sha256") or {}).items():
        if not (REPO / rel).exists() or sha((REPO / rel).read_bytes()) != h:
            problems.append(f"executor source moved: {rel}")
    if not am.get("executor_sources_sha256"):
        problems.append("no executor sources pinned")
    if (auth.get("PRODUCER_R4_IDENTITY") or {}).get("executor_binding_sha256") != sha(AMENDMENT.read_bytes()):
        problems.append("authorization names another executor binding")
    return not problems, "; ".join(problems) or "executor bound and qualified"


def live_host_facts() -> dict:
    facts = {"host": platform.node(), "machine": platform.machine(), "python": platform.python_version(),
             "venv_prefix": sys.prefix}
    try:
        facts["kernel_release"] = platform.release()
        facts["cpu_model"] = next((l.split(":", 1)[1].strip() for l in Path("/proc/cpuinfo").read_text().splitlines()
                                   if l.startswith("model name")), None)
        facts["logical_cpus"] = os.cpu_count()
        facts["glibc_package_version"] = subprocess.run(["dpkg-query", "-W", "-f=${Version}", "libc6"],
                                                        capture_output=True, text=True).stdout.strip() or None
        libc = Path("/usr/lib/x86_64-linux-gnu/libc.so.6")
        facts["libc_path"] = str(libc)
        facts["libc_sha256"] = sha(libc.read_bytes()) if libc.exists() else None
    except OSError:
        pass
    from importlib import metadata
    for dist, key in (("python-flint", "python_flint"), ("numpy", "numpy"), ("scipy", "scipy")):
        try:
            facts[key] = metadata.version(dist)
        except metadata.PackageNotFoundError:
            facts[key] = None
    so = Path(sys.prefix) / "lib/python3.12/site-packages/flint/pyflint.abi3.so"
    facts["flint_so_sha256"] = sha(so.read_bytes()) if so.exists() else None
    return facts


def check_P06(auth, prereg):
    want = prereg["host_runtime_contract"]
    live = live_host_facts()
    diff = {k: {"frozen": v, "live": live.get(k)} for k, v in want.items() if live.get(k) != v}
    return not diff, f"host differs: {sorted(diff)}" if diff else "host runtime identity matches", live


def _own_tree() -> set[int]:
    pids, pid = set(), os.getpid()
    while pid > 1:
        pids.add(pid)
        try:
            stat = Path(f"/proc/{pid}/stat").read_text()
            pid = int(stat.rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            break
    return pids


def check_P07(auth, prereg):
    proc = Path("/proc")
    if not proc.exists():
        return False, "no /proc: cannot prove absence of conflicting producers (not the frozen host)"
    own, hits = _own_tree(), []
    for d in proc.iterdir():
        if not d.name.isdigit() or int(d.name) in own:
            continue
        try:
            argv = (d / "cmdline").read_bytes().split(b"\0")
        except OSError:
            continue
        names = {Path(a.decode(errors="replace")).name for a in argv if a}
        if names & set(CONFLICTING_ARGV_BASENAMES):
            hits.append({"pid": int(d.name), "argv": [a.decode(errors="replace") for a in argv if a][:4]})
    return not hits, f"conflicting producers: {hits}" if hits else "no conflicting producer"


def _namespace(auth) -> Path | None:
    ns = auth.get("OUTPUT_NAMESPACE")
    return Path(ns) if ns else None


def check_P08(auth, prereg):
    found = [str(p) for p in NS.rglob("SCIENTIFIC_RECORD_SEALED.json")]
    ns = _namespace(auth)
    if ns and ns.exists():
        found += [str(p) for p in ns.rglob("SCIENTIFIC_RECORD_SEALED.json")]
    return not found, f"finalized records exist: {found}" if found else "no finalized record for any frozen address"


def check_P09(auth, prereg):
    c = auth.get("CPU_CEILING") or {}
    ok = (c == prereg["cpu_ceiling"] and c["per_attempt_cpu_seconds_rlimit"] > 0
          and c["per_attempt_cpu_seconds_rlimit"] * c["max_attempts"] <= c["campaign_cpu_seconds_hard"]
          and c["per_attempt_cpu_seconds_rlimit"] >= 2 * prereg["cost_model"]["estimate_per_attempt_cpu_seconds"])
    return ok, "CPU ceiling valid" if ok else "CPU ceiling invalid or differs"


def check_P10(auth, prereg):
    ns = _namespace(auth)
    if ns is None:
        return False, "no output namespace"
    if not ns.exists():
        return True, "output namespace new"
    entries = list(ns.iterdir())
    return not entries, "output namespace empty" if not entries else f"output namespace not empty ({len(entries)} entries)"


def check_P11(auth, prereg):
    ns, when = _namespace(auth), auth.get("AUTHORIZATION_UTC")
    if not when:
        return False, "no AUTHORIZATION_UTC"
    t = datetime.fromisoformat(when.replace("Z", "+00:00")).timestamp()
    old = [str(p) for p in (ns.rglob("*") if ns and ns.exists() else []) if p.stat().st_mtime < t]
    return not old, f"files predate authorization: {old[:5]}" if old else "nothing predates authorization"


def verify(auth_path: Path) -> dict:
    prereg = json.loads(SCIENCE.read_text())
    auth = json.loads(auth_path.read_text())
    checks, live = {}, None
    for cid in ORDER:
        try:
            res = globals()[f"check_{cid}"](auth, prereg)
        except Exception as exc:                                              # fail closed
            res = (False, f"check raised {type(exc).__name__}: {exc}")
        if cid == "P06" and len(res) == 3:
            live = res[2]
        checks[cid] = {"pass": bool(res[0]), "detail": res[1]}
    failing = [c for c in ORDER if not checks[c]["pass"]]
    return {"schema": "rebaseguard.p5y.k5.cusum-first-real-probe.prelaunch-report.v1",
            "verdict": "LAUNCH_PERMITTED" if not failing else "REFUSED",
            "primary_reason": None if not failing else f"{failing[0]}: {checks[failing[0]]['detail']}",
            "failing_checks": failing, "checks": checks, "authorization_sha256": sha(auth_path.read_bytes()),
            "science_sha256": sha(SCIENCE.read_bytes()), "live_host_facts": live,
            "head": git("rev-parse", "HEAD").stdout.strip(), "read_only": True}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authorization", default=str(NS / "protocol/AUTHORIZATION_TEMPLATE.json"))
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    rep = verify(Path(a.authorization))
    text = json.dumps(rep, indent=1, sort_keys=True, default=str)
    if a.out:
        Path(a.out).write_text(text + "\n")
    print(text)
    return 0 if rep["verdict"] == "LAUNCH_PERMITTED" else 3


if __name__ == "__main__":
    sys.exit(main())
