"""CUSUM Aux5 composite closure: deterministic verifier and record builder. READ-ONLY, RESULT-AGNOSTIC.

Everything this verifier needs is committed in this namespace: it never contacts the production host and never
requires the external 326-record export tree. It verifies

  1  every committed closure artifact against config/ARTIFACT_HASHES.json;
  2  that config/ARTIFACT_HASHES.json and config/CLOSURE_VERDICT.json rebuild byte-identically from that evidence;
  3  the composite audit: COMPLETE, K4-ready, 128 carry-over + 198 successor pairs, union exactly 0-325, no overlap,
     no missing cell, exactly the two tolerated predecessor issues, no successor issue;
  4  the K4 composite attestation, by rebuilding it from the audit with the FROZEN glibc-successor code
     (gs_composite.build_composite_attestation) and requiring canonical equality;
  5  the export manifest: 326 records covering 0-325, each record hash equal to the audited pair;
  6  the predecessor binding: unchanged hash, and the same terminal ledger state as the audited predecessor half.

  python -B code/verify_closure.py                      # verify the Git-resident package (exit 0 iff it verifies)
  python -B code/verify_closure.py --export-tree DIR     # additionally verify a retrieved external export tree
  python -B code/verify_closure.py build                 # rebuild config/ARTIFACT_HASHES.json + CLOSURE_VERDICT.json

The closure facts that no Git object can carry (the external export tree digest and size, the terminal runtime
ledger and journal hashes, and the settled CPU accounting) are declared once in ATTESTED below, exactly as the
gated terminal-closure run reported them on rebaseguard-vultr-02.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
GLIBC = REPO / "level4/closure_proofs/p5y_k1_cusum_aux5_glibc_successor"
for p in (GLIBC / "code",
          REPO / "level4/closure_proofs/p5y_k1_cusum_aux5_production_checkpoint/code",
          REPO / "level4/closure_proofs/p5y_k1_cusum_aux5_production_provenance_successor/code"):
    sys.path.insert(0, str(p))

import gs_composite as GC                                                        # noqa: E402
import gs_schema as GS                                                           # noqa: E402
from prod_common import canonical, sha256_bytes                                  # noqa: E402

EV = "evidence/closure_r1"
ARTIFACTS = ["COMPOSITE_AUDIT.json", "K4_COMPOSITE_ATTESTATION.json", "PREDECESSOR_BINDING_FINAL.json",
             "COMPOSITE_EXPORT_MANIFEST.json", "HOST_AT_CLOSURE.json",
             "CONTAINMENT_PRE_RESTORE.json", "CONTAINMENT_POST_RESTORE.json"]
HASHES = "config/ARTIFACT_HASHES.json"
VERDICT = "config/CLOSURE_VERDICT.json"

SUCCESSOR_CHECKPOINT = "f9380847c92b6f5eb014d56021d11c2b66a95bef0990e392c7021c05d537a6cb"
SUCCESSOR_AUTHORIZATION = "0c7621d47fd862e06355276492fe9a425f8fe2eec280d8c7375a4acedaaa043f"
CARRYOVER_COUNTERSIGNATURE = "e1ee7fb112c4d013c53f3adf10f12421c04b39f2ec1d3edd98ec2cc07edf143a"
PREDECESSOR_CHECKPOINT = "dd4c89d773c411355d93d0d703e40c027f9913e11e116e4bfe35117f84b4baf2"
PREDECESSOR_AUTHORIZATION = "b8f11ec05efc2476f733dd989ae02b542dc9efa374f24fa0a27688d76ec2b329"
PREDECESSOR_COUNTERSIGNATURE = "1ceb92d463d1332dfb26505143454b3c3fd87a611bc731372d9e227017682b07"
CANONICAL_AUDIT_DIGEST = "fa1d79b52c8ac6014c34ced67f1c53dd862b55c66cd6fcee47ab1797c7404266"

ATTESTED = {
    "external_export_tree": {
        "host": "rebaseguard-vultr-02",
        "path": "/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT",
        "records": 326,
        "record_universe": [0, 325],
        "bytes": 93128357,
        "tree_sha256_attested": "5c3c1f854fd04ea44a9a9a14902c7ba6bf4361fa5fa5bb9c311124de281acf59",
        "tree_sha256_attested_rule": "sha256 of `find . -type f | sort | xargs sha256sum` over k4_records/ as computed at "
                                    "closure on the host, whose LANG was en_US.UTF-8: the listing is in that locale's "
                                    "collation order, so this value is locale-dependent",
        "tree_sha256_bytewise": "7517199ae57fe99dd63e60bd820c72349f6faf1e5cf139be75ce331a6fedb0a3",
        "tree_sha256_bytewise_rule": "the same listing under `LC_ALL=C sort` (equivalently Python's byte-order sort): "
                                     "`sha256(''.join(f'{sha256(file)}  ./{name}\\n' for name in sorted(names)))`. "
                                     "Locale-independent, and the value verify_closure.py --export-tree checks",
        "manifest_sha256": "29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334",
        "committed_to_git": False},
    "terminal_runtime": {
        "host": "rebaseguard-vultr-02",
        "root": "/root/work/postk1-runs/cusum-aux5-production-glibc-r1",
        "ledger_sha256": "d6f63cf41910437ebc2a0c3413b0698ada3ab4170a6ac1db23b7dd195c0b1a59",
        "journal_sha256": "c59a243d560067495d90647dcf0d59a368afcf74c445e627f6835670e544ad58",
        "ledger_state_sha256": "241af4f12aa6ee390af6c113cbc262cbefbb9476f6f442be7acfd40f877cffca",
        "seq": 2531,
        "committed_to_git": False},
    "cpu_accounting_usec": {
        "pre_settlement_total": 412497973063,
        "post_settlement_total": 412551818627,
        "science": 412353959598,
        "settlement_overhead": 53845564,
        "supervisor_extra": 381577,
        "keeper_overhead": 53463987,
        "successor_residual_cap": 817313389420,
        "predecessor_settled": 262686610580,
        "absolute_campaign_cap": 1080000000000},
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _json(rel: str, ns: Path) -> dict:
    return json.loads((ns / rel).read_bytes())


def halves(rep: dict) -> tuple[set, set]:
    return ({int(c) for c in rep["halves"]["predecessor"]["pairs"]},
            {int(c) for c in rep["halves"]["successor"]["pairs"]})


def build_hashes(ns: Path = NS) -> dict:
    return {"schema": "rebaseguard.p5y.k1.cusum-aux5.composite-closure.artifact-hashes.v1",
            "git_artifacts": {f"{EV}/{n}": sha256_file(ns / EV / n) for n in ARTIFACTS},
            "governance_objects": {
                "successor_checkpoint_sha256": SUCCESSOR_CHECKPOINT,
                "successor_authorization_sha256": SUCCESSOR_AUTHORIZATION,
                "carryover_countersignature_sha256": CARRYOVER_COUNTERSIGNATURE,
                "predecessor_checkpoint_sha256": PREDECESSOR_CHECKPOINT,
                "predecessor_authorization_sha256": PREDECESSOR_AUTHORIZATION,
                "predecessor_countersignature_sha256": PREDECESSOR_COUNTERSIGNATURE,
                "predecessor_binding_sha256": sha256_file(ns / EV / "PREDECESSOR_BINDING_FINAL.json"),
                "canonical_composite_audit_sha256": CANONICAL_AUDIT_DIGEST},
            "external_evidence": {k: ATTESTED[k] for k in ("external_export_tree", "terminal_runtime")},
            "cpu_accounting_usec": ATTESTED["cpu_accounting_usec"]}


def build_verdict(ns: Path = NS) -> dict:
    rep = _json(f"{EV}/COMPOSITE_AUDIT.json", ns)
    att = _json(f"{EV}/K4_COMPOSITE_ATTESTATION.json", ns)
    man = _json(f"{EV}/COMPOSITE_EXPORT_MANIFEST.json", ns)
    old, new = halves(rep)
    return {"schema": "rebaseguard.p5y.k1.cusum-aux5.composite-closure.verdict.v1",
            "cusum_aux5_composite_closure": "CLOSED",
            "k4_attestation": "PASS",
            "composite_universe": [min(old | new), max(old | new)],
            "composite_total": len(old | new),
            "carryover_universe": [min(old), max(old)],
            "carryover_cells": len(old),
            "successor_universe": [min(new), max(new)],
            "successor_cells": len(new),
            "predecessor_cells_recomputed": False,
            "predecessor_disposition": rep["halves"]["predecessor"]["disposition"],
            "successor_disposition": rep["halves"]["successor"]["disposition"],
            "successor_sealed": len(new),
            "successor_failed": 0,
            "successor_torn": 0,
            "composite_audit_state": rep["state"],
            "k4_ready": rep["K4_READY"],
            "attested_cell_count": att["cells_verified"],
            "export_records": man["cells"],
            "producer_identity_hash": rep["producer_identity_hash"],
            "governance": {
                "successor_checkpoint_sha256": SUCCESSOR_CHECKPOINT,
                "successor_authorization_sha256": SUCCESSOR_AUTHORIZATION,
                "carryover_countersignature_sha256": CARRYOVER_COUNTERSIGNATURE,
                "predecessor_checkpoint_sha256": PREDECESSOR_CHECKPOINT,
                "predecessor_binding_sha256": sha256_file(ns / EV / "PREDECESSOR_BINDING_FINAL.json"),
                "canonical_composite_audit_sha256": CANONICAL_AUDIT_DIGEST},
            "cpu_accounting_usec": ATTESTED["cpu_accounting_usec"],
            "scope": "This verdict closes the CUSUM Aux5 composite production universe 0-325 only. It is not a K1, "
                     "P5Y, SR or PS1 verdict, and it evaluates no K4 scientific value.",
            "tolerated_predecessor_issues": rep["tolerated_predecessor_issues"]}


def write_records(ns: Path = NS) -> list[str]:
    written = []
    for rel, obj in ((HASHES, build_hashes(ns)), (VERDICT, build_verdict(ns))):
        (ns / rel).write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")
        written.append(rel)
    return written


def verify(ns: Path = NS, export_tree: Path | None = None) -> list[str]:
    p: list[str] = []
    for name in ARTIFACTS:
        if not (ns / EV / name).is_file():
            p.append(f"MISSING_ARTIFACT: {EV}/{name}")
    if p:
        return p
    for rel, rebuilt in ((HASHES, build_hashes(ns)), (VERDICT, build_verdict(ns))):
        if not (ns / rel).is_file():
            p.append(f"MISSING: {rel}")
        elif (ns / rel).read_text() != json.dumps(rebuilt, indent=1, sort_keys=True) + "\n":
            p.append(f"DOES_NOT_REBUILD: {rel}")
    if p:
        return p

    inv = _json(HASHES, ns)
    for rel, want in inv["git_artifacts"].items():
        if not (ns / rel).is_file():
            p.append(f"MISSING_ARTIFACT: {rel}")
        elif sha256_file(ns / rel) != want:
            p.append(f"ARTIFACT_HASH_DIFFERS: {rel}")
    if p:
        return p

    rep = _json(f"{EV}/COMPOSITE_AUDIT.json", ns)
    att = _json(f"{EV}/K4_COMPOSITE_ATTESTATION.json", ns)
    man = _json(f"{EV}/COMPOSITE_EXPORT_MANIFEST.json", ns)
    binding = _json(f"{EV}/PREDECESSOR_BINDING_FINAL.json", ns)
    verdict = _json(VERDICT, ns)
    old, new = halves(rep)

    if rep.get("state") != "COMPLETE" or not rep.get("K4_READY") or rep.get("problems"):
        p.append(f"AUDIT_NOT_COMPLETE: {rep.get('state')} {rep.get('problems')}")
    if sorted(old) != list(GS.OLD_CELLS):
        p.append("CARRYOVER_UNIVERSE_IS_NOT_0_127")
    if sorted(new) != list(GS.NEW_CELLS):
        p.append("SUCCESSOR_UNIVERSE_IS_NOT_128_325")
    if old & new:
        p.append(f"PARTITION_OVERLAP: {sorted(old & new)[:8]}")
    if (old | new) != set(range(GS.UNIVERSE)):
        p.append(f"UNION_IS_NOT_0_325: missing {sorted(set(range(GS.UNIVERSE)) - (old | new))[:8]}")
    if list(rep.get("tolerated_predecessor_issues") or []) != list(GS.TOLERATED_ISSUES):
        p.append("TOLERATED_PREDECESSOR_ISSUES_CHANGED")
    if rep.get("successor_issues"):
        p.append(f"SUCCESSOR_ISSUES: {rep['successor_issues']}")
    if not rep.get("successor_integrity_ready"):
        p.append("SUCCESSOR_INTEGRITY_NOT_READY")
    if rep["halves"]["predecessor"]["disposition"] != "HALTED":
        p.append("PREDECESSOR_DISPOSITION_CHANGED")
    if rep["halves"]["successor"]["disposition"] != "COMPLETE":
        p.append("SUCCESSOR_DISPOSITION_IS_NOT_COMPLETE")

    digest = sha256_bytes(canonical(rep))
    if digest != CANONICAL_AUDIT_DIGEST:
        p.append(f"CANONICAL_AUDIT_DIGEST_DIFFERS: {digest}")
    for where, got in (("attestation", att["production_provenance"]["composite_audit_sha256"]),
                       ("export manifest", man["composite_audit_sha256"])):
        if got != digest:
            p.append(f"AUDIT_DIGEST_NOT_BOUND_BY: {where}")
    try:
        GC.verify_composite_attestation(att, rep, successor_checkpoint_sha256=SUCCESSOR_CHECKPOINT,
                                        predecessor_checkpoint_sha256=PREDECESSOR_CHECKPOINT)
    except Exception as exc:                                                     # frozen refusal or mismatch
        p.append(f"ATTESTATION_DOES_NOT_REBUILD: {exc}")
    if att.get("cells_verified") != GS.UNIVERSE or att.get("mode") != "COMPOSITE":
        p.append("ATTESTATION_DOES_NOT_COVER_326_COMPOSITE_CELLS")

    cells = sorted(int(Path(f).name.split("_")[2]) for f in man["files"])
    if man.get("cells") != GS.UNIVERSE or len(man["files"]) != GS.UNIVERSE or cells != list(range(GS.UNIVERSE)):
        p.append("EXPORT_MANIFEST_IS_NOT_326_RECORDS_0_325")
    for rel, want in man["files"].items():
        cell = int(Path(rel).name.split("_")[2])
        pair = rep["halves"]["predecessor" if cell in old else "successor"]["pairs"].get(str(cell))
        if not pair or pair["record_sha256"] != want:
            p.append(f"EXPORT_RECORD_NOT_THE_AUDITED_PAIR: cell {cell}")

    if binding["ledger_state_sha256"] != rep["halves"]["predecessor"]["ledger_state_sha256"]:
        p.append("PREDECESSOR_BINDING_IS_NOT_THE_AUDITED_TERMINAL_LEDGER")
    if binding["predecessor"]["disposition"] != "HALTED" or binding["predecessor"]["checkpoint_sha256"] != PREDECESSOR_CHECKPOINT:
        p.append("PREDECESSOR_BINDING_CHANGED")
    if verdict["cusum_aux5_composite_closure"] != "CLOSED" or verdict["k4_attestation"] != "PASS":
        p.append("VERDICT_IS_NOT_CLOSED")
    if verdict["predecessor_cells_recomputed"] is not False:
        p.append("VERDICT_CLAIMS_RECOMPUTED_PREDECESSOR_CELLS")

    if export_tree is not None:
        p += verify_export_tree(Path(export_tree), man)
    return p


def verify_export_tree(root: Path, man: dict) -> list[str]:
    """Verify a retrieved external export tree (the 90 MB k4_records/ directory) against the committed manifest."""
    p: list[str] = []
    records = root / "k4_records" if (root / "k4_records").is_dir() else root
    files = sorted(x for x in records.iterdir() if x.is_file())
    if len(files) != man["cells"]:
        p.append(f"EXPORT_TREE_FILE_COUNT: {len(files)} != {man['cells']}")
    for rel, want in man["files"].items():
        f = records / Path(rel).name
        if not f.is_file():
            p.append(f"EXPORT_TREE_MISSING: {Path(rel).name}")
        elif sha256_file(f) != want:
            p.append(f"EXPORT_TREE_HASH_DIFFERS: {Path(rel).name}")
    listing = "".join(f"{sha256_file(f)}  ./{f.name}\n" for f in files).encode()
    digest = hashlib.sha256(listing).hexdigest()
    if digest != ATTESTED["external_export_tree"]["tree_sha256_bytewise"]:
        p.append(f"EXPORT_TREE_DIGEST_DIFFERS: {digest}")
    return p


def main() -> int:
    ap = argparse.ArgumentParser(description="CUSUM Aux5 composite closure verifier (read-only)")
    ap.add_argument("cmd", nargs="?", default="verify", choices=["verify", "build"])
    ap.add_argument("--export-tree", help="optional path to a retrieved external COMPOSITE_EXPORT directory")
    a = ap.parse_args()
    if a.cmd == "build":
        print(json.dumps({"written": write_records()}, indent=1))
        return 0
    problems = verify(export_tree=Path(a.export_tree) if a.export_tree else None)
    print(json.dumps({"CLOSURE_PACKAGE_VALID": not problems,
                      "CUSUM_AUX5_COMPOSITE_CLOSURE": "CLOSED" if not problems else "UNVERIFIED",
                      "external_export_tree_checked": bool(a.export_tree),
                      "problems": problems}, indent=1))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
