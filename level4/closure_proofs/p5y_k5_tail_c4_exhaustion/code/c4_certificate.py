"""Phase 6: evaluate route L against the FROZEN C4 gate and classify mechanically.

Refuses unless the gate hashes to its frozen value. Reads only committed artifacts and the frozen model constants;
evaluates no kernel, runs no operator certification, contacts no host.

    python3 -B c4_certificate.py --out OUT.json
"""
import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c4_rigorous_gaussian as G                                                            # noqa: E402
from c4_common import NS, OPEN_CELLS, cell_supply, committed_inputs, frozen_stack, gamma_at, sha  # noqa: E402
from c4_lower_bound import bound_at, cell_geometry, monotone_check                          # noqa: E402
from c4_model_identity import model                                                         # noqa: E402

GATE_SHA = "d5b5b385d5c123ccd5993116901797f1ef2b75054a56617dfd07e860d526a647"


def frozen_gate() -> dict:
    p = NS / "config/FEASIBILITY_GATES_C4.json"
    if sha(p) != GATE_SHA:
        raise SystemExit("the C4 gate is not the frozen one")
    return json.loads(p.read_bytes())


def intersection_nonempty(d, ad5) -> bool:
    return not (max(F(ad5["R2_interval"]["lo"]), d["lo"]) > min(F(ad5["R2_interval"]["hi"]), d["hi"]))


def evaluate(gate, *, evaluate_at="e_lo", knockout="zero", use_upper_end=False,
             exclude_if=lambda gam: gam >= 0, K_override=None, H_override=None,
             domain_shift=None) -> dict:
    """The whole Phase 6 computation, parameterised ONLY so that the adversarial suite can perturb it.

    The committed certificate is produced by the default arguments; every departure from them is a mutant.
    """
    m = model()
    K = F(K_override) if K_override is not None else m["K"]
    H = F(H_override) if H_override is not None else m["H"]
    geo = cell_geometry()
    FC, B, T, R, DC, SEL = frozen_stack()
    adopted, cover, c1, c2 = committed_inputs(FC)

    per, excluded, not_excluded, outside = {}, [], [], []
    for k in OPEN_CELLS:
        g = geo[k]
        src = k if domain_shift is None else domain_shift.get(k, k)
        e = geo[src][evaluate_at]
        in_closed_cell = g["e_lo"] <= e <= g["e_hi"]
        if not in_closed_cell:
            raise SystemExit(f"cell {k}: the bound is certified at e = {e}, outside its closed cell "
                             f"[{g['e_lo']}, {g['e_hi']}] -- the gate forbids this")
        bd = bound_at(e, K, H)
        Bk = bd["B_hi"] if use_upper_end else bd["B_lo"]

        meas, aux, ad5, cov, s = cell_supply(k, FC, B, T, R, DC, SEL, adopted, cover, c1, c2)
        A = s["A"]
        ko = (F(0), F(0)) if knockout == "zero" else (A["A1"], A["A2"])
        cert_ko = gamma_at(FC, T, R, B, meas, aux, ad5, cov, A["A0"], *ko)
        at_bound = gamma_at(FC, T, R, B, meas, aux, ad5, cov, Bk, *ko)
        blocker_is_A0 = not cert_ko["pass"]

        # the licence for the direct test, exercised per cell rather than assumed
        ladder = [Bk + (A["A0"] - Bk) * F(i, 16) for i in range(17)] if A["A0"] > Bk else [Bk]
        lv = [gamma_at(FC, T, R, B, meas, aux, ad5, cov, x, *ko) for x in ladder]
        licence = {"intersection_nonempty_at_bound": intersection_nonempty(at_bound, ad5),
                   "Gamma_nondecreasing_from_bound_to_certified": all(
                       lv[i]["Gamma"] <= lv[i + 1]["Gamma"] for i in range(len(lv) - 1)),
                   "ladder_points": len(ladder)}

        is_excluded = bool(blocker_is_A0 and exclude_if(at_bound["Gamma"]))
        row = {"evaluated_at_e": str(e), "e_in_closed_cell": in_closed_cell,
               "e_lo": str(g["e_lo"]), "e_hi": str(g["e_hi"]),
               "E_excess_upper": str(bd["EV_hi"]),
               "lower_bound_E_a_tau": str(Bk), "lower_bound_float": float(Bk),
               "A0_certified_float": float(A["A0"]),
               "Gamma_at_bound": float(at_bound["Gamma"]),
               "Gamma_at_certified_A0": float(cert_ko["Gamma"]),
               "blocker_is_A0": blocker_is_A0, "excluded": is_excluded, "licence": licence}
        if not blocker_is_A0:
            row["outside_the_count"] = ("the cell already closes at A1 = A2 = 0 with A0 exactly as certified, so "
                                        "no lower bound on E_a[tau] can bear on it")
            outside.append(k)
        elif is_excluded:
            excluded.append(k)
        else:
            not_excluded.append(k)
        per[str(k)] = row

    in_count = excluded + not_excluded
    if not in_count:
        cls = "FAIL_INCONCLUSIVE"
    elif not excluded:
        cls = "FAIL_INCONCLUSIVE"
    elif not not_excluded:
        cls = "PASS"
    else:
        cls = "PARTIAL"
    return {"cells": per, "excluded": excluded, "not_excluded": not_excluded,
            "outside_the_count": outside, "C4_CLASS": cls,
            "model_used": {"K": str(K), "H": str(H)}, "knockout": knockout}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    gate = frozen_gate()
    r = evaluate(gate)

    # the reported (never load-bearing) bisected critical values, carried through from Phase 1
    th = json.loads((NS / "evidence/phase1/C4_THRESHOLDS.json").read_bytes())["cells"]
    for k, v in r["cells"].items():
        c = th[k]["critical_A0"]
        v["critical_A0_reported_only"] = c["closes_below"] if c else None
        v["slack_over_critical_percent"] = (None if not c else
                                            float(100 * (F(v["lower_bound_E_a_tau"]) / F(str(c["closes_below"])) - 1)))

    out = {"schema": "rebaseguard.p5y.k5.tail-c4.certificate.v1",
           "gate_sha256": GATE_SHA,
           "route": "L: E_a[tau] >= H / E[(|z| - K)^+], ladder/Wald minorant",
           "exclusion_test": gate["exclusion_test"]["statement"],
           "arithmetic": {"library": "fractions.Fraction only", "outward_rounding_grid": f"2^-{G.SCALE}"},
           "monotonicity_of_E_excess": monotone_check(model()["K"], model()["H"],
                                                      F("1701923/1000000"), F("2092283/1000000")),
           **r,
           "permitted_conclusions": gate["permitted_conclusions"][r["C4_CLASS"]],
           "family_exhausted": gate["admissible_family"]["definition"],
           "new_real_scientific_addresses_evaluated": 0,
           "kernel_evaluations": 0, "operator_certifications_run": 0, "remote_hosts_contacted": 0,
           "guard": "REAL_SCIENTIFIC_COMPUTE = DENY"}
    data = json.dumps(out, sort_keys=True, indent=1) + "\n"
    Path(a.out).write_text(data)
    print(json.dumps({"C4_CLASS": out["C4_CLASS"], "excluded": out["excluded"],
                      "not_excluded": out["not_excluded"], "outside_the_count": out["outside_the_count"],
                      "sha256": __import__("hashlib").sha256(data.encode()).hexdigest()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
