# Incident audit for route R-MB / cell 308 (pre-freeze; coordinator draft a0)

**Author:** the campaign coordinator. It is the same agent that coordinated the overnight campaign (incidents 01 and
03) and the cell-307 campaign, and it is **not target-blind** (`ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`). This audit
is therefore **not** independent. No formal freeze may proceed unless an **independent** review accepts the
conclusions in §5 (`reviews/INCIDENT_INDEPENDENCE_REVIEW_MB308.md`, line 3 exactly INCIDENT_AUDIT_ACCEPTED or
INCIDENT_AUDIT_REJECTED).

**Rule for this document.** It quotes no validation-drift value of any route and no committed tail figure; committed
facts are pointed to by path (`history/`), incidents by class.

## 1. The route under audit

R-MB (`registry/ROUTE_REGISTRY.md`; `theory/THEOREM_MB.md` r1; `streams/FORMAL/MB308_DESIGN_DRAFT.md`):
block-resolved atom constants on cell 308's C2 partition, each the componentwise minimum of S_I1, Dv′-M on the
committed registry inputs, D14-M on RLR block certificates and Lemma G, with a Theorem-M pointwise Λ certificate at
each block's left hull endpoint (monotone envelope), consumed by the TPT-B transport on the committed TC-T inputs.

## 2. Provenance timeline of every load-bearing element

| element | first committed | where | before this campaign? |
|---|---|---|---|
| Theorem M | 7e851139 / 0d32a2e8 (02:00–04:03 +0900, 2026-09-28); review 07ab6b94 (05:13); corrections 5a49f37b (05:14) | overnight `streams/C_308/A0X/EXCLUSION_308.md` §c | yes |
| Lemma SM(d), Lemma Dv′ r2, whole-kernel supersolution | THEOREM_AD (perron-deflated campaign) | `p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md` | yes (days earlier) |
| TPT, TC-P | af4365aa (02:46) | overnight `streams/E_assembly/` | yes |
| TPT-B | ccc4ea36 (03:23) | overnight `tpt.py` | yes |
| "strongest host-free combination = TPT ∘ min(RLR, Dv′, G) ∘ tight A0" | bcb9c699 (05:21), corrected 0b44c947 (07:50) | overnight `registry/CROSS_ROUTE_THEOREM_COMPARISON.md` §5 | yes |
| lever B2c "constants re-certified on sub-segments" (outside the refuted fixed-input family) | 6d0f0615 (04:09) | overnight `streams/D_309/COVER_REFINEMENT_309.md` | yes |
| RLR / D14 | cbff958a … d3b60795 (overnight); formal 307 campaign cd5016f1 … b73b9449 | `p5y_k5_cell307_rlr_r1/theory/THEOREM_RLR307.md` | yes |
| C2b certifier | 06a7d6a5 (05:28); review 1ee93ac5 (06:06) | overnight `streams/C_308/A0X/gen/` | yes |
| C2b exact-scale selection, `sub_certify`, pointwise ladder R1–R6 | this campaign, stream A0 (after 33185113) | `streams/A0/` | **no** (new; chosen at non-target drifts only) |
| Lemmas M-U, A0-M, Dv′-M, D14-M, DM; Theorem MB | b6ab352e (r0), bfa9ad3c (r1); review 5dd80cb9 | `theory/THEOREM_MB.md` | **no** (new; corollaries of the above) |
| TPT-B on the TC-T path (`tptb_tail`) | 5dd80cb9 | `streams/ASSEMBLY/` | **no** (new wrapper of frozen code + overnight tpt.py) |

No cell-308 value under any new route exists anywhere (history inventory `history/recon/HISTORY_308_INVENTORY.md`;
Γ308 new evaluations 0).

## 3. Incidents and exposures, and their relevance to R-MB / 308

| # | record | relevance to R-MB |
|---|---|---|
| L1, L4 | overnight incident 01 + residue: committed tail radius shares beside TPT-G factors | **Relevant.** R-MB uses a profile transport (TPT-B). The route's inclusion of TPT was informed by committed tail structure (disclosed there and in E2 I-d here). Qualitative; nothing combined into a number. |
| L2, L5 | incident 02 + residue: a committed 309 value re-attributed as a floor for Λ₃₀₈ | **Not relevant to R-MB's value path**: it is exclusion-direction (a lower bound) and R-MB uses only certified upper bounds at 308's own block drifts. Relevant as history of Theorem-M-adjacent reasoning; the transfer rules T1–T4 now forbid it. |
| L3 | incident 03: the C2b brief's comparison scale derived from 308 figures | **Relevant**: C2b is on R-MB's upper-bound path. The C2b design aimed at tightness in general; this campaign's C2b parameters (exact-scale selection, N ladder) were fixed by stream A0 from non-target drifts only, without that scale (the stream had no tail figure). |
| L6 | 306 stream breach | not relevant |
| H4.3b | route audit ROUTE_AUDIT.md:315 (a 307 factor beside a 308 factor, pre-overnight) | historical; no bearing on any R-MB parameter |
| E2 I-a … I-e | coordinator inferences from committed facts (this campaign) | **Relevant (motivation provenance)**: the coordinator concluded from committed facts that a host-free route must change a consumer-side inequality. This selects the route *family*, not any parameter. |
| stream exposures | stream ASSEMBLY read THEOREM_TCT §5 (committed tail-adjacent geometry) and the overnight share text; reviewMB read committed tail figures in assigned sources; stream A (sanctioned) read everything | none was used, computed on or written (each disclosed in its report); no parameter of R-MB came from them |

## 4. Parameters of R-MB and their provenance (all fixed by rules)

| parameter | value | provenance |
|---|---|---|
| partition, hulls | C2 rule; outward 2^-20 | C2 / 307 (committed before) |
| RLR ladder | (4, 6, 8), flags as 307 | 307 decoy-cost rule (committed before) |
| pointwise ladder | C2b-x N ∈ {20, 40, 80}; C1b d ∈ {8, 10, 12}; min U / max L; L ≤ U | stream A0 study F1–F4 at drifts {1/2, 1, 11/10, 27/10, 3, 7/2} (no tail figure available to the stream) |
| members of S_i | all available (S_I1, Dv′-M ×2, D14-M, G) | dominance (charter rule 5); no member dropped by estimated effect |
| transport | TPT-B, piece-end rule, cap split | THEOREM_TPT / THEOREM_MB (sharp in its input family, TPT-O) |
| decision | Γ_dec = g_hi + max(two certified upper bounds) < 0 | conservative by construction |
| caps / workers | 307 rule from decoy costs | to be measured on decoys only |

## 5. Conclusions for the independent reviewer to accept or reject

| # | conclusion | coordinator's finding |
|---|---|---|
| 1 | Every load-bearing theorem and component of R-MB existed independently of any cell-308 outcome | **Yes**: no R-MB value for 308 has ever been computed; §2 timeline |
| 2 | No new Γ308 value has been generated | **Yes**: ledger 0/0/0/0; the only 308 computations are the pre-registered historical reconstructions (55/55 equal to committed values) |
| 3 | No target-equivalent numeric proxy for 308 has been generated in this campaign | **Yes, numerically**; the coordinator's qualitative inferences (E2) concern committed facts and idealised families, and the incident-01 state is inherited, not new |
| 4 | No R-MB parameter was selected using a target outcome | **Yes**: §4; the pointwise ladder was selected by a stream that held no tail figure |
| 5 | R-MB is prospectively defensible despite the incidents | **Yes, with disclosure**: result-chasing risk MEDIUM–HIGH (route family chosen knowing committed tail structure), mitigated by dominance-only composition, rule-fixed parameters and a single execution |

**Coordinator's recommendation:** proceed toward a formal freeze only after the independent review accepts §5, and
carry L1/L3/L4, E2 and §3's stream exposures as disclosed liabilities into the protocol, grant and adjudication.

## 6. Reproducible checks

```bash
NS=level4/closure_proofs/p5y_k5_cell308_research
python3 -I -S -B $NS/code/c308_quarantine.py --scan          # PASS; tail figures only in history/ and ledger/
grep -c '"new_target_evaluations": [1-9]' $NS/ledger/TARGET_INTEGRITY_LEDGER.jsonl   # -> 0
```
