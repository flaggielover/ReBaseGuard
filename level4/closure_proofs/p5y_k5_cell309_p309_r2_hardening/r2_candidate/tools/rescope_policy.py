"""Re-scope the scratch copy of the session guard for task 3 (adoption candidate)."""
import sys
from pathlib import Path

hooks = Path(sys.argv[1])
RUNNER = "p309_" + "qualify.py"
DRILL = "p309_" + "topology_drill.py"
p = hooks / "p309_guard_policy.py"
s = p.read_text()
a = s.index("# Task 2 (r2 qualification hardening")
b = s.index("# --------------------------------------------------------------------------------------------------- patterns")
new = '''# Task 3 (minimal r2 adoption candidate, 2026-10-05).  The only branch this session may commit to or push; it is
# created once from r2's head R2_HEAD (the guard admits exactly `git checkout -b ALLOWED_BRANCH R2_HEAD`).
ALLOWED_BRANCH = "claude/p309-r2-adoption-candidate-20261005"
R2_HEAD = "101ef2cb17e5eab2892212178278da45b98004ed"
# branches the session repository may be on (the finished task-1 and task-2 branches, read only, and this one)
KNOWN_BRANCHES = ("claude/p309-q11-recovery-20261005", "claude/p309-r2-hardening-20261005", ALLOWED_BRANCH)
ALLOWED_REMOTE = "origin"
BASE_COMMIT = R2_HEAD                                           # the branch point of ALLOWED_BRANCH

# the write-set (working tree): the two r2 files of the adoption candidate, the task-2 hardening namespace (drafts of
# this task's reports, never committed to ALLOWED_BRANCH) and the guard itself.  Everything else is protected.
NEW_NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/"
R2_RUNNER = "level4/closure_proofs/p5y_k5_cell309_p309_r2/code/@RUNNER@"
R2_DRILL = "level4/closure_proofs/p5y_k5_cell309_p309_r2/code/@DRILL@"
WRITE_ALLOW = (NEW_NS, R2_RUNNER, R2_DRILL, ".claude/hooks/", ".claude/settings.json", ".claude/audit/",
               ".claude/.gitignore")
# the commit-set: a commit on ALLOWED_BRANCH may contain these two r2 files and nothing else (the adoption candidate
# carries no .claude/**, no hardening namespace, no evidence and no documentation)
COMMIT_ALLOW = (R2_RUNNER, R2_DRILL)
# files under these prefixes may name prohibited identifiers as data (the guard's own rules and test vectors)
CONTENT_SCAN_EXEMPT = (".claude/hooks/",)

'''.replace("@RUNNER@", RUNNER).replace("@DRILL@", DRILL)
p.write_text(s[:a] + new + s[b:])

g = hooks / "p309_pretooluse_guard.py"
t = g.read_text()
anchor = '''        bad = sorted({s for s in staged if s and not in_write_set(s)})
        if bad:
            raise Refuse("R5_PROTECTED_WRITE", f"the commit would touch protected paths: {bad[:5]}")
'''
assert t.count(anchor) == 1
t = t.replace(anchor, anchor + '''        commit_allow = getattr(P, "COMMIT_ALLOW", None)
        if commit_allow is not None:
            extra = sorted({s for s in staged if s and s.replace(os.sep, "/") not in commit_allow})
            if extra:
                raise Refuse("R5_PROTECTED_WRITE", f"the commit may contain only {list(commit_allow)}: {extra[:5]}")
''')
g.write_text(t)

v = hooks / "tests" / "guard_vectors.json"
v.write_text(v.read_text().replace("claude/p309-r2-hardening-20261005", "claude/p309-r2-adoption-candidate-20261005"))
print("ok")
