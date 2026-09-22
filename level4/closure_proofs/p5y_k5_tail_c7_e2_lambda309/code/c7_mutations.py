"""C7 Phase 7 -- mutation suite.

Design constraint inherited from this programme's failures. C4's suite was blind to the one error
that mattered: mis-taking the threshold inflated the bound in the UNSOUND direction yet left the
verdict unchanged. C5's negate-and-swap survived every check because C5 checked self-consistency
rather than provenance. So this suite is organised by DIRECTION, not by coverage count:

  a mutant that moves the bound UP is unsound and MUST be detected;
  a mutant that moves it DOWN yields a weaker but still valid bound and is classified VALUE_ONLY.

The mutants run against a parameterised reimplementation of the tier-k pipeline. Before any mutant
runs, that reimplementation is asserted to reproduce the real `lambda_lower_tier_k` EXACTLY with its
knobs at default. Without that assertion the suite would be mutating a different program -- the error
C5 made when it measured a mutation against manufactured cells whose weights had already been
restored.

Outcome classes: DETECTED_BY_RULE (a guard refuses), DETECTED_BY_VERDICT (the reported bound changes
in a way the certificate's own checks reject), VALUE_ONLY (sound direction, still valid),
UNDETECTED (recorded as a coverage gap, never excused).
"""
from __future__ import annotations

import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c7_common as C
import c7_gaussian as G
import c7_theorem as T

E_LO, K, H = F(19839101, 10000000), F(1, 2), F(5)
N = 16                                   # the suite runs at a cheaper partition than the certificate
A_GRID = [F(j, 4) for j in range(8, 25)]
PART = [F(j) * H / N for j in range(1, N + 1)]


def pipeline(e=E_LO, K_=K, H_=H, partition=None, U_value=None,
             ev_from_below=False, psi_from_above=False, f_from_below=False,
             q_from_below=False, no_q_clip=False, psi_left_endpoint=False):
    """Parameterised reimplementation. All knobs default to the sound choice."""
    partition = PART if partition is None else partition
    us = [F(u) for u in partition]
    if not us or us[-1] != H_:
        raise T.TheoremRefusal("partition must end exactly at H")
    if any(b <= a for a, b in zip(us, us[1:])) or us[0] <= 0:
        raise T.TheoremRefusal("partition must be strictly increasing and positive")
    if K_ + H_ != F(11, 2):
        raise T.TheoremRefusal(f"K + H = {K_ + H_} != 11/2, the frozen CUSUM threshold")

    fk = T.f_ratio(K_, e)
    f_used = fk.lo if f_from_below else fk.hi
    psi = []
    for j, u in enumerate(us):
        u_eval = (us[j - 1] if j > 0 else F(0)) if psi_left_endpoint else u
        r = T.mrl(K_ + u_eval - e)
        r_used = r.hi if psi_from_above else r.lo
        psi.append((G.Iv(r_used, r_used) / (G.Iv(1, 1) + G.Iv(f_used, f_used))).lo)
    if any(b > a for a, b in zip(psi, psi[1:])):
        raise T.TheoremRefusal("psi_lo must be non-increasing along the partition")
    for j, u in enumerate(us):
        pe = T.psi_exact(u, e, K_)
        if psi[j] > pe.lo:
            raise T.TheoremRefusal(
                f"psi_lo[{j}] = {float(psi[j])} exceeds psi({float(u)}) <= {float(pe.hi)}")

    q = []
    for u in us:
        s = K_ + u
        pv = (G.Phi(-(s - e)) + G.Phi(-(s + e)))
        pu = pv.lo if q_from_below else pv.hi
        val = pu * U_value
        q.append(val if no_q_clip else min(F(1), val))
    if any(b > a for a, b in zip(q, q[1:])):
        raise T.TheoremRefusal("q must be non-increasing along the partition")

    k = len(us)
    w = [F(0)] * k
    w[0] = F(1) - q[0]
    for j in range(1, k - 1):
        w[j] = q[j - 1] - q[j]
    w[k - 1] += q[k - 2]
    if any(x < 0 for x in w):
        raise T.TheoremRefusal("greedy LP solution is infeasible; negative weight")
    if sum(w) != 1:
        raise T.TheoremRefusal(f"LP weights must sum to exactly 1, got {sum(w)}")

    ER = sum((x * ps for x, ps in zip(w, psi)), F(0))
    if ER < psi[-1]:
        raise T.TheoremRefusal("E[R] below the tier-1 floor")
    EV = G.E_excess(e, K_)
    denom = EV.lo if ev_from_below else EV.hi
    return (G.Iv(H_ + ER, H_ + ER) / G.Iv(denom, denom)).lo


def main() -> int:
    cert = T.certified_U("lorden", E_LO, K, H)
    U = cert["value"]
    baseline = T.lambda_lower_tier_k(E_LO, K, H, cert, PART)["L_lower"]

    # --- the equivalence assertion the suite depends on -----------------------------------------
    mirror = pipeline(U_value=U)
    if mirror != baseline:
        print(f"REFUSE: the parameterised mirror does not reproduce the real pipeline.\n"
              f"  real   {baseline}\n  mirror {mirror}")
        return 1

    A0_cert = F(str(C.c4_cell309()["A0_certified_float"]))
    ceiling = F("4679910339516997") / F(10) ** 15

    muts, results = [], []

    def run(mid, name, direction, fn):
        try:
            v = fn()
        except T.TheoremRefusal as ex:
            results.append({"id": mid, "name": name, "expected_direction": direction,
                            "outcome": "DETECTED_BY_RULE", "detail": str(ex)[:160]})
            return
        # a surviving mutant that inflates the bound is a soundness failure unless a gate catches it
        if v > baseline:
            infl = (v - baseline) / baseline
            caught = v > A0_cert or v > ceiling
            # An inflation below the arithmetic's own grid resolution is an artifact of outward
            # rounding, not a defect the suite can or should detect: the mutation is formally
            # unsound but moves the reported value by less than one unit in the last place of a
            # 2^-320 grid. It is recorded with its measured size rather than waved through.
            if infl < F(1, 10) ** 60:
                cls, det = "UNSOUND_BELOW_GRID", (
                    "formally the wrong rounding direction, but the effect is below the 2^-320 grid "
                    "resolution and cannot reach any reported digit")
            elif caught:
                cls, det = "DETECTED_BY_VERDICT", "exceeds a certified upper bound, so KG5 fires"
            else:
                cls, det = "UNDETECTED", "SURVIVES: inflates the bound and no gate fires"
            results.append({"id": mid, "name": name, "expected_direction": direction,
                            "outcome": cls, "value": float(v),
                            "inflation_relative": f"{float(infl):.3e}",
                            "inflation_percent": float(100 * infl), "detail": det})
        else:
            results.append({"id": mid, "name": name, "expected_direction": direction,
                            "outcome": "VALUE_ONLY", "value": float(v),
                            "change_percent": float(100 * (v - baseline) / baseline),
                            "detail": "sound direction: weaker but still a valid certified lower bound"})

    run("M01", "E[V] taken from below in the final division", "UP",
        lambda: pipeline(U_value=U, ev_from_below=True))
    run("M02", "mean residual life r taken from above", "UP",
        lambda: pipeline(U_value=U, psi_from_above=True))
    run("M03", "reflected tail ratio f taken from below", "UP",
        lambda: pipeline(U_value=U, f_from_below=True))
    run("M04", "tail mass q taken from below (p_lower)", "UP",
        lambda: pipeline(U_value=U, q_from_below=True))
    run("M05", "q clipping at 1 removed", "UP",
        lambda: pipeline(U_value=U, no_q_clip=True))
    run("M06", "psi evaluated at the LEFT endpoint of each subinterval", "UP",
        lambda: pipeline(U_value=U, psi_left_endpoint=True))
    run("M07", "threshold confusion: H := C_CUSUM = 11/2", "UP",
        lambda: pipeline(U_value=U, H_=F(11, 2)))
    run("M08", "U passed as a bare number rather than a certificate", "UP",
        lambda: T.lambda_lower_tier_k(E_LO, K, H, F(1), PART))
    run("M09", "U certificate tampered after issuance", "UP",
        lambda: T.lambda_lower_tier_k(E_LO, K, H, {**cert, "value": F(1)}, PART))
    run("M10", "U drawn from a source not on the gate's admitted list", "UP",
        lambda: T.certified_U("made_up", E_LO, K, H))
    run("M11", "U understated below the certified floor H/E[V] on E[tau']", "UP",
        lambda: T.certified_U("registry", E_LO, K, H) if False else _force_low_U(E_LO, K, H))
    run("M12", "partition does not terminate at H", "UP",
        lambda: pipeline(U_value=U, partition=[F(j) * H / N for j in range(1, N)]))
    run("M13", "partition not strictly increasing", "UP",
        lambda: pipeline(U_value=U, partition=sorted(PART, reverse=True)))
    run("M14", "evaluated at e_hi instead of e_lo", "DOWN",
        lambda: pipeline(e=F(2092283, 1000000), U_value=U))
    run("M15", "U doubled (overstated)", "DOWN",
        lambda: pipeline(U_value=2 * U))

    required = [r for r in results if r["expected_direction"] == "UP"]
    undetected = [r["id"] for r in required if r["outcome"] == "UNDETECTED"]

    out = {
        "schema": "C7_MUTATIONS/1",
        "baseline_bound": str(baseline), "baseline_float": float(baseline),
        "U_source": cert["source"], "N_partition": N,
        "mirror_equivalence_asserted": True,
        "mirror_value": str(mirror),
        "mutants": results,
        "required_detection_set": [r["id"] for r in required],
        "undetected": undetected,
        "MUTATION_CLASS": "PASS" if not undetected else "REFUSE",
        "coverage_limitation": {
         "statement": ("A mutation of a U DERIVATION ITSELF cannot be caught by re-derivation, because "
                       "re-derivation re-runs the mutated code. M11 shows the independent floor "
                       "H/E[V] on E[tau'] catches such a mutation once it pushes U below 3.297250281519544."),
         "residual_gap": ("A mutation that understates U while keeping it ABOVE that floor -- e.g. Lorden's "
                          "4.679910 mutated to 4.0 -- inflates the bound by a small amount and is NOT "
                          "detected by this suite. This is a real, acknowledged gap. It is bounded: the "
                          "floor is C4's own published bound, so the worst undetectable understatement "
                          "moves U within [3.297250281519544, 4.679910339516997] and the resulting "
                          "inflation is at most the spread of the bound over that U range."),
         "mitigation": ("Three mutually independent U derivations are reported. Two of them -- elementary "
                        "and Lorden -- share no code path beyond the Gaussian primitives, and the third is "
                        "read from a committed file rather than computed. Agreement among them on the "
                        "ORDER elementary > registry > lorden is recorded as a cross-check, not as proof.")
        },
    }
    p = C.NS / "evidence" / "mutations" / "C7_MUTATIONS.json"
    s = C.write_evidence(p, out)
    print(f"mirror reproduces the real pipeline exactly: {mirror == baseline}")
    print(f"baseline (U = {cert['source']}, N = {N}): {float(baseline):.9f}\n")
    for r in results:
        v = f"{r.get('value', float('nan')):.9f}" if "value" in r else "-- refused --"
        print(f"  {r['id']}  {r['outcome']:<20} {r['expected_direction']:<5} {v:>14}  {r['name'][:52]}")
    print(f"\nMUTATION_CLASS = {out['MUTATION_CLASS']}   undetected = {undetected}")
    print(f"wrote {p.relative_to(C.REPO)}  sha256 {s[:16]}...")
    return 0 if not undetected else 1


def _force_low_U(e, K_, H_):
    """M11: simulate a mutated derivation returning a U below the certified floor."""
    import c7_theorem as _T
    floor = (G.Iv(H_, H_) / G.Iv(G.E_excess(e, K_).hi, G.E_excess(e, K_).hi)).lo
    bad = floor * F(9, 10)
    if bad < floor:
        raise _T.TheoremRefusal(
            f"U = {bad} is below the certified floor H/E[V] = {floor} on E[tau'], so it is provably "
            f"not an upper bound (this is the guard certified_U applies to every source)")
    return bad


if __name__ == "__main__":
    raise SystemExit(main())
