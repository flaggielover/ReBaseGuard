# K5 order-3 readiness audit (read-only; nothing frozen, nothing authorized)

**Verdict: `K5_FULL_CAMPAIGN_RECOMMENDATION = NOT_READY`.** Two independent blockers stand before any order-3
campaign, and a third finding shows the proposed campaign is substantially larger than the mathematics requires.

This namespace is additive and non-certifying. It runs no scientific computation, freezes no protocol, issues no
countersignature, and changes no frozen artifact. It reads the committed K5 objects and the certified CUSUM K1
records, and reports what they imply.

```text
K5_BRIDGE_THEOREM                    = PASS (sufficient, not complete; independent countersignature still recommended)
K5_ORDER3_PRODUCER_EXISTS            = NO   (SR: AUX3_SR_FEASIBILITY_FAIL; CUSUM: order-3 sources only, no F_r:3)
K5_SR_K1_INPUTS_EXIST                = NO   (PS1 production is still draining; no SR R/R'/R'' records exist)
K5_CUSUM_K1_INPUTS_EXIST             = YES  (new since 2026-09-16: the 326-cell composite closure)
CUSUM_CELLS_PROVABLY_NOT_NEEDING_R3  = 156 of 310  (cells 149-304, for every m in {1,2,3,5})
K5_ORDER3_PROBE                      = INCONCLUSIVE (not run: the frozen oracle's execution precondition is unmet)
FULL_K5_PRODUCTION_AUTHORIZED        = NO
```

## 1. Lineage

```text
K2 CLOSED -> K3 CLOSED -> K1/K4 inputs -> K5 bridge (Theorem K5-B) -> certified order-3 evidence
                                                -> K5 feasibility oracle -> K5 adjudication -> P5Z integration
```

| Stage | Where | State |
|---|---|---|
| Binding target | `p5y_postk1_precompute_resolution/K5_TARGET_AND_THIRD_ORDER.md` | H3a (form A), adjudicated against the P5X form-B weakening |
| Bridge theorem | `p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md` (Theorem K5-B) | PASS, sufficient-only |
| Feasibility oracle | `p5y_k5_feasibility/config/K5_FEASIBILITY_ORACLE.json` | FROZEN_PRE_RESULT, `executed: false` |
| K4 assembly | `p5y_k2k5_postk1_audit/` | frozen; `WAITING_FOR_COMPLETE_K1_INPUTS` |
| CUSUM K1 inputs | `p5y_k1_cusum_aux5_composite_closure/` | **CLOSED 2026-09-16**, 326 cells 0-325 |
| SR K1 inputs | `p5y_k1_ps1_production/production/` | empty; the AWS gen-2 campaign is draining |
| SR order-3 producer | `p5y_k1_sr_o9_aux3_successor/` | `AUX3_SR_FEASIBILITY_FAIL` at Phase 4 |
| CUSUM order-3 evidence | Aux3/Aux4/Aux5 `auxiliary_third_derivative_evidence_v1` | magnitudes only; no `F_r:3`, no signed value |

## 2. What K5 actually asks (reconstructed from the repository)

- `R = R_{D,m}(e)` is the frozen nonlinear response of detector `D` at parameter `m`, odd (P5-T3) and real-analytic
  (P5X L5), hence C³ with `R''(0) = 0` and `R'(0) = 1 − Γ̃`.
- `s(e) := −R(e)/e` on `(0,2]`. **H3a** (binding, form A): for each frozen `(D,m)`, `s` is continuous and **strictly
  decreasing** on `(0,2]`, with `s(0+) = Γ̃ − 1` and `s(2) < 1`.
- Already analytic, no numerics needed: continuity; `s(0+) = −R'(0)`; and `s(2) < 1 ⇔ R(2) > −2`, which K1 certifies.
- What remains numerical is exactly **`s' < 0` on `(0,2]`**. With `g(e) := R(e) − e R'(e)` one has `g(0) = 0`,
  `g' = −e R''` and `s'(e) = g(e)/e²`, so H3a reduces to `g < 0` on `(0,2]`.

The exact implication chain in the repository is **not** the schematic "sign of R''' ⇒ convexity ⇒ s' < 0":

```text
certified lower bound L_k <= inf_{C_k} R'''        (new, per cell)
        + K1 certified R(e0), R'(e0), R''(cell)     (existing)
  -> per-cell lower bounds l_k, mu_k for R''        (exact rational recurrence, MVT for R'')
  -> per-cell upper bounds gamma_k, U_k, Gamma_k for g  (integration of g' = -e R'')
  -> g < 0 on (0,2]  ->  s' < 0  ->  H3a
```

**Order 3 is necessary only near zero, and only because order 2 cannot work there.** `R''` is odd, so `R''(0) = 0`
and every `R''` enclosure over the first cell contains 0: `mu_1 <= 0`, and the direct bound is structurally hopeless
because `|g| = O(e³)` there. `a3 = R'''(0)/6 > 0` is the only generic way H3a can hold at 0; `a3 < 0` would
*disprove* H3a. So order-3 evidence is necessary **for this route at the left endpoint**, and a certified
`R'''(cell 0) < 0` would be a mathematical counterexample rather than a failure of method.

## 3. Bridge theorem audit — PASS, with three caveats

Theorem K5-B is sound as written: exact rational recurrences, outward endpoints, no tolerance or tuning; the MVT
step for `R''`, the integral step for `g`, and the independent direct bound `Γ_k` each check out, and the
endpoint facts (`s(0+)`, `s(2) < 1`) come from analytic results plus a K1 gate, not from the recurrence. Cell 1's
special case is correct: `R''(0) = 0` gives `R'' ≥ L_1 t`, hence `g ≤ −L_1 e³/3 < 0` when `L_1 > 0`. No circularity:
order-3 objects depend only on orders 0–2 of the same frozen recursions.

Caveats that the repository states and this audit confirms:

1. **Sufficient, not complete.** A failed recurrence proves nothing against H3a. Degenerate cases (`a3 = 0`, or `g`
   touching 0 inside `(0,2]`) are not certifiable by any interval method.
2. **Not independently countersigned.** `p5y_k5_feasibility/RESULT.md` records that the theorem and the oracle were
   written by the same agent session as the K2/K3 packet and recommends an independent countersignature before K5-B
   is cited as adjudicated. That recommendation is still open.
3. **The chain is contiguity-dependent.** `l_k = max(H_k.lo, l_{k−1} + 2ρ_k L_k)`: on any cell with no order-3
   bound, `l_k` collapses to `H_k.lo`. An order-3 island therefore buys nothing downstream — only an unbroken run
   from cell 0 propagates.

## 4. Minimality — the proposed CUSUM universe is not minimal

The CUSUM K1 records needed by the bridge (`R_interval`, `D_interval`, `R2_interval`, `M_R2` per m) exist for the
first time as of the 2026-09-16 composite closure. `code/k5_minimality.py` evaluates the frozen K5-B recurrences on
those 326 certified records with **no** order-3 evidence (`L_k = −∞`) and reports, per m, which cells the theorem
still cannot discharge. Result (`evidence/CUSUM_MINIMALITY_R1.json`):

| m | cells needing order-3 | count | cells closed by K1 records alone |
|---|---|---:|---|
| 1 | 0–132 | 133 | 133–309 (177) |
| 2 | 0–144 | 145 | 145–309 (165) |
| 3 | 0–145 | 146 | 146–309 (164) |
| 5 | 0–148 **and 305–309** | 154 | 149–304 (156) |
| **union** | **0–148 ∪ 305–309** | **154** | **149–304 (156), for every m** |

Consequences.

- **`CUSUM candidate 0–309 (310 cells) = SUFFICIENT_BUT_NONMINIMAL`.** For m = 1, 2, 3 the minimal order-3 universe
  is exactly the prefix 0–132 / 0–144 / 0–145: every later cell is discharged by the direct bound `Γ_k < 0` from
  records that already exist. 156 cells (149–304) are provably unnecessary for **every** m.
- **The near-zero strip fallback would have been INSUFFICIENT.** The "left < 1/4" strip (CUSUM cells 0–221) covers
  the prefix but misses the m = 5 cells 305–309, which fail near `e = 2`. Nothing in the pre-result documents
  anticipated a second failing region; it appears only against realised widths.
- **`Z2` never fires.** No cell, for any m, has `R2_interval.lo > 0`: the realised K1 curvature enclosures are
  nowhere sign-determinate. The entire tail is carried by the direct bound `Γ_k`, not by the `R'' > 0` route the
  design anticipated.
- **The m = 5 tail is a chain problem, not a local one.** On 305–309 the failure is `Γ_k = g_mid_hi + ρ x M_R2 > 0`
  driven by the curvature slack (e.g. cell 305: `g_mid_hi = −0.337`, `ρ x M_R2 = +0.379`), while `μ_k` can only
  improve through the accumulated `l` chain. Closing them through K5-B therefore needs an **unbroken** order-3 run
  0–309, or a tightened K1 `R''` enclosure on those five cells, or acceptance of `K5_INCONCLUSIVE` for m = 5 on
  roughly `(1.62, 2]`.

So the smallest defensible CUSUM campaign is **0–148 (149 cells)** for m ∈ {1,2,3} plus a decision about the m = 5
tail; the 310-cell candidate is justified only if that tail is to be closed through the chain.

**SR minimality cannot be decided at all yet**: it needs SR K1 records, which do not exist.

## 5. Reuse — what the existing records do and do not contain

| | SR | CUSUM |
|---|---|---|
| `ORDER3_REUSE` | **NONE** | **PARTIAL** |

- CUSUM Aux3/Aux4/Aux5 records carry `auxiliary_third_derivative_evidence_v1`: order-3 **source** objects
  (`S_r:3`, `W_(r,j):3`, `h_j:3`), their residuals, and order-3 midpoint error nodes (`F:3`, `D:3`, `H:3`).
- Every one of those numbers is `mag_fraction(...) = max(|lo|,|hi|)` — an **unsigned magnitude**. The bridge needs a
  signed lower bound `L_k ≤ inf R'''`. No sign can be recovered from a magnitude, so **no R''' sign or enclosure is
  derivable from the committed records**, and the near-zero question (`a3 > 0`?) is untouched by them.
- What is missing beyond signs: the order-3 rung `F_r:3` (r = 0..4), the all-m assembly at order 3, and the
  whole-cell fourth-order remainder `ρ·T[R,4]`.
- The order 0–2 payload in the records is likewise residual bounds (`delta_mid`, `delta_cell`), not the signed
  candidate polynomials, so an order-3 producer cannot seed itself from the sealed records: it must redo the base
  per-cell solve. That is what makes the cost estimate below a *full* cell cost, not a delta.
- Reused without recomputation: the order-3 **cost and conditioning** measurements, and all of `R`, `R'`, `R''`,
  which is exactly what §4 exploits to delete 156 cells from the campaign.

## 6. Producer status — the hard blocker

The frozen oracle's own `execution_precondition` is *a governed certified order-3 producer (identity-bound) exists
for the detector*. It is unmet on both sides, and this audit confirms it:

- **SR**: `AUX3_SR_FEASIBILITY_FAIL`. Every certifiable whole-cell fourth-order bound is norm-based; the best
  self-consistent tower fed by ideal midpoint evidence and exact norms still left m = 2, 3, 5 above the kill
  threshold at cell 313, where `C·ρ ≈ 0.31`. This audit checked the frozen PS1 geometry: cells 0, 1 and 207 all sit
  at `C·ρ = 0.3133`, the *same* product as the cell where the tower failed — the RHO_CAP rule ties `ρ` to `C`. The
  amplification that killed Aux3 is therefore present exactly where K5 needs R''' most. (The K5 test is a sign test,
  not the 1/20 cover budget, so this is a strong risk signal, not a proof of infeasibility.)
- **CUSUM**: Aux4/Aux5 compute order-3 sources only. No `F_r:3`, no signed export, no fourth-order tower.

Building such a producer is a separately governed work item; it is out of scope here, and until it exists the
frozen probes cannot be run.

## 7. Probe design review (no probe was run)

The oracle freezes SR {0, 207, 294} and CUSUM {0, 221, 309} by the rule *first cell, last cell with left < 1/4, last
cell meeting (0,2]*. This audit reproduced that rule exactly against the frozen tables: SR PS1 cells 0–294 meet
`(0,2]` (295 cells), last with `left < 1/4` is 207, cell 294 contains 2; CUSUM cells 0–309 (310), last with
`left < 1/4` is 221, cell 309 contains 2. The predeclared cells are what the rule says.

Against §4, the set is diagnostically imperfect: **CUSUM 221 lies inside 149–304, the region now proved not to need
order-3 evidence at all**, while the newly identified difficult region is 305–309. A stronger minimal set would be
{0, 148, 305}: left endpoint, the last cell of the required prefix, and the first cell of the m = 5 tail failure.
The probe set is nevertheless **frozen pre-result and must not be edited**; adopting a better set requires a new
predeclared successor oracle, not a change to this one. No probe is proposed or run here.

## 8. Cost model (measured where possible)

Measured, CUSUM Aux5 production, 326 sealed cells: **2,069.5 CPU-s per cell** (min 2,027, max 2,150), peak RSS
248 MiB, record 281 KiB, of which the existing order-3 *source* work is 172 CPU-s (8.3 %).

| | per cell | minimal universe | full candidate |
|---|---|---|---|
| CUSUM order-3 producer (est. 1.3–1.9× the measured cell, since the base solve must be redone) | 0.75–1.10 CPU-h | 149 cells: **110–165 CPU-h** | 310 cells: **230–340 CPU-h** |
| SR order-3 producer (PS1 measured mean 12.0 CPU-h/cell, worst+10 % 13.8, reservation 19.0) | 16–26 CPU-h | unknown | 295 cells: **4,700–7,700 CPU-h** |

The earlier pre-result estimate (CUSUM ≲ 124 CPU-h at 0.4 CPU-h/cell; SR 1,500–2,870 CPU-h at 5.1–9.7 CPU-h/cell)
assumed an order-3 *increment* on top of an existing cell. §5 shows that increment is not available from the sealed
records, so the realistic figures are the ones above. Artifacts: ~281 KiB/cell → 41 MiB (149 cells) or 85 MiB (310).

Wall time, CUSUM minimal universe at ~0.9 CPU-h/cell: 4 workers ≈ 34 h, 8 ≈ 17 h, 16 ≈ 8.5 h, 32 ≈ 4 h — but
`rebaseguard-vultr-02` has 4 physical cores and the frozen runtime contract pins 4 workers on cores 0/2/4/6, so 8+
workers means new hosts, and the SR cross-host replay measured **0/24** bit-identical records against AWS. Any
multi-host K5 plan must re-qualify determinism first; the 16- and 32-worker figures are arithmetic, not a plan.

## 9. Adversarial review

| Falsification attempt | Outcome |
|---|---|
| Is order-3 really necessary? | Yes for this route at the left endpoint, and only there by necessity: `R''(0) = 0` makes order 2 sign-blind. It is *one sufficient route*, not the unique one: sharper K1 `R''`/`g` enclosures near 0 would do, but the frozen budgets are orders of magnitude too wide (`M_R2 ≈ 1.7·10⁴` on CUSUM cell 0). |
| Is the claimed minimal universe right? | It is a statement about the frozen theorem on committed records, reproduced by `verify --records`, and it is conservative: it deletes only cells the theorem discharges *without any* order-3 input, for every m. |
| Could the deleted cells matter later? | Only if the theorem changed. Under K5-B the direct bound `Γ_k < 0` is unconditional on those cells. |
| Contamination of K1/K4/CUSUM artifacts? | None: the scan is read-only, reads the exported closure records, and writes only into this namespace. The composite closure, its export and the production runtime are untouched. |
| Probe representativeness | Weak on one of six cells (CUSUM 221), and the set cannot be changed without a new oracle. |
| Is the full campaign ready? | No: no producer, no SR inputs, no countersignature on the bridge. |
| Is the cost model honest? | It is measured on the CUSUM side and extrapolated on the SR side, with the extrapolation stated and a range given; the SR figure is 2–3× the earlier pre-result estimate because the base solve cannot be reused. |

## 10. What would unblock K5

1. An independent countersignature of Theorem K5-B (recommended by its own result record).
2. A governed, identity-bound **certified order-3 producer**, gated by its own feasibility oracle — the SR Aux3
   failure and the equal `C·ρ` near zero make this the decisive technical risk.
3. SR K1 inputs: the PS1 campaign has to finish and close before the SR half of K5 can even be scoped.
4. A new predeclared probe oracle if the probe set is to reflect §4 (CUSUM {0, 148, 305} rather than {0, 221, 309}).

Only then does a full-campaign authorization become a meaningful question — and by §4 it should be authorized for
149 CUSUM cells plus an explicit decision on the m = 5 tail, not for 310.

```text
K5_FULL_CAMPAIGN_RECOMMENDATION = NOT_READY
FULL_K5_PRODUCTION_LAUNCHED     = NO
```

## Commands

```bash
python -B tests/test_k5_minimality.py
python -B code/k5_minimality.py verify --evidence evidence/CUSUM_MINIMALITY_R1.json
# against the external export tree (records live on rebaseguard-vultr-02, not in Git):
python -B code/k5_minimality.py verify --evidence evidence/CUSUM_MINIMALITY_R1.json \
    --records /root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records \
    --cells   level4/closure_proofs/p5y_k1_cover_ledger_successor/config/cells.json
```
