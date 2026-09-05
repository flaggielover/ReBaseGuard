# Repair 2 status

    REPAIR2_VERDICT             = REPAIR2_READY_FOR_INDEPENDENT_ADJUDICATION
    BASE                        = 41641218363f2c8b2bf14a571eecc193ae271fc2 (Repair1)
    PRODUCER_IMPLEMENTATION_HASH= f703921b045f39092d9bdf67d02927f70961dd344dc3be50d17aab0b23df16bd
    BACKEND_CONTRACT_HASH       = 495058e3e1635615ff2ee39d2ae5b4299e732b7350e25805aed789ff59a9a1ea
    REVIEWED_PARENT_HASH        = 44f5417bdbba87fd34ff1d161fa307b3236bf7f55ea9b27cb12ddd5681938155
    WORK_UNIVERSE               = reserved for independent adjudication
    PRODUCTION_READY            = false
    IMPLEMENTATION_COMPLETE     = false
    COST_CAP_STATUS             = NOT_ESTABLISHED
    SCIENTIFIC_VERDICT_CHANGED  = NO

--------------------------------------------------------------------------
## A. Repair1 defect reproduction (Phase 0)

Nothing in the repository was mutated: Repair1's certifying bytes were copied
to a scratch tree and altered there, and Repair1's own hash functions applied.

**Control A -- the stamped hash is blind to the producer.**

```text
Repair1 evidence stamps           44f5417bdbba87fd...   (implementation_hash)
Repair1 evidence stamps           44f5417bdbba87fd...   (backend_hash)
universe.implementation_hash()    44f5417bdbba87fd...   -> identical
files that function hashes        13, all in the reviewed namespace
Repair1 producer modules among them                     none
mutate repair_layer2.ROUNDING_SLACK in a scratch copy   stamp UNCHANGED
same change against the Repair2 manifest                hash CHANGES
```

**Control B -- source hashes are identity-only.**

```text
Repair1 source_certificate_hashes[dep]
    == sha256(canonical(_base_identity(dep)))            exactly
change the consumed F_2 certificate content              hash UNCHANGED
same change under Repair2                                certificate hash CHANGES
                                                         parent hash CHANGES
                                                         chain verification REJECTS
```

Both controls are committed as tests and pass.

--------------------------------------------------------------------------
## B. Producer implementation identity (Phase 1)

`producer.producer_manifest()` -- deterministic `path -> sha256`, canonically
ordered, no timestamps, no worktree noise -- over **38 certifying inputs**:

```text
6   Repair2 certifying modules
5   Repair1 modules actually executed
13  reviewed-implementation modules actually executed
6   frozen successor inputs (checkpoint, cells, witnesses, record schema,
                             ERROR_ALGEBRA.md, algebra.py)
8   certified backend contract (rebaseguard_certify, ra_certifier,
                                raw_certifier, fast_range)
+   generation parameters: Taylor order, degree, quadrature, scale bits,
    subdivision depth, W indices, precision, m values, pinned python-flint
```

`producer_hash()` is the canonical hash of that manifest. It is **not** a Git
commit id. Reporting and self-audit modules are deliberately out of scope --
they cannot change a certified value.

Enforced by tests: determinism; canonical ordering; mutating **any** of the 38
inputs or any generation parameter changes the hash; documentation and
diagnostics are excluded; the parent hash alone is rejected; a stale producer
hash is rejected; `verify_loaded_modules_covered()` catches an executed but
unhashed repo-local module.

--------------------------------------------------------------------------
## C. Source certificate hashes (Phase 2)

```text
certificate      = { schema, identity, certified, status }
certificate_hash = sha256(canonical(certificate))
```

`identity` carries the producer hash and the dependency certificate hashes, so
binding is recursive. `certified` is the obligation's real content: residuals
and eps nodes for objects; the order-1 h/S chain and finite powers for the
bundle; the order-2 jets, refinement and `M_R2` for curvature; the intervals,
cover charge with children, top-level and nested gates, target gate and status
for an assembly.

Excluded, and asserted excluded: `cpu_seconds`, call counts, `peak_rss_kib`,
threading, timestamps. A certificate re-emitted on a busier machine hashes the
same; a certificate with different certified content never does.

--------------------------------------------------------------------------
## D. Chain integrity and substitution attacks (Phase 3)

Certificates are built bottom-up in a dependency-respecting order, then
verified recursively. All twelve attacks reject:

```text
modified certified interval          REJECT
modified error bound                 REJECT
different producer hash              REJECT
certificate from another cell        REJECT
certificate from another m           REJECT
certificate from another shard       REJECT
dependency omitted                   REJECT
extra dependency inserted            REJECT
dependency hashes mispaired          REJECT
forged metadata, wrong content       REJECT
non-leaf presenting an empty map     REJECT
leaf declaring a dependency          REJECT
```

Benign JSON key reordering is **accepted**: the canonical serialisation sorts
keys, so a reordered record is the same bytes and the same hash. Rejecting on
Python insertion order would reject a semantically identical record.

--------------------------------------------------------------------------
## E. Record / resume identity (Phase 4)

Admission binds obligation identity **and** evidence provenance: all 18
identity fields, a recomputed `unit_hash`, the Repair2 producer hash, the
`implementation_hash_kind` discriminator, and `source_certificate_hashes`
recomputed from the dependency certificates actually on hand.

```text
Repair1 record admitted as Repair2   REJECT (no Repair2 kind; parent hash)
old 12,255 universe                  REJECT
superseded parent checkpoints        REJECT
any single identity field mutated    REJECT (18 fields)
forged self-consistent unit_hash     REJECT
float in an exact field              REJECT
absent dependency certificate        REJECT
benign JSON reordering               ADMIT
```

--------------------------------------------------------------------------
## F. Representative provenance replay and regression (Phase 5)

`diagnostics/regression/`, `diagnostics/PROVENANCE.md`.

```text
CUSUM cell 221, m = 1,2,3,5, 256 bits, full frozen dependency graph
  obligations certified            28
  chain units verified             28 / 28
  leaf obligations                 CUSUM|221|object|h_1, CUSUM|221|object|S_0
  leaf source maps                 exactly empty
  non-leaf example  dF_2 consumes  dependency_bundle|orders_0_1, object|F_2

CUSUM cell 221, m = 1, SCOPED      NOT_A_CERTIFICATE, 0 obligations
  (the frozen dependency bundle is not computed on that path, so the run
   discharges no obligation and Repair2 refuses to certify it)
```

Scientific regression against Repair1, cell 221:

```text
mag(D_interval) delta = 0   M_R2 delta = 0   B_cover delta = 0
R_intervals identical       all statuses PASS -> PASS
S0 remainder charged exactly once, representation A   (DERIVATIVE_DEPENDENCY_SOUND)
h_2:0 = 1.831353e-06        S_1:0 = 2.764060e-06
DAG audits: 0 duplicate edges, all derivative edges on B_cover
```

Cell 325 was not run; `repair2_qualify` refuses it by construction.

--------------------------------------------------------------------------
## G. Tests (Phase 6)

| suite | result |
|---|---|
| repair2 | **76 passed** |
| repair2 pre-repair mode | 9 passed (documents Repair1's defects) |
| repair1 | **52 passed** |
| reviewed implementation | **102 passed** |
| CUSUM kernel | 18 passed |
| production driver | 25 passed |
| frozen successor | 24 passed, **2 failed** (known guard conflict) |
| `git diff --check` | clean |

The 2 frozen failures are the documented freeze-time guard conflict:
`audit.protected_check()` diffs START_HEAD against the worktree and rejects any
differing path outside its own namespace, so it fails for any commit made
anywhere after the freeze. The frozen tree is byte-identical to its freeze
manifest. Not a mutation, not caused by this repair.

Two `writes_only_inside_its_own_namespace` tests in Repair1 and the reviewed
implementation fail only while Repair2 is uncommitted and clear on commit;
neither namespace may be edited, so this is reported rather than changed.

--------------------------------------------------------------------------
## H. Self-audit (Phase 7)

`manifests/repair2_self_audit.json` -- 19 checks, 0 failed:

```text
frozen_successor_byte_preserved         reviewed_implementation_byte_preserved
repair1_byte_preserved                  S0_double_charge_remains_fixed
producer_hash_covers_certifying_code    producer_hash_distinct_from_commit_ids
loaded_modules_covered                  source_hashes_cover_certificate_content
exact_dependency_chain_replay_passes    substitution_attacks_all_reject
work_universe_17978_unchanged           shard_conservation_unchanged
precision_unchanged                     cap_remains_1126
budgets_unchanged                       production_off
SR_absent                               far_field_absent
cell_325_unresolved
```

--------------------------------------------------------------------------
## I. Remaining unresolved

```text
SR raw DAG absent                    (316 of 642 cells, 8,850 obligations)
SR M_R2 absent
SR all-m absent
far-field not implemented            (2 obligations)
cell 325 CURRENT_CERTIFICATE_FAILURE_ONLY   (m = 2, 3, 5)
full cost cap NOT_ESTABLISHED        (1126 CPU-h retained, not increased)
```

Repair2 claims no WORK_UNIVERSE pass, no implementation completeness, no SR or
far-field completion, no cost-cap pass, no production readiness and no P5Y
closure. WORK_UNIVERSE remains reserved for independent adjudication.
