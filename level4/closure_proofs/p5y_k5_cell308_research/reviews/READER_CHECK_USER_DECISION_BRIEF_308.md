# Reader check (MBS-10): governance/USER_DECISION_BRIEF_308_SUCCESSOR.md, fresh non-holder reader readerUDB
NO_OUTCOME_EXPECTATION

## Scope and reader status

* Reader: readerUDB, a fresh non-holder. I have not seen any observation of the lost MB308 r1 target run, E1″'s
  contents, or any MBS308 incident or governance review.
* Read, and nothing else in the research or formal namespaces (checked 2026-09-29T21:13Z):
  * `governance/USER_DECISION_BRIEF_308_SUCCESSOR.md`, sha256 `b8f8e22e94580fecd8e35a816fa8ab887c20a5157bac53408f65aae099f3dffe`
  * `governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1.md`, sha256 `c170c726c43601ee8c3d028a64b0639708c8b5799698aaf1ced62f5a13ee152c`
  * `ledger/USER_TEXTS_SUCCESSOR_308.md`, sha256 `16f0efccbcf92b7787d261701399bea8d979836a8eb59a576e678fa33440a2f9`
* The only other file I touched was `code/c308_quarantine.py`. I read the signature of `log_event`, not the file,
  and called it once. I did no scientific computation and no git writes. The only tools I used were text comparison
  (`sed`/`diff`), `grep` and `shasum`.

## 1. Outcome expectation (MBS-10): none found

I read every sentence of the brief and grepped it for margin, likelihood, closure, expectation, chance, probability,
promise, worth, near, estimate, recommend, benefit, improvement and numeric or percentage values. The brief contains:
* no margin, estimate or likelihood of MB-S closing cell 308;
* no statement or hint of how close anything is;
* no "worth running" argument drawn from cell 308's structure.

The only structure of cell 308 it mentions is the frozen criterion `Γ_dec = g_hi + max(P*_B, P_hi)`. That appears
only inside the verbatim O3 quote and carries no value.

Borderline items I checked and accept:
* "Caps change only the probability of completion, never Γ" (A.2, and O4 in §D). This describes how caps work
  (review N3). It gives no estimate and nothing about closure.
* "EVAL_CAP 8 h" (A.2(i)) is a frozen parameter, not an observation from a run.
* "MEDIUM–HIGH at the upper end" (§C) is a rating of result-chasing risk, not an expectation about the outcome.
* The heading "IF THE FIRST FORMAL ROUTE DOES NOT CLOSE 308" and "observed target margin" are the user's own
  verbatim §26 text.
* The host readiness paragraph (§F) concerns host gates today, not the outcome. See N-6 for a separate point.

## 2. Verbatim sections: byte-identical

I compared these by exact line-range `diff`; every pair is identical:

| Brief section | Brief lines | Source | Source lines |
| --- | --- | --- | --- |
| §D, O1–O5 with their reconciliations | 57–117 | A1 §1 | 21–81 |
| §E 3a (§20) | 121–145 | ledger | 885–909 |
| §E 3b (§21) | 147–165 | ledger | 911–929 |
| §E 3c (§23) | 167–185 | ledger | 931–949 |
| §E 1c (§26) | 187–208 | ledger | 31–52 |

* §D has the full content of A1 §1: nothing is omitted or added, and there is no trailing whitespace.
* The §E sub-headings are identical to the source's. The brief orders them 3a, 3b, 3c, 1c, which only reorders them.
  Each keeps its source numbering.

## 3. Neutrality between options: sentences I would change

Nothing below is an outcome expectation. These are framing asymmetries. Whatever changes are made must **not**
state what any option would contribute to cell 308's result.

**N-1 (A.3, lines 19–20).** Current text: "Is an INDETERMINATE-class outcome of MB-S **final** for route MB on
cell 308? The incident review recommends "final"."
* Reason: A1 §3 item 6 poses two options: "final", or "a further successor may be governed". The brief names only
  the first, and attaches a reviewer's endorsement to it alone.
* Proposed: "Decide one of: (a) an INDETERMINATE-class outcome of MB-S is final for route MB on cell 308; or (b) a
  further successor may be governed (A1 §3 item 6)."
* Keep the incident review's recommendation as an attributed input, for example in §C with its reference. Do not use
  it to frame the question.

**N-2 (B.6, line 38).** Current text: "confirm finality (A.3) and the member decision (A.4)."
* Reason: "confirm finality" assumes the answer is "final". It is inconsistent with B.4, which confirms "the caps
  option" without favouring either.
* Proposed: "record your decision on finality (A.3) and on the members (A.4)."

**N-3 (A.4, lines 22–27).** The heading says "trade". Option 2 lists five costs ("new code, new reviews, a new
qualification, the loss of the determinism argument, and a fresh incident re-rating"). Option 1 lists only a
deferred, post-result consequence.
* Reason: the two options have unequal consequence lists, and "the loss of" is value-laden.
* Proposed heading: "The C11R-I2 / COR-T members (MBS-7; …)".
* Proposed wording for each option, written in parallel:
  * **Keep MB-S unchanged.** MB-S is frozen with MB r1's science only (S11 byte identity), and the determinism
    argument (A1, review N2) and the current re-rating (conditional on byte-identical science) stand. Any later use
    of those members on 308 is post-result, is governed by the brief's §26 path, and starts at not lower than HIGH.
  * **Adopt them before the freeze.** MB-S moves to the S4 "changed science" branch: new code, new reviews and a new
    qualification. The determinism argument no longer applies, and a fresh incident re-rating is required
    (presumptively HIGH).
* Do not add any statement of what the members would do for cell 308. That would breach MBS-10.

**N-4 (A.1, lines 11–13; B lead-in, line 31).** The go/no-go decision is shown only as "go". "The ruling must
expressly: 1. authorise a second consumed evaluation …" reads as if authorisation is the expected ruling, and the
brief never says that withholding permission is an equally available option.
* Proposed addition to A.1: "You may give or withhold this permission. If you withhold it, there is no successor
  freeze and cell 308 stays OPEN. MB r1 stays INDETERMINATE either way (A1 classification and §5; O1′
  reconciliation)."
* Proposed lead-in for B: "If you decide to authorise a successor grant, the ruling must expressly:".

**N-5 (minor; §E heading, line 119).** "Your own words (verbatim …)" is a selection of four restraint passages
(§20, §21, §23, §26).
* The same ledger also records §1a, §1b and the §2 overnight program. A1 §2 itself cites §1b and the overnight
  program's "unless the user explicitly authorizes" as the user's words on successors.
* Proposed: say what the selection is, for example "Your own words: the passages the S1 ruling overrides and the
  passage that governs post-result use (verbatim excerpts …)". Optionally add §1a and §1b verbatim, so the user sees
  their continuation texts next to their restraint texts.

**N-6 (§F, lines 222–224: host readiness).** "this host would refuse today. Memory pressure is elevated, thermal
level is 1, …"
* Reason: the reading is undated. I cannot check whether any of it overlaps the MB r1 target-run host observations
  that E1″ names, because I am a non-holder.
* Proposed: give the reading a UTC timestamp and its source, so it is clearly a present-day, target-free builder
  reading.
* Ask the holder side or scanner to confirm it repeats no MB r1 run observation (S13).

**N-7 (note only; §D O5).** O5 cites `reviews/REVIEW_EXECUTION_INTERRUPTION.md` lines 463–464. S13 forbids a
successor brief from pointing to REVIEW_EXECUTION_INTERRUPTION §4b.
* The quoted words contain no runtime or host value, and A1 labels them "C6 / postexec §4". I was not allowed to read
  that file, so I cannot verify that the lines are outside §4b.
* No change is proposed, because §D must stay verbatim from A1 §1. The scanner or holder side should confirm the line
  range.

**N-8 (clarity; A.2, line 14).** "exactly one of two options, chosen mechanically": it is unclear whether the user
chooses, or a rule does.
* Proposed: say which is meant, for example "exactly one of two options, chosen by you; the resulting caps then follow
  mechanically", if that is MBS-8's intent. I could not check MBS-8.

## Summary

* No outcome expectation of any kind.
* §D and §E are byte-identical to their sources.
* The framing is not fully neutral. N-1 to N-4 are recommended before the brief goes to the user. N-5 and N-8 are
  minor. N-6 and N-7 need a holder-side or scanner confirmation that I cannot give.
