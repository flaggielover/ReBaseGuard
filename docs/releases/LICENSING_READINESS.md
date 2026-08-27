# ReBaseGuard licensing readiness

## Current status

**License: not yet specified.** No root `LICENSE`, `COPYING`, or `NOTICE` file
exists, and the GitHub repository reports no detected license. Copyright
defaults therefore apply. This audit records presentation-layer readiness; it
does not grant permission or provide legal advice.

## Rights and provenance inventory

| Material | Current evidence | Readiness boundary |
|---|---|---|
| Source code | Repository history identifies project-authored implementations, but no file-level license grant or complete contributor rights statement exists. | Confirm ownership and contributor authority before selecting MIT, Apache-2.0, or another code license. |
| Documentation and prose | Project-authored Markdown is tracked without an explicit reuse license. Some novelty-audit JSON contains third-party titles and abstracts as research metadata. | Confirm rights in original prose and keep quoted/abstract metadata within source-specific terms; a future documentation license must not relicense third-party text. |
| Figures | Final figures are deterministic derivatives of repository evidence and appear project-authored; their provenance is recorded in `figures/final/manifest.json`. | Confirm rights in every source/input before considering CC BY 4.0 or another figure/documentation license. |
| Formal proofs and certificates | Lean sources, certificate programs, JSON enclosures, and reports are tracked as project artifacts without an explicit license. They also depend on separately licensed tools and libraries. | Decide whether these follow the code license, documentation license, or an explicit split; do not imply third-party tool licenses cover project artifacts. |
| Third-party datasets and derived evidence | Raw public downloads are not tracked in the reviewed external-validation trees. V2 and V3 manifests record UCI sources as CC BY 4.0; Stage E records source URLs and hashes but not a complete license field for every source. Derived JSON and figures are tracked. | Preserve source attribution, verify each dataset's terms at the authoritative source, and determine whether derived artifacts trigger attribution or redistribution obligations. |

## Third-party dependency boundary

The repository uses Python, NumPy, SciPy, Matplotlib, PyArrow, pytest,
python-flint/FLINT-Arb, Lean, Lake, and Mathlib-related packages. Their licenses
govern those dependencies, not ReBaseGuard automatically. No tracked
third-party notice aggregation currently exists. A release license decision
should be accompanied by a dependency and notice review.

## Dataset evidence found

- `level4/closure_proofs/external_validation_v2/data_manifest/datasets.json`
  records its selected UCI sources under CC BY 4.0.
- `level4/closure_proofs/external_validation_v3/manifests/datasets.json`
  records MetroPT-3 and Online Retail II under CC BY 4.0, with UCI identifiers
  and source URLs.
- `level4/stage_e/notes/DATA_PROVENANCE.md` records OpenML/UCI source URLs and
  hashes, but the presentation audit did not find a complete per-source license
  inventory there.
- Novelty-audit records include bibliographic metadata and abstracts obtained
  from external indexes. Those records should not be treated as relicensed
  project prose.

## Decisions required before licensing

1. Confirm Jingzhe Su's authority to license the original code, prose, figures,
   proofs, and certificates, including any university, employer, or contributor
   obligations.
2. Complete a file-level provenance review for copied, adapted, generated, or
   externally sourced material.
3. Verify and document dataset licenses and attribution requirements, including
   Stage E and any derived-data implications.
4. Choose whether to use one license or a split scheme. A possible future
   scheme is MIT or Apache-2.0 for code and CC BY 4.0 for original
   documentation/figures, but this audit does **not** authorize or recommend a
   final selection without the preceding rights review.
5. Add the selected license text, a scope statement, third-party notices, and
   dataset attributions together; then update README and release metadata.

Until those decisions are complete, the accurate public statement is:

> License: not yet specified.
