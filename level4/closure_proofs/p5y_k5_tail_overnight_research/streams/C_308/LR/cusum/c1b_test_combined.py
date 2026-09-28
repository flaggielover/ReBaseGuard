"""C1b test of the combined supply (review REVIEW_RLR_R2 condition C2, declaration D14).  Exact rationals.

The test recomputes raw RLR, Dv' r2 and Lemma G INDEPENDENTLY of c1b_certpw.assemble (own formulas below) and checks
    SUPPLY_j <= min(RLR_j, Dv'_j, G_j)   (j = 0, 1, 2)
on (i) every certified record of the regenerated evidence (C1B_R2_PW_*.json, if present), (ii) three PLANTED input
sets (raw RLR worse than Dv' by inflated L1/L2; Lemma G smallest; mixed), (iii) 2000 seeded random positive input
sets.  For the planted RLR > Dv' case it also asserts the plant is valid (raw RLR_1 > Dv'_1 exactly) and that SUPPLY
replaced it.  MUTANTS: assemble(use_min=False) and assemble without C_R (no Lemma G) must each FAIL this test.
Output NS/validation/C1B_R2_TEST_COMBINED.json.  No kernel evaluation; no drift is evaluated.
"""
from __future__ import annotations

import json
import random
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[3]
sys.path.insert(0, str(NS / "code"))
sys.path.insert(0, str(HERE))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()
import c1b_certpw as CP  # noqa: E402
import c1b_prov as PV  # noqa: E402

K1, K2 = CP.KAPPA1, CP.KAPPA2
KEYS = ("A_bar", "tau", "D_lo", "C_T", "C_R", "D1", "D2", "L1_up", "L2_up", "tau_a_lo")


def reference(r: dict) -> dict:
    """own formulas (THEOREM_LR LR-3, THEOREM_AD Lemma Dv' r2, THEOREM_LR LR-4 Lemma G)."""
    Ae = min(r["A_bar"], r["tau"] / r["D_lo"])
    d1, d2 = r["D1"] / r["D_lo"], r["D2"] / r["D_lo"]
    q1 = min(Ae * r["L1_up"] / r["tau_a_lo"], r["L1_up"] / r["D_lo"])
    q2 = min(Ae * r["L2_up"] / r["tau_a_lo"], r["L2_up"] / r["D_lo"])
    C = r["C_T"]
    CR = r["C_R"]
    return {"RLR": (Ae, q1 + Ae * d1, q2 + 2 * q1 * d1 + Ae * (2 * d1 * d1 + d2)),
            "Dv": (Ae, Ae * (K1 * C + d1), Ae * (2 * K1 ** 2 * C ** 2 + K2 * C + 2 * K1 * C * d1 + 2 * d1 * d1 + d2)),
            "G": (CR, K1 * CR ** 2, K2 * CR ** 2 + 2 * K1 ** 2 * CR ** 3)}


def check_one(fn, r: dict) -> dict:
    out = fn(r)
    ref = reference(r)
    sup = (out["A0_SUPPLY"], out["A1_SUPPLY"], out["A2_SUPPLY"])
    ok = all(sup[j] <= min(ref["RLR"][j], ref["Dv"][j], ref["G"][j]) for j in range(3))
    # the supply must still be a valid bound: >= the smallest of the three supplies' termwise combination is not
    # required; but it must be positive
    ok = ok and all(x > 0 for x in sup)
    return {"ok": ok, "supply": sup, "ref": ref}


def planted_sets(base: dict) -> dict:
    p1 = dict(base)
    p1["L1_up"] = base["L1_up"] * 100
    p1["L2_up"] = base["L2_up"] * 100                 # raw RLR worse than Dv'
    p2 = dict(base)
    p2["C_R"] = F(101, 100)                            # Lemma G smallest (planted small resolvent norm)
    p3 = dict(p1)
    p3["C_R"] = base["C_R"] * F(1, 2)
    return {"P1_RLR_worse_than_Dv": p1, "P2_G_smallest": p2, "P3_mixed": p3}


def random_sets(n: int, seed: int) -> list:
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        tau_a_lo = F(rng.randint(1, 400), 20)
        tau = tau_a_lo * (1 + F(rng.randint(0, 200), 100))
        D_lo = F(rng.randint(1, 1000), 1000)
        r = {"tau_a_lo": tau_a_lo, "tau": tau, "D_lo": D_lo,
             "A_bar": tau / D_lo * F(rng.randint(50, 300), 100),
             "C_T": tau * F(rng.randint(100, 500), 100), "C_R": tau / D_lo * F(rng.randint(100, 400), 100),
             "D1": F(rng.randint(0, 1000), 100), "D2": F(rng.randint(0, 5000), 100),
             "L1_up": tau_a_lo * F(rng.randint(10, 4000), 100), "L2_up": tau_a_lo * F(rng.randint(10, 40000), 100)}
        out.append(r)
    return out


def real_sets() -> list:
    sets = []
    for p in sorted((NS / "validation").glob("C1B_R2_PW_*.json")):
        d = json.loads(p.read_text())
        for r in d.get("records", []):
            if r.get("status") == "CERTIFIED":
                x = {k: F(r[k]["exact"]) for k in KEYS if isinstance(r.get(k), dict)}
                if len(x) == len(KEYS):
                    sets.append((p.name, r["degree"], x))
    return sets


def run_test(fn) -> dict:
    res = {"real": [], "planted": {}, "random_fail": 0}
    reals = real_sets()
    for name, d, x in reals:
        c = check_one(fn, x)
        res["real"].append({"file": name, "degree": d, "ok": c["ok"]})
    base = reals[0][2] if reals else random_sets(1, 7)[0]
    for k, x in planted_sets(base).items():
        c = check_one(fn, x)
        ent = {"ok": c["ok"]}
        if k == "P1_RLR_worse_than_Dv":
            ent["plant_valid_RLR1_gt_Dv1"] = c["ref"]["RLR"][1] > c["ref"]["Dv"][1]
            ent["plant_valid_RLR2_gt_Dv2"] = c["ref"]["RLR"][2] > c["ref"]["Dv"][2]
            ent["supply_replaced_RLR1"] = c["supply"][1] < c["ref"]["RLR"][1]
            ent["ok"] = ent["ok"] and ent["plant_valid_RLR1_gt_Dv1"] and ent["supply_replaced_RLR1"]
        if k == "P2_G_smallest":
            ent["plant_valid_G1_smallest"] = c["ref"]["G"][1] < min(c["ref"]["RLR"][1], c["ref"]["Dv"][1])
            ent["ok"] = ent["ok"] and ent["plant_valid_G1_smallest"]
        res["planted"][k] = ent
    for x in random_sets(2000, 20260928):
        if not check_one(fn, x)["ok"]:
            res["random_fail"] += 1
    res["n_real"] = len(res["real"])
    res["passed"] = (all(e["ok"] for e in res["real"]) and all(e["ok"] for e in res["planted"].values())
                     and res["random_fail"] == 0)
    return res


def main():
    t = {"schema": "C1B_R2_TEST_COMBINED/1", "declaration": "PROGRESS.md D14"}
    t["assemble"] = run_test(CP.assemble)
    t["mutant_no_min"] = run_test(lambda r: CP.assemble(r, use_min=False))
    t["mutant_no_G"] = run_test(lambda r: CP.assemble({k: v for k, v in r.items() if k != "C_R"}))
    t["verdict"] = {"assemble_passes": t["assemble"]["passed"],
                    "mutant_no_min_caught": not t["mutant_no_min"]["passed"],
                    "mutant_no_G_caught": not t["mutant_no_G"]["passed"]}
    t["PASS"] = all(t["verdict"].values())
    t["provenance"] = PV.provenance({"TIGHT_CT": CP.TIGHT_CT, "BLOCK_LIGHT": CP.BLOCK_LIGHT})
    path = NS / "validation" / "C1B_R2_TEST_COMBINED.json"
    path.write_text(json.dumps(t, indent=1, sort_keys=True, default=str) + "\n")
    Q.log_execution("streams/C_308/LR/cusum/c1b_test_combined.py", "C1b combined-supply test with mutants (C2)",
                    cells_touched=[], klass="SYNTHETIC_VALIDATION", notes="no kernel evaluation; exact rationals")
    print(json.dumps({"verdict": t["verdict"], "PASS": t["PASS"], "n_real": t["assemble"]["n_real"],
                      "planted": t["assemble"]["planted"], "mutant_no_min_planted": t["mutant_no_min"]["planted"],
                      "mutant_no_G_planted": t["mutant_no_G"]["planted"],
                      "random_fail": [t[k]["random_fail"] for k in ("assemble", "mutant_no_min", "mutant_no_G")]},
                     indent=1, default=str))


if __name__ == "__main__":
    main()
