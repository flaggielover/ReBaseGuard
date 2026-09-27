"""Stream A (306) -- HISTORICAL_READ reproduction of each supply's OWN atom constants (no Gamma, no mixing).

Purpose (stream brief, deliverable 1, "bound decomposition"): a consistency check only.  For each
single-implementation constant set that historically entered a cell-306 supply, recompute A0/A1/A2
by Lemma Dv' r2 (THEOREM_AD.md:86) from THAT set's own committed constants, and confirm equality with
the committed atom constants:

  * I1 / C2 set (REGISTRY_C2 row, read through the C11R comparison's `original_value` strings, which
    review REVIEW_C11R_COMPARISON.md item 17 verified equal to the registry row)  ->  exact
    `A_exact` of C2_D5_FORECAST.json cells["306"] (provenance C2/C2/C2) and floats of `supplies`.
  * I1 / C1 set (REGISTRY_C1.json block)  ->  floats of C2_D5_FORECAST.json supplies["306"]["C1"].
  * I2 set (C11R comparison `independent_value` for C_T (outward-rounded record, as floor r2 section 6
    binds it), tau, Abar, D_lo; C11RD comparison `independent_value` for D1, D2)  ->  exact target
    `A_exact` of the sealed C12-R2 result (provenance I2/I2/I2).

What is NOT done (quarantine Q1, TARGET_QUARANTINE forbidden classes): no Gamma, no enclosure, no
margin, no per-term decomposition value is emitted; no constant of one implementation is combined
with a constant of the other; no perturbation.  The only derived output besides equality booleans is
the LABEL of the binding eff branch inside each supply (brief: "eff = min(Abar, tau/D_lo) branch that
binds in each supply").  The negative controls compare against PLANTED WRONG committed strings (no new
quantity is computed for them; WITHDRAWN in the R1 repair as class (d)) and against a planted mixed-provenance set, which must be refused
before any arithmetic.

Ledger class HISTORICAL_READ (TARGET_QUARANTINE allowed[1]: arithmetic on committed historical
intermediate values under the historically evaluated supply only).
"""
# ov-quarantine: historical-read reproduce each cell-306 supply's OWN committed A0/A1/A2 (no Gamma, no mixing, no per-term decomposition)
from __future__ import annotations

import json
import re
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[2]
CP = NS.parent
sys.path.insert(0, str(NS / "code"))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()

CELL_KEY = "306"  # string key into committed JSON (HISTORICAL_READ only; see the file-level marker)
SRC = {
    "theorem_ad": CP / "p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md",
    "deflated_consume": CP / "p5y_k5_perron_deflated_resolvent/code/deflated_consume.py",
    "c11r_comparison": CP / "p5y_k5_tail_c11r_n9_statement_alignment/evidence/comparison/C11R_COMPARISON.json",
    "c11rd_comparison": CP / "p5y_k5_tail_c11rd_d1d2_extension/evidence/comparison/C11RD_COMPARISON.json",
    "registry_c1": CP / "p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json",
    "c2_forecast": CP / "p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json",
    # sealed C12-R2 result: committed text, read (never executed, never fed to a new route)
    "c12r2_result": CP / "p5y_k5_tail_c12r2_cell306_adoption/evidence/execution/C12R2_CELL306_RESULT.json",  # sanctioned historical read (file-level marker); not suppressed
}


class MixedSupply(RuntimeError):
    pass


def kappas() -> tuple[F, F]:
    """kappa_1, kappa_2 parsed from the committed consumer source (deflated_consume.py:55-56), not hand-copied."""
    src = SRC["deflated_consume"].read_text()
    k1 = re.search(r"^K1_BOUND = F\((\d+), 10 \*\* (\d+)\)", src, re.M)
    k2 = re.search(r"^K2_BOUND = F\((\d+), 10 \*\* (\d+)\)", src, re.M)
    return F(int(k1.group(1)), 10 ** int(k1.group(2))), F(int(k2.group(1)), 10 ** int(k2.group(2)))


def dv_r2(c: dict, k1: F, k2: F) -> tuple[dict, str]:
    """Lemma Dv' r2 (THEOREM_AD.md:86) on ONE constant set; refuses a set whose provenance is mixed."""
    labels = {v[1] for v in c.values()}
    if len(labels) != 1:
        raise MixedSupply(f"constant set mixes implementations {sorted(labels)}; refused before arithmetic")
    Ab, tau, C, Dlo, D1, D2 = (c[k][0] for k in ("Abar", "tau", "C_T", "D_lo", "D1", "D2"))
    valid = bool(tau >= 1 and C >= tau and Dlo > 0 and Ab >= 1)       # consumer validation (FLOOR_R2 :97)
    if not valid:
        raise ValueError("consumer validation fails")
    ratio = tau / Dlo
    branch = "Abar" if Ab < ratio else ("tau/D_lo" if ratio < Ab else "tie")
    eff = min(Ab, ratio)
    d1, d2 = D1 / Dlo, D2 / Dlo
    A = {"A0": eff, "A1": eff * (k1 * C + d1),
         "A2": eff * (2 * k1 ** 2 * C ** 2 + k2 * C + 2 * k1 * C * d1 + 2 * d1 ** 2 + d2)}
    return A, branch


def load_sets() -> dict:
    cmp_ = json.loads(SRC["c11r_comparison"].read_text())["result"]["per_target"]
    cmpd = json.loads(SRC["c11rd_comparison"].read_text())["per_target"]
    reg1 = {b["cell"]: b for b in json.loads(SRC["registry_c1"].read_text())["blocks"]}[int(CELL_KEY)]
    I1_C2 = {k: (F(cmp_[k]["original_value"]), "I1") for k in ("Abar", "tau", "C_T", "D_lo", "D1", "D2")}
    I1_C1 = {k: (F(reg1[k]), "I1") for k in ("Abar", "tau", "C_T", "D_lo", "D1", "D2")}
    I2 = {k: (F(cmp_[k]["independent_value"]), "I2") for k in ("Abar", "tau", "C_T", "D_lo")}
    I2.update({k: (F(cmpd[k]["independent_value"]), "I2") for k in ("D1", "D2")})
    return {"I1_C2": I1_C2, "I1_C1": I1_C1, "I2": I2}


def float_close(x: F, committed: float) -> bool:
    return abs(float(x) - committed) <= 4e-15 * max(1.0, abs(committed))


def main() -> dict:
    k1, k2 = kappas()
    sets = load_sets()
    fc = json.loads(SRC["c2_forecast"].read_text())
    res = json.loads(SRC["c12r2_result"].read_text())
    out = {"schema": "A306_HISTORICAL_A_REPRO/1", "class": "HISTORICAL_READ",
           "kappa_from_committed_source": {"k1": str(k1), "k2": str(k2), "source": "deflated_consume.py:55-56"},
           "sources": {k: str(v.relative_to(CP)) for k, v in SRC.items()},
           "checks": {}, "branches": {}, "negative_controls": {}}
    A = {}
    for name, s in sets.items():
        A[name], out["branches"][name] = dv_r2(s, k1, k2)

    # I1 / C2  ->  exact A_exact (C2 forecast and the C12-R2 control), and float supplies
    cexp = {j: F(fc["cells"][CELL_KEY]["A_exact"][j]) for j in ("A0", "A1", "A2")}
    ctrl = {j: F(res["control"]["evaluated"]["A_exact"][j]) for j in ("A0", "A1", "A2")}
    out["checks"]["I1_C2_equals_C2_forecast_A_exact"] = A["I1_C2"] == cexp
    out["checks"]["C2_forecast_provenance_is_C2"] = fc["cells"][CELL_KEY]["provenance"] == {"A0": "C2", "A1": "C2", "A2": "C2"}
    out["checks"]["I1_C2_equals_C12R2_control_A_exact"] = A["I1_C2"] == ctrl
    for nm, key in (("I1_C2", "C2"), ("I1_C1", "C1")):
        sup = fc["supplies"][CELL_KEY][key]
        out["checks"][f"{nm}_floats_equal_forecast_supplies_{key}"] = all(float_close(A[nm][j], sup[j]) for j in sup)
    # I2  ->  exact target A_exact of the sealed C12-R2 result, provenance I2/I2/I2
    texp = {j: F(res["target"]["evaluated"]["A_exact"][j]) for j in ("A0", "A1", "A2")}
    out["checks"]["I2_equals_C12R2_target_A_exact"] = A["I2"] == texp
    out["checks"]["C12R2_target_provenance_is_I2"] = res["target"]["provenance"] == {"A0": "I2", "A1": "I2", "A2": "I2"}
    # S_I2 = min{G, I2}: the committed provenance says I2 won every field; confirm against the committed
    # G floats (historical supply only; G is common to both supplies and is not an implementation constant)
    G = fc["supplies"][CELL_KEY]["G"]
    out["checks"]["I2_below_committed_G_every_field"] = all(float(A["I2"][j]) < G[j] for j in G)
    # S_I1 = min{G, C1, C2}: C2 won every field (committed provenance); confirm against committed floats
    out["checks"]["C2_below_G_and_C1_every_field"] = all(
        float(A["I1_C2"][j]) < min(G[j], fc["supplies"][CELL_KEY]["C1"][j]) for j in G)
    # structural read-offs (no number emitted)
    out["checks"]["I2_tau_equals_I2_Abar"] = sets["I2"]["tau"][0] == sets["I2"]["Abar"][0]
    out["checks"]["I2_A0_equals_I2_Abar"] = A["I2"]["A0"] == sets["I2"]["Abar"][0]
    out["checks"]["I2_C_T_record_exceeds_exact_sup_3429_over_500"] = sets["I2"]["C_T"][0] > F(3429, 500)

    # ---- negative control (class a, through the code under test): a planted mixed-provenance constant set must be
    # refused by dv_r2 BEFORE any arithmetic.  No new target quantity is computed.
    # R1 repair (REVIEW_GLOBAL_INTEGRITY_R1 C-6): the former "planted wrong committed A1 string" and "float mismatch"
    # controls tested only a comparison operator (class d); they are WITHDRAWN.  A through-the-code plant for the
    # equality checks would require evaluating Lemma Dv' on a perturbed cell-306 constant set, which the quarantine
    # forbids (no perturbation at a target cell), so none is offered.
    mixed = dict(sets["I2"])
    mixed["D2"] = (sets["I1_C2"]["D2"][0], "I1")               # planted mixed-provenance set
    try:
        dv_r2(mixed, k1, k2)
        out["negative_controls"]["planted_mixed_supply_refused"] = False
    except MixedSupply:
        out["negative_controls"]["planted_mixed_supply_refused"] = True
    out["withdrawn_controls"] = ["planted_wrong_committed_A1_detected (class d)",
                                 "planted_float_mismatch_detected (class d)"]

    out["verdict"] = "PASS" if all(out["checks"].values()) and all(out["negative_controls"].values()) else "FAIL"
    out["coverage"] = {"supplies_reproduced": sorted(sets), "fields": ["A0", "A1", "A2"],
                       "exact_comparisons": 3, "float_comparisons": 2, "negative_controls": 1}
    return out


if __name__ == "__main__":
    o = main()
    dst = NS / "validation" / "A306_HISTORICAL_A_REPRO.json"
    dst.write_text(json.dumps(o, indent=1, sort_keys=True) + "\n")
    Q.log_execution("streams/A_306/audit/a306_reproduce_A.py",
                    "reproduce each cell-306 supply's OWN A0/A1/A2 via Lemma Dv' r2 from its own committed "
                    "constants; equality with committed A_exact; eff-branch label only",
                    cells_touched=[{"detector": "CUSUM", "m": 5, "cell": int(CELL_KEY)}], klass="HISTORICAL_READ",
                    notes="HISTORICAL_DECOMPOSITION per TARGET_QUARANTINE allowed[1]; no Gamma; no mixing; "
                          "no perturbation; outputs booleans + branch labels")
    print(json.dumps({k: o[k] for k in ("verdict", "checks", "branches", "negative_controls")}, indent=1))
