"""QC15: read-only self-audit of the formal campaign (adapted from the research self-audit A1-A10).  Exit 0 iff all pass.

  python3 code/p309_self_audit.py LABEL   -> evidence/self_audit/SELF_AUDIT_<LABEL>.json

A1 every formal ZERO_TARGET_LEDGER line has zero target counters and touched no quarantined cell
A2 no ledgered drift (point or interval) meets the band [6/5, 13/5] or its mirror (geometry-blind)
A3 immutable governance files are byte-identical to their first committed versions: r2's own preserved records (the
   owner's 2026-10-01 instructions verbatim, r2's reviews and their ledgers, briefs, the verifier author's report)
   and r2's byte copies of r1's governance records, each also equal to r1's blob; r1's own records, including its
   reviews, are inherited at r1's paths and covered by A7's r1-tree check (r2 addendum 1, P2)
A4 the formal static scan passes (code/p309_scan.py; planted controls fire)
A5 the research producer files are byte-identical to the lock commit and the fingerprint equals the lock fingerprint
A6 r5 blob unchanged; no coverage map r6 anywhere in the tree
A7 since r2's base (c902fe2f, r1's final head) every changed path lies in r2's namespace; r1's namespace tree is
   exactly ecd1c359 (r1 never mutated); the research namespace is unchanged since eb9a9c22 (r2 addendum 1, P2)
A8 no non-ordinary ref (no exactly-once marker, no pending ref, no production-namespace ref) and no campaign tag
A9 the band-scoped verifier variant imports no producer or C1b module
A10 the research verifier-probe envelope audit (committed evidence) reports no in-band evaluated probe, and every
    formal ledger line with drifts is out of band (A2)
A11 (informational) local HEAD, remote tip, dirt
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

FNS = Path(__file__).resolve().parents[1]
REPO = FNS.parents[2]
RNS = FNS.parent / "p5y_k5_cell309_research_r1"
NS_PREFIX = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
RNS_PREFIX = "level4/closure_proofs/p5y_k5_cell309_research_r1/"
BRANCH = "claude/p5y-k5-cell309-p309-r2"  # q309: literal-ok (branch name, not a cell reference)
BASE = "eb9a9c22b093f938e1bf13e0b30512608c58c370"          # research HEAD: the research-unchanged check (A7) and tags (A8)
R2_BASE = "c902fe2fe33003ac7e4e61f29c10c81682fc940c"       # r1's final head: r2's base for the namespace-only check (A7)
R1_PREFIX = "level4/closure_proofs/p5y_k5_cell309_p309_r1"  # inherited r1 records: read-only, never written
R1_TREE = "ecd1c359ef0c3e0c9911b014b884376a10f6ed5b"      # r1's namespace tree at its final head
LOCK_COMMIT = "2a03e838498ab8a8c1c61b9a142ba45adb941592"
LOCK_FP = "377057bef1d1f21be4db38488235596c0e4134bb75ffdced08e667e6c48cc8db"
PRODUCER = ["impl/srk_kernel.py", "impl/srk_float.py", "impl/srk_envelope.py", "impl/srk_certify.py"]
R5_PATH = "level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
R5_BLOB = "f978eeb6b41188eabaf3c6d590c9178d711f1ce6"
BAND = (F(6, 5), F(13, 5))   # q309: literal-ok (the quarantine band definition, used only to classify)
# r2's own preserved records (unchanged since their first r2 commit)
IMMUTABLE = ["governance/OWNER_INSTRUCTIONS_R2_VERBATIM.md", "governance/BRIEF_R2_PLAN_REVIEW.md",
             "governance/REVIEW_R2_PLAN.md", "governance/REVIEW_R2_PLAN_EXEC_LEDGER.jsonl",
             "governance/BRIEF_R2_PLAN_FOLLOWUP_1.md", "governance/REVIEW_R2_PLAN_FOLLOWUP_1.md",
             "governance/REVIEW_R2_PLAN_FOLLOWUP_1_EXEC_LEDGER.jsonl", "governance/BRIEF_R2_VERIFIER_AUTHOR_1.md",
             "verify/R2_VERIFIER_CHANGES_REPORT.md", "verify/R2_VERIFIER_EXEC_LEDGER.jsonl",
             "governance/OWNER_INSTRUCTIONS_R2_MSG4_VERBATIM.md",
             # r2 delta review A5: the delta brief, the review with its ledger, and every review's sha256 record
             "governance/BRIEF_R2_DELTA_REVIEW.md", "governance/REVIEW_R2_DELTA.md",
             "governance/REVIEW_R2_DELTA_EXEC_LEDGER.jsonl", "governance/REVIEW_R2_DELTA.sha256",
             "governance/REVIEW_R2_PLAN.sha256", "governance/REVIEW_R2_PLAN_FOLLOWUP_1.sha256"]
# r2's byte copies of r1's immutable governance records (step 3a): unchanged in r2 AND equal to r1's blob.  r1's
# config/FORMAL_QUARANTINE_P309.json is not here: r2's copy carries the relocation map; r1's original is covered by A7
IMMUTABLE_COPIES = ["governance/OWNER_DECISIONS_P309_VERBATIM.md", "governance/OWNER_RULINGS_2_P309_VERBATIM.md",
                    "governance/U2_CORRECTED_PROPOSITION.md", "fc2/FC2_SPEC.md", "fc2/FC2_SPEC_R2.md",
                    "governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md",
                    "governance/D5_OWNER_RATIFICATION_REQUEST_P309.md",
                    "governance/INCIDENT_P309F_01_FC2_REV1_INSTRUCTION.md",
                    "governance/briefs_recovered/AGENT_BRIEFS_TRANSCRIPT.jsonl"]
# the append-only documents (FC2_SPEC_R2_ERRATUM_1, ERRATA_FORMAL, P309_REV2C_AMENDMENTS, D5_SITE_BACKSTOP_REPORT, the
# qualification-review brief with its addenda) are not "unchanged since
# their first commit"; after the freeze they are fixed like every frozen-directory file (QC13, check_grant)
PRODUCER_MODULES = re.compile(r"^\s*(import|from)\s+(srk_kernel|srk_certify|srk_envelope|srk_float|srk_gate|srk_assemble|"
                              r"c1b_\w+|p309_guard|q309_guard)\b", re.M)


def git(*a) -> str:
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()


def meets(lo: F, hi: F) -> bool:
    return not (hi < BAND[0] or lo > BAND[1]) or not (hi < -BAND[1] or lo > -BAND[0])


def run(label: str) -> tuple:
    res, detail = {}, {}
    rows = [json.loads(l) for l in (FNS / "ledger" / "ZERO_TARGET_LEDGER.jsonl").read_text().splitlines() if l.strip()]
    res["A1_target_counters_zero"] = all(r.get("new_target_evaluations", 0) == 0 and
                                         r.get("target_equivalent_proxies", 0) == 0 and
                                         r.get("target_informed_optimisation", 0) == 0 and
                                         not r.get("cells_touched") for r in rows)
    hits = []
    for r in rows:
        for d in r.get("drifts", []):
            lo, hi = F(d[0]), F(d[-1])
            if meets(min(lo, hi), max(lo, hi)):
                hits.append(d)
    res["A2_no_band_drift"] = not hits
    detail["ledger_lines"] = len(rows)
    detail["band_hits"] = hits[:5]
    imm = {}
    for rel in IMMUTABLE + IMMUTABLE_COPIES:
        first = git("log", "--diff-filter=A", "--format=%H", "--", NS_PREFIX + rel).split()
        first = first[-1] if first else None
        now = git("rev-parse", f"HEAD:{NS_PREFIX}{rel}")
        then = git("rev-parse", f"{first}:{NS_PREFIX}{rel}") if first else None
        wt = hashlib.sha1(b"blob %d\0" % len((FNS / rel).read_bytes()) + (FNS / rel).read_bytes()).hexdigest()
        r1 = git("rev-parse", f"{R2_BASE}:{R1_PREFIX}/{rel}") if rel in IMMUTABLE_COPIES else now
        imm[rel] = {"first_commit": first, "unchanged": now == then == wt == r1}
    res["A3_immutable_governance"] = all(v["unchanged"] for v in imm.values())
    detail["immutable"] = imm
    sc = subprocess.run([sys.executable, str(FNS / "code" / "p309_scan.py")], capture_output=True, text=True)
    try:
        sv = json.loads(sc.stdout)["verdict"]
    except ValueError:
        sv = "UNREADABLE"
    res["A4_formal_static_scan"] = sv == "PASS"
    same = all(git("rev-parse", f"{LOCK_COMMIT}:{RNS_PREFIX}{p}") == git("rev-parse", f"HEAD:{RNS_PREFIX}{p}")
               for p in PRODUCER)
    fp = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import srk_certify as S; "
                         "print(S.producer_fingerprint()['combined'])" % str(RNS / "impl")],
                        capture_output=True, text=True, cwd=str(FNS)).stdout.strip()
    res["A5_producer_lock"] = same and fp == LOCK_FP
    detail["producer_fp"] = fp
    tree = git("ls-tree", "-r", "HEAD", "--name-only").splitlines()
    res["A6_r5_unchanged_no_r6"] = (git("rev-parse", f"HEAD:{R5_PATH}") == R5_BLOB
                                    and not any(re.search(r"COVERAGE_MAP_R6", p, re.I) for p in tree))
    changed = git("diff", "--name-only", R2_BASE, "HEAD").splitlines()
    outside = [p for p in changed if not p.startswith(NS_PREFIX)]
    research_changed = git("diff", "--name-only", BASE, "HEAD", "--", RNS_PREFIX).splitlines()
    r1_tree = git("rev-parse", f"HEAD:{R1_PREFIX}")
    res["A7_formal_namespace_only_research_unchanged"] = not outside and not research_changed and r1_tree == R1_TREE
    detail["r1_tree"] = r1_tree
    detail["outside"] = outside[:5]
    refs = git("for-each-ref", "--format=%(refname)").splitlines()
    odd = [r for r in refs if not re.match(r"^refs/(heads|remotes|tags)/|^refs/stash$", r)]
    ours = set(git("rev-list", "HEAD", f"^{BASE}").split())
    new_tags = [r for r in refs if r.startswith("refs/tags/") and git("rev-parse", f"{r}^{{commit}}") in ours]
    res["A8_refs_ordinary_no_marker"] = not odd and not new_tags
    detail["odd_refs"] = odd
    var = FNS / "verify" / "srk_verify_indep_scoped.py"
    res["A9_variant_independent_imports"] = var.exists() and not PRODUCER_MODULES.search(var.read_text())
    env = json.loads((RNS / "evidence" / "VERIFIER_PROBE_ENVELOPE.json").read_text())
    res["A10_probe_envelope"] = env.get("ok") is True and not env["v2"]["inband_evaluated"] and res["A2_no_band_drift"]
    remote = subprocess.run(["git", "ls-remote", "origin", f"refs/heads/{BRANCH}"], cwd=REPO, capture_output=True,
                            text=True).stdout.split()
    detail["A11_local_head"] = git("rev-parse", "HEAD")
    detail["A11_remote_head"] = remote[0] if remote else None
    detail["A11_dirty"] = git("status", "--porcelain").splitlines()[:20]
    ok = all(res.values())
    out = {"label": label, "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "ok": ok, "checks": res, "detail": detail,
           "statement": "NEW Γ309 TARGET EVALUATIONS = 0 per the formal ledger" if res["A1_target_counters_zero"]
           else "CHECK A1 FAILED"}
    return ok, out


if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "adhoc"
    ok, out = run(label)
    sys.path.insert(0, str(FNS / "code"))
    import p309_env as E
    d = E.evidence_dir("self_audit")
    (d / f"SELF_AUDIT_{label}.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"ok": ok, "checks": out["checks"]}, indent=1))
    sys.exit(0 if ok else 1)
