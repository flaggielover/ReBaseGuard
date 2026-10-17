# READING_EXTERNAL_B2_T6_MITIGATIONS_SUPPLEMENT

## Identity, authorization and exposure update

- Reader: **B2-External**, the same Codex reader and conversation that produced `READING_EXTERNAL_B2_INCIDENT_REVIEW.md`.
- Date: 2026-10-16 (Asia/Tokyo).
- Original report SHA256, recomputed before this supplemental reading and confirmed unchanged: `201aa5af49da3c0d3a9b4a13bc4b356fb4f42c59fde86c780d123b0d3930f9b2`.
- Authority: the owner's explicit supplemental permission in this conversation to locate and quote M1–M6 from exactly one additional source, including its applicable qualifications. This continues the original extraction task only.

No intervening role or exposure change occurred in the conversation available to me between the original report and this authorization. I have taken no later route, implementation, provenance, caps, qualification, acceptance or risk-rating role, and have not become B3 or S12X. My original limitations remain: I cannot independently certify account ownership, platform-level access isolation, or involvement outside my available context. The owner's acknowledgement does not certify platform-level isolation.

The only new project-source exposure for this supplement was the added, verified T6 source, read in this B2 context. It contains descriptions of E1″ material; I continue to treat myself as an E1″ holder. I encountered references in that source but followed none. I accessed no local checkout, clone, repository directory listing, other source, other chat or Cell-309 material; ran no repository code; used no other reviewer; and published, pushed and communicated nothing to the coordinator. I observed no disqualifying change or exposure outside the supplemental permission.

The original report remains immutable. Its missing-source finding was correct within its original four-file boundary.

## Added source and pre-read verification

- Source URL: https://raw.githubusercontent.com/flaggielover/ReBaseGuard/f814fe84053bf8df61149e3d07bbc00aea50846c/level4/closure_proofs/p5y_k5_cell308_research/reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308_T6.md
- Pinned commit: `f814fe84053bf8df61149e3d07bbc00aea50846c`.
- Expected and computed Git blob OID: `d3d1ef537df47cc08dcfd981b6b9635319b9438a` — **MATCH**.
- Expected and actual raw byte length: **8745 bytes** — **MATCH**.
- Computed raw-byte SHA256: `d091e4ba4a31f0aa5723435add320ddbe43ee1f1d9b726d00facd861414e77e4`.

The Git blob OID was computed as SHA1 of `b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw`. Identity and length were checked before decoding or displaying the text. The raw-byte SHA256 was also computed and reported directly to the owner before reading the text. No expected SHA256 was supplied or claimed previously verified. No redirect was followed.

## Sanitized quotations

All source line references below are one-based lines of the added T6 source. Blockquote markers are report formatting. Source wording and internal line breaks are preserved except for the single [WITHHELD] substitution in M2. The qualifications and rating consequences below are statements by the source author, reproduced as evidence; they are not a new ruling or risk rating by B2-External.

### Applicable scope and timing qualifications

**Source lines 4–9 — conditionality and limitation to the original case.**

> **Ruling.** T6 fired. The rating stays **MEDIUM–HIGH (upper end), not lowered**, conditional on M1–M8 below. If any
> of M1–M6 fails, the rating is **HIGH**.
>
> **This is an explicit amendment of T6's consequence for this one instance.** The review said any trigger makes the
> rating HIGH. The text of T6 is unchanged, and it is not reinterpreted. This is not the silent narrowing of a gate: the
> consequence is replaced here, on the record, for this case only. The reasons are in section 3.

**Source line 68 — timing qualification for the conditions.**

> ## 4. Conditions (before the MB-S freeze unless stated)

The source expressly makes its ruling conditional on M1–M8. The extraction below supplies M1–M6 as requested; it does not assess satisfaction of any condition or decide transfer to another case.

### M1

**Source lines 70–76.**

> * **M1. Non-dependence, itemised.** Brief 37's item 10 must return a trace for every constant, cap, limit, timeout,
>   threshold, interval, budget and allow-list in the successor code and protocol draft. Each is traced to one of:
>   * an MB r1 frozen value, byte-equal;
>   * the architecture or review text, cited;
>   * recorded decoy, synthetic or host evidence, with a stated rule and a ledger line.
>
>   A non-holder re-derives any item it cannot trace. If that is impossible, the rating is HIGH.

### M2

**Source lines 77–81.**

> * **M2. The content, confirmed.** An agent that already holds `postexec` confirms in one REVIEW ledger line that
>   `MB308_RECOVERY_RECORD.md` holds only the kinds of item BUILD_REPORT §9 lists. The agent is neither the coordinator
>   nor builder2; reviewADJ or reviewEXEC would do, and neither becomes a new holder. The record must hold no per-job
>   runtime, [WITHHELD] per-worker observation, per-coalition CPU value, in-run thermal reading or memory event. If it holds
>   any of these, this ruling is re-opened.

### M3

**Source lines 82–85.**

> * **M3. Builder-set values replaced or confirmed.** Before the freeze a non-holder confirms or replaces the memory-cap
>   rule (multiplier and floor), the free-memory headroom, the exclusivity threshold and the allow-list, with a written
>   rationale from decoy or host evidence only. Their frozen values come from official decoy runs that a non-holder
>   executes.

### M4

**Source lines 86–91.**

> * **M4. builder2's roles from now on.**
>   * The exposure record names builder2 as an E1″ holder, with what it read (named, never valued).
>   * builder2 takes no caps, qualification (official runs, verifier, manifest, scanner), qualification-review or
>     S1-brief role.
>   * Bounded code repairs are allowed only on a non-holder reviewer's request. They never set or change an operational
>     number, and a non-holder reviews each repair diff.

### M5

**Source lines 92–93.**

> * **M5. Non-holders verified.** Every later implementation, caps and qualification agent is checked against the full
>   MBS-1 location list. Brief 37's forbidden list covers it; I checked this.

### M6

**Source lines 94–97.**

> * **M6. No precedent beyond this case.** This mitigation covers builder2's pre-instruction reading only. The following
>   fires T6 at HIGH, unmitigated: any agent that reads an MBS-1 location after the rule reached it, and holds or takes a
>   route, implementation, caps or qualification role. For builder2 the rule arrived at 2026-09-29T18:39:04Z; for every
>   other agent, with governance A1 (`ce145e51`).

## Extraction status and remaining evidence gap

M1_M6_EXTRACTION: COMPLETE

The added source supplies all six actual definitions at lines 70–97, with the applicable scope and timing qualifications quoted above. No evidence gap remains for locating and quoting M1–M6. This supplement does not determine whether any condition has been met, whether the original mitigation transfers, or what rating applies to any route.

## Sanitization verification

I checked all eight quotation blocks against the verified source lines. The only textual substitution is [WITHHELD] for a target-run event-time label in M2 at source line 80. M2's remaining terms identify categories that its confirmation rule forbids, rather than reporting actual target-run observations. M6's timestamp is the exposure-instruction time, not a target-run observation.

I reviewed the complete supplement for target-run observations, figures, runtimes and rates; none is released. No raw source or raw notes are attached or reproduced beyond the requested sanitized quotations and their applicable qualifications. No excluded pattern file or repository scanner was accessed or executed. This is the B2 sanitization check, not certification of platform-level isolation or of any other party's checks.

## No later role and standing

After this supplemental extraction I take no later route, implementation, provenance, caps, qualification, acceptance or risk-rating role on this route. I will not become B3 or S12X. All remaining retirement and isolation restrictions continue in force. I report directly to the owner only and will not publish, push or contact the coordinator.

This supplement is evidence for the owner's later decisions. It decides no T6 transfer, issues no risk rating, adopts nothing and authorizes no execution.
