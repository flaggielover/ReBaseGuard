# Independent fresh-context adjudication — P5Y / K5 Campaign C4

Adjudicator: fresh context, no prior knowledge of this programme. Working tree `/Users/suzhe/ReBaseGuard-k5c4`,
branch `p5y-k5-tail-c4`, HEAD `5c69be5c`, tree clean throughout. I modified nothing in the repository; every
artifact I produced lives in my scratchpad. I contacted no remote host and used neither the `rebaseguard-aws` nor
the `rebaseguard-vultr` tools. I ran no Order3Certifier, no R-stage computation and no kernel certification.

**What I ran.** `c4_lower_bound.py`, `c4_certificate.py`, `c4_mutations.py`, `c4_phase0_audit.py` (all into
scratch); my own driver against the frozen consumer stack to recompute Γ at chosen triples, to bisect the critical
A0 independently, and to test monotonicity in A1 and A2; my own 2,000,000-path Monte-Carlo of the CUSUM chain as
identified from `cusum_layer1.py`; my own float quadrature and closed-form cross-check of `E[(|z|−K)⁺]`; and a set
of single-knob sensitivity probes on the measurement inputs. I read `THEOREM_AD.md` and `cusum_layer1.py` directly
rather than accepting the campaign's description of either.

Nothing below is taken on the campaign's word, and nothing is taken on the pre-result reviewer's word. Where I
agree with the reviewer I say so because I checked it myself; where the campaign's repairs did not land, I say so.

---

## 1. Is the lower bound VALID?

**Yes. Theorem L is correct, the model is correctly identified, the arithmetic is rigorous, and the premises are
met.** This is real mathematics, not a dressed-up numerical observation.

**The theorem.** `E_a[τ] ≥ H / E[(|z| − K)⁺]`. I checked every step rather than the shape of the argument.

* *Pathwise domination.* For `s ≥ 0`, `max(0, s + z − K) ≤ s + (z − K)⁺`: if `s + z − K ≤ 0` the left side is 0
  and the right is non-negative; otherwise `z − K ≤ (z − K)⁺`. Induction from `s±₀ = 0` gives
  `s⁺_t ≤ Σ_{i≤t}(z_i − K)⁺` and `s⁻_t ≤ Σ_{i≤t}(−z_i − K)⁺` for `t ≤ τ−1`, which is all the argument uses.
* *Per-step majorant.* `(z−K)⁺ ≤ (|z|−K)⁺` and `(−z−K)⁺ ≤ (|z|−K)⁺` because `±z ≤ |z|` and `x ↦ (x−K)⁺` is
  nondecreasing. The proof text now says exactly this; the earlier non sequitur via disjointness is gone, and
  disjointness has been moved to the one place it does work (writing `E[(|z|−K)⁺]` as a sum of two one-sided
  expectations, valid because `K > 0`). Repair landed.
* *The alarm step.* The unclipped value is `s±_{τ−1} ± z_τ − K ≤ Σ_{i≤τ−1}V_i + V_τ`, and it exceeds `H`, so
  `H < Σ_{i≤τ}V_i` pathwise. Whether the alarm is `>` or `≥` is immaterial for a continuous innovation.
* *Wald.* `{τ ≥ i} = {τ ≤ i−1}ᶜ ∈ σ(z₁,…,z_{i−1})`, independent of `V_i`; `V_i ≥ 0`; Tonelli gives
  `E[Σ_{i≤τ}V_i] = E[V]·E[τ]` **as an identity in [0,∞]**, so no integrability or finiteness hypothesis is needed.
  `E[V] > 0` because the Gaussian has unbounded support. Divide. The proof is complete and the finiteness
  hypothesis that the pre-result reviewer attacked has been removed rather than patched.

**Model identification.** I read `p5y_k1_cover_ledger_implementation/code/cusum_layer1.py` directly; its sha256 is
`efcc0f36…`, matching the pin, and `c4_model_identity.py` additionally refuses if any of seven literal
model-defining lines moves.

* `ell, upper = m − C_CUSUM, C_CUSUM − p` is the **survival** window over which the kernel integrates `z`. So
  alarm ⟺ `z > C − p` ⟺ `p + z − K > H`, or `z < m − C` ⟺ `m − z − K > H`. **The threshold on the statistic is
  H = 5, not C = 11/2.** This is the single most load-bearing identification in the campaign and it is right.
* `wp = _basis(max(0.0, p + z − K_FROZEN), …)`, `wm = _basis(max(0.0, m − z − K_FROZEN), …)` give the update.
* `y = z + drift`, `dens ∝ exp(−y²/2)` gives `z ~ N(−e, 1)`. `E_excess` works with `N(+e,1)` and states the
  correct reason (`|z|` has the same law under either sign). Not an error.
* `h1[row] = 1 − Φ(au) + Φ(al)` is the one-step alarm probability, consistent with `K_e 1 = 1 − h₁`.
* `nodes = 0.5·H·(1 − x)` puts the atom `(0,0)` at row 0.
* `K_e` is positive and sub-Markov, so `(I − K_e)⁻¹1(x) = Σ_j P_x(τ > j) = E_x[τ]`, as THEOREM_AD §3 states.

The state space is correctly described as the reachable closure `X` (the earlier `[0,H]²` mis-statement is
repaired); theorem L is pathwise from the atom and is unaffected either way.

**The premise, and its direction.** THEOREM_AD §4 Lemma Dv concludes `|[R f](a)| ≤ A0‖f‖` for every `e` in the
drift set, and §3 Lemma SM(d) states `sup_{‖f‖≤1}|[(I−K_e)⁻¹f](a)| = τ_a/D_e = E_a[τ]`, **attained at f = 1**. So
admissibility is *equivalent* to `A0 ≥ sup_cell E_a[τ] = Λ_k`, and a certified lower bound on `E_a[τ]` is a floor
under every admissible `A0`. The direction is right and is not reversed anywhere. I checked it separately for each
of the three supplies the gate claims to cover (Lemma G via `C_upper ≥ sup_x E_x[τ]`; Lemma Dv' via
`Ā ≥ sup_E E_a[τ]` and `τ/D_lo ≥ E_a[τ]`; C3's componentwise minimum of valid upper bounds).

**Arithmetic.** `fractions.Fraction` only, outward rounding onto a `2⁻³²⁰` grid. I re-derived each remainder bound:
the exp tail `y^{N+1}/(N+1)!·1/(1−y/(N+2))` dominated by a geometric series; the alternating `I(t)` series, whose
magnitudes decrease for ever once `n ≳ t²/2` so the first-omitted-term bound is genuinely proved, with a run-time
guard that locates the turning index and verifies monotone decrease over the kept tail; Machin's arctan; and the
integer-square-root enclosure (`r/2^S ≤ √x ≤ (r+1)/2^S`). `_out` rounds `lo` down and `hi` up under floored
`divmod`, including for negatives, and every `Iv` operation reconstructs through the constructor. Critically,
`Iv(H,H)/EV` takes `lo = H/EV.hi`, so the *upper* bound on `E[V]` yields the *lower* bound on `H/E[V]` — the safe
direction.

**Independent numerical corroboration (mine).**

| check | mine | campaign |
|---|---|---|
| `E[V]` at 309's `e_lo`, closed form with `math.erf` | 1.516415065009 | 1.516415065 |
| `E[V]` at 309's `e_lo`, 400k-point quadrature | 1.516415065016 | — |
| `Λ_309 = E_a[τ](1.9839101)`, 2e6-path MC | **4.04731 ± 0.00092** | bound 3.297250282 |
| `Λ_308 = E_a[τ](1.8824130)`, 2e6-path MC | **4.30910 ± 0.00102** | bound 3.512733596 |
| `E_a[τ]` at 308 midpoint, 2e6-path MC | 4.17398 ± 0.00097 | diagnostic 4.174300 |
| `E_a[τ]` at 309 midpoint, 2e6-path MC | 3.92108 ± 0.00088 | diagnostic 3.920787 |

The certified bound is below the truth in every cell, with 22–23 % to spare; it is a genuinely loose but genuinely
valid minorant, capturing about 81 % of the truth. The committed float diagnostics are confirmed to ~3e-4.

**Reproduction.** `c4_lower_bound.py`, `c4_certificate.py` and `c4_mutations.py` all reproduce their committed
evidence **byte-identically** on my re-run. `c4_phase0_audit.py` returns **13/13 PASS** at the current HEAD (only
the recorded `head` and `uncommitted_files_at_audit` differ from the committed run, as they must).

## 2. Does it exceed the exact critical threshold?

**Yes at cell 309, and the load-bearing test is what the gate says it is.**

`c4_certificate.evaluate` computes `is_excluded = blocker_is_A0 and exclude_if(at_bound["Gamma"])` with the default
`exclude_if = lambda gam: gam >= 0`, applied to the **exact `Fraction`** Γ returned by the frozen consumer. The
bisected critical values appear only as `critical_A0_reported_only` and `slack_over_critical_percent`, both written
after the decision and never read by it. No rounded critical value enters. I confirmed this by reading the code and
by driving the consumer myself:

```
cell 309: Γ(B, 0, 0) = +0.004661129657978107   (exact sign positive)  → EXCLUDED
cell 308: Γ(B, 0, 0) = −0.040467542629         (exact sign negative)  → not excluded
independent bisection: critical A0 = 3.214236022678 (309), 4.375228833136 (308)
B_309 / critical_309 − 1 = +2.582706 %
```

**The monotonicity licence — I checked it structurally, not just on the ladder.** The licence is genuinely
load-bearing: the exclusion needs `Γ(A0, A1, A2) ≥ Γ(B, 0, 0)` for every admissible `A0 ≥ Λ ≥ B` and every
`A1, A2 ≥ 0`, so monotonicity in all three arguments is required, not just in `A0`.

* In `tct_rule.tail_enclosure_crosscheck`, `halves[r] = ρ·aG + Σ_i C(2,i)·A_i·p_{2−i}` with every `p_n ≥ 0` (they
  are sums of non-negative residuals, envelopes and powers of ρ). So `[lo, hi]` widens monotonically in **each** of
  `A0, A1, A2`.
* In `c2_d5_forecast.direct`, `Γ = (R_hi − e0·D_lo) + ρ·x_hi·M` with `M = M0` when the TC-T/K5-B intersection is
  empty and `min(M0, max(|a|,|b|))` otherwise. Since `min(M0, ·) ≤ M0`, an empty intersection gives the *largest*
  `M`; widening `[lo,hi]` can only take the intersection from empty to non-empty, never the reverse. Hence Γ is
  nondecreasing in `A0, A1, A2` **provided the intersection is non-empty at the bound**, and that is exactly the
  condition the certificate checks. It is true at all four cells.

So the licence the gate names is precisely the right condition, and it holds. I verified the A1/A2 direction
numerically too: at cell 309, Γ rises from +0.004661 at `(B,0,0)` to +0.064868 at `(B, A1_cert, A2_cert)`, and no
`(A1,A2)` reduction whatever closes 309 at `A0 = B`.

**Two defects in how the licence is handled, neither of which changes the result.**

* **The licence is recorded but not enforced.** `is_excluded` never consults `row["licence"]`. The gate says "Both
  facts must be exercised per cell, not assumed"; they are exercised, they are true, and they are reported — but a
  re-run on inputs where the intersection went empty at the bound would still emit `excluded: true`. The guard is
  decorative.
* **Monotonicity in A1 and A2 is asserted, never exercised.** The ladder varies `A0` only, with the knockout fixed
  at `(0,0)`. The gate's "A1 = A2 = 0 is the most generous possible setting" is therefore an unexercised claim in
  the campaign's own machinery. I verified it independently and it holds; it should not have needed me to.

The extension of the `A0` ladder to `10⁵ ×` the certified value did land (24 points, Γ nondecreasing throughout,
intersection non-empty throughout, saturating at +0.374145 at 309 and +0.288317 at 308). That repair is real.

## 3. On which cells and domains?

**Excluded: cell 309 only.** Detector CUSUM, `m = 5`, drift `e = 19839101/10000000 = 1.9839101`, which is the left
endpoint of the closed cell `[1.9839101, 2.0922830]` and simultaneously cell 308's right endpoint. The certificate
enforces `e_lo ≤ e ≤ e_hi` per cell and refuses otherwise; the cell endpoints are cross-checked between the cover
ledger and the C1 registry with a refusal on disagreement. I re-derived 309's geometry by hand from `cells.json`
and it matches.

The domain quantifier is legitimate and I checked the frozen theorem rather than the campaign's gloss.
THEOREM_AD §5 fixes "a drift set `E ⊇ [e0 − ρ, e0 + ρ]` on which the hypotheses of Lemma Dv hold", and Lemma Dv
asserts `|[R f](a)| ≤ A0‖f‖` for every `e ∈ E`. So admissibility really is a supremum over the **closed** cell, and
a pointwise lower bound at any single point of it is a floor. I went one step further and confirmed that `A0`
enters the consumer **only** through the whole-cell `R″` enclosure (`Γ` depends on `A` solely via `halves[r]`,
whose `A0` coefficient is the `p₂` slot matching theorem AD's `A0·f_H^cell` line) — so a cell-uniform `A0` is
exactly what this consumer needs, and the gate's family boundary is drawn in the right place for it.

**Not excluded: cell 308.** `Γ(B₃₀₈, 0, 0) = −0.040468 < 0`; the bound is 19.71 % below the threshold.

**Outside the count: cells 306 and 307.** `Γ(A0_certified, 0, 0) = −0.079279` and `−0.021906`, both negative, so
`A0` is not what keeps them open and no floor under `A0` can bear on them. This is correct and correctly reported
with `critical_A0: null` and an explicit reason.

**One fragility the campaign does not state, and should.** The same route evaluated at cell 309's **midpoint**
gives `3.191359686`, which is **0.71 % below** the threshold 3.214236. The entire exclusion therefore lives on the
sup-over-the-closed-cell quantifier and on the choice of the left endpoint. The quantifier is correct — I verified
it in THEOREM_AD — but the margin is a product of it, and any successor that weakens the quantifier loses the
result outright.

## 4. Does it establish that NO improvement of A1/A2 and NO admissible operator-level A0 supply can close the cell?

**Cell 309 — YES, within the admissible family and with the frozen inputs held fixed.** Every admissible supply has
`A0 ≥ Λ₃₀₉ ≥ B₃₀₉ = 3.297250282` (Lemma SM(d) plus theorem L) and `A1, A2 ≥ 0`. Γ is nondecreasing in all three
(§2). Therefore `Γ ≥ Γ(B, 0, 0) = +0.004661 > 0` for every admissible triple, and `Γ < 0` is the closure condition.
The cell does not close. I confirmed the A1/A2 leg directly: at `A0 = B₃₀₉` **no** reduction of `(A1, A2)`, however
deep, closes 309.

**Cell 308 — NO, and on the evidence it never will be excluded by this route.** Not established: `Γ(B, 0, 0) < 0`.
Worse, my own 2,000,000-path Monte-Carlo puts `Λ₃₀₈ = 4.30910 ± 0.00102` against the threshold 4.375229 — a gap of
0.066, about 65 standard errors — so the threshold genuinely exceeds the truth and no lower bound on `E_a[τ]` can
ever discharge 308. That is corroboration, not proof: **C4 certifies no upper bound on `Λ`**, and the campaign says
so plainly (C4-N2, and the certificate's own `reason_not_excluded` field). The *certified* answer for 308 is "the
bound is too weak"; the *evidenced* answer is "the threshold is above the truth". Both must be reported, in that
order, and the campaign does report both.

**What "308 can be closed under the knockout" is actually worth.** Phase 1 §5 offers the diagnostic-free
restatement that a certified upper bound on `Λ₃₀₈` below 4.375229 would itself be an admissible `A0` closing 308 at
`A1 = A2 = 0`, and concludes "the two possibilities for 308 are exhaustive and one of them is progress". The
dichotomy is correct. The word "progress" is not earned, and I quantified why: **at `A0 = 4.311` (the Monte-Carlo
value of `Λ₃₀₈`), closing cell 308 still requires an 18.2× reduction of `(A1, A2)`; at `A0 = 4.375229` it is
impossible at any `(A1, A2)`.** The knockout branch therefore demands a certified upper bound essentially at the
truth *and* an eighteen-fold improvement in the first- and second-order atom constants. C4-N3 already disclaims the
sentence "cell 308 is closable"; the 18.2× figure is what should replace "one of them is progress".

## 5. What EXACT deterministic family has been exhausted?

The family is, exactly:

> every atom-constant triple `(A0, A1, A2)` whose `A0` is a valid **uniform** order-0 bound on the closed cell —
> `|[(I − K_e)⁻¹f](a)| ≤ A0‖f‖` for every `f ∈ B(X)` and every `e ∈ [e0 − ρ, e0 + ρ]` — consumed through the
> **frozen** theorem TC-T and the **frozen** K5-B direct clause, at the **frozen** measurement inputs, at cell 309,
> `m = 5`.

That covers Lemma G (`A0 = C_upper`), Lemma Dv' (`A0 = min(Ā, τ/D_lo)`), C3's operator-mixed supply, and any future
supply of the same shape. It excludes, by the gate's own `does_not_cover`: residual-specific (non-norm-only) order-0
bounds; any change to TC-T, to the K5-B clause or to the frozen measurement inputs; and order-3 candidates of F.

**Is that the right boundary? Yes — and I verified it against the consumer rather than accepting it.** Because `A0`
enters only the whole-cell `R″` enclosure, cell-uniformity is precisely what this consumer requires; a supply with
a per-line or midpoint-only `A0` would not be consumable here without changing TC-T, which the gate already
excludes. The `does_not_cover` clause naming non-norm-only bounds is the decisive escape hatch, and it is the right
one: SM(d)'s sharpness is attained at `f = 1` and says nothing whatever about a specific residual.

**Is the campaign's claim confined to it?** In the machinery, yes, cleanly. `c4_certificate.py` writes
`family_exhausted` as the gate's definition verbatim and emits the PARTIAL `permitted_conclusions`, including "no
R-stage consequence of any kind". The README's headline question is now correctly scoped to "no certificate *of the
admissible family*", and Phase 3's `{309}` sentence now says "under any *lower-bound* route" with the qualification
that 308 is corroborated, not proved.

**But two committed artifacts still exceed it — see §"Over- and under-claiming" below.** Neither is load-bearing;
both are text a successor could cite.

## 6. Is broader deterministic exhaustion now established?

**No. Emphatically not, and the gap is larger than the campaign's framing conveys.**

C4 exhausts one channel — the order-0 atom constant — at one of four open cells, with every other input frozen. I
probed where the exclusion's critical `A0` actually lives, by scaling single groups of measurement inputs at cell
309 and re-bisecting. These are incoherent single-knob perturbations and are indicative only, not feasible
campaigns; but the ordering they reveal is unambiguous.

| perturbation at cell 309 | critical `A0` | exclusion survives (`B` = 3.2973)? | closable at the MC truth `Λ` = 4.047? |
|---|---|---|---|
| none (baseline) | 3.214236 | yes | no |
| order-0/1/2 residuals `delta_{F,D,H}`, `eps_src` × 0.90 | 3.214686 | yes | no |
| source suprema `sup_S0` × 0.5 | 3.367552 | **no** | no |
| candidate sup norms `sup{F,D,H}` × 0.5 | 4.160309 | **no** | **yes** |
| enclosure `ρ` × 0.5 | 7.534321 | **no** | **yes** |

A 10 % cut in the residuals the campaign's channel sits next to moves the critical `A0` by 0.014 %. Halving the
candidate sup norms — which feed the order-3 surrogate `resG = k₃·supF + 3k₂·supD + 3k₁·supH + σ₃` and the fourth-
order envelope — moves it above both the certified bound and the true `Λ₃₀₉`, i.e. the cell would become closable
under the knockout. Halving `ρ` moves it to 7.53.

So the atom-constant channel that C4 has closed is **not** the dominant channel at this cell. The dominant channels
are the order-3 surrogate and the cell width. Describing C4's result as "the deterministic operator route is
exhausted" without qualification would be a serious misreading, and the qualification is not decoration.

Beyond cell 309, the tail's other three cells are untouched by any exhaustion argument. I reproduced C3's targets
exactly from the equations: **cell 307 closes on a 2.203053× reduction of `(A1, A2)` with `A0` unchanged, or a
1.111966× uniform reduction**; **cell 306 already closes at the full certified triple** (`Γ = −0.036198`), its
blocker being the inherited adoption floor rather than the mathematics. Neither is an exhausted direction; 307's is
the kind of factor this programme has repeatedly found by recombination alone.

## 7. What exact deterministic mechanism remains unexcluded?

Seven, named concretely.

1. **Residual-specific order-0 bounds.** SM(d) is sharp only at `f = 1`. Replacing `A0‖φ_H‖` by `(Ĝ|φ_H|)(a)/D_e` —
   a pointwise majorant of the actual residual rather than its sup-norm — sits legitimately below `E_a[τ]·‖φ‖` and
   escapes the floor entirely. The gate names this; nothing in the programme quantifies it. This is the sharpest
   unexcluded mechanism and the one a successor should cost first.
2. **Tightening the candidate sup norms `sup{F, D, H}` and `sup_S0`.** Per §6, the dominant channel.
3. **Refining the cover: a smaller `ρ` at cell 309.** The largest single lever in the probe. It requires new K1
   measurement work at finer cells — deterministic and order-3-free, but not free.
4. **Tightening theorem TC-T's assembly or the K5-B clause**: the `W2` enclosures, the `(P3)` envelope, the σ₃/σ₄
   towers. Explicitly outside C4's family.
5. **For cell 308 specifically:** a certified upper bound on `Λ₃₀₈` below 4.375229 **together with** an ≥ 18.2×
   reduction of `(A1, A2)`. Either alone is insufficient.
6. **For cells 306 and 307:** wholly untouched. 307 needs 2.203× on `(A1, A2)` or 1.112× uniform; 306 needs the
   adoption floor addressed, or a second independent certifier.
7. **The order-3 R-stage itself**, which is what replaces the `resG` surrogate in channel 2.

C4-N1 additionally records two designed-but-unrun sharper lower-bound routes (R1, taboo-defect inversion, needing
only the `sup_X` of a defect the frozen certifier already computes and discards; and R5, a two-sided `τ_a`
certificate). Neither can change any C4 verdict, and the campaign is right that running them would have been
wasted compute.

## 8. Is the scientific prerequisite for designing a real order-3 R-stage now satisfied?

**No. Another deterministic successor remains necessary.** I decide this on the evidence, not by deferring to C3 or
to C4.

The premise the R-stage needs is that the deterministic direction is spent for the cells the R-stage would be spent
on. Measured against that:

* **Cell 309:** the premise is discharged, but only for the order-0 atom-constant channel, and §6 shows that
  channel is not the one that dominates the cell's critical `A0`.
* **Cell 308:** the operator-level route is *not* excluded and, on the evidence, cannot be excluded by this route.
  Its own closure path (a certified upper bound on `Λ₃₀₈` plus 18.2× on `(A1,A2)`) is deterministic and unattempted.
* **Cell 307:** exhaustion is not merely unproved, it is not in prospect by this route at all — `A0` is not its
  blocker. A 2.203× reduction of `(A1, A2)` closes it. That is a live, cheap, quantified deterministic target.
* **Cell 306:** closes today at the full certified triple; what blocks it is the adoption floor, which no
  order-3 computation addresses.

One cell of four, in the narrowest of the available channels, is not exhaustion of the deterministic direction. The
R-stage premise is **not available**, and the guard must stay DENY. C4 asserts none of this itself — its gate
forbids it to, and the certificate emits "no R-stage consequence of any kind" — and that restraint is correct.

I want to say plainly, because the question invites the opposite judgement: **C4 is real work.** It found and
proved a clean, cheap, correct theorem that no one in this programme had; it certified it in exact rational
arithmetic with proved and run-time-checked remainder bounds; it closed, for one cell, precisely the gap the C3
adjudicator named as the single highest-value next step; and it did so at literally zero new scientific compute. It
is not a thin result dressed up. It is a narrow result honestly labelled — and the labelling, not the result, is
where the residual problems are.

---

## Rulings on the specific questions asked

### Over- and under-claiming

**Two committed over-claims that the campaign's own disposition records as repaired, but which did not land.**

* `evidence/phase3/C4_ROUTES.json` → `DIAGNOSTIC_note`: *"They are recorded because they decide whether any route
  could discharge cell 308, and the honest answer is that none can."* That is an unhedged universal negative
  resting on uncertified float diagnostics. `OPEN_NOTES_DISPOSITION_C4.md` row (e) records this class of over-claim
  as "Fixed at source"; it was fixed in `phase_3/C4_CANDIDATE_ROUTES.md`, which now says "corroborated, not
  proved", but **not** in the machine-readable evidence its own producer (`code/c4_routes.py:146`) emits.
* `evidence/phase3/C4_ROUTES.json` → `routes.L_ladder_Wald.assumptions`: *"E[tau] < infinity (Lemma T)"*. This is
  verbatim the mis-citation the pre-result review flagged as its one real error in the proof text (Lemma T bounds
  `E_x[τ ∧ T_a]`, the taboo time, not `τ`). Disposition row (a) records it as "Fixed at source". It was fixed in
  `code/c4_lower_bound.py`; the same wrong citation survives in `code/c4_routes.py:98`, in the committed
  `C4_ROUTES.json`, and in `phase_3/C4_CANDIDATE_ROUTES.md` §"Route L / Assumptions".

Neither is load-bearing — `c4_certificate.py` reads only the frozen gate, `evidence/phase1/C4_THRESHOLDS.json`, the
pinned model, the cover ledger and the C1 registry; it never opens `C4_ROUTES.json`. But the disposition document
describes two partial repairs as complete, and that is itself a finding: a reader auditing by the disposition table
would conclude both were fixed.

**One over-claim of framing, self-corrected but not removed.** Phase 1 §5's "the two possibilities for 308 are
exhaustive and one of them is progress." The dichotomy is sound; "progress" is not, for the 18.2× reason in §4.
C4-N3 explicitly disclaims the bad reading ("Nothing in C4 licenses the sentence 'cell 308 is closable'"), so the
campaign is not being dishonest — it has left a sentence in place that its own notes then have to defend against.

**"Closed under the knockout" is handled correctly.** C4-N3 states without hedging that the knockout sets
`A1 = A2 = 0`, which no real supply achieves, and that it is not closure. That is the right treatment and it is
consistent everywhere in the machinery. My only addition is the quantification.

**Under-claiming.** None material. If anything the campaign under-states the internal robustness of the 309 result:
no `(A1, A2)` reduction whatever closes 309 at `A0 = B₃₀₉`, which is a stronger statement than the certificate makes.

**Minor documentation defects, for completeness.** The README's phase table points at
`evidence/freeze/C4_FREEZE_RECORD.json`, which does not exist (the directory is empty and untracked). Phase 0's
check `1_branch_head_clean` does not test cleanliness — it tests the branch name and ancestry — and the committed
run records `uncommitted_files_at_audit: 12` while returning true. Neither affects any result.

### Is the gate freeze sound governance, given E2?

**The freeze is fully retrospective as to the result, the campaign says so without euphemism, and that candour is
sufficient — but the freeze carries no evidential weight and must never be cited as though it did.**

I verified the ordering myself. `376950be` is a single commit touching one file, 108 insertions, with no
certificate or mutation artifact in the tree. But `c9b06abf`, its immediate predecessor, already contained
`evidence/phase3/C4_ROUTES.json` carrying the final numbers exactly:

```
306 {'lower_bound': 3.959880291432561, 'Gamma_at_bound': -0.14388116320706978, 'excludes_cell': False}
307 {'lower_bound': 3.734070430633033, 'Gamma_at_bound': -0.09298528787328704, 'excludes_cell': False}
308 {'lower_bound': 3.512733596022926, 'Gamma_at_bound': -0.04046754262884166, 'excludes_cell': False}
309 {'lower_bound': 3.297250281519544, 'Gamma_at_bound':  0.004661129657978107, 'excludes_cell': True}
```

`PASS` was unattainable and `FAIL_INCONCLUSIVE` was already ruled out before the gate existed; `PARTIAL` was the
only reachable class, and the gate names `PARTIAL` as expected. Erratum E2 states this in exactly those terms,
notes that the ordering was mandated by the campaign instruction rather than chosen, and forbids any report of C4
from describing the freeze as a pre-registration of the result. That is honest — more honest than most
retrospective freezes are.

**What the freeze does do, and it is not nothing:** it fixes the exclusion test, the domain requirement, the
admissible family, the permitted conclusions and the refusals before the result is written down, and
`c4_certificate.py` pins the gate sha and refuses to run against any other. Those bindings are mechanical and I
verified they are honoured.

**One correction to erratum E3.** E3 flags the `cells_whose_blocker_is_not_A0` carve-out as a candidate for
gate-fitting, says those are "exactly the cells that would otherwise have counted against the campaign", and
concludes it is logically forced. The conclusion is right — if `Γ(A0_certified, 0, 0) < 0` then `A0` is not the
blocker and no floor under it can bear on the cell. But E3 overstates its own stakes: **the class is `PARTIAL`
with or without the carve-out** (309 excluded, 308 not), so the carve-out cannot have been outcome-fitting in the
decisive sense. It changes the denominator from four to two, which is presentational. That strengthens the
campaign's position and should be recorded as such rather than left as a confessed near-miss.

**Net:** the freeze is sound governance for what it binds, the characterisation is honest and sufficient, and the
exclusion's credibility rests — and in this adjudication does rest — on the mathematics and on independent
reproduction, not on the freeze.

### Is ~2.6 % slack a safe margin for a permanent negative claim?

**As a mathematical margin, yes, decisively. As a description of the claim's robustness, no — and the campaign
does not distinguish the two.**

Safe, for three independent reasons I checked rather than assumed:

* The arithmetic uncertainty is ~1.9e-95 against a gap of 0.083 in `A0` — a ratio of about 10⁹⁴. No rounding
  decision anywhere in the module can move the verdict, and the decision is the exact sign of a rational.
* The rounding *direction* is correct at every step, and the load-bearing test never touches a rounded critical
  value.
* The 2.6 % is the margin of a deliberately loose certificate, not of the fact. The true `Λ₃₀₉ = 4.047` exceeds
  the threshold 3.214 by **26 %**. The route consumes 23 of those 26 points and leaves 2.6. The mathematics has ten
  times the headroom the certificate reports.

Not safe, as robustness, for two reasons the campaign does not state:

* The same bound at the cell **midpoint** is 0.71 % **below** the threshold. The margin exists only because
  admissibility is a supremum over the closed cell and the route is evaluated at the left endpoint. That quantifier
  is correct, but the result has no margin at all against any weakening of it.
* The critical `A0` is highly sensitive to inputs the gate freezes (§6): halving the candidate sup norms takes it
  to 4.160, above both `B₃₀₉` and the true `Λ₃₀₉`. A 2.6 % margin in `A0` is not a 2.6 % margin in anything else.

So: safe to publish as stated, provided "as stated" always carries "against the frozen measurement inputs and the
frozen consumer". It is not safe to carry forward as a standing fact about cell 309.

### Is any repair cosmetic rather than real?

**Mostly real. One label is inflated; two repairs did not land.**

*Real, and I verified each:*

* **M04/M05 structural guard.** `c4_certificate.evaluate` now refuses any `(K, H)` with `K + H ≠ C_CUSUM`, tying
  the pair theorem L consumes back to the frozen producer's own definition. Both mutants are now
  `DETECTED_BY_GUARD`. This is the right kind of fix — structural, not a bolted-on test — and it addresses the
  reviewer's most serious finding (a mis-identified threshold inflating the bound in the unsound direction). It is
  narrow (it catches one-sided perturbations, not a coordinated mis-reading), but it is genuine.
* **M06 rewrite.** Now shifts 307→306, 308→306, 309→307, so cell 309's evaluation point falls genuinely outside
  its closed cell and the domain guard fires. The previous version perturbed nothing. Real.
* **`c4_independent.py` rewrite.** Bernoulli/AM-GM brackets for `exp` with repeated squaring, Archimedes polygons
  for `π`, composite midpoint with a second-derivative remainder for the erf integral. I read it and verified each
  bound (`(1+y/n)^n ≤ e^y ≤ (1−y/n)^{−n}`; harmonic/geometric mean iteration from the hexagon; midpoint error
  `t·h²/24·sup|f″|` with `sup|(u²−1)e^{−u²/2}| = 1`). It genuinely shares no series with production, and the
  evidence honestly records the achieved ~1e-7 resolution as a cross-check rather than a reproduction. Real, and
  it also fixed the 17-minute runtime (the suite now completes in 46 s on my host).
* **Ladder extension to 10⁵ ×, Phase 0 check 10a/10b split (13/13 at HEAD), the theorem-L proof rewrite via
  Tonelli, the state-space correction, the `reason_not_excluded` field, and deriving `monotone_check`'s endpoints
  from `cell_geometry()`** — all landed and all verified.

*Inflated label:* **M02**. Reclassified `DETECTED_BY_RULE` on the strength of evaluating `(0 >= 0) != (0 > 0)` on
a literal. The accompanying note is entirely honest — it says the two rules differ exactly at `Γ = 0`, that C4's
run does not land there, and that a verdict-level check could never have separated them. But nothing in the
production pipeline is exercised, and "DETECTED_BY_RULE" reads as a test result. It is a correct note wearing a
detection's clothes. (The `VALUE_ONLY` reclassifications of M03, M09 and M12, by contrast, are honest downgrades
and I have no objection to them.)

*Did not land:* the two `C4_ROUTES.json` items in "Over- and under-claiming" above.

### Did C4 respect its own compute policy?

**Yes, and the evidence is stronger than the campaign's own accounting.**

* **Static import audit.** The whole C4 code set and the entire frozen consumer stack it loads
  (`c2_d5_forecast.py` → `tail_forecast_r2.py` → `tct_rule.py`/`tc_rule.py` → `deflated_consume.py` →
  `c3_selector.py`) import only `argparse, json, sys, re, hashlib, importlib.util, types, subprocess, fractions,
  pathlib, math`. No `numpy`, no `python-flint`, no `socket`/`urllib`/`requests`/`http`/`paramiko`. The only
  `subprocess` uses are local `git -C <repo>` calls.
* **Negative capability.** This host has neither `numpy` nor `flint` installed. `cusum_layer1.py` cannot even be
  imported here, so a kernel evaluation is not merely absent but impossible. Every producer nonetheless runs to
  completion.
* **Repository footprint.** `git diff --name-only 019ecce0 HEAD` returns exactly 26 paths, all inside
  `p5y_k5_tail_c4_exhaustion`. C2's and C3's seal manifests verify byte-intact (Phase 0 check 7). `main` is
  untouched at `c123b9bb`.
* **No host contacted.** Consistent with everything above, and with the README's corrected phrasing (a statement
  about C4's actions, not about the AWS estate's state, which C4 cannot observe).

One honesty caveat, which the campaign itself raises as C4-N4: `new_real_scientific_addresses_evaluated: 0`,
`kernel_evaluations: 0`, `operator_certifications_run: 0` and `remote_hosts_contacted: 0` are literal constants in
the emitters, not instrumented counters. They are true — I verified statically and dynamically — but they are
assertions, and a successor that wants them to be evidence should instrument them.

### Does anything license adopting a cell, changing a coverage map, reporting K5 closed, or authorizing the R-stage?

**No. I looked for all four and found none.**

* **No adoption.** No adoption artifact of any kind exists in the namespace. The certificate's vocabulary is
  `excluded` / `not_excluded` / `outside_the_count`, never `adopted`.
* **No coverage map.** Only `K5_COVERAGE_MAP_R3/R4/R5.json` exist anywhere under `level4/closure_proofs`; r5
  hashes to its pin, and Phase 0 check 5 verifies no `_R6` file exists. The gate's `r6_rule` — "excluding a cell
  removes a ROUTE, not the cell; the cell stays open in r5" — is exactly the right framing and is honoured.
* **K5 not reported closed.** Phase 0 records `K5_COVERAGE_COMPLETE` from r5 unchanged and the m = 5 open set as
  `{306, 307, 308, 309}`.
* **No R-stage authorization.** `permitted_conclusions` in the certificate is the gate's PARTIAL list verbatim,
  including "no R-stage consequence of any kind". No authorization packet, countersignature, launch notice, slot
  binding or seal exists in the namespace. Guard `REAL_SCIENTIFIC_COMPUTE = DENY` throughout.

**The one vector that could leak, and it is textual, not mechanical:** the phrase
`DETERMINISTIC_OPERATOR_ROUTE_EXHAUSTED` together with the two unhedged sentences still sitting in
`C4_ROUTES.json` is precisely the material a successor could quote as though exhaustion had been demonstrated —
the same failure mode the C3 adjudicator flagged in `C3_BLOCKER_ANALYSIS.md` §3. That is why Condition 2 below is
binding.

---

## VERDICT

**ACCEPTED_WITH_SCOPE_LIMITATION**

The exclusion of cell 309 stands. Theorem L is correct, the model is correctly identified from its pinned source,
the arithmetic is rigorous in exact rationals with proved and run-time-checked remainder bounds, the load-bearing
test is a direct exact evaluation rather than a comparison against a rounded critical value, the monotonicity
licence it depends on genuinely holds in all three atom constants, and every artifact reproduces byte-identically
on an independent re-run. Two independent Monte-Carlos and my own closed-form and quadrature checks corroborate
every number. The compute policy was respected in full.

**The claim must be narrowed, exactly as follows.** Wherever the result is stated, it must read:

> Against the **frozen measurement inputs** and the **frozen theorem TC-T / K5-B direct clause**, no atom-constant
> supply whose `A0` is a valid **uniform** order-0 bound on the closed cell can close CUSUM cell **309** at `m = 5`,
> for any `A1, A2 ≥ 0`. This removes one route from one cell. It is not a statement that cell 309 is unclosable, it
> is not exhaustion of the deterministic direction, and it has no R-stage consequence.

The narrowing is not pedantry. The campaign's own certificate is correctly scoped, but the bare phrase
"deterministic operator route exhausted" is false of everything except the order-0 atom-constant channel at one
cell — and my sensitivity probes show that channel is not even the dominant one at that cell.

Cell 308 is **not** excluded and, on 2,000,000-path Monte-Carlo evidence at ~65 standard errors, never will be by
any lower-bound route; but C4 certifies no upper bound on `Λ₃₀₈`, so its status is "operator-level route not
excluded", not "cannot be excluded". Cells 306 and 307 are correctly outside the count.

## EXCLUDED CELL SET

[309]

## CONDITIONS

These bind any successor campaign in this line.

1. **Scope every restatement.** The exclusion holds for the uniform-`A0` atom-constant family, at cell 309, at
   `m = 5`, **against the frozen measurement inputs and the frozen TC-T / K5-B consumer**. The last clause is not
   optional: halving the candidate sup norms raises the critical `A0` to 4.160, above both the certified bound and
   the Monte-Carlo truth. The token `DETERMINISTIC_OPERATOR_ROUTE_EXHAUSTED` may not appear unqualified.

2. **Erratum required before any successor cites Phase 3.** Two repairs the disposition records as complete did not
   land in committed evidence. `evidence/phase3/C4_ROUTES.json` still asserts of cell 308 "the honest answer is that
   none can" (an unhedged universal negative resting on uncertified floats) and still cites `E[tau] < infinity
   (Lemma T)` for a hypothesis the proof no longer uses and which Lemma T does not supply. Both appear in
   `code/c4_routes.py` and the first also in `phase_3/C4_CANDIDATE_ROUTES.md`. Record them in
   `ERRATUM_C4_GATE.md` as E4 and E5. **No successor may quote either sentence as establishing anything.**

3. **Strike "one of them is progress" (Phase 1 §5).** Replace it with the quantified fact: at `A0 = 4.311`, the
   Monte-Carlo value of `Λ₃₀₈`, closing cell 308 still requires an **18.2× reduction of `(A1, A2)`**; at
   `A0 = 4.375229` it is impossible at any `(A1, A2)`. C4-N3 stands and is binding: nothing licenses "cell 308 is
   closable".

4. **Enforce the licence, do not merely record it.** `c4_certificate.evaluate` must refuse — not merely report —
   when `intersection_nonempty_at_bound` is false, and the ladder must exercise monotonicity in `A1` and `A2` as
   well as in `A0`. Both hold today; I verified them structurally and numerically. The machinery does not.

5. **The 2.6 % margin is the certificate's, not the fact's.** The true `Λ₃₀₉ = 4.047 ± 0.001` exceeds the
   threshold by 26 %. But the same route at the cell midpoint falls 0.71 % **below** threshold, so the published
   margin exists only by virtue of the sup-over-closed-cell quantifier and the left-endpoint evaluation. Any
   successor that weakens either loses the result. State this wherever the 2.58 % figure is quoted.

6. **The R-stage premise is not available and the guard stays DENY.** Deterministic exhaustion is established for
   one of four open cells, in one channel. Cells 306 and 307 have live, quantified, cheap deterministic targets
   (307: 2.203053× on `(A1, A2)`, or 1.112× uniform; 306: the inherited adoption floor — it already closes at the
   full certified triple, `Γ = −0.036198`). No new-real address, launch, authorization packet or countersignature
   is licensed by anything in C4.

7. **The next deterministic successor should cost these four, in this order:** (a) a residual-specific, non-norm-only
   order-0 bound, `(Ĝ|φ|)(a)/D_e` in place of `A0‖φ‖` — the only mechanism that escapes the `E_a[τ]` floor
   outright, named by the gate and quantified by no one; (b) tightening the candidate sup norms feeding the
   order-3 surrogate `resG`, the dominant channel at cell 309; (c) cell-width refinement at 309; (d) cell 307's
   `(A1, A2)` target. C4-N1's routes R1 and R5 remain the right starting point for a sharper floor, and R1 needs
   only the `sup_X` of a defect the frozen certifier already computes and discards.

8. **No coverage map revision.** r5 remains authoritative and immutable; the `m = 5` open set is unchanged at
   {306, 307, 308, 309}. Excluding a route does not close, adopt or remove a cell. C4 generated no r6 and none may
   be generated on the strength of this adjudication.

9. **Carry C3's conditions forward unchanged.** In particular the K5 tail adoption floor with the C2 adjudicator's
   N9-lapse condition on F1, the standing prohibition on citing `C3_BLOCKER_ANALYSIS.md` §3, and N9/N10 (the
   registry constants' Arb certification has never been independently written, and no build host is recorded).
   Neither was in C4's scope and neither is discharged.

10. **Correct erratum E3's framing.** The `cells_whose_blocker_is_not_A0` carve-out is logically forced, as E3
    says — and it could not have been outcome-fitting in the decisive sense, because the class is `PARTIAL` with or
    without it. E3 concedes more than the facts require; record the correction rather than leaving the concession
    to be quoted against the campaign.

11. **Minor, for hygiene:** `README.md` advertises `evidence/freeze/C4_FREEZE_RECORD.json`, which does not exist;
    Phase 0's check `1_branch_head_clean` does not test cleanliness and returned true on a run recording twelve
    uncommitted files; and `kernel_evaluations`, `operator_certifications_run` and `remote_hosts_contacted` are
    literal constants rather than counters (C4-N4). None affects any result; all three should be fixed rather than
    inherited.

HANDOVER: ADJUDICATION COMPLETE
