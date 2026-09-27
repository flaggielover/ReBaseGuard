# EXCLUSION_308 — the cell-308 uniform-A0 exclusion question (Stream C2a)

Status:
* **Theorem M** (§c): **VALIDATED_NON_TARGET** after `reviews/REVIEW_THEOREM_M_R1.md` (ACCEPTED_WITH_CORRECTIONS;
  C1/C2/N3 applied).
* **X308** (§a): undecided, not executed; the draft protocol only.
* This stream performed no computation at any drift and computed no new quantity for cells 305-309.
All numbers below are quoted from committed files with file:line.

**S8 correction notice (2026-09-28, after the coordinator's rule S8).** The first version of this file combined
Theorem M (a new result of this stream) with committed tail-cell values, and estimated the outcome of X308:
* it used Theorem M to read the committed MC value at e_lo as Lambda_308 and compared it with A0*
  (old §b.1 "universal cap", §d verdict, §e items 2-3, classification "expected refutable");
* it used committed 306-309 MC and diagnostic values as validation evidence for Theorem M (old §c.10, §d row D3);
* it derived a new cell-308 floor from C7's committed 309 number and placed it next to A0* (old §b.1 entailment
  paragraph, §b.3, §d row D2 and verdict);
* it placed committed tail-cell factors (C4 Condition 3's reduction factor, C5-T's consumed-margin share) in its
  own reasoning (old §a.2, §e item 5).

All of these are removed below. Each place is marked "[S8-corrected]". Committed tail-cell numbers now appear only
in this §0 history table, with no route factor attached, and in comparisons of committed numbers with committed
numbers that the committed record itself makes. The outcome of X308 is **not estimated** anywhere in this file.

## 0. Sources and committed facts (HISTORY SECTION — no route factor is attached to any row)

Path prefix `LP/` = `level4/closure_proofs/`. Every row is a reading; no row was recomputed by this stream.

| id | fact (quoted or paraphrased tightly) | source |
|---|---|---|
| F1 | Frozen model: state set X = {(p,m) in [0,5]^2 : p=0 or m=0 or p+m <= H-2K = 4}; H=5, K=1/2, C=H+K=11/2; innovation z i.i.d. with density phi(.+e) (i.e. z = raw - e, raw ~ N(0,1)); update s+ <- max(0, s+ + z - K), s- <- max(0, s- - z - K); alarm iff the **unclipped** update exceeds H in either coordinate | `LP/p5y_k5_tail_c4_exhaustion/phase_1/C4_TARGET_RECONSTRUCTION.md:39-47` |
| F2 | Lemma SM(d): sup_{norm f <= 1} abs([(I-K_e)^{-1} f](a)) = tau_a/D_e = E_a[tau], attained at f = 1 | `LP/p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md:51` (proof :56) |
| F3 | A0 admissible on a cell iff abs([(I-K_e)^{-1}f](a)) <= A0 norm f for every f and **every e in the closed cell**; by SM(d) this is *equivalent to* A0 >= sup_{e in cell} E_a[tau](e) =: Lambda_k | `C4_TARGET_RECONSTRUCTION.md:8-18` |
| F4 | To *exclude*, a pointwise lower bound at one drift of the closed cell suffices: Lambda_k >= E_a[tau](e*) for any e* in the closed cell | `C4_TARGET_RECONSTRUCTION.md:52-63` |
| F5 | Cell 308 = [1882413/1000000, 19839101/10000000]; it shares e = 19839101/10000000 with cell 309 (adjacent closed intervals) | `cells.json:1` as tabulated in SCR/graph_C_inputs.md §1.4; `C4_TARGET_RECONSTRUCTION.md:84-90` |
| F6 | Certified floor Lambda_308 >= 3.512733596 (route L, H/E[(abs z - K)^+], at e_lo; monotone decreasing in e so e_lo is optimal *for this route*) | `LP/p5y_k5_tail_c4_exhaustion/phase_3/C4_CANDIDATE_ROUTES.md:52` (route def :25-45); `LP/p5y_k5_tail_c8_operator_feasibility/evidence/phase9/C8_DECISION.json:131` |
| F7 | Uncertified 2,000,000-path MC (C4 adjudicator): E_a[tau](1.8824130) = 4.30910 +- 0.00102; 308 midpoint 4.17398 +- 0.00097; E_a[tau](1.9839101) = 4.04731 +- 0.00092; 309 midpoint 3.92108 +- 0.00088 | `LP/p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md:76-83` |
| F8 | C4-committed float diagnostics of E_a[tau] at midpoints: 306 4.7299, 307 4.4445, 308 4.1743, 309 3.9208 (candidate values, not bounds) | `C4_CANDIDATE_ROUTES.md:81-92` |
| F9 | C5-T critical A0 ("ceiling") at A1=A2=0, cell 308: **4.442851487961** (float rendering; bisection value, not a directed enclosure) | `LP/p5y_k5_tail_c8_operator_feasibility/review/ADJUDICATION_C8.md:270`; `C8_DECISION.json:124` |
| F10 | Frozen-clause (C3/C4 TC-T/K5-B) critical A0 at 308: 4.375228833136 | `C4_TARGET_RECONSTRUCTION.md:76` |
| F11 | Certified admissible A0 at 308 (hence certified **upper** bounds on Lambda_308 by F3): C3 operator-mixed 5.218548599; Lemma G 6.174137363908812 | `C4_TARGET_RECONSTRUCTION.md:23-27, 76`; `TAIL_FORECAST_R2.json:53` via graph_C §5.3 |
| F12 | C4 Condition 2 (errata E4/E5: "the honest answer is that none can" and the Lemma-T citation may not be quoted as establishing anything); Condition 3 (at A0 = 4.311 closing 308 still needs an 18.2x reduction of (A1,A2); at A0 = 4.375229 impossible at any (A1,A2); "nothing licenses 'cell 308 is closable'") | `C4_ADJUDICATION.md:527-537` |
| F13 | C4-N2: C4 certifies no upper bound on Lambda below the thresholds; the dichotomy "a certified upper bound on Lambda_308 below 4.375229 would itself be an admissible A0 closing 308 under the knockout" | `LP/p5y_k5_tail_c4_exhaustion/OPEN_NOTES_DISPOSITION_C4.md:33-36`; `C4_TARGET_RECONSTRUCTION.md:113-115` |
| F14 | C7 E2 family, evaluated at e = 19839101/10000000: PRIMARY certified E_a[tau] >= 3.586306094; family analytic ceiling (H + Lorden upper bound on E[R]) / E[V] = 4.679910340 | `LP/p5y_k5_tail_c7_e2_lambda309/README.md:15, 109`; `evidence/phase1/C7_LEDGER.json:24-33` |
| F15 | X308 as registered: "Certified Lambda_308 floor above the ceiling", exclusion only, zero closure leverage, scientific risk VERY_HIGH, result-chasing risk LOW, r2 adoptability exclusion-only | `LP/p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md:450-459` |
| F16 | Floor r2: every operator constant (incl. Abar, kernel K_e) must be "a certified statement, uniform in e, on a domain that contains the cell's whole block. A scalar drift or a strict sub-interval never qualifies" | `LP/p5y_k5_tail_floor_r2/FLOOR_R2_SPECIFICATION.md:113`, context :112-118 |
| F17 | Monotonicity of the two-sided alarm time in e is recorded as unproved: "Pathwise coupling gives monotonicity of each arm separately ... not of tau = min(tau+, tau-)"; P5 records sup_e E[tau given e] = E[tau given 0] as open; the cover's M2 is one-sided only | `LP/p5x_global_nonlinear_dynamics/DEFECT_REGISTER.md:36-45`; `LP/p5_nonlinear_dynamics/LIMITATIONS.md:49-53`; `LP/p5x_global_nonlinear_dynamics/compute_optimization_r1/PROOF.md:93-110`; caveat for 308: `C4_TARGET_RECONSTRUCTION.md:88-90` and graph_C §5.3 |

Notation warning. C8 uses the symbol "Lambda" for the certified *floor* (e.g. `C8_DECISION.json:131`
`Lambda_floor_on_A0`). In this file Lambda_308 always means the **true** process quantity
sup_{e in cell 308} E_a[tau](e) of F3, and certified numbers are called floors (lower) or upper bounds.

## (a) The exclusion proposition — exact statement

### a.1 Objects

* `Lambda(e) := E_a[tau](e)` for the frozen chain F1 started at the atom a = (0,0); finite for every e (Lemma T;
  C7-U step 0). It is continuous, indeed real-analytic, in e (THEOREM_AD Lemma K, `THEOREM_AD.md:21-22`, used at :75).
* `E308 := [e_lo, e_hi] = [1882413/1000000, 19839101/10000000]` (F5), closed.
* `Lambda_308 := sup_{e in E308} Lambda(e)` (F3). By continuity on a compact interval the sup is attained.
* `Gamma(A0, A1, A2)` := the value of the **C5-T** clause for CUSUM cell 308 at m = 5 with the frozen measurement
  inputs (the clause ADJUDICATION_C8 re-derived, `ADJUDICATION_C8.md:262-275`). Not computed here. The committed
  licence used by every exclusion so far: Gamma is nondecreasing in each of A0, A1, A2 once the TC-T/K5-B intersection
  is non-empty, and the intersection only widens as A0 grows (`C4_TARGET_RECONSTRUCTION.md:96-99`;
  `C4_ADJUDICATION.md:109-115`, Condition 4 at :539-541). Closure is `Gamma < 0`; C4's exclusion test is
  `Gamma(B,0,0) >= 0` (`C4_ADJUDICATION.md:95-97`).
* `A0* := sup{A0 : Gamma(A0,0,0) < 0}`, the C5-T critical A0 at A1 = A2 = 0. Committed float rendering
  **4.442851487961** (F9). It is a bisection value, not a directed enclosure (see (b.4)).

### a.2 The proposition

> **X308.** `Gamma(Lambda_308, 0, 0) >= 0`; equivalently (by the licence) `Lambda_308 >= A0*`; equivalently
> **there exists e* in E308 with Lambda(e*) >= A0*.**

**Quantifier — sup, not inf.** Lemma SM(d) is a statement at one drift: the smallest admissible order-0 constant at
drift e is exactly Lambda(e) (F2). A *uniform* A0 must work at every e of the closed cell (F3, the "for every e"
at `C4_TARGET_RECONSTRUCTION.md:10`), so the smallest admissible uniform A0 is `sup_e Lambda(e)`. Hence:

* X308 is about **sup_{e in E308} Lambda(e)**. Its witness is **existential in e**: one drift where Lambda is at
  least A0* suffices, and a *certified lower bound at one drift* is a complete proof (F4).
* `inf_{e in E308} Lambda(e)` is not the relevant quantity. `inf > A0*` would be sufficient but is strictly stronger
  than needed; `inf <= A0*` proves nothing. A route that certified an e-uniform lower bound would be paying for the
  wrong quantifier.
* The frozen-clause version `X308_frozen: Lambda_308 >= 4.375228833136` (F10) is **implied by** X308, since
  4.375229 < 4.442851. It is not the relevant proposition: C5-T is the tighter accepted consumer, and an
  exclusion stated against the frozen clause could be voided by C5-T, as happened to part of C4's 309 exclusion
  margin (`LP/p5y_k5_tail_c7_e2_lambda309/README.md:21-24`; the committed figure is not repeated here, S8).
* Ties: at `Lambda_308 = A0*`, Gamma = 0 is not closure, so the tie counts as excluded. This is measure-zero in
  practice, but the acceptance rule of any protocol must say which side a tie falls on (it does: see the draft
  protocol, rule R-TIE).

### a.3 What X308 would establish if true

For every atom-constant supply (A0, A1, A2) whose A0 is a valid uniform order-0 bound on E308 (Lemma G, Lemma Dv' r2,
C3 operator-mixed, and any future certificate of the same shape, `C4_TARGET_RECONSTRUCTION.md:29-32`) and every
A1, A2 >= 0:

    A0 >= Lambda_308 >= A0*   ==>   Gamma(A0, A1, A2) >= Gamma(A0, 0, 0) >= Gamma(A0*, 0, 0) = 0   (licence; Gamma continuous in A0),

so no such supply closes cell 308 under the C5-T clause. Scope, transplanted verbatim from C4 Condition 1
(`C4_ADJUDICATION.md:521-523`): **the uniform-A0 atom-constant family, cell 308, m = 5, against the frozen
measurement inputs and the C5-T/K5-B consumer.** It removes one route family from one cell; it is not "308 is
unclosable"; it has **zero closure leverage** (F15) and changes no cell status. Any later consumer tightening
(raising A0*) or input change (e.g. sup-norm cuts, C4 Condition 1's "halving the candidate sup norms raises the
critical A0") can void it.

### a.4 What the negation establishes

> **not-X308.** `Lambda_308 < A0*`; equivalently `Lambda(e) < A0*` **for every** e in E308 (universal in e).

* It establishes that the A0-floor argument **cannot** exclude cell 308: every valid lower bound on Lambda at any
  point of the cell is <= Lambda_308 < A0*, so no lower-bound route whatever can prove X308 (the statement C4
  Condition 2 forbids quoting from uncertified evidence would then be a theorem).
* It establishes that the perfect-information supply `A0 = Lambda_308, A1 = A2 = 0` closes under the knockout. It
  does **not** establish closability: real A1, A2 are not zero; C4 Condition 3 / C4-N3 are binding ("nothing
  licenses 'cell 308 is closable'", F12).
* not-X308 is a true-or-false fact about the process whether or not anyone certifies it. To *use* it one needs a
  certified **upper** bound U on Lambda_308 with U < A0*, and by F3 such a U is itself an admissible uniform A0
  (the C4 dichotomy, F13). So certifying not-X308 is the same act as producing a new A0 supply for cell 308 — the
  root of the leakage analysis in the draft protocol.
* The truth value of X308 is fixed; only its certifiability is open. X308 and not-X308 are exhaustive and exclusive.

## (b) Refutation and proof certificates

X308 is existential in e; not-X308 is universal in e (a.2, a.4). The certificate shapes follow from that asymmetry,
and Theorem M (section (c)) changes only the refutation side.

### b.1 What would PROVE X308

A certified number L with `L <= Lambda(e*)` for **one** e* in E308, and a directed decision `L >= A0*` (b.4).
One drift always suffices (F4). By Theorem M the truth Lambda(e) is largest at e_lo, so e_lo maximises Lambda over the
cell, hence the cap on every lower-bound route; **for a given route, e_lo is optimal only if its slack does not grow
faster than Lambda decreases** (route L is monotone, so it is optimal there, as F6 says). *[Corrected per
REVIEW_THEOREM_M_R1 C1: the earlier text said "e* = e_lo is the optimal point for every route", an overstatement.]*

Families, reasoning from committed facts only:

| family | what caps it | committed cap at cell 308 | can it exceed A0* = 4.442851 in principle? |
|---|---|---|---|
| C4 route L, `H / E[(abs z - K)^+]` (ladder/Wald minorant) | parameter-free formula, decreasing in e (`C4_TARGET_RECONSTRUCTION.md:60-63`) | its value at e_lo, **3.512733596** (F6), is the family's maximum over the cell | **No** — rigorous, no MC needed |
| C4 R4, `1/D` from `D_mid` | recombination of committed artifacts | 1.051130 (`C4_CANDIDATE_ROUTES.md:18`) | **No** |
| C7 E2 / E2c overshoot LP, `(H + E[R]) / E[V]` | (i) analytic family ceiling `(H + Lorden upper bound on E[R]) / E[V]`; (ii) E[tau'] <= Lambda(e), tau >= tau' pathwise (`C7 README.md:115-118`) | **no committed ceiling at e_lo(308)** (computing it would be a forbidden in-band evaluation) | **Not excluded by any committed ceiling at cell 308** *[Corrected per REVIEW_THEOREM_M_R1 N3: the earlier row placed the committed family ceiling at a cell-309 drift next to A0*(308), a cross-cell comparison the committed record does not make; that value now appears only in the history table (F14).]* |
| C4-N1 R1 (invert Lemma T on a taboo candidate, `tau_a >= w(a)/(1 + sup_X g)`) and R5 (two-sided tau_a certificate) | designed, never run (`OPEN_NOTES_DISPOSITION_C4.md:27-32`) | no committed ceiling; sharp routes converge to the truth | **Not excluded**; capped only by the truth |

(Every entry in this table compares committed numbers with the committed A0*; no new route factor is involved. The
comparisons for route L and the E2 ceiling are the ones the task asked for, "from committed family-ceiling facts
only".)

Universal cap (definition, no theorem needed): every valid lower bound at any e in E308 is <= Lambda(e) <= Lambda_308.
So a lower-bound route can prove X308 only if X308 is true. **[S8-corrected]** The first version went on to combine
this cap, Theorem M and the committed MC to estimate that X308 is false. That estimate is withdrawn. The committed
record's own assessments of the proof direction are history. They are listed at `C4_ADJUDICATION.md:175-181` and
`ROUTE_AUDIT_R1.md:450-459` (X308 scientific risk VERY_HIGH) and are not re-derived, extended or combined with
anything here. C4 Condition 2 in any case forbids quoting them as established (F12).

**[S8-corrected]** The first version also derived, from C7's committed 309 bound at the shared endpoint, a new floor
statement for cell 308, and placed it next to A0*. That is withdrawn. This stream states no cell-308 floor other than
the committed one (F6).

### b.2 What would REFUTE X308

A certified U with `U >= Lambda_308 = sup_{e in E308} Lambda(e)` and a directed decision `U < A0*` (b.4).

**Supersolution certificate.** If W : X -> [1, infinity) is bounded, measurable and `W >= 1 + K_e W` on X, then
`E_x[tau](e) <= W(x)` for every x (Lemma T's induction with K_e in place of K-hat_e: K_e >= 0 and
sum_{j<n} K_e^j 1 <= W for every n, `THEOREM_AD.md:34-41`), in particular `Lambda(e) <= W(a)`.

**Does one drift suffice?**

* **Without Theorem M: no.** A W certified at a single drift e* bounds Lambda(e*) only, while not-X308 needs every
  e in E308. One would need either (alpha) one W with `W >= 1 + K_e W` for **all** e in E308 simultaneously (an
  interval-in-e kernel enclosure, the "for every e in E" form of Lemma T, `THEOREM_AD.md:34-38`), or (beta) a finite
  drift mesh with a W_j at each node plus a certified bound on abs(dLambda/de) between nodes — by Lemma Dv with f = 1
  that is `abs([dR 1](a)) <= A1`, itself a cell operator constant (`THEOREM_AD.md:63-72`).
* **With Theorem M: yes, exactly one drift, and it must be e_lo = 1882413/1000000 (exact rational).** W at e_lo with
  W(a) < A0* gives Lambda_308 = Lambda(e_lo) <= W(a) < A0* (M1, M4). A W at an interior point or at e_hi does **not**
  suffice: upper bounds transport only towards larger e. Several drifts are unnecessary.
* The inequality must hold on **all of X**, a continuum: verification needs outward-rounded interval arithmetic over a
  state partition with a certified state-modulus for W and for the kernel integral (as in the cover's Bellman upper
  bound and the taboo supersolution certifier). The *proposal* W may come from any heuristic generator — the sibling
  stream C2b's cell-independent strategy — because the proposal affects tightness only, never validity (the C7
  disclosure principle, `C7 README.md:120-126`).

**Completeness (both sides decide X308 in principle).** If not-X308 holds, a refuting W exists: u = E_.[tau](e_lo)
solves u = 1 + K u, and W = (1 + eta) u satisfies W = (1 + eta) + K W >= 1 + K W with W(a) = (1 + eta) Lambda_308 < A0*
for small eta > 0. If X308 holds strictly, the partial Neumann sums sum_{j<n} K_{e_lo}^j 1 (a) increase to
Lambda(e_lo) and eventually exceed any number below it. So X308 is decidable by certified computation unless
Lambda_308 = A0* exactly; what is open is only which side, and at what certification cost.

**Committed upper bounds do not refute.** The certified admissible A0 values 5.218548599 (C3) and 6.174137364
(Lemma G) are certified upper bounds on Lambda_308 (F11), both above A0*. The sentence "No certified upper bound on
Lambda_308 exists" (`ROUTE_AUDIT_R1.md:281`) is accurate only in the sense "none below the thresholds".

### b.3 Summary

| goal | quantifier | certificate | drifts needed | committed status |
|---|---|---|---|---|
| prove X308 | exists e | certified lower bound L >= A0* | 1 (any e in E308; e_lo maximises the cap Lambda, and is optimal for a given route only if that route's slack does not grow faster than Lambda decreases, per review C1) | best committed floor 3.512733596 [S8-corrected: entailed value withdrawn]; no family *shown* incapable except L and R4 |
| refute X308 | for all e | certified upper bound U < A0* | without Theorem M: whole-cell uniform W, or mesh + A1; with Theorem M: 1 (exactly e_lo) | best committed U: 5.218548599 |

### b.4 The comparison target is not certified

A0* is committed only as a float bisection value, 4.442851487961334 (`C8_DECISION.json:124`), not as a directed
enclosure. A certified verdict therefore needs, inside an authorized protocol, either (a) the C4 method: evaluate the
frozen C5-T clause on exact Fractions at the certified number with A1 = A2 = 0 and test the sign, as C4's gate did
("`exclude_if = lambda gam: gam >= 0`, applied to the **exact `Fraction`** Gamma", `C4_ADJUDICATION.md:95-99`); or (b)
a pre-registered exact bisection giving [A0*_lo, A0*_hi] and the rules `L >= A0*_hi` (prove) / `U < A0*_lo` (refute).
Both are **Gamma evaluations at a target cell**. For a refutation, (a) is literally a knockout-closure value
Gamma(U, 0, 0) < 0 at cell 308. Neither may be done outside an authorized exactly-once protocol, and the committed
float may not serve as a certified comparator.

## (c) General theorems: monotonicity of Lambda(e)

**Result: PROVED; VALIDATED_NON_TARGET after REVIEW_THEOREM_M_R1 (ACCEPTED_WITH_CORRECTIONS; C1/C2/N3 applied)
— Lambda(e) = E_a[tau](e) is even in e and
nonincreasing on [0, infinity); in fact P_e(tau > n) is nonincreasing in abs(e) for every n.** The proof does
*not* use a pathwise coupling (which fails, as F17 records); it uses the V-mask form of the two-sided CUSUM from the
atom and Anderson's theorem on symmetric unimodal densities. It is stated for the **atom start**, and by review C2
it holds verbatim from every diagonal start p0 = m0. It says nothing about sup_x E_x[tau].

### c.1 Why the obvious coupling fails (recorded, not used)

Couple z_i = r_i - e with common r_i ~ N(0,1). For e < e', z' < z pathwise. The m-arm map (m, z) -> max(0, m - z - K)
is nondecreasing in m and nonincreasing in z, so m'_t >= m_t and tau_m' <= tau_m; the p-arm map is nondecreasing in
p and z, so p'_t <= p_t and tau_p' >= tau_p. tau = min(tau_p, tau_m) has no pathwise order. This is exactly the gap
F17 records (`DEFECT_REGISTER.md:42`), and the reason the cover's M2 is one-sided only (`PROOF.md:93-110`).

### c.2 Lemma V (the atom-started two-sided CUSUM is a V-mask)

Let S_0 = 0, S_t = z_1 + ... + z_t. Started at a = (0,0), on the event {tau >= t} the unclipped updates of F1 are

    p_{t-1} + z_t - K  =  max_{0 <= s <= t-1} [ (S_t - S_s) - K (t - s) ],
    m_{t-1} - z_t - K  =  max_{0 <= s <= t-1} [ -(S_t - S_s) - K (t - s) ].

*Proof.* Induction on the Lindley recursion. p_0 = 0 = max over s = 0 of (S_0 - S_0) - 0. If
p_{t-1} = max_{0<=s<=t-1}[(S_{t-1} - S_s) - K(t-1-s)], adding z_t - K gives the first display; clipping,
p_t = max(0, that) = max_{0<=s<=t}[(S_t - S_s) - K(t-s)] (the s = t term is 0), which closes the induction. The
m-arm is the same with S replaced by -S. No alarm has occurred before t, so the recursion is the unkilled one. QED

Since the alarm fires iff an unclipped update exceeds H (F1), for every n >= 0

    {tau > n}  =  { abs(S_t - S_s) <= H + K (t - s)   for all 0 <= s < t <= n }.          (V)

(For P5X's inclusive convention `>= h`, `PROOF.md:8-10`, replace <= by < ; nothing below changes.)

### c.3 Lemma S (the survival set is a centrally symmetric convex body)

A_n := { x in R^n : abs(x_t - x_s) <= H + K(t - s) for all 0 <= s < t <= n }, with x_0 := 0. A_n is a finite
intersection of slabs {abs(l(x)) <= c} with l linear and c = H + K(t-s) > 0, hence **convex**, **closed**, and
**centrally symmetric** (x in A_n iff -x in A_n); it is bounded (the s = 0 constraints give abs(x_t) <= H + Kt) and
has 0 in its interior. (With the open convention, the open slabs give the same three properties.)

### c.4 Lemma G (the law)

With r_i i.i.d. N(0,1), R = (R_1, ..., R_n), R_t = r_1 + ... + r_t, is N(0, Sigma_n) with Sigma_n[s,t] = min(s,t),
nondegenerate (R = L r, L lower-triangular all-ones, det 1). Its density
f_n(x) = (2 pi)^{-n/2} exp(-(1/2) sum_t (x_t - x_{t-1})^2) satisfies f_n(x) = f_n(-x), and every superlevel set
{f_n >= u} is an ellipsoid, hence convex. S = R - e v with v := (1, 2, ..., n). By (V),

    P_e(tau > n) = P(R - e v in A_n) = integral over A_n of f_n(y + e v) dy.                   (P)

### c.5 Anderson's theorem (external, cited, not re-proved)

T. W. Anderson, "The integral of a symmetric unimodal function over a symmetric convex set and some probability
inequalities", Proc. Amer. Math. Soc. 6 (1955) 170-176, Theorem 1: if E in R^n is convex and symmetric about 0,
f >= 0 satisfies f(x) = f(-x), {f >= u} is convex for every u > 0, and the integral of f over E is finite, then for
every y in R^n and 0 <= k <= 1,

    integral over E of f(x + k y) dx  >=  integral over E of f(x + y) dx.

This is the only external input. A reviewer who wants no dependency on it can use instead, for the Gaussian case,
Prekopa's theorem (marginals of log-concave functions are log-concave), as in the remark after the proof.

### c.6 Theorem M

> **Theorem M (atom-ARL monotonicity).** For the frozen chain F1 started at the atom, every n >= 0 and every
> 0 <= e <= e': P_e(tau > n) = P_{-e}(tau > n) and P_e(tau > n) >= P_{e'}(tau > n). Consequently
> tau(e) is stochastically nonincreasing in abs(e), and
>
>     Lambda(e) = E_a[tau](e) = sum_{n >= 0} P_e(tau > n)   is even and nonincreasing on [0, infinity).

*Proof.* n = 0: both sides are 1. n >= 1: evenness — by (P), A_n = -A_n and R =d -R, so
P(R + e v in A_n) = P(-R - e v in A_n) = P(R - e v in A_n). Monotonicity — if e' = 0 then e = 0; otherwise put
y = e' v, k = e/e' in [0,1] and apply c.5 to (P) with E = A_n (convex, symmetric, finite integral since f_n is a
probability density): the integral over A_n of f_n(x + k y) is >= that of f_n(x + y), i.e.
P_e(tau > n) >= P_{e'}(tau > n). Summing the tail formula term by term (nonnegative terms; finite by Lemma T) gives
the statement for Lambda. QED

*Remark (Prekopa route, no Anderson).* The set {(x, e) : x - e v in A_n} is convex in R^{n+1} (preimage of a convex
set under a linear map), so (x, e) -> 1_{A_n}(x - e v) f_n(x) is log-concave; its x-marginal g_n(e) = P_e(tau > n) is
log-concave (Prekopa 1973) and positive (A_n has interior). An even log-concave g satisfies, for 0 <= e < e', with
lambda = (1 + e/e')/2: log g(e) >= lambda log g(e') + (1 - lambda) log g(-e') = log g(e'). Same conclusion.

### c.7 Corollaries (logical consequences of Theorem M; validated with it by REVIEW_THEOREM_M_R1)

* **M1 — the quantifier collapses to the left endpoint.** For every cell [e_lo, e_hi] with e_lo >= 0:
  `Lambda_k = sup_cell Lambda = Lambda(e_lo)`. For 308: `Lambda_308 = Lambda(1882413/1000000)`, and
  X308 iff Lambda(e_lo) >= A0*.
* **M2' — C4's caveat is discharged.** "Identifying Lambda_308 with the value at e_lo assumes E_a[tau] is decreasing
  in e. No committed artifact certifies that" (`C4_TARGET_RECONSTRUCTION.md:88-90`, graph_C §5.3) — Theorem M is
  that missing statement. C7's listed lever S4, "the gap between sup over the cell and the value at e_lo. Needs
  operator information" (`LP/p5y_k5_tail_c7_e2_lambda309/evidence/certificate/C7_CERTIFICATE.json:144`;
  `README.md:115-117`), is **identically zero** for every cell with e_lo >= 0: no headroom exists there.
* **M3 — P5's open claim, atom version.** `sup_e E_a[tau | e] = E_a[tau | 0]` (`LIMITATIONS.md:49-53`) holds for the
  atom start (evenness plus monotonicity). The sup_x version in D3/L4 (`DEFECT_REGISTER.md:36-45`) is **not** implied.
* **M4 — one-drift upper bounds become uniform.** A certified upper bound on Lambda at the single drift e_lo of a cell
  with e_lo >= 0 is a certified upper bound on Lambda_k, i.e. (by F3) an admissible uniform A0 for that cell. This is
  what makes a one-drift refutation of X308 possible (b.2) — and what makes it a new A0 supply (draft protocol,
  leakage analysis).

### c.8 What Theorem M does not give

* **Other starting states.** From x = (p0, m0) with p0 != m0 the survival set is not centrally symmetric and
  monotonicity in e can fail. *[Corrected per REVIEW_THEOREM_M_R1 C2: for DIAGONAL starts p0 = m0 = c (0 < c <= 2)
  the proof goes through verbatim (the s = 0 slab becomes |S_t| <= H - c + Kt), verified numerically by the reviewer;
  Theorem M therefore holds from every diagonal state. Nothing about sup_x E_x[tau], C_T, C_upper or Lemma G's A0
  follows either way.]* *Analytic derivation (not a test, and not counted as a negative control; review note C-12):*
  for n = 1,
  P_x(tau > 1) = Phi(C - p0 + e) - Phi(m0 - C + e), whose e-derivative with m0 = 0 at e = 0 is phi(C - p0) - phi(C),
  strictly **positive** whenever 0 < p0 < 2C. So from any start (p0, 0) with p0 > 0 the one-step survival *increases*
  in e near 0, whereas at the atom (p0 = 0) the derivative phi(C + e) - phi(C - e) is 0 at e = 0 and < 0 for e > 0.
  Central symmetry (atom or diagonal start) is load-bearing: the symmetry step of the proof is exactly what fails
  for off-diagonal starts. Hence nothing about
  sup_x E_x[tau], the cover's C_upper, Lemma G's A0 or C_T follows.
* **Taboo quantities.** tau_a(e) = E_a[tau ^ T_a] and D_e separately: "not at the atom at time t" is the complement
  of a symmetric convex set, so {T_a > n} is not convex and Anderson does not apply. Only the ratio
  tau_a/D_e = E_a[tau] (SM(d)) is covered.
* **Derivatives / A1, A2 channels.** Theorem M gives the sign of dLambda/de on e > 0 (<= 0), not its size; nothing
  about A1 or A2 follows.
* **Strictness** is not claimed (not needed).
* **Governance.** Floor r2 requires every operator constant, Abar included, to be certified "uniform in e, on a domain
  that contains the cell's whole block. A scalar drift ... never qualifies" (F16). Theorem M makes a scalar-drift
  certificate at e_lo *mathematically* uniform, but consuming it that way changes the admissible form of a supply
  input: under S6 that is **CLOSURE-ONLY** until a user-decided floor extension is frozen before any evaluation.

### c.9 Proxy prohibition (binding on any use of Theorem M in this campaign)

Theorem M transports information between drifts: a certified **upper** bound on Lambda at any 0 <= e' <= e_lo(308)
is an upper bound on Lambda_308, and a certified **lower** bound at any e'' >= e_lo(308) is a lower bound on
Lambda_308. Therefore:

* combining Theorem M with values at **other drifts inside the quarantined band [1.2, 2.6]** (committed 305-307 A0s,
  committed 309 floors, or anything new computed in the band) to derive a statement about cell 308 is a
  **target-equivalent proxy** and is **forbidden** (Q1, Q2; `config/TARGET_QUARANTINE.json`
  forbidden_evaluation_classes, "target-equivalent proxy");
* combining it with values at the **declared validation drifts** (e in {0, 1/4, 1/2, 1} lies below e_lo(308); e >= 3
  lies above e_hi(308)) would also produce a new bound on a target cell and is equally forbidden, whatever its
  tightness. This stream did not evaluate how tight any such transport would be.
* **Quarantine-policy observation for the campaign lead.** QUARANTINE_AMENDMENT_1's premise ("operator quantities ...
  depend on the drift e only, not on the cell label") is now stronger: for the atom ARL, *every* drift carries
  one-sided information about every tail cell. Validation-drift values of Lambda must never be compared against any
  305-309 threshold. No such comparison was made here.
* This stream derived **no** new number for cell 308 from Theorem M.

### c.10 Validation status (S2) and what would falsify it

This stream ran no code (it is theory-only by instruction). **Theorem M is VALIDATED_NON_TARGET** by the
independent review `reviews/REVIEW_THEOREM_M_R1.md` (ACCEPTED_WITH_CORRECTIONS; C1/C2/N3 applied):
* §2 of the review validates it numerically at the declared drifts only;
* the review's numerical negative controls are in its §2.3.

The §c.8 argument is a derivation. It is not counted as a negative control (review note C-12).

**[S8-corrected]** The first version listed as "consistency checks" the ordering of the committed 306-309 MC values
and float diagnostics. That used target-cell values as validation evidence for a new result, and it is withdrawn.
Theorem M must be validated at non-target drifts only.

The original recommendation here is now superseded by the review. It asked for an evaluation at the declared drifts
{0, 1/4, 1/2, 1, 3}, with a planted numerical case at an off-diagonal start (p0, 0), p0 > 0, where §c.8's derivation
predicts failure near e = 0. Per c.9 and amendment 2 R2.1, validation-drift values must never be compared with any
305-309 number.

## (d) Internal consistency of committed evidence

Only committed numbers are compared here, each with other committed numbers. No new route result (Theorem M included)
enters this section (S8).

| # | check (could it fail?) | committed values | result |
|---|---|---|---|
| D1 | certified floor <= MC <= certified uniform upper bound, at e_lo(308) | 3.512733596 (F6) <= 4.30910 +- 0.00102 (F7) <= 5.218548599 (F11) | consistent |
| D2 | the same check for cell 309's own committed numbers at cell 309's e_lo | C7's committed 309 bound 3.586306094 (F14) <= MC 4.04731 +- 0.00092 (F7) <= 4.867216117 (309's certified A0, `C4_TARGET_RECONSTRUCTION.md:77`) | consistent |
| D3 | **[S8-corrected] withdrawn.** It checked Theorem M against the ordering of committed 306-309 MC and diagnostic values | — | — |
| D4 | the two independent float diagnostics at the 308 midpoint vs the MC there | 4.174300305 / 4.174300818 (`C4_CANDIDATE_ROUTES.md:91`) vs 4.17398 +- 0.00097 | consistent; the adjudicator reports agreement "to ~3e-4" (`C4_ADJUDICATION.md:84-85`) |
| D5 | thresholds ordered as consumer tightening predicts (a tighter transport raises the critical A0) | frozen clause 4.375228833 (F10) < C5-T 4.442851488 (F9) | consistent |
| D6 | the E2 family ceiling is not a bound on Lambda, so it may exceed the truth | at the same drift: ceiling 4.679910340 (F14) vs MC 4.04731 (F7); E2 PRIMARY 3.586306094 below both | consistent (Lorden is simply loose) |
| D7 | "4.311" used in C4 Condition 3 vs the adjudicator's MC | 4.311, "reproduced independently by both the pre-result reviewer and the adjudicator" (`C4_TARGET_RECONSTRUCTION.md:119-120`) vs 4.30910 +- 0.00102 | consistent to the precision quoted. C4 Condition 3 is a frozen-clause statement (F12) |
| D8 | the diagnostic interpolation "about 4.315" at e_lo (`C4_TARGET_RECONSTRUCTION.md:107-111`) vs MC 4.30910 | uncertified vs uncertified | consistent to about 1e-2 |

**One real inconsistency of wording (not of numbers).**
* ADJUDICATION_C8's R3 row says that under perfect information (A0 -> Lambda, A1 = A2 = 0) R3 "closes 307 and 308"
  (`ADJUDICATION_C8.md:382`). It justifies this by "ceilings ... vs floors", i.e. by comparing A0* with the
  **certified floor**.
* For 309 that comparison is valid: floor > ceiling implies true Lambda > ceiling.
* For 308 it is not: floor < ceiling says nothing about whether the **true** Lambda_308 is below the ceiling.
  "R3 closes 308" is therefore conditional on not-X308, which no certified fact establishes: the best certified upper
  bound, 5.218548599, is above A0*.
* For 307 the same claim is certified independently, because 307 already closes at A1 = A2 = 0 with its certified A0
  (`C4_TARGET_RECONSTRUCTION.md:75`).
* This is a wording scope issue for the C8 record, not a numerical error, and it changes no status. **[S8-corrected]**
  A sentence saying which way uncertified evidence leans was removed.

**Verdict on (d).** No committed number contradicts any other committed number. The certified bracket is
`3.512733596 <= Lambda_308 <= 5.218548599`, and the committed A0* = 4.442851 lies strictly inside it (as C8's own
table already implies: ceiling vs floor at `ADJUDICATION_C8.md:270`, A_now vs ceiling at `C8_DECISION.json:124-129`).
**[S8-corrected]** The first version added where the MC places Lambda_308 relative to A0*; that outcome estimate is
withdrawn.

## (e) Conclusion

**[S8-corrected] Classification with current information, outcome-neutral.**
* **BOUNDABLE now:** X308 is undecided on certified evidence.
* **DECIDABLE in principle** by one certified computation, in either direction. That computation is a single drift,
  e_lo, if Theorem M is accepted.
* **NOT PROVABLE by route L or R4**, per their committed values.
* No committed ceiling fact excludes E2/E2c, R1 or R5 as proof routes.
* **NOT undecidable.**
* This stream does not estimate which direction a certified computation would take.

The first version said "expected to be refutable" and "expected not provable". Those were outcome estimates built
from Theorem M plus committed MC and A0*, and they are withdrawn under S8.

Justification.

1. **Undecided now.** The certified bracket 3.512733596 <= Lambda_308 <= 5.218548599 strictly contains A0* (d).
   Nothing committed decides X308 either way.
2. **Proof direction.**
   * Route L and R4 are rigorously incapable. Their committed maxima over the cell, 3.512733596 and 1.051130, are
     below the committed A0*; this is a comparison of committed numbers only.
   * For E2/E2c, no committed ceiling at e_lo(308) exists; R1/R5 have no committed ceiling either. So no committed
     ceiling fact rules out a proof by those families.
   * Every lower-bound route is capped by Lambda_308 itself (definition). Whether that cap lies above or below A0* is
     exactly X308, and it is not estimated here.
   * The committed record's own risk assessment of this direction is history (`ROUTE_AUDIT_R1.md:450-459`), and C4
     Condition 2 forbids quoting it as established.
3. **Refutation direction.**
   * A refuting certificate exists iff not-X308 (b.2, completeness).
   * With Theorem M it needs exactly one drift, e_lo = 1882413/1000000. Without Theorem M it needs a whole-cell
     uniform supersolution, or a drift mesh plus a certified A1-type modulus.
   * In both cases the comparator A0* must itself be certified (b.4), which is a target Gamma evaluation.
4. **Not undecidable.** Lambda(e_lo) and A0* are fixed computable reals. Unless they are exactly equal, a certified
   computation of finite precision decides X308 (b.2). "Undecidable" would misdescribe a question that is only
   *unauthorized* and *costly*, not unsettleable.
5. **Value of settling it.** Either outcome has **zero closure leverage** by itself.
   * X308 true is exclusion-only (F15).
   * X308 false yields an admissible A0 < A0*, but closing 308 would still need reductions of (A1, A2) (C4 Condition 3,
     F12). **[S8-corrected]** The committed factor is no longer repeated here.
   * Under floor r2 a scalar-drift A0 is CLOSURE-ONLY (c.8, F16).
   * The durable, cell-independent gain is Theorem M itself.

What this stream did **not** do:
* evaluate anything at any drift;
* compute any Gamma, margin, bound or critical value for cells 305-309;
* combine Theorem M with any in-band, validation-drift or committed tail-cell value (c.9; S8 corrections above).
