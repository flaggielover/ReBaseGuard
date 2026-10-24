# Owner decision: adoption of A6c brief erratum A6C-E15, sanitized input set S1 and manifest R2, with the B2 classification rule (Cell-308 Cloud route r1), 2026-10-24

**Status: OWNER DECISION (the owner's words recorded verbatim in §1) · RECORDED BY claude_cloud_recorder_20261022.**
§1 governs. §2 and §3 apply it, and §1 prevails over them if they differ. `new_target_evaluations = 0` ·
`cell309_activity = none`.

```text
A6C-E15                 ADOPTED (in force from this decision)
A6C_SANITIZED_INPUTS_S1 ADOPTED (entries 4, 6, 7 of manifest R2)
A6C_PHASE2_MANIFEST_R2  ADOPTED and PINNED (supersedes manifest R1 for A6c)
B2 CLASSIFICATION RULE  ADOPTED (§1)
A6C                     BLOCKED: owner appointment of a new candidate
```

## 1. The owner's decision (verbatim, as issued on 2026-10-24)

> I adopt A6C-E15 together with sanitized input set S1 and manifest R2.
>
> Adopted manifest R2:
>
> Commit:
> 0c6c0a30f321ecc3d9891acef9fb5d99e1e6ffef
>
> Path:
> level4/closure_proofs/p5y_k5_cell308_research/ledger/briefs/A6C_PHASE2_MANIFEST_R2.json
>
> Bytes: 20981
> SHA-256:
> a12470137f0f34c0a687a07c2b8f5e45517acd29ffc377143c50ae2e6e3c07cf
>
> Adopted brief erratum A6C-E15:
>
> Commit:
> a2aff3cbf92b6b5d53cadf16406d0df8ae993a22
>
> Path:
> level4/closure_proofs/p5y_k5_cell308_research/ledger/briefs/A6C_REDERIVATION_CLOUD_R1_ERRATUM_A6C_E15.txt
>
> Bytes: 4855
> SHA-256:
> 680b4d3e48328c1caa850e128899e99cd98d483e67d7c2cd4292eea9d6d8d701
>
> Adopt the following classification rule:
>
> - B2-derived material means explicit B2Q/B2S or incident-review attribution, a pointer to those B2 files, or verbatim content from them.
> - Bare T6, M1–M8, mitigation, ruling, gate-B2, or role-list terms without such attribution are not B2-derived.
> - Under this rule, entry 15 line 57 and entry 8 line 1 remain unchanged.
>
> Create the owner decision record, RM-E16 readiness-matrix erratum, receipt, and append-only ledger line. Preserve the canonical brief, original entries, sanitized S1 files, and R1 manifest unchanged.
>
> Do not launch a candidate or send a proceed instruction yet.

## 2. What it applies to

| item | value |
|---|---|
| brief erratum adopted | **A6C-E15**: `ledger/briefs/A6C_REDERIVATION_CLOUD_R1_ERRATUM_A6C_E15.txt` at `a2aff3cbf92b6b5d53cadf16406d0df8ae993a22`, 4,855 bytes, `680b4d3e48328c1caa850e128899e99cd98d483e67d7c2cd4292eea9d6d8d701`, blob `966652d6fa473f3d9835fe98ada5a0732f7b9656` |
| manifest adopted | **R2**: `ledger/briefs/A6C_PHASE2_MANIFEST_R2.json` at `0c6c0a30f321ecc3d9891acef9fb5d99e1e6ffef`, 20,981 bytes, `a12470137f0f34c0a687a07c2b8f5e45517acd29ffc377143c50ae2e6e3c07cf`, blob `1ab17821b855e8633fc25002bcb347fd1e562e9c`. It has 40 entries, numbered 1–40 |
| sanitized input set adopted | **S1** at `90d12cef2b97980991888a1cde819829c9a361ea`: entry 6 (46,480 bytes, `691eff13…d8a6`), entry 4 (14,955 bytes, `8c91a8f9…0390`), entry 7 (20,593 bytes, `979a3b97…c26e`) |
| A6C-E15's status line | line 3 reads "PROPOSED. NOT IN FORCE until the owner adopts it by a recorded owner decision". **This decision is that record.** The file is not edited |
| effect | the A6c brief is read with A6C-E14 and A6C-E15. Precedence: A6C-E15, then A6C-E14, then the brief. **Manifest R1 is no longer used for A6c** (A6C-E15.1) |
| classification rule | adopted as stated in §1. **Entry 15 line 57 and entry 8 line 1 remain unchanged** |
| preserved unchanged | the canonical brief (`797248fc`, `489dec78…2f0c`); the original entries 1, 4, 6 and 7 at `4f814796`; the S1 files; manifest R1 (`be78ccd5`, `45e2d97d…3999`); A6C-E14 |
| naming | brief errata **A6C-E\<n\>**; readiness-matrix errata **RM-E\<n\>**. This decision is recorded in **RM-E16** |

## 3. The recorder's consistency notes (facts only; nothing decided)

* **N1. S1 against the rule.** S1 was built under the broader rule in the audit record
  (`A6C_SANITIZED_INPUT_SET_S1_AUDIT_AND_PROTOCOL_PROPOSAL_20261024.md` §4).
  * Some of its class R and T redactions are unattributed mitigation-series references, or T6 analysis. Under the
    adopted rule, these are **not** B2-derived:
    * entry 6 lines 18, 155, 165, 167, 177, 197, 199, 211;
    * entry 4 lines 127, 131;
    * entry 7 lines 33, 60, 61, 69–72, 98, 100, 102, 118.
  * So **S1 redacts a superset** of what the rule requires. The owner adopted S1 unchanged, so those lines stay
    redacted.
  * Within the rule, on the line itself:
    * explicit B2Q/B2S attribution or B2-file pointers: entry 6 lines 11, 30, 51, 157, 161, 163, 170, 172, 175,
      242, 243;
    * verbatim B2Q content: entry 6 line 159.
  * Not established either way: entry 6 rows 169, 171, 173 and 174.
    * They sit in the table that line 163 introduces as B2S material, but carry no attribution on the line itself.
    * They may carry verbatim B2S mitigation wording. The token screen does not show whether they do.
* **N2. Incident-review attribution in kept lines** (counts only; content not displayed).
  * In manifest R2's inputs, outside the S1 markers, **one line** pairs the phrase "incident review" with an
    attribution verb: **entry 24** (`PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5_ERRATUM_E1.md`) **line 115**.
  * Six lines name the incident review without an attribution verb: entry 7 line 21, entry 9 lines 41 and 49, entry
    11 line 75, entry 23 line 353, entry 25 line 62.
  * A further 18 lines mention "incident" only.
  * Whether entry 24 line 115 is an **explicit incident-review attribution** under the rule is not established by the
    token screen.
* **N3. Where the rule lives.** The rule is in **this decision record**, which is not a candidate input.
  * The candidate-facing texts state it only in part:
    * A6C-E15.3 lists "the content of the historical T6 mitigation series" without an attribution qualifier;
    * A6C-E15.4 lists the term T6, ER-T6 and T6_TRANSFER, gate B2 and role-list names, but **not** bare M1–M8,
      mitigation or ruling terms.
  * So a candidate reading only the pinned texts could still treat entry 15 line 57 as triggering A6C-E15.6.
  * How the rule reaches the next candidate is for the owner: for example in the appointment and the proceed
    instruction, or in a pinned erratum A6C-E16.

## 4. State and non-effects

* **A6c is BLOCKED** on the owner's appointment of a new candidate. Its Phase 1 fetches only the brief (A6C-E15.5).
  Candidates 1–5 and the A6b External Candidate are declined (A6C-E15.7).
* **Not done:**
  * no candidate is launched, and no proceed instruction is sent;
  * no B2 source and no Phase 2 input is fetched;
  * nothing is adopted beyond §1, and no result exists;
  * the register was not read.
