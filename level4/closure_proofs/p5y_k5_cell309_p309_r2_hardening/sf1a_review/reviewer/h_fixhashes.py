"""Replace abbreviated evidence hashes in the review table with full recomputed values; then scan the review for the
unresolved-marker and choice patterns (patterns copied, no p309 module imported)."""
import hashlib
import re
import subprocess
from pathlib import Path

W = Path("/tmp/claude-0/-home-user-ReBaseGuard/ede4e097-f9ec-54f5-9e84-81294f8ad688/scratchpad/t7/sf1a_review/work2")
R = W / "REVIEW_SF1A_DELTA.md"
EV = "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/sf1a_review/evidence/"
names = subprocess.run(["git", "-C", "/home/user/ReBaseGuard", "ls-tree", "-r", "--name-only", "b6efec42", "--", EV],
                       capture_output=True, text=True, check=True).stdout.split()
full = {}
for n in names:
    if "/rehearsal/attempt/" in n:
        continue
    raw = subprocess.run(["git", "-C", "/home/user/ReBaseGuard", "show", f"b6efec42:{n}"], capture_output=True,
                         check=True).stdout
    full[n[len(EV):]] = hashlib.sha256(raw).hexdigest()
text = R.read_text()
lines = text.split("\n")
fixed = 0
for i, ln in enumerate(lines):
    m = re.match(r"\| `([^`]+)` \| `([0-9a-f]{8})…[0-9a-f]+` \|", ln)
    if m and m.group(1) in full:
        assert full[m.group(1)].startswith(m.group(2)), (m.group(1), full[m.group(1)], m.group(2))
        lines[i] = re.sub(r"`[0-9a-f]{8}…[0-9a-f]+`", f"`{full[m.group(1)]}`", ln, count=1)
        fixed += 1
R.write_text("\n".join(lines))
print("rows fixed:", fixed, "of", len(full), "files")
MARKERS = re.compile(r"\bTBD\b|\bTODO\b|\bFIXME\b|\bXXX\b|<to be\b|to be decided|to be determined|\bplaceholder\b|"
                     r"\?\?\?|\bPENDING_DECISION\b|\bundecided\b|\bopen question\b", re.I)
CHOICE = re.compile(r"owner (decides|to decide|may choose)|may be chosen|at the coordinator's discretion|"
                    r"after (seeing|inspecting) the result|depending on the result", re.I)
t = R.read_text()
print("marker hits:", [m.group(0) for m in MARKERS.finditer(t)], "choice hits:", [m.group(0) for m in CHOICE.finditer(t)])
print("line 2:", repr(t.split("\n")[1]))
