# CUSUM Aux5 composite closure: artifact inventory

What this repository carries, what stays on the production host, and what a retrieved archive has to satisfy.
Machine-readable form: `config/ARTIFACT_HASHES.json`.

## 1. Committed to Git (`evidence/closure_r1/`)

Each file is byte-identical to the artifact produced by the gated terminal closure on `rebaseguard-vultr-02` under
`/root/work/postk1-runs/closure-r1/`, and is bound by `config/ARTIFACT_HASHES.json`.

| File | Bytes | sha256 | What it proves |
|---|---:|---|---|
| `COMPOSITE_AUDIT.json` | 117,383 | `2ec4dcbb9f2bc27568742db053133c01a369863a21f9a4f066471fcd9cb4b670` | the composite audit: both halves, all 326 verified (record, envelope) pairs with their hashes, partition, state COMPLETE |
| `K4_COMPOSITE_ATTESTATION.json` | 120,089 | `039e2e1cbebb9561c177ddca790dbc2c675eafde15553ad4e1282777d9bd8d2c` | the K4 composite integrity attestation, `cells_verified = 326` |
| `PREDECESSOR_BINDING_FINAL.json` | 245,462 | `0676fc8267bac3fc6044ab4cb9f57c8769b2b9d62e0d2f0bb2a2d3b1d9db8ac3` | the terminal predecessor, re-collected after closure and unchanged |
| `COMPOSITE_EXPORT_MANIFEST.json` | 35,312 | `29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334` | the export: 326 record paths, each bound by sha256, plus the canonical audit digest |
| `HOST_AT_CLOSURE.json` | 1,567 | `a5dd10a1c5ae77e669bf96729b287a67e56d36d3447f708a2d9fd4666f270429` | package versions and the 11 bound library hashes at closure |
| `CONTAINMENT_PRE_RESTORE.json` | 3,776 | `d83b4eb6028155a472e26a2d4923819332d77577a075e50b504011610029b09e` | containment still intact when the campaign ended |
| `CONTAINMENT_POST_RESTORE.json` | 3,429 | `eee9f12af1021ae3f5fbba0c9696026fa08463e84a32695059285e4c948f4a6d` | containment restored to the recorded pre-containment state |

Total committed evidence: 527,018 bytes.

Governance objects bound by the inventory but living in their own namespaces: successor checkpoint `f9380847…`,
run authorization `0c7621d4…`, carry-over countersignature `e1ee7fb1…`, predecessor checkpoint `dd4c89d7…`,
predecessor authorization `b8f11ec0…`, predecessor countersignature `1ceb92d4…`, and the canonical composite-audit
digest `fa1d79b5…`.

## 2. Not committed — external evidence

| Object | Where | Size | Digest |
|---|---|---:|---|
| Export record tree `COMPOSITE_EXPORT/k4_records/` (326 files) | `rebaseguard-vultr-02:/root/work/postk1-runs/closure-r1/` | 93,128,357 B (~88.8 MiB) | see §3 |
| Terminal ledger `ledger.json` | `rebaseguard-vultr-02:/root/work/postk1-runs/cusum-aux5-production-glibc-r1/` | 280 KiB | `d6f63cf41910437ebc2a0c3413b0698ada3ab4170a6ac1db23b7dd195c0b1a59` |
| Terminal journal `journal.jsonl` | same root | 1.1 MiB | `c59a243d560067495d90647dcf0d59a368afcf74c445e627f6835670e544ad58` |
| Attempt records and provenance envelopes (`attempts/`, `provenance/`) | same root | ~58 MiB | bound pair-by-pair inside `COMPOSITE_AUDIT.json` |

**Why the export tree is not in Git.** It is ~88.8 MiB of 326 JSON records that Git would carry forever in every
clone, and it adds no verifiable fact that the repository does not already hold: every one of those records is bound
by sha256 in the committed export manifest and, independently, as a `record_sha256` in the committed composite
audit. Committing the manifest gives the same cryptographic binding at 35 KiB.

**This tree is not reproducible from Git alone.** The records are the output of the frozen producer over the
production runtime; re-deriving them means re-running the frozen export against the terminal runtime on the host
(`gs_entry.py export`), or retrieving the archived tree. Nothing in this repository regenerates them.

## 3. Verifying a retrieved export archive

A retrieved copy is the authentic export if and only if:

1. it contains exactly 326 files, `k4_records/aux5_CUSUM_<cell>_256.json` for every cell 0-325, with no extra file;
2. every file's sha256 equals its entry in `evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json`;
3. every one of those hashes also equals the `record_sha256` of that cell's pair in
   `evidence/closure_r1/COMPOSITE_AUDIT.json` (128 pairs from the predecessor half, 198 from the successor half);
4. the tree digest matches (below).

```bash
python -B code/verify_closure.py --export-tree /path/to/COMPOSITE_EXPORT
```

**Tree digests.** Both are sha256 over the listing `"<sha256>  ./<name>\n"` for the 326 files, and they differ only
in the sort order of that listing:

| Value | Rule |
|---|---|
| `5c3c1f854fd04ea44a9a9a14902c7ba6bf4361fa5fa5bb9c311124de281acf59` | `find . -type f \| sort \| xargs sha256sum`, as computed at closure on the host, whose `LANG` was `en_US.UTF-8` — locale-dependent collation |
| `7517199ae57fe99dd63e60bd820c72349f6faf1e5cf139be75ce331a6fedb0a3` | the same listing under `LC_ALL=C sort` (byte order) — locale-independent, and the value the verifier checks |

Both digests cover the identical 326 files; only the order of the lines differs. Use the byte-order value when
reproducing the digest yourself.

## 4. Verifying the Git package on its own

`code/verify_closure.py` needs nothing but this repository. It re-derives `config/ARTIFACT_HASHES.json` and
`config/CLOSURE_VERDICT.json` from the committed evidence, re-hashes every artifact, re-checks the partition and the
tolerated-issue set, recomputes the canonical composite-audit digest `fa1d79b5…`, and rebuilds the K4 attestation
from the audit with the frozen `gs_composite.build_composite_attestation`, requiring canonical equality. It exits 0
only if every check passes, and it never needs the external tree.
