# Discrepancy register — every cross-priority tension P9 could find

Classes: `RESOLVED_DEFINITIONALLY` · `RESOLVED_NUMERICALLY` ·
`CONSISTENT_WITH_MC` · `CONSISTENT_WITH_BIAS` · `GENUINE_MODEL_DIFFERENCE` ·
`OPEN` · `CONTRADICTION`.

**No discrepancy is hidden.** After the authoritative P8 reconciliation, **three
rows remain `OPEN`** (`D-09`, `D-13`, `D-15`); they are listed with the same
prominence as the resolved ones. `D-08`, `D-10` and `D-14` were resolved during
the campaign by events outside P9's control, and each entry records how.

| # | discrepancy | class |
|---|---|---|
| D-01 | P2 SR gains vs P4's 1.6M-path re-run | `CONSISTENT_WITH_MC` |
| D-02 | P4 `skewnormal4/SR/m=2`, combined `\|z\| = 4.29` | `CONSISTENT_WITH_BIAS` |
| D-03 | local `rho_c` vs operational safety | `RESOLVED_DEFINITIONALLY` |
| D-04 | deterministic skeleton vs stochastic stationary behaviour | `RESOLVED_DEFINITIONALLY` |
| D-05 | P5's T10 branch-SNR asymptotic vs P7's negative crossing result | `RESOLVED_DEFINITIONALLY` |
| D-06 | P6 policy safety vs fixed-`rho` theoretical boundaries | `RESOLVED_DEFINITIONALLY` |
| D-07 | P5 premise `P9` (`m` monotonicity) vs premise `S14` | `RESOLVED_DEFINITIONALLY` |
| D-08 | root `README.md` was stale | `RESOLVED_DEFINITIONALLY` (fixed by the owner during the campaign) |
| D-09 | "Level-4 campaign CLOSED" vs `L4R-11` MANDATORY FAIL | `OPEN` |
| D-10 | `P6 = CLOSED` vs the P6 namespace's `PARTIAL` record | `RESOLVED_DEFINITIONALLY` (status table updated; namespace gap noted) |
| D-11 | P9 reproduction full-reuse ARL `45.21` vs P7 `48.36` | `RESOLVED_DEFINITIONALLY` |
| D-12 | P9 reproduction nominal CUSUM `A(0)` `452.55`, `z = -3.09` | `CONSISTENT_WITH_MC` |
| D-13 | P5-T11 map-predicted vs chain-measured `ACF1` | `OPEN` |
| D-14 | model-class / detector transfer across P3, P7, P8 | `GENUINE_MODEL_DIFFERENCE` |
| D-15 | P3 grid preregistration cannot be authenticated | `OPEN` |

---

### D-01 — P2's SR gains vs P4's 1.6M-path re-run · `CONSISTENT_WITH_MC`

P4's adjudicator re-ran the **frozen P2 score implementation** at 1.6M paths:

| m | fresh P2 implementation | P4 Route A | combined `\|z\|` |
|---:|---:|---:|---:|
| 1 | `17.3132 ± 0.0363` | `17.2589 ± 0.0203` | 1.31 |
| 2 | `14.4055 ± 0.0309` | `14.3586 ± 0.0161` | 1.35 |
| 3 | `12.8688 ± 0.0268` | `12.8313 ± 0.0130` | 1.26 |
| 5 | `10.9575 ± 0.0210` | `10.9230 ± 0.0097` | 1.49 |

This **independently rules out** a recurrence, alarm, or window mismatch. The
older 240k-path P2 result was a correlated high Monte Carlo realization across
`m`. **Not fully resolved:** the literal historical comparison gate still
**fails**, because that frozen gate treats the older Monte Carlo point as exact.
P9 carries `P2-N1` with this limitation attached and does **not** restate the
gate as passing.

### D-02 — `skewnormal4 / SR / m=2` · `CONSISTENT_WITH_BIAS`

Route A `6.3875 ± 0.0284` vs Route B `6.5561 ± 0.0270`, combined `|z| = 4.29`.
Two independent attacks (finer Route B at 960k, smallest Route B at 480k, fresh
Route A at 1.6M) converge: at the smallest step pair all four windows agree
within `0.09–0.56` combined SE. Diagnosis: **finite-step bias** in the
asymmetric frozen-SR map plus score-route MC scatter; the variance cost at
`h = 0.00625` explains why a finer step is *less precise* even as its bias falls.
**Not fully resolved:** the original protocol result is immutable and its gate
`P4-F1` remains **FAILED**. A resolved anomaly is not a passed gate.

### D-03 — local `rho_c` vs operational safety · `RESOLVED_DEFINITIONALLY`

Different quantities (`DEFINITION_CROSSWALK.md` X-06). `rho_c` is a first-order
local boundary of a deterministic map at the origin; P7's frozen operational
criterion finds no corresponding operational cliff. `P7-R1` states this as the
authoritative position. This is the single most load-bearing resolution in the
project and it resolves *in the negative direction*: the local theory does not
transfer.

### D-04 — deterministic skeleton vs stochastic stationary behaviour · `RESOLVED_DEFINITIONALLY`

P1–P3 prove the origin is locally repelling; P5-T7/P7 find a bounded,
high-dispersion stationary regime. These are not in tension: `P5-MECH` shows
they are **the same selection channel evaluated at opposite ends of its dynamic
range** — maximal per unit of `e` at `e = 0` (alarm rare, therefore exquisitely
selective, giving `GammaTilde ~ 10–17`) and vanishing once `|e|` is large enough
that the alarm is immediate (a certain event selects nothing). The chain does
not *return* from an excursion; it is **reset**. P9 regards this as the
strongest exact reconciliation in the campaign.

### D-05 — T10 vs P7's negative result · `RESOLVED_DEFINITIONALLY`

P5's own closure report states the conditional asymptotic (branch amplitude → 0
against an `O(1)` noise floor) is *consistent with* P7's negative crossing
result. **The residue that is not resolved:** the *universal*
operational-invisibility inference drawn from T10 was **REJECTED** by P5's
adjudicator. Only the conditional asymptotic survives; P9 carries `P5-T10` at
`CONDITIONAL_THEOREM` with the rejection recorded.

### D-06 — P6 policy vs fixed-`rho` boundaries · `RESOLVED_DEFINITIONALLY`

Different kernels (`DEFINITION_CROSSWALK.md` X-07). P6-T6B is a closed-loop
result for memoryless policies with `rho_max < 1`; P5-T7 is per fixed `rho`.
P6's `THEORY.md` §4.3 enumerates the differences instead of asserting
generalisation. P9 enforces that no fixed-`rho` stationary number is quoted as
adaptive-policy behaviour.

### D-07 — premise `P9` vs premise `S14` · `RESOLVED_DEFINITIONALLY`

Recorded in P6's pre-design as cross-tension `X8`. Premise `P9` says larger `m`
lowers stationary RMS and raises ARL *in absolute terms*; `S14` says
reuse-attributable ARL loss *grows* with `m` as a **ratio against the same-`m`
fresh baseline**. Measured against different controls, so both hold. This is the
same trap as `DEFINITION_CROSSWALK.md` X-05. Quoting either without the other is
misleading (P6's failure register `F16`).

### D-08 — the root `README.md` was stale · `RESOLVED_DEFINITIONALLY`

**Resolved during the campaign by the repository owner, not by P9.** The root
`README.md` now carries a P6 row and a P8 row and no longer says P6 "has not
started". P9's position — record the defect, decline to edit a frozen artifact —
was correct and required no revision. The original finding is retained below.

*Original finding:*

`README.md:34` states "P6 has a pre-design directory only; its full campaign has
not started." Four P6 campaign trees exist at the anchor commit. The Level-4
status table also has **no** P6 and **no** P8 row. This is a genuine
documentation contradiction against `HEAD`.

P9 did not fix it: editing the root README is outside P9's declared scope
(`P9_DEFINITION_AUDIT.md` §7). It was recorded as owed work, and the owner has
since discharged it.

### D-09 — "campaign CLOSED" vs `L4R-11` FAIL · `OPEN`

`level4/final_level4_closure/FINAL_REPORT.md:164` says
`CURRENT LEVEL-4 CAMPAIGN: CLOSED` and "No further Level-4 scientific closure
campaign is required." `level4/reports/LEVEL_4_CURRENT_LEDGER.md:19` keeps
`L4R-11` (the `m`–`rho` phase map, D4) as a **MANDATORY** row at **FAIL (not
run)**, and `final_global_reaudit` says the global Level-4 status "remains
partial because two original mandatory rows retain non-PASS partial/negative
outcomes."

Both statements are frozen and they are about different scopes (the *frozen*
campaign vs the *global* requirement ledger), but the repository nowhere
reconciles them explicitly. Six further priorities (P3–P8) have run *since* that
"no further campaign is required". **P9 leaves this OPEN**: it is a
project-governance question, not a scientific one, and it is not P9's to close
(`P9_DEFINITION_AUDIT.md` §3 `U4`).

### D-10 — `P6 = CLOSED` vs the P6 namespace's `PARTIAL` record · `RESOLVED_DEFINITIONALLY`

**At the anchor commit** the campaign prompt asserted `P6 = CLOSED` while the
last record in the P6 namespace read `FINAL_P6_VERDICT = PARTIAL` (gates
`G6`/`G9`/`G12` `PARTIAL`), and `p6r2b/GATE9_REPAIR_REPORT.md` said verbatim
"`P6 = CLOSED` is **not** declared here." P9 flagged the conflict and carried
every P6 claim at `PARTIAL`-consistent strength rather than granting a status
the repository had not granted.

**The authoritative status table has since been updated to `P6 = CLOSED`**, in
the same pass that produced the P8 verdict. P9 follows it.

**The residue P9 still records:** no independent Gate-9 review is documented
*inside* the P6 namespace, so a reader tracing P6's closure through
`p6r2b_gate9_crn_identity/` alone will not find it — that directory's own
verdict line remains `READY_FOR_INDEPENDENT_GATE9_REVIEW`. This is a
traceability gap, not a status dispute. `P6-NOV` remains `NOT_ESTABLISHED`:
closure is scope-bound and is not novelty.

### D-11 — P9 reproduction `45.21` vs P7 `48.36` · `RESOLVED_DEFINITIONALLY`

P9's independent full-reuse SR `m=1` ARL was `45.21 ± 0.36` discarding only
cycle 1, against P7's `48.36`. Investigated rather than reported as a
disagreement: the approach to stationarity is **oscillatory and slow**
(`460.5, 5.8, 73.7, 38.2, 53.6, 46.0, 48.6, 46.4, …`). Under a longer burn-in
the estimate rises monotonically to `48.49` (discard 10), matching P7 to `0.13`.
The apparent `3.15` gap is **entirely a burn-in convention difference** with no
scientific content. Recorded as `DEFINITION_CROSSWALK.md` X-08, which is a
P9-original crosswalk row.

### D-12 — P9 nominal CUSUM `A(0)` · `CONSISTENT_WITH_MC`

P9 measured `452.55 ± 4.07` against P7's production `465.12`, i.e.
`z = -3.09`. A second independent seed in the burn-in study gave `467.6`. P7's
**own** independent replay reported a first-cycle range of `447–492` across
families, which contains both P9 values. Diagnosis: ordinary Monte Carlo scatter
of a heavy-tailed run-length mean, not a semantic mismatch. P9 reports both of
its values rather than the more favourable one.

### D-13 — P5-T11 map-vs-chain `ACF1` · `OPEN`

Map-predicted and chain-measured `ACF1` agree to `<= 0.0174` absolute
(`<= 3.5%`) — but that is up to **16 chain standard errors**. P5's attack `A13`
was "**overturned as unresolved**": direct replay isolates the residual to the
gridded-map/PCHIP plug-in, and the prediction's own error budget is
unquantified. The **identity** `ACF1 = rho(1-Gamma_eff)` is proved
(`P5-T11`, `EXACT_THEOREM`); what is open is the accuracy of the plug-in used to
evaluate it. P9 does not close this and does not quote `<= 3.5%` as agreement
without the `16 SE` beside it.

### D-14 — model-class and detector transfer · `GENUINE_MODEL_DIFFERENCE`

**Resolved by the authoritative P8 adjudication, in the negative.** Detector
transfer is now **measured absent**, not merely unestablished, and literal `G7`
(P7-boundary transfer) **fails**. The preregistered cross-family
window-separability law and both its sub-gates are **rejected**. These are
authoritative negative results (`P8-S4`).

They are recorded as a genuine difference between model classes — the
phenomenon's *magnitude* does not carry across families — and **not** as a
positive premise for any weaker law. P9 uses none of them (§`P8_TO_P9_RECONCILIATION.md`
§4). The P8 campaign itself is `FAIL`, so this evidence is citable only as a
failed-campaign evidence set within its exact tested scope.

*Original entry, retained:*

The prompt anticipated a P3-vs-P7/P8 SR gain offset. At the anchor commit P9
finds the P1–P7 SR chain internally consistent (D-01 resolves the only recorded
SR gain tension). Any residual offset, and every question of detector or
distribution transfer, lives in P8 and is **not adjudicated**. Claude's P8
discovery *provisionally* reports that detector transfer is not established and
that boundary-transfer gate `G7` failed literally — but a failed gate is not a
positive premise, and none of it is authoritative. Left `OPEN` pending
`P8_TO_P9_RECONCILIATION.md`.

### D-15 — P3 grid preregistration · `OPEN`

P3's 49 candidate files arrived in one uncommitted intake, so temporal
preregistration cannot be independently authenticated; reports call it the
"candidate-declared fixed grid". Its adjudicator judged this not to change the
scientific result, because the boundary is analytic and continuous in `rho` so
grid cells are descriptive evaluations rather than fitted thresholds. P9 agrees
with that reasoning and still records the row `OPEN`, because temporal integrity
is a claim about process that a later reader cannot re-derive. It is carried as
`P3-LIM1` at `NOT_ESTABLISHED`.

---

## What P9 could **not** resolve

`D-09`, `D-13` and `D-15` remain `OPEN`. P9 states plainly that a synthesis
which reported "all cross-priority discrepancies resolved" would be false.

`D-08`, `D-10` and `D-14` were resolved **during** the campaign by events
outside P9's control — the owner fixed the README, the status table settled P6,
and the authoritative P8 adjudication settled transfer in the negative. P9
claims credit for none of the three; it claims only that it recorded each
correctly while it was open, and revised when the repository spoke.
