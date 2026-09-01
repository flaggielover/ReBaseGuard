# P8 adversarial review

A deliberate attempt to break P8's own claims before declaring a candidate
verdict. Each attack is stated as an adversary would state it, then answered
with the specific artifact that settles it, then given one of

`SURVIVES` · `NARROWED` · `REJECTED` · `OPEN`

`NARROWED` and `REJECTED` verdicts were acted on: the claim wording in
`RESULTS.md` and `CODEX_HANDOFF.md` is the post-review wording, and §14 lists
every change this review forced.

Final gate outcome: **17 of 21 pass**; `G4`, `G4-D`, `G4-F` and `G7` fail and
are reported failed. Verdict `P8 = PARTIAL_CANDIDATE`.

---

## A1. "The window law is an artifact of the `m` grid."

**Attack.** `K(D,f,m)` is evaluated at `m in {1,2,3,5,10,20}`. A different grid
could make the spread look smaller or larger, and `m = 1` is the normaliser, so
everything is anchored on one point.

**Answer.** `K` is *defined* against `m = 1`, so the anchor is a definition, not
a selection: `K(D,f,1) = 1` identically. The gate is evaluated at every
`m in {2,3,5}` separately and requires all three; there is no aggregation across
`m` that a grid choice could bias. `m in {10,20}` is reported but never gated,
and is labelled `EXTRAPOLATION_BEYOND_P3` in the artifact for each row.
Independently, `P8-L1(b)` gives the exact decomposition
`Gamma_A(m) = mean_{r<m} gamma_r + R_m`, and the **lag profile `gamma_r` is
measured at every `r < 20` regardless of the `m` grid** — so the mechanism
behind `K` is visible without reference to any `m` grid at all, and the `m`-grid
result is a consequence of a grid-free measurement.

**Verdict: `SURVIVES`.** The window-law *rejection* is if anything grid-robust
in the safe direction: the spread grows with `m`, so a coarser grid stopping at
`m = 2` would understate it.

## A2. "The result depends on the seed choice."

**Attack.** One seed family, one namespace. Re-run it and the numbers move.

**Answer.** `E5` repeats the entire `E1` matrix at a **different experiment tag
and a disjoint batch range** (`p8_gamma_E5`, batches 100–119), so both address
components differ and the two fields are independent, not merely offset. Gate
`G10` requires agreement at `|z| <= 3` in `>= 90%` of the 72 cells and `>= 95%`
of the 60 non-`t3` cells. Within `E1` itself, every reported SE is a
batch-means SE over 20 independent batch addresses, so the per-cell sampling
variability is measured, not assumed.

**Verdict: `NARROWED`.** `G10` **passes** (69/72 overall, 57/60 non-`t3` —
exactly at its `95%` threshold), but the attack lands partially: one cell, SR /
`gaussian`, is offset by `+0.4%` between the two seed families at every window,
and the matrix-wide `z` distribution has sd `1.26` rather than `1`. The
batch-means SE understates cell-to-cell variability at the tightest cells. No
conclusion depends on that precision, and the anomaly is reported unexplained
(`RESULTS.md` §13, `STATISTICAL_AUDIT.md` §7.7).

## A3. "Interpolation artifacts."

**Attack.** `rho_c` is a reciprocal of a noisy quantity; intervals were probably
linearised; the `rho` ladder is built from an estimated `rho_c` so the rungs
themselves are random.

**Answer.** (i) `rho_c` intervals use the **exact monotone image** of the
`Gamma` interval under `rho_c = 1/|1-Gamma|`, P3's own rule, and return an
unbounded end whenever the `Gamma` interval contains `1` — no linearisation.
(ii) `K`'s SE is computed from the **batch ratios**, not by an
independence-assuming delta method, because `Gamma(1)` and `Gamma(m)` are
measured on the same cycles. (iii) The ladder rungs *are* built from an
estimated `rho_c`, and that is inherited from P7's design, which does the same;
the relative SE of `rho_c` is under `0.2%` in every non-`t3` cell, so the rung
placement error is far below the ladder's own spacing. (iv) No quantity anywhere
in P8 is interpolated between grid points.

**Verdict: `SURVIVES`, with (iii) recorded as an inherited design feature, not a
P8 defence.**

## A4. "Tuning data was reused for the confirmatory result."

**Attack.** The pilot informed the sizes and possibly the gate thresholds; the
same data then produced the result.

**Answer.** The pilot (`results/pilot_notes.json`) is a **separate experiment
tag** (`pilot`), so not one pilot cycle enters any production estimate. The
gate margins are traceable to two *external* numbers — P3's `CLOSED`
cross-detector `K` spread (0.1–1.1%) and Stage-D's cross-family spread of a
**different** estimand (~12%) — and the pilot notes say so explicitly in a
`not_fixed_by_the_pilot` field written before production. **The one place the
attack lands** is `results/posthoc_preregistration_H2.json`: hypotheses `H2a`–
`H2c` were written *after* four CUSUM cells were inspected. They are labelled
`POST_HOC_EXPLORATORY_THEN_OUT_OF_SAMPLE_CONFIRMATORY`, they are **not gates**,
the file records exactly which cells were visible, and they are evaluated on
cells that did not exist when they were written.

**Verdict: `NARROWED`.** `H1`/`G4` are clean. `H2a`–`H2c` are exploratory and
are reported as such everywhere, never as preregistered confirmation.

## A5. "There are hidden calibration differences between the families."

**Attack.** The families are compared at "the same ARL", but the thresholds come
from two different places and the SR ones are P8's own.

**Answer.** Gate `G14` checks that every CUSUM threshold used in every P8
artifact is **byte-identical** (`float.hex`) to Stage-D D3's, and that every SR
threshold is byte-identical to the value in `results/sr_calibration.json`. Gate
`G1c` re-measures the achieved `ARL_0` at the frozen CUSUM thresholds on P8's
own field and requires `<= 1%` of the frozen target. Gate `G2` requires the
P8-calibrated SR thresholds to hit the same target within `0.5%` at a
1,024,000-cycle verification. The SR calibration is labelled
`NEW_P8_CALIBRATION` in every artifact that touches it and its full iteration
trace, with batch addresses, is stored.

**Residual exposure, stated:** an SR `ARL_0` residual of up to `0.5%` does
propagate into the SR non-Gaussian `Gamma` values. Since the cross-family
`Gamma` differences P8 reports are tens of percent, this cannot explain them;
it *can* matter for the `3%` detector-invariance sub-gate `G4-D`, and that is
recorded in `LIMITATIONS.md` `S9`.

**Verdict: `NARROWED`** — the headline cross-family result is immune, the
detector sub-gate is not fully immune.

## A6. "Detector / window convention mismatch."

**Attack.** P8 compares against P3, P4, Stage-D and P7 numbers that use subtly
different windows, denominators, stopping rules or score conventions. Any
agreement is luck.

**Answer.** This attack is the reason the campaign exists in its present form,
and it found a real thing — but pointing the other way. P8 measures **three**
estimands in one pass and reproduces each against its own source
(`results/cross_priority_consistency.json`): `Gamma_A` against P4's `Gamma_f`,
`Gamma_psipsi` against Stage-D D3's `Gamma_psi`, and `Gamma_naive` against
Stage-D's `gamma_T_naive_DIAGNOSTIC_ONLY`. All twelve comparisons agree within
`|z| <= 2.1`. The *published* P4 and Stage-D numbers differ by up to a factor of
3.3 on the same family and threshold, and P8 shows that gap is **entirely
definitional**: P4 weights the raw window by the family score sum; Stage-D
weights the *score-transformed* window by the same sum. Semantics are further
pinned by `tests/test_semantics.py` (inclusive post-update alarm, `tau >= 1`,
terminal increment included, convention A vs B, newest-first truncated window,
the frozen update line) and by `tests/test_metrics.py`'s degenerate-detector
anchor, which forces `Gamma_A(m) = E[eps psi(eps)] = 1` exactly.

**Verdict: `SURVIVES`, and upgraded to a reported P8 finding.**

## A7. "Multiple comparisons."

**Attack.** 72 `Gamma` cells, 12 `K` columns, 312 chain rows, hundreds of
numbers. Something was bound to look significant.

**Answer.** No P8 gate is a null-hypothesis test. `G4` is a
practical-equivalence gate at a pre-declared margin; `G3` is a conjunction over
all 40 eligible cells; `G7` is P7's count criterion applied verbatim; `G10` is a
coverage fraction. Cochran's `Q` is computed and is labelled
`homogeneity_DESCRIPTIVE_ONLY` in the artifact key itself. Where a `p`-value is
reported inside a secondary metric family, BH at `q = 0.10` is applied within
that family. And the headline outcome is a **rejection with a large effect**
(tens of percent against a 10% margin), which multiplicity cannot manufacture.

**Verdict: `SURVIVES`.**

## A8. "Post-selection bias: the interesting law was found after looking."

**Attack.** `H1` was preregistered, failed, and then a story about lag profiles
appeared. That is the definition of post-selection.

**Answer.** Half true, and handled in the open. The lag-profile *measurement*
was preregistered — `gamma_r` for `r < 20` is in `EXPERIMENT_PROTOCOL.md` §6 and
`P8-L1(b)` before any production cell — precisely so a failure of `H1` would be
diagnosable rather than merely observed. What was **not** preregistered is the
`H2` family, and that is why `results/posthoc_preregistration_H2.json` exists:
it was frozen while 7 of the 12 cells did not yet exist, it names the visible
cells with their SHA-256 digests, it names the held-out cells, and it states in
advance that the Fisher-information reading and the tail-heaviness reading make
**opposite** predictions for the contaminated families, so exactly one could
survive. `H2b` was then **rejected** by the held-out cells. A post-hoc story
that survives its own falsification test is worth something; one that is only
narrated is not, and P8 reports which it has.

**Verdict: `NARROWED`.** `H1`/`G4` preregistered and reported as measured;
`H2a`–`H2c` exploratory, one of them out-of-sample rejected and reported as
rejected.

## A9. "Finite-horizon results are being read as stationary."

**Attack.** Chain ARLs, reference MSEs and ACF1s are quoted as if they were
properties of an invariant law. Outside the Gaussian core no such law is known
to exist.

**Answer.** Correct, and binding. P5's `T7` is Gaussian-scoped
(`p5/LIMITATIONS.md` §1), so P8 has **no** stationarity theorem in five of its
six families. Every chain quantity in P8 is a finite-horizon average over 50
post-burn-in cycles with a declared burn-in of 20, is called that, and is never
called stationary. `LIMITATIONS.md` `L7` states it; `PRIORITY_DEPENDENCY_AUDIT`
`D3` forbids importing `T7`. The word "stationary" appears in no P8 result
statement.

**Verdict: `SURVIVES` only because the claims were written to survive it.** The
underlying gap — no ergodicity outside the Gaussian core — is `OPEN` and is not
P8's to close.

## A10. "Local mathematical claims are being inflated into operational ones."

**Attack.** `Gamma_A > 2` and `rho_c < 1` are statements about a derivative at a
fixed point. P8 has a big matrix of them and will slide into talking about
safety.

**Answer.** `X6` and the **rejected** candidate `P7-E` are carried as
`NOT_ALLOWED_AS_PREMISE` (`PRIORITY_DEPENDENCY_AUDIT` `G5`) and the ban is
stated inside `THEORY.md` `P8-T1` itself: no operational number in P8 is derived
from `Gamma` or `rho_c`. Every operational number is measured by `E3`/`E4`. P7's
own boundary criterion is then applied **verbatim** per family (`G7`) to test
whether `rho_c` is operationally visible anywhere, and `P8-T2` — the only bridge
P8 has between the reference-error law and a monitoring quantity — is stated
together with the sentence "exact **and useless on its own**".

**Verdict: `SURVIVES`, by construction rather than by luck.**

## A11. "Protected-tree drift."

**Attack.** A long campaign touched something it should not have.

**Answer.** `results/protected_tree_manifest_pre.json` records a per-tree
SHA-256 over the git index for 24 protected trees at the anchor commit, before
any substantive work. Gate `G12` recomputes all 24 and additionally requires
`git status --porcelain` to contain nothing outside
`level4/closure_proofs/p8_model_class_robustness/`.
`tests/test_protected_scope.py` re-checks each tree independently, asserts that
no P8 write call targets a protected-tree path constant, and asserts that no P8
module loads a P5 or P6 *result* artifact.

**Verdict: `SURVIVES`.** `G12` passes: 24 protected trees, **zero**
differences from the pre-campaign manifest, and `git status --porcelain` reports
nothing outside the P8 namespace. `tests/test_protected_scope.py` re-checks each
tree independently and passes.

## A12. "P8 contradicts a historical claim."

**Attack.** Somewhere in this matrix is a number that contradicts a `CLOSED`
priority, and it has been quietly averaged away.

**Answer.** Every reproduction target is reported with both numbers, both SEs,
the `z` and the relative difference, whether it passes or not (`G1a`, `G1b`,
`G1c`, and `results/cross_priority_consistency.json`). The one place the
campaign *does* touch a historical difficulty — P4's failed `t3` replication
gate — is handled by `E6`, which measures the sampling behaviour of the same
estimand on P8's own field and reports it as a diagnosis, **not** as an
adjudication, with an explicit statement that P8 owns and edits neither P4 nor
Stage D. P8 changes no historical status: P4 stays `PARTIAL`, P5 stays
`PARTIAL`, Stage D stays `STAGE-D-PARTIAL`, P6 and P7 stay `CLOSED` with their
limitations intact.

**One live item this attack does surface.** P8's Gaussian **SR** gain sits
`0.70%`–`0.80%` below P3's at every window, `z = -1.75` to `-2.07`. `G1a` passes
(all `|z| < 3`), but four same-signed deviations are not noise. P7 recorded
exactly this and sharpened it at P3's own sample size; P8 is a third independent
implementation on an independent primitive field and **agrees with P7**
(`z = +0.66` to `+0.86`), not with P3. P8 reports it, records it in
`results/cross_priority_consistency.json`, and — like P7 — **does not resolve
it**, because P8 does not own P3's numbers. No P8 conclusion depends on it:
`rho_c` moves by under `0.9%` and P8's effects are `22%` and larger.

**Verdict: `NARROWED`.** No P8 claim contradicts a historical claim; but P8
independently corroborates a pre-existing, unresolved discrepancy inside a
`CLOSED` priority, and says so rather than letting `G1a`'s PASS bury it.

## A13. "`t3`'s exclusion is convenient."

**Attack.** The one family that breaks the pattern was declared ineligible for
the primary gate.

**Answer.** The exclusion is derived from the tail index, not from a P8
measurement: the `Gamma_A` integrand inherits the innovation tail index, so
`E|X|^3` diverges iff `nu <= 3`. It was declared in `config.MOMENT_MARGINAL`
before production, is re-derived (not read) by
`tests/test_families.py::test_declared_moment_marginal_family_is_exactly_t3`,
and `E6` measures the predicted consequence directly. **And it does not change
the verdict**: `t3` is the family with the *largest* `K`, so including it makes
the `G4` spread larger, not smaller. Every `t3` number is reported in full in
every table.

**Verdict: `SURVIVES`** — and the reader should note the exclusion is
conservative *against* P8's own preregistered hypothesis, not for it.

## A14. "Two closely related detectors is not 'detector robustness'."

**Attack.** CUSUM and SR are both two-chart likelihood-ratio schemes with the
same Gaussian design. Agreement between them is nearly a tautology.

**Answer.** Conceded. This is recorded as `LIMITATIONS.md` `L3` in exactly those
words, and it is the reason `G9` has **no threshold**: it requires the ratios to
be reported and requires no transfer claim beyond them. P8 declined to add a
third detector family (`P8_DEFINITION_AUDIT.md` §6 `O1`) because no closed
derivative theorem would stand behind it; the cost of that decision is precisely
this attack, and P8 pays it rather than manufacturing coverage.

**Verdict: `NARROWED`.** Any detector-invariance statement in P8 means *these
two frozen detectors*, and is worded that way.

## A15. "P7's boundary criterion has no error bars, so `G7` is noise."

**Attack.** `G7` applies a bare `max` over brackets at 4 sub-families per family
where P7 had 8. Two families flip. That is a coin toss, not a finding — in
either direction.

**Answer.** Correct, and it cuts both ways, so P8 reports both. The literal gate
**fails** (4 of 6 families reproduce P7's verdict against a required 5) and is
reported failed; it is not re-thresholded. Separately, an uncertainty companion
tests one-sided whether the boundary rate exceeds the best rate elsewhere across
**all 96** `(family, sub-family, metric)` comparisons carrying a replicate-level
SE, with BH at `q = 0.10`. Exactly one survives (`t3`, CUSUM, `m = 5`,
`fap100`, `+3.11` SE); `contam0.05`'s two verdict-flipping "peaks" are under
1 SE. So the *gate* failed on noise and the *science* is that P7's verdict
reproduces in five of six families with one narrow, uncorroborated exception.

**Verdict: `NARROWED`.** The gate stands failed; the scientific claim attached to
it is stated at the strength the uncertainty analysis supports, and the one
surviving signal is labelled a lead rather than a result because it does not
replicate under SR.

## A16. "The discrimination ratio's denominator is contaminated."

**Attack.** `R_Delta` divides by an in-control cycle length. If that comes from
the drift run's own pre-change cycles, it includes the `e_0 = 0` start, whose
first cycle runs at the nominal `465` and inflates the denominator.

**Answer.** It did, by 20–40%. Fixed: `R_Delta` is now computed against the
`E3` post-burn-in in-control ARL at the same cell and the same `rho`, and both
denominators are stored side by side in `results/closure_decision.json`. With
the correct control, CUSUM `gaussian` `m=1` `rho=1` gives `R_Delta = 0.976`
against P7's independently measured `1.06`; with the contaminated one it gave
`0.703` and would have understated the loss of discrimination.

**Verdict: `REJECTED` as an outstanding defect — it was real and is fixed** —
and the corrected number is the one that agrees with P7.

## A17. "The ramp conclusion is drawn from a metric that cannot see a ramp."

**Attack.** The delay metric is the first post-change cycle. A ramp's whole
question is accumulation over many cycles. Four post-change cycles cannot
answer it.

**Answer.** Conceded and acted on. The `rho = 0` half of the claim is exact and
does not depend on the horizon: the recursion collapses to
`e_{j+1} = mu_fresh - slope`, so the reference error is pinned near `-slope`
forever and the ramp is permanently absorbed. The `rho > 0` half is **not**
established: at `rho = 1` the recursion is a random walk with drift and the
offset does accumulate, which P8's horizon cannot measure. `RESULTS.md` §11 now
states the confinement explicitly and `LIMITATIONS.md` `S5b` records it.

**Verdict: `NARROWED`.**

---

## What this review changed

1. Every occurrence of "the window law holds" was replaced by the preregistered
   `NARROWED`/`REJECTED` wording of `EXPERIMENT_PROTOCOL.md` §10.
2. `H2a`–`H2c` are labelled exploratory in every document, and the sentence
   "out-of-sample" is used only where the cells were genuinely held out, with
   the `contam0.05` timing caveat recorded in the preregistration file itself.
3. Detector-invariance statements are worded as "across the two frozen detector
   families", never "across detectors" (attack `A14`).
4. The SR-calibration residual is carried explicitly into the `G4-D` discussion
   rather than only into `LIMITATIONS.md` (attack `A5`).
5. `A5`'s wording in `PRIORITY_DEPENDENCY_AUDIT.md` was corrected: P3's exact
   finite-support witnesses anchor the `rho_c` **arithmetic**, not the Monte
   Carlo estimator; the estimator is anchored instead by P8's own
   degenerate-detector construction.
6. `G7` records a **declared adaptation**: P7's ladder is clipped to
   `rho in [0,1]`, and cells whose `rho_c` is large enough that `4 rho_c` leaves
   the domain are evaluated on the rungs that exist. The rungs used are stored
   per sub-family.
7. **An uncertainty companion was added to `G7`** (attack `A15` below). P7's
   criterion is a bare `max` with no error bars, and at 4 sub-families it
   flipped two families. The companion tests all 96 boundary comparisons
   one-sided with BH at `q = 0.10`; it is `DESCRIPTIVE_ONLY`, it changed no
   gate, and `G7` is reported **failed** on the literal criterion regardless.
8. **The discrimination ratio's control was corrected** (attack `A16`). `R_Delta`
   was first computed against the drift run's own pre-change mean, which
   includes the `e_0 = 0` transient and inflates the denominator by 20–40%. It
   is now computed against the `E3` post-burn-in in-control ARL at the same
   `rho`, and both numbers are stored.
9. **The ramp claim was narrowed** (attack `A17`). `E4` runs only 4 post-change
   cycles, which cannot measure ramp accumulation. The claim is now confined to
   the first post-change cycle plus an exact `rho = 0` argument, and
   `LIMITATIONS.md` `S5b` records the gap.
