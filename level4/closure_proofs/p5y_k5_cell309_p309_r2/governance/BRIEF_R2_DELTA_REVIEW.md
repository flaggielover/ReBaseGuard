# Brief: the r2 delta review (gate step 6)

This brief is committed before it is issued (C5).

## Who and what

**Recipient.** A **fresh** independent reviewer. You wrote none of these:
* the r2 code;
* the verifier author's changes;
* the r2 plan or its addenda;
* any earlier r2 review.

**Boundaries:**
* no git write of any kind (no commit, ref, stash, config, fetch or push);
* NEW Γ309 TARGET EVALUATIONS = 0: never run `p309_driver.py execute` or `seal-only`, and never anything that could
  read a target input;
* no cell-305–309 values;
* no cell-307/308 file contents and no hashes of them;
* no decoy outputs opened;
* no network;
* scratch runs only under your own scratchpad, with `P309_SCRATCH_ROOT` and `P309_EVIDENCE_DIR` pointed there.

**What you review.** The **committed bytes and evidence** on branch `claude/p5y-k5-cell309-p309-r2` at the commit that
adds this brief, over the range `c902fe2f..` (r2's base is r1's final head). The coordinator's account,
`governance/R2_IMPLEMENTATION_REPORT.md`, is a guide only. Verify from git and from the preserved evidence, not from
that summary.

## What to assess (every item)

1. **The binding conditions.**
   * P1–P23 of `governance/REVIEW_R2_PLAN.md`, and F1–F11 of `governance/REVIEW_R2_PLAN_FOLLOWUP_1.md`.
   * For each one, say whether it is met in the bytes, deferred by the plan (owner decisions, worker steps), or not
     met.
2. **The QC11 repair after the freeze.** The sandbox base rule in the QC11 harness, the guard harness and the
   verifier author's helper. The pre- and postconditions. The refusal-detail assertions. The two R2-M01 mutants and
   what each must show.
3. **The namespace prohibitions (F1).** No ref in either production namespace is ever created. Check TestContext,
   the variant, the verifier helper, QC13, production_tokens, the planted control and QC12 T12.
4. **r1 immutability.** The r1 tree is `ecd1c359` at every r2 commit. The r1 branch is `c902fe2f`. r1's reviews are
   inherited by r1 path.
5. **Scratch-root portability (P7).** Every consumer refuses loudly.
6. **The host package, Q-HOST, the launcher, the drill and the evidence.**
   * The host package: provenance, continuity, the exclusion gate (start), the monitor (in-run), isolation, the
     preflight and the audit. Check the semantics against owner message 3. In particular:
     * the strict start gate versus the in-run heavy-work monitor;
     * the instance-unverified rule;
     * foreign processes recorded only as pid, uid, tag, CPU fraction and cmdline sha256;
     * nothing read inside a foreign root;
     * the only signal is the monitor's SIGTERM to its own parent.
   * The launcher: the unit properties, fixed names, no retry, refusals and the launch record.
   * The runner's Q-HOST: every refusal comes before the attempt directory and the RUN START line, and the abort
     path.
   * The drill: the topology, subprocess-only execution, the guards, confinement, F2 (repository invariance) and F4
     (the drill ledger in full), plus the new survival control and the host-package tests run in the clone.
7. **The scanner, QC12 and the pins.**
   * Check scanner coverage of the new files, and every new runner, reviewed-function, ref-mutation, verb-option
     and import entry, with its reason.
   * QC12 T11–T13 and their negative controls.
   * `governance/R2_REPIN_LIST.json`, row by row, against r1's config at F (hashes on CPython 3.11).
   * Recompute `production_read_path_pins` against r1's F.
8. **Equivalence P8(a)–(d).** Recompute from the passing drill's synthetic F' (its report names the commits; the F'
   bytes can be regenerated from the committed tree with the unmodified generators in your own scratch clone), or
   from git:
   * (a) the pins outside the namespace equal r1's F;
   * (b) reverse substitution for the relocation-only files;
   * (c) every remaining r1 token, classified;
   * (d) the frozen-parameter key diff, every difference classified.

   Confirm that **no scientific behaviour or parameter changed**: the SRK route, supplies, closure criterion, Γ309,
   the cell interval, budgets, workers, the outcome table, Stage 1a/1b/2, the exactly-once sites and the A38
   backstop.
9. **The failed development attempts and disclosures.**
   * All drill attempts in `evidence/drill/*`: each failure, its diagnosis and its fix.
   * The coordinator's disclosures: the mid-drill write; pushes made before the checkpoint tool; the missed label in
     the seal message; the self-audit A3 consequence that put owner message 4 in its own file; the open items in the
     report.
10. **Owner decisions.** Was any decision reserved for OD-R2-0 … OD-R2-6 made implicitly, beyond the disclosed
    provisional OD-R2-1(b)?

## Output

**`governance/REVIEW_R2_DELTA.md`.** Line 2 is exactly one of:
* `R2_DELTA_ACCEPTED`, with a section headed exactly `## Conditions` (it may be empty);
* `R2_DELTA_REJECTED`, with reasons.

Mark each condition **blocking-before-owner-decisions**, **before-freeze**, or **advisory**.

**Your execution ledger** goes in your scratchpad. Do not commit.
