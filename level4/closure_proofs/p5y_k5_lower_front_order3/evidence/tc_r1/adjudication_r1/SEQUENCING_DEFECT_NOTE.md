# Procedural defect in the adjudication handover (disclosed; adjudicator note N7)

**What happened.** The campaign operator polled the adjudicator's output file while the fresh-context adjudication was
still running, and at `f2ac1eb3` committed an **in-progress copy** of `ADJUDICATION_R1.md`/`.json` together with the
coverage map r4. The map was therefore generated *before* the adjudication had been handed over. The adjudicator
completed afterwards with `ADJUDICATION = ADOPTED`, 27 PASS · 7 INFO · 3 NOT_CHECKABLE_LOCALLY · **0 FAIL**, and this
commit replaces the stale files with the final ones.

**Why the published map is nevertheless the one the verdict permits.**
- The final adjudicator re-verified the already-published `K5_COVERAGE_MAP_R4.json` (sha256 `a3bddd83…`) directly and
  states it is exactly what the verdict permits: `K5_COVERAGE_COMPLETE = false`, union open `[[305, 309]]`, inputs bound
  to the adopted map r3 (`6d598dc5…`) and the sealed consumption (`1fa8d8de…`).
- The map is a deterministic function of those two inputs only. Regenerating it after the final adjudication gives a
  byte-identical file (verified in this commit), so nothing in the published artifact depends on the timing.
- The verdict never changed sign: the interim text already carried `ADOPTED`; the additions were INFO notes (N6, N7) and
  the completed reproduction of theorem TC and K5-B.

**Governance consequence.** The rule "only ADOPTED results may modify the authoritative coverage map" was satisfied in
substance but violated in sequence: the gate was consumed before handover. A late FAIL would have found the map already
published. The correct procedure — wait for the adjudicator's completion signal, then generate the map — is recorded
here and in the campaign status, and must be followed in Campaign B.

**Other load-bearing adjudicator notes (open obligations).**
- **N1 / C7.** The order-3 producer's frozen registry still reads that no real CUSUM cell may be evaluated by that
  producer, while its `Order3Certifier` was executed here on real cells 11–44 under this protocol's authorization. That
  namespace is adopted and must not be edited; the cross-reference therefore has to be made by a successor that owns it.
  Recorded as an open obligation, not silently repaired.
- **N3.** The manufactured suite's ground-truth oracle covers r = 0 and m = 1; the r ≥ 1 source tower and the W assembly
  are protected by the exact cross-check and, now, by the adjudicator's own independent implementation (136/136 exact).
- **N5.** The four new order-3 fields have no identity gate; they can only widen the enclosure (the centre remains the
  adopted order-2 candidate value), so a poor order-3 candidate cannot move the enclosure off the true value.
