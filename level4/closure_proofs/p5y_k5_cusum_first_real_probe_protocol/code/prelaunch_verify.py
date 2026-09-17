"""READ-ONLY prelaunch verifier of the first governed real CUSUM signed-R''' probe, r2. Fail closed.

    python3 -B code/prelaunch_verify.py [--authorization PATH] [--out report.json]

Never imports flint, never builds a certifier, never reads an operator, never writes outside --out. LAUNCH_PERMITTED
(exit 0) only if every check passes; otherwise REFUSED (exit 3) with the FIRST failing check in the frozen order as the
primary reason (all checks are evaluated and reported; an exception inside a check fails that check).

    P01 EXECUTION_AUTHORIZED is true
    P02 authorization content: fixed committed path, protocol sha256, cell / m / precision / CPU / host / K1 / producer,
        pinned OUTPUT_NAMESPACE, no unfilled field, AUTHORIZED_BY
    P03 protocol freeze: the r2 science file is introduced by exactly one commit, unchanged since, HEAD descends from it,
        and every pinned packet code file at HEAD is byte-equal to its blob at that commit
    P04 authorization temporal: the authorization file is committed at its fixed path; AUTHORIZATION_COMMIT := the commit
        that introduced it (derived from git; the file may not claim it) and it is unchanged since; freeze commit and
        amendment commit are ancestors of it; it is an ancestor of HEAD; AUTHORIZATION_UTC within one hour of its committer
        time and not before the amendment commit
    P05 protected hashes: R1-R4 pins (R4 protocol), preregistration references, packet code sha256
    P06 executor binding: committed amendment with whitelisted keys, BOUND_QUALIFIED, same science sha256, executor entry
        among pinned sources, qualification evidence and independent review pinned and present, review verdict accepted,
        authorization names this amendment
    P07 host runtime identity equals the frozen contract (live facts)
    P08 no conflicting real producer process (exact argv element basenames over /proc; own ancestry excluded)
    P09 no sealed record (scientific or VOID) exists for this protocol: namespace root, packet tree, all git history
    P10 CPU ceiling valid and equal to the preregistration
    P11 attempt slot: every existing entry is an attempt-N directory with RUN_FAILED.json; attempts that started arithmetic
        failed only with a transient class; fewer than max_attempts started; the next slot is valid and does not exist
    P12 no file in the output namespace predates the authorization
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
sys.path.insert(0, str(NS / "code"))

import probe_rules as PR  # noqa: E402

SCIENCE = NS / "protocol/SCIENCE_PREREGISTRATION_R2.json"
BINDING = NS / "protocol/EXECUTION_BINDING_R2.json"
AMENDMENT = NS / "protocol/EXECUTION_BINDING_AMENDMENT.json"
AUTH_ACTIVE = NS / "protocol/AUTHORIZATION_ACTIVE.json"
R4_PROTOCOL = REPO / "level4/closure_proofs/p5y_k5_cusum_order3_r4_tightening/config/QUALIFICATION_PROTOCOL_R4.json"
CONFLICTING_ARGV_BASENAMES = ("first_real_probe_executor.py", "cusum_order3.py", "qualify5.py", "gs_entry.py")
ORDER = [f"P{i:02d}" for i in range(1, 13)]
AMENDMENT_KEYS = {"schema", "status", "science_preregistration_sha256", "executor_entry", "executor_sources_sha256",
                  "qualification_evidence_sha256", "independent_review", "independent_review_sha256",
                  "independent_review_verdict", "amendment_rule_ack"}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


def rel(p: Path) -> str:
    return str(p.resolve().relative_to(REPO.resolve()))


def introduced_by(path: Path) -> list[str]:
    return git("log", "--diff-filter=A", "--format=%H", "--", rel(path)).stdout.split()


def touched_by(path: Path) -> list[str]:
    return git("log", "--format=%H", "--", rel(path)).stdout.split()


def is_ancestor(a: str, b: str) -> bool:
    return git("merge-base", "--is-ancestor", a, b).returncode == 0


def committed_unmodified(path: Path) -> bool:
    r = git("ls-files", "--error-unmatch", rel(path))
    return r.returncode == 0 and not git("status", "--porcelain", "--", rel(path)).stdout.strip()


# ------------------------------------------------------------------ checks
def check_P01(auth, prereg, ctx):
    ok = auth.get("EXECUTION_AUTHORIZED") is True
    return ok, "authorized" if ok else "EXECUTION_NOT_AUTHORIZED: EXECUTION_AUTHORIZED is not true"


def check_P02(auth, prereg, ctx):
    p = []
    if ctx["auth_path"].resolve() != AUTH_ACTIVE.resolve():
        p.append("authorization is not at the fixed path protocol/AUTHORIZATION_ACTIVE.json")
    if auth.get("PROTOCOL_SHA256") != sha(SCIENCE.read_bytes()):
        p.append("protocol sha256 mismatch")
    for key, want in (("CELL_SET", [0]), ("M_SET", prereg["m_values"]["set"]), ("PRECISION_POLICY", prereg["precision_ladder"]),
                      ("CPU_CEILING", prereg["cpu_ceiling"]), ("K1_INPUT_IDENTITY", prereg["k1_input_identity"]),
                      ("POINT_E", "0/1"), ("THEOREM_CELL", "C_1"), ("OUTPUT_NAMESPACE", prereg["output_namespace"])):
        if auth.get(key) != want:
            p.append(f"{key} differs from the preregistration")
    if (auth.get("HOST_RUNTIME_IDENTITY") or {}).get("sha256") != prereg["host_runtime_identity_sha256"]:
        p.append("host runtime identity differs")
    if (auth.get("PRODUCER_R4_IDENTITY") or {}).get("producer_identity_sha256") != prereg["producer_identity_sha256"]:
        p.append("producer identity differs")
    if "SET_AT_ACTIVATION" in json.dumps(auth):
        p.append("unfilled SET_AT_ACTIVATION field")
    if not isinstance(auth.get("AUTHORIZED_BY"), str) or not auth.get("AUTHORIZED_BY").strip():
        p.append("AUTHORIZED_BY missing")
    return not p, "; ".join(p) or "authorization content matches the preregistration"


def check_P03(auth, prereg, ctx):
    intro = introduced_by(SCIENCE)
    if len(intro) != 1:
        return False, f"r2 science file introduced by {len(intro)} commits (expected exactly 1)"
    p = []
    if touched_by(SCIENCE) != intro:
        p.append("science file changed after its introducing commit")
    if auth.get("PROTOCOL_FREEZE_COMMIT") != intro[0]:
        p.append(f"PROTOCOL_FREEZE_COMMIT != introducing commit {intro[0][:12]}")
    if not is_ancestor(intro[0], "HEAD"):
        p.append("HEAD does not descend from the freeze commit")
    for relpath in prereg["packet_code_sha256"]:
        blob = subprocess.run(["git", "-C", str(REPO), "show", f"{intro[0]}:{relpath}"], capture_output=True)
        if blob.returncode != 0 or blob.stdout != (REPO / relpath).read_bytes():
            p.append(f"{relpath} differs from its blob at the freeze commit")
    if git("status", "--porcelain", "--untracked-files=no", "--", rel(NS)).stdout.strip():
        p.append("tracked packet files have uncommitted changes")
    return not p, "; ".join(p) or f"freeze commit {intro[0][:12]} verified"


def check_P04(auth, prereg, ctx):
    p = []
    if not committed_unmodified(AUTH_ACTIVE):
        return False, "AUTHORIZATION_ACTIVE.json is not committed and unmodified"
    intro = introduced_by(AUTH_ACTIVE)
    if len(intro) != 1 or touched_by(AUTH_ACTIVE) != intro:
        return False, "authorization file must be introduced once and never changed"
    ac = intro[0]                                  # AUTHORIZATION_COMMIT is derived from git, never read from the file
    ctx["authorization_commit"] = ac
    if "AUTHORIZATION_COMMIT" in auth:
        p.append("the authorization file must not claim its own commit")
    if not is_ancestor(str(auth.get("PROTOCOL_FREEZE_COMMIT")), ac):
        p.append("freeze commit is not an ancestor of the authorization commit")
    am = introduced_by(AMENDMENT) if AMENDMENT.exists() else []
    if len(am) != 1 or not is_ancestor(am[0], ac):
        p.append("amendment commit is not an ancestor of the authorization commit")
    if not is_ancestor(ac, "HEAD"):
        p.append("authorization commit is not an ancestor of HEAD")
    try:
        t_auth = datetime.fromisoformat(str(auth.get("AUTHORIZATION_UTC")).replace("Z", "+00:00")).timestamp()
        t_commit = int(git("show", "-s", "--format=%ct", ac).stdout.strip())
        if abs(t_auth - t_commit) > 3600:
            p.append("AUTHORIZATION_UTC is not within one hour of the authorization commit time")
        if am and t_auth < int(git("show", "-s", "--format=%ct", am[0]).stdout.strip()):
            p.append("AUTHORIZATION_UTC predates the amendment commit")
    except (ValueError, TypeError):
        p.append("AUTHORIZATION_UTC unparseable")
    return not p, "; ".join(p) or f"authorization commit {ac[:12]} verified"


def check_P05(auth, prereg, ctx):
    moved = []
    r4 = json.loads(R4_PROTOCOL.read_text())
    for key in ("r1_bound_sha256", "r2_bound_sha256", "r3_bound_sha256", "bound_code_sha256", "bound_config_sha256"):
        moved += [r for r, h in r4[key].items() if not (REPO / r).exists() or sha((REPO / r).read_bytes()) != h]
    for table in ("references_sha256", "packet_code_sha256"):
        moved += [r for r, h in prereg[table].items() if not (REPO / r).exists() or sha((REPO / r).read_bytes()) != h]
    return not moved, f"moved: {moved[:8]}" if moved else "all protected hashes match"


def check_P06(auth, prereg, ctx):
    if not AMENDMENT.exists():
        status = json.loads(BINDING.read_text())["status"]
        return False, f"EXECUTOR_BINDING_PENDING: no EXECUTION_BINDING_AMENDMENT.json (binding status {status})"
    am = json.loads(AMENDMENT.read_text())
    p = []
    if not committed_unmodified(AMENDMENT) or touched_by(AMENDMENT) != introduced_by(AMENDMENT):
        p.append("amendment not committed once and unchanged")
    if set(am) - AMENDMENT_KEYS:
        p.append(f"amendment carries non-whitelisted keys {sorted(set(am) - AMENDMENT_KEYS)}")
    if am.get("status") != "BOUND_QUALIFIED":
        p.append(f"amendment status {am.get('status')}")
    if am.get("science_preregistration_sha256") != sha(SCIENCE.read_bytes()):
        p.append("amendment names another science file")
    srcs = am.get("executor_sources_sha256") or {}
    if not srcs or am.get("executor_entry") not in srcs:
        p.append("executor entry is not among the pinned sources")
    for table in ("executor_sources_sha256", "qualification_evidence_sha256"):
        items = am.get(table) or {}
        if not items:
            p.append(f"{table} empty")
        p += [f"{table} moved: {r}" for r, h in items.items() if not (REPO / r).exists() or sha((REPO / r).read_bytes()) != h]
    review = am.get("independent_review")
    if not review or not (REPO / review).exists() or sha((REPO / review).read_bytes()) != am.get("independent_review_sha256"):
        p.append("independent review missing or moved")
    if am.get("independent_review_verdict") not in ("PASS", "PASS_WITH_SCOPE_LIMITATION"):
        p.append("independent review verdict not accepted")
    if (auth.get("PRODUCER_R4_IDENTITY") or {}).get("executor_binding_sha256") != sha(AMENDMENT.read_bytes()):
        p.append("authorization names another executor binding")
    return not p, "; ".join(p) or "executor bound, qualified and reviewed"


def live_host_facts() -> dict:
    facts = {"host": platform.node(), "machine": platform.machine(), "python": platform.python_version(),
             "venv_prefix": sys.prefix, "kernel_release": platform.release(), "logical_cpus": os.cpu_count()}
    try:
        facts["cpu_model"] = next((l.split(":", 1)[1].strip() for l in Path("/proc/cpuinfo").read_text().splitlines()
                                   if l.startswith("model name")), None)
        facts["glibc_package_version"] = subprocess.run(["dpkg-query", "-W", "-f=${Version}", "libc6"],
                                                        capture_output=True, text=True).stdout.strip() or None
    except OSError:
        pass
    libc = Path("/usr/lib/x86_64-linux-gnu/libc.so.6")
    facts["libc_path"] = str(libc)
    facts["libc_sha256"] = sha(libc.read_bytes()) if libc.exists() else None
    from importlib import metadata
    for dist, key in (("python-flint", "python_flint"), ("numpy", "numpy"), ("scipy", "scipy")):
        try:
            facts[key] = metadata.version(dist)
        except metadata.PackageNotFoundError:
            facts[key] = None
    so = Path(sys.prefix) / "lib/python3.12/site-packages/flint/pyflint.abi3.so"
    facts["flint_so_sha256"] = sha(so.read_bytes()) if so.exists() else None
    return facts


def check_P07(auth, prereg, ctx):
    live = live_host_facts()
    ctx["live"] = live
    diff = sorted(k for k, v in prereg["host_runtime_contract"].items() if live.get(k) != v)
    return not diff, f"host differs: {diff}" if diff else "host runtime identity matches"


def _own_ancestry() -> set[int]:
    pids, pid = set(), os.getpid()
    while pid > 1:
        pids.add(pid)
        try:
            pid = int(Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            break
    return pids


def check_P08(auth, prereg, ctx):
    proc = Path("/proc")
    if not proc.exists():
        return False, "no /proc: cannot prove absence of conflicting producers (not the frozen host)"
    own, hits = _own_ancestry(), []
    for d in proc.iterdir():
        if not d.name.isdigit() or int(d.name) in own:
            continue
        try:
            argv = [a.decode(errors="replace") for a in (d / "cmdline").read_bytes().split(b"\0") if a]
        except OSError:
            continue
        if {Path(a).name for a in argv} & set(CONFLICTING_ARGV_BASENAMES):
            hits.append({"pid": int(d.name), "argv": argv[:4]})
    return not hits, f"conflicting producers: {hits}" if hits else "no conflicting producer"


SEALED_NAMES = ("SCIENTIFIC_RECORD_SEALED.json", "VOID_RECORD_SEALED.json")


def check_P09(auth, prereg, ctx):
    found = [str(p) for n in SEALED_NAMES for p in NS.rglob(n)]
    root = Path(prereg["output_namespace"])
    if root.exists():
        found += [str(p) for n in SEALED_NAMES for p in root.rglob(n)]
    hist = git("log", "--all", "--format=", "--name-only").stdout.split()
    found += sorted({h for h in hist if Path(h).name in SEALED_NAMES})
    return not found, f"sealed records exist: {found[:5]}" if found else "no sealed record for this protocol"


def check_P10(auth, prereg, ctx):
    c = auth.get("CPU_CEILING") or {}
    try:
        ok = (c == prereg["cpu_ceiling"] and c["per_attempt_cpu_seconds_rlimit"] > 0
              and c["per_attempt_cpu_seconds_rlimit"] * c["max_attempts"] <= c["campaign_cpu_seconds_hard"]
              and c["per_attempt_cpu_seconds_rlimit"] >= 2 * prereg["cost_model"]["estimate_per_attempt_cpu_seconds"])
    except (KeyError, TypeError):
        ok = False
    return ok, "CPU ceiling valid" if ok else "CPU ceiling invalid or differs"


def check_P11(auth, prereg, ctx):
    root = Path(prereg["output_namespace"])
    rp = prereg["retry_policy"]
    entries = sorted(root.iterdir()) if root.exists() else []
    started = 0
    for d in entries:
        if not d.is_dir() or not d.name.startswith("attempt-"):
            return False, f"unexpected entry in the namespace root: {d.name}"
        failed = d / "RUN_FAILED.json"
        if not failed.exists():
            return False, f"{d.name} has no RUN_FAILED.json (running, sealed or unknown)"
        info = json.loads(failed.read_text())
        if info.get("arithmetic_started") is not False:
            started += 1
            if info.get("failure_class") not in rp["transient_failure_classes_after_arithmetic"]:
                return False, f"{d.name} failed after arithmetic with non-transient class {info.get('failure_class')}"
    if started >= rp["max_attempts"]:
        return False, "maximum attempts reached"
    try:
        slot = PR.attempt_dir(len(entries) + 1)
    except PR.RuleViolation as exc:
        return False, f"no attempt slot left: {exc}"
    if (root / slot).exists():
        return False, f"next attempt slot {slot} already exists"
    return True, f"next attempt slot {slot}"


def check_P12(auth, prereg, ctx):
    when = auth.get("AUTHORIZATION_UTC")
    try:
        t = datetime.fromisoformat(str(when).replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError):
        return False, "no valid AUTHORIZATION_UTC"
    root = Path(prereg["output_namespace"])
    old = [str(p) for p in (root.rglob("*") if root.exists() else []) if p.stat().st_mtime < t]
    return not old, f"files predate authorization: {old[:5]}" if old else "nothing predates authorization"


def verify(auth_path: Path) -> dict:
    prereg = json.loads(SCIENCE.read_text())
    auth = json.loads(auth_path.read_text())
    ctx, checks = {"auth_path": auth_path, "live": None}, {}
    for cid in ORDER:
        try:
            ok, detail = globals()[f"check_{cid}"](auth, prereg, ctx)
        except Exception as exc:                                              # fail closed
            ok, detail = False, f"check raised {type(exc).__name__}: {exc}"
        checks[cid] = {"pass": bool(ok), "detail": detail}
    failing = [c for c in ORDER if not checks[c]["pass"]]
    return {"schema": "rebaseguard.p5y.k5.cusum-first-real-probe.prelaunch-report.v2",
            "verdict": "LAUNCH_PERMITTED" if not failing else "REFUSED",
            "primary_reason": None if not failing else f"{failing[0]}: {checks[failing[0]]['detail']}",
            "failing_checks": failing, "checks": checks, "authorization_path": str(auth_path),
            "authorization_sha256": sha(auth_path.read_bytes()), "science_sha256": sha(SCIENCE.read_bytes()),
            "live_host_facts": ctx["live"], "authorization_commit_derived": ctx.get("authorization_commit"),
            "head": git("rev-parse", "HEAD").stdout.strip(), "read_only": True}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authorization", default=str(NS / "protocol/AUTHORIZATION_TEMPLATE_R2.json"))
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
