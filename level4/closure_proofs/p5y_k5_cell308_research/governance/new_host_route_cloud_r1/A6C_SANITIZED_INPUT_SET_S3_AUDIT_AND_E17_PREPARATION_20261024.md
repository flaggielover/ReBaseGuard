# A6c option A after candidate 6: complete excluded-source audit of the R3 inputs, sanitized input set S3, manifest R4 and proposed brief erratum A6C-E17 (Cell-308 Cloud route r1), 2026-10-24

**Status: OWNER-DIRECTED PREPARATION · READ-ONLY AUDIT BY claude_cloud_recorder_20261022 · PROPOSED · NOT IN FORCE.**
`new_target_evaluations = 0` · `cell309_activity = none`.

```text
A6C_CANDIDATE_6   PHASE_2_STOPPED · NO_REDERIVATION_RESULT · NOT_ADOPTED · PERMANENTLY STOPPED · NOT TO BE REUSED
A6C               BLOCKED: owner adoption of A6C-E17, then appointment of a new candidate
```

## 1. The owner's direction (verbatim, as issued on 2026-10-24)

> Choose Option A.
>
> Keep candidate 6 permanently stopped:
>
> PHASE_2_STOPPED
> NO_REDERIVATION_RESULT
> NOT_ADOPTED
>
> Do not reuse candidate 6 or launch another candidate yet.
>
> Perform a complete read-only audit of all 40 R3 inputs against the canonical brief's excluded-source stop rule. Do not fetch any excluded source. Detect not only B2Q/B2S material, but also:
>
> - E1 register references or attributed content;
> - audit/*;
> - REVIEW_EXECUTION_INTERRUPTION*;
> - INCIDENT_INDEPENDENCE_REVIEW_MBS308*.md;
> - MB r1 namespace or runtime/host observations;
> - history/;
> - Cell-309 material.
>
> Catch file-path attribution, introduced blockquotes, quoted text, possessive attribution, and verbatim content. Do not display excluded content; report only paths, line ranges, structural features, and classifications.
>
> Prepare:
>
> 1. Sanitized input set S3, preserving line numbers where possible;
> 2. Manifest R4 with exactly 40 entries and all new byte counts and SHA-256 values;
> 3. A self-contained A6C-E17 that states:
>    - what counts as excluded-source content;
>    - what bare source names, gate labels, role lists, and generic terms do not count;
>    - that candidates must fetch only the sanitized R4 inputs;
>    - that any excluded-source material reaching them is a stop condition;
> 4. Owner decision, receipt, readiness-matrix bookkeeping, and ledger draft.
>
> Keep the canonical brief, original files, S1/S2, R1/R2/R3, and E16 unchanged. Do not launch a candidate, fetch excluded sources, fetch Phase 2 inputs, or send a proceed instruction.

## 2. Method (read-only; local git objects only)

* **Inputs.** All 40 R3 inputs were read from their git objects at manifest R3's pins (`558a3dbd`, `eb93d4f1…4fa1`):
  **40/40 MATCH**.
* **Tail-figure scan.** The confined scan (scanner `e103c196`, configuration `ab0104c6`, counts only) found **0
  findings** in 35 text and 5 py files. No committed tail figure or MB r1 value pattern is present.
* **Families screened:**

  | family | pattern basis |
  |---|---|
  | E1″ register | `COORDINATOR_EXPOSURE_DISCLOSURE`, "E1″ register", "holder/disclosure/exposure register" |
  | `audit/` | path |
  | `REVIEW_EXECUTION_INTERRUPTION*` | name |
  | incident review | `INCIDENT_INDEPENDENCE_REVIEW_MBS308*`, "incident review", "incident source" |
  | MB r1 | the namespace path, and MB r1 lines carrying observation vocabulary |
  | `history/` | path |
  | Cell-309 | name |
  | B2 | B2Q, B2S, B2 file names |

* **Attribution features:**
  * the source's path followed by a line or section citation;
  * a blockquote introduced by a line that names the source;
  * a blockquote carrying the source's path;
  * quotation marks;
  * possessive after the source's name;
  * an attribution verb after the name;
  * for MB r1, observation vocabulary with an assertion verb, unnegated;
  * **verbatim propagation**: two or more six-word shingles shared with a line selected for redaction, anywhere in
    the 40 inputs.
* **Quote provenance.** Each blockquote was compared by shingles with every other input, to tell quotations of
  allowlisted governance from quotations of excluded sources.
* **Displayed to the recorder:** line numbers, line types and lengths, section headings, token families, feature
  flags and counts. **No content line of any flagged passage was displayed.** No excluded source was fetched, read,
  listed or hashed.

## 3. Findings

### 3.1 Redacted in S3: 34 lines in 6 entries

| entry | file (original at `4f814796`) | lines | class | basis |
|---|---|---|---|---|
| 9 | `governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1.md` | 41 + 43 | A | an incident-review path with line citation, introducing a quote |
| 9 | same | 49 + 51–54 | A | an incident-review mention introducing a 4-line quote |
| 9 | same | 75 + 77–78 | A | a REVIEW_EXECUTION_INTERRUPTION path with line citation, introducing a quote |
| 9 | same | 106 | V | repeats the line 78 quote (5 shared shingles) |
| 9 | same | 150 | C | a REVIEW_EXECUTION_INTERRUPTION path with line citation |
| 10 | `governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1_ERRATUM_E1.md` | 44–45 | C | a REVIEW_EXECUTION_INTERRUPTION line citation; the list item continues on line 45 |
| 11 | `registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md` | 75–77 | K | an incident-review mention opening a quoted span; the source is not established |
| 11 | same | 86 | O | MB r1 with observation vocabulary and an assertion verb, unnegated (conservative) |
| 12 | `registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1_ERRATUM_E1.md` | 24–28, 30–32 | O | two quoted paragraphs: MB r1 with observation vocabulary and assertion verbs, unnegated (conservative) |
| 23 | `governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5.md` | 239–241, 243–244 | Q | a blockquote carrying the incident-review path; it is not a copy of any allowlisted text. Line 242, a blank quote line, is unchanged |
| 23 | same | 266, 275 | C | REVIEW_EXECUTION_INTERRUPTION line citations, inside quotations of entry 9 line 150 and entry 10 line 44 |
| 23 | same | 282–284 | K | quoted text naming Cell-309; the source is not established (conservative) |
| 25 | `governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5_ERRATUM_E2.md` | 62–64 | K | a quoted paragraph naming the incident review; the source is not established (conservative) |

**Classes:**
* A: attributed by an introduced quotation;
* C: attributed by file path and line citation;
* Q: a quoted block carrying an excluded-source path;
* V: verbatim repetition;
* O: a possible MB r1 target-run observation;
* K: quoted text naming an excluded source, source not established.

### 3.2 Kept, as bare naming (allowed under A6C-E17.6): 33 lines

The lines below are listed as entry:line.

| family | lines |
|---|---|
| E1″ register | 1:17, 6:28 (S1), 7:21 (S1), 8:134, 9:36, 9:148, 23:264, 39:14 |
| `audit/` | 8:133 |
| `REVIEW_EXECUTION_INTERRUPTION*` | 1:17, 8:133, 39:14 |
| incident review | 6:28, 6:32 (S1), 7:21 (S1), 8:134, 9:145, 23:353 |
| MB r1 namespace path | 8:122, 8:135, 29:67, 39:38–42 |
| `history/` | 6:140 (S1) |
| Cell-309 | 1:15, 1:17, 6:32 (S1), 7:21 (S1), 9:182, 23:35 |

* None of these lines carries a path-and-line citation, an introduced or carrying quote, a possessive or an
  attribution verb.
* **Entry 23 line 264** names the register's path inside a blockquote. That blockquote is a quotation of entry 9 §4
  (10 shared shingles with entry 9 line 148, which is itself a bare naming). It is kept in both places.
* **73 further lines** use "MB r1" only as the campaign name. They carry no unnegated observation assertion, and no
  numbers paired with observation vocabulary outside negated policy-constant tables. They are kept under
  A6C-E17.6.

### 3.3 Checks on the would-be R4 set

* **S3 copies:**
  * only the mapped lines differ, plus one trailer line each; line numbers are preserved;
  * the generator is deterministic.
* **The R4 set as a whole:**
  * no remaining excluded-source attribution by path and line, introduced or carrying quote, possessive or verb;
  * **no unnegated MB r1 observation-assertion line**;
  * **0 lines** share two or more six-word shingles with any redacted line;
  * no B2 pointer outside markers (as in the candidate 6 audit).
* **Confined scans:** S3, R4 and A6C-E17, findings 0, PASS.

### 3.4 Scope bearing (facts for the owner; no judgment)

* **Entry 23** is S5 material. Its §6, "Incident-independence (S12)", loses lines 239–244 and 282–284.
* **Entry 9** loses its quotations of omitted governing texts at lines 43 and 51–54, plus lines 77–78 and 106.
* **Entry 12** loses two quoted paragraphs. **Entry 25** loses lines 62–64.
* Items that rely on these lines become NOT_DETERMINABLE under A6C-E17.4. Which Part A–C items those are has not
  been checked.

## 4. New artifacts (all under `level4/closure_proofs/p5y_k5_cell308_research/`)

**Sanitized input set S3, commit `fcd35d8c02fae94214dc9d4d66562dce8687aab6`:**

| path (`ledger/briefs/A6C_SANITIZED_INPUTS_S3/`) | entry | bytes | sha256 | blob |
|---|---|---|---|---|
| `SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1.A6C_SANITIZED_S3.md` | 9 | 12,532 | `1dd58e78307721c819bdfccd06a6e04ff04cd109423ff0c3de323784ceb3c62f` | `e98f9e4c80062e930ca769b1bcb0697af58888a2` |
| `SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1_ERRATUM_E1.A6C_SANITIZED_S3.md` | 10 | 3,463 | `ae0f2681925b47c8280da604ea65686cfb1eaff7b77c1b1a4270f609d1c235f1` | `ff23da3c5d2fe8eb632ecbd0077d88deea3c694c` |
| `SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.A6C_SANITIZED_S3.md` | 11 | 8,197 | `31210f4113d7e8e3bb9a3f05348f9043157126f1c8e653ab66d23dfbd41ea036` | `17be8bb8c4b955787e8c14f30a8c74e438fc9fa4` |
| `SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1_ERRATUM_E1.A6C_SANITIZED_S3.md` | 12 | 5,478 | `39eae86aaad87cd6faa4895778f89dd6c87a8799d7fa6e05c86017f22334bf1c` | `23e9d96a8a496103bbaa6e9199f86ebff66e0f9d` |
| `PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5.A6C_SANITIZED_S3.md` | 23 | 50,124 | `288c54e64348e839177d7bf0a9cc639d22a685e5e46a99a50ab47b15cc98cc42` | `a5a8d652cb1e77fd94406bdb78bd2a4dcc46d23d` |
| `PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5_ERRATUM_E2.A6C_SANITIZED_S3.md` | 25 | 7,946 | `0b35fe2f53eac58c49f6198306daf366d5a6415a0cb310d7689f74185751737c` | `52653556127b2a329ff034856b009910f7f55ef3` |
| `a6c_sanitize_s3.py.txt` (the generator) | — | 4,456 | `4d4ab5e0d2ab0100ecc8f4a42458a13ed191a3c0597e974e19898a4062d6c50b` | `968f27eacbc8fea934476de5ba276de007767dc2` |

**Manifest R4, commit `3c037959c21dbdebd279f6200b2d1c7910a7975c`:**

| path | bytes | sha256 | blob |
|---|---|---|---|
| `ledger/briefs/A6C_PHASE2_MANIFEST_R4.json` | **21,629** | **`a1018065c2d2a0add2c3074cd6ad0d3dba9c74b5bfe89061129a0457ae171e24`** | `0bdc8ff63227be1e5760a66227f6ba7874561347` |
| `ledger/briefs/A6C_SANITIZED_INPUTS_S3/a6c_derive_manifest_r4.py.txt` (the generator) | 2,984 | `f2649c215cc49ffb356ff975a4cf4ce9a8f4da56dc668702a332fb9f829d1985` | `36b6ad826d234f5a1a337917a7c64a2a2c709baa` |

* R4 is derived from R3. **Exactly 40 entries, numbered 1–40** (39 Part 1, 1 Part 2).
* **Only entries 9, 10, 11, 12, 23 and 25 differ from R3.** The S1 entries 4, 6, 7 and the S2 entry 24 are unchanged.
* **Byte-verified 40/40** against git, including each URL. Deterministic across two runs.

**Proposed brief erratum A6C-E17** (in the same commit as this record):

| path | bytes | sha256 | blob |
|---|---|---|---|
| `ledger/briefs/A6C_REDERIVATION_CLOUD_R1_ERRATUM_A6C_E17.txt` | 8,212 | `e7d173b30d6794592bb6cb071984e25674b39babb3401fe26b373dd416c7f98b` | `05812c7cf7dca153699ec84ef544b298aa22a3e9` |

* A6C-E17 is **self-contained**. For future candidates it replaces A6C-E14, A6C-E15 and A6C-E16 in full.
* It states:
  * what counts as excluded-source content (A6C-E17.5);
  * what does not count: bare names and paths, gate labels, role lists and generic terms (A6C-E17.6);
  * that only the 40 R4 URLs may be fetched in Phase 2 (A6C-E17.1);
  * that any excluded-source content reaching a candidate is a stop (A6C-E17.7).
* Phase 1 is brief-only. A6C-E17 and R4 are fetched after eligibility and proceed. Candidates 1–6 are declined.
* Every pinned value was cross-checked against git.

## 5. Unchanged

* the canonical brief;
* all original files;
* S1 and S2;
* manifests R1, R2 and R3;
* A6C-E14, A6C-E15 and A6C-E16.

## 6. Prepared, not issued

These are in the owner's working materials:
* the owner decision adopting A6C-E17, S3 and R4;
* its receipt;
* readiness-matrix erratum **RM-E18**;
* a ledger-line draft.

## 7. Not done

* No candidate is launched. Candidate 6 is not reused.
* No excluded source and no Phase 2 input is fetched. No proceed instruction is sent.
* Nothing is adopted. The register was not read.
