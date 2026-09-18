# E6 K5-B consumption adapter: result

**`E6_K5B_CONSUMPTION_ADAPTER = ACCEPTED`.**

The adapter composes the frozen readiness loader `k5_minimality.py` with the frozen countersigned
`k5b_check.k5b_literal`. On the certified CUSUM K1 records 0–309 with L = None, it reproduces the CUSUM_MINIMALITY_R1
pass sets exactly for every m. All acceptance gates G01–G09 pass, and the read-only `check` reports 0 problems.

No real order-3 result exists or was observed:
- no sealed record, activation object, ledger, amendment or real namespace exists in any history or on the host;
- the E6 obligation was frozen on 2026-09-17 (protocol r2 `c4716a88`, carried into r4 `852b2d65`), before any real
  order-3 observation, and none has happened since.

`EXECUTION_AUTHORIZED = false` · `REAL_INPUT_ARITHMETIC_GUARD = DENY` · `REAL_CELL_EXECUTED = NO` ·
`REAL_R3_VALUE_OBSERVED = NO` · `REAL_R5_VALUE_OBSERVED = NO` · `SCIENTIFIC_K5_PROBE_RUN = NO`

## Commits and hashes

| item | value |
|---|---|
| **E6_SPEC_COMMIT** (spec + frozen acceptance protocol, before code) | `8635b1b7` |
| **E6_IMPLEMENTATION_COMMIT** | `a2bb280d` |
| **E6_ACCEPTANCE_COMMIT** | this commit (evidence `evidence/acceptance_r1/`) |
| ADAPTER_SHA256 (`code/consumption_adapter.py`) | `fbad7d33261fd47fc56c034d6a016f8427b81b51f9199f0e3a8f3e74df35973d` |
| cross-check sha256 (`code/crosscheck.py`) | `3d5447b0a2dcd6ef0cad747167aa4323bdc4a5ff4d214c90f0ef47c807690389` |
| harness sha256 (`code/acceptance.py`) | `072d9fbdd30954c71e1795123d6e39a421eb250235edc0f52981f16a1d0b36d1` |
| ACCEPTANCE_PROTOCOL_SHA256 | `bbd655cbfe48de43494bcc9d9eae9f0f4649965b3f6148a0c7bfff616916f64f` |
| ACCEPTANCE_RESULT_SHA256 | `0a35e0f2101e5927b69b88082028e21a08a721b73082ce001ce48c351a31376f` |
| adapter output sha256 | `d4c315d6f150c9ed676a0ad6bfed62ff182025580b441777aee270320fd6c0f7` |
| PROVENANCE.json sha256 | `8a85327ffca624a5e220d16a7f975cb36648b8d9e3a231f7fdabe632794c4611` |
| LOADER_SHA256 (`k5_minimality.py`, frozen pin) | `3a54f0fb290a9b8a07c861653d4399e6c588afdaef77ee51473f778c6c988885` |
| K5B_LITERAL_SHA256 (`k5b_check.py`, frozen pin) | `ddd54dc469375a2d64352782add8573231be07b94f7246dad83c4e55a2bf35a6` |
| record manifest (`COMPOSITE_EXPORT_MANIFEST.json`) | `29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334` |
| records sha256 (canonical `{index: sha256}` of records 0–309) | `76fc2af5023f222e51b75e2a92e29a3d80ec84dab26057c2c9ae6ea549e96f51` |
| cover (`cells.json`) | `341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f` |
| expected evidence (`CUSUM_MINIMALITY_R1.json`) | `7feb576b84508c91a79e605fc190ac5da5083662ad9640aea4976c566a0c2a30` |

## Acceptance (L = None, CUSUM cells 0–309, CELL_COUNT = 310)

| m | EXPECTED_PASS_SET | OBSERVED_PASS_SET | FALSE_POSITIVES | FALSE_NEGATIVES |
|---|---|---|---|---|
| 1 | 133–309 | 133–309 | {} | {} |
| 2 | 145–309 | 145–309 | {} | {} |
| 3 | 146–309 | 146–309 | {} | {} |
| 5 | 149–304 | 149–304 | {} | {} |

## Gates

The run used a clean detached checkout of `a2bb280d` on rebaseguard-vultr-02 (Python 3.13.5). Porcelain was empty at
start and at end, and the scratch area was empty afterwards.

| gate | result |
|---|---|
| G01 preconditions | PASS: guard DENY; no AUTHORIZATION_ACTIVE, COUNTERSIGNATURE_ACTIVE, ATTEMPT_LEDGER or amendment; `/root/work/k5-first-real-probe` absent at start and end; pins match; preregistration `9ace6896…` unchanged |
| G02 inputs bound | PASS: all 310 record sha256 equal the manifest; manifest, cover and evidence hashes are unchanged after the run |
| G03 acceptance | PASS: exact set equality for every m |
| G04 determinism | PASS: two processes (PYTHONHASHSEED 1 and 2) give byte-identical output |
| G05 independent cross-check | PASS (see below) |
| G06 synthetic differential | PASS: 6 deterministic fixtures from the frozen generators; the adapter equals the frozen scan for every m |
| G07 mutations | PASS: 14/14 detected |
| G08 static fences | PASS |
| G09 fail closed | PASS, 13 rows: every invalid L1 type or key set, a missing field, a symlinked record, changed record bytes, a wrong universe and a wrong cover binding are refused, and an exact positive L1 passes cell 0 (synthetic only) |

**Cross-check.** Two paths, each independent of the adapter:
- **X-A.** The frozen `k5_minimality.verify` re-runs the readiness scan from the records and reproduces
  CUSUM_MINIMALITY_R1 exactly (problems = []).
- **X-B.** Records are addressed through the manifest keys, and the cover is built independently. The frozen
  `k5b_readiness_variant` gives pass sets equal to both the expected sets and the adapter's. Every boundary-row
  `Gamma` matches the same cell in R1. Every H.lo ≤ 0, which is the premise under which the variant equals the literal
  theorem.

**Mutations (each detected):**

| mutant | detected by |
|---|---|
| M01 off-by-one indexing | acceptance comparison and synthetic differential |
| M02 final cell dropped | acceptance comparison and synthetic differential |
| M03 cell duplicated | refused: row count differs from cell count |
| M04 wrong detector | refused: universe differs |
| M05 wrong m | acceptance comparison and synthetic differential |
| M06 wrong L = None handling | acceptance comparison and synthetic differential |
| M07 reversed inequality | acceptance comparison and synthetic differential |
| M08 wrong K1 record | refused: manifest mismatch |
| M09 stale manifest | refused: manifest binding |
| M10 missing record | refused |
| M11 modified loader | refused: pin |
| M12 modified `k5b_literal` | refused: pin |
| M13 result-dependent branch | synthetic differential and static fence |
| M14 non-deterministic ordering | acceptance ordering, determinism, synthetic differential and fence |

## Preservation

Nothing below was modified. The E6 namespace is additive.
- R1–R5 executor artifacts;
- the science preregistration;
- the K1 records (read only, hashes checked before and after);
- the K5-B theorem and countersignature;
- the CUSUM closure;
- AWS PS1 and origin/main;
- `k5_minimality.py` and `k5b_check.py`.

The adapter still has to be bound as `consumption_adapter_entry` in a later `EXECUTION_BINDING_AMENDMENT.json`. That
step is separate and not part of E6.

## Next step

`REPEAT_INDEPENDENT_EXTERNAL_AUTHORIZATION_REVIEW`.
