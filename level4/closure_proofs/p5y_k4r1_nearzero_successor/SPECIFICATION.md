# P5Y-K4R1: near-zero successor certificate (specification, written before any target evaluation)

## Standing

Historical K4 is **permanently** `K4_FROZEN_EXECUTION_R1 = NOT_CLOSED` with disposition `K4_INCONCLUSIVE_K1_RECORDS`:
- checkpoint `95b1fd16` @ `e5cc5a90`;
- execution `bc4ba08e`;
- independent review ACCEPTED.

K4R1 is a new, prospectively frozen successor. It does not repair, re-run or relabel that execution.

## Obligation (unchanged)

For each D ∈ {CUSUM, SR} and m ∈ {1, 2, 3, 5}, R_{D,m}(e) < 0 must hold for every e ∈ (0, 2]. The source is the K4 checkpoint target (P5X-T7(1)). The far-field region e > 2 is not asserted, exactly as frozen in K4.

K4R1 does not change any of the following:
- the detectors, the m scope, the domain, or the handoff at 2;
- strictness;
- any historical K4 decision.

## Residual universe

The universe is `config/RESIDUAL_UNIVERSE.json`: exactly the historical CERTIFICATE_TOO_LOOSE cells.

| m | cells | region |
|---|---|---|
| CUSUM m = 2 | 0–1 | (0, 10187/10⁷] |
| CUSUM m = 3 | 0–2 | (0, 957/625000] |
| CUSUM m = 5 | 0–2 | (0, 957/625000] |

The implementation refuses unless this list equals the hash-bound historical report for every (D, m).

## Certificate (route D3)

The exact formulas and their proof are in `config/GATE.json` → `certificate`. In brief, for each residual m:

```
G = D0.hi − L1·e0²/2                       (≥ R'(0))
T = min( M3(a), U0 + a²/2·M5(a) )          (≥ R''' on [0, a])
B = G + a²/6·max(T, 0)                     PASS iff B < 0   ⇒  R(e) ≤ e·B < 0 for all e ∈ (0, a]
```

### Inputs

All inputs are hash-bound in `config/PROVENANCE.json`:

| Symbol | Source |
|---|---|
| D0 | K1 CUSUM Aux5 cell-0 record `4f8df44c`, entry for m, `D_interval` |
| L1, U0 | slot-1 sealed record `cf90f1ea`, `per_m[m]` (ADOPTED, `84299314`) |
| M3, M5 | T-EXT result `cb97cabc`, row with `x_hi == a`, `M['3'][m]` and `M['5'][m]` (ADOPTED 37/37, `a3547b9b`) |

### Premises

- P5-T3: oddness.
- P5X L5: C^∞, used qualitatively only.

### Semantics

- **Arithmetic:** exact rationals; floats are refused.
- **Endpoints:** the region is (0, a]. e = 0 is not required to satisfy R(0) < 0. The handoff at a goes to the historical K4 cell that starts exactly at a.

## Rules

`config/GATE.json` defines:
- `pass_rule`;
- `science_rule`;
- `assembly_rule`;
- `adoption_rule`;
- `inherited_cells` (never recomputed);
- `budget`: 0 new real addresses and at most 60 CPU-s;
- `execution`: exactly once, locked behind `config/FREEZE.json`;
- `stop_conditions`.

There is no tunable parameter.

## Governance sequence

1. **Candidate commit.** Contains this specification, the gate, the universe, the provenance, the code, the tests, and the qualification evidence (the synthetic suite, the mutation harness, and a value-blind preflight).
2. **Independent pre-result qualification.** A fresh-context reviewer returns exactly one of `QUALIFICATION_ACCEPTED`, `QUALIFICATION_REJECTED` or `QUALIFICATION_BLOCKED`. Anything other than ACCEPTED stops this lineage.
3. **Freeze commit.** `config/FREEZE.json` and `FREEZE_HASH` bind hashes of:
   - the specification, the gate, the universe and the provenance;
   - the code and the tests;
   - the qualification review;
   - every source.
4. **Exactly-once execution** from a clean checkout of the freeze commit, producing `evidence/execution_r1/K4R1_RESULT.json`.
5. **Fresh-context final adjudication:** ACCEPTED, REJECTED or BLOCKED.
6. **Publication.** A closure tag is created only if K4R1_SUCCESSOR_SCIENCE = PASS and the final adjudication is ACCEPTED.

See `FEASIBILITY.md` for the Phase A–C analysis and the pre-result disclosure.
