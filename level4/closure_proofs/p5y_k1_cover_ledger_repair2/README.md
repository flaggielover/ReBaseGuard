# P5Y K1 cover-ledger repair 2

A narrow provenance/evidence-binding repair of the two defects the independent
adjudication found in Repair1 (`41641218…`):

```text
1. PRODUCER IMPLEMENTATION HASH  -- evidence stamped the reviewed PARENT hash,
   which does not cover Repair1's certificate-producing code
2. SOURCE CERTIFICATE HASH       -- dependency hashes were derived from identity
   METADATA, not from the certificates actually consumed
```

The S0 double-charge defect closed by Repair1 stays closed and is re-verified
here. No science changes.

```text
PRODUCTION_ENABLED   = false     HARD_CPU_CAP   = 1126 (unchanged)
PRODUCTION_BITS      = 256 (unchanged)
FROZEN SUCCESSOR     = untouched, byte-identical
REVIEWED (c0a1f40)   = untouched, byte-identical
REPAIR1  (4164121)   = untouched, byte-identical
CELL 325             = CURRENT_CERTIFICATE_FAILURE_ONLY (unchanged)
WORK_UNIVERSE        = reserved for independent adjudication
```

## Structure: override provenance only

Repair1 and the reviewed implementation are **imported, not copied**.
`code/prior2.py` puts both on the import path; Repair2 overrides only the
evidence binding. A self-audit check asserts
`git diff <commit> -- <namespace>` is empty for both.

| module | role | certifying? |
|---|---|---|
| `producer.py` | canonical producer manifest and hash | yes |
| `certhash.py` | canonical certificate hash over certified content | yes |
| `provenance.py` | bottom-up chain construction and recursive verification | yes |
| `repair2_universe.py` | identity + admission binding producer and evidence | yes |
| `repair2_qualify.py` | runner: certify, then bind | yes |
| `prior2.py` | import bootstrap | yes |
| `repair2_audit.py`, `repair2_report.py` | self-audit and reporting | no |

## Defect 1: the producer hash did not cover the producer

`universe.implementation_hash()` hashes exactly thirteen files in the reviewed
namespace. Repair1 stamped it as both `implementation_hash` and `backend_hash`,
so changing `repair_layer2.correct_residuals` -- which decides the certified
`delta_mid`/`delta_cell` -- left the stamped identity bit-identical.

`producer_manifest()` is a deterministic `path -> sha256` map over every input
that can change an emitted certified value: Repair2's modules, the Repair1
modules actually executed, the reviewed modules actually executed, the frozen
algebra and config, the certified backend contract, and the fixed generation
parameters (including the pinned `python-flint` version). `producer_hash()` is
the canonical hash of that manifest.

It is **not** the Git commit hash: the frozen contract nowhere accepts a commit
id as complete implementation identity, and a commit covers unrelated files
while saying nothing about which bytes were executed.

`verify_loaded_modules_covered()` closes the general form of the hole: any
repo-local module that was actually imported but is absent from the manifest is
an error. Third-party libraries are bound by pinned version rather than by
hashing the in-tree virtualenv.

## Defect 2: source hashes did not cover the certificates

A certificate is now hashed over its scientific content:

```text
certificate      = { schema, identity, certified, status }
certificate_hash = sha256(canonical(certificate))
```

`identity` carries the producer hash and the dependency certificate hashes, so
the binding is recursive: a change anywhere below a node changes that node's
hash. `certified` holds the obligation's actual certified content -- residuals
and eps for objects, the order-1 chain for the bundle, the order-2 jets and
`M_R2` for curvature, and the intervals, cover charge, gates and status for an
assembly.

Deliberately excluded: CPU seconds, call counts, peak RSS, timestamps and log
formatting. The frozen `work.resume_identity` makes none of them
identity-bearing, and binding them would make an identical scientific
certificate hash differently on a busier machine.

## What the m=1 scoped run taught us

The m=1 SCOPED path computes only `F_0/D_0/H_0` and the closed-form leaves. It
never computes the dependency bundle that the frozen graph makes the m=1
assembly depend on, so it **cannot** discharge that obligation. Repair2 refuses
to issue a certificate for work that was not done, and the run is recorded as
`NOT_A_CERTIFICATE` with zero obligations. Refusing to certify uncomputed work
is the same class of protection this repair adds.

## Running it

```bash
PYTHONDONTWRITEBYTECODE=1 level4/.venv/bin/python -m pytest \
    level4/closure_proofs/p5y_k1_cover_ledger_repair2/tests -q

# demonstrate Repair1's two provenance defects
PRE_REPAIR_EXPECT_FAILURE=1 level4/.venv/bin/python -m pytest \
    level4/closure_proofs/p5y_k1_cover_ledger_repair2/tests/test_pre_repair2_defects.py -q

level4/.venv/bin/python \
    level4/closure_proofs/p5y_k1_cover_ledger_repair2/code/repair2_audit.py \
    --records level4/closure_proofs/p5y_k1_cover_ledger_repair2/diagnostics/regression
```

Note that editing any certifying module changes the producer hash and makes the
committed evidence stale; `test_stamped_producer_hash_is_the_current_one`
catches exactly that, and the regression must then be re-run.
