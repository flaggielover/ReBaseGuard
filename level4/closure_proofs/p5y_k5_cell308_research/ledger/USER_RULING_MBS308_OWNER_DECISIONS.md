# Owner decisions for the cell-308 successor MB-S (S16(c), MBS-6, MBS-7, MBS-8, S1) and conditional execution authorization

**Record.** The user's text is reproduced **byte for byte** in `USER_RULING_MBS308_OWNER_DECISIONS.txt` (this
directory; sha256 `34eb1d41b56742fda2ba7fb7b70a46de5e0219ba324aa510437cc6c6d1065ad1`, 633 lines, 17291 bytes). It
was given in chat on 2026-09-30, received at or shortly before 2026-09-30T16:48:20Z (the coordinator's first command
after receipt), as one block forming the whole of the user's turn. It answers the coordinator's read-only extraction of
the DRAFT decision brief r2 (`governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md` @ `59dc1ada`, not yet reader-checked).
Recorded by the coordinator (editorR3C1, a holder), clerically: no word is paraphrased here beyond the index below.

**Decisions as stated (index only; the .txt is authoritative):**

| item | decision (user's words) | text section |
|---|---|---|
| S16(c) | "OPTION (A): GIVE PERMISSION" | 1 |
| MBS-6 | "OPTION (i): FINAL" | 2 |
| MBS-7 | "OPTION (i): KEEP MB-S SCIENCE UNCHANGED" | 3 |
| MBS-8 | "OPTION (i): MB r1 r3 CAPS" (values listed in section 4) | 4 |
| S1 | "OPTION (A): GIVE THE RULING", conditional on the chain in section 5 | 5, 6 |
| §11.2 sequencing | no owner choice among (a)-(d); resolve only if mechanically determined, else stop before freeze and ask that question only | 7 |
| execution | conditional prospective authorization of exactly one MB-S target execution after every gate | 15 |

**Binding notes (clerical; not rulings).**
1. The S1 ruling text for the grant's `user_ruling_s1` field is the user's section 5 (with section 6, the
   exactly-once limit), taken from the .txt bytes; the mechanism (verbatim text, its sha256, `reaffirms_c4`) is the
   frozen protocol's. Which exact byte range the grant carries is fixed at grant construction and checked by the
   independent grant validation, not here.
2. Conformance of the S1 text with the required content (governance addendum A1 §3 as read by erratum E1 D1, items
   1-6, including item 1's "expressly notwithstanding the brief's §21 and mitigation 5") is **not self-adjudicated by
   the coordinator**: it is an open point for an independent reviewer before any grant.
3. These decisions bind nothing yet: they bind at the freeze (S16(c), MBS-6/7/8) and at the grant (S1). Nothing in
   them changes an operational value in the pre-freeze candidate; MBS-8 (i) equals the values the candidate already
   carries (to be verified mechanically by a non-holder).

0 target evaluations; target exposure none; cell 309 out of scope.
