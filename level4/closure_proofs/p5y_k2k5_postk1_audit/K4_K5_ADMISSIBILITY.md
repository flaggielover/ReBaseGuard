# K4 and K5: independent admissibility audit of K1 cell records (2026-09-13)

**Scope and blinding.** This audit asks whether already-produced K1 cell records can discharge K4/K5 with **no** new result-bearing campaign.
- It inspected **schemas, frozen code and frozen geometry only**.
- No certified interval **value** of any cell record was read or evaluated for K4/K5. Only field names, the `encoding` metadata string and frozen cell endpoints were read.
- No genuine PS1 production record was opened.
- No verdict is issued.

## 1. Exact definitions (frozen text)

| id | frozen statement | source |
|---|---|---|
| K4 = `H2` | "`R(e) < 0` for all `e > 0`" | `p5_nonlinear_dynamics/THEOREM.md` measured hypotheses; K1 checkpoint §1 "`K4` (`H2`)" |
| H2 load-bearing domain | "needed only on `(0, 2]`", because `sup|R| < 2` (K1) excludes fixed points beyond 2; P5X-T7(1): "`R_{D,m}(e) < 0` for every `e in (0, E]`", `E = 2`, "for each frozen `(D,m)`" | P5X `FEASIBILITY_AUDIT.md` §8; `FROZEN_THEOREM.md` §8 |
| K4 frozen route | "certified on `[e_0, E]` by direct enclosure and on `(0, e_0]` by a certified `R' < 0` together with the **exact** `R(0) = 0` of `P5-T3`" | `FROZEN_THEOREM.md` §8; TA `K4_H2.proof_path` |
| K5 = `H3a` | "`s(e) := -R(e)/e` is continuous and strictly decreasing on `(0,2]`, with `s(0+) = GammaTilde - 1 = 1/rho_c` and `s(2) < 1`" | `p5_nonlinear_dynamics/THEOREM.md`; K1 checkpoint §1 "`K5` (`H3a`)" |
| K5 weaker frozen target | P5X-T7(2): "`s` … continuous on `(0,E]`, `s(0+) = GammaTilde - 1`, and each level `L >= 1` is attained exactly once on `(0,E]`". Route: "`s'(e) = (R(e) - eR'(e))/e^2 < 0` cellwise on `[e_0, E]`, with the behaviour on `(0, e_0]` supplied by the certified `R'` enclosure and a second-order remainder" | `FROZEN_THEOREM.md` §8 |
| scope | both detectors, `m ∈ {1,2,3,5}`: 8 `(D,m)` cells | K1 checkpoint §2 |
| precision | K1 production precision 256 bits; records carry outward exact rational endpoints | `spec.PRODUCTION_BITS`; `intervals.record()` |

## 2. What the K1 cell records contain (schema-verified)

Each per-`m` ledger entry of a **PS1 T4 record** (`succ_t4.t4`, frozen `t4_cell` algebra) and of a **CUSUM Aux4 record** (same `cover_ledger_implementation.ledger.cell_ledger`) carries these fields:

| field | exact meaning (frozen code) | used by K1 as |
|---|---|---|
| `R_interval` | enclosure of `R_{D,m}(e_0)` at the cell midpoint (`assembly.assemble` over midpoint `F` enclosures) | signed, in `taylor_enclosure` → `target_gate` |
| `D_interval` | enclosure of `R'_{D,m}(e_0)` at the midpoint (midpoint DAG `F:r:k1`) | signed, in `taylor_enclosure` (`Δ·D`) and `cover_charge` (`|D|`) |
| `R2_interval` | curvature interval from the cell-refined `F:r:k2` enclosures | **magnitude only**: `M_R2 = mag(R2_interval) >= sup_cell |R''|` (`assembly.curvature_bound` docstring); its signed use is never gated by K1 |
| `M_R2` | exact rational upper bound of `sup_cell |R''|` | cover charge and Taylor remainder |
| `rho`, `e0` | exact affine cell geometry | cell `[e0-rho, e0+rho]` |
| encoding | `"outward exact rational endpoints"` (`intervals.record`) | — |

Every field lies inside `t4_record_sha256` → `scientific_content_hash` → the sealed PS1 cell record (producer `scientific_adapter_hash 13ba2ecd…`, producer commit `c9b12670`). The same holds for Aux4 through `scientific_content_hash` and producer identity `f85bd92c…`.

Frozen geometry (pre-result, from committed tables):
- SR: PS1 cells 0–294 intersect `(0,2]`. They are contiguous from exactly `0` and reach past 2; none is symbolic. Max `rho = 0.0394919`.
- CUSUM: see `CUSUM_READINESS.md` §geometry.

## 3. K4 admissibility

| question | finding |
|---|---|
| required quantities present? | **Yes.** On a cell, `R(e) ∈ R_interval + [-ρ,ρ]·D_interval + [-ρ²M_R2/2, ρ²M_R2/2]` (the frozen `taylor_enclosure`) and `R'(e) ∈ D_interval + [-ρM_R2, ρM_R2]` (mean value theorem with `|R''| <= M_R2`). Both use D signed exactly as K1 does, and R2 only through `M_R2`. |
| domain | covered: SR cover `[0, c_SR]` and CUSUM cover `[0, 5.5]` both contain `(0,2]`; contiguity from 0 verified on frozen geometry |
| precision | 256-bit production, exact rational outward endpoints; assembly can be done in exact `Fraction` arithmetic with no rounding |
| disposition-bearing? | Yes for **K1** (inside the sealed scientific hash). **Not predeclared for K4**: the PS1 protocol/authorization and the K1 checkpoint declare only K1 gates, and the K1 checkpoint lists K4 out of scope. TA (2026-09-05, before PS1 production) records the K4 route and requires persistence of per-cell R and R′. The PS1 T4 records do persist them. |
| frozen before production? | The **route** yes (P5X FROZEN_THEOREM, TA). The **mechanical decision procedure** no. It is predeclared now in `config/K4_ASSEMBLY_PREDECLARATION.json`, blind to every genuine production value; freezing it is a governance act. Disclosure: committed non-production T4 records (PS1 control and qualification cells) have existed since before this declaration; they were not evaluated for K4 and are not K1 production records. |
| producer identity governed? | Yes: PS1 via the frozen launch authorization. CUSUM depends on the Aux4 full rerun (`CUSUM_READINESS.md`). |
| aggregation alone sufficient? | **Yes, logically**: chain `R′ < 0` cells from `e = 0` (with exact `R(0)=0`), then direct `R < 0` cells to `E = 2`, per `(D,m)`. Whether every cell's **width** is small enough is a result-dependent outcome. A width failure would be `CERTIFICATE_TOO_LOOSE` for that cell, not a missing quantity. |
| missing quantity requiring new compute? | **None.** K4 needs the complete K1 production record sets (PS1 369 cells and the CUSUM 326-cell Aux4 rerun), which are K1's own campaigns. |
| **conclusion** | **`K4_NEW_COMPUTE_REQUIRED = NO`** (assembly-only over K1 production records). Blocked by K1 completion, the CUSUM rerun, predeclaration freeze and independent adjudication. |

## 4. K5 admissibility

**Adverse finding: the frozen near-zero route is incomplete.**

1. `R` is odd (P5-T3), so where it exists `R''` is odd and `R''(0) = 0`.
2. Write `g(e) = R(e) - eR'(e)`. Then `g(0) = 0`, `g'(e) = -eR''(e)`, and `s'(e) = g(e)/e²`.
3. If `R` is C³, then `s(e) = s(0+) - (R'''(0)/6)e² + o(e²)`, and the sign of `s'` near 0 is the sign of `-R'''(0)`.
4. A second-order remainder `|R''| <= M` on `[0,δ]` gives `|s(e) - s(0+)| <= Me/2` and `|s'(e)| <= M/2`. That is continuity and the limit, **but no sign**.
5. A signed `R''` enclosure cannot certify a strict sign on a cell containing 0, because `R''(0) = 0`. The K1 records certify `R''` only in magnitude (`M_R2`) anyway.

Consequences:
- **H3a** (strict decrease on `(0,δ]`) is undecidable from K1 records on some neighbourhood of 0.
- **P5X-T7(2)** (each level attained exactly once) is also undecidable there. Levels near `s(0+)` are attained near 0, and the `rho <= rho_c` non-attainment used by P5 T9 needs `s(e) < s(0+)` on `(0,E]`, which again depends on the near-zero sign.
- The TA / FROZEN_THEOREM wording "a certified second-order remainder" near 0 therefore does not suffice. A **third-order object** is required: a certified `R'''` enclosure near 0, or equivalently a signed certified `R''` of the form `R''(e) ∈ e·[c_lo, c_hi]` on `(0,δ]`. The only other route is an exact lemma fixing that sign. No such lemma exists in the repository. The P5X obligation `L8` ("coefficient built from `R'''(0)`") lists a third-derivative system only for P5X-T8, not for T7.
- Related immutable negative evidence: the SR O9 "Aux3-style third-derivative evidence" was a `FEASIBILITY_FAIL` in that architecture (its applicability to a near-zero `R'''` rung is not established).

| question | finding |
|---|---|
| away from 0 (cells with left endpoint `> 0` beyond a near-zero strip) | assembly-only: `g(e) ∈ (R_interval - e0·D_interval) + [-ρ·e_hi·M_R2, ρ·e_hi·M_R2]`, requiring upper `< 0` cellwise; `s(2) < 1` ⇔ `R(2) > -2`, which K1's target gate gives; continuity from H1 |
| near 0 | **not assembly-only**: a third-order certified object is missing from every K1 record |
| frozen-text defects to adjudicate (not repaired here) | (a) H3a (P5, strict) and P5X-T7(2) (level attainment) are different frozen targets for "K5". FORWARD_AUDIT says adopting the weaker one "needs an explicit pre-registered decision", while FROZEN_THEOREM §8 claims it discharges H3a. (b) P5X-T7(2) read literally ("each level `L >= 1` … exactly once") is false for `L > sup s`. It must be read as levels in `[1, s(0+))`, which is itself a governance ruling. |
| **conclusion** | **`K5_NEW_COMPUTE_REQUIRED = YES`**: a near-zero third-order certificate (new certified computation under its own checkpoint), unless a new exact lemma is proved. TA's `K5_incremental_if_emitted = 105.4 CPU-h` was priced for a second-derivative rung that PS1 now persists; it does **not** cover the missing third-order object. |

## 5. Assembly readiness

- **K4**: assembly tooling built (`code/k4_assembly.py`) and tested on synthetic records only. Genuine mode is locked until `config/K4_ASSEMBLY_CHECKPOINT_HASH` is frozen. No verdict is issued. The frozen rules name no K4 verdict authority, so any verdict requires the independent adjudication of a frozen K4 checkpoint.
- **K5**: not assembly-only; no K5 discharge tooling built.
- `K4_K5_ASSEMBLY_READY = NO` (K4 tooling ready; K5 is not assembly-only).
