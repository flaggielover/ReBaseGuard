"""Cell-308 MB campaign (r1) -- write the freeze manifest `protocol/MB308_FREEZE.json` (the input manifest the grant
binds by sha256). Run once, immediately before the freeze commit (and by the flow tests inside their sandbox). It
lists, with sha256 and git blob id computed from the bytes AT THAT TIME (nothing about the protocol text is pinned in
code), EVERY file of the namespace except the manifest itself and the post-freeze directories (qualification,
review, authorization, evidence, adjudication, postexec): protocol, theory, errata, evidence_prefreeze, config,
code, tests and the root files; and EVERY pinned external file (pinned modules, F2, F3, the C2b PL verifier, the
consumer inputs, the qualification's pinned files, the A0 certificates of QC06) with its sha256 and its git blob at
HEAD. It writes nothing else.

    python3.14 -I -S -B mb308_manifest.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
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

sys.path.insert(1, str(NS / "tests"))
import mb308_qualify as QF  # noqa: E402
import test_mb308_a0 as TA  # noqa: E402

OUT = NS / "protocol" / "MB308_FREEZE.json"


def blob(b: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def namespace_files() -> list:
    """Every file of the namespace that the freeze covers (the manifest itself and post-freeze directories excluded)."""
    out = []
    for p in sorted(NS.rglob("*")):
        rel = p.relative_to(NS).parts
        if p.is_file() and p != OUT and "__pycache__" not in p.parts and rel[0] not in D.POST_FREEZE_DIRS:
            out.append(p)
    return out


def external_pins() -> dict:
    """Every pinned external file: key -> (repo-relative path, pinned sha256 or None)."""
    ext = {f"module:{k}": (v[0], v[1]) for k, v in PIN.PINS.items()}
    ext["module:F2_mb_independent"] = PIN.INDEP_PIN[:2]
    ext["module:F3_tuple_independent"] = PIN.TUPLE_PIN[:2]
    if PIN.C2B_PL_HOOK:
        ext["module:vd_pl"] = PIN.C2B_PL_HOOK[:2]
    ext.update({f"input:{k}": (v[0], v[1]) for k, v in D.CON.PINS.items()})
    ext["qualify:mc"] = QF.MC_PIN[:2]
    ext["qualify:assembly_E4"] = QF.E4_PIN[:2]
    ext["qualify:tail_patterns"] = QF.PATTERNS_PIN[:2]
    ext["qualify:theory_research"] = (QF.THEORY_RESEARCH[0], QF.THEORY_RESEARCH[2])
    ext["qc06:r_eval"] = TA.R_EVAL_PIN[:2]
    certs = TA.A0_CERTS.relative_to(REPO)
    ext["qc06:A0_CERTS_MANIFEST"] = (str(certs / "CERTS_MANIFEST.json"), None)
    for case in TA.BYTE_CASES:
        for f in case[3:]:
            if f:
                ext[f"qc06:{f}"] = (str(certs / f), None)
    return ext


def external_files() -> dict:
    out = {}
    for key, (rel, pin) in sorted(external_pins().items()):
        raw = (REPO / rel).read_bytes()
        got = hashlib.sha256(raw).hexdigest()
        head = subprocess.run(["/usr/bin/git", "-C", str(REPO), "rev-parse", f"HEAD:{rel}"], capture_output=True,
                              text=True).stdout.strip()
        if (pin is not None and got != pin) or head != blob(raw):
            raise SystemExit(f"manifest refused: {rel} differs from its pin or from its committed blob")
        out[key] = {"path": rel, "sha256": got, "git_blob": head}
    return out


def manifest() -> dict:
    files = {}
    for p in namespace_files():
        raw = p.read_bytes()
        files[str(p.relative_to(REPO))] = {"sha256": hashlib.sha256(raw).hexdigest(), "git_blob": blob(raw)}
    return {
        "schema": "rebaseguard.p5y.k5.cell308-mb-r1.freeze-manifest.v1",
        "cell": D.TARGET_CELL, "route": "MB", "scope": "CLOSURE_ONLY", "frozen_dirs": list(D.FROZEN_DIRS),
        "post_freeze_dirs": list(D.POST_FREEZE_DIRS), "frozen_files": files, "external_files": external_files(),
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
