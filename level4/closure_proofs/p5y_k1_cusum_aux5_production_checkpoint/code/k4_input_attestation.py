"""K4 CUSUM input attestation. STRUCTURAL ONLY: no K4 value is evaluated, compared, ordered or assembled.

SCHEMA ATTESTATION (before production; `attest_schema`)
  A  the frozen K4 assembly checkpoint is intact (hash file, bound sources), its CUSUM per-cell input schema is
     exactly {cell|cell_index, e0, rho, m.{1|2|3|5}.{R_interval.lo/hi, D_interval.lo/hi, M_R2, detector}}, and the
     frozen k4_assembly.py reads exactly those fields plus the record's producer_identity_hash
  B  the four qualification records (the same frozen producer; cells 318 and 323 lie outside the K4 domain (0, 2],
     so no K4-relevant value is exposed) carry every consumed field -- and the R'' interval, C_upper, precision and
     producer identity -- as exact rational strings / exact identity fields
  C  no consumed path is classified INCIDENTAL by the frozen Aux4 schema, and mutating each one moves the
     recomputed scientific_content_hash (one record per cell)
  D  enforcement: `prod_sealer.verify_record` refuses any production record failing A-C (K4_INPUT_STRUCTURE,
     K4_HASH_COVERAGE), so every sealed record satisfies them

INTEGRITY ATTESTATION (after a COMPLETE production ledger; `build_integrity_attestation`)
  emits `rebaseguard.p5y.k1.cusum-production.integrity-attestation.v1`, the exact object the frozen K4
  checkpoint's integrity clause and `k4_assembly.check_cusum_attestation` require. Not run in this phase.

  python k4_input_attestation.py schema --out ../config/K4_INPUT_SCHEMA_ATTESTATION.json
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prod_ledger as L                                                               # noqa: E402
from prod_cells import K4_E_CAP, M_VALUES                                             # noqa: E402
from prod_common import K4_NS, Refusal, atomic_write_json, sha256_bytes, sha256_file  # noqa: E402
from prod_sealer import (INTERVALS, hash_coverage_problems, k4_consumed_paths,       # noqa: E402
                         k4_structure_problems, verify_record)
from prod_spec import QUALIFICATION_RECORDS                                           # noqa: E402

SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.k4-input-schema-attestation.v1"
K4_ATTESTATION_SCHEMA = "rebaseguard.p5y.k1.cusum-production.integrity-attestation.v1"
K4_CHECKPOINT = K4_NS / "config/K4_ASSEMBLY_CHECKPOINT.json"
K4_CHECKPOINT_HASH = K4_NS / "config/K4_ASSEMBLY_CHECKPOINT_HASH"
K4_ASSEMBLY = K4_NS / "code/k4_assembly.py"
# the exact reads in the frozen k4_assembly.py that touch a CUSUM record or attestation
K4_SOURCE_READS = (
    'rec.get("cell", rec.get("cell_index"))', 'v.get("detector") for v in rec["m"].values()',
    'e0, rho = rec["e0"], rec["rho"]', 'entry["R_interval"]["lo"]', 'entry["R_interval"]["hi"]',
    'entry["D_interval"]["lo"]', 'entry["D_interval"]["hi"]', 'entry["M_R2"]', 'set(rec["m"]) != set(M_SCOPE)',
    'M_SCOPE = ("1", "2", "3", "5")', 'r.get("producer_identity_hash") != a["producer_identity_hash"]',
    'a.get("cells_verified") == 326', 'a.get("all_scientific_hashes_verified") is True',
    'a.get("producer_checkpoint_sha256")', f'CUSUM_ATTESTATION_SCHEMA = "{K4_ATTESTATION_SCHEMA}"',
    'raise AssemblyRefusal("floating-point value in a certified field")')
MUTATION_RECORDS = ("318A", "323A")


def k4_checkpoint_facts() -> tuple[dict, list]:
    problems = []
    raw = K4_CHECKPOINT.read_bytes()
    sha = sha256_bytes(raw)
    if K4_CHECKPOINT_HASH.read_text().strip() != sha:
        problems.append("K4_ASSEMBLY_CHECKPOINT_HASH does not equal the checkpoint sha256")
    cp = json.loads(raw)
    if cp.get("status") != "FROZEN_PRE_RESULT":
        problems.append(f"K4 checkpoint status {cp.get('status')!r}")
    for relpath, digest in cp["bound_sources"].items():
        if sha256_file(K4_NS / relpath) != digest:
            problems.append(f"K4 bound source drifted: {relpath}")
    per_cell = cp["input_schema"]["per_cell"]
    if set(per_cell) != {"cell|cell_index", "e0", "rho", "m"}:
        problems.append(f"K4 per-cell schema {sorted(per_cell)}")
    m_schema = per_cell["m"].get("1|2|3|5", {})
    if (set(m_schema) != {"D_interval", "M_R2", "R_interval", "detector"}
            or set(m_schema.get("D_interval", {})) != {"hi", "lo"} or set(m_schema.get("R_interval", {})) != {"hi", "lo"}):
        problems.append(f"K4 per-m schema {m_schema}")
    if cp["input_schema"].get("floats") != "refused":
        problems.append("K4 input schema does not refuse floats")
    integrity = cp["integrity"]["CUSUM"]
    for token in (K4_ATTESTATION_SCHEMA, "cells_verified == 326", "all_scientific_hashes_verified",
                  "producer_identity_hash", "producer_checkpoint_sha256"):
        if token not in integrity:
            problems.append(f"K4 CUSUM integrity clause lacks {token!r}")
    source = K4_ASSEMBLY.read_text()
    missing = [r for r in K4_SOURCE_READS if r not in source]
    if missing:
        problems.append(f"k4_assembly.py no longer reads {missing}")
    return {"checkpoint_sha256": sha, "k4_assembly_sha256": sha256_file(K4_ASSEMBLY),
            "status": cp.get("status"), "per_cell_schema": per_cell,
            "integrity_clause_cusum": integrity, "source_reads_verified": list(K4_SOURCE_READS)}, problems


def _outside_k4_domain(rec: dict) -> bool:
    e0, rho = rec["e0"], rec["rho"]
    return F(e0[1]) == 0 and F(rho[1]) == 0 and not (F(e0[0]) - F(rho[0]) < K4_E_CAP)


def attest_schema() -> dict:
    """Deterministic: no timestamps, so the entrypoint can recompute it and require byte equality."""
    k4, problems = k4_checkpoint_facts()
    records = {}
    for key, path in sorted(QUALIFICATION_RECORDS.items()):
        rec = json.loads(Path(path).read_text())
        structure = k4_structure_problems(rec)
        coverage = hash_coverage_problems(rec, mutate=key in MUTATION_RECORDS)
        outside = _outside_k4_domain(rec)
        records[key] = {"record_sha256": sha256_file(path), "cell_index": rec["cell_index"],
                        "outside_k4_domain_so_no_k4_value_exposed": outside,
                        "structure_problems": structure, "hash_coverage_problems": coverage,
                        "mutation_tested": key in MUTATION_RECORDS}
        problems += [f"{key}: {p}" for p in structure + coverage]
        if not outside:
            problems.append(f"{key}: record lies inside the K4 domain; structural attestation must not read it")
    attested = not problems
    return {"schema": SCHEMA, "K4_CUSUM_INPUT_SCHEMA_ATTESTED": "YES" if attested else "NO",
            "k4_values_evaluated": False, "k4_assembly_run": False,
            "k4_checkpoint": k4,
            "consumed_record_paths": k4_consumed_paths(),
            "required_fields": {
                "R": [f"m.{m}.R_interval.lo|hi" for m in M_VALUES],
                "R_prime": [f"m.{m}.D_interval.lo|hi" for m in M_VALUES],
                "R_double_prime_and_curvature": [f"m.{m}.R2_interval.lo|hi, m.{m}.M_R2" for m in M_VALUES],
                "midpoint_and_geometry": ["cell_index", "e0 [p, s]", "rho [p, s]", "C_upper"],
                "precision": ["precision_bits == 256", "producer.runtime.precision_bits == 256"],
                "producer_identity": ["producer_identity_hash", "producer.producer_identity_hash",
                                      "runtime_contract_hash"],
                "scientific_hash_coverage": "every path above: not INCIDENTAL under the frozen Aux4 schema, and a "
                                            "mutation moves the recomputed scientific_content_hash"},
            "interval_fields": list(INTERVALS),
            "qualification_records_read_structurally": records,
            "enforcement": {"at_seal": "prod_sealer.verify_record: K4_INPUT_STRUCTURE and K4_HASH_COVERAGE refuse "
                                       "the record, so no sealed record can lack a consumed field",
                            "after_completion": f"build_integrity_attestation emits {K4_ATTESTATION_SCHEMA}"},
            "problems": problems}


def build_integrity_attestation(spec, st: dict, *, checkpoint_sha256: str) -> dict:
    """Post-production only. Requires a COMPLETE, fully settled ledger; re-verifies every sealed record."""
    if st["disposition"] != "COMPLETE":
        raise Refusal("ATTESTATION_REFUSED", f"ledger disposition is {st['disposition']}, not COMPLETE")
    if any(not r["settled"] for r in st["supervisor_runs"].values()):
        raise Refusal("ATTESTATION_REFUSED", "supervisor runs are unsettled; run `prod_entry.py settle` first")
    records = {}
    for aid, a in sorted(st["attempts"].items()):
        if a["status"] != "SEALED":
            continue
        facts = verify_record(Path(spec.root) / a["record"], cell=a["cell"], spec=spec)
        if (facts["record_sha256"] != a["seal"]["record_sha256"]
                or facts["scientific_content_hash"] != a["seal"]["scientific_content_hash"]):
            raise Refusal("SEALED_EVIDENCE_CORRUPT", f"cell {a['cell']} no longer matches its seal")
        records[str(a["cell"])] = {"attempt": aid, "record_sha256": facts["record_sha256"],
                                   "scientific_content_hash": facts["scientific_content_hash"]}
    if sorted(int(c) for c in records) != sorted(spec.cell_indices):
        raise Refusal("ATTESTATION_REFUSED", "sealed cells differ from the frozen cell universe")
    return {"schema": K4_ATTESTATION_SCHEMA, "mode": spec.mode, "cells_verified": len(records),
            "all_scientific_hashes_verified": True, "k4_input_structure_verified": True,
            "k4_values_evaluated": False, "producer_identity_hash": spec.identity["producer_identity_hash"],
            "producer_checkpoint_sha256": checkpoint_sha256, "ledger_state_sha256": L.state_sha256(st),
            "records": records}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["schema"])
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    att = attest_schema()
    atomic_write_json(a.out, att)
    print(json.dumps({"K4_CUSUM_INPUT_SCHEMA_ATTESTED": att["K4_CUSUM_INPUT_SCHEMA_ATTESTED"],
                      "problems": att["problems"][:10]}, indent=1))
    return 0 if att["K4_CUSUM_INPUT_SCHEMA_ATTESTED"] == "YES" else 1


if __name__ == "__main__":
    raise SystemExit(main())
