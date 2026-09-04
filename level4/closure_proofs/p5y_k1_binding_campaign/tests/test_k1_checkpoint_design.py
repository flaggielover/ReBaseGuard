"""P5Y K1 binding checkpoint -- DESIGN-VALIDATION tests (T2).

These tests validate the CHECKPOINT ITSELF. They execute no certified numerics,
launch no production work, and are non-result-bearing. Integrity tests read the
ANCHOR COMMIT through `git ls-tree` / `git show`, never the worktree.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import pathlib
import subprocess
import unittest
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
NS_REL = str(NS.relative_to(ROOT))


def load(rel: str) -> dict:
    return json.loads((NS / rel).read_text())


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *a],
                          capture_output=True, text=True, check=True).stdout


class TestScope(unittest.TestCase):
    def setUp(self):
        self.ck = load("CHECKPOINT.json")

    def test_exactly_two_detectors_from_frozen_scope(self):
        det = self.ck["scope"]["detectors"]
        self.assertEqual(set(det), {"CUSUM", "SR"})
        self.assertEqual(det["CUSUM"]["k"], 0.5)
        self.assertEqual(det["CUSUM"]["h"], 5)
        self.assertEqual(det["SR"]["A"], 520.886133602749)
        fs = (ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics"
                     "/FROZEN_SCOPE.md").read_text()
        self.assertIn("520.886133602749", fs)

    def test_m_set_is_exactly_the_frozen_set(self):
        self.assertEqual(self.ck["scope"]["m_values"], [1, 2, 3, 5])
        self.assertEqual(self.ck["scope"]["cartesian_cells"], 8)
        self.assertFalse(self.ck["scope"]["result_dependent_cell_deletion_allowed"])

    def test_k1_only_scope(self):
        for k in ("K2_s_min", "K3_M2", "K4_H2", "K5_H3a", "novelty"):
            self.assertIn(k, self.ck["target"]["out_of_scope"])


class TestBudgetLedger(unittest.TestCase):
    def setUp(self):
        self.b = load("config/budget_ledger.json")

    def test_fractions_and_reserve_sum_to_one_exactly(self):
        fr = {k: Fraction(*v) for k, v in self.b["ledger_fractions"].items()}
        res = Fraction(*self.b["reserve_fraction"])
        self.assertEqual(sum(fr.values()) + res, Fraction(1))
        self.assertTrue(self.b["allocated_plus_reserve_eq_one"])

    def test_allocated_absolute_within_w_target(self):
        alloc = sum(v for k, v in self.b["ledger_absolute"].items()
                    if k != "B_resolvent")
        self.assertAlmostEqual(alloc, 0.190, places=12)
        self.assertLessEqual(alloc, self.b["w_target"])
        self.assertAlmostEqual(self.b["w_target"], 0.2, places=12)

    def test_resolvent_has_no_additive_share(self):
        self.assertEqual(self.b["ledger_absolute"]["B_resolvent"], 0.0)

    def test_non_borrowing_is_absolute(self):
        self.assertFalse(self.b["redistribution_allowed"])
        self.assertFalse(self.b["reserve_drawable"])
        self.assertFalse(self.b["post_result_rebudgeting_allowed"])

    def test_local_gate_budget(self):
        self.assertAlmostEqual(self.b["local_gate_budget"], 0.100, places=12)

    def test_m1_tightening_is_exactly_half_of_gate2e(self):
        rc = self.b["reference_cell"]
        self.assertEqual(self.b["assembly_coefficient_max_over_m"], 1.0)
        self.assertEqual(self.b["assembly_coefficient_argmax_m"], 1)
        self.assertEqual(self.b["gate2e_assembly_coefficient_used"], 0.5)
        self.assertAlmostEqual(rc["tightening_factor_vs_gate2e"], 0.5, places=7)
        self.assertAlmostEqual(
            rc["w_panel_max"],
            self.b["local_gate_budget"] / (rc["C_D"] * rc["n_panels"]), places=15)

    def test_delta_max_is_not_looser_than_gate2e(self):
        rc = self.b["reference_cell"]
        self.assertLess(rc["delta_max"], rc["gate2e_delta_candidate_max_carried"])

    def test_C_is_evaluated_at_worst_case_end(self):
        self.assertIn("e_lo", self.b["C_evaluated_at"])
        self.assertLess(self.b["worst_case_C_at_e0"]["delta_max"],
                        self.b["reference_cell"]["delta_max"])


class TestAssembly(unittest.TestCase):
    """The per-m coefficient tables must equal the general formula."""

    def test_per_m_tables_match_general_formula(self):
        dag = load("config/production_dag.json")
        per_m = dag["assembly"]["per_m"]
        for m in (1, 2, 3, 5):
            tab = per_m[str(m)]
            for r in range(m):
                self.assertEqual(Fraction(tab["F"][f"F_{r}"]), Fraction(1, m))
            expect: dict[str, Fraction] = {}
            for t in range(1, m):
                c = Fraction(1, t) - Fraction(1, m)
                for r in range(t):
                    p = t - r - 1
                    key = ("S_%d" % r) if p == 0 else (
                        "K S_%d" % r if p == 1 else "K^%d S_%d" % (p, r))
                    expect[key] = expect.get(key, Fraction(0)) + c
            got = {k: Fraction(v) for k, v in tab["finite"].items()}
            self.assertEqual(got, expect, f"m={m}")

    def test_m1_is_bare_F0(self):
        per_m = load("config/production_dag.json")["assembly"]["per_m"]
        self.assertEqual(per_m["1"]["F"], {"F_0": "1"})
        self.assertEqual(per_m["1"]["finite"], {})


class TestDag(unittest.TestCase):
    def setUp(self):
        self.d = load("config/production_dag.json")

    def test_nineteen_functions_ten_solves(self):
        self.assertEqual(self.d["functions_per_detector"], 19)
        self.assertEqual(self.d["resolvent_solves_per_detector"], 10)
        self.assertEqual(len(self.d["functions"]), 19)

    def test_union_over_m_equals_m5_set_and_no_m_specific_solve(self):
        ids = {f["id"] for f in self.d["functions"]}
        m5 = {f["id"] for f in self.d["functions"] if 5 in f["needed_by_m"]}
        self.assertEqual(ids, m5)
        self.assertEqual(self.d["m_specific_solves"], 0)
        self.assertTrue(self.d["union_over_m_equals_m5_set"])

    def test_geometry_not_multiplied_by_m(self):
        self.assertFalse(self.d["geometry_multiplied_by_m"])

    def test_dependencies_are_acyclic_and_resolvable(self):
        ids = {f["id"] for f in self.d["functions"]}
        seen: set[str] = set()
        for f in self.d["functions"]:
            for dep in f["deps"]:
                self.assertIn(dep, ids)
                self.assertIn(dep, seen, f"{f['id']} depends on unbuilt {dep}")
            seen.add(f["id"])

    def test_work_units_conserve(self):
        self.assertEqual(self.d["total_work_units"], (323 + 322) * 19)
        self.assertEqual(self.d["total_work_units"], 12255)

    def test_shard_partition_is_exact(self):
        n = self.d["total_work_units"]
        for s in (1, 7, 16, 64, 128, 997):
            bnds = [(n * k) // s for k in range(s + 1)]
            sizes = [bnds[k + 1] - bnds[k] for k in range(s)]
            self.assertEqual(sum(sizes), n)
            self.assertTrue(all(x >= 0 for x in sizes))
            self.assertEqual(bnds[0], 0)
            self.assertEqual(bnds[-1], n)

    def test_rng_not_load_bearing(self):
        self.assertTrue(self.d["RNG_NOT_LOAD_BEARING"])

    def test_phase_order_puts_task1_first_and_cusum_before_sr(self):
        ph = [p["id"] for p in self.d["phases"]]
        self.assertEqual(ph, ["A", "B", "C", "D", "E", "F"])
        by = {p["id"]: p for p in self.d["phases"]}
        self.assertEqual(by["B"]["detector"], "CUSUM")
        self.assertEqual(by["C"]["detector"], "SR")
        self.assertLess(by["B"]["cpu_hours_est"], by["C"]["cpu_hours_est"])
        self.assertFalse(by["F"]["producer_may_self_award"])


class TestCpuModelAndCap(unittest.TestCase):
    def setUp(self):
        self.c = load("CHECKPOINT.json")["cpu"]["model"]
        self.b = self.c["bands_cpu_hours"]

    def test_programme_central_reproduces_carried_value(self):
        self.assertTrue(self.c["programme_central_reproduces"])
        self.assertAlmostEqual(self.c["programme_central_recomputed"],
                               3091.856205551252, places=9)

    def test_k1_scope_factor_is_derived_not_chosen(self):
        self.assertAlmostEqual(self.b["k1_scope_factor"], (19 / 49) / 1.17,
                               places=12)

    def test_bands_are_ordered(self):
        self.assertLess(self.b["optimistic"], self.b["central"])
        self.assertLess(self.b["central"], self.b["conservative"])
        self.assertLess(self.b["conservative"], self.b["worst_plausible"])

    def test_cap_formula_and_that_it_binds_without_binding_too_low(self):
        self.assertEqual(self.b["hard_cpu_cap"],
                         math.ceil(1.5 * self.b["conservative"]))
        self.assertGreater(self.b["hard_cpu_cap"], self.b["worst_plausible"])
        self.assertGreater(self.b["cap_over_central"], 1.5)
        self.assertLess(self.b["hard_cpu_cap"], 4597)

    def test_cap_is_not_the_programme_worst(self):
        ck = load("CHECKPOINT.json")["cpu"]
        self.assertNotEqual(ck["HARD_CPU_CAP_CPU_HOURS"],
                            ck["programme_worst_reference_not_adopted"])
        self.assertFalse(ck["cap_extension_allowed"])


class TestStopRulesAndVerdicts(unittest.TestCase):
    def setUp(self):
        self.s = load("config/stop_rules.json")
        self.v = load("config/final_verdict_spec.json")

    def test_thirteen_stop_rules_all_classified(self):
        self.assertEqual(len(self.s["rules"]), 13)
        tax = set(self.s["failure_taxonomy"])
        for r in self.s["rules"]:
            self.assertIn(r["failure_class"], tax)
            self.assertEqual(r["action"], "STOP IMMEDIATELY")

    def test_no_continue_to_see_what_happens(self):
        self.assertFalse(self.s["continue_to_see_what_happens_allowed"])
        self.assertFalse(self.s["non_decisive_diagnostic_work_exists"])

    def test_cpu_stop_forbids_inferring_pass(self):
        sem = self.s["cpu_stop_semantics"]
        self.assertIn("K1_INCOMPLETE_BUDGET", " ".join(sem["on_cap"]))
        self.assertTrue(any("may not be inferred" in x for x in sem["on_cap"]))
        self.assertTrue(any("NOT_COMPUTED" in x for x in sem["on_cap"]))

    def test_k1_closed_requires_independent_adjudication(self):
        k = self.v["verdicts"]["K1_CLOSED"]
        self.assertFalse(k["producer_may_self_award"])
        self.assertIn("independent_adjudication_PASS", k["requires_all"])
        self.assertIn("every_compact_cover_cell_in_scope_PASS", k["requires_all"])
        self.assertIn("all_m_assembled_for_both_detectors", k["requires_all"])

    def test_k1_closed_does_not_close_p5(self):
        d = self.v["downstream_effects"]["if_K1_CLOSED"]
        self.assertFalse(d["auto_close_P5"])
        self.assertEqual(d["P5_SCIENTIFIC_LINE_STATUS"],
                         "PARTIALLY_REPAIRED_BY_SUCCESSOR")
        self.assertEqual(d["LEVEL4_GLOBAL_CLOSURE"], "NO")
        self.assertEqual(d["NOVELTY_STATUS"], "NOT_ESTABLISHED")
        for k in ("K2_s_min", "K3_M2", "K4_H2", "K5_H3a"):
            self.assertEqual(d[k], "OPEN")

    def test_missing_artifact_is_failure_not_silence(self):
        self.assertEqual(self.v["missing_artifact_is"],
                         "CHECKPOINT_INTEGRITY_FAILURE")
        self.assertFalse(self.v["summary_only_artifacts_allowed"])
        self.assertFalse(self.v["post_freeze_amendment_allowed"])


class TestNumericalGovernance(unittest.TestCase):
    def setUp(self):
        self.ck = load("CHECKPOINT.json")

    def test_amplification_is_an_upper_bound_and_audited(self):
        a = self.ck["amplification"]
        self.assertEqual(a["type"], "UPPER")
        self.assertTrue(a["direction_audit_mandatory_before_cells"])
        self.assertFalse(a["uses_P5X_defect_D3_assumption"])
        for det in ("CUSUM", "SR"):
            self.assertLessEqual(a["per_detector"][det]["C_at_0"],
                                 a["certified_cap"])

    def test_amplification_is_frozen_per_detector(self):
        pd = self.ck["amplification"]["per_detector"]
        self.assertNotEqual(pd["CUSUM"]["source"], pd["SR"]["source"])
        self.assertNotEqual(pd["CUSUM"]["cells"], pd["SR"]["cells"])

    def test_p1_rule_and_check_are_distinct_with_explicit_workprec(self):
        p = load("config/p1_rule.json")
        self.assertTrue(p["rule_and_check_distinct"])
        target = (1 - p["eps_P1"]) * 1e-9
        self.assertLess(target, p["P1_CHECK_THRESHOLD"])
        self.assertEqual(p["P1_RULE_WORKPREC_BITS"], 512)
        self.assertGreater(p["expected_headroom_rel"], p["P1_HEADROOM_GUARD"])
        self.assertAlmostEqual(p["headroom_over_guard"], 1000.0, places=6)

    def test_precision_policy_forbids_adaptation(self):
        pr = load("config/precision_policy.json")
        self.assertEqual(pr["SR_production_bits"], 256)
        self.assertEqual(pr["CUSUM_production_bits"], 256)
        self.assertFalse(pr["PRECISION_ESCALATION_ALLOWED"])
        self.assertFalse(pr["DEGREE_ADAPTATION_ALLOWED"])
        self.assertFalse(pr["POST_RESULT_REBUDGETING_ALLOWED"])

    def test_complexity_ceiling_admits_measured_and_rejects_escalation(self):
        c = load("config/complexity_guard.json")
        ceil_ = c["PRODUCTION_COMPLEXITY_CEILING"]
        self.assertEqual(ceil_, 60000)
        self.assertNotEqual(ceil_, c["pilot_era_ceiling_not_used"])
        for det, s in c["measured_scores"].items():
            self.assertLess(s, ceil_, det)
        self.assertGreater(c["rejects_bidegree_20"], ceil_)
        self.assertGreater(c["gate2c_defect_score_order"], 10 * ceil_)
        self.assertTrue(c["fires_before_kernel_construction"])


class TestCover(unittest.TestCase):
    def test_cover_counts_and_sources(self):
        cu = load("manifests/cover_cusum.json")
        sr = load("manifests/cover_sr.json")
        self.assertEqual(cu["subcell_count"], 323)
        self.assertEqual(sr["subcell_count"], 322)
        self.assertEqual(cu["e_star"], 5.5)
        self.assertAlmostEqual(sr["e_star"], 6.755531464321473, places=12)
        for c in (cu, sr):
            self.assertTrue(c["covers_exactly"])
            self.assertFalse(c["adaptive_splitting_allowed"])
            self.assertTrue((ROOT / c["source_artifact"]).exists(),
                            c["source_artifact"])

    def test_sr_patch_accounting_is_measured_not_inherited(self):
        sr = load("manifests/cover_sr.json")
        self.assertEqual(sr["patches_nominal"] - sr["patches_excluded"],
                         sr["patches_live"])
        self.assertEqual(sr["total_panels_over_live_patches"], 83452)
        self.assertTrue(sr["n_z_is_not_global_28"])
        self.assertNotEqual(sr["total_panels_over_live_patches"],
                            sr["patches_live"] * 28)

    def test_cover_matches_gate2b_artifact(self):
        sr = load("manifests/cover_sr.json")
        g = json.loads((ROOT / sr["source_artifact"]).read_text())
        self.assertEqual(sr["subcell_count"], g["cover"]["subcell_count_upper_bound"])
        self.assertEqual(sr["patches_live"], g["patches"]["live"])
        self.assertEqual(sr["total_panels_over_live_patches"],
                         g["patches"]["total_panels_over_live_patches"])


class TestNoProductionPerformed(unittest.TestCase):
    def test_no_result_bearing_artifacts_exist(self):
        for d in ("results", "certificates", "logs"):
            files = [p for p in (NS / d).rglob("*") if p.is_file()
                     and p.name != ".gitkeep"]
            self.assertEqual(files, [], f"{d}/ must be empty at T2")
        self.assertFalse((NS / "FINAL_K1_VERDICT.json").exists())

    def test_checkpoint_code_imports_no_certified_numerics(self):
        forbidden = {"flint", "mpmath", "sympy", "numpy"}
        for p in sorted((NS / "code").glob("*.py")) + \
                sorted((NS / "tests").glob("*.py")):
            tree = ast.parse(p.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        self.assertNotIn(a.name.split(".")[0], forbidden, p.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    self.assertNotIn(node.module.split(".")[0], forbidden, p.name)

    def test_checkpoint_declares_production_not_run(self):
        ck = load("CHECKPOINT.json")
        self.assertEqual(ck["production_run"], "NO")
        self.assertTrue(ck["design_only"])
        self.assertFalse(ck["result_bearing_artifacts_present"])
        self.assertFalse(ck["task1"]["executed"])
        self.assertEqual(ck["state"]["P5Y_PRODUCTION_RUN"], "NO")
        self.assertEqual(ck["state"]["P5Y_BINDING_CHECKPOINT_CREATED"], "YES")
        self.assertEqual(ck["state"]["P5Y_K1_CHECKPOINT_STATUS"], "FROZEN")

    def test_doc_final_block_says_production_no(self):
        txt = (NS / "CHECKPOINT.md").read_text()
        self.assertIn("P5Y_PRODUCTION_RUN             = NO", txt)
        self.assertIn("P5Y_BINDING_CHECKPOINT_CREATED = YES", txt)
        self.assertNotIn("K1_CLOSED\n```\n\n## 31", txt)


class TestInheritedVerdictsUnchanged(unittest.TestCase):
    def test_failed_gates_stay_failed(self):
        s = load("CHECKPOINT.json")["inherited_state"]
        self.assertEqual(s["P5Y_GATE2D"], "SR_REALCANDIDATE_FAIL_REPRESENTATION")
        self.assertEqual(s["P5Y_GATE2E"], "SR_METRIC_FAIL_CANDIDATE")
        self.assertEqual(s["P5Y_GATE2C"], "M2_ASSEMBLY_INCOMPLETE_EXTERNAL")
        self.assertEqual(s["P5_ORIGINAL_VERDICT"], "PARTIAL")
        self.assertEqual(s["P5X_FINAL_VERDICT"], "PARTIAL")
        self.assertTrue(s["failed_gates_remain_failed_permanently"])
        self.assertFalse(s["reinterpretation_of_prior_verdicts"])


class TestAnchorIntegrity(unittest.TestCase):
    """Hashes must come from the object database at the anchor commit."""

    def setUp(self):
        self.man = load("manifests/source_manifest.json")
        self.anchor = self.man["anchor_commit"]

    def test_manifest_declares_git_ls_tree_provenance(self):
        self.assertIn("git ls-tree", self.man["hash_source"])
        self.assertNotIn("worktree", self.man["hash_source"].split("never")[0])

    def test_every_hashed_file_matches_the_anchor_blob(self):
        for rel, digest in self.man["file_sha256"].items():
            raw = subprocess.run(
                ["git", "-C", str(ROOT), "show",
                 f"{self.anchor}:{NS_REL}/{rel}"],
                capture_output=True, check=True).stdout
            self.assertEqual(hashlib.sha256(raw).hexdigest(), digest, rel)

    def test_checkpoint_hash_recomputes(self):
        agg = hashlib.sha256()
        for rel, digest in self.man["file_sha256"].items():
            agg.update(rel.encode()); agg.update(b"\0")
            agg.update(digest.encode()); agg.update(b"\n")
        self.assertEqual(agg.hexdigest(), self.man["CHECKPOINT_HASH"])
        self.assertEqual(load("manifests/CHECKPOINT_HASH.json")["CHECKPOINT_HASH"],
                         self.man["CHECKPOINT_HASH"])

    def test_protected_inputs_unchanged_since_anchor(self):
        prot = load("manifests/protected_inputs.json")
        self.assertEqual(prot["absent_at_anchor"], [])
        for path, sha in prot["directory_tree_sha1"].items():
            out = git("ls-tree", "HEAD", path + "/")
            self.assertTrue(out.strip(), path)
            self.assertEqual(out.split()[2], sha, f"{path} MUTATED since anchor")

    def test_writable_paths_are_only_the_three_output_dirs(self):
        prot = load("manifests/protected_inputs.json")
        self.assertEqual(sorted(prot["writable_paths"]), sorted([
            f"{NS_REL}/results", f"{NS_REL}/certificates", f"{NS_REL}/logs"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
