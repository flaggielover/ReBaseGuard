# Independent static review of the r2 packet (freeze c4716a88): FAIL

The reviewer was a separate read-only agent session that ran no real computation. **Science: PASS. Governance:
FAIL.**

## Forgery test

In scratch clones, a forged amendment plus authorization obtained LAUNCH_PERMITTED in 4 of 5 variants. Across the
variants:
- the review file said FAIL, but the amendment claimed PASS;
- amendment and authorization sat in the same commit;
- the authorization was backdated;
- the executor was untracked;
- only a symlinked authorization was refused.

## Findings

| # | finding | summary |
|---|---|---|
| A temporal | PASS_WITH_NOTES | r2 introduced once; r1 JSON byte-identical; the r1 manifest is stale as history |
| B cell selection | PASS | Citations corrected; POSITIVE downstream limits disclosed |
| C result-driven gates | PASS | |
| D qualification / science | PASS_WITH_NOTES | Q15 excluded from `science_requires` while cost failures seal VOID (inconsistent) |
| E object / verdict | PASS_WITH_NOTES | Aggregate label text mismatch; one m's VOID could hide another m's NEGATIVE |
| F precision / retry | PASS_WITH_NOTES | RUN_FAILED class self-declared; SIGXCPU overlaps external-signal; deleting a seal defeats P09; pre-arithmetic refusals consume attempt slots |
| G K5-B consumption | PASS_WITH_NOTES | K1 records source and per-record manifest check unspecified |
| H negative results | PASS_WITH_NOTES | VOID exposure of cell 0 not disclosed |
| I address / attempts | PASS | |
| J authorization fail-closed | **FAIL** | P06 trusted the amendment's own verdict and did not require committed pins; P04 allowed collapsed commits and a forgeable UTC with no publication anchor; P03 had no literal identity anchor; a genuine activation was impossible because the template's text contains SET_AT_ACTIVATION |
| K r1 repairs | PARTIAL | Items 2, 5, 6 partial; 7 not met |
| L amendment | PASS_WITH_NOTES | Adapter-in-sources and commit order not enforced |
| M host | PASS_WITH_NOTES | Host and producer identity sha256 never recomputed |

## Required repairs

1. **Commits.** Strictly ordered freeze < amendment < authorization, published on the remote ref; UTC ≤ now.
2. **Identity.** A literal freeze-identity anchor; authorization non-activation fields must equal the template.
3. **P06.** Verdict read from the review file; pins committed before the amendment; adapter pins among the sources;
   amendment after the freeze.
4. **Activation.** Fix the genuine-activation blocker.
5. **Consistency.** Make Q15 handling consistent; split SIGXCPU and wall-timeout from the transient classes.
6. **Disclosure.** Records source plus per-record manifest check; VOID exposure disclosure.
7. **Test.** A committed-forgery test in a temporary repository.

## Disposition

Addressed by the r3 re-freeze:
- **Verifier:** anchored on the published ref, with strict commit order, a freeze record, review-file verdict
  lines, and an append-only ledger with committed launch notices.
- **Rules:** failure class derived mechanically, launch slots, and a whole-record VOID.
- **CPU:** soft < hard limits.
- **Disclosures:** records source and VOID exposure.
- **Tests:** a git-repo harness in which F1 (the r2 forgery) is refused and F2 (a genuine activation) passes the
  governance checks.

r2 was never authorized or executed.
