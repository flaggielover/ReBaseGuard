# Cell 308 — pruning theorems from committed facts (Stream A, Task 3)

Sanctioned location (`history/recon/`). Class PRUNING_FROM_COMMITTED. Every numeric input below is a committed value
or its exact reproduction in `C3_KNOCKOUT_RECONSTRUCTION.md` (R1–R4). No new supply, clause, evaluation point, route
factor or gain is introduced; no quantity of any new route appears. `LP/` = `level4/closure_proofs/`.

## 0. Objects and conventions

* **Cell.** CUSUM, m = 5, cell 308, closed drift interval [e_lo, e_hi] = [1882413/1000000, 19839101/10000000]
  (`LP/p5y_k1_cover_ledger_successor/config/cells.json`, CUSUM entries).
* **Frozen consumer (direct clause).** Theorem TC-T whole-cell enclosure of R″₅ with the zero order-3 candidate
  (`LP/p5y_k5_m5_tail_closure/code/tct_rule.py`, blob 98f6eee4) composed with the frozen K5-B direct clause
  (`LP/p5y_k5_tail_c2_closure/code/c2_d5_forecast.py::direct`, blob 18403dbe), at the frozen non-constant inputs
  (`TCT_INPUTS_308.json` sha256 386f4a77…, `ADOPTED_TAIL_INPUTS.json` 485fb125…, the cover). Closure ⟺ Γ < 0.
  This is floor r2's adoption quantity (`LP/p5y_k5_tail_overnight_research/graph/K5_TAIL_DEPENDENCY_GRAPH.md:15–21`).
* **C5-T clause.** Theorem C5-T (`LP/p5y_k5_tail_c5_exhaustion/code/c5_transport.py:63–87`,
  `phase_6/C5_SELECTED_MECHANISM.md:3–36`), the clause C5's adjudicator made authoritative for scientific
  statements; C8 inverts it as "pass iff M < M_needed_C5T, with the budget read from C5_FORECAST"
  (`LP/p5y_k5_tail_c8_operator_feasibility/code/c8_decision.py:1–5`), M_needed_C5T = 2.463911269745421 for 308
  (`C8_DECISION.json:133`).
* **Atom-constant supply.** A triple (A0, A1, A2) with A_j ≥ 0 that is admissible, i.e. a valid uniform bound on the
  closed cell (`LP/p5y_k5_tail_c4_exhaustion/phase_1/C4_TARGET_RECONSTRUCTION.md:8–16`).
* **Λ₃₀₈ := sup_{e ∈ cell} E_a[τ](e).** Lemma SM(d) (`LP/p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md:51`,
  §3 l.44–56): sup_{‖f‖≤1} |[(I − K_e)⁻¹f](a)| = τ_a/D_e = E_a[τ], attained at f = 1. Hence **every admissible
  supply has A0 ≥ Λ₃₀₈** (C4_TARGET_RECONSTRUCTION.md:12–18; for Lemma G, Lemma Dv′ and the operator-mixed supply
  separately, ibid. :23–27).
* **A0\*** := the exact rational root of A0 ↦ Γ(A0, 0, 0) under the direct clause (reconstruction R2.4, exact string
  in `C3_KNOCKOUT_RECONSTRUCTION.json` `coefficients_exact.A0_critical`; float 4.375228833135616; inside C4's
  committed bisection bracket, `C4_THRESHOLDS.json:44–46`; outward 4.375228833136, `C4_TARGET_RECONSTRUCTION.md:76`;
  C3 adjudicator 4.3752, `C3_ADJUDICATION.md:350`).
* **A0\*_T** := C8's committed C5-T A0 ceiling at A1 = A2 = 0, 4.442851487961334 (`C8_DECISION.json:124`; the lower
  end of a 70-step bisection from [0, 40] against a budget rationalised from the committed float M_needed_C5T,
  `c8_decision.py:50–63`; so a closing value, correct to float rendering, not a directed enclosure —
  cf. `EXCLUSION_308.md:38`).

## 1. Structural lemma (monotonicity) — certified

**Lemma P0.** Under either clause, Γ is non-decreasing in each of A0, A1, A2 ≥ 0 on the set where the TC-T/K5-B
intersection is non-empty, and that set is up-closed in each A_j.

*Proof.* A_j enters only through half_r = A0·p₂(r) + 2·A1·p₁(r) + A2·p₀(r) with p_j(r) ≥ 0 (the frozen
`tc_rule.radius`, `tc_rule.py:83–87`; Ĝ := 0 so ρ·|Ĝ(a)| = 0), and lo = C_lo − Σ_r (1/5)·half_r,
hi = C_hi + Σ_r (1/5)·half_r (reproduced exactly at seven points, R4.1). Raising any A_j widens [lo, hi]; a non-empty
intersection with the fixed R2 interval stays non-empty and its endpoints move outward. The direct clause uses
M = min(M_R2, max(|a|, |b|)) (`c2_d5_forecast.py:85–86`), non-decreasing; C5-T uses
P = max(max(−H_lo, 0)·w_R, max(H_hi, 0)·w_L) (`c5_transport.py:63–75`), non-decreasing; ρ·x_hi, w_R, w_L > 0. ∎
The intersection is non-empty already at A = 0 (R4.2 at P_ZERO; C4's committed ladder
`intersection_nonempty_from: 0.0`, `C4_THRESHOLDS.json:48–53`), hence for every A ≥ 0. This matches C4's committed
licence (C4_TARGET_RECONSTRUCTION.md:96–99) and the C4 adjudicator's "Γ is nondecreasing in all three"
(`C4_ADJUDICATION.md:170–171`).

## 2. Theorem P308-D (direct clause)

Let the consumer be the frozen TC-T + K5-B direct clause with the frozen non-constant inputs. Then:

**(D1) Exact knockout threshold.** For A1 = A2 = 0: Γ(A0, 0, 0) < 0 **iff** A0 < A0\*.
*Proof.* On 0 ≤ A0 ≤ A0\* the binding regime holds throughout (it holds at both ends, R4.2 at P_ZERO and P_CRIT,
and each regime inequality is monotone along the segment; `C3_KNOCKOUT_RECONSTRUCTION.md` §R4 "Scope"), so Γ is
affine there with slope ρ·x_hi·P̄2 > 0 and Γ(A0\*, 0, 0) = 0 exactly (R2.4a). For A0 ≥ A0\* use Lemma P0. ∎

**(D2) No (A1, A2) rescues A0 ≥ A0\*.** For all A1, A2 ≥ 0 and A0 ≥ A0\*: Γ(A0, A1, A2) ≥ Γ(A0, 0, 0) ≥ 0, so cell
308 does not close. (Lemma P0 and D1; this is the C3 adjudicator's "infeasible by any improvement of A1 and A2
whatsoever" (`C3_ADJUDICATION.md:353–354`) and the C4 adjudicator's "at A0 = 4.375229 it is impossible at any
(A1, A2)" (`C4_ADJUDICATION.md:187–188`), both reproduced: R2.3, R3.2.)

**(D3) Necessary condition on any admissible closing supply.** If an admissible supply closes 308, then
Λ₃₀₈ ≤ A0 < A0\*.

**Pruning consequences (CERTIFIED — exact reproduction plus Lemma P0; no Monte-Carlo used).**

* **P-D-a (A1/A2-only routes are dead).** Every committed supply has A0 ≥ A0\*: Lemma G 6.174137363908812,
  C1 5.590460453801663, S_I1 5.332021179343055, C3 mixed 5.218548598870686 (`C2_CRITICAL_RATIOS.json` supplies;
  `C3_FORECAST.json`). So no route that improves only A1 and/or A2 of any committed supply — including any
  first/second-order-only certificate (e.g. a score or likelihood-ratio representation of A1, A2 that keeps A0) —
  can close 308 under this consumer. Knockout value at the best committed A0: Γ(5.218548598870686, 0, 0) =
  +0.039567845828196446 (C4_THRESHOLDS.json:37; R2.3).
* **P-D-b (A0-only routes from the mixed (A1, A2) are dead).** With (A1, A2) held at the C3-mixed values
  (22.79374449569498, 230.3658154880664), or componentwise above them, the largest closing A0 is
  3.203078438436744 (`C8_ROUTES.json:218`, frozen clause, C8 phase 4), below the **certified** floor
  Λ₃₀₈ ≥ 3.512733596 (below). By D3 no admissible A0 closes 308 there. (C8's own statement: "A0 to its floor AND
  A1 … ≤ 16.190847", `C8_ROUTES.json:217`.)
* **P-D-c (a closing route must move A0 and (A1, A2) together, and A0 must end below A0\*).** Any closing route
  must certify an order-0 constant strictly below A0\* ≈ 4.375228833 — a ≥ ×1.19274872192929 reduction of the best
  committed A0 (R2.5) — **and** a first/second-order pair below the mixed values (P-D-b).

**What is certified about Λ₃₀₈, and what that decides.**

| fact | value | status | source |
|---|---|---|---|
| certified lower bound (route L, H/E[(\|z\| − K)⁺] at e_lo) | Λ₃₀₈ ≥ 3.512733596022926 | CERTIFIED | `C4_CERTIFICATE.json:79`; `C4_BOUND_PHASE3.json`; `phase_3/C4_CANDIDATE_ROUTES.md:52`; independent cross-check 3.5127332118947487 (`C4_MUTATIONS.json`) |
| Γ at the certified floor, A1 = A2 = 0 | −0.04046754262884166 (closes) | CERTIFIED (committed evaluation) | `C4_CERTIFICATE.json:61`; `C5_SENSITIVITY.json:16` |
| certified upper bound | Λ₃₀₈ ≤ 5.218548598870686 (= τ/D_lo of the mixed tuple, an admissible A0) | CERTIFIED | `C3_FORECAST.json`; `EXCLUSION_308.md:40` (F11) |
| no certified upper bound below A0\* | — | committed absence | `OPEN_NOTES_DISPOSITION_C4.md:33–36` (C4-N2) |

Since 3.512733596 < A0\* < 5.218548599, **D3 is undecided by certified facts**: the certified floor does not exclude
308 (C4's certified answer: "the bound is too weak", `C4_ADJUDICATION.md:175–181`), and no certified admissible A0
reaches below A0\*. The dichotomy is exact (C4-N2): a certified upper bound on Λ₃₀₈ below A0\* would itself be an
admissible A0 that closes 308 at A1 = A2 = 0 — which D2/P-D-b show is not a real supply.

**What is only EVIDENCED (uncertified Monte-Carlo and float diagnostics).**

| fact | value | status | source |
|---|---|---|---|
| E_a[τ](e_lo), 2·10⁶ paths (C4 adjudicator) | 4.30910 ± 0.00102 | EVIDENCED | `C4_ADJUDICATION.md:81` |
| E_a[τ](e_lo) (C4 pre-result reviewer) | 4.31108 ± 0.00102 | EVIDENCED | `REVIEW_C4_PRERESULT.md:191` |
| E_a[τ] at the 308 midpoint | 4.17398 ± 0.00097 (MC); 4.1743 (float diagnostics) | EVIDENCED | `C4_ADJUDICATION.md:82`; `C4_CANDIDATE_ROUTES.md:81–92` |
| Λ₃₀₈ = E_a[τ](e_lo) (the sup sits at the left endpoint) | Theorem M, reviewed ACCEPTED_WITH_CORRECTIONS | THEORY (reviewed, not frozen) | `K5_OVERNIGHT_ROUTE_REGISTRY.md:26`; `EXCLUSION_308.md:294–297` (M1) |

On that evidence Λ₃₀₈ lies about 65 standard errors **below** A0\* (`C4_ADJUDICATION.md:176–178`; gap 0.066), so D3's
necessary condition is (evidentially) satisfiable by a sufficiently sharp order-0 certificate, and no lower-bound
route can ever prove the exclusion X308 (C4 §4; `ROUTE_AUDIT_R1.md:592`, X308 REJECT). But the evidenced truth also
prices the remaining requirement: at A0 = 4.311 closing requires the C3-mixed (A1, A2) to be divided uniformly by
**s\* = 18.2496** (exact reproduction R3.1; `OPEN_NOTES_DISPOSITION_C4.md:52`), and s\*(A0) =
ρ·x_hi·(2·A1·P̄1 + A2·P̄0) / −(G0 + ρ·x_hi·A0·P̄2) is increasing in A0 on [0, A0\*) and diverges at A0\*. So:

* CERTIFIED (conditional): **every** admissible supply whose A0 ≥ 4.311 needs a uniform (A1, A2) divisor ≥ 18.2496
  relative to the C3-mixed pair; every supply with A0 ≥ A0\* cannot close at all.
* EVIDENCED only: that every admissible A0 is ≥ ≈ 4.31 (the MC values straddle 4.311: 4.30910 below, 4.31108 above).
  The 18.2496 figure is exact **at** A0 = 4.311; its relevance to the true Λ₃₀₈ is Monte-Carlo.
* Caveat carried from C3 (`C3_ADJUDICATION.md:340–344`): a uniform divisor is a proxy for the feasible set; the exact
  feasible set at fixed A0 is the half-plane 2·A1·P̄1 + A2·P̄0 < −(G0 + ρ·x_hi·A0·P̄2)/(ρ·x_hi) (coefficients only in
  `C3_KNOCKOUT_RECONSTRUCTION.json`). No point of it is evaluated here.
* Not established by any committed certified fact: whether the idealised proportional family "eff → Λ₃₀₈" (Lemma
  Dv′: A0, A1, A2 all ∝ eff) closes 308. Committed: "eff at the floor closes 308 under both the sealed frozen clause
  and the C5-T clause" (`REVIEW_C8_PREPUBLICATION.md:245–248`) — at the *floor*, which is not known to be attainable.
  The coordinator's contrary inference at the Monte-Carlo level (disclosure I-b) is evidenced, not certified.

## 3. Theorem P308-T (C5-T clause)

Same setting, with the C5-T clause in place of the direct clause.

**(T1)** For A1 = A2 = 0, 308 closes under C5-T iff A0 < A0\*_T = 4.442851487961334 (C8's committed ceiling,
`C8_DECISION.json:124`; monotone by Lemma P0; the value is a bisection closing value, see §0).
**(T2)** For all A1, A2 ≥ 0 and A0 ≥ A0\*_T, 308 does not close under C5-T (Lemma P0).
**(T3)** An admissible closing supply under C5-T needs Λ₃₀₈ ≤ A0 < A0\*_T.

**Pruning consequences under C5-T.**

* **P-T-a (A1/A2-only routes are dead) — CERTIFIED.** Every committed supply's A0 (≥ 5.218548598870686) exceeds
  A0\*_T; C8's committed inversion agrees (`max_admissible_A1: null`, `max_admissible_A2: null`,
  `C8_DECISION.json:137–138`).
* **P-T-b (A0-only routes from the mixed (A1, A2) are dead) — CERTIFIED.** With (A1, A2) at the mixed values the
  largest closing A0 is 3.270701093262461 (`C8_DECISION.json:136`) < certified floor 3.512733596022926
  (`C8_DECISION.json:131`).
* **P-T-c — CERTIFIED (conditional on the floor, not on the truth).** At A0 = the certified floor and A2 at the mixed
  value, C5-T closure needs A1 ≤ 17.632791191529485 (from 22.79374449569498; C8's "1.2927x",
  `C8_DECISION.json:125`, `:135`). This is the most favourable certified-compatible corner; the true Λ₃₀₈ is not
  known to be that low.
* **Undecided by certified facts:** 3.512733596 < A0\*_T < 5.218548599 (C8 verdict `FEASIBLE`,
  `C8_DECISION.json:139`, i.e. "not refuted", not "achievable").
* **EVIDENCED only:** the MC values (4.30910 / 4.31108) lie below A0\*_T, so the C5-T necessary condition is
  evidentially satisfiable; `ROUTE_AUDIT_R1.md:592` rejects X308 under C5-T on this evidence ("MC says false").
  C8's C5-T uniform-eff factors (×1.438423 to close, ×1.798029 to adopt; `C8_ADOPTION.json:50` block, README.md:54)
  are committed; no factor of any new route is compared with them here.

## 4. Scope (what these theorems do not say)

* They concern the **atom-constant family** at the frozen non-constant inputs and the two named clauses. They do not
  cover residual-specific (non-norm-only) order-0 bounds, any change to TC-T, to the K5-B clause, to the measurement
  inputs, to the cover (e.g. ρ halved), or real order-3 candidates (C4 `does_not_cover`, `C4_ADJUDICATION.md:
  202–208`; C5 oracle rows in the inventory, C5.4).
* They license neither "308 is closable" nor "308 is not closable" (C4 Condition 3, `C4_ADJUDICATION.md:534–537`;
  C4-N3). They say exactly: under these consumers, **A0 must be certified below A0\* (resp. A0\*_T) and, jointly,
  (A1, A2) must be certified below the committed mixed pair** — the first is certified-undecided and MC-favourable;
  the second's size at the MC value is ×18.2496 (uniform, direct clause), an exact number whose relevance is
  Monte-Carlo.
* Nothing here evaluates Γ at a new point; the only derived quantities (A0\*, s\*, P̄j, G0) are exact reproductions of
  committed figures, kept in `history/recon/` only.
