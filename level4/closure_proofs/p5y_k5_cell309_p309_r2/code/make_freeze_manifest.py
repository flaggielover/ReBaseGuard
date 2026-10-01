"""Build freeze/P309_FREEZE_MANIFEST.json: the FC1 pin set (package rev. 2b section A 'pins' + section J FC1, as amended).

  python3 code/make_freeze_manifest.py [--check]

--check recomputes the manifest and compares it with the committed file (exit 0 iff identical, apart from `built_utc`).

Every pin carries the path, the sha256 of the bytes, and the git blob id.  Data files are HASHED ONLY: their bytes are
read into hashlib and never parsed or displayed.  The data paths are taken from the reviewed rev. 2b candidate
manifest (research protocol_prep/P309_CANDIDATE_FREEZE_MANIFEST.json, data_pins_blob_only), by position, with a
name-shape assertion, plus the four pins that the rev. 2b open items name (K1 record manifest, C2 forecast record for
the historical control, floor r2 configuration, consumption adapter code).
"""
from __future__ import annotations

import datetime
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
REPO = FNS.parents[2]
sys.path.insert(0, str(FNS / "code"))
import p309_guard as G  # noqa: E402

CP = "level4/closure_proofs/"
NS_REL = CP + "p5y_k5_cell309_p309_r2/"
RNS_REL = CP + "p5y_k5_cell309_research_r1/"
CANDIDATE = RNS_REL + "protocol_prep/P309_CANDIDATE_FREEZE_MANIFEST.json"
OUT_REL = NS_REL + "freeze/P309_FREEZE_MANIFEST.json"
FROZEN_DIRS = ("code", "config", "fc2", "freeze", "tests", "verify", "governance")
EXCLUDE = {OUT_REL}
# candidate data pins by position: (role, name prefix)
CANDIDATE_ROLES = [("tct_inputs_target", "TCT_INPUTS_"), ("adopted_inputs", "ADOPTED_TAIL"),
                   ("registry_c1", "REGISTRY_C1"), ("registry_c2", "REGISTRY_C"), ("cells_json", "cells.json"),
                   ("coverage_r5", "K5_COVERAGE_MAP_R5"), ("floor_r2_spec", "FLOOR_R2_SPECIFICATION")]
EXTRA_DATA = [("record_manifest", CP + "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json"),
              ("c2_forecast", CP + "p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json"),
              ("floor_r2_rule", CP + "p5y_k5_tail_floor_r2/config/K5_TAIL_ADOPTION_FLOOR_R2.json")]
EXTRA_CODE = [CP + "p5y_k5_m5_tail_closure/code/tct_rule.py", CP + "p5y_k5_m5_tail_closure/code/tail_forecast_r2.py",
              CP + "p5y_k5_lower_front_order3/code/tc_rule.py", CP + "p5y_k5_lower_front_order3/code/tc_crosscheck.py",
              CP + "p5y_k5_tail_c2_closure/code/c2_d5_forecast.py",
              CP + "p5y_k5_perron_deflated_resolvent/code/deflated_consume.py",
              CP + "p5y_k5b_consumption_adapter/code/consumption_adapter.py",
              CP + "p5y_k5_cell307_rlr_r1/code/rlr307_stage1.py",
              CP + "p5y_k5_cell307_rlr_r1/code/rlr307_independent.py",
              CP + "p5y_k5_cell307_rlr_r1/code/rlr307_pinned.py",
              CP + "p5y_k5_tail_overnight_research/validation/C1B_R2_CODE_PINS.json",
              # QC03's research test (test_srk_fsm_truth) imports these overnight cell-309-stream modules; they are
              # read in the archive mirror only, and pinned so that qualification runs on frozen bytes (dry run)
              CP + "p5y_k5_tail_overnight_research/code/ov_fixtures.py",
              CP + "p5y_k5_tail_overnight_research/code/ov_quarantine.py",
              CP + "p5y_k5_tail_overnight_research/streams/D_309/code/d309_core.py",
              CP + "p5y_k5_tail_overnight_research/streams/D_309/code/d309_rso.py"]
C1B_DIR = CP + "p5y_k5_tail_overnight_research/streams/C_308/LR/cusum/"
C1B_LOAD_ORDER = ("c1b_gauss", "c1b_kernel", "c1b_float", "c1b_pw", "c1b_prov", "c1b_certpw")


def git(*a) -> str:
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, check=True).stdout


def pin(rel: str, role: str | None = None) -> dict:
    raw = (REPO / rel).read_bytes()
    d = {"path": rel, "sha256": hashlib.sha256(raw).hexdigest(),
         "git_blob": hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()}
    if role:
        d["role"] = role
    return d


def build() -> dict:
    tracked = set(git("ls-files", NS_REL).split()) | set(git("ls-files", "--others", "--exclude-standard", NS_REL).split())
    tracked = {p for p in tracked if "__pycache__" not in p}
    code = [p for p in sorted(tracked) if p.split("/")[3] in FROZEN_DIRS and p not in EXCLUDE]
    cand = json.loads((REPO / CANDIDATE).read_bytes())
    code += [p["path"] for p in cand["code_pins"]]
    code += EXTRA_CODE + [C1B_DIR + n + ".py" for n in C1B_LOAD_ORDER]
    seen, code_pins = set(), []
    for rel in code:
        if rel not in seen:
            seen.add(rel)
            code_pins.append(pin(rel))
    data = []
    dp = cand["data_pins_blob_only"]
    if len(dp) != len(CANDIDATE_ROLES):
        raise SystemExit("the candidate manifest's data pins changed shape")
    for (role, prefix), p in zip(CANDIDATE_ROLES, dp):
        if not Path(p["path"]).name.startswith(prefix):
            raise SystemExit(f"candidate data pin for {role} has an unexpected name")
        d = pin(p["path"], role)
        if d["git_blob"] != p["git_blob"]:
            raise SystemExit(f"data pin {role}: bytes differ from the reviewed candidate blob")
        data.append(d)
    data += [pin(rel, role) for role, rel in EXTRA_DATA]
    return {"schema": "P309_FREEZE_MANIFEST/1",
            "built_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "built_at_head": git("rev-parse", "HEAD").strip(),
            "candidate_manifest": pin(CANDIDATE),
            "runtime": dict(runtime_identity(), platform=f"{sys.platform} {platform.machine()}",
                            host_id_sha256=G.host_id(), stdlib_only=True, workers_max=4),
            "verifier_settings": {"taylor_order_N": 8, "max_depth": 24, "procs": 1},
            "code_pins": code_pins, "data_pins": data}


def runtime_identity() -> dict:
    """the runtime the driver's check_bindings compares (r2 delta review C14; P15): the python version and
    implementation, glibc, and the sha256 of the real interpreter binary.  The same computation as
    p309_driver.runtime_identity (tests/test_p309_host_controls.py checks that both agree)."""
    import os
    try:
        glibc = os.confstr("CS_GNU_LIBC_VERSION")
    except (AttributeError, ValueError, OSError):
        glibc = None
    try:
        with open(os.path.realpath(sys.executable), "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        digest = None
    return {"python": platform.python_version(), "implementation": platform.python_implementation(), "glibc": glibc,
            "interpreter_sha256": digest}


if __name__ == "__main__":
    m = build()
    out = REPO / OUT_REL
    if "--check" in sys.argv:
        old = json.loads(out.read_bytes())
        same = {k: v for k, v in old.items() if k not in ("built_utc", "built_at_head")} == {
            k: v for k, v in m.items() if k not in ("built_utc", "built_at_head")}
        print("MANIFEST", "IDENTICAL" if same else "DIFFERS")
        sys.exit(0 if same else 1)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
    print(f"{len(m['code_pins'])} code pins, {len(m['data_pins'])} data pins -> {OUT_REL}")
