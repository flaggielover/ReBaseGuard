# Route-selection rule for cell 309 (target-free; fixed before any cross-route comparison)

**Written:** 2026-09-29, after the route matrix, and before any decoy output was compared across routes. At the time
of writing, the only decoy outputs in existence were the SRK profiling runs and the exact FSM tests. No other route
has decoy output in this campaign.

## Rule S (maximal liability-free dominance composition)

The preferred 309 route is the composite built from **every** component that meets all of C1–C5:

| id | criterion |
|---|---|
| C1 | **Soundness.** The component has a written theorem with a proof. Either it has already passed an independent review, or it will be reviewed in the same freeze package |
| C2 | **Dominance by construction.** It enters the consumer only through a min (or intersection) with the term it replaces. So it can never raise Γ, for any input |
| C3 | **Data/host-free.** No candidate payloads, no new K1 or order-3 records, no replay host (U1), no new quantity derived from the P3 record (U2). Only operator-only certificates computed in exact stdlib arithmetic, inside the formal campaign's single Stage 1 |
| C4 | **Not liability-blocked.** No component whose 309 use is BLOCKED by a recorded incident (TPT: incidents 01 and 309R1-01) |
| C5 | **Ready.** The component's certifier is implemented, qualified on decoys, and cross-checked by an independent implementation, or it will be, in the same freeze package |

The rule makes **no reference to cell 309, to any committed 309 quantity, or to any decoy gain**. It does not ask
whether a component "is needed" at 309. Components are included or excluded only by C1–C5.

## Application (as of this writing)

| component | C1 | C2 | C3 | C4 | C5 | decision |
|---|---|---|---|---|---|---|
| SRK whole-kernel (R16) | theorem + FSM; review pending | min | yes | yes | in progress | **IN**, subject to C1/C5 completion |
| SRK-T taboo (R17) | theorem; review pending | min | yes, since D_lo is a pinned supply-registry constant, not a record-derived quantity | yes | certifier implemented; decoy qualification needs a certified D_lo at decoy blocks | **IN** only if C5 is met in the same package; otherwise OUT (safe: omitting a min component never invalidates) |
| RLR A1/A2 (R4) | reviewed (R2, R3, 307 qualification) | min with Dv′ and Lemma G (D14) | yes | yes (disclosures carried) | qualified for 307; needs its own 309 Stage-1 blocks | **IN** |
| Corollary T g_hi (R10) | adopted theorem | yes | **no** (U2) | yes | — | OUT |
| TPT / TPT∘SRK (R7, R18) | sound | yes | yes | **no** | — | OUT |
| SC, RSO-P, real Ĝ, refinement (R5, R6, R8, R11) | sound | yes | **no** | — | — | OUT |

The resulting preferred composite is **P309 = frozen direct clause** with:
* TC-T enclosure, and rad_r's order-0 term replaced by the SRK B3/B4 min construction (whole-kernel, and taboo if IN);
* supply S = (A0 from S_I1, A1 = min(A1_I1, A1_RLR), A2 = min(A2_I1, A2_RLR)), the 307 S_RLR construction;
* every other input unchanged.

**Closure-only** under floor r2. **Exactly one** sealed evaluation, in a separately authorized formal campaign.

## What this rule forbids

* Adding or removing a component after any 309-related number is known, including the formal campaign's Stage-1
  outputs.
* Choosing between SRK variants by decoy gain. Both are min-composed, so both stay in if ready.
* Choosing degree, ladder, cover, sub-block count or tolerance by anything other than THEOREM_SRK §7 / amendment A1
  (fixed) and the 307 RLR Stage-1 rules (frozen).
