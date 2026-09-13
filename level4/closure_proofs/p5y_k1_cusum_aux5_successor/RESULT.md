# P5Y K1 CUSUM Aux5 successor: freeze and qualification result

**Classification: NON-PRODUCTION qualification.** This record contains no production cell, makes no claim about the full cover, and does not close K1 or P5Y. The per-cell obligation statuses printed by the runner are **not** criteria under the frozen protocol, and nothing here interprets them.

## Freeze

The freeze was committed **before** any qualification run.

- Pre-manifest commit `868fa2c8` holds the generated identity layer, the host qualification record, the cap formula and the qualification protocol.
- Freeze commit `d31ea4ed` holds `manifests/producer_manifest_v3.json` and `config/FREEZE_RECORD.json`. The manifest was generated on rebaseguard-vultr-02 from a clean checkout of `868fa2c8`.

| Identity | Hash |
|---|---|
| producer_manifest_hash | `b55a2da1fea0c7ee889f8da6a4b893c12d3ef24e2bc02d19bd5488187fd30fd9` |
| runtime_contract_hash | `bc75c9ea7cd5f9406a0509bb0a161aa2c013f80427d1035197989e3d202c845a` |
| producer_identity_hash | `3692d0feeaef71365798cd99399fdb6d744573f38d59dba5cfe2e99294f0ae19` |
| manifest file sha256 | `611bd0a9f356b0e7f5e63da60567ac1afa9e69fc1f8c464c7e5b89aeedbd2b9f` |
| QUALIFICATION_PROTOCOL.json sha256 | `81e28577fdb0ebf671e0ea99799245e6d02a58015cf7c8e7a229f0d4f26b1d94` |

**Runtime:**
- uv CPython 3.12.3 in the dedicated venv `/root/work/rbg-cusum-aux5-venv`;
- numpy 2.5.2, python-flint 0.9.0, scipy 1.18.1;
- OpenBLAS 0.3.34, runtime corename **Haswell**;
- **5 backend libraries bound by absolute path**: flint, gmp, mpfr, numpy OpenBLAS64 and SciPy OpenBLAS.

**External-venv defect:** REPAIRED. Aux4 bound `{}` for an out-of-tree venv.

The scientific modules and the scientific-hash semantics (`schema.py`, `hash_v2.py`) are byte-identical to Aux4, and `manifest_v3.verify()` enforces this.

## Qualification run

- **Run:** `evidence/qualification_r1/`, from 2026-09-13 07:33:52Z to 08:07:55Z, on a clean checkout at `d31ea4ed` (head recorded in `checkout_head`).
- **Isolation:** four fresh `env -i` interpreters with pinned threads and no resume, run concurrently with `taskset` on physical cores 0, 2, 4 and 6. Host load before launch was 0.10.
- **Analyzer:** `code/analyze_qualification.py`, output in `QUALIFICATION_RESULT.json`.

| Criterion | 318 A | 318 B | 323 A | 323 B |
|---|---|---|---|---|
| P1 runs complete (rc 0, final gate, chain verified, SciPy-free) | ✓ | ✓ | ✓ | ✓ |
| P4 runtime and producer identity equal the frozen manifest v3 | ✓ | ✓ | ✓ | ✓ |
| P5 backend binding non-empty, four families, absolute paths | ✓ | ✓ | ✓ | ✓ |

| Per-cell criterion | 318 | 323 |
|---|---|---|
| P2 `scientific_content_hash` identical across repeats | ✓ `01ff4f7a26321024…` | ✓ `054a5ef0cd932ddc…` |
| P3 every `certificate_hash` identical across repeats | ✓ | ✓ |

**QUALIFICATION = PASS. CUSUM_DETERMINISM = PASS.**

The raw record files are not byte-identical between repeats. A recursive comparison of each cell's two records finds 80 differing leaf values per cell, all in measurement fields: `cpu_seconds`, `cpu_seconds_auxiliary`, `cpu_seconds_including_dependencies`, `cpu_seconds_prepare`, `peak_rss_kib` and `wall_seconds`. The frozen hash semantics exclude these fields by design. Each cell carries 28 certificates, all of which match across repeats.

## Cost

| Run | CPU-s incl. dependencies | aux CPU-s | wall s | peak RSS KiB |
|---|---|---|---|---|
| 318 A | **2041.449** | 169.93 | 2042.2 | 253568 |
| 318 B | 2033.363 | 169.93 | 2033.7 | 253296 |
| 323 A | 2039.921 | 170.58 | 2040.0 | 253516 |
| 323 B | 2038.723 | 169.37 | 2038.8 | 253528 |

**c_max = 2041.449 CPU-s (0.56707 CPU-h).** The spread across the four runs is 0.4%.

**Derived cap, from the frozen formula** (N = 326, W = 4), in CPU-h:

| Term | Value |
|---|---|
| P | 203.351 (exact: 3660318826872961/18000000000000) |
| R | 1.0 |
| INFL | 4.0 |
| RETRY | 9.78 |
| OVH | 4.067 |
| **CAP** | **300** |

The recomputed cap equals the prefreeze value. That value was derived from the Aux4 AWS basis of 2278.1 s; the formula, not the number, is what binds.

**Informational only (never a criterion):** the scientific hashes differ from the Aux4 SkylakeX records of 318 and 323, as the protocol predeclared (different kernel and producer identity).

## Status fields

| Field | Value |
|---|---|
| `CUSUM_SUCCESSOR_FROZEN` | **YES**: `d31ea4ed` |
| `CUSUM_DETERMINISM` | **PASS** (2 cells × 2 fresh repeats) |
| `CUSUM_MEASURED_CMAX` | **2041.449 CPU-s** |
| `CUSUM_DERIVED_CPU_CAP` | **300 CPU-h** |
| `CUSUM_FULL_CAMPAIGN_READY` | **NO.** The producer is qualified, but the protocol requires a separate frozen production checkpoint (ledger, lifecycle, cap invariant, K4 integrity attestation), and none exists yet. |
| `CUSUM_FULL_CAMPAIGN_LAUNCHED` | **NO** |
| Qualification certificates used as production cells | **NO** (the protocol forbids it) |

## Disclosures

- **SciPy download:** scipy 1.18.1 was downloaded from PyPI into a new dedicated venv, with explicit user permission. The pre-existing Vultr venv was not modified.
- **Independence:** the successor, the protocol, the analyzer and this record were written by the same agent session. The qualification criteria were frozen before the run, but independent review of the identity layer is still recommended before any production checkpoint.
- **Live campaign:** the live AWS PS1 campaign was not touched.
