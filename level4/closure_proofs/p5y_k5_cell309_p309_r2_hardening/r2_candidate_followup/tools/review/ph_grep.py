"""static placeholder grep over the delta (same regexes as code/p309_placeholder_check.py; no freeze needed)"""
import re
import subprocess

REPO = "/home/user/ReBaseGuard"
NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
MARKERS = re.compile(r"\bTBD\b|\bTODO\b|\bFIXME\b|\bXXX\b|<to be\b|to be decided|to be determined|\bplaceholder\b|"
                     r"\?\?\?|\bPENDING_DECISION\b|\bundecided\b|\bopen question\b", re.I)
CHOICE = re.compile(r"owner (decides|to decide|may choose)|may be chosen|at the coordinator's discretion|"
                    r"after (seeing|inspecting) the result|depending on the result", re.I)
for rel in ("code/p309_" + "qualify.py", "governance/R2_REPIN_LIST_SUPPLEMENT_5.json"):
    for rev in ("93d55063", "a119e978"):
        try:
            txt = subprocess.run(["git", "-C", REPO, "show", f"{rev}:{NS}{rel}"], capture_output=True, text=True,
                                 check=True).stdout
        except subprocess.CalledProcessError:
            print(rev, rel, "absent")
            continue
        hits = [(i + 1, l.strip()[:120]) for i, l in enumerate(txt.splitlines()) if MARKERS.search(l) or CHOICE.search(l)]
        print(rev, rel, "hits:", len(hits), hits[:5])
diff = subprocess.run(["git", "-C", REPO, "diff", "93d55063", "a119e978"], capture_output=True, text=True).stdout
added = [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
print("added lines:", len(added), "marker hits:", [l for l in added if MARKERS.search(l) or CHOICE.search(l)])
