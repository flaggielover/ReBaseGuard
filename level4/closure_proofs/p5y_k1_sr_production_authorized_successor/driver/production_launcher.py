"""THE operative entry point for AUTHORISED, RESULT-BEARING P5Y K1 SR production.

This module implements NO science, NO accounting and NO scheduling of its own.
It COMPOSES the frozen, already-adjudicated primitives carried forward
byte-identically in this namespace's driver/ directory, and adds exactly the two
things the frozen stack does not have and production requires:

    1. a production authorization (production_enabled=true) that is loaded and
       hash-checked like every other frozen identity, and
    2. the genuine-vs-synthetic provenance firewall plus a dedicated, immutable
       production result namespace.

Everything else -- role detection, runtime fingerprint, worker topology,
scientific scope, shard ownership, the ONE 4500 CPU-h global budget, in-flight
reservation arithmetic, the authenticated AWS -> VULTR handoff, obligation
conservation and final assembly -- is the frozen implementation, unmodified.

RESULT STATE AT FREEZE TIME: zero genuine SR production cells have been executed.
`run_production_cells` below is complete and reachable, and is deliberately not
invoked by any test.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

PROD_NS = Path(__file__).resolve().parents[1]
ROOT = PROD_NS.parents[2]
sys.path.insert(0, str(PROD_NS / "driver"))

import multihost as M                                              # noqa: E402
import executor_adapter as EA                                      # noqa: E402
import global_budget as GB                                         # noqa: E402
import worker_pool as WP                                           # noqa: E402
import integrated_sr_launcher as L                                 # noqa: E402
import production_provenance as PP                                 # noqa: E402

LAUNCHER_SCHEMA = "rebaseguard.p5y.k1.sr.production.launcher.v1"
AUTH_PATH = PROD_NS / "config/LAUNCH_AUTHORIZATION.json"
AUTH_HASH_PATH = PROD_NS / "config/LAUNCH_AUTHORIZATION_HASH"

# The dedicated, immutable production result namespace. Genuine results live
# ONLY here; synthetic / control evidence lives ONLY under evidence/.
PRODUCTION_DIR = PROD_NS / "production"
PRODUCTION_LEDGER = PRODUCTION_DIR / "PRODUCTION_LEDGER.json"
PRODUCTION_LEDGER_SCHEMA = "rebaseguard.p5y.k1.sr.production.ledger.v1"
FORBIDDEN_RESULT_PARTS = ("evidence", "diagnostics", "phase8", "tests", "config")

# The additive production source closure: the modules the frozen
# INTEGRATED_SOURCE_MANIFEST cannot know about because they did not exist at the
# predecessor freeze. Bound by the production authorization.
PRODUCTION_CLOSURE = ("driver/production_launcher.py", "driver/production_provenance.py")

Refusal = M.MultiHostRefusal


class ProductionRefusal(RuntimeError):
    """The production launcher refused. Always fail closed."""


def _sha256(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ------------------------------------------------------------ authorization
def production_closure_hash(ns=None) -> str:
    ns = Path(ns) if ns else PROD_NS
    files = {}
    for rel in sorted(PRODUCTION_CLOSURE):
        p = ns / rel
        if not p.exists():
            raise ProductionRefusal(f"production closure file absent: {rel}")
        files[rel] = _sha256(p)
    blob = "".join(f"{k}:{v}\n" for k, v in sorted(files.items())).encode()
    return hashlib.sha256(blob).hexdigest()


def authorization_hash(path=None) -> str:
    return _sha256(path or AUTH_PATH)


def load_production_authorization(path=None, hash_path=None) -> dict:
    """Load the ADDITIVE production authorization through the FROZEN loader.

    The frozen loader still enforces every predecessor invariant, including
    `result_bearing is False` -- this artifact carries no results; it only
    switches production on.
    """
    path = Path(path) if path else AUTH_PATH
    hash_path = Path(hash_path) if hash_path else AUTH_HASH_PATH
    if not path.exists():
        raise ProductionRefusal(
            f"production authorization absent at {path}; SCIENCE is refused")
    if not hash_path.exists():
        raise ProductionRefusal(f"production authorization hash absent at {hash_path}")
    expect = hash_path.read_text().strip()
    auth = L.load_authorization(path, expect_sha256=expect)      # frozen gate chain
    if auth.get("schema") != "rebaseguard.p5y.k1.sr.production.launch-authorization.v1":
        raise ProductionRefusal(f"not a production authorization: {auth.get('schema')!r}")
    if auth.get("production_enabled") is not True:
        raise ProductionRefusal("production authorization does not enable production")
    if auth.get("result_bearing") is not False:
        raise ProductionRefusal("the authorization artifact itself must be result-free")
    got = production_closure_hash()
    if auth.get("production_closure_sha256") != got:
        raise ProductionRefusal(
            f"production closure {got} != authorised {auth.get('production_closure_sha256')}")
    return auth


def gate_campaign_scope(auth, owners) -> dict:
    """Re-derive the frozen campaign scope and refuse any drift."""
    s = auth["scientific_scope"]
    aws = sorted(c for c, r in owners.items() if r == "AWS")
    vul = sorted(c for c, r in owners.items() if r == "VULTR")
    checks = {
        "total_cells": (len(owners), s["total_cells"], 316),
        "aws_cells": (len(aws), auth["hosts"]["AWS"]["cell_count"], 247),
        "vultr_cells": (len(vul), auth["hosts"]["VULTR"]["cell_count"], 69),
        "obligations": (s["obligations"], 8849, 8849),
        "global_cpu_cap": (auth["global_cpu_cap"], M.GLOBAL_CPU_CAP, 4500.0),
    }
    for name, (got, want, frozen) in checks.items():
        if got != want or want != frozen:
            raise ProductionRefusal(f"{name} drift: {got} / {want} / frozen {frozen}")
    shard = auth["shard_identity"]
    if M.sha256_obj(aws) != shard["aws_cell_set_sha256"]:
        raise ProductionRefusal("AWS 247-cell set is not the authorised frozen set")
    if M.sha256_obj(vul) != shard["vultr_cell_set_sha256"]:
        raise ProductionRefusal("VULTR 69-cell set is not the authorised frozen set")
    if auth["execution_order"] != ["AWS", "AUTHENTICATED_HANDOFF", "VULTR"]:
        raise ProductionRefusal(f"execution order drift: {auth['execution_order']}")
    if auth["concurrency"]["host_sequence"] != ["AWS", "VULTR"]:
        raise ProductionRefusal("host sequence drift")
    total = sum(L.obligations_for_cell(auth, owners, r, c) for c, r in owners.items())
    if total != 8849:
        raise ProductionRefusal(f"obligation conservation drift: {total} != 8849")
    return {"total_cells": len(owners), "aws_cells": len(aws), "vultr_cells": len(vul),
            "obligations": total, "global_cpu_cap": auth["global_cpu_cap"],
            "execution_order": auth["execution_order"]}


# --------------------------------------------------- result-namespace safety
def gate_production_result_path(path, *, ns=None) -> Path:
    """Genuine results may be written ONLY inside the production namespace."""
    ns = Path(ns) if ns else PROD_NS
    p = Path(path).resolve()
    root = (ns / "production").resolve()
    if not str(p).startswith(str(root) + os.sep) and p != root:
        raise ProductionRefusal(
            f"production output {p} is outside the dedicated production namespace {root}")
    rel = p.relative_to(ns) if str(p).startswith(str(ns.resolve())) else p
    for part in Path(rel).parts:
        if part in FORBIDDEN_RESULT_PARTS and part != "production":
            raise ProductionRefusal(
                f"production output {p} would land in the control/evidence area {part!r}")
    return p


def gate_no_evidence_collision(paths, *, ns=None) -> None:
    """No genuine production file may overwrite Phase-8 evidence."""
    ns = Path(ns) if ns else PROD_NS
    ev = (ns / "evidence").resolve()
    for p in paths:
        rp = Path(p).resolve()
        if str(rp).startswith(str(ev) + os.sep) or rp == ev:
            raise ProductionRefusal(
                f"refusing to write a production result over evidence: {rp}")


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try: os.unlink(tmp)
        except FileNotFoundError: pass
        raise


# ------------------------------------------------------------------ preflight
def production_preflight(auth=None, **kw) -> dict:
    """Every frozen gate, plus the production gates. Executes NO science."""
    auth = auth or load_production_authorization()
    kw.setdefault("ns", PROD_NS)
    kw.setdefault("root", ROOT)
    kw.setdefault("repo", ROOT)
    kw.setdefault("budget_path", PRODUCTION_LEDGER)
    pf = L.preflight(auth, **kw)                       # the FROZEN gate chain
    scope = gate_campaign_scope(auth, pf["owners"])
    pf["production"] = {
        "authorization_hash": authorization_hash(),
        "production_closure_sha256": production_closure_hash(),
        "scientific_adapter_hash": auth["scientific_adapter_hash"],
        "production_dir": str(PRODUCTION_DIR),
        "production_ledger": str(PRODUCTION_LEDGER),
        "production_ledger_schema": PRODUCTION_LEDGER_SCHEMA,
        "scope": scope,
        "genuine_cells_completed": len(pf["budget"].status()["completed_cells"]),
    }
    pf["trace"].append({"gate": "production_authorization", "status": "PASS",
                        "detail": {"production_enabled": True,
                                   "authorization_hash": pf["production"]["authorization_hash"]}})
    pf["trace"].append({"gate": "production_campaign_scope", "status": "PASS",
                        "detail": scope})
    pf["trace"].append({"gate": "production_result_namespace", "status": "PASS",
                        "detail": {"dir": str(PRODUCTION_DIR)}})
    pf["READY"] = True
    return pf


def admit_cell(pf, cell_id, *, reservation_cpu_h=None) -> str:
    """Every Section-E condition, then ONE atomic draw. Runs NO science."""
    auth, role, budget = pf["auth"], pf["role"], pf["budget"]
    L.gate_production_enabled(auth)
    L.gate_concurrency(auth, role, enforce_active=True,
                       active_host=pf["active"]["active_host"])
    if pf["active"]["active_host"] != role:
        raise Refusal(f"{role} is not the active host ({pf['active']['active_host']}): "
                      f"{pf['active']['reason']}")
    M.gate_cell_ownership(role, cell_id, pf["owners"])
    if cell_id not in pf["pending"]:
        raise Refusal(f"cell {cell_id} is not pending for {role}")
    gate_production_result_path(PRODUCTION_LEDGER)
    res = M.validate_governed_cost(
        reservation_cpu_h if reservation_cpu_h is not None
        else auth["hosts"][role]["per_cell_reservation_cpu_h"], "cell reservation")
    return budget.draw(role, cell_id, res)


# ------------------------------------------------- the result-bearing loop
def run_production_cells(pf, *, max_cells=None, poll_timeout=3600.0) -> dict:
    """GENUINE SR production. Never invoked by any test in this namespace.

    Identical scheduling discipline to the frozen scheduler -- the PARENT is the
    sole admission, accounting, finalisation and resume authority -- with each
    finalised record additionally SEALED with production provenance and written
    into the dedicated production namespace.
    """
    auth, role, budget = pf["auth"], pf["role"], pf["budget"]
    L.gate_production_enabled(auth)
    ah = authorization_hash()
    adapter = auth["scientific_adapter_hash"]
    if EA.adapter_identity(pf["root"])["SCIENTIFIC_ADAPTER_HASH"] != adapter:
        raise ProductionRefusal("live scientific adapter is not the authorised adapter")
    pool, info = L.build_pool(pf, science_enabled=True)          # SCIENCE only
    pending = list(pf["pending"] if max_cells is None else pf["pending"][:max_cells])
    inflight, done, stopped = {}, [], None
    try:
        while pending or inflight:
            while pending and len(inflight) < info["workers"]:
                cell = pending[0]
                try:
                    key = admit_cell(pf, cell)
                except (GB.BudgetRefusal, M.MultiHostRefusal) as exc:
                    stopped = f"admission stopped: {exc}"; pending = []; break
                pending.pop(0); inflight[cell] = key
                pool.submit({"kind": "SCIENCE", "cell_id": cell,
                             "driver_dir": str(PROD_NS / "driver")})
            if not inflight:
                break
            rec = pool.get(timeout=poll_timeout)
            cell = rec.get("cell_id")
            if cell not in inflight:
                raise Refusal(f"worker returned unknown/duplicate cell {cell!r}")
            key = inflight.pop(cell)
            if not rec.get("ok"):
                budget.release(key); continue
            payload = rec.get("payload")
            if not isinstance(payload, dict) or "certificate" not in payload:
                budget.release(key)
                raise ProductionRefusal(f"cell {cell}: worker returned no certificate")
            sci = payload.get("scientific_content_hash")
            cert_digest = hashlib.sha256(PP.canonical(
                {"cell": cell, "cert": repr(payload["certificate"])})).hexdigest()
            M.gate_cell_ownership(role, cell, pf["owners"])
            actual = M.validate_governed_cost(rec["cpu_seconds"] / 3600.0,
                                              "actual cell CPU-h")
            record = {"cell_id": cell, "role": role,
                      "producer_commit": auth["producer_commit"],
                      "checkpoint_sha256": auth["checkpoint_sha256"],
                      "runtime_contract_hash": auth["runtime_contract_hashes"][role],
                      "scientific_content_hash": sci,
                      "cpu_seconds": actual * 3600.0,
                      "obligations_completed": L.obligations_for_cell(
                          auth, pf["owners"], role, cell),
                      "complete": True}
            M.validate_record(record, role, pf["owners"], auth["producer_commit"],
                              auth["checkpoint_sha256"])
            sealed = PP.seal(record, production_authorization_hash=ah,
                             scientific_adapter_hash=adapter,
                             certificate_digest=cert_digest)
            PP.verify(sealed, production_authorization_hash=ah,
                      scientific_adapter_hash=adapter)
            out = gate_production_result_path(PRODUCTION_DIR / "cells" / f"{cell:04d}.json")
            gate_no_evidence_collision([out])
            _atomic_write(out, (json.dumps(sealed, indent=1, sort_keys=True) + "\n").encode())
            budget.commit(key, actual, sealed)
            done.append(cell)
    finally:
        for k in inflight.values():
            budget.release(k)
        pool.close()
    return {"completed": done, "stopped": stopped, "status": budget.status()}


# --------------------------------------------------------------- assembly
def assemble_production_campaign(pf, host_ledgers) -> dict:
    """The GENUINE production assembler.

    Every record passes the provenance firewall BEFORE the frozen assembler is
    allowed to see it, so a Phase-8 synthetic stand-in can never be assembled
    into a production campaign.
    """
    auth = pf["auth"]
    ah = authorization_hash()
    adapter = auth["scientific_adapter_hash"]
    checked = 0
    for role, recs in host_ledgers.items():
        for rec in recs:
            PP.verify(rec, production_authorization_hash=ah,
                      scientific_adapter_hash=adapter)
            checked += 1
    out = L.final_assembly(pf, host_ledgers)                     # frozen assembler
    if out["cells_completed"] != 316 or out["obligations_completed"] != 8849:
        raise ProductionRefusal(
            f"production assembly drift: {out['cells_completed']} cells / "
            f"{out['obligations_completed']} obligations")
    out["production_records_verified"] = checked
    out["production_authorization_hash"] = ah
    return out


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=LAUNCHER_SCHEMA)
    ap.add_argument("--ready-check", action="store_true",
                    help="run every gate and report READY. Executes no science.")
    ap.add_argument("--produce", action="store_true",
                    help="RESULT-BEARING. Requires independent approval.")
    a = ap.parse_args(argv)
    if not (a.ready_check or a.produce):
        ap.error("choose --ready-check or --produce")
    pf = production_preflight()
    for t in pf["trace"]:
        print(f"  {t['status']:5s} {t['gate']}")
    p = pf["production"]
    print(f"  role={pf['role']} owned={len(pf['owned'])} pending={len(pf['pending'])} "
          f"genuine_completed={p['genuine_cells_completed']}")
    print(f"  scope={p['scope']}")
    if a.produce:
        run_production_cells(pf)
        return 0
    print("  READY (ready-check only: no science executed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
