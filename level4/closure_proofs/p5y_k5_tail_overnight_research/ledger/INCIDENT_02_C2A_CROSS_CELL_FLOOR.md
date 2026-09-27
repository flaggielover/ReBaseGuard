# Incident 02: zero-compute target-cell derived quantity (C2a first version)

| item | value |
|---|---|
| found by | independent Theorem M review, `reviews/REVIEW_THEOREM_M_R1.md` §3.3 and note N4 |
| introduced by | stream C2a, first version of `streams/C_308/A0X/EXCLUSION_308.md` (committed by the coordinator in 7e851139) |
| withdrawn | by C2a under rule S8; the corrected files are committed at 0d32a2e8 |
| class | **PROXY_EXPOSURE**: a zero-compute derived quantity for a target cell (a cross-cell re-attribution) |
| new Γ evaluations | 0 |
| numbers computed | 0; the quantity was obtained by reasoning over committed values |

## What happened

C7's committed certificate `E_a[τ] ≥ 3.586306094` at the drift 19839101/10000000 was re-read as a floor for Λ₃₀₈.
* That drift is 309's left endpoint and 308's right endpoint.
* The committed record attributes the value to cell 309 only.
* The re-attribution creates a new certified endpoint for a target-cell quantity. That is
  `TARGET_QUARANTINE.json` forbidden class 2.
* The value was placed next to the committed critical A0 of cell 308, which made it an input to the X308 decision
  (S8).
* It used no Theorem M, and it is exclusion-direction only, with zero closure leverage.

## Consequences

* The 308 exclusion route (X308) is not executed and remains a DRAFT.
* Any future X308 protocol must disclose this incident.
* Ledger: one `PROXY_EXPOSURE` line with `target_equivalent_proxies = 1`. Git history cannot be rewritten (Q4), so
  the ledger fences it.
* Process lesson (coordinator): 7e851139 was committed after C2a's first completion notification. C2a had been
  resumed by the coordinator's S8 notice and was still correcting. The final files landed in 0d32a2e8.
