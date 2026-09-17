"""READ-ONLY prelaunch verifier of the first governed real CUSUM signed-R''' probe, r4. Fail closed.

    python3 -B code/prelaunch_verify.py [--authorization PATH] [--out report.json]

Never imports flint, never builds a certifier, never reads an operator, never writes (except --out); its only network
call is a read-only `git ls-remote origin` of the pinned ref. LAUNCH_PERMITTED (exit 0) only if every check passes;
otherwise REFUSED (exit 3) with the FIRST failing check in the frozen order as the primary reason. Every check runs;
an exception inside a check fails that check.

TRUST MODEL. Prevents accidental, unreviewed, self-attested, uncommitted, unpublished, symlinked or drifted launches.
Publication = reachable from the PINNED ref origin/p5y-postk1-frontier, whose value must equal `git ls-remote` of an
origin whose URL is in the frozen allow-list; the freeze commit's first parent is a literal constant. Review verdicts
are read from the review file (exactly one verdict line). The committed append-only ledger governs host files.
Residual (declared): a party with push rights to the allow-listed origins who publishes fabricated reviews and commits;
covered by the public history and independent adjudication before any adoption.

    P01 EXECUTION_AUTHORIZED is true
    P02 authorization content: exact fixed path (no symlink); every non-activation field equal to the committed r4
        template; no extra keys; activation fields filled; identity hashes recomputed
    P03 protocol freeze: r4 science file introduced once, unchanged, no symlink; its commit's first parent is the literal
        FREEZE_PARENT; template and binding introduced by the same commit and unchanged; FREEZE_RECORD_R4.json committed
        once strictly later names the commit and sha256; all published; packet code byte-equal to the freeze blobs
    P04 authorization temporal: authorization and amendment committed once (no symlink); strictly ordered
        freeze < amendment < authorization, all published; HEAD descends from the authorization commit;
        AUTHORIZATION_UTC not in the future, within the hour before the authorization commit, after the amendment commit
    P05 protected hashes: R1-R4 pins (R4 protocol), preregistration references, packet code sha256
    P06 executor binding: amendment strictly after the freeze, whitelisted keys, BOUND_QUALIFIED, same science sha256;
        executor entry, consumption adapter and frozen adapter pins among the sources; every pinned file committed,
        unmodified, no symlink, introduced no later than the amendment; the review file has exactly one REVIEW_VERDICT
        (PASS or PASS_WITH_SCOPE_LIMITATION) and exactly one REVIEWED_AMENDMENT_SOURCES_SHA256 naming these sources;
        the authorization names this amendment
    P07 host runtime identity equals the frozen contract (live facts)
    P08 no conflicting real producer process (exact argv element basenames over /proc; own ancestry excluded)
    P09 no sealed record: namespace root, packet tree, published evidence paths in git history, ledger seal events,
        ledger OUTCOME with a non-null sealed_record_sha256
    P10 CPU ceiling valid (soft < hard) and equal to the preregistration
    P11 slots: the committed append-only ledger governs; every namespace entry is a slot-N directory with exactly one
        LAUNCH_NOTICE and one OUTCOME; RUN_FAILED.json sha256 equals the OUTCOME's; arithmetic_started and the
        mechanically derived failure class agree with the OUTCOME; arithmetic attempts < max and each transient; the
        next slot is free and has exactly one published LAUNCH_NOTICE naming this authorization
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

SCIENCE = NS / "protocol/SCIENCE_PREREGISTRATION_R4.json"
TEMPLATE = NS / "protocol/AUTHORIZATION_TEMPLATE_R4.json"
BINDING = NS / "protocol/EXECUTION_BINDING_R4.json"
FREEZE_RECORD = NS / "protocol/FREEZE_RECORD_R4.json"
AMENDMENT = NS / "protocol/EXECUTION_BINDING_AMENDMENT.json"
AUTH_ACTIVE = NS / "protocol/AUTHORIZATION_ACTIVE.json"
LEDGER = NS / "ledger/ATTEMPT_LEDGER.jsonl"
PUBLISHED_EVIDENCE_PREFIX = str(NS.relative_to(REPO)) + "/evidence/"
R4_PROTOCOL = REPO / "level4/closure_proofs/p5y_k5_cusum_order3_r4_tightening/config/QUALIFICATION_PROTOCOL_R4.json"
REMOTE_BRANCH = "p5y-postk1-frontier"
REMOTE_REF = f"origin/{REMOTE_BRANCH}"
FREEZE_PARENT = "5da170dbf8f3a256e460d239db4644d39ca773bc"
ALLOWED_ORIGIN_URLS = ("https://github.com/flaggielover/ReBaseGuard.git", "/root/work/postk1.git")
CONFLICTING_ARGV_BASENAMES = ("first_real_probe_executor.py", "first_real_probe_supervisor.py", "cusum_order3.py",
                              "qualify5.py", "gs_entry.py")
ORDER = [f"P{i:02d}" for i in range(1, 13)]
ACTIVATION_FIELDS = ("EXECUTION_AUTHORIZED", "PROTOCOL_FREEZE_COMMIT", "AUTHORIZED_BY", "AUTHORIZATION_UTC")
AMENDMENT_KEYS = {"schema", "status", "science_preregistration_sha256", "executor_entry", "consumption_adapter_entry",
                  "executor_sources_sha256", "qualification_evidence_sha256", "independent_review",
                  "independent_review_sha256", "independent_review_verdict", "amendment_rule_ack"}
OUTCOME_KEYS = {"event", "slot", "arithmetic_started", "failure_class", "run_failed_sha256", "sealed_record_sha256"}
SEALED_NAMES = ("SCIENTIFIC_RECORD_SEALED.json", "VOID_RECORD_SEALED.json")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


def rel(p) -> str:
    d = os.path.realpath(os.path.dirname(os.path.abspath(p)))
    return os.path.relpath(os.path.join(d, os.path.basename(p)), os.path.realpath(REPO))


def no_symlink(path) -> bool:
    """The path itself is not a symlink and, if tracked, git stores a regular file. A symlinked directory inside the
    repository is caught by the git tracking checks (files under it are not tracked at that path)."""
    if os.path.islink(path):
        return False
    staged = git("ls-files", "-s", "--", rel(path)).stdout.split()
    return not staged or staged[0] in ("100644", "100755")


def same_location(a, b) -> bool:
    try:
        return (os.path.basename(a) == os.path.basename(b) and not os.path.islink(a)
                and os.path.samefile(os.path.dirname(os.path.abspath(a)), os.path.dirname(os.path.abspath(b))))
    except OSError:
        return False


def introduced_by(path) -> list:
    return git("log", "--diff-filter=A", "--format=%H", "--", rel(path)).stdout.split()


def touched_by(path) -> list:
    return git("log", "--format=%H", "--", rel(path)).stdout.split()


def is_ancestor(a, b) -> bool:
    return bool(a) and bool(b) and git("merge-base", "--is-ancestor", a, b).returncode == 0


def strictly_before(a, b) -> bool:
    return bool(a) and bool(b) and a != b and is_ancestor(a, b)


def committed_unmodified(path) -> bool:
    return (no_symlink(path) and git("ls-files", "--error-unmatch", rel(path)).returncode == 0
            and not git("status", "--porcelain", "--", rel(path)).stdout.strip())


def once_unchanged(path):
    intro = introduced_by(path)
    if len(intro) != 1 or touched_by(path) != intro or not committed_unmodified(path):
        return None
    return intro[0]


def commit_time(c: str) -> int:
    return int(git("show", "-s", "--format=%ct", c).stdout.strip())


def published_tip(ctx):
    """The pinned remote-tracking ref, accepted only if origin is allow-listed and ls-remote agrees with it."""
    if "published_tip" not in ctx:
        url = git("remote", "get-url", "origin").stdout.strip()
        local = git("rev-parse", "--verify", "-q", REMOTE_REF).stdout.strip()
        remote = git("ls-remote", "origin", f"refs/heads/{REMOTE_BRANCH}").stdout.split()
        ok = url in ctx["allowed_origin_urls"] and bool(local) and bool(remote) and remote[0] == local
        ctx["published_tip"] = local if ok else None
        ctx["publication_detail"] = {"origin_url": url, "local_ref": local or None, "ls_remote": remote[0] if remote else None}
    return ctx["published_tip"]


def published(commit, ctx) -> bool:
    tip = published_tip(ctx)
    return bool(tip) and is_ancestor(commit, tip)


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
    if not same_location(ctx["auth_path"], AUTH_ACTIVE) or not no_symlink(AUTH_ACTIVE):
        p.append("authorization is not the regular file at protocol/AUTHORIZATION_ACTIVE.json")
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
        p.append("protocol sha256 differs from the r4 science file")
    if prereg["producer_identity_sha256"] != sha(PR.canonical(prereg["producer_identity"])):
        p.append("producer identity sha256 does not recompute")
    if prereg["host_runtime_identity_sha256"] != sha(PR.canonical(prereg["host_runtime_contract"])):
        p.append("host runtime identity sha256 does not recompute")
    return not p, "; ".join(p) or "authorization content matches the template and the preregistration"


def check_P03(auth, prereg, ctx):
    fz = once_unchanged(SCIENCE)
    if fz is None:
        return False, "r4 science file not introduced exactly once, unchanged and regular"
    p = []
    ctx["freeze_commit"] = fz
    parents = git("show", "-s", "--format=%P", fz).stdout.split()
    if not parents or parents[0] != FREEZE_PARENT:
        p.append("freeze commit's first parent is not the literal FREEZE_PARENT")
    for label, path in (("template", TEMPLATE), ("binding", BINDING)):
        if once_unchanged(path) != fz:
            p.append(f"{label} not introduced by the freeze commit or changed since")
    if auth.get("PROTOCOL_FREEZE_COMMIT") != fz:
        p.append(f"PROTOCOL_FREEZE_COMMIT != introducing commit {fz[:12]}")
    if not published(fz, ctx):
        p.append(f"freeze commit not published on {REMOTE_REF} ({ctx.get('publication_detail')})")
    if not is_ancestor(fz, "HEAD"):
        p.append("HEAD does not descend from the freeze commit")
    fr_commit = once_unchanged(FREEZE_RECORD) if FREEZE_RECORD.exists() else None
    if fr_commit is None:
        p.append("FREEZE_RECORD_R4.json missing, uncommitted, changed or a symlink")
    else:
        fr = json.loads(FREEZE_RECORD.read_text())
        if fr.get("freeze_commit") != fz or fr.get("science_sha256") != sha(SCIENCE.read_bytes()):
            p.append("FREEZE_RECORD_R4.json does not name this freeze commit and science sha256")
        if not strictly_before(fz, fr_commit) or not published(fr_commit, ctx):
            p.append("freeze record not committed strictly after the freeze and published")
    for relpath in prereg["packet_code_sha256"]:
        blob = subprocess.run(["git", "-C", str(REPO), "show", f"{fz}:{relpath}"], capture_output=True)
        if blob.returncode != 0 or blob.stdout != (REPO / relpath).read_bytes() or not no_symlink(REPO / relpath):
            p.append(f"{relpath} differs from its blob at the freeze commit")
    if git("status", "--porcelain", "--untracked-files=no", "--", rel(NS)).stdout.strip():
        p.append("tracked packet files have uncommitted changes")
    return not p, "; ".join(p) or f"freeze commit {fz[:12]} verified and published"


def check_P04(auth, prereg, ctx):
    ac = once_unchanged(AUTH_ACTIVE) if AUTH_ACTIVE.exists() or AUTH_ACTIVE.is_symlink() else None
    if ac is None:
        return False, "AUTHORIZATION_ACTIVE.json not committed exactly once, unchanged and regular"
    am = once_unchanged(AMENDMENT) if AMENDMENT.exists() else None
    fz = ctx.get("freeze_commit") or once_unchanged(SCIENCE)
    p = []
    ctx["authorization_commit"] = ac
    if not (strictly_before(fz, am) and strictly_before(am, ac)):
        p.append("commits are not strictly ordered freeze < amendment < authorization")
    for label, c in (("freeze", fz), ("amendment", am), ("authorization", ac)):
        if not published(c, ctx):
            p.append(f"{label} commit not published on {REMOTE_REF}")
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
        key = head.strip()
        if sep and key.replace("_", "").isalnum() and key.isupper():
            out.setdefault(key, []).append(tail.strip())
    return out


def check_P06(auth, prereg, ctx):
    if not AMENDMENT.exists() and not AMENDMENT.is_symlink():
        status = json.loads(BINDING.read_text())["status"]
        return False, f"EXECUTOR_BINDING_PENDING: no EXECUTION_BINDING_AMENDMENT.json (binding status {status})"
    am_commit = once_unchanged(AMENDMENT)
    am = json.loads(AMENDMENT.read_text())
    fz = ctx.get("freeze_commit") or once_unchanged(SCIENCE)
    p = []
    if am_commit is None or not strictly_before(fz, am_commit):
        p.append("amendment not committed once, unchanged, regular and strictly after the freeze")
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
    if any(Path(r).name in SEALED_NAMES for r in list(srcs) + list(evidence)):
        p.append("qualification files may not use sealed-record names")
    pinned = dict(srcs)
    pinned.update(evidence)
    review = am.get("independent_review")
    if review:
        pinned[review] = am.get("independent_review_sha256")
    else:
        p.append("no independent review")
    for r, h in pinned.items():
        path = REPO / r
        if not path.exists() or not no_symlink(path) or sha(path.read_bytes()) != h:
            p.append(f"pinned file moved or not regular: {r}")
            continue
        intro = introduced_by(path)
        if not committed_unmodified(path) or not intro or not am_commit or not is_ancestor(intro[-1], am_commit):
            p.append(f"pinned file not committed before the amendment: {r}")
    if review and (REPO / review).exists():
        lines = review_lines(REPO / review)
        verdicts, named = lines.get("REVIEW_VERDICT", []), lines.get("REVIEWED_AMENDMENT_SOURCES_SHA256", [])
        if len(verdicts) != 1 or verdicts[0] not in ("PASS", "PASS_WITH_SCOPE_LIMITATION"):
            p.append(f"review file must carry exactly one accepted REVIEW_VERDICT line (found {verdicts})")
        elif am.get("independent_review_verdict") != verdicts[0]:
            p.append("amendment verdict differs from the review file")
        if len(named) != 1 or named[0] != sha(PR.canonical(srcs)):
            p.append("review file must carry exactly one REVIEWED_AMENDMENT_SOURCES_SHA256 naming these sources")
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


def _append_only(path) -> bool:
    prev = b""
    for c in reversed(touched_by(path)):
        blob = subprocess.run(["git", "-C", str(REPO), "show", f"{c}:{rel(path)}"], capture_output=True)
        if blob.returncode != 0 or not blob.stdout.startswith(prev):
            return False
        prev = blob.stdout
    return True


def ledger_entries() -> list:
    if not LEDGER.exists() and not LEDGER.is_symlink():
        return []
    if not committed_unmodified(LEDGER) or not _append_only(LEDGER):
        raise RuntimeError("attempt ledger is uncommitted, modified, a symlink or not append-only")
    return [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()]


def check_P09(auth, prereg, ctx):
    found = [str(p) for n in SEALED_NAMES for p in NS.rglob(n)]
    root = Path(prereg["output_namespace"])
    if root.exists():
        found += [str(p) for n in SEALED_NAMES for p in root.rglob(n)]
    hist = git("log", "--all", "--format=", "--name-only").stdout.split()
    found += sorted({h for h in hist if h.startswith(PUBLISHED_EVIDENCE_PREFIX) and Path(h).name in SEALED_NAMES})
    for e in ledger_entries():
        if e.get("event") in ("SCIENTIFIC_RECORD_SEALED", "VOID_RECORD_SEALED") or \
                (e.get("event") == "OUTCOME" and e.get("sealed_record_sha256") is not None):
            found.append(f"ledger:{e.get('event')}:{e.get('slot')}")
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
    slots_in_ledger = {e.get("slot") for e in ledger}
    started = 0
    for d in entries:
        if d.is_symlink() or not d.is_dir() or not d.name.startswith("slot-"):
            return False, f"unexpected entry in the namespace root: {d.name}"
    for n in range(1, len(entries) + 1):
        if not (root / PR.slot_dir(n)).is_dir():
            return False, "slot directories are not contiguous from slot-1"
    if any(s not in {d.name for d in entries} for s in slots_in_ledger if s != PR.slot_dir(len(entries) + 1)):
        return False, "the ledger names a slot absent from the namespace"
    for d in entries:
        notices = [e for e in ledger if e.get("slot") == d.name and e.get("event") == "LAUNCH_NOTICE"]
        outcomes = [e for e in ledger if e.get("slot") == d.name and e.get("event") == "OUTCOME"]
        if len(notices) != 1 or len(outcomes) != 1 or set(outcomes[0]) != OUTCOME_KEYS:
            return False, f"{d.name} lacks exactly one LAUNCH_NOTICE and one well-formed OUTCOME in the ledger"
        out = outcomes[0]
        failed = d / "RUN_FAILED.json"
        if failed.is_symlink() or not failed.exists() or sha(failed.read_bytes()) != out["run_failed_sha256"]:
            return False, f"{d.name}: RUN_FAILED.json missing or differs from the ledger OUTCOME"
        info = json.loads(failed.read_text())
        derived = PR.failure_class(info.get("supervisor_evidence") or {})
        if info.get("arithmetic_started") is not out["arithmetic_started"] or out["failure_class"] != derived:
            return False, f"{d.name}: host record and ledger OUTCOME disagree (derived class {derived})"
        if out["arithmetic_started"] is not False:
            started += 1
            if derived not in rp["transient_failure_classes_after_arithmetic"]:
                return False, f"{d.name} failed after arithmetic with non-transient class {derived}"
    if started >= rp["max_attempts"]:
        return False, "maximum arithmetic attempts reached"
    try:
        slot = PR.slot_dir(len(entries) + 1)
    except PR.RuleViolation as exc:
        return False, f"no launch slot left: {exc}"
    if (root / slot).exists() or (root / slot).is_symlink():
        return False, f"next slot {slot} already exists"
    notice = [e for e in ledger if e.get("slot") == slot and e.get("event") == "LAUNCH_NOTICE"]
    if len(notice) != 1 or any(e.get("slot") == slot and e.get("event") != "LAUNCH_NOTICE" for e in ledger):
        return False, f"next slot {slot} lacks exactly one committed LAUNCH_NOTICE (and nothing else) in the ledger"
    if notice[0].get("authorization_sha256") != sha(Path(ctx["auth_path"]).read_bytes()):
        return False, f"LAUNCH_NOTICE for {slot} names another authorization"
    last = git("log", "-1", "--format=%H", "--", rel(LEDGER)).stdout.strip()
    if not published(last, ctx):
        return False, "ledger commit carrying the LAUNCH_NOTICE is not published"
    return True, f"next slot {slot} ({started} arithmetic attempts so far), launch notice committed and published"


def check_P12(auth, prereg, ctx):
    try:
        t = datetime.fromisoformat(str(auth.get("AUTHORIZATION_UTC")).replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError):
        return False, "no valid AUTHORIZATION_UTC"
    root = Path(prereg["output_namespace"])
    old = [str(p) for p in (root.rglob("*") if root.exists() else []) if p.lstat().st_mtime < t]
    return not old, f"files predate authorization: {old[:5]}" if old else "nothing predates authorization"


def verify(auth_path, *, allowed_origin_urls=ALLOWED_ORIGIN_URLS) -> dict:
    prereg = json.loads(SCIENCE.read_text())
    auth = json.loads(Path(auth_path).read_text())
    if not isinstance(auth, dict):
        raise ValueError("authorization is not a JSON object")
    ctx = {"auth_path": auth_path, "live": None, "allowed_origin_urls": tuple(allowed_origin_urls)}
    checks = {}
    for cid in ORDER:
        try:
            ok, detail = globals()[f"check_{cid}"](auth, prereg, ctx)
        except Exception as exc:                                              # fail closed
            ok, detail = False, f"check raised {type(exc).__name__}: {exc}"
        checks[cid] = {"pass": ok is True, "detail": detail}
    failing = [c for c in ORDER if not checks[c]["pass"]]
    return {"schema": "rebaseguard.p5y.k5.cusum-first-real-probe.prelaunch-report.v4",
            "verdict": "LAUNCH_PERMITTED" if not failing and len(checks) == len(ORDER) else "REFUSED",
            "primary_reason": None if not failing else f"{failing[0]}: {checks[failing[0]]['detail']}",
            "failing_checks": failing, "checks": checks, "authorization_path": str(auth_path),
            "authorization_sha256": sha(Path(auth_path).read_bytes()), "science_sha256": sha(SCIENCE.read_bytes()),
            "remote_ref": REMOTE_REF, "published_tip": ctx.get("published_tip"),
            "publication_detail": ctx.get("publication_detail"),
            "freeze_commit_derived": ctx.get("freeze_commit"), "authorization_commit_derived": ctx.get("authorization_commit"),
            "live_host_facts": ctx["live"], "head": git("rev-parse", "HEAD").stdout.strip(), "read_only": True}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authorization", default=str(TEMPLATE))
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    try:
        rep = verify(Path(a.authorization))
    except Exception as exc:                                                   # fail closed, never permitted
        rep = {"verdict": "REFUSED", "primary_reason": f"verifier error {type(exc).__name__}: {exc}", "read_only": True}
    text = json.dumps(rep, indent=1, sort_keys=True, default=str)
    if a.out:
        Path(a.out).write_text(text + "\n")
    print(text)
    return 0 if rep["verdict"] == "LAUNCH_PERMITTED" else 3


if __name__ == "__main__":
    sys.exit(main())
