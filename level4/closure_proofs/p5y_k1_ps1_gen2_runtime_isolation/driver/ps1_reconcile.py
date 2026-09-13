"""Pre-settlement reconciliation of durable per-cell completion markers.

WHY THIS EXISTS (measured, not assumed): on WORKER_LOST the supervisor calls
kill_all() -> child.kill(), which is SIGKILL. The launcher's finally block, atexit
handlers and any further marker polling are therefore UNREACHABLE. No poll interval can
make launcher-side reconciliation correct; the race is structural.

So the SUPERVISOR owns reconciliation. A durable marker is a write-ahead completion fact:
before any open reservation is classified torn, a valid marker converts that cell into a
FINALIZED commit through the EXACT governed sealing path (ps1_cellseq_launcher._seal_one),
so validation semantics and budget classification are identical to the live path.

Never infers a scientific result from a partial marker: the final atomic name must exist,
the schema/cell/run binding must match, and every referenced evidence file must re-hash.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generation_paths as GP                                                   # noqa: E402

MARKER_SCHEMA = "rebaseguard.p5y.k1.ps1.cell-done-marker.v1"
FINALIZED_FROM_MARKER = "FINALIZED_FROM_DURABLE_MARKER"


def _launcher(spec):
    d = str(Path(spec["production_root"]) / "level4/closure_proofs/p5y_k1_ps1_production/driver")
    if d not in sys.path:
        sys.path.insert(0, d)
    import ps1_cellseq_launcher as PL                                   # noqa: E402
    return PL


def _markers(spec, launcher_pid, roots=None):
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
    out = {}
    if not root.exists():
        return out
    for p in sorted(root.rglob("cell_done_[0-9]*.json")):
        try:
            m = json.loads(p.read_text())
        except (OSError, ValueError):
            continue                                   # truncated => not a completion
        if m.get("marker_schema") != MARKER_SCHEMA:
            continue
        if launcher_pid is not None and m.get("launcher_pid") != launcher_pid:
            continue                                   # wrong run/generation => rejected
        cell = m.get("cell_id")
        if isinstance(cell, int):
            out.setdefault(cell, (p, m))
    return out


def reconcile(contract, role, spec, io, launcher_pid, *, validator=None, say=print) -> dict:
    """Convert durable completions into authoritative commits BEFORE settlement.

    Idempotent: a cell the launcher already committed has no open reservation (and its
    sealed record already exists on disk), so it is skipped -- never double-committed.
    """
    rep = {"scanned": 0, "finalized": [], "skipped_already_committed": [],
           "rejected": [], "no_marker": []}
    try:
        PL = _launcher(spec)
    except Exception as exc:                                            # noqa: BLE001
        rep["error"] = f"launcher import failed: {type(exc).__name__}: {exc}"
        return rep

    st = io.read() or {}
    open_res = {k: v for k, v in (st.get("open_reservations") or {}).items()
                if k.startswith(f"{role}:")}
    if not open_res:
        return rep
    roots = GP.GenerationPaths.for_host(contract, role).marker_roots()
    rep["marker_roots"] = [str(r) for r in roots]
    marks = _markers(spec, launcher_pid, roots=roots)
    rep["scanned"] = len(marks)
    if not marks:
        rep["no_marker"] = sorted(v["cell_id"] for v in open_res.values())
        return rep

    auth = PL.load_production_authorization()
    ah = PL.authorization_hash()
    adapter = auth["scientific_adapter_hash"]
    import supervisor as SV                                             # noqa: E402
    owners = SV.owners_of(spec, contract)
    M, GB = __import__("opscommon").frozen_accounting(spec)
    budget = __import__("opscommon").frozen_budget(spec, contract)
    pf = {"auth": auth, "role": role, "owners": owners, "budget": budget}

    for key, res in sorted(open_res.items()):
        cell = res["cell_id"]
        hit = marks.get(cell)
        if hit is None:
            rep["no_marker"].append(cell)
            continue
        path, m = hit
        sealed_path = (Path(spec["production_root"]) /
                       "level4/closure_proofs/p5y_k1_ps1_production/production/cells" /
                       f"{cell:04d}.json")
        if sealed_path.exists() or str(cell) in (st.get("completed_cells") or {}):
            rep["skipped_already_committed"].append(cell)
            continue
        task = {"task_id": m.get("task_id"), "evidence_dir": str(path.parent)}
        ok = validator(m, cell, task) if validator else PL._verified(m, cell, task)
        if not ok:
            rep["rejected"].append({"cell": cell, "why": "marker/evidence validation failed"})
            continue
        try:
            actual, sealed = PL._seal_one(pf, cell, task, m, ah, adapter)
            budget.commit(key, actual, sealed)
        except Exception as exc:                                        # noqa: BLE001
            rep["rejected"].append({"cell": cell, "why": f"{type(exc).__name__}: {exc}"[:200]})
            continue
        rep["finalized"].append(cell)
        say(f"reconciled cell {cell}: {FINALIZED_FROM_MARKER} (durable marker {path.name})")
    return rep
