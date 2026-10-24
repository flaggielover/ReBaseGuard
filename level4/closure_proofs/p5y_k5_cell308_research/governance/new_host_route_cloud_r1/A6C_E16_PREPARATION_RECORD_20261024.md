# A6c protocol revision A6C-E16: preparation record (sanitized input set S2, manifest R3, proposed brief erratum A6C-E16) (Cell-308 Cloud route r1), 2026-10-24

**Status: OWNER-DIRECTED PREPARATION · RECORDED BY claude_cloud_recorder_20261022 · PROPOSED · NOT IN FORCE.**
`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The owner's direction (verbatim, as issued on 2026-10-24)

> Do not launch a new candidate yet.
>
> Prepare protocol revision A6C-E16 to resolve N1–N3.
>
> 1. Put the B2-derived classification rule directly into the candidate-facing erratum:
>
> B2-derived material means explicit B2Q/B2S or incident-review attribution, a pointer to those B2 files, or verbatim content from those sources. Bare T6, M1–M8, mitigation, ruling, gate-B2, or role-list terms without that attribution are not B2-derived.
>
> 2. Resolve N2 conservatively by sanitizing entry 24 line 115 in a new sanitized copy. Preserve the original entry unchanged.
>
> 3. Keep the already sanitized entries 4, 6 and 7 unchanged. Do not fetch B2 sources.
>
> 4. Generate a new manifest R3 with exactly 40 entries, replacing only the affected sanitized paths and hashes. Verify every entry against the pinned git object and record the manifest byte count and SHA-256.
>
> 5. Make A6C-E16 explicitly govern the new manifest and sanitized input set. State that future candidates must fetch the canonical brief only during Phase 1, and fetch E16 and manifest R3 only after eligibility and proceed authorization.
>
> 6. Prepare the owner decision, receipt, and the next readiness-matrix erratum with an unambiguous namespace.
>
> Do not launch a candidate, fetch Phase 2 inputs, issue eligibility, or send a proceed instruction.

## 2. How N1–N3 are resolved

| note | resolution |
|---|---|
| **N1** (S1 redacts a superset of the rule) | **S1 is kept unchanged.** A6C-E16.4 tells candidates that S1 was redacted under a broader rule, and S2 conservatively, so a marker is not evidence that its line was B2-derived |
| **N2** (entry 24 line 115) | **Sanitized conservatively in a new set S2.** Line 115 is replaced by a class I marker ("possible incident-review attribution, redacted conservatively"). The original entry 24 is unchanged |
| **N3** (the rule is not candidate-facing) | **The rule is in A6C-E16.5**, word for word as the owner gave it, with an ASCII hyphen in "M1-M8" because the brief files are ASCII. A6C-E16.6 ties the stop condition to that rule |

## 3. Entry 24 (read-only; line structure only, content not displayed)

* **Source.** `governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5_ERRATUM_E1.md` at
  `4f814796`: 7,474 bytes, `b4728654…f41b`, verified against manifest R2; 115 lines.
* **Line 115** is its last line: a 72-character paragraph in section "E1.9 — not changed".
* **After sanitization:**
  * outside the marker, no line of the S2 copy pairs "incident review" with an attribution verb;
  * only line 115 differs from the original, plus the trailer.

## 4. New artifacts (all under `level4/closure_proofs/p5y_k5_cell308_research/`)

**Sanitized input set S2, commit `51388ecf04180123ac3cfbd60b106436121eab60`:**

| path | bytes | sha256 | blob |
|---|---|---|---|
| `ledger/briefs/A6C_SANITIZED_INPUTS_S2/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5_ERRATUM_E1.A6C_SANITIZED_S2.md` (entry 24) | 7,935 | `7388271653e61c4a6870208c53559352643a9ec2fa9a33184b6373607b867066` | `3eea3b948b6631323fd69655399213b806fc5ee9` |
| `ledger/briefs/A6C_SANITIZED_INPUTS_S2/a6c_sanitize_s2.py.txt` (the generator) | 3,224 | `3cc62761b16d3ee6029a22c3471f98864aca13af7b7093fae0fd7d273dbf3627` | `a5ed77ad151f968f49fd3e6777938357d3966cb7` |

**Manifest R3, commit `558a3dbd32623ee152feef7f74218813eafb8030`:**

| path | bytes | sha256 | blob |
|---|---|---|---|
| `ledger/briefs/A6C_PHASE2_MANIFEST_R3.json` | **21,101** | **`eb93d4f17e745bbba818a17f9f86f0e29880ba7b535d61db8fb0412553a04fa1`** | `a8cae0176a9888970eb1d7dccee10142999cacad` |
| `ledger/briefs/A6C_SANITIZED_INPUTS_S2/a6c_derive_manifest_r3.py.txt` (the generator) | 2,618 | `545bd61117c1391b150d8631221cb5404c5ee8c2e9c7007adc2b1243e4af306d` | `346c5fc3bb1e61585974660d71ad64e68e14106d` |

**Proposed brief erratum A6C-E16** (in the same commit as this record):

| path | bytes | sha256 | blob |
|---|---|---|---|
| `ledger/briefs/A6C_REDERIVATION_CLOUD_R1_ERRATUM_A6C_E16.txt` | 6,461 | `69faff4c2c3283ee82e90e7591e24a656feeb9c1273a10e575dbc0f33795313e` | `d1dfb7c4fcb2bd0ca4fe9ea6e2c2d44bb85fd753` |

## 5. Checks

* **Manifest R3:**
  * derived mechanically from the adopted manifest R2 (`0c6c0a30`, `a1247013…07cf`);
  * **exactly 40 entries, numbered 1–40** (39 Part 1, 1 Part 2);
  * **only entry 24 differs from R2**;
  * entries 4, 6 and 7 keep their S1 bindings (`90d12cef`);
  * **byte-verified 40/40** against the pinned git objects, including each URL;
  * deterministic across two runs.
* **S2:** only line 115 differs, plus one trailer line. Deterministic.
* **A6C-E16:** every pinned commit, byte count, SHA-256 and URL was cross-checked mechanically against git, and the
  rule text against the owner's wording.
* **Confined scans** (scanner `e103c196`, configuration `ab0104c6`): S2, R3 and this commit's files, findings 0,
  PASS.
* **Unchanged:**
  * the canonical brief;
  * the original entries 4, 6, 7 and 24;
  * the S1 files;
  * manifests R1 and R2;
  * A6C-E14 and A6C-E15.
* **A6C-E16's design.** It is **self-contained**. For candidates appointed after its adoption, it replaces A6C-E14
  and A6C-E15 in full, restating their operative provisions. So a future candidate fetches only:
  * the brief, in Phase 1;
  * A6C-E16 and manifest R3, after eligibility and proceed.

  A6C-E16 cannot pin its own digest, so the owner's proceed instruction supplies it (A6C-E16.1).

## 6. Prepared, not issued

These are in the owner's working materials:
* the owner decision adopting A6C-E16, S2 and R3;
* its receipt;
* readiness-matrix erratum **RM-E17**.

## 7. Not done

* No candidate is launched. No eligibility is issued. No proceed instruction is sent.
* No B2 source and no Phase 2 input is fetched.
* Nothing is adopted. The register was not read.
