"""Cell-308 MB campaign (r1) -- load every external module from its PINNED bytes (B2).

No external file is copied, edited or re-implemented here. Each module is read from its committed path, checked
against the sha256 below and (for committed files) against its git blob at HEAD, and executed from those bytes into a
module object (no filesystem import, no .pyc). The guard `mb308_guard` is bound as `ov_quarantine` (C1b, C2b, tpt.py),
as `c308E_quarantine` (tptb_tail) and as the `Q` attribute of the independent verifier vd_verify.

Groups (all pins are sha256 of the exact bytes; BLOB = the git blob id at the research tip c494705d):
  C1B      the overnight C1b certifier (pins = C1B_R2_CODE_PINS.json, as rlr307_pinned)
  C2B      c7_gaussian + the overnight C2b modules (pins = streams/A0/A0_CODE_PINS.json)
  RLR307   rlr307_stage1 (rules P1-P5) and rlr307_independent (D14 / Lemma Lad oracle), the cell-307 campaign's
           frozen helpers (sha256 = rlr307_driver.HELPER_SHA256)
  VERIFY   the independent verifier vd_verify + its C1b adapter vd_adapt; C2B_PL_HOOK (a C2b P1 nodal-format
           adapter being added by stream VERIFY) -- None until it exists, and C2b rungs are then UNVERIFIED
  ASSEMBLY tptb_tail + frozen_path_loader (stream ASSEMBLY) and the frozen files the loader pins (c2_d5_forecast,
           tct_rule, tc_rule, deflated_consume, k5_minimality, tpt.py r2), executed here from verified bytes and
           handed to the loader's cache; decoy_gen (decoy mode only)
  INDEP    stream F2's independent reconstruction mb_independent (HOOK: pinned at the freeze; see INDEP_PIN)
  RESEARCH the research quarantine module c308_quarantine, which vd_verify and frozen_path_loader execute at import
           (bytes checked here first; its import guard is inert for exec-loaded modules; its drift guard is never
           reached because every `Q` binding is re-pointed to mb308_guard)
Uncommitted files (stream A0, stream INDEP) cannot be blob-checked: `committed=False` pins are accepted only when
the caller passes allow_uncommitted=True (decoy / development); the driver's execute / preflight never does.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
import types
from pathlib import Path

CP = "level4/closure_proofs/"
OV = CP + "p5y_k5_tail_overnight_research/"
RS = CP + "p5y_k5_cell308_research/"
C1B_DIR = OV + "streams/C_308/LR/cusum/"
C2B_DIR = OV + "streams/C_308/A0X/gen/"

# key -> (relative path, sha256, git blob at the research tip or None for an uncommitted file)
PINS = {
    "c1b_gauss": (C1B_DIR + "c1b_gauss.py", "3189208d6c4ce37ce7dd1e013caf58ae454f35211fd36154b2afa8b96cd9c43f", "61d756cb8dac"),
    "c1b_kernel": (C1B_DIR + "c1b_kernel.py", "dfdc871b18ff132a95ed98d7354e3e95fbbc749cc473629923e4dec19bc4c41e", "b5b8dcf05724"),
    "c1b_float": (C1B_DIR + "c1b_float.py", "2a14067cd0c629f5d9b18a56bf66e439acd9802dc62a166e5ff5f7e2d5726f5f", "6b3b8e23f6dd"),
    "c1b_pw": (C1B_DIR + "c1b_pw.py", "f10c2cf14691e56699aa823800381d799eb6bdbdf47fdfcf5f28e1f1abb839d0", "607fc7075446"),
    "c1b_prov": (C1B_DIR + "c1b_prov.py", "d12c2a2183e6636ec3fa1379db8024c5402f6b7e1f8cb6f7ad11b3ce6d20cf47", "530b4b222bcb"),
    "c1b_certpw": (C1B_DIR + "c1b_certpw.py", "48080dd4df193a1474113ea792ab550fe325f51cb0e4d0e1c8a3e3bebd195c25", "807b64fed49a"),
    "c7_gaussian": (CP + "p5y_k5_tail_c7_e2_lambda309/code/c7_gaussian.py",
                    "bd73b5b46766ca4272cdf5db3c7258e45e81599e712f9984cd03a5455cea9815", "be492720abb6"),
    "c2b_common": (C2B_DIR + "c2b_common.py", "2f059c0aa5761d571da6af82b86d0ab788d1a608740116c9f2cd59fc025d49b5", "3960490f4b41"),
    "c2b_exact": (C2B_DIR + "c2b_exact.py", "fb94e7cec4d2379ab5999c056410fcfc58ac5efee06a074b0c756619d238c8e5", "49e72fe09a92"),
    "c2b_float": (C2B_DIR + "c2b_float.py", "b33e3f908fc5166e80ebc7faf99a0aee537e93b5eba78ebe5ce9762aa7739d4f", "fa24dfe4508d"),
    "c2b_certify": (C2B_DIR + "c2b_certify.py", "1c7e111be4cf50f1644decd98d4ce8f20526741f18a596d551cffa1f7993e8de", "2d92ba8ec15a"),
    "rlr307_stage1": (CP + "p5y_k5_cell307_rlr_r1/code/rlr307_stage1.py",
                      "6fa9f69168d619a194c1e508e9bb264c01715998dc755e8bd481846758cf685f", "cadb9f83d8be"),
    "rlr307_independent": (CP + "p5y_k5_cell307_rlr_r1/code/rlr307_independent.py",
                           "91a75ea8f4c5a6183efc0eeec4eff3315abaafd92c4a4c8bc5d94c6d44cf94f4", "85397b5538bd"),
    "vd_verify": (RS + "streams/VERIFY/vd_verify.py",
                  "cd4cec35e86d8036618a53c85d76f685d1475847af4fac9b879ba33c37cefc7f", "2b50f8dd5c53"),
    "vd_adapt": (RS + "streams/VERIFY/vd_adapt.py",
                 "1b2acd616f3dc75b5cb812c0508977b001cd4f8d0518ca81513fcfb9907dc761", "3ffc0fef9d48"),
    "c308_quarantine": (RS + "code/c308_quarantine.py",                     # scanner r2 (8da57f89)
                        "72d529cc352208fe6dc9c2045d991a799eb0fcca2f2fe3b2969cd5b7554faa12", "e103c196ef0e"),
    "tptb_tail": (RS + "streams/ASSEMBLY/tptb_tail.py",
                  "b373a8b4389b6e572a2297c069606c790b7e8bb6ede9e05619fc8308256862c2", "1995004c6c49"),
    "frozen_path_loader": (RS + "streams/ASSEMBLY/frozen_path_loader.py",
                           "97c0feb34e6fc31f436adbe1e5afa871e5f3ddaf28f9726dcc89fe1ca5fac18a", "26fdb8f7580d"),
    "decoy_gen": (RS + "streams/ASSEMBLY/decoy_gen.py",
                  "457472689cfcb70761707cde027c9f1ee971dd6edec4261ecdc84dedeae61ed6", "621a7a56c142"),
    "fp_c2_d5": (CP + "p5y_k5_tail_c2_closure/code/c2_d5_forecast.py",
                 "bd7854bce2434215c0a72eeb825ff87db4c729e80b0e4d125911e806a084f06b", "18403dbec855"),
    "fp_tctr": (CP + "p5y_k5_m5_tail_closure/code/tct_rule.py",
                "f5a343e7f7bfb742d0a41c38512e27e7311d0919b38bcea0dfe98775c73d9a3e", "98f6eee4d867"),
    "fp_tcr": (CP + "p5y_k5_lower_front_order3/code/tc_rule.py",
               "8d402d11f6fc06ea2af88e3d3a01e376fefbe8ebacd8418f772116010e57afd5", "ce101d175360"),
    "fp_dc": (CP + "p5y_k5_perron_deflated_resolvent/code/deflated_consume.py",
              "ef5d0474183053bb7cde3075bda66f99211706a9bf7bf27e31fe994ff8b87e72", "a0a836fa83c6"),
    "fp_km": (CP + "p5y_k5_order3_readiness_audit/code/k5_minimality.py",
              "3a54f0fb290a9b8a07c861653d4399e6c588afdaef77ee51473f778c6c988885", "fbd624aaecbb"),
    "fp_tpt": (OV + "streams/E_assembly/tpt.py",
               "05cebc9cd3278e1099ed2faf0c2ca5b32ee155f85be93654a80892873e4beab8", "c6d4cdde3f04"),
}
# stream F2 (streams/INDEP/mb_independent.py, revision F2-r1), committed at a7014669 (research branch). Its research
# band guard is ON by default: the formal path turns it off only when mb308_guard is ARMED for the target (see
# mb308_consumer.f2_band_guard); its private `_mutant` hooks are never used by the formal path.
INDEP_PIN = (RS + "streams/INDEP/mb_independent.py",
             "32aa83a866005ad737424225ff8bfcb3898ebb79b3598e37d80a1e89a16ca4c0", "8aacb252b57b")
# stream F3 (streams/INDEP_TUPLE/tuple_independent.py), committed at 0292d654: an independent re-derivation of the TC-T
# per-r tuple and profile coefficients (gate G-R3b). Its own research guard `_guard` (quarantined labels and band,
# no opt-out) is re-pointed at load time to an adapter that asks the FORMAL guard instead (guard_cell for CUSUM m = 5
# labels 305-309, guard_drift for the geometry): it refuses exactly what mb308_guard refuses.
TUPLE_PIN = (RS + "streams/INDEP_TUPLE/tuple_independent.py",
             "47ae88dcc792779b247ae1827e66c9f460a5e1b2c56e6b081a828ae245e6cbc8", "86061897e6cc")
# stream VERIFY's independent P1 (C2b piecewise-linear) verifier, committed at 58f190dc (VERIFIER_REPORT sections 10-15).
# It imports vd_verify BY NAME: it is executed after the pinned vd_verify is registered and re-pointed (identity checked).
C2B_PL_HOOK = (RS + "streams/VERIFY/vd_pl.py",
               "1f10c9506422adf11e001c05d39dda59c7081c595abae45a1540ab05e0aa1221", "0764c0b11d77")
C1B_ORDER = ("c1b_gauss", "c1b_kernel", "c1b_float", "c1b_pw", "c1b_prov", "c1b_certpw")
C2B_ORDER = ("c7_gaussian", "c2b_common", "c2b_exact", "c2b_float", "c2b_certify")
FP_KEYS = {"c2_d5": "fp_c2_d5", "tctr": "fp_tctr", "tcr": "fp_tcr", "dc": "fp_dc", "km": "fp_km", "tpt": "fp_tpt"}
ENV = {"PATH": "/usr/bin:/bin", "GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C"}
_LOADED: dict = {}
LOAD_RECORD: list = []
GUARD_SHA256 = None          # set by the driver from its HELPER_SHA256; every binding of the guard checks it


class PinError(RuntimeError):
    """The bytes are not the pinned bytes, or a module identity check failed."""


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob_id(b: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def _git(repo: Path, *args) -> str:
    p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(repo), *args], capture_output=True, text=True,
                       env=ENV, stdin=subprocess.DEVNULL)
    return p.stdout.strip() if p.returncode == 0 else ""


def verified_bytes(repo: Path, pin: tuple, check_git: bool = True, allow_uncommitted: bool = False) -> bytes:
    rel, want, blob = pin
    raw = (Path(repo) / rel).read_bytes()
    if sha(raw) != want:
        raise PinError(f"{rel}: sha256 differs from the pin")
    if blob is None:
        if not allow_uncommitted:
            raise PinError(f"{rel}: uncommitted pin refused (freeze must pin a committed blob)")
    elif check_git:
        head = _git(Path(repo), "rev-parse", f"HEAD:{rel}")
        if not head.startswith(blob) or blob_id(raw) != head:
            raise PinError(f"{rel}: bytes differ from the committed blob at HEAD")
    return raw


def exec_pinned(repo: Path, name: str, pin: tuple, *, check_git: bool = True, allow_uncommitted: bool = False,
                register: bool = True) -> types.ModuleType:
    raw = verified_bytes(repo, pin, check_git, allow_uncommitted)
    path = Path(repo) / pin[0]
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    mod._mb308_sha256 = pin[1]
    saved = list(sys.path)
    if register:
        sys.modules[name] = mod
    try:
        exec(compile(raw, str(path), "exec"), mod.__dict__)
    finally:
        sys.path[:] = saved
    LOAD_RECORD.append({"name": name, "path": pin[0], "sha256": pin[1], "blob": pin[2]})
    return mod


def _bind_guard(guard: types.ModuleType) -> None:
    """Bind the formal guard as `ov_quarantine` after CHECKING its bytes against the driver's pin (REVIEW_A0 C1)."""
    if GUARD_SHA256 is None or sha(Path(guard.__file__).read_bytes()) != GUARD_SHA256:
        raise PinError("the guard module's bytes are not the pinned bytes (or no pin was set)")
    cur = sys.modules.get("ov_quarantine")
    if cur is not None and cur is not guard:
        raise PinError("ov_quarantine is already bound to another module")
    sys.modules["ov_quarantine"] = guard
    guard.install_import_guard()


def no_pycache(repo: Path, rel: str) -> None:
    """vd_verify and frozen_path_loader execute c308_quarantine through the import machinery (spec_from_file_location),
    which would READ a cached .pyc; none may exist next to it (the bytes check covers the .py only)."""
    d = (Path(repo) / rel).parent / "__pycache__"
    if d.exists():
        raise PinError(f"{d} exists: a cached .pyc could be executed instead of the pinned bytes")


def _fresh(names) -> None:
    for n in names:
        m = sys.modules.get(n)
        if m is not None and getattr(m, "_mb308_sha256", None) is None:
            raise PinError(f"{n} is already imported from somewhere else")


# ------------------------------------------------------------------ C1b (flags set per call by the caller)
def load_c1b(repo: Path, guard, check_git: bool = True) -> dict:
    if "c1b" in _LOADED:
        return _LOADED["c1b"]
    _fresh(C1B_ORDER)
    _bind_guard(guard)
    mods = {n: exec_pinned(repo, n, PINS[n], check_git=check_git) for n in C1B_ORDER}
    cp = mods["c1b_certpw"]
    ident = {"certpw.G": cp.G is mods["c1b_gauss"], "certpw.KX": cp.KX is mods["c1b_kernel"],
             "certpw.PW": cp.PW is mods["c1b_pw"], "certpw.PV": cp.PV is mods["c1b_prov"], "certpw.Q": cp.Q is guard,
             "pw.KX": mods["c1b_pw"].KX is mods["c1b_kernel"], "pw.FL": mods["c1b_pw"].FL is mods["c1b_float"],
             "kernel.G": mods["c1b_kernel"].G is mods["c1b_gauss"]}
    if not all(ident.values()):
        raise PinError(f"C1b identity check failed: {ident}")
    mods["_identity"] = ident
    _LOADED["c1b"] = mods
    return mods


def set_c1b_flags(mods: dict, tight_ct: bool, block_light: bool) -> dict:
    cp = mods["c1b_certpw"]
    cp.TIGHT_CT, cp.BLOCK_LIGHT = bool(tight_ct), bool(block_light)
    return {"TIGHT_CT": cp.TIGHT_CT, "BLOCK_LIGHT": cp.BLOCK_LIGHT}


# ------------------------------------------------------------------ C2b
def load_c2b(repo: Path, guard, check_git: bool = True) -> dict:
    if "c2b" in _LOADED:
        return _LOADED["c2b"]
    _fresh(C2B_ORDER)
    _bind_guard(guard)
    mods = {n: exec_pinned(repo, n, PINS[n], check_git=check_git) for n in C2B_ORDER}
    ident = {"common.G": mods["c2b_common"].G is mods["c7_gaussian"], "common.Q": mods["c2b_common"].Q is guard,
             "exact.CM": mods["c2b_exact"].CM is mods["c2b_common"],
             "float.CM": mods["c2b_float"].CM is mods["c2b_common"],
             "certify.EX": mods["c2b_certify"].EX is mods["c2b_exact"],
             "certify.FL": mods["c2b_certify"].FL is mods["c2b_float"]}
    if not all(ident.values()):
        raise PinError(f"C2b identity check failed: {ident}")
    mods["_identity"] = ident
    _LOADED["c2b"] = mods
    return mods


# ------------------------------------------------------------------ the cell-307 helpers (rules, D14 oracle)
def load_rlr307(repo: Path, check_git: bool = True) -> tuple:
    if "rlr307" not in _LOADED:
        s1 = exec_pinned(repo, "mb308_rlr307_stage1", PINS["rlr307_stage1"], check_git=check_git)
        ind = exec_pinned(repo, "mb308_rlr307_independent", PINS["rlr307_independent"], check_git=check_git)
        _LOADED["rlr307"] = (s1, ind)
    return _LOADED["rlr307"]


# ------------------------------------------------------------------ the independent verifier (D5)
def load_verifier(repo: Path, guard, check_git: bool = True) -> dict:
    """vd_verify executes the research c308_quarantine at import (by path); its bytes are checked first, and the
    verifier's `Q` is re-pointed to the formal guard before any use. `from vd_verify import StripPW` inside vd_adapt
    resolves to this module through sys.modules."""
    if "verify" in _LOADED:
        return _LOADED["verify"]
    verified_bytes(repo, PINS["c308_quarantine"], check_git)
    no_pycache(repo, PINS["c308_quarantine"][0])
    cur = sys.modules.get("vd_verify")
    if cur is not None and getattr(cur, "_mb308_sha256", None) is None:
        raise PinError("vd_verify is already imported from somewhere else")
    vd = exec_pinned(repo, "vd_verify", PINS["vd_verify"], check_git=check_git)
    vd.Q = guard
    ad = exec_pinned(repo, "vd_adapt", PINS["vd_adapt"], check_git=check_git)
    out = {"vd": vd, "adapt": ad, "c2b_pl": None, "c2b_pl_status": "HOOK_ABSENT"}
    if C2B_PL_HOOK is not None:
        cur = sys.modules.get("vd_pl")
        if cur is not None and getattr(cur, "_mb308_sha256", None) is None:
            raise PinError("vd_pl is already imported from somewhere else")
        pl = exec_pinned(repo, "vd_pl", C2B_PL_HOOK, check_git=check_git)
        if pl.V is not vd or pl.Q is not guard:
            raise PinError("vd_pl did not bind the pinned vd_verify / the formal guard")
        out["c2b_pl"] = pl
        out["c2b_pl_status"] = "PINNED"
    out["_identity"] = {"vd.Q": vd.Q is guard, "vd_pl.V": out["c2b_pl"] is None or out["c2b_pl"].V is vd,
                        "vd_pl.Q": out["c2b_pl"] is None or out["c2b_pl"].Q is guard}
    _LOADED["verify"] = out
    return out


# ------------------------------------------------------------------ stream ASSEMBLY (TPT-B on the frozen path)
def load_assembly(repo: Path, guard, check_git: bool = True, with_decoy_gen: bool = False) -> dict:
    """frozen_path_loader is executed from pinned bytes; each frozen file it pins is executed HERE from verified bytes
    under the loader's own module name (c308E_fp_<key>) and placed in the loader's cache, so the loader never
    reads a file through the import system. Then tptb_tail runs with c308E_quarantine = the formal guard."""
    if "asm" in _LOADED and (not with_decoy_gen or "DG" in _LOADED["asm"]):
        return _LOADED["asm"]
    if "asm" not in _LOADED:
        _bind_guard(guard)
        verified_bytes(repo, PINS["c308_quarantine"], check_git)
        no_pycache(repo, PINS["c308_quarantine"][0])
        fp = exec_pinned(repo, "c308E_frozen_path_loader", PINS["frozen_path_loader"], check_git=check_git)
        for k, key in FP_KEYS.items():
            rel, pin, _ = fp.FROZEN_FILES[k]
            if (rel, pin) != PINS[key][:2]:
                raise PinError(f"frozen_path_loader pin {k} differs from the campaign pin")
            mod = exec_pinned(repo, "c308E_fp_" + k, PINS[key], check_git=check_git)
            fp._CACHE[k] = mod
            fp.LOAD_RECORD.append({"key": k, "path": rel, "module_name": "c308E_fp_" + k, "sha256": pin,
                                   "git_blob": PINS[key][2], "loaded_by": "mb308_pinned (verified bytes)"})
        sys.modules["c308E_quarantine"] = guard                 # tptb_tail's _load_by_path returns this binding
        tb = exec_pinned(repo, "c308E_tptb_tail", PINS["tptb_tail"], check_git=check_git)
        ident = {"tb.Q": tb.Q is guard, "tb.FP": tb.FP is fp, "tpt.Q": tb.TPT.Q is guard,
                 "tb.TPT": tb.TPT is fp._CACHE["tpt"], "tb.C2": tb.C2 is fp._CACHE["c2_d5"]}
        if not all(ident.values()):
            raise PinError(f"ASSEMBLY identity check failed: {ident}")
        _LOADED["asm"] = {"TB": tb, "TPT": tb.TPT, "FP": fp, "_identity": ident}
    if with_decoy_gen and "DG" not in _LOADED["asm"]:
        _LOADED["asm"]["DG"] = exec_pinned(repo, "c308E_decoy_gen", PINS["decoy_gen"], check_git=check_git)
        if _LOADED["asm"]["DG"].TB is not _LOADED["asm"]["TB"]:
            raise PinError("decoy_gen did not bind the pinned tptb_tail")
    return _LOADED["asm"]


# ------------------------------------------------------------------ stream F2 (hook)
def load_indep(repo: Path, check_git: bool = True, allow_uncommitted: bool = False):
    """The independent reconstruction, or None when its file is absent. Present bytes must equal INDEP_PIN."""
    if "indep" in _LOADED:
        return _LOADED["indep"]
    if not (Path(repo) / INDEP_PIN[0]).exists():
        _LOADED["indep"] = None
        return None
    mod = exec_pinned(repo, "mb308_f2_independent", INDEP_PIN, check_git=check_git,
                      allow_uncommitted=allow_uncommitted)
    _LOADED["indep"] = mod
    return mod


def load_tuple_indep(repo: Path, guard, check_git: bool = True):
    """Stream F3, or None when its file is absent. Present bytes must equal TUPLE_PIN."""
    if "f3" in _LOADED:
        return _LOADED["f3"]
    if not (Path(repo) / TUPLE_PIN[0]).exists():
        _LOADED["f3"] = None
        return None
    mod = exec_pinned(repo, "mb308_f3_tuple_independent", TUPLE_PIN, check_git=check_git)

    def formal_guard(label, left, right):
        try:
            lab = int(label)
        except (TypeError, ValueError):
            lab = None
        if lab is not None and 305 <= lab <= 309:
            guard.guard_cell("CUSUM", 5, lab)
        guard.guard_drift(left, right)

    mod._research_guard = mod._guard
    mod._guard = formal_guard
    mod._mb308_identity = {"F3._guard_is_formal_adapter": mod._guard is formal_guard}
    _LOADED["f3"] = mod
    return mod


def record() -> list:
    return [dict(r) for r in LOAD_RECORD]
