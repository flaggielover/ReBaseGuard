"""Repair2 focused tests: producer identity, real certificate hashes,
chain integrity, substitution attacks and resume admission.

Every negative control here would have passed (i.e. failed to catch the attack)
under Repair1.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import prior2                                                   # noqa: E402

import spec                                                     # noqa: E402
import universe as reviewed                                     # noqa: E402
import repair_universe as RU1                                   # noqa: E402

import certhash                                                 # noqa: E402
import producer                                                 # noqa: E402
import provenance                                               # noqa: E402
import repair2_universe as RU2                                  # noqa: E402

REC221 = json.loads((prior2.REPAIR1_NS /
                     "diagnostics/regression/repaired_221_256_full.json").read_text())
REC293 = json.loads((prior2.REPAIR1_NS /
                     "diagnostics/regression/repaired_293_256_full.json").read_text())
CTX = RU2.context()
CERTS221 = provenance.build_cell_certificates(REC221, **CTX)
CERTS293 = provenance.build_cell_certificates(REC293, **CTX)

DF2 = ("CUSUM", 221, "object", "dF_2")
F2_ID = "CUSUM|221|object|F_2"
ASM5 = ("CUSUM", 221, "assembly", "5")
LEAF = ("CUSUM", 221, "object", "h_1")


def rebuild(mutate) -> dict:
    rec = copy.deepcopy(REC221)
    mutate(rec)
    return provenance.build_cell_certificates(rec, **CTX)


# =========================================================== producer identity
class ProducerIdentity(unittest.TestCase):
    def test_deterministic_and_canonically_ordered(self):
        a, b = producer.producer_manifest(), producer.producer_manifest()
        self.assertEqual(a, b)
        self.assertEqual(list(a["files"]), sorted(a["files"]))
        self.assertEqual(producer.producer_hash(a), producer.producer_hash(b))

    def test_manifest_has_no_timestamps_or_worktree_noise(self):
        blob = json.dumps(producer.producer_manifest())
        for noise in ("mtime", "ctime", "timestamp", "/tmp/", "/home/"):
            self.assertNotIn(noise, blob)
        for digest in producer.producer_manifest()["files"].values():
            self.assertEqual(len(digest), 64)
            int(digest, 16)

    def test_repair2_certifying_module_mutation_changes_the_hash(self):
        base = producer.producer_manifest()
        for name in producer.REPAIR2_MODULES:
            rel = str((prior2.NS / "code" / name).relative_to(prior2.ROOT))
            self.assertIn(rel, base["files"], name)
            m = copy.deepcopy(base)
            m["files"][rel] = "0" * 64
            self.assertNotEqual(producer.producer_hash(m),
                                producer.producer_hash(base), name)

    def test_inherited_certifying_module_mutation_changes_the_hash(self):
        base = producer.producer_manifest()
        inherited = (
            [(prior2.REPAIR1_NS / "code" / n) for n in producer.REPAIR1_MODULES]
            + [(prior2.IMPL_NS / "code" / n) for n in producer.REVIEWED_MODULES]
            + [(prior2.SPEC_NS / n) for n in producer.FROZEN_INPUTS]
            + list(producer.BACKEND_INPUTS))
        for p in inherited:
            rel = str(p.relative_to(prior2.ROOT))
            self.assertIn(rel, base["files"], rel)
            m = copy.deepcopy(base)
            m["files"][rel] = "0" * 64
            self.assertNotEqual(producer.producer_hash(m),
                                producer.producer_hash(base), rel)

    def test_generation_parameter_change_changes_the_hash(self):
        base = producer.producer_manifest()
        m = copy.deepcopy(base)
        m["generation_parameters"]["taylor_order"] = 119
        self.assertNotEqual(producer.producer_hash(m), producer.producer_hash(base))

    def test_documentation_and_diagnostics_are_out_of_scope(self):
        files = producer.producer_manifest()["files"]
        for rel in files:
            self.assertTrue(rel.endswith((".py", ".json", ".md")), rel)
            self.assertNotIn("/diagnostics/", rel)
            self.assertNotIn("/manifests/", rel)
            self.assertNotIn("/tests/", rel)
        self.assertNotIn("level4/closure_proofs/p5y_k1_cover_ledger_repair2/README.md",
                         files)
        # ERROR_ALGEBRA.md is the one .md included, and deliberately so.
        mds = [r for r in files if r.endswith(".md")]
        self.assertEqual(mds, ["level4/closure_proofs/"
                               "p5y_k1_cover_ledger_successor/ERROR_ALGEBRA.md"])

    def test_parent_hash_alone_is_insufficient_and_rejected(self):
        self.assertNotEqual(producer.producer_hash(), producer.parent_hash())
        ident = copy.deepcopy(CERTS221[RU2.unit_id(DF2)]["identity"])
        ident["implementation_hash"] = producer.parent_hash()
        with self.assertRaises(RU2.ProvenanceRejected):
            RU2.admit_resume_record(ident, DF2, dependency_certificates=CERTS221,
                                    **CTX)

    def test_stale_producer_hash_rejected(self):
        ident = copy.deepcopy(CERTS221[RU2.unit_id(DF2)]["identity"])
        ident["implementation_hash"] = "9" * 64
        ident["unit_hash"] = hashlib.sha256(certhash.canonical(
            {k: ident[k] for k in RU2.IDENTITY_FIELDS})).hexdigest()
        with self.assertRaises(RU2.ResumeRejected):
            RU2.admit_resume_record(ident, DF2, dependency_certificates=CERTS221,
                                    **CTX)

    def test_loaded_certifying_modules_are_all_covered(self):
        self.assertTrue(producer.verify_loaded_modules_covered()["ok"])

    def test_producer_hash_is_not_the_commit_hash(self):
        self.assertNotEqual(producer.producer_hash(), prior2.REPAIR1_COMMIT)
        self.assertNotEqual(producer.producer_hash(), prior2.REVIEWED_COMMIT)


# ================================================== certificate content hashes
class CertificateHashes(unittest.TestCase):
    def test_same_content_same_hash(self):
        again = provenance.build_cell_certificates(copy.deepcopy(REC221), **CTX)
        for uid, cert in CERTS221.items():
            self.assertEqual(certhash.certificate_hash(cert),
                             certhash.certificate_hash(again[uid]), uid)

    def test_runtime_noise_does_not_change_a_hash(self):
        def bump(rec):
            rec["cpu_seconds_including_dependencies"] = 99999.0
            rec["peak_rss_kib"] = 1
            for o in rec["objects"].values():
                o["cpu_seconds"] = 0.0
                o["bernstein_calls"] = 999
        noisy = rebuild(bump)
        for uid in CERTS221:
            self.assertEqual(certhash.certificate_hash(CERTS221[uid]),
                             certhash.certificate_hash(noisy[uid]), uid)

    def test_modified_certified_interval_changes_the_hash(self):
        changed = rebuild(lambda r: r["m"]["5"].__setitem__(
            "M_R2", "123456789/1"))
        self.assertNotEqual(
            certhash.certificate_hash(CERTS221["CUSUM|221|assembly|5"]),
            certhash.certificate_hash(changed["CUSUM|221|assembly|5"]))

    def test_modified_error_bound_changes_the_hash(self):
        changed = rebuild(lambda r: r["objects"]["F_2"].__setitem__(
            "envelope", "7/3"))
        self.assertNotEqual(certhash.certificate_hash(CERTS221[F2_ID]),
                            certhash.certificate_hash(changed[F2_ID]))

    def test_different_producer_changes_every_hash(self):
        other = RU2.context(producer_hash="f" * 64)
        certs = provenance.build_cell_certificates(REC221, **other)
        for uid in CERTS221:
            self.assertNotEqual(certhash.certificate_hash(CERTS221[uid]),
                                certhash.certificate_hash(certs[uid]), uid)

    def test_certificate_refuses_runtime_fields(self):
        bad = dict(CERTS221[F2_ID]); bad["cpu_seconds"] = 1.0
        with self.assertRaises(ValueError):
            certhash.certificate_hash(bad)


# ================================================ chain integrity & attacks
class SubstitutionAttacks(unittest.TestCase):
    """The ten attacks required by Phase 3. Every one must reject."""

    def _swap(self, uid: str, replacement: dict) -> dict:
        certs = dict(CERTS221)
        certs[uid] = replacement
        return certs

    def test_1_same_identity_modified_certified_interval(self):
        changed = rebuild(lambda r: r["objects"]["F_2"].__setitem__(
            "delta_mid", "1/2"))
        with self.assertRaises(RU2.ProvenanceRejected):
            provenance.verify_chain(DF2, self._swap(F2_ID, changed[F2_ID]), **CTX)

    def test_2_same_identity_modified_error_bound(self):
        changed = rebuild(lambda r: r["objects"]["F_2"].__setitem__(
            "delta_cell", "3/4"))
        with self.assertRaises(RU2.ProvenanceRejected):
            provenance.verify_chain(DF2, self._swap(F2_ID, changed[F2_ID]), **CTX)

    def test_3_same_identity_different_producer(self):
        other = provenance.build_cell_certificates(
            REC221, **RU2.context(producer_hash="a" * 64))
        with self.assertRaises(RU2.ProvenanceRejected):
            provenance.verify_chain(DF2, self._swap(F2_ID, other[F2_ID]), **CTX)

    def test_4_certificate_from_another_cell(self):
        foreign = CERTS293["CUSUM|293|object|F_2"]
        with self.assertRaises(RU2.ProvenanceRejected):
            provenance.verify_chain(DF2, self._swap(F2_ID, foreign), **CTX)

    def test_5_certificate_from_another_m(self):
        certs = dict(CERTS221)
        certs["CUSUM|221|curvature|5"] = CERTS221["CUSUM|221|curvature|3"]
        with self.assertRaises(RU2.ProvenanceRejected):
            provenance.verify_chain(ASM5, certs, **CTX)

    def test_6_certificate_from_another_shard(self):
        units = reviewed.work_ids()
        a = units[reviewed.shard_bounds(len(units), 0, 8)[0]]
        b = units[reviewed.shard_bounds(len(units), 5, 8)[0]]
        self.assertNotEqual(a, b)
        ctx = CTX
        ident_a = RU2.canonical_identity(a, source_certificate_hashes={}, **ctx)
        with self.assertRaises(RU2.ResumeRejected):
            RU2.admit_resume_record(ident_a, b, dependency_certificates={}, **ctx)

    def test_7_dependency_omitted(self):
        cert = copy.deepcopy(CERTS221[RU2.unit_id(DF2)])
        cert["identity"]["source_certificate_hashes"].pop(F2_ID)
        with self.assertRaises(RU2.ProvenanceRejected):
            provenance.verify_chain(DF2, self._swap(RU2.unit_id(DF2), cert), **CTX)

    def test_8_extra_dependency_inserted(self):
        cert = copy.deepcopy(CERTS221[RU2.unit_id(DF2)])
        cert["identity"]["source_certificate_hashes"]["CUSUM|221|object|h_4"] = \
            "0" * 64
        with self.assertRaises(RU2.ProvenanceRejected):
            provenance.verify_chain(DF2, self._swap(RU2.unit_id(DF2), cert), **CTX)

    def test_9_dependency_hashes_reordered_or_mispaired(self):
        cert = copy.deepcopy(CERTS221[RU2.unit_id(DF2)])
        m = cert["identity"]["source_certificate_hashes"]
        keys = sorted(m)
        # mispairing: same multiset of hashes, wrong owners
        m[keys[0]], m[keys[1]] = m[keys[1]], m[keys[0]]
        with self.assertRaises(RU2.ProvenanceRejected):
            provenance.verify_chain(DF2, self._swap(RU2.unit_id(DF2), cert), **CTX)

    def test_9b_benign_json_reordering_is_accepted(self):
        cert = copy.deepcopy(CERTS221[RU2.unit_id(DF2)])
        m = cert["identity"]["source_certificate_hashes"]
        cert["identity"]["source_certificate_hashes"] = {
            k: m[k] for k in reversed(list(m))}
        roundtrip = json.loads(json.dumps(cert))
        certs = self._swap(RU2.unit_id(DF2), roundtrip)
        provenance.verify_chain(DF2, certs, **CTX)

    def test_10_forged_metadata_without_matching_content(self):
        """Identity says the right thing; the certificate body does not."""
        cert = copy.deepcopy(CERTS221[F2_ID])
        cert["certified"]["residual"]["delta_mid"] = "1/2"
        # identity untouched, so a metadata-only check would pass
        self.assertEqual(cert["identity"],
                         CERTS221[F2_ID]["identity"])
        with self.assertRaises(RU2.ProvenanceRejected):
            provenance.verify_chain(DF2, self._swap(F2_ID, cert), **CTX)


class ChainIntegrity(unittest.TestCase):
    def test_full_cell_chain_verifies(self):
        v = provenance.verify_cell(REC221, certificates=CERTS221, **CTX)
        self.assertTrue(v["all_verified"])
        self.assertEqual(v["obligations"], 28)
        self.assertEqual(v["units_verified"], 28)
        self.assertTrue(v["leaf_maps_empty"])

    def test_leaf_units_have_exactly_empty_maps(self):
        for uid in provenance.verify_cell(
                REC221, certificates=CERTS221, **CTX)["leaf_units"]:
            self.assertEqual(
                CERTS221[uid]["identity"]["source_certificate_hashes"], {})

    def test_non_leaf_cannot_present_an_empty_map(self):
        cert = copy.deepcopy(CERTS221[RU2.unit_id(DF2)])
        cert["identity"]["source_certificate_hashes"] = {}
        certs = dict(CERTS221); certs[RU2.unit_id(DF2)] = cert
        with self.assertRaises(RU2.ProvenanceRejected):
            provenance.verify_chain(DF2, certs, **CTX)

    def test_leaf_cannot_declare_a_dependency(self):
        cert = copy.deepcopy(CERTS221[RU2.unit_id(LEAF)])
        cert["identity"]["source_certificate_hashes"] = {
            "CUSUM|221|object|S_0": "0" * 64}
        certs = dict(CERTS221); certs[RU2.unit_id(LEAF)] = cert
        with self.assertRaises(RU2.ProvenanceRejected):
            provenance.verify_chain(LEAF, certs, **CTX)

    def test_build_order_respects_the_frozen_graph(self):
        order = provenance.cell_units("CUSUM", 221)
        self.assertTrue(provenance._topologically_sound(order))
        self.assertEqual(len(order), 28)

    def test_assembly_chain_reaches_the_leaves(self):
        seen: set = set()
        provenance.verify_chain(ASM5, CERTS221, _seen=seen, **CTX)
        self.assertIn(RU2.unit_id(LEAF), seen)
        self.assertIn("CUSUM|221|curvature|5", seen)
        self.assertIn("CUSUM|221|dependency_bundle|orders_0_1", seen)


# ==================================================== record / resume identity
class ResumeIdentity(unittest.TestCase):
    def test_valid_repair2_record_admitted(self):
        ident = CERTS221[RU2.unit_id(DF2)]["identity"]
        self.assertTrue(RU2.admit_resume_record(
            ident, DF2, dependency_certificates=CERTS221, **CTX))

    def test_repair1_record_is_not_admissible_as_repair2(self):
        r1 = json.loads((prior2.REPAIR1_NS /
                         "diagnostics/regression/repaired_221_256_full.json"
                         ).read_text())
        for ident in r1["identity"].values():
            unit = (ident["detector"], ident["cell_index"],
                    ident["unit_kind"], ident["function_or_m"])
            with self.assertRaises(RU2.ProvenanceRejected):
                RU2.admit_resume_record(ident, unit,
                                        dependency_certificates=CERTS221, **CTX)

    def test_missing_identity_kind_rejected(self):
        ident = copy.deepcopy(CERTS221[RU2.unit_id(DF2)]["identity"])
        ident.pop("implementation_hash_kind")
        with self.assertRaises(RU2.ProvenanceRejected):
            RU2.admit_resume_record(ident, DF2,
                                    dependency_certificates=CERTS221, **CTX)

    def test_old_12255_universe_still_rejected(self):
        ident = copy.deepcopy(CERTS221[RU2.unit_id(DF2)]["identity"])
        ident["obligation_universe_total"] = 12255
        with self.assertRaises(RU2.ResumeRejected):
            RU2.admit_resume_record(ident, DF2,
                                    dependency_certificates=CERTS221, **CTX)

    def test_superseded_checkpoints_still_rejected(self):
        for h in RU1.SUPERSEDED_CHECKPOINT_HASHES:
            ident = copy.deepcopy(CERTS221[RU2.unit_id(DF2)]["identity"])
            ident["checkpoint_hash"] = h
            with self.assertRaises(RU2.ResumeRejected):
                RU2.admit_resume_record(ident, DF2,
                                        dependency_certificates=CERTS221, **CTX)

    def test_every_single_identity_field_mutation_rejected(self):
        base = CERTS221[RU2.unit_id(DF2)]["identity"]
        bad = {"detector": "SR", "cell_index": 137, "unit_kind": "curvature",
               "function_or_m": "F_2", "e0": ["1/3", "0/1"],
               "rho": ["1/7", "0/1"], "left": ["9/8", "0/1"],
               "right": ["9/8", "0/1"], "C_upper": "1/1",
               "precision_bits": 384, "checkpoint_hash": "1" * 64,
               "cells_sha256": "2" * 64, "error_algebra_sha256": "3" * 64,
               "backend_hash": "4" * 64, "implementation_hash": "5" * 64,
               "implementation_hash_kind": "other",
               "obligation_universe_total": 17977,
               "source_certificate_hashes": {}}
        for field, value in bad.items():
            ident = copy.deepcopy(base); ident[field] = value
            with self.assertRaises(RU2.ResumeRejected, msg=field):
                RU2.admit_resume_record(ident, DF2,
                                        dependency_certificates=CERTS221, **CTX)

    def test_forged_self_consistent_unit_hash_rejected(self):
        ident = copy.deepcopy(CERTS221[RU2.unit_id(DF2)]["identity"])
        ident["detector"] = "SR"
        ident["unit_hash"] = hashlib.sha256(certhash.canonical(
            {k: ident[k] for k in RU2.IDENTITY_FIELDS})).hexdigest()
        with self.assertRaises(RU2.ResumeRejected):
            RU2.admit_resume_record(ident, DF2,
                                    dependency_certificates=CERTS221, **CTX)

    def test_floats_in_exact_fields_rejected(self):
        for field in RU2.EXACT_FIELDS:
            ident = copy.deepcopy(CERTS221[RU2.unit_id(DF2)]["identity"])
            ident[field] = 0.25
            with self.assertRaises(RU2.InexactField, msg=field):
                RU2.admit_resume_record(ident, DF2,
                                        dependency_certificates=CERTS221, **CTX)

    def test_benign_json_normalisation_survives(self):
        ident = CERTS221[RU2.unit_id(DF2)]["identity"]
        shuffled = json.loads(json.dumps(
            {k: ident[k] for k in reversed(list(ident))}))
        self.assertTrue(RU2.admit_resume_record(
            shuffled, DF2, dependency_certificates=CERTS221, **CTX))

    def test_absent_dependency_certificate_rejects(self):
        certs = {k: v for k, v in CERTS221.items() if k != F2_ID}
        with self.assertRaises(RU2.ProvenanceRejected):
            RU2.admit_resume_record(CERTS221[RU2.unit_id(DF2)]["identity"],
                                    DF2, dependency_certificates=certs, **CTX)


class FrozenInvariants(unittest.TestCase):
    def test_universe_and_shards_unchanged(self):
        ids = reviewed.work_ids()
        self.assertEqual(len(ids), 17978)
        for w in (1, 8, 16, 32, 64):
            r = reviewed.verify_shard_conservation(w, ids)
            self.assertTrue(r["union_equals_universe"])
            self.assertTrue(r["no_overlap"])

    def test_frozen_numbers_unchanged(self):
        self.assertEqual(spec.HARD_CAP_CPU_H, 1126)
        self.assertEqual(spec.PRODUCTION_BITS, 256)
        self.assertFalse(spec.PRODUCTION_ENABLED)
        self.assertFalse(spec.PRECISION_ESCALATION_ALLOWED)
        self.assertEqual(spec.verify_frozen_spec(), spec.FROZEN_HASHES)


if __name__ == "__main__":
    unittest.main(verbosity=2)
