"""C1b TWO-SIDED test of the combined supply (REVIEW_RLR_R2 C2; REVIEW_RLR_R3_VERIFY note N5; declarations D14, D18).

For every input set the test recomputes, INDEPENDENTLY of c1b_certpw.assemble (own formulas below):
  raw RLR (THEOREM_LR LR-3), Dv' r2 (THEOREM_AD §4), Lemma G (THEOREM_LR LR-4) and the declared combination D14
  (term-level min with the Dv' factors, quotient-rule assembly with the minimised c1 in the A2 cross term, then the
  componentwise min with G), and asserts
    (E) EXACT rational equality of assemble's A0/A1/A2_SUPPLY and G0/G1/G2 with the recomputation (two-sided), and
    (U) SUPPLY_j <= min(RLR_j, Dv'_j, G_j) and SUPPLY_j > 0.
Inputs: every certified record of the regenerated evidence (C1B_R2_PW_*.json), three PLANTED sets (raw RLR worse than
Dv'; Lemma G smallest; mixed) and 2000 seeded random positive sets.
MUTANTS (each must FAIL the test): no_min, no_G (too large); supply_half, drop_A2_cross, drop_A1_delta, G_no_cubic
(too small / unsound).  Output NS/validation/C1B_R2_TEST_COMBINED.json.  No kernel evaluation, no drift evaluated.
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
OUT_KEYS = ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY", "G0", "G1", "G2")


def reference(r: dict, variant: str = "") -> dict:
    """own formulas; `variant` builds the declared mutants (empty = the correct D14 combination)."""
    Ae = min(r["A_bar"], r["tau"] / r["D_lo"])
    d1, d2 = r["D1"] / r["D_lo"], r["D2"] / r["D_lo"]
    q1 = min(Ae * r["L1_up"] / r["tau_a_lo"], r["L1_up"] / r["D_lo"])
    q2 = min(Ae * r["L2_up"] / r["tau_a_lo"], r["L2_up"] / r["D_lo"])
    C, CR = r["C_T"], r["C_R"]
    f1, f2 = K1 * C, 2 * K1 ** 2 * C ** 2 + K2 * C                  # Dv' factors
    rlr = (Ae, q1 + Ae * d1, q2 + 2 * q1 * d1 + Ae * (2 * d1 * d1 + d2))
    dv = (Ae, Ae * (f1 + d1), Ae * (f2 + 2 * K1 * C * d1 + 2 * d1 * d1 + d2))
    g_cubic = 0 if variant == "G_no_cubic" else 2 * K1 ** 2 * CR ** 3
    G = (CR, K1 * CR ** 2, K2 * CR ** 2 + g_cubic)
    if variant == "no_min":
        c1, c2 = q1, q2
    else:
        c1, c2 = min(q1, Ae * f1), min(q2, Ae * f2)
    A1c = c1 + (0 if variant == "drop_A1_delta" else Ae * d1)
    A2c = c2 + (0 if variant == "drop_A2_cross" else 2 * c1 * d1) + Ae * (2 * d1 * d1 + d2)
    if variant == "no_G":
        sup = (Ae, A1c, A2c)
    else:
        sup = (min(Ae, G[0]), min(A1c, G[1]), min(A2c, G[2]))
    if variant == "supply_half":
        sup = tuple(x / 2 for x in sup)
    return {"RLR": rlr, "Dv": dv, "G": G, "SUPPLY": sup}


def mutant(variant: str):
    def fn(r):
        ref = reference(r, variant)
        return dict(zip(OUT_KEYS, ref["SUPPLY"] + ref["G"]))
    return fn


def check_one(fn, r: dict) -> dict:
    out = fn(r)
    ref = reference(r)                                               # the correct D14 recomputation
    got = tuple(out.get(k) for k in OUT_KEYS)
    want = ref["SUPPLY"] + ref["G"]
    equal = all(g is not None and g == w for g, w in zip(got, want))                     # (E) two-sided
    sup = got[:3]
    upper = all(sup[j] is not None and sup[j] <= min(ref["RLR"][j], ref["Dv"][j], ref["G"][j]) for j in range(3))
    pos = all(x is not None and x > 0 for x in sup)
    return {"ok": equal and upper and pos, "equal": equal, "upper": upper, "pos": pos, "supply": sup, "ref": ref}


def planted_sets(base: dict) -> dict:
    p1 = dict(base)
    p1["L1_up"] = base["L1_up"] * 100
    p1["L2_up"] = base["L2_up"] * 100                 # raw RLR worse than Dv'
    p2 = dict(base)
    p2["C_R"] = F(101, 100)                            # Lemma G smallest
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
        out.append({"tau_a_lo": tau_a_lo, "tau": tau, "D_lo": D_lo,
                    "A_bar": tau / D_lo * F(rng.randint(50, 300), 100),
                    "C_T": tau * F(rng.randint(100, 500), 100), "C_R": tau / D_lo * F(rng.randint(100, 400), 100),
                    "D1": F(rng.randint(0, 1000), 100), "D2": F(rng.randint(0, 5000), 100),
                    "L1_up": tau_a_lo * F(rng.randint(10, 4000), 100),
                    "L2_up": tau_a_lo * F(rng.randint(10, 40000), 100)})
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
    res = {"real": [], "planted": {}, "random_fail": 0, "random_fail_equal": 0, "random_fail_upper": 0}
    reals = real_sets()
    for name, d, x in reals:
        c = check_one(fn, x)
        res["real"].append({"file": name, "degree": d, "ok": c["ok"], "equal": c["equal"], "upper": c["upper"]})
    base = reals[0][2] if reals else random_sets(1, 7)[0]
    for k, x in planted_sets(base).items():
        c = check_one(fn, x)
        ent = {"ok": c["ok"], "equal": c["equal"], "upper": c["upper"]}
        if k == "P1_RLR_worse_than_Dv":
            ent["plant_valid_RLR1_gt_Dv1"] = c["ref"]["RLR"][1] > c["ref"]["Dv"][1]
            ent["plant_valid_RLR2_gt_Dv2"] = c["ref"]["RLR"][2] > c["ref"]["Dv"][2]
            ent["supply_replaced_RLR1"] = c["supply"][1] is not None and c["supply"][1] < c["ref"]["RLR"][1]
            ent["ok"] = ent["ok"] and ent["plant_valid_RLR1_gt_Dv1"] and ent["supply_replaced_RLR1"]
        if k == "P2_G_smallest":
            ent["plant_valid_G1_smallest"] = c["ref"]["G"][1] < min(c["ref"]["RLR"][1], c["ref"]["Dv"][1])
            ent["ok"] = ent["ok"] and ent["plant_valid_G1_smallest"]
        res["planted"][k] = ent
    for x in random_sets(2000, 20260928):
        c = check_one(fn, x)
        res["random_fail"] += not c["ok"]
        res["random_fail_equal"] += not c["equal"]
        res["random_fail_upper"] += not c["upper"]
    res["n_real"] = len(res["real"])
    res["passed"] = (all(e["ok"] for e in res["real"]) and all(e["ok"] for e in res["planted"].values())
                     and res["random_fail"] == 0)
    return res


MUTANTS = {
    "mutant_no_min": lambda r: CP.assemble(r, use_min=False),
    "mutant_no_G": lambda r: CP.assemble({k: v for k, v in r.items() if k != "C_R"}),
    "mutant_supply_half": mutant("supply_half"),
    "mutant_drop_A2_cross": mutant("drop_A2_cross"),
    "mutant_drop_A1_delta": mutant("drop_A1_delta"),
    "mutant_G_no_cubic": mutant("G_no_cubic"),
}
TOO_SMALL = ("mutant_supply_half", "mutant_drop_A2_cross", "mutant_drop_A1_delta", "mutant_G_no_cubic")


def main():
    t = {"schema": "C1B_R2_TEST_COMBINED/2", "declaration": "PROGRESS.md D14, D18", "two_sided": True}
    t["assemble"] = run_test(CP.assemble)
    for name, fn in MUTANTS.items():
        t[name] = run_test(fn)
    # the too-small mutants must be caught by the EQUALITY clause although they satisfy the one-sided bound
    t["too_small_mutants_pass_one_sided_bound"] = {n: t[n]["random_fail_upper"] == 0 for n in TOO_SMALL}
    t["verdict"] = {"assemble_passes": t["assemble"]["passed"],
                    **{f"{n}_caught": not t[n]["passed"] for n in MUTANTS}}
    t["PASS"] = all(t["verdict"].values())
    t["provenance"] = PV.provenance({"TIGHT_CT": CP.TIGHT_CT, "BLOCK_LIGHT": CP.BLOCK_LIGHT})
    path = NS / "validation" / "C1B_R2_TEST_COMBINED.json"
    path.write_text(json.dumps(t, indent=1, sort_keys=True, default=str) + "\n")
    Q.log_execution("streams/C_308/LR/cusum/c1b_test_combined.py",
                    "C1b two-sided combined-supply test with 6 mutants (R2 C2, R3 N5)",
                    cells_touched=[], klass="SYNTHETIC_VALIDATION", notes="no kernel evaluation; exact rationals")
    print(json.dumps({"verdict": t["verdict"], "PASS": t["PASS"], "n_real": t["assemble"]["n_real"],
                      "too_small_pass_one_sided": t["too_small_mutants_pass_one_sided_bound"],
                      "random_fail": {k: t[k]["random_fail"] for k in ["assemble", *MUTANTS]},
                      "real_ok": {k: sum(e["ok"] for e in t[k]["real"]) for k in ["assemble", *MUTANTS]}},
                     indent=1, default=str))


if __name__ == "__main__":
    main()
