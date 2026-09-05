"""Repair2 self-audit.

A read-only self-adjudication of Repair2. Not an independent review, and it
cannot conclude WORK_UNIVERSE = PASS, implementation completeness, cost-cap
adequacy or production readiness.
"""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from fractions import Fraction as F
from pathlib import Path

import prior2

import spec                                                     # noqa: E402
import universe as reviewed                                     # noqa: E402
import repair_universe as RU1                                   # noqa: E402

import certhash                                                 # noqa: E402
import producer                                                 # noqa: E402
import provenance                                               # noqa: E402
import repair2_universe as RU2                                  # noqa: E402

NS = prior2.NS
ROOT = prior2.ROOT

PRESERVED = (
    ("frozen_successor", prior2.SPEC_NS, None),
    ("reviewed_implementation", prior2.IMPL_NS, prior2.REVIEWED_COMMIT),
    ("repair1", prior2.REPAIR1_NS, prior2.REPAIR1_COMMIT),
)


def frozen_tree_unchanged() -> bool:
    manifest = json.loads((prior2.SPEC_NS / "manifests/freeze.json").read_text())
    actual = {}
    for p in prior2.SPEC_NS.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts \
                and p != prior2.SPEC_NS / "manifests/freeze.json":
            actual[str(p.relative_to(prior2.SPEC_NS))] = \
                hashlib.sha256(p.read_bytes()).hexdigest()
    return actual == manifest["files"]


def namespace_preserved(ns: Path, commit: str) -> dict:
    rel = str(ns.relative_to(ROOT))
    out = subprocess.run(["git", "diff", "--name-only", commit, "--", rel],
                         cwd=ROOT, capture_output=True, text=True)
    changed = [x for x in out.stdout.split("\n") if x.strip()]
    return {"namespace": rel, "commit": commit, "paths_changed": changed,
            "preserved": not changed}


def load_records(directory: Path) -> list[dict]:
    if not directory.exists():
        return []
    return [json.loads(p.read_text())
            for p in sorted(directory.glob("repair2_*.json"))]


def certified_records(records: list[dict]) -> list[dict]:
    return [r for r in records if r.get("certificates")]


def substitution_attacks(record: dict) -> dict:
    """Re-run the ten attacks against a live record; every one must reject."""
    ctx = RU2.context(precision_bits=record["precision_bits"])
    certs = provenance.build_cell_certificates(record, **ctx)
    cell = record["cell_index"]
    dF2 = ("CUSUM", cell, "object", "dF_2")
    f2 = f"CUSUM|{cell}|object|F_2"
    asm5 = ("CUSUM", cell, "assembly", "5")
    leaf = ("CUSUM", cell, "object", "h_1")

    def rebuilt(mutate):
        rec = copy.deepcopy(record)
        mutate(rec)
        return provenance.build_cell_certificates(rec, **ctx)

    def rejects(fn) -> bool:
        try:
            fn()
            return False
        except RU2.ResumeRejected:
            return True

    def swap(uid, cert):
        c = dict(certs); c[uid] = cert
        return c

    out = {}
    out["modified_certified_interval"] = rejects(lambda: provenance.verify_chain(
        dF2, swap(f2, rebuilt(lambda r: r["objects"]["F_2"].__setitem__(
            "delta_mid", "1/2"))[f2]), **ctx))
    out["modified_error_bound"] = rejects(lambda: provenance.verify_chain(
        dF2, swap(f2, rebuilt(lambda r: r["objects"]["F_2"].__setitem__(
            "delta_cell", "3/4"))[f2]), **ctx))
    other_producer = provenance.build_cell_certificates(
        record, **RU2.context(producer_hash="a" * 64,
                              precision_bits=record["precision_bits"]))
    out["different_producer_hash"] = rejects(lambda: provenance.verify_chain(
        dF2, swap(f2, other_producer[f2]), **ctx))
    out["certificate_from_another_m"] = rejects(lambda: provenance.verify_chain(
        asm5, swap(f"CUSUM|{cell}|curvature|5",
                   certs[f"CUSUM|{cell}|curvature|3"]), **ctx))

    omitted = copy.deepcopy(certs[RU2.unit_id(dF2)])
    omitted["identity"]["source_certificate_hashes"].pop(f2)
    out["dependency_omitted"] = rejects(lambda: provenance.verify_chain(
        dF2, swap(RU2.unit_id(dF2), omitted), **ctx))

    extra = copy.deepcopy(certs[RU2.unit_id(dF2)])
    extra["identity"]["source_certificate_hashes"][
        f"CUSUM|{cell}|object|h_4"] = "0" * 64
    out["extra_dependency"] = rejects(lambda: provenance.verify_chain(
        dF2, swap(RU2.unit_id(dF2), extra), **ctx))

    mispaired = copy.deepcopy(certs[RU2.unit_id(dF2)])
    m = mispaired["identity"]["source_certificate_hashes"]
    k = sorted(m)
    m[k[0]], m[k[1]] = m[k[1]], m[k[0]]
    out["dependency_hashes_mispaired"] = rejects(lambda: provenance.verify_chain(
        dF2, swap(RU2.unit_id(dF2), mispaired), **ctx))

    forged = copy.deepcopy(certs[f2])
    forged["certified"]["residual"]["delta_mid"] = "1/2"
    out["forged_metadata_only"] = rejects(lambda: provenance.verify_chain(
        dF2, swap(f2, forged), **ctx))

    empty = copy.deepcopy(certs[RU2.unit_id(dF2)])
    empty["identity"]["source_certificate_hashes"] = {}
    out["non_leaf_empty_map"] = rejects(lambda: provenance.verify_chain(
        dF2, swap(RU2.unit_id(dF2), empty), **ctx))

    leafcert = copy.deepcopy(certs[RU2.unit_id(leaf)])
    leafcert["identity"]["source_certificate_hashes"] = {"x": "0" * 64}
    out["leaf_declaring_dependency"] = rejects(lambda: provenance.verify_chain(
        leaf, swap(RU2.unit_id(leaf), leafcert), **ctx))

    r1 = json.loads((prior2.REPAIR1_NS /
                     "diagnostics/regression/repaired_221_256_full.json").read_text())
    ident = list(r1["identity"].values())[0]
    unit = (ident["detector"], ident["cell_index"], ident["unit_kind"],
            ident["function_or_m"])
    out["repair1_record_as_repair2"] = rejects(
        lambda: RU2.admit_resume_record(ident, unit,
                                        dependency_certificates=certs, **ctx))

    old = copy.deepcopy(certs[RU2.unit_id(dF2)]["identity"])
    old["obligation_universe_total"] = 12255
    out["old_12255_universe"] = rejects(
        lambda: RU2.admit_resume_record(old, dF2,
                                        dependency_certificates=certs, **ctx))

    out["all_rejected"] = all(v for v in out.values() if isinstance(v, bool))
    return out


def chain_replay(records: list[dict]) -> dict:
    out = {}
    for r in certified_records(records):
        ctx = RU2.context(precision_bits=r["precision_bits"])
        v = provenance.verify_cell(r, **ctx)
        out[f"cell{r['cell_index']}_{r['precision_bits']}"] = {
            "obligations": v["obligations"], "units_verified": v["units_verified"],
            "all_verified": v["all_verified"],
            "leaf_maps_empty": v["leaf_maps_empty"]}
    return out


def sr_and_far_field_absent() -> dict:
    import qualify
    sr = qualify.run_cell("SR", 0)
    status = (prior2.IMPL_NS / "IMPLEMENTATION_STATUS.md").read_text()
    return {"sr_reports_not_implemented": sr["status"] == "NOT_IMPLEMENTED",
            "sr_never_reports_pass": "PASS" not in json.dumps(sr),
            "far_field_declared_not_implemented":
                "far-field certificates" in status and "NOT_IMPLEMENTED" in status}


def cell_325_unresolved() -> dict:
    import repair2_qualify
    rec = json.loads((prior2.IMPL_NS / "diagnostics/representatives"
                      / "CUSUM_325_256.json").read_text())
    failing = sorted(m for m, L in rec["m"].items() if L["status"] == "FAIL")
    return {"reviewed_failures_preserved": failing == ["2", "3", "5"],
            "repair2_refuses_325": 325 in repair2_qualify.FORBIDDEN_CELLS,
            "state": "CURRENT_CERTIFICATE_FAILURE_ONLY"}


def review(records_dir: Path | None = None) -> dict:
    d = records_dir or (NS / "diagnostics/regression")
    records = load_records(d)
    certified = certified_records(records)

    preserved = {name: namespace_preserved(ns, c) if c else
                 {"namespace": str(ns.relative_to(ROOT)),
                  "preserved": frozen_tree_unchanged()}
                 for name, ns, c in PRESERVED}
    attacks = substitution_attacks(certified[0]) if certified else {}
    replay = chain_replay(records)
    srff = sr_and_far_field_absent()
    c325 = cell_325_unresolved()
    s0 = all(r["s0_charge_audit"]["all_charged_exactly_once"] for r in records) \
        if records else None

    checks = {
        "frozen_successor_byte_preserved": preserved["frozen_successor"]["preserved"],
        "reviewed_implementation_byte_preserved":
            preserved["reviewed_implementation"]["preserved"],
        "repair1_byte_preserved": preserved["repair1"]["preserved"],
        "S0_double_charge_remains_fixed": s0 is True,
        "producer_hash_covers_certifying_code":
            producer.covers_repair1_producer_code()
            and producer.producer_hash() != producer.parent_hash(),
        "producer_hash_distinct_from_commit_ids":
            producer.producer_hash() not in (prior2.REVIEWED_COMMIT,
                                             prior2.REPAIR1_COMMIT),
        "loaded_modules_covered": producer.verify_loaded_modules_covered(
            strict=False)["ok"],
        "source_hashes_cover_certificate_content": bool(certified) and all(
            v["all_verified"] for v in replay.values() if v["obligations"]),
        "exact_dependency_chain_replay_passes": bool(replay) and all(
            v["all_verified"] for v in replay.values() if v["obligations"]),
        "substitution_attacks_all_reject": attacks.get("all_rejected") is True,
        "work_universe_17978_unchanged": len(reviewed.work_ids()) == 17978,
        "shard_conservation_unchanged": all(
            reviewed.verify_shard_conservation(w)["union_equals_universe"]
            for w in (1, 8, 16, 32, 64)),
        "precision_unchanged": (spec.PRODUCTION_BITS == 256
                                and not spec.PRECISION_ESCALATION_ALLOWED),
        "cap_remains_1126": spec.HARD_CAP_CPU_H == 1126,
        "budgets_unchanged": sum(spec.TOP_BUDGETS.values()) == F(19, 100),
        "production_off": spec.PRODUCTION_ENABLED is False,
        "SR_absent": (srff["sr_reports_not_implemented"]
                      and srff["sr_never_reports_pass"]),
        "far_field_absent": srff["far_field_declared_not_implemented"],
        "cell_325_unresolved": (c325["reviewed_failures_preserved"]
                                and c325["repair2_refuses_325"]),
    }
    failed = [k for k, v in checks.items() if v is False]
    return {
        "review_kind": ("read-only self-adjudication of repair2; not an "
                        "independent human or agent review"),
        "reviewed_commit": prior2.REVIEWED_COMMIT,
        "repair1_commit": prior2.REPAIR1_COMMIT,
        "producer_hash": producer.producer_hash(),
        "backend_hash": producer.backend_hash(),
        "reviewed_parent_hash": producer.parent_hash(),
        "checks": checks, "checks_failed": failed,
        "namespaces_preserved": preserved,
        "substitution_attacks": attacks,
        "chain_replay": replay,
        "verdict": ("REPAIR2_READY_FOR_INDEPENDENT_ADJUDICATION" if not failed
                    else "REPAIR2_FAILED"),
        "work_universe_verdict": "RESERVED_FOR_INDEPENDENT_ADJUDICATION",
        "production_ready": False,
        "implementation_complete": False,
        "cost_cap_status": "NOT_ESTABLISHED",
        "scientific_verdict_changed": False,
        "remaining_unresolved": [
            "SR raw DAG absent", "SR M_R2 absent", "SR all-m absent",
            "far-field not implemented",
            "cell 325 CURRENT_CERTIFICATE_FAILURE_ONLY",
            "full cost cap NOT_ESTABLISHED",
        ],
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--records")
    ap.add_argument("--out")
    args = ap.parse_args()
    result = review(Path(args.records) if args.records else None)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n")
    print(text)
    raise SystemExit(bool(result["checks_failed"]))
