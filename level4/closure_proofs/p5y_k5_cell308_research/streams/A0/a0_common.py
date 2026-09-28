"""Stream A0 (stream C of the cell-308 research campaign): common wiring for the pointwise order-0 / ARL certifier study.

Stdlib only.  Exact arithmetic (fractions.Fraction / integers) for every load-bearing comparison.

What this module does
  * loads the campaign quarantine ``code/c308_quarantine.py`` BY PATH and installs its import guard;
  * binds the name ``ov_quarantine`` (imported by the overnight certifiers) to a SHIM whose drift guard calls BOTH the
    campaign guard (c308_quarantine.guard_drift) AND the overnight guard (ov_quarantine.guard_drift, loaded by path
    under a private name), and whose ``log_execution`` always refuses (no certifier ever writes into the overnight
    namespace from this stream);
  * loads the overnight certifier modules from their committed bytes (exec of verified bytes, no filesystem import,
    no .pyc): C1b from the sha256 pins in OV/validation/C1B_R2_CODE_PINS.json, C2b (no pins file exists) from the
    sha256 recorded by this stream in A0_CODE_PINS.json, and in both cases also against the git blob at HEAD;
  * provides the declared drift set and the ledger helper.

Nothing here computes an operator quantity.  Every entry point of this stream calls ``declared_drift`` (declared set
membership + both guards) before any evaluation.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import types
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent                     # NS/streams/A0
NS = HERE.parents[1]                                       # NS = .../p5y_k5_cell308_research
CLOSURE = NS.parent                                        # .../level4/closure_proofs
REPO = CLOSURE.parents[1]
OV = CLOSURE / "p5y_k5_tail_overnight_research"
C1B_DIR = OV / "streams" / "C_308" / "LR" / "cusum"
C2B_DIR = OV / "streams" / "C_308" / "A0X" / "gen"
C7_FILE = CLOSURE / "p5y_k5_tail_c7_e2_lambda309" / "code" / "c7_gaussian.py"
C1B_PINS_FILE = OV / "validation" / "C1B_R2_CODE_PINS.json"
A0_PINS_FILE = HERE / "A0_CODE_PINS.json"
RESULTS = HERE / "results"
CERTS = HERE / "certs"
LOGS = HERE / "logs"


def _load_by_path(name: str, path: Path) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------------------------------------ quarantine
C = sys.modules.get("c308_quarantine") or _load_by_path("c308_quarantine", NS / "code" / "c308_quarantine.py")
C.install_import_guard()
QuarantineRefusal = C.QuarantineRefusal
_OVQ = sys.modules.get("_ov_quarantine_real") or _load_by_path("_ov_quarantine_real", OV / "code" / "ov_quarantine.py")


def _shim() -> types.ModuleType:
    s = types.ModuleType("ov_quarantine")
    s.__doc__ = "A0 shim: campaign guard AND overnight guard; log_execution refuses."
    s.QuarantineRefusal = C.QuarantineRefusal

    def guard_drift(e_lo, e_hi=None):
        C.guard_drift(e_lo, e_hi)
        _OVQ.guard_drift(e_lo, e_hi)

    def guard_cell(detector, m, cell):
        C.guard_cell(detector, m, cell)
        _OVQ.guard_cell(detector, m, cell)

    def guard_path(path):
        C.guard_path(path)
        _OVQ.guard_path(path)

    def install_import_guard():
        C.install_import_guard()
        _OVQ.install_import_guard()

    def log_execution(*_a, **_k):
        raise C.QuarantineRefusal("A0: overnight log_execution refused (this stream never writes into OV)")

    for f in (guard_drift, guard_cell, guard_path, install_import_guard, log_execution):
        setattr(s, f.__name__, f)
    s._a0_shim = True
    return s


if not getattr(sys.modules.get("ov_quarantine"), "_a0_shim", False):
    if "ov_quarantine" in sys.modules:
        raise C.QuarantineRefusal("ov_quarantine already imported from somewhere else")
    sys.modules["ov_quarantine"] = _shim()
sys.modules["ov_quarantine"].install_import_guard()

# ------------------------------------------------------------------------------------------------ declared drifts
DECLARED_DRIFTS = ("1/2", "1", "11/10", "27/10", "3", "7/2")     # stream-C declaration (brief); 0, 1/4 optional
OPTIONAL_DRIFTS = ("0", "1/4")
PRIORITY_DRIFTS = ("11/10", "27/10", "1", "3")


def declared_drift(e) -> F:
    """Refuse anything that is not a declared validation drift (or its mirror, used only by the drift-change control),
    then run BOTH quarantine guards.  Returns the exact drift."""
    e = F(e)
    allowed = {F(x) for x in DECLARED_DRIFTS + OPTIONAL_DRIFTS}
    if e not in allowed and -e not in allowed:
        raise C.QuarantineRefusal(f"A0: drift {e} is not a declared validation drift of this stream")
    C.guard_drift(e)
    _OVQ.guard_drift(e)
    return e


def fs(x) -> str:
    x = F(x)
    return f"{x.numerator}/{x.denominator}"


def tag(e) -> str:
    e = F(e)
    return (f"{e.numerator}_{e.denominator}" if e.denominator != 1 else f"{e.numerator}").replace("-", "m")


# ------------------------------------------------------------------------------------------------ git / hashes
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git_blob_ok(path: Path, raw: bytes) -> bool:
    rel = str(path.resolve().relative_to(REPO.resolve()))
    p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(REPO), "rev-parse", f"HEAD:{rel}"],
                       capture_output=True, text=True, env={"PATH": "/usr/bin:/bin", "GIT_OPTIONAL_LOCKS": "0",
                                                            "LC_ALL": "C"}, stdin=subprocess.DEVNULL)
    head = p.stdout.strip() if p.returncode == 0 else ""
    return bool(head) and hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest() == head


class PinError(RuntimeError):
    pass


def _exec_verified(name: str, path: Path, sha: str, check_git: bool = True) -> types.ModuleType:
    raw = path.read_bytes()
    if sha256_bytes(raw) != sha:
        raise PinError(f"{name}: sha256 differs from the pin")
    if check_git and not git_blob_ok(path, raw):
        raise PinError(f"{name}: bytes differ from the committed blob at HEAD")
    if name in sys.modules and getattr(sys.modules[name], "_a0_sha256", None) != sha:
        raise PinError(f"{name} is already imported from somewhere else")
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    mod._a0_sha256 = sha
    sys.modules[name] = mod
    exec(compile(raw, str(path), "exec"), mod.__dict__)
    return mod


C1B_LOAD_ORDER = ("c1b_gauss", "c1b_kernel", "c1b_float", "c1b_pw", "c1b_prov", "c1b_certpw")
C2B_LOAD_ORDER = ("c7_gaussian", "c2b_common", "c2b_exact", "c2b_float", "c2b_certify")
_LOADED: dict = {}


def load_c1b(tight_ct: bool = True, block_light: bool = False, check_git: bool = True) -> dict:
    """Pinned C1b modules (flags set explicitly; they are read from sys.argv at exec and then overridden)."""
    if "c1b" in _LOADED:
        cp = _LOADED["c1b"]["c1b_certpw"]
    else:
        pins = json.loads(C1B_PINS_FILE.read_text())["pins"]
        saved = list(sys.path)
        mods = {}
        try:
            for name in C1B_LOAD_ORDER:
                mods[name] = _exec_verified(name, C1B_DIR / f"{name}.py", pins[f"{name}.py"], check_git)
        finally:
            sys.path[:] = saved
        cp = mods["c1b_certpw"]
        ident = {"certpw.G": cp.G is mods["c1b_gauss"], "certpw.KX": cp.KX is mods["c1b_kernel"],
                 "certpw.PW": cp.PW is mods["c1b_pw"], "pw.KX": mods["c1b_pw"].KX is mods["c1b_kernel"],
                 "pw.FL": mods["c1b_pw"].FL is mods["c1b_float"], "kernel.G": mods["c1b_kernel"].G is mods["c1b_gauss"],
                 "certpw.Q_is_shim": getattr(cp.Q, "_a0_shim", False)}
        if not all(ident.values()):
            raise PinError(f"C1b identity check failed: {ident}")
        mods["_identity"] = ident
        mods["_sha256"] = {n: mods[n]._a0_sha256 for n in C1B_LOAD_ORDER}
        _LOADED["c1b"] = mods
    cp.TIGHT_CT = bool(tight_ct)
    cp.BLOCK_LIGHT = bool(block_light)
    _LOADED["c1b"]["_flags"] = {"TIGHT_CT": cp.TIGHT_CT, "BLOCK_LIGHT": cp.BLOCK_LIGHT}
    return _LOADED["c1b"]


def c2b_paths() -> dict:
    return {"c7_gaussian": C7_FILE, **{n: C2B_DIR / f"{n}.py" for n in C2B_LOAD_ORDER[1:]}}


def load_c2b(check_git: bool = True) -> dict:
    if "c2b" in _LOADED:
        return _LOADED["c2b"]
    pins = json.loads(A0_PINS_FILE.read_text())["c2b_pins"]
    saved = list(sys.path)
    mods = {}
    try:
        for name, path in c2b_paths().items():
            mods[name] = _exec_verified(name, path, pins[name], check_git)
    finally:
        sys.path[:] = saved
    ident = {"common.G": mods["c2b_common"].G is mods["c7_gaussian"],
             "common.Q_is_shim": getattr(mods["c2b_common"].Q, "_a0_shim", False),
             "exact.CM": mods["c2b_exact"].CM is mods["c2b_common"],
             "float.CM": mods["c2b_float"].CM is mods["c2b_common"],
             "certify.EX": mods["c2b_certify"].EX is mods["c2b_exact"],
             "certify.FL": mods["c2b_certify"].FL is mods["c2b_float"]}
    if not all(ident.values()):
        raise PinError(f"C2b identity check failed: {ident}")
    mods["_identity"] = ident
    mods["_sha256"] = {n: mods[n]._a0_sha256 for n in C2B_LOAD_ORDER}
    _LOADED["c2b"] = mods
    return mods


def own_code_sha256() -> dict:
    return {p.name: sha256_bytes(p.read_bytes()) for p in sorted(HERE.glob("a0_*.py"))}


# ------------------------------------------------------------------------------------------------ canonical JSON
def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def write_json(path: Path, obj) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")
    tmp.replace(path)
    return sha256_bytes(path.read_bytes())


def ledger(script: str, purpose: str, klass: str = "NONTARGET_DRIFT_VALIDATION", notes: str = "") -> None:
    C.log_event(f"streams/A0/{script}", purpose, klass=klass, agent="streamC", notes=notes)
