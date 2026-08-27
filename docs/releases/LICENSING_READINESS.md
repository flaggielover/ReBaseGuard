# ReBaseGuard licensing readiness

## Current decision

Original ReBaseGuard material is licensed under **Apache License 2.0** only to
the extent owned by the licensor. The canonical grant is the root `LICENSE`.
Third-party dependencies, datasets, bibliographic records, abstracts, and
source-derived portions are excluded and remain under their respective terms;
the repository boundary is documented in `THIRD_PARTY_NOTICES.md`.

This is a repository-governance record, not legal advice. Citation guidance in
`CITATION.cff` is scholarly practice and does not add a licensing condition.

## Rights confirmation and limits

Jingzhe Su confirmed that the Git author identities `SuZhe`, `suzhe`, and `苏浙`
are his, and that, to the best of his knowledge, he has authority to license
the original ReBaseGuard material he owns and authored. He reported no known
university, employer, contributor, or other agreement restricting that grant.
AI-assisted coauthor trailers do not identify separate human contributors or
ownership claims.

That confirmation does not cover third-party dependencies, datasets, external
abstracts or metadata, externally sourced material, or any content not owned
by the licensor. The Apache-2.0 grant does not relicense any such material.

## Rights and provenance inventory

| Material | Licensing treatment | Evidence boundary |
|---|---|---|
| Source code | Original ReBaseGuard code is Apache-2.0 to the extent owned. | External packages are dependencies, not relicensed project code. |
| Documentation and prose | Original ReBaseGuard prose is Apache-2.0 to the extent owned. | External titles, metadata, abstracts, quotations, and source-derived portions retain source terms. |
| Figures | Original selection, arrangement, and rendering are Apache-2.0 to the extent owned. | Underlying third-party data or content remains excluded. Figure provenance is recorded in `figures/final/manifest.json`. |
| Formal proofs and certificates | Original Lean sources and proof/certificate implementations are Apache-2.0 to the extent owned. | Lean, Mathlib, Python, FLINT/Arb, and other tools retain their own licenses. Scientific verification boundaries are unchanged. |
| Third-party datasets and derived evidence | Original ReBaseGuard analysis and presentation are covered only to the extent owned. | Dataset content and source-derived portions retain source-specific terms; raw downloads are not redistributed. |

## Why Apache-2.0

Apache-2.0 is a permissive license with an express patent grant, contribution
terms, warranty disclaimer, and redistribution conditions suited to a mixed
research-software, formalization, and documentation repository.

- MIT is shorter and permissive, but lacks Apache-2.0's express patent grant
  and contribution framework.
- BSD-3-Clause is permissive and includes a non-endorsement clause, but also
  lacks Apache-2.0's express patent grant and contribution terms.
- A split Apache/CC BY scheme was considered and rejected. Applying one license
  to original code, prose, and figures avoids an ongoing classification burden
  for mixed reports, generated figures, and research-software documentation.

No CC BY license is granted for original ReBaseGuard prose or figures.

## Third-party boundary and notices

The audit found no tracked vendored dependency tree. Python, Lean, Mathlib,
NumPy, SciPy, Matplotlib, PyArrow, pytest, python-flint/FLINT-Arb, and related
packages remain governed by their own licenses.

The repository records UCI datasets under CC BY 4.0 in the V2 and V3 external
validation manifests. Stage E records UCI CC BY 4.0 inputs and an OpenML Elec2
source subject to source-specific terms; raw files are fetched into a
gitignored cache and are not redistributed. Novelty-audit records contain
externally sourced publication titles, bibliographic metadata, and abstracts.
These categories are described in `THIRD_PARTY_NOTICES.md` and are excluded
from the repository-level Apache-2.0 grant.

No evidence found by this audit requires an Apache `NOTICE` file, so none is
added. If a future contribution, vendored component, or upstream notice creates
such an obligation, the release materials must be revisited.

## Release state

The governance migration consists of the canonical `LICENSE`, the scoped
`THIRD_PARTY_NOTICES.md`, consistent public presentation, and fail-closed guard
coverage. It does not alter any scientific claim, theorem, certificate,
experiment, result, historical failure, or closure decision.
