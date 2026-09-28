"""Stream E (ASSEMBLY) -- the FROZEN-PATH LOADER (the only module of this stream that executes historical code).

It loads specific frozen consumer-path files BY EXPLICIT PATH (importlib.util.spec_from_file_location) under
DIFFERENT module names (prefix ``c308E_fp_``), after checking each file's sha256 pin and, where the brief names one,
its git blob id. Every load is recorded (key, relative path, module name, sha256, git blob) in ``LOAD_RECORD``.

Rules (binding, from the stream brief):
* The historical consumer modules are never imported by name: the c308 import guard is installed first, and the
  files are executed from their bytes under ``c308E_fp_*`` names.
* This module reads NO input data file of any cell. It loads code only. Nothing here evaluates anything.
* It must never be imported by code that touches a quarantined cell. Its only importer is ``tptb_tail.py``, whose
  every entry point refuses the quarantined labels (guard_cell) and the drift band (guard_drift) before any use.
* No historical driver / main() is executed (c2_d5_forecast.main and tail_forecast_r2 are NOT loaded: the latter
  imports a historical module by name and reads target inputs).

Loaded files (pins):
  c2_d5    level4/closure_proofs/p5y_k5_tail_c2_closure/code/c2_d5_forecast.py        blob 18403dbe  (direct, combine)
  tctr     level4/closure_proofs/p5y_k5_m5_tail_closure/code/tct_rule.py               blob 98f6eee4  (tail_enclosure ...)
  tcr      level4/closure_proofs/p5y_k5_lower_front_order3/code/tc_rule.py             sha 8d402d11   (frozen Campaign-A arithmetic;
                                                                                        the same pin tct_rule.FROZEN uses)
  dc       level4/closure_proofs/p5y_k5_perron_deflated_resolvent/code/deflated_consume.py  blob a0a836fa (atom_constants_r2)
  km       level4/closure_proofs/p5y_k5_order3_readiness_audit/code/k5_minimality.py   sha 3a54f0fb   (the frozen loader's rat)
  tpt      level4/closure_proofs/p5y_k5_tail_overnight_research/streams/E_assembly/tpt.py  sha 05cebc9c (theorem TPT r2)
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[2]
REPO = HERE.parents[5]
CP = "level4/closure_proofs/"

_spec = importlib.util.spec_from_file_location("c308E_quarantine", NS / "code" / "c308_quarantine.py")
Q = importlib.util.module_from_spec(_spec)
sys.modules["c308E_quarantine"] = Q
_spec.loader.exec_module(Q)
Q.install_import_guard()

FROZEN_FILES = {
    "c2_d5": (CP + "p5y_k5_tail_c2_closure/code/c2_d5_forecast.py",
              "bd7854bce2434215c0a72eeb825ff87db4c729e80b0e4d125911e806a084f06b",
              "18403dbec85513355414beb6869746703f7bbda2"),
    "tctr": (CP + "p5y_k5_m5_tail_closure/code/tct_rule.py",
             "f5a343e7f7bfb742d0a41c38512e27e7311d0919b38bcea0dfe98775c73d9a3e",
             "98f6eee4d867455065e20043fcf47ae54ffcad1e"),
    "tcr": (CP + "p5y_k5_lower_front_order3/code/tc_rule.py",
            "8d402d11f6fc06ea2af88e3d3a01e376fefbe8ebacd8418f772116010e57afd5", None),
    "dc": (CP + "p5y_k5_perron_deflated_resolvent/code/deflated_consume.py",
           "ef5d0474183053bb7cde3075bda66f99211706a9bf7bf27e31fe994ff8b87e72",
           "a0a836fa83c6d85d02bd377e8f2dc3ebfcc436ef"),
    "km": (CP + "p5y_k5_order3_readiness_audit/code/k5_minimality.py",
           "3a54f0fb290a9b8a07c861653d4399e6c588afdaef77ee51473f778c6c988885", None),
    "tpt": (CP + "p5y_k5_tail_overnight_research/streams/E_assembly/tpt.py",
            "05cebc9cd3278e1099ed2faf0c2ca5b32ee155f85be93654a80892873e4beab8", None),
}

LOAD_RECORD: list[dict] = []
_CACHE: dict = {}


class FrozenPathRefusal(RuntimeError):
    pass


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()


def load(key: str):
    """Execute one pinned frozen file under the module name c308E_fp_<key>; record its hashes."""
    if key in _CACHE:
        return _CACHE[key]
    rel, pin, blob = FROZEN_FILES[key]
    path = REPO / rel
    Q.guard_path(path)
    raw = path.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != pin:
        raise FrozenPathRefusal(f"{rel}: sha256 {got[:12]} != pin {pin[:12]}")
    gb = git_blob(raw)
    if blob is not None and gb != blob:
        raise FrozenPathRefusal(f"{rel}: git blob {gb[:8]} != pinned blob {blob[:8]}")
    name = "c308E_fp_" + key
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod          # dataclasses (tpt.py) resolve their module through sys.modules
    spec.loader.exec_module(mod)
    # the file on disk must still be the pinned one after execution (no swap between hash and exec)
    if hashlib.sha256(path.read_bytes()).hexdigest() != pin:
        raise FrozenPathRefusal(f"{rel} changed during load")
    LOAD_RECORD.append({"key": key, "path": rel, "module_name": name, "sha256": got, "git_blob": gb})
    _CACHE[key] = mod
    return mod


def load_all() -> dict:
    mods = {k: load(k) for k in FROZEN_FILES}
    # tct_rule pins its own copy of tc_rule; ours must be the same bytes
    if mods["tctr"].FROZEN["tc_rule"][1] != FROZEN_FILES["tcr"][1]:
        raise FrozenPathRefusal("tct_rule.FROZEN['tc_rule'] pin differs from the loader's tc_rule pin")
    if mods["c2_d5"].DC_SHA != FROZEN_FILES["dc"][1]:
        raise FrozenPathRefusal("c2_d5_forecast.DC_SHA differs from the loader's deflated_consume pin")
    return mods


def record() -> list:
    return [dict(r) for r in LOAD_RECORD]


if __name__ == "__main__":
    import json
    load_all()
    print(json.dumps(record(), indent=1))
