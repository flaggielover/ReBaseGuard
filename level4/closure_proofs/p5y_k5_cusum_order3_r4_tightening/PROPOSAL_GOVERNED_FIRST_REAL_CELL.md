# PROPOSAL (prepared, NOT executed): governed first real-cell qualification of the CUSUM signed-R''' producer

**Status.**
- DRAFT for the governance owner.
- `REAL_CELL_QUALIFICATION = NOT_AUTHORIZED` until a separate, pre-registered protocol is frozen and an entry is
  added to a successor authorization registry.
- Nothing in this file authorizes any evaluation.

**Basis.** R4 (freeze `0a7ce2fd`, qualification in `RESULT.md`): QUALIFIED_FOR_GOVERNED_REAL_CELL_QUALIFICATION on
manufactured and synthetic evidence. The certified pre-result Strategy-B forecast for CUSUM cell 0 is MARGINAL on the
frozen R3 scale.

## 1. Decision required before any protocol is written (not decided here)

The first real cell must be exactly one of:

| option | meaning | consequence |
|---|---|---|
| **A. Pure qualification** | cell 0 is evaluated only to qualify the producer on a real record; its signed `R'''` enclosure is **permanently excluded** from any scientific K5 use | science needs a later, separately pre-registered evaluation of cells that exclude this one, or a re-run under option B rules with a fresh pre-registration |
| **B. Pre-registered scientific probe** | cell 0 is a pre-registered K5 probe whose outcome counts scientifically **and** simultaneously qualifies the producer | the scientific acceptance rule, stopping rule and reporting of a negative or uninformative outcome must be frozen before evaluation; no post-hoc reclassification to A |

`FIRST_REAL_CELL_MODE = UNDECIDED` (must be set by the governance owner).

## 2. Items the future protocol must freeze (for either option)

1. **Scope.** Cell 0 only; m ∈ {1, 2, 3, 5}; Strategy B = certified point run at e = 0 + `local_r5` majorant
   (R4 constants `C_o0 ≤ 5.3601`, `C_e0 ≤ 469.7697`).
2. **Pinned artifacts.** R1–R4 code and config sha256; K1 record `aux5_CUSUM_0_256.json` sha256; producer identity;
   runtime contract.
3. **Assumption A1 retired.** The point run produces its own residuals, candidates and graded point errors at e = 0.
   The forecast is not evidence and is not reused.
4. **Pre-result acceptance.** Enclosure-quality thresholds from `FEASIBILITY_CRITERION_R4` (engineering), and (option B
   only) the scientific decision rule for `L_1 ≤ inf_{C_1} R'''`.
5. **Fail-closed.** Refuse on any missing certificate, record mismatch, precision or runtime drift. There is no
   fallback to the R3 C_o0 unless the protocol explicitly declares it.
6. **Authorization.** A successor registry with a single entry (cell 0, authorization sha256), re-pinned in a new
   gate module; R4's registry stays empty.
7. **Reporting.** All outcomes are published, including uninformative enclosures; no rerun with changed parameters
   without a new pre-registration.
8. **Mutation and replay.** The R4 suites are re-executed at the protocol commit before the real evaluation.
