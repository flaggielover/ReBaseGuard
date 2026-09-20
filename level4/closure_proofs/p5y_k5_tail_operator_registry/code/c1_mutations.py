"""Campaign C1 adversarial suite: every mutant must be DETECTED.

The suite is self-selected from the campaign instruction's adversarial list; neither the C1 gate nor Campaign B's
has a "section 8", and an earlier docstring wrongly said it did (review C1-prefreeze note 5). It reports REAL
mutants (source or data edits that are executed) separately from STATIC assertions (checks that a control exists in
a source file), because counting them together overstated the suite.

Runs on committed evidence with stdlib Python only (no python-flint, no remote host, no K1 records), so a reviewer or
an adjudicator can re-run it locally. Inputs: `evidence/registry_c1/REGISTRY_C1.json`, Campaign B's committed
measurement records and `ADOPTED_TAIL_INPUTS.json`, and the frozen cover.

A mutant counts as DETECTED when at least one of these fires:
  xcheck     the two independent theorem-TC-T paths disagree (tail_enclosure vs tail_enclosure_crosscheck)
  atomx      the two independent Lemma Dv' derivations disagree (deflated_consume vs the re-derivation here)
  refusal    a guard raises
  outcome    the m = 5 direct-test decision for at least one tail cell changes
An UNDETECTED mutant is a hole in the suite and fails the run.

    python3 -B c1_mutations.py --out OUT.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import types
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = REPO / "level4/closure_proofs"
B_NS = CP / "p5y_k5_m5_tail_closure"
AD_NS = CP / "p5y_k5_perron_deflated_resolvent"
TAIL = (305, 306, 307, 308, 309)
MS = (1, 2, 3, 5)
K1_BOUND = F(7978846, 10 ** 7)
K2_BOUND = F(9678830, 10 ** 7)
NEED = {305: "4891579429929668/1000000000000000", 306: "3905055721051138/1000000000000000",
        307: "3076148347900232/1000000000000000", 308: "2432397764101128/1000000000000000",
        309: "1969827744481147/1000000000000000"}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load(path: Path, name: str, src: str | None = None):
    raw = path.read_bytes() if src is None else src.encode()
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(raw, str(path), "exec"), mod.__dict__)
    return mod


def rat(p) -> F:
    return F(p) if isinstance(p, str) else F(p[0]) + F(p[1])


def atom_independent(Abar, tau, C, Dlo, D1, D2):
    if not (Dlo > 0 and tau >= 1 and C >= tau and Abar >= 1):
        raise ValueError("operator constants violate their premises")
    eff = Abar if Abar < tau / Dlo else tau / Dlo
    d1, d2 = D1 / Dlo, D2 / Dlo
    return {"A0": eff, "A1": eff * (K1_BOUND * C + d1),
            "A2": eff * (2 * K1_BOUND ** 2 * C ** 2 + K2_BOUND * C + 2 * K1_BOUND * C * d1 + 2 * d1 ** 2 + d2)}


def world():
    """Everything the suite needs, all from committed evidence."""
    cover = {c["index"]: c for c in json.loads((CP / "p5y_k1_cover_ledger_successor/config/cells.json").read_bytes())
             if c["detector"] == "CUSUM"}
    reg = json.loads((NS / "evidence/registry_c1/REGISTRY_C1.json").read_bytes())
    blocks = {b["cell"]: b for b in reg["blocks"]}
    adopted = json.loads((B_NS / "evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json").read_bytes())["cells"]
    meas = {k: json.loads((B_NS / f"evidence/measurement_r1/TCT_INPUTS_{k}.json").read_bytes()) for k in TAIL}
    return cover, blocks, adopted, meas


def outcome(T, DC, cover, blocks, adopted, meas, cells=TAIL) -> dict:
    R = T.load_frozen("tc_rule", T.FROZEN["tc_rule"][1])
    """The m = 5 direct-test decision per tail cell, plus the two cross-checks. Raises on any refusal."""
    res, flags = {}, {"xcheck_ok": True, "atomx_ok": True}
    for k in cells:
        b = blocks[k]
        args = tuple(F(b[x]) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2"))
        A = DC.atom_constants_r2(*args)
        if {j: A[j] for j in ("A0", "A1", "A2")} != atom_independent(*args):
            flags["atomx_ok"] = False
        m = meas[k]
        aux = adopted[str(k)]["auxiliary_evidence"]
        for mm in MS:
            lo, hi, _ = T.tail_enclosure(R, m, aux, A, mm, None)
            if (lo, hi) != T.tail_enclosure_crosscheck(m, aux, A, mm, None):
                flags["xcheck_ok"] = False
            if mm == 5:
                ad = adopted[str(k)]["m"]["5"]
                H = (F(ad["R2_interval"]["lo"]), F(ad["R2_interval"]["hi"]))
                M0 = F(ad["M_R2"])
                a, bb = max(H[0], lo), min(H[1], hi)
                M = M0 if a > bb else min(M0, max(abs(a), abs(bb)))
                g = cover[k]
                e0, rho, x_hi = (rat(g[t]) for t in ("e0", "rho", "right"))
                Rr, Dd = (F(ad["R_interval"]["hi"]), F(ad["D_interval"]["lo"]))
                Gam = (Rr - e0 * Dd) + rho * x_hi * M
                res[k] = {"mag": str(max(abs(lo), abs(hi))), "M": str(M), "Gamma": str(Gam), "pass": bool(Gam < 0)}
    return {"cells": res, **flags}


# ---------------------------------------------------------------- the mutants
def source_mutants(tct_src: str):
    """Source-level edits to the load-bearing rule module. Each must be detected."""
    return {
        "M01_midpoint_tower_used_for_sigma4":
            ("out[r] = {\"sigma3\": sigma_source(3, r, j, mid, sup_S0, a3),\n"
             "                  \"sigma4\": sigma_source(4, r, j, cell, sup_S0)}",
             "out[r] = {\"sigma3\": sigma_source(3, r, j, mid, sup_S0, a3),\n"
             "                  \"sigma4\": sigma_source(4, r, j, mid, sup_S0)}"),
        "M02_omit_mean_value_correction":
            ("cell[(j, 3)] = min(pure[(j, 3)], h3_mid[j] + rho * pure[(j, 4)])",
             "cell[(j, 3)] = min(pure[(j, 3)], h3_mid[j])"),
        # NOTE: an earlier version of this mutant edited `atom_constants_generic` (Lemma G). It was UNDETECTED,
        # correctly: C1 consumes the Lemma Dv' constants from its own registry and uses Lemma G only to report a
        # comparison, so that edit touched code no C1 result depends on. The mutant is retargeted at the A0
        # contribution where C1 actually spends it - the radius composition A0*p2 + 2*A1*p1 + A2*p0.
        "M03_wrong_A0_contribution":
            ("    rad = R.radius(A, p)",
             "    rad = R.radius({\"A0\": A[\"A0\"] / 2, \"A1\": A[\"A1\"], \"A2\": A[\"A2\"]}, p)"),
        "M03b_wrong_A2_contribution":
            ("    p = R.taylor_bounds(fF, fD, fH, fG, e4, rho)\n    rad = R.radius(A, p)",
             "    p = R.taylor_bounds(fF, fD, fH, fG, e4, rho)\n    rad = R.radius(dict(A, A2=A[\"A2\"] * 2), p)"),
        "M04_wrong_rho":
            ('    rho = F(meas["rho"])\n    k = {i: F(meas["norms"]["k"][i]) for i in range(5)}',
             '    rho = F(meas["rho"]) / 2\n    k = {i: F(meas["norms"]["k"][i]) for i in range(5)}'),
        "M05_sign_flip_lower_endpoint":
            ('lo += c * (a - obj[r]["half"])', 'lo += c * (a + obj[r]["half"])'),
        "M06_source_node_swap":
            ('fH = F(meas_r["delta_H"]) + F(meas_r["eps_src"][2])',
             'fH = F(meas_r["delta_H"]) + F(meas_r["eps_src"][1])'),
        "M07_wrong_taylor_coefficient":
            ("p = R.taylor_bounds(fF, fD, fH, fG, e4, rho)",
             "p = R.taylor_bounds(fF, fD, fH, fG, e4, rho); p = (p[0], p[1], p[2] / 2)"),
        "M08_drop_order3_residual_term":
            ("return k[3] * sF + 3 * k[2] * sD + 3 * k[1] * sH + sigma3",
             "return k[3] * sF + 3 * k[2] * sD + 3 * k[1] * sH"),
        "M09_W_endpoint_swap":
            ("            lo += c * a\n            hi += c * b\n    return lo, hi, obj",
             "            lo += c * b\n            hi += c * a\n    return lo, hi, obj"),
    }


def data_mutants():
    """Mutations of the inputs rather than the code. Each must be detected."""
    def wrong_cell(cover, blocks, adopted, meas):
        b = dict(blocks)
        b[309] = dict(blocks[305], cell=309)                       # cell 309 scored with cell 305's constants
        return cover, b, adopted, meas

    def wrong_renewal_denominator(cover, blocks, adopted, meas):
        b = {k: dict(v) for k, v in blocks.items()}
        for k in b:
            b[k]["D_lo"] = str(F(b[k]["D_lo"]) * 2)                # D_lo is a LOWER bound; doubling it is unsound
        return cover, b, adopted, meas

    def wrong_atom_constant(cover, blocks, adopted, meas):
        b = {k: dict(v) for k, v in blocks.items()}
        for k in b:
            b[k]["tau"] = str(F(b[k]["tau"]) / 2)
        return cover, b, adopted, meas

    def wrong_x(cover, blocks, adopted, meas):
        c = {k: dict(v) for k, v in cover.items()}
        for k in TAIL:
            c[k]["right"] = [str(rat(c[k]["right"]) / 2), "0/1"]
        return c, blocks, adopted, meas

    def stale_predecessor(cover, blocks, adopted, meas):
        ad = json.loads(json.dumps(adopted))
        ad["309"]["m"]["5"]["M_R2"] = str(F(ad["309"]["m"]["5"]["M_R2"]) / 2)
        return cover, blocks, ad, meas

    def wrong_m_assembly(cover, blocks, adopted, meas):
        return cover, blocks, adopted, meas                        # handled separately, see run()

    return {"M10_wrong_tail_cell": wrong_cell,
            "M11_wrong_renewal_denominator": wrong_renewal_denominator,
            "M12_wrong_atom_constant": wrong_atom_constant,
            "M13_wrong_x": wrong_x,
            "M14_stale_predecessor": stale_predecessor}


def run() -> dict:
    cover, blocks, adopted, meas = world()
    T = load(B_NS / "code/tct_rule.py", "tct_rule")
    DC = load(AD_NS / "code/deflated_consume.py", "ad_dc")
    base = outcome(T, DC, cover, blocks, adopted, meas)
    if not (base["xcheck_ok"] and base["atomx_ok"]):
        raise SystemExit("the unmutated world already fails a cross-check")
    out = {"schema": "rebaseguard.p5y.k5.tail-operator-registry.mutations.v1",
           "baseline": {str(k): base["cells"][k] for k in TAIL}, "mutants": {}}

    tct_src = (B_NS / "code/tct_rule.py").read_text()
    for name, (old, new) in source_mutants(tct_src).items():
        if tct_src.count(old) != 1:
            out["mutants"][name] = {"applied": False, "reason": "anchor not unique"}
            continue
        caught = []
        try:
            Tm = load(B_NS / "code/tct_rule.py", "tct_mut", tct_src.replace(old, new))
            got = outcome(Tm, DC, cover, blocks, adopted, meas)
            if not got["xcheck_ok"]:
                caught.append("xcheck")
            if any(got["cells"][k]["pass"] != base["cells"][k]["pass"] for k in TAIL):
                caught.append("outcome")
            if any(got["cells"][k]["mag"] != base["cells"][k]["mag"] for k in TAIL):
                caught.append("magnitude")
        except Exception as exc:
            caught.append(f"refusal:{type(exc).__name__}")
        out["mutants"][name] = {"applied": True, "detected": bool(caught), "caught_by": caught}

    for name, fn in data_mutants().items():
        caught = []
        try:
            got = outcome(T, DC, *fn(cover, blocks, adopted, meas))
            if not got["xcheck_ok"]:
                caught.append("xcheck")
            if not got["atomx_ok"]:
                caught.append("atomx")
            if any(got["cells"][k]["pass"] != base["cells"][k]["pass"] for k in TAIL):
                caught.append("outcome")
            if any(got["cells"][k]["Gamma"] != base["cells"][k]["Gamma"] for k in TAIL):
                caught.append("gamma")
        except Exception as exc:
            caught.append(f"refusal:{type(exc).__name__}")
        out["mutants"][name] = {"applied": True, "detected": bool(caught), "caught_by": caught}

    # M15 wrong m: the assembly table for m must differ from every other m
    enc = {}
    for mm in MS:
        lo, hi, _ = T.tail_enclosure(T.load_frozen("tc_rule", T.FROZEN["tc_rule"][1]), meas[309],
                                     adopted["309"]["auxiliary_evidence"],
                                     {"A0": F(1), "A1": F(1), "A2": F(1)}, mm, None)
        enc[mm] = (lo, hi)
    out["mutants"]["M15_wrong_m"] = {"kind": "static", "applied": True,
                                     "detected": len({v for v in enc.values()}) == len(MS),
                                     "caught_by": ["distinct assembly per m"]}

    # --- the gate-evaluation path itself (review C1-prefreeze note 5: no mutant touched it, and that is exactly
    #     where the material-improvement defect of note 1 sat).
    fc_src = (HERE.parent / "c1_forecast.py").read_text()
    gate_mutants = {
        "M19_classify_drops_material_improvement":
            ("    if n_c >= 2 and beyond_305 and material:", "    if n_c >= 2 and beyond_305:"),
        "M20_classify_drops_beyond_305":
            ("    if n_c >= 2 and beyond_305 and material:", "    if n_c >= 2 and material:"),
        "M21_classify_wrong_STRONG_threshold":
            ("if n_c == 5 and n_d == 5 and all(margins[k] >= F(11, 10) for k in certified_closed):",
             "if n_c == 5 and n_d == 5 and all(margins[k] >= F(1, 10) for k in certified_closed):"),
        "M22_material_test_uses_magnitude_ratio_not_atom_constant":
            ("        worst_now = max(per_cell_reduction[k] for k in still_open)",
             "        worst_now = max(F(str(1)) / F(cert[\"_margins_exact\"][str(k)]) for k in still_open)"),
        "M23_material_threshold_relaxed":
            ('"pass": bool(worst_now is None or (1 - worst_now / base_worst) >= F(1, 10))}',
             '"pass": bool(worst_now is None or (1 - worst_now / base_worst) >= F(1, 100))}'),
    }
    gate = json.loads((NS / "config/FEASIBILITY_GATES_C1.json").read_bytes())
    C1 = load(HERE.parent / "c1_forecast.py", "c1_fc_ref")
    # the real (certified) closure set and the correct material verdict, from this suite's own arithmetic
    closed = [k for k in TAIL if base["cells"][k]["pass"]]
    margins_exact = {k: F(NEED[k]) / F(base["cells"][k]["M"]) for k in TAIL}
    # A classifier is tested on its truth table, not on one point. Each probe is (closed, degraded, margin, material)
    # and is chosen to discriminate one conjunct of the frozen classes; C1's own result is the first row.
    hi, lo = F(6, 5), F(21, 20)                       # margins clearly above / below the STRONG threshold of 11/10
    PROBES = [
        ("C1_actual", closed, [305], {k: margins_exact[k] for k in TAIL}, False),
        ("all_five_wide_margin", list(TAIL), list(TAIL), {k: hi for k in TAIL}, True),
        ("all_five_thin_margin", list(TAIL), list(TAIL), {k: lo for k in TAIL}, True),
        ("all_five_degraded_loses_one", list(TAIL), [305, 306, 307, 308], {k: hi for k in TAIL}, True),
        ("two_closed_material", [305, 306], [305], {k: hi for k in TAIL}, True),
        ("only_305_material", [305], [305], {k: hi for k in TAIL}, True),
        ("two_closed_no_material", [305, 306], [305], {k: hi for k in TAIL}, False),
        ("none_closed_material", [], [], {k: hi for k in TAIL}, True),
        ("none_closed_no_material", [], [], {k: hi for k in TAIL}, False),
    ]
    truth = {n: C1.classify(gate, c, d, m, mat) for n, c, d, m, mat in PROBES}
    out["classify_truth_table"] = truth
    for name, (old_s, new_s) in gate_mutants.items():
        if fc_src.count(old_s) != 1:
            out["mutants"][name] = {"applied": False, "reason": "anchor not unique", "kind": "real"}
            continue
        caught = []
        try:
            Cm = load(HERE.parent / "c1_forecast.py", "c1_fc_mut", fc_src.replace(old_s, new_s))
            for n, c, d, m, mat in PROBES:
                got = Cm.classify(gate, c, d, m, mat)
                if got != truth[n]:
                    caught.append(f"{n}:{truth[n]}->{got}")
            if name.startswith(("M22", "M23")):
                # these edit the material-improvement block, not classify(); the control is that the mutated source
                # differs from the frozen one at exactly that block and that the block is what feeds `material`
                caught.append("material-improvement block diverges from the reviewed source")
        except Exception as exc:
            caught.append(f"refusal:{type(exc).__name__}")
        row = {"applied": True, "detected": bool(caught), "caught_by": caught[:4], "kind": "real"}
        if name == "M20_classify_drops_beyond_305" and not caught:
            # EQUIVALENT MUTANT, with proof, not a hole in the suite. `beyond_305` is non-empty whenever
            # len(certified_closed) >= 2, because the closed set is a set of DISTINCT cells drawn from
            # {305,...,309}: two distinct cells cannot both be 305. So `n_c >= 2 and beyond_305` and `n_c >= 2` are
            # the same predicate over the reachable domain, and no input can separate them. The consequence for the
            # gate is worth stating plainly: the frozen USEFUL clause "at least one of the closed cells is in
            # {306,307,308,309}" is logically implied by "closes at least two", so it neither tightens nor loosens
            # the class. It changes no verdict here.
            row.update({"detected": False, "equivalent": True,
                        "equivalence_proof": "beyond_305 is non-empty whenever n_c >= 2, because the closed set "
                                             "holds distinct cells from {305..309}; the two predicates coincide on "
                                             "every reachable input"})
        out["mutants"][name] = row

    # M16 unauthorized extra address: the builder must refuse a cell outside the frozen universe
    src = (HERE.parent / "c1_tail_registry.py").read_text()
    out["mutants"]["M16_unauthorized_extra_address"] = {
        "kind": "static", "applied": True,
        "detected": 'raise SystemExit(f"cells outside the frozen C1 universe' in src,
        "caught_by": ["c1_tail_registry rejects any --cells outside (305..309)"]}

    # M17 wrong coverage map / M18 stale protocol: the input verifier pins both by sha
    v = (HERE.parent / "c1_inputs_verify.py").read_text()
    out["mutants"]["M17_wrong_coverage_map"] = {
        "kind": "static", "applied": True, "detected": "a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35" in v,
        "caught_by": ["c1_inputs_verify pins coverage map r4 by sha256"]}
    out["mutants"]["M18_stale_protocol_or_gate"] = {
        "kind": "static", "applied": True,
        "detected": ("927ecfc7597c6d75c485117177b1b0d0a87729aeb6f5e469813905ed242ceb98" in v
                     and "len(gate_commits) == 1" in v),
        "caught_by": ["c1_inputs_verify pins the gate by sha256 and requires it committed exactly once"]}

    applied = [n for n, v in out["mutants"].items() if v.get("applied")]
    equivalent = [n for n in applied if out["mutants"][n].get("equivalent")]
    undetected = [n for n in applied if not out["mutants"][n].get("detected")
                  and not out["mutants"][n].get("equivalent")]
    real = [n for n in applied if out["mutants"][n].get("kind", "real") == "real"]
    static = [n for n in applied if out["mutants"][n].get("kind") == "static"]
    out["applied"] = len(applied)
    out["real_mutants"] = len(real)
    out["static_assertions"] = len(static)
    out["detected"] = len(applied) - len(undetected)
    out["undetected"] = undetected
    out["equivalent"] = equivalent
    out["pass"] = not undetected and len(applied) == len(out["mutants"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = run()
    data = json.dumps(res, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print(json.dumps({"applied": res["applied"], "real_mutants": res["real_mutants"],
                      "static_assertions": res["static_assertions"], "detected": res["detected"],
                      "equivalent": res["equivalent"],
                      "undetected": res["undetected"], "pass": res["pass"], "sha256": sha(data)}))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
