# Coordinator incident audit for P309 package 1 (NOT independent; input to the independent incident-independence review)

**Scope.** This audit covers every disclosed incident, erratum and exposure as it bears on P309. For each, it records
what the coordinator (the author of P309) knew, and when, relative to every P309 design decision. It is an input to
the independent review (`P309_REVIEW_BRIEFS.md` §1). It is **not** a verdict. The owner has accepted the existing
classifications to allow proceeding, and this audit changes none of them.

## Timeline of P309 design decisions (commit times, 2026-09-29/30 UTC; research branch)

| time | commit | decision |
|---|---|---|
| 09-29 12:58:44 | 52e00290 | charter; target quarantine (305–309 and the band); guard with planted control |
| 13:02 | 1f6b724a | **309R1-01 recorded** (the coordinator saw incident-01 tail shares through an over-broad grep) |
| 13:06 | daa1bd64 | **309R1-02 recorded** (the coordinator made an in-band mental estimate while conceiving SRK) |
| 13:15:54 | 3df7a1a5 | THEOREM_SRK (the route's mathematics) |
| 13:44:15 | f0dbaa79 | SRK implementation; decoy declaration (e ≤ 33/32; synthetic h ∈ {3, 4}) |
| 13:52:08 | 7f1eb363 | dossier, route matrix, **rule S** (component selection C1–C5) |
| 14:11:58 | (scratchpad) | **309R1-04**: Phase-4 drafting begins, uncommitted |
| 15:55:20 | 5f41d8a9 | review-R1 repairs: A3 drift-block rule (2⁻¹⁰ hull, N_E = 4), gate |
| 16:07:36 | 2a03e838 | producer lock for the qualification rerun |
| 16:11:12 | 61a65003 | A4: pinned implementation constants |
| 16:12:58 | a748ac49 | SRK-T OUT of package 1 (rule S C5), before any taboo rerun output |
| 09-30 00:06:01 | f026c80b | R2: FREEZE_READY |
| 00:08:58 | ce829bb4 | Phase-4 package committed |
| 00:33:57 | 814ff984 | **rev. 2 rule choices**: the Stage-1a failure mapping (exception → INDETERMINATE; non-success → fallback); the 48 CPU-h budget; **Stage-1b fallback to S_I1** |
| 00:41:11 | 36e672be | rev. 2b budget mechanics (per-job limit, rung-major order) |
| 01:38 | owner | owner decisions: G1, G3 (Stage-1b fallback adopted), §2.5 accepted |

## Incidents and their bearing

| item | information exposed | exposed before which P309 decisions | could it have informed a P309 choice? | coordinator assessment |
|---|---|---|---|---|
| inherited: C4/C5/C7 retrospective-gate issues (09-22) | provenance of the Λ_309 floor and of the exclusion | all | They define the negative results that SRK is designed to escape. Programme-wide knowledge that norm-only order-0 bounds fail at 309 | disclosed. It is the root of the MEDIUM-HIGH motivation rating (G1, accepted) |
| overnight 01 (09-28) | tail radius shares beside TPT factors | all | TPT is excluded (BLOCKED), so it bears on SRK only through 309R1-01 | TPT stays OUT |
| overnight 02 (09-28) | re-attribution of C7's 309 floor to 308 | all | It motivates the non-re-attribution rule, which P309 now states and enforces | no P309 parameter depends on it |
| overnight 03 (09-28) | C2b brief scale from 308 figures | all | only if the C2b certifier were used. P309 does not use C2b | not applicable |
| **309R1-01** (13:02) | incident-01 tail shares (radius composition at 309) | THEOREM_SRK, the decoys, rule S and every later choice | It could suggest which radius term dominates at 309, hence which channel to attack. SRK attacks the order-0 channel | disclosed in THEOREM_SRK, the dossier, the route matrix and Phase 3. It is part of G1 (accepted) |
| **309R1-02** (13:06) | the coordinator's own in-band mental estimate while conceiving SRK | THEOREM_SRK and every later choice | It could bias the belief that SRK "might close". It did not set any parameter: the degree ladder, cover, μ, N_E, hull grid and budget are all fixed on target-free grounds (C1b inheritance, decoy timing) | disclosed; part of G1 |
| ledgered necessary reads (09-29) | graph A §0–3 (309 critical-A0 versus floor), THEOREM_TCT tail lines (filtered) | most | the same class as 309R1-01/02 | disclosed in the exposure ledger |
| **309R1-03** (00:1x on 09-30) | none (a parse-time refused probe, nothing evaluated) | — | no | liability NONE (concurred by R2) |
| **309R1-04** (drafts from 14:11) | none new: the drafts contain no target information (quarantine-checked; preserved verbatim with sha256 in `research/ledger/incident_309R1_04_drafts/`) | THEOREM_SRK, the decoys and rule S **predate** the drafts. A3, A4, the SRK-T exclusion and all evidence **postdate** them | The drafts show an early intent to reach a formal campaign (a motivational risk). They could not inform any parameter with target information, because they contain none | LOW; the drafts are to be compared directly with the committed package by the independent reviewer |
| E-3 | the ordering of an early real-kernel decoy probe (out of band) relative to the declaration commit cannot be verified | — | no. The drift was out of band and declared | disclosed |
| E-17(a) | the verifier's pre-commit self-test development runs are unrecorded | — | The committed test samples real-kernel drifts \|e\| ≤ 1.05 (seeded replay). The pre-commit runs are unverifiable | disclosed |
| E-18 / generator runs (23:11, 23:47 on 09-29) | git metadata; hashes of two other campaigns' governance files | — | no | disclosed |

## The three rev. 2 rule choices (explicitly for the reviewer, per R3 F2.8)

All three were made at 00:3x–00:4x on 09-30, **after** every incident above and with programme-wide dominance knowledge.
That knowledge includes the committed C3 knockout: A1 = A2 = 0 still leaves Γ > 0 at 309, so RLR alone cannot close
309.

1. **Stage-1a failure mapping.** Exception → EXECUTION_INDETERMINATE; non-CERTIFIED, non-ACCEPT or budget → fallback.
   This was proposed by R3 as the minimal fix consistent with the outcome table. It **reduces** the chance of a
   closure (it does not turn a malfunction into a fallback). There is no target dependence.
2. **The 48 CPU-h budget** (a start threshold; per-job limit 12 CPU-h; rung-major order). The basis is about 10× the
   qualified real-kernel decoy cell (about 4.5 CPU-h, decoy only). There is no reference to 309 cost, and 309 cost is
   unknown.
3. **Stage-1b fallback to S_I1** (instead of RLR307's NOT_CLOSED). The basis is min-composition validity: S_I1 is a
   valid supply, and RLR is optional. **Adversarial reading:** compared with NOT_CLOSED, it raises the chance of a
   closure whenever Stage 1b fails, because SRK with S_I1 can still close. The C3 knockout means the coordinator knew
   RLR alone cannot close 309. It did not know whether SRK with or without RLR closes 309: efficacy is unknown by
   design, and no 309 Stage-1 number exists. The owner adopted this choice explicitly (G3). The reviewer should assess
   whether it is target-independent in the required sense.

## Coordinator's request to the independent reviewer

Decide on temporal and parametric independence of P309 from the exposed information. That includes:
* a direct comparison of the preserved pre-FREEZE_READY drafts with the committed package rev. 2b;
* the U2 reconstruction (`governance/U2_FACTUAL_RECONSTRUCTION.md`).

Rate result-chasing independently. The coordinator's MEDIUM-HIGH rating is an input, not a bound.
