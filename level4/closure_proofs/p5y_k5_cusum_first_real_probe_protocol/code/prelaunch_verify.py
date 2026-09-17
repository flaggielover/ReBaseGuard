"""READ-ONLY prelaunch verifier of the first governed real CUSUM signed-R''' probe, r3. Fail closed.

    python3 -B code/prelaunch_verify.py [--authorization PATH] [--out report.json] [--remote-ref origin/p5y-postk1-frontier]

Never imports flint, never builds a certifier, never reads an operator, never fetches or writes (except --out).
LAUNCH_PERMITTED (exit 0) only if every check passes; otherwise REFUSED (exit 3) with the FIRST failing check in the
frozen order as the primary reason. Every check runs; an exception inside a check fails that check.

TRUST MODEL. The verifier prevents accidental, unreviewed, self-attested, uncommitted or unpublished launches. It anchors
on the PUBLISHED remote-tracking ref (the operator fetches first) and reads review verdicts from the review files
themselves. It cannot stop a party with push rights who publishes fabricated reviews; that residual is covered by the
public append-only history and by independent adjudication before any adoption (preregistration).

    P01 EXECUTION_AUTHORIZED is true
    P02 authorization content: fixed path; every non-activation field equal to the committed r3 template; activation
        fields filled; protocol / producer / host identity hashes recomputed from the preregistration
    P03 protocol freeze: the r3 science file introduced by exactly one commit and unchanged; that commit is on the remote
        ref and HEAD descends from it; FREEZE_RECORD_R3.json (committed strictly after the freeze, on the remote ref)
        names exactly that commit and sha256; pinned packet code byte-equal to its blobs at the freeze commit
    P04 authorization temporal: authorization committed once at its fixed path; commits strictly ordered
        freeze < amendment < authorization, all on the remote ref; HEAD descends from the authorization commit;
        AUTHORIZATION_UTC not in the future, within the hour before the authorization commit, after the amendment commit
    P05 protected hashes: R1-R4 pins (R4 protocol), preregistration references, packet code sha256
    P06 executor binding: amendment committed once strictly after the freeze, whitelisted keys, BOUND_QUALIFIED, same
        science sha256; executor entry and consumption adapter among the pinned sources; frozen adapter pins
        (k5_minimality.py, k5b_check.py) present with their frozen sha256; every pinned source / evidence / review file
        committed, unmodified and introduced no later than the amendment commit; the REVIEW FILE's own REVIEW_VERDICT
        line is PASS or PASS_WITH_SCOPE_LIMITATION and its REVIEWED_AMENDMENT_SOURCES_SHA256 line names these sources;
        the authorization names this amendment
    P07 host runtime identity equals the frozen contract (live facts)
    P08 no conflicting real producer process (exact argv element basenames over /proc; own ancestry excluded)
    P09 no sealed record (scientific or VOID): namespace root, packet tree, all git history, committed attempt ledger
    P10 CPU ceiling valid (soft < hard) and equal to the preregistration
    P11 slots and attempts: every namespace entry is a slot-N directory with a committed LAUNCH_NOTICE and a single
        committed OUTCOME whose failure class equals the class derived mechanically from the supervisor wait status;
        arithmetic attempts < max_attempts and each ended transient; the next slot is free and has exactly one committed,
        published LAUNCH_NOTICE naming this authorization
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
import time
from datetime import datetime
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
sys.path.insert(0, str(NS / "code"))

import probe_rules as PR  # noqa: E402

SCIENCE = NS / "protocol/SCIENCE_PREREGISTRATION_R3.json"
TEMPLATE = NS / "protocol/AUTHORIZATION_TEMPLATE_R3.json"
BINDING = NS / "protocol/EXECUTION_BINDING_R3.json"
FREEZE_RECORD = NS / "protocol/FREEZE_RECORD_R3.json"
AMENDMENT = NS / "protocol/EXECUTION_BINDING_AMENDMENT.json"
AUTH_ACTIVE = NS / "protocol/AUTHORIZATION_ACTIVE.json"
LEDGER = NS / "ledger/ATTEMPT_LEDGER.jsonl"
R4_PROTOCOL = REPO / "level4/closure_proofs/p5y_k5_cusum_order3_r4_tightening/config/QUALIFICATION_PROTOCOL_R4.json"
CONFLICTING_ARGV_BASENAMES = ("first_real_probe_executor.py", "first_real_probe_supervisor.py", "cusum_order3.py",
                              "qualify5.py", "gs_entry.py")
ORDER = [f"P{i:02d}" for i in range(1, 13)]
ACTIVATION_FIELDS = ("EXECUTION_AUTHORIZED", "PROTOCOL_FREEZE_COMMIT", "AUTHORIZED_BY", "AUTHORIZATION_UTC")
AMENDMENT_KEYS = {"schema", "status", "science_preregistration_sha256", "executor_entry", "consumption_adapter_entry",
                  "executor_sources_sha256", "qualification_evidence_sha256", "independent_review",
                  "independent_review_sha256", "independent_review_verdict", "amendment_rule_ack"}
SEALED_NAMES = ("SCIENTIFIC_RECORD_SEALED.json", "VOID_RECORD_SEALED.json")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


def rel(p) -> str:
    return str(Path(p).resolve().relative_to(REPO.resolve()))


def introduced_by(path) -> list[str]:
    return git("log", "--diff-filter=A", "--format=%H", "--", rel(path)).stdout.split()


def touched_by(path) -> list[str]:
    return git("log", "--format=%H", "--", rel(path)).stdout.split()


def is_ancestor(a, b) -> bool:
    return bool(a) and bool(b) and git("merge-base", "--is-ancestor", a, b).returncode == 0


def strictly_before(a, b) -> bool:
    return bool(a) and bool(b) and a != b and is_ancestor(a, b)


def committed_unmodified(path) -> bool:
    return (git("ls-files", "--error-unmatch", rel(path)).returncode == 0
            and not git("status", "--porcelain", "--", rel(path)).stdout.strip())


def once_unchanged(path):
    intro = introduced_by(path)
    if len(intro) != 1 or touched_by(path) != intro or not committed_unmodified(path):
        return None
    return intro[0]


def commit_time(c: str) -> int:
    return int(git("show", "-s", "--format=%ct", c).stdout.strip())


def _get(d, dotted: str):
    for k in dotted.split("."):
        d = d.get(k) if isinstance(d, dict) else None
    return d


# ------------------------------------------------------------------ checks
def check_P01(auth, prereg, ctx):
    ok = auth.get("EXECUTION_AUTHORIZED") is True
    return ok, "authorized" if ok else "EXECUTION_NOT_AUTHORIZED: EXECUTION_AUTHORIZED is not true"


def check_P02(auth, prereg, ctx):
    p = []
    if Path(ctx["auth_path"]).resolve() != AUTH_ACTIVE.resolve():
        p.append("authorization is not at the fixed path protocol/AUTHORIZATION_ACTIVE.json")
    template = json.loads(TEMPLATE.read_text())
    for key, value in template.items():
        if key in ACTIVATION_FIELDS:
            continue
        if key == "PRODUCER_R4_IDENTITY":
            if _get(auth, "PRODUCER_R4_IDENTITY.producer_identity_sha256") != value["producer_identity_sha256"] \
                    or set((auth.get(key) or {})) != set(value):
                p.append("PRODUCER_R4_IDENTITY differs from the template")
            continue
        if auth.get(key) != value:
            p.append(f"{key} differs from the committed template")
    extra = set(auth) - set(template)
    if extra:
        p.append(f"authorization carries keys absent from the template: {sorted(extra)}")
    for key in ("PROTOCOL_FREEZE_COMMIT", "AUTHORIZED_BY", "AUTHORIZATION_UTC"):
        v = auth.get(key)
        if not isinstance(v, str) or not v.strip() or v.startswith("SET_AT_ACTIVATION"):
            p.append(f"activation field {key} not filled")
    eb = _get(auth, "PRODUCER_R4_IDENTITY.executor_binding_sha256")
    if not isinstance(eb, str) or eb.startswith("SET_AT_ACTIVATION"):
        p.append("activation field executor_binding_sha256 not filled")
    if auth.get("PROTOCOL_SHA256") != sha(SCIENCE.read_bytes()):
        p.append("protocol sha256 differs from the r3 science file")
    if prereg["producer_identity_sha256"] != sha(PR.canonical(prereg["producer_identity"])):
        p.append("producer identity sha256 does not recompute")
    if prereg["host_runtime_identity_sha256"] != sha(PR.canonical(prereg["host_runtime_contract"])):
        p.append("host runtime identity sha256 does not recompute")
    return not p, "; ".join(p) or "authorization content matches the template and the preregistration"


def check_P03(auth, prereg, ctx):
    remote = ctx["remote_ref"]
    fz = once_unchanged(SCIENCE)
    if fz is None:
        return False, "r3 science file not introduced exactly once and unchanged"
    p = []
    ctx["freeze_commit"] = fz
    if auth.get("PROTOCOL_FREEZE_COMMIT") != fz:
        p.append(f"PROTOCOL_FREEZE_COMMIT != introducing commit {fz[:12]}")
    if not is_ancestor(fz, remote):
        p.append(f"freeze commit not on {remote}")
    if not is_ancestor(fz, "HEAD"):
        p.append("HEAD does not descend from the freeze commit")
    fr_commit = once_unchanged(FREEZE_RECORD) if FREEZE_RECORD.exists() else None
    if fr_commit is None:
        p.append("FREEZE_RECORD_R3.json missing, uncommitted or changed")
    else:
        fr = json.loads(FREEZE_RECORD.read_text())
        if fr.get("freeze_commit") != fz or fr.get("science_sha256") != sha(SCIENCE.read_bytes()):
            p.append("FREEZE_RECORD_R3.json does not name this freeze commit and science sha256")
        if not strictly_before(fz, fr_commit) or not is_ancestor(fr_commit, remote):
            p.append("freeze record not committed strictly after the freeze on the remote ref")
    for relpath in prereg["packet_code_sha256"]:
        blob = subprocess.run(["git", "-C", str(REPO), "show", f"{fz}:{relpath}"], capture_output=True)
        if blob.returncode != 0 or blob.stdout != (REPO / relpath).read_bytes():
            p.append(f"{relpath} differs from its blob at the freeze commit")
    if git("status", "--porcelain", "--untracked-files=no", "--", rel(NS)).stdout.strip():
        p.append("tracked packet files have uncommitted changes")
    return not p, "; ".join(p) or f"freeze commit {fz[:12]} verified on {remote}"


def check_P04(auth, prereg, ctx):
    remote = ctx["remote_ref"]
    ac = once_unchanged(AUTH_ACTIVE) if AUTH_ACTIVE.exists() else None
    if ac is None:
        return False, "AUTHORIZATION_ACTIVE.json not committed exactly once and unchanged"
    am = once_unchanged(AMENDMENT) if AMENDMENT.exists() else None
    fz = ctx.get("freeze_commit") or once_unchanged(SCIENCE)
    p = []
    ctx["authorization_commit"] = ac
    if not (strictly_before(fz, am) and strictly_before(am, ac)):
        p.append("commits are not strictly ordered freeze < amendment < authorization")
    for label, c in (("freeze", fz), ("amendment", am), ("authorization", ac)):
        if not is_ancestor(c, remote):
            p.append(f"{label} commit not on {remote}")
    if not is_ancestor(ac, "HEAD"):
        p.append("HEAD does not descend from the authorization commit")
    try:
        t = datetime.fromisoformat(str(auth.get("AUTHORIZATION_UTC")).replace("Z", "+00:00")).timestamp()
        if t > time.time() + 300:
            p.append("AUTHORIZATION_UTC is in the future")
        if not (commit_time(ac) - 3600 <= t <= commit_time(ac) + 60):
            p.append("AUTHORIZATION_UTC is not within the hour before the authorization commit")
        if am and t < commit_time(am):
            p.append("AUTHORIZATION_UTC predates the amendment commit")
    except (ValueError, TypeError):
        p.append("AUTHORIZATION_UTC unparseable")
    return not p, "; ".join(p) or f"authorization commit {ac[:12]} ordered and published"


def check_P05(auth, prereg, ctx):
    moved = []
    r4 = json.loads(R4_PROTOCOL.read_text())
    for key in ("r1_bound_sha256", "r2_bound_sha256", "r3_bound_sha256", "bound_code_sha256", "bound_config_sha256"):
        moved += [r for r, h in r4[key].items() if not (REPO / r).exists() or sha((REPO / r).read_bytes()) != h]
    for table in ("references_sha256", "packet_code_sha256"):
        moved += [r for r, h in prereg[table].items() if not (REPO / r).exists() or sha((REPO / r).read_bytes()) != h]
    return not moved, f"moved: {moved[:8]}" if moved else "all protected hashes match"


def review_lines(path) -> dict:
    out = {}
    for line in Path(path).read_text().splitlines():
        head, sep, tail = line.partition(":")
        if sep and head.strip().replace("_", "").isalnum() and head.strip().isupper():
            out.setdefault(head.strip(), tail.strip())
    return out


def check_P06(auth, prereg, ctx):
    if not AMENDMENT.exists():
        status = json.loads(BINDING.read_text())["status"]
        return False, f"EXECUTOR_BINDING_PENDING: no EXECUTION_BINDING_AMENDMENT.json (binding status {status})"
    am_commit = once_unchanged(AMENDMENT)
    am = json.loads(AMENDMENT.read_text())
    fz = ctx.get("freeze_commit") or once_unchanged(SCIENCE)
    p = []
    if am_commit is None or not strictly_before(fz, am_commit):
        p.append("amendment not committed once, unchanged and strictly after the freeze")
    if set(am) - AMENDMENT_KEYS:
        p.append(f"non-whitelisted amendment keys {sorted(set(am) - AMENDMENT_KEYS)}")
    if am.get("status") != "BOUND_QUALIFIED":
        p.append(f"amendment status {am.get('status')}")
    if am.get("science_preregistration_sha256") != sha(SCIENCE.read_bytes()):
        p.append("amendment names another science file")
    srcs = am.get("executor_sources_sha256") or {}
    for key in ("executor_entry", "consumption_adapter_entry"):
        if am.get(key) not in srcs:
            p.append(f"{key} is not among the pinned sources")
    for name, h in prereg["k5b_consumption_adapter"]["pins"].items():
        if not any(Path(r).name == name and v == h for r, v in srcs.items()):
            p.append(f"frozen adapter pin {name} missing from the sources")
    evidence = am.get("qualification_evidence_sha256") or {}
    if not evidence:
        p.append("no qualification evidence pinned")
    pinned = dict(srcs)
    pinned.update(evidence)
    review = am.get("independent_review")
    if review:
        pinned[review] = am.get("independent_review_sha256")
    else:
        p.append("no independent review")
    for r, h in pinned.items():
        path = REPO / r
        if not path.exists() or sha(path.read_bytes()) != h:
            p.append(f"pinned file moved: {r}")
            continue
        intro = introduced_by(path)
        if not committed_unmodified(path) or not intro or not am_commit or not is_ancestor(intro[-1], am_commit):
            p.append(f"pinned file not committed before the amendment: {r}")
    if review and (REPO / review).exists():
        lines = review_lines(REPO / review)
        verdict = lines.get("REVIEW_VERDICT")
        if verdict not in ("PASS", "PASS_WITH_SCOPE_LIMITATION"):
            p.append(f"review file verdict is {verdict}")
        if am.get("independent_review_verdict") != verdict:
            p.append("amendment verdict differs from the review file")
        if lines.get("REVIEWED_AMENDMENT_SOURCES_SHA256") != sha(PR.canonical(srcs)):
            p.append("review file does not name these executor sources")
    if _get(auth, "PRODUCER_R4_IDENTITY.executor_binding_sha256") != sha(AMENDMENT.read_bytes()):
        p.append("authorization names another executor binding")
    return not p, "; ".join(p) or "executor bound, qualified and independently reviewed"


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


def _own_ancestry() -> set:
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


def ledger_entries() -> list:
    if not LEDGER.exists():
        return []
    if not committed_unmodified(LEDGER) or not _append_only(LEDGER):
        raise RuntimeError("attempt ledger is uncommitted, modified or not append-only")
    return [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()]


def _append_only(path) -> bool:
    """Every committed version of the ledger is a prefix of the next one (no rewrite, no deletion of lines)."""
    commits = list(reversed(touched_by(path)))
    prev = b""
    for c in commits:
        blob = subprocess.run(["git", "-C", str(REPO), "show", f"{c}:{rel(path)}"], capture_output=True)
        if blob.returncode != 0 or not blob.stdout.startswith(prev):
            return False
        prev = blob.stdout
    return True


def check_P09(auth, prereg, ctx):
    found = [str(p) for n in SEALED_NAMES for p in NS.rglob(n)]
    root = Path(prereg["output_namespace"])
    if root.exists():
        found += [str(p) for n in SEALED_NAMES for p in root.rglob(n)]
    hist = git("log", "--all", "--format=", "--name-only").stdout.split()
    found += sorted({h for h in hist if Path(h).name in SEALED_NAMES})
    found += [f"ledger:{e.get('event')}:{e.get('slot')}" for e in ledger_entries()
              if e.get("event") in ("SCIENTIFIC_RECORD_SEALED", "VOID_RECORD_SEALED")]
    return not found, f"sealed records exist: {found[:5]}" if found else "no sealed record for this protocol"


def check_P10(auth, prereg, ctx):
    c = auth.get("CPU_CEILING") or {}
    try:
        ok = (c == prereg["cpu_ceiling"] and 0 < c["per_attempt_cpu_seconds_soft"] < c["per_attempt_cpu_seconds_rlimit"]
              and c["per_attempt_cpu_seconds_rlimit"] * c["max_attempts"] <= c["campaign_cpu_seconds_hard"]
              and c["per_attempt_cpu_seconds_soft"] >= 2 * prereg["cost_model"]["estimate_per_attempt_cpu_seconds"])
    except (KeyError, TypeError):
        ok = False
    return ok, "CPU ceiling valid" if ok else "CPU ceiling invalid or differs"


def check_P11(auth, prereg, ctx):
    rp = prereg["retry_policy"]
    root = Path(prereg["output_namespace"])
    entries = sorted(root.iterdir()) if root.exists() else []
    ledger = ledger_entries()
    started = 0
    for d in entries:
        if not d.is_dir() or not d.name.startswith("slot-"):
            return False, f"unexpected entry in the namespace root: {d.name}"
        notices = [e for e in ledger if e.get("slot") == d.name and e.get("event") == "LAUNCH_NOTICE"]
        outcomes = [e for e in ledger if e.get("slot") == d.name and e.get("event") == "OUTCOME"]
        if len(notices) != 1 or len(outcomes) != 1:
            return False, f"{d.name} lacks exactly one committed LAUNCH_NOTICE and one OUTCOME in the ledger"
        failed = d / "RUN_FAILED.json"
        if not failed.exists():
            return False, f"{d.name} has no supervisor RUN_FAILED.json"
        info = json.loads(failed.read_text())
        derived = PR.failure_class(info.get("supervisor_evidence") or {})
        if outcomes[0].get("failure_class") != derived:
            return False, f"{d.name}: ledger failure class differs from the derived class {derived}"
        if info.get("arithmetic_started") is not False:
            started += 1
            if derived not in rp["transient_failure_classes_after_arithmetic"]:
                return False, f"{d.name} failed after arithmetic with non-transient class {derived}"
    if started >= rp["max_attempts"]:
        return False, "maximum arithmetic attempts reached"
    try:
        slot = PR.slot_dir(len(entries) + 1)
    except PR.RuleViolation as exc:
        return False, f"no launch slot left: {exc}"
    if (root / slot).exists():
        return False, f"next slot {slot} already exists"
    notice = [e for e in ledger if e.get("slot") == slot and e.get("event") == "LAUNCH_NOTICE"]
    if len(notice) != 1 or any(e.get("slot") == slot and e.get("event") != "LAUNCH_NOTICE" for e in ledger):
        return False, f"next slot {slot} lacks exactly one committed LAUNCH_NOTICE (and nothing else) in the ledger"
    if notice[0].get("authorization_sha256") != sha(Path(ctx["auth_path"]).read_bytes()):
        return False, f"LAUNCH_NOTICE for {slot} names another authorization"
    lc = introduced_by(LEDGER)
    last = git("log", "-1", "--format=%H", "--", rel(LEDGER)).stdout.strip()
    if not lc or not is_ancestor(last, ctx["remote_ref"]):
        return False, "ledger commit carrying the LAUNCH_NOTICE is not on the remote ref"
    return True, f"next slot {slot} ({started} arithmetic attempts so far), launch notice committed and published"


def check_P12(auth, prereg, ctx):
    try:
        t = datetime.fromisoformat(str(auth.get("AUTHORIZATION_UTC")).replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError):
        return False, "no valid AUTHORIZATION_UTC"
    root = Path(prereg["output_namespace"])
    old = [str(p) for p in (root.rglob("*") if root.exists() else []) if p.stat().st_mtime < t]
    return not old, f"files predate authorization: {old[:5]}" if old else "nothing predates authorization"


def verify(auth_path, remote_ref: str = "origin/p5y-postk1-frontier") -> dict:
    prereg = json.loads(SCIENCE.read_text())
    auth = json.loads(Path(auth_path).read_text())
    if not isinstance(auth, dict):
        raise ValueError("authorization is not a JSON object")
    ctx, checks = {"auth_path": auth_path, "live": None, "remote_ref": remote_ref}, {}
    for cid in ORDER:
        try:
            ok, detail = globals()[f"check_{cid}"](auth, prereg, ctx)
        except Exception as exc:                                              # fail closed
            ok, detail = False, f"check raised {type(exc).__name__}: {exc}"
        checks[cid] = {"pass": ok is True, "detail": detail}
    failing = [c for c in ORDER if not checks[c]["pass"]]
    return {"schema": "rebaseguard.p5y.k5.cusum-first-real-probe.prelaunch-report.v3",
            "verdict": "LAUNCH_PERMITTED" if not failing and len(checks) == len(ORDER) else "REFUSED",
            "primary_reason": None if not failing else f"{failing[0]}: {checks[failing[0]]['detail']}",
            "failing_checks": failing, "checks": checks, "authorization_path": str(auth_path),
            "authorization_sha256": sha(Path(auth_path).read_bytes()), "science_sha256": sha(SCIENCE.read_bytes()),
            "remote_ref": remote_ref, "remote_ref_commit": git("rev-parse", "--verify", "-q", remote_ref).stdout.strip() or None,
            "freeze_commit_derived": ctx.get("freeze_commit"), "authorization_commit_derived": ctx.get("authorization_commit"),
            "live_host_facts": ctx["live"], "head": git("rev-parse", "HEAD").stdout.strip(), "read_only": True}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authorization", default=str(TEMPLATE))
    ap.add_argument("--remote-ref", default="origin/p5y-postk1-frontier")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    try:
        rep = verify(Path(a.authorization), a.remote_ref)
    except Exception as exc:                                                   # fail closed, never permitted
        rep = {"verdict": "REFUSED", "primary_reason": f"verifier error {type(exc).__name__}: {exc}", "read_only": True}
    text = json.dumps(rep, indent=1, sort_keys=True, default=str)
    if a.out:
        Path(a.out).write_text(text + "\n")
    print(text)
    return 0 if rep["verdict"] == "LAUNCH_PERMITTED" else 3


if __name__ == "__main__":
    sys.exit(main())
