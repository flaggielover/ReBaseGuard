#!/usr/bin/env python3
"""Mutants of the repaired QC11 harness (the repaired invariant: every QC11 / QC-D5 sandbox chain holds exactly the
freeze-record commits its own flow builds; FREEZE_RECORD refusals are checked by their detail).

  python3 make_harness_mutants.py          -> repair/mutants/<ID>.py.txt and repair/mutants/MUTANTS.json

Each mutant is one textual change to the ported repair (data files; the rehearsal tool swaps one in for QC11 with
--harness mutant).  Expected outcomes, judged later from the QC11 record content (not its exit status):
  M1_BASE_HEAD            sandbox base back to HEAD, postcondition kept  -> QC11 FAIL, loudly (postcondition)
  M2_BASE_HEAD_NO_POST    sandbox base back to HEAD, no postcondition    -> QC11 FAIL (the r1 FREEZE_RECORD refusal)
  M3_DETAIL_SWAP          A24 / A25 refusal details swapped             -> QC11 FAIL (P6(c) detail check)
  M4_MANIFEST_FROM_TREE   manifest always from the working tree         -> QC11 PASS: an EQUIVALENT mutant in this
                          replica (the working-tree manifest equals F's); reported as a survivor, not hidden
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
SRC = NS / "repair" / "test_p309_exactly_once.R2_PORTED_TO_R1.py.txt"
OUT = NS / "repair" / "mutants"

HEAD_LINE = '    head, _mode = sandbox_base()                 # r2 P6: F after the freeze, HEAD before it (never "HEAD" blindly)\n'
R1_HEAD = ('    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True,\n'
           '                          check=True).stdout.strip()\n')
POST = ('    want = {"ok": 1, "wrong": 1, "late_change": 2}.get(freeze_record, 0)\n'
        '    have = len(sh(sb, "log", "--format=%H", tip, "--", D.FREEZE_RECORD_REL).split())\n'
        '    if have != want:\n'
        '        raise RuntimeError(f"QC11 harness: {have} freeze-record commits in the sandbox chain, expected {want}")\n')
A24 = "the record commit is not the freeze commit's record-only child"
A25 = "the freeze record was changed after it was made"
MAN = '''    base, mode = sandbox_base()
    if mode == "post-freeze":'''


def main() -> int:
    src = SRC.read_text()
    for frag in (HEAD_LINE, POST, A24, A25, MAN):
        if frag not in src:
            raise SystemExit(f"the ported harness lacks the expected text {frag[:50]!r}")
    muts = {
        "M1_BASE_HEAD": (src.replace(HEAD_LINE, R1_HEAD), "FAIL", "freeze-record commits in the sandbox chain"),
        "M2_BASE_HEAD_NO_POST": (src.replace(HEAD_LINE, R1_HEAD).replace(POST, ""), "FAIL",
                                 "the freeze record was changed after it was made"),
        "M3_DETAIL_SWAP": (src.replace(A24, "\0").replace(A25, A24).replace("\0", A25), "FAIL", "detail"),
        "M4_MANIFEST_FROM_TREE": (src.replace(MAN, '''    base, mode = sandbox_base()
    if False:'''), "PASS (equivalent here)", ""),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {"schema": "P309_QC11_HARNESS_MUTANTS/1", "source_sha256": hashlib.sha256(src.encode()).hexdigest(),
            "mutants": {}}
    for mid, (text, expect, frag) in muts.items():
        if text == src:
            raise SystemExit(f"{mid}: the mutation changed nothing")
        (OUT / f"{mid}.py.txt").write_text(text)
        meta["mutants"][mid] = {"sha256": hashlib.sha256(text.encode()).hexdigest(), "expected_qc11": expect,
                                "expected_reason_fragment": frag}
    (OUT / "MUTANTS.json").write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n")
    print(json.dumps(meta, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
