"""Generate the ops/ and driver/ of the generation-2 RUNTIME ISOLATION successor.

Source: the sibling generation-2 recovery namespace (p5y_k1_ps1_portable_recovery) at the SAME
checkout. Every source file is first verified against the recovery_source_manifest frozen in the
generation-2 operational contract, then either copied byte-identically or patched with anchored
substitutions (each anchor must occur exactly once). Nothing in the source namespace, the
production namespace or any runtime directory is written.

Operational repair only (see driver/generation_paths.py): no scientific module is read or changed.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
SRC_NS = NS.parent / "p5y_k1_ps1_portable_recovery"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


COPIES = ("ops/ledger_ops.py", "ops/locks.py", "ops/runtime_state.py",
          "driver/ps1_checkpoint.py", "driver/host_guard.py")
CONFIG_COPIES = ("config/RUNTIME_STATE_EXCLUDE",)

GP_IMPORT = ('sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "driver"))\n'
             "import generation_paths as GP                                              # noqa: E402\n")

PATCHES = {
    # -------------------------------------------------------------- opscommon
    "ops/opscommon.py": [
        ('''    if path.resolve() == CONTRACT_PATH.resolve():
        want = CONTRACT_HASH_PATH.read_text().strip()''',
         '''    if path.resolve() == CONTRACT_PATH.resolve():
        if not CONTRACT_HASH_PATH.exists():
            raise OpsRefusal("UNFROZEN: this successor's PRODUCTION contract has no "
                             "OPERATIONAL_CONTRACT_HASH; an operator freeze is required")
        want = CONTRACT_HASH_PATH.read_text().strip()'''),
    ],
    # --------------------------------------------------------- produce_entry
    "ops/produce_entry.py": [
        ("import ledger_ops as LO                                                # noqa: E402\n",
         "import ledger_ops as LO                                                # noqa: E402\n" + GP_IMPORT),
        ('''    pf["budget"] = LO.make_ops_budget(GB, pf["budget"], run_id, PL.__file__)\n''',
         '''    # GENERATION2_RUNTIME_PATH_SPLIT: the launcher takes work_dir / DRAIN / evidence_dir from
    # the frozen authorization host block. Rebind exactly those two keys to the generation
    # paths so the launcher, prodctl drain and supervisor reconciliation agree.
    paths = GP.GenerationPaths.for_host(contract, role)
    iso = GP.gate_isolation(contract, role, paths, frozen_auth=pf["auth"])
    rb = GP.rebinding_record(pf["auth"], role, paths)
    pf["auth"] = GP.rebind_authorization(pf["auth"], role, paths)
    pf["generation_paths"] = paths.as_dict()
    print(f"  isolation {json.dumps(iso, sort_keys=True)}", flush=True)
    print(f"  rebinding {json.dumps(rb, sort_keys=True)}", flush=True)
    pf["budget"] = LO.make_ops_budget(GB, pf["budget"], run_id, PL.__file__)\n'''),
    ],
    # ------------------------------------------------------------ supervisor
    "ops/supervisor.py": [
        ("import ps1_reconcile as RECON                                               # noqa: E402\n",
         "import ps1_reconcile as RECON                                               # noqa: E402\n"
         "import generation_paths as GP                                              # noqa: E402\n"),
        ('''        if root in cmd and any(x in cmd for x in ("produce_entry.py", "synthetic_entry.py",
                                                  "production_launcher.py")):''',
         '''        if root in cmd and any(x in cmd for x in ("produce_entry.py", "synthetic_entry.py",
                                                  "production_launcher.py", "ps1_cellseq_worker.py",
                                                  "synthetic_cellseq_entry.py",
                                                  "synthetic_isolation_entry.py")):'''),
        ('''    report = {"ops": verify_ops_source(contract), "parent": verify_parent(contract, spec)}\n''',
         '''    report = {"ops": verify_ops_source(contract), "parent": verify_parent(contract, spec)}
    paths = GP.GenerationPaths.for_host(contract, role)
    report["isolation"] = GP.gate_isolation(contract, role, paths)
    if paths.drain_flag.exists() and not allow_complete:
        raise OpsRefusal(f"STALE_DRAIN_FLAG: {paths.drain_flag} exists before start; a new run "
                         "would drain immediately. Archive it with: prodctl clear-drain")
    report["legacy_drain_flags_ignored"] = paths.legacy_drain_flags()\n'''),
        # crash recovery: a run whose supervisor died (SIGKILL, host loss) never reconciled its
        # durable markers; reconcile them from the recorded launcher pid BEFORE settling.
        ('''        u, kind = LO.resolve_cpu_evidence(contract, rt, run_id, run,
                                          service_mode=service_mode(contract))
        settled.append(LO.settle_run(io, rt, role, run_id, u, kind))''',
         '''        rec_p = rt.run_record(run_id)
        child_pid = json.loads(rec_p.read_text()).get("child_pid") if rec_p.exists() else None
        if child_pid:
            report.setdefault("prestart_reconciliation", {})[run_id] = RECON.reconcile(
                contract, role, spec, io, child_pid, validator=_synthetic_validator(contract), say=say)
        u, kind = LO.resolve_cpu_evidence(contract, rt, run_id, run,
                                          service_mode=service_mode(contract))
        settled.append(LO.settle_run(io, rt, role, run_id, u, kind))'''),
        ('''               "supervisor_pid": os.getpid(), "cpu_source": cpu.kind}''',
         '''               "supervisor_pid": os.getpid(), "cpu_source": cpu.kind,
               "prestart_reconciliation": pre.get("prestart_reconciliation"),
               "generation_paths": GP.GenerationPaths.for_host(contract, role).as_dict()}'''),
    ],
    # --------------------------------------------------------------- prodctl
    "ops/prodctl.py": [
        ("import supervisor as SV                                                              # noqa: E402\n",
         "import supervisor as SV                                                              # noqa: E402\n" + GP_IMPORT),
        ('''    LK.reclaim_ledger_lock(Path(str(io.path) + ".lock"), contract, campaign_lock=lock)
    return {"settled": True, "settlement": LO.settle_run(io, rt, role, run_id, u,''',
         '''    LK.reclaim_ledger_lock(Path(str(io.path) + ".lock"), contract, campaign_lock=lock)
    if rec.get("child_pid"):
        rec["reconciliation_stop_post"] = SV.RECON.reconcile(
            contract, role, spec, io, rec["child_pid"],
            validator=SV._synthetic_validator(contract), say=print)
        write_json_atomic(rec_p, rec)
    return {"settled": True, "settlement": LO.settle_run(io, rt, role, run_id, u,'''),
        ('''    d = str(prod_ns(spec).parent / "p5y_k1_ps1_portable_recovery" / "driver")''',
         '''    d = str(Path(__file__).resolve().parents[1] / "driver")      # THIS ops root, never the production tree'''),
        ('''    out = {"draining": True, "flag": str(flag),''',
         '''    paths = GP.GenerationPaths.for_host(contract, role)
    if flag != paths.drain_flag:
        raise OpsRefusal(f"drain flag {flag} != generation drain flag {paths.drain_flag}")
    out = {"draining": True, "flag": str(flag), "launcher_polls": str(paths.drain_flag),
           "legacy_drain_flags_ignored": paths.legacy_drain_flags(),'''),
        ('''                  evidence_root=Path(auth["hosts"][role]["evidence_dir"]),''',
         '''                  evidence_root=GP.GenerationPaths.for_host(contract, role).evidence_root,'''),
        # resume probes the worker contract with the CONTRACT-bound interpreter of THIS host (on
        # AWS identical to the authorization's; a portable bundle must not require the authorised
        # host's filesystem layout just to verify)
        ('''    gates["probe"] = PL._probe(auth, role)''',
         '''    _pauth = json.loads(json.dumps(auth))
    _pauth["hosts"][role]["python"] = spec["python"]
    gates["probe_interpreter"] = {"contract": spec["python"], "authorization": auth["hosts"][role]["python"]}
    gates["probe"] = PL._probe(_pauth, role)'''),
        ('''    src_root = Path(auth["hosts"][role]["evidence_dir"])''',
         '''    src_root = GP.GenerationPaths.for_host(contract, role).evidence_root'''),
        ('''            "heartbeat_age_s": (time.time() - json.loads(hb.read_text())["t_wall"])
            if hb.exists() else None}''',
         '''            "heartbeat_age_s": (time.time() - json.loads(hb.read_text())["t_wall"])
            if hb.exists() else None,
            "generation_paths": GP.GenerationPaths.for_host(contract, role).as_dict(),
            "drain_flag_present": GP.GenerationPaths.for_host(contract, role).drain_flag.exists(),
            "legacy_drain_flags_ignored": GP.GenerationPaths.for_host(contract, role).legacy_drain_flags()}'''),
        ('''def main(argv=None) -> int:\n''',
         '''def _clear_drain(contract, role, rt, lock):
    """Archive (never delete) a generation DRAIN flag left by a completed drain, so the next
    start is not drained at once. Runs under the campaign lock, so no run is live."""
    spec = host_spec(contract, role)
    paths = GP.GenerationPaths.for_host(contract, role)
    if not paths.drain_flag.exists():
        return {"cleared": False, "why": "no generation drain flag", "flag": str(paths.drain_flag)}
    raw = paths.drain_flag.read_bytes()
    dst = paths.drain_archive / f"DRAIN-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{sha256_bytes(raw)[:12]}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    os.replace(paths.drain_flag, dst)
    M, GB = frozen_accounting(spec)
    st = LO.LedgerIO(ledger_path(spec), M, GB, frozen_budget(spec, contract)).read()
    LO.append_continuity(rt, "DRAIN_FLAG_ARCHIVED", st, {"archived": str(dst), "sha256": sha256_bytes(raw)})
    return {"cleared": True, "archived": str(dst), "sha256": sha256_bytes(raw)}


def main(argv=None) -> int:\n'''),
        ('''                                        "drain", "checkpoint", "export", "resume"))''',
         '''                                        "drain", "checkpoint", "export", "resume",
                                        "clear-drain", "paths"))'''),
        ('''        elif a.command == "resume":
            out = with_lock(c, a.role, lambda *x: _resume(*x, ckpt=a.ckpt))''',
         '''        elif a.command == "resume":
            out = with_lock(c, a.role, lambda *x: _resume(*x, ckpt=a.ckpt))
        elif a.command == "clear-drain":
            out = with_lock(c, a.role, _clear_drain)
        elif a.command == "paths":
            gp = GP.GenerationPaths.for_host(c, a.role)
            out = {"paths": gp.as_dict(), "isolation": GP.gate_isolation(c, a.role, gp)}'''),
    ],
    # --------------------------------------------------------- ps1_reconcile
    "driver/ps1_reconcile.py": [
        ('''from pathlib import Path\n''',
         '''from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generation_paths as GP                                                   # noqa: E402\n'''),
        ('''def _markers(spec, launcher_pid):
    """Every durably-renamed marker under the runtime evidence root for THIS run.
    A .tmp- file can never match: only the final atomic name is globbed."""
    root = Path(spec["runtime_dir"]) / "evidence"
''',
         '''def _markers(spec, launcher_pid, roots=None):
    """Durable markers for THIS run under every root in `roots` (default: the contract
    runtime evidence root). The generation root is scanned first; a legacy root is read only."""
    out = {}
    for root in (roots if roots is not None else [Path(spec["runtime_dir"]) / "evidence"]):
        for cell, hit in _markers_under(Path(root), launcher_pid).items():
            out.setdefault(cell, hit)
    return out


def _markers_under(root, launcher_pid):
    """Every durably-renamed marker under ONE evidence root for THIS run.
    A .tmp- file can never match: only the final atomic name is globbed."""
'''),
        ('''    marks = _markers(spec, launcher_pid)\n''',
         '''    roots = GP.GenerationPaths.for_host(contract, role).marker_roots()
    rep["marker_roots"] = [str(r) for r in roots]
    marks = _markers(spec, launcher_pid, roots=roots)\n'''),
    ],
}


def expected_hashes() -> dict:
    c = json.loads((SRC_NS / "config/OPERATIONAL_CONTRACT.json").read_text())
    return c["recovery_source_manifest"]


def main() -> int:
    want = expected_hashes()
    report = {"schema": "rebaseguard.p5y.k1.ps1.gen2-runtime-isolation.generation-report.v1",
              "source_namespace": SRC_NS.name, "copied": {}, "patched": {}}
    for rel in list(COPIES) + list(PATCHES):
        src = (SRC_NS / rel).read_bytes()
        if rel in want and sha(src) != want[rel]:
            raise SystemExit(f"source drift vs frozen recovery_source_manifest: {rel}")
        dst = NS / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if rel in COPIES:
            dst.write_bytes(src)
            report["copied"][rel] = sha(src)
            continue
        text = src.decode()
        for i, (old, new) in enumerate(PATCHES[rel]):
            if old.startswith("import ") and old.endswith("# noqa: E402\n") and new.startswith(old):
                # import anchors: match the unique line by its import prefix (column padding varies)
                prefix = old.split("#")[0].rstrip()
                lines = text.splitlines(keepends=True)
                hits = [j for j, l in enumerate(lines) if l.split("#")[0].rstrip() == prefix]
                if len(hits) != 1:
                    raise SystemExit(f"{rel} import anchor #{i} {prefix!r} found {len(hits)} times")
                lines.insert(hits[0] + 1, new[len(old):])
                text = "".join(lines)
                continue
            n = text.count(old)
            if n != 1:
                raise SystemExit(f"{rel} anchor #{i} found {n} times (need exactly 1)")
            text = text.replace(old, new, 1)
        dst.write_text(text)
        report["patched"][rel] = {"source_sha256": sha(src), "generated_sha256": sha(dst.read_bytes()),
                                  "substitutions": len(PATCHES[rel])}
    for rel in CONFIG_COPIES:
        data = (SRC_NS / rel).read_bytes()
        (NS / rel).parent.mkdir(parents=True, exist_ok=True)
        (NS / rel).write_bytes(data)
        report["copied"][rel] = sha(data)
    (NS / "config/GENERATION_REPORT.json").write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"copied": len(report["copied"]), "patched": len(report["patched"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
