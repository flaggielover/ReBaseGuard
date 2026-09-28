# Incident audit MB308 — addendum a1 (applies INCIDENT_INDEPENDENCE_REVIEW_MB308 conditions C1, C3, C8)

The a0 text (`INCIDENT_AUDIT_MB308.md`, commit `4b55c67e`) is kept unchanged. This addendum prevails where they differ.
Author: the coordinator (not independent). No committed tail figure and no validation-drift value is quoted here.

## C1(a) — stream A0 was exposed to the incident-03 sentence

* `streams/A0/a0_c2bx.py:4` cites `OV/streams/C_308/A0X/gen/C2B_ROUTE_SUMMARY.md` §2.1 (line 52). Line 49 of that
  section is the incident-03 sentence (a comparison scale derived from committed cell-308 figures). Stream A0's brief
  warned it about that line (brief 02, "NOTE: ... line ~49 contains a comparison sentence that is struck (incident
  03); do not use it"), but the brief could not prevent reading it. **Stream A0 was therefore exposed to the
  incident-03 scale.** The a0 audit's claim "the stream had no tail figure" is withdrawn.
* **Corrected evidence for conclusion 4 (no parameter selected using target information):** the ladder rungs were
  selected from findings F1–F4 at declared non-target drifts and from cost; U is a minimum over certified rungs, so
  adding a rung can only tighten a valid bound and no rung choice can be steered toward a threshold; every rung is
  far tighter than any such scale, so the scale could not discriminate between rungs (review Q3).

## C1(b) — exposures of streams F2 and F3 through theorem texts

* Streams F2 (INDEP) and F3 (INDEP_TUPLE) were directed to read `THEOREM_TCT.md` §1–§4 (both) and `THEOREM_TPT.md`
  §0 (F2). Those sections quote committed tail figures (TC-T Lemma G constants across cells 305–309; the incident-01
  provenance disclosure in TPT §0). Their reports say they read no tail number; that is inaccurate. **Correction
  (beside, not in, the committed reports):** both streams were exposed to committed tail figures through assigned
  theorem texts; neither used, computed on or wrote them (their outputs contain none; scanner PASS).

## C1(c) — coordinator exposures after the charter

See `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md` §E1′ (appended with this addendum).

## C1(d) — the builder's rehearsal and the pre-review formal build

* The formal builder (brief 11) ran `mb308_driver.py rehearse --cell 305` at 2026-09-28T16:07:45Z on untracked formal
  code (equality-only reproduction of C2's committed cell-305 record; tripwires on; ledgered as
  HISTORICAL_RECONSTRUCTION). Its output file or hash will be committed with the build (C7a), and the qualification
  review must verify on the frozen driver that the controls yield reproduction values and equality booleans only.
* The formal namespace `p5y_k5_cell308_mb_r1/` was being written during the incident review and is not covered by it.

## C1(e) — timeline corrections to a0 §2

| a0 claim | correction (verified in the object store by the review) |
|---|---|
| Theorem M first committed "02:00–04:03" | first committed at `7e851139` (09-28 03:56:59 +0900), corrected at `0d32a2e8` (04:03) |
| A0 components listed as existing at the audit | first committed at `646e7e18` (09-29 01:10 +0900), after the audit (`4b55c67e`, 23:46) and after design d0 (`c8b68d4d`, 23:44) which already fixed D4 |
| A0 study: "ladder fixed before any exact-scale or hull result" | contradicted by the ledger: first c2bx job 13:10:55Z, c1bh jobs 13:37Z, ladder runs from 13:43Z, and C1b d = 8 added after the ladder runs had started. Harmless for target independence (the choices rest on non-target findings), but the temporal claim is wrong |

## C3 — what "independent of target outcome" means in every document of this campaign

**Temporal and parametric independence only.** Every load-bearing element predates any cell-308 value of R-MB (none
exists), and no parameter was selected using target information. **Motivational independence is not claimed**:
Theorem M came from the overnight 308-exclusion stream, TPT/TPT-B were designed with the committed tail radius
structure known (incident 01), and R-MB's family and cell were chosen knowing committed 308 facts (I-a … I-e). The
result-chasing risk is **MEDIUM–HIGH** and is not lowered.

## C8 — scanner literals (disclosure and repair)

* The research scanner `code/c308_quarantine.py` (committed `33185113`) carried the committed tail figures as its own
  pattern table (`TAIL_FIGURES`, self-excluded from its scan) and, in its planted text control, a phrase of the
  incident-01 shape ("route gain … on the order-3 term; critical A0 … for the cell") built from committed figures.
* **Repair (scanner r2, with this addendum):** the pattern table moves to the sanctioned file
  `ledger/TAIL_FIGURE_PATTERNS.json`; the planted controls are built at run time from that file with neutral wording
  and no gain-beside-threshold phrase. The formal package's scanner must do the same (C8).

## Other conditions (tracked, not met by this addendum)

C2 (quarantine record) — `config/QUARANTINE_AMENDMENT_308_1.json` and a QUARANTINE_RULE_BREACH ledger line, with this
addendum. C4 (user ruling) — before any grant. C5 (briefs) — `ledger/briefs/` with this addendum. C6 (registry
completeness) — route registry r2, with this addendum. C7 (rehearsal and decoy handling) — formal build and
qualification. C9 (mechanics unchanged) — design d1 §5.4 and D10 stay as frozen.
