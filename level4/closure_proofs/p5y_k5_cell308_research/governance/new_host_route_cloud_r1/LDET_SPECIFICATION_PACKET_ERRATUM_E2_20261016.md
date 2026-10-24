# Erratum E2 to the L-DET specification packet (Cell-308 Cloud route r1) — after FR2

**Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE · NOT EXECUTED.** This erratum corrects erratum E1
(`LDET_SPECIFICATION_PACKET_ERRATUM_E1_20261016.md`, `36398544…969c`) and the packet (`f0f367a9…80e4`). Both are
preserved unchanged. Its source is FR2 (`reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR2.md`, `1ad769bb…8cac`): K8, K14 and
K21. `new_target_evaluations = 0` · `cell309_activity = none`.

## E2.1 — (b) number tokens: the source token verbatim (K14)

Comparison (b) does not re-format Decimal values.
* The parser keeps each JSON number's **source token** exactly as written, digits, sign, exponent and trailing zeros
  included. For example, the `parse_float` and `parse_int` hooks return an object that carries the raw token string
  next to its exact value.
* The canonical writer emits that token unchanged.

The (b) bytes are therefore equal only if every number token is byte-identical. Exactness of value is (a)'s job. A
difference of form only (e.g. `1.50` vs `1.5`, `-0.0` vs `0.0`, `1E+2` vs `100`) is a (b) difference, so it is a
MISMATCH. Both sides are written by the same pinned serializer, so a form difference is itself a reproduction failure.

## E2.2 — exactness control fallback (K14)

The exactness control acts on one Decimal leaf. It uses the first Decimal leaf in canonical key order in the first
case's view.
* If no view of any case has a Decimal leaf, the control acts instead on the first `fs`-grammar string leaf: the
  numerator is replaced by numerator × 10^40 + 1 over denominator × 10^40, re-normalised so that gcd = 1. Its `float`
  is unchanged unless the leaf is 0 or extremely small, and (a) must detect the change in every case.
* If neither kind of leaf exists, the exactness control is recorded as **NOT APPLICABLE**. That is fixed before OD-3
  and decided on the reference side by type only (value-free: the presence of a leaf type, not any value). It is never
  turned into INCOMPLETE after the attempt starts.

## E2.3 — bytecode caches and the prefix manifest (K14)

* The prefix manifest **excludes** every `__pycache__` directory.
* The interpreter prefix is owned by root and is read-only to the campaign user.
* Every computing step runs with `PYTHONDONTWRITEBYTECODE=1`. No cache can then be written between steps.
* An existing cache inside the prefix is removed **at install time, before the manifest is taken**. If one later
  appears, that is a manifest mismatch.

## E2.4 — pin list (K8)

The L-PIN list of erratum E1 §4 gains three pins:
* the **interpreter path**;
* **`sys.version`**;
* the **architecture** (`platform.machine()`).

The accepted RC2 pin (route A1 §1) binds in any case. The list is now complete against amendment r5's L-PIN row and
the development `PIN_KEYS`.

## E2.5 — standing of the re-derived reference list (K21)

Erratum E1 §5 says FR1 re-derived the reference list independently. That re-derivation rests on FR1's self-declared
eligibility. FR1 disclosed that its full clone fetched every branch's commit and tree objects (blob:none) and that it
counted ref names containing "309". The list's standing as "the reviewer's own" depends on the owner's adoption of
FR1's appointment.
