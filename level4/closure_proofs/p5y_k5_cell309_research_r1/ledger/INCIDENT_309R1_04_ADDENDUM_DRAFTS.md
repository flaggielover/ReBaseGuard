# Incident 309R1-04 addendum: the pre-FREEZE_READY Phase-4 drafts, preserved verbatim (append-only; per review R3 follow-up 3)

Review R3 recommended preserving the scratchpad drafts, which a container restart can lose, so that the
incident-independence review can compare them directly with the committed package instead of relying on the
coordinator's statement.

* **What is kept.** The three files below are byte-identical copies of the coordinator's scratchpad drafts, as they
  stood when the committed package was built. Birth and modify times are the scratchpad filesystem timestamps.
* **Quarantine check before commit** (coordinator). A search for decimals and "Γ =" patterns found:
  * symbolic formulas only (Γ = g_hi + ρ·x_hi·M; Γ < 0; Γ = 0 in the outcome table);
  * the Python version string 3.11.15 in the manifest.

  There is no 305–309 value and no quantity derived from 309. The static quarantine scan passes.
* **Relation to the committed package.** The committed package (`protocol_prep/`, from ce829bb4 onward, after R2's
  FREEZE_READY) was derived from these drafts and then revised in response to R2's FC items and R3's notes.

| file | sha256 | birth (UTC) | last modify (UTC) |
|---|---|---|---|
| `P309_PROTOCOL_DRAFT.md` | `978e382d24dcc3c414201fe099a764ff8d2a2f831522d462f7213026d5d36855` | 2026-09-29 14:11:58Z | 2026-09-29 16:13:32Z |
| `P309_FORMAL_PACKAGE_DRAFT.md` | `76621281b8d8f177657861c3117fd32b46a14b7d039fb8230b4246f80de76eab` | 2026-09-29 14:12:43Z | 2026-09-29 23:29:12Z |
| `P309_CANDIDATE_FREEZE_MANIFEST.json` | `57708bfca1e6ca739bc8a166fb97b79d11b109fd90b1e4d00369070573da1370` | 2026-09-29 23:11:03Z | 2026-09-29 23:47:29Z |
