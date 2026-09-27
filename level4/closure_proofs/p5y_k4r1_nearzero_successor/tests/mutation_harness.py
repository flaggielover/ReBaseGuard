"""K4R1 mutation harness: every mutant of the decision path must be killed by tests/test_k4r1.py.

Each mutant is a copy of code/k4r1_certificate.py with ONE textual change, written to a temporary directory and
tested through $K4R1_CODE_PATH. The unmodified copy (null mutant) must pass; every real mutant must fail.
Synthetic only. Writes a JSON report.

  python tests/mutation_harness.py --out MUTATION_REPORT.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CODE = NS / "code/k4r1_certificate.py"
TESTS = NS / "tests/test_k4r1.py"

MUTANTS = [
    ("strict_to_nonstrict", "\"PASS\": B < 0,", "\"PASS\": B <= 0,"),
    ("drop_max_T_0", "return G + a * a / 6 * max(T, F(0))", "return G + a * a / 6 * T"),
    ("weaker_remainder_24", "return G + a * a / 6 * max(T, F(0))", "return G + a * a / 24 * max(T, F(0))"),
    ("remainder_linear_in_a", "return G + a * a / 6 * max(T, F(0))", "return G + a / 6 * max(T, F(0))"),
    ("g_sign_flip", "return D0_hi - L1 * e0 * e0 / 2", "return D0_hi + L1 * e0 * e0 / 2"),
    ("g_drop_correction", "return D0_hi - L1 * e0 * e0 / 2", "return D0_hi"),
    ("t_drop_transport", "return min(M3, U0 + a * a / 2 * M5)", "return min(M3, U0)"),
    ("t_half_transport", "return min(M3, U0 + a * a / 2 * M5)", "return min(M3, U0 + a * a / 4 * M5)"),
    ("t_accept_negative_majorant", "if M3 < 0 or M5 < 0:", "if False:"),
    ("accept_floats", "if isinstance(x, float) or isinstance(x, bool):", "if False:"),
    ("accept_bad_interval", "if lo > hi:\n        raise K4R1Refusal(\"malformed interval lo > hi\")",
     "if False:\n        raise K4R1Refusal(\"malformed interval lo > hi\")"),
    ("universe_unchecked", "if hist != declared:", "if False:"),
    ("prefix_unchecked", "if cells != list(range(len(cells))):", "if False:"),
    ("a_unchecked", "if a != F(r[\"a\"]):", "if False:"),
    ("counterexample_unchecked", "if per[\"outcome\"] != \"K4_CERTIFICATE_TOO_LOOSE\" or per.get(\"counterexample_cells\"):",
     "if False:"),
    ("producer_unchecked", "if k1.get(\"producer_identity_hash\") != prov[\"identities\"][\"k1_cusum_producer_identity_hash\"]:",
     "if False:"),
    ("slot1_binding_unchecked", "and fr(b[\"left\"]) == 0 and fr(ctx[\"point_e\"]) == 0):",
     "and True):"),
    ("x1_unchecked", "if x1 != fr(b[\"right\"]) or not (e0 <= x1):", "if False:"),
    ("text_binding_unchecked", "if text.get(\"sealed_record_sha256\") != prov[\"sources\"][\"slot1_record\"][\"sha256\"]:",
     "if False:"),
    ("hull_ge", "hits = [r for r in rows if fr(r[\"x_hi\"]) == a]", "hits = [r for r in rows if fr(r[\"x_hi\"]) >= a][:1]"),
    ("eta_unchecked", "if not (a <= eta <= a * (1 + F(1, 2 ** 200))):", "if False:"),
    ("assembly_handoff_unchecked", "and bool(rest) and F(rest[0][\"left\"]) == a)", "and bool(rest))"),
    ("assembly_rest_unchecked", "and all(c[\"how\"] in (\"CHAIN_RPRIME_NEGATIVE\", \"DIRECT_R_NEGATIVE\") for c in rest)",
     "and True"),
    ("assembly_inherited_unchecked", "per[key] = {\"status\": \"PASS\" if ok else \"FAIL\"", "per[key] = {\"status\": \"PASS\""),
    ("assembly_contiguity_unchecked", "if not contiguous:", "if False:"),
    ("assembly_ignores_cert", "status = \"PASS\" if (hist_ok and cert[\"PASS\"]) else \"FAIL\"",
     "status = \"PASS\" if hist_ok else \"FAIL\""),
    ("freeze_qualification_unchecked", "if fz.get(\"qualification_verdict\") != \"QUALIFICATION_ACCEPTED\":", "if False:"),
    ("freeze_hash_unchecked", "if not hp.exists() or hp.read_text().strip() != sha_file(freeze_path):", "if False:"),
    ("freeze_drift_unchecked", "if not p.exists() or sha_file(p) != h:", "if False:"),
    ("exact_once_removed", "if out.exists():\n        raise K4R1Refusal(\"EXACT_ONCE: output already exists\")",
     "if False:\n        raise K4R1Refusal(\"EXACT_ONCE: output already exists\")"),
    ("document_hash_unchecked", "if not p.exists() or sha_file(p) != v[\"sha256\"]:", "if False:"),
    ("json_hash_unchecked", "if sha_file(p) != entry[\"sha256\"]:", "if False:"),
]


def run(code_text: str, tmp: Path) -> int:
    p = tmp / "k4r1_certificate.py"
    p.write_text(code_text)
    env = {**os.environ, "K4R1_CODE_PATH": str(p), "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", str(TESTS)],
                       env=env, capture_output=True, text=True)
    return r.returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    src = CODE.read_text()
    rows = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        null_rc = run(src, tmp)
        for name, old, new in MUTANTS:
            n = src.count(old)
            if n != 1:
                rows.append({"mutant": name, "applied": False, "occurrences": n, "killed": False})
                continue
            rc = run(src.replace(old, new), tmp)
            rows.append({"mutant": name, "applied": True, "killed": rc != 0, "pytest_rc": rc})
    rep = {"schema": "rebaseguard.p5y.k4r1.mutation-report.v1",
           "code_sha256": hashlib.sha256(src.encode()).hexdigest(),
           "tests_sha256": hashlib.sha256(TESTS.read_bytes()).hexdigest(),
           "null_mutant_passes": null_rc == 0, "mutants": rows,
           "all_applied": all(r["applied"] for r in rows), "all_killed": all(r["killed"] for r in rows)}
    rep["PASS"] = rep["null_mutant_passes"] and rep["all_applied"] and rep["all_killed"]
    Path(a.out).write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"PASS": rep["PASS"], "null": rep["null_mutant_passes"],
                      "survivors": [r["mutant"] for r in rows if not r["killed"]]}))
    return 0 if rep["PASS"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
