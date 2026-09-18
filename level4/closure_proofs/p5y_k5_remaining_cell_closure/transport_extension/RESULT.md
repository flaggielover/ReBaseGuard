# T-EXT result: wider-hull evenness transport of the adopted slot-1 record

```text
T_EXT_QUALIFICATION     = QUALIFIED (Q00–Q08, sign-blind)
T_EXT_ADJUDICATION      = ADOPTED (independent, fresh context, own clones; 37/37 checks)
NEW_REAL_ADDRESSES      = 0          (no model solve; sealed slot-1 intermediates + certified constants + closed-form norms)
CELLS_NEWLY_PASSING     = K1 cells 1–10, for every m ∈ {1, 2, 3, 5}
OPEN_AFTER              = m1 11–132 · m2 11–144 · m3 11–145 · m5 11–148, 305–309
H3a / K5                = NOT established (cells remain open)
```

## Timeline (temporal integrity)

| step | commit | content |
|---|---|---|
| freeze | `d91bc7de` | TEXT_SPEC, `config/TEXT_PROTOCOL.json` (`ffe108e0…`, 55 pins), code, tests, Phase A–C. `evaluate` refuses before this freeze (exercised: refused). |
| qualification + seal | `20dc6b98` | QUALIFIED: Q00–Q08 all pass. TEXT_RESULT `cb97cabc…` committed before any consumption or interpretation. The ledger shows two evaluations, both at the freeze head, byte-identical. |
| consumption | `f6540638` | C1 = C2: cells 1–10 pass for every m. Independent X-B PASS. |
| adjudication | this commit | ADOPTED 37/37 (`adjudication/ADJUDICATION.{md,json}`): fresh context, own clones on the Mac and vultr-02, byte-identical reproduction of TEXT_RESULT, the consumption, X-A and X-B |

## Qualification (`evidence/qualification_r1/QUALIFICATION_RESULT.json`, `425e88aa…`)

| gate | outcome |
|---|---|
| Q00 clean checkout | HEAD `d91bc7de`, no dirty files |
| Q01 pins | 55/55 |
| Q02 replay (η = x1) | hull norms equal to the sealed ones; M5 for all m and the 13-step trace reproduced exactly |
| Q03 manufactured exact-truth fixtures | 176 RAN, **0 violations**; max η·C_e0 19.98; 5 graded cases with 0 < det ≤ 0.1, min graded det 0.021; 12 scalar-fallback cases |
| Q04 evaluate | hulls 0..40, all graded; hull 0 equals the sealed M5 exactly |
| Q05 independent X-A | M2..M5 and Λ equal; M_n nondecreasing in k |
| Q06 mutations | 19/19 detected; the shams reproduce |
| Q07 cost | 158 CPU-s (ceiling 3600) |
| Q08 determinism | the rerun is byte-identical |

## What the sealed values show (interpreted only after the seal)

| K1 cell k | x_hi | M5 (m = 1) on [0, x_hi] | Λ(k), m = 1 | Λ(k), m = 5 |
|---:|---:|---:|---:|---:|
| 0 (slot-1) | 5.08e-4 | 1.061e8 | L1 = 1787.7 | 1064.5 |
| 1 | 1.02e-3 | 1.111e8 | 1745.7 | 1035.5 |
| 3 | 2.05e-3 | 1.359e8 | 1566.6 | 911.6 |
| 5 | 3.08e-3 | 3.114e8 | 1205.0 | 664.5 |
| 8 | 4.65e-3 | 7.518e9 | −2407.8 | −1451.2 |
| 10 | 5.71e-3 | 2.780e10 | −18886 | −10611 |
| 20 | 1.11e-2 | 7.112e12 | −1.6e7 | −4.7e6 |
| 40 | 2.28e-2 | 3.627e19 | −1.7e12 | −4.1e11 |

- **The chain.** Λ(k) is positive through cell 6 for every m and negative from cell 7. The K5-B chain then carries
  through cell 10 on the accumulated ℓ/γ. All passes of cells 1–10 are `chain` passes.
- **The piecewise rule adopted from review F2 matters.** The single-hull value L0 − (x²/2)·M5(x) is already −4225 at
  cell 6 (m = 1), where Λ(6) = +822.
- **M5 growth.** The certified M5 grows about 250-fold between cells 5 and 10, and explodes beyond. This is the
  graded resolvent amplification (the determinant falls from 0.99 to 0.05 across the zone) combined with the
  wrong-parity leakage η·T_{n+1}.
- **Curvature tightening (C2) adds nothing.** M2 grows from 1.4 at x1 to 2.2e3 at cell 10, and the passing set is
  decided by the channel.
- **Review F8, now answered.** The 0-anchored M4(η) is 9.2e7 at cell 10 and 1.7e10 at cell 20. A hybrid anchor at
  a ≠ 0 would transport over a radius L_a/M4 ≲ 2e-5, far below one cell width (≈ 5e-4). Anchors away from 0 cannot
  form multi-cell blocks with this tower.

## Disclosures (adjudication notes N1–N8, none load-bearing)

- **N1.** The frozen `text_transport.py` docstring says that any tower with η ≠ x1 is guarded. In the code the
  pre-freeze guard is in `evaluate()` and in X-A, not in `tower()`. The file is pinned, so the docstring is left
  as is and corrected here.
- **N2.** X-A re-derives the wrapper independently but calls the same frozen R3/R4 tower. There is no second
  implementation of the tower; it rests on its own R3/R4 qualification.
- **N3.** Q05 reads the order of M_n (the monotonicity gate), not its size or any sign of Λ.
- **N4.** Transport mutants are detected by output difference. That shows each site is load-bearing; it is not an
  exact-truth check. The exact-truth checks are the Q03 fixtures.
- **N5.** The cross-checks against K1 data have low power near 0, because the K1 intervals are wide there.
- **N6.** The pre-freeze runs are not all file-auditable.
  - Everything run on the dev clone `/root/work/k5c-dev` before the freeze is listed here:
    - the replay at η = x1;
    - manufactured-fixture DEV calibrations (seed offsets 900000 and 800000, plus the `fix_extra` / `fix_det`
      scripts);
    - the placeholder plumbing smoke test (every M = 10³⁰);
    - two guard checks, both refused.
  - No real hull wider than x1 was evaluated.
  - The adjudicator scanned about 22k pre-freeze files and found none.
- **N7.** C2 = C1: the curvature tightening adds no cell.
- **N8.** At adjudication time the producer checkout held these result documents uncommitted. They are committed
  here.
- **Load-bearing regime.** The pass set depends only on hulls 0–10, where the resolvent is benign: det ≥ 0.94,
  η·C_e0 ≤ 2.68, and no ee cap. That regime is inside the fixture-qualified range.

## Files

- `evidence/qualification_r1/`: every runner output, `EVAL_LEDGER.jsonl`, `TEXT_RESULT.json` (`cb97cabc…`).
- `evidence/consumption_r1/`: `TEXT_CONSUMPTION.json` (`9562eda8…`), `XB.json`.
- `adjudication/`: the independent adjudication.

Nothing frozen or historical changed. The slot-1 record, its E6 output and its POSITIVE map are not amended.
