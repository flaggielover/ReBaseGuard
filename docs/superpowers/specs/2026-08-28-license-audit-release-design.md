# License audit and release design

## Objective

License original ReBaseGuard material under Apache License 2.0 while excluding
third-party dependencies, datasets, externally sourced material, and any
content not owned by the licensor. This is a repository-governance and public
presentation migration only. It does not change scientific artifacts, source
implementations, theorem statements, certificates, experiments, results,
historical failures, or closure decisions.

## Rights authority and boundary

Jingzhe Su confirmed that the Git identities `SuZhe`, `suzhe`, and `苏浙` are
all his and that, to the best of his knowledge, he has authority to license the
original ReBaseGuard materials he owns and authored. He is unaware of a
university, employer, contributor, or other agreement restricting the grant.
AI-assisted coauthor trailers do not represent separate human contributors or
ownership claims.

This confirmation does not authorize relicensing dependencies, datasets,
external abstracts or metadata, externally sourced material, or any artifact
whose rights are not owned by the licensor. Any newly discovered ownership or
compatibility conflict stops implementation before the licensing commit.

## Audit findings

- The repository currently has no root `LICENSE`, `COPYING`, `NOTICE`, or
  other license grant.
- Git history uses the three confirmed aliases above. No additional human
  contributor identity was identified by the history audit.
- No vendored dependency, virtual environment, Mathlib package checkout, or
  third-party source tree is tracked.
- Python dependencies are declared normally in
  `rebaseguard-proof/pyproject.toml` and its lock file.
- Lean and Mathlib dependencies are declared normally in
  `rebaseguard-lean/lakefile.toml` and `lake-manifest.json`.
- Raw external-validation datasets are not redistributed. Stage E fetches raw
  files into a gitignored cache.
- V2 and V3 dataset manifests record UCI sources under CC BY 4.0. Stage E also
  records UCI CC BY 4.0 inputs and an OpenML source whose terms remain
  source-specific.
- Tracked novelty-audit records include externally sourced bibliographic
  metadata and abstracts. Those records are not original ReBaseGuard prose and
  cannot be relicensed as such.
- Final publication figures are deterministic presentation derivatives of
  frozen repository evidence with recorded provenance. Original selection,
  arrangement, and rendering may be licensed only to the extent owned by the
  licensor; underlying third-party source content remains excluded.
- No evidence currently requires an Apache `NOTICE` file. A substantive
  `THIRD_PARTY_NOTICES.md` is justified by actual external dataset and abstract
  content.

## License alternatives

### Selected: Apache License 2.0

Apache-2.0 is selected for original ReBaseGuard software, Lean formalizations,
proof and certificate implementations, documentation, figures, and other
original material to the extent owned by the licensor. It permits inspection,
reproduction, extension, and redistribution while providing an express patent
grant, contribution terms, warranty disclaimer, and clearer legal structure
than a minimal permissive license.

### MIT

MIT would be shorter and permissive but does not contain Apache-2.0's express
patent grant or contribution framework. No audit finding makes that brevity
preferable for this research-software and formalization repository.

### BSD-3-Clause

BSD-3-Clause is also permissive and adds a non-endorsement clause, but it does
not provide Apache-2.0's express patent grant or contribution terms. The
repository already separately disclaims institutional endorsement in its
presentation materials.

### Split Apache / Creative Commons model

A split model was considered and rejected. CC BY 4.0 could be familiar for
scholarly prose and figures, but it would require continuing classification of
mixed reports, certificates, generated figures, and research-software
documentation. No concrete distribution advantage justifies that complexity.
Original ReBaseGuard prose and figures will therefore use the same Apache-2.0
grant, subject to explicit third-party exclusions.

## License and notice artifacts

### `LICENSE`

Add the canonical, unmodified Apache License 2.0 text from the Apache Software
Foundation. Include the complete official text and appendix without inserting
a project-specific copyright holder. Before commit, verify exact content and a
fixed SHA-256 digest against the official source.

### `THIRD_PARTY_NOTICES.md`

Create a concise, evidence-based boundary notice covering:

1. normal external dependencies, which are not vendored and remain under their
   own licenses;
2. UCI dataset sources recorded as CC BY 4.0, with links to the authoritative
   repository manifests;
3. the Stage-E/OpenML source-specific terms and the fact that raw datasets are
   not redistributed;
4. externally sourced publication titles, bibliographic metadata, and
   abstracts retained in the novelty-audit records;
5. the rule that third-party material and source-derived portions are excluded
   from the Apache-2.0 grant, while original ReBaseGuard code, analysis,
   selection, arrangement, and presentation are licensed only to the extent
   owned by the licensor.

Do not add a boilerplate Apache `NOTICE`. If implementation reveals an upstream
notice obligation or vendored component, stop and report the new evidence.

## Public presentation migration

### Root README

Keep citation and licensing conceptually separate. Replace the obsolete
unlicensed statement with a concise `## License` section that:

- links `LICENSE`;
- limits Apache-2.0 to original ReBaseGuard material owned by the licensor;
- links `THIRD_PARTY_NOTICES.md`;
- states that third-party dependencies and materials retain their own terms;
- does not make university or employer ownership claims;
- does not make citation a legal condition of Apache-2.0.

### Licensing readiness record

Update `docs/releases/LICENSING_READINESS.md` into a current decision and
readiness record without renaming it. Preserve its useful audit evidence, but
replace obsolete statements that no license exists. Record:

- the Apache-2.0 decision and scope;
- comparison with MIT and BSD-3-Clause;
- rejection of split licensing;
- third-party exclusions and notice necessity;
- the rights confirmation and its limits;
- any remaining caveats.

### Research Brief

Change only the final licensing sentence in
`docs/research_brief/ReBaseGuard_Research_Brief.md` and directly dependent
presentation wording. Regenerate
`docs/research_brief/ReBaseGuard_Research_Brief.pdf` with the existing
deterministic ReportLab pipeline. Do not change scientific prose, figures,
values, equations, page structure, or conclusions.

## Presentation guard migration

Narrowly update `scripts/verify_academic_presentation.py` and its focused test
file to replace the obsolete unlicensed invariant. The migrated guard will:

- require `LICENSE` and reject alternative root license filenames unless the
  invariant is deliberately revisited;
- verify the canonical Apache-2.0 bytes through a fixed SHA-256 digest;
- require the README's Apache scope, license link, separate citation language,
  and third-party notice link;
- require substantive dependency, dataset, OpenML/Stage-E, and novelty-record
  exclusions in `THIRD_PARTY_NOTICES.md`;
- require current Apache-2.0 wording in the licensing decision record and
  Research Brief Markdown;
- reject the obsolete phrase `License: not yet specified` in current public
  presentation artifacts;
- pin the regenerated Research Brief PDF hash after deterministic double
  rendering;
- preserve every unrelated science-first, author, citation, claim-firewall,
  figure-provenance, historical-tag, and diff-scope check.

The guard migration is an intentional replacement of one governance invariant,
not permission to weaken unrelated validation.

## Verification

Before implementation commit:

1. fetch the official Apache-2.0 text from an authoritative Apache source;
2. verify exact canonical bytes and SHA-256 in both implementation checks and
   the presentation guard;
3. run the focused academic-presentation tests;
4. run the complete presentation guard and synthesis verifier;
5. verify every Markdown link in changed public documents;
6. confirm `THIRD_PARTY_NOTICES.md` covers every external-content category
   found by the audit without asserting licenses not established by evidence;
7. regenerate the Research Brief PDF twice and require byte-identical hashes;
8. extract PDF text and confirm the new license line, unchanged scientific
   markers, author identity, page count, and metadata;
9. render every PDF page and visually inspect it for clipping or layout drift;
10. compare old and new extracted PDF text and require changes to be limited to
    licensing-related content;
11. inspect `git diff --check`, the complete diff, and `git status --short`;
12. require the implementation diff to remain inside the approved file set;
13. confirm no theorem, Lean source, certificate, experiment, scientific
    result, figure, historical artifact, or closure decision changed;
14. confirm both historical release tags remain unmoved.

No expensive scientific experiment is rerun for this governance migration.
Any new ownership conflict, incompatible third-party material, unexpected
scientific-content change, independent obsolete guard, or additional required
file stops the implementation for user review.

## Approved file scope

The design checkpoint is separate. The implementation may change only:

- `LICENSE`;
- `README.md`;
- `THIRD_PARTY_NOTICES.md`;
- `scripts/verify_academic_presentation.py`;
- `docs/research_brief/tests/test_academic_presentation.py`;
- `docs/releases/LICENSING_READINESS.md`;
- `docs/research_brief/ReBaseGuard_Research_Brief.md`;
- `docs/research_brief/ReBaseGuard_Research_Brief.pdf`.

Any additional required path needs explicit user approval.

## Git handoff

Commit this design as a separate decision-provenance checkpoint. After written
spec review and implementation verification, commit the governance migration
as `docs: add repository license` and push by ordinary fast-forward update.
Do not move tags, rewrite releases, force-push, or alter history.
