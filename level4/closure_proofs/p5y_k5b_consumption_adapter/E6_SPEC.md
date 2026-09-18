# E6: K5-B consumption adapter, specification (written before the adapter code)

## Why this exists

The frozen execution binding `p5y_k5_cusum_first_real_probe_protocol/protocol/EXECUTION_BINDING_R4.json` lists
authorization prerequisite **E6**:

> implement the K5-B consumption adapter and pass its frozen acceptance test (reproduce CUSUM_MINIMALITY_R1 pass sets
> with L = None)

`SCIENCE_PREREGISTRATION_R4.json` (sha256 `9ace6896…`, unchanged by this work) fixes the adapter in its
`k5b_consumption_adapter` block:
- **specification.** Records become cells through the frozen readiness loader `k5_minimality.py` (`load_cells` and
  `record_path`, with the scan field mapping `x_lo, x_hi, rho, e0, R, D, H, M` from
  `R_interval, D_interval, R2_interval, M_R2`). The cells then go to `k5b_check.k5b_literal(cells)`, once per m.
- **acceptance_before_use.** With every L = None, the adapter plus `k5b_literal` must reproduce exactly the per-m pass
  sets of `p5y_k5_order3_readiness_audit/evidence/CUSUM_MINIMALITY_R1.json`. Otherwise POSITIVE consumption is refused.
- **pins.**
  - `k5_minimality.py`: `3a54f0fb290a9b8a07c861653d4399e6c588afdaef77ee51473f778c6c988885`
  - `k5b_check.py`: `ddd54dc469375a2d64352782add8573231be07b94f7246dad83c4e55a2bf35a6`
- **records_source.** Files `aux5_CUSUM_<i>_256.json` for i = 0..309, under the host directory
  `/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records`. Every record's sha256 must equal its entry in
  `COMPOSITE_EXPORT_MANIFEST.json` (sha256 `29ad1f9b…`). The `cells.json` sha256 is pinned. Any mismatch refuses.

This namespace implements that block and nothing more. It is additive. It changes no frozen component, no K1 record, no
preregistration, no executor artifact and no activation object.

`EXECUTION_AUTHORIZED = false` · `REAL_INPUT_ARITHMETIC_GUARD = DENY` · no real R''' or R^(5) exists or is formed here.

## S1. Exact input artifacts

| input | path | sha256 |
|---|---|---|
| frozen loader | `level4/closure_proofs/p5y_k5_order3_readiness_audit/code/k5_minimality.py` | `3a54f0fb290a9b8a07c861653d4399e6c588afdaef77ee51473f778c6c988885` |
| frozen theorem checker | `level4/closure_proofs/p5y_k5b_independent_countersignature/code/k5b_check.py` | `ddd54dc469375a2d64352782add8573231be07b94f7246dad83c4e55a2bf35a6` |
| expected pass sets | `level4/closure_proofs/p5y_k5_order3_readiness_audit/evidence/CUSUM_MINIMALITY_R1.json` | `7feb576b84508c91a79e605fc190ac5da5083662ad9640aea4976c566a0c2a30` |
| cover | `level4/closure_proofs/p5y_k1_cover_ledger_successor/config/cells.json` | `341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f` |
| record manifest | `level4/closure_proofs/p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json` | `29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334` |
| K1 records | host `/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records/aux5_CUSUM_<i>_256.json`, i = 0..309 | each equal to `files["k4_records/aux5_CUSUM_<i>_256.json"]` in the manifest |

The records are the certified CUSUM K1 composite-closure export (published closure `ce7fb933`). Record 0 is also
committed at `p5y_k5b_k1_premise_binding_audit/result_r1/records/aux5_CUSUM_0_256.json` (`4f8df44c…`), equal to its
manifest entry.

## S2. Exact loader and theorem implementation

Both frozen modules are loaded the same way:
1. Read the file bytes once.
2. Require their sha256 to equal the pin.
3. Compile and execute exactly those bytes as a fresh module whose `__file__` is the frozen path.

The same bytes are hashed and run, so no second read can race the check. Neither file is copied, edited or
re-implemented.

- **Loader.** `k5_minimality.load_cells(cells_json, "CUSUM")` gives the ordered cover restricted to the cells meeting
  (0,2]. It already refuses a non-contiguous index set, a cover not starting at x_0 = 0 exactly, or a gap.
  `k5_minimality.record_path(records_dir, "CUSUM", k)` gives each record's path. `k5_minimality.rat` reads cover
  rationals.
- **Theorem.** `k5b_check.k5b_literal(cells)` is called with `mutation=None`, once per m.

## S3. Adapter API

`code/consumption_adapter.py`:
- `consume(L1=None, *, records_dir=HOST_RECORDS_DIR, repo_root=REPO)`
  - Binds the frozen pins, cover, manifest and universe [0, 309] of S1.
  - Returns the result object (S7) or raises `AdapterRefusal`.
- `evaluate(records_dir, cells_json, manifest_path, *, manifest_sha256, cells_sha256, universe, L1=None, components=...)`
  - The same evaluation with explicit bindings.
  - Used only by `consume` and by the synthetic qualification fixtures.
- **`L1`.** Either `None`, meaning L_1 := None for every m, or a dict keyed by exactly `"1", "2", "3", "5"` whose
  values are `fractions.Fraction` or `None`.
  - Floats, bools, ints, strings, extra keys and missing keys are refused.
  - There is no parameter for L_k with k ≥ 2: it is always None (−inf), as `k5b_consumption_map.POSITIVE` requires.

## S4. Field mapping and L = None semantics

For each m in ("1","2","3","5") and each cover cell c in loader order (cell index k = c["index"], k5b row k+1):

| k5b field | source |
|---|---|
| `x_lo, x_hi, rho, e0` | `rat(c["left"]), rat(c["right"]), rat(c["rho"]), rat(c["e0"])` (cover) |
| `R` | `(Fraction(r["R_interval"]["lo"]), Fraction(r["R_interval"]["hi"]))` |
| `D` | `(Fraction(r["D_interval"]["lo"]), Fraction(r["D_interval"]["hi"]))` |
| `H` | `(Fraction(r["R2_interval"]["lo"]), Fraction(r["R2_interval"]["hi"]))` |
| `M` | `Fraction(r["M_R2"])` |
| `L` | `L1[m]` for the first cell (k = 0), `None` for every other cell |

Here `r = record["m"][m]`.

- **L = None** is the frozen `k5b_literal` reading of −inf: no L_1 pass, `gamma_1` unbounded, and `mu_k = ell_k = H_k.lo`.
- **Pass set of m.** It is `{k : rows[k]["pass"] is True}`, so row i of `k5b_literal` is cell index i.
- **Expected set.** It is `expand(CUSUM_MINIMALITY_R1.per_m[m].closed_by_k1)` (S6).

## S5. Missing or invalid records: fail closed

The adapter raises `AdapterRefusal`, and returns no partial result, if any of the following holds:
- a frozen pin is not matched;
- the manifest or cover sha256 differs from its binding;
- the loader universe is not exactly `universe`;
- a record is missing, or is a symlink out of `records_dir`;
- a record's sha256 differs from its manifest entry;
- a record does not name `detector == "CUSUM"` and `cell_index == k`;
- a record's `e0` or `rho` differs from the cover (the loader's own geometry rule);
- an m entry or field is missing, or a value is not an exact rational string;
- `k5b_literal` raises;
- the number of rows differs from the number of cells;
- `L1` is invalid.

Records are read, never written.

## S6. Expected pass sets and the comparison rule

Frozen here, copied from `CUSUM_MINIMALITY_R1.json` (`closed_by_k1`):

| m | expected pass set | count |
|---|---|---|
| 1 | 133..309 | 177 |
| 2 | 145..309 | 165 |
| 3 | 146..309 | 164 |
| 5 | 149..304 | 156 |

**Acceptance** runs `consume(L1=None)` on the S1 inputs. For every m:
- `OBSERVED[m] == EXPECTED[m]` as sets of integers;
- `FALSE_POSITIVES[m] = OBSERVED − EXPECTED = ∅`;
- `FALSE_NEGATIVES[m] = EXPECTED − OBSERVED = ∅`.

The acceptance harness reads the expected sets from the evidence file and requires them to equal the table above.
This criterion is not weakened after the result is seen.

## S7. Output schema and deterministic ordering

The schema is `rebaseguard.p5y.k5b.consumption-adapter.result.v1`, with these fields:
- `detector`
- `universe` ([lo, hi])
- `cell_count`
- `m_values` (in the order "1","2","3","5")
- `L1` ({m: null | "p/q"})
- `L_k_ge_2` (always null)
- `per_m[m]`:
  - `pass` (a strictly increasing list of cell indices)
  - `pass_ranges`
  - `pass_count`
  - `open_ranges`
  - `open_count`
  - `rows_sha256`: sha256 of the canonical JSON of the `k5b_literal` rows, with every Fraction written as `"p/q"`
    and None as null
- `inputs`:
  - `manifest_sha256`
  - `cells_json_sha256`
  - `records_sha256`: sha256 of the canonical JSON `{index: record sha256}`
  - `record_count`
- `components` ({file: sha256})
- `adapter_sha256`

Canonical JSON is `sort_keys=True, separators=(",", ":")`. Two runs on the same inputs are byte-identical.

## S8. Provenance

Acceptance runs on rebaseguard-vultr-02 from a clean detached checkout of the implementation commit. The evidence
records the following, and every item is re-checked:
- the git commit and an empty porcelain, at start and at end;
- host and Python version;
- the adapter, harness and cross-check sha256 values;
- the component pins;
- the manifest, cover, evidence and record hashes, before and after the run (the originals must be unchanged).

## S9. Independent cross-check (not the adapter twice)

`code/crosscheck.py` is written separately from the adapter. It shares no function with the adapter and uses two
paths:
- **X-A: frozen reproduction.** `k5_minimality.verify(CUSUM_MINIMALITY_R1, records, cells)` re-runs the frozen
  readiness scan from the records. It must reproduce the committed evidence exactly (problems = []). This path never
  calls `k5b_literal`.
- **X-B: own addressing.**
  - Records are addressed through the manifest keys (not `record_path`), and each is sha-checked.
  - The cover is built from `cells.json` by its own filter and sort (not `load_cells`).
  - Cells are fed to the frozen `k5b_check.k5b_readiness_variant`, a separately written recurrence.
  - The resulting per-m pass sets must equal EXPECTED and the adapter's sets.
  - Every per-cell `Gamma` must equal the `Gamma` string of the same cell in the R1 `boundary_rows`. This detects an
    index or address shift.
  - Every `H.lo <= 0`, which is the premise under which the countersignature shows the variant equals the literal
    theorem.

No new mathematical rule is introduced: both paths are frozen implementations of the same frozen theorem.

## S10. Mutation and adversarial tests (each must be detected)

A mutant is **detected** when the acceptance evaluation does not reach ACCEPTED. The harness records why: a refusal, a
set mismatch, a synthetic differential mismatch, an ordering or determinism failure, or a static fence failure.

| id | mutation | kind |
|---|---|---|
| M01 | off-by-one cell indexing (row i reported as cell i+1) | adapter source |
| M02 | final cell dropped | adapter source |
| M03 | a cell duplicated | adapter source |
| M04 | wrong detector (SR) | adapter source |
| M05 | wrong m (m read from the next m's entry) | adapter source |
| M06 | wrong L = None handling (None replaced by 1) | adapter source |
| M07 | reversed inequality (non-passing rows reported) | adapter source |
| M08 | wrong K1 record (record 200 replaced by record 201's bytes) | input |
| M09 | stale manifest (a manifest whose bytes differ from the pin) | input |
| M10 | missing record (record 309 absent) | input |
| M11 | modified frozen loader (one byte appended) | input |
| M12 | modified `k5b_literal` (strict < made non-strict in the source) | input |
| M13 | result-dependent branch (return the R1 sets when every L is None) | adapter source |
| M14 | non-deterministic ordering (pass list shuffled) | adapter source |

Source mutants are exact, single-occurrence text replacements of the adapter. A replacement that does not match
exactly once is a harness error, not a detection. Input mutants use scratch copies under `/var/tmp/e6scratch`, which is
removed afterwards; the original records are never written.

**Synthetic differential.** Deterministic fixtures from the frozen generators `k5b_check.make_cover`,
`synthetic_cells` and `random_odd_poly` (fixed seed, only fixtures where every H.lo <= 0) are written as records, a
cover and a manifest. The adapter's pass sets must equal the frozen `k5_minimality.scan` on the same fixture. This is
what exposes M13, whose output on the real inputs would look correct.

**Static fences on the adapter source.**
- It must not reference the evidence file or its keys (`CUSUM_MINIMALITY`, `closed_by_k1`, `needs_order3`).
- It must not reference any real-probe output (`k5-first-real-probe`, `SCIENTIFIC_RECORD_SEALED`, `slot-`, `L0`,
  `U0`, `L1_m`, `U1`, `R3`, `R5`).
- It must not use `float(`, `random` or `time`.
- It may import only the standard library and the two frozen components.

## S11. Gates

| gate | requirement |
|---|---|
| G01 | preconditions: guard DENY; no AUTHORIZATION_ACTIVE, COUNTERSIGNATURE_ACTIVE, ledger or amendment; real namespace absent; component pins match |
| G02 | inputs bound: manifest and cover pins; all 310 record sha256 equal the manifest; unchanged after the run |
| G03 | acceptance: OBSERVED == EXPECTED for every m; FP = FN = ∅ |
| G04 | determinism: two separate processes (different PYTHONHASHSEED) give byte-identical results |
| G05 | independent cross-check X-A and X-B PASS |
| G06 | synthetic differential PASS |
| G07 | all mutants M01–M14 detected |
| G08 | static fences PASS |
| G09 | fail-closed unit rows: invalid L1 types, extra or missing m keys, missing field, symlinked record, wrong universe |

**Verdict.** `E6_K5B_CONSUMPTION_ADAPTER = ACCEPTED` requires all gates G01–G09 to pass. Otherwise it is FAILED, and
POSITIVE consumption stays refused.

## S12. Prohibitions

The adapter has no path to any real-probe output. L_1 is its only order-3 channel. Acceptance runs only with
L = None, and no test uses a real R''' value.

Nothing in E6 does any of the following:
- reads, forms or observes a real R'''(0), R^(5), L0, U0, L1 or U1;
- creates an activation object or a LAUNCH_NOTICE;
- creates slot-1;
- launches the executor;
- changes the guard.

Binding the adapter into `EXECUTION_BINDING_AMENDMENT.json` (as `consumption_adapter_entry`, with the frozen pins) is
a later, separate step, and is not part of E6.
