"""Focused tests for repair1: single S0 charge and exact resume identity.

Every negative control here would have FAILED at c0a1f40.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import prior                                                    # noqa: E402
from flint import arb                                           # noqa: E402

import algebra as FROZEN                                        # noqa: E402
import depgraph                                                 # noqa: E402
import opnorms                                                  # noqa: E402
import spec                                                     # noqa: E402
import universe as reviewed_universe                            # noqa: E402
from intervals import exact, mag_fraction, tight_upper, workprec  # noqa: E402

import repair_check                                             # noqa: E402
import repair_layer2                                            # noqa: E402
import repair_universe as RU                                    # noqa: E402

UNIT = ("CUSUM", 0, "object", "h_1")
CTX = RU.context(backend_hash="B")


# ===========================================================================
# PHASE 1 - the S0 remainder is charged exactly once
# ===========================================================================
class SingleS0Charge(unittest.TestCase):
    REWARD = F(1, 1024)
    CORRECTED = F(1, 2 ** 30)

    def _positions(self, *, local: bool, dependency: bool):
        return repair_check.charge_positions(
            truncation_allowance=self.CORRECTED + (self.REWARD if local else 0),
            corrected=self.CORRECTED,
            dependency=self.REWARD if dependency else F(0),
            reward=self.REWARD)

    def test_repaired_representation_charges_once(self):
        r = self._positions(local=False, dependency=True)
        self.assertEqual(r["charge_count"], 1)
        self.assertFalse(r["in_local_residual"])
        self.assertTrue(r["in_dependency_graph"])

    def test_charged_twice_is_detected(self):
        """The exact c0a1f40 defect."""
        r = self._positions(local=True, dependency=True)
        self.assertEqual(r["charge_count"], 2)

    def test_charged_zero_times_is_detected(self):
        """Removing the remainder from both places is equally wrong."""
        r = self._positions(local=False, dependency=False)
        self.assertEqual(r["charge_count"], 0)

    def test_representation_b_alone_is_also_single(self):
        """Complete residual against the true source with epsS = 0."""
        r = self._positions(local=True, dependency=False)
        self.assertEqual(r["charge_count"], 1)

    def test_require_single_charge_raises_on_double_and_zero(self):
        class Stub:
            reward_allow = {}
            sup = {}

            def eps_zi(self, i):
                return arb(0)
        with workprec(spec.PRODUCTION_BITS):
            stub = Stub()
            stub.reward_allow = {k: exact(self.REWARD) for k in range(3)}
            stub.sup = {("F", 0, 0): arb(0), ("D", 0, 0): arb(0),
                        ("H", 0, 0): arb(0)}
            for local, expect_ok in ((True, False), (False, True)):
                residuals = {}
                for name, k in zip(repair_layer2.DUPLICATE_SITES, (0, 1, 2)):
                    residuals[name] = {"truncation_allowance": tight_upper(
                        exact(self.REWARD) if local else arb(0))}
                    residuals[f"Sclosed_{k}"] = {
                        "delta_mid": tight_upper(exact(self.REWARD))}
                if expect_ok:
                    repair_check.require_single_charge(stub, residuals)
                else:
                    with self.assertRaises(repair_check.ChargeAccountingError):
                        repair_check.require_single_charge(stub, residuals)

    def test_frozen_error_formulas_are_unchanged(self):
        """epsF and epsD keep their exact frozen shape after the repair."""
        ef, ed = depgraph.reference_resolvent_errors(
            3, F(1, 100), F(2, 100), F(4, 5), F(1, 1000), F(1, 50))
        self.assertEqual((ef, ed), (F(9, 100), F(279, 1000)))
        self.assertEqual((ef, ed), FROZEN.resolvent_errors(
            3, F(1, 100), F(2, 100), F(4, 5), F(1, 1000), F(1, 50)))

    def test_repair_touches_only_the_three_r0_sites(self):
        self.assertEqual(repair_layer2.DUPLICATE_SITES, ("F_0", "dF_0", "H_0"))
        self.assertTrue(issubclass(repair_layer2.RepairedCellCertifier,
                                   __import__("cusum_layer2").CellCertifier))

    def test_style_1_and_single_taylor_charge_untouched(self):
        import ledger
        with workprec(spec.PRODUCTION_BITS):
            with self.assertRaises(ledger.SeparateDerivativeCharge):
                ledger.cover_charge(arb(1), F(1, 10), arb(1),
                                    separate_derivative_charge=F(1, 5))
            got = ledger.cover_charge(exact(1) + arb(0, 4), F(1, 10), exact(4))
            self.assertEqual(got["style"], "STYLE_1_COMPLETE_D_INTERVAL")


# ===========================================================================
# PHASE 2 - exact resume identity
# ===========================================================================
SINGLE_FIELD_MUTATIONS = {
    "detector": ("detector", "SR"),
    "cell": ("cell_index", 137),
    "unit_kind": ("unit_kind", "curvature"),
    "function": ("function_or_m", "dF_4"),
    "e0": ("e0", ["1/3", "0/1"]),
    "rho": ("rho", ["1/7", "0/1"]),
    "unit_hash": ("unit_hash", "0" * 64),
    "checkpoint_hash": ("checkpoint_hash", "1" * 64),
    "implementation_hash": ("implementation_hash", "2" * 64),
    "precision": ("precision_bits", 384),
    "cells_sha256": ("cells_sha256", "3" * 64),
    "error_algebra_sha256": ("error_algebra_sha256", "4" * 64),
    "backend_hash": ("backend_hash", "OTHER"),
    "left": ("left", ["9/8", "0/1"]),
    "right": ("right", ["9/8", "0/1"]),
    "C_upper": ("C_upper", "1/1"),
    "obligation_universe_total": ("obligation_universe_total", 17977),
}


class ExactResumeIdentity(unittest.TestCase):
    def test_valid_exact_record_is_admitted(self):
        good = RU.canonical_identity(UNIT, **CTX)
        self.assertTrue(RU.admit_resume_record(good, UNIT, **CTX))

    def test_every_single_field_mutation_is_rejected(self):
        good = RU.canonical_identity(UNIT, **CTX)
        for name, (field, bad) in SINGLE_FIELD_MUTATIONS.items():
            rec = copy.deepcopy(good)
            rec[field] = bad
            with self.assertRaises(RU.ResumeRejected, msg=f"accepted {name}"):
                RU.admit_resume_record(rec, UNIT, **CTX)

    def test_m_mutation_rejected_for_an_assembly_obligation(self):
        unit = ("CUSUM", 0, "assembly", "5")
        good = RU.canonical_identity(unit, **CTX)
        self.assertTrue(RU.admit_resume_record(good, unit, **CTX))
        for other_m in ("1", "2", "3"):
            rec = copy.deepcopy(good)
            rec["function_or_m"] = other_m
            with self.assertRaises(RU.ResumeRejected):
                RU.admit_resume_record(rec, unit, **CTX)
            # ... and it must not be admissible AS that other obligation either
            with self.assertRaises(RU.ResumeRejected):
                RU.admit_resume_record(good, ("CUSUM", 0, "assembly", other_m),
                                       **CTX)

    def test_dependency_and_source_certificate_hash_mutations_rejected(self):
        unit = ("CUSUM", 3, "object", "dF_2")
        good = RU.canonical_identity(unit, **CTX)
        self.assertTrue(RU.admit_resume_record(good, unit, **CTX))
        self.assertTrue(good["source_certificate_hashes"])

        # drop one dependency
        rec = copy.deepcopy(good)
        rec["source_certificate_hashes"].pop(
            sorted(rec["source_certificate_hashes"])[0])
        with self.assertRaises(RU.ResumeRejected):
            RU.admit_resume_record(rec, unit, **CTX)

        # corrupt one dependency hash
        rec = copy.deepcopy(good)
        key = sorted(rec["source_certificate_hashes"])[0]
        rec["source_certificate_hashes"][key] = "0" * 64
        with self.assertRaises(RU.ResumeRejected):
            RU.admit_resume_record(rec, unit, **CTX)

        # add a dependency that the frozen graph does not require
        rec = copy.deepcopy(good)
        rec["source_certificate_hashes"]["CUSUM|3|object|h_4"] = "5" * 64
        with self.assertRaises(RU.ResumeRejected):
            RU.admit_resume_record(rec, unit, **CTX)

    def test_missing_identity_field_is_rejected(self):
        for field in RU.IDENTITY_FIELDS:
            rec = copy.deepcopy(RU.canonical_identity(UNIT, **CTX))
            rec.pop(field)
            with self.assertRaises(RU.ResumeRejected, msg=field):
                RU.admit_resume_record(rec, UNIT, **CTX)

    def test_forged_unit_hash_cannot_survive(self):
        """A mutated body with a self-consistently recomputed hash still fails."""
        rec = copy.deepcopy(RU.canonical_identity(UNIT, **CTX))
        rec["detector"] = "SR"
        body = {k: rec[k] for k in RU.IDENTITY_FIELDS}
        rec["unit_hash"] = hashlib.sha256(RU.canonical(body)).hexdigest()
        with self.assertRaises(RU.ResumeRejected):
            RU.admit_resume_record(rec, UNIT, **CTX)

    def test_floats_in_exact_fields_are_rejected(self):
        for field in RU.EXACT_FIELDS:
            rec = copy.deepcopy(RU.canonical_identity(UNIT, **CTX))
            rec[field] = 0.25
            with self.assertRaises(RU.InexactField, msg=field):
                RU.admit_resume_record(rec, UNIT, **CTX)

    def test_reordered_json_does_not_change_identity(self):
        good = RU.canonical_identity(UNIT, **CTX)
        shuffled = json.loads(json.dumps(
            {k: good[k] for k in reversed(list(good))}))
        self.assertTrue(RU.admit_resume_record(shuffled, UNIT, **CTX))
        self.assertEqual(RU.canonical(shuffled), RU.canonical(good))

    def test_old_12255_universe_still_rejected(self):
        rec = copy.deepcopy(RU.canonical_identity(UNIT, **CTX))
        rec["obligation_universe_total"] = 12255
        with self.assertRaises(RU.ResumeRejected):
            RU.admit_resume_record(rec, UNIT, **CTX)

    def test_superseded_parent_checkpoints_still_rejected(self):
        for h in reviewed_universe.SUPERSEDED_CHECKPOINT_HASHES:
            rec = copy.deepcopy(RU.canonical_identity(UNIT, **CTX))
            rec["checkpoint_hash"] = h
            with self.assertRaises(RU.ResumeRejected):
                RU.admit_resume_record(rec, UNIT, **CTX)

    def test_cross_shard_identity_substitution_is_impossible(self):
        """A record from one shard must not be admissible as a unit in another."""
        units = reviewed_universe.work_ids()
        a = units[reviewed_universe.shard_bounds(len(units), 0, 8)[0]]
        b = units[reviewed_universe.shard_bounds(len(units), 5, 8)[0]]
        self.assertNotEqual(a, b)
        rec_a = RU.canonical_identity(a, **CTX)
        self.assertTrue(RU.admit_resume_record(rec_a, a, **CTX))
        with self.assertRaises(RU.ResumeRejected):
            RU.admit_resume_record(rec_a, b, **CTX)

    def test_no_two_obligations_share_an_identity(self):
        """Sampled uniqueness across kinds, detectors and cells."""
        units = reviewed_universe.work_ids()
        sample = units[::577] + units[-2:]
        seen = {}
        for u in sample:
            h = RU.canonical_identity(u, **CTX)["unit_hash"]
            self.assertNotIn(h, seen, f"{u} collides with {seen.get(h)}")
            seen[h] = u
        self.assertGreater(len(seen), 25)

    def test_reviewed_admission_was_weaker(self):
        """Documents the defect: the reviewed function accepts these."""
        rec = reviewed_universe.unit_identity(
            UNIT, backend_hash="B",
            impl_hash=reviewed_universe.implementation_hash())
        rec["detector"] = "SR"
        rec["cell_index"] = 999
        self.assertTrue(reviewed_universe.admit_resume_record(
            rec, backend_hash="B"))


class FrozenDependencyRules(unittest.TestCase):
    def test_dependencies_of_matches_the_frozen_graph(self):
        cells = [c for c in spec.CELLS if c["index"] < 2]
        graph = FROZEN.unit_dependencies(cells)
        for unit, deps in graph.items():
            self.assertEqual(set(RU.dependencies_of(unit)), set(deps), unit)

    def test_far_field_has_no_dependencies(self):
        self.assertEqual(RU.dependencies_of(("CUSUM", -1, "far_field", "all_m")),
                         [])

    def test_curvature_m5_owns_the_shared_jets(self):
        owner = ("CUSUM", 0, "curvature", "5")
        deps = RU.dependencies_of(owner)
        self.assertEqual(len(deps), 20)          # 19 objects + the bundle
        for m in ("1", "2", "3"):
            self.assertEqual(RU.dependencies_of(("CUSUM", 0, "curvature", m)),
                             [owner])


class UniverseUnchanged(unittest.TestCase):
    def test_17978_enumeration_and_shards_unchanged(self):
        ids = reviewed_universe.work_ids()
        self.assertEqual(len(ids), 17978)
        self.assertEqual(ids, FROZEN.work_ids(spec.CELLS))
        for w in (1, 8, 16, 32, 64):
            r = reviewed_universe.verify_shard_conservation(w, ids)
            self.assertTrue(r["union_equals_universe"])
            self.assertTrue(r["no_overlap"])
            self.assertTrue(r["no_dropped_work"])

    def test_frozen_invariants_untouched(self):
        self.assertEqual(spec.HARD_CAP_CPU_H, 1126)
        self.assertEqual(spec.PRODUCTION_BITS, 256)
        self.assertFalse(spec.PRODUCTION_ENABLED)
        self.assertFalse(spec.PRECISION_ESCALATION_ALLOWED)
        self.assertFalse(spec.DEGREE_ADAPTATION_ALLOWED)
        self.assertEqual(sum(spec.TOP_BUDGETS.values()), F(19, 100))
        self.assertEqual(spec.verify_frozen_spec(), spec.FROZEN_HASHES)


if __name__ == "__main__":
    unittest.main(verbosity=2)
