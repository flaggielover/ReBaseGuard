"""PS1 downstream assembly successor: AWS-ONLY local complete-shard route.

The genuine PS1 SR campaign finished 369/369 cells on a single host under the frozen
topology A_AWS_ONLY. The frozen assembler (prodctl.assemble) cannot consume it:

  1. it accepts only role VULTR, because it was written for the historical
     AWS -> VULTR authenticated-handoff topology; and
  2. its accounting identity is committed == records + settlement charges, which has
     no term for the generation-2 imported predecessor accounting seed (92.32 CPU-h).

This module is ADDITIVE. It never writes to production evidence, never touches either
historical ledger, and never re-runs science. It selects the assembly route from the
FROZEN authorization + shard manifest and, for AWS_ONLY, performs the local
complete-shard assembly over the frozen aggregation function. MULTI_HOST is deliberately
NOT reimplemented here: it still belongs to the untouched frozen handoff path.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
from pathlib import Path

SCHEMA = "rebaseguard.p5y.k1.ps1.aws-only-assembly.v1"
ROUTE_AWS_ONLY = "AWS_ONLY"
ROUTE_MULTI_HOST = "MULTI_HOST"
FROZEN_AWS_ONLY_TOPOLOGY = "A_AWS_ONLY"
FAR_FIELD_WORK_ID = "SR:-1:far_field:all_m"
OBLIGATIONS_PER_CELL = 28
ACCOUNTING_TOL = 1e-6          # same tolerance as the frozen reconcile()
IMPORT_ROUNDING_TOL = 0.01     # the import is the predecessor measurement rounded UP
MULTI_HOST_ENTRY = "ops/prodctl.py assemble --role VULTR (frozen recovery namespace)"


class AssemblyRefusal(Exception):
    """Fail closed. Never downgrade a refusal into a warning."""


def frozen_gate(module_obj, fn, *args, **kwargs):
    """Run a FROZEN gate and translate its refusal into ours.

    The frozen modules raise their own refusal types (ProvenanceRefusal,
    MultiHostRefusal, ProductionRefusal). A caller that only catches
    AssemblyRefusal would see those escape as an unhandled exception -- a crash
    instead of a clean, fail-closed refusal. The frozen verdict is preserved verbatim.
    """
    names = ("ProvenanceRefusal", "MultiHostRefusal", "ProductionRefusal")
    frozen_types = tuple(t for m in module_obj for n in names
                         if isinstance(t := getattr(m, n, None), type))
    try:
        return fn(*args, **kwargs)
    except frozen_types as e:                       # noqa: B030
        raise AssemblyRefusal(f"{type(e).__name__}: {e}") from e


def sha256_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_json(p):
    return json.loads(Path(p).read_text())


def load_frozen(production_root: str, namespace: str):
    """Import the FROZEN production driver modules; never vendor copies of them."""
    import sys
    drv = str(Path(production_root) / namespace / "driver")
    if drv not in sys.path:
        sys.path.insert(0, drv)
    import multihost as M          # noqa: E402
    import production_provenance as PP  # noqa: E402
    import production_launcher as PL    # noqa: E402
    return PL, PP, M


# ------------------------------------------------------------------ route
def select_route(auth: dict, shard: dict) -> str:
    """Route from frozen evidence only. Unknown or self-inconsistent -> refuse."""
    topo_a, topo_s = auth.get("topology"), shard.get("topology")
    if topo_a != topo_s:
        raise AssemblyRefusal(
            f"topology disagreement: authorization {topo_a!r} != shard manifest {topo_s!r}")
    ho = auth.get("handoff") or {}
    fp, status = ho.get("public_key_fingerprint"), str(ho.get("status", ""))
    others = {h: len((shard.get(h) or {}).get("cells", []))
              for h in shard if isinstance(shard.get(h), dict) and "cells" in shard[h]}
    aws_cells = others.get("AWS", 0)
    remote_cells = sum(n for h, n in others.items() if h != "AWS")
    total = shard.get("cells_total")

    if topo_a == FROZEN_AWS_ONLY_TOPOLOGY:
        if remote_cells:
            raise AssemblyRefusal(
                f"topology {topo_a} but {remote_cells} cell(s) are owned off-AWS")
        if aws_cells != total:
            raise AssemblyRefusal(
                f"topology {topo_a} but AWS owns {aws_cells}/{total} cells")
        if fp is not None or not status.startswith("NOT_USED"):
            raise AssemblyRefusal(
                f"topology {topo_a} but the authorization carries handoff material "
                f"(fingerprint={fp!r}, status={status!r})")
        return ROUTE_AWS_ONLY

    if isinstance(fp, str) and fp and remote_cells > 0:
        return ROUTE_MULTI_HOST

    raise AssemblyRefusal(
        f"unknown or inconsistent topology {topo_a!r} (handoff fingerprint={fp!r}, "
        f"AWS cells={aws_cells}, remote cells={remote_cells}): failing closed")


# ------------------------------------------------------------- shard gates
def gate_ownership(auth: dict, shard: dict, M) -> dict:
    """Complete local ownership of the FROZEN shard."""
    aws = sorted((shard.get("AWS") or {}).get("cells", []))
    if aws != list(range(M.TOTAL_CELLS)):
        raise AssemblyRefusal(
            f"AWS does not own the complete frozen shard: {len(aws)}/{M.TOTAL_CELLS}")
    if shard.get("cells_total") != M.TOTAL_CELLS:
        raise AssemblyRefusal(
            f"shard manifest cells_total {shard.get('cells_total')} != frozen {M.TOTAL_CELLS}")
    return {"owners": {c: "AWS" for c in aws}, "cells": len(aws)}


def gate_ledger_state(ledger: dict, ops_field: str = "operational_lifecycle") -> dict:
    """369 unique completed, nothing pending, nothing open, nothing unsettled, no halt."""
    comp = ledger.get("completed_cells") or {}
    ids = [int(k) for k in comp]
    if len(ids) != len(set(ids)):
        raise AssemblyRefusal("duplicate cell ids in the ledger")
    if ledger.get("open_reservations"):
        raise AssemblyRefusal(
            f"{len(ledger['open_reservations'])} open reservation(s) remain")
    if ledger.get("remote_completed_cells"):
        raise AssemblyRefusal("AWS_ONLY route: the ledger carries remote completed cells")
    ops = ledger.get(ops_field)
    if not ops:
        raise AssemblyRefusal("ledger carries no operational lifecycle block")
    if ops.get("halt"):
        raise AssemblyRefusal(f"active generation is HALTED: {ops['halt']}")
    unsettled = sorted(r for r, v in (ops.get("runs") or {}).items()
                       if v.get("status") != "SETTLED")
    if unsettled:
        raise AssemblyRefusal(f"unsettled run(s): {unsettled}")
    torn = ops.get("torn_attempts") or {}
    return {"completed": len(ids), "runs": len(ops.get("runs") or {}),
            "settlements": len(ops.get("settlements") or []), "torn_attempts": torn}


def gate_campaign_lock(runtime_dir: str) -> str:
    """Read-only probe: the campaign lock must be FREE (no producer may be live)."""
    p = Path(runtime_dir) / "campaign.lock"
    if not p.exists():
        raise AssemblyRefusal(f"campaign lock {p} does not exist")
    with open(p, "r+") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise AssemblyRefusal("campaign lock is HELD: a producer is still live")
        fcntl.flock(f, fcntl.LOCK_UN)
    return "FREE"


def scientific_content_hash(ev: dict, M) -> str:
    """Recompute the frozen scientific-content identity from the evidence on disk."""
    t3 = read_json(ev["t3"]["path"])
    t4 = read_json(ev["t4"]["path"])
    t5 = read_json(ev["t5"]["path"])
    return hashlib.sha256(M.canonical({
        "t3_record_sha256": t3["t3_record_sha256"],
        "t4_record_sha256": t4["t4_record_sha256"],
        "t5_certificate_hashes": [o["certificate_hash"] for o in t5["obligations"]],
    }) + b"\n").hexdigest()


def verify_cell(rec: dict, cell_file: Path, owners: dict, auth: dict, auth_hash: str,
                M, PP) -> dict:
    """Frozen record gate + provenance gate + evidence re-hash + obligations."""
    cid = rec.get("cell_id")
    frozen_gate((M, PP), M.validate_record, rec, "AWS", owners,
                auth["producer_commit"], auth["checkpoint_sha256"])
    frozen_gate((M, PP), PP.verify, rec, production_authorization_hash=auth_hash,
                scientific_adapter_hash=auth["scientific_adapter_hash"])
    if cell_file.exists() and read_json(cell_file) != rec:
        raise AssemblyRefusal(f"cell {cid}: sealed file differs from the ledger record")
    ev = rec.get("evidence") or {}
    if set(ev) != {"t3", "t4", "t5", "patches_gz"}:
        raise AssemblyRefusal(f"cell {cid}: unexpected evidence set {sorted(ev)}")
    for k, v in ev.items():
        p = Path(v["path"])
        if not p.exists():
            raise AssemblyRefusal(f"cell {cid}: evidence {k} missing at its bound path {p}")
        if sha256_file(p) != v["sha256"]:
            raise AssemblyRefusal(f"cell {cid}: evidence {k} does not match its sealed sha256")
    t5 = read_json(ev["t5"]["path"])
    if not (t5.get("status") == "T5_28_OF_28_PASS" and t5.get("pass_count") == OBLIGATIONS_PER_CELL
            and t5.get("total") == OBLIGATIONS_PER_CELL and t5.get("cell") == cid
            and t5.get("obligation_ids_equal_frozen_universe") is True
            and t5.get("provenance_chain_verified") is True
            and all(o.get("status") == "PASS" for o in t5["obligations"])):
        raise AssemblyRefusal(f"cell {cid}: T5 does not certify {OBLIGATIONS_PER_CELL}/28")
    if rec.get("obligations_completed") != OBLIGATIONS_PER_CELL:
        raise AssemblyRefusal(f"cell {cid}: obligations_completed != {OBLIGATIONS_PER_CELL}")
    if scientific_content_hash(ev, M) != rec["scientific_content_hash"]:
        raise AssemblyRefusal(f"cell {cid}: scientific content hash does not recompute")
    if rec["production_provenance"]["certificate_digest"] != ev["t5"]["sha256"]:
        raise AssemblyRefusal(f"cell {cid}: certificate digest != sealed t5 hash")
    return {"cell_id": cid, "task_id": rec["task_id"],
            "evidence_root": str(Path(ev["t5"]["path"]).parents[2])}


def gate_far_field(auth: dict, contract_parent: dict, cells: int) -> dict:
    """The far field is a SEPARATE, inherited obligation: 28*cells + 1 == global universe."""
    ff = auth.get("far_field_obligation") or {}
    if ff.get("work_id") != FAR_FIELD_WORK_ID:
        raise AssemblyRefusal(f"far-field work id {ff.get('work_id')!r} is not frozen")
    status = str(ff.get("status", ""))
    if not status.startswith("INHERITED"):
        raise AssemblyRefusal(f"far-field obligation is not INHERITED: {status!r}")
    campaign = OBLIGATIONS_PER_CELL * cells
    declared = contract_parent.get("obligations")
    if declared != campaign + 1:
        raise AssemblyRefusal(
            f"global obligations {declared} != campaign {campaign} + 1 inherited far field")
    return {"work_id": ff["work_id"], "status": status, "units": 1,
            "campaign_obligations": campaign, "global_obligations": declared}


def gate_executor_manifest(auth: dict, production_root: str) -> dict:
    """The scientific executor must be bit-identical to the authorised manifest."""
    root = Path(production_root)
    pinned = auth["executor_source_sha256"]
    drift = [f for f in auth["executor_source_manifest"]
             if not (root / f).exists() or sha256_file(root / f) != pinned[f]]
    if drift:
        raise AssemblyRefusal(f"scientific executor drift: {drift[:4]}")
    integrated = hashlib.sha256(json.dumps(
        {f: pinned[f] for f in sorted(pinned)}, sort_keys=True,
        separators=(",", ":")).encode()).hexdigest()
    if integrated != auth["scientific_adapter_hash"]:
        raise AssemblyRefusal("integrated executor manifest digest != authorised adapter hash")
    return {"files": len(auth["executor_source_manifest"]), "drift": [],
            "integrated_source_manifest_sha256": integrated}


# -------------------------------------------------------------- accounting
def reconcile_with_import(ledger: dict, recs: list, contract: dict, transition: dict,
                          predecessor_ledger: Path, M,
                          ops_field: str = "operational_lifecycle") -> dict:
    """committed == scientific records + operational charges + imported predecessor CPU.

    Every term comes from frozen or ledger evidence; there is no balancing residual.
    """
    ops = ledger[ops_field]
    science = M.per_host_cpu_h(recs)
    charges = sum(s["charge_cpu_h"] for s in ops.get("settlements") or [])
    committed = ledger["committed_cpu_h_by_role"].get("AWS")
    if committed is None:
        raise AssemblyRefusal("ledger carries no committed AWS CPU-h")

    imp = (transition.get("accounting_import") or {})
    imported = imp.get("predecessor_science_cpu_h")
    if not isinstance(imported, (int, float)):
        raise AssemblyRefusal(
            "generation transition record declares no imported predecessor CPU term")
    gen = contract.get("execution_generation") or {}
    if gen.get("imported_science_cpu_h") != imported:
        raise AssemblyRefusal(
            f"imported CPU disagreement: contract {gen.get('imported_science_cpu_h')} "
            f"!= transition record {imported}")
    if imp.get("seeded_into_generation_2_as") != "committed_cpu_h_by_role.AWS":
        raise AssemblyRefusal("transition record does not seed the import into committed CPU-h")

    # the import was seeded BEFORE any science: the first run opens at exactly that value
    runs = ops.get("runs") or {}
    if not runs:
        raise AssemblyRefusal("ledger carries no runs")
    first = min(runs.values(), key=lambda r: r.get("committed_start", float("inf")))
    if first.get("completed_start"):
        raise AssemblyRefusal("the earliest run already carried completed cells")
    if abs(first.get("committed_start", -1) - imported) > ACCOUNTING_TOL:
        raise AssemblyRefusal(
            f"earliest run opened at {first.get('committed_start')} != imported {imported}")

    # the predecessor ledger is the authority for the measurement behind the import
    if sha256_file(predecessor_ledger) != gen.get("predecessor_ledger_sha256"):
        raise AssemblyRefusal("predecessor ledger is not the frozen historical ledger")
    pred = read_json(predecessor_ledger)
    if pred.get("completed_cells"):
        raise AssemblyRefusal(
            "predecessor ledger carries completed cells: the import would double-count science")
    measured = pred["committed_cpu_h_by_role"].get("AWS", 0.0)
    if not (0.0 <= imported - measured <= IMPORT_ROUNDING_TOL):
        raise AssemblyRefusal(
            f"imported {imported} is not the predecessor measurement {measured} rounded up")

    total = science + charges + imported
    if abs(committed - total) > ACCOUNTING_TOL:
        raise AssemblyRefusal(
            f"accounting does not reconcile: committed {committed} != records {science} + "
            f"charges {charges} + imported {imported} (delta {committed - total})")
    return {"scientific_record_cpu_h": science, "settlement_or_operational_cpu_h": charges,
            "imported_predecessor_cpu_h": imported, "committed_cpu_h": committed,
            "identity_residual_cpu_h": committed - total, "tolerance": ACCOUNTING_TOL,
            "predecessor_measured_cpu_h": measured,
            "import_counted_once": True}


def gate_cap(committed: float, contract_parent: dict, M) -> dict:
    gov = contract_parent["governed_overhead_cpu_h"]
    cap = contract_parent["global_cpu_cap"]
    g = frozen_gate((M,), M.gate_global_cap, {"AWS": committed}, gov)
    if g["cap"] != cap:
        raise AssemblyRefusal(f"frozen cap {g['cap']} != authorised {cap}")
    if not g["charged_cpu_h"] < cap:
        raise AssemblyRefusal(f"charged {g['charged_cpu_h']} is not below the cap {cap}")
    return {"charged_cpu_h": g["charged_cpu_h"], "cap_cpu_h": g["cap"],
            "headroom_cpu_h": g["headroom_cpu_h"], "cap_refusal": None,
            "governed_overhead_cpu_h": gov, "overhead_factor": g["overhead_factor"]}


# --------------------------------------------------------------- preflight
def load_inputs(acfg: dict) -> dict:
    """Resolve every frozen input from the assembly contract. Read-only."""
    cpath = Path(acfg["operational_contract_path"])
    chash = Path(acfg["operational_contract_hash_path"]).read_text().strip()
    if sha256_file(cpath) != chash:
        raise AssemblyRefusal("operational contract does not match its frozen hash")
    contract = read_json(cpath)
    role = acfg.get("role", "AWS")
    spec = contract["hosts"][role]
    ns = contract["parent"]["namespace"]
    prod_ns = Path(spec["production_root"]) / ns
    PL, PP, M = load_frozen(spec["production_root"], ns)
    auth_path = prod_ns / "config/LAUNCH_AUTHORIZATION.json"
    auth = PL.load_production_authorization(
        path=auth_path, hash_path=prod_ns / "config/LAUNCH_AUTHORIZATION_HASH")
    auth_hash = sha256_file(auth_path)
    if auth_hash != contract["parent"]["production_authorization_sha256"]:
        raise AssemblyRefusal("authorization hash != the contract's bound authorization")
    shard_path = prod_ns / "config/SHARD_MANIFEST.json"
    if sha256_file(shard_path) != contract["parent"]["shard_manifest_sha256"]:
        raise AssemblyRefusal("shard manifest does not match its frozen hash")
    gen = contract["execution_generation"]
    ops_root = Path(spec["ops_root"])
    transition_path = ops_root / gen["transition_record"]
    if sha256_file(transition_path) != gen["transition_record_sha256"]:
        raise AssemblyRefusal("generation transition record does not match its frozen hash")
    return {"contract": contract, "spec": spec, "namespace": ns, "prod_ns": prod_ns,
            "PL": PL, "PP": PP, "M": M, "auth": auth, "auth_path": auth_path,
            "auth_hash": auth_hash, "shard": read_json(shard_path), "shard_path": shard_path,
            "transition": read_json(transition_path), "transition_path": transition_path,
            "ledger_path": prod_ns / "production/PRODUCTION_LEDGER.json",
            "cells_dir": prod_ns / "production/cells",
            "predecessor_ledger": Path(gen["predecessor_production_root"]) / ns
            / "production/PRODUCTION_LEDGER.json",
            "runtime_dir": spec["runtime_dir"]}


def preflight(acfg: dict) -> dict:
    """Full read-only pre-assembly verification. Raises AssemblyRefusal on any gate."""
    I = load_inputs(acfg)
    M, PP, PL, auth = I["M"], I["PP"], I["PL"], I["auth"]
    route = select_route(auth, I["shard"])
    if route != ROUTE_AWS_ONLY:
        raise AssemblyRefusal(
            f"route {route}: this successor implements the AWS_ONLY route only; "
            f"the authenticated handoff route remains {MULTI_HOST_ENTRY}")
    own = gate_ownership(auth, I["shard"], M)
    ledger = read_json(I["ledger_path"])
    state = gate_ledger_state(ledger)
    lock = gate_campaign_lock(I["runtime_dir"])
    comp = ledger["completed_cells"]
    ids = sorted(int(k) for k in comp)
    if ids != list(range(M.TOTAL_CELLS)):
        missing = sorted(set(range(M.TOTAL_CELLS)) - set(ids))
        raise AssemblyRefusal(
            f"frozen cell coverage incomplete: {len(ids)}/{M.TOTAL_CELLS}, missing {missing[:6]}")
    keyed = [comp[str(c)].get("cell_id") for c in ids]
    if keyed != ids:
        dup = sorted({x for x in keyed if keyed.count(x) > 1})
        raise AssemblyRefusal(
            f"ledger key/record cell-id disagreement (duplicate or misfiled records: {dup[:6]})")
    recs, split = [], {}
    for c in ids:
        rec = comp[str(c)]
        info = verify_cell(rec, I["cells_dir"] / f"{c:04d}.json", own["owners"],
                           auth, I["auth_hash"], M, PP)
        recs.append(rec)
        split.setdefault(info["evidence_root"], []).append(c)
    succ_path = Path(I["spec"]["production_root"]) / auth["successor_cells_path"]
    if sha256_file(succ_path) != auth["successor_cells_sha256"]:
        raise AssemblyRefusal("frozen successor cell universe does not match its sealed hash")
    universe = read_json(succ_path)
    universe = universe["cells"] if isinstance(universe, dict) else universe
    if len(universe) != M.TOTAL_CELLS:
        raise AssemblyRefusal(f"frozen universe holds {len(universe)} cells")
    mism = [c for c in ids
            if (universe[c].get("successor_id") or universe[c].get("id"))
            != comp[str(c)]["successor_id"]
            or (universe[c].get("index") is not None and universe[c]["index"] != c)]
    if mism:
        raise AssemblyRefusal(f"successor identity mismatch at cells {mism[:5]}")
    far = gate_far_field(auth, I["contract"]["parent"], len(ids))
    executor = gate_executor_manifest(auth, I["spec"]["production_root"])
    acct = reconcile_with_import(ledger, recs, I["contract"], I["transition"],
                                 I["predecessor_ledger"], M)
    cap = gate_cap(acct["committed_cpu_h"], I["contract"]["parent"], M)
    obligations = sum(r["obligations_completed"] for r in recs)
    if obligations != OBLIGATIONS_PER_CELL * M.TOTAL_CELLS:
        raise AssemblyRefusal(f"campaign obligations {obligations} != "
                              f"{OBLIGATIONS_PER_CELL * M.TOTAL_CELLS}")
    return {"schema": SCHEMA, "route": route, "campaign_lock": lock,
            "cells_completed": len(ids), "pending": M.TOTAL_CELLS - len(ids),
            "unique_cell_coverage": True, "obligations_completed": obligations,
            "far_field": far, "executor": executor, "accounting": acct, "cap": cap,
            "ledger_state": state, "evidence_split": {k: len(v) for k, v in sorted(split.items())},
            "inputs": {"operational_contract_sha256": sha256_file(acfg["operational_contract_path"]),
                       "production_authorization_sha256": I["auth_hash"],
                       "shard_manifest_sha256": sha256_file(I["shard_path"]),
                       "production_ledger_sha256": sha256_file(I["ledger_path"]),
                       "predecessor_ledger_sha256": sha256_file(I["predecessor_ledger"]),
                       "generation_transition_sha256": sha256_file(I["transition_path"]),
                       "successor_cells_sha256": auth["successor_cells_sha256"]},
            "_frozen": {"PL": PL, "auth": auth, "owners": own["owners"], "recs": recs}}


# ---------------------------------------------------------------- assembly
def assemble(acfg: dict, report: dict | None = None) -> dict:
    """Build the AWS_ONLY final assembly document over the FROZEN aggregation function.

    Pure: it returns the document. Writing it is the entry point's job, and it never
    writes anywhere inside a production namespace or runtime tree.
    """
    rep = report or preflight(acfg)
    fr = rep["_frozen"]
    agg = frozen_gate((fr["PL"],), fr["PL"].assemble_production_campaign,
        {"auth": fr["auth"], "owners": fr["owners"]}, {"AWS": fr["recs"]})
    if agg["cells"] != rep["cells_completed"] or agg["obligations"] != rep["obligations_completed"]:
        raise AssemblyRefusal("frozen aggregation disagrees with the verified shard")
    if abs(agg["cpu_h"] - rep["accounting"]["scientific_record_cpu_h"]) > ACCOUNTING_TOL:
        raise AssemblyRefusal("frozen aggregation CPU-h disagrees with the reconciliation")
    body = {k: v for k, v in rep.items() if not k.startswith("_")}
    body.update({
        "schema": "rebaseguard.p5y.k1.ps1.aws-only-final-assembly.v1",
        "route": ROUTE_AWS_ONLY,
        "aggregate": {"cells": agg["cells"], "obligations": agg["obligations"],
                      "scientific_cpu_h": agg["cpu_h"], "far_field": agg["far_field"]},
        "remote_handoff": {"required": False, "present": False,
                           "reason": fr["auth"]["handoff"]["status"]},
        "k1_status": "NOT_DECIDED_HERE: final assembly is not scientific adjudication",
    })
    body["assembly_sha256"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return body
