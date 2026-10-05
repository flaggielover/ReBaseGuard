"""Task 7 (the owner's message-5 sequence): re-scope a COPY of the session guard, one phase at a time.

usage: rescope_t7.py <hooks dir of the copy> r2|sf1a|c [--sf1a-base COMMIT]
  r2   steps 2-4 (H-A, AF-3): the only branch is r2 itself, claude/p5y-k5-cell309-p309-r2. The guard admits exactly
       `git checkout -b <r2> a119e978` (the local branch is created only at the formally accepted candidate) and
       `git push -u origin <r2>` (git refuses a non-fast-forward). A commit on r2 may contain ONLY the named NEW
       governance files of AF-3; no code, no existing record. The runner and every other r2 file are protected.
  sf1a step 5: the SF1-A branch, created only from the r2 governance commit given with --sf1a-base; a commit may
       contain only the runner.
  c    the records go back to the hardening branch; no r2 file is writable.
Vectors: push vectors name the phase's branch; H41 always pushes to r1 (refused); W24 guards a file that is protected
in the phase; W23 keeps an earlier repin supplement protected; P25 admits a file that is writable in the phase.
"""
import json
import sys
from pathlib import Path

hooks, phase = Path(sys.argv[1]), sys.argv[2]
base = sys.argv[sys.argv.index("--sf1a-base") + 1] if "--sf1a-base" in sys.argv else None
RUN, DRILL = "p309_" + "qualify.py", "p309_" + "topology_drill.py"
NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
R2B, HB, CB = "claude/p5y-k5-cell309-p309-r2", "claude/p309-r2-hardening-20261005", "claude/p309-r2-adoption-candidate-20261005"
SB, R1B = "claude/p309-r2-sf1a-20261005", "claude/p5y-k5-cell309-p309-r1"
CAND = "a119e9789e2a1d42b584fff8a2301946a37f1bcb"
GOV = ["BRIEF_R2_DELTA_FOLLOWUP_5.md", "REVIEW_R2_DELTA_FOLLOWUP_5.md", "REVIEW_R2_DELTA_FOLLOWUP_5.sha256",
       "REVIEW_R2_DELTA_FOLLOWUP_5_EXEC_LEDGER.jsonl", "R2_DELTA_FOLLOWUP_5_RECORD.md",
       "OWNER_DECISIONS_R2_MSG5_VERBATIM.md", "OWNER_DECISIONS_R2_RECORD_1.json",
       "R2_DEVELOPMENT_HISTORY_SUPPLEMENT_1.md", "R2_INCORPORATION_RECORD_C1.json"]
if phase == "r2":
    branch, start = R2B, CAND
    write = "R2_GOV_NEW"
    commit = "R2_GOV_NEW"
elif phase == "sf1a":
    assert base and len(base) == 40, "--sf1a-base <40-hex r2 governance commit> is required"
    branch, start = SB, base
    write = "(R2_RUNNER,)"
    commit = "(R2_RUNNER,)"
elif phase == "c":
    branch, start = HB, "101ef2cb17e5eab2892212178278da45b98004ed"
    write = "()"
    commit = "None"
else:
    raise SystemExit("phase must be r2, sf1a or c")
p = hooks / "p309_guard_policy.py"
s = p.read_text()
a = min(s.index(x) for x in ("# Task 4 (S1-S3 follow-up", "# Task 7 (owner message 5") if x in s)
b = s.index("# files under these prefixes may name prohibited identifiers as data")
gov = ",\n              ".join(f'R2_GOV + "{g}"' for g in GOV)
block = f'''# Task 7 (owner message 5: H-A, AF-3, SF1-A; 2026-10-05), phase {phase}.  The only branch this session may commit to
# or push.  `git checkout -b ALLOWED_BRANCH R2_HEAD` creates it only at R2_HEAD; a push is never forced.
ALLOWED_BRANCH = "{branch}"
R2_HEAD = "{start}"
KNOWN_BRANCHES = ("claude/p309-q11-recovery-20261005", "{HB}", "{CB}", "{R2B}", "{SB}")
ALLOWED_REMOTE = "origin"
BASE_COMMIT = "101ef2cb17e5eab2892212178278da45b98004ed"        # r2 before the owner's H-A fast-forward

NEW_NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/"
R2_RUNNER = "{NS2}code/{RUN}"
R2_GOV = "{NS2}governance/"
# AF-3: the NEW, additive governance files of the separate governance-only commit on r2 (no existing record changes)
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
        for name in (HB, CB, SB, R2B):
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
protected = {"r2": NS2 + "code/" + RUN, "sf1a": NS2 + "code/" + DRILL, "c": NS2 + "code/" + RUN}[phase]
lines.insert(w21 + 1, vec("W24", "R5_PROTECTED_WRITE", "Edit", protected) + ",")
lines.insert(w21 + 2, vec("W23", "R5_PROTECTED_WRITE", "Write", NS2 + "governance/R2_REPIN_LIST_SUPPLEMENT_4.json") + ",")
k24 = [k for k, l in enumerate(lines) if l.lstrip().startswith('{"id": "P24"')][0]
assert lines[k24 + 1].strip() == "]"
allowed = {"r2": ("Write", NS2 + "governance/" + GOV[5]), "sf1a": ("Edit", NS2 + "code/" + RUN), "c": None}[phase]
lines[k24] = lines[k24].rstrip().rstrip(",") + ("," if allowed else "")
if allowed:
    lines.insert(k24 + 1, vec("P25", None, allowed[0], allowed[1], allow=True))
t = "\n".join(lines)
d = json.loads(t)
ids = [c["id"] for c in d["deny"] + d["allow"]]
dup = sorted({i for i in ids if ids.count(i) > 1})
v.write_text(t)
stale = [n for n in (HB, CB, SB, R2B) if n != branch and any(n in json.dumps(c) for c in d["deny"] + d["allow"]
                                                              if c["id"] != "H41")]
print("ok", phase, branch, "deny", len(d["deny"]), "allow", len(d["allow"]), "dup", dup, "stale branch names", stale)
