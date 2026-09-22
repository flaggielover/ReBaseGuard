# Handover to the C7 independent adjudicator

You are the final adjudicator for campaign **C7**. Fresh context; assume nothing.

Working tree: `/Users/suzhe/ReBaseGuard-k5c7`, branch `p5y-k5-tail-c7-e2`, HEAD `ce018ffa`.
Namespace: `level4/closure_proofs/p5y_k5_tail_c7_e2_lambda309`.

## What already happened

A hostile fresh-context reviewer returned **NOT_READY** with 17 findings, including 2 CRITICAL that
were *live exploits of the campaign's own public API*. Its report is committed at
`review/REVIEW_C7_PREPUBLICATION.md`. The campaign then made repairs and re-ran everything.

**Your primary job is not to re-review the mathematics.** The reviewer verified items A–E by hand and
found the proofs correct, and an independent from-scratch numerical checker found no disagreements.
Your job is the thing this programme actually keeps getting wrong.

## The question that matters

**Did the repairs land?**

This programme has, on at least five occasions across C4, C5 and C6, recorded a repair as complete
when it had not been made — and once published a reviewer's claim adopted without verification that
turned out to be false. The campaign has just asserted, in commit `ce018ffa`, that all 17 findings
are addressed. **Verify that claim finding by finding against the committed tree.** For each of the
17, decide: LANDED, PARTIAL, or NOT_LANDED, and say how you checked.

Pay particular attention to:

1. **Findings 1 and 2 (CRITICAL).** Re-run the reviewer's exploits yourself. The report gives them
   explicitly: a certificate with `source: "elementary"` and `a_grid = ['-47/20']`, and evaluation at
   `e = 1.90`. Confirm they are now refused, and confirm the refusal comes from a real guard rather
   than from an incidental failure for an unrelated reason.
2. **Finding 4.** The mutation suite's four rounding-direction mutants still SURVIVE. The campaign
   says it now reports them as surviving rather than hiding them. Check that `MUTATION_CLASS` is not
   quietly laundering them, and decide whether the current presentation is honest.
3. **Finding 3.** `E_tau_prime_finite` was dead code while a docstring called it "certified". Confirm
   it now actually executes on the path that produces the published bound.
4. **Finding 14.** The frozen gate forbids "Monte Carlo of any kind"; a Monte Carlo cross-check was
   run anyway. Judge whether the disclosure in `ERRATUM_C7_GATE.md` E4 and the certificate's
   `external_non_evidence_activity` is adequate, or whether this should block publication.
5. **New defects introduced by the repairs themselves.** The repairs touched the theorem, the
   mutation suite, B0, the fact-checker and the certificate. Look for damage.

## Also decide

- Is `C7_CLASS = STRENGTHENED` the right verdict under the gate's own frozen rule?
- Is the PRIMARY selection (largest bound with an EMPTY dependency set) correctly applied?
- Are the gate's `forbidden_conclusions` respected — C7 must NOT claim cell 309 is closed, that K5 is
  closed, that any other cell changed, or that the R-stage may launch?
- Is the erratum the right instrument, or did the campaign effectively amend a frozen gate?

## Constraints

- Do NOT contact AWS or Vultr. No ssh. No package installs. No `numpy/scipy/flint/mpmath/sympy/gmpy2`.
- Do NOT modify any file except your report. Do NOT run state-changing git commands.
- Running the campaign's producers REWRITES evidence files — if you run one, say so in your report.
  Prefer reading the JSON and running probes out of tree.
- Use `PYTHONINTMAXSTRDIGITS=0`.

## Output

Write `review/ADJUDICATION_C7.md`. Include a table of all 17 findings with LANDED/PARTIAL/NOT_LANDED
and your evidence. End with exactly one verdict line:
`ACCEPTED`, `ACCEPTED_WITH_SCOPE_LIMITATION`, `ACCEPTED_WITH_CONDITIONS`, or `REJECTED`.

Do not repair anything. If you find something unverifiable from the committed tree, say so rather
than inferring it.
