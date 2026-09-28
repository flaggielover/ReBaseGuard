"""C1b provenance helper (declaration D16): sha256 of every c1b_*.py in this directory, the pinned set, the CLI
flags and argv, recorded in every output JSON.  No side effects at import."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOAD_BEARING = ("c1b_gauss.py", "c1b_kernel.py", "c1b_pw.py", "c1b_certpw.py", "c1b_certify.py")


def code_hashes() -> dict:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("c1b_*.py"))}


def pins_file() -> Path:
    return HERE.parents[3] / "validation" / "C1B_R2_CODE_PINS.json"


def provenance(flags: dict | None = None) -> dict:
    h = code_hashes()
    out = {"code_sha256": h, "argv": list(sys.argv), "flags": dict(flags or {}),
           "python": sys.version.split()[0]}
    pf = pins_file()
    if pf.exists():
        pins = json.loads(pf.read_text())["pins"]
        out["pinned"] = pins
        out["matches_pins"] = all(h.get(k) == v for k, v in pins.items())
    else:
        out["pinned"] = None
        out["matches_pins"] = None
    return out
