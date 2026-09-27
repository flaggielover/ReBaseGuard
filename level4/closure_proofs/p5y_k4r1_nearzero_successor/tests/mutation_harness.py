"""K4R1 mutation harness: every mutant of the decision path must be killed by tests/test_k4r1.py.

Each mutant is a copy of code/k4r1_certificate.py with ONE textual change, written to a temporary directory and
tested through $K4R1_CODE_PATH. The unmodified copy (null mutant) must pass; every real mutant must fail.
Synthetic only. Writes a JSON report.

Known equivalent mutants (not listed):
- `science = all(PASS) and asm["complete"]` -> `science = asm["complete"]` (r2 R7): the assembly already marks a residual (D,m)
  PASS only when its certificate PASSes.
- removing `if here not in fz["bound_files"]` (r2 F4): the implementation path is also in the mandatory bound set.
- `open(OUT, "x")` -> `open(OUT, "w")`: launch_gates already refuses when OUT exists (differs only under a concurrent race).
- removing the mandatory-binding check in verify_freeze (r3/r4): every mandatory file is tracked in the namespace, and the
  completeness check (bound namespace files == tracked namespace files) plus the review-file checks already refuse.
- removing the ".." test on --review-dir in make_freeze: the pattern review/qualification_rN already excludes "..".
- removing the "review file already existed at the candidate" check in verify_freeze: an unchanged pre-existing file
  cannot appear in `git diff <candidate> HEAD`, so the delta check refuses; a changed one is still pinned by name and
  the bound review JSON must accept the candidate (defence in depth only).

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
MAKE_FREEZE = NS / "code/make_freeze.py"
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
    ("exact_once_removed", "if OUT.exists():\n        raise K4R1Refusal(\"EXACT_ONCE: the canonical output already exists\")",
     "if False:\n        raise K4R1Refusal(\"EXACT_ONCE: the canonical output already exists\")"),
    ("document_hash_unchecked", "if not p.exists() or sha_file(p) != v[\"sha256\"]:", "if False:"),
    ("json_hash_unchecked", "if sha_file(p) != entry[\"sha256\"]:", "if False:"),
    # qualification r1 reviewer's extra mutants (7 survived r1)
    ("D0_lo_instead_of_hi", '"_D0_hi": D0[1]', '"_D0_hi": D0[0]'),
    ("M3_from_order2", 'M3, M5 = fr(row["M"]["3"][m]), fr(row["M"]["5"][m])', 'M3, M5 = fr(row["M"]["2"][m]), fr(row["M"]["5"][m])'),
    ("M5_from_order4", 'M3, M5 = fr(row["M"]["3"][m]), fr(row["M"]["5"][m])', 'M3, M5 = fr(row["M"]["3"][m]), fr(row["M"]["4"][m])'),
    ("M_wrong_m", 'M3, M5 = fr(row["M"]["3"][m]), fr(row["M"]["5"][m])', 'M3, M5 = fr(row["M"]["3"]["1"]), fr(row["M"]["5"]["1"])'),
    ("L1_U0_swapped", 'L1, U0 = fr(pm["L1"]), fr(pm["U0"])', 'U0, L1 = fr(pm["L1"]), fr(pm["U0"])'),
    ("D0_wrong_m", 'ent = k1["m"][m]', 'ent = k1["m"]["1"]'),
    ("exec_g_uses_x1", 'G = g_bound(v["_D0_hi"], v["_L1"], v["e0"])', 'G = g_bound(v["_D0_hi"], v["_L1"], v["x1"])'),
    ("exec_t_args_swapped", 'T = t_bound(v["_M3"], v["_U0"], v["_M5"], v["a"])', 'T = t_bound(v["_M3"], v["_U0"], v["_M5"], v["e0"])'),
    ("exec_science_or", 'science = all(c["PASS"] for c in certs.values()) and asm["complete"]',
     'science = all(c["PASS"] for c in certs.values()) or asm["complete"]'),
    ("hull_row_wrong", 'hits = [r for r in rows if fr(r["x_hi"]) == a]', 'hits = [rows[0]]'),
    ("eta_upper_unbounded", 'if not (a <= eta <= a * (1 + F(1, 2 ** 200))):', 'if not (a <= eta):'),
    ("assembly_residual_how_unchecked",
     'hist_ok = (all(c["how"] == "CERTIFICATE_TOO_LOOSE" for c in cells if c["index"] in rcells)', 'hist_ok = (True'),
    # r2 repair checks
    ("k1_entry_metadata_unchecked", 'if ent.get("detector") != "CUSUM" or ent.get("m") != int(m) or ent.get("cell_index") != 0 \\',
     'if ent.get("detector") != "CUSUM" or False or ent.get("cell_index") != 0 \\'),
    ("slot1_transport_unchecked",
     "if not (tf >= x1 * x1 / 2 and M5x1 >= 0 and L0 <= U0 and L1 <= L0 - tf * M5x1 and U1 >= U0 + tf * M5x1):",
     "if not (tf >= x1 * x1 / 2 and M5x1 >= 0 and L0 <= U0 and True and U1 >= U0 + tf * M5x1):"),
    ("git_clean_unchecked", 'if not (gs["clean"] and gs["freeze_committed"]):', 'if not (True and gs["freeze_committed"]):'),
    ("git_freeze_committed_unchecked", 'if not (gs["clean"] and gs["freeze_committed"]):', 'if not (gs["clean"] and True):'),
    ("coverage_flag_always_pass",
     '"K4R1_COMPACT_RESIDUAL_COVERAGE": "PASS" if all(c["PASS"] for c in certs.values()) else "FAIL",',
     '"K4R1_COMPACT_RESIDUAL_COVERAGE": "PASS",'),
    ("residual_remaining_empty",
     '"residual_remaining": {f"CUSUM|m={m}": c["cells"] for m, c in sorted(certs.items()) if not c["PASS"]},',
     '"residual_remaining": {},'),
    # qualification r2 reviewer survivors (non-equivalent) and r3 execution-path mutants
    ('W1_x1_right_unchecked', 'if x1 != fr(b["right"]) or not (e0 <= x1):', 'if not (e0 <= x1):'),
    ('W2_e0_le_x1_unchecked', 'if x1 != fr(b["right"]) or not (e0 <= x1):', 'if x1 != fr(b["right"]):'),
    ('W3_geometry_e0_unchecked', 'if e0 != F(prov["geometry"]["k1_cell0_e0"]):', 'if False:'),
    ('W4_e0_rho_unchecked', 'if e0 != rho or e0 - rho != 0:', 'if False:'),
    ('W5_k1_detector_unchecked', 'if k1.get("detector") != "CUSUM" or k1.get("cell_index") != 0:', 'if k1.get("cell_index") != 0:'),
    ('W6_slot1_cell_index_unchecked', 'if not (b["k1_cell_index"] == 0 and b["detector"] == "CUSUM"', 'if not (True and True'),
    ('W7_slot1_left_unchecked', 'and fr(b["left"]) == 0 and fr(ctx["point_e"]) == 0):', 'and fr(ctx["point_e"]) == 0):'),
    ('W8_detector_scope_unchecked', ' or universe["detector_scope"] != ["CUSUM"]:', ':'),
    ('W9_M5x1_nonneg_unchecked', 'if not (tf >= x1 * x1 / 2 and M5x1 >= 0 and', 'if not (tf >= x1 * x1 / 2 and True and'),
    ('W11_entry_rho_unchecked', 'or ent.get("rho", k1["rho"]) != k1["rho"]:', 'or False:'),
    ('R1_head_not_recorded', '"executed_at_head": gs["head"], "arithmetic": "exact rational",', '"executed_at_head": None, "arithmetic": "exact rational",'),
    ('R2_freeze_sha_wrong', '"freeze_sha256": sha_file(CONFIG / "FREEZE.json"),\n            "executed_at_head"', '"freeze_sha256": \'0\',\n            "executed_at_head"'),
    ('R3_inputs_record_L1_as_U0', '"L1": str(v["_L1"]), "U0": str(v["_U0"])', '"L1": str(v["_U0"]), "U0": str(v["_L1"])'),
    ('R4_T_branch_inverted', '"T_branch": "M3" if v["_M3"] <= v["_U0"]', '"T_branch": "M3" if v["_M3"] > v["_U0"]'),
    ('F2_git_show_bytes_ignored', 'shown.returncode == 0 and shown.stdout == freeze_path.read_bytes()', 'shown.returncode == 0'),
    ('A1_cover_start_unchecked', 'contiguous = (bool(cells) and F(cells[0]["left"]) == 0 and', 'contiguous = (bool(cells) and'),
    ('A3_counterexample_asm_unchecked', 'and not h.get("counterexample_cells")\n', '\n'),
    ('A4_rest_nonempty_unchecked', 'and bool(rest) and F(rest[0]["left"]) == a)', 'and (not rest or F(rest[0]["left"]) == a))'),
    ('A6_outside_universe_pass', 'per[key] = {"status": "FAIL", "reason": f"historical {h[\'outcome\']} outside the K4R1 universe"}', 'per[key] = {"status": "PASS", "reason": "x"}'),
    ('r3_mkdir_removed', 'OUT.parent.mkdir(parents=True, exist_ok=True)', 'pass'),
    ('r3_crash_record_removed', 'fh.write(json.dumps({"schema": "rebaseguard.p5y.k4r1.result.v1", "status": "EXECUTION_CRASHED",', 'fh.write(json.dumps({"schema": "rebaseguard.p5y.k4r1.result.v1", "status": "EXECUTED",'),
    ('r3_ready_skips_gates', 'gs = launch_gates()[1] if a.cmd == "ready" else None', 'gs = None'),
    ('r3_status_field', '"status": "EXECUTED",\n', '"status": "CRASHED",\n'),
]


CERT_R4 = [
    ("r5_delta_unchecked", "if parents[1:] != [cand] or diff.returncode != 0 or sorted(diff.stdout.split()) != delta:", "if False:"),
    ("r5_parent_unchecked", "if parents[1:] != [cand] or diff.returncode != 0 or sorted(diff.stdout.split()) != delta:",
     "if diff.returncode != 0 or sorted(diff.stdout.split()) != delta:"),
    ("r5_renames_detected", 'diff = git("diff", "--no-renames", "--name-only", cand, "HEAD")', 'diff = git("diff", "--name-only", cand, "HEAD")'),
    ("r5_review_shape_unchecked", "if not (len(review_files) == 2 and re.fullmatch(", "if not (True or len(review_files) == 2 and re.fullmatch("),
    ("r5_review_verdict_unchecked", 'if rv.get("verdict") != "QUALIFICATION_ACCEPTED" or rv.get("candidate_commit") != cand:', "if False:"),
    ("r5_review_candidate_unchecked", 'if rv.get("verdict") != "QUALIFICATION_ACCEPTED" or rv.get("candidate_commit") != cand:',
     'if rv.get("verdict") != "QUALIFICATION_ACCEPTED":'),
    ("r5_blob_unchecked", "if blob.returncode != 0 or sha_bytes(blob.stdout) != h:", "if False:"),
    ("r5_namespace_pristine_unchecked", 'if not gs["namespace_pristine"]:', "if False:"),
    ("r5_isolation_guard_removed", 'if __name__ == "__main__" and not sys.flags.isolated:', "if False:"),
    ("r4_completeness_unchecked", "if tracked.returncode != 0 or bound_ns != set(tracked.stdout.split()) - freeze_rel:", "if False:"),
    ("r4_delta_malformed_unchecked", "if not (freeze_rel <= set(delta) and set(delta) == freeze_rel | set(review_files)", "if not (True"),
    ("r4_majorant_sign_extract_unchecked", "if M3 < 0 or M5 < 0 or a <= 0:", "if False:"),
    ("r4_crash_head_missing", '"error": repr(exc), "executed_at_head": gs["head"],', '"error": repr(exc), "executed_at_head": None,'),
    ("r4_crash_only_Exception", "except BaseException as exc:", "except Exception as exc:"),
]
MUTANTS += CERT_R4

MF_MUTANTS = [
    ("mf_existing_freeze_ok", "if fz_path.exists() or fh_path.exists():", "if False:"),
    ("mf_review_dir_anywhere", 'if rdir.is_absolute() or ".." in rdir.parts or not re.fullmatch(r"review/qualification_r[0-9]+", rdir.as_posix()):', "if False:"),
    ("mf_review_dir_name_free", 'if rdir.is_absolute() or ".." in rdir.parts or not re.fullmatch(r"review/qualification_r[0-9]+", rdir.as_posix()):',
     'if rdir.is_absolute() or ".." in rdir.parts or rdir.parts[0] != "review":'),
    ("mf_blob_unchecked", "if blob.returncode != 0 or hashlib.sha256(blob.stdout).hexdigest() != h:", "if False:"),
    ("mf_isolation_guard_removed", 'if __name__ == "__main__" and not sys.flags.isolated:', "if False:"),
    ("mf_tracked_review_ok", 'if git("ls-files", "--", str(ns_rel / rdir)).strip():', "if False:"),
    ("mf_status_unchecked", "if sorted(other) != expected or ignored_in_ns:", "if False:"),
    ("mf_ignored_ok", "if sorted(other) != expected or ignored_in_ns:", "if sorted(other) != expected:"),
    ("mf_verdict_unchecked", 'if rv.get("verdict") != "QUALIFICATION_ACCEPTED":', "if False:"),
    ("mf_candidate_unchecked", 'if rv.get("candidate_commit") != head:', "if False:"),
    ("mf_source_drift_unchecked", 'if h != v["sha256"]:', "if False:"),
    ("mf_sources_unbound", "        bound[v[\"path\"]] = h\n", "        pass\n"),
    ("mf_reviews_unbound", "bound.update({p: sha(REPO / p) for p in review_rel})", "pass"),
    ("mf_delta_without_reviews", 'delta = sorted(review_rel + [str(ns_rel / "config/FREEZE.json"), str(ns_rel / "config/FREEZE_HASH")])',
     'delta = sorted([str(ns_rel / "config/FREEZE.json"), str(ns_rel / "config/FREEZE_HASH")])'),
    ("mf_target_flag", '"target_values_present": False,', '"target_values_present": True,'),
]


def run(code_text: str, tmp: Path, mf_text: str | None = None) -> int:
    p = tmp / "k4r1_certificate.py"
    p.write_text(code_text)
    q = tmp / "make_freeze.py"
    q.write_text(mf_text if mf_text is not None else MAKE_FREEZE.read_text())
    env = {**os.environ, "K4R1_CODE_PATH": str(p), "K4R1_MAKE_FREEZE_PATH": str(q), "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", str(TESTS)],
                       env=env, capture_output=True, text=True)
    return r.returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    src = CODE.read_text()
    mf = MAKE_FREEZE.read_text()
    rows = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        null_rc = run(src, tmp)
        for name, old, new in MUTANTS:
            n = src.count(old)
            if n != 1:
                rows.append({"mutant": name, "target": "k4r1_certificate.py", "applied": False, "occurrences": n, "killed": False})
                continue
            rc = run(src.replace(old, new), tmp)
            rows.append({"mutant": name, "target": "k4r1_certificate.py", "applied": True, "killed": rc != 0, "pytest_rc": rc})
        for name, old, new in MF_MUTANTS:
            n = mf.count(old)
            if n != 1:
                rows.append({"mutant": name, "target": "make_freeze.py", "applied": False, "occurrences": n, "killed": False})
                continue
            rc = run(src, tmp, mf.replace(old, new))
            rows.append({"mutant": name, "target": "make_freeze.py", "applied": True, "killed": rc != 0, "pytest_rc": rc})
    rep = {"schema": "rebaseguard.p5y.k4r1.mutation-report.v1",
           "code_sha256": hashlib.sha256(src.encode()).hexdigest(),
           "make_freeze_sha256": hashlib.sha256(mf.encode()).hexdigest(),
           "tests_sha256": hashlib.sha256(TESTS.read_bytes()).hexdigest(),
           "null_mutant_passes": null_rc == 0, "mutants": rows,
           "all_applied": all(r["applied"] for r in rows), "all_killed": all(r["killed"] for r in rows)}
    rep["PASS"] = rep["null_mutant_passes"] and rep["all_applied"] and rep["all_killed"]
    rep["counts"] = {"total": len(rows), "killed": sum(r["killed"] for r in rows)}
    Path(a.out).write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"PASS": rep["PASS"], "null": rep["null_mutant_passes"],
                      "survivors": [r["mutant"] for r in rows if not r["killed"]]}))
    return 0 if rep["PASS"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
