"""Cell-307 RLR campaign (r1) -- load the overnight RLR certifier from its PINNED bytes, unmodified.

No file of the certifier is copied, edited or re-implemented. Each module is read from its committed path in the
overnight namespace, checked against the sha256 recorded in `validation/C1B_R2_CODE_PINS.json` (pins revision 3,
load-bearing set unchanged since revision 1) and against its git blob at HEAD, and executed into `sys.modules` in
dependency order, so that every `import c1b_*` inside the certifier binds the verified module and no import is
resolved from the filesystem. The one binding that differs from the overnight runs is the quarantine module
`ov_quarantine`, which is bound to `rlr307_guard` (campaign drift policy; see that module).

Two module-level switches of `c1b_certpw` are read from `sys.argv` when the module is executed. They are set here
explicitly to the values of the pinned, reviewed block rung (`C1B_R2_PW_BLOCK_1_2__17_32_d4.json`: TIGHT_CT = True,
BLOCK_LIGHT = True = declaration D11), so the result can never depend on the caller's command line.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
import types
from pathlib import Path

CUSUM_REL = "level4/closure_proofs/p5y_k5_tail_overnight_research/streams/C_308/LR/cusum/"
PINS_REL = "level4/closure_proofs/p5y_k5_tail_overnight_research/validation/C1B_R2_CODE_PINS.json"
# name -> (sha256 of the exact bytes (= C1B_R2_CODE_PINS.json), git blob prefix at the overnight handover 7f45e048)
PINNED = {
    "c1b_gauss": ("3189208d6c4ce37ce7dd1e013caf58ae454f35211fd36154b2afa8b96cd9c43f", "61d756cb8dac"),
    "c1b_kernel": ("dfdc871b18ff132a95ed98d7354e3e95fbbc749cc473629923e4dec19bc4c41e", "b5b8dcf05724"),
    "c1b_float": ("2a14067cd0c629f5d9b18a56bf66e439acd9802dc62a166e5ff5f7e2d5726f5f", "6b3b8e23f6dd"),
    "c1b_pw": ("f10c2cf14691e56699aa823800381d799eb6bdbdf47fdfcf5f28e1f1abb839d0", "607fc7075446"),
    "c1b_prov": ("d12c2a2183e6636ec3fa1379db8024c5402f6b7e1f8cb6f7ad11b3ce6d20cf47", "530b4b222bcb"),
    "c1b_certpw": ("48080dd4df193a1474113ea792ab550fe325f51cb0e4d0e1c8a3e3bebd195c25", "807b64fed49a"),
}
LOAD_ORDER = ("c1b_gauss", "c1b_kernel", "c1b_float", "c1b_pw", "c1b_prov", "c1b_certpw")
FLAGS = {"TIGHT_CT": True, "BLOCK_LIGHT": True}


class PinError(RuntimeError):
    """The certifier bytes are not the pinned bytes."""


def _git(repo: Path, *args) -> str:
    p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(repo), *args], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C"},
                       stdin=subprocess.DEVNULL)
    return p.stdout.strip() if p.returncode == 0 else ""


def pinned_bytes(repo: Path, name: str, check_git: bool = True) -> bytes:
    sha, blob = PINNED[name]
    path = repo / (CUSUM_REL + name + ".py")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != sha:
        raise PinError(f"{name}: sha256 differs from the pin")
    if check_git:
        head_blob = _git(repo, "rev-parse", f"HEAD:{CUSUM_REL}{name}.py")
        if not head_blob.startswith(blob):
            raise PinError(f"{name}: committed blob at HEAD differs from the pinned blob")
        if hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest() != head_blob:
            raise PinError(f"{name}: worktree bytes differ from the committed blob")
    return raw


def load_certifier(repo: Path, guard: types.ModuleType, check_git: bool = True) -> dict:
    """Execute the pinned modules into sys.modules (guard bound as `ov_quarantine`) and return them by name."""
    for name in LOAD_ORDER + ("ov_quarantine",):
        if name in sys.modules and getattr(sys.modules[name], "_rlr307_pinned", None) is None and name != "ov_quarantine":
            raise PinError(f"{name} is already imported from somewhere else")
    saved_path = list(sys.path)
    sys.modules["ov_quarantine"] = guard
    mods = {}
    try:
        for name in LOAD_ORDER:
            raw = pinned_bytes(repo, name, check_git)
            path = repo / (CUSUM_REL + name + ".py")
            mod = types.ModuleType(name)
            mod.__file__ = str(path)
            mod._rlr307_pinned = PINNED[name][0]
            sys.modules[name] = mod
            exec(compile(raw, str(path), "exec"), mod.__dict__)
            mods[name] = mod
    finally:
        sys.path[:] = saved_path                       # c1b_certpw inserts two directories; nothing is imported from them
    cp = mods["c1b_certpw"]
    for k, v in FLAGS.items():
        setattr(cp, k, v)
    # identity: every internal binding is the verified module (no filesystem import happened)
    ident = {"certpw.G": cp.G is mods["c1b_gauss"], "certpw.KX": cp.KX is mods["c1b_kernel"],
             "certpw.PW": cp.PW is mods["c1b_pw"], "certpw.PV": cp.PV is mods["c1b_prov"], "certpw.Q": cp.Q is guard,
             "pw.KX": mods["c1b_pw"].KX is mods["c1b_kernel"], "pw.FL": mods["c1b_pw"].FL is mods["c1b_float"],
             "kernel.G": mods["c1b_kernel"].G is mods["c1b_gauss"],
             "flags": all(getattr(cp, k) is v for k, v in FLAGS.items())}
    if not all(ident.values()):
        raise PinError(f"module identity check failed: {ident}")
    mods["_identity"] = ident
    return mods
