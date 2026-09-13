# K2 and K3: no-compute theorem and governance audit (2026-09-13)

**Scope.** This is a read-only audit of committed records. No computation was run, no obligation was added, and no closure is claimed.

**Sources.**
- `p5y_k1_binding_campaign/CHECKPOINT.md` §1 and `CHECKPOINT.json` `target.out_of_scope`
- `p5y_theorem_adjudication/THEOREM_ADJUDICATION.json` (binding, 2026-09-05; hereafter TA)
- `p5x_global_nonlinear_dynamics/{FROZEN_THEOREM.md §7, §10, FROZEN_GATES.md G4, PROOF_OBLIGATIONS.md L2/L5/L6/C2, DEPENDENCY_AUDIT.md, LEAN_COMPATIBILITY.md X2}`
- `p5_nonlinear_dynamics/{THEOREM.md, PROOF.md, INDEPENDENT_ADJUDICATION.md}`
- `p5y_k2k5_forward_audit/FORWARD_AUDIT.md`
- `p5y_micropilot_gate1/GATE1_RESULT.md`

## Correction carried forward

`FORWARD_AUDIT.md` classified K2 and K3 as "not hypotheses of the authoritative theorem". The binding TA overturned that reading ("WRONG"). Both quantities are consumed by **P5X-T6**, a `CERTIFIED_THEOREM` and the P5X primary target. They are also consumed by P5X-T9 items 4–5 and by frozen gate G4. The DAG row in `p5y_postk1_frontier/P5Y_POST_K1_DAG.md` that said K2 "is not a hypothesis of T8/T9/T10" is right about T8–T10, but it is not the governing consumer. This audit uses the TA reading.

## K2: `s_min = inf_e S_{D,m}(e) > 0`

| item | finding |
|---|---|
| frozen obligation | K1 checkpoint §1: "`K2` (`s_min > 0`)", out of K1 scope and OPEN. P5X-T6: "with certified `s_min = inf_e S_{D,m}(e) > 0` … `rho^2 s_min + (1-rho)^2/m <= E_pi[e^2]`" for each frozen `(D,m)`, all `rho ∈ [0,1]`. Gate G4 requires "`s_min > 0` … certified" (TWO_SIDED / UPPER_ONLY / NOT_ESTABLISHED). P5X-T9 item 5 (high dispersion) consumes it. TA verdict: `K2_POSITIVITY_STILL_REQUIRED`. |
| exact theorems available | P5-T2 (exact `V = rho^2 S + (1-rho)^2/m`); P5-T3 (`S` even); P5-T7 (invariant law, all moments); P5X `L6` identity (proof route: invariance + P5-T2 + P5-T7). For `rho < 1`, `V >= (1-rho)^2/m > 0` automatically. That is **not** the frozen statement, which bounds via `s_min` uniformly in `rho` including `rho = 1`. |
| proofs of positivity | **none**. No committed exact theorem gives `inf_e S > 0`. P5 T10's proof uses only `S(0) > 0` ("measured; also … non-degenerate") and the hypothesis "`S` continuous at 0". Both concern `e = 0` only, and continuity is unproved (TA; INDEPENDENT_ADJUDICATION T10). |
| certified numerical evidence | **none**. The obligation route is `C2` (enclosure of `E_e[Rbar^2]` on the cover, `S = E[Rbar^2] - R^2`), with `L2` (pair recursion) for `m >= 2`. No C2 producer or record exists. K1 machinery certifies first moments only ("First-moment machinery does not certify second moments", FORWARD_AUDIT). |
| non-certifying evidence | Gate-1 `PILOT-SMIN-ANALYTIC` scoping scan: min conditional variance `0.0403`, "Explicitly a scoping scan, not a certificate"; measured `s_min = 0.478`. |
| formal evidence | P5X Lean spine `X2` (two-sided invariant-mean bound) consumes `g_min` as a **hypothesis** and asserts no value (`LEAN_COMPATIBILITY.md`, `LEAN_PLAN.md`). P5 Lean (`NonlinearSkeletonP5.lean`, 12 declarations) contains no `S` positivity statement. |
| frozen fallback | `L2` failure: "`S_{D,m}` for `m >= 2` is not certifiable; `P5X-T6` retreats to `m = 1` (still a real theorem)". G4 admits `UPPER_ONLY`. These are frozen outcome labels, not discharges of K2. |
| missing | (i) a certified `s_min > 0` per frozen `(D,m)`: scientific, requires C2/L2 certified computation under its own pre-result checkpoint; or (ii) an exact positivity theorem, which does not exist in the repository and is not invented here. (iii) Governance: no K2 checkpoint (scope, cover, far-field for `S`, budget, verdicts) has been frozen; K1's checkpoint explicitly excludes K2. |
| scientific vs governance | **Scientific incompleteness** (no proof, no certificate), plus a **governance gap** (no checkpoint). Publication wording is already correct: every status record lists K2 OPEN. |
| **status** | **`K2 = INCOMPLETE`**. Not closable without new certified compute or a new exact theorem. Not blocked by K1. |

## K3: `M_2 = sup_e E_e[Rbar^2]` "finite / useful"

| item | finding |
|---|---|
| frozen obligation | K1 checkpoint §1: "`K3` (finite / useful `M_2`)", OPEN. P5X-T6 upper arm: "`M_2 = sup_e E_e[Rbar^2] < infinity` … `E_pi[e^2] <= rho^2 M_2 + (1-rho)^2/m`". G4: "`M_2 < infinity` … certified". TA verdict: `K3_FINITE_BUT_TIGHT_BOUND_STILL_REQUIRED`, which reads the "useful" half as binding. |
| finiteness half | **Discharged exactly.** P5-T5 (EXACT, every `p >= 1`, every `D, m, rho, e`, right side `e`-free) at `p = 1` gives `M_2 <= C_D`, with P5-T4 (EXACT, explicit constants) `C_CUSUM <= 9.8959e8` and `C_SR <= 1.4054e11`. The P5X-T6 upper arm and G4's `M_2 < infinity` therefore hold exactly with `M_2 := C_D`. |
| usefulness half | **Not discharged.** With `M_2 = C_D` the upper arm is numerically empty (TA: bounds stationary `E_pi[e^2]` by ~`1e9`/`1e11` against measured RMS 1.37). TA rules that P5X-T6 was frozen as the primary target "to deliver a quantitative sandwich", so a tight `M_2` is still required. |
| quantitative usefulness criterion | **None frozen.** FROZEN_THEOREM, FROZEN_GATES G4, PROOF_OBLIGATIONS and the K1 checkpoint state no numerical threshold for a "useful" `M_2`. P5X LIMITATIONS mentions "Level B … if `M_2` is also loose" without a threshold. |
| certified numerical evidence | **none** for a tight `M_2`. The route is `C2` (same producer gap as K2). |
| formal evidence | Lean `X2` consumes `g_max` as a hypothesis. No numerical `M_2` is formalised. |
| missing | (i) Scientific: a certified non-vacuous `M_2` per `(D,m)` (C2 compute). (ii) **Governance: a frozen, pre-result usefulness criterion.** Without it, "useful" cannot be adjudicated mechanically, and choosing it after seeing a C2 result would be post-hoc. |
| scientific vs governance | Finiteness: discharged (exact theorem). Usefulness: **scientific incompleteness plus a governance definition gap**. |
| **status** | **`K3 = INCOMPLETE`**. The finite half is closed exactly; the frozen "useful" half, as ruled binding by TA, is open. K3 is not closable with no compute unless a governance record supersedes TA's reading. This audit does not create such a record. |
