# P9R discrepancy register

Frozen at Checkpoint A, **before** any P9R result exists, so that no ruling here
can have been shaped by a P9R finding. Each entry is classified with the frozen
vocabulary

```text
BLOCKS_P9R  ·  DOES_NOT_BLOCK_P9R  ·  BLOCKS_GLOBAL_LEVEL4_CLOSURE
SCOPE_LIMITING  ·  PROVENANCE_LIMITATION
```

None of these is resolved by wording. All three inherited discrepancies remain
**open**.

---

## D-09 — global governance contradiction

**Statement.** The root line `CURRENT LEVEL-4 CAMPAIGN: CLOSED` conflicts with
current mandatory ledger rows: `L4R-11` `FAIL`, `L4R-06`/`L4R-12` `PARTIAL`,
`L4R-15` `FAIL`, `L4R-16` `OPEN`.

**Classification.** `BLOCKS_GLOBAL_LEVEL4_CLOSURE` · `DOES_NOT_BLOCK_P9R`

**Reasoning.** This is a genuine unresolved governance contradiction about the
campaign's own status bookkeeping. It is closure-threatening for *global*
Level-4 closure. It is not theorem-threatening: no P9R lemma, `P9R-T2a`,
`P9R-T2b` or `P9R-T3` consumes any global-closure statement. P9 correctly left
it open and P9R does the same. It is carried in the ledger as node
`GLOBAL-CLOSURE` (`NOT_ESTABLISHED`).

**What would close it.** A separate governance audit that either corrects the
root line or resolves the mandatory rows. Not a P9R deliverable.

---

## D-13 — P5-T11 plug-in residual

**Statement.** `P5-T11`'s stationary autocorrelation identity is **exact**. The
gridded-map / PCHIP plug-in used to evaluate it leaves a residual reaching about
16 chain standard errors, while a direct realized-window replay reduces the
paired gap to `-0.00045 +/- 0.00034`.

**Classification.** `SCOPE_LIMITING` · `DOES_NOT_BLOCK_P9R`

**Reasoning.** The 16-SE discrepancy is evidence that the plug-in lacks a valid
uncertainty budget, not evidence against the identity. It is a numerical /
model-reconstruction defect confined to that plug-in. `P9R-T2a` uses `P5-T1` and
`P5-T7`, not `P5-T11`, so nothing in the P9R core depends on it. It may **not**
be summarised as "within 3.5% agreement".

**What would close it.** A valid uncertainty budget for the gridded-map/PCHIP
plug-in, or its replacement by the direct realized-window estimator. Not a P9R
deliverable.

---

## D-15 — P3 grid preregistration authenticity

**Statement.** P3's 49 files arrived in a single uncommitted intake, so the grid
preregistration cannot be authenticated.

**Classification.** `PROVENANCE_LIMITATION` · `DOES_NOT_BLOCK_P9R`

**Reasoning.** A real process limitation that cannot be repaired retroactively —
the evidence needed to authenticate it does not exist. It does not threaten the
analytic boundary formula `rho_c = 1/|1-Gamma|`, because that formula is derived,
not fitted to the grid. `P9R-T2a` consumes `P3-T1` (the analytic boundary) and
never the grid. Carried in the ledger as `P3-PROV` (`PROVENANCE_LIMITATION`).

**What would close it.** Nothing available; it stays as process history.

---

## P9R-internal discrepancies

Recorded here as they arise during production. Any post-anchor bug follows
`FROZEN_PROTOCOL.md` §11: stop, preserve the invalid artifact, classify, and
re-anchor rather than patch.

| id | statement | classification |
|---|---|---|
| `P9R-D01` | `P1-T1` is classified `CONDITIONAL_THEOREM` here, against P9's `EXACT_THEOREM`, on the authority of P1's own `DEFINITION_AUDIT.md` §4 | `SCOPE_LIMITING` · `DOES_NOT_BLOCK_P9R` — a downgrade, not load-bearing for any P9R theorem |
| `P9R-D02` | `P3-X1` is reclassified `CERTIFIED_NUMERICAL`, against P9's `FORMALLY_VERIFIED` | `SCOPE_LIMITING` · `DOES_NOT_BLOCK_P9R` — this is the repair mandated by the P9 adjudication |
| `P9R-D03` | P9's `THEORY.md` states 66 dependency edges while its graph has 64 | `PROVENANCE_LIMITATION` · `DOES_NOT_BLOCK_P9R` — a defect of the P9 artifact; P9R's own counts are generated, never transcribed |
| further rows | appended during production only | |
