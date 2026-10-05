"""Task 8 (the owner's message 6: SF1-A incorporation): re-scope a COPY of the session guard, one phase at a time.

usage: rescope_t8.py <hooks dir of the copy> sfco|ff|gov|push|c
  sfco the only branch is the SF1-A branch (local, at 716946e8): the guard admits `git checkout <sf1a>`; no r2 file
       is writable (none is committed).
  ff   the incorporation step: the only push target is r2, as `git push -u origin HEAD:refs/heads/<r2>` with HEAD on the
       SF1-A branch at 716946e8 (git refuses a non-fast-forward; a push is never forced); HEAD is not on the allowed
       branch, so no commit is possible; no r2 file writable.
  gov  the separate governance-only filing: the only branch is a LOCAL filing branch, created only at 716946e8
       (`git checkout -b <filing> 716946e8`); a commit may contain ONLY the named NEW SF1-A governance files; no
       code, no existing record; the filing branch is never pushed under its own name.
  push the filing commit goes to r2 as `git push -u origin HEAD:refs/heads/<r2>` (a fast-forward from 716946e8); HEAD
       is not on the allowed branch, so no commit is possible; no r2 file writable.
  c    the records go back to the hardening branch; no r2 file is writable.
Vectors: push vectors name the phase's branch; H41 always pushes to r1 (refused); W24 guards a file that is protected
in the phase; W23 keeps an earlier repin supplement protected; P25 admits a file that is writable in the phase.
"""
import json
import sys
from pathlib import Path

hooks, phase = Path(sys.argv[1]), sys.argv[2]
RUN, DRILL = "p309_" + "qualify.py", "p309_" + "topology_drill.py"
NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
R2B, HB, CB = "claude/p5y-k5-cell309-p309-r2", "claude/p309-r2-hardening-20261005", "claude/p309-r2-adoption-candidate-20261005"
SB, R1B = "claude/p309-r2-sf1a-20261005", "claude/p5y-k5-cell309-p309-r1"
FB = "claude/p309-r2-sf1a-filing-20261005"
OLD, NEW = "b66a45f097989764176075802c953df4b72c2aef", "716946e8d9a6744d0b49de6acc802605b6eb1bf8"
CAND = "a119e9789e2a1d42b584fff8a2301946a37f1bcb"
GOV = ["BRIEF_SF1A_DELTA_REVIEW.md", "REVIEW_SF1A_DELTA.md", "REVIEW_SF1A_DELTA.sha256",
       "REVIEW_SF1A_DELTA_EXEC_LEDGER.jsonl", "OWNER_DECISIONS_R2_MSG6_VERBATIM.md", "R2_SF1A_INCORPORATION_RECORD.json"]
# COMMIT_ALLOW None (as in phase c): no r2 file is in the write-set; in ff and push HEAD is never on ALLOWED_BRANCH,
# so the guard refuses every commit there (CM4).
PH = {"sfco": (SB, OLD, "()", "None"), "ff": (R2B, NEW, "()", "None"), "gov": (FB, NEW, "R2_GOV_NEW", "R2_GOV_NEW"),
      "push": (R2B, NEW, "()", "None"), "c": (HB, "101ef2cb17e5eab2892212178278da45b98004ed", "()", "None")}
if phase not in PH:
    raise SystemExit("phase must be one of " + ", ".join(PH))
branch, start, write, commit = PH[phase]
p = hooks / "p309_guard_policy.py"
s = p.read_text()
a = min(s.index(x) for x in ("# Task 4 (S1-S3 follow-up", "# Task 7 (owner message 5", "# Task 8 (owner message 6") if x in s)
b = s.index("# files under these prefixes may name prohibited identifiers as data")
gov = ",\n              ".join(f'R2_GOV + "{g}"' for g in GOV)
block = f'''# Task 8 (owner message 6: SF1-A incorporation b66a45f0 -> 716946e8, then one governance-only commit; 2026-10-05),
# phase {phase}.  The only branch this session may commit to or push.  `git checkout -b ALLOWED_BRANCH R2_HEAD` creates
# it only at R2_HEAD; a push is never forced.
ALLOWED_BRANCH = "{branch}"
R2_HEAD = "{start}"
KNOWN_BRANCHES = ("claude/p309-q11-recovery-20261005", "{HB}", "{CB}", "{R2B}", "{SB}", "{FB}")
ALLOWED_REMOTE = "origin"
BASE_COMMIT = "{OLD}"        # r2 before the owner's SF1-A incorporation

NEW_NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/"
R2_RUNNER = "{NS2}code/{RUN}"
R2_GOV = "{NS2}governance/"
# message 6: the NEW, additive SF1-A governance files of the separate governance-only commit (no existing record changes)
R2_GOV_NEW = ({gov})
WRITE_ALLOW = (NEW_NS, ".claude/hooks/", ".claude/settings.json", ".claude/audit/", ".claude/.gitignore") + tuple({write})
COMMIT_ALLOW = {commit}

'''
p.write_text(s[:a] + block + s[b:])

v = hooks / "tests" / "guard_vectors.json"
lines = v.read_text().split("\n")
out = []
for l in lines:
    st = l.lstrip()
    if st.startswith(('{"id": "W23"', '{"id": "P25"', '{"id": "W24"')):
        continue
    if st.startswith('{"id": "H41"'):
        l = f'  {{"id": "H41", "rule": "R3_PUSH_TARGET", "cmd": "git push origin {branch}:{R1B}"}},'
    elif st.startswith('{"id": "H10"'):      # was: a push to r2 is refused; r2 is the owner-authorized target now
        l = f'  {{"id": "H10", "rule": "R3_PUSH_TARGET", "cmd": "git push origin {R1B}"}},'
    elif st.startswith('{"id": "H39"'):      # was: a checkout of r2 is refused; r1 stays refused in every phase
        l = f'  {{"id": "H39", "rule": "R3_HISTORY", "cmd": "git checkout {R1B}"}},'
    else:
        for name in (HB, CB, SB, R2B, FB):
            if name != branch and name in l and '"id": "H' in l or (name != branch and name in l and '"id": "P' in l):
                l = l.replace(name, branch)
    out.append(l)
lines = out


def vec(vid, rule, tool, rel, allow=False):
    if tool == "Edit":
        body = f'"tool": "Edit", "file": "{rel}", "old": "a", "new": "b"'
    else:
        body = f'"tool": "Write", "file": "{rel}", "content": "{{}}"'
    return f'  {{"id": "{vid}", ' + ("" if allow else f'"rule": "{rule}", ') + body + "}"


w21 = [k for k, l in enumerate(lines) if l.lstrip().startswith('{"id": "W21"')][0]
protected = NS2 + "code/" + RUN
lines.insert(w21 + 1, vec("W24", "R5_PROTECTED_WRITE", "Edit", protected) + ",")
lines.insert(w21 + 2, vec("W23", "R5_PROTECTED_WRITE", "Write", NS2 + "governance/R2_REPIN_LIST_SUPPLEMENT_4.json") + ",")
k24 = [k for k, l in enumerate(lines) if l.lstrip().startswith('{"id": "P24"')][0]
assert lines[k24 + 1].strip() == "]"
allowed = ("Write", NS2 + "governance/" + GOV[4]) if phase == "gov" else None
lines[k24] = lines[k24].rstrip().rstrip(",") + ("," if allowed else "")
if allowed:
    lines.insert(k24 + 1, vec("P25", None, allowed[0], allowed[1], allow=True))
t = "\n".join(lines)
d = json.loads(t)
ids = [c["id"] for c in d["deny"] + d["allow"]]
dup = sorted({i for i in ids if ids.count(i) > 1})
v.write_text(t)
stale = [n for n in (HB, CB, SB, R2B, FB) if n != branch and any(n in json.dumps(c) for c in d["deny"] + d["allow"]
                                                              if c["id"] != "H41")]
print("ok", phase, branch, "deny", len(d["deny"]), "allow", len(d["allow"]), "dup", dup, "stale branch names", stale)
