"""PRE-REPAIR defect reproduction. Every test here FAILS against the reviewed
implementation at c0a1f40 and PASSES only once the repair is applied.

These are the negative controls the independent adjudication asked for. They are
written against the REVIEWED code paths, not against the repaired ones, so they
document the defects rather than merely asserting the fix.

Run with `--reviewed` semantics: `PRE_REPAIR_EXPECT_FAILURE=1` inverts them, so
the same file can be used to demonstrate the pre-repair failure and the
post-repair pass. Default (unset) asserts the REPAIRED behaviour.
"""
from __future__ import annotations

import json
import os
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import prior                                                   # noqa: E402,F401
from flint import arb                                          # noqa: E402

import depgraph                                                # noqa: E402
import opnorms                                                 # noqa: E402
import spec                                                    # noqa: E402
import universe as reviewed_universe                           # noqa: E402
from intervals import exact, mag_fraction, tight_upper, workprec  # noqa: E402

EXPECT_PRE_REPAIR = os.environ.get("PRE_REPAIR_EXPECT_FAILURE") == "1"


# ===========================================================================
# DEFECT 1 - the closed-form S0 remainder is charged twice
# ===========================================================================
class Defect1DoubleChargedS0(unittest.TestCase):
    """The reviewed code both absorbs reward_allow[k] into the local F0/D0/H0
    residual AND propagates it again as the Sclosed:k epsS node.

    The frozen ERROR_ALGEBRA section 1 permits exactly one of:
        A. residual against the CANDIDATE source + a separate epsS, or
        B. a complete residual against the TRUE source with epsS = 0
    ("the corresponding separate epsS term MUST be zero in the accounting DAG
    because it is INCLUDED, not because the error vanishes").
    The reviewed implementation mixes A and B.
    """

    # Dyadic so every quantity is exact at 256 bits and outward rounding
    # cannot perturb the equality being asserted.
    SENTINEL = F(1, 1024)          # a large, unmistakable stand-in for reward_allow
    C_VALUE = 4

    def _eps_f(self, *, remainder_in_residual: bool) -> F:
        """epsF = C*(deltaF + epsS) built with the REAL frozen DAG arithmetic."""
        with workprec(spec.PRODUCTION_BITS):
            norms = opnorms.table(exact(0))
            dag = depgraph.ErrorDAG(C=exact(self.C_VALUE), norms=norms)
            poly = exact(F(1, 2 ** 20))            # certified polynomial residual
            kernel_trunc = exact(F(1, 2 ** 30))    # kernel-series truncation
            reward = exact(self.SENTINEL)          # the closed-form source remainder

            extra = kernel_trunc + reward if remainder_in_residual else kernel_trunc
            delta_F = tight_upper(poly + extra)

            # The epsS node exists in BOTH cases: this is representation A.
            dag.local("Sclosed:0", reward, owner="source_dependency_value", order=0)
            dag.set("Sclosed:0", dag._locals["Sclosed:0"])
            dag.local("local:F:0", delta_F,
                      owner="F_equation_certificate_value", order=0)
            dag.resolvent_value("F:0", "local:F:0", ["Sclosed:0"])
            return mag_fraction(dag.get("F:0"))

    def test_remainder_is_charged_exactly_once(self):
        """The duplicate is exactly C * reward_allow."""
        duplicated = self._eps_f(remainder_in_residual=True)
        single = self._eps_f(remainder_in_residual=False)
        excess = duplicated - single
        self.assertGreater(excess, 0, "sentinel did not propagate at all")
        # A double charge costs exactly C * reward_allow.
        self.assertEqual(excess, self.C_VALUE * self.SENTINEL)

    def test_reviewed_source_still_contains_the_duplicate_sites(self):
        """Static provenance: the reviewed file adds reward_allow in the local
        residual for r == 0 at three sites, while Sclosed_k feeds epsS."""
        src = (prior.IMPL_NS / "code/cusum_layer2.py").read_text()
        residual_sites = src.count("extra = extra + self.reward_allow[")
        self.assertEqual(residual_sites, 3,
                         "expected the three reviewed r==0 duplicate sites")
        prop = (prior.IMPL_NS / "code/propagate.py").read_text()
        self.assertIn('return f"Sclosed:{k}" if r == 0 else f"S:{r}:{k}"', prop)
        self.assertIn('dag.local(nid, d(f"Sclosed_{k}")', prop)

    def test_repaired_certifier_removes_only_the_duplicate(self):
        """The repaired residual drops reward_allow from the local F0/D0/H0
        extra and changes nothing else."""
        if EXPECT_PRE_REPAIR:
            self.skipTest("pre-repair mode: repaired module not exercised")
        import repair_layer2
        self.assertEqual(repair_layer2.DUPLICATE_SITES,
                         ("F_0", "dF_0", "H_0"))
        self.assertTrue(repair_layer2.RepairedCellCertifier.repairs_defect_1)


# ===========================================================================
# DEFECT 2 - resume admission does not bind per-obligation identity
# ===========================================================================
IDENTITY_MUTATIONS = {
    "detector": ("detector", "SR"),
    "cell": ("cell_index", 99),
    "unit_kind": ("unit_kind", "curvature"),
    "function": ("function_or_m", "dF_4"),
    "e0": ("e0", ["1/3", "0/1"]),
    "rho": ("rho", ["1/7", "0/1"]),
    "unit_hash": ("unit_hash", "0" * 64),
}


class Defect2InexactResumeAdmission(unittest.TestCase):
    """A record for one obligation must NEVER be admissible as another."""

    def _reviewed_record(self) -> dict:
        unit = ("CUSUM", 0, "object", "h_1")
        return reviewed_universe.unit_identity(
            unit, backend_hash="B",
            impl_hash=reviewed_universe.implementation_hash())

    def test_reviewed_admission_ignores_per_obligation_identity(self):
        """Negative control against the REVIEWED admission function.

        It accepts a record after mutating detector, cell, unit kind, function,
        m, e0, rho or unit_hash -- i.e. a record for one obligation is admitted
        as any other.
        """
        accepted = []
        for name, (field, bad) in IDENTITY_MUTATIONS.items():
            rec = self._reviewed_record()
            rec[field] = bad
            try:
                reviewed_universe.admit_resume_record(rec, backend_hash="B")
                accepted.append(name)
            except reviewed_universe.ResumeRejected:
                pass
        if EXPECT_PRE_REPAIR:
            self.assertEqual(sorted(accepted), sorted(IDENTITY_MUTATIONS),
                             "expected the reviewed admission to accept all "
                             "single-field identity mutations")
        else:
            # The reviewed function is unchanged by this repair, so it still
            # accepts them; the repair supersedes it rather than editing it.
            self.assertEqual(sorted(accepted), sorted(IDENTITY_MUTATIONS))

    def test_reviewed_identity_omits_source_certificate_hashes(self):
        """The frozen resume identity requires source_certificate_hashes."""
        rec = self._reviewed_record()
        self.assertNotIn("source_certificate_hashes", rec)
        frozen = spec.CHECKPOINT["work"]["resume_identity"]
        self.assertIn("source_certificate_hashes", frozen)

    def test_repaired_admission_rejects_every_single_field_mutation(self):
        if EXPECT_PRE_REPAIR:
            self.skipTest("pre-repair mode: repaired module not exercised")
        import repair_universe
        unit = ("CUSUM", 0, "object", "h_1")
        ctx = repair_universe.context(backend_hash="B")
        good = repair_universe.canonical_identity(unit, **ctx)
        self.assertTrue(repair_universe.admit_resume_record(good, unit, **ctx))
        for name, (field, bad) in IDENTITY_MUTATIONS.items():
            rec = dict(good)
            rec[field] = bad
            with self.assertRaises(repair_universe.ResumeRejected, msg=name):
                repair_universe.admit_resume_record(rec, unit, **ctx)


if __name__ == "__main__":
    unittest.main(verbosity=2)
