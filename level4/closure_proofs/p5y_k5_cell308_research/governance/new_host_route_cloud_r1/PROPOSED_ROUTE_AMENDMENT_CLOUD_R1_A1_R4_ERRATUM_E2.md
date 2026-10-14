# PROPOSED route amendment r4 — erratum E2: complete proc-field payloads

**Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE.** Date: 2026-10-15 (Asia/Tokyo).
Read with unchanged amendment r4 and erratum E1. All20 D-* decisions remain undecided. This additive development
clarification chooses no host or measurement policy and grants no operational, qualification, freeze or target authority.

The preserved independent revision-5 code report (`reviews/REVIEW_CLOUD_R1_DELTA_R5_CODEX_CODE.md`, reviewed commit
`13047bbebe509c1c04cd25ea90651c853cc61b03`) reproduced two malformed supplied status records establishing a complete
proc view: `NSpid:garbage<TAB>77` and `NSpid:77 88`. Whitespace tokenization discarded part of the field payload.
These are helper-input findings; no native kernel corruption or whole-preflight false PASS was demonstrated.

For the proposed proc-view input boundary, parse the recognized `NSpid:` delimiter before tokenizing its complete
payload. Exactly one recognized positive ASCII decimal PID token may establish the single-PID condition. Missing,
duplicate, malformed, non-ASCII or multiple PID evidence cannot establish completeness. Space/tab-separated valid
controls remain valid; a single valid numeric payload adjoining the delimiter may also be recognized. Positive mount
and parent IDs use ASCII decimal grammar; device major/minor use ASCII decimal components. Validation must not rely
on permissive Unicode digit classification or raise integer-conversion exceptions for malformed supplied tokens.
This clarifies record recognition, without changing namespace, mount, clock or resource thresholds.

The development-only `lx_verified.py` prototype composes the previously required A1/A2 canonical attestation and
launch observations with restricted public inputs. It does not discharge those conditions for operation: an accepted
complete wrapper still requires independent implementation review. It withholds unresolved memory allowances, keeps
decisions empty and the campaign detector UNKNOWN, and supplies no A5 science-import/pin-point proof. All formal
route/host/implementation conditions and governing sequence gates remain unmet.

Required validation: preserve the original counterexamples, provide refusal and positive-control tests, detect the
payload-dropping weakening, bind the full synthetic Linux run to exact source/test/harness/wrapper hashes, and obtain
fresh bounded code and evidence review. This text describes requirements; it is neither the review nor acceptance.

`new_target_evaluations = 0` · `cell309_activity = none`.
