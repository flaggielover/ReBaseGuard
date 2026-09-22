# Handover to the C7 fresh-context reviewer

You are reviewing campaign **C7** in the ReBaseGuard P5Y/K5 programme. You have no prior context and
should not assume any. Everything you need is in this namespace plus the predecessors it reads.

## Disclosure of a phase-ordering deviation — read this first

The campaign plan put a fresh-context review (phase 8) **before** the final certified evaluation
(phase 9). That is **not** the order that happened. The gate was frozen before the final evaluation,
which was the load-bearing requirement, but a draft certificate
(`evidence/certificate/C7_CERTIFICATE.json`) already exists at the time you are reading this.

This is disclosed rather than concealed, and it is being repaired in substance: **if you find anything
material, the certificate will be regenerated after the fix.** Treat the existing certificate as a
draft that must survive your review, not as a result that has already stood. Do not soften a finding
because an artifact already exists.

A second disclosure: the gate itself
(`config/FEASIBILITY_GATES_C7.json`) states that it was frozen **after** exploratory evaluation and
does **not** claim blindness. Its section `disclosure_of_non_blindness` argues that this is sound
because every prospective choice affects only tightness and never validity, and because the verdict
rule contains no tuned threshold. **Test that argument.** If you can construct a choice admitted by
the gate that changes validity rather than tightness, that is a finding of the first order.

## What C7 claims

`Λ_309 = E_a[τ]` for the frozen CUSUM model (K = 1/2, H = 5, m = 5, cell 309) satisfies

- **3.586306094** with an EMPTY dependency set (the PRIMARY claim), and
- 3.600337620 if Lorden (1970) is admitted, 3.597941639 if the Arb/FLINT registry is admitted.

C4's committed floor is 3.297250282. The C5-T critical `A0` is 3.266415728, so C4's margin was
0.9440 % and C7's PRIMARY margin is 9.7933 %.

## What to check — items A–L

- **A.** Is Theorem C7-E2 correct? Specifically: is `E[R] = ∫ψ dμ` with `μ` a *probability* measure,
  and does the total mass really telescope to 1?
- **B.** Are the two monotonicity facts (`r` decreasing, `f` decreasing) true **on all of ℝ**, as the
  code now assumes after a positivity guard was removed? The removal is deliberate; verify it.
- **C.** Is the multi-tier LP argument correct, in particular that the greedy assignment really is the
  minimiser and that the constraint set is what the theorem says?
- **D.** Is Lemma C7-U correct? Check the independence step `{τ′ ≥ n} = {S_{n−1} ≤ H} ⫫ V_n`, the
  rearrangement (which divides by `E[V] − g(a)`), and whether `E[τ′] < ∞` is genuinely established
  rather than assumed.
- **E.** Is every rounding direction sound — that is, does every interval endpoint chosen push the
  final value DOWN? Find any place where an endpoint choice inflates the bound.
- **F.** Is `psi_exact` genuinely independent of `psi_lo_at`, or do they share enough code that the
  guard is circular?
- **G.** Is the claim "`ψ` decreasing is NOT proved, so `psi_exact` is used only as a guard" correct,
  or is `ψ` in fact provably monotone (which would mean C7 left a tighter bound unused)?
- **H.** Does the U-provenance mechanism actually close the hole it claims to close? Try to obtain a
  bound from an understated `U`.
- **I.** Is the acknowledged residual gap in `evidence/mutations/C7_MUTATIONS.json`
  (`coverage_limitation`) stated accurately, or is it wider than admitted?
- **J.** Does any artifact assert something that is not true of the committed tree — a repair recorded
  as landed that has not landed, a number that does not match its source file? **This programme has
  made that exact error at least five times.** Check every number in `README.md` against the JSON,
  and every number in the JSON against C4's and C5's committed files.
- **K.** Is the compute boundary genuinely respected? `0` new-real, `0` kernel evaluations, `0` remote
  hosts, guard DENY. The B0 audit asserts this via an AST import walk — verify the walk is not
  evadable.
- **L.** Are the forbidden conclusions respected? C7 must NOT claim cell 309 is closed, that K5 is
  closed, that any other cell changed, or that the R-stage may launch.

## How to report

Write `review/REVIEW_C7_PREPUBLICATION.md`. End with an explicit verdict line, one of
`READY_TO_PUBLISH`, `READY_WITH_CONDITIONS`, `NOT_READY`. List findings as numbered items with
severity. **Do not repair anything yourself** — report, and the campaign will repair and re-run.

State plainly if a claim is unverifiable from the committed tree; do not upgrade it by inference.
