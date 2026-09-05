"""Focused tests for the final-completion campaign.

The load-bearing new object is the drift-aware operator-norm family. Its
correctness is what flipped cell 325, so it is tested against closed forms,
against independent numerical integration, and for the one-sided property that
makes it admissible (it may only tighten).
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import base                                                     # noqa: E402

from flint import arb                                           # noqa: E402

import opnorms as reviewed_norms                                # noqa: E402
import spec                                                     # noqa: E402
import universe as reviewed                                     # noqa: E402
from intervals import exact, mag_fraction, workprec             # noqa: E402

import far_field                                                # noqa: E402
import final_audit                                              # noqa: E402
import sharp_norms as SN                                        # noqa: E402
import sr_cost                                                  # noqa: E402
import sr_status                                                # noqa: E402

CELLS = [c for c in spec.CELLS if c["detector"] == "CUSUM"]
RECORDS = sorted((NS / "diagnostics/cells").glob("sharp_*.json"))


def load(paths):
    return [json.loads(p.read_text()) for p in paths]


def _he(n, y):
    a, b = 1.0, y
    if n == 0:
        return 1.0
    for k in range(1, n):
        a, b = b, y * b - k * a
    return b


def _simpson(n, lo, hi, N=200001):
    h = (hi - lo) / (N - 1)
    tot = 0.0
    for i in range(N):
        y = lo + i * h
        w = 1 if i in (0, N - 1) else (4 if i % 2 else 2)
        tot += w * abs(_he(n, y)) * math.exp(-0.5 * y * y) / math.sqrt(2 * math.pi)
    return tot * h / 3


class HermiteMoments(unittest.TestCase):
    def test_whole_line_reproduces_frozen_named_constants(self):
        with workprec(256):
            lo, hi = exact(F(-40)), exact(F(40))
            for n in range(4):
                a = float(SN.absolute_hermite_moment(n, lo, hi).abs_upper())
                b = float(reviewed_norms.kernel_norm(n).abs_upper())
                self.assertAlmostEqual(a, b, places=11, msg=f"He_{n}")

    def test_matches_independent_numerical_integration(self):
        with workprec(256):
            for lo, hi in ((-6.0, 6.0), (-0.1, 10.9), (-5.5, 5.5)):
                l, h = exact(F(lo).limit_denominator(10 ** 6)), \
                    exact(F(hi).limit_denominator(10 ** 6))
                for n in range(5):
                    a = float(SN.absolute_hermite_moment(n, l, h).abs_upper())
                    b = _simpson(n, lo, hi)
                    self.assertLess(abs(a - b) / max(b, 1e-30), 1e-5,
                                    f"He_{n} on [{lo},{hi}]")

    def test_antiderivative_identity(self):
        """int He_n phi = -He_(n-1) phi, checked by differencing."""
        with workprec(256):
            for n in range(1, 5):
                for y0 in (-1.5, 0.3, 2.0):
                    y = exact(F(y0).limit_denominator(10 ** 6))
                    eps = exact(F(1, 10 ** 6))
                    d = (SN._antiderivative(n, y + eps)
                         - SN._antiderivative(n, y - eps)) / (arb(2) * eps)
                    want = SN.hermite_he(n, y) * SN.phi(y)
                    self.assertLess(abs(float(d.mid()) - float(want.mid())),
                                    1e-6, f"He_{n} at {y0}")

    def test_moment_is_nonnegative_and_monotone_in_the_window(self):
        with workprec(256):
            for n in range(5):
                a = SN.absolute_hermite_moment(n, exact(F(-1)), exact(F(1)))
                b = SN.absolute_hermite_moment(n, exact(F(-3)), exact(F(3)))
                self.assertTrue(a >= 0)
                self.assertLessEqual(float(a.abs_upper()), float(b.abs_upper()))


class DriftAwareNormsOnlyTighten(unittest.TestCase):
    """The admissibility property: a sharper bound, never a looser one."""

    def test_every_cusum_cell_tightens_or_equals(self):
        with workprec(256):
            for c in CELLS[::17] + CELLS[-3:]:
                left, right = F(c["left"][0]), F(c["right"][0])
                e_max = exact(max(abs(left), abs(right)))
                for i in range(4):
                    self.assertLessEqual(
                        SN.kernel_norm(i, left, right).upper(),
                        reviewed_norms.kernel_norm(i).upper(), (c["index"], "k", i))
                    self.assertLessEqual(
                        SN.raw_kernel_norm(i, left, right).upper(),
                        reviewed_norms.raw_kernel_norm(i, e_max).upper(),
                        (c["index"], "j", i))

    def test_large_drift_gives_the_large_improvement(self):
        c = CELLS[325]
        r = SN.improvement_report(F(c["left"][0]), F(c["right"][0]))
        self.assertGreater(r["j_0"]["factor"], 20.0)
        self.assertGreater(r["j_1"]["factor"], 15.0)
        self.assertGreater(r["j_2"]["factor"], 10.0)

    def test_small_drift_is_essentially_the_whole_line_bound(self):
        c = CELLS[0]
        r = SN.improvement_report(F(c["left"][0]), F(c["right"][0]))
        for i in range(4):
            self.assertLess(r[f"k_{i}"]["factor"], 1.05)

    def test_window_contains_every_state_and_drift_of_the_cell(self):
        """W = [left - 11/2, right + 11/2] must cover y = z + e for all x, e."""
        with workprec(256):
            for c in (CELLS[0], CELLS[200], CELLS[325]):
                left, right = F(c["left"][0]), F(c["right"][0])
                lo, hi = SN._window(left, right)
                # widest z-window is [-11/2, 11/2] at x = (0,0)
                self.assertLessEqual(float(lo.mid()), float(left) - 5.5 + 1e-12)
                self.assertGreaterEqual(float(hi.mid()), float(right) + 5.5 - 1e-12)


class FarField(unittest.TestCase):
    def setUp(self):
        self.r = far_field.report()

    def test_passes_at_p5x_e_far_12_for_every_m_both_detectors(self):
        for det, d in self.r["detectors"].items():
            self.assertTrue(d["at_p5x_e_far_12"]["all_m_pass"], det)

    def test_does_not_close_m5_at_the_frozen_k1_splice(self):
        for det, d in self.r["detectors"].items():
            self.assertFalse(d["at_frozen_k1_splice"]["all_m_pass"], det)
            self.assertEqual(d["failure_class"], "CERTIFICATE_TOO_LOOSE")

    def test_failure_is_not_called_a_counterexample(self):
        blob = json.dumps(self.r)
        self.assertNotIn("SCIENTIFIC_FAILURE", blob)
        self.assertNotIn("COUNTEREXAMPLE", blob.upper())

    def test_majorant_is_monotone_decreasing(self):
        with workprec(256):
            for det in ("CUSUM", "SR"):
                prev = None
                for e in (F(6), F(7), F(8), F(10), F(12)):
                    b = far_field.majorant(det, 5, exact(e))
                    if prev is not None:
                        self.assertLess(float(b.abs_upper()), prev)
                    prev = float(b.abs_upper())

    def test_uncovered_interval_is_reported(self):
        for det, d in self.r["detectors"].items():
            lo, hi = d["uncovered_interval_if_cover_ends_at_c"]
            self.assertGreater(hi, lo)
            self.assertLess(hi, 12.0)


class SRStatus(unittest.TestCase):
    def test_sr_reported_absent_with_evidence(self):
        r = sr_status.report()
        self.assertEqual(r["SR_IMPLEMENTATION"], "ABSENT")
        self.assertEqual(r["failure_class"], "IMPLEMENTATION_INCOMPLETE")
        self.assertEqual(r["task1r_evidence"]["objects_certified"], ["F_0"])
        self.assertEqual(r["coverage"]["drifts_implemented"], 1)
        self.assertEqual(r["coverage"]["sr_obligations_total"], 8849)

    def test_sr_absence_is_not_called_a_scientific_failure(self):
        r = sr_status.report()
        self.assertTrue(r["not_a_scientific_failure"])


class Cost(unittest.TestCase):
    def setUp(self):
        self.m = sr_cost.model()

    def test_reproduces_the_frozen_base_only_sr_model(self):
        self.assertTrue(self.m["model_check"]["reproduces_frozen_model"])

    def test_cap_unchanged_and_not_claimed_pass(self):
        self.assertEqual(self.m["frozen_hard_cap_cpu_h"], 1126)
        self.assertFalse(self.m["cap_increased"])
        self.assertEqual(self.m["COST_CAP_STATUS"], "NOT_ESTABLISHED")

    def test_assumption_free_lower_bound_does_not_establish_fail(self):
        lb = self.m["lower_bounds"]
        self.assertFalse(lb["assumption_free_exceeds_cap"])
        self.assertTrue(lb["assumption_dependent_exceeds_cap"])
        self.assertIn("NOT proved", lb["the_assumption"])

    def test_extrapolation_is_labelled_as_such(self):
        self.assertIn("EXTRAPOLATION", self.m["extrapolation"]["label"])


class RecertifiedCells(unittest.TestCase):
    def test_records_exist(self):
        self.assertGreaterEqual(len(RECORDS), 4)

    def test_low_and_mid_radius_cells_pass_every_m(self):
        """Everything below the high-radius block certifies cleanly."""
        for r in load(RECORDS):
            if r["cell_index"] in range(318, 325):
                continue
            for m, L in r["m"].items():
                self.assertEqual(L["status"], "PASS", (r["cell_index"], m))

    def test_every_failure_is_certificate_looseness_not_a_counterexample(self):
        """A FAIL whose R2 enclosure straddles zero proves nothing about R''."""
        seen = 0
        for r in load(RECORDS):
            for m, L in r["m"].items():
                if L["status"] != "FAIL":
                    continue
                seen += 1
                lo = F(L["R2_interval"]["lo"])
                hi = F(L["R2_interval"]["hi"])
                self.assertLess(lo, 0, (r["cell_index"], m))
                self.assertGreater(hi, 0, (r["cell_index"], m))
        self.assertGreater(seen, 0, "expected the known high-radius failures")

    def test_failing_block_is_the_high_radius_one(self):
        failing = {r["cell_index"] for r in load(RECORDS)
                   if any(L["status"] == "FAIL" for L in r["m"].values())}
        self.assertTrue(failing <= set(range(318, 325)),
                        f"failures outside the known block: {failing}")

    def test_cell_325_is_certified_pass(self):
        r = next((x for x in load(RECORDS) if x["cell_index"] == 325), None)
        self.assertIsNotNone(r, "cell 325 must be re-certified")
        for m, L in r["m"].items():
            self.assertEqual(L["status"], "PASS", m)
            self.assertLess(L["cover"]["utilization"], 1.0, m)

    def test_cusum_compact_cover_is_not_claimed_certified(self):
        a = final_audit.review(NS / "diagnostics/cells")
        self.assertFalse(a["recertified_cells"]["cusum_compact_cover_certified"])
        self.assertEqual(a["recertified_cells"]["failure_class"],
                         "CERTIFICATE_TOO_LOOSE")

    def test_enclosures_never_loosened_against_the_reviewed_run(self):
        impl = base.IMPL_NS / "diagnostics/representatives"
        for r in load(RECORDS):
            p = impl / f"CUSUM_{r['cell_index']}_256.json"
            if not p.exists():
                continue
            old = json.loads(p.read_text())
            for m, L in r["m"].items():
                a = old["m"][m]
                self.assertLessEqual(F(L["M_R2"]), F(a["M_R2"]), (r["cell_index"], m))
                self.assertGreaterEqual(F(L["R_interval"]["lo"]),
                                        F(a["R_interval"]["lo"]))
                self.assertLessEqual(F(L["R_interval"]["hi"]),
                                     F(a["R_interval"]["hi"]))

    def test_provenance_and_s0_invariants_hold(self):
        for r in load(RECORDS):
            self.assertTrue(r["provenance_chain"]["all_verified"])
            self.assertEqual(r["provenance_chain"]["obligations"], 28)
            self.assertTrue(r["s0_charge_audit"]["all_charged_exactly_once"])
            for k in ("dag_audit_mid", "dag_audit_cell"):
                self.assertEqual(r[k]["duplicate_edges"], 0)

    def test_frozen_kernel_correspondence_retained(self):
        r = next((x for x in load(RECORDS) if x["cell_index"] == 221), None)
        if r is None:
            self.skipTest("cell 221 not in this record set")
        self.assertAlmostEqual(float(F(r["objects"]["h_2:0"]["delta_mid"])),
                               1.83e-06, delta=0.02e-06)
        self.assertAlmostEqual(float(F(r["objects"]["S_1:0"]["delta_mid"])),
                               2.76e-06, delta=0.02e-06)


class Governance(unittest.TestCase):
    def test_protected_namespaces_byte_preserved(self):
        for name, ns, commit in final_audit.PROTECTED:
            if commit is None:
                self.assertTrue(final_audit.frozen_tree_unchanged())
            else:
                r = final_audit.namespace_preserved(ns, commit)
                self.assertEqual(r["paths_changed"], [], name)

    def test_frozen_invariants_unchanged(self):
        self.assertEqual(spec.HARD_CAP_CPU_H, 1126)
        self.assertEqual(spec.PRODUCTION_BITS, 256)
        self.assertFalse(spec.PRODUCTION_ENABLED)
        self.assertFalse(spec.PRECISION_ESCALATION_ALLOWED)
        self.assertFalse(spec.DEGREE_ADAPTATION_ALLOWED)
        self.assertEqual(sum(spec.TOP_BUDGETS.values()), F(19, 100))
        self.assertEqual(len(reviewed.work_ids()), 17978)
        self.assertEqual(spec.verify_frozen_spec(), spec.FROZEN_HASHES)

    def test_cover_geometry_unchanged(self):
        self.assertEqual(spec.CELLS_SHA256,
                         spec.CHECKPOINT["geometry"]["cells_sha256"])
        self.assertEqual(spec.COUNTS, {"CUSUM": 326, "SR": 316})

    def test_writes_only_inside_this_namespace(self):
        changed = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=base.ROOT).decode().splitlines()
        rel = str(NS.relative_to(base.ROOT))
        stray = [line for line in changed if rel not in line]
        self.assertEqual(stray, [], f"writes outside {rel}: {stray}")

    def test_production_not_authorized_and_not_launched(self):
        a = final_audit.review(NS / "diagnostics/cells")
        self.assertEqual(a["P5Y_PRODUCTION_ALLOWED"], "NO")
        self.assertFalse(a["production_launched"])
        self.assertFalse(a["K1_CLOSED_claimed"])
        self.assertEqual(a["overall_state"], "K1_INCOMPLETE_IMPLEMENTATION")


if __name__ == "__main__":
    unittest.main(verbosity=2)
