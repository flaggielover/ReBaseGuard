# P5Y K1 SR O9 — A5 governance amendment (pre-T2)

**Classification: `T2_A5_GOVERNANCE_AMENDMENT_CLOSED`.** Additive on top of
`a296244c` (`p5y-k1-sr-o9-pre-t2-governance`), which is preserved unchanged as history.
Machine-readable record and verification: `config/A5_AMENDMENT.json`.

**Old A5 was a governance specification error.** It demanded bit-identity of the O9
Taylor coefficients with the Task1R reference harness and `delta_O9 >= delta_baseline`,
contradicting the already-adjudicated optimized-backend doctrine
(`p5y_k1_sr_backend_cost_audit/adjudication/AUDIT_ADJUDICATION.json`:
"bit-equality was never the frozen criterion. Section 10 requires enclosure overlap /
containment"; full certificate "NOT uniformly conservative").

**New A5** (A5.1–A5.5, exact text in the JSON):
* A5.1 (a) O9 per-panel output bit-identical to the committed O9 reference (packet hashes
  including `ex`, `ez`); (b) Taylor coefficients bit-identical to the accepted
  `opt_backend`, error channels related exactly as frozen-disclosed (cap PROTOCOL "O9
  error-channel observation", `error_channel_exact.json`, governance C4): O9 <= opt,
  relative shortfall < 2^-200.
* A5.2 every O9 coefficient enclosure overlaps the Task1R harness enclosure (4032/4032).
* A5.3 the O9-mode certificate is recomputed independently; every frozen line passes
  under outward-safe exact comparison.
* A5.4 no requirement `delta_O9 >= delta_baseline`.
* A5.5 baseline Task1R mode = authoritative A4 reproduction path; O9 mode = authoritative
  T2 evidence path; all historical records immutable.

**No science changed:** A1–A4, A6, B1–B5, C1–C5, the executable panel universe, the cap
status and every threshold, budget, patch, panel, D, Z, precision, degree, candidate,
contract, obligation and the theorem target are unchanged; the original verifier passes
unmodified and leaves its namespace untouched.
