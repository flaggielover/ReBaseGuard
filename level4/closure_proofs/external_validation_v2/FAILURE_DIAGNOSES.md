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
