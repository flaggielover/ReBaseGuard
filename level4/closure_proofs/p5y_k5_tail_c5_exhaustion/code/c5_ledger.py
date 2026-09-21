"""Phases 3, 4 and 5: the route ledger. Every deterministic route investigated, kept or killed, with its reason.

Nothing is deleted. A killed route is evidence, and the kill reason is recorded in one of three kinds:

  MATH        the mathematics cannot deliver enough even under an oracle-perfect version of the route
  DATA        the mathematics could deliver, but the inputs it needs are not in the committed corpus
  NEW_REAL    the route would require a new scientific value at a previously unevaluated real address

Only MATH is a statement about the science. DATA and NEW_REAL are statements about this campaign's permissions and
corpus, and a route killed for either is a live future route, not a refuted one.

    python3 -B c5_ledger.py --sensitivity S.json --out LEDGER.json
"""
import argparse
import json
import sys
from pathlib import Path

ROUTES = [
    # ---------------------------------------------------------------- A. order-3 surrogate
    dict(id="A1", family="order-3 surrogate", mechanism="tighten the candidate sup norms sF, sD, sH feeding "
         "f_G = k3*sF + 3k2*sD + 3k1*sH + sigma3 and env4",
         inputs="the frozen K1 object candidates F_r, D_r, H_r as polynomials",
         inputs_exist=False, target="f_G and env4, jointly ~82% of the radius sum S",
         max_gain="oracle: sup F/D/H -> 0 closes 307, 308 and (by 0.00035) 309",
         closure_possible=True, exhaustion_provable=False, new_real_required=False,
         status="KILLED", kill_kind="DATA",
         kill_reason="the K1 object candidates are NOT in the committed corpus. TCT_INPUTS_*.json carries only "
                     "their sup VALUES; the payloads live in the external 90 MB K1 record store. The only "
                     "Chebyshev payloads committed under level4/closure_proofs are the OPERATOR taboo/arl "
                     "candidates, which are a different object. Verified by searching every committed .json for "
                     "'numerators' and checking which concern the tail cells."),
    dict(id="A2", family="order-3 surrogate", mechanism="replace the zero-candidate surrogate by a real order-3 "
         "candidate Ghat, so residual_G becomes delta_G instead of the triangle-inequality sum",
         inputs="real order-3 evaluations at the tail cells", inputs_exist=False,
         target="f_G", max_gain="oracle: f_G -> 0 closes all three open cells",
         closure_possible=True, exhaustion_provable=False, new_real_required=True,
         status="KILLED", kill_kind="NEW_REAL",
         kill_reason="this is the R-stage. Forbidden outright by the campaign's compute boundary."),
    dict(id="A3", family="order-3 surrogate", mechanism="exploit cancellation in the identity "
         "phi''' = S''' + 3K1*Hhat + 3K2*Dhat + K3*Fhat instead of the triangle inequality",
         inputs="the candidate polynomials AND the operators K1, K2, K3 applied to them", inputs_exist=False,
         target="f_G", max_gain="unknown; bounded above by the f_G -> 0 oracle",
         closure_possible=True, exhaustion_provable=False, new_real_required=False,
         status="KILLED", kill_kind="DATA",
         kill_reason="needs both the candidates (see A1) and kernel applications. python-flint is absent on this "
                     "host, so no kernel application can be certified here in any case."),
    dict(id="A4", family="order-3 surrogate", mechanism="reuse already-certified order-3 evidence "
         "(the first real probe, T-EXT, the GammaTilde point certificate)",
         inputs="committed order-3 artifacts", inputs_exist=True,
         target="f_G", max_gain="none at the tail",
         closure_possible=False, exhaustion_provable=False, new_real_required=False,
         status="KILLED", kill_kind="MATH",
         kill_reason="the one real order-3 probe that ran is at CUSUM cell 0, drift e ~ 0. The tail cells are at "
                     "e in [1.70, 2.09]. An order-3 value at e ~ 0 constrains nothing at e ~ 2 without a transport "
                     "argument across the whole drift range, and no certified such transport exists."),
    # ---------------------------------------------------------------- sigma towers
    dict(id="A5", family="order-3 surrogate", mechanism="tighten sigma3, the (P3') midpoint source tower",
         inputs="k, j, sup_S0, aux.candidate_suprema, aux.midpoint_eps -- all committed", inputs_exist=True,
         target="sigma3, 42-48% of f_G at r >= 1",
         max_gain="oracle: sigma3 -> 0 closes 307 only",
         closure_possible=False, exhaustion_provable=False, new_real_required=False,
         status="KILLED", kill_kind="MATH",
         kill_reason="sigma3 is ALREADY measurement-improved: sigma_source takes the min of the pure tower and the "
                     "adopted measured sup of S_r'''. At r = 3, 4 the measured value is 5-20x below the tower, so "
                     "the tower is not what binds. And the oracle sigma3 -> 0 does not close 308 or 309."),
    dict(id="A6", family="order-3 surrogate", mechanism="tighten sigma4, the (P3) whole-cell 4th-order envelope",
         inputs="an order-4 measurement of the source, i.e. sup ||S_r''''||", inputs_exist=False,
         target="sigma4, which reaches 235 at r = 4",
         max_gain="oracle: sigma4 -> 0 closes 307 only",
         closure_possible=False, exhaustion_provable=False, new_real_required=True,
         status="KILLED", kill_kind="MATH",
         kill_reason="killed on MATH before NEW_REAL matters: the oracle sigma4 -> 0 leaves 308 at +0.0273 and 309 "
                     "at +0.0725. The order-3 measured data already propagates into the order-4 tower (CL[(4,4)] = "
                     "99.5 against the pure 128.5, a 22.6% gain already taken), and no order-4 measurement exists."),
    # ---------------------------------------------------------------- B. rho
    dict(id="B1", family="rho", mechanism="refine the cover: narrower cells, smaller rho",
         inputs="new K1 records at new, finer cells", inputs_exist=False,
         target="rho, which enters both the Taylor transport and the penalty",
         max_gain="oracle: rho halved closes all three open cells",
         closure_possible=True, exhaustion_provable=False, new_real_required=True,
         status="KILLED", kill_kind="NEW_REAL",
         kill_reason="rho is the K1 cover cell half-width. Reducing it means certifying the objects on new, "
                     "narrower cells, which is a new K1 numerical cell at a previously unevaluated address. "
                     "Forbidden outright. This is the single largest lever found and it is a live FUTURE route."),
    dict(id="B2", family="rho", mechanism="split the K5-B clause over sub-intervals of the existing cell, "
         "transporting R and D from e0 to each sub-midpoint",
         inputs="certified R, D at sub-midpoints", inputs_exist=False,
         target="the effective transport half-width",
         max_gain="bounded by B1",
         closure_possible=False, exhaustion_provable=False, new_real_required=True,
         status="KILLED", kill_kind="NEW_REAL",
         kill_reason="R_interval and D_interval are certified AT THE MIDPOINT e0 only (cusum_layer2: delta_mid). "
                     "Applying the clause at a different sub-midpoint needs R and D there, and transporting them "
                     "costs exactly what the split saves, because the transport of R' needs the same R'' bound."),
    # ---------------------------------------------------------------- C/D. joint and direct
    dict(id="D1", family="direct K5-B", mechanism="exact-weight, sign-aware transport (theorem C5-T): replace the "
         "penalty rho*x_hi*M by max((-H_lo)^+ * rho*(x_hi - rho/2), (H_hi)^+ * rho*(x_lo + rho/2))",
         inputs="g(e0) enclosure and the whole-cell R'' enclosure -- both already certified", inputs_exist=True,
         target="the transport constant in the K5-B direct clause",
         max_gain="1.211% to 1.295% of the penalty; closes nothing",
         closure_possible=False, exhaustion_provable=True, new_real_required=False,
         status="SELECTED", kill_kind=None,
         kill_reason=None),
    dict(id="D2", family="direct K5-B", mechanism="sign-awareness alone, keeping the weight rho*x_hi",
         inputs="the signed whole-cell R'' enclosure", inputs_exist=True,
         target="the transport constant", max_gain="zero on these cells",
         closure_possible=False, exhaustion_provable=False, new_real_required=False,
         status="KILLED", kill_kind="MATH",
         kill_reason="max(|H_lo|, |H_hi|) equals max((H_hi)^+, (-H_lo)^+) identically, for a one-signed or a "
                     "zero-straddling enclosure alike. Sign-awareness pays only when combined with DIFFERENT "
                     "directional weights, which is what D1 supplies, and even then only when the POSITIVE end "
                     "dominates. On all four tail cells the negative end dominates."),
    dict(id="D3", family="direct K5-B", mechanism="second-order transport of g using g'(e0) = -e0 R''(e0)",
         inputs="a tight midpoint enclosure of R'' and a whole-cell bound on R'''", inputs_exist=False,
         target="the transport constant", max_gain="unknown",
         closure_possible=False, exhaustion_provable=False, new_real_required=True,
         status="KILLED", kill_kind="NEW_REAL",
         kill_reason="the second-order remainder needs R''', which is precisely the order-3 quantity the whole "
                     "programme lacks. Circular."),
    dict(id="D4", family="direct K5-B", mechanism="tighten g_hi = R.hi - e0*D.lo by exploiting correlation "
         "between the R and D enclosures",
         inputs="joint certified information about R and D", inputs_exist=False,
         target="g_hi, which is 59-60% of the closure deficit",
         max_gain="unknown", closure_possible=False, exhaustion_provable=False, new_real_required=True,
         status="KILLED", kill_kind="DATA",
         kill_reason="R_interval and D_interval are sealed independently certified intervals in the adopted K1 "
                     "record. No joint/correlation information is committed, and manufacturing it means "
                     "re-certifying the K1 objects."),
    # ---------------------------------------------------------------- atom constants
    dict(id="E1", family="atom constants", mechanism="tighten A0 below the C3 operator-mixed value",
         inputs="a new Arb operator certification (better tau, D_lo or Abar)", inputs_exist=False,
         target="A0, which carries 82% of the radius sum",
         max_gain="bounded by Lambda = sup_cell E_a[tau]: at the DIAGNOSTIC Lambda with A1 = A2 = 0, cell 307 "
                  "closes (-0.0602), cell 308 barely closes (-0.0030), cell 309 does NOT (+0.0468)",
         closure_possible=True, exhaustion_provable=True, new_real_required=False,
         status="KILLED", kill_kind="DATA",
         kill_reason="operator certification needs python-flint, which is absent on this host; the programme's "
                     "certifying workers are out of scope for this campaign. Live FUTURE route for 307 and 308, "
                     "and PROVABLY USELESS for 309 (C4 already excluded 309, and the oracle confirms it)."),
    dict(id="E2", family="atom constants", mechanism="certify a sharper LOWER bound on E_a[tau] than C4's "
         "ladder/Wald minorant, to strengthen the exclusion",
         inputs="committed evidence plus exact analysis", inputs_exist=True,
         target="the exclusion margin, not closure", max_gain="no verdict change",
         closure_possible=False, exhaustion_provable=False, new_real_required=False,
         status="KILLED", kill_kind="MATH",
         kill_reason="zero verdict value. 309 is already excluded by C4 and a better floor only widens a margin "
                     "that is already positive; 308 can never be excluded because the C4 adjudicator's Monte-Carlo "
                     "puts the truth (4.311) BELOW the threshold (4.375229). A sharper floor changes no cell."),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sensitivity", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sen = json.loads(Path(a.sensitivity).read_bytes())
    ko = {r["knob"]: r for r in sen["knockouts"]}

    # every MATH kill must be backed by a kill gate actually present in the sensitivity evidence
    backing = {
        "A4": None,
        "A5": "sigma3 -> 0",
        "A6": "sigma4 -> 0",
        "D2": None,
        "E2": None,
    }
    for rid, knob in backing.items():
        if knob and knob not in ko:
            raise SystemExit(f"route {rid} claims a MATH kill with no kill gate named {knob!r} in the evidence")

    by_status, by_kind = {}, {}
    for r in ROUTES:
        by_status.setdefault(r["status"], []).append(r["id"])
        if r["kill_kind"]:
            by_kind.setdefault(r["kill_kind"], []).append(r["id"])
    out = {"schema": "rebaseguard.p5y.k5.tail-c5.route-ledger.v1",
           "kill_kinds": {"MATH": "the mathematics cannot deliver even at oracle-perfect",
                          "DATA": "inputs are not in the committed corpus (a live future route)",
                          "NEW_REAL": "would need a new scientific value at an unevaluated real address"},
           "routes": ROUTES, "by_status": by_status, "by_kill_kind": by_kind,
           "kill_gate_backing": {k: (ko[v]["cells"] if v else "argued in the kill_reason")
                                 for k, v in backing.items()},
           "selected": [r["id"] for r in ROUTES if r["status"] == "SELECTED"],
           "future_routes_ranked": ["B1 (cover refinement at 309 - the largest lever)",
                                    "E1 (operator certification of A0 - closes 307, nearly closes 308)",
                                    "A1 (tighten the K1 candidate sup norms - needs the record store)",
                                    "A2 (the real order-3 R-stage - a separate governed campaign)"],
           "new_real_scientific_addresses_evaluated": 0,
           "guard": "REAL_SCIENTIFIC_COMPUTE = DENY"}
    Path(a.out).write_text(json.dumps(out, sort_keys=True, indent=1) + "\n")
    print(json.dumps({"routes": len(ROUTES), "by_status": by_status, "by_kill_kind": by_kind}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
