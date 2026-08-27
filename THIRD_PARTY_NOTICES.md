# Third-party material and license boundaries

ReBaseGuard's Apache License 2.0 applies only to original material owned by the
licensor. It does not relicense third-party dependencies, datasets,
bibliographic records, abstracts, quotations, or other externally sourced
material. Those items and any source-derived portions remain subject to their
respective licenses and terms.

## Software dependencies

The repository declares external Python and Lean dependencies through ordinary
package manifests; the audit found no tracked vendored dependency tree. These
include Python, NumPy, SciPy, Matplotlib, PyArrow, pytest,
python-flint/FLINT-Arb, Lean, Lake, Mathlib, and their transitive dependencies.
Each dependency remains under its own license. The root `LICENSE` does not
change those licenses.

## External-validation datasets

Raw external-validation datasets are not redistributed by this repository.
Where reproduction retrieves them, their content remains governed by the
source terms.

- The [V2 dataset manifest](level4/closure_proofs/external_validation_v2/data_manifest/datasets.json)
  records its selected UCI sources under CC BY 4.0.
- The [V3 dataset manifest](level4/closure_proofs/external_validation_v3/manifests/datasets.json)
  records MetroPT-3 and Online Retail II under CC BY 4.0.
- [Stage E data provenance](level4/stage_e/notes/DATA_PROVENANCE.md) records
  UCI Air Quality and Bike Sharing under CC BY 4.0, and Elec2 through OpenML
  under the source-specific redistribution terms recorded there. Stage E
  fetches raw files into a gitignored cache rather than redistributing them.

Original ReBaseGuard code, analysis, selection, arrangement, and presentation
of derived evidence are Apache-2.0 only to the extent owned by the licensor.
That grant does not change rights in the underlying datasets or source-derived
portions.

## Bibliographic and novelty-audit records

The [novelty-verification records](level4/closure_proofs/novelty_verification/)
retain externally sourced publication titles, bibliographic metadata,
abstracts, and source notices for auditability. Those records are not original
ReBaseGuard prose and are excluded from the Apache-2.0 grant. Their reuse is
subject to the applicable source terms.

## Figures and reports

Final figures have repository-recorded provenance. Original ReBaseGuard
selection, arrangement, annotations, and rendering are licensed under
Apache-2.0 only to the extent owned by the licensor. Any underlying third-party
data, text, marks, or other source content retains its existing status.

This file records boundaries identified by the repository audit; it does not
replace the license or attribution information supplied by third-party sources.
