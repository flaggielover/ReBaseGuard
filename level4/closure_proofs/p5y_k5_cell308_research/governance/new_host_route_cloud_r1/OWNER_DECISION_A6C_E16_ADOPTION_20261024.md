# Owner decision: adoption of A6c brief erratum A6C-E16, sanitized input sets S1 and S2, and manifest R3 (Cell-308 Cloud route r1), 2026-10-24

**Status: OWNER DECISION (the owner's words recorded verbatim in §1) · RECORDED BY claude_cloud_recorder_20261022.**
§1 governs. §2 applies it, and §1 prevails over it if they differ. `new_target_evaluations = 0` ·
`cell309_activity = none`.

```text
A6C-E16                  ADOPTED (in force from this decision; replaces A6C-E14 and A6C-E15 for future candidates)
A6C_SANITIZED_INPUTS_S1  ADOPTED (entries 4, 6, 7; unchanged)
A6C_SANITIZED_INPUTS_S2  ADOPTED (entry 24)
A6C_PHASE2_MANIFEST_R3   ADOPTED and PINNED (manifests R1 and R2 not used)
B2 CLASSIFICATION RULE   ADOPTED exactly as written in A6C-E16.5
A6C                      BLOCKED: owner appointment of candidate 6 (not yet launched)
```

## 1. The owner's decision (verbatim, as issued on 2026-10-24)

> I adopt A6C-E16, sanitized input sets S1 and S2, and manifest R3.
>
> A6C-E16:
>
> Commit:
> 22af529c31b306a4293b77f5550c2b26298f1e3e
>
> Path:
> level4/closure_proofs/p5y_k5_cell308_research/ledger/briefs/A6C_REDERIVATION_CLOUD_R1_ERRATUM_A6C_E16.txt
>
> Bytes: 6461
> SHA-256:
> 69faff4c2c3283ee82e90e7591e24a656feeb9c1273a10e575dbc0f33795313e
>
> Manifest R3:
>
> Commit:
> 558a3dbd32623ee152feef7f74218813eafb8030
>
> Path:
> level4/closure_proofs/p5y_k5_cell308_research/ledger/briefs/A6C_PHASE2_MANIFEST_R3.json
>
> Bytes: 21101
> SHA-256:
> eb93d4f17e745bbba818a17f9f86f0e29880ba7b535d61db8fb0412553a04fa1
>
> Adopt the conservative S1/S2 sanitization and the B2-derived classification rule exactly as written in A6C-E16. Record the owner decision, receipt, RM-E17 readiness-matrix erratum, and append-only ledger line.
>
> Keep the canonical brief, original entries, S1, S2, and manifests R1/R2 unchanged. Do not launch candidate 6 yet and do not send a proceed instruction.

## 2. What it applies to

| item | value |
|---|---|
| brief erratum adopted | **A6C-E16**: `ledger/briefs/A6C_REDERIVATION_CLOUD_R1_ERRATUM_A6C_E16.txt` at `22af529c31b306a4293b77f5550c2b26298f1e3e`, 6,461 bytes, `69faff4c2c3283ee82e90e7591e24a656feeb9c1273a10e575dbc0f33795313e`, blob `d1dfb7c4fcb2bd0ca4fe9ea6e2c2d44bb85fd753` |
| manifest adopted | **R3**: `ledger/briefs/A6C_PHASE2_MANIFEST_R3.json` at `558a3dbd32623ee152feef7f74218813eafb8030`, 21,101 bytes, `eb93d4f17e745bbba818a17f9f86f0e29880ba7b535d61db8fb0412553a04fa1`, blob `a8cae0176a9888970eb1d7dccee10142999cacad`. It has 40 entries, numbered 1–40 |
| sanitized input sets adopted | **S1** at `90d12cef2b97980991888a1cde819829c9a361ea`: entries 4, 6 and 7, unchanged. **S2** at `51388ecf04180123ac3cfbd60b106436121eab60`: entry 24 (7,935 bytes, `73882716…7066`). The **conservative** sanitization of both is adopted as it stands |
| classification rule | **exactly as written in A6C-E16.5** (candidate-facing). It supersedes, as the operative text, the wording recorded in `OWNER_DECISION_A6C_E15_ADOPTION_20261024.md` §1. The substance is the same, with an ASCII hyphen in "M1-M8" |
| A6C-E16's status line | line 3 reads "PROPOSED. NOT IN FORCE until the owner adopts it by a recorded owner decision". **This decision is that record.** The file is not edited |
| effect | for every candidate appointed from now on, the A6c brief is read with **A6C-E16 alone**. A6C-E16 replaces A6C-E14 and A6C-E15 in full, and they are not inputs. **Manifests R1 and R2 are not used** |
| fetch sequence (A6C-E16.1) | **Phase 1:** the canonical brief only. **After** the owner's individual eligibility determination and proceed instruction: A6C-E16, at the commit, bytes and SHA-256 that the proceed instruction gives, then manifest R3 |
| preserved unchanged | the canonical brief (`797248fc`, `489dec78…2f0c`); the original entries 4, 6, 7 and 24 at `4f814796`; the S1 and S2 files; manifests R1 (`be78ccd5`) and R2 (`0c6c0a30`); A6C-E14 and A6C-E15 as records |
| recorder notes N1–N3 | resolved as prepared (`A6C_E16_PREPARATION_RECORD_20261024.md` §2) |

## 3. State and non-effects

* **A6c is BLOCKED** on the owner's appointment of **candidate 6**, which is **not launched**. Candidates 1–5 and the
  A6b External Candidate are declined (A6C-E16.7).
* **Not done:**
  * no candidate is launched or appointed;
  * no eligibility is issued, and no proceed instruction is sent;
  * no B2 source and no Phase 2 input is fetched;
  * nothing else is adopted, and no result exists;
  * the register was not read.
