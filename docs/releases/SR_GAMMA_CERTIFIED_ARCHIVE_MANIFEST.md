# SR Gamma certified archive manifest

## Archive identity

This manifest freezes the additive post-Level-4 SR certification release. The
immutable integration/content anchor is
`9935671f2051bd8d2a7c2a958e729e6d57926aca`. The final archive/release commit
is resolved mechanically from the annotated tag
`rebaseguard-sr-gamma-certified`; a commit cannot embed its own SHA without
changing that SHA.

The original Level-4 tag `rebaseguard-level4-closed` remains fixed at
`5e43336264f257c7224b622f8063eb10aad481d6`. Its verdict remains
`LEVEL-4-CLOSED`: 17 PASS, 1 PARTIAL, 0 FAIL, 0 OPEN; 16/16 mandatory
requirements pass and L4R-13 remains nonmandatory PARTIAL.

## Additive SR authority

The post-Level-4 verdict is `SR-GAMMA-CERTIFIED` for the authoritative
symmetric two-chart SR detector. At 192-bit Arb precision:

```text
Gamma_SR in [5.80039179950844233566163341719178681375064361627654095,
             28.78128580308149205926606197637053008078060638372345905]
lower-endpoint margin above 2 =
  3.80039179950844233566163341719178681375064361627654095
epsilon_a = 4.504390937831505821584329894078802406556132351891806631e-6
epsilon_b = 0.004003813425152367039816387453712930372411790871914867036
||(I-K)^(-1)||_infinity <= 25000/19
||K_z|| <= sqrt(2/pi)
```

The exact-dyadic candidate has degree 16. The global `a` and `b` covers each
certify 1,210/1,210 patches. Full patch, subdivision, artifact-hash, test,
auditor, and toolchain records are in the machine-readable companion
`docs/releases/sr_gamma_certified_archive_manifest.json`.

## Historical freeze preservation

The historical SR tree contains 52 protected files. The certificate adds 40
tracked files, producing the current 92-file tree. All original 52 files are
compared against the historical tag by Git blob ID and remain byte-identical.
The old verifier's rejection of the 92-file tree as though it were the 52-file
snapshot is therefore an expected historical freeze rejection. The old guard
is unchanged; `scripts/verify_post_level4_archive.py` verifies the additive
layout separately.

## Independent reproduction

Terminal Level-4 closure:

```bash
bash level4/final_level4_closure/reproduce.sh
```

Post-Level-4 SR certificate:

```bash
bash level4/closure_proofs/sr_derivative/certificate/reproduce_closed_upgrade.sh
```

Archive state:

```bash
python3 scripts/verify_post_level4_archive.py
```

The source package is generated from the final annotated tag with:

```bash
git archive --format=tar \
  --prefix=ReBaseGuard-rebaseguard-sr-gamma-certified/ \
  rebaseguard-sr-gamma-certified |
  gzip -n > ReBaseGuard-rebaseguard-sr-gamma-certified.tar.gz
shasum -a 256 ReBaseGuard-rebaseguard-sr-gamma-certified.tar.gz
```

No archive binary is committed. The generated checksum is recorded in the
GitHub Release and final handoff.
