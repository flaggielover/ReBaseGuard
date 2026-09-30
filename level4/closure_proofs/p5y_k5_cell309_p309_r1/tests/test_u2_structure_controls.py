"""Planted negative controls for code/u2_structure_check.py (the checker must be able to FAIL).

  python3 tests/test_u2_structure_controls.py     -> exit 0 iff the genuine sources pass and every planted defect fails

Each control copies one pinned source into a temporary directory, plants one defect, points the checker at the copy
and requires the corresponding check to fail.  Nothing is evaluated; the checker is static.
"""
from __future__ import annotations

import importlib
import sys
import tempfile
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FNS / "code"))
U = importlib.import_module("u2_structure_check")


def planted(rel: str, old: str, new: str, tmp: Path) -> str:
    src = (U.REPO / rel).read_text(encoding="utf-8")
    assert src.count(old) == 1, f"control anchor not unique in {rel}: {old!r}"
    p = tmp / (Path(rel).stem + "_planted.py")
    p.write_text(src.replace(old, new), encoding="utf-8")
    return str(p)                                     # absolute: REPO / abs == abs


def s1_ok() -> bool:
    return all(v for v in U.s1_identity().values() if isinstance(v, bool))


def run() -> dict:
    res = {}
    res["genuine_S1"] = s1_ok()
    res["genuine_S3"] = all(not v["consumer_or_record_imports"] and not v["record_words_in_string_constants"]
                            for v in U.s3_isolation().values())
    s4 = U.s4_no_record_recompute()
    res["genuine_S4"] = not s4["direct_subscript_assignments"] and not s4["adapter_subscripts_record_fields"]
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        saved_src, saved_s1 = dict(U.SRC), dict(U.STAGE1)
        controls = [
            ("C1_new3_extra_adopted_product", "srk_assemble",
             '3 * f["sH"] * g[1]', '3 * f["sH"] * g[1] + f["sH"] * f["sD"]', "S1"),
            ("C2_new4_coefficient_changed", "srk_assemble", '6 * f["sH"] * g[2]', '5 * f["sH"] * g[2]', "S1"),
            ("C3_new3_operator_factor_on_wrong_scalar", "srk_assemble",
             '3 * f["sD"] * g[2]', '3 * f["sH"] * g[2]', "S1"),
            ("C4_frozen_env4_drifted", "tc_rule", "6 * k[2] * (sH + rho * sG)", "6 * k[2] * (sD + rho * sG)", "S1"),
            ("C5_producer_imports_consumer", "srk_certify@", "\nimport hashlib\n", "\nimport hashlib\nimport tct_rule\n",
             "S3"),
            ("C6_stage1b_names_record_file", "rlr307_stage1@", "\nimport hashlib\n",
             "\nimport hashlib\n_X = 'TCT_INPUTS_'\n", "S3"),
            ("C7_direct_recomputes_record_interval", "c2_d5_forecast", 'M0 = F(ad["M_R2"])',
             'M0 = F(ad["M_R2"])\n    ad["R2_interval"] = {"lo": lo, "hi": hi}', "S4"),
            ("C8_adapter_reads_C_upper", "srk_adapter", 'rho = F(meas["rho"])',
             'rho = F(meas["rho"])\n    _c = meas["C_upper"]', "S4"),
        ]
        for name, key, old, new, check in controls:
            U.SRC.clear(); U.SRC.update(saved_src)
            U.STAGE1.clear(); U.STAGE1.update(saved_s1)
            try:
                if key.endswith("@"):
                    k = key[:-1]
                    U.STAGE1[k] = planted(saved_s1[k], old, new, tmp)
                else:
                    U.SRC[key] = planted(saved_src[key], old, new, tmp)
                if check == "S1":
                    fired = not s1_ok()
                elif check == "S3":
                    fired = any(v["consumer_or_record_imports"] or v["record_words_in_string_constants"]
                                for v in U.s3_isolation().values())
                else:
                    s4 = U.s4_no_record_recompute()
                    fired = bool(s4["direct_subscript_assignments"] or s4["adapter_subscripts_record_fields"])
            except U.Unsupported:
                fired = True                              # the checker refuses to certify an unparseable change
            res[name] = fired
        U.SRC.clear(); U.SRC.update(saved_src)
        U.STAGE1.clear(); U.STAGE1.update(saved_s1)
        # ---- version 2 controls (U2 check U3(d)): RV1-RV3 and the U3c / U4 extensions
        v2 = [
            ("RV1_sH_takes_a_new_adopted_product", "srk_adapter", 'F(m["sup"]["H"]),',
             'F(m["sup"]["H"]) + F(m["delta_H"]) * F(m["sup"]["D"]),', "U3a"),
            ("RV2_sigma3_multiplied_by_an_adopted_sup", "srk_adapter", '"sigma3": F(obj_r["sigma3"])',
             '"sigma3": F(obj_r["sigma3"]) * F(m["sup"]["F"])', "U3a"),
            ("RV3_selection_adds_an_adopted_product", "srk_assemble",
             "B3 = old3 if new3 is None or new3 >= old3 else new3",
             'B3 = old3 if new3 is None or new3 >= old3 else new3 + f["sH"] * f["sD"]', "U3b"),
        ]
        for name, key, old, new, check in v2:
            U.SRC.clear(); U.SRC.update(saved_src)
            U.SRC[key] = planted(saved_src[key], old, new, tmp)
            r = U.u3_field_binding() if check == "U3a" else U.u3_branch_selection()
            res[name] = not all(r.values())
        U.SRC.clear(); U.SRC.update(saved_src)
        saved_g = dict(U.GUARD_MODULES)
        U.GUARD_MODULES["p309_guard"] = planted(saved_g["p309_guard"], "\nimport hashlib\n",
                                                "\nimport hashlib\nimport tct_rule\n", tmp)
        res["U3c_guard_imports_a_consumer"] = any(v["consumer_or_record_imports"] for v in U.s3_isolation().values())
        U.GUARD_MODULES.clear(); U.GUARD_MODULES.update(saved_g)
        saved_d = dict(U.DRIVER)
        drv = saved_d["p309_driver"]
        u4 = [
            ("U4i_direct_not_through_the_shim", 'res = con["C2F"].direct(shim, R,', 'res = con["C2F"].direct(con["T"], R,',
             "i_direct_called_unchanged_via_shim"),
            ("U4ii_forbidden_consumer_call", "    shim = _SRKShim(", "    con[\"FC\"].compose(None, 5, None)\n    shim = _SRKShim(",
             "ii_no_forbidden_consumer_calls"),
            ("U4iii_stage1_reads_target_inputs", "    wb, subs = S.cell_blocks(cell[0], cell[1])\n    specs",
             "    wb, subs = S.cell_blocks(cell[0], cell[1])\n    _x = cell_inputs\n    specs",
             "iii_stage1_reads_no_record_or_measurement"),
            ("U4iv_record_interval_rewritten", "    shim = _SRKShim(", '    ci["ad"]["R2_interval"] = None\n    shim = _SRKShim(',
             "iv_record_fields_read_only_in_frozen_roles"),
            ("U4v_target_inputs_from_another_function", "def stage1a_jobs() -> list:\n",
             "def stage1a_jobs() -> list:\n    cell_inputs(None, None, 0)\n", "v_cell_inputs_only_from_the_control"),
        ]
        for name, old, new, key in u4:
            U.DRIVER.clear(); U.DRIVER.update(saved_d)
            U.DRIVER["p309_driver"] = planted(drv, old, new, tmp)
            try:
                res[name] = U.u4_drivers()[key] is False
            except Exception:  # noqa: BLE001
                res[name] = True
        U.DRIVER.clear(); U.DRIVER.update(saved_d)
        res["genuine_U3_U4"] = (all(U.u3_field_binding().values()) and all(U.u3_branch_selection().values())
                                and all(v for v in U.u4_drivers().values() if isinstance(v, bool)))
    return res


if __name__ == "__main__":
    r = run()
    import datetime, hashlib, json
    sys.path.insert(0, str(FNS / "code"))
    import p309_env as E
    (E.evidence_dir("u2") / "U2_CONTROLS_V2.json").write_text(json.dumps(
        {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         "checker_sha256": hashlib.sha256((FNS / "code" / "u2_structure_check.py").read_bytes()).hexdigest(),
         "all_pass": all(r.values()), "results": r}, indent=1, sort_keys=True) + "\n")
    for k, v in r.items():
        print(f"[{'PASS' if v else 'FAIL'}] {k}")
    sys.exit(0 if all(r.values()) else 1)
