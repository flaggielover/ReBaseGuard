# Owner records for MB-S: provenance check against the session transcript (clerical)

On 2026-10-01 the coordinator extracted, by program, the pasted block of each of the user's four turns from the session
transcript (`~/.claude/projects/-Users-suzhe-ReBaseGuard/fb722654-cd8d-472d-928c-34a116f8b315.jsonl`; the block
between the paste markers, with one trailing newline) and compared it with the recorded file. The three rulings had
been typed out by the coordinator when recorded; the comparison shows them byte-identical to the transcript.

| record (ledger/) | transcript line | received (transcript timestamp, UTC) | bytes | sha256 | equals transcript |
|---|---|---|---|---|---|
| USER_RULING_MBS308_OWNER_DECISIONS.txt | 2088 | 2026-09-30T16:47:12Z | 17291 | 34eb1d41b56742fda2ba7fb7b70a46de5e0219ba324aa510437cc6c6d1065ad1 | yes |
| USER_RULING_MBS308_OWNER_SUPPLEMENT_1.txt | 2477 | 2026-10-01T11:09:52Z | 18797 | 3f7d477b24900b64c7e30b3180ae7114fe642753956e31fe185fc6ef129d33d6 | yes |
| USER_RULING_MBS308_OWNER_SUPPLEMENT_2.txt | 2738 | 2026-10-01T16:00:52Z | 12941 | 4ba4a6662828137628902c941439f0af33309bde38410ab0cbba3baba90870b0 | yes |
| USER_DIRECTIVE_MBS308_OVERNIGHT.txt | 2800 | 2026-10-01T16:20:02Z | 23942 | d099821c4f422c204324e1148aac6b82314003b3f22bb6b423ca47db15113bdb | written from the transcript |

The fourth text (overnight autonomous completion campaign) is an operating directive: it changes no option, restates
the rulings and the stop conditions (its section 27), and fixes the grant's binding order as (1) the original
owner-decision record, (2) supplement 1, (3) supplement 2 (its sections 2 and 16). It is recorded for provenance and is
not itself one of the three records the grant binds. Supplement 1 was received together with the typed words "Try
again"; each other block formed the whole of its turn.

0 target evaluations; target exposure none.
