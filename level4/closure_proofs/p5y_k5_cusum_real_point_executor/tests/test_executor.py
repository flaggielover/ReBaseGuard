"""Development tests of the real point executor that need no python-flint (the full suite is qualify_executor.py on vultr-02).

    python3 -B tests/test_executor.py
"""
from __future__ import annotations

import ast
import json
import sys
import unittest
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CODE = NS / "code"
sys.path.insert(0, str(CODE))


class Static(unittest.TestCase):
    def test_guard_policy_is_deny(self):
        self.assertEqual(json.loads((NS / "config/REAL_INPUT_GUARD.json").read_text())["policy"], "DENY")

    def test_authorization_template_inactive(self):
        a = json.loads((NS / "config/EXTERNAL_AUTHORIZATION_TEMPLATE.json").read_text())
        self.assertIs(a["EXECUTION_AUTHORIZED"], False)
        self.assertEqual(a["status"], "INACTIVE_TEMPLATE")
        for key in ("protocol_authorization_sha256", "execution_binding_amendment_sha256", "attempt_slot", "nonce",
                    "countersigner", "result_blind"):
            self.assertIn(key, a)
        self.assertFalse((NS / "authorization/COUNTERSIGNATURE_ACTIVE.json").exists())

    def test_d1_validate_calls_frozen_verifier_in_process_only(self):
        tree = ast.parse((CODE / "authorization_interface.py").read_text())
        fns = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        self.assertEqual([a.arg for a in fns["validate"].args.args], ["ctx"])
        self.assertIn("return validate_with(ctx, PV, COUNTERSIGNATURE_FILE)", ast.unparse(fns["validate"]))
        body = ast.unparse(fns["validate_with"])
        self.assertIn("run_verifier(module.verify, module.AUTH_ACTIVE)", body)
        self.assertLess(body.index("present"), body.index("verifier_source_problems(module)"))
        self.assertLess(body.index("verifier_source_problems(module)"), body.index("run_verifier("))
        cli = (CODE / "executor_cli.py").read_text()
        self.assertNotIn("--authorization", cli)
        core = (CODE / "executor_core.py").read_text()
        self.assertNotIn("authorization_bundle", core)

    def test_r4_single_verifier_call_site(self):
        for f in ("executor_core.py", "backends.py", "executor_cli.py", "input_adapters.py"):
            t = ast.unparse(ast.parse((CODE / f).read_text()))
            for x in ("prelaunch_decision(", "AI.validate(", "validate_with(", "run_verifier(", "PV.verify(",
                  "prelaunch_verify.verify("):
                self.assertNotIn(x, t, (f, x))
        sup = ast.unparse(ast.parse((CODE / "supervisor.py").read_text()))
        self.assertEqual(sup.count("AI.prelaunch_decision(ctx)"), 1)
        body = sup.split("def supervise")[1].split("def finish")[0]
        self.assertLess(body.index("governed_prelaunch("), body.index("slot.mkdir()"))

    def test_r4_fence_first_in_validate_with(self):
        tree = ast.parse((CODE / "authorization_interface.py").read_text())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "validate_with")
        body = [st for st in fn.body if not (isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant))]
        self.assertIn("EC.arithmetic_started()", ast.unparse(body[1]))

    def test_r5_canonical_slot_before_verification(self):
        sup = ast.unparse(ast.parse((CODE / "supervisor.py").read_text()))
        body = sup.split("def governed_prelaunch")[1].split("def launch_state_changes")[0]
        order = [body.find(x) for x in ("before, problems = launch_state(slot)", "AI.prelaunch_decision(ctx)",
                                        "after, _ = launch_state(slot)", "toctou = launch_state_changes(before, after, decision)")]
        self.assertTrue(all(i >= 0 for i in order) and order == sorted(order), order)
        self.assertNotIn("slot_dir(len(", sup.split("def supervise")[1].split("def finish")[0])

    def test_d2_markers_written_only_through_lifecycle(self):
        sv = (CODE / "supervisor.py").read_text()
        self.assertNotIn("write_text(", sv.split("def supervise")[1])
        self.assertIn("LC.write_terminal(slot, LC.RUN_COMPLETE", sv)
        self.assertIn("LC.write_terminal(slot, LC.RUN_FAILED", sv)

    def test_guard_checked_before_any_backend_method(self):
        tree = ast.parse((CODE / "executor_core.py").read_text())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "execute")
        body = [st for st in fn.body if not (isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant))]
        self.assertIn("enforce_guard(backend, ctx)", ast.unparse(body[0]))

    def test_executor_never_interprets_signs(self):
        for mod in ("executor_core.py", "backends.py", "input_adapters.py"):
            src = (CODE / mod).read_text()
            for name in ("scientific_verdict", "point_sign", "h3a_consequence", "aggregate(", "consumer", "qualification_gates"):
                self.assertNotIn(name, src, (mod, name))

    def test_qualification_gates_use_only_address_rules(self):
        tree = ast.parse((CODE / "qualification_gates.py").read_text())
        used = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "PR"}
        self.assertLessEqual(used, {"scientific_address", "load_prereg"})

    def test_smoke_forms_no_enclosure(self):
        tree = ast.parse((CODE / "smoke.py").read_text())
        used = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)} | {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        for forbidden in ("certify_graded", "local_tower", "enclosure_stages", "execute", "transport"):
            self.assertNotIn(forbidden, used)

    def test_mutation_anchors_match_once(self):
        import make_protocol_executor as MP
        muts = MP.mutations()
        self.assertEqual([m["id"][:3] for m in muts], [f"E{i:02d}" for i in range(1, 17)])
        for m in muts:
            self.assertEqual((CODE / m["file"]).read_text().count(m["old"]), 1, m["id"])

    def test_production_backend_rechecks_guard(self):
        tree = ast.parse((CODE / "backends.py").read_text())
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "CusumPointBackend")
        prep = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "prepare_point")
        body = [st for st in prep.body if not (isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant))]
        self.assertIn("enforce_guard(self, ctx)", ast.unparse(body[0]))

    def test_r2_mutation_groups_match_once(self):
        import make_protocol_executor as MP
        groups = {"P": MP.production_mutations(), "A": MP.authorization_mutations(), "V": MP.void_mutations(),
                  "C": MP.cramer_mutations(), "D": MP.d1_mutations(), "L": MP.lifecycle_mutations(),
                  "R": MP.recovery_mutations(), "N": MP.governed_mutations(), "X": MP.x1_mutations()}
        self.assertEqual([len(groups[k]) for k in "PAVCDLRNX"], [4, 3, 1, 1, 4, 4, 2, 5, 5])
        for muts in groups.values():
            for m in muts:
                self.assertEqual((CODE / m["file"]).read_text().count(m["old"]), 1, m["id"])

    def test_guard_file_not_part_of_identity_or_pins(self):
        import authorization_interface as AI
        self.assertNotIn("config/REAL_INPUT_GUARD.json", AI.IDENTITY_FILES)
        pins = NS / "config/EXECUTOR_PINS.json"
        if pins.exists():
            self.assertFalse(any(k.endswith("REAL_INPUT_GUARD.json") for k in json.loads(pins.read_text())["files"]))

    def test_void_sealed_on_any_failure_after_arithmetic_started(self):
        src = (CODE / "executor_core.py").read_text()
        fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "execute")
        text = ast.unparse(fn)
        self.assertIn("except BaseException", text)
        self.assertIn("VOID_NAMES", text)
        self.assertIn("void_class(exc)", text)
        self.assertLess(text.index("log.emit('ARITHMETIC_STARTED')"), text.index("run_stages_before_enclosure"))

    def test_consumer_uses_frozen_producer_qualification(self):
        src = (CODE / "consumer.py").read_text()
        self.assertIn("PR.producer_qualification(", src)
        self.assertIn("PR.science_usable(", src)
        self.assertNotIn("QE05_GUARD_RECORDED", (CODE / "qualification_gates.py").read_text())

    def test_trust_model_does_not_claim_cryptographic_authority(self):
        text = (NS / "TRUST_MODEL.md").read_text()
        self.assertIn("No cryptographic authorization", text)
        self.assertIn("not trust roots", text)


if __name__ == "__main__":
    unittest.main()
