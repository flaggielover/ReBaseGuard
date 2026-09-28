"""Cell-308 MB campaign (r1) -- write the freeze manifest `protocol/MB308_FREEZE.json` (the input manifest the grant
binds by sha256). Run once, immediately before the freeze commit (and by the flow tests inside their sandbox). It
lists every frozen file (sha256, git blob id), every external pin (consumer inputs, pinned modules, F2, the C2b-PL
hook), the frozen rules and the exactly-once names. It writes nothing else.

    python3.14 -I -S -B mb308_manifest.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
CODE = HERE.parent
NS = HERE.parents[1]
REPO = HERE.parents[4]
sys.path.insert(0, str(CODE))
import mb308_a0core as A0C  # noqa: E402
import mb308_driver as D  # noqa: E402
import mb308_guard as G  # noqa: E402
import mb308_pinned as PIN  # noqa: E402
import mb308_stage1 as S1M  # noqa: E402

OUT = NS / "protocol" / "MB308_FREEZE.json"


def blob(b: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def manifest() -> dict:
    files = {}
    for d in D.FROZEN_DIRS:
        for p in sorted((NS / d).rglob("*")):
            if p.is_file() and p != OUT and "__pycache__" not in p.parts:
                raw = p.read_bytes()
                files[str(p.relative_to(REPO))] = {"sha256": hashlib.sha256(raw).hexdigest(), "git_blob": blob(raw)}
    return {
        "schema": "rebaseguard.p5y.k5.cell308-mb-r1.freeze-manifest.v1",
        "cell": D.TARGET_CELL, "route": "MB", "scope": "CLOSURE_ONLY", "frozen_dirs": list(D.FROZEN_DIRS),
        "frozen_files": files,
        "driver": {"path": D.NS_REL + "/code/mb308_driver.py",
                   "sha256": hashlib.sha256((CODE / "mb308_driver.py").read_bytes()).hexdigest()},
        "helper_sha256": D.HELPER_SHA256,
        "module_pins": {k: {"path": v[0], "sha256": v[1], "git_blob_prefix": v[2]} for k, v in PIN.PINS.items()},
        "independent_F2_pin": {"path": PIN.INDEP_PIN[0], "sha256": PIN.INDEP_PIN[1], "git_blob_prefix": PIN.INDEP_PIN[2]},
        "c2b_pl_hook": PIN.C2B_PL_HOOK,
        "consumer_and_input_pins": {k: {"path": v[0], "sha256": v[1], "git_blob_prefix": v[2]}
                                    for k, v in D.CON.PINS.items()},
        "a0_extraction_sources": A0C.EXTRACTION_SOURCES,
        "lineage": D.LINEAGE,
        "rules": {"D1_sub_block_max_width": str(G.SUB_BLOCK_MAX_WIDTH), "D2_hull_bits": G.HULL_BITS,
                  "D3_rlr_ladder": list(S1M.LADDER_RLR), "D4_c2b_N": list(S1M.LADDER_C2B_N),
                  "D4_c1b_d": list(S1M.LADDER_C1B_D), "rlr_flags": list(S1M.RLR_FLAGS), "pw_flags": list(S1M.PW_FLAGS),
                  "members": ["S_I1", "DvM_C1", "DvM_C2", "D14M", "G"],
                  "decision": "Gamma_dec = g_hi + max(P_B primary, P_hi F2) < 0 exact (Gamma_dec = 0 is NOT closed)"},
        "outcomes": list(D.OUTCOMES),
        "caps": {"pre_marker_s": D.PRE_CAP_S, "evaluation_s": D.EVAL_CAP_S, "workers": D.WORKERS},
        "exactly_once": {"marker": D.CONSUMED_REF, "pending": D.PENDING_REF, "result": D.RESULT_REL,
                         "emergency_file": D.EMERGENCY_NAME, "qualified_worktree": D.QUALIFIED_WORKTREE,
                         "qualified_branch": D.QUALIFIED_BRANCH},
        "guard": {"cell308_cover": [str(x) for x in G.CELL308], "admitted_pairs": len(G.target_admitted_set())},
    }


def main() -> int:
    man = manifest()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(man, indent=1, sort_keys=True) + "\n")
    print(f"wrote {OUT.relative_to(REPO)}: {len(man['frozen_files'])} frozen files; sha256 "
          f"{hashlib.sha256(OUT.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
