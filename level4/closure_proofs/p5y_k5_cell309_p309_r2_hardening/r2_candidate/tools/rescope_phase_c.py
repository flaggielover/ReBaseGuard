"""Task 3 phase C: re-scope a COPY of the session guard so the deliverables can be committed on the task-2 branch.

usage: rescope_phase_c.py <hooks dir of the copy>
ALLOWED_BRANCH -> the task-2 hardening branch (already in KNOWN_BRANCHES); the write-set narrows to the hardening
namespace and the guard itself (no r2 file is writable any more); COMMIT_ALLOW is dropped (the commit-set is the
write-set).  Test vectors follow: push vectors name the hardening branch; P23 (an r2 runner edit, allowed while the
runner was in the write-set) becomes a refusal W22, and P23 edits a hardening-namespace file instead.
"""
import json
import sys
from pathlib import Path

hooks = Path(sys.argv[1])
p = hooks / "p309_guard_policy.py"
s = p.read_text()
rep = [
    ('ALLOWED_BRANCH = "claude/p309-r2-adoption-candidate-20261005"',
     'ALLOWED_BRANCH = "claude/p309-r2-hardening-20261005"   # task 3 phase C: the reports go here, not on the candidate'),
    ('KNOWN_BRANCHES = ("claude/p309-q11-recovery-20261005", "claude/p309-r2-hardening-20261005", ALLOWED_BRANCH)',
     'KNOWN_BRANCHES = ("claude/p309-q11-recovery-20261005", ALLOWED_BRANCH,\n'
     '                  "claude/p309-r2-adoption-candidate-20261005")'),
    ('WRITE_ALLOW = (NEW_NS, R2_RUNNER, R2_DRILL, R2_ALLOWANCE, ".claude/hooks/", ".claude/settings.json",\n'
     '               ".claude/audit/", ".claude/.gitignore")',
     '# phase C: the candidate is committed and pushed; no r2 file is writable any more\n'
     'WRITE_ALLOW = (NEW_NS, ".claude/hooks/", ".claude/settings.json", ".claude/audit/", ".claude/.gitignore")'),
    ('COMMIT_ALLOW = (R2_RUNNER, R2_DRILL, R2_ALLOWANCE)',
     'COMMIT_ALLOW = None                                             # phase C: the commit-set is the write-set'),
]
for a, b in rep:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
p.write_text(s)

v = hooks / "tests" / "guard_vectors.json"
t = v.read_text().replace("claude/p309-r2-adoption-candidate-20261005", "claude/p309-r2-hardening-20261005")
old = ('{"id": "P23", "tool": "Edit", "file": "level4/closure_proofs/p5y_k5_cell309_p309_r2/code/p309_' + 'qualify.py", '
       '"old": "a", "new": "b"}')
assert t.count(old) == 1
new = ('{"id": "P23", "tool": "Edit", "file": "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/r2_candidate/x.md", '
       '"old": "a", "new": "b"}')
t = t.replace(old, new)
lines = t.split("\n")
i = [k for k, l in enumerate(lines) if l.lstrip().startswith('{"id": "W21"')]
assert len(i) == 1 and lines[i[0]].rstrip().endswith("},")
lines.insert(i[0] + 1, '  {"id": "W22", "rule": "R5_PROTECTED_WRITE", "tool": "Edit", '
                       '"file": "level4/closure_proofs/p5y_k5_cell309_p309_r2/code/p309_' + 'qualify.py", "old": "a", '
                       '"new": "b"},')
t = "\n".join(lines)
d = json.loads(t)
assert len(d["deny"]) == 125 and len(d["allow"]) == 24
v.write_text(t)
print("ok")
