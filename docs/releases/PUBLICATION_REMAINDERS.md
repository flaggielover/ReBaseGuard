# Publication remainders

Open **publication-only** items. Neither affects any scientific or governance
verdict, and neither reopens the P4Z closure.

Current public semantics, which are up to date in the Markdown surfaces
(`README.md`, `docs/research_brief/ReBaseGuard_Research_Brief.md`) and in
`figures/final/figure09_campaign_lineage.png`:

```text
P4                    PARTIAL                     historical, immutable
P4Z                   CLOSED                      successor closure
P4_SCIENTIFIC_LINE    CLOSED_BY_LATER_SUCCESSOR
```

---

## 1. Research brief PDF is behind its Markdown source

```text
artifact   docs/research_brief/ReBaseGuard_Research_Brief.pdf
state      STALE_PUBLICATION_ONLY
```

`ReBaseGuard_Research_Brief.md` carries the current P4Z semantics. The PDF is
generated from it by `scripts/generate_research_brief.py` and has **not** been
regenerated, so it still carries superseded P4Z wording.

**Why it was not regenerated.** The repository pins no publication environment:
there is no root `requirements.txt`, lock file or `pyproject.toml` covering
`reportlab`, the generator records no version, and `figures/final/manifest.json`
records only the generator path. The only pin is the output hash,
`BRIEF_PDF_SHA256` in `scripts/verify_academic_presentation.py`.

Rendering with an unpinned `reportlab` does not reproduce the committed PDF byte
for byte, so regenerating would substitute an artifact that cannot be verified
against the one the pin describes, and would require editing the integrity
constant to match it. That is a fabricated equivalence, so it was not done.

**To close this item**, in the project's own pinned publication environment:

```bash
python3 scripts/generate_research_brief.py
python3 scripts/verify_academic_presentation.py --no-diff-check
```

then update `BRIEF_PDF_SHA256` as part of that justified regeneration. Record
the reportlab version used, so the next regeneration is checkable.

By contrast the **figure** toolchain *is* byte-reproducible here: regenerating
with `matplotlib 3.11.2` reproduces every untouched figure exactly, which is why
`figure09_campaign_lineage` could be updated and re-pinned safely. Two known
non-determinisms are excluded from figure updates on purpose:
`figure04_m_rho_stability.svg` differs only by a randomly named hatch-pattern id,
and `figures/final/README.md` carries source hashes that drift when a cited
source file changes.

## 2. Presentation verifier diff-check base

```text
constant   BASE_COMMIT in scripts/verify_academic_presentation.py
value      b04578810126d3fbc4d938a721481b1e6186b8ce
state      PUBLICATION_ONLY -- deliberately not changed
```

`python3 scripts/verify_academic_presentation.py` fails its diff-check. The
content checks pass:

```bash
python3 scripts/verify_academic_presentation.py --no-diff-check
# ACADEMIC PRESENTATION VERIFICATION OK
```

**Finding.** `BASE_COMMIT` is not a forgotten value. It is byte-identical to
`SR_TAG_COMMIT` in the same file — the commit carrying the
`rebaseguard-sr-gamma-certified` release tag, which `check_tags()` independently
verifies. The diff-check therefore asserts *"nothing outside the approved
presentation surface has changed since the SR-gamma release tag."* Around 190
commits of subsequent scientific work on `main` necessarily violate that, so the
check has been failing for reasons unrelated to any presentation change. It
fails identically at a clean checkout of `origin/main`.

**Why it was not repaired.** Repair requires choosing what the presentation
baseline means:

- keep it tied to the release tag, and accept that the diff-check only applies
  to a branch containing presentation changes alone; or
- retarget it at the current publication point, decoupling it from
  `SR_TAG_COMMIT` and redefining the constant.

Both are publication-policy decisions, and the second would turn a failing check
green by editing an integrity constant. Neither was guessed at.

**Interim use.** `--no-diff-check` exercises the meaningful content checks —
figure-manifest hash coherence, brief structure, licence, citation and the PDF
pin. A reviewer scoping a presentation branch can also pass an explicit base:

```bash
python3 scripts/verify_academic_presentation.py --base <publication-baseline>
```
