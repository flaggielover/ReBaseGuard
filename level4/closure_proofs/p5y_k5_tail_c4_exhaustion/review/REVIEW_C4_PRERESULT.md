# Independent fresh-context pre-result review — P5Y / K5 Campaign C4

Reviewer: fresh context, no prior knowledge of this programme. Working tree `/Users/suzhe/ReBaseGuard-k5c4`,
branch `p5y-k5-tail-c4`. Repository read-only throughout; every artifact I produced lives in my scratchpad.
HEAD moved during the review: it was `376950be` (gate freeze) when I started and `8262a2bb` (Phase 6/7 producers,
not yet run) when I finished. I reviewed `c4_certificate.py` and `c4_mutations.py` as well, since they were in the
tree and they decide whether the load-bearing test is what the gate says it is.

What I ran (all local, `python3`, stdlib only, no host contacted, nothing in the repo modified):
`c4_lower_bound.py`, `c4_thresholds.py`, `c4_phase0_audit.py`, `c4_certificate.py` (into scratch), plus my own
independent re-implementations: a 160-digit cancellation-free Gaussian reference, a 2,000,000-path Monte-Carlo of
the identified CUSUM chain, and direct drivers for the individual mutants.

---

## A. Are the target thresholds derived correctly?

I re-ran `code/c4_thresholds.py` from the committed source and reproduced every number:

| cell | A0 certified | Γ at A1=A2=0 | closes? | critical A0 |
|---|---|---|---|---|
| 306 | 6.004490785 | −0.079278659 | yes | — |
| 307 | 5.597995510 | −0.021906451 | yes | — |
| 308 | 5.218548599 | +0.039567846 | no | 4.375228833136 |
| 309 | 4.867216117 | +0.092812423 | no | 3.214236022678 |

These are derived, not transcribed: the producer evaluates the frozen TC-T whole-cell enclosure composed with the
frozen K5-B direct clause at chosen `(A0, A1, A2)` triples, in exact `Fraction` arithmetic, and bisects over 220
steps (bracket widths 3.1e-66 at 308 and 2.9e-66 at 309). The C3 adjudicator's figures are reproduced by Phase 0
checks 11/12 from the equations rather than from its prose; both checks pass on my re-run.

The bisection presupposes that Γ is nondecreasing in A0. The producer exercises that on a 21-point ladder from 0 to
the certified A0. I went further and evaluated Γ(A0,0,0) at A0 ∈ {3.2, 3.3, 4, 5, 6, 10, 50, 200, 1000, 100000}:
monotone nondecreasing throughout, saturating at +0.288317 (308) and +0.374145 (309), with the TC-T/K5-B
intersection non-empty at every point. The structural licence holds far beyond the range the campaign exercises.

Critical values are correctly held at arm's length: they are reported, and the Phase 6 test is the direct exact
evaluation `Γ(B, 0, 0) ≥ 0`. I confirmed in `c4_certificate.py` that `exclude_if` is applied to the exact
`Fraction` Γ, not to the float that is printed beside it.

**Verdict: PASS.**

## B. Do the domains and quantifiers match the C3 knockout?

Cell geometry, from `cells.json` and cross-checked against the C1 registry (the producer refuses on disagreement;
I also checked the arithmetic by hand, e.g. 309: e0 = 40761931/20000000, ρ = 1083729/20000000, e_lo = 39678202/20000000
= 19839101/10000000 = 1.9839101):

| cell | closed cell |
|---|---|
| 306 | [1.7019225, 1.7885921] |
| 307 | [1.7885921, 1.8824130] |
| 308 | [1.8824130, 1.9839101] |
| 309 | [1.9839101, 2.0922830] |

The bound is certified at `e = e_lo`, the left endpoint of the **closed** cell, which is inside it. `c4_certificate.py`
enforces `e_lo ≤ e ≤ e_hi` per cell and raises otherwise; I verified the guard is live.

The quantifier direction is right. Admissibility requires `A0 ≥ sup_{e∈[e0−ρ, e0+ρ]} E_a[τ](e) =: Λ_k`, and
`Λ_k ≥ E_a[τ](e*)` for any single `e*` in the closed cell, so a pointwise lower bound suffices. This is a hypothesis
of the frozen theorem, not a C4 invention: THEOREM_AD §5 fixes "a drift set E ⊇ [e0 − ρ, e0 + ρ] on which the
hypotheses of Lemma Dv hold", and Lemma Dv's `|[R f](a)| ≤ A0‖f‖` is asserted for every `e ∈ E`.

The choice of endpoint is also right, and for the right reason. `E_a[τ]` decreases in `e` (my Monte-Carlo: 4.7309 at
306's midpoint falling to 3.9214 at 309's), so the left endpoint maximises both the truth and the route's bound; the
producer's `dE[V]/de = Φ(e−K) − Φ(−(e+K)) ≥ 0` is correct — I re-derived it by differentiating the two one-sided
integrals under the integral sign and got exactly that expression.

One error of description. `phase_1/C4_TARGET_RECONSTRUCTION.md` §4 reason 1 says the thresholds "belong to different
cells over **disjoint** drift ranges". They are not disjoint: they are adjacent closed intervals sharing
`e = 1.9839101`. Nothing in the arithmetic is wrong — but the consequence is worth stating, because the campaign
does not: the number C4 certifies for cell 309 is evaluated exactly at the shared endpoint, so it is *simultaneously*
a valid lower bound on Λ_308 (it is literally the same number as the 308 evaluation at `e_hi`, 3.297250282). The
same mistake is baked into mutant M06 (OTHER FINDINGS 1).

**Verdict: PASS_WITH_NOTES.**

## C. Is the A0 / E_a[τ] relationship stated in the correct DIRECTION?

Checked against `level4/closure_proofs/p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md`.

§4 Lemma Dv ends: "and |[R f](a)| ≤ A0 ‖f‖ with A0 = τ / D_lo". A0 is an **upper** bound on the order-0
amplification at the atom. §3 Lemma SM(d): "sup_{‖f‖ ≤ 1} |[(I − K_e)⁻¹ f](a)| = τ_a / D_e = E_a[τ] (attained at
f = 1)". Hence admissibility ⟺ `A0 ≥ sup_cell E_a[τ]`, and a certified **lower** bound on `E_a[τ]` is a floor under
every admissible A0. Not reversed. C4 states it this way in Phase 1 §1, in the gate's `admissible_family.floor`,
and in the module docstring of `c4_lower_bound.py`.

I checked it separately for each of the three supplies the gate claims to cover:
* Lemma G, `A0 = C_upper`: `C_upper ≥ sup_cell ‖(I−K_e)⁻¹‖`, and OPERATOR_AUDIT §4 gives
  `‖(I−K)⁻¹‖ = sup_x E_x[τ] ≥ E_a[τ]` for positive operators on B(X). ✓
* Lemma Dv', `A0 = Ā_eff = min(Ā, τ/D_lo)`: `Ā ≥ sup_E E_a[τ]` is a hypothesis, and `τ ≥ τ_a(e)`, `D_lo ≤ D_e`
  give `τ/D_lo ≥ E_a[τ](e)`; a min of two valid upper bounds is a valid upper bound. ✓
* C3's operator-mixed supply: componentwise min of the above. ✓

The consequence note under SM(d) ("No decomposition improves the order-0 bound … from a residual *norm*") is exactly
the C3 knockout C4 is trying to make quantitative, and C4 uses it the way the theorem states it.

**Verdict: PASS.**

## D. Is Lemma SM(d) used correctly?

Yes. SM(d) is quoted with its two load-bearing parts intact — that the supremum *equals* `E_a[τ]`, and that it is
*attained at f = 1*. The attainment is what lets Phase 1 upgrade "admissibility implies A0 ≥ Λ" to
"admissibility is equivalent to A0 ≥ Λ", and C4 does lean on the equivalence and is entitled to.

The order of quantifiers is handled correctly: SM(d) is sharp at a single `e`; C4 takes the sup over the cell of a
pointwise-sharp quantity, and then only ever uses the weakening `Λ_k ≥ E_a[τ](e*)`.

Two defects of statement, neither of which changes a number:

1. `c4_model_identity.py` and Phase 1 §2 describe the state space as `[0, H]²`. That is the ambient box, not the
   operator's state space. OPERATOR_AUDIT §1 defines the reachable closure `X = {(p,m) ∈ [0,5]² : p = 0 or m = 0 or
   p + m ≤ h − 2k = 4}`, and SM(d) is a statement about `B(X)`. This is harmless here — the chain started at
   `a = (0,0)` never leaves `X`, `T` maps `X` into `X`, and theorem L's argument is pathwise, so `E_a[τ]` is
   identical under either description — but it is a mis-statement of the frozen operator inside the one module whose
   entire job is to state the model exactly, and it should be corrected rather than left for a later reader to trip on.
2. A mis-citation of Lemma T; see item E(v).

**Verdict: PASS_WITH_NOTES.**

## E. Is the candidate lower-bound theorem SOUND?

### E.0 Model identification — verified independently from the frozen producer

Read `level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/cusum_layer1.py` directly (sha256
`efcc0f36632632577a24c4ddf1a7c2c3579d471cdba5a752dd72c708667cdc79`, which matches the pin), cross-read against
OPERATOR_AUDIT.md §1–2.

* `K_FROZEN = 0.5`, `H_FROZEN = 5.0`, `C_CUSUM = H_FROZEN + K_FROZEN = 5.5`. OPERATOR_AUDIT independently gives
  `h = 5, k = 1/2, c = h + k = 11/2`.
* `ell, upper = m - C_CUSUM, C_CUSUM - p` is the **survival** window for `z`; the kernel integrates `z` over
  `[ell, upper]`. So alarm ⟺ `z > C − p` ⟺ `p + z − K > H`, or `z < m − C` ⟺ `m − z − K > H`.
  **The threshold is H = 5, not C = 5.5.** The campaign has this right, and `c4_model_identity` pins the literal
  line plus `C_CUSUM = H_FROZEN + K_FROZEN` so the identification cannot drift silently.
* `wp = _basis(max(0.0, p + z - K_FROZEN), …)`, `wm = _basis(max(0.0, m - z - K_FROZEN), …)` ⟹
  `s+ ← max(0, s+ + z − K)`, `s− ← max(0, s− − z − K)`. Matches.
* `y = z + drift`, `dens ∝ exp(−y²/2)` ⟹ `z` has density `φ(z + e)`, i.e. `z ~ N(−e, 1)`. `E_excess`'s docstring
  works with `N(+e, 1)` and gives the correct reason (`|z|` has the same law under either sign). Not an error.
* `h1[row] = 1 - Phi(au) + Phi(al)` with `au = upper + drift`, `al = ell + drift` is `P(z > upper) + P(z < ell)`
  under `z ~ N(−e,1)` — the one-step alarm probability. Consistent with `K_e 1 = 1 − h_1`.
* `nodes = 0.5 * H_FROZEN * (1.0 - x)` with `x = cos(πj/12) ∈ [−1,1]` places nodes on `[0, H]` with `nodes[0] = 0`,
  so the atom `(0,0)` is row 0. OPERATOR_AUDIT confirms the evaluation point is `x0 = (0,0)`.
* `K_e` is positive and sub-Markov, so `(I − K_e)⁻¹1(x) = Σ_j P_x(τ > j) = E_x[τ]`, as THEOREM_AD §3 states.

**No mis-identification.** Threshold, reference value, alarm rule and innovation law are all as the campaign states.
The one inaccuracy is the state space (item D note 1), which does not touch the bound.

### E.1 The proof, step by step

(i) **Pathwise domination.** `s ≥ 0` and `max(0, s + z − K) ≤ s + (z−K)⁺`, so by induction from `s±_0 = 0`,
`s+_t ≤ Σ_{i≤t}(z_i−K)⁺` and `s−_t ≤ Σ_{i≤t}(−z_i−K)⁺`. Correct. The induction is only valid while the clipped
update is actually taken, i.e. for `t ≤ τ−1`, which is all the argument needs.

(ii) **The per-step majorant.** `(z−K)⁺ ≤ (|z|−K)⁺` and `(−z−K)⁺ ≤ (|z|−K)⁺` hold trivially, because `±z ≤ |z|` and
`x ↦ (x−K)⁺` is nondecreasing. The docstring instead writes: "K > 0 makes (z − K)⁺ and (−z − K)⁺ never simultaneously
positive, **so** each is at most V_i". The disjointness claim is true (`z > K` and `z < −K` are incompatible for
`K > 0`) but it is not what implies "each is at most V_i"; the "so" is a non sequitur. **The conclusion is correct
and the theorem is unaffected.** Disjointness *is* genuinely needed — and is correctly used — one level down, in
`E_excess`, to write `E[(|z|−K)⁺]` as the sum of the two one-sided expectations. The docstring should either drop
the clause or move it to where it does work.

(iii) **Boundary convention.** At the alarm step the *unclipped* value strictly exceeds `H`, and that unclipped value
is `s±_{τ−1} ± z_τ − K ≤ Σ_{i≤τ−1}V_i + V_τ`. So `H < Σ_{i≤τ}V_i`. With `H = 5` (verified in E.0), the convention is
right. Whether the alarm is `>` or `≥` is immaterial: `z` is continuous.

(iv) **Wald.** `V_i = (|z_i|−K)⁺` are i.i.d. (the `z_i` are), non-negative, and integrable (`V ≤ |z|`). `τ` is a
stopping time for `σ(z_1,…,z_t)` because the alarm at step `t` is a function of `z_1,…,z_t`, so
`{τ ≥ i} = {τ ≤ i−1}ᶜ ∈ σ(z_1,…,z_{i−1})` is independent of `V_i`. Tonelli then gives
`E[Σ_{i≤τ}V_i] = Σ_i E[V]P(τ ≥ i) = E[V]E[τ]`, **valid in [0,∞] and therefore not requiring `E[τ] < ∞` at all**.
`E[V] > 0` since the Gaussian has unbounded support. Divide: `E_a[τ] ≥ H / E[(|z|−K)⁺]`. Sound.

(v) **The one real error in the proof text.** The docstring justifies `E[τ] < ∞` with "Lemma T gives
`E_x[tau] <= C_T < infinity`". That is wrong. THEOREM_AD §2 Lemma T bounds `‖Ĝ_e‖ = ‖Ĝ_e 1‖ ≤ C_T`, and the same
section records `Ĝ_e 1(x) = E_x[τ ∧ T_a]` — the **taboo** time, killed on return to the atom, which is a different
and smaller random variable than `τ`. Finiteness of `E_a[τ]` *is* available, twice over: from the whole-kernel
supersolution paragraph in §4 (`W ≥ 1 + K_e W` ⟹ `E_a[τ] ≤ W(a) = Ā`), or from SM(d) with `τ_a ≤ C_T` and
`D ≥ D_lo > 0`. Because of (iv) the hypothesis is not needed anyway, so this is **non-blocking** — but as written the
proof cites a bound on the wrong random variable, and that must be corrected before the certificate is published.

(vi) **Which point.** `dE[V]/de = Φ(e−K) − Φ(−(e+K)) ≥ 0`: I differentiated
`E[(z−K)⁺] = (e−K)Φ(e−K) + φ(e−K)` and `E[(−z−K)⁺] = −(e+K)Φ(−(e+K)) + φ(e+K)` under the integral and obtained
exactly that. So the bound decreases in `e` and `e_lo` is optimal among admissible points. The producer also
exercises it on a 25-point ladder.

### E.2 Is the claimed bound actually true? (independent numerical check)

Monte-Carlo of the chain as identified in E.0, 2,000,000 paths, exact alarm rule, start at `(0,0)`:

| cell | e_lo | certified lower bound | simulated `E_a[τ](e_lo)` | slack |
|---|---|---|---|---|
| 308 | 1.8824130 | 3.512733596 | 4.31108 ± 0.00102 | +22.7 % |
| 309 | 1.9839101 | 3.297250282 | 4.04806 ± 0.00092 | +22.8 % |

The bound holds comfortably and is a genuinely loose minorant (it captures about 81 % of the truth). Nothing here
is knife-edge at the level of the mathematics.

**Verdict: PASS_WITH_NOTES** — the theorem is sound and the model identification is correct; the Lemma T
mis-citation (E.1.v) and the non sequitur (E.1.ii) must be repaired in the text.

## F. Are the inputs already certified / committed?

Three pinned inputs; I recomputed all three sha256 and they match the evidence exactly:

```
efcc0f36632632577a24c4ddf1a7c2c3579d471cdba5a752dd72c708667cdc79  .../p5y_k1_cover_ledger_implementation/code/cusum_layer1.py
341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f  .../p5y_k1_cover_ledger_successor/config/cells.json
87bb1cfacb09c2a144cab0270427d91980ea742b36fd80f8963265a22d2eebb3  .../p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json
```

`c4_model_identity.py` refuses on a sha mismatch *and* on the disappearance of any of seven literal model-defining
lines plus the `C_CUSUM = H_FROZEN + K_FROZEN` definition. `K` and `H` are parsed out of the pinned source rather
than transcribed. The cell endpoints are cross-checked between the cover ledger and the C1 registry with a refusal
on disagreement. The Γ evaluation loads the frozen consumer stack (`c2_d5_forecast` → `tail_forecast_r2` →
`tct_rule`/`tc_rule` → `deflated_consume`, pinned by `DC_SHA` → `c3_selector`) and committed evidence
(`ADOPTED_TAIL_INPUTS.json`, `TCT_INPUTS_*.json`, `REGISTRY_C1/C2.json`, `cells.json`).

Reproducibility, measured rather than assumed: I re-ran `c4_lower_bound.py` and got `evidence/phase3/C4_BOUND_PHASE3.json`
**byte-identical** to the committed file, and `c4_thresholds.py` value-for-value against `evidence/phase1/C4_THRESHOLDS.json`.

Two caveats:
* Phase 0 is **not** reproducible at the current HEAD — see OTHER FINDINGS 5.
* The `DIAGNOSTIC_true_E_a_tau_at_e0` values are float candidate values read out of committed artifacts. They are
  committed but not certified; they are correctly labelled as such and nothing load-bearing leans on them (item on
  308 below).

**Verdict: PASS_WITH_NOTES.**

## G. Is any new-real computation hidden in the route?

**Import audit.** The whole C4 code set imports only `argparse, json, sys, re, hashlib, importlib.util, subprocess,
fractions, pathlib`. The only `subprocess` use is `c4_phase0_audit.py`'s local `git -C <repo> …`. No `numpy`, no
`python-flint`, no Arb, no `socket`/`urllib`/`requests`/`http`/`ssh`/`paramiko`. The frozen consumer stack it loads
(`c2_d5_forecast.py`, `c3_selector.py`, and the modules they load) is likewise `Fraction`-only. No kernel is
evaluated, no operator certification is run, no host is contacted. I ran every runnable producer to completion on a
host that has neither numpy nor flint installed, which is itself a strong negative test.

One honesty note: `kernel_evaluations: 0`, `operator_certifications_run: 0`, `remote_hosts_contacted: 0` are literal
constants in the emitters, not measured counters. They are *true* — I verified by static and dynamic means — but
they are asserted, not instrumented, and a reader should not take them as evidence.

**`c4_rigorous_gaussian.py` — are the remainder bounds proved, and checked at run time?**

* **exp.** `S_N = Σ_{n≤N} y^n/n!`, `0 < e^y − S_N ≤ y^{N+1}/(N+1)! · 1/(1 − y/(N+2))` for `y < N+2`. I re-derived it
  (the tail `Σ_{k≥0} y^k (N+1)!/(N+1+k)!` is dominated by the geometric series with ratio `y/(N+2)`) — correct, and
  the loop leaves `p` equal to `y^{N+1}/(N+1)!` exactly as the bound requires. Guard fires on `y ≥ N+2` and on `y < 0`.
* **I(t) = ∫₀ᵗ e^{−u²/2}du = Σ(−1)ⁿ t^{2n+1}/(2ⁿ n! (2n+1)).** Series correct. `|a_{n+1}/a_n| = t²(2n+1)/(2(n+1)(2n+3))`
  is decreasing in `n` and `< 1` for `n ≳ t²/2`, so magnitudes decrease monotonically to zero from that index onward
  *for ever* — the alternating bound is genuinely proved, not just observed. The run-time guard (locate the turning
  index, refuse if it is within 2 of the truncation point, verify monotone decrease over the whole kept tail, verify
  the first omitted term does not exceed the last kept term) correctly checks the hypothesis over the range it can
  see. The returned `Iv(s − nxt, s + nxt)` is conservative by a factor 2 relative to the sharp bracket — fine.
* **π by Machin**, `π/4 = 4·arctan(1/5) − arctan(1/239)`, each arctan by its alternating series with the
  first-omitted-term bound (valid at every index for `0 < x < 1`). ✓
* **sqrt by integer square root with outward rounding.** I verified the direction algebraically. With
  `n = ⌊x·2^{2S}⌋` and `r = ⌊√n⌋`: `r/2^S ≤ √x` gives the lower end; and `(r+1)² > n` ⟹ `(r+1)² ≥ n+1` ⟹
  `r+1 ≥ √(n+1) ≥ √(x·2^{2S})` gives the upper. Correct.
* **`_out`** uses floored `divmod`, so it rounds down for `lo` and up for `hi` including for negative arguments; and
  every `Iv` operation reconstructs through the constructor, so every intermediate is re-rounded outward.
* **Division direction, which is the one that matters here.** `Iv.__truediv__` takes `min`/`max` over the four
  corners, so `Iv(H,H) / EV` has `lo = H / EV.hi`. The **upper** bound on `E[(|z|−K)⁺]` produces the **lower** bound
  on `H/E[…]` — the safe direction for this use. Confirmed in code and numerically (below).

**Trying to break it.** I fed thirteen out-of-domain inputs. Twelve fired the intended `Refusal`:
`exp_neg(y<0)`, `exp_neg(y ≥ N+2)`, `_erf_integral(t<0)`, `_erf_integral` truncated at 2 terms ("the alternating
series has not entered its decreasing regime"), `_atan_small(x ≥ 1)`, `_atan_small(0)`, `sqrt_iv` of a non-positive
interval, `sqrt_iv` of an interval that underflows the grid, division by a zero-containing interval,
`E_excess(K = 0)`, `E_excess(K < 0)`, `Iv(2,1)`. `Φ(30)` is refused outright rather than answered wrongly. One did
not: `_isqrt(0)` raises `ZeroDivisionError` rather than a `Refusal` — unreachable through `sqrt_iv`, which refuses
`v.lo ≤ 0` first, so cosmetic.

**Independent correctness check.** I re-implemented Φ, φ, π at 160 decimal digits sharing nothing with the module:
`I(t) = e^{−t²/2} · Σ_{n≥0} t^{2n+1}/(2n+1)!!` (an all-positive, cancellation-free identity) and π by the
Gauss–Legendre AGM. **Every interval the module returns contains my reference** — at Φ(1), Φ(1.4839101),
Φ(2.4839101), Φ(3), Φ(5), φ(0), φ(1.4839101), φ(2.4839101), π and √(2π) — with residual disagreements of order
1e-97, i.e. at the 2⁻³²⁰ grid. `E_excess` contains my reference at all four `e_lo`, and in every cell
`B_lo ≤ H / E[V]_true` exactly. (My first reference, a Decimal Romberg, disagreed at 1e-39; raising its precision
made the disagreement vanish, confirming the reference, not the module, was the limiting factor. I report this
because a reviewer who stopped at the first reference would have filed a false alarm.)

**Verdict: PASS.**

## H. Was the prospective gate frozen BEFORE the result?

**Formally, yes.** `376950be` is a single commit touching one file, `config/FEASIBILITY_GATES_C4.json`, 108
insertions. `git ls-tree -r 376950be` over the namespace lists exactly the Phase 0–3 artifacts and the code: no
certificate, no mutation output, no adjudication artifact. The gate's own sha256 (`d5b5b385…`) is pinned in
`c4_certificate.py`, which refuses to run against any other gate.

**In substance, it is retrospective, and the gate says so.** The freeze commit comes *after* `c9b06abf`, which
already contains `evidence/phase3/C4_ROUTES.json` with every cell's bound, every Γ at the bound and every
`excludes_cell` boolean. The outcome was fully determined before the gate existed. `prior_evidence_known_at_freeze`
discloses the bounds, the Γ values, the bisected critical A0s, the diagnostics and the expected class.

**Are the classes fitted?** I do not think so, and I looked hard.
* The four-way partition INVALID / PASS / PARTIAL / FAIL_INCONCLUSIVE is the natural exhaustive trichotomy plus a
  premise-failure class. Nothing about it is shaped to the answer.
* The one place to suspect fitting is the carve-out "cells that already close at A1 = A2 = 0 with A0 as certified
  are OUTSIDE the PASS/PARTIAL count". It happens to remove exactly 306 and 307, which are exactly the cells the
  campaign knew would otherwise count against it. But the carve-out is **logically forced**, not fitted: if
  `Γ(A0_certified, 0, 0) < 0` then A0 is not what keeps the cell open, so no floor under A0 can bear on it. A gate
  that counted those as failures would be measuring the wrong thing. It matches 306/307 because that is the fact.
* The exclusion test is written as a direct evaluation `Γ(B,0,0) ≥ 0` rather than a comparison against a bisected
  critical value. That is genuinely good design: it removes the one place where a rounding direction could have been
  chosen to suit the answer, and I confirmed the certificate implements exactly that on exact `Fraction`s.

**But the gate cannot discriminate.** With 306/307 carved out, 308 known (from C4's own disclosed diagnostics) to be
unreachable, and Γ = +0.004661 at 309 already disclosed, PASS was unattainable and FAIL_INCONCLUSIVE was already
ruled out. PARTIAL was the only reachable class, and the gate names PARTIAL as the expected class. So the freeze has
essentially **no prospective evidential value**. Its real value — which is not nothing — is that it binds the
exclusion test, the domain requirement, the permitted conclusions and the refusals before the certificate is
written, and those are mechanical and enforceable.

The adjudication should describe the freeze as *a binding statement of what the result is allowed to mean*, not as
*a pre-registration of what the result would be*. As long as it does, I have no objection.

**Verdict: PASS_WITH_NOTES.**

## I. Is the claimed exhaustion scope neither too broad nor too narrow?

**As emitted by the machinery: correct.** `c4_certificate.py` writes `family_exhausted` = the gate's
`admissible_family.definition` verbatim, and under PARTIAL it writes the PARTIAL `permitted_conclusions`, which
include "no R-stage consequence of any kind". The certificate produces no coverage map and touches none; the gate's
`r6_rule` ("excluding a cell removes a ROUTE, not the cell; the cell stays open in r5") is exactly the right framing.

**The family boundary is drawn in the right place, and the right escape hatch is named.** `does_not_cover` includes
"a route that bounds the order-0 point value by something other than a norm-only argument". That matters: a
certificate that bounded `|[R f](a)|` for the *particular* residual `f` rather than uniformly over `‖f‖ ≤ 1` would
sit legitimately below `E_a[τ]` and escape the floor entirely, because SM(d)'s sharpness is attained at `f = 1` and
says nothing about a specific `f`. The gate names this; the campaign must keep naming it.

**306 and 307 are handled correctly.** Named, kept outside the count, given the reason, and `critical_A0: null`
rather than a meaningless number. Nothing implies A0 is their blocker.

**Too broad in two places in the prose, both outside the machinery:**
* `README.md` asks whether there is a bound "strong enough to prove that **no operator-level certificate** can ever
  close the remaining tail cells" — unqualified, and read literally it is exactly the claim the `does_not_cover`
  clause forbids.
* `phase_3/C4_CANDIDATE_ROUTES.md` line 62: "The set of cells this campaign can discharge is therefore `{309}` under
  route L and **`{309}` under any route**." In context "any route" means any lower-bound route, and its support at
  308 is a float diagnostic; as written it reads as unrestricted. Compare the same file's careful hedge fifteen
  lines later ("Measured, not asserted").

**One gap against the gate's own requirement.** Under PARTIAL the gate requires: "for every non-excluded cell the
report must say which of the two reasons applies: the bound is too weak, or the threshold is unreachable because it
exceeds the truth." The Phase 6 producer emits no such field for 308. Whoever writes Phase 8 must supply it — and
must say honestly that the *certified* answer is "the bound is too weak", while "the threshold exceeds the truth"
rests on uncertified float diagnostics (corroborated, see OTHER FINDINGS 8, but not certified).

**Verdict: PASS_WITH_NOTES.**

---

## OTHER FINDINGS

**1. Mutant M06 does not do what it says, and is NOT DETECTED.** `c4_mutations.py` describes M06 as "each cell is
certified at the NEXT cell's left endpoint, **outside its own closed cell**". The cells are adjacent *closed*
intervals, so cell k's successor's `e_lo` *is* cell k's own `e_hi` and lies **inside** the closed cell. The domain
guard in `c4_certificate.evaluate` therefore never fires, and because the map sends `309 → 309`, cell 309 — the only
excluded cell — is not perturbed at all. I ran it:

```
M06_shift       -> ((309,), (308,), 'PARTIAL')   *** NOT DETECTED ***
```

The mutant intended to exercise the gate's `domain_requirement` and exercises nothing. A mutant that actually tests
it would have to place `e` outside `[e_lo, e_hi]` — e.g. cell 309 evaluated at cell 307's `e_lo`.

**2. Mutant M05 crashes the entire Phase 7 run.** `evaluate(gate, K_override=F(0))` reaches
`G.E_excess(e, 0)`, which raises `c4_rigorous_gaussian.Refusal`. `c4_mutations.main` catches only `SystemExit` and
`TypeError`, so the exception propagates and the run dies with a traceback — before M06–M12 are even reached. Run:

```
M05 *** UNCAUGHT-BY-SUITE *** Refusal the CUSUM reference value K must be positive
```

As committed, `c4_mutations.py` cannot complete.

**3. Three further mutants are NOT DETECTED, and one of them matters.** Driving `evaluate` directly:

```
M01_reversed  -> ((308,), (309,), 'PARTIAL')             DETECTED
M02_strict    -> ((309,), (308,), 'PARTIAL')             *** NOT DETECTED ***
M03_upper     -> ((309,), (308,), 'PARTIAL')             *** NOT DETECTED ***
M04_H=11/2    -> ((309,), (308,), 'PARTIAL')             *** NOT DETECTED ***
M07_e_hi      -> ((), (308, 309), 'FAIL_INCONCLUSIVE')   DETECTED
M08_knockout  -> ((308, 309), (307,), 'PARTIAL')         DETECTED
```

So 4 of 8 certificate-layer mutants are undetected, against the suite's own stated rule: "A mutant that changes
nothing must be PROVED EQUIVALENT in the table, with the reason; 'it happened not to matter' is not a reason."
* M02 (`>` vs `≥`) is not equivalent — it differs exactly when Γ = 0. It happens not to matter because Γ = +0.004661.
* M03 (upper end of the interval as the bound) differs by ~1.9e-95, far below any threshold. Not equivalent in
  principle; undetectable in practice.
* **M04 is the serious one.** Taking the alarm threshold as `C = 11/2` instead of `H = 5` makes the bound *larger*
  (3.627 instead of 3.297 at 309) — i.e. a mis-identification of the threshold in the **unsound** direction is
  invisible to this suite. The suite therefore provides no protection at all on the single point item E calls the
  most important, and the correctness of `H = 5` rests entirely on reading `cusum_layer1.py`. (I did read it; it is
  right. But the suite should not be credited with having checked it.)

The arithmetic mutants M09 and M12 are "detected" only in the sense that the bound *moves*, by ~1e-96 and ~1e-12
respectively — neither could ever flip a verdict. That should be stated rather than reported as a detection.

**4. `c4_mutations.py`'s independence claim is false.** Docstring: "recomputed by a SECOND, independent
implementation that **shares no function** with `c4_rigorous_gaussian`"; the emitted JSON repeats "shares no function
with the production power-series path". In fact `_pi_alt` calls `G._atan_small` (the production arctan **power
series**), `_phi_alt` calls `G.exp_neg` (the production exp **power series**) and `G.sqrt_iv`, and `_Phi_alt` calls
`G.exp_neg`, `G.sqrt_iv` and `G.Iv`/`G._out`. What is genuinely independent is the erf path (series → Simpson) and
the π identity (Machin → Euler). Nothing else. I ran the reproduction block: it passes, and the production interval
sits inside the alternative interval in all four cells — but the alternative intervals are 2.0e-13 to 4.3e-13 wide
against the production's 8.0e-96, so the cross-check has resolution ~1e-13. That is a real check (it would catch any
gross error) and should be described as one, not as an independent reproduction at certificate precision. Related:
`_Phi_alt`'s Simpson remainder takes `sup|f''''|` as a **float** max over grid points, described in the docstring as
"a fine grid with an interval guard" — it is neither an interval nor a guard. (The value is conservative in fact:
dropping the `e^{−u²/2}` factor is safe, and `int(M)+1` rounds up.)

**5. Phase 0 is not reproducible at the current HEAD.** Re-running `c4_phase0_audit.py` now yields
`MATERIAL_MISMATCH_STOP`: check `10_zero_new_real` is false, because it asserts `git diff --name-only ae4cbc2c HEAD`
contains no path outside the C3 namespace — which necessarily breaks as soon as C4 commits its own files. Checks
1–9 and 11–12 still pass. The check conflates two different things under one name ("zero new-real scientific
addresses" and "no repository path changed outside the C3 namespace"). Either split it, or scope the diff to exclude
C4's own namespace, or state in the README that Phase 0 is a one-shot audit of the starting state. Also minor:
several `git` calls use `subprocess(..., check=True)` and then compare stdout to `""`, so `merge-base --is-ancestor`
failures surface as a `CalledProcessError` traceback rather than a `False` check.

**6. Unverified universal self-descriptive claims.** You asked specifically. Three:
* `README.md`: "Reproduce any number by running its producer in `code/`; **each refuses unless its pinned inputs
  match**." `c4_prior_evidence.py`, `c4_routes.py` and `c4_thresholds.py` have no pin of their own and refuse
  nothing; `c4_phase0_audit.py` does not reproduce at all (finding 5). No check exists for this claim.
* `README.md`: "`main`, the coverage maps r4 and r5, and **the AWS SR/PS1 estate** are untouched." `main` and the
  maps are checked (Phase 0 checks 4, 5, 8 — all pass on my re-run). The AWS estate is not checked and *cannot* be,
  since the gate forbids contacting it. Drop the clause or mark it as a statement about C4's own actions rather than
  about the estate's state.
* `c4_rigorous_gaussian.py`: "**No float is used in any value that reaches a certificate**", echoed by Phase 3's "No
  float reaches a certified value". The certificate JSON carries `Gamma_at_bound`, `lower_bound_float`,
  `A0_certified_float` and `slack_over_critical_percent` as floats. None is load-bearing — the exclusion decision is
  taken on exact `Fraction`s, which I verified — but the claim is absolute and the artifact contradicts it. Say
  "no float enters any load-bearing comparison" and it becomes true and checkable.

Also worth a line: Phase 2's sweep covers `*.json` and `*.py` only. Its own text says so accurately, but the
conclusion drawn ("NO committed certified quantity lower-bounds `E_a[τ]`") is universal over a corpus that includes
`.md` theorem texts — `THEOREM_AD.md` and `PRIOR_ART.md` among them — which were never swept.

**7. A transcribed constant, in the one producer that should not have one.**
`c4_certificate.monotone_check(..., F("1701923/1000000"), F("2092283/1000000"))` hardcodes the ladder endpoints.
Cell 306's actual `e_lo` is `680769/400000 = 1.7019225`, so the hardcoded lower end is 5e-7 *above* the true left
edge of the universe. Harmless (the monotonicity is global, and I verified it), but `c4_lower_bound.monotone_check`
derives the same endpoints from `cell_geometry()`, and Phase 1 opens with "none is transcribed".

**8. The cell-308 "can never be excluded" claim — correctly labelled, independently corroborated, but the disclosed
diagnostic is not the decision-relevant one.** Labelling: correct. `C4_ROUTES.json` carries
`DIAGNOSTIC_note` ("measured, not asserted … nothing in the gate or the certificate depends on them"), the gate
carries `diagnostic_status` with the same words, and I confirmed by running the certificate that no gate class, test
or conclusion consumes them. Nothing load-bearing leans on them.

Corroboration: my own 2,000,000-path Monte-Carlo gives `Λ_308 = E_a[τ](e_lo = 1.882413) = 4.31108 ± 0.00102`
(95 % CI [4.30909, 4.31307]) against the exclusion threshold 4.375228833136. The gap is 0.0641, about 63 standard
errors. The campaign's claim is almost certainly true.

The presentational problem: the gate discloses `diagnostic_true_E_a_tau_at_midpoints` = 4.17430 for 308, which
against 4.375229 looks like 4.8 % of headroom. But the quantity that decides excludability is
`Λ_308 = sup_{cell} E_a[τ] = E_a[τ](e_lo)` = 4.311, which leaves **1.5 %**. Phase 1 §5 does do this interpolation
correctly ("about 4.315") — the *gate*, which is the frozen document a later reader will consult, discloses only the
midpoints. If the claim is going to be repeated, repeat it with the endpoint number.

One more precision point on the same passage. Phase 1 §5 offers the diagnostic-free restatement: "a certified upper
bound on `Λ_308` below 4.375229 would itself be an admissible `A0` that closes cell 308 at `A1 = A2 = 0`. So '308
cannot be excluded' and '308 can be closed under the knockout' are the same statement." That is right, and it is the
strongest thing said about 308 — but "closed under the knockout" is not closure: the knockout sets `A1 = A2 = 0`,
which no real supply achieves. The sentence "one of them is progress" should not be allowed to drift into "308 is
closable" in the adjudication.

**9. The `licence` ladder stops at the certified A0.** The gate requires the monotonicity licence to be "exercised
per cell, not assumed". `c4_certificate.evaluate` exercises it on 17 points spanning `[B_k, A0_certified]`. But an
admissible `A0` is *any* valid upper bound and can be arbitrarily larger than the certified one, so the exclusion
argument needs `Γ(A0,0,0) ≥ 0` for all `A0 ≥ B_k`, not just up to `A0_certified`. I checked the unexercised region
myself out to `A0 = 10^5`: Γ is nondecreasing throughout and the TC-T/K5-B intersection stays non-empty, saturating
at +0.288317 (308) and +0.374145 (309). **The licence holds**; the campaign simply has not exercised the part of the
range its own argument ranges over. Extending the ladder past the certified A0 costs nothing.

**10. Is the thin 309 margin real and rigorous, or does it depend on a rounding direction? It is real, and no
rounding direction is load-bearing.** The numbers:

| quantity | value |
|---|---|
| certified lower bound `B_309` | 3.297250281519544 |
| bisected critical A0 (reported only) | 3.2142360226778806 |
| slack | +2.5827 % |
| `Γ(B_309, 0, 0)` | +0.004661129657978107 (exact `Fraction`; sign is exact) |
| width of the `E_a[τ]` enclosure at 309 | 1.87e-95 |
| true `Λ_309` (my MC, 2e6 paths) | 4.04806 ± 0.00092 |

Three independent reasons the margin does not rest on rounding:
* The arithmetic uncertainty is 1.9e-95 against a gap of 0.083 — a ratio of about 10⁹⁴. No rounding decision
  anywhere in the module can move the verdict.
* The rounding **direction** is nonetheless correct at every step, and I checked it rather than assuming: `_out`
  rounds `lo` down and `hi` up under floored `divmod` (including for negatives); every `Iv` operation reconstructs
  through the constructor; `Iv(H,H)/EV` takes `lo = H/EV.hi`, so the *upper* bound on `E[(|z|−K)⁺]` yields the
  *lower* bound on `H/E[…]`; and against my 160-digit cancellation-free reference, `B_lo ≤ H/E[V]_true` holds
  exactly in all four cells.
* The load-bearing test is `Γ(B,0,0) ≥ 0` evaluated directly on exact rationals, so the bisected critical value —
  the only rounded object in sight — never enters. I confirmed this in the code and by running it.

The margin is thin only in the sense that the *bound* is loose: `B_309 = 3.297` captures 81 % of the true 4.048,
and the threshold is 3.214. The mathematics has 26 % of room; the route consumes 23 % of it and leaves 2.6 %. That
is a statement about the quality of the Wald minorant, not about arithmetic.

**11. Phase 7 will be slow.** The independent-reproduction block took about 17 minutes on this host (composite
Simpson with 2048 panels in exact `Fraction`s, ~0.028 s per `exp_neg` node, and `_pi_alt(600)` recomputed inside
every `_Phi_alt`/`_phi_alt` call). Not a defect; budget for it, or hoist `_pi_alt` out of the inner functions.

**12. For the record, the result I obtained.** Running `c4_certificate.py` into my scratchpad gives
`C4_CLASS = PARTIAL`, `excluded = [309]`, `not_excluded = [308]`, `outside_the_count = [306, 307]` — matching the
gate's disclosed `expected_class` exactly. Γ at the bound: 306 −0.143881163, 307 −0.092985288, 308 −0.040467543,
309 +0.004661130. All four `e_in_closed_cell` true, all four `licence` sub-checks true.

---

## Summary of verdicts

| item | verdict |
|---|---|
| A thresholds | PASS |
| B domains / quantifiers | PASS_WITH_NOTES |
| C A0 / E_a[τ] direction | PASS |
| D Lemma SM(d) | PASS_WITH_NOTES |
| E lower-bound theorem soundness | PASS_WITH_NOTES |
| F inputs committed / certified | PASS_WITH_NOTES |
| G no hidden new-real; rigorous Gaussian | PASS |
| H gate frozen before the result | PASS_WITH_NOTES |
| I exhaustion scope | PASS_WITH_NOTES |

No blocking FAIL. The theorem is sound, the model is correctly identified (threshold `H = 5`, reference `K = 1/2`,
alarm on the unclipped update, innovation `z ~ N(−e,1)`, atom `(0,0)`), the arithmetic is verified to ~96 digits
against an independent implementation, the rounding direction is safe for this use, the 309 exclusion does not
depend on any rounding, and nothing new-real, no kernel and no remote call is hidden in the route.

The notes the campaign must address before the certificate is adjudicated:
(a) the Lemma T mis-citation in the theorem L proof (E.1.v) and the non sequitur in the per-step majorant (E.1.ii);
(b) the state space `[0,H]²` vs the reachable closure `X` (D.1);
(c) the Phase 7 suite: M05 crashes it, M06 tests nothing, M02/M03/M04 are undetected against the suite's own rule,
    and the "shares no function" independence claim is false (findings 1–4);
(d) the three unverified universal self-descriptive claims, plus the `.md`-free Phase 2 sweep (finding 6);
(e) the over-broad "no operator-level certificate" / "under any route" phrasings (item I);
(f) the missing per-cell reason for non-excluded cell 308 that the gate's PARTIAL clause requires (item I);
(g) the licence ladder that stops at the certified A0 (finding 9) — cheap to extend, and it does hold;
(h) Phase 0's non-reproducibility and the conflated check 10 (finding 5);
(i) the gate's midpoint-only diagnostic disclosure for 308, where the endpoint value is the decision-relevant one
    and leaves 1.5 % rather than 4.8 % (finding 8);
(j) the freeze should be described as binding what the result may mean, not as a pre-registration of what it would
    be (item H).

HANDOVER: READY_TO_EVALUATE_WITH_NOTES
