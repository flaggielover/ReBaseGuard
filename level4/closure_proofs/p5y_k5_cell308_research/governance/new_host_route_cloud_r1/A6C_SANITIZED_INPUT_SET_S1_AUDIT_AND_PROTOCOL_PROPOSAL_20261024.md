# A6c option B2: audit of entries 1, 4 and 7, sanitized input set S1, manifest R2 and proposed brief erratum A6C-E15 (Cell-308 Cloud route r1), 2026-10-24

**Status: OWNER-DIRECTED PREPARATION · READ-ONLY AUDIT BY claude_cloud_recorder_20261022 · PROPOSED · NOT IN FORCE.**
`new_target_evaluations = 0` · `cell309_activity = none`.

```text
A6C_CANDIDATE_5   PHASE_2_STOPPED · PERMANENTLY_STOPPED · NOT_RESUMED · NO_REDERIVATION_RESULT · NOT_ADOPTED
A6C               BLOCKED: owner adoption of A6C-E15, then appointment of a new candidate
```

## 1. The owner's direction (verbatim, as issued on 2026-10-24)

> Choose option B2.
>
> Keep candidate 5 permanently stopped. Do not resume candidate 5 and do not treat its Phase 2 attempt as a result.
>
> Perform a read-only audit of entries 1, 4, and 7 for B2-derived material. Do not fetch either B2 source. Do not display the B2-derived content; report only paths, line ranges, counts, and classifications.
>
> Prepare a new sanitized A6c input set:
>
> 1. Preserve entry 6's S11 trace content that is within scope.
> 2. Remove or replace the B2-derived T6 material and all related B2-derived references that would expose out-of-scope incident-review content.
> 3. Keep the sanitized artifact separate from the unchanged original entry 6.
> 4. Audit entries 1, 4, and 7 and sanitize them too if they contain equivalent out-of-scope B2-derived content.
> 5. Regenerate a new pinned manifest from the sanitized artifacts, preserving exactly 40 numbered entries unless a documented scope decision proves otherwise.
> 6. Record every new path, commit, byte count and SHA-256.
> 7. Prepare a new brief erratum that supersedes the current manifest binding and explicitly states that B2-derived incident-review material is out of scope.
>
> Avoid reusing the label E15 without a namespace distinction, because matrix E15 already exists. Propose an unambiguous new brief-erratum and matrix-erratum name.
>
> Do not launch a new candidate, fetch B2 sources, fetch Phase 2 inputs, or send a proceed instruction. Keep the canonical brief and original entry 6 unchanged until the owner adopts the new protocol.

## 2. Candidate 5

**Permanently stopped.** It is not resumed. Its Phase 2 attempt is **not a result**, and nothing from it is adopted.
It is declined under proposed A6C-E15.7.

## 3. Method and the recorder's own contact

* **Sources.** All sources were read from git objects at `4f814796`, each verified against manifest R1:
  * entry 1: 23,691 bytes, `c91c7ff9…a4b7`;
  * entry 4: 14,529 bytes, `f8987a93…2046`;
  * entry 7: 25,507 bytes, `6a721ada…253c`.
* **Confined scan** of entries 1, 4 and 7 (scanner `e103c196`, configuration `ab0104c6`, counts only): 3 text files,
  **0 findings**, PASS.
* **Displayed to the recorder for entries 1, 4 and 7:**
  * section headings;
  * table header rows;
  * first table cells only where they are short IDs (for example `O19`);
  * the file-name column of entry 1's verification manifest (lines 33–44);
  * the first cells of entry 7 lines 129–130 (evidence file names);
  * token counts, vocabulary booleans and column positions;
  * five-word shingle-overlap counts.
* **Not displayed:** no content line of entries 1, 4 or 7. For entry 6, nothing beyond what is disclosed in
  `A6C_CANDIDATE5_PHASE2_STOP_AND_ENTRY6_AUDIT_20261024.md` §3.1.
* **B2 sources:** neither was fetched, read, listed or hashed.

## 4. Classification rule (applied mechanically)

| class | meaning | action |
|---|---|---|
| **P** | content attributed to B2Q or B2S | redact |
| **Q** | a verbatim quotation attributed to B2Q (the T6 definition) | redact |
| **R** | a reference to the historical T6 mitigation series in B3-derived texts (an M1–M8 token, or T6 together with historical or mitigation vocabulary). B3's only source for that series was B2S (entry 6 line 51) | redact |
| **T** | out-of-scope T6 transfer or dependency analysis built on B2-derived material (brief line 114) | redact |
| **S** | a pointer to a non-manifest B2 source file (pin, alias, method or digest) | redact |
| keep | the term T6, ER-T6 and T6_TRANSFER with their verdict labels; the gate designation B2 (B1–B9 gates); B1–B3 named in a role list; vocabulary such as "historical" or "original" without T6, mitigation-series or B2 context | keep |

## 5. Audit results: entries 1, 4 and 7 (line numbers, counts and classes only)

| entry | lines | flagged | classification | result |
|---|---|---|---|---|
| **1** `reviews/external/TRACE_EXTERNAL_A6B_POLICY_PROVENANCE.md` | 137 | 15; 7; 101, 103, 113 | 15: role list (B1, B2, B3), keep. 7: "T6 ruling" term, keep. 101, 103, 113: generic vocabulary (definition, exception, mitigation/ruling) with no T6, M-series or B2 token, keep. M-series tokens: 0. Blockquotes: 0. Shingles shared with entry 6 lines 157–175: 0 | **no B2-derived content found; not sanitized.** Entry 1's own inputs included entries 6 and 7 (its items 11–12). No propagation was found |
| **4** `governance/new_host_route_cloud_r1/PROVENANCE_DISPOSITION_RECORD_B3_20261016.md` | 132 | 104, 109, 114; 110; 127, 131 | 104 (O19), 109 (O24), 114 (O29): "B2" sits in the **gate** column (5 of 5), so gate B2, keep. 110 (O25): incident/historical vocabulary without T6, M-series or B2, keep (an S11 row). **127** (§6 Disposition): T6 with mitigation and historical, **R**. **131** (§6): M-series, **R**. Shingles shared: 0 | **sanitized: 2 lines** (127, 131) |
| **7** `reviews/external/CONFIRMATION_EXTERNAL_B3_CORRECTIONS.md` | 143 | see right | **redacted:** 33 (R, verdict line), 60 (R, the Y5 row: mitigation series, T6, definition), 61 (R, the Y6 row: mitigation, historical), **69–72** (T, the K-T6-1…4 dependency rows; 71–72 name B2 beside B3, and 71 carries the mitigation series and quotation marks), 98 and 100 (R, YC3: mitigation series), 102 (R, YC3: T6, historical, transfer), 118 (R, a clarification: mitigation series M1–M8, T6). **Kept:** 15 (role list B1–B3); T6-term-only lines 5, 11, 17, 31, 44, 45, 59, 62, 63, 78, 86, 88, 96, 114, 129, 130, 143; and 19, 27, 57, 58, 115 (57–58 are the Y1/Y2 rows on N1/N2, S11 items). Lines 88 and 114 contain quotation marks, but share **no** shingle with the B2Q quotation. Shingles shared: 0 | **sanitized: 11 lines** |

**Entry 6** (246 lines; the audit record above): **24 lines redacted**:

| class | lines |
|---|---|
| S | 11, 30, 51, 242, 243 |
| R | 18, 155, 199, 211 |
| P | 157, 161, 163, 169–175 |
| Q | 159 |
| T | 165, 167, 177, 197 |

* **Kept:** line 24 (role list) and the S11 trace sections, lines 57–151, which are unchanged.
* **Heading 153** ("T6 transfer and reasons") stays, as structure.

## 6. Whole-manifest screen (counts only)

* **The verbatim T6 definition** (entry 6 line 159) shares **no** five-word shingle with any other entry.
* **Entry 6 lines 157–175** share shingles only with **entry 16**
  (`CONSOLIDATED_DSTAR_PACKAGE_R2_ERRATUM_E2_20261016.md`) **line 49**: 8 shingles.
  * All 8 fall in column 3 of entry 6 line 169, which is B3's own assessment column.
  * Entry 16 line 49 has no B2, M-series, T6 or mitigation token.
  * Kept.
* **Residuals outside the requested audit** (owner decision before adoption, §10 D3):
  * **R-1. Entry 15** `CONSOLIDATED_DSTAR_PACKAGE_R2_ERRATUM_E1_20261016.md` **line 57.**
    * A 106-character paragraph in §3 "New-constant provenance trace", which is S2 material.
    * It carries the tokens M1, M6, T6, "mitigation" and "ruling", with **no B2 attribution**.
    * Under A6C-E15.3 a candidate could read it as historical T6 mitigation content.
  * **R-2. Entry 8** `CONSTANTS_RATIFICATION_MBS308.md` **line 1.** The document title (123 characters), with T6 and
    M1 tokens and no B2 attribution.
  * **R-3. Other M-series tokens,** read as other numbering series:
    * entries 34 (lines 18–25) and 35 (13, 16, 19): host or check vocabulary;
    * entry 17 (1160–1210): code identifiers;
    * entries 3 (8, 90), 5 (36) and 15 (20, 56): M1 or M8 alone.

    None has T6 or mitigation context.

## 7. New artifacts (all under `level4/closure_proofs/p5y_k5_cell308_research/`)

**Sanitized input set S1, commit `90d12cef2b97980991888a1cde819829c9a361ea`:**

| path | bytes | sha256 | blob |
|---|---|---|---|
| `ledger/briefs/A6C_SANITIZED_INPUTS_S1/REVIEW_EXTERNAL_B3_PROVENANCE.A6C_SANITIZED_S1.md` (entry 6) | 46,480 | `691eff13b23a9fa3aecbdbab5928365dbe96de323107648c49ce1ab8502bd8a6` | `63a864411e35d37b6f9edad08ccd6b5dddfca39a` |
| `ledger/briefs/A6C_SANITIZED_INPUTS_S1/PROVENANCE_DISPOSITION_RECORD_B3_20261016.A6C_SANITIZED_S1.md` (entry 4) | 14,955 | `8c91a8f91238b3f18426305f1eabf1be90beac80b420389a514f15f68bd80390` | `f0f00fd564d14fa5fade8c0601e64956394c4add` |
| `ledger/briefs/A6C_SANITIZED_INPUTS_S1/CONFIRMATION_EXTERNAL_B3_CORRECTIONS.A6C_SANITIZED_S1.md` (entry 7) | 20,593 | `979a3b97ec3525d2d545a6cd1f59c3a6bd22dd8c842f96d4d5eb9bc894d7c26e` | `3dd5cdaa4f7a3133b6b557be4e844ff788a03f12` |
| `ledger/briefs/A6C_SANITIZED_INPUTS_S1/a6c_sanitize_s1.py.txt` (the generator) | 4,062 | `076b45fa83916f3cad50bdff31998fb5cdca182332c52b156d40a81fd1357e35` | `f4ff1dfe32da98ed3fd51581da5dffc7ebc95ff6` |

**Manifest R2, commit `0c6c0a30f321ecc3d9891acef9fb5d99e1e6ffef`:**

| path | bytes | sha256 | blob |
|---|---|---|---|
| `ledger/briefs/A6C_PHASE2_MANIFEST_R2.json` | 20,981 | `a12470137f0f34c0a687a07c2b8f5e45517acd29ffc377143c50ae2e6e3c07cf` | `1ab17821b855e8633fc25002bcb347fd1e562e9c` |
| `ledger/briefs/A6C_SANITIZED_INPUTS_S1/a6c_derive_manifest_r2.py.txt` (the generator) | 2,582 | `c724ef676528c621905f05ff281d5891cd7c0a827c2dc3b7a5d6faa48994dee0` | `4dbd0d485211b271aa793bf1a4ee2cea7d8b3456` |

**Proposed brief erratum A6C-E15** (in the same commit as this record):

| path | bytes | sha256 | blob |
|---|---|---|---|
| `ledger/briefs/A6C_REDERIVATION_CLOUD_R1_ERRATUM_A6C_E15.txt` | 4,855 | `680b4d3e48328c1caa850e128899e99cd98d483e67d7c2cd4292eea9d6d8d701` | `966652d6fa473f3d9835fe98ada5a0732f7b9656` |

## 8. Checks

* **Sanitized artifacts:**
  * only the mapped lines differ, plus one appended trailer line each; every other line is byte-identical to the
    original; line numbers are preserved;
  * outside the markers, no B2Q, B2S, B2-file, builder-N or M1–M8 token remains. The remaining "B2" tokens are role
    lists (entry 6 line 24, entry 7 line 15) or gate references (entry 4);
  * **0** five-word shingles are shared with entry 6 lines 157–175;
  * confined scan: 4 text files, 0 findings, PASS. The generator's output is deterministic.
* **Manifest R2:**
  * derived mechanically from the verified manifest R1;
  * **exactly 40 entries, numbered 1–40** (39 Part 1, 1 Part 2);
  * only entries 4, 6 and 7 differ from R1;
  * byte-verified 40/40 against git; deterministic across two runs.
* **A6C-E15:** every cited commit, byte count, SHA-256 and URL was cross-checked mechanically against git.
* **Unchanged:** the canonical brief (`797248fc`, `489dec78…2f0c`), A6C-E14, manifest R1, and original entries 1, 4, 6
  and 7.
* **Correction before push.** A first S1 build also redacted entry 7 line 15. That line is a role list, so it was
  re-classified as keep. S1, R2 and A6C-E15 were rebuilt before anything was pushed, and the superseded local commits
  were never published.

## 9. Naming proposal

| series | label form | so far | next |
|---|---|---|---|
| brief errata | **`A6C-E<n>`** (file `…_ERRATUM_A6C_E<n>.txt` from n = 15) | A6C-E14 (file `…_ERRATUM_E14.txt`, adopted) | **A6C-E15** (this proposal) |
| readiness-matrix errata | **`RM-E<n>`** (file `READINESS_MATRIX_R4_ERRATUM_E<n>_*.md`) | RM-E1 … RM-E15 | **RM-E16** (to record the adoption) |

## 10. Owner decisions required

* **D1. Adopt A6C-E15** (`680b4d3e…d701`), with S1 (`90d12cef`) and manifest R2 (`0c6c0a30`, `a1247013…07cf`).
  Or amend it.
* **D2. Confirm the classification rule (§4) and the redaction sets (§5).** In particular:
  * entry 7's T6-term-only lines are kept;
  * entry 4's gate-B2 rows are kept.
* **D3. Residuals R-1 and R-2.** Either:
  * extend S1 to entry 15 line 57, and possibly entry 8 line 1, through a rebuilt S1, R2 and A6C-E15; or
  * declare them in-scope, non-B2 governance context in A6C-E15.4.

  Without one of these, a candidate under A6C-E15.6 could stop at entry 15 line 57.
* **D4.** Record the adoption as matrix erratum **RM-E16**, with a receipt and a ledger line.
* **D5. Later and separately:** a new candidate appointment whose Phase 1 fetches only the brief (A6C-E15.5).

## 11. Not done

* No candidate is launched, and candidate 5 is not resumed.
* No B2 source and no Phase 2 input is fetched. No proceed instruction is sent.
* Nothing is adopted. The register was not read.
* **Not added:** a matrix erratum and a ledger line. They are proposed as RM-E16 on adoption.
