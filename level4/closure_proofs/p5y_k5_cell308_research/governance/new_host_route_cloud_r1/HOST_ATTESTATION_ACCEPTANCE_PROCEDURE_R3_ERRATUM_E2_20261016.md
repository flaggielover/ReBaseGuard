# Erratum E2 to host-attestation acceptance procedure r3 (Cell-308 Cloud route r1): adverse outcomes, pending appointments and scheduled waiting (Z1)

**Status: AUTHOR-PROPOSED CORRECTION · NOT INDEPENDENTLY CONFIRMED · NOT ACCEPTED · NOT IN FORCE · NOT IMPLEMENTED.**

This erratum clarifies erratum E1 (`HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_R3_ERRATUM_E1_20261016.md`, `f6a7e3c5…0f9f`)
and procedure r3 (`e4376ee1…4637`). Both are preserved unchanged.

**Source.** Residual finding Z1 (MINOR) in the owner-supplied B1 confirmation excerpt
(`reviews/external/OWNER_SUPPLIED_B1_CONFIRMATION_EXCERPT_20261016.md`, sha256 `10af3d09847668c806ea15b77cca52f5461b8e24372f45ae667f4cf3dfb15011`). Z1 is at lines
73–94 of the excerpt, and its required correction is at lines 85–90. That excerpt is incomplete. Its receipt is
`OWNER_RECEIPT_B1_CONFIRMATION_EXCERPT_20261016.md`. The six rules below follow the owner's release instructions of
2026-10-16, which are quoted in that receipt.

B1's historical verdict on X4 stays **PARTLY**. This erratum is the coordinator side's own wording correction. No
reviewer has confirmed it, and none is asked to: the B1 appointment's single confirmation is finished.

**Precedence.** E2 governs over E1, and E1 governs over r3. E2 replaces **only** the wording named in E2.7. Every other
part of E1 and r3 stands, including the machine-wide veto and every acceptance requirement. Nothing here decides
D-HOST-LIFETIME. `DECIDED` stays empty. `new_target_evaluations = 0` · `cell309_activity = none`.

## E2.1 — Adverse outcomes refuse permanently

A `REJECTED` outcome or a `NOT_COMPLETED` outcome, of either part, for any attestation of a machine (same
`machine_identity`), **permanently refuses every official step on that machine**, across all parts and all
attestations. These are the eight steps of E1.3, and OD-3 is not put.

Nothing can erase either adverse outcome:
* re-attestation;
* withdrawal of an appointment entry;
* a superseding record;
* another review, of the same or a different attestation.

## E2.2 — A pending appointment refuses while it is unfinished

An appointment entry with no outcome refuses every official step on the machine **while it remains unfinished**.

## E2.3 — What a valid ACCEPTED outcome ends

When the same appointment's valid `ACCEPTED` outcome is recorded (E1.1 digest, order and identity rules all met), it
ends **only that appointment's pending-status block**.

It does not lift:
* any adverse outcome (E2.1);
* any other unfinished appointment (E2.2);
* any other failed gate or failed check;
* any route-stopping consequence already incurred (amendment erratum E2.7; r3 §5).

## E2.4 — Scheduled waiting is not a failed check

A planned review interval in which **no official step is scheduled** is waiting for a prerequisite. For example, the
interval between the P2 appointment entry and its outcome, after the L-DET interpreter build (matrix R4, rows B10–B11).
Such waiting is not, by itself, a failed official-step check, and it does not by itself stop the route.

## E2.5 — A check that refuses stays refused

If an official-step check actually occurs and refuses, during such an interval or at any other time:
* the refusal is recorded (`ANCHOR_CHECK … MISMATCH` or a refusal record, per r3 §5) and preserved;
* the governing stopping consequences apply. Before the marker, that is a gate failure on the named host: the route
  stops, and a restart needs a new owner ruling, a fresh S12 rating and a formal review (amendment erratum E2.7).
  After the marker, the step does not start, and r3 §5's after-marker rules apply.

A failed check is **never** relabelled afterwards as scheduled waiting.

## E2.6 — NOT_COMPLETED is adverse; no evasive withdrawal or reclassification

* A recorded `NOT_COMPLETED` outcome is **adverse, not pending**. E2.1 applies to it.
* An appointment entry must not be withdrawn, cancelled or reclassified to evade its deadline or its outcome rules.
* An entry that ends without a review file is recorded as `NOT_COMPLETED`. It never ends silently and never ends as
  "withdrawn".

## E2.7 — Wording replaced in erratum E1

| E1 location | E1 wording | replaced by |
|---|---|---|
| E1.2, last sentences | "An entry with no outcome yet also refuses (r3 §5). No outcome, and no withdrawal of an entry, ever lifts a refusal." | E2.2, E2.3 and E2.6. A pending entry refuses while unfinished. Its own valid ACCEPTED outcome ends only its pending block. No outcome, withdrawal or record lifts an adverse outcome |
| E1.3, "An open P2 appointment", last two sentences | "The order schedules no official step in that interval. This is intended and fail-closed." | E2.4 and E2.5. The interval is waiting for a prerequisite, not a failed check; a check that occurs and refuses stays refused, with its stopping consequences |
| E1.3, "Re-attestation" | "… can therefore **never** pass. … It lifts nothing." | E2.1. A new attestation of a machine whose record holds an adverse outcome is refused at every official step, permanently. A machine whose only refusing entry is pending is refused while that entry is unfinished (E2.2, E2.3). `prior_rejected_attestations` is disclosure only |

## E2.8 — Implementation state

The successor build must implement E2.1–E2.6 when it implements E1 (matrix R4 row B8; r3 §7 item 4 as amended by
E1.4). Additional items:
* adverse outcomes are terminal;
* a pending block ends only by that entry's own valid ACCEPTED;
* refusal records are preserved.

The development code (`9db01504`) implements none of this. **Operational implementation is not complete**, and is not
claimed.
