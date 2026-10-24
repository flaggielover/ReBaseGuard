# A6c candidate 4: retry stop record and manifest-digest audit (Cell-308 Cloud route r1), 2026-10-24

**Status: OWNER-REPORTED STOP · READ-ONLY AUDIT BY claude_cloud_recorder_20261022 · NO RESULT · NOTHING ADOPTED.**
`new_target_evaluations = 0` · `cell309_activity = none`.

```text
A6C_CANDIDATE_4   PHASE_2_RETRY   STOPPED (manifest digest mismatch before any input fetch was relied on)
                  ROLE            ENDED: a second stop of any kind (owner decision R1)
                  RESULT          none; nothing adopted
```

## 1. The owner's report and direction (verbatim, 2026-10-24)

> Record candidate 4's retry as permanently stopped with no Phase 2 result and no adoption.
>
> The canonical A6c brief and all 40 allowlist entries were mechanically extracted successfully, but the retry protocol's expected manifest digest 45e2d97dbb07a24ef40d0a9027e2c67c08b6e44b36626742b46b9e68ec363999 does not match the candidate's mechanically derived digest 99c4983e39c759c53efda1e269bbcd285de6347f4ead64e9abe405df7d601a08.

## 2. Audit (local and parse-only; no allowlisted input fetched)

**Inputs used:**
* the canonical brief `ledger/briefs/A6C_REDERIVATION_CLOUD_R1.txt` at `797248fc` (17,499 bytes, `489dec78…2f0c`);
* the checked script `a6c_derive_manifest.py` (3,164 bytes, `78e672da064e21f14c427dc70438f2951c1c7c75fb3d7cba024f30b5e6f27572`), the one
  embedded in the R1 retry instruction.

| question | finding |
|---|---|
| **reproducibility** | the checked script on the canonical brief reproduces **`45e2d97d…3999`** exactly, under CPython 3.11.17, 3.12.3 and 3.13.16. The manifest file and the printed digest agree |
| **field order** | `sort_keys=True`. Top level: `brief_sha256`, `entries`, `part1_commit`, `part2_commit`. Each entry: `bytes`, `commit`, `n`, `part`, `path`, `sha256`, `url` |
| **entry numbering** | `n` is the integer 1–40, in brief order. 39 entries have `part` = 1 and 1 has `part` = 2 |
| **separators and quoting** | `separators=(",", ":")`: no spaces. Strings are JSON double-quoted. `ensure_ascii` is the default; the output is pure ASCII |
| **line endings and trailing newline** | exactly **one** byte `\n` (LF), at the end. **No** CR. 20,603 bytes in all |
| **representation** | `commit` is the 40-character lowercase hex string from the Part header. `path` is the repository-relative string as printed in the brief. `bytes` is a JSON integer. `sha256` is the 64-character lowercase hex string. `url` is `https://raw.githubusercontent.com/flaggielover/ReBaseGuard/<commit>/<path>` |
| **search for `99c4983e…`** | 7,818 serialization variants of the same parsed data were tried, all failing to reproduce it. They covered: field subsets; sorted and insertion order; compact and default separators; indents of none, 1, 2, 4 and tab; ASCII on and off; trailing newline none, LF or CRLF; CRLF throughout; TSV, CSV and space-separated line forms; the raw allowlist section; the whole brief; the script's stdout. **None** gives `99c4983e…`. Only the script's own form gives `45e2…` |
| **where `45e2…` is specified** | **not in the canonical brief**, which contains no manifest digest and no manifest concept. It was computed by the recorder (R1 draft, 2026-10-23), then adopted in the owner's decision R1 (`OWNER_DECISION_A6C_CANDIDATE4_RETRY_R1_20261023.md`, commit `6a56dd3f`) and carried into the owner's retry instruction |

## 3. Conclusion

* **`45e2…` is reproducible** from the canonical brief and the checked script. It is not a defect of the brief or of
  the script.
* **A byte-identical script, run on a verified brief, cannot print `99c4983e…`.** The script refuses any brief whose
  bytes differ, and its serialization is deterministic across interpreter versions. So the candidate's digest came
  from a run that differed in at least one of these ways:
  * (a) **the script's bytes differ** from `78e672da…`, for example altered in pasting, retyped or edited;
  * (b) **the digest was computed by another procedure**: its own code, or hashing a different file or form;
  * (c) **the brief guard was bypassed**, and different brief bytes were parsed.
* **The precise serialization error cannot be named from the available evidence.** No variant tried explains it, and
  the candidate's artifacts are not on the record.
* **Evidence that would identify it.** None of it contains Phase 2 input content; all of it is derived from the brief:
  1. the candidate's script file: its byte count and SHA-256;
  2. the exact command lines and the Python version;
  3. the candidate's `manifest.json` bytes, or at least their length, from which the first differing byte can be
     located;
  4. the script's full stdout.

## 4. State

* **Candidate 4:** role ended. Not to be reused.
* **No result exists, and nothing is adopted.** The canonical brief is unchanged. No new candidate is appointed, and
  no new proceed instruction is issued.
* **A6c** stays BLOCKED. A new appointment should wait until either the cause in §3 is identified, or the owner
  adopts an amended protocol that does not depend on a candidate-reproduced digest.
  * One example of such a protocol: the manifest is published as a pinned file, fetched by raw URL and verified by
    its own SHA-256.

**Not added:** a matrix erratum and a ledger line.
