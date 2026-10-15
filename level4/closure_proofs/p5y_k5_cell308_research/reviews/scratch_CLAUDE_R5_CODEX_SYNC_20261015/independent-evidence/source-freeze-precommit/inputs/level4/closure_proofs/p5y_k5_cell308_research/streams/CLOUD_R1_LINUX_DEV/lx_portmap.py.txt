"""Cell-308 new-host route (Claude Cloud, r1) -- read-only PORT MAP of the historical MB-S r1 candidate (DEV stream).

Reads every ``code/*.py`` and ``tests/*.py`` file of the candidate namespace at commit 142d97a9 through
``git show <commit>:<path>`` (nothing is checked out, imported, executed or modified) and lists each line that uses a
macOS-only facility, by category. The categories are the ones the PROPOSED amendment must replace or decide
(PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1.md section 3). A static scan cannot see dynamically built names; the map is a
checklist for reviewers, not a proof of completeness.

usage: python3 lx_portmap.py <repo> <out.json>
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

COMMIT = "142d97a90a1c3fafff394044aa1448674f7a633c"
CAND = "level4/closure_proofs/p5y_k5_cell308_mbs_r1"
CATEGORIES = {
    "LAUNCHD": r"launchctl|launchd|XPC_SERVICE_NAME|\.plist\b|LaunchAgents",
    "SLEEP_PREVENTION": r"caffeinate",
    "POWER_PMSET": r"\bpmset\b|AC Power|lowpowermode",
    "THERMAL": r"notifyutil|thermalpressurelevel|ThermalEvent",
    "MACOS_CLOCKS": r"CLOCK_UPTIME_RAW|CLOCK_MONOTONIC_RAW|kern\.(sleeptime|waketime)",
    "SYSCTL": r"\bsysctl\b|hw\.memsize|kern\.memorystatus|kern\.boot",
    "VM_STAT_MEMORY": r"vm_stat|wired down|speculative|purgeable",
    "PS_SEMANTICS": r"/bin/ps|\bpcpu\b|lstart",
    "SOFTWARE_UPDATE": r"SoftwareUpdate|/usr/bin/defaults|sw_vers",
    "FULLFSYNC": r"F_FULLFSYNC",
    "MACOS_PATHS": r"/Library/|/System/|/Applications/|/Users/|/usr/libexec/",
    "PLATFORM_PIN": r"PLATFORM_PINS|libpython|os_build",
}


def git(repo: str, *args: str) -> str:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout


def main(repo: str, out: str) -> int:
    files = [f for f in git(repo, "ls-tree", "-r", "--name-only", COMMIT, CAND).splitlines()
             if re.search(r"/(code|tests)/[^/]+\.py$", f)]
    rx = {k: re.compile(v) for k, v in CATEGORIES.items()}
    hits, per_cat = [], {k: 0 for k in CATEGORIES}
    for f in files:
        for i, ln in enumerate(git(repo, "show", f"{COMMIT}:{f}").splitlines(), 1):
            cats = [k for k, r in rx.items() if r.search(ln)]
            if cats:
                for k in cats:
                    per_cat[k] += 1
                hits.append({"file": f[len(CAND) + 1:], "line": i, "categories": cats, "text": ln.strip()[:160]})
    per_file = {}
    for h in hits:
        per_file[h["file"]] = per_file.get(h["file"], 0) + 1
    rec = {"schema": "rebaseguard.p5y.k5.newhost-cloud-r1.portmap.v1", "class": "INFRASTRUCTURE",
           "candidate_commit": COMMIT, "files_scanned": len(files), "lines_flagged": len(hits),
           "per_category": per_cat, "per_file": dict(sorted(per_file.items())), "hits": hits,
           "limits": "regex scan of source text; dynamically built names and transitive platform behaviour "
                     "(e.g. RSS semantics of a portable call) are not detected"}
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=1)
        fh.write("\n")
    print(json.dumps({k: rec[k] for k in ("files_scanned", "lines_flagged", "per_category", "per_file")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
