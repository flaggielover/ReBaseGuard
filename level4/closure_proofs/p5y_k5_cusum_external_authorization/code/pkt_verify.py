"""Read-only verification of the K5 CUSUM external-authorization packet against a clone of p5y-postk1-frontier.

    python -B pkt_verify.py REPO --stage amendment [--draft amendment_draft.json]
    python -B pkt_verify.py REPO --stage full [--draft ...] [--frozen-verify]

Never writes anything. It uses the UNMODIFIED frozen prelaunch_verify functions (check_P02..P06, check_P11,
ledger_entries, verify) and the frozen r5 supervisor.launch_state / slot_binding_problems (pure reads). The
countersignature rule of authorization_interface.countersignature_problems is mirrored here, because importing
executor_core would pull in the certificate stack. Every JSON object is parsed with duplicate-key rejection.
Prints one JSON report; exit 0 iff every check passed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("repo")
ap.add_argument("--stage", choices=("amendment", "full"), required=True)
ap.add_argument("--draft")
ap.add_argument("--frozen-verify", action="store_true", help="also run the complete frozen verify() (on the host)")
A = ap.parse_args()
REPO = Path(A.repo).resolve()
CP = "level4/closure_proofs/"
PROTO = CP + "p5y_k5_cusum_first_real_probe_protocol/"
EX = CP + "p5y_k5_cusum_real_point_executor/"
E6 = CP + "p5y_k5b_consumption_adapter/"
AUTH = PROTO + "protocol/AUTHORIZATION_ACTIVE.json"
AMEND = PROTO + "protocol/EXECUTION_BINDING_AMENDMENT.json"
LEDGER = PROTO + "ledger/ATTEMPT_LEDGER.jsonl"
CS = EX + "authorization/COUNTERSIGNATURE_ACTIVE.json"
REVIEW = CP + "p5y_k5_cusum_external_authorization/review/AMENDMENT_REVIEW.md"
FREEZE = "852b2d65c9332facd59771da7940ab429a7e2f2f"
SCIENCE_SHA = "9ace6896d70b7a17225c03cd6d8092e3d33089d001dd3e2736894dd866f3780a"
IDENTITY = "ef1c86e40bff0b13e40e924ba27d0841aff71f7344d114f71f517ab3adfdd41b"
ADAPTER = E6 + "code/consumption_adapter.py"
ADAPTER_SHA = "fbad7d33261fd47fc56c034d6a016f8427b81b51f9199f0e3a8f3e74df35973d"
GITHUB = "https://github.com/flaggielover/ReBaseGuard.git"
R = {}


def rec(name, ok, detail=""):
    R[name] = {"pass": bool(ok), "detail": detail}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fsha(rel: str) -> str:
    return sha((REPO / rel).read_bytes())


def git(*a) -> str:
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()


def anc(a, b) -> bool:
    return bool(a) and bool(b) and subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", a, b]).returncode == 0


def strict(a, b) -> bool:
    return bool(a) and bool(b) and a != b and anc(a, b)


def intro(rel):
    return git("log", "--diff-filter=A", "--format=%H", "--", rel).split()


def touched(rel):
    return git("log", "--format=%H", "--", rel).split()


def once(rel):
    i, t = intro(rel), touched(rel)
    return i[0] if len(i) == 1 and t == i else None


def nodup(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError(f"duplicate JSON keys {sorted({k for k in keys if keys.count(k) > 1})}")
    return dict(pairs)


def load(rel):
    return json.loads((REPO / rel).read_text(), object_pairs_hook=nodup)


def canonical(o) -> bytes:
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


# ------------------------------------------------------------------ frozen modules (unmodified, imported from the clone)
sys.path.insert(0, str(REPO / PROTO / "code"))
import prelaunch_verify as PV  # noqa: E402
import probe_rules as PR  # noqa: E402

rec("frozen_verifier_bytes", fsha(PROTO + "code/prelaunch_verify.py") == "54b198bc2d149f3a942a7f4b261f691afc935e3252d687797ef5d3282f02b53e"
    and Path(PV.__file__).resolve() == (REPO / PROTO / "code/prelaunch_verify.py").resolve(), PV.__file__)
rec("frozen_probe_rules_bytes", fsha(PROTO + "code/probe_rules.py") == "5ce87758f6caa773ce9fa0a77b65e5af0fff662b069c6ef62ac26accfb479fe6")

# ------------------------------------------------------------------ publication and freeze
head = git("rev-parse", "HEAD")
url = git("remote", "get-url", "origin")
local = git("rev-parse", "--verify", "-q", "origin/p5y-postk1-frontier")
remote = git("ls-remote", "origin", "refs/heads/p5y-postk1-frontier").split()
tip = remote[0] if remote else None
rec("publication_github", url == GITHUB and tip == local and anc(head, tip) and not git("status", "--porcelain"),
    {"origin": url, "head": head, "origin_ref": local, "ls_remote": tip})
fz = once(PROTO + "protocol/SCIENCE_PREREGISTRATION_R4.json")
rec("science_frozen", fz == FREEZE and fsha(PROTO + "protocol/SCIENCE_PREREGISTRATION_R4.json") == SCIENCE_SHA
    and git("show", "-s", "--format=%P", FREEZE).split()[0] == PV.FREEZE_PARENT, fz)
ok5, d5 = PV.check_P05({}, json.loads(PV.SCIENCE.read_text()), {})
rec("frozen_P05_protected_hashes", ok5, d5)
rec("guard_DENY", json.loads((REPO / EX / "config/REAL_INPUT_GUARD.json").read_text()).get("policy") == "DENY")
rec("executor_unchanged_since_r5_freeze",
    not git("diff", "--name-only", git("rev-parse", "a16d22b5"), "HEAD", "--", EX + "code", EX + "config"))
pins = json.loads((REPO / EX / "config/EXECUTOR_PINS.json").read_text())["files"]
rec("executor_pins_279", len(pins) == 279 and all(fsha(p) == h for p, h in pins.items()))
hist = set(git("log", "--all", "--format=", "--name-only").split())
sealed = sorted(p for p in hist if Path(p).name in PV.SEALED_NAMES)
rec("no_sealed_record_in_any_history", not sealed, sealed[:5])

# ------------------------------------------------------------------ amendment
am_raw = (REPO / AMEND).read_bytes()
am = load(AMEND)
am_sha = sha(am_raw)
am_commit = once(AMEND)
srcs = am.get("executor_sources_sha256") or {}
rec("amendment_once_after_freeze", am_commit is not None and strict(FREEZE, am_commit) and anc(am_commit, tip), am_commit)
rec("amendment_keys_allowed", set(am) <= PV.AMENDMENT_KEYS and set(am) == PV.AMENDMENT_KEYS, sorted(set(am) ^ PV.AMENDMENT_KEYS))
rec("amendment_status_science", am.get("status") == "BOUND_QUALIFIED" and am.get("science_preregistration_sha256") == SCIENCE_SHA)
idf = ["code/paths.py", "code/executor_core.py", "code/backends.py", "code/input_adapters.py",
       "code/authorization_interface.py", "code/lifecycle.py", "code/executor_cli.py", "code/supervisor.py",
       "code/qualification_gates.py", "code/consumer.py", "config/EXECUTOR_PINS.json"]
ident = sha(canonical({f: srcs.get(EX + f) for f in idf}))
rec("executor_identity_from_sources", ident == IDENTITY and all(srcs.get(EX + f) == fsha(EX + f) for f in idf), ident)
rec("entries", am.get("executor_entry") == EX + "code/executor_cli.py" and am.get("consumption_adapter_entry") == ADAPTER
    and ADAPTER in srcs and srcs[ADAPTER] == ADAPTER_SHA == fsha(ADAPTER))
rec("sources_exactly_14", len(srcs) == 14 and all(fsha(p) == h for p, h in srcs.items()), len(srcs))
src_canon = sha(PR.canonical(srcs))
rec("sources_canonical_sha", src_canon == sha(canonical(srcs)), src_canon)
lines = PV.review_lines(REPO / REVIEW) if (REPO / REVIEW).exists() else {}
rv, rh = lines.get("REVIEW_VERDICT", []), lines.get("REVIEWED_AMENDMENT_SOURCES_SHA256", [])
rec("review_file_binding", am.get("independent_review") == REVIEW and am.get("independent_review_sha256") == fsha(REVIEW)
    and len(rv) == 1 and rv[0] in ("PASS", "PASS_WITH_SCOPE_LIMITATION") and am.get("independent_review_verdict") == rv[0]
    and len(rh) == 1 and rh[0] == src_canon and intro(REVIEW) and anc(intro(REVIEW)[-1], am_commit)
    and touched(REVIEW) == intro(REVIEW), {"verdicts": rv, "hashes": rh, "review_intro": intro(REVIEW)})
if A.draft:
    d = json.loads(Path(A.draft).read_text(), object_pairs_hook=nodup)
    diff = sorted(k for k in set(d) | set(am) if d.get(k) != am.get(k))
    rec("amendment_equals_reviewed_draft", diff == ["independent_review_sha256", "independent_review_verdict"], diff)
# the frozen P06, unmodified, with an in-memory authorization that names this amendment (the only activation input)
ok6, d6 = PV.check_P06({"PRODUCER_R4_IDENTITY": {"executor_binding_sha256": am_sha}}, json.loads(PV.SCIENCE.read_text()), {})
rec("frozen_P06_amendment_integrity", ok6, d6)
R["_amendment"] = {"commit": am_commit, "sha256": am_sha, "sources_sha256": src_canon, "review_commit": (intro(REVIEW) or [None])[0]}

# ------------------------------------------------------------------ full packet
if A.stage == "full":
    auth_raw = (REPO / AUTH).read_bytes()
    auth = load(AUTH)
    auth_sha = sha(auth_raw)
    tmpl = load(PROTO + "protocol/AUTHORIZATION_TEMPLATE_R4.json")
    changed = sorted(k for k in set(tmpl) | set(auth) if tmpl.get(k) != auth.get(k))
    pri = {k: v for k, v in auth.get("PRODUCER_R4_IDENTITY", {}).items() if tmpl["PRODUCER_R4_IDENTITY"].get(k) != v}
    rec("authorization_only_activation_fields", set(changed) <= {"EXECUTION_AUTHORIZED", "PROTOCOL_FREEZE_COMMIT", "AUTHORIZED_BY",
        "AUTHORIZATION_UTC", "PRODUCER_R4_IDENTITY"} and list(pri) == ["executor_binding_sha256"] and set(auth) == set(tmpl),
        {"changed": changed, "producer_identity_changed": list(pri)})
    utc = datetime.fromisoformat(str(auth.get("AUTHORIZATION_UTC")).replace("Z", "+00:00"))
    rec("authorization_values", auth.get("EXECUTION_AUTHORIZED") is True and auth.get("PROTOCOL_FREEZE_COMMIT") == FREEZE
        and pri.get("executor_binding_sha256") == am_sha and utc.utcoffset() is not None and bool(auth.get("AUTHORIZED_BY")),
        {"AUTHORIZATION_UTC": auth.get("AUTHORIZATION_UTC"), "AUTHORIZED_BY": auth.get("AUTHORIZED_BY")})
    ctx = {"auth_path": PV.AUTH_ACTIVE, "live": None, "allowed_origin_urls": PV.ALLOWED_ORIGIN_URLS}
    prereg = json.loads(PV.SCIENCE.read_text())
    for cid in ("P01", "P02", "P03", "P04", "P06", "P09", "P10", "P11", "P12"):
        try:
            ok, det = getattr(PV, f"check_{cid}")(auth, prereg, ctx)
        except Exception as exc:
            ok, det = False, f"raised {type(exc).__name__}: {exc}"
        rec(f"frozen_{cid}", ok, det)
    ac = once(AUTH)
    rec("authorization_once_after_amendment", ac is not None and strict(am_commit, ac) and anc(ac, tip), ac)
    # countersignature (mirror of authorization_interface.countersignature_problems)
    c = load(CS)
    ctmpl = load(EX + "config/EXTERNAL_AUTHORIZATION_TEMPLATE.json")
    cc = once(CS)
    cs_ = c.get("countersigner") or {}
    slot = c.get("attempt_slot")
    rec("countersignature", set(c) == set(ctmpl) and c.get("schema") == ctmpl["schema"] and c.get("status") == "COUNTERSIGNED"
        and c.get("EXECUTION_AUTHORIZED") is True and c.get("result_blind") == ctmpl["result_blind"]
        and all(c.get(k) == ctmpl[k] for k in ("role", "activation_rule", "trust_model"))
        and c.get("protocol_authorization_sha256") == auth_sha and c.get("execution_binding_amendment_sha256") == am_sha
        and type(slot) is int and slot == 1 and PR.slot_dir(slot) == "slot-1"
        and re.match(r"^[0-9a-f]{32,}$", str(c.get("nonce"))) is not None
        and bool(cs_.get("identity")) and cs_.get("independent_of_execution_host") is True
        and type(cs_.get("utc")) in (int, float) and cs_["utc"] <= time.time() and set(cs_) == set(ctmpl["countersigner"])
        and cc is not None and strict(ac, cc) and anc(cc, tip),
        {"commit": cc, "attempt_slot": slot, "nonce_len": len(str(c.get("nonce"))), "utc": cs_.get("utc"),
         "identity": cs_.get("identity")})
    # ledger / LAUNCH_NOTICE
    raw_lines = [l for l in (REPO / LEDGER).read_text().splitlines() if l.strip()]
    entries = [json.loads(l, object_pairs_hook=nodup) for l in raw_lines]
    lc = git("log", "-1", "--format=%H", "--", LEDGER)
    n = entries[0] if len(entries) == 1 else {}
    nutc = datetime.fromisoformat(str(n.get("utc"))) if isinstance(n.get("utc"), str) else None
    rec("launch_notice", len(entries) == 1 and set(n) == {"event", "slot", "authorization_sha256", "utc"}
        and n.get("event") == "LAUNCH_NOTICE" and n.get("slot") == "slot-1" and n.get("authorization_sha256") == auth_sha
        and nutc is not None and nutc.utcoffset() is not None and nutc.timestamp() >= utc.timestamp()
        and not any(e.get("event") == "OUTCOME" for e in entries) and PV.ledger_entries() == entries
        and once(LEDGER) == lc and strict(cc, lc) and anc(lc, tip), {"commit": lc, "entries": len(entries), "notice": n})
    # r5 slot binding (frozen, pure read; nothing is created)
    sys.path.insert(0, str(REPO / EX / "code"))
    import supervisor as SV  # noqa: E402
    ns = Path(prereg["output_namespace"])
    state, problems = SV.launch_state(ns / "slot-1")
    _, wrong = SV.launch_state(ns / "slot-2")
    rec("r5_canonical_slot_binding", not problems and state.get("canonical_slot") == "slot-1" and bool(wrong)
        and not ns.exists(), {"problems": problems, "slot-2_refusals": wrong[:2], "namespace_exists": ns.exists()})
    R["_packet"] = {"authorization_commit": ac, "authorization_sha256": auth_sha, "countersignature_commit": cc,
                    "countersignature_sha256": fsha(CS), "ledger_commit": lc}
    if A.frozen_verify:
        rep = PV.verify(PV.AUTH_ACTIVE)
        rec("FROZEN_PRELAUNCH_VERIFY", rep["verdict"] == "LAUNCH_PERMITTED",
            {"verdict": rep["verdict"], "failing": rep["failing_checks"], "primary": rep["primary_reason"],
             "details": {k: v["detail"] for k, v in rep["checks"].items()}, "published_tip": rep["published_tip"],
             "head": rep["head"], "authorization_sha256": rep["authorization_sha256"],
             "freeze": rep["freeze_commit_derived"], "authorization_commit": rep["authorization_commit_derived"]})

out = {"checks": R, "all_pass": all(v["pass"] for k, v in R.items() if not k.startswith("_")),
       "failing": [k for k, v in R.items() if not k.startswith("_") and not v["pass"]], "stage": A.stage,
       "repo_head": head, "utc": datetime.now().astimezone().isoformat()}
print(json.dumps(out, indent=1, sort_keys=True, default=str))
sys.exit(0 if out["all_pass"] else 1)
