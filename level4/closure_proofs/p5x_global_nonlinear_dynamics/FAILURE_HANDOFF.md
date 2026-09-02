# P5X failure handoff — after the single-cell certified stop-gate

```text
PHASE_1_HUMAN_PROOFS = COMPLETE   (L1, L2, L3, L5, L6 proved; L4/L7/L8 not in scope)
PHASE_2_DEPENDENCY   = COMPLETE   (mechanism premise closure contains no Monte Carlo)
PHASE_3_STOP_GATE    = FAIL       (achieved half-width 6.417e+42 vs frozen 0.2)
PHASE_4_DECISION     = ABORT the full certified cover; no production launched
P5   = PARTIAL (unchanged)
P5X  = analytical spine established; certified continuum layer blocked
```

Read `STOP_GATE.md` first for the measured result, then `PROOF.md` for what is
now proved, then `DEFECT_REGISTER.md` for the four registered defects.

## 1. What a successor must not redo

* `L1`, `L2`, `L3`, `L5`, `L6` are proved in `PROOF.md`. `P5X-T1`, `P5X-T2` and
  `P5X-T3` are established exact theorems. Do not re-derive them; do check them
  (attack 1 of `CODEX_HANDOFF.md` §5 is still the right first attack).
* The `e = 0` self-test is the correctness anchor: the P5X equation at `e = 0`
  **is** the certified `Gamma` `a` equation, and the implementation reproduces
  its residual `3.0027342e-6` to every digit and returns `ghat(0,0) = 8.9e-16`.
  Any repaired implementation must pass this before anything else is believed.
* The drift-explicit resolvent bound works and is better than the imported
  `e = 0` constant (`1239.27` vs `1315.79`). It needs no monotonicity in `e`, so
  `L4`'s unproved clause (`D3`) stays out of the proof path.

## 2. The blocking defect — two mechanisms, one design choice

Both come from the inherited use of a **single global degree-100 Maclaurin
expansion of `phi`** (`STOP_GATE.md` §4):

1. **`phi`-truncation blow-up with drift.** The Lagrange remainder depends on
   the expansion radius through a 51st power, and a drift widens the limits from
   `|zeta| <= 11/2` to `11/2 + |e|`. Error: `3.76e-7` at `e = 0`, `4.18e-5` at
   `|e| <= 0.26` (`111x`), `7.04e+44` at `e_far = 12`. It already dominates
   `delta` at the first drifted cell and is meaningless at the far end of the
   cover. **This alone defeats the plan**, independently of intervals.
2. **Interval dependency.** The residual is exactly linear in the `e`-ball
   radius with amplification `4.96e41`, measured from `1e-8` to `1e-2`. Neither
   more Arb precision nor adaptive bisection is a rescue.

The resolvent — the risk `CERTIFICATE_PLAN.md` actually flagged — is fine and
gets *better* with drift (`5323` at `e = 0`, `1125` at `e = 1/4`, `1.000` at
`e = 12`).

## 3. The two repairs, in priority order

1. **`R-A`, panel-local Taylor expansion of `phi`** — addresses **both**
   mechanisms. Replace the single order-50 Maclaurin series by degree-`~10`
   Taylor expansions on unit-width innovation panels that follow the shifted
   limits, each with its own uniform Lagrange remainder. The truncation error
   becomes `~1e-18` per panel and stops depending on the drift entirely
   (mechanism 1 gone), and integration limits are raised to powers `~11` rather
   than `~102` (most of mechanism 2 gone). Cheaper per cell, not dearer.
   Estimated effort: a focused change to the kernel-piece assembly; no new
   mathematics.
2. **`R-B`, `e` as a Bernstein variable.** Lift the residual algebra from
   `(p, m)` to `(p, m, e)` and take the continuum range bound jointly over the
   reachable set times the `e`-cell, so dependency vanishes by construction.
   Estimated effort: one more tensor dimension throughout `polynomial.py`'s
   analogue and the Bernstein subdivision; more work than `R-A`.

Do `R-A` first, then re-measure **both** diagnostics: the `phi`-truncation
allowance as a function of the drift bound (it must become flat in `|e|`), and
the radius scan (the amplification must drop below `~1e6` per unit radius). If
both hold, cells of width `1e-4`-`1e-3` become viable and the cover returns to
the `CERTIFICATE_PLAN.md` budget.

## 4. Mandatory procedure for a repaired attempt

1. Write a new stop-gate specification, declaring detector, `m`, cell,
   precision, expansion scheme and parameters **before** running. Do not reuse
   `STOP_GATE_SPEC.md`; it describes the method that failed.
2. Keep the frozen threshold `0.2`. It is not renegotiable and it is not the
   thing that failed — the method missed it by `3.4e43`.
3. Run the `e = 0` self-test first (`certificate/selftest_e0.py`).
4. Run the radius scan (`certificate/radius_scan.py`) before the gate, and
   publish the amplification constant. A repaired method that does not report a
   radius scan has not addressed the defect.
5. Run the gate once. Record it. Do not iterate parameters against the verdict.

## 5. Adjudication items still open

| id | item | blocking |
|---|---|---|
| `D1` | frozen `b_SR = log A` is too small; correct value `log(1 + A)` | all SR certified work |
| `D2` | frozen operator enumeration for second moments omits `K_{z2,e}` | nothing; recorded |
| `D3` | `L4`'s monotonicity clause unproved | nothing, given the per-cell resolvent |
| `D4` | `L5`'s "hence" clause over-attributes | nothing |
| `D5` | a Checkpoint-A test asserts a transient worktree property instead of gate `G1`'s anchor property; frozen bytes untouched, marked `xfail` and superseded | nothing |
| — | this failure handoff and the repaired-method plan | the next stop-gate |

## 6. Honest statement of where the campaign stands

The mathematics of the campaign is in better shape than at Checkpoint A: the
reduction that the whole plan rests on is now a proved theorem rather than a
probe-supported conjecture, the far-field lemma is proved with explicit
constants that close `e_far = 12` by many orders of magnitude, the drift-explicit
resolvent bound is proved from scratch and beats the imported one, and the
inherited machinery is reproduced exactly at `e = 0` (half-width `0.0100`,
`20x` inside the threshold).

The engineering bet of `CERTIFICATE_PLAN.md` §3 — that an interval-valued `e`
could be pushed through the inherited residual architecture, with adaptive
bisection controlling the inflation — is **refuted**, quantitatively, at a cost
of about twenty minutes of compute. That is what the stop-gate was for.

`P5X` is not failed; its certified layer is blocked on a specific, understood,
repairable implementation defect. Nothing about `P5X-T4`'s truth is implicated:
the candidate value at the binding cell is still `R(0.25) = -1.5766`, against a
target of `2`.
