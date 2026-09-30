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
    return res


if __name__ == "__main__":
    r = run()
    import datetime, hashlib, json
    (FNS / "evidence" / "u2").mkdir(parents=True, exist_ok=True)
    (FNS / "evidence" / "u2" / "U2_CONTROLS.json").write_text(json.dumps(
        {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         "checker_sha256": hashlib.sha256((FNS / "code" / "u2_structure_check.py").read_bytes()).hexdigest(),
         "all_pass": all(r.values()), "results": r}, indent=1, sort_keys=True) + "\n")
    for k, v in r.items():
        print(f"[{'PASS' if v else 'FAIL'}] {k}")
    sys.exit(0 if all(r.values()) else 1)
