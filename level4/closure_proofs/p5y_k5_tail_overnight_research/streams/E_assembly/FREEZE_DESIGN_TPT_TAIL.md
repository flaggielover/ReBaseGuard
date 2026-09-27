# TPT tail application — freeze design for a FUTURE campaign

**DESIGN ONLY — NOT FROZEN — NOT AUTHORIZED — NOT FREEZE_READY IN THIS CAMPAIGN.**

This design answers review R1 blocker B4 (`reviews/REVIEW_TPT_R1.md`). It records what a later, separately
authorized campaign would have to bind before applying theorem TPT to cells 307–309. Under this campaign's charter,
TPT's tail application is **BLOCKED** by incident 01 (`ledger/INCIDENT_01_TPT_GRAPH_PROXY.md`), and no step below may
be executed tonight.

## 0. Preconditions (user decisions, in this order)

1. **Disclosure.** The authorizing user sees incident 01. The campaign record already contains a qualitative estimator
   of TPT's tail effect, and the route's prioritization was informed by committed tail radius structure. Any decision
   below is taken knowing this.
2. **U3, floor extension.** TPT changes the consumer, so it is closure-only under floor r2
   (`quantity_compared.adoption_quantity`, `fail_closed[2]`).
   * If adoption is wanted, a floor extension naming the TPT clause must be frozen **before** any evaluation
     (C2 Condition 1).
   * Otherwise the campaign is explicitly CLOSURE_ONLY: a pass is scientific closure without adoption.
3. **Cell set, fixed now.** The set is {307, 308, 309}.
   * **305 OUT**: adopted under r1, not re-adjudicable.
   * **306 OUT**: the sealed adverse I2 result is known; route audit 306-g; THEOREM_TPT §3.
   * No cell may be added after any result is seen.

## 1. What is evaluated (exactly once)

For each k ∈ {307, 308, 309}:

    Γ_TPT(k) = g_hi(k) + P*(k)

* Supply: S_I1 as frozen by floor r2, the componentwise min over {Lemma G, C1, C2}, with C2's committed provenance.
* P* is theorem TPT with profile L, U from Lemma TC-P under the TC-T premises.
* The cap is the **consumed** whole-cell enclosure H_final.
* All other inputs are C2's frozen consumer inputs.

## 2. Input extraction

Per-r extraction must come from the **frozen code path**, not from a hand re-derivation (review R1 B4(a)).

* The driver imports the pinned consumer modules at their frozen blobs:
  * `c2_d5_forecast.py` 18403dbe;
  * `deflated_consume.py` a0a836fa;
  * `tct_rule.py` 98f6eee4;
  * `tail_forecast_r2.py`, pinned by hash. This closes the floor-r2 review's unpinned-load note.
* From `tct_rule`'s own per-r computation, the driver reads the tuple
  `(f_F, f_D, f_H, f_G, Env4, Ĥ_r(a), |Ĝ_r(a)| = 0)`, the W sum, the supply A, g_hi = `R.hi − e0·D.lo`, H_final and M.
* If `tct_rule` exposes these only inside a function, the driver wraps that function **without modifying it**, for
  example by recomputing through the same public sub-functions. It must record which functions were called.

## 3. Reproduction gates, inside the one sealed execution, before P* is computed

| gate | requirement (exact rational equality unless stated) |
|---|---|
| G-R1 | the whole-cell enclosure rebuilt from the extracted per-r tuple at s = ρ equals C2's committed `H_exact` for cell k |
| G-R2 | the frozen-clause Γ from the extracted inputs equals C2's committed `Gamma_exact` for cell k (floor r2 `fail_closed[2]` control) |
| G-R3 | coefficient level: each extracted per-r (f_*, Env4) equals the committed per-r values where committed. This catches an error that preserves rad(ρ) but mis-shapes rad(s) (R1 B4 last bullet). |
| G-R4 | `M_consumed == mag(H_final)` (`tpt.py` N7), and the non-emptiness check at s = 0 passes (N5) |

Any failed gate means **STOP**, with no P* computed, recorded as `REPRODUCTION_FAILED`.

## 4. Qualification (before the grant; decoys only)

* **Manufactured TC-T-shaped decoy inputs**, in the same schema, with Ĝ = 0, two towers and synthetic numbers. They
  exercise the full driver, including gates G-R1…G-R4 against decoy "committed" values. Planted mismatches must STOP.
* The qualification sandbox is built **at the freeze commit** (C12 lesson). The verifier refuses at any later
  governance state: after a grant, an accepted review or a consumed ref.
* Every path the driver writes is a seal precondition (C12-R1 lesson):
  * lexists / lstat checks, including gitignored paths;
  * `O_CREAT|O_EXCL|O_NOFOLLOW` writes;
  * every post-marker failure is sealable.
* `tpt.py` is pinned by hash (r2: `05cebc9c…`). Every validation (V1, r2 controls, V2, V3, TPT-B) is regenerated
  against that hash at the freeze commit (R1 N9).

## 5. Exactly-once mechanics (C12-R2 pattern)

* Consumed ref `refs/tpt-tail/target-consumed` → the grant commit.
* The pending-result ref and the sealed result are committed alone.
* The ledger line is written **before** execution (R1 N17).
* Refusals are recorded outcomes, not exceptions.
* No re-run.

## 6. Leakage and result-chasing classification (for the authorizing user)

* The evaluation is the target itself: three Γ values, consumed once.
* Result-chasing risk is **MEDIUM–HIGH**:
  * the route's tail relevance was anticipated from committed tail structure (incident 01);
  * no parameter is tunable after the freeze.
* A pass under CLOSURE_ONLY is scientific closure. It is **not** adoption, and it creates no r6.
