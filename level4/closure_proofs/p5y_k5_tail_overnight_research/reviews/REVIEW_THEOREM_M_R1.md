# REVIEW_THEOREM_M_R1 — independent adversarial review of Theorem M (atom-ARL monotonicity)

THEOREM_REVIEW: ACCEPTED_WITH_CORRECTIONS

| item | value |
|---|---|
| object | Theorem M, `streams/C_308/A0X/EXCLUSION_308.md` §c.2–c.9 (Lemma V, Lemma S, Lemma G, Anderson citation, Theorem M, corollaries M1–M4, §c.8 limits, §c.9 proxy prohibition) |
| reviewer | fresh-context reviewer; did not write Theorem M or any C_308 file |
| date | 2026-09-28 |
| binding rules | `SCR/PREAMBLE.md` Q1–Q8, S1–S8; `config/TARGET_QUARANTINE.json`; `config/QUARANTINE_AMENDMENT_1.json` |
| scratch code | `SCR/review_M/` (SCR = `/private/tmp/claude-501/-Users-suzhe-ReBaseGuard/d7244e7c-65ad-4f06-9f5d-3a05e822ef9b/scratchpad`) |
| numerics file | `validation/THEOREM_M_REVIEW_NUMERICS.json` |

## 1. Proof check (task 1)

### 1.0 Model conventions, read not imported

I read the model twice, from two independent sources.

* `LP/p5y_k5_tail_c4_exhaustion/phase_1/C4_TARGET_RECONSTRUCTION.md:36-47`. This is the pinned producer as read by
  `c4_model_identity.py`. It has update `s+ <- max(0, s+ + z - K)`, `s- <- max(0, s- - z - K)` and "alarm iff the
  unclipped update exceeds H in either coordinate". The producer's form is `ell, upper = m - C_CUSUM, C_CUSUM - p`.
* The `LP/p5y_k5_tail_c11_n9_independent_certifier/code/c11_certifier.py` docstring (lines 22-36). It has window
  `z in [ell, up] = [m - C, C - p]`, `C = K + H = 11/2`, next state `(max(0, p+z-K), max(0, m-z-K))`, and weight
  `phi(z + e)`.

The two sources agree with each other and with F1 of EXCLUSION_308.md:
`p + z - K > H  <=>  z > C - p` and `m - z - K > H  <=>  z < m - C`. The arm threshold is **H = 5**, applied to the
unclipped update. The one-step window half-width at the atom is **H + K = 11/2**.

### 1.1 (a) Lemma V, the V-mask equivalence: CORRECT

* **Induction.** `p_t = max_{0<=s<=t}[(S_t - S_s) - K(t-s)]` holds for the unkilled Lindley recursion with `p_0 = 0`
  on every path. The s = t term is 0, which is the clipping. The unclipped update at t is
  `max_{0<=s<=t-1}[(S_t - S_s) - K(t-s)]`. The m-arm is the same with S replaced by -S. The killed chain agrees with
  the unkilled recursion on `{tau >= t}`. So `{tau > n}` is the intersection over t <= n of the no-alarm events, and
  each is `{|S_t - S_s| <= H + K(t-s) for all s < t}`. That is (V) exactly, with threshold **H + K(t-s)**, which is
  11/2 at lag 1.
* **Atom hypothesis.** It enters through `p_0 = m_0 = 0`, i.e. the s = 0 term. From `(p0, m0)` the s = 0 constraints
  become `S_t <= H - p0 + Kt` and `-S_t <= H - m0 + Kt`, and every other constraint is unchanged.
* **Clipped vs unclipped alarm.** This is immaterial because H > 0: `max(0, x) > H <=> x > H`. So the "unclipped
  update" wording and P5X's clipped `max(S+, S-) >= h` (`p5x_global_nonlinear_dynamics/compute_optimization_r1/PROOF.md:8-10`)
  define the same stopping time, up to the strict/inclusive boundary. That boundary has probability 0 because z has a
  density. The pathwise check in §2.1 confirms this: 0 mismatches.

### 1.2 (b) Lemma S, convexity and central symmetry: CORRECT

* A_n is a finite intersection of slabs `{|l(x)| <= c}` with c > 0, so it is closed, convex and centrally symmetric.
  It is bounded by the s = 0 slabs and has 0 in its interior.
* In increment coordinates the survival set is `L^{-1} A_n`, with L the lower-triangular all-ones matrix. A linear
  preimage keeps all three properties.

### 1.3 (c) Anderson's theorem and its application: CORRECT

* **The citation.** The quoted statement matches Anderson (1955), Theorem 1: E convex and symmetric; f >= 0, even,
  with convex superlevel sets and a finite integral over E; conclusion `int_E f(x + ky) >= int_E f(x + y)` for
  `0 <= k <= 1`.
* **The density.** `f_n(x) = (2 pi)^{-n/2} exp(-1/2 sum (x_t - x_{t-1})^2)` is the density of `R = L r` (det L = 1).
  It is even, and its superlevel sets are ellipsoids because the quadratic form is positive definite.
* **The representation.** `S = R - e v` with `v = (1, ..., n)`, because z_t = r_t - e. Hence
  `P_e(tau > n) = P(R in A_n + e v) = int_{A_n} f_n(y + e v) dy`, which is (P).
* **The shift.** In increment coordinates it is along the direction (1, ..., 1), as the task states; in partial-sum
  coordinates it is along v. These are equivalent under L.
* **The application.** `y = e' v` and `k = e/e'` give `P_e >= P_{e'}` for `0 <= e <= e'`. Rays only need the
  one direction v, because the drift enters only through e v.
* **The Prekopa remark is also correct.** `(x, e) -> 1_{A_n}(x - e v) f_n(x)` is log-concave because
  `{(x, e) : x - e v in A_n}` is convex. So `g_n(e) = P_e(tau > n) > 0` is log-concave. An even, positive log-concave
  function is nonincreasing on [0, inf): take `lambda = (1 + e/e')/2`. This gives a second, independent route to the
  same conclusion.

### 1.4 (d) Passage to E[tau]: CORRECT

* tau is N-valued with tau >= 1, so `E_a[tau] = sum_{n>=0} P_a(tau > n)`.
* This equals `[(I - K_e)^{-1} 1](a) = sum_j (K_e^j 1)(a)`, the SM(d) quantity (`THEOREM_AD.md:51`), because
  `(K_e^j 1)(a) = P_a(tau > j)`.
* The termwise inequalities between nonnegative series carry over to the sums. Finiteness (Lemma T) is not even
  needed for the inequality.

### 1.5 (e) Evenness: CORRECT, and more elementary than presented

The Anderson proof is fine. Evenness also follows directly from the model's symmetry
`(z, e, p, m) -> (-z, -e, m, p)`, which fixes the atom. Only **monotonicity** needs Lemma S together with Anderson or
Prekopa.

### 1.6 (f) What Theorem M does not say

The limits in §c.8 are right in substance, with one factual correction (C2 below).

1. **Other starting states.** Monotonicity and evenness fail in general. The §c.8 analytic control is correct:
   `P_x(tau > 1) = Phi(C - p0 + e) - Phi(m0 - C + e)`, with derivative at e = 0 equal to `phi(C - p0) - phi(C) > 0`
   for `0 < p0 <= 5`. It is confirmed numerically in §2.2, including for `E_x[tau]`.
   **Correction C2.** §c.8 says "From x = (p0, m0) != a the survival set is not centrally symmetric". That is false
   for **diagonal starts p0 = m0 = c**, with 0 < c <= 2 (in X since 2c <= 4). There the s = 0 slabs are
   `|S_t| <= H - c + Kt`, still symmetric, and the proof goes through verbatim. Theorem M therefore also holds from
   every diagonal state (c, c). The load-bearing hypothesis is "symmetric start (p0 = m0)", not "atom". The
   conclusion "nothing about sup_x E_x[tau] follows" is unaffected.
2. **Taboo quantities.** `tau_a(e) = (G-hat_e 1)(a) = E_a[tau ^ T_a]` and `D_e` are not covered separately, and
   neither is the atom-removed kernel K-hat_e or its resolvent norm. The survival-and-no-return event is
   `A_n` minus a union of symmetric convex sets, which is not convex. §c.8 states this correctly. The theorem also
   does not claim that these quantities are *non*-monotone; it is silent on them.
3. **Uniform constants.** Theorem M implies nothing about `sup_x E_x[tau]`, C_T, the cover's C_upper, Lemma G's A0,
   the P5X obligation L4 (`DEFECT_REGISTER.md:40-44`), or a block-robust value such as C2b's `Lambda*(E)`
   (time-varying drift).
4. **Derivatives.** It gives the sign of `dLambda/de` on e > 0 only, not its size. Nothing about A1 or A2 follows.
5. **Certification.** The theorem transports **true-value** inequalities. A certified bound at one drift transports
   as a certified bound. A float or MC estimate transports only as an estimate.
6. **Strictness.** Not claimed. Numerically the inequalities are strict at every declared drift (§2).

## 2. Non-target numerical validation (task 2)

**Declared before any run.** The validation set was fixed in `SCR/review_M/DECLARATION.json`:
* drifts: {0, ±1/4, ±1/2, ±1, ±3} only;
* n in {1, 2, 3, 5, 10, 20, 50, 100, 200, 500};
* starts: the atom, plus non-atom starts (p0, 0) and (0, p0) with p0 in {1, 5/2, 5}.

Two addenda were written before their runs:
* ADDENDUM_1: diagonal starts (1, 1) and (2, 2), to test my correction C2, with the off-diagonal (2, 1) as a
  negative control;
* ADDENDUM_2: a score-function estimate of dE/de at e = 0 only.

**Quarantine and code.** Every entry point calls `Q.guard_drift` and refuses undeclared drifts. The code is stdlib
only and imports nothing historical. `Q.scan` on `SCR/review_M/` gives PASS: 8 files, 0 findings, and the planted
control detected all three kinds. All values are in `validation/THEOREM_M_REVIEW_NUMERICS.json`, regenerated by
`rm_assemble.py` from the `out_*.json` files.

### 2.1 Lemma V pathwise: PASS, and the controls fire

`rm_vmask.py` ran 13,500 paths (1,500 per drift, 80 steps, independent seeds), containing 10,235 alarms.

| comparison against the literal killed recursion | mismatches |
|---|---|
| literal double-loop V-mask `abs(S_t - S_s) <= H + K(t-s)` | **0** |
| alarm on the clipped state (convention check) | **0** |
| planted: threshold `H + K(t-s-1)` (H instead of H + K at lag 1) | 4,588 (detected) |
| planted: V-mask without the s = 0 slab | 3,520 (detected) |
| planted: V-mask applied to the start (5/2, 0) | 3,559 (detected) |
| ADDENDUM_1: diagonal starts (1,1), (2,2) with the s = 0 slab `abs(S_t) <= H - c + Kt` | **0** and **0** (9,000 paths) |
| ADDENDUM_1 planted: atom V-mask applied to the start (2,2) | 4,024 (detected) |

### 2.2 Monotonicity in abs(e) and evenness from the atom: PASS on every resolved comparison

**Values of E_a[tau] along e = 0, 1/4, 1/2, 1, 3.** These are non-target. By §3.1 they must never be set against any
305-309 number.

| method | 0 | 1/4 | 1/2 | 1 | 3 |
|---|---|---|---|---|---|
| grid chain N = 10 | 463.9622 | 139.2670 | 37.9758 | 10.3758 | 2.5733 |
| grid chain N = 20 | 465.0725 | 139.4370 | 37.9910 | 10.3759 | 2.5733 |
| MC, 200,000 paths, ± 1 SE | 465.66 ± 1.03 | 139.64 ± 0.30 | 37.918 ± 0.069 | 10.377 ± 0.012 | 2.5717 ± 0.0015 |

**Grid chain.**
* The tail is extrapolated geometrically. At e = 0 the tail is 33.5 % of the sum, and the ratio has converged:
  the change over 50 iterations is at most 1.1e-16.
* N = 10 and N = 20 differ by 0.24 % at e = 0, which is the discretisation error.
* MC minus grid (N = 20), in MC standard errors, lies in [-1.78, +0.68] over all nine drifts.

**Monotone detector.** It flags any increase along increasing abs(e).
* Grid E, both rays, N = 10 and N = 20: **0 violations**.
* Grid P_n(atom) for every declared n, N = 10 and N = 20: **0 violations**.
* MC E, both rays: 0 significant violations (none at 3 SE). All 4 + 4 pairs resolve at > 3 SE in the predicted
  direction.
* MC P_n: 0 significant violations for any n. Some pairs are **unresolved**; for example at n = 1 three of four
  pairs are unresolved, because the true differences are about 1e-8. Those pairs are covered exactly by the next row.
* Exact n = 1 (closed form) and n = 2 (Gauss-Legendre; the change from M = 40 to M = 80 is at most 8e-16 relative):
  0 violations on both rays. At n = 1 the alarm probability is 3.80e-8, 8.05e-8, 2.88e-7, 3.40e-6 and 6.21e-3; at
  n = 2 it is 2.214e-5, 5.255e-5, 2.041e-4, 2.341e-3 and 0.5000. Both increase strictly.

**Evenness.**
* MC z-scores for E(e) - E(-e) at 1/4, 1/2, 1, 3: 0.37, -0.64, 1.34, -0.34.
* Exact n = 1 and n = 2: relative differences 0 and 2.7e-16.
* The grid chain is even to 7e-13, but that is an implementation check only: the discretisation is symmetric by
  construction.

### 2.3 Negative control: from a non-atom start the order fails

| check | start | result |
|---|---|---|
| exact n = 1, `P_x(tau > 1)`, e = 0, 1/4, 1/2, 1, 3 | (5, 0) | 0.691462, 0.773373, 0.841344, 0.933189, 0.993558: **increasing**, 4 violations flagged |
| exact n = 1, same | (1, 0) / (5/2, 0) | 2 / 3 violations flagged on the + ray |
| exact n = 1, same | (0, p0) mirrors | the same violations on the - ray |
| exact d/de `P_x(tau > 1)` at 0, `= phi(C - p0) - phi(C)` | p0 = 1, 5/2, 5 | +1.6e-5, +0.00443, +0.352 (atom: 0); matches §c.8 |
| exact n = 2 alarm probability | (1, 0), (5, 0) | 1 and 3 violations flagged |
| E_x evenness, grid N = 20 | (5, 0) | E(±1/4) = 96.18 / 50.05; E(±1/2) = 30.41 / 8.71: **not even** |
| E_x evenness, MC 100,000 paths | (5, 0) | E(1/4) = 96.57 ± 0.40 vs E(-1/4) = 49.32 ± 0.32 (z = 91.9) |
| dE_x/de at e = 0, grid differentiated recursion | (5, 0) | +321.22 (N = 10), +321.98 (N = 20); (0, 5) mirrored; atom -0.0 |
| dE_x/de at e = 0, score-function MC (ADDENDUM_2), 100,000 paths | (5, 0) / (0, 5) / atom | +319.1 ± 45.2 / -360.4 ± 45.0 / +10.6 ± 52.2 (consistent with 0) |
| ADDENDUM_1, exact n = 1, 2 and grid E, P_n (N = 10, 20) | (1,1), (2,2) | **0 violations** (C2 confirmed) |
| ADDENDUM_1, same detectors | (2, 1), off-diagonal | n = 1: 2 violations; n = 2, 3: 1 violation (**flagged**) |

**Honest coverage note.** At the declared drift spacing, the *E-level* monotone detector does **not** fire for
non-atom starts: E_x decreases along both rays at 0, 1/4, 1/2, 1, 3. The failure of monotonicity for E_x is local
near e = 0, and it is established only through the derivative at e = 0 by two independent methods. The failure for
P_x(tau > n) is established at declared drifts, for n = 1, 2, 3. Evenness fails at every declared drift. The atom
restriction, or more precisely the diagonal restriction (C2), is therefore necessary. The ingredient that fails is
central symmetry.

## 3. Quarantine risk assessment (task 3)

### 3.1 Which transfers Theorem M licenses, and in which direction

These are true-value statements. Evenness lets |e| stand for e throughout. The same rules hold for every
P(tau > n), and, by §1.6 item 1 (C2), for every diagonal start (c, c).

| # | transfer | valid? |
|---|---|---|
| T-UP | an **upper** bound U >= Lambda(e') transfers **outward**: U >= Lambda(e) for every abs(e) >= abs(e') | VALID |
| T-LO | a **lower** bound L <= Lambda(e'') transfers **inward**: L <= Lambda(e) for every abs(e) <= abs(e'') | VALID |
| T-UP-in | an upper bound transferred inward (to smaller abs(e)) | INVALID |
| T-LO-out | a lower bound transferred outward (to larger abs(e)) | INVALID |
| M1 | for a block [a, b] with a >= 0: sup over the block = Lambda(a), inf over the block = Lambda(b); for a block containing 0: sup = Lambda(0) | VALID |
| mixed start | any transfer for a non-diagonal start (p0 != m0), for tau_a / D_e / K-hat quantities, or for sup_x E_x[tau] | NOT LICENSED |

What this means for the quarantined band B = [6/5, 13/5] and its mirror:

1. **Upper bounds from below the band.** Every upper bound at a drift with abs(e') <= 6/5 is, by T-UP, an upper bound
   on Lambda throughout B, and on every tail cell's Lambda_k. This includes the declared validation drifts
   0, 1/4, 1/2 and 1.
2. **Lower bounds from above the band.** Every lower bound at abs(e'') >= 13/5 is, by T-LO, a lower bound throughout B.
   This includes the declared drift 3.
3. **Consequence for the quarantine.** Amendment 1's premise was that drifts outside the band carry no band
   information. For Lambda this premise is false: the band is bracketed from both sides by the declared validation
   drifts. The author already observed this (§c.9, third bullet), and I confirm it.
4. **Committed tail values.** By T-UP, a committed certified A0 of a *lower-indexed* tail cell transfers to every
   *higher-indexed* tail cell. By T-LO, a committed floor of a *higher-indexed* cell transfers to every lower-indexed
   cell. Both are target-equivalent proxies (§c.9, first bullet). **I did not look up, combine or compare any such
   value.** In particular I did not open `C4_TARGET_RECONSTRUCTION.md:75-77`.
5. **Certification.** A float or MC value transfers only as an estimate. The certified supersolution values in
   C2b's `gen/` (point and block certificates at e in {1/4, 1/2, 1, 3}, ledger lines 61-70) are **certified** and
   transfer as certified band bounds: T-UP for e <= 1, T-LO for any certified lower side at 3. They are the most
   concrete latent proxy in the namespace. **I did not open their values.**

### 3.2 Does any document of this campaign use such a transfer into the band? Not as a number.

Commands and hit lists are in §5.

* **Grep coverage.** I grepped the whole namespace (`*.md`, `*.json`, `*.py`) for "Theorem M", "Lemma V", "atom-ARL
  monoton" and "monoton | nonincreasing | decreasing in e".
* **Where Theorem M appears.** Only in `streams/C_308/A0X/` (EXCLUSION_308.md, C2A_ROUTE_SUMMARY.md, PROGRESS.md,
  FREEZE_308_EXCLUSION_PROTOCOL_DRAFT.md). No other stream cites it. The other monotonicity hits are unrelated:
  TPT-M profiles, B307's rho, C2b's iterate monotonicity, and graph_C §5.3 quoting the historical caveat.
* **In the current EXCLUSION_308.md (0d32a2e8) no numeric transfer into the band exists.** The band uses are
  structural and carry no number:
  * §b.1: "e* = e_lo is the optimal point".
  * §b.2 and M4: a one-drift refutation certificate *would* suffice.
  * M1 and M2': the sup is at e_lo, and S4 is zero.
* **In the draft freeze protocol.** Variant P is an in-band evaluation *design* at e_lo(308). It is gated on P4, user
  authorization, which is not given. No evaluation took place: there is no ledger line and no code path.
* **Leftover cross-cell juxtaposition (note N3).** The §b.1 table row "C7 E2 / E2c" places the committed E2 *family
  ceiling* (4.679910340, committed at the drift 19839101/10000000, a 309 quantity) next to A0*(308).
  * Both numbers are committed, no route factor is attached and Theorem M is not used.
  * The ceiling is not a bound on Lambda (§d D6), so this carries no information on the sign of X308.
  * It is still a cross-cell comparison that the committed record does not make. It should be moved to the history
    section or re-worded as "no committed ceiling at e_lo(308) exists".
* **C2b code.** The quarantine guard is honoured (`gen/c2b_common.py:44`, guard_drift at every entry point). The
  ledger shows only drifts outside the band. No C2b document references Theorem M.

### 3.3 The "entailment" of C7's committed floor to cell 308: classification

**What it was.** The first version of EXCLUSION_308.md read C7's committed certificate "E_a[tau] >= 3.586306094 at
e = 19839101/10000000" (F14; `LP/p5y_k5_tail_c7_e2_lambda309/README.md:15`) as a floor for Lambda_308. It placed
that floor next to A0*.

**It was not a Theorem M consequence.** The drift is e_hi(308), which lies in the closed cell 308 (F5). The inference
uses only F3/F4, the definition of Lambda_308 as a sup over the closed cell. I state this to classify the inference.
**I do not re-assert the floor, and I do not place it next to any threshold.**

**It was not a pure reading.**
* The committed record attributes the value to cell 309 only:
  * `C8_ROUTES.json:152`: "C7 certifies Lambda(e_lo) >= 3.586306093865 for cell 309";
  * `ADJUDICATION_C8.md:382`: 309 column.
* The committed cell-308 floor is 3.512733596 (F6; `C8_DECISION.json:131`).
* Re-attributing a 309 value to 308 creates a new certified enclosure endpoint for a target-cell quantity. It needs
  no computation.

**Classification: a zero-compute target-cell derived quantity, a cross-cell re-attribution.** It falls under
`TARGET_QUARANTINE.json` forbidden_evaluation_classes item 2: an "enclosure ... for a target cell under any new ...
theorem". It is not covered by the "allowed" clause, which permits reading historical values "exactly as committed"
or decomposing them "under the historically evaluated supply only". Placing it next to A0* also made it an input to
the X308 decision (S8). **Its withdrawal was correct and necessary.**

**Residue.**
* The current file has none. D2 now uses the value only as a 309-drift consistency check among committed numbers.
* The first version is **preserved in git history** on the local branch: commit `7e851139`, EXCLUSION_308.md, lines
  191, 364 and 383. Line 364 says "(F14, entailed)". Line 383 says "(3.586306094 on the left by entailment)".
* The ledger has **no** entry for the C2a S8 withdrawals. I grepped `ZERO_TARGET_LEDGER.jsonl` for
  EXCLUSION / C2A / C2a / Theorem M: my own lines are the only hits.
* **Recommendation (note N4).** Record a `PROXY_EXPOSURE` ledger line and an incident note for the C2a first version,
  analogous to INCIDENT_01, with `target_equivalent_proxies = 1`, pointing at 7e851139 and superseded by 0d32a2e8.
  Git history cannot be rewritten under Q4, so the ledger is the only place to fence it.

### 3.4 This review's own exposure

* **Drifts evaluated.** Only the declared drifts {0, ±1/4, ±1/2, ±1, ±3}. Every entry point calls
  `rm_common.check_drift`, which calls `Q.guard_drift` and also refuses any undeclared drift.
* **Cells.** None touched.
* **Values produced.** They include float/MC estimates of Lambda at e = 1 and e = 3. By §3.1 these are one-sided
  estimates for the band. **They are not placed next to, or combined with, any 305-309 number, here or in the
  numerics JSON.** The JSON carries the same prohibition in its `quarantine` field.
* **Ledger.** 7 `NONTARGET_DRIFT_VALIDATION` lines from `SCR/review_M/rm_*.py`.

## 4. Verdict, blockers, corrections, notes

**Theorem M is correct as stated.** It says that for the frozen chain started at the atom, P_e(tau > n) is even and
nonincreasing in abs(e) for every n, and therefore so is E_a[tau](e).

* Lemma V, Lemma S, the Gaussian law, the Anderson application, the Prekopa alternative, the tail-sum passage and
  evenness all check line by line (§1).
* The exact model conventions check too: arm threshold H on the unclipped update, V-mask half-width H + K(t - s), and
  clipped vs unclipped immaterial for H > 0.
* Numerical validation at the declared drifts found no violation on any resolved comparison (§2.2).
* The negative controls fire where the theorem says they must (§2.3).

**Blockers: none.**

**Corrections required.** Neither affects the theorem.

* **C1.** §b.1 (and the b.3 table): "By Theorem M the truth Lambda(e) is largest at e_lo, so e* = e_lo is the optimal
  point for every route" overstates.
  * Theorem M makes e_lo maximise the **truth**, which is the universal cap on every lower-bound route.
  * A particular lower-bound route's certified value need not be maximised at e_lo, because its slack may vary
    with e.
  * Suggested wording: "e_lo maximises Lambda over the cell, hence the cap on every lower-bound route; for a given
    route, e_lo is optimal only if its slack does not grow faster than Lambda decreases" (route L is monotone, so it
    is optimal there, as F6 already says).
* **C2.** §c.8, first bullet: "From x = (p0, m0) != a the survival set is not centrally symmetric" is false for
  diagonal starts p0 = m0 = c (0 < c <= 2).
  * For those starts the proof goes through verbatim: the s = 0 slab becomes `abs(S_t) <= H - c + Kt`.
  * This is verified in §2.1 and §2.3 (ADDENDUM_1).
  * Replace with "not centrally symmetric unless p0 = m0". Theorem M then holds from every diagonal state.
  * The conclusion that nothing about sup_x E_x[tau], C_T, C_upper or Lemma G's A0 follows is unaffected.

**Notes.** None is required for acceptance.

* **N1.** Evenness follows from the elementary model symmetry `(z, e, p, m) -> (-z, -e, m, p)`. Only monotonicity
  needs Lemma S together with Anderson or Prekopa. It is worth saying so, because it makes clear which ingredient the
  negative control defeats: central symmetry of the s = 0 slabs.
* **N2.** The §c.8 analytic control is correct. At the declared spacing, non-atom E_x[tau] is not even but is still
  decreasing on both rays. Its monotonicity failure is local at e = 0 (dE_x/de(0) about +320 for x = (5, 0), by two
  methods). Any future validation stream should not expect the E-level detector to fire at the declared drifts.
* **N3.** The §b.1 table row "C7 E2 / E2c" juxtaposes the committed E2 family ceiling at the 309 drift with A0*(308).
  It is harmless in information content (§3.2), but it is a cross-cell comparison that the record does not make.
  Move it to history or re-word it.
* **N4.** The withdrawn "entailment" (§3.3) is a zero-compute target-cell derived quantity. It persists in commit
  `7e851139`. It is not in the ledger. Record a PROXY_EXPOSURE ledger line or an incident note for it.
* **N5 (quarantine policy, for the campaign lead).** Under Theorem M the declared validation drifts bracket the band
  for Lambda: upper bounds from {0, 1/4, 1/2, 1} and lower bounds from 3 (§3.1). C2b's *certified* supersolution
  values at e <= 1 are therefore certified upper bounds on every tail cell's Lambda_k. Recommend an amendment that
  forbids any juxtaposition of validation-drift Lambda / E_a[tau] / supersolution values with 305-309 thresholds, and
  that labels those files accordingly.
* **N6.** The draft freeze protocol's precondition P1 ("Theorem M reviewed and ACCEPTED ... validated at the declared
  non-target drifts ... negative control") is **met by this review, subject to C1 and C2**. The other preconditions
  are not addressed here. P4 (user authorisation of an in-band computation) is not given, and nothing in this review
  bears on it.

**Status and scope of this verdict.**
* Route status of Theorem M after this review: **VALIDATED_NON_TARGET** (G2, G3, G5, G6 pass; G8 pass for the
  current file, with N4 for history).
* It changes no cell status and computes no target quantity.

THEOREM_REVIEW: ACCEPTED_WITH_CORRECTIONS

## 5. Commands and outputs

All commands were run locally with `nice`, stdlib Python 3.14. Wall time for all runs together was under 10 minutes.
No git writes and no remote hosts were used.

```
# model conventions (read only)
sed -n 36,50p LP/p5y_k5_tail_c4_exhaustion/phase_1/C4_TARGET_RECONSTRUCTION.md
sed -n 1,80p  LP/p5y_k5_tail_c11_n9_independent_certifier/code/c11_certifier.py    # docstring only; not imported

# namespace grep for uses of Theorem M / drift monotonicity
grep -rn -i "theorem m\b\|Theorem M\|thm M\|atom-ARL monoton\|Lemma V\b" --include='*.md' --include='*.json' --include='*.py' NS
  -> hits only in streams/C_308/A0X/{EXCLUSION_308.md, C2A_ROUTE_SUMMARY.md, PROGRESS.md, FREEZE_308_EXCLUSION_PROTOCOL_DRAFT.md}
grep -rn -i "monoton\|nonincreasing\|non-increasing\|decreasing in e\|decreasing in abs" (same scope, excluding A0X docs)
  -> unrelated only: b307_lib rho, c2b_float iterates, THEOREM_LR, D_309, TPT-M profiles, graph_B/graph_C historical quotes
grep -n "guard_drift\|guard_cell\|log_execution" NS/streams/C_308/A0X/gen/*.py   -> c2b_common.py:44 guard_drift; ledger lines 61-70 non-band

# entailment provenance (read only)
grep -rn '3\.586306' LP --include='*.md' --include='*.json' | grep 308   -> ADJUDICATION_C8.md:382 (309 column), C8_ROUTES.json:152 ("for cell 309")
git -C /Users/suzhe/ReBaseGuard-k5ov log --oneline -- NS/streams/C_308/A0X/EXCLUSION_308.md   -> 0d32a2e8 (S8 final), 7e851139
git show 7e851139:NS/streams/C_308/A0X/EXCLUSION_308.md | grep -n -i entail   -> lines 11, 191, 364 "(F14, entailed)", 383 "(... on the left by entailment)"
grep -n "EXCLUSION\|C2A\|C2a\|Theorem M" NS/ledger/ZERO_TARGET_LEDGER.jsonl   -> only this review's own lines

# numerics (SCR/review_M)
python3 rm_exact.py        -> atom: 0 violations, evenness 0 / 2.7e-16; (p0,0), (0,p0): violations flagged; n2 M40->M80 rel 8e-16
python3 rm_vmask.py        -> true 0/13500 mismatches; clipped 0; NC 4588 / 3520 / 3559
python3 rm_grid.py 10 all  -> E_atom 463.9622, 139.2670, 37.9758, 10.3758, 2.5733; dE/de(0) (5,0) +321.22
python3 rm_grid.py 20 all  -> E_atom 465.0725, 139.4370, 37.9910, 10.3759, 2.5733; dE/de(0) (5,0) +321.98, atom -0.0
python3 rm_mc.py 200000    -> atom E 465.66±1.02, 139.64±0.30, 37.918±0.069, 10.377±0.012, 2.5717±0.0015;
                              mirrors 139.48±0.30, ...; start (5,0): E(0) 249.76±1.29, E(1/4) 96.57±0.40, E(-1/4) 49.32±0.32
python3 rm_diag.py 10 20   -> (1,1), (2,2): 0 violations, V-mask 0 mismatches; (2,1) flagged; atom V-mask from (2,2): 4024 mismatches
python3 rm_score.py 100000 -> dE/de(0): atom 10.6±52.2, (5,0) 319.1±45.2, (0,5) -360.4±45.0
python3 rm_assemble.py     -> wrote validation/THEOREM_M_REVIEW_NUMERICS.json
python3 -c "... ov_quarantine.scan(Path('SCR/review_M'))"   -> PASS, 8 files, 0 findings, planted control kinds detected (3/3)
grep -c 'SCR/review_M/rm_' NS/ledger/ZERO_TARGET_LEDGER.jsonl   -> 7 lines, 0 LEAK_FLAG
```
