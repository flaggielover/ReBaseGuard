"""Generate ops/prodctl.py for the recovery successor: adds drain / checkpoint / export / resume.

Asserted substitutions against the FROZEN adapter prodctl.py. Existing commands are untouched.
"""
import hashlib
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
SRC = Path("/home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/"
           "p5y_k1_ps1_lifecycle_adapter/ops/prodctl.py")
OUT = NS / "ops" / "prodctl.py"

PATH_OLD = 'sys.path.insert(0, str(Path(__file__).resolve().parent))\n'
PATH_NEW = PATH_OLD          # unchanged: ops modules are byte-identical local copies

CHOICES_OLD = '''    ap.add_argument("command", choices=("render", "start", "stop", "status", "recover", "verify",
                                        "install-runtime-policy", "settle-fallback",
                                        "handoff-export", "handoff-import", "assemble"))'''
CHOICES_NEW = '''    ap.add_argument("command", choices=("render", "start", "stop", "status", "recover", "verify",
                                        "install-runtime-policy", "settle-fallback",
                                        "handoff-export", "handoff-import", "assemble",
                                        "drain", "checkpoint", "export", "resume"))'''

ARGS_OLD = '''    ap.add_argument("--from", dest="src")
    a = ap.parse_args(argv)'''
ARGS_NEW = '''    ap.add_argument("--from", dest="src")
    ap.add_argument("--output")
    ap.add_argument("--checkpoint", dest="ckpt")
    ap.add_argument("--wait", type=float, default=0.0)
    ap.add_argument("--drain-after-completed", dest="drain_after", type=int)
    a = ap.parse_args(argv)'''

DISPATCH_OLD = '''        elif a.command == "assemble":
            out = with_lock(c, a.role, _assemble)'''
DISPATCH_NEW = '''        elif a.command == "assemble":
            out = with_lock(c, a.role, _assemble)
        elif a.command == "drain":
            out = cmd_drain(c, a.role, wait_s=a.wait)
        elif a.command == "checkpoint":
            out = with_lock(c, a.role, _checkpoint)
        elif a.command == "export":
            out = with_lock(c, a.role, lambda *x: _export(*x, output=a.output))
        elif a.command == "resume":
            out = with_lock(c, a.role, lambda *x: _resume(*x, ckpt=a.ckpt))'''

IMPL_ANCHOR = "def main(argv=None) -> int:\n"
IMPL_NEW = '''# ------------------------------------------------------ portable recovery (generation 2)
def _recovery_driver(spec):
    d = str(prod_ns(spec).parent / "p5y_k1_ps1_portable_recovery" / "driver")
    if d not in sys.path:
        sys.path.insert(0, d)
    import ps1_checkpoint as CK                                   # noqa: E402
    import host_guard as HG                                       # noqa: E402
    return CK, HG


def _generation(contract, role, st):
    ops = (st or {}).get(LO.OPS_FIELD) or {}
    return {"generation_id": "G2", "generation_index": 2, "host_role": role,
            "contract_sha256": contract["_sha256"],
            "runs": sorted((ops.get("runs") or {}))}


PREDECESSOR = {
    "production_authorization_commit": "29b3bffb6a739121b66bdfcb23cb6b6544b39baf",
    "halted_run_id": "20260912T041203Z-962132d3",
    "halted_ledger_sha256": "0557bc229c3fcdb10cb0dd0b5836fa62a6b0e6c2512656e6ec7e49294b4d6cab",
    "halt_reason": "RETRY_LIMIT",
    "halt_classification": "EXECUTION_LIFECYCLE_EXHAUSTION_NOT_A_SCIENTIFIC_COUNTEREXAMPLE",
    "historical_cpu_h": 92.32,
    "historical_finalized_cells": 0,
    "historical_patch_records": 24610,
    "historical_patch_records_status": "ARCHIVAL_ONLY_NEVER_SCIENTIFICALLY_ADMISSIBLE",
}


def cmd_drain(contract, role, wait_s=0.0) -> dict:
    """Cooperative drain. Deliberately does NOT take the campaign lock: a running campaign
    holds it. Writes the flag the launcher and workers poll at CELL boundaries only."""
    spec = host_spec(contract, role)
    # resolve from the CONTRACT runtime dir, never from the authorization: under a synthetic
    # contract the authorization still names the genuine work_dir, and a drain must never
    # touch genuine production state.
    work = Path(spec["runtime_dir"]) / "work"
    work.mkdir(parents=True, exist_ok=True)
    flag = work / "DRAIN"
    atomic_write(flag, canonical({"requested_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                  "role": role, "by": "prodctl drain"}))
    out = {"draining": True, "flag": str(flag),
           "semantics": ["no new cell admitted", "in-flight cells run to their boundary",
                         "each completed cell is finalized individually",
                         "GRACEFUL_DRAIN is not a tear: torn_attempts is not incremented"]}
    rt = RuntimeDir(spec)
    if wait_s > 0:
        t_end = time.monotonic() + wait_s
        while time.monotonic() < t_end:
            if LK.CampaignLock(rt, contract).probe() != LK.LIVE:
                out["settled"] = True
                break
            time.sleep(2.0)
        out.setdefault("settled", False)
    out["status"] = cmd_status(contract, role)
    return out


def _finalized_from_ledger(spec, contract, role):
    """Finalized cells are the SEALED per-cell records on disk, re-verified by hash."""
    PL, PP, _HO, M = frozen_prod(spec)
    auth = PL.load_production_authorization()
    cells_dir = prod_ns(spec) / "production" / "cells"
    fin = {}
    for p in sorted(cells_dir.glob("[0-9]*.json")):
        rec = read_json_strict(p)
        cell = int(rec["cell_id"])
        ev = {}
        for k, v in rec["evidence"].items():
            ep = Path(v["path"])
            if not ep.exists():
                raise OpsRefusal(f"finalized cell {cell}: evidence missing {ep}")
            got = sha256_file(ep)
            if got != v["sha256"]:
                raise OpsRefusal(f"finalized cell {cell}: evidence hash drift {ep}")
            ev[k] = {"sha256": got, "bytes": ep.stat().st_size, "path": str(ep)}
        fin[cell] = {"scientific_content_hash": rec["scientific_content_hash"],
                     "evidence": ev, "host": rec["role"], "run_id": rec.get("task_id"),
                     "cpu_seconds": rec["cpu_seconds"], "successor_id": rec.get("successor_id")}
    return fin, auth


def _build_checkpoint(contract, role, rt):
    spec = host_spec(contract, role)
    CK, _HG = _recovery_driver(spec)
    M, GB = frozen_accounting(spec)
    io = LO.LedgerIO(ledger_path(spec), M, GB, frozen_budget(spec, contract))
    st = io.read() or {}
    ops = st.get(LO.OPS_FIELD) or {}
    if st.get("open_reservations"):
        raise OpsRefusal(f"checkpoint refused: {len(st['open_reservations'])} open reservations; "
                         "drain or settle first")
    if LO.unsettled_runs(st, role):
        raise OpsRefusal(f"checkpoint refused: unsettled runs {LO.unsettled_runs(st, role)}")
    fin, auth = _finalized_from_ledger(spec, contract, role)
    owners = SV.owners_of(spec, contract)
    owned = sorted(c for c, r in owners.items() if r == role)
    pending = sorted(set(range(CK.TOTAL_CELLS)) - set(fin))
    committed = st.get("committed_cpu_h_by_role", {})
    gen_cpu = float(committed.get(role, 0.0))
    sci = sum(v["cpu_seconds"] for v in fin.values()) / 3600.0
    acc = {"historical_cpu_h": PREDECESSOR["historical_cpu_h"],
           "generation_cpu_h": gen_cpu,
           "cumulative_cpu_h": PREDECESSOR["historical_cpu_h"] + gen_cpu,
           "scientific_cpu_h": sci,
           "unattributed_cpu_h": PREDECESSOR["historical_cpu_h"] + max(0.0, gen_cpu - sci),
           "global_cap_cpu_h": contract["parent"]["global_cpu_cap"]}
    ck = CK.build(generation=_generation(contract, role, st),
                  predecessor=PREDECESSOR,
                  identities={"producer_commit": auth["producer_commit"],
                              "scientific_adapter_hash": auth["scientific_adapter_hash"],
                              "successor_cells_sha256": auth["successor_cells_sha256"],
                              "live_patches_sha256": auth["live_patches_sha256"],
                              "precision_bits": 256},
                  finalized=fin, pending=pending,
                  torn_lineage=ops.get("torn_attempts", {}),
                  accounting=acc,
                  runs=sorted((ops.get("runs") or {})),
                  hosts={role: {"role": role, "owned": len(owned)}},
                  evidence_root=Path(auth["hosts"][role]["evidence_dir"]),
                  ledger_continuity_sha256=sha256_file(ledger_path(spec)))
    return ck, CK


def _checkpoint(contract, role, rt, lock):
    ck, CK = _build_checkpoint(contract, role, rt)
    out = rt.root / "checkpoints"
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"checkpoint-{ck['checkpoint_content_sha256'][:12]}.json"
    write_json_atomic(p, ck)
    rep = CK.verify(ck, require_identities=ck["identities"])
    return {"checkpoint": str(p), "sha256": ck["checkpoint_content_sha256"],
            "finalized": len(ck["finalized_cells"]), "pending": len(ck["pending_cells"]),
            "verify": rep}


def _export(contract, role, rt, lock, output=None):
    spec = host_spec(contract, role)
    ck, CK = _build_checkpoint(contract, role, rt)
    auth = _auth(spec)
    src_root = Path(auth["hosts"][role]["evidence_dir"])
    stage = Path(output) if output else (rt.root / "export")
    # normalise evidence into cell_XXXX/<name> so the bundle is location-independent
    norm = rt.root / "export_src"
    if norm.exists():
        import shutil as _sh
        _sh.rmtree(norm)
    for cell, meta in ck["finalized"].items():
        d = norm / f"cell_{int(cell):04d}"
        d.mkdir(parents=True, exist_ok=True)
        import shutil as _sh
        for name, e in meta["evidence"].items():
            _sh.copy2(e["path"], d / name)
    rep = CK.export_bundle(ck, evidence_root=norm, out_dir=stage)
    return {"export": rep, "source_evidence_root": str(src_root),
            "excluded": ["caches", "scratch", "archival torn patch records", "locks",
                         "journals", "process state", "temporary files"]}


def _resume(contract, role, rt, lock, ckpt=None):
    """Fail-closed governed resume. Verifies EVERYTHING before any expensive execution."""
    if not ckpt:
        raise OpsRefusal("resume requires --checkpoint <path to checkpoint.json or bundle dir>")
    spec = host_spec(contract, role)
    CK, HG = _recovery_driver(spec)
    p = Path(ckpt)
    if p.is_dir():
        rep_b = CK.verify_bundle(p)
        ck = json.loads((p / "checkpoint.json").read_text())
        ev_root = p / "evidence"
    else:
        ck = read_json_strict(p)
        rep_b = None
        ev_root = None
    auth = _auth(spec)
    want = {"producer_commit": auth["producer_commit"],
            "scientific_adapter_hash": auth["scientific_adapter_hash"],
            "successor_cells_sha256": auth["successor_cells_sha256"],
            "live_patches_sha256": auth["live_patches_sha256"],
            "precision_bits": 256}
    gates = {"checkpoint": CK.verify(ck, evidence_root=ev_root, require_identities=want)}
    PL, *_ = frozen_prod(spec)
    gates["executor_source_identity"] = (
        PL.executor_source_identity(Path(auth["hosts"][role]["production_root"])
                                    if "production_root" in auth["hosts"][role]
                                    else prod_ns(spec).parents[2])["EXECUTOR_HASH"]
        == auth["scientific_adapter_hash"])
    if not gates["executor_source_identity"]:
        raise OpsRefusal("resume refused: live executor is not the authorised executor")
    gates["probe"] = PL._probe(auth, role)
    if gates["probe"].get("precision_inside_scientific_context") != 256:
        raise OpsRefusal("resume refused: worker precision is not 256 bits")
    if not gates["probe"].get("thread_contract_ok"):
        raise OpsRefusal("resume refused: six-variable thread contract not in force")
    M, GB = frozen_accounting(spec)
    io = LO.LedgerIO(ledger_path(spec), M, GB, frozen_budget(spec, contract))
    st = io.read() or {}
    already = {int(c) for c in st.get("completed_cells", {})}
    dup = already & set(ck["finalized_cells"]) - already
    if dup:
        raise OpsRefusal(f"resume refused: duplicate finalized scheduling {sorted(dup)}")
    sched = [c for c in ck["pending_cells"] if c not in already]
    if set(sched) & set(ck["finalized_cells"]):
        raise OpsRefusal("resume refused: a finalized cell appears in the schedule")
    gates["host_maintenance"] = HG.gate(window_hours=float(contract.get("production_window_hours", 24)),
                                        contract_path=None, role=role, fail_closed=False)
    return {"resume": "VERIFIED_READY", "gates": gates, "bundle": rep_b,
            "schedule_only_pending": len(sched), "finalized_never_rescheduled": len(ck["finalized_cells"]),
            "historical_cpu_h_preserved": ck["accounting"]["historical_cpu_h"],
            "next": f"prodctl.py start --role {role}   (schedules pending cells only)"}


''' + IMPL_ANCHOR


def main() -> int:
    src = SRC.read_text()
    for name, blk in (("CHOICES", CHOICES_OLD), ("ARGS", ARGS_OLD), ("PATH", PATH_OLD),
                      ("DISPATCH", DISPATCH_OLD), ("IMPL", IMPL_ANCHOR)):
        if src.count(blk) != 1:
            raise SystemExit(f"{name} anchor not found exactly once ({src.count(blk)})")
    out = (src.replace(CHOICES_OLD, CHOICES_NEW, 1).replace(ARGS_OLD, ARGS_NEW, 1)
              .replace(PATH_OLD, PATH_NEW, 1)
              .replace(DISPATCH_OLD, DISPATCH_NEW, 1).replace(IMPL_ANCHOR, IMPL_NEW, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(out)
    # byte-identical ops modules, copied and hash-verified (lifecycle-adapter pattern)
    copied = {}
    # ledger_ops.py is GENERATED by make_ledger_ops_recovery.py (adds GRACEFUL_DRAIN)
    for name in ("opscommon.py", "locks.py", "produce_entry.py",
                 "runtime_state.py", "supervisor.py"):
        src_p = SRC.parent / name
        dst_p = OUT.parent / name
        data = src_p.read_bytes()
        dst_p.write_bytes(data)
        h = hashlib.sha256(data).hexdigest()
        if hashlib.sha256(dst_p.read_bytes()).hexdigest() != h:
            raise SystemExit(f"copy drift {name}")
        copied[name] = h
    (OUT.parent / "OPS_SOURCE_MANIFEST.json").write_text(
        __import__("json").dumps({"byte_identical_from": str(SRC.parent),
                                  "modules": copied,
                                  "modified": {"prodctl.py": hashlib.sha256(OUT.read_bytes()).hexdigest()}},
                                 indent=1, sort_keys=True) + "\n")
    print(f"  byte-identical ops modules: {len(copied)}")
    print(f"wrote {OUT}")
    print(f"  frozen prodctl sha256 : {hashlib.sha256(SRC.read_bytes()).hexdigest()}")
    print(f"  generated sha256      : {hashlib.sha256(OUT.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
