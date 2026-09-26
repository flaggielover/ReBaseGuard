"""K1R4 SR bridge production entry. ORCHESTRATION ONLY - no scientific algebra lives here.

admit(index) is the production entry path up to, but excluding, the decisive patch solve: it
enforces freeze identity, authorization, runtime, ownership and registry acceptance, reconstructs
geometry and identity, builds the obligation universe and the T3 inputs. run_cell() then hands the
admitted task to the GENERATED k1r4_bridge_cellseq.run_group (frozen worker text).
"""
import hashlib
import json
import platform
import sys
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CFG = NS / "config"
PROD = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod-gen2")
PS1 = PROD / "level4/closure_proofs/p5y_k1_ps1_production"


class BridgeRefused(RuntimeError):
    pass


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _j(name) -> dict:
    return json.loads((CFG / name).read_text())


def setup_path() -> None:
    auth = json.loads((PS1 / "config/LAUNCH_AUTHORIZATION.json").read_text())
    for p in [str(NS / "driver")] + [str(PROD / r) for r in auth["pythonpath_rel"]] + [str(PS1 / "driver")]:
        if p not in sys.path:
            sys.path.append(p)


def host_facts() -> dict:
    try:
        vendor = Path("/sys/class/dmi/id/sys_vendor").read_text().strip()
    except OSError:
        vendor = "UNKNOWN"
    return {"sys_vendor": vendor, "python": sys.executable, "node": platform.node()}


def verify_freeze() -> dict:
    cp = _j("CHECKPOINT.json")
    if _sha(CFG / "CHECKPOINT.json") != (CFG / "CHECKPOINT_HASH").read_text().strip():
        raise BridgeRefused("CHECKPOINT does not match its frozen hash")
    drift = [n for n, h in cp["frozen_artifacts"].items() if _sha(CFG / n) != h]
    drift += [n for n, h in cp["generated_stages"].items() if _sha(NS / "driver" / n) != h]
    if drift:
        raise BridgeRefused(f"frozen artifact / generated stage drift: {drift}")
    return cp


def admit(index, *, role="AWS", host=None, task_kind="SCIENCE", handoff=False,
          successor_cells_sha256=None) -> dict:
    cp = verify_freeze()
    authz, owners = _j("SR_BRIDGE_AUTHORIZATION.json"), _j("SR_BRIDGE_OWNERSHIP.json")["owners"]
    rt = _j("RUNTIME_CONTRACT.json")["SR_BRIDGE"]
    host = host or host_facts()
    if role != authz["role"]:
        raise BridgeRefused(f"role {role!r} is not authorised (AWS only; no Vultr substitution)")
    if host["sys_vendor"] != rt["sys_vendor"]:
        raise BridgeRefused(f"host vendor {host['sys_vendor']!r} is not the qualified AWS runtime")
    if task_kind != "SCIENCE":
        raise BridgeRefused("synthetic task kinds are prohibited for bridge production")
    if handoff:
        raise BridgeRefused("handoff paths are prohibited for the AWS-only bridge")
    if not isinstance(index, int) or str(index) not in owners:
        raise BridgeRefused(f"cell {index!r} is not in the bridge ownership map")
    if owners[str(index)] != role:
        raise BridgeRefused(f"cell {index} is owned by {owners[str(index)]}, not {role}")
    setup_path()
    import k1r4_bridge_cells as SC
    SC.set_mode("BRIDGE")
    import k1r4_bridge_t3 as S3
    import k1r4_bridge_t5 as S5
    import sr_o9_candidates as T
    if successor_cells_sha256 is not None and successor_cells_sha256 != SC.table_sha256():
        raise BridgeRefused("task binds a successor-cell table hash that is not the bridge table")
    rec = SC.cell(index)
    SC.validate(rec)
    with T.scientific_precision():
        g = SC.geometry(rec)
        cands, hashes, C, e0, clsha = S3.cell_inputs(index)
    ident = SC.identity(rec)
    declared = _j("SR_BRIDGE_UNIVERSE.json")["cells"][rec["id"]]["units"]
    built = [[u[0], rec["id"], u[2], u[3]]
             for u in S5.universe.work_ids(cells=[SC.universe_carrier(rec)]) if u[2] != "far_field"]
    if sorted(map(tuple, built)) != sorted(map(tuple, declared)) or len(built) != 28:
        raise BridgeRefused(f"cell {index}: obligation universe does not match the frozen declaration")
    return {"index": index, "id": rec["id"], "record": rec, "geometry": g, "identity": ident,
            "C_upper": C, "e0_ball": e0, "candidate_list_sha256": clsha, "candidates": len(cands),
            "universe_units": len(built), "bridge_table_sha256": SC.table_sha256(),
            "producer_identity_sha256": authz["producer_identity_sha256"],
            "checkpoint_sha256": (CFG / "CHECKPOINT_HASH").read_text().strip(), "host": host}


def run_cell(index, evidence_dir, task_id):
    """PRODUCTION ONLY. Not called during qualification."""
    adm = admit(index)
    import k1r4_bridge_cellseq as W
    ps1a = json.loads((PS1 / "config/LAUNCH_AUTHORIZATION.json").read_text())
    live = PROD / ps1a["live_patches_path"]
    task = {"cells": [index], "live_patches": str(live), "expect_patches": ps1a["live_patches_count"],
            "live_patches_sha256": ps1a["live_patches_sha256"],
            "successor_cells_sha256": adm["bridge_table_sha256"], "evidence_dir": str(evidence_dir),
            "task_id": task_id}
    return W.run_group(task)
