# K4R1 Phases A–C: forensic reconstruction, route feasibility, selection (pre-result)

Nothing here evaluates any successor certificate on real inputs. Phase A reads only the historical K4 records. The route study uses symbolic arithmetic, the historical values in `evidence/RESIDUAL_TABLE.json`, and a blinded scout report. That report covers the schema, provenance and scope of the candidate inputs, with their decisive numbers withheld.

## Phase A: why each residual failed

`code/phase_a_residual_table.py` produces `evidence/RESIDUAL_TABLE.json`. It works from the historical report `83cabce2` and the CUSUM records bound by manifest `29ad1f9b`, recomputes each cell exactly, and asserts equality with the historical `R_cell_hi` and `Rprime_cell_hi`.

| m | cells | region | D.hi at cell-0 e0 | ρ·M_R2 | R2_interval over cell |
|---|---|---|---|---|---|
| 2 | 0, 1 | (0, 10187/10⁷] | −3.73 | 7.89 / 7.83 | symmetric, ±3.10e4 / ±3.07e4 |
| 3 | 0, 1, 2 | (0, 957/625000] | −2.53 | 7.76 / 7.71 / 7.65 | symmetric, about ±3.0e4 |
| 5 | 0, 1, 2 | (0, 957/625000] | −0.94 | 7.63 / 7.57 / 7.52 | symmetric, about ±2.95e4 |

Findings common to all 8 residual (m, cell) pairs:
- D.hi < 0 in every one, but `D.hi + ρ·M_R2 ≥ 0`, so the chain is empty.
- `R.hi + remainder ≥ 0`. Cell 0 contains e = 0, where R(0) = 0 exactly, so the direct rule can never certify it.
- R.lo < 0 everywhere, so there is no counterexample.
- `R_interval` and `D_interval` are local, taken at the point e0. `R2_interval` is local and uniform over the closed cell. `M_R2` equals the magnitude of `R2_interval`. The one-sided gain of `R2_interval` over `M_R2` is exactly **0** in all 8 cases: the interval is sign-free, as oddness forces near 0.

## Phase B: routes

**Route A: finer near-zero partition. Sound, but needs a new producer campaign.**
- The frozen chain inequality on a subcell is `D.hi + r·M_R2 < 0`, which needs `r < |D.hi|/M_R2`.
- If D.hi and M_R2 behaved as they do on cell 0, the radius limits and minimum subcell counts would be:

| m | r_max | subcells |
|---|---|---|
| 2 | 1.20e-4 | ≥ 5 over (0, 10187/10⁷] |
| 3 | 8.29e-5 | ≥ 10 |
| 5 | 3.13e-5 | ≥ 25 over (0, 957/625000] |

- One CUSUM record carries every m, so the common partition is driven by m = 5.
- That means **≥ 25 new real CUSUM addresses**, at about 0.57–0.60 CPU-h each, so **≥ 14–15 CPU-h**. It also needs a new cell table and a producer successor: K1R6 is frozen to its own two-cell table.
- The records do not show whether D.hi and M_R2 keep these values under subdivision. M_R2 ≈ 3e4 barely changes between cells 0 and 3, so shrinking cells may not shrink it.
- Cell 0 would be handled through the chain, which is anchored at R(0) = 0 exactly.
- **Verdict: FEASIBLE_ONLY_WITH_NEW_REAL_CAMPAIGN**, with high cost, high complexity, and uncertain strength.

**Route B: signed local R″. Not feasible.** `R2_interval` is symmetric on every residual cell, so signed use equals `M_R2` exactly and no uniform R′ < 0 follows.

**Route C: integration anchored at R(0) = 0. Sound, but no leverage on its own.**
- `R(e) = ∫₀ᵉ R′` with R′ < 0 on (0, a] gives R < 0 on (0, a].
- This is exactly the frozen chain rule, so it needs the same uniform R′ enclosure that fails.
- It is the correct endpoint semantics: e = 0 is not required to satisfy R(0) < 0, because the obligation is on e > 0.

**Route D: Taylor expansion at 0 using licensed higher derivatives. Sound, needs no new real addresses, and is selected as route D3.**
- Oddness (P5-T3) gives R(0) = R″(0) = R⁗(0) = 0, and L5 gives smoothness (used qualitatively).
- Hence `R(e) = e·R′(0) + e³/6·R‴(ξ)`.
- The two ingredients come only from independently adjudicated evidence:
  - **Upper bound on R′(0).** `G = D0.hi − L1·e0²/2`, from the K1 cell-0 midpoint derivative (K1 CLOSED) and the slot-1 lower bound L1 of R‴ on [0, x1] (ADOPTED). The factor is e0²/2 = 3.23e-8.
  - **Upper bound on R‴ over [0, a].** `T = min(M3(a), U0 + a²/2·M5(a))`, from T-EXT hull majorants (ADOPTED 37/37) and slot-1 U0.
- The certificate factor is a²/6 = 1.73e-7 for m = 2 and 3.91e-7 for m = 3, 5.
- Considered and **not used**:
  - the GammaTilde point certificate `84aaa6a5`, which has only scripted self-adjudication;
  - the m = 2 sign audit `323e2b8f`, which is not countersigned.
- **Verdict: FEASIBLE.** The designer was blinded to G, T and the hull M values; strength is determined by the frozen execution.

**Route E: combined certificate. Not needed.** Route D covers each residual region (0, a] in a single piece, so a composition with signed R″ (worthless, per B) or subdivision (A) would add machinery without adding scope.

## Phase C: comparison

| | A | B | C | D3 | E |
|---|---|---|---|---|---|
| Scientific validity | sound | sound but vacuous | sound (= chain) | sound | sound |
| Expected strength | uncertain | none | none alone | unknown to designer (blinded) | ≤ D3 |
| New real addresses | ≥ 25 | 0 | 0 | **0** | ≥ 0 |
| CPU | ≥ 14–15 CPU-h | 0 | 0 | < 60 CPU-s | — |
| Implementation complexity | high (new table, producer successor, host authorization) | low | low | low (exact arithmetic over 4 records) | high |
| Unproved assumptions | D.hi and M_R2 under subdivision | none | none | none beyond P5-T3, L5, adopted records | — |
| Temporal / governance risk | new production chain | — | — | inputs pre-exist; values not read before freeze (disclosure below) | — |
| Cell 0 | via chain | no | via chain (needs R′) | yes, natively | — |
| m = 2 / 3 / 5 | yes / yes / yes (cost) | no | no | yes / yes / yes | — |

**SELECTED: route D3.** It is the smallest sound architecture that tests the full residual obligation for every m, including cell 0, with no new real computation. If D3 does not close K4, route A is the natural next predeclared successor; it would be a new campaign, not a repair.

## Pre-result disclosure (leakage), revised in r2 after qualification r1 note N4

**Not computed, printed or read by the designer before freeze:**
- G_m, T_m, B_m;
- the T-EXT hull rows 1–2 majorants M3(a) and M5(a);
- the exact slot-1 per-m rationals (L0, U0, L1, U1, M5);
- every value of the GammaTilde and sign-audit artifacts.

The preflight runs every identity and structural check without computing any of these.

**Prior knowledge the designer held,** from the published K4 r1 record and from earlier K5 campaign summaries in the designer's notes:
- the historical K1 D intervals (D0.hi, in the table above);
- slot-1 lower bounds L1 on cell 0, of order 10³;
- an R4-campaign cell-0 M5 of order 10⁹;
- the verdicts `GammaTilde > 1 CERTIFIED` for m = 3 and 5.

This knowledge fixes the order of magnitude of G and of the slot-1 part of T. The designer's claim of blindness is therefore limited to M3(a) and M5(a). The qualification r1 reviewer also reports having seen the exact slot-1 rationals, through a faulty redaction filter, without combining them.

**Why this does not bias the certificate.** The gate has no tunable parameter. Every quantity is a named field of a hash-bound adopted record, and the formula follows deductively from the theorem. A valid deductive certificate is not biased by what its designer knew. The only design choice, the route, is justified above on value-independent grounds.
