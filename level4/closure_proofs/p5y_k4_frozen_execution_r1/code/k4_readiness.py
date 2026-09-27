"""K4 input-readiness gate (Phase B). READ-ONLY. Evaluates no K4 decision (no R_cell / Rprime_cell sign is read).

Independent of the frozen code/k4_assembly.py: it re-derives every identity the frozen checkpoint
(K4_ASSEMBLY_CHECKPOINT.json sha256 95b1fd16...) requires of its inputs, and additionally checks what the frozen
code leaves implicit -- that each record's geometry (e0, rho) equals the hash-bound frozen domain table.

  python k4_readiness.py --checkpoint CKPT --sr-sealed-cells DIR --sr-table T --sr-integrity-audit A
                         --cusum-records DIR --cusum-table T --cusum-attestation ATT --cusum-manifest MAN --out OUT
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

M_SCOPE = {"1", "2", "3", "5"}
CKPT_SHA = "95b1fd16ac420d6f545cbb2619a6086ced31c6d748a9c801ca7f7c114e77a1e1"
FROZEN_CUSUM_PRODUCER_IDENTITY = "3692d0feeaef71365798cd99399fdb6d744573f38d59dba5cfe2e99294f0ae19"


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(p) -> str:
    return sha_bytes(Path(p).read_bytes())


def t4_canonical(o) -> bytes:
    return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str) + "\n").encode()


def exact(pair):
    return F(pair[0]), F(pair[1])


def domain_from_table(cells, detector):
    """Frozen predicate: non-symbolic cell with left < 2 and right > 0."""
    out = {}
    for c in cells:
        if c["detector"] != detector:
            continue
        e0, rho = exact(c["e0"]), exact(c["rho"])
        if e0[1] != 0 or rho[1] != 0:
            continue
        left, right = e0[0] - rho[0], e0[0] + rho[0]
        if exact(c["left"]) != (left, F(0)) or exact(c["right"]) != (right, F(0)):
            raise SystemExit(f"table inconsistency {detector} {c['index']}")
        if left < 2 and right > 0:
            out[c["index"]] = (left, right, c["e0"], c["rho"])
    return out


def contiguous(dom):
    cs = sorted(dom.values(), key=lambda t: t[0])
    return (bool(cs) and cs[0][0] == 0 and cs[-1][1] >= 2
            and all(a[1] == b[0] for a, b in zip(cs, cs[1:])))


def check_entries(rec, det, problems, tag):
    if set(rec["m"]) != M_SCOPE:
        problems.append(f"{tag}: m scope {sorted(rec['m'])}")
        return
    for m, v in rec["m"].items():
        if v.get("detector") != det:
            problems.append(f"{tag} m={m}: detector {v.get('detector')}")
        for key in ("R_interval", "D_interval"):
            iv = v.get(key) or {}
            if not all(isinstance(iv.get(s), str) for s in ("lo", "hi")):
                problems.append(f"{tag} m={m}: {key} not exact-rational strings")
            elif iv.get("encoding") != "outward exact rational endpoints":
                problems.append(f"{tag} m={m}: {key} encoding {iv.get('encoding')}")
        if not isinstance(v.get("M_R2"), str):
            problems.append(f"{tag} m={m}: M_R2 not an exact-rational string")
        if "e0" in v and v["e0"] != rec["e0"] or "rho" in v and v["rho"] != rec["rho"]:
            problems.append(f"{tag} m={m}: per-m geometry differs from record geometry")


def main() -> int:
    ap = argparse.ArgumentParser()
    for a in ("checkpoint", "sr-sealed-cells", "sr-table", "sr-integrity-audit", "cusum-records", "cusum-table",
              "cusum-attestation", "cusum-manifest", "out"):
        ap.add_argument("--" + a, required=True)
    a = ap.parse_args()
    ck = json.loads(Path(a.checkpoint).read_text())
    rep = {"schema": "rebaseguard.p5y.k4.input-readiness.v1", "k4_values_evaluated": False,
           "checkpoint_sha256": sha_file(a.checkpoint)}
    probs = {"checkpoint": [], "SR": [], "CUSUM": []}
    if rep["checkpoint_sha256"] != CKPT_SHA:
        probs["checkpoint"].append("checkpoint sha256 differs from the frozen 95b1fd16...")

    # ---------------- SR
    if sha_file(a.sr_table) != ck["domain"]["SR"]["table_sha256"]:
        probs["SR"].append("SR table sha256 differs from checkpoint")
    sr_tab = json.loads(Path(a.sr_table).read_text())["cells"]
    sr_dom = domain_from_table(sr_tab, "SR")
    sr_by_idx = {c["index"]: c for c in sr_tab}
    audit = json.loads(Path(a.sr_integrity_audit).read_text())
    if not (audit.get("schema") == "rebaseguard.p5y.k1.ps1.postk1-adjudication-audit.v1"
            and audit.get("INTEGRITY_READY_FOR_ADJUDICATION") is True
            and (audit.get("A_completeness") or {}).get("complete") is True and not audit.get("issues")):
        probs["SR"].append("Lane C audit not INTEGRITY_READY / complete / issue-free")
    sealed = sorted(Path(a.sr_sealed_cells).glob("[0-9][0-9][0-9][0-9].json"))
    sr_seen, sr_checkpoints, sr_prov = set(), set(), set()
    for p in sealed:
        s = json.loads(p.read_text())
        ev = (s.get("evidence") or {}).get("t4") or {}
        if not ev or sha_file(ev["path"]) != ev["sha256"]:
            probs["SR"].append(f"{p.name}: t4 evidence hash drift")
            continue
        t4 = json.loads(Path(ev["path"]).read_text())
        body = {k: v for k, v in t4.items() if k != "t4_record_sha256"}
        if sha_bytes(t4_canonical(body)) != t4.get("t4_record_sha256"):
            probs["SR"].append(f"{p.name}: t4_record_sha256 mismatch")
        if t4.get("cell") != s.get("cell_id") or int(p.stem) != s.get("cell_id"):
            probs["SR"].append(f"{p.name}: cell identity mismatch")
        idx = t4.get("cell")
        tab = sr_by_idx.get(idx)
        if tab is None or t4["e0"] != tab["e0"] or t4["rho"] != tab["rho"] or s.get("successor_id") != tab.get("id"):
            probs["SR"].append(f"SR cell {idx}: geometry/id differs from frozen successor_cells.json")
        check_entries(t4, "SR", probs["SR"], f"SR cell {idx}")
        sr_seen.add(idx)
        sr_checkpoints.add(s.get("checkpoint_sha256"))
        prov = s.get("production_provenance") or {}
        sr_prov.add((prov.get("production_authorization_hash"), prov.get("synthetic"), prov.get("task_kind")))
    if sr_seen != set(range(369)):
        probs["SR"].append(f"SR sealed set != 0..368 (have {len(sr_seen)})")
    if not set(sr_dom) <= sr_seen:
        probs["SR"].append(f"SR domain cells missing: {sorted(set(sr_dom) - sr_seen)[:10]}")
    rep["SR"] = {"sealed_records": len(sealed), "domain_cells": len(sr_dom),
                 "domain_indices": [min(sr_dom), max(sr_dom)] if sr_dom else None,
                 "domain_contiguous_0_to_ge_2": contiguous(sr_dom),
                 "domain_last_right": str(max(t[1] for t in sr_dom.values())) if sr_dom else None,
                 "sealed_checkpoint_sha256_values": sorted(x for x in sr_checkpoints if x),
                 "production_provenance_values": sorted([list(map(str, t)) for t in sr_prov]),
                 "lane_c_audit_sha256": sha_file(a.sr_integrity_audit)}
    if sr_prov != {("fc7cb93465916c3a7842066701b0e11fb6799bfdfc7fff55073a3f6e4cfc03ef", False, "SCIENCE")}:
        probs["SR"].append(f"SR production provenance not uniform genuine SCIENCE under fc7cb934: {sr_prov}")

    # ---------------- CUSUM
    if sha_file(a.cusum_table) != ck["domain"]["CUSUM"]["table_sha256"]:
        probs["CUSUM"].append("CUSUM table sha256 differs from checkpoint")
    cu_tab = json.loads(Path(a.cusum_table).read_text())
    cu_dom = domain_from_table(cu_tab, "CUSUM")
    cu_by_idx = {c["index"]: c for c in cu_tab if c["detector"] == "CUSUM"}
    att = json.loads(Path(a.cusum_attestation).read_text())
    if not (att.get("schema") == "rebaseguard.p5y.k1.cusum-production.integrity-attestation.v1"
            and att.get("cells_verified") == 326 and att.get("all_scientific_hashes_verified") is True
            and att.get("producer_identity_hash") == FROZEN_CUSUM_PRODUCER_IDENTITY
            and att.get("producer_checkpoint_sha256")):
        probs["CUSUM"].append("CUSUM attestation does not meet the checkpoint integrity clause")
    man = json.loads(Path(a.cusum_manifest).read_text())
    root = Path(a.cusum_manifest).parent
    recs = sorted(Path(a.cusum_records).glob("*.json"))
    cu_seen = set()
    for p in recs:
        rel = f"{Path(a.cusum_records).name}/{p.name}"
        if man["files"].get(rel) != sha_file(p):
            probs["CUSUM"].append(f"{rel}: sha256 differs from export manifest")
        r = json.loads(p.read_text())
        idx = r.get("cell_index")
        if idx in cu_seen:
            probs["CUSUM"].append(f"duplicate CUSUM cell {idx}")
        cu_seen.add(idx)
        if r.get("producer_identity_hash") != att.get("producer_identity_hash"):
            probs["CUSUM"].append(f"CUSUM cell {idx}: producer identity differs from attestation")
        tab = cu_by_idx.get(idx)
        if tab is None or r["e0"] != tab["e0"] or r["rho"] != tab["rho"]:
            probs["CUSUM"].append(f"CUSUM cell {idx}: geometry differs from frozen cells.json")
        if r.get("detector") != "CUSUM":
            probs["CUSUM"].append(f"CUSUM cell {idx}: top-level detector {r.get('detector')}")
        check_entries(r, "CUSUM", probs["CUSUM"], f"CUSUM cell {idx}")
    if len(man["files"]) != 326 or len(recs) != 326 or cu_seen != set(range(326)):
        probs["CUSUM"].append("CUSUM export is not exactly cells 0..325")
    if not set(cu_dom) <= cu_seen:
        probs["CUSUM"].append(f"CUSUM domain cells missing: {sorted(set(cu_dom) - cu_seen)[:10]}")
    rep["CUSUM"] = {"records": len(recs), "domain_cells": len(cu_dom),
                    "domain_indices": [min(cu_dom), max(cu_dom)] if cu_dom else None,
                    "domain_contiguous_0_to_ge_2": contiguous(cu_dom),
                    "domain_last_right": str(max(t[1] for t in cu_dom.values())) if cu_dom else None,
                    "attestation_sha256": sha_file(a.cusum_attestation),
                    "attested_producer_identity_hash": att.get("producer_identity_hash"),
                    "attested_producer_checkpoint_sha256": att.get("producer_checkpoint_sha256"),
                    "export_manifest_sha256": sha_file(a.cusum_manifest)}
    rep["problems"] = probs
    rep["K4_INPUT_READINESS"] = "PASS" if not any(probs.values()) and rep["SR"]["domain_contiguous_0_to_ge_2"] \
        and rep["CUSUM"]["domain_contiguous_0_to_ge_2"] else "FAIL"
    Path(a.out).write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"K4_INPUT_READINESS": rep["K4_INPUT_READINESS"],
                      "problems": {k: len(v) for k, v in probs.items()},
                      "SR_domain": rep["SR"]["domain_indices"], "CUSUM_domain": rep["CUSUM"]["domain_indices"]}))
    return 0 if rep["K4_INPUT_READINESS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
