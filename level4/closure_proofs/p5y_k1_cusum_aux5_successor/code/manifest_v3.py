"""PHASE 3/6: the immutable committed producer manifest V2, and the final gate.

THE ARTIFACT
------------
`manifests/producer_manifest_v2.json` is committed and holds

    files    : exact repository path -> sha256, for the whole TCB
    runtime  : the complete runtime contract (see `runtime_identity`)

from which three identities are derived and carried by every certificate:

    manifest_hash          sha256(canonical(manifest))
    runtime_contract_hash  sha256(canonical(manifest["runtime"]))
    producer_identity_hash sha256(canonical(schema, manifest, runtime hashes))

An independent verifier needs the repository bytes and the declared host facts:
read the artifact, rehash every listed file from disk, recompute the three
hashes, and compare them with the record.

THE GATE, AND WHY ITS POSITION IS THE POINT
-------------------------------------------
Aux3 ran its last check BEFORE assembling the auxiliary evidence, before building
the certificates, before a lazy import, and before computing the scientific hash.
Everything after that point was unguarded -- and something did happen there: a
swallowed `import successor_producer` whose success or failure silently changed a
field inside the scientific hash.

Here `final_gate()` runs after the scientific hash exists and immediately before
the record is written. It re-verifies the manifest, re-measures loaded-module
coverage, re-compares the runtime contract, and requires the SciPy guard to be
clean. Anything imported, mutated or drifted at any point during the run is
caught, because the measurement happens last.

`initial_gate()` still runs first, so a doomed run fails in seconds rather than
after forty minutes of arithmetic; but it is the final gate that authorises a
certificate.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import ancestry5
import ancestry4
import runtime_identity5 as runtime_identity
import tcb5 as tcb

SCHEMA = "k1.cusum-aux5.producer-manifest.v3"
MANIFEST_VERSION = 3
ARTIFACT = ancestry5.NS / "manifests" / "producer_manifest_v3.json"
AUX4_MANIFEST = ancestry5.AUX4_NS / "manifests" / "producer_manifest_v2.json"


class ManifestFailure(RuntimeError):
    """The committed manifest does not describe this repository state."""


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build() -> dict:
    """The manifest for the CURRENT working tree and runtime."""
    files = {}
    for p in tcb.certifying_paths():
        path = Path(p)
        rel = str(path.resolve().relative_to(ancestry4.ROOT))
        if not path.exists():
            raise ManifestFailure(f"certifying input missing: {rel}")
        files[rel] = sha256_file(path)
    return {"schema": SCHEMA,
            "manifest_version": MANIFEST_VERSION,
            "kind": "cusum_aux5_successor_producer_manifest_v3",
            "files": dict(sorted(files.items())),
            "runtime": runtime_identity.contract(),
            "boundary": {
                "membership": "exact repository-relative path",
                "basename_exemptions": [],
                "non_certifying_modules_of_this_namespace":
                    sorted(tcb.AUX5_NON_CERTIFYING),
                "note": "non-certifying modules are excluded by never being "
                        "imported on the certifying path, not by a name rule",
            }}


def load() -> dict:
    if not ARTIFACT.exists():
        raise ManifestFailure(
            f"committed producer manifest is missing: "
            f"{ARTIFACT.relative_to(ancestry4.ROOT)}")
    return json.loads(ARTIFACT.read_text())


def write() -> dict:
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    m = build()
    ARTIFACT.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
    return identity(m)


def science_unchanged_problems() -> list[str]:
    """Every Aux4 manifest-v2 input that is not an Aux4 identity-layer module must be byte-identical here."""
    aux4 = json.loads(AUX4_MANIFEST.read_text())["files"]
    replaced = {str((ancestry5.AUX4_NS / "code" / n).relative_to(ancestry4.ROOT)) for n in tcb.AUX4_REPLACED_MODULES}
    out = []
    for rel, digest in sorted(aux4.items()):
        if rel in replaced:
            continue
        path = ancestry4.ROOT / rel
        if not path.exists() or sha256_file(path) != digest:
            out.append(f"science input differs from Aux4 manifest v2: {rel}")
    return out


def manifest_hash(m: dict | None = None) -> str:
    return hashlib.sha256(canonical(m if m is not None else load())).hexdigest()


def runtime_contract_hash(m: dict | None = None) -> str:
    m = load() if m is None else m
    return hashlib.sha256(canonical(m["runtime"])).hexdigest()


def producer_identity_hash(m: dict | None = None) -> str:
    m = load() if m is None else m
    return hashlib.sha256(canonical({
        "schema": SCHEMA,
        "manifest_version": m["manifest_version"],
        "manifest_hash": manifest_hash(m),
        "runtime_contract_hash": runtime_contract_hash(m),
    })).hexdigest()


def identity(m: dict | None = None) -> dict:
    """Exactly what a certificate carries as its producer identity."""
    m = load() if m is None else m
    return {"producer_manifest_schema": m["schema"],
            "producer_manifest_version": m["manifest_version"],
            "producer_manifest_path": str(ARTIFACT.relative_to(ancestry4.ROOT)),
            "producer_manifest_hash": manifest_hash(m),
            "runtime_contract_hash": runtime_contract_hash(m),
            "producer_identity_hash": producer_identity_hash(m),
            "manifest_file_count": len(m["files"])}


def verify() -> dict:
    """Recompute every committed entry from disk. Returns the discrepancies."""
    committed = load()
    problems = []
    if committed.get("schema") != SCHEMA:
        problems.append(f"schema {committed.get('schema')!r} != {SCHEMA!r}")
    if committed.get("manifest_version") != MANIFEST_VERSION:
        problems.append(f"manifest_version {committed.get('manifest_version')!r}")
    listed = committed.get("files", {})
    for rel, sha in listed.items():
        path = ancestry4.ROOT / rel
        if not path.exists():
            problems.append(f"missing certifying input: {rel}")
            continue
        actual = sha256_file(path)
        if actual != sha:
            problems.append(f"content changed: {rel} ({actual[:12]} != {sha[:12]})")
    expected = tcb.tcb_paths()
    for extra in sorted(set(listed) - expected):
        problems.append(f"manifest lists a path outside the TCB: {extra}")
    for missing in sorted(expected - set(listed)):
        problems.append(f"TCB input absent from the manifest: {missing}")
    problems += science_unchanged_problems()
    problems += runtime_identity.compare(committed.get("runtime", {}))
    return {"ok": not problems, "problems": problems,
            "manifest_hash": manifest_hash(committed),
            "runtime_contract_hash": runtime_contract_hash(committed),
            "producer_identity_hash": producer_identity_hash(committed),
            "files": len(listed)}


def _gate(stage: str, scipy_guard=None) -> dict:
    committed = load()
    state = verify()
    if not state["ok"]:
        raise ManifestFailure(
            f"[{stage}] producer manifest does not describe this repository "
            f"state: " + "; ".join(state["problems"][:8]))
    coverage = tcb.verify_coverage(set(committed["files"]))
    if not coverage["ok"]:
        raise ManifestFailure(
            f"[{stage}] executed repository modules outside the TCB: "
            + ", ".join(coverage["uncovered"][:8]))
    runtime_identity.require(committed["runtime"])
    guard_report = None
    if scipy_guard is not None:
        guard_report = scipy_guard.require_clean()
    return {**identity(committed),
            "stage": stage,
            "loaded_repository_modules": coverage["loaded_repository_modules"],
            "tcb_size": coverage["tcb_size"],
            "runtime": committed["runtime"],
            "scipy_guard": guard_report}


def initial_gate() -> dict:
    """Cheap early failure. Does NOT authorise a certificate."""
    return _gate("initial")


def final_gate(scipy_guard=None) -> dict:
    """The gate that authorises a certificate. Must run last: after all lazy
    imports, all computation, the auxiliary evidence, the assembled certificates
    and the scientific hash."""
    return _gate("final", scipy_guard=scipy_guard)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if a.write:
        print(json.dumps(write(), indent=2, sort_keys=True))
    if a.verify or not a.write:
        state = verify()
        print(json.dumps({k: v for k, v in state.items() if k != "problems"}
                         | {"problems": state["problems"][:10]},
                         indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
