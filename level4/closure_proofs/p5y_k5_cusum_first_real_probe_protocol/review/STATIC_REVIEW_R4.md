# Independent static review of the r4 packet (freeze 852b2d65, freeze record cf09d6fc): FAIL

**Reviewer.** A separate read-only agent session. Its throwaway repositories used only the harness's stated
substitutions and were deleted afterwards. Science: **PASS**, unchanged since r1; F2 is a faithful genuine activation.
Governance: **FAIL**.

## Refused variants

| variants | caught by |
|---|---|
| V04, V06 | P06 |
| V05 | P06 |
| V11 | P02 / P03 / P04 / P11 |
| V12 | P03 |
| V13, V15 | P04 |
| V16, V17, V20 | P11 |
| V21, V22, V25 | P04 / P11 |
| V23 | P02 / P04 |
| S1 | P11 |
| S2 | P09 |
| S3, S4 | P09 / P11 |
| S5, S6 | P11 / exception handling |
| N2 | P03 / P04 / P09 |
| N6 | `get-url` expands the rewrite |

## Permitted variants

| variant | what it did | status |
|---|---|---|
| N1 | `git replace --graft` / `info/grafts` rewrites the commit graph the publication check trusts | local, real |
| N3 | ledger read at HEAD, not at the published tip | local, real |
| N4 | LAUNCH_NOTICE not single-use | real |
| N5 | allow-listed mirror path is a symlink to the local repository | local, real |
| N7 | inherited `GIT_CONFIG_*` / `uploadpack` environment | local, real |
| N8 | duplicate JSON keys in the ledger (last value wins) | real |
| N9b | unknown or misspelled seal events ignored | real |
| N10 | `ls-remote` tail match on a crafted ref name | needs a push; cheap fix |
| N11 | executor source stubbed before the amendment, replaced after it | real |
| N12 | decorated verdict lines ignored by the parser | minor |
| N13 | type-lax equality (bool/int/float) | real, low |
| N15 | forged ignored `.pyc` next to a byte-equal source | local code execution |

**Also:** the evidence and the amendment are never reviewed (only the sources are). The in-process verify
obligation conflicts with the supervisor creating slot-N first.

## Required repairs listed

1. Clean git environment; refuse replace refs, grafts, shallow and alternates.
2. Exact `ls-remote` ref parsing; refuse a symlinked mirror; GitHub confirmation.
3. Read the ledger from the published tip.
4. Single-use notice (`SLOT_OPENED`).
5. Strict JSON: no duplicate keys; allow-listed events and keys.
6. Pins checked against their blobs at the amendment commit; a second review naming the amendment sha256.
7. Canonical-bytes template comparison; `Z` timestamps.
8. No untracked or ignored files in the code tree; run with `python -I -B`.
9. Ordering: verify, then create the slot.
10. Tests for the new variants.
