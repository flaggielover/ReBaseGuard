"""Read-only self-audit before every major transition (owner instruction 2026-09-29, overnight run, section 10).

  python3 code/self_audit.py LABEL      -> evidence/self_audit/SELF_AUDIT_<LABEL>.json; exit 0 iff every check passes

Checks (each mechanical; nothing is evaluated, nothing is modified except the audit output file):
  A1 every ZERO_TARGET_LEDGER line has new_target_evaluations = target_equivalent_proxies =
     target_informed_optimisation = 0 and no quarantined cell touched
  A2 every ledgered drift is outside the band [6/5, 13/5] and its mirror (|e| < 6/5 or |e| > 13/5)
  A3 the quarantine config and the incident files are byte-identical to their first committed versions
  A4 the static quarantine scan passes (planted control fires)
  A5 producer files byte-identical to the lock commit, fingerprint == the lock fingerprint, and every rerun evidence
     file (srk_decoys/, srk_decoys_cell/) carries that fingerprint and git_head_at_start == the lock commit
  A6 r5 blob unchanged (f978eeb6...), no coverage map r6 anywhere in the tree
  A7 every path changed on this branch since the campaign base lies inside the research namespace (so no historical
     verdict, no cell-308 file, no r5 and no K5/P5Y status file changed)
  A8 no non-ordinary ref exists (no exactly-once marker, no p5y-* / c1* ref); local branches are only main and BRANCH
  A9 the independent verifier imports no producer module and no C1b module
  A10 (informational) local HEAD vs remote branch tip; working-tree dirt
"""
from __future__ import annotations

import datetime
import hashlib
import json
import re
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[4]
BRANCH = "claude/rebaseguard-k5-cell-309-w0jv8m"
BASE = "b73b9449fb13e7134455d8f5819c1f9d5290bb0b"
NS_PREFIX = "level4/closure_proofs/p5y_k5_cell309_research_r1/"
LOCK_COMMIT = "2a03e838498ab8a8c1c61b9a142ba45adb941592"
LOCK_FP = "377057bef1d1f21be4db38488235596c0e4134bb75ffdced08e667e6c48cc8db"
PRODUCER = ["impl/srk_kernel.py", "impl/srk_float.py", "impl/srk_envelope.py", "impl/srk_certify.py"]
R5_PATH = "level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
R5_BLOB = "f978eeb6b41188eabaf3c6d590c9178d711f1ce6"
BAND = (F(6, 5), F(13, 5))   # q309: literal-ok (the quarantine band definition, used only to REFUSE)
IMMUTABLE = ["config/TARGET_QUARANTINE_309.json", "ledger/INCIDENT_309R1_01_TPT_SHARES.md",
             "ledger/INCIDENT_309R1_02_INBAND_MENTAL_ESTIMATE.md"]


def git(*a) -> str:
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()


def in_band(x: F) -> bool:
    return BAND[0] <= abs(x) <= BAND[1]


def run(label: str) -> tuple:
    res, detail = {}, {}
    rows = [json.loads(l) for l in (NS / "ledger" / "ZERO_TARGET_LEDGER.jsonl").read_text().splitlines() if l.strip()]
    res["A1_target_counters_zero"] = all(r.get("new_target_evaluations", 0) == 0 and
                                         r.get("target_equivalent_proxies", 0) == 0 and
                                         r.get("target_informed_optimisation", 0) == 0 and
                                         not r.get("cells_touched") for r in rows)
    drifts = [F(x) for r in rows for d in r.get("drifts", []) for x in d]
    hits = [str(x) for x in drifts if in_band(x)]
    # an interval straddling the band would also be caught by the runtime guard; check intervals too
    for r in rows:
        for d in r.get("drifts", []):
            if len(d) == 2:
                lo, hi = F(d[0]), F(d[1])
                if not (hi < BAND[0] or lo > BAND[1]) or not (hi < -BAND[1] or lo > -BAND[0]):
                    hits.append(f"[{d[0]},{d[1]}]")
    res["A2_no_band_drift"] = not hits
    detail["ledger_lines"] = len(rows)
    detail["max_abs_drift"] = str(max((abs(x) for x in drifts), default=F(0)))
    detail["band_hits"] = hits[:5]
    imm = {}
    for rel in IMMUTABLE:
        first = git("log", "--diff-filter=A", "--format=%H", "--", NS_PREFIX + rel).split()
        first = first[-1] if first else None
        now = git("rev-parse", f"HEAD:{NS_PREFIX}{rel}")
        then = git("rev-parse", f"{first}:{NS_PREFIX}{rel}") if first else None
        imm[rel] = {"first_commit": first, "unchanged": now == then}
    res["A3_quarantine_and_incidents_immutable"] = all(v["unchanged"] for v in imm.values())
    detail["immutable"] = imm
    scan = subprocess.run([sys.executable, str(NS / "code" / "q309_guard.py"), "--scan"], capture_output=True, text=True)
    try:
        sv = json.loads(scan.stdout)["verdict"]
    except Exception:  # noqa: BLE001
        sv = "UNREADABLE"
    res["A4_static_scan"] = sv == "PASS"
    same = all(git("rev-parse", f"{LOCK_COMMIT}:{NS_PREFIX}{p}") == git("rev-parse", f"HEAD:{NS_PREFIX}{p}")
               and hashlib.sha1(b"blob %d\0" % len((NS / p).read_bytes()) + (NS / p).read_bytes()).hexdigest()
               == git("rev-parse", f"HEAD:{NS_PREFIX}{p}") for p in PRODUCER)
    sys.path.insert(0, str(NS / "impl"))
    import srk_certify as S  # noqa: E402
    fp = S.producer_fingerprint()["combined"]
    ev = sorted((NS / "evidence" / "srk_decoys").glob("*.json")) + sorted((NS / "evidence" / "srk_decoys_cell").glob("*.json"))
    bad_ev = []
    for f in ev:
        d = json.loads(f.read_text())
        if d.get("producer", {}).get("combined") != LOCK_FP or d.get("git_head_at_start") != LOCK_COMMIT:
            bad_ev.append(f.name)
        for c in d.get("certificates", {}).values():
            if c.get("status") == "CERTIFIED" and c.get("producer_sha256") != LOCK_FP:
                bad_ev.append(f.name + ":cert")
    res["A5_producer_lock_and_evidence_binding"] = same and fp == LOCK_FP and not bad_ev
    detail["producer_fp"] = fp
    detail["evidence_files"] = len(ev)
    detail["evidence_binding_failures"] = bad_ev
    tree = git("ls-tree", "-r", "HEAD", "--name-only").splitlines()
    res["A6_r5_unchanged_no_r6"] = (git("rev-parse", f"HEAD:{R5_PATH}") == R5_BLOB
                                    and not any(re.search(r"COVERAGE_MAP_R6", p, re.I) for p in tree))
    changed = git("diff", "--name-only", BASE, "HEAD").splitlines()
    outside = [p for p in changed if not p.startswith(NS_PREFIX)]
    res["A7_namespace_only_since_base"] = not outside
    detail["paths_changed_since_base"] = len(changed)
    detail["outside"] = outside[:5]
    refs = git("for-each-ref", "--format=%(refname)").splitlines()
    odd = [r for r in refs if not re.match(r"^refs/(heads|remotes|tags)/|^refs/stash$", r)]
    heads = [r for r in refs if r.startswith("refs/heads/")]
    # pre-existing repository tags (fetched with the clone) are allowed; a tag pointing INTO this campaign's commits
    # (BASE..HEAD) would be one the campaign created, and fails the check
    ours = set(git("rev-list", "HEAD", f"^{BASE}").split())
    new_tags = [r for r in refs if r.startswith("refs/tags/")
                and git("rev-parse", f"{r}^{{commit}}") in ours]
    res["A8_refs_ordinary"] = not odd and not new_tags and set(heads) <= {f"refs/heads/{BRANCH}", "refs/heads/main"}
    detail["odd_refs"] = odd
    detail["campaign_tags"] = new_tags
    vsrc = (NS / "verify" / "srk_verify_indep.py").read_text()
    res["A9_verifier_independent_imports"] = not re.search(
        r"^\s*(import|from)\s+(srk_kernel|srk_certify|srk_envelope|srk_float|srk_gate|srk_assemble|c1b_\w+)", vsrc, re.M)
    remote = subprocess.run(["git", "ls-remote", "origin", f"refs/heads/{BRANCH}"], cwd=REPO, capture_output=True,
                            text=True).stdout.split()
    detail["A10_local_head"] = git("rev-parse", "HEAD")
    detail["A10_remote_head"] = remote[0] if remote else None
    detail["A10_dirty"] = git("status", "--porcelain").splitlines()
    ok = all(res.values())
    out = {"label": label, "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "ok": ok, "checks": res, "detail": detail,
           "statement": "NEW Γ309 TARGET EVALUATIONS = 0 per ledger" if res["A1_target_counters_zero"] else "CHECK A1 FAILED"}
    return ok, out


if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "adhoc"
    ok, out = run(label)
    d = NS / "evidence" / "self_audit"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"SELF_AUDIT_{label}.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({"ok": ok, "checks": out["checks"], "max_abs_drift": out["detail"]["max_abs_drift"],
                      "evidence_files": out["detail"]["evidence_files"]}, indent=1))
    sys.exit(0 if ok else 1)
