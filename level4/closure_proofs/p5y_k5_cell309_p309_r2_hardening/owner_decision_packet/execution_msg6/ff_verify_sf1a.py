"""Fail-closed verification around the owner's SF1-A incorporation (message 6): r2 b66a45f0 -> 716946e8, nothing else.

usage: ff_verify_sf1a.py pre|prepush|post <session repo> <hardening commit holding the review> <out.json> [<pre.json>]
pre    : origin's r2 is EXACTLY b66a45f0 and origin's SF1-A branch EXACTLY 716946e8; b66a45f0 is an ancestor of
         716946e8; the range is exactly one commit whose only parent is b66a45f0; it changes exactly one path, the
         runner, by exactly the three reviewed added lines (no deletion); by AST only `fs_probe` differs and every
         other definition and every module-level statement is identical; the runner bytes and the tree are the ones
         the accepted review names; the review on the hardening branch carries its recorded sha256 and the
         accepted verdict; r1, main and the candidate unchanged; no protected ref on origin.  Exit 1 on any mismatch.
prepush: as pre, and HEAD is the local SF1-A branch at exactly 716946e8 with no tracked change.
post   : origin's r2 is EXACTLY 716946e8 (no new commit made), and every other ref on origin is exactly as in the pre
         snapshot given as <pre.json>.  Exit 1 on any mismatch.
"""
import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

mode, repo, hb, out = sys.argv[1], Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
pre = json.loads(Path(sys.argv[5]).read_text()) if len(sys.argv) > 5 else None
OLD, NEW = "b66a45f097989764176075802c953df4b72c2aef", "716946e8d9a6744d0b49de6acc802605b6eb1bf8"
R1, MAIN = "c902fe2fe33003ac7e4e61f29c10c81682fc940c", "1cb453826313c189f0bdafd5b84120c1edb74da9"
CAND = "a119e9789e2a1d42b584fff8a2301946a37f1bcb"
TREE_NEW, RUN_SHA_NEW = "3afb045cea6b78c708686ecc9108abd6a2d46100", "540df0552bfc31512289e30eaf1ead57bf82a4ac806f38080439c05c43f9a3af"
RUN_SHA_OLD = "36e428fbcd386a013bb97eb7ba154c9a815ab85265129daf11eb5cb5243abe1d"
REVIEW_SHA = "1f95ca2f81953a8643fc41cfc7a4bf6dcfd2175adccefce5670db39f141828a2"
R2B, SB = "claude/p5y-k5-cell309-p309-r2", "claude/p309-r2-sf1a-20261005"
NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
RUN = NS2 + "code/p309_" + "qualify.py"
REVIEW = "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/sf1a_review/REVIEW_SF1A_DELTA.md"
ADDED = [
    "        for led in (E.Q.EXEC_LEDGER, E.Q.EXPOSURE_LEDGER):  # SF1-A: RUN START's append must not fail after the mkdir",
    '            step = f"ledger appendability ({Path(led).name}: must exist and open for appending; nothing is written)"',
    "            os.close(os.open(str(led), os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW))",
]


def git(*a, check=True):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=check)


def blob(commit, path):
    return subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"], capture_output=True, check=True).stdout


remote = {}
for line in git("ls-remote", "origin").stdout.splitlines():
    sha, ref = line.split("\t")
    remote[ref] = sha
r = lambda b: remote.get("refs/heads/" + b)  # noqa: E731
res = {"mode": mode, "origin_refs": remote,
       "origin": {"r2": r(R2B), "sf1a": r(SB), "candidate": r("claude/p309-r2-adoption-candidate-20261005"),
                  "r1": r("claude/p5y-k5-cell309-p309-r1"), "main": r("main")},
       "protected_refs_on_origin": sorted(k for k in remote if re.match(r"refs/(p5y-k5-cell30|p309-cell309|rlr-tail/|p309-test/)", k))}
checks = {
    "candidate unchanged (a119e978)": res["origin"]["candidate"] == CAND,
    "r1 unchanged": res["origin"]["r1"] == R1,
    "main unchanged": res["origin"]["main"] == MAIN,
    "no protected ref on origin": not res["protected_refs_on_origin"],
    "SF1-A branch tip is exactly 716946e8": res["origin"]["sf1a"] == NEW,
}
if mode in ("pre", "prepush"):
    checks["origin r2 is exactly b66a45f0"] = res["origin"]["r2"] == OLD
    checks["716946e8 is a descendant of b66a45f0"] = git("merge-base", "--is-ancestor", OLD, NEW, check=False).returncode == 0
    commits = git("rev-list", "--reverse", f"{OLD}..{NEW}").stdout.split()
    res["range_commits"] = commits
    checks["range is exactly one commit, 716946e8"] = commits == [NEW]
    checks["its only parent is b66a45f0"] = git("rev-list", "--parents", "-n", "1", NEW).stdout.split() == [NEW, OLD]
    paths = git("diff", "--name-only", OLD, NEW).stdout.split()
    res["range_paths"] = paths
    checks["exactly one path changed: the runner"] = paths == [RUN]
    res["numstat"] = git("diff", "--numstat", OLD, NEW).stdout.strip()
    checks["3 lines added, 0 deleted"] = res["numstat"] == f"3\t0\t{RUN}"
    d = git("diff", "-U0", OLD, NEW).stdout.splitlines()
    plus = [l[1:] for l in d if l.startswith("+") and not l.startswith("+++")]
    minus = [l for l in d if l.startswith("-") and not l.startswith("---")]
    hunks = [l for l in d if l.startswith("@@")]
    res["hunks"], res["added_lines"] = hunks, plus
    checks["exactly one hunk"] = len(hunks) == 1
    checks["added lines are byte-for-byte the reviewed three"] = plus == ADDED and not minus
    old_b, new_b = blob(OLD, RUN), blob(NEW, RUN)
    res["runner_sha256_old"], res["runner_sha256_new"] = hashlib.sha256(old_b).hexdigest(), hashlib.sha256(new_b).hexdigest()
    checks["runner at b66a45f0 is the reviewed base bytes"] = res["runner_sha256_old"] == RUN_SHA_OLD
    checks["runner at 716946e8 is the reviewed bytes (540df055)"] = res["runner_sha256_new"] == RUN_SHA_NEW
    checks["tree of 716946e8 is the reviewed tree (3afb045c)"] = git("rev-parse", NEW + "^{tree}").stdout.strip() == TREE_NEW
    to, tn = ast.parse(old_b), ast.parse(new_b)
    defs = lambda t: {n.name: ast.dump(n) for n in t.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}  # noqa: E731
    mods = lambda t: [ast.dump(n) for n in t.body if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]  # noqa: E731
    do, dn = defs(to), defs(tn)
    res["ast_changed"] = sorted(k for k in set(do) | set(dn) if do.get(k) != dn.get(k))
    checks["by AST only fs_probe differs"] = res["ast_changed"] == ["fs_probe"] and set(do) == set(dn)
    checks["module-level statements identical"] = mods(to) == mods(tn)
    # the added lines sit inside fs_probe's body
    fp = [n for n in tn.body if isinstance(n, ast.FunctionDef) and n.name == "fs_probe"][0]
    m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", hunks[0]) if hunks else None
    first = int(m.group(1)) if m else -1
    checks["the hunk lies inside fs_probe"] = fp.lineno < first and first + 2 <= fp.end_lineno
    rv = subprocess.run(["git", "-C", str(repo), "show", f"{hb}:{REVIEW}"], capture_output=True, check=True).stdout
    res["review_sha256"] = hashlib.sha256(rv).hexdigest()
    checks["accepted review is the recorded bytes (1f95ca2f)"] = res["review_sha256"] == REVIEW_SHA
    checks["review line 2 is SF1A_DELTA_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS"] = (
        rv.decode().split("\n")[1] == "SF1A_DELTA_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS")
    checks["review names 716946e8 and b66a45f0"] = NEW.encode() in rv and OLD.encode() in rv
    checks["review rules SF1: RESOLVED"] = b"SF1: RESOLVED" in rv and b"SF1: NOT_RESOLVED" not in rv.replace(
        b"`SF1: RESOLVED` or `SF1: NOT_RESOLVED`", b"")
    if mode == "prepush":
        checks["HEAD is the local SF1-A branch"] = git("branch", "--show-current").stdout.strip() == SB
        checks["HEAD is exactly 716946e8"] = git("rev-parse", "HEAD").stdout.strip() == NEW
        checks["no tracked change in the working tree"] = git("status", "--porcelain", "--untracked-files=no").stdout == ""
else:
    checks["origin r2 is exactly 716946e8 (no new commit)"] = res["origin"]["r2"] == NEW
    checks["b66a45f0 is an ancestor of origin r2"] = git("merge-base", "--is-ancestor", OLD, res["origin"]["r2"] or "0" * 40,
                                                         check=False).returncode == 0
    assert pre is not None, "post needs the pre snapshot"
    before = dict(pre["origin_refs"])
    changed = sorted(k for k in set(before) | set(remote) if before.get(k) != remote.get(k))
    res["refs_changed_since_pre"] = {k: [before.get(k), remote.get(k)] for k in changed}
    checks["only r2 changed on origin since the pre snapshot"] = changed == ["refs/heads/" + R2B]
    checks["r2 moved exactly b66a45f0 -> 716946e8"] = before.get("refs/heads/" + R2B) == OLD and remote.get("refs/heads/" + R2B) == NEW
res["checks"] = checks
res["ok"] = all(checks.values())
out.write_text(json.dumps(res, indent=1) + "\n")
print(json.dumps({"checks": checks, "ok": res["ok"]}, indent=1))
sys.exit(0 if res["ok"] else 1)
