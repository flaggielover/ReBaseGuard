# Incident audit for the RLR / cell-307 route (campaign brief §4)

**Author:** the campaign coordinator. It is the same agent that coordinated the overnight campaign and introduced
incidents 01 and 03. This audit is therefore **not** independent. The brief (§4) lets the campaign proceed only if
an **independent** review accepts the five conclusions in §4 below. That review is
`review/INCIDENT_INDEPENDENCE_REVIEW.md`.

**Rule for this document.**
* It quotes no validation-drift value of the RLR route.
* Committed tail-cell numbers appear only as literal grep patterns in §5, with nothing placed beside them.
* Incidents are described by class. Committed facts are pointed to by path.

## 1. The incident record (overnight, preserved unchanged)

The overnight ledger `p5y_k5_tail_overnight_research/ledger/ZERO_TARGET_LEDGER.jsonl` (242 lines, blob `409952c415de`)
has six LEAK_FLAG lines. All carry `new_target_evaluations = 0`.

| # | ledger class | incident file | cells named | what | computed? |
|---|---|---|---|---|---|
| L1 | PROXY_EXPOSURE | INCIDENT_01 (`25874c71a53a`) | 306–309 | Dependency graph r0 §3: committed tail radius shares written beside theorem TPT's generic charge factors | no number computed |
| L2 | PROXY_EXPOSURE | INCIDENT_02 (`e6c108871765`) | 308 | C2a re-read a committed cell-309 certificate as a floor for a cell-308 quantity (A0 channel) | reasoning over committed values; no computation |
| L3 | PROXY_EXPOSURE | INCIDENT_03 (`bcdfb7d431b6`) | 308 | Coordinator's C2b brief defined a comparison scale derived from committed cell-308 figures (A0 channel) | no |
| L4 | PROXY_EXPOSURE | INCIDENT_01 residue (global review F13) | 306–309 | Further co-locations in the same graph: committed tail shares in the node table, TPT-G's over-charge formula, and **the synthetic LR slack ratio** of the idea probe; plus a C5-T gain share beside "superseded by TPT" | no |
| L5 | QUARANTINE_RULE_BREACH | INCIDENT_02 residue (global review F12) | 308 | The cross-cell re-labelling in L2 survived in three places; re-worded | no |
| L6 | QUARANTINE_RULE_BREACH | disclosed by stream A (global-review repair) | 306 | An R2.1 breach in stream A's files, found and fixed by the author | no |

## 2. Relevance of each to the RLR route and to cell 307

RLR changes only the atom constants **A1 and A2**. A0 is C2's committed value, unchanged (protocol draft §2–§3).
The route is evaluated on cell 307 only.

### 2.1 L1 and L4 (incident 01 and its residue): relevant, qualitatively

* **L1** pairs committed tail shares with **TPT** factors. TPT is a transport theorem, and its tail use is BLOCKED.
  RLR shares no factor, code or parameter with TPT. L1 itself does not bear on RLR.
* **L4 does bear on RLR.**
  * The residue shows that graph r0/r1 contained, in one document:
    * the committed tail share of the A0 radius term (node N17's "Dom" column);
    * in §3's looseness ranking, the synthetic probe's "true functional norm ≪ positive majorant" factors for A1
      and A2. The idea note `IDEA_LR_SCORE_CONSTANTS.md` (`cbff958a`, 02:49) introduced those factors as the
      motivation of the LR route.
  * Together these say, qualitatively, how much of the tail radius the A1/A2 channel carries and how much slack a
    score-level bound might remove there. That is a latent proxy for the LR route's effect at the tail.
  * The ledger counts it as one qualitative proxy exposure (L4).
  * The residue note records that "no one combined" it. I re-checked this:
    * no artifact of the LR stream contains a committed tail-cell number, a C8/C9 factor or cell 307's drift
      interval;
    * the searched artifacts are `streams/C_308/LR/**`, the idea note, `pm_probe_synthetic.py` and the three RLR
      reviews;
    * the search was a grep for the committed C8/C9 factors, the C5 shares and cell 307's endpoints; the command is
      reproduced in §5;
    * the only "307" strings in the LR stream are the cell-set lines of the protocol draft.
* **Parameters.** No RLR parameter depends on L1/L4.
  * They are the families (P_d, PW_d, e-free block PW_d), degree ladders, scaling rules (D3, D6, D7), enclosure
    settings (D9, D11), coverage rule (D13), combined supply (D14) and the controls.
  * All are declared in `cusum/PROGRESS.md` (D0–D18, blob `159badb5759c`) before their runs, at declared drifts
    {0, 1/4, 1/2, 1, 3} and the block [1/2, 17/32].
  * The overnight guard refused every drift in [6/5, 13/5] and its mirror.
  * The declarations name no cell and no tail number (§5).

### 2.2 L2, L3 and L5 (incidents 02 and 03, and the 02 residue): not relevant

* All three concern cell 308, the A0 channel and the 308 exclusion question (X308).
* RLR does not touch A0, and it is not evaluated on 308.
* None of them names cell 307 or an A1/A2 quantity.

### 2.3 L6: not relevant

It concerns stream A (cell 306, I1/I2 disagreement). It names no LR quantity and no cell-307 quantity.

## 3. Exposures that are not ledger incidents but bear on RLR / 307

These are listed because the brief asks whether incidents *exposed information relevant to the route*.

1. **Motivation provenance (disclosed overnight, protocol draft §1.2).**
   * The LR route, and its cell, were chosen knowing the committed C3 knockout:
     * with A1 = A2 = 0 and the certified A0, the frozen consumer closes cell 307 but not 308 or 309;
     * sources: C3-N4, C4 §8, ROUTE_AUDIT_R1 §4.
   * The idea note states this in its table ("cells potentially relevant: 307 …").
   * This is **committed historical information**, readable under every quarantine, not new target information.
   * It fixed the route's *channel* (A1/A2) and its *cell set* ({307}). It fixed no parameter of the certifier.
2. **Committed per-cell factors known to the coordinator.** C8/C9 recorded, for cell 307, the factor by which
   an operator-constant lever would have to improve.
   * The coordinator knew them overnight and knows them now.
   * They appear in no RLR artifact and in no document of this campaign.
3. **RLR validation-drift values known to the coordinator.**
   * Location: C1B Appendix V; a latent-proxy class under QUARANTINE_AMENDMENT_2 R2.3.
   * The same agent knows items 2 and 3, so combining them in reasoning is the realistic proxy risk. No such
     combination is written anywhere, and none enters any decision of this campaign.
   * The decisions this campaign adds (outward 2^-20 hull, D8 ladder for blocks, exception classification, caps)
     are fixed by neutral written rules with a stated reason (protocol §3). The independent qualification review is
     asked to check each for target dependence.
4. **Scope narrowing r0 → r1 (`9e8ae240` → `d3b60795`).**
   * The draft's cell set went from {307, 308, 309} to {307}, using the committed knockout scope fact before any
     result existed.
   * This removes two evaluations that could not close under an A1/A2-only supply. It does not tune the route.
   * The brief (§1) itself fixes the campaign to 307 for the same reason.

## 4. The five conclusions the brief requires (for the independent reviewer to accept or reject)

| # | brief §4 conclusion | coordinator's finding | evidence |
|---|---|---|---|
| 1 | The RLR theorem and design existed independently of target outcome | **Yes.** No target outcome for RLR on 307 exists: it has never been computed. The design was fixed between 02:49 and 10:51 on 2026-09-28, on synthetic fixtures and declared non-target drifts only | timeline §1 rows 1, 3, 7, 12, 15, 16; `START_STATE.json` |
| 2 | No new numeric Γ307 value was generated | **Yes.** No Γ(5, 307) under any supply since C2's committed record; no marker, result ref or result artifact on any ref | `START_STATE.json` items `no_cell307_*`; overnight ledger `new_target_evaluations` = 0 on every line |
| 3 | No target-equivalent numeric proxy for 307 was generated | **Yes, numerically.** L4 is a *qualitative* co-location covering the tail generally (306–309): it was ledgered, nobody combined it, and no number derived from it exists. No RLR quantity was ever computed on a drift in the band | §2.1; overnight ledger; the guard |
| 4 | No RLR parameter was selected using target outcome | **Yes.** Every certifier parameter was declared at non-target drifts before its run (D0–D18). The cell set {307} is a scope decision from a committed fact, and names no parameter | §2.1, §3.4 |
| 5 | The final RLR design is prospectively defensible despite the broader incidents | **Yes, with disclosure.** The result-chasing risk is MEDIUM (motivation provenance, §3.1–3.3), as the draft recorded. It is mitigated by: one sealed evaluation; the closure criterion frozen before the grant; independent qualification, execution and adjudication reviews; no post-result tuning | protocol §3, §7 |

**Coordinator's recommendation:** PROCEED to the formal freeze. Carry L1/L4 and §3 as disclosed liabilities in the
protocol, the grant and the adjudication.

## 5. Reproducible checks behind §2.1

Run from the repository root at the handover:

```bash
NS=level4/closure_proofs/p5y_k5_tail_overnight_research
grep -rn -E "1\.0988|1\.1374|1\.3700|1\.096007|1\.067071|81\.[59]|17885921|1882413|1\.788|1\.882" \
  $NS/streams/C_308/LR $NS/streams/C_308/IDEA_LR_SCORE_CONSTANTS.md $NS/streams/C_308/pm_probe_synthetic.py \
  $NS/reviews/REVIEW_RLR_*.md $NS/registry $NS/OVERNIGHT_FINAL_REPORT.md        # -> no output
grep -rn "307" $NS/streams/C_308/LR $NS/reviews/REVIEW_RLR_*.md | grep -v "/logs/"  # -> protocol draft lines only
```

The patterns are:
* the committed C8/C9 cell-307 factors;
* the committed A0 radius share (N17);
* cell 307's cover endpoints.

They appear here only as search patterns, and nothing is placed beside them.
