# SR history audit

## Verdict

```text
BENIGN HISTORICAL DRIFT WITH EXPLICIT SNAPSHOT SCOPES
```

The apparent 52-versus-92 mismatch is caused by 40 legitimate additive files
committed for the post-Level-4 SR Gamma certificate. It is not mutation of the
original 52 files. The old guard correctly rejects a tree larger than its
terminal-release snapshot; applying that result as a current whole-repository
integrity verdict is a path-scope/version ambiguity.

## Existing SR packages and authority

- `level4/stage_d/`: frozen authoritative Stage-D recurrence and stopping
  semantics.
- `level4/closure_proofs/sr_derivative/`: protected historical `m=1` theorem
  package plus its later additive certificate; immutable prior evidence.
- `level4/closure_proofs/sr_derivative_priority2/`: the new independent
  Priority-2 package; the only writable scientific namespace in this campaign.

## Snapshot A: terminal Level 4

Tag `rebaseguard-level4-closed` resolves to commit `5e43336264f257c7224b622f8063eb10aad481d6`
dated `2026-08-26T13:14:50+09:00`. Its protected SR subtree has 52 files and Git
tree `abd869b91fe8ba3e69af9db0e7356a73c36c724f`.

## Snapshot B: additive SR certificate

Tag `rebaseguard-sr-gamma-certified` resolves to commit
`b04578810126d3fbc4d938a721481b1e6186b8ce` dated
`2026-08-27T22:12:01+08:00`. Its SR subtree contains the same 52 blobs plus 40
new certificate/result/test files, for 92 total, with Git tree
`a4fbe9890b0ba59d588766dccfa17e9ef9d45f1b`. The current protected SR subtree
has that same tree identity.

`history/snapshots.json` contains complete, separate per-path SHA-256 manifests
and proves that all original paths are byte-identical in Snapshot B.

## HISTORICAL_DIAGNOSTICS

1. The old terminal verifier expects exactly Snapshot A and rejects Snapshot B's
   92-file scope. This predates Priority 2 and is not weakened or rewritten.
2. `scripts/verify_post_level4_archive.py` currently fails its repository-root
   `README.md` archive hash. Commits `acf8e16`, `e1f87d6`, and `e3dee7c` changed
   that README after the additive tag. The protected 92-file SR tree itself is
   unchanged.

These diagnostics remain outside Priority-2 pass counts only while both tag
identities reconstruct, their manifests pass, and Priority 2 leaves the
protected SR namespace untouched. Failure of any such check is a Priority-2
integrity failure.
