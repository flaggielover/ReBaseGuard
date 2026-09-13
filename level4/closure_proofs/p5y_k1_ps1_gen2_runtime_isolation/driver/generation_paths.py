"""ONE resolver for every mutable runtime path of an execution generation.

DEFECT REPAIRED: GENERATION2_RUNTIME_PATH_SPLIT. Generation 2 bound its own runtime_dir in the
operational contract, but three independent consumers resolved runtime paths from three
different sources:

  * prodctl drain / heartbeat / lock / continuity / runs  -> contract hosts[role].runtime_dir
  * ps1_cellseq_launcher work_dir, DRAIN, evidence_dir     -> frozen LAUNCH_AUTHORIZATION hosts
                                                              (= the generation-1 runtime root)
  * ps1_reconcile durable-marker scan                      -> contract runtime_dir / "evidence"

so `prodctl drain` wrote a flag the launcher never polls, and supervisor-owned marker
reconciliation scanned a directory the launcher never writes. The synthetic acceptance hook
rewrote the authorization work_dir/evidence_dir to the contract runtime_dir, which masked both.

REPAIR (operational only, additive): every consumer derives its paths from THIS module, and the
launcher receives a copy of the frozen authorization whose hosts[role].work_dir / evidence_dir
(and nothing else) are rebound to the generation paths. The frozen authorization FILE, its hash
and every scientific identity are untouched.
"""
from __future__ import annotations

import copy
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

REBOUND_KEYS = ("work_dir", "evidence_dir")
DRAIN_NAME = "DRAIN"


class IsolationRefusal(RuntimeError):
    """A generation-isolation gate refused. Always fail closed."""


def _real(p) -> str:
    return os.path.realpath(str(p))


def _inside(child, parent) -> bool:
    c, p = _real(child), _real(parent)
    return c == p or c.startswith(p.rstrip(os.sep) + os.sep)


@dataclass(frozen=True)
class GenerationPaths:
    role: str
    runtime_root: Path
    legacy_work_roots: tuple = field(default_factory=tuple)
    legacy_evidence_roots: tuple = field(default_factory=tuple)

    @classmethod
    def for_host(cls, contract, role) -> "GenerationPaths":
        spec = contract["hosts"][role]
        iso = (contract.get("runtime_isolation") or {}).get("legacy_bound_roots", {}).get(role, {})
        return cls(role=role, runtime_root=Path(spec["runtime_dir"]),
                   legacy_work_roots=tuple(Path(p) for p in iso.get("work_dirs", [])),
                   legacy_evidence_roots=tuple(Path(p) for p in iso.get("evidence_dirs", [])))

    # every mutable path of the generation, and nothing outside runtime_root
    @property
    def work_root(self) -> Path:
        return self.runtime_root / "work"

    @property
    def evidence_root(self) -> Path:
        return self.runtime_root / "evidence"

    @property
    def drain_flag(self) -> Path:
        return self.work_root / DRAIN_NAME

    @property
    def checkpoints(self) -> Path:
        return self.runtime_root / "checkpoints"

    @property
    def export_stage(self) -> Path:
        return self.runtime_root / "export"

    @property
    def export_src(self) -> Path:
        return self.runtime_root / "export_src"

    @property
    def drain_archive(self) -> Path:
        return self.runtime_root / "quarantine" / "drain_flags"

    def as_dict(self) -> dict:
        return {"role": self.role, "runtime_root": str(self.runtime_root),
                "work_root": str(self.work_root), "evidence_root": str(self.evidence_root),
                "drain_flag": str(self.drain_flag), "checkpoints": str(self.checkpoints),
                "export_stage": str(self.export_stage), "export_src": str(self.export_src),
                "legacy_work_roots": [str(p) for p in self.legacy_work_roots],
                "legacy_evidence_roots": [str(p) for p in self.legacy_evidence_roots]}

    def marker_roots(self) -> list:
        """Roots a durable-marker reconciliation scans: the generation root first, then any
        legacy authorization-bound root (READ ONLY; markers there are pid-bound to one run)."""
        out, seen = [], set()
        for p in (self.evidence_root,) + self.legacy_evidence_roots:
            if _real(p) not in seen:
                seen.add(_real(p))
                out.append(p)
        return out

    def legacy_drain_flags(self) -> list:
        return [str(p / DRAIN_NAME) for p in self.legacy_work_roots if (p / DRAIN_NAME).exists()]


def rebind_authorization(auth: dict, role: str, paths: GenerationPaths) -> dict:
    """Deep copy of the frozen authorization with ONLY hosts[role].work_dir/evidence_dir
    rebound. Refuses if the copy differs from the original anywhere else."""
    if role not in auth.get("hosts", {}):
        raise IsolationRefusal(f"authorization has no host block for {role}")
    bound = copy.deepcopy(auth)
    h = bound["hosts"][role]
    for k in REBOUND_KEYS:
        if k not in h:
            raise IsolationRefusal(f"authorization host block lacks {k}")
    h["work_dir"], h["evidence_dir"] = str(paths.work_root), str(paths.evidence_root)
    probe = copy.deepcopy(bound)
    for k in REBOUND_KEYS:
        probe["hosts"][role][k] = auth["hosts"][role][k]
    if json.dumps(probe, sort_keys=True) != json.dumps(auth, sort_keys=True):
        raise IsolationRefusal("rebinding changed a field other than work_dir/evidence_dir")
    return bound


def rebinding_record(auth: dict, role: str, paths: GenerationPaths) -> dict:
    h = auth["hosts"][role]
    return {"schema": "rebaseguard.p5y.k1.ps1.generation-path-rebinding.v1", "role": role,
            "frozen": {k: h[k] for k in REBOUND_KEYS},
            "bound": {"work_dir": str(paths.work_root), "evidence_dir": str(paths.evidence_root)},
            "changed": sorted(k for k in REBOUND_KEYS
                              if h[k] != {"work_dir": str(paths.work_root),
                                          "evidence_dir": str(paths.evidence_root)}[k]),
            "scientific_identity_changed": False}


def gate_isolation(contract, role, paths: GenerationPaths, *, frozen_auth=None) -> dict:
    """Structural isolation. Pure path checks; reads and writes nothing."""
    spec = contract["hosts"][role]
    rt = paths.runtime_root
    for key in ("production_root", "ops_root"):
        if spec.get(key) and _inside(rt, spec[key]):
            raise IsolationRefusal(f"runtime root {rt} lies inside {key} {spec[key]}")
    eg = contract.get("execution_generation") or {}
    pred = eg.get("predecessor_production_root")
    if pred and (_inside(rt, pred) or _inside(pred, rt)):
        raise IsolationRefusal(f"runtime root {rt} aliases predecessor production root {pred}")
    for p in (paths.work_root, paths.evidence_root, paths.drain_flag, paths.checkpoints,
              paths.export_stage, paths.export_src):
        if not _inside(p, rt):
            raise IsolationRefusal(f"{p} escapes the generation runtime root {rt}")
    for legacy in paths.legacy_work_roots + paths.legacy_evidence_roots:
        if _inside(rt, legacy) or _inside(legacy, rt):
            raise IsolationRefusal(f"generation runtime root {rt} aliases legacy root {legacy}")
    rep = {"runtime_root": str(rt), "isolated": True}
    if frozen_auth is not None:
        h = frozen_auth["hosts"][role]
        rep["authorization_bound_paths"] = {k: h[k] for k in REBOUND_KEYS}
        rep["authorization_paths_differ_from_generation"] = (
            h["work_dir"] != str(paths.work_root) or h["evidence_dir"] != str(paths.evidence_root))
        for k in REBOUND_KEYS:
            if _inside(h[k], rt) and _real(h[k]) not in (_real(paths.work_root), _real(paths.evidence_root)):
                raise IsolationRefusal(f"authorization {k} {h[k]} points into the generation root "
                                       "at a non-canonical location")
    return rep
