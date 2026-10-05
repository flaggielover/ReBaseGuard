"""Independent verification of r2 after the owner's H-A fast-forward, from a FRESH clone of origin (task 7, step 3).

usage: verify_r2_fresh.py <origin url or path> <hardening evidence commit> <session repo> <work dir (new)> <out.json>
The fresh clone fetches only origin's r2 branch.  Checks, against hashes bound by the REVIEWED evidence (read from the
session repository at the given hardening commit, never from the clone itself):
  * r2 HEAD == a119e978 (the candidate commit itself; no new commit); tree == the tree the rehearsal bound;
  * ancestry: HEAD's first-parent chain is a119e978 -> 93d55063 -> 101ef2cb, and 101ef2cb is an ancestor;
  * 101ef2cb..HEAD changes exactly the four reviewed r2-namespace paths;
  * the runner's sha256 == the one the S1/regression evidence bound; the allowance sha256 == the reviewed one;
    supplement 5 sha256 == the reviewed one; the drill blob == the candidate's;
  * no path outside r2's namespace changed since c902fe2f (QC15 A7); r1 tree ecd1c359; r5 blob unchanged; no r6;
    no freeze record and no qualification directory in r2.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

url, hb, repo, work, out = sys.argv[1], sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5])
R2_OLD, CAND = "101ef2cb17e5eab2892212178278da45b98004ed", "a119e9789e2a1d42b584fff8a2301946a37f1bcb"
NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
FU = "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/r2_candidate_followup/evidence/"
RUN, DRILL = NS2 + "code/p309_" + "qualify.py", NS2 + "code/p309_" + "topology_drill.py"
ALLOW, SUPP5 = NS2 + "config/SCANNER_ALLOWANCE_P309.json", NS2 + "governance/R2_REPIN_LIST_SUPPLEMENT_5.json"
R5 = "level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"


def g(d, *a, check=True):
    return subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, check=check).stdout.strip()


def ev(rel):
    return json.loads(g(repo, "show", f"{hb}:{FU}{rel}"))


work.mkdir()
clone = work / "r2"
subprocess.run(["git", "clone", "-q", "--single-branch", "--branch", "claude/p5y-k5-cell309-p309-r2", "--no-tags", url,
                str(clone)], check=True)
head = g(clone, "rev-parse", "HEAD")
prov = ev("rehearsal/PROVENANCE.json")
ast_new = ev("AST_RUNNER_93d55063_VS_a119e978.json")
allow_diff = ev("ALLOWANCE_DIFF_R2_VS_a119e978.json")
reg = ev("REG_a119e978.json")
sha = lambda rel: hashlib.sha256((clone / rel).read_bytes()).hexdigest()  # noqa: E731
chain = g(clone, "rev-list", "--first-parent", "--max-count=3", "HEAD").split()
paths = sorted(g(clone, "diff", "--name-only", R2_OLD, "HEAD").split())
outside = [p for p in g(clone, "diff", "--name-only", "c902fe2fe33003ac7e4e61f29c10c81682fc940c", "HEAD").split()
           if not p.startswith(NS2)]
checks = {
    "HEAD is a119e978 (no new commit)": head == CAND,
    "tree equals the tree the rehearsal bound": g(clone, "rev-parse", "HEAD^{tree}") == prov["package"]["tree"]
    if "package" in prov else g(clone, "rev-parse", "HEAD^{tree}") == prov.get("tree"),
    "rehearsal bound this exact commit": (prov.get("package", prov)).get("commit") == CAND,
    "first-parent chain a119e978 -> 93d55063 -> 101ef2cb": [c[:8] for c in chain] == ["a119e978", "93d55063", "101ef2cb"],
    "101ef2cb is an ancestor of HEAD": subprocess.run(["git", "-C", str(clone), "merge-base", "--is-ancestor", R2_OLD,
                                                       "HEAD"]).returncode == 0,
    "exactly the four reviewed paths changed since 101ef2cb": paths == sorted([RUN, DRILL, ALLOW, SUPP5]),
    "runner sha256 equals the reviewed bytes (AST evidence)": sha(RUN) == ast_new["new_sha256"],
    "runner sha256 equals the regression-bound runner": sha(RUN) == reg.get("runner_sha256"),
    "allowance sha256 equals the reviewed one": sha(ALLOW) == allow_diff["new_sha256"],
    "drill blob equals the candidate's": g(clone, "rev-parse", f"HEAD:{DRILL}") == g(repo, "rev-parse", f"{CAND}:{DRILL}"),
    "supplement 5 blob equals the candidate's": g(clone, "rev-parse", f"HEAD:{SUPP5}") == g(repo, "rev-parse", f"{CAND}:{SUPP5}"),
    "no path outside r2's namespace changed since c902fe2f (A7)": outside == [],
    "r1 tree is ecd1c359": g(clone, "rev-parse", "HEAD:level4/closure_proofs/p5y_k5_cell309_p309_r1") ==
    "ecd1c359ef0c3e0c9911b014b884376a10f6ed5b",
    "r5 unchanged": g(clone, "rev-parse", f"HEAD:{R5}") == "f978eeb6b41188eabaf3c6d590c9178d711f1ce6",
    "no r6": not [p for p in g(clone, "ls-tree", "-r", "--name-only", "HEAD").split()
                  if "COVERAGE_MAP_R6" in p or p.endswith("_R6.json")],
    "no freeze record": not (clone / NS2 / "ledger" / "FREEZE_RECORD.json").exists(),
    "no qualification directory": not (clone / NS2 / "qualification").exists(),
}
res = {"origin_url": url, "head": head, "tree": g(clone, "rev-parse", "HEAD^{tree}"), "first_parent_chain": chain,
       "paths_since_101ef2cb": paths, "runner_sha256": sha(RUN), "allowance_sha256": sha(ALLOW),
       "evidence_commit": hb, "checks": checks, "ok": all(checks.values())}
out.write_text(json.dumps(res, indent=1) + "\n")
print(json.dumps(res, indent=1))
sys.exit(0 if res["ok"] else 1)
