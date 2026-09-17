# Independent static review of the r3 packet (freeze 38234751, freeze record 0c3d1f29): FAIL

**Reviewer.** A separate read-only agent session. It built its throwaway repositories under a scratchpad and deleted
them afterwards. Science: **PASS**, unchanged since r1. Governance: **FAIL**.

## Forgery variants

**Refused.**

| variants | caught by |
|---|---|
| r2 forgery (V01) | P04 / P06 / P11 |
| collapsed commits (V02) | P04 |
| unpublished commits (V03) | P04 / P11 |
| review file FAIL vs amendment PASS (V04) | P06 |
| review naming other sources (V06) | P06 |
| untracked or late sources (V07, V08) | P06 |
| missing adapter pins, extra amendment key (V09, V10) | P06 |
| extra authorization key (V11) | P02 |
| authorization UTC before the amendment (V13) | P04 |
| future authorization UTC (V15) | P04 |
| launch-notice games (V16, V17, V20) | P11 |
| ledger rewrite or delete (S3) | P09 / P11 |
| committed-then-deleted seal (S4) | P09 |
| slot-directory games (S5) | P11 |
| malformed authorization (S6) | exception handling / P01 |

**Permitted without fabricated reviews** (outside the declared trust model):

| variant | what it did |
|---|---|
| V21 | `--remote-ref HEAD` on an unpublished chain |
| V22 | local `update-ref` of `origin/p5y-postk1-frontier` |
| V25 | chain published on another ref |
| V12 | template edited in a later published commit, so the authorization drifts with it |
| V19/V23 | authorization supplied through a symlink |
| V05 | review file with duplicate `REVIEW_VERDICT` lines (the first wins) |
| S1/S2 | host `RUN_FAILED.json` contradicting the committed ledger; a VOID seal deleted on the host while the ledger's OUTCOME still carries its sha256 |

**Harmless or minor:** V14 (commit dated in the future), V18 (notice in the same commit as the authorization), V24
(backdated chain).

## Required repairs

1. Pin the remote ref, no CLI override, and confirm it against `git ls-remote`.
2. Literal freeze anchor.
3. Template introduced by the freeze commit and never touched.
4. Refuse symlinks on every governed path.
5. Exactly one verdict line and one sources line in the review file.
6. The ledger OUTCOME governs: cross-check `arithmetic_started`, pin the `RUN_FAILED.json` sha256, and treat any
   non-null `sealed_record_sha256` as sealed.
7. Tests for V05, V12, V21/V22, V23, S1/S2, plus P09/P12 inside F2.

**Executor-amendment items:**
- `cpu_soft_limit_reached` derived from child CPU time, since a hard-limit SIGKILL must not count as an external signal.
- A post-reboot writer for `RUN_FAILED.json`.
- No E3 evidence named `*_RECORD_SEALED.json`.

## Disposition

Addressed by the r4 re-freeze. r3 was never authorized or executed.
