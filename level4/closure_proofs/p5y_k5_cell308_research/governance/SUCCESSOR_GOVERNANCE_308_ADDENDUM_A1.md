# Cell-308 successor governance: addendum A1 (coordinator; review GC-1 to GC-10)

**Why.** The independent review `reviews/REVIEW_SUCCESSOR_GOVERNANCE_308.md` (research `e3c60491`, sha256
`19c8e5c4…620f0d`) returned GOVERNANCE_REJECTED as submitted. It confirmed the classification, and conditions GC-1
to GC-10 apply.

**Status of the original.** The determination `governance/SUCCESSOR_GOVERNANCE_308.md` (`e5871aa6`) stays
byte-unchanged. A1 prevails where they differ.

**Classification (unchanged): SUCCESSOR_ALLOWED_WITH_CONDITIONS.**
* Target-free preparation is permitted **up to, but not including, the successor freeze**.
* A recorded user decision is required **before the freeze** (§14 / G2; GC-9) and **before any grant** (S1).
* New cell-308 target evaluations: 0.

**The decisive argument (review N2).** With byte-identical science (GC-4), the successor's certified value is, by
exact determinism, the value the lost MB r1 run would have produced. The cause of the interruption, including the
user's Force Quit, is therefore immaterial to Γ. No selection on an outcome is possible, because no outcome exists.

## 1. The omitted governing texts, quoted verbatim and reconciled (GC-1)

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

## 2. Corrections (GC-1)

* **Driver quote.** Determination §2 row 2 attributes "NEVER run execute again" to the driver docstring. It is the
  driver's printed message for exit 6 (`after_marker`); the docstring states "6 CONSUMED_UNRECORDED (never rerun)".
* **"Steps 6–8 are running separately".** When `e5871aa6` was committed, only step 6 was running. The state now:
  * step 6 is **EXECUTION_ACCEPTED** (formal `a40211cc`, adapted sense);
  * step 7 (the adjudication) is running;
  * step 8 follows.
* **"The user's Force Quit".** It stands. The recovery chain (A1 as corrected by E1, accepted at `98118e22`)
  attributes the Force Quit to the user's Force Quit dialog (`loginwindow` "Forcequit confirmed"). It carries no
  target information either way.
* **Cell-306 precedent.** The determination's paraphrase is replaced by floor r2's rule (`a15d083b`,
  `config/K5_TAIL_ADOPTION_FLOOR_R2.json`, `disagreement.never`):

  > no re-evaluation, parameter change or supply change after a disagreement in the same campaign

  306 was not re-run **within that campaign**. The rule is campaign-scoped, which is consistent with a separately
  governed successor.
* **K4 → K4R1: an existence precedent only.** K4R1 shows that separately governed successors exist in this
  project. It is not a template: K4R1 was designed from the observed K4 residual table (`81f5195a`), and no user
  ruling is on record. MB-S differs, since no MB r1 outcome exists.
* **The §10 asymmetry.** MB r1's §10 names "a successor campaign only" after QUALIFICATION_REJECTED (step 3). It says
  nothing about successors after a consumed execution (steps 5–8). The operative authority for recomputing lost
  result information is E7 / C6: "a new independent governance process and a new user decision".
* **The user-text rows (determination §2 rows 8–9).** They are replaced by the verbatim record
  `ledger/USER_TEXTS_SUCCESSOR_308.md` (GC-2).
  * The 2026-09-28 row was a coordinator paraphrase. The user's words are the brief's §26: "Any successor route must
    have an independently defensible scientific motivation not derived from chasing the observed target result …
    obtain independent governance review before considering it". Also the rule on rejection: "Return to research
    only through a new successor campaign if the defect can be prospectively repaired".
  * The 2026-09-30 overnight program (received 2026-09-29T17:41:26Z) authorises preparation and forbids any target
    authorization, grant, marker or Γ(5,308) evaluation without a later explicit user authorization.

## 3. The required content of the S1 ruling (GC-3)

The ruling put to the user must expressly:

1. authorise a **second consumed evaluation** of cell 308 (the count becomes 2), under the successor MB-S only;
2. **lift mitigation 5** for the successor;
3. state that the successor is **a new governance decision, not a rerun on host grounds** (E3); MB r1 stays
   INDETERMINATE;
4. decide the **§14 / G2 same-caps question**: keep MB r1's caps, or re-derive them from decoys under the new
   launcher;
5. **re-affirm U1–U8** of the C4 ruling;
6. say whether **a successor INDETERMINATE is final** for route MB, or whether a further successor may be governed.

The brief put to the user lists O1–O5 verbatim (§1). **Separately:** because MB-S keeps the caps, a recorded user
decision is needed **before the successor freeze** (GC-9).

## 4. Conditions added to S1–S10

* **S11 (GC-4). Unchanged science means byte identity.**
  * The following are sha256-identical to freeze r3 `c46434a3`:
    * the theory;
    * every pinned certifier byte;
    * `mb308_stage1`, `mb308_supply`, `mb308_consumer`, `mb308_a0core`, `mb308_pinned`;
    * the guard's admitted-pair derivation, the cover geometry, D1–D14 and the criterion.
  * Everything else lies outside the evaluation path.
  * The qualification includes an exact-equality comparison of certified non-target outputs (successor vs MB r1
    frozen code, at the decoy cells, timing stripped as in QC04). The route review's RC2 adds reproduction of MB
    r1's committed r3 records and platform pinning.
  * Otherwise S4's "changed" branch governs.
* **S12 (GC-5). Result-chasing risk: not lower than MEDIUM–HIGH.** A **fresh incident-independence reviewer**
  re-rates it for the successor before the successor freeze, because Q4's premises (one sealed evaluation; only
  R-MB on 308) are altered.
* **S13 (GC-6). Exposure.** A formal exposure addendum (E1″ in `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`) names,
  never values, the MB r1 target-run runtime and host observations, where they are recorded, and who holds them.
  * No successor brief contains them or points to REVIEW_EXECUTION_INTERRUPTION §4b.
  * The successor's route, implementation and caps agents have not seen them. The builder was instructed so on
    2026-09-29 ~20:40Z, and must disclose any prior reading.
  * The caps decision is justified from decoy and qualification evidence only.
* **S14 (GC-7). MB r1 closeout first.** There is no successor freeze or grant until MB r1's §10 steps 6–8 have
  returned EXECUTION_ACCEPTED, the adjudication (§8 verbatim) and ADJUDICATION_ACCEPTED. The successor cites them.
  If any is REJECTED, this determination is re-reviewed before anything else proceeds.
* **S15 (GC-8). The successor preflight asserts MB r1's recorded state.**
  * `refs/p5y-k5-cell308-mb-r1/target-consumed` → `afa93072` is the only ref under that prefix.
  * There is no pending ref, no emergency file and no MB r1 `evidence/`.
  * The successor refuses otherwise.
  * Later-found MB r1 evidence is a permanent STOP for the successor, pending its own governance.
  * That one marker is a **named** exception to "no prior evaluation", never a prefix wildcard.
* **S16 (GC-9). Freeze gating.** There is no successor freeze and no official qualification until all four hold:
  * (a) this addendum has been accepted by a delta review;
  * (b) the route selection, accepted with conditions RC1–RC6, has its conditions met;
  * (c) a recorded user decision covers the freeze under §14 / G2;
  * (d) S14 holds.

  The preparation done before this (`bddd85f8`, the Phase 4–8 architecture, the `-c308mbs` worktree and the build)
  is **at risk**, and is re-checked against the accepted texts.
* **S17 (GC-10). Reliability additions to S6** (target-free, sized from decoys only):
  * **Resource containment:** per-worker memory limits and a watchdog; host headroom at preflight. Exhaustion
    becomes a recorded INDETERMINATE, not a host hang.
  * **Host exclusivity:** no other heavy compute on the host during the run, including any other session's. It is
    arranged through the user, without inspecting that session.
  * **MB r1's E1 restated:** nothing else runs until the seal, and no in-run audit beyond the frozen host contract.

## 5. Unchanged

* S1–S10 as amended by S11–S17.
* No status change: cell 308 OPEN, r5 unchanged, no r6, K5 and P5Y unchanged.
* Cell 309 untouched.
* No target step authorised.
