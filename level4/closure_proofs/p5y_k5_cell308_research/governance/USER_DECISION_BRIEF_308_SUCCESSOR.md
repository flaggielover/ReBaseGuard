# Decision brief for the user: the cell-308 successor MB-S (freeze decision now; S1 ruling later)

**Revision r1.** Neutrality repairs N-1 to N-6 and N-8 from the non-holder reader check
(`reviews/READER_CHECK_USER_DECISION_BRIEF_308.md`, NO_OUTCOME_EXPECTATION), then R-1 to R-9 of its re-check
(`reviews/READER_CHECK_USER_DECISION_BRIEF_308_R1.md`). Earlier texts are in git history.

**What this is.** It prepares the decisions the governance leaves to you. **It contains no expectation of MB-S's
outcome**: no margin, estimate, likelihood or "worth running" argument (MBS-10). A research scanner and a non-holder
reader check this before you receive it.

**What it authorises.** Nothing: no freeze, no grant, no target step. New cell-308 target evaluations: 0.
MB308 r1: CELL308_EXECUTION_INDETERMINATE (ADJUDICATION_ACCEPTED `e451e634`). Cell 308: OPEN.

## A. Decisions needed before the successor freeze (§14 / G2; S16(c); MBS-6, MBS-7, MBS-8)

1. **Freeze permission: grant or withhold.** MB-S keeps MB r1's science and is "an r4 with the same caps" in
   substance. §14 and G2 require a new explicit user decision, recorded before any such freeze.
   * **Withholding permission is equally available.** In that case MB-S stays an unfrozen, pre-freeze build (its
     implementation review and the T6 condition M1 are pending at the time of writing), and cell 308 stays OPEN with
     MB r1 INDETERMINATE.
   * **Granting permission** meets only freeze gate S16(c). The freeze still needs S16(b): the route conditions
     RC1–RC6 established as facts, and the implementation review and M1 accepted. It does **not** authorise a
     target step (see B).
2. **Caps (MBS-8).** Exactly one of the two options below. "Mechanically" means that no cap value is set by hand;
   the option alone determines the values.
   * **(i)** keep MB r1's r3 caps (EVAL_CAP 8 h; per-job CPU caps as frozen); or
   * **(ii)** apply MB r1's frozen §3.2 rule to MB-S's own official decoy runtimes under its new launcher.

   Either way Q12 must pass. Caps change only the probability of completion, never Γ.
3. **Finality (MBS-6; S1 item 6).** Record your decision, one of:
   * **(i) final:** an INDETERMINATE-class outcome of MB-S ends route MB on cell 308;
   * **(ii) not final:** a further successor may be governed after an MB-S INDETERMINATE, through its own process
     and ruling.

   The successor incident re-rating (reviewINC2, `b7e62dec`, condition MBS-6) recommends (i). Under either option, any evaluation of 308 after the MB-S marker,
   of any route, starts at a risk rating of not lower than HIGH (MBS-5(b)).
4. **The member decision on C11R-I2 / COR-T (MBS-7; route erratum E1 DR1; route re-check R3-N2).** Record one of:

   | | (i) keep MB-S unchanged | (ii) add the members before the freeze |
   |---|---|---|
   | science | MB r1's, byte-identical | changed (the S4 "changed science" branch) |
   | determinism argument (successor value = lost-run value) | applies (under the pin) | does not apply |
   | work before any freeze | the current build and reviews | new code, new reviews, a new qualification |
   | incident rating | MEDIUM–HIGH, upper end, conditional, **and only under the T6 conditions M1–M6 (M1 pending); otherwise HIGH** (§G) | a fresh re-rating, presumptively HIGH |
   | later use of these members on 308 | post-result; the brief's §26 path; not lower than HIGH | not applicable (already included) |

## B. The ruling needed before any successor grant (S1; governance addendum A1 §3 with erratum E1 D1)

**You may give or withhold this ruling.** Withholding it leaves the successor without a grant: no marker, no target
step, cell 308 OPEN. If given, the ruling must expressly:
1. authorise a **second consumed evaluation** of cell 308 (count 2) under MB-S only, **notwithstanding the brief's §21
   ("execute cell 308 exactly once") and mitigation 5**;
2. lift mitigation 5 for MB-S, and confirm that the brief's §20–§21 and §23 **continue to bind MB r1 unchanged**;
3. state that MB-S is **a new governance decision, not a rerun on host grounds** (E3); MB r1 stays INDETERMINATE;
4. confirm the caps option (A.2);
5. re-affirm U1–U8 of your C4 ruling;
6. record your decisions on finality (A.3) and on the members (A.4).

## C. What the ruling is taken with in view (C4 list, extended; MBS-10)

* Incidents 01–03 and their residue, H4.3b, the coordinator inferences I-a…I-e, and E1′
  (`ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`).
* The original incident-independence review (`reviews/INCIDENT_INDEPENDENCE_REVIEW_MB308.md`).
* **E1″ and its errata 1–2**, which name the MB r1 run observations and their holders.
* **The successor incident re-rating** (`reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md`, `b7e62dec`,
  INCIDENT_AUDIT_ACCEPTED):
  * the rating is **MEDIUM–HIGH at the upper end, conditional** on byte-identical science on the pinned platform;
  * triggers T1–T6 move it to HIGH;
  * conditions MBS-1…MBS-14;
  * the T6 ruling on the builder's disclosed exposure (`reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308_T6.md`,
    `ff2280e9`) is **T6_FIRED_MITIGATED**; see §G.
* The governance texts O1–O5, verbatim (§D below), and the brief's §20, §21, §23 and §26, verbatim (§E below).

## D. The governing texts O1–O5 (verbatim, from governance addendum A1 §1)

**O1. Qualification review E3.** `47bb37c7`, `review/MB308_QUALIFICATION_REVIEW.md` lines 439–441:

> **E3. Provenance never changes the result (review r3 E2).** Host provenance never changes the status, the outcome
> or exactly-once. There is no rerun and no reinterpretation on host grounds. An EVAL_CAP hit is the pre-declared
> INDETERMINATE.

**O1'. Protocol §14.** `c46434a3`, lines 370–372:

> **Host provenance never changes the status, the outcome or exactly-once**: there is no re-run and no
> re-interpretation on host grounds.

*Reconciliation.* The successor is **not** a rerun of MB r1 on host grounds. It is a new campaign under a new
governance process (E7 and C6 below) and needs a new user decision. It changes no MB r1 status or outcome. MB r1
stays INDETERMINATE for ever. The S1 ruling must state this (GC-3).

**O2. Exposure-disclosure mitigation 5.** `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md` §E3, "Mitigations, bound into
the charter":

> 5. at most one target evaluation, of one frozen route.

The incident review Q4 relied on it (`reviews/INCIDENT_INDEPENDENCE_REVIEW_MB308.md` line 215):

> There is exactly one sealed evaluation, and NOT_CLOSED and INDETERMINATE are pre-declared outcomes.

*Reconciliation.* A successor would be a **second** target evaluation of cell 308. Mitigation 5 binds this campaign's
charter, so it can be lifted only by the user's S1 ruling, expressly (GC-3). Q4's premise changes with it, so the
risk rating is re-rated (GC-5).

**O3. Incident-review C9.** Lines 386–389:

> **C9, unchanged mechanics.** These stay exactly as designed:
> * D10: nothing but R-MB is evaluated on 308;
> * d1 §5.4, frozen: Γ_dec = g_hi + max(P*_B, P_hi), strict, exact;
> * one sealed execution, with no retry and no post-result tuning.

*Reconciliation.* The successor keeps D10 and §5.4 unchanged (GC-4). "No retry" binds MB r1. A successor is a new
execution under a new governance process and a user ruling, never a retry inside MB r1.

**O4. The pre-declared consequence of §14.** Line 361:

> Freeze r3 is **never re-run**, and **no r4 with the same caps** is made, without a new explicit user decision
> recorded before it.

**Qualification review G2.** Lines 397–399:

> No file under `code/`, `protocol/`, `theory/`, `tests/`, `config/`, `errata/` or `evidence_prefreeze/` changes
> after this review. Any needed change means STOP: no same-round repair and no r4 with the same caps without a new
> recorded user decision (§14).

*Reconciliation.* MB-S keeps MB r1's caps (route audit, `bddd85f8`). It is therefore "an r4 with the same caps" in
substance, and **its freeze needs a new explicit user decision recorded before it** (GC-9). That decision must also
settle the caps question: keep MB r1's caps, or re-derive them from decoy runtimes under the new launcher (review N3:
caps change only the probability of completion, never Γ).

**O5. Recovery-chain C6 and postexec §4.** `reviews/REVIEW_EXECUTION_INTERRUPTION.md` lines 463–464:

> no new grant, rerun, resumption or recomputation of cell 308 under route MB r1. Lost information is recomputed
> only through a new independent governance process and a new user decision (E7);

*Reconciliation.* **E7 and C6 are the operative path**, not §10 step 3. The successor is that new independent
governance process. It needs the new user decision.

## E. Your own words (verbatim, from `ledger/USER_TEXTS_SUCCESSOR_308.md`)

The selection is the brief's §20, §21 and §23 of 2026-09-28 (on exactly one execution) and its §26 (on successor
routes). Other passages of that brief are not reproduced.

### 3a. The brief's §20

======================================================================
20. EXPLICIT GRANT
======================================================================

QUALIFICATION_ACCEPTED does not itself authorize target execution.

Create a separate explicit grant.

The grant must bind:

- cell 308;
- route;
- freeze commit;
- theorem;
- implementation;
- driver;
- manifest;
- qualification;
- qualification review;
- exactly one target execution;
- closure-only interpretation unless separately authorized otherwise.

No floor/adoption permission is implied.

### 3b. The brief's §21

======================================================================
21. EXACTLY-ONCE 308 EXECUTION
======================================================================

Only after the grant:

execute cell 308 exactly once.

Use the strongest already-frozen qualified route.

Do not compare several candidate routes on 308.

Do not run parameter sweeps.

Do not tune after seeing the result.

The consumed marker must make any second execution refuse.

### 3c. The brief's §23

======================================================================
23. POST-EXECUTION REVIEW
======================================================================

Run all frozen post-execution checks.

Then launch a fresh independent execution reviewer.

Required verdict:

    EXECUTION_ACCEPTED

or:

    EXECUTION_REJECTED

No rerun on rejection.

### 1c. The brief's §26

======================================================================
26. IF THE FIRST FORMAL ROUTE DOES NOT CLOSE 308
======================================================================

A valid negative result is NOT permission to tune against 308.

Do not use the observed target margin to redesign the same route.

Preserve the result.

Any successor route must have an independently defensible scientific
motivation not derived from chasing the observed target result.

If no such route exists:

stop with the negative result.

If such a route genuinely existed prospectively before the target was
seen, document temporal evidence and obtain independent governance
review before considering it.

## F. Where the successor stands

* **Governance.** GOVERNANCE_ACCEPTED (research `00a432df`; errata `a7c969e8`).
* **Route.** ROUTE_ACCEPTED (research `87d0b2b9`).
* **Incident re-rating.** Accepted (`b7e62dec`).
* **Pre-freeze build.** `afba20e5` on `p5y-k5-cell308-mbs-r1`, target-free:
  * a crash-safe durable state machine;
  * governed checkpoints with mandatory resume;
  * launchd detachment;
  * a host contract.

  The independent implementation review is **pending at the time of writing**.
* **Host readiness for any future official run** (reported by the successor builder in its BUILD_REPORT, from its
  readings at the end of its build, about 2026-09-29 21:00Z; a reading at that time only): at that time, this host
  would have refused. Memory pressure is
  elevated, thermal level is 1, automatic macOS and critical-update installation is on, and another application
  exceeds the CPU exclusivity limit. Disabling automatic installation for the whole window is your action. The
  campaign never changes system settings.
* **Conditions register.** `governance/SUCCESSOR_CONDITIONS_REGISTER_308.md`.

## G. Trigger T6: fired and mitigated (the T6 ruling's M7 disclosure)

* **The ruling.** `reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308_T6.md` (research `ff2280e9`, sha256
  `d091e4ba4a31f0aa5723435add320ddbe43ee1f1d9b726d00facd861414e77e4`), line 2: **T6_FIRED_MITIGATED**.
* **What happened.** The successor builder read the formal MB r1 postexec recovery record before its exposure
  instruction reached it, and then held the implementation role. That record holds:
  * the run chronology;
  * the coordinator-reported launch host readings;
  * a qualitative statement about worker-pool load;
  * caffeinate PIDs;
  * probe and trial object ids.

  No values are reproduced here.
* **M2 (satisfied).** An earlier holder (reviewEXEC) confirmed by a ledger line (2026-09-29T21:13:47Z) that the record
  holds no per-job runtime, no per-worker observation from the coordinator's in-run audit, and no per-coalition CPU
  value.
* **M1 (pending at the time of writing).** An itemised provenance trace of every constant in the build, by the
  non-holder implementation reviewer. Anything untraceable must be re-derived by a non-holder, or the rating becomes
  HIGH.
* **The rating.** MEDIUM–HIGH (upper end) **only under M1–M6**; otherwise HIGH. The builder takes no caps,
  qualification, qualification-review or S1-brief role (M4).
