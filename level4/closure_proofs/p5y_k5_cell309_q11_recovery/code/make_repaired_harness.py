#!/usr/bin/env python3
"""Derive the repaired QC11 harness for the r1 rehearsal mechanically from r2's reviewed file (no new logic).

  python3 make_repaired_harness.py [--check]

Inputs (git blobs, read-only):
  r1 frozen harness  c902fe2f:level4/closure_proofs/p5y_k5_cell309_p309_r1/tests/test_p309_exactly_once.py
  r2 repaired harness 101ef2cb:level4/closure_proofs/p5y_k5_cell309_p309_r2/tests/test_p309_exactly_once.py
Mapping: r2 names -> r1 names; the two r2-only infrastructure lines (P7 scratch root, the r2 forbidden-namespace
tuple) are reverted to r1's.  The output is DATA (.py.txt): the rehearsal tool copies it over the replica's harness
for QC11 / QC-D5 only.  The unified diff against the frozen r1 harness is written beside it, and the run refuses
unless every changed line belongs to the reviewed repair (r2 plan section 4; review P6 (a), (b), (c)).
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
R1_COMMIT, R2_COMMIT = "c902fe2fe33003ac7e4e61f29c10c81682fc940c", "101ef2cb17e5eab2892212178278da45b98004ed"
R1_REL = "level4/closure_proofs/p5y_k5_cell309_p309_r1/tests/test_p309_exactly_once.py"
R2_REL = "level4/closure_proofs/p5y_k5_cell309_p309_r2/tests/test_p309_exactly_once.py"
OUT = NS / "repair" / "test_p309_exactly_once.R2_PORTED_TO_R1.py.txt"
DIFF = NS / "repair" / "QC11_HARNESS_REPAIR.diff"
META = NS / "repair" / "QC11_HARNESS_REPAIR.json"

R2_ONLY = [
    ("import p309_env as E  # noqa: E402  (r2 P7: scratch_dir)\n", ""),
    ('SCRATCH = E.scratch_dir("qc11_sandboxes")   # r2 P7: under P309_SCRATCH_ROOT (validated; no fallback)\n',
     'SCRATCH = Path("/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/'
     'qc11_sandboxes")\n'),
    ("G._FORBIDDEN_NAMESPACES", "G._PROD_NAMESPACE"),
]
# every line the repair may remove from r1, and a marker that every added line must carry or belong to
REMOVED_OK = {
    '    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True,',
    "                          check=True).stdout.strip()",
    "    man = (REPO / D.MANIFEST_REL).read_bytes()",
    '        R[name] = {"pass": (out == ("REFUSED", code) and before == after and nonce_ok',
    '                   "got": str(out)}',
    '        R[name] = {"pass": out == ("REFUSED", code) and refs(sb) == before and G.TEST_MARKER not in refs(sb),',
}
ADDED_TOKENS = ("sandbox_base", "manifest_bytes", "P6", "LAST_REFUSAL", "detail_ok", "FREEZE_RECORD_DETAIL",
                "freeze-record commits", "hist(", "post-freeze", "development", "want =", "have =", "if have != want",
                "raise RuntimeError", "return base, mode", "base, mode", "F14_", "F16_", "A23_", "A24_", "A25_",
                "a frozen directory changed", "no freeze record", "the record commit is not", "the freeze record was",
                "def hist", "capture_output=True", "check=True", "head = subprocess.run", "if not hist(head)",
                "else:", "try:", "except D.Refusal", "if hist(base)", "if mode ==", "return subprocess.run",
                "return (REPO / D.MANIFEST_REL)", "R[name] = {", '"got": str(out), "detail"', "and detail_ok",
                "}", '"""', "* development", "* post-freeze", "Precondition", "record commits", "flow builds",
                "it.  A malformed", "it validates", "\"HEAD\"", "more: the real record", "# r2 P6", "def ")


def blob(commit: str, rel: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), "show", f"{commit}:{rel}"], capture_output=True, text=True,
                          check=True).stdout


def build() -> tuple[str, str, dict]:
    r1, r2 = blob(R1_COMMIT, R1_REL), blob(R2_COMMIT, R2_REL)
    port = r2.replace("p309_r2", "p309_r1").replace("p309-r2", "p309-r1")
    for old, new in R2_ONLY:
        if old not in port:
            raise SystemExit(f"r2 file does not contain the expected r2-only text: {old[:60]!r}")
        port = port.replace(old, new)
    diff = "".join(difflib.unified_diff(r1.splitlines(True), port.splitlines(True), "r1-frozen/" + R1_REL,
                                        "r2-repair-ported/" + R1_REL, n=2))
    removed = [l[1:].rstrip("\n") for l in diff.splitlines(True) if l.startswith("-") and not l.startswith("---")]
    added = [l[1:].rstrip("\n") for l in diff.splitlines(True) if l.startswith("+") and not l.startswith("+++")]
    bad_removed = [l for l in removed if l not in REMOVED_OK]
    bad_added = [l for l in added if l.strip() and not any(t in l for t in ADDED_TOKENS) and not l.strip().startswith("#")]
    meta = {"schema": "P309_QC11_HARNESS_REPAIR/1", "r1_commit": R1_COMMIT, "r1_rel": R1_REL,
            "r1_sha256": hashlib.sha256(r1.encode()).hexdigest(), "r2_commit": R2_COMMIT, "r2_rel": R2_REL,
            "r2_sha256": hashlib.sha256(r2.encode()).hexdigest(),
            "ported_sha256": hashlib.sha256(port.encode()).hexdigest(),
            "diff_sha256": hashlib.sha256(diff.encode()).hexdigest(), "lines_removed": len(removed),
            "lines_added": len(added), "unexpected_removed": bad_removed, "unexpected_added": bad_added,
            "mapping": ["p309_r2 -> p309_r1", "p309-r2 -> p309-r1"] + [f"{o.strip()[:50]} -> {n.strip()[:50]}"
                                                                      for o, n in R2_ONLY],
            "repair_scope": "r2 plan section 4; review P6 (a) manifest from F post-freeze, (b) sandbox base = "
                            "recorded freeze F post-freeze + record-count postcondition, (c) FREEZE_RECORD detail"}
    return port, diff, meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    port, diff, meta = build()
    if meta["unexpected_removed"] or meta["unexpected_added"]:
        print(json.dumps({k: meta[k] for k in ("unexpected_removed", "unexpected_added")}, indent=1))
        print("REPAIR DERIVATION REFUSED: the diff contains lines outside the reviewed repair")
        return 1
    if a.check:
        ok = OUT.read_text() == port and DIFF.read_text() == diff
        print("REPAIRED HARNESS " + ("REGENERATES IDENTICALLY" if ok else "DIFFERS"))
        return 0 if ok else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(port)
    DIFF.write_text(diff)
    META.write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n")
    print(f"ported harness sha256 {meta['ported_sha256']}; diff -{meta['lines_removed']} +{meta['lines_added']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
