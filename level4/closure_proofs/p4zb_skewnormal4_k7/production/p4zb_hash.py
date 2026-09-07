"""P4ZA producer manifest and exclusion-based scientific hashing.

Same contract as P4Z: exclusion based so an unenumerated field is hashed rather
than dropped, path-based TCB, final gate after all scientific imports, no
basename exemption, HEAD recorded but excluded from the producer hash.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
REPO = NS.parent.parent.parent
REL = "level4/closure_proofs"
P4ZB = f"{REL}/p4zb_skewnormal4_k7"
P4Z = f"{REL}/p4z_location_family_feasibility"
P4 = f"{REL}/p4_theory_generalization"

TCB_PATHS = (
    # estimators, inherited from P4Z UNCHANGED and bound by content
    f"{P4Z}/src/rebaseguard_p4z/__init__.py",
    f"{P4Z}/src/rebaseguard_p4z/analytic.py",
    f"{P4Z}/src/rebaseguard_p4z/rbscore.py",
    f"{P4Z}/src/rebaseguard_p4z/rbmap.py",
    f"{P4Z}/production/runtime_contract.py",
    f"{P4Z}/production/mac_runtime_contract.json",
    # frozen P4 implementation, read-only
    f"{P4}/src/rebaseguard_p4_general/__init__.py",
    f"{P4}/src/rebaseguard_p4_general/detectors.py",
    f"{P4}/src/rebaseguard_p4_general/families.py",
    f"{P4}/src/rebaseguard_p4_general/simulate.py",
    f"{P4}/configs/P4_PROTOCOL.json",
    # P4ZB's own producer and frozen plan
    f"{P4ZB}/production/run_p4zb.py",
    f"{P4ZB}/production/p4zb_hash.py",
    f"{P4ZB}/production/p4zb_campaign_plan.json",
)

SCIENTIFIC_MODULES = (
    "rebaseguard_p4z.analytic", "rebaseguard_p4z.rbscore", "rebaseguard_p4z.rbmap",
    "rebaseguard_p4_general.detectors", "rebaseguard_p4_general.families",
    "rebaseguard_p4_general.simulate",
)

NON_SCIENTIFIC_FIELDS = frozenset({
    "cpu_seconds","wall_seconds","peak_rss_mb","started_utc","finished_utc",
    "elapsed_seconds","host_load","note","schema_note","progress",
    "scientific_hash","producer_hash",
})


class ProducerGateError(RuntimeError):
    """Fail-closed producer failure."""


def _git(*a):
    o = subprocess.run(("git","-C",str(REPO))+a, capture_output=True, text=True)
    if o.returncode: raise ProducerGateError(f"git {' '.join(a)}: {o.stderr.strip()}")
    return o.stdout.strip()


def refuse_dirty_scientific_state() -> str:
    d = _git("status","--porcelain","--",*TCB_PATHS)
    if d: raise ProducerGateError("scientific source state is dirty:\n"+d)
    return _git("rev-parse","HEAD")


def build_manifest() -> dict:
    entries = {}
    for rel in sorted(TCB_PATHS):
        p = REPO/rel
        if not p.exists(): raise ProducerGateError(f"TCB path missing: {rel}")
        entries[rel] = {"git_blob": _git("rev-parse", f"HEAD:{rel}"),
                        "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
    m = {"schema":"rebaseguard.p4zb-producer-manifest.v1","entries":entries}
    m["producer_hash"] = hashlib.sha256(
        json.dumps({k:v for k,v in m.items() if k!="producer_hash"},
                   indent=2, sort_keys=True).encode()).hexdigest()
    m["head_informational"] = _git("rev-parse","HEAD")
    return m


def verify_manifest(m: dict) -> None:
    body = {k:v for k,v in m.items() if k not in ("producer_hash","head_informational")}
    if hashlib.sha256(json.dumps(body,indent=2,sort_keys=True).encode()).hexdigest() != m["producer_hash"]:
        raise ProducerGateError("producer manifest's own hash does not match")
    for rel, e in m["entries"].items():
        p = REPO/rel
        if not p.exists(): raise ProducerGateError(f"TCB path vanished: {rel}")
        if hashlib.sha256(p.read_bytes()).hexdigest() != e["sha256"]:
            raise ProducerGateError(f"TCB file changed mid-run: {rel}")


def final_producer_gate(m: dict) -> None:
    allowed = {str((REPO/rel).resolve()) for rel in m["entries"]}
    for name in SCIENTIFIC_MODULES:
        mod = sys.modules.get(name)
        if mod is None:
            raise ProducerGateError(f"final gate: {name!r} was never imported")
        f = getattr(mod, "__file__", None)
        if f is None or str(Path(f).resolve()) not in allowed:
            raise ProducerGateError(
                f"final gate: {name!r} resolved to {f}, not in the manifest")
    verify_manifest(m)


def _strip(node, path=""):
    if isinstance(node, dict):
        return {k:_strip(v,f"{path}.{k}") for k,v in node.items()
                if k not in NON_SCIENTIFIC_FIELDS}
    if isinstance(node,(list,tuple)):
        return [_strip(v,f"{path}[{i}]") for i,v in enumerate(node)]
    if isinstance(node,(str,int,float,bool)) or node is None:
        return node
    raise ProducerGateError(f"unknown scientific field type at {path}: {type(node).__name__}")


def scientific_hash(doc: dict) -> str:
    return hashlib.sha256(json.dumps(_strip(doc),indent=2,sort_keys=True,
                                     ensure_ascii=True,allow_nan=False).encode()).hexdigest()
