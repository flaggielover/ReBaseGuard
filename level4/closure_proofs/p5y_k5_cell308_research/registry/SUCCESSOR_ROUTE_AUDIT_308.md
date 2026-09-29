# Cell 308: target-free successor route audit (Phase 3; coordinator; for independent review)

**Basis.** Only committed, target-free evidence:

* the route registry r2 (`registry/ROUTE_REGISTRY.md`, written before the MB308 r1 freeze);
* the reviewed theory (`theory/THEOREM_MB.md` r1; REVIEW_THEOREM_MB_R1);
* the certifier review (REVIEW_A0_CERTIFIER_R1);
* the incident review;
* the MB r1 qualification r3 (PASS, QUALIFICATION_ACCEPTED);
* the committed prunings (C3 knockout, history H1.3; C4/C8 inversion, H1.5–H1.7).

No information from the MB308 r1 target run exists as a value, and none is used (governance S3). New cell-308 target
evaluations: 0.

## 1. Route matrix

| id | route | classification | reason (target-free) |
|---|---|---|---|
| P0 | existing consumer, A1/A2 only (RLR, Dv′, Lemma G alone) | **REFUTED** | the committed C3 knockout (H1.3) certifies that A1/A2 alone cannot close under the frozen consumer. Not resurrected |
| P1 | existing consumer, atom constants only (uniform triple, frozen clause or C5-T) | **REFUTED as a stand-alone route** | the committed C4 §4 / C8 inversion plus the SM(d) floor (the A0 part rests on an uncertified MC; the certified part is in PRUNING_308). Survives only as a component of R-MB |
| R1 | Theorem-M extremal A0 (Lemma M-U, A0-M) | component of R-MB | REVIEW_ACCEPTED |
| R2 | atom-level exact pointwise certificate (C1b, THEOREM_AD) | component of R-MB | certifier review accepted with conditions; qualified in MB r1 (QC06) |
| R3 | resolvent / supersolution certificate (C2b exact-scale) | component of R-MB | as R2; admitted only with independent verification (D5) |
| R5 | piecewise / profile A0 inside TC-P + TPT-B | component of R-MB | REVIEW_ACCEPTED; incident-01 liability disclosed |
| R6 | Dv′-M, D14-M, DM (one Ā′ tightens A0, A1, A2, D_lo) | component of R-MB | REVIEW_ACCEPTED |
| R7 | independent second implementation (VERIFY, F2, F3) | required element of R-MB | implemented; qualified (QC05–QC07) |
| R8 | TPT / TPT-B assembly | component of R-MB | validated synthetic and decoys; incident-01 liability |
| R10a | monotone envelope | component of R-MB | REVIEW_ACCEPTED |
| C-RLR | RLR A1/A2 block supply | component of R-MB | cell-307 campaign; single certifier implementation disclosed |
| TPT, C5-T | single-profile transports | included as special cases of TPT-B | dominance chain, THEOREM_MB r1 §7 |
| LR, B2c | plain score-level atom constants; sub-segment re-certification | included in R-MB (D14 min; block resolution) | registry r2 |
| **R-MB** | composite (R1+R2/R3+R5+R6+R8+R10a+C-RLR, with R7) | **SUCCESSOR_CANDIDATE** | see §2 |
| C11R-I2 | the I2 certifier family as an additional member at 308's blocks | **DEFERRED** | registry r2 marked it "a successor-campaign item" before the MB r1 freeze. It has never run at any block of this cell and is not wired or reviewed at this cell. Adding it means new code, a new trust surface and new reviews, and it breaks the determinism argument (S4). A candidate for a later increment, not tonight |
| COR-T | AD Corollary T for g_hi | **DEFERRED** | not implemented on the TC-T path; a new trust surface in g_hi. Same position as C11R-I2 |
| R4 | adaptive certified cover | **BLOCKED** | needs new real K1 records (governance + host) |
| R9 | residual-specific RSO / SC | **BLOCKED** | K1 candidate payloads never serialized; certifying host + P3 admissibility ruling |
| C9-E1 | α-ladder lever | **BLOCKED** | toolchain/host (numpy, python-flint; U1) |
| RO3 | genuine order-3 Ĝ (R-stage) | **BLOCKED** | governance: new real K1 addresses; guard DENY |
| CHAIN | K5-B chain clause | **EXCLUDED** | not a per-cell quantity; needs the quarantined adjacent tail cells |
| X308 | exclusion (lower bound on Λ₃₀₈) | **DEFERRED** | zero closure leverage |
| sharper sup / operator norms, other A1/A2 improvements | — | no committed, reviewed instrument beyond R6/C-RLR | nothing to select without new theory; not pursued tonight |

No route above is resurrected merely because the MB execution was lost, and no refutation is revisited.

## 2. Selected successor route: **MB-S (R-MB with the science of MB308 r1 unchanged)**

**Definition.** The successor evaluates cell 308 under exactly Theorem MB r1, with MB r1's:

* members, ladder (RLR d 4/6/8; C2b N 20/40/80; C1b d 8/10/12) and admission rule D5;
* envelope and composition;
* TPT-B consumer on the committed TC-T inputs;
* independent layers F2 and F3 and the verifiers;
* frozen criterion Γ_dec = g_hi + max(P*_B, P_hi) < 0 (strict, exact).

The science modules are **byte-identical** to the MB r1 freeze r3 bytes, bound by sha256 and git blob. Only the
execution infrastructure changes (Phases 5–8).

**Why this route, and not a changed one:**

1. **Dominance is preserved.** R-MB is already the strongest host-free, data-free combination (registry r2). Every
   route outside it is refuted, blocked (data, host, governance) or deferred (unimplemented or unreviewed at this
   cell).
2. **Integrity (governance S4).** With the science unchanged, the successor's value is, by exact determinism (MB r1
   QC04), the value the lost run would have produced. No selection effect is possible, and no scientific choice is
   made after the loss.
3. **Everything is already reviewed.** The theory review, the certifier review, the incident review and the r3
   qualification cover every scientific element. A changed science would need new reviews and would reopen the
   motivation question (incident-01 class).
4. **Deferred members are recorded.** C11R-I2 and COR-T stay available for a *later* increment, with their own
   prospective motivation and reviews. Excluding them now is not a judgement of their effect on 308. They are simply
   not implemented, reviewed or qualified at this cell.

**Required elements** (the user's list):

| element | status |
|---|---|
| explicit closure mechanism | Γ_dec < 0 (exact) via TPT-B with block-resolved S_i = min of {S_I1, Dv′-M(C1), Dv′-M(C2), D14-M, G} (Theorem MB r1 §6–7) |
| theorem / derivation | `theory/THEOREM_MB.md` r1 (REVIEW_THEOREM_MB_R1 accepted with corrections applied) |
| implementation plan | reuse MB r1's pinned science bytes; the new campaign adds the launcher, persistence, state machine and host contract (Phases 5–8) |
| independent verification path | F2 (`mb_independent.py`), F3 (`tuple_independent.py`), VERIFY (`vd_pl`, `vd_verify`), `rlr307_independent`, all as in MB r1 |
| prospective non-target qualification | the MB r1 case set (QC01–QC13, Q8, Q12 with host provenance), plus successor cases for detachment, persistence, crash recovery and the state machine |
| no dependence on the lost result | none exists; the runtime observations of the MB r1 target run are excluded (S3) |

**Known risks carried forward:**

* the incident-01 liability (profile transport), with result-chasing risk MEDIUM–HIGH;
* single-implementation RLR block certificates;
* the thin Q12 margins on this host (about 6 % and 9 % in r3);
* the long runtime (Stage-1 projection about 4.9 h), which is the crash-exposure window Phases 5–7 address.

## 3. What this audit does not do

It evaluates nothing on cell 308, changes no status, and authorises nothing. Target authorization for the successor
requires the user ruling (governance S1).
