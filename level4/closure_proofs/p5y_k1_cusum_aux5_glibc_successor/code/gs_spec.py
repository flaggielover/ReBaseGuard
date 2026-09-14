"""Campaign specifications of the new-glibc successor. NON-CERTIFYING.

  production_spec()   every value from the frozen, hash-bound GLIBC_SUCCESSOR_CHECKPOINT.json: universe exactly 128-325,
                      ledger genesis cap = the residual cap, per-admission guard = the frozen host facts + all 11
                      system-library hashes + the bound boot id
  synthetic_spec(cfg) the provenance synthetic spec (unchanged synthetic worker) with the successor universe rule;
                      refused inside any production runtime root

The universe rule is enforced three times: here (an old cell in any successor universe is refused), by the frozen
op_reserve (CELL_NOT_IN_UNIVERSE) and by the frozen validate_state (a ledger with another cell set is corrupt).
"""
from __future__ import annotations

import json
from pathlib import Path

import gs_schema as GS
import prod_cells
import prov_spec
from gs_host import library_hashes
from prod_common import Refusal, boot_id, sha256_bytes, sha256_file
from prod_spec import CampaignSpec


class SuccessorSpec(CampaignSpec):
    """A CampaignSpec whose admission guard also covers the system libraries and the boot."""

    def host_guard(self) -> list[str]:
        problems = super().host_guard()
        libs = getattr(self, "library_expected", None) or {}
        if libs:
            live = library_hashes()
            problems += [f"host system library {p}: live {live.get(p)!r} != bound {h!r}" for p, h in libs.items()
                         if live.get(p) != h]
        boot = getattr(self, "boot_expected", None)
        if boot and boot_id() != boot:
            problems.append(f"host boot_id: live {boot_id()!r} != bound {boot!r}")
        return problems


def check_universe(indices) -> None:
    idx = [int(c) for c in indices]
    old = sorted(set(idx) & set(GS.OLD_CELLS))
    if old:
        raise Refusal("RECOMPUTATION_OF_CARRYOVER_CELL", f"cells {old[:8]} are carried over and never enter a successor ledger")
    if len(set(idx)) != len(idx) or not set(idx) <= set(GS.NEW_CELLS):
        raise Refusal("CELL_NOT_IN_UNIVERSE", "successor cells must be distinct members of 128-325")


def check_cost_cap(cc: dict) -> None:
    if cc.get("absolute_campaign_cap_usec") != GS.ABSOLUTE_CAP_US:
        raise Refusal("CAP_ABSOLUTE_CHANGED", f"absolute cap {cc.get('absolute_campaign_cap_usec')} != 300 CPU-h")
    if cc.get("predecessor_settled_usec") != GS.PREDECESSOR_SETTLED_US:
        raise Refusal("CAP_PREDECESSOR_CONSUMPTION", f"predecessor settled {cc.get('predecessor_settled_usec')}")
    if cc.get("cap_usec") == GS.ABSOLUTE_CAP_US:
        raise Refusal("CAP_RESET_FORBIDDEN", "the successor ledger may not start from the full 300 CPU-h")
    if (cc.get("successor_residual_cap_usec") != GS.RESIDUAL_CAP_US or cc.get("cap_usec") != GS.RESIDUAL_CAP_US
            or GS.ABSOLUTE_CAP_US - GS.PREDECESSOR_SETTLED_US != GS.RESIDUAL_CAP_US):
        raise Refusal("CAP_RESIDUAL_CHANGED", f"ledger cap {cc.get('cap_usec')} != residual {GS.RESIDUAL_CAP_US}")
    if cc.get("invariant") != GS.INVARIANT or cc.get("reservation_usec") != GS.RESERVATION_US:
        raise Refusal("CAP_INVARIANT_CHANGED", "admission invariant or reservation differs")


def load_checkpoint(path=GS.CHECKPOINT, hash_path=GS.CHECKPOINT_HASH, *, root=GS.ROOT) -> tuple[dict, str]:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise Refusal("CHECKPOINT_MISSING", str(exc)) from exc
    sha = sha256_bytes(raw)
    if not Path(hash_path).exists() or Path(hash_path).read_text().strip() != sha:
        raise Refusal("CHECKPOINT_HASH", "GLIBC_SUCCESSOR_CHECKPOINT_HASH does not equal the checkpoint sha256")
    cp = json.loads(raw)
    if cp.get("schema") != GS.CHECKPOINT_SCHEMA or cp.get("status") != "FROZEN_PRE_PRODUCTION":
        raise Refusal("CHECKPOINT_SCHEMA", f"{cp.get('schema')!r} / {cp.get('status')!r}")
    drift = sorted(r for r, h in cp["bound_sources"].items() if not (Path(root) / r).exists() or sha256_file(Path(root) / r) != h)
    if drift:
        raise Refusal("BOUND_SOURCE_DRIFT", f"bound sources changed since the freeze: {drift[:6]}")
    if cp["production_universe"] != list(GS.NEW_CELLS) or cp["carryover_cells"] != list(GS.OLD_CELLS):
        raise Refusal("UNIVERSE", "checkpoint universe is not OLD 0-127 / NEW 128-325")
    check_cost_cap(cp["cost_cap"])
    return cp, sha


def spec_from_checkpoint(cp: dict, sha: str, *, root=GS.ROOT) -> SuccessorSpec:
    cells = prod_cells.cusum_cells()
    if prod_cells.geometry_digest(cells) != cp["geometry"]["geometry_digest"]:
        raise Refusal("FROZEN_GEOMETRY_MUTATED", "geometry digest differs from the checkpoint")
    manifest = Path(root) / cp["producer"]["manifest_path"]
    if sha256_file(manifest) != cp["producer"]["manifest_file_sha256"]:
        raise Refusal("PRODUCER_IDENTITY", "producer manifest v3 bytes differ from the checkpoint")
    check_universe(cp["production_universe"])
    cc, w, lc, host = cp["cost_cap"], cp["workers"], cp["lifecycle"], cp["host"]
    return SuccessorSpec(
        mode="PRODUCTION", synthetic=False, root=Path(cp["runtime_root"]), checkpoint_sha256=sha,
        campaign_id=cp["campaign_id"], cells=cells, cell_indices=list(cp["production_universe"]),
        cap_usec=int(cc["cap_usec"]), reservation_usec=int(cc["reservation_usec"]), cores=list(w["cores"]),
        poll_s=float(lc["poll_seconds"]), heartbeat_s=float(lc["heartbeat_seconds"]),
        identity=dict(cp["producer"]["record_identity"]), runtime=json.loads(manifest.read_text())["runtime"],
        precision_bits=int(cp["precision"]["precision_bits"]),
        qualification_record_sha256=frozenset(cp["qualification_firewall"]["record_file_sha256"].values()),
        worker_template=list(w["argv_template"]), worker_cwd=Path(cp["checkout_path"]), worker_env={},
        host_expected=dict(host["bound_facts"]), library_expected=dict(host["system_libraries_sha256"]),
        boot_expected=host["boot_id"], accounting_exclusions=cc["excluded_from_accounting"], require_keeper=True)


def production_spec() -> tuple:
    cp, sha = load_checkpoint()
    return spec_from_checkpoint(cp, sha), cp


def synthetic_spec(cfg: dict) -> SuccessorSpec:
    root = Path(cfg["root"]).resolve()
    for prod in (GS.SUCCESSOR_RUNTIME_ROOT, *GS.REFUSED_ROOTS):
        if root == prod or prod in root.parents:
            raise Refusal("SYNTHETIC_PRODUCTION_MIX", "a synthetic campaign may not use a production runtime root")
    if not cfg.get("predecessor_shape"):
        check_universe(cfg["cells"])
    base = prov_spec.synthetic_spec(cfg)
    fields = dict(base.__dict__)
    fields.update(library_expected=cfg.get("library_expected"), boot_expected=cfg.get("boot_expected"))
    spec = SuccessorSpec(**fields)
    drift_file = cfg.get("drift_after_records")
    if drift_file:
        spec.drift_after_records = int(drift_file)
    return spec


class SyntheticDriftSpec(SuccessorSpec):
    """Acceptance fixture only: reports a libc drift once `drift_after_records` record files exist (one core)."""

    def host_guard(self) -> list[str]:
        n = sum(1 for _ in Path(self.root).glob("attempts/*/aux5_CUSUM_*_256.json"))
        if n >= getattr(self, "drift_after_records", 10 ** 9):
            return ["host libc_sha256: live 'SYNTHETIC-NEW' != bound 'SYNTHETIC-OLD'"]
        return super().host_guard()


def synthetic_drift_spec(cfg: dict) -> SyntheticDriftSpec:
    spec = synthetic_spec(cfg)
    return SyntheticDriftSpec(**spec.__dict__)
