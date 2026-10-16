# Target-free recommendations for the two new owner numbers (Cell-308 Cloud route r1)

**Status: RECOMMENDATION · NOT ADOPTED · PROVENANCE CHECK PENDING (handoff B3).** S12 S5 and S13 (amendment erratum
E2.7, procedure r3 §5) require two new numbers, fixed by the owner before the Phase-1 inventory of the named machine.
The owner instruction of 2026-10-16 (continuation) says: "Where a new number is needed, develop a target-free,
evidence-backed recommendation and obtain the required provenance check before its adoption."

Each number is derived only from:
* accepted ratification text;
* a published provider schedule, quoted.

No MB r1 target-run observation, no MB r1 runtime and no new-host reading was used. `new_target_evaluations = 0` ·
`cell309_activity = none`.

## 1. Accepted basis (quoted verbatim)

From `governance/CONSTANTS_RATIFICATION_MBS308.md` (ACCEPTED):

> row 18, MAX_RESUMES: "3 (attempt ≤ 4) | **ratified** | … Each extra attempt costs up to 8 h awake and lengthens the
> no-update window."
>
> row 19, DEADLINE_S: "7 days after the marker | **ratified** | Lower bound: 4 × 8 h = 32 h of awake work, plus up to
> about 3 days for the operator to notice an interruption over a weekend (resume is operator-launched), is about 4.3
> days. Upper bound: the no-automatic-install window (marker to deadline) should stay a bounded exposure, about one
> Rapid-Security-Response cadence. A platform change is terminal anyway (DR2 b). 7 days satisfies both."

From brief R2 (reader-checked), line 280: under MBS-8 (i) "the maximum awake budget is fixed now (4 × 8 h)". Under (ii)
"it is 4 × the derived EVAL_CAP, which may be above or below 8 h (its floor is 6 h)".

Provider schedule, quoted verbatim from Ubuntu, "About kernel stable release updates (SRU)",
https://ubuntu.com/kernel/docs/explanation/stable-release-updates/ (page modified 2026-10-13; retrieved 2026-10-16):

> "Since August 2023, the Ubuntu Kernel team has adopted a 4/2 Kernel SRU cycle to improve predictability and
> responsiveness. It involves a 4-week ("4/") stable update cycle for regular fixes and features, combined with an
> additional mid-cycle 2-week ("/2") update focused on urgent CVE security patches and critical fixes." … "SRU cycle
> dates are tentative. As such, they cannot be guaranteed and may be subject to change."

## 2. N1: response time for H7 and the post-marker anchor check

**Recommendation: 24 hours** from an interruption, or from a step's readiness, to the anchor check and the operator's
`resume` / `recover` launch.

**Derivation.**
* The accepted deadline reserves "up to about 3 days for the operator to notice an interruption", across at most 3
  resumes (row 18). That is 72 h / 3 = **24 h per response**.
* With the accepted 4 × 8 h awake budget: 32 h + 3 × 24 h = 104 h, about 4.3 days. That is the accepted lower bound
  exactly, inside the 7-day deadline.
* **Constraint carried forward:** under MBS-8 (ii), the derived EVAL_CAP must satisfy 4 × EVAL_CAP + 72 h ≤ 168 h, i.e.
  EVAL_CAP ≤ 24 h. A derived value above that stops the route before the freeze, and the deadline is never extended.

**Consequence (procedure r3 §5).** A response later than 24 h that causes a lapse is an INCIDENT firing T4. It is not a
pre-declared outcome.

**Free-choice content:** none beyond reading "about 3 days" as 72 h.

## 3. N2: maximum interval from the L-DET interpreter build to the marker

**Recommendation: 21 days.** The whole no-update window, from the interpreter build to the deadline, is then at most
21 + 7 = **28 days**.

**Derivation.**
* The accepted principle is that the no-automatic-install window "should stay a bounded exposure, about one
  Rapid-Security-Response cadence".
* Amendment erratum E1.4 moved the window's start from the marker to the L-DET interpreter build. That was needed to
  keep the L-DET platform fixed. The window therefore now spans the pre-marker gates (L-DET, official decoys, caps,
  designation, freeze, qualification, S1, grant) as well.
* The Linux analogue of the cadence is the published Ubuntu kernel SRU cycle: 4 weeks regular, with a mid-cycle 2-week
  CVE update.
* Bounding the whole window by **one regular 4-week cycle** keeps the exposure to one regular cycle plus one CVE
  mid-cycle. A 14-day bound (one CVE cycle) would leave 7 days for every pre-marker gate. That is the ratified
  deadline's own length, with no stated basis for the gates fitting in it.
* The accepted text already says a platform change is terminal (DR2 b). So applying any update inside the window,
  including an urgent CVE fix the owner decides must be applied, **stops the route on that platform**. It is never
  applied and then continued.

**Free-choice content (stated for the provenance check):**
* choosing the 4-week regular cycle rather than the 2-week CVE cycle as "one cadence";
* subtracting the 7-day deadline.

The alternative, a 7-day bound (14 − 7), is stricter and much more likely to stop the route before the marker. A stop
before the marker consumes nothing of cell 308.

**Feasibility note (no target data).** The pre-marker compute is bounded by ratified caps. The pre-marker governance
steps (qualification review, S1 ruling, grant) depend on the owner's timing. If they cannot fit in 21 days, the route
stops on that platform. It is never extended.

## 4. What B3 must check

For each number, B3 checks that:
* only the sources quoted above were used;
* no target-run or runtime observation entered;
* the free-choice content is as stated.

B3 also checks each item of `CONSOLIDATED_DSTAR_PACKAGE_R2_ERRATUM_E1_20261016.md` §3.
