"""Independent verification of r2 after the owner's message-6 sequence (SF1-A incorporation, then one governance-only
commit), from a FRESH clone of origin's r2 branch.

usage: verify_r2_final.py <origin url> <filing commit> <hardening commit with the sources> <session repo>
                          <work dir (new)> <out.json>
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

url, filing, hb, repo, work, out = sys.argv[1], sys.argv[2], sys.argv[3], Path(sys.argv[4]), Path(sys.argv[5]), Path(sys.argv[6])
OLD, NEW = "b66a45f097989764176075802c953df4b72c2aef", "716946e8d9a6744d0b49de6acc802605b6eb1bf8"
NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
GOV = NS2 + "governance/"
HNS = "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/"
RUN = NS2 + "code/p309_" + "qualify.py"
R5 = "level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
SRC = {"BRIEF_SF1A_DELTA_REVIEW.md": HNS + "sf1a_review/BRIEF_SF1A_DELTA_REVIEW.md",
       "REVIEW_SF1A_DELTA.md": HNS + "sf1a_review/REVIEW_SF1A_DELTA.md",
       "REVIEW_SF1A_DELTA_EXEC_LEDGER.jsonl": HNS + "sf1a_review/REVIEW_SF1A_DELTA_EXEC_LEDGER.jsonl",
       "OWNER_DECISIONS_R2_MSG6_VERBATIM.md": HNS + "owner_decision_packet/owner_reply_msg6/OWNER_DECISIONS_R2_MSG6_VERBATIM.md"}
NEWFILES = sorted(GOV + n for n in list(SRC) + ["REVIEW_SF1A_DELTA.sha256", "R2_SF1A_INCORPORATION_RECORD.json"])


def g(d, *a, check=True):
    return subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, check=check).stdout.strip()


def gb(d, *a):
    return subprocess.run(["git", "-C", str(d), *a], capture_output=True, check=True).stdout


h = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
work.mkdir()
clone = work / "r2"
subprocess.run(["git", "clone", "-q", "--single-branch", "--branch", "claude/p5y-k5-cell309-p309-r2", "--no-tags", url,
                str(clone)], check=True)
head = g(clone, "rev-parse", "HEAD")
chain = g(clone, "rev-list", "--first-parent", "--max-count=6", "HEAD").split()
ns = g(clone, "diff", "--name-status", NEW, "HEAD").splitlines()
ls = lambda c: dict(l.split("\t")[::-1] for l in g(clone, "ls-tree", "-r", c, NS2).splitlines())  # noqa: E731
l16, lh = ls(NEW), ls("HEAD")
changed_existing = sorted(p for p in l16 if lh.get(p) != l16[p])
nongov_same = all(lh.get(p) == l16[p] for p in l16 if not p.startswith(GOV))
copies = {n: (clone / GOV / n).read_bytes() == gb(repo, "show", f"{hb}:{s}") for n, s in SRC.items()}
review = (clone / GOV / "REVIEW_SF1A_DELTA.md").read_bytes()
msg = (clone / GOV / "OWNER_DECISIONS_R2_MSG6_VERBATIM.md").read_text()
body = msg.split("```text\n", 1)[1].rsplit("\n```", 1)[0]
rec = json.loads((clone / GOV / "R2_SF1A_INCORPORATION_RECORD.json").read_text())
outside = [p for p in g(clone, "diff", "--name-only", "c902fe2fe33003ac7e4e61f29c10c81682fc940c", "HEAD").split()
           if not p.startswith(NS2)]
checks = {
    "HEAD is the filing commit": head == filing,
    "HEAD's only parent is 716946e8": g(clone, "rev-list", "--parents", "-n", "1", "HEAD").split() == [filing, NEW],
    "first-parent chain filing -> 716946e8 -> b66a45f0 -> a119e978 -> 93d55063 -> 101ef2cb":
        [c[:8] for c in chain[1:]] == ["716946e8", "b66a45f0", "a119e978", "93d55063", "101ef2cb"],
    "716946e8 is an ancestor of HEAD": subprocess.run(["git", "-C", str(clone), "merge-base", "--is-ancestor", NEW,
                                                       "HEAD"]).returncode == 0,
    "the filing only ADDS exactly the six governance files": sorted(l.split("\t")[1] for l in ns) == NEWFILES
    and all(l.startswith("A\t") for l in ns),
    "no existing r2 file changed by the filing": changed_existing == [],
    "every non-governance r2 file identical to 716946e8": nongov_same,
    "runner is the reviewed bytes (540df055)": h((clone / RUN).read_bytes()) ==
        "540df0552bfc31512289e30eaf1ead57bf82a4ac806f38080439c05c43f9a3af",
    "runner blob equals 716946e8's": g(clone, "rev-parse", f"HEAD:{RUN}") == g(repo, "rev-parse", f"{NEW}:{RUN}"),
    "filed copies byte-identical to the accepted records": all(copies.values()),
    "review sha256 1f95ca2f and its .sha256 file agree": h(review) == "1f95ca2f81953a8643fc41cfc7a4bf6dcfd2175adccefce5670db39f141828a2"
    and (clone / GOV / "REVIEW_SF1A_DELTA.sha256").read_text() == f"{h(review)}  {GOV}REVIEW_SF1A_DELTA.md\n",
    "review verdict line": review.decode().split("\n")[1] == "SF1A_DELTA_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS",
    "message 6 verbatim hash matches": f"sha256: `{h(body.encode())}`" in msg
    and h(body.encode()) == "c073fc02239cca6bd643b7387d702671fbc93ae49ac3bda6e782189af8e6e448",
    "incorporation record binds b66a45f0 -> 716946e8, not forced, no new commit": rec["fast_forward"]["from"] == OLD
    and rec["fast_forward"]["to"] == NEW and rec["fast_forward"]["forced"] is False
    and rec["fast_forward"]["new_commit_created"] is False,
    "incorporation record states SF1 RESOLVED for the incorporated bytes": rec["sf1_status"].startswith("SF1: RESOLVED"),
    "no path outside r2's namespace changed since c902fe2f (A7)": outside == [],
    "r1 tree is ecd1c359": g(clone, "rev-parse", "HEAD:level4/closure_proofs/p5y_k5_cell309_p309_r1") ==
        "ecd1c359ef0c3e0c9911b014b884376a10f6ed5b",
    "r5 unchanged": g(clone, "rev-parse", f"HEAD:{R5}") == "f978eeb6b41188eabaf3c6d590c9178d711f1ce6",
    "no r6": not [p for p in g(clone, "ls-tree", "-r", "--name-only", "HEAD").split()
                  if "COVERAGE_MAP_R6" in p or p.endswith("_R6.json")],
    "no freeze record": not (clone / NS2 / "ledger" / "FREEZE_RECORD.json").exists(),
    "no freeze directory content": not any((clone / NS2 / "freeze").glob("*")) if (clone / NS2 / "freeze").exists() else True,
    "no qualification directory": not (clone / NS2 / "qualification").exists(),
}
res = {"origin_url": url, "head": head, "tree": g(clone, "rev-parse", "HEAD^{tree}"), "first_parent_chain": chain,
       "filing_name_status": ns, "copies_identical": copies, "checks": checks, "ok": all(checks.values())}
out.write_text(json.dumps(res, indent=1) + "\n")
print(json.dumps({"checks": checks, "ok": res["ok"]}, indent=1))
sys.exit(0 if res["ok"] else 1)
