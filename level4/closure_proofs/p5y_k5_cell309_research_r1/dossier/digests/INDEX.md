# INDEX — sources opened by the firewalled reader, and exposure ledger

This records the **reader's** exposure (not the coordinator's). The digests contain no tail-cell numeric values: every
such value was replaced by `[TAIL-NUMBER REDACTED]`; sentences that combine a route's gain factor or effect with tail
quantities were replaced by `[TAIL-COMPARISON REDACTED]`; conservatively withheld latent-scale values carry
`[LATENT-PROXY REDACTED]`. A post-write grep of all digests for ~110 distinct tail values seen in the sources returned
only false positives: "13/5", the band endpoint, and a commit hash.

Repository: `/home/user/ReBaseGuard`, HEAD `1f6b724a`. Read-only. No repository code was run. No file was written inside
the repository.
NS = `level4/closure_proofs/p5y_k5_tail_overnight_research/`; CP = `level4/closure_proofs/`.

## Files opened (content read)

| # | file | tail-cell numeric values present? | content class of tail material (if any) | digest |
|---|---|---|---|---|
| 1 | NS/streams/E_assembly/THEOREM_TPT.md | **yes (1 item)** | one committed share of the tail radius mean (midpoint-residual term share, from the C5 decomposition) plus a qualitative statement that the order-3/4 terms dominate the tail radius (provenance paragraph) | TPT.md |
| 2 | NS/streams/E_assembly/FREEZE_DESIGN_TPT_TAIL.md | no | — (commit hashes, cell labels only) | TPT.md |
| 3 | NS/streams/E_assembly/IDEA_ADLR_ATOM_DIRECT.md | no | — | TPT.md |
| 4 | NS/streams/E_assembly/tpt.py | no | — | TPT.md |
| 5 | NS/streams/E_assembly/validate_tpt_r2.py | no | — (synthetic configs) | TPT.md |
| 6 | NS/streams/E_assembly/validate_tpt_synthetic.py | no | — (synthetic configs) | TPT.md |
| 7 | NS/streams/E_assembly/validate_tptb_synthetic.py | no | — | TPT.md |
| 8 | NS/streams/E_assembly/test_tpt_guards.py | no tail-cell values | one **synthetic** spoof test geometry e0 inside the band (a test input, not a tail-cell quantity); omitted from digest | TPT.md |
| 9 | NS/streams/E_assembly/v3/TPT_V3_REPORT.md | no | — (lower-front cells 11–44 only; includes non-tail Γ values for lower-front cell 41) | TPT.md |
| 10 | NS/streams/E_assembly/v3/tc_reder.py | no | — | TPT.md |
| 11 | NS/streams/E_assembly/v3/tpt_v3_lower_front.py (lines 1–140) | no | — | TPT.md |
| 12 | NS/reviews/REVIEW_TPT_R1.md | **yes** | per-cell tail shares of S̄ for 306–309 (A0·ρ·f_G, A0·ρ²·Env4/2, A0·f_H); rounded shares in the quoted graph row next to TPT-G charges (the incident-01 proxy); the sealed Γ(5, 306; S_I2) value; tail penalty formula (symbolic; binding-side form withheld in digest) | TPT.md |
| 13 | NS/streams/D_309/SUPNORM_THEOREM.md | no | — (synthetic and declared-drift results only) | SC_SUPNORM.md |
| 14 | NS/streams/D_309/code/d309_core.py | no | — | SC_SUPNORM.md |
| 15 | NS/streams/D_309/code/d309_supnorm_fsm.py | no | — | SC_SUPNORM.md |
| 16 | NS/streams/D_309/code/d309_sct.py | no | — | SC_SUPNORM.md |
| 17 | NS/streams/D_309/code/d309_hermite.py | no | — (detector constants K = 1/2, C = 11/2 only) | SC_SUPNORM.md |
| 18 | NS/streams/D_309/code/d309_hermite_tf.py | no | — | SC_SUPNORM.md |
| 19 | NS/reviews/REVIEW_STREAM_D_R1.md | **yes** | §4.2 lists about fifteen committed tail values used as grep targets (A0/Λ floors and ceilings, C1 need values, lever percentage, factors, the |Ĝ(a)|/s_G hinge ratio) | SC_SUPNORM.md (also used in COVER/RSO/D309) |
| 20 | NS/streams/D_309/RESIDUAL_SPECIFIC_309.md | no | — (history quoted without numbers) | RSO.md |
| 21 | NS/streams/D_309/code/d309_rso.py | no | — | RSO.md |
| 22 | NS/streams/D_309/COVER_REFINEMENT_309.md | **yes (§9 only)** | committed replay CPU cost per tail cell (306–309) and for 305–309 (cost class, not Γ/margin) | COVER.md |
| 23 | NS/streams/D_309/code/d309_cover.py | no | — | COVER.md |
| 24 | NS/streams/D_309/D_309_ROUTE_SUMMARY.md | no | — | D309_SUMMARY_AND_NEGATIVES.md |
| 25 | NS/streams/D_309/SCOPED_NEGATIVE_FAMILIES_309.md | **yes** | 309 C5-T critical A0; C7 floor on Λ₃₀₉; E2 family ceiling; certified A0; C1 need before/after and relative fall; MARGINAL threshold in context; deflation factor on A0; T2 USEFUL-cell counts; the |Ĝ(a)|/s_G hinge constant; cheapest source-supply lever percentage | D309_SUMMARY_AND_NEGATIVES.md |
| 26 | NS/streams/D_309/PROGRESS.md | no | — | D309_SUMMARY_AND_NEGATIVES.md |
| 27 | NS/streams/B_307/REAL_ORDER3_THEORY.md | no | — (tail facts cited by file:line only; synthetic fixture Λ ranges and lower-front values present) | ORDER3.md |
| 28 | NS/streams/B_307/HIGHER_ORDER_AUDIT_307.md | **yes (§0 history)** | 307 knockout Γ and certified A0; C5 radius-sum decomposition shares for 307/308/309; C2 elasticities; σ3 share at the tail; tail midpoint residual magnitudes; qualitative tail binding-endpoint statement (HO-14) and "higher-order monomials carry the weight at 307" inference | ORDER3.md |
| 29 | NS/streams/B_307/B_307_ROUTE_SUMMARY.md | **yes (per-cell §0)** | 307 radius-share decomposition (C5) | ORDER3.md |
| 30 | CP/p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md | **yes (many)** | tail drift domain; Lemma G A0/A1/A2 ranges on 305–309; tail f_G range; tail ρ range; break-even s_G/s_H multiples; per-cell `critical_sup_G_over_sup_H_ratio`; pure/adopted σ3 values and σ4 tower values at 309/305; whole-cell magnitude before/after (P3′); cell-305 e₀/ρ/C_upper (and an SR index-collision example); Γ error size from the index trap; derived-gate gap; enclosure-vs-need ratios for 306–309 and the 305 margin factor | ORDER3.md (symbolic only) |
| 31 | CP/p5y_k5_cusum_order3_producer_design/README.md | no | — | ORDER3.md |
| 32 | CP/p5y_k5_cusum_order3_r2_repair/README.md | no | — | ORDER3.md |
| 33 | CP/p5y_k5_cusum_order3_r3_infrastructure/README.md | no | — | ORDER3.md |
| 34 | CP/p5y_k5_cusum_order3_r4_tightening/README.md | no | — | ORDER3.md |
| 35 | CP/p5y_k5_cusum_order3_real_producer/README.md | no | — | ORDER3.md |
| 36 | CP/p5y_k5_order3_readiness_audit/README.md | **yes (2 items)** | cell-305 g_mid_hi and ρ·x·M_R2 values; the tail drift interval for K5_INCONCLUSIVE | ORDER3.md |
| 37 | CP/p5y_k5_tail_c2_closure/OPEN_NOTES_DISPOSITION_C2.md (opened to define N1/N3/N5/N7) | **yes (comparison)** | N7 sentence: an unregistered operator-level combination "clears the gate's own bar on all three still-open cells", with the bar percentage (tail comparison) | ORDER3.md |
| 38 | CP/p5y_k5_m5_tail_closure/CAMPAIGN_A_OPEN_NOTES_DISPOSITION.md (opened to define N1/N3/N5) | **yes (many)** | tail σ3/σ4 tower values; whole-cell magnitude scale; per-r term shares at r = 3/4 on 308/309; tail-geometry ranges for fixtures (e₀, ρ, A0, A2); derived-gate gap; lower-front |Ĝ(a)|/s_G ratio (used as the tail evidence model; withheld) | ORDER3.md |

## Non-content operations (metadata only)
* `ls` of `CP/` and of `CP/p5y_k5_m5_tail_closure/` (+ `theorem/`) and of the order-3 namespaces; `find` listing of
  `NS/` to depth 3 (file names only, including `graph/`, `ledger/INCIDENT_0*.md`, `validation/*.json` names — **none of
  these opened**); `wc -c` on stream files; `git log --oneline -1` (subject line mentions incident 309R1-01 and "tail
  radius shares" with no numbers); `grep -n "^#"` headings of HIGHER_ORDER_AUDIT_307.md.

## Not opened (explicitly avoided)
* No `validation/*.json` (TPT_*, D309_*, B307_*), no `graph/*` (including `K5_TAIL_DEPENDENCY_GRAPH.md` and
  `graph_A_consumer.md`), no `ledger/*`, no `TCT_INPUTS_30x`, `REGISTRY_C2`, `phase_c/EXECUTION_DECISION.md`,
  `C5_*` adjudication/decomposition files, `TAIL_FORECAST_R2.json`, `PROPOSAL_GOVERNED_FIRST_REAL_CELL.md`, or any other
  file beyond the list above.

## Redaction decisions worth noting (for the coordinator's ledger)
* TPT §0 provenance bullet: the sentence stating the tail-radius term dominance and the midpoint-residual share →
  `[TAIL-COMPARISON REDACTED]`.
* REVIEW_TPT_R1 B1: the graph row that places tail shares beside the TPT-G charges → `[TAIL-COMPARISON REDACTED]`; the
  "true at the tail" sentence → `[TAIL-COMPARISON REDACTED]`; the exact binding-side penalty form → withheld as
  tail-structural; N12's sealed Γ → `[TAIL-NUMBER REDACTED]` (kept: "adverse").
* SCOPED F1/F3 are kept only as symbolic orderings that the verdicts themselves state (critical A0 below the Λ floor;
  E2 ceiling below the certified A0). All magnitudes are redacted.
* THEOREM_TCT "what is traded" tail paragraph and §6 enclosure-vs-need ratios → `[TAIL-COMPARISON REDACTED]`; only the
  conceptual distinction between the break-even threshold and the closing threshold is kept.
* HIGHER_ORDER_AUDIT HO-14 binding-endpoint statement and the §1 "carry the weight at 307" inference →
  `[TAIL-COMPARISON REDACTED]`.
* C2 note N7's tail comparison → `[TAIL-COMPARISON REDACTED]`.
* Conservative `[LATENT-PROXY REDACTED]`: synthetic fixture Λ ranges (FX_A/FX_B), the lower-front C scale, and the
  lower-front |Ĝ(a)|/s_G and s_G/s_H rows. These last two are the committed tail evidence model.
* Kept as non-tail: lower-front (cells 11–44) numbers, including V3 Γ values for lower-front cell 41 and
  2k₁ρC_upper ≈ 1/2; synthetic FSM, FX and LR-toy numbers; real-kernel test-function results at the declared drifts
  {0, 1/4, 1/2, 1, 3}, which contain no Λ, E_a[τ], τ, C_T or supersolution values; generic constants (κ_n, cover-rule
  bounds, TPT-G factor formula); cell index ranges; costs over all 326 CUSUM cells (not tail-specific).
