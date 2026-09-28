"""reviewA0 scratch helpers: guard every drift (declared set + campaign guard), ledger lines as REVIEW / reviewA0."""
from __future__ import annotations

import importlib.util
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[1]
A0 = NS / "streams" / "A0"
REVIEWER_DRIFTS = frozenset(F(x) for x in ("1/2", "1", "11/10", "27/10", "3", "7/2"))


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


Cq = _load("c308_quarantine", NS / "code" / "c308_quarantine.py")
Cq.install_import_guard()


def rv_drift(e) -> F:
    e = F(e)
    if e not in REVIEWER_DRIFTS:
        raise Cq.QuarantineRefusal(f"reviewA0: {e} not in the reviewer's declared drift set")
    Cq.guard_drift(e)
    return e


def rv_log(script: str, purpose: str, notes: str = "") -> None:
    Cq.log_event(f"reviews/scratch_A0_R1/{script}", purpose, klass="REVIEW", agent="reviewA0", notes=notes)


def dump(name: str, obj) -> None:
    (HERE / name).write_text(json.dumps(obj, indent=1, sort_keys=True, default=str) + "\n")
