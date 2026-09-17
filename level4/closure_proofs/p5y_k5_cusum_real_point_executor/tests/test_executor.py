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
        for key in ("science_preregistration", "executor", "k1_input", "cell", "m_set", "precision_bits", "cpu_ceiling",
                    "host_runtime_identity_sha256", "output_namespace", "attempt_slot", "nonce", "result_blind"):
            self.assertIn(key, a)

    def test_guard_checked_before_any_backend_method(self):
        tree = ast.parse((CODE / "executor_core.py").read_text())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "execute")
        body = [st for st in fn.body if not (isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant))]
        self.assertIn("enforce_guard(backend)", ast.unparse(body[0]))

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
        self.assertIn("enforce_guard(self)", ast.unparse(body[0]))

    def test_trust_model_does_not_claim_cryptographic_authority(self):
        text = (NS / "TRUST_MODEL.md").read_text()
        self.assertIn("No cryptographic authorization", text)
        self.assertIn("not trust roots", text)


if __name__ == "__main__":
    unittest.main()
