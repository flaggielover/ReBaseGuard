# K5-B to K1 premise-binding audit: plan only, not executed

K5-B is countersigned (`d7d3c08b`, `PASS_WITH_SCOPE_LIMITATION`). That review checked the theorem's logic *given*
its premises. This audit asks a separate question: **do those premises hold for the exact K1 objects K5-B would
consume?**

```text
B3_K5B_NOT_INDEPENDENTLY_COUNTERSIGNED = CLOSED_BY_SESSION_INDEPENDENT_COUNTERSIGNATURE
    scope limitation: the reviewer was a separate Claude session, not a human and not a different model family
PREMISE_BINDING_AUDIT                  = PLAN_ONLY_NOT_EXECUTED
REOPENS_B3                             = NO, under every outcome
```

| id | Question (carried over from F2–F6) | Reads |
|---|---|---|
| PB2 | Does P5X `L5` give C³ regularity on every cell meeting `(0,2]`, including `e = 0` and the part of the cell containing 2 that lies beyond 2? L5 is recorded as "nothing certified depends on it" but is now load-bearing. Has it had independent review? | docs |
| PB3 | Does `R'(0) = 1 − Γ̃` hold with the sign and normalisation of the raw-variable `R` that K1 encloses (no `+e`)? | docs (an optional record check needs separate owner approval) |
| PB4 | Is the K1-enclosed function exactly H3a's `R_{D,m}`? Same parameters, `m` convention, domain and assembly | docs + frozen config |
| PB5 | Is `R2_interval` in the **Aux5** closure records a whole-cell enclosure of `R''`? Those records came through `aux_propagate` and `AuxiliaryRefinement`, not `propagate.py` | code + manifests |
| PB6 | Which certified object gives `R(2) > −2` for every `m`? Is it `target_gate` on the cell containing 2, rather than the far-field splice? Is PASS required by the closure verdict? | code + closure config |

**Verdicts:**
- `BOUND`, `BOUND_WITH_NOTE`, `UNDETERMINED`: no new blocker.
- `NOT_BOUND`: recorded as a new premise-binding blocker against using K5-B on K1 inputs for that detector. It
  does not reopen B3.

**Constraints:** read-only. No scientific computation, no producer execution, no K1 record access (except PB3's
optional check with separate approval), no AWS/PS1 access, no edit to any existing artifact.

The full method per question and the sha256 pins at `d7d3c08b` are in `config/AUDIT_PLAN.json`.

```bash
python3 -B level4/closure_proofs/p5y_k5b_k1_premise_binding_audit/tests/test_plan.py
```
