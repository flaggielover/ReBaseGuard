# K5 Campaign C1 — certified operator-only registry extension over the CUSUM m = 5 tail (cells 305–309)

Additive namespace. Start: `p5y-postk1-frontier` at `76c37de1`. Nothing outside this namespace is modified; AWS
SR/PS1 untouched; `main` untouched. **NEW_REAL_ADDRESSES = 0, NEW_REAL_CPU_HOURS = 0**, guard DENY throughout.

| phase | where | state |
|---|---|---|
| gate (frozen **before** any forecast, at `36d8e39b`) | `config/FEASIBILITY_GATES_C1.json` (`927ecfc7…`) | frozen, unmodified |
| A. authoritative-input verification | `code/c1_inputs_verify.py`, `evidence/phase_a/` | 7/7 PASS |
| B. tail operator certification | `code/c1_tail_registry.py`, `evidence/registry_c1/` | **5/5 cells certified**, 1232.2 CPU-s |
| B. forecast and classification | `code/c1_forecast.py`, `evidence/forecast_r1/` | **MARGINAL** |
| adversarial suite | `code/c1_mutations.py`, `evidence/prefreeze/` | 24/24 (20 real mutants, 4 static assertions, 1 equivalent with proof) |
| independent pre-freeze review | `review/REVIEW_C1_PREFREEZE.md` | **NOT_READY** (37 PASS / 11 INFO / 3 NOT_CHECKABLE_LOCALLY / 6 FAIL); repairs applied |
| C. execution decision | `phase_c/C1_EXECUTION_DECISION.md` | **STOPPED before freeze** by the frozen `stop_rule` |
| notes N1 / N3 / N5 and the (P3′) repair | `OPEN_NOTES_DISPOSITION_C1.md` | dispositioned |

K5 remains **PARTIAL** (m = 5 open on 305–309). Coverage map r4 (`a3bddd83…`) is untouched and **no r5 exists**.

## What C1 found

The operator extension certified all five tail cells at the first rung of both pre-registered ladders. The result is
scientifically negative and that is its value:

- **Atom deflation buys 1.10–1.13× on A0 at the tail, not the 2.46× the e = 0 precedent suggested, and it makes A2
  worse by 1.25–1.36×.** Theorem AD §3 predicted this — the gain lives in cross terms where the generic stack
  multiplies copies of C, and at the tail C_upper is already only 5.78–7.73. Campaign B's continuation estimate was
  wrong by a factor of ≈ 2.2, and this is now measured rather than guessed.
- Cells 305 and 306 close under the certified constants; 307, 308 and 309 reach 0.815× / 0.643× / 0.529×.
- The remaining uniform atom-constant reduction needed falls from 2.252903 to **2.101597** — a **6.716 %** fall
  against the gate's 10 % threshold, so the frozen material-improvement test **fails** and the class is **MARGINAL**.
- `Ā` is **inert**: Ā_eff = τ/D_lo on all five cells, so the whole-kernel ARL supersolution — about half the build
  cost — feeds nothing. A successor should spend on τ, D_lo and D2, not on Ā.

Nothing is adopted: at MARGINAL the frozen selection rule forbids execution, so there is no freeze, no seal, no
adjudication and no coverage-map change. The costed C2 plan is `phase_c/C1_EXECUTION_DECISION.md` §4.

## The pre-freeze review, and the defect it caught

The first evaluation reported the material-improvement test as a 16.1 % fall and the class as **USEFUL — EXECUTE**.
The independent fresh-context reviewer found that the test was computed on a different quantity than the gate states:
the gate's baseline is a **uniform atom-constant** reduction factor, the code used a **magnitude** ratio. On the
gate's own quantity the fall is 6.716 %, and the verdict is STOP. The gate text was not touched; the code was
corrected to match it — the only direction a gate repair may take.

Five further FAILs were repaired: the adopted taboo certifier is now pinned and **enforced** (the control had been
claimed but not implemented); the ARL alpha ladder's provenance is stated accurately; the adversarial suite now
separates real mutants from static assertions and **covers the gate-evaluation path**, which no mutant had touched —
exactly where the defect sat; and the specification's constants table and thin-cell paragraph are corrected against
the registry.
