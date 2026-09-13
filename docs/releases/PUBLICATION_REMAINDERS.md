# Publication remainders

Publication-only items tracked after the P4Z closure. Neither affected any
scientific or governance verdict, and neither reopened the P4Z closure.

**Both items below are now RESOLVED** by commit `058c89ec59c1d44b6dce6293d5dc924243c893de` on
`codex/presentation-refresh`. The history is kept rather than deleted.

Current public semantics, carried by `README.md`,
`docs/research_brief/ReBaseGuard_Research_Brief.md`, the regenerated
`ReBaseGuard_Research_Brief.pdf`, and
`figures/final/figure09_campaign_lineage.png`:

```text
P4                    PARTIAL                     historical, immutable
P4Z                   CLOSED                      successor closure
P4_SCIENTIFIC_LINE    CLOSED_BY_LATER_SUCCESSOR
```

---

## 1. Research brief PDF — RESOLVED

```text
artifact          docs/research_brief/ReBaseGuard_Research_Brief.pdf
state             CURRENT
sha256            a761151c95ec42c6cb57a8ec06fb83a22ed4088e7b99ae965e5e5fbfa8019f51
previous sha256   8a28709e67810f62850c897f96c2a973415a3308ebc6df51dd9bf3ad121a9f19
environment       docs/releases/publication-requirements.txt
```

The PDF is regenerated from the current Markdown and carries the final P4Z
semantics. `BRIEF_PDF_SHA256` in `scripts/verify_academic_presentation.py` is
updated to the new hash as part of that justified re-render.

### Correction to the earlier record

An earlier revision of this document stated that the historical publication
environment was not recoverable and that byte-equivalence to the previous PDF
could not be shown. **That was wrong, and the error was mine.** The probe behind
it re-rendered the *previous* Markdown against an *already-updated*
`figure09_campaign_lineage.png`, so it compared two genuinely different
documents and mistook a content difference for toolchain drift.

Re-run correctly against a clean worktree at the pre-publication baseline
`59ad9bb8d238cea5c050bdb1f79cee73848f9715`, the pinned toolchain reproduces the
previous PDF **exactly**:

```text
committed at 59ad9bb8   8a28709e67810f62850c897f96c2a973415a3308ebc6df51dd9bf3ad121a9f19
re-rendered             8a28709e67810f62850c897f96c2a973415a3308ebc6df51dd9bf3ad121a9f19
```

So the pin in `publication-requirements.txt` is a **recovery of the historical
toolchain**, not a new and incomparable environment, and byte-equivalence is
claimed on evidence rather than asserted.

### Why rendering is deterministic

`scripts/generate_research_brief.py` sets `rl_config.invariant = 1`, which zeroes
the PDF timestamp and fixes the document id, and it uses only the base-14 PDF
fonts (Helvetica, Helvetica-Bold, Courier) with no embedded font files and a
fixed A4 geometry. Three consecutive renders of the current source produce
identical bytes.

### Verification performed

```bash
python3 scripts/generate_research_brief.py     # x3, identical sha256 each time
python3 scripts/verify_academic_presentation.py
```

All seven figures embedded in the brief were confirmed to match
`figures/final/manifest.json`, and the extracted PDF text was checked to carry
`P4Z = CLOSED` and `CLOSED_BY_LATER_SUCCESSOR`, to retain the stage-specific
historical labels, and to contain no `P4 = CLOSED` assertion and no stale
`SCIENTIFICALLY_COMPLETE_GOVERNANCE_INCOMPLETE` or
`CLOSABLE_WITH_REMAINING_OBLIGATIONS`.

## 2. Presentation verifier baseline — RESOLVED

```text
state    PASS with the full diff-check
tests    docs/releases/tests/test_presentation_baseline.py
```

### What was wrong

`BASE_COMMIT` was byte-identical to `SR_TAG_COMMIT`, conflating two unrelated
roles in one constant:

- the **identity pin** for the historical `rebaseguard-sr-gamma-certified`
  release tag, checked by `check_historical_tags()`; and
- the **baseline** for the current publication generation's diff-check.

Against the SR-gamma release tag the diff-check asked whether anything outside
the presentation surface had changed since that *scientific* release. Roughly
190 commits of legitimate later scientific work necessarily violated that, so
the check failed for reasons unrelated to any presentation change — it failed
identically at a clean checkout of `origin/main`.

### The migration

The two concepts are now separate constants:

| constant | role | value |
|---|---|---|
| `SR_CERTIFIED_TAG_COMMIT` | historical SR release-tag identity pin; **does not move** | `b04578810126d3fbc4d938a721481b1e6186b8ce` (unchanged) |
| `LEVEL4_TAG_COMMIT` | historical Level-4 release-tag identity pin; **does not move** | `5e43336264f257c7224b622f8063eb10aad481d6` (unchanged) |
| `CURRENT_PUBLICATION_BASE_COMMIT` | baseline for the current publication generation's diff | `59ad9bb8d238cea5c050bdb1f79cee73848f9715` |

`59ad9bb8` is the direct pre-publication parent of the publication lineage: the
last commit before publication work began, and the `main` tip this publication
generation fast-forwards. That is the only point against which "did this
publication generation touch anything outside the approved surface?" is a
meaningful question. It moves when a publication generation lands; the tag pins
never move.

### The surface was not broadened

`ALLOWED_PREFIXES` is unchanged at `("docs/research_brief/", "figures/final/")`.
Three individual files were added to `ALLOWED_PATHS`, each part of the
publication tooling: `docs/releases/PUBLICATION_REMAINDERS.md`,
`docs/releases/publication-requirements.txt` and
`docs/releases/tests/test_presentation_baseline.py`. `docs/releases/` is
deliberately **not** a prefix, and a test asserts that a different file in that
directory is still rejected.

### Regression coverage

`docs/releases/tests/test_presentation_baseline.py` — 27 tests covering: the
current publication diff passes; each allowed presentation path passes; each
protected or scientific path fails; the allowlist is not broadened to a whole
directory; both historical tag identities remain separately pinned and verified
against the real tags; the baseline is a real ancestor commit; the old conflated
baseline would still fail; the PDF matches its pinned hash; a tampered PDF is
caught; the hash constant is neither a placeholder nor the superseded value; and
the pinned ReportLab matches the installed renderer.

### Verification performed

```bash
python3 scripts/verify_academic_presentation.py
# ACADEMIC PRESENTATION VERIFICATION OK

python3 -m pytest docs/releases/tests/test_presentation_baseline.py -q
# 27 passed
```

---

## Maintaining this going forward

When a publication generation lands on `main`, advance
`CURRENT_PUBLICATION_BASE_COMMIT` to the new `main` tip in the same reviewed
publication commit that lands the next generation's changes. Leave
`SR_CERTIFIED_TAG_COMMIT` and `LEVEL4_TAG_COMMIT` alone — they pin history.
