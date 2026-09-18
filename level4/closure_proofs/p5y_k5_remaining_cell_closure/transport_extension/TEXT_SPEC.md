# T-EXT — wider-hull evenness transport from the adopted slot-1 record (specification, written before any evaluation)

**Status at freeze: FROZEN_PRE_RESULT.**
- No hull wider than x1 = 5083/10⁷ had been evaluated before the freeze commit.
- `code/text_transport.py evaluate` refuses to run unless this protocol is committed, clean and pin-exact. That guard
  was exercised before the freeze: it refused.
- The only real-data computation before the freeze is the replay at η = x1, which reproduces the sealed record
  exactly.
- This revision incorporates the pre-freeze conditions of the independent strategy review
  (`../phase_c/STRATEGY_REVIEW.md`: F1–F7, F11, F13).

**Relation to slot-1 (F13).** T-EXT is a successor consumption of the sealed slot-1 record `cf90f1ea…`, whose
intermediates the executor spec declared load-bearing. It does not amend the slot-1 result, its E6 output
(`89017388…`) or the slot-1 POSITIVE consumption map.

**Notation (F7).**
- K1 cell k is the 0-based index in `cells.json`, with x_lo(k) and x_hi(k).
- Theorem cell C_{k+1} is K1 cell k.
- The T-EXT channel for K1 cell k is written **Λ(k)**. It is fed to K5-B as L_{k+1} := Λ(k).

## 1. Question

Can the adopted slot-1 evidence certify lower bounds on R''' beyond K1 cell 0? The route must be deterministic, and
it may use no new real scientific address and no model solve. If it can, how many CUSUM front cells does the frozen
Theorem K5-B then discharge?

## 2. Theorem T-EXT

Fix m ∈ {1, 2, 3, 5} and a prefix hull [0, η] with η = x_hi(k) for some k ∈ {0, …, 40}.

**Premises.**
- **(P1a)** R_m is odd (P5-T3) and C^∞ (P5X L5, independently reviewed `879792d0`; that review certifies R only).
- **(P1b)** The regularity of the component objects F_r, S_r, h_j, W_{r,j} in e, as Banach-valued functions to the
  orders the tower uses, and the differentiated resolvent identities of `r5_majorant.true_tower`. These are the R2/R3
  producer premises: σ-parity at e = 0 (`R2_DESIGN.md` §3), and the K1 kernel-derivative norm machinery, which is valid
  on any window. They are e-uniform. Slot-1 used exactly this basis on [0, x1]. (F5)
- **(P2)** R'''_m(0) ≥ L0_m, from the sealed, ADOPTED enclosure.
- **(P3)** For n = 2..5, M_{n,m}(η) := Σ|c|·sup‖P_e X⁽ⁿ⁾‖ is read from the frozen `local_r5.local_tower` tower, via
  `r5_majorant.m5(order=n)`. The tower is called with:
  - candidates and point nodes = the sealed `candidate_graded_sups` and `point_nodes`, which are the exact dyadics of
    the slot-1 run;
  - anchor drift `x1 := η`. The wrapper refuses a drift different from the hull η (F6).
  - base = { `C` = max C_upper over K1 cells 0..k; `C_e0`, `C_o0` from registry `a645a157`;
    `k`, `j` = `hermite6_ext.norm_table(0, η)`; `S0` = `hermite6_ext.sup_S0_on(n, 0, η)`; `eta` = η }.

**Conclusion.** M_{n,m}(η) ≥ sup_{[0,η]} |R_m⁽ⁿ⁾| for n = 2, 3, 4, 5.

**Proof (rule-wise, F4).**
- Each rule of the R3 tower and of the R4 local-anchoring lemma is a valid inequality whenever its inputs are valid
  upper bounds of sups over the same hull. The rules are:
  - the operator rule with leakage η·k_{i+1};
  - the graded resolvent rule for |e| ≤ η, whose scalar fallback C is valid on the hull;
  - `graded_true_sup` with wrong-parity drift η·T_{n+1};
  - local anchoring (a)–(c) with drift η, anchored at the e = 0 objects.
- A componentwise minimum of valid bounds is valid.
- The inputs above are such bounds on [0, η]:
  - the drift-aware He₆ hull norms;
  - the Hermite source sups;
  - C: each C_upper is a proved bound on ‖(I − K_e)⁻¹‖ for every e in its cell, and the hull is a union of cells 0..k;
  - the e = 0 anchors, which do not depend on η.
- At the σ-fixed x0 the odd part vanishes, so |R⁽ⁿ⁾(e)| ≤ Σ|c|·‖P_e X⁽ⁿ⁾(e)‖. ∎

The tower is also monotone in its inputs (review §2.3). Soundness does not use that; it is used only as a gate
(M_n nondecreasing in k).

**Corollary (piecewise evenness transport, F2).** Fix K1 cell k and X = x_hi(k). R''' is even and R⁽⁴⁾(0) = 0, so
for e ∈ C_k:

```text
R'''(e) = R'''(0) + ∫₀ᵉ (e−t) R⁽⁵⁾(t) dt ≥ L0 − Σ_{j=0..k} M5(x_hi(j)) ∫_{C_j ∩ [0,e]} (e−t) dt
```

The subtracted sum is nondecreasing in e, so

```text
Λ(k) := max( L0 − Σ_{j=0..k} M5(x_hi(j))·[(X − x_lo(j))² − (X − x_hi(j))²]/2 ,  −M3(X) )  ≤  inf_{C_k} R'''
```

Here M5(x_hi(0)) is the sealed slot-1 M5, and hull 0 must reproduce it exactly. The weights telescope to X²/2, so Λ(k)
is never below the single-hull value L0 − (X²/2)·M5(X). That value is reported as `L_simple`, for disclosure only.

**Corollary (curvature tightening).** For K1 cell k ≤ 40, the interval [−M2(x_hi(k)), M2(x_hi(k))] contains R''(C_k).
So H'_k = H_k ∩ [−M2, M2] and M'_k = min(M_R2, M2) are valid K5-B inputs. An empty intersection is refused as
evidence of unsoundness.

## 3. Frozen evaluation family and consumption

- **Hulls.** k = 0, 1, …, 40: the whole graded zone of the Phase A map, fixed by certified operator constants before
  any result. Hull 0 is the replay.
- **Rules.** No adaptation, no stopping rule and no selection. Every hull is evaluated. Each Λ(k) and each M2-tightened
  enclosure is an independent valid bound.
- **C1 (channel only).** Cell 0 keeps the adopted sealed L1. Cells 1–40 receive Λ(k). Cells ≥ 41 keep L = None.
  Records, loader and `k5b_literal` go through the accepted E6 adapter's frozen functions.
- **C2 (the T-EXT result).** C1 plus curvature tightening on cells 0–40. K5-B is monotone under tighter valid inputs,
  so C2 ⊇ C1.
- **Scope.** H3a is claimed for no m unless every cell meeting (0, 2] passes.

## 4. Gates

Mechanical and sign-blind: no gate reads a value of Λ or M_n.

| gate | content |
|---|---|
| Q00 CLEAN | the qualification runs from a clean checkout of the freeze commit |
| Q01 PINS | every bound file equals its sha256 in `config/TEXT_PROTOCOL.json` |
| Q02 REPLAY | η = x1: hull norms equal the sealed ones exactly; M5 (all m), the 13-step trace and L1 within relative 2⁻¹⁶⁰; mode graded; CRAMER contract |
| Q03 FIXTURES | frozen R4 `first_cell_r4.run`, exact rational truth, checking every tower node and anchor component, the Strategy-B bounds and M5 ≥ max\|R⁽⁵⁾\| on 17 grid points, at widened hulls. Families: R4 fixtures × widening factors; T-EXT wide slow-even (η·C_e0 up to 20); T-EXT small-determinant (slow even and odd modes, strong drift, dense η grid). Requirements: 0 violations; ≥ 100 cases RAN; max η·C_e0 ≥ 10.7; ≥ 3 cases with η·C_e0 ≥ 4; ≥ 2 graded cases with 0 < det ≤ 0.1; min graded det ≤ 0.06 (CUSUM hull 40: 0.050); ≥ 1 scalar-fallback case. **Not covered by fixtures:** the ee-cap regime of hulls 33–40. Its rule is min(graded, C) of two valid bounds; manufactured Neumann rigs always have C above the graded value. (F1) |
| Q04 EVALUATE | hulls 0..40, all graded; hull 0 reproduces the sealed M5 exactly |
| Q05 X-A | an independent re-derivation of M2..M5 and Λ is exactly equal; M_n nondecreasing in k |
| Q06 MUTATIONS | the shams reproduce the frozen result, and all 19 mutants (TM01–TM14, CM01–CM05) are detected |
| Q07 COST | total CPU ≤ 1 CPU-h |
| Q08 DETERMINISM | a second evaluation is byte-identical |

**Verdict rule (F11).**
- Every gate passes: QUALIFIED.
- A gate before evaluation (Q00–Q03) fails: NOT_QUALIFIED.
- Any later gate fails: VOID. The result is not consumed, and nothing is re-run under this protocol.
- Every evaluation writes EVALUATE_START and EVALUATE_OUTPUT (output sha256) lines to `EVAL_LEDGER.jsonl`.

## 5. Temporal order (publication)

1. **Freeze commit:** this spec, `config/TEXT_PROTOCOL.json`, all code, and the Phase A–C documents, published.
2. **Qualification and evaluation**, from a clean checkout of the freeze commit on vultr-02 with the frozen venv.
   The evidence lives outside the checkout. TEXT_RESULT is sealed by committing its sha256 with the qualification
   evidence and the ledger, before any consumption.
3. **Consumption** C1/C2 and X-B (independent chain, fed channel and curvature), published.
4. **Independent adjudication** (fresh context, own clone), published. Only then does the T-EXT pass set enter the
   open-cell map.

## 6. Scope limits

- T-EXT reuses the e = 0 point evidence only.
- Its reach is capped by M5 growth: pointwise L > 0 means cells ≤ 9–10 even if M5 stayed flat. The piecewise rule and
  the chain can carry further.
- It cannot touch the scalar-only zone (cells ≥ 41) or the m = 5 tail.
- The exported M2–M4 are sealed for later successors, such as hybrid anchors at a ≠ 0 (review F8). Any such use needs
  its own preregistration.
