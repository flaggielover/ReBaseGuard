# Preregistration — P5Y-K1R

Written, self-checked, committed and frozen **before** any K1R production. Not
result-bearing. K1R decides nothing about K1 by existing.

## What K1R will do

1. **B1** — evaluate the ten admission conditions `A1…A10` of
   `config/B1_ADMISSION_CONTRACT.json` against the Aux5 composite ledger. The conditions read
   only counts, hashes, producer/runtime identity, authorisation provenance and the audit's
   self-declared mode. They never read an obligation status, enclosure, utilisation, margin or
   majorant. All ten PASS ⇒ `B1_ROUTE = AUX5_COMPOSITE_ADMISSION`, the 326-cell composite is
   admitted indivisibly, and the fallback must not run. Any FAIL ⇒ zero Aux5 records are
   admitted and `B1_ROUTE = PREREGISTERED_RECOMPUTE_FALLBACK`: cells 319–323, each split
   exactly once into 2 equal exact-rational children, 10 children total, m ∈ {1,2,3,5}, no
   second refinement.
2. **B2** — certify the 2 frozen CUSUM bridge cells.
3. **B3** — certify the 6 frozen SR bridge cells on AWS.
4. Compose `[0,c] ∪ (c,e_close] ∪ [e_close,∞)` per `config/DOMAIN_COVER.json`.

## Disclosed prior observation

The read-only reconstruction that preceded this preregistration observed the Aux5 record
statuses (326/326 cells, 1304/1304 obligations PASS; m=5 utilisation 0.583–0.733 on cells
319–323) and the historical failure values quoted in `BLOCKER_MAP.md`. This is disclosed so
no reviewer is misled about what was known at freeze time. It creates no selection freedom:
admission is total (`A9`), the admission conditions read no scientific value, and gate
`G_AUX5_STATUS` halts K1R if any admitted obligation is not PASS. If a reviewer holds that a
post-K1-dated source may not be admitted at all, condition `A8` fails and the frozen fallback
runs — that branch is fixed here, in advance, at 3.2 CPU-h.

## Kill gates

`G_SCIENCE` (an enclosure reaching target 2 ⇒ HALT, report a potential scientific failure, no
refinement around it), `G_COVERAGE`, `G_BUDGET`, `G_GOVERNANCE`, `G_AUX5` (all-or-nothing),
`G_AUX5_STATUS`, `G_COST` (halt *before* 150 CPU-h), `G_SCOPE` (no post-result endpoint
movement, cell deletion, m deletion, threshold or precision relaxation, host substitution or
theorem narrowing).

## What would make K1R fail

Any kill gate firing; a bridge cell exceeding its frozen budget at refinement depth 0; an
admission condition failing *and* the fallback then failing; or any drift in an inherited
identity. K1R closing B1–B3 does **not** by itself close K1: that requires independent
scientific adjudication, which is out of scope here.
