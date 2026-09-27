import os, subprocess, json, tempfile, sys
from pathlib import Path
S = Path(sys.argv[1])
NS = S / "ns/level4/closure_proofs/p5y_k4r1_nearzero_successor"
src = (NS / "code/k4r1_certificate.py").read_text()
TESTS = NS / "tests/test_k4r1.py"
M = [
 # wiring / extraction
 ("W1_x1_right_unchecked", 'if x1 != fr(b["right"]) or not (e0 <= x1):', 'if not (e0 <= x1):'),
 ("W2_e0_le_x1_unchecked", 'if x1 != fr(b["right"]) or not (e0 <= x1):', 'if x1 != fr(b["right"]):'),
 ("W3_geometry_e0_unchecked", 'if e0 != F(prov["geometry"]["k1_cell0_e0"]):', 'if False:'),
 ("W4_e0_rho_unchecked", 'if e0 != rho or e0 - rho != 0:', 'if False:'),
 ("W5_k1_detector_unchecked", 'if k1.get("detector") != "CUSUM" or k1.get("cell_index") != 0:', 'if k1.get("cell_index") != 0:'),
 ("W6_slot1_cell_index_unchecked", 'if not (b["k1_cell_index"] == 0 and b["detector"] == "CUSUM"', 'if not (True and True'),
 ("W7_slot1_left_unchecked", 'and fr(b["left"]) == 0 and fr(ctx["point_e"]) == 0):', 'and fr(ctx["point_e"]) == 0):'),
 ("W8_detector_scope_unchecked", ' or universe["detector_scope"] != ["CUSUM"]:', ':'),
 ("W9_M5x1_nonneg_unchecked", 'if not (tf >= x1 * x1 / 2 and M5x1 >= 0 and', 'if not (tf >= x1 * x1 / 2 and True and'),
 ("W10_U1_unchecked", 'and U1 >= U0 + tf * M5x1):', 'and True):'),
 ("W11_entry_rho_unchecked", 'or ent.get("rho", k1["rho"]) != k1["rho"]:', 'or False:'),
 ("W12_eta_lower_unchecked", 'if not (a <= eta <= a * (1 + F(1, 2 ** 200))):', 'if not (eta <= a * (1 + F(1, 2 ** 200))):'),
 ("W13_M_order_from_x1row", 'hits = [r for r in rows if fr(r["x_hi"]) == a]', 'hits = [r for r in rows if fr(r["x_hi"]) == a or fr(r["x_hi"]) == x1][-1:]'),
 ("W14_U0_from_U1", 'L1, U0 = fr(pm["L1"]), fr(pm["U0"])', 'L1, U0 = fr(pm["L1"]), fr(pm["U1"])'),
 ("W15_L1_from_L0", 'L1, U0 = fr(pm["L1"]), fr(pm["U0"])', 'L1, U0 = fr(pm["L0"]), fr(pm["U0"])'),
 # execute composition / result fields
 ("R1_head_not_recorded", '"executed_at_head": gs["head"]', '"executed_at_head": None'),
 ("R2_freeze_sha_wrong", '"freeze_sha256": sha_file(CONFIG / "FREEZE.json")', '"freeze_sha256": "0"'),
 ("R3_inputs_record_L1_as_U0", '"L1": str(v["_L1"]), "U0": str(v["_U0"])', '"L1": str(v["_U0"]), "U0": str(v["_L1"])'),
 ("R4_T_branch_inverted", '"T_branch": "M3" if v["_M3"] <= v["_U0"]', '"T_branch": "M3" if v["_M3"] > v["_U0"]'),
 ("R5_assembly_flag_always_pass", '"K4R1_COMPLETE_K4_ASSEMBLY": "PASS" if asm["complete"] else "FAIL"', '"K4R1_COMPLETE_K4_ASSEMBLY": "PASS"'),
 ("R6_new_addresses", '"new_real_addresses": 0,\n', '"new_real_addresses": 1,\n'),
 ("R7_science_ignore_certs", 'science = all(c["PASS"] for c in certs.values()) and asm["complete"]', 'science = asm["complete"]'),
 # freeze gating / git state
 ("F1_git_status_ignored", 'status.returncode == 0 and status.stdout.strip() == b""', 'status.returncode == 0'),
 ("F2_git_show_bytes_ignored", 'shown.returncode == 0 and shown.stdout == freeze_path.read_bytes()', 'shown.returncode == 0'),
 ("F3_freeze_committed_always", '"freeze_committed": shown.returncode == 0 and shown.stdout == freeze_path.read_bytes()', '"freeze_committed": True'),
 ("F4_here_not_bound_unchecked", 'if here not in fz["bound_files"]:', 'if False:'),
 ("F5_review_not_required", 'required = [str(ns_rel / r) for r in REQUIRED_BOUND] + [fz.get("qualification_review") or "<absent>"]', 'required = [str(ns_rel / r) for r in REQUIRED_BOUND]'),
 ("F6_exact_once_after_compute", '    if out.exists():\n        raise K4R1Refusal("EXACT_ONCE: output already exists")\n', '    pass\n'),
 ("F7_git_check_skipped", '    if not (gs["clean"] and gs["freeze_committed"]):', '    if False:'),
 ("F8_freeze_absent_ok", 'if not freeze_path.exists():\n        raise K4R1Refusal("EXECUTION_LOCKED: config/FREEZE.json absent")', 'if False:\n        raise K4R1Refusal("EXECUTION_LOCKED: config/FREEZE.json absent")'),
 # assembly
 ("A1_cover_start_unchecked", 'contiguous = (bool(cells) and F(cells[0]["left"]) == 0 and', 'contiguous = (bool(cells) and'),
 ("A2_adjacency_unchecked", 'and all(F(x["right"]) == F(y["left"]) for x, y in zip(cells, cells[1:])))', ')'),
 ("A3_counterexample_asm_unchecked", 'and not h.get("counterexample_cells")\n', '\n'),
 ("A4_rest_nonempty_unchecked", 'and bool(rest) and F(rest[0]["left"]) == a)', 'and (not rest or F(rest[0]["left"]) == a))'),
 ("A5_cellwise_only_CHAIN", 'ok = all(c["how"] in ("CHAIN_RPRIME_NEGATIVE", "DIRECT_R_NEGATIVE") for c in cells)', 'ok = True'),
 ("A6_outside_universe_pass", 'per[key] = {"status": "FAIL", "reason": f"historical {h[\'outcome\']} outside the K4R1 universe"}', 'per[key] = {"status": "PASS", "reason": "x"}'),
 # decision
 ("D1_B_uses_e0", 'B = b_bound(G, T, a)', 'B = b_bound(G, T, a / 2)'),
 ("D2_max_T_minus", 'return min(M3, U0 + a * a / 2 * M5)', 'return max(M3, U0 + a * a / 2 * M5) if False else min(M3, U0 + a * a / 2 * M5 - 1)'),
]
rows = []
with tempfile.TemporaryDirectory() as td:
    for name, old, new in M:
        n = src.count(old)
        if n != 1:
            rows.append({"mutant": name, "result": "NOT_APPLIED", "occurrences": n}); print(name, "NOT_APPLIED", n); continue
        p = Path(td) / "k4r1_certificate.py"; p.write_text(src.replace(old, new))
        env = {**os.environ, "K4R1_CODE_PATH": str(p), "PYTHONDONTWRITEBYTECODE": "1"}
        r = subprocess.run(["/usr/bin/python3", "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", str(TESTS)], env=env, capture_output=True, text=True)
        res = "KILLED" if r.returncode else "SURVIVED"
        rows.append({"mutant": name, "result": res, "rc": r.returncode, "old": old, "new": new}); print(name, res, r.returncode)
json.dump(rows, open(S / "MY_MUTANTS.json", "w"), indent=1)
