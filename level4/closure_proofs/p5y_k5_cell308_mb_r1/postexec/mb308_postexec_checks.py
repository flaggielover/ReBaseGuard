"""Cell-308 MB campaign (r1) -- post-interruption repository checks (review REVIEW_EXECUTION_INTERRUPTION C4).

Read-only: stdlib and git plumbing only (GIT_OPTIONAL_LOCKS=0). It imports no campaign module (no mb308_*), loads no
pinned certifier, never arms the guard, never runs the driver, never reads the content of any git object written after
the marker, and writes only its own --out JSON. It never evaluates anything.

    python3.14 -I -S -B mb308_postexec_checks.py --out FILE
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
NS_REL = "level4/closure_proofs/p5y_k5_cell308_mb_r1"
PREFIX = "refs/p5y-k5-cell308-mb-r1/"
MARKER = PREFIX + "target-consumed"
PENDING = PREFIX + "pending-result"
EMERGENCY_NAME = "mb308-cell308-emergency-result.json"
GRANT = "afa930727d084a5b70e6b85d30ca8f34c0e8ae74"
CHAIN = {"freeze": "c46434a399eca18a709616a4a4d51918d1a30298", "qualification": "7eb057bbbcb3c8d18afc852c1d90f0b3fc0fefc8",
         "qualification_review": "47bb37c724841c6a8d53bc89eba28765609598ea", "grant": GRANT}
PROBES = {"a1995184cdbcf51f5e1885873958a5168fbd5f69": ("blob", 31), "501388e2a1c285bc4a71524be79e36ddc1a1a8c5": ("commit", 253)}
PROBE_BYTES = b"mb308 object-store write probe\n"          # the frozen driver's check_seal_preconditions probe
GUARDED = ("evidence", "evidence/execution", "evidence/execution/MB308_CELL308_RESULT.json",
           "evidence/execution/MB308_CELL308_RESULT.tmp", "evidence/execution/MB308_CELL308_RESULT.json.tmp",
           "evidence/execution/MB308_CELL308_RESULT.partial")
ENV = {"PATH": "/usr/bin:/bin:/usr/sbin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0"}


def git(*a) -> subprocess.CompletedProcess:
    return subprocess.run(["/usr/bin/git", "-C", str(REPO), *a], capture_output=True, text=True, env=ENV,
                          stdin=subprocess.DEVNULL)


def out(*a) -> str:
    return git(*a).stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    c = {}
    refs = out("for-each-ref", "--format=%(refname) %(objectname)", PREFIX).splitlines()
    c["1_marker"] = {"refs_under_prefix": refs, "exactly_one_ref": len(refs) == 1,
                     "marker_names_grant": out("rev-parse", "-q", "--verify", MARKER) == GRANT}
    common = Path(out("rev-parse", "--path-format=absolute", "--git-common-dir"))
    gd = Path(out("rev-parse", "--path-format=absolute", "--git-dir"))
    mfile = common / MARKER
    marker_mtime = int(mfile.stat().st_mtime) if mfile.exists() else None
    c["1_marker"]["ref_file_mtime_epoch"] = marker_mtime
    c["2_no_persisted_evidence"] = {
        "pending_ref_absent": git("rev-parse", "-q", "--verify", PENDING).returncode != 0,
        "emergency_file_absent": not os.path.lexists(gd / EMERGENCY_NAME),
        "guarded_paths_absent": {p: not os.path.lexists(REPO / NS_REL / p) for p in GUARDED},
        "result_path_not_in_any_commit": out("log", "--all", "--format=%H", "--", NS_REL + "/evidence") == ""}
    boot = subprocess.run(["/usr/sbin/sysctl", "-n", "kern.boottime"], capture_output=True, text=True, env=ENV).stdout
    m = re.search(r"sec = (\d+)", boot)
    boot_epoch = int(m.group(1)) if m else None
    written = []
    if marker_mtime and boot_epoch:
        for p in (common / "objects").glob("??/*"):
            t = p.stat().st_mtime
            if marker_mtime - 5 <= t <= boot_epoch:
                oid = p.parent.name + p.name
                written.append({"oid": oid, "type": out("cat-file", "-t", oid), "size": out("cat-file", "-s", oid),
                                "mtime_epoch": int(t)})
        packs = [str(p.name) for p in (common / "objects" / "pack").glob("*") if marker_mtime - 5 <= p.stat().st_mtime
                 <= boot_epoch]
    else:
        packs = None
    probe_id = hashlib.sha1(b"blob %d\0" % len(PROBE_BYTES) + PROBE_BYTES).hexdigest()
    after_marker = [w for w in written if w["mtime_epoch"] > marker_mtime] if marker_mtime else None
    c["3_object_store_marker_to_boot"] = {
        "boot_epoch": boot_epoch, "objects_in_window_incl_5s_before_marker": written, "packs_in_window": packs,
        "objects_strictly_after_marker": after_marker,
        "no_object_after_marker": after_marker == [] and packs == [],
        "probe_blob_id_recomputed_from_frozen_bytes": probe_id,
        "window_objects_are_exactly_the_probes": {w["oid"] for w in written} <= set(PROBES) and all(
            (w["type"], int(w["size"])) == PROBES[w["oid"]] for w in written) and probe_id in PROBES}
    c["4_chain_unchanged"] = {k: out("rev-parse", "-q", "--verify", v + "^{commit}") == v for k, v in CHAIN.items()}
    c["4_chain_unchanged"]["parents"] = (out("rev-parse", GRANT + "^") == CHAIN["qualification_review"]
                                         and out("rev-parse", CHAIN["qualification_review"] + "^") == CHAIN["qualification"]
                                         and out("rev-parse", CHAIN["qualification"] + "^") == CHAIN["freeze"])
    man = json.loads(out("show", f"{GRANT}:{NS_REL}/protocol/MB308_FREEZE.json"))
    bad = [rel for rel, v in man["frozen_files"].items()
           if not (REPO / rel).exists() or hashlib.sha256((REPO / rel).read_bytes()).hexdigest() != v["sha256"]]
    c["5_frozen_files_match_manifest_at_grant"] = {"files": len(man["frozen_files"]), "mismatches": bad}
    c["6_no_mb308_process"] = subprocess.run(["/usr/bin/pgrep", "-f", "mb308_driver.py execute"], capture_output=True,
                                             env=ENV).returncode != 0
    ok = (c["1_marker"]["exactly_one_ref"] and c["1_marker"]["marker_names_grant"]
          and all(v for k, v in c["2_no_persisted_evidence"].items() if k != "guarded_paths_absent")
          and all(c["2_no_persisted_evidence"]["guarded_paths_absent"].values())
          and c["3_object_store_marker_to_boot"]["no_object_after_marker"]
          and c["3_object_store_marker_to_boot"]["window_objects_are_exactly_the_probes"]
          and all(v for v in c["4_chain_unchanged"].values()) and not bad and c["6_no_mb308_process"])
    rep = {"schema": "rebaseguard.p5y.k5.cell308-mb-r1.postexec-checks.v1", "checks": c, "all_hold": ok,
           "frozen_outcome": "CELL308_EXECUTION_INDETERMINATE", "target_evaluations": 1,
           "note": "repository facts only; no target value exists or was read; no seal, no exit code"}
    Path(a.out).write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(f"MB308 POSTEXEC CHECKS: all_hold={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
