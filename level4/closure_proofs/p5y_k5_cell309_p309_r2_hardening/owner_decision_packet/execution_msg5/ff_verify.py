"""Fail-closed verification around the owner's H-A fast-forward (C1): r2 101ef2cb -> a119e978, nothing else.

usage: ff_verify.py pre|post <session repo> <out.json>
pre : origin's r2 is EXACTLY 101ef2cb and origin's candidate EXACTLY a119e978; 101ef2cb is an ancestor of a119e978;
      the range is exactly the two reviewed commits (93d55063, a119e978) and exactly the four reviewed r2-namespace
      paths; r1 and main unchanged; no protected ref on origin.  Exit 1 on any mismatch.
post: origin's r2 is EXACTLY a119e978 (the candidate commit itself: no new commit was made), the candidate branch
      unchanged, r1/main unchanged, no protected ref.  Exit 1 on any mismatch.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

mode, repo, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
R2, CAND = "101ef2cb17e5eab2892212178278da45b98004ed", "a119e9789e2a1d42b584fff8a2301946a37f1bcb"
R1, MAIN = "c902fe2fe33003ac7e4e61f29c10c81682fc940c", "1cb453826313c189f0bdafd5b84120c1edb74da9"
NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
PATHS = sorted([NS2 + "code/p309_" + "qualify.py", NS2 + "code/p309_" + "topology_drill.py",
                NS2 + "config/SCANNER_ALLOWANCE_P309.json", NS2 + "governance/R2_REPIN_LIST_SUPPLEMENT_5.json"])


def git(*a, check=True):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=check)


remote = {}
for line in git("ls-remote", "origin").stdout.splitlines():
    sha, ref = line.split("\t")
    remote[ref] = sha
r = lambda b: remote.get("refs/heads/" + b)  # noqa: E731
res = {"mode": mode, "origin": {"r2": r("claude/p5y-k5-cell309-p309-r2"),
                                "candidate": r("claude/p309-r2-adoption-candidate-20261005"),
                                "r1": r("claude/p5y-k5-cell309-p309-r1"), "main": r("main")},
       "protected_refs_on_origin": sorted(k for k in remote if re.match(r"refs/(p5y-k5-cell30|p309-cell309|rlr-tail/|p309-test/)", k))}
checks = {}
checks["candidate is a119e978"] = res["origin"]["candidate"] == CAND
checks["r1 unchanged"] = res["origin"]["r1"] == R1
checks["main unchanged"] = res["origin"]["main"] == MAIN
checks["no protected ref on origin"] = not res["protected_refs_on_origin"]
checks["local object a119e978 is a commit"] = git("cat-file", "-t", CAND, check=False).stdout.strip() == "commit"
if mode in ("pre", "prepush"):
    checks["r2 is exactly 101ef2cb"] = res["origin"]["r2"] == R2
    checks["101ef2cb is an ancestor of a119e978 (fast-forward)"] = git("merge-base", "--is-ancestor", R2, CAND,
                                                                       check=False).returncode == 0
    commits = git("rev-list", "--reverse", f"{R2}..{CAND}").stdout.split()
    res["range_commits"] = commits
    checks["range is exactly the two reviewed commits"] = [c[:8] for c in commits] == ["93d55063", "a119e978"]
    paths = sorted(git("diff", "--name-only", R2, CAND).stdout.split())
    res["range_paths"] = paths
    checks["range is exactly the four reviewed paths"] = paths == PATHS
    local = git("rev-parse", "-q", "--verify", "refs/heads/claude/p5y-k5-cell309-p309-r2", check=False)
    if mode == "pre":          # before the local branch is created
        checks["no local branch named r2 yet"] = local.returncode != 0
    else:                      # prepush: the local branch exists and is exactly the candidate commit
        checks["local r2 branch is exactly a119e978"] = local.stdout.strip() == CAND
        checks["HEAD is the local r2 branch at a119e978"] = (
            git("branch", "--show-current", check=False).stdout.strip() == "claude/p5y-k5-cell309-p309-r2"
            and git("rev-parse", "HEAD").stdout.strip() == CAND)
        checks["no tracked change in the working tree"] = git("status", "--porcelain", "--untracked-files=no").stdout == ""
else:
    checks["r2 is exactly a119e978 (no new commit)"] = res["origin"]["r2"] == CAND
    checks["101ef2cb is an ancestor of r2"] = git("merge-base", "--is-ancestor", R2, res["origin"]["r2"] or "0" * 40,
                                                  check=False).returncode == 0
    res["r2_tree"] = git("rev-parse", CAND + "^{tree}").stdout.strip()
res["checks"] = checks
res["ok"] = all(checks.values())
out.write_text(json.dumps(res, indent=1) + "\n")
print(json.dumps(res, indent=1))
sys.exit(0 if res["ok"] else 1)
