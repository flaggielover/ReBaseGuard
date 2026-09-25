# C11R — N9 adjudication of the Phase 15 comparison (cell 306)

| item | value |
|---|---|
| adjudicated artifact | `evidence/comparison/C11R_COMPARISON.json`, committed alone in `2c24a98935fee46a07b73f15337191f9045432e1` (C11R_COMPARISON/6, body sha256 `142259bf814641eb38a607beb28c5d69c68935b9708adc753a021bca085bf952`) |
| sealed run | `evidence/runs/C11R_RUNS.json`, seal `5ff4cc5b310b31bc7b61213598aade9a5188964e` (runs body `1e0d82ac…`, file `1552dfa9…`) — EXECUTION_ACCEPTED (`22537709`) |
| protocol chain | approved `ee1a6a8aab8ff57360249bc813a44b3c724200aa` (R8 READY_TO_QUALIFY, `5890511b`); qualification `c06ce377` (QUALIFICATION_ACCEPTED, `445fd84e`); authorization + GRANT `377bbcbb` (AUTHORIZATION_ACCEPTED, `9bd17be5`) |
| frozen authorities used | gate `config/N9R_GATE_C11R.json` (`2d23a8b8…`, frozen before any target run): `SCOPE`, `target`, `forbidden_conclusions`, `permitted_N9_classifications`; statement table `evidence/table/C11R_N9_STATEMENTS.json` (`b937cace…`): `N9_wording`, `DEPENDENCY_FINDING`, `drift_domain`, `original_statements`, `comparison_semantics_frozen_before_results`; comparator `code/c11r_compare.py` (`7065cc6a…`, contract-bound); C2 adjudication and C10 findings on the C2 floor (quoted below) |
| adjudicator | the campaign author (Claude Opus 5.5 via Claude Code), on the user's explicit Phase 15 instruction, 2026-09-25. This is the author's adjudication; an independent comparison review follows it. |

This adjudication reads only the committed comparison artifact, the sealed run's certificate
metadata and the frozen texts. **The first component to interpret the sealed cell-306 values was the
frozen comparator** (one start, `c11r_launch.py compare --approved-commit ee1a6a8a…`,
2026-09-25T06:37:51Z–06:37:56Z, exit 0 = COMPARED) — the first legitimate scientific consumption of
the sealed result. No value below was recomputed by another formula; decimals are renderings of the
exact rationals the comparator emitted.

## 1. What the frozen comparison says (verbatim classes, exact emitted values)

Frozen rule (statement table, frozen before results; factor 2 equal in the table, the contract and
the gate): UPPER_BOUND — STRONGER if independent ≤ original, AGREES if original < independent ≤ 2 ×
original, else INSUFFICIENT; LOWER_BOUND — STRONGER if independent ≥ original, AGREES if original/2 ≤
independent < original, else INSUFFICIENT. "SAME STATEMENT BEFORE SAME NUMBER."

| constant | direction | statement status | independent (C11R, sealed) | original (quarantine) | ratio indep/orig | class |
|---|---|---|---|---|---|---|
| C_T | UPPER | EQUIVALENT | 6.858000000 (exact rational in artifact) | 5.829887954 | 1.176351939 | **AGREES** |
| tau | UPPER | EQUIVALENT | 3429/500 = 6.858 | 5.169819806 | 1.326545268 | **AGREES** |
| Abar | UPPER | EQUIVALENT | 3429/500 = 6.858 | 7.912416712 | 0.866738981 | **STRONGER** |
| D_lo | LOWER | STRONGER | 101/200 = 0.505 | 0.844492286 | 0.597992437 | **AGREES** |
| D1 | UPPER | NO_INDEPENDENT_STATEMENT | — (NOT_IMPLEMENTED) | 0.455295982 | — | **INSUFFICIENT** |
| D2 | UPPER | NO_INDEPENDENT_STATEMENT | — (NOT_IMPLEMENTED) | 5.416355434 | — | **INSUFFICIENT** |

Frozen thresholds and position of each value (derived only by the frozen rule above):
- C_T: STRONGER needs ≤ 5.829887954, AGREES needs ≤ 11.659775908; 6.858 sits inside AGREES.
- tau: STRONGER ≤ 5.169819806, AGREES ≤ 10.339639612; 6.858 inside AGREES.
- Abar: STRONGER ≤ 7.912416712; 6.858 is STRONGER (0.867 × the original).
- D_lo: STRONGER ≥ 0.844492286, AGREES ≥ 0.422246143; 0.505 inside AGREES (0.598 × the original).
- D1, D2: no independent value, hence INSUFFICIENT by the frozen rule ("no certified value").

Guards G8, G10, G19 and the value trace: PASS. Independence violations: none. Opposite-direction
pairs: none. Class counts {AGREES 3, STRONGER 1, INSUFFICIENT 2}.

**Frozen N9 classification by precedence** [INDEPENDENCE_VIOLATION, SCIENTIFIC_DISAGREEMENT,
EXECUTION_INVALID, N9_CLOSED, AGREEMENT_INSUFFICIENT]: **AGREEMENT_INSUFFICIENT.**

## 2. The ten adjudication questions

1. **Was the second certifier genuinely independent in the sense C11R froze?** Yes. The comparator's
   independence predicate (step 12) recorded no violation; no certificate uses the original
   certifier's load-bearing graph (Q5 import scan, the firewall, the contract's certifier hashes);
   the certificates' premises are empty — D_lo is proved from C11R's OWN Khat_e route (F_D), never
   from the original's C_T or tau, as the statement table's DEPENDENCY_FINDING requires.
2. **Same mathematical statement, not an easier scalar-drift surrogate?** Yes for the four certified
   constants: the comparator's statement-equivalence record gives STATUS EQUIVALENT for C_T, tau and
   Abar (domain EQUAL, premises SAME) and STRONGER for D_lo (domain EQUAL, premises FEWER); every
   certificate is a single whole-block certificate over the full drift block at D5/P32
   (`drift_block` equal to the contract's; certificate premises empty; no scalar collapse, no
   sub-interval). No statement exists for D1 or D2.
3. **Correct cell-306 interval?** Yes. The sealed run's drift block is
   [680769/400000, 17885921/10000000] = [1.7019225, 1.7885921], cell 306's own block, in the top level
   and in every certificate's inputs. The adjacent cell-307 interval [1.7885921, 1.882413] was not
   used; the statement table records that the instruction's carry-over of that pair was resolved to
   cell 306 before the freeze.
4. **K and Khat distinguished?** Yes. Abar cites F_K, certified on K_e (atom not removed); C_T and tau
   cite F_H, certified on Khat_e (atom removed); D_lo cites F_D on Khat_e — exactly the frozen citation
   rule (c11r_schema.TARGET_CERTIFICATE).
5. **Abar and tau distinguished?** Yes. They come from two DISTINCT certificates (F_K on K_e, input
   digest `927411e0…`; F_H on Khat_e, input digest `913fa6aa…`), each compared with its own original
   statement. Their independent values are equal (3429/500) because the frozen selector chose the same
   grid weight w = 3429/500 − (1113/1000)·m in both families and that one function is a certified
   supersolution for both kernels; w(atom) = A is then the value of both constants. Equal numbers from
   different certified statements are not a substitution; the originals differ (7.912… vs 5.169…) and
   the classes differ (STRONGER vs AGREES).
6. **All six constants with the correct aggregation directions?** Four of six. The directions were
   applied as frozen (C_T, tau, Abar, D1, D2 upper; D_lo the only lower bound, classified with the
   lower-bound rule). The comparator's equivalence record pairs each original aggregation (max over
   nine sub-blocks for C_T and tau; min over nine sub-blocks for D_lo; a single whole-block
   certificate for Abar) with C11R's single whole-block certificate on the EQUAL domain and accepts
   it as EQUIVALENT or STRONGER. **D1 and D2 were not handled at all**: NOT_IMPLEMENTED by design (DEPENDENCY_FINDING: they
   need drift-derivative kernels, h_1' and h_1'', operator-norm bounds and a residual-to-error
   propagation theorem).
7. **Prospective?** Yes. The gate, the statement table, the comparison rule (factor 2 and both
   directions) and the policy were frozen at the approved commit, before any target run
   (gate `frozen_before`: "any target certification run"); qualification → authorization → one
   execution → seal → comparison followed the frozen lifecycle in order.
8. **Execution accepted?** Yes: EXECUTION_ACCEPTED, no blockers (preserved at `22537709`).
9. **Comparison produced by the frozen comparator?** Yes: one launcher start; producer
   `c11r_compare.py` at its contract hash; all twelve pre-load steps passed; loader called once;
   written once (exclusive create); lifecycle now COMPARED.
10. **Does the evidence satisfy N9 as actually written?** **No.** N9 (C2 adjudication, line 501, as
    frozen in the statement table): *"a second, independently written certifier reproducing the six
    operator constants for cell 306 (closing N9)"*. The frozen gate: N9 closure requires *"all six
    constants for cell 306 classified AGREES or STRONGER"*, and *"if D1 and D2 are not independently
    certified, N9 remains OPEN whatever the other four constants yield"*; it forbids concluding
    *"that N9 is closed while any of the six constants lacks an independent statement"*. D1 and D2
    lack one.

## 3. Verdict

**N9_REMAINS_OPEN.**

The frozen comparison's own classification is AGREEMENT_INSUFFICIENT, and N9_CLOSED was unreachable by
scope in production (comparator docstring: *"D1 and D2 are NOT_IMPLEMENTED, so N9_CLOSED is unreachable
by scope"*). N9 is not weakened, and the historical C11 result stays EXECUTION_INVALID; C11R is a
successor campaign and does not rewrite it.

## 4. Scientific closure vs prospective adoption, kept separate

- **A. N9 statement alignment:** achieved for FOUR of the six constants (C_T, tau, Abar EQUIVALENT;
  D_lo STRONGER; all at the numerical level AGREES or STRONGER). Not achieved for N9 as a whole
  (D1, D2). Per the gate, *"independent same-statement certification of a SUBSET of the six is
  scientific and governance evidence. It is not N9 closure."*
- **B. Frozen scientific closure criterion for cell 306:** **not evaluated by C11R.** C11R's frozen
  comparison computes statement and numerical agreement with the original certifier; it contains no
  K5 closure criterion, and the gate forbids concluding *"that any cell is closed or adopted"*. The
  historical scientific evidence for cell 306 (C3/C5-T) is untouched and not re-adjudicated here.
- **C. Frozen prospective robustness/adoption criterion:** **not satisfied / not reached.** The C2
  adoption floor remains the standard for K5 m = 5 tail adoptions (C2 adjudication, verdict
  Condition 1). Its F1 condition is *"available for as long as N9 … remains open, and lapses when N9
  is closed"* — N9 remains open, so F1 remains live; and the "two independent certifier
  implementations" route for discharging the floor for cell 306 is *conditioned on closing N9*
  (C10) — not reached. The gate forbids concluding *"that the C2 adoption floor may be replaced"*
  and *"that F1 has lapsed"*. No successor floor was frozen before this magnitude was computed, so
  none may be applied now.
- **D. The frozen comparison itself:** AGREEMENT_INSUFFICIENT (per-target: C_T AGREES, tau AGREES,
  Abar STRONGER, D_lo AGREES, D1 INSUFFICIENT, D2 INSUFFICIENT). Recorded by the comparator, not
  inferred from A–C.

## 5. K5 consequence

Outcome **C** of the instruction: N9 remains open. **K5 remains PARTIAL**; **r5 remains
authoritative**; the open m = 5 cells remain {306, 307, 308, 309}; **no successor coverage update is
permitted and no coverage-map r6 is created.**

- **What changed:** for the first time, an independently written certifier has certified four of the
  six N9 constants for cell 306 — C_T, tau, Abar and D_lo — as the SAME block-uniform statements the
  original certifier makes, prospectively, under an accepted qualification, authorization and
  execution, and all four agree with or are stronger than the originals within the frozen factor 2.
  This is sealed, compared and committed evidence.
- **What remains open:** independent certification of D1 and D2 for cell 306 (a later prospective
  derivative-system extension, per the gate's SCOPE); hence N9; hence the C2-floor route for 306 that
  N9 closure would unlock; cells 307, 308 and 309 (untouched: not executed, not compared).
- N9_CLOSED would not by itself have meant K5_CLOSED; the question does not arise.

## 6. Governance classification proposed (final only after the independent comparison review)

**N9_REMAINS_OPEN.** No adoption; no coverage change; r5 authoritative; no r6. Historical verdicts
unchanged: original P8 FAIL, P9 PARTIAL, P8R and P9R CLOSED, P4 PARTIAL, P4Z CLOSED, C11
EXECUTION_INVALID, C2–C10 as recorded; R1–R8 and the qualification, authorization and execution
reviews unchanged.
