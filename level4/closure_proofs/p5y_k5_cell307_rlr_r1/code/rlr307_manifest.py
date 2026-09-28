"""Cell-307 RLR campaign (r1) -- write the freeze manifest `protocol/RLR307_FREEZE.json` (the input manifest the grant
binds by sha256). Run once, immediately before the freeze commit; it lists every frozen file (sha256 and git blob id),
every external pin of the driver and of the certifier loader, the frozen rules and the governance anchors.

    python3.14 -I -S -B rlr307_manifest.py
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
import rlr307_driver as D  # noqa: E402
import rlr307_pinned as PIN  # noqa: E402
import rlr307_stage1 as S1  # noqa: E402

OUT = NS / "protocol" / "RLR307_FREEZE.json"
FROZEN_DIRS = D.FROZEN_DIRS


def blob(b: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def main() -> int:
    files = {}
    for d in FROZEN_DIRS:
        for p in sorted((NS / d).rglob("*")):
            if p.is_file() and p != OUT and "__pycache__" not in p.parts:
                raw = p.read_bytes()
                files[str(p.relative_to(REPO))] = {"sha256": hashlib.sha256(raw).hexdigest(), "git_blob": blob(raw)}
    rev = subprocess.run(["/usr/bin/git", "-C", str(REPO), "log", "-1", "--format=%H", "--",
                          D.NS_REL + "/review/INCIDENT_INDEPENDENCE_REVIEW.md"], capture_output=True, text=True).stdout.strip()
    review_text = (NS / "review/INCIDENT_INDEPENDENCE_REVIEW.md").read_text().splitlines()
    man = {
        "schema": "rebaseguard.p5y.k5.cell307-rlr-r1.freeze-manifest.v1",
        "cell": D.TARGET_CELL, "route": "RLR", "scope": "CLOSURE_ONLY",
        "frozen_dirs": list(FROZEN_DIRS), "frozen_files": files,
        "driver": {"path": D.NS_REL + "/code/rlr307_driver.py",
                   "sha256": hashlib.sha256((CODE / "rlr307_driver.py").read_bytes()).hexdigest()},
        "helper_sha256": D.HELPER_SHA256,
        "certifier_pins": {n: {"path": PIN.CUSUM_REL + n + ".py", "sha256": s, "git_blob_prefix": b}
                           for n, (s, b) in PIN.PINNED.items()},
        "certifier_flags": PIN.FLAGS,
        "consumer_and_input_pins": {k: {"path": v[0], "sha256": v[1], "git_blob_prefix": v[2]} for k, v in D.PINS.items()},
        "lineage": D.LINEAGE,
        "stage1_rules": {"sub_block_max_width": str(S1.SUB_BLOCK_MAX_WIDTH), "hull_bits": S1.HULL_BITS,
                         "ladder": list(S1.LADDER), "cell_composition": "componentwise max over blocks of A1/A2_SUPPLY",
                         "ladder_composition": "c1b_certpw.run_point: LADDER_KEYS_MIN min, LADDER_KEYS_MAX max, assemble"},
        "stage2": {"supply": "S_RLR = (A0_I1, min(A1_I1, A1_cell), min(A2_I1, A2_cell))",
                   "consumer": "C2 frozen path (c2_d5_forecast.direct via tail_forecast_r2 / tct_rule / adapter)",
                   "closure_criterion": "consumer pass: Gamma(5, 307; S_RLR) < 0 in exact rationals (Gamma = 0 is NOT closed)"},
        "outcome_table": {
            "TARGET_EVALUATED + pass True": "CELL307_CLOSED_UNDER_RLR",
            "TARGET_EVALUATED + pass False (Gamma >= 0)": "CELL307_NOT_CLOSED_UNDER_RLR",
            "TARGET_EVALUATED + Stage 1 CERTIFICATION_FAILED": "CELL307_NOT_CLOSED_UNDER_RLR (RLR_CERTIFICATION_FAILED)",
            "any post-marker failure status": "CELL307_EXECUTION_INDETERMINATE",
            "CONTROL_FAILED": "no conclusion; target not consumed; STOP"},
        "caps": {"pre_marker_s": D.PRE_CAP_S, "evaluation_s": D.EVAL_CAP_S, "workers": D.WORKERS},
        "exactly_once": {"marker": D.CONSUMED_REF, "pending": D.PENDING_REF, "result": D.RESULT_REL,
                         "emergency_file": D.EMERGENCY_NAME, "qualified_worktree": D.QUALIFIED_WORKTREE,
                         "qualified_branch": D.QUALIFIED_BRANCH},
        "incident_independence_review": {"path": D.NS_REL + "/review/INCIDENT_INDEPENDENCE_REVIEW.md", "commit": rev,
                                         "line2": review_text[1] if len(review_text) > 1 else None},
        "governance_anchors": {"start_state": D.NS_REL + "/evidence/start/START_STATE.json",
                               "incident_audit": D.NS_REL + "/audit/INCIDENT_AUDIT_RLR307.md",
                               "incident_addendum": D.NS_REL + "/audit/INCIDENT_AUDIT_ADDENDUM_R1.md",
                               "overnight_handover": "7f45e048c39023f4805b21a461650fd332af951f"},
    }
    OUT.write_text(json.dumps(man, indent=1, sort_keys=True) + "\n")
    print(f"wrote {OUT.relative_to(REPO)}: {len(files)} frozen files; sha256 "
          f"{hashlib.sha256(OUT.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
