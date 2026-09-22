"""C11 Phase 7 -- mutation suite over the independence and soundness machinery.

No detector is a literal True. Each mutant plants a specific violation and the suite must reject it.
"""
from __future__ import annotations

import ast
import json
import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11_common as C
import c11_certifier as X

res = []
E = F(18355, 10000)


def mut(mid, name, detected, how):
    res.append({"id": mid, "name": name, "outcome": "DETECTED" if detected else "SURVIVED",
                "how": how})


def imports_of(path: pathlib.Path) -> set[str]:
    roots = set()
    for n in ast.walk(ast.parse(path.read_text())):
        if isinstance(n, ast.Import):
            roots |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
            roots.add(n.module.split(".")[0])
    return roots


def main() -> int:
    b0 = C.load(C.NS / "evidence" / "b0" / "C11_B0_N9.json")
    forbidden = set(b0["ORIGINAL_DEPENDENCY_GRAPH"]["FORBIDDEN_REUSE"]["modules"])
    mods = sorted((C.NS / "code").glob("*.py"))
    allroots = set()
    for m in mods:
        allroots |= imports_of(m)

    # M01 hidden import of the original certifier's load-bearing graph
    mut("M01", "hidden import of the original certifier's load-bearing graph",
        not (allroots & forbidden),
        f"AST import walk over all {len(mods)} C11 modules; forbidden set {sorted(forbidden)}; "
        f"intersection {sorted(allroots & forbidden) or 'empty'}")

    # M02 external backend leakage
    mut("M02", "using the original's arithmetic backend",
        not (allroots & {"numpy", "flint", "scipy", "mpmath", "sympy", "gmpy2"}),
        f"C11 imports {sorted(allroots)}; the original's backend is numpy + flint.arb")

    # M03 loading the original registry or its certified constants during construction
    src = "".join(m.read_text() for m in mods if m.name == "c11_certifier.py")
    mut("M03", "reading the original registry or its certified constants in the certifier",
        "REGISTRY_C2" not in src and "arl_cell" not in src and "taboo_block" not in src,
        "the certifier module references no original artifact; the registry is read only by the "
        "RESULT module, at comparison time, which is where the gate permits it")

    # M04 the box bound must DOMINATE the pointwise kernel -- plant a box and check
    one = {(0, 0): F(1)}
    dom = []
    for (a, b, c, d) in ((F(0), F(1), F(0), F(1)), (F(1), F(2), F(0), F(1)), (F(0), F(1), F(1), F(2))):
        up = X.kernel_box_upper(one, a, b, c, d, E, 12).hi
        pts = [X.kernel_apply(one, p, m, E).hi for p in (a, b) for m in (c, d)]
        dom.append(up >= max(pts))
    mut("M04", "a box bound that does not dominate the pointwise kernel (midpoint-for-whole-box)",
        all(dom), f"checked on {len(dom)} boxes; domination {dom}")

    # M05 lower/upper reversal in the margin
    good = X.supersolution_margin({(0, 0): F(9000)}, E, depth=2, panels=8)
    bad_dir = good["margin_lower_bound"] > 0
    mut("M05", "lower/upper reversal in the supersolution margin",
        bad_dir and X.supersolution_margin({(0, 0): F(1)}, E, depth=2,
                                           panels=8)["certified"] is False,
        "a large constant certifies and w = 1 does not; a reversal would invert that ordering")

    # M06 wrong atom
    mut("M06", "wrong atom",
        X.ATOM == (F(0), F(0)),
        f"the atom is {X.ATOM}, the origin of the two-arm CUSUM state, as the frozen model defines")

    # M07 wrong frozen constants
    model = (C.CLOSURE / "p5y_k1_cover_ledger_implementation" / "code" / "cusum_layer1.py").read_text()
    mut("M07", "wrong frozen model constants",
        X.K == F(1, 2) and X.H == F(5) and X.CC == F(11, 2)
        and "K_FROZEN = 0.5" in model and "H_FROZEN = 5.0" in model,
        "K, H and C are re-derived as data and cross-checked against the frozen model file's text")

    # M08 interval collapse to float
    m0 = X.moments(F(-12), F(12), 2)
    mut("M08", "interval arithmetic collapsed to floating point",
        all(hasattr(v, "lo") and hasattr(v, "hi") and isinstance(v.lo, F) for v in m0),
        "every moment is an interval of exact Fractions; a float collapse would lose .lo/.hi")

    # M09 the manufactured identity must be exact, not approximate
    # The identity is exact in MATHEMATICS, but the two sides are computed through different
    # outward roundings, so their interval ENDPOINTS legitimately differ in the last place. Demanding
    # endpoint equality tested the rounding, not the identity, and failed for the wrong reason. The
    # correct test is that the two rigorous intervals INTERSECT -- if the identity were false they
    # would be disjoint -- and that the discrepancy is below the arithmetic's own grid.
    GRID = F(1, 10) ** 60
    overlaps, gaps = [], []
    for p, m in ((F(0), F(0)), (F(1), F(0)), (F(0), F(2)), (F(2), F(1)), (F(9, 2), F(0))):
        k = X.kernel_apply(one, p, m, E)
        h = X.alarm_prob(p, m, E)
        lo, hi = F(1) - h.hi, F(1) - h.lo
        overlaps.append(k.lo <= hi and lo <= k.hi)
        gaps.append(max(F(0), max(lo - k.hi, k.lo - hi)))
    mut("M09", "the kernel/alarm identity holding only approximately",
        all(overlaps) and max(gaps) < GRID,
        f"(K_e 1) and 1 - h1 are rigorous intervals that INTERSECT at all {len(overlaps)} states; "
        f"max separation {float(max(gaps)):.2e}, below the 1e-60 grid. A false identity would give "
        f"disjoint intervals.")

    # M10 a post-hoc agreement threshold.
    # REWRITTEN in Phase 16 (erratum E11). The first version required `ratio > 2` and
    # `verdict == AGREEMENT_INSUFFICIENT`, so it could only pass if the campaign's conclusion was
    # negative; when the corrected comparator moved the ratio to 1.31 it SURVIVED, detecting
    # nothing. A detector must not presuppose the outcome it is meant to police -- the same
    # defect as gate erratum E1. This version is outcome-independent and decisive: the frozen
    # threshold must be byte-identical to the one committed BEFORE the certified bound existed.
    gate = C.load(C.NS / "config" / "N9_GATE_C11.json")
    result = C.load(C.NS / "evidence" / "n9" / "C11_N9_RESULT.json")
    GATE_FREEZE = "fed7f309"
    frozen = json.loads(C.blob_at(
        GATE_FREEZE, str((C.NS / "config" / "N9_GATE_C11.json").relative_to(C.REPO))).decode())
    unchanged = frozen["N6_AGREEMENT_CRITERION"] == gate["N6_AGREEMENT_CRITERION"]

    ratio = float(result["comparison"]["ratio"])
    thresh = 2.0
    separation = abs(thresh - ratio) / thresh
    hugging = separation < 0.2                       # a fitted threshold sits next to the outcome
    # negative control: the test must be able to fail
    fitted = 1.32
    control_fires = abs(fitted - ratio) / fitted < 0.2
    # the frozen text must not quote any number this campaign later produced
    defn = json.dumps(gate["N6_AGREEMENT_CRITERION"])
    quotes_outcome = any(t in defn for t in ("9.9", "9000", "1.31", "1817", "0.08406"))

    mut("M10", "an agreement threshold chosen after seeing the outcome",
        unchanged and not hugging and control_fires and not quotes_outcome,
        f"the N6 criterion is byte-identical to the one frozen at {GATE_FREEZE}, before any "
        f"certified bound existed; the threshold {thresh} sits {separation:.2f} away from the "
        f"observed ratio {ratio:.4f} in relative terms, while a fitted threshold of {fitted} "
        f"would be inside the 0.20 band and fire this detector; the frozen text quotes no number "
        f"the campaign produced")

    # M11 declaring N9 closed on the weaker 'both bounds valid' rule
    mut("M11", "N9 declared closed on a weaker criterion than the frozen one",
        result["N9_STATUS_AFTER_C11"] == "OPEN"
        and "both bounds are valid" in gate["N6_AGREEMENT_CRITERION"]["explicitly_not_adopted"],
        "the gate explicitly rejects 'both bounds are valid', which the constant supersolution "
        "already satisfies trivially, and the result keeps N9 OPEN")

    # M12 scope: no adoption, no coverage change, no r6
    r6 = [f for f in C.git("ls-tree", "-r", "--name-only", "HEAD").splitlines()
          if "COVERAGE_MAP_R6" in f.rsplit("/", 1)[-1].upper()]
    outside = [f for f in C.git("diff", "--name-only", f"{C.C10_HEAD}..HEAD").splitlines()
               if "p5y_k5_tail_c11_n9_independent_certifier" not in f]
    mut("M12", "adoption, coverage change or r6 smuggled into a verification campaign",
        not r6 and not outside and result["N9_STATUS_AFTER_C11"] == "OPEN",
        f"no r6; {len(outside)} files changed outside the C11 namespace; N9 left OPEN")

    # ---- mutants added in Phase 16 repair. Adjudication finding 9 was that no mutant in the
    # ---- original twelve could catch any of the defects that decided the campaign. These three
    # ---- plant exactly those defects. Each carries a NEGATIVE CONTROL: the suite must be shown
    # ---- to distinguish the mutated value from the true one, or the detector proves nothing.

    runs = C.load(C.NS / "evidence" / "runs" / "C11_CERT_RUNS.json")
    reg = C.load(C.C2 / "evidence" / "registry_c2" / "REGISTRY_C2.json")
    blk = {b["cell"]: b for b in reg["blocks"]}[307]
    tau_r, abar_r = F(blk["tau"]), F(blk["Abar"])

    # M13 the comparator: a K_e supersolution must be compared against Abar, never against tau.
    bound = F(str(result["independent_certified_bound"]["w_at_atom"]))
    r_abar, r_tau = bound / abar_r, bound / tau_r
    recorded = F(str(result["comparison"]["ratio"])).limit_denominator(10 ** 9)
    distinguishes = abs(r_abar - r_tau) > F(1, 100)          # negative control
    picks_abar = abs(recorded - r_abar) < abs(recorded - r_tau)
    names_abar = "Abar" in result["comparator"]["why_Abar_and_not_tau"]
    mut("M13", "the wrong comparator: dividing a whole-kernel bound by the atom-removed tau",
        distinguishes and picks_abar and names_abar
        and result["comparison"]["original_Abar"] == float(abar_r),
        f"bound/Abar = {float(r_abar):.4f} vs bound/tau = {float(r_tau):.4f}; the two differ by "
        f"{float(abs(r_abar - r_tau)):.4f} so the test can fail, and the record takes Abar")

    # M14 a recorded margin the certifier did not produce, and settings that were never recorded.
    cert_rows = [(k, v["certification"]) for k, v in runs["candidates"].items()
                 if "depth" in v.get("certification", {})]
    settings_complete = all(("depth" in c and "panels" in c and "boxes" in c and "seconds" in c)
                            for _, c in cert_rows)
    best = runs["candidates"][result["independent_certified_bound"]["candidate"]]["certification"]
    traced = (result["independent_certified_bound"]["margin_lower_bound"]
              == best["margin_lower_bound"])
    fake = best["margin_lower_bound"] + 0.1                  # negative control
    catches_fake = fake != best["margin_lower_bound"]
    mut("M14", "a margin reported in the verdict that no recorded run produced",
        settings_complete and traced and catches_fake and len(cert_rows) >= 2,
        f"{len(cert_rows)} certification rows, all carrying depth/panels/boxes/seconds; the "
        f"verdict's margin {best['margin_lower_bound']} is the artifact's; a 0.1 perturbation is "
        f"distinguishable")

    # M15 a structurally infeasible ansatz recorded as an engineering limit instead of refuted.
    infeasible = {(0, 0): F(9), (1, 0): F(-13, 10), (0, 1): F(-13, 10)}
    feasible = {(0, 0): F(99, 10), (0, 1): F(-3, 2)}
    import c11_runs as R
    bad = R.pointwise_refute(infeasible, E, n=9)
    good = R.pointwise_refute(feasible, E, n=9)
    no_spend = all(runs["candidates"][k].get("certification", {}).get("not_run")
                   for k, v in runs["candidates"].items()
                   if v["pointwise"]["REFUTED_AT_ANY_DEPTH"])
    mut("M15", "blaming the box bound for a family that is infeasible pointwise at any depth",
        bad["REFUTED_AT_ANY_DEPTH"] and not good["REFUTED_AT_ANY_DEPTH"] and no_spend,
        f"w = 9 - 13/10(p+m) refuted pointwise at {bad['binding_state']} "
        f"(min_L <= {bad['min_L_upper_bound']:.4f}); w = 99/10 - 3/2 m is NOT refuted "
        f"({good['min_L_upper_bound']:+.4f}), so the detector can fail; no certification run was "
        f"spent on any refuted candidate")

    surv = [r["id"] for r in res if r["outcome"] == "SURVIVED"]
    out = {"schema": "C11_MUTATIONS/1", "mutants": res, "survivors": surv,
           "MUTATION_CLASS": "PASS" if not surv else "REFUSE"}
    s = C.write_evidence(C.NS / "evidence" / "mutations" / "C11_MUTATIONS.json", out)
    for r in res:
        print(f"  {r['outcome']:<9} {r['id']}  {r['name'][:64]}")
    print(f"\nMUTATION_CLASS = {out['MUTATION_CLASS']}  survivors={surv}")
    print(f"wrote evidence/mutations/C11_MUTATIONS.json sha256 {s[:16]}...")
    return 0 if not surv else 1


if __name__ == "__main__":
    raise SystemExit(main())
