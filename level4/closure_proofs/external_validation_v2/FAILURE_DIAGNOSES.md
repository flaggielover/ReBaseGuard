# Failure diagnoses

## F1 — UCI Beijing metadata contradicted the archive

The public API described the dataset as having no missing values, but the
official station files contain 8,739 `NA` PM2.5 cells. The first structure scan
stopped at the explicit token. The frozen loader counts `NA` as missing and
requires eight observed stations; no outcome had been generated.

## F2 — first protocol checkpoint attempt failed whitespace hygiene

`git diff --cached --check` rejected extra EOF blank lines. They were normalized
before commit, the protocol bundle was rehashed from `1f44d91c...` to the
authoritative `878c4dd7...`, and the 12/12 freeze suite was rerun. No protocol
content or outcome changed.

## F3 — pre-outcome gate trace was not strict JSON

The first read-only calibration gate printed `Infinity` for one household
bisection probe that produced zero cycles. Before persisting the gate, only
that diagnostic trace value was changed to JSON `null` and deterministic file
persistence was added. Calibration criteria, thresholds, and outcomes were not
changed; the same gate was rerun and passed.

## F4 — first outcome-suite run was 43/45

One test incorrectly asserted that a decision file absent at protocol freeze
must remain absent after the campaign; it now inspects the frozen Git commit
instead. A second test matched a phrase without normalizing a Markdown line
wrap. Only the audit assertions changed. The persisted outcome arrays,
hypotheses, and `EXTERNAL-VALIDATION-V2-PARTIAL` decision were untouched.

## F5 — first adversarial run was 19/22

A21 and A22 correctly failed before repository-verification and reproduction
records existed. A19 also failed because its checker rejected the harmless
substring `task_` in `figure_d_task_support.png`; the check now rejects raw
confirmatory/analysis input paths specifically. The plotting code always read
only `results/summary.json`. No campaign criterion or result changed.
