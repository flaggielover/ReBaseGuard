# Owner supplement 2 for MB-S: official-qualification watchdog semantics, MEM_POLL_S non-canonical branch, resume

**Record.** The user's text is reproduced **byte for byte** in `USER_RULING_MBS308_OWNER_SUPPLEMENT_2.txt` (this
directory; sha256 `4ba4a6662828137628902c941439f0af33309bde38410ab0cbba3baba90870b0`). It was given in chat, received at or shortly before 2026-10-01T16:02:05Z (the coordinator's first command
after receipt), as one block forming the whole of the user's turn, after the session's usage limit had reset. It
answers the two questions the coordinator put after ratifier2's rulings (`ca66e367`). It supplements the
owner-decision record (`5c2394ba`) and supplement 1 (`8fc2b038`) and replaces neither. Recorded clerically by the
coordinator (editorR3C1, a holder).

**Index (the .txt is authoritative).**

| item | the user's ruling | section |
|---|---|---|
| pre-freeze designated measurement | R-MEM step 1 unchanged: a watchdog event at the provisional 3 GiB is an invalid input; the specified 6 GiB re-run, subject to the step-5 bound | 1, 7 |
| official qualification | ANY watchdog event under the actual frozen MEM_CAP: FAIL CLOSED with a distinct status; no doubling, no qualification-only cap, no cure by another clean run, no grant, no target | 1, 6 |
| MEM_POLL_S | only already-canonical branches (unchanged value, or clipped to exactly 0.5 s); the unrounded-quotient branch at the designated measurement: STOP BEFORE FREEZE with a distinct status, nothing rounded or inferred; at the official qualification: FAIL CLOSED | 2, 3 |
| growth sampler | first-observation semantics NOT amended (as the ratifier confirmed) | 4 |
| sampler spacing | observed spacing <= 0.5 s; a shorter configured interval may be chosen; independent review before the freeze | 5 |
| event runs | cured only by the specific valid re-run the accepted rule permits | 6 |
| re-runs | no invented limit, no repeated doubling; a 6 GiB re-run outside the step-5 bound: stop and report before the freeze | 7 |
| EXCL_ALLOW | exact canonical equality NOT weakened; complete the analysis; a genuine ambiguity or undefined comparison: stop before the freeze with the smallest exact question; no tolerance, subset, union, intersection or sticky list | 8 |
| work order | resume the interrupted builder (inspect and preserve its uncommitted work first); then a FRESH non-holder builder for the reviewQ6 repairs; then ONE fresh review of everything; then brief update, MBS-10, host readiness, designated measurements, derivation, final review, single freeze, and the chain | 9-12 |
| grant | binds the complete owner records and supplements | 12 |

0 target evaluations; target exposure none; cell 309 out of scope.
