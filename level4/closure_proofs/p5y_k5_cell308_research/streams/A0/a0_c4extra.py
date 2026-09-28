"""Stream A0 task C4 (supplement): byte-identity of certificate files written by two SEPARATE processes.

  python3 -I -B -S a0_c4extra.py TAG NAME_A NAME_B [NAME_A NAME_B ...]     (names relative to certs/)

Writes results/C4_FILEPAIRS_<TAG>.json.  Used for the C1b d = 8 rung (added to the recommended ladder after the
ladder determinism runs had started; a0_ladder.py was left untouched so that both ladder runs used identical code).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a0_common as A  # noqa: E402


def main(argv):
    tag, names = argv[1], argv[2:]
    rows = []
    for a, b in zip(names[::2], names[1::2]):
        ba, bb = (A.CERTS / a).read_bytes(), (A.CERTS / b).read_bytes()
        rows.append({"a": a, "b": b, "byte_identical": ba == bb, "sha256_a": A.sha256_bytes(ba),
                     "sha256_b": A.sha256_bytes(bb)})
    out = {"schema": "A0_C4_FILEPAIRS/1", "tag": tag, "pairs": rows,
           "PASS": bool(rows) and all(r["byte_identical"] for r in rows)}
    A.write_json(A.RESULTS / f"C4_FILEPAIRS_{tag}.json", out)
    print("PASS" if out["PASS"] else "FAIL", flush=True)


if __name__ == "__main__":
    main(list(sys.argv))
