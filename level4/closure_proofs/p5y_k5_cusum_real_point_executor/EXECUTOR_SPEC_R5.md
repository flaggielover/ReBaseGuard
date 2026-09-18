# Real point executor r5: specification addendum (written before the repair code)

**Why an r5.**
- The independent review of the r4 freeze `77afd942` (qualification `d64bcd10`, 22/22 gates, publication `327cc35e`)
  ruled N1–N3 and D1–D4 CLOSED. It returned FAIL on one new load-bearing finding, **X1**: the launch slot is not bound to
  the slot the frozen verifier approved.
- r5 closes exactly X1. N1–N3, D1–D4, the mathematics, the science preregistration and the executor architecture are
  not reopened.
- REAL_INPUT_ARITHMETIC_GUARD stays DENY and EXECUTION_AUTHORIZED stays false.

## R5-1. One canonical launch slot, derived before verification

**Derivation.** In `supervisor.governed_prelaunch`, after the namespace and guard-policy checks and **before** the frozen
verifier, the supervisor derives

    canonical_slot = slot_dir(number of slot-N directories in the preregistered namespace + 1)

Namespace entries must be `slot-N` directories and contiguous from slot-1, as the frozen P11 requires. The committed
ledger is read through the frozen `prelaunch_verify.ledger_entries()`, which requires it to be committed, unmodified and
append-only.

**Checks.** A pure, accumulating check then requires all of the following, and reports every violated clause:
- the CLI-requested slot equals `canonical_slot`;
- the countersignature's `attempt_slot` equals `canonical_slot`;
- the ledger holds exactly one LAUNCH_NOTICE for `canonical_slot`, and nothing else for that slot;
- that notice is well formed (`{event, slot, authorization_sha256, utc}`), names the file-bytes sha256 of the protocol
  authorization, and is not older than that authorization's `AUTHORIZATION_UTC` (a stale notice is refused);
- the ledger names no slot that is absent from the namespace, other than `canonical_slot`.

Any violation gives **SLOT_BINDING_REFUSED**. It is a prelaunch refusal: no verifier call, no slot, no RUN_STATE, no
VOID, and no address consumed.

**No fallback.** The requested slot is never rewritten, auto-corrected or replaced by another free slot, and no slot is
chosen after verification.

**The authorization has no slot field** (the r4 template admits no extra keys). It is bound to the slot through the
LAUNCH_NOTICE, which names both the slot and the authorization's file-bytes sha256, and through the countersignature,
which names the authorization's sha256 and the slot.

## R5-2. The verifier's approval and a TOCTOU-bound launch state

**Launch state.** The supervisor snapshots the launch state before the verifier: the canonical slot, the namespace slot
list, the ledger sha256, the authorization sha256, the countersignature sha256 and the LAUNCH_NOTICE.

**After PASS, before the slot is created.** The supervisor re-derives the launch state and requires:
- it is identical to the pre-verification snapshot;
- the verifier's own P11 detail approves exactly that slot (`next slot <canonical_slot> …`).

Otherwise the result is SLOT_BINDING_REFUSED, before any slot exists. The snapshot is bound into the decision as
`launch_state`, so it is covered by `prelaunch_decision_sha256` in RUN_STATE. The full verifier is still never called
after the slot exists.

**Child re-check (pure, extends R4-2).** The decision's `launch_state.canonical_slot`, the decision's slot, RUN_STATE's
slot and the child's output slot must all be the same slot.

## Tests and gates

**Focused X1 matrix.**
- *Synthetic governed clone, integration:*
  - X1-01: every slot is 1 → PASS, end to end;
  - X1-03: CLI 2 → refuse;
  - X1-02: countersignature 2 with CLI 2 → refuse, and countersignature 2 with CLI 1 → refuse;
  - X1-06: no notice → refuse;
  - a genuine frozen-verifier REFUSED with the slot binding satisfied → no slot.
- *Pure, on synthetic ledgers and namespaces:*
  - X1-04: notice for slot 2 while the ledger's next slot is 1;
  - X1-05: duplicate notices;
  - X1-06: missing notice;
  - X1-07: notice for another authorization;
  - X1-08: stale notice;
  - malformed notice;
  - other events already recorded for the canonical slot;
  - a non-contiguous or foreign namespace.
- *X1-09 (TOCTOU):* a pure comparator on changed namespace, ledger, authorization or countersignature bytes, plus a
  static order fence: snapshot, then verify, then re-snapshot and compare, then mkdir.
- *X1-10:* a child whose RUN_STATE slot differs from the decision's canonical slot is refused by the guard.

**Each refusal must carry its own stated reason**, so a mutant that removes one check cannot hide behind another layer.

**Mutants.**
- X01: trust the CLI slot (the r4 defect restored);
- X02: ignore the countersignature slot;
- X03: ignore the notice's slot;
- X04: skip the post-verification launch-state re-check;
- X05: allow duplicate notices.

**Gates.** EG23 is the X1 suite. EG01–EG22 are regressions (N1–N3 and D1–D4 included). No existing mutation group is
reduced.
