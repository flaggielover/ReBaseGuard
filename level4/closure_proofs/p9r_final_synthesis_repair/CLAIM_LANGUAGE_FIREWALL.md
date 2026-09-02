# P9R claim-language firewall

One rule: **the wording a sentence uses is fixed by the class of the claim it
reports.** Frozen at Checkpoint A; `scripts/audit_integrity.py` enforces the
mechanical parts, and `tests/test_language_firewall.py` scans the P9R prose.

## Licensed wording by class

| class | licensed | forbidden |
|---|---|---|
| `EXACT_THEOREM` | "proves", "exactly", "identically", "for all ... within the frozen model", "unique" | any hedge that implies measurement; any monotonicity wording |
| `CONDITIONAL_THEOREM` | "under assumption X", "if X then", "conditional on X" | "proves" without naming the assumption; dropping the assumption in a summary |
| `FORMALLY_VERIFIED` | "kernel-checked", "machine-checked", "no `sorry`", naming the axiom set | "proves the model"; extending the claim past the checked declarations |
| `CERTIFIED_NUMERICAL` | "certified interval", "enclosure", "certified to N bits" | "formally verified"; "proved"; extending a certified number to a bridge or a campaign |
| `EMPIRICAL_REPRODUCED` | "reproduced", "independently replayed", "MC-consistent with" | "exact agreement"; "confirms the theorem" |
| `EMPIRICAL_ONLY` | "observed", "measured", "within the tested regimes/grid" | "shows that ... in general"; "establishes" |
| `NEGATIVE_RESULT` | "rejected under the frozen criterion", "not validated as" | "disproved in general"; "no ... can ever exist" |
| `NOT_ESTABLISHED` | "not established", "not proved", "remains open" | "false"; "refuted" |
| `PARTIAL_PRIORITY_RESULT` | "survives at partial strength", "usable only at its adjudicated tier" | writing it at `CLOSED` strength |
| `PROVENANCE_LIMITATION` | "cannot be authenticated", "process limitation" | treating it as a scientific refutation |

## Specific bans carried from the P9 adjudication

* **Monotonicity.** No `EXACT_THEOREM` statement in this campaign may contain
  "monotone", "monotonic", "monotonicity", "non-increasing" or "decreasing in".
  Mechanically enforced by rule `V11`.
* **The operational corollary.** The sentence "no conceivable `rho`-based
  operational boundary can ever exist" and its paraphrases are banned. The
  licensed form is: *"`rho < rho_c` does not, in the frozen tested models,
  guarantee nominal-ARL preservation."*
* **`A(0)` versus `rho = 0`.** Nominal `A(0)` and the `rho = 0` mixture are two
  different controls and are never merged into one degradation figure.
* **Exact agreement.** A Monte Carlo comparison is never "exact agreement". Use
  `MC_CONSISTENT` / `MC_TENSION` / `MC_DISAGREEMENT` with the combined SE.
* **`P8R = CLOSED`.** Never written as changing `P8 = FAIL`, and never as
  implying model-class transfer.
* **Novelty.** Never stronger than `NOT_ESTABLISHED` unless independently
  adjudicated. A finite search with zero direct hits is prior-art evidence, not
  proof of novelty.
* **`CLOSED` status.** A `CLOSED` priority status never implies calibration
  quality, production readiness, novelty, or transfer.

## Enforcement

* rules `V1`-`V5`, `V11`, `V14` in `experiments/ledger_schema.py` (mechanical,
  over the ledger);
* `tests/test_language_firewall.py` scans every P9R markdown file for the banned
  phrases above and for `EXACT_THEOREM` rows whose statement contains
  monotonicity wording;
* gate `I8` fails the campaign if any mechanical rule reports a violation.
