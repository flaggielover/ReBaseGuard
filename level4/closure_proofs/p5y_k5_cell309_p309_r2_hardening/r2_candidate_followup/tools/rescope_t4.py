"""Task 4 (S1-S3 follow-up): re-scope a COPY of the session guard.

usage: rescope_t4.py <hooks dir of the copy> a|c
  a: commits only on the adoption-candidate branch, and only of the runner (S1 probe) and the NEW additive governance
     supplement R2_REPIN_LIST_SUPPLEMENT_5.json (S2).  Every earlier supplement, the drill, the allowance and the rest
     of r2 stay protected.  The hardening namespace stays writable for untracked drafts and tests.
  c: back to the hardening branch for the reports (no r2 file writable), as in task-3 phase C.
Vectors: push vectors follow the branch; the task-3 phase-C runner vector (which reused the id W22) is renamed W24 and
guards the drill in phase a, the runner in phase c; W23 (an earlier supplement is protected) and P25 (the new
supplement is admitted) exist in phase a only.
"""
import json
import sys
from pathlib import Path

hooks, phase = Path(sys.argv[1]), sys.argv[2]
RUN = "p309_" + "qualify.py"
DRILL = "p309_" + "topology_drill.py"
NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
p = hooks / "p309_guard_policy.py"
s = p.read_text()
for start in ("# Task 4 (S1-S3 follow-up", "# Task 3 (minimal r2 adoption candidate"):
    if start in s:
        a = s.index(start)
        break
b = s.index("# files under these prefixes may name prohibited identifiers as data")
block = '''# Task 4 (S1-S3 follow-up of the r2 adoption candidate, 2026-10-05), phase @PHASE@.  The only branch this session may
# commit to or push; the guard admits `git checkout ALLOWED_BRANCH` (both branches already exist).
ALLOWED_BRANCH = "@BRANCH@"
R2_HEAD = "101ef2cb17e5eab2892212178278da45b98004ed"
KNOWN_BRANCHES = ("claude/p309-q11-recovery-20261005", "claude/p309-r2-hardening-20261005",
                  "claude/p309-r2-adoption-candidate-20261005")
ALLOWED_REMOTE = "origin"
BASE_COMMIT = R2_HEAD                                           # the branch point of both task branches

NEW_NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/"
R2_RUNNER = "@NS2@code/@RUN@"
# S2: one NEW additive governance supplement; every earlier supplement and the rest of governance stay protected
R2_REPIN_SUPP5 = "@NS2@governance/R2_REPIN_LIST_SUPPLEMENT_5.json"
'''
if phase == "a":
    block += '''WRITE_ALLOW = (NEW_NS, R2_RUNNER, R2_REPIN_SUPP5, ".claude/hooks/", ".claude/settings.json", ".claude/audit/",
               ".claude/.gitignore")
# the commit-set on the candidate branch: the runner (S1) and the new supplement (S2), nothing else
COMMIT_ALLOW = (R2_RUNNER, R2_REPIN_SUPP5)
'''
    branch, other = "claude/p309-r2-adoption-candidate-20261005", "claude/p309-r2-hardening-20261005"
else:
    block += '''# phase c: the candidate is committed and pushed; no r2 file is writable any more
WRITE_ALLOW = (NEW_NS, ".claude/hooks/", ".claude/settings.json", ".claude/audit/", ".claude/.gitignore")
COMMIT_ALLOW = None                                             # the commit-set is the write-set
'''
    branch, other = "claude/p309-r2-hardening-20261005", "claude/p309-r2-adoption-candidate-20261005"
block = block.replace("@PHASE@", phase).replace("@BRANCH@", branch).replace("@RUN@", RUN).replace("@NS2@", NS2)
p.write_text(s[:a] + block + "\n" + s[b:])

v = hooks / "tests" / "guard_vectors.json"
lines = v.read_text().replace(other, branch).split("\n")
RUNLINE = NS2 + "code/" + RUN


def edit_vec(vid, rel):
    return (f'  {{"id": "{vid}", "rule": "R5_PROTECTED_WRITE", "tool": "Edit", "file": "{rel}", "old": "a", '
            f'"new": "b"}},')


W23 = ('  {"id": "W23", "rule": "R5_PROTECTED_WRITE", "tool": "Write", "file": '
       f'"{NS2}governance/R2_REPIN_LIST_SUPPLEMENT_4.json", "content": "{{}}"}},')
P25 = f'  {{"id": "P25", "tool": "Write", "file": "{NS2}governance/R2_REPIN_LIST_SUPPLEMENT_5.json", "content": "{{}}"}}'
lines = [l for l in lines if not l.lstrip().startswith(('{"id": "W23"', '{"id": "P25"'))]
hit = [k for k, l in enumerate(lines) if (l.lstrip().startswith('{"id": "W22"') and RUNLINE in l)
       or l.lstrip().startswith('{"id": "W24"')]
assert len(hit) == 1, hit
k24 = [k for k, l in enumerate(lines) if l.lstrip().startswith('{"id": "P24"')][0]
assert lines[k24 + 1].strip() == "]"
if phase == "a":
    lines[hit[0]] = edit_vec("W24", NS2 + "code/" + DRILL)
    lines.insert(hit[0] + 1, W23)
    k24 += 1
    lines[k24] = lines[k24].rstrip().rstrip(",") + ","
    lines.insert(k24 + 1, P25)
else:
    lines[hit[0]] = edit_vec("W24", RUNLINE)
    lines[k24] = lines[k24].rstrip().rstrip(",")
t = "\n".join(lines)
d = json.loads(t)
ids = [c["id"] for c in d["deny"] + d["allow"]]
dup = sorted({i for i in ids if ids.count(i) > 1})
v.write_text(t)
print("ok", phase, len(d["deny"]), len(d["allow"]), "duplicate ids:", dup)
