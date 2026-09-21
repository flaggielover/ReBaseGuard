# Phase 1 — what exactly has to be certified, and over what

Producers: `code/c4_thresholds.py`, `code/c4_model_identity.py`. Evidence: `evidence/phase1/C4_THRESHOLDS.json`.
Every number below is emitted by one of those two programs; none is transcribed from C3's prose.

## 1. A0, and why it has a floor

`A0` is the order-0 atom constant of theorem AD. It is admissible on a cell only if

    |[(I - K_e)^{-1} f](a)|  <=  A0 ||f||     for every f in B(X) and every e in [e0 - rho, e0 + rho].

Lemma SM(d) (`p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md` §3) states that the supremum of the left side
over `||f|| <= 1` is **exactly** `tau_a(e) / D_e = E_a[tau](e)`, attained at `f = 1`. So admissibility is not merely
implied by, it is *equivalent to*

    A0 >= sup_{e in cell} E_a[tau](e)  =:  Lambda_k .

`Lambda_k` is a property of the process, not of any certificate. No certificate can go under it, now or ever.

The three supplies the frozen C3 mechanism admits all respect this, each for its own reason, and the point is worth
making separately for each because the exhaustion claim is only as wide as the family it covers:

| supply | A0 | why A0 >= Lambda_k |
|---|---|---|
| Lemma G | `C_upper` | the frozen K1 block bound is `>= sup_cell ||(I - K_e)^{-1}||`, and by positivity that operator norm is `sup_x E_x[tau] >= E_a[tau]` |
| Lemma Dv' | `min(Abar, tau/D_lo)` | `Abar >= sup_E E_a[tau]` is a hypothesis of Lemma Dv'; and `tau >= tau_a(e)`, `D_lo <= D_e` give `tau/D_lo >= E_a[tau](e)` |
| operator-mixed (C3) | `min` of the above over componentwise-best tuples | a minimum of valid upper bounds is a valid upper bound |

**The family that a lower bound on `E_a[tau]` exhausts is therefore: every atom-constant supply whose `A0` is a
valid uniform order-0 bound on the cell.** That is wider than the three supplies listed — it covers any future
certificate of the same shape — and narrower than "all deterministic routes", which is the distinction section 5
returns to.

## 2. E_a[tau]

`E_a[tau]` is the expected number of steps to alarm from the atom. `(I - K_e)^{-1} 1 (x) = E_x[tau]`; the frozen
CUSUM model that defines `tau` is read out of its pinned producer by `code/c4_model_identity.py`:

    state      the reachable closure X = {(p, m) in [0,5]^2 : p = 0 or m = 0 or p + m <= H - 2K = 4},
               T-invariant, containing the atom a = (0, 0);   H = 5,  K = 1/2,  C = H + K = 11/2
               (OPERATOR_AUDIT.md section 1. The ambient box [0, H]^2 is not the operator's state space, and
               Lemma SM(d) is a statement about B(X). Corrected after pre-result review, item D.1; nothing in
               theorem L changes, because its argument is pathwise and the chain started at a stays in X.)
    innovation z_i i.i.d. with density phi(. + e)
    update     s+ <- max(0, s+ + z - K),   s- <- max(0, s- - z - K)
    alarm      iff the unclipped update exceeds H in either coordinate
               (the producer's `ell, upper = m - C_CUSUM, C_CUSUM - p`, which is the same condition)

`cusum_layer1.py` is pinned at `efcc0f36632632577a24c4ddf1a7c2c3579d471cdba5a752dd72c708667cdc79`; the module
refuses if that sha changes or if any of the seven model-defining lines it matches has moved.

## 3. The quantifier, and the one place the campaign gets a discount

The requirement is `A0 >= Lambda_k`, a **supremum over the closed cell**. But to *exclude* a cell we need a lower
bound on `Lambda_k`, and

    Lambda_k = sup_{e in cell} E_a[tau](e)  >=  E_a[tau](e*)   for ANY single e* in the closed cell.

So a **pointwise** lower bound at one admissible drift suffices. This is the whole reason the campaign is cheap: it
never has to certify anything uniformly in `e`. The route of Phase 3 evaluates at `e = e_lo`, which is an endpoint
of the closed cell `[e0 - rho, e0 + rho]` and is the best point for that route because its bound is monotone
decreasing in `e` (`code/c4_lower_bound.py`, `monotonicity`, exercised on a 25-point ladder as well as argued from
`dE[V]/de = Phi(e - K) - Phi(-(e + K)) >= 0`).

`m` does not enter. `A0` is an operator constant of the cell; `m` selects which assembly consumes it. The exclusion
argument is run against the `m = 5` clause because that is the clause the four open cells fail.

## 4. The thresholds — per cell, and not interchangeable

`evidence/phase1/C4_THRESHOLDS.json`, bisected over 220 steps on the committed equations:

| cell | certified A0 | Gamma at A1 = A2 = 0 | closes? | critical A0 (outward) | A0 reduction needed |
|---|---|---|---|---|---|
| 306 | 6.004490785 | −0.079278659 | yes | — | — |
| 307 | 5.597995510 | −0.021906451 | yes | — | — |
| 308 | 5.218548599 | +0.039567846 | **no** | **4.375228833136** | ×1.19275 (16.16 %) |
| 309 | 4.867216117 | +0.092812423 | **no** | **3.214236022678** | ×1.51427 (33.96 %) |

Reproduces the C3 adjudicator's figures (Phase 0 checks 11 and 12 compare them mechanically).

**Does `E_a[tau] > 4.3752` discharge both required inequalities? No, and the question is the wrong way round.**
Three separate reasons, each sufficient:

1. **The thresholds belong to different cells.** Cell 308 is `e in [1.882413, 1.983910]`, cell 309 is
   `e in [1.983910, 2.092283]`. These are *adjacent closed* intervals sharing the endpoint `e = 1.983910`, not
   disjoint ones (corrected after pre-result review, item B), and the sharing has a consequence the campaign
   should state rather than leave implicit: the number certified for cell 309 is evaluated exactly at that shared
   endpoint, so it is simultaneously a valid lower bound on `Lambda_308` -- it is the same number that cell 308's
   evaluation at `e_hi` produces. A bound proved at a drift in cell 309's *interior* would say nothing about 308
   without a monotonicity argument in `e` that no committed artifact supplies.
2. **309's requirement is the weaker one**, `3.2142 < 4.3752`. A bound that happened to hold uniformly over the
   union at level `4.3752` would discharge both — but only because it would be far stronger than 309 needs, not
   because 308's threshold implies 309's.
3. **The implication cannot be exercised anyway**, because `4.3752` is not attainable at 308. Section 5.

Nothing downstream consumes a rounded threshold. The load-bearing test of Phase 6 is the direct evaluation
`Gamma(B, 0, 0) >= 0`, licensed by monotonicity: `Gamma` is nondecreasing in `A0` once the TC-T/K5-B intersection
is non-empty, and `[lo, hi]` only widens as `A0` grows, so non-emptiness at `B` persists for every `A0 >= B`. Both
facts are exercised on a 21-point ladder per cell (`monotone` in the evidence file), not asserted.

## 5. What is and is not in prospect, per cell

* **306 and 307: `A0` is not the blocker.** Both close at `A1 = A2 = 0` with `A0` exactly as certified, so no lower
  bound on `E_a[tau]`, however strong, can exclude them. 306 is blocked by the inherited adoption floor; 307 needs
  `A1`/`A2`, not `A0`. The producer records this as `critical_A0: null` with the reason, rather than emitting a
  meaningless threshold.
* **308: the threshold is out of reach.** Two independent committed float diagnostics
  (`evidence/phase3/C4_ROUTES.json`, agreeing to 5e-7) put `E_a[tau]` at cell midpoints at 4.4445 (307) and 4.1743
  (308); cell 308's `Lambda` is the value at their shared boundary `e = 1.882413`, which interpolates to about
  4.315 — **below** the 4.375229 the exclusion needs. These are candidate values, not bounds, and nothing in the
  gate or the certificate depends on them; but they say plainly that no lower-bound route can discharge 308.

  This has an exact restatement that needs no diagnostic at all: **a certified upper bound on `Lambda_308` below
  4.375229 would itself be an admissible `A0` that closes cell 308 at `A1 = A2 = 0`.** So "308 cannot be excluded"
  and "308 can be closed under the knockout" are the same statement. The two possibilities for 308 are exhaustive
  and one of them is progress.
* **309: in prospect, with room.** The threshold is 3.214236; the diagnostics put the truth near 3.92 at the
  midpoint and higher at `e_lo`. Phase 3 has to find a rigorous bound somewhere in between.
