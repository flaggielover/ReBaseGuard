# P5Y K4 — final successor adjudication (K4R1)

**Historical K4 is unchanged:** `NOT_CLOSED` (`K4_INCONCLUSIVE_K1_RECORDS`) at `bc4ba08e`. That was the frozen checkpoint `95b1fd16` at `e5cc5a90`, executed once, with its independent review ACCEPTED. **K4R1_SUCCESSOR_VERDICT = CLOSED**, so **K4_SCIENTIFIC_LINE = CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN** and **K4_RESIDUAL_BLOCKERS = NONE**.

## Residual certified

The historical K4 residual was CUSUM m=2 cells 0–1, and m=3 and m=5 cells 0–2. Near e = 0 the chain certificate was too loose: ρ·M_R2 was larger than |D.hi|.

K4R1 (`../p5y_k4r1_nearzero_successor/`) certifies this residual with a prospectively frozen Taylor certificate anchored at 0. It uses P5-T3 oddness and the smoothness from L5.

| Input | Source |
|---|---|
| R′(0) upper bound | the K1 cell-0 midpoint derivative, corrected by the slot-1 lower bound of R‴ |
| R‴ upper bound on [0, a] | the T-EXT hull majorants and the slot-1 U0 |

All three residual regions are **K4R1_CERTIFIED**:

| m | region | B |
|---|---|---|
| 2 | (0, 10187/10⁷] | −3.7306 |
| 3 | (0, 957/625000] | −2.5318 |
| 5 | (0, 957/625000] | −0.9396 |

The successor assembly combines the inherited historical K4 cells, the K4R1 certificates and the far-field handoff as frozen. It is PASS for all 8 (D, m) on (0, 2].

## Governance trail

- **Qualification:** r1–r4 were QUALIFICATION_REJECTED, each for a governance-tooling defect and never frozen. r5 accepted candidate `93d82c87`.
- **Freeze:** `8928b8f1` (FREEZE sha `874e63e2`).
- **Execution:** exactly once at the freeze commit, with 0 new real addresses. The result `cbf1332b` is committed unmodified in `b5b4c917`.
- **Final adjudication:** fresh context, **ACCEPTED** (`adjudication/`). The adjudicator independently recomputed the result with exact rationals and matched it character for character; 88/88 structural checks passed. It checked:
  - the freeze in a fresh `--no-local` clone;
  - ancestry and timing;
  - the leakage scan across all refs;
  - the residual universe and the inherited cells.

## Scope and state

**Scope:** H2 on (0, 2], the frozen K4 obligation. R < 0 for e > 2 is not asserted, exactly as frozen in K4.

**P5Y state:** K1 CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN · K2 CLOSED · K3 CLOSED · K4 CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN · K5 OPEN · P5Y NOT_YET_CLOSED.

The machine-readable record is `K4R1_FINAL_VERDICT.json`.
