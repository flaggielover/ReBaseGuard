# Independent pre-freeze review — brief (theorem-TC successor, CUSUM K5 lower front)

You are a fresh-context reviewer. You did not write this code. Your verdict is one of READY_TO_FREEZE, PASS_WITH_NOTES,
NOT_READY. Load-bearing findings must be stated as such. Be adversarial: the goal is to find an unsound step, not to
confirm the design.

Repository: this worktree (branch `p5y-k5-lower-front-order3`, based on `p5y-postk1-frontier` @ `e89b33f2`, whose parent
`7cb01e38` is the adopted state). Namespace: `level4/closure_proofs/p5y_k5_lower_front_order3/`. Nothing outside it
may be modified.

## What the successor claims

The adopted state (coverage map r3) leaves CUSUM K5 cells open: m1 11–35, m2 11–41, m3 11–42, m5 11–44 (+ the m5 tail,
out of scope). Theorem K5-B (`../p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md`) passes a cell by the chain if μ_k (a lower
bound on R'' over the cell) keeps U_k < 0. Phase A (`phase_a/`) shows that H.lo ≥ 0 on cells 11..K_m is sufficient,
given γ_10 < 0 from the adopted chain. Theorem TC (`theorem/THEOREM_TC.md`) gives a whole-cell R''_m enclosure built
from a Taylor-in-e candidate F̃ = F̂ + tD̂ + t²Ĥ/2 + t³Ĝ/6 and the adopted atom-deflation constants (theorem AD,
`../p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md`, Lemma Dv'). The only new real objects are the order-3
midpoint candidates Ĝ_r (frozen order-3 producer) at 34 pre-registered cells.

## Read

`TC_SUCCESSOR_SPEC.md`, `theorem/THEOREM_TC.md`, `phase_a/LOWER_FRONT_BLOCKER_AUDIT.md`, `phase_b/ROUTE_COMPARISON.md`,
`config/FEASIBILITY_GATES_A.json` (frozen and published at e89b33f2 before any forecast), and the code:
`code/tc_rule.py` (the rule), `code/tc_crosscheck.py` (independent path), `code/tc_manufactured.py` (fixtures and 14
mutants), `code/tc_producer.py` (vultr producer, governance gate, identity gate), `code/tc_consume.py` (consumer),
`code/tc_run.py`, `code/tc_qualify.py`, `code/make_tc_protocol.py`. Frozen code it relies on (read as needed):
`../p5y_k5_cusum_order3_real_producer/code/{cusum_order3.py,rung3_residual.py}`,
`../p5y_k1_cusum_aux3_successor/code/{aux_certifier.py,aux_propagate.py}`,
`../p5y_k1_cover_ledger_implementation/code/{propagate.py,assembly.py,cusum_layer2.py}`,
`../p5y_k5_perron_deflated_resolvent/code/deflated_consume.py`, `../p5y_k5b_independent_countersignature/code/k5b_check.py`.
Manufactured-suite result from the dev run: `evidence/dev/MANUFACTURED_DEV.json` (if present).

## Check at least

1. **Theorem.** Is each premise P1–P4 of THEOREM_TC actually supplied by the frozen objects the producer reads? In
   particular: are δ_mid(F_r), δ_mid(dF_r), δ_mid(H_r) and δ_mid(G_r) residuals of exactly the equations whose
   Leibniz form gives φ⁽ʲ⁾(e0) (signs, coefficients, the operator derivatives K_i at e0)? Is the source-error term
   ε_mid(src(r,k)) the right node (k = 0..3, Sclosed vs S:r)? Is the Taylor step for φ, φ', φ'' with the fourth
   derivative envelope correct (factorials, powers, which terms carry t)? Is Env4 a valid bound of ‖φ⁗(e)‖ for every e
   in the cell (k_i valid on the whole cell? candidate suprema valid on X? σ4 valid?). Is the step from (I−K_e)E = φ to
   E'' = Rφ'' + 2(∂R)φ' + (∂²R)φ right, and do the adopted A0, A1, A2 bound exactly those three functionals at a for
   every e in the cell?
2. **Regularity.** Analyticity of e ↦ K_e, S_r(e) into B(X) as used; any hidden requirement (e.g. window e-dependence)?
3. **Enclosure and assembly.** centre ± (ρ|Ĝ(a)| + rad); frozen coefficients c(m); W enclosures from the frozen cellwise
   DAG; interval arithmetic outward and exact; intersection with the adopted H.
4. **Consumer.** Does the empty-TC composition really reproduce the adopted consumption (and is the replay gate strong
   enough)? Is the cell/geometry/record binding sufficient against stale-cell or wrong-m mapping? Is monotonicity
   (no regression) enforced?
5. **Producer.** Does the governance gate precede every computation in mode real? Does replay mode avoid computing any
   order-3 value of F (it uses a synthetic G := Ĥ only to exercise the code path)? Is the identity gate (recomputed
   adopted K1 quantities equal to the sealed record) strong enough and correctly implemented?
6. **Feasibility gate and temporal integrity.** Gates frozen before the forecast? Forecast inputs honest (measured vs
   estimated, CONSERVATIVE ×4)? Any certified or real TC value observed before the freeze? (None should exist.)
7. **Mutation/falsification coverage.** Do the fixtures make each bound term necessary (A0, A1, A2, ρf_G, centre
   motion, Env4, source node)? Is any unsound change to `tc_rule` NOT caught? Propose a concrete mutant if so.
8. **Runtime pins / provenance.** Is the pin list (collected from loaded modules) adequate? Anything executed but not
   pinned?

Write your report as `review/REVIEW_R1.md` in this namespace with a findings table (id, severity: BLOCKING / NOTE,
file:line, finding, required fix) and the verdict line. Do not modify any other file. Do not run any real CUSUM
computation. You may run the pure-Python parts locally (tc_rule, tc_crosscheck; the manufactured suite needs
python-flint, which is on the vultr worker only — you may skip it and read its dev result instead).
