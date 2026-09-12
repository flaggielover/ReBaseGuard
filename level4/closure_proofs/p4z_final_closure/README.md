# P4Z final closure packet

**Additive. It stores no result data, modifies no scientific artifact, and ran
no numerical computation.**

```text
P4                      PARTIAL                        historical, immutable
P4Z                     CLOSED                         successor closure
P4_SCIENTIFIC_LINE      CLOSED_BY_LATER_SUCCESSOR

NEW_NUMERICAL_COMPUTE   NONE
```

> **`P4 = CLOSED` is not asserted here and is not implied.** P4's own recorded
> verdict is `PARTIAL` and stays `PARTIAL`. A successor continues a line; it
> never converts an earlier campaign's verdict into a pass. P4X keeps its
> historical governance-failure outcome and is **not** rehabilitated as a
> campaign; P4Y stays `NOT_FEASIBLE`.

## What closed, and on what

The frozen P4 theorem G1a was recorded `PARTIAL` with three preregistered gates
false. All three are now discharged by admissible later evidence:

| original P4 gate | discharged by |
|---|---|
| `all_theorem_supported_cells_pass` | P4Z → P4ZA → P4ZB, **96/96 `COVERED_PASS`**, 0 FAIL, 0 INCONCLUSIVE |
| `all_outside_assumption_cells_demonstrate_failure` | P4X obligation **C4** under obligation-local Rule C |
| `gaussian_consistency_with_closed_core` | P4X obligation **C5** under obligation-local Rule C |

At its strictest — every cell re-decided on Monte Carlo error alone, with the
successor-added `T_B` term removed, which can only raise `|z|`:

```text
96 / 96 pass
worst |z|                    1.7876746141   frozen limit 4.0
worst relative discrepancy   0.0094996044   frozen limit 0.03
```

No final disposition depends on any successor-added uncertainty convention.

## Files

| file | what it is |
|---|---|
| `FINAL_ADJUDICATION.md` | the reasoned verdict, the three-status distinction, B1–B4, residual uncertainty |
| `EVIDENCE_MAP.md` | where every load-bearing claim lives, by branch / commit / tree / SHA-256 / path |
| `final_closure.json` | machine-readable verdict; **authoritative** if it and the prose disagree |
| `MANIFEST.json` | every evidence pin, derived from the repository |
| `gate_discharge.json` | the three-gate map with per-obligation Rule-C findings |
| `build_manifest.py`, `build_closure.py` | re-derive the above from the repository |
| `tests/` | consistency, pin, protected-tree and status-string checks |

`MANIFEST.json` deliberately carries **no hash of itself** — its integrity comes
from the commit containing it, and a test asserts the self-hash field is absent.

## Four campaign-level records this packet keeps distinct

1. **P4's historical verdict** — `PARTIAL`, immutable.
2. **Each successor stage's own self-verdict** — P4Z
   `P4Z_NUMERICAL_PASS_AWAITING_FORMAL_OR_GOVERNANCE`, P4ZA `P4ZA_INCONCLUSIVE`
   (four cells left open rather than widening the frozen K7 limit), P4ZB
   `P4ZB_CLOSED`. Retained verbatim.
3. **The independent integrated adjudication** — `P4Z = CLOSED`. This packet.
4. **The scientific line** — `CLOSED_BY_LATER_SUCCESSOR`.

`P4ZB_CLOSED` is a campaign self-verdict. `P4Z = CLOSED` is the independent
adjudication. They are different statements by different authors and the record
keeps both.

## Known defects carried on the record, not erased

- **P4Z RNG address overlap.** 5 same-campaign calibration/production overlaps
  across 25 shared addresses; on three of them the delivered innovations were
  byte-identical. Admissible because **zero disposition-bearing final cells rely
  on overlapped P4Z evidence** — both affected configurations are authored by
  P4ZA at disjoint addresses. Full record:
  `../p4zr_rng_provenance_repair/RNG_ADDRESS_SEPARATION.md`.
- **P4ZA seed-namespace reuse.** One integer keying Philox in calibration and
  PCG64 in production — no shared innovation stream, but bookkeeping that cannot
  tell the two roles apart.
- **P4ZB** is clean on both axes.
- **K7 diagnostic redesign.** The statistic changed three times, each version
  frozen before its own run, with no frozen threshold ever moved. The adaptive
  development history is preserved, not rewritten.

Residual uncertainty — including that no counterfactual disjoint-address
campaign was reconstructed — is listed in `FINAL_ADJUDICATION.md` §5 and in
`final_closure.json`, and is **not** discharged by this packet.

## Scope

```text
IN SCOPE      the frozen P4 theorem G1a, its 96 theorem-supported cells,
              and P4's three originally failed gates

OUT OF SCOPE  P5, P5Y, K1, PS1, Level-4 global closure, novelty,
              production readiness, and any claim beyond the frozen scope
```

## Reproduce

```bash
python3 build_manifest.py
python3 build_closure.py
python3 -m pytest tests/ -q
```
