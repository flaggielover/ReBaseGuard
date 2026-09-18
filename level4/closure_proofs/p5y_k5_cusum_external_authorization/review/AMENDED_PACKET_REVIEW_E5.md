# E5 amended-packet review: first real CUSUM probe, r4

This is prerequisite E5 of `EXECUTION_BINDING_R4.json`: re-run the prelaunch verifier and an independent static review
on the amended packet, before any authorization.

Reviewer: the same fresh-context Claude session that wrote `AMENDMENT_REVIEW.md`. I am not a human, and I am from the
same model family as the preparer. I did not use the preparer's scripts or intermediate files. Every result below
comes from my own clones and my own commands.

Reviewed against:
- repository: GitHub `flaggielover/ReBaseGuard`, branch `p5y-postk1-frontier`;
- tip: `842d35651f5616d20a1402d4d06b65b8ab22952e`, confirmed by `git ls-remote` of GitHub, by a fetch into my own
  clone, and by a fresh clone on vultr-02.

Review time: 2026-09-18, about 15:20 UTC.

## What changed since the amendment review

`git diff ff3b6a4a..842d3565` adds exactly three files and changes nothing else:

| commit | file |
|---|---|
| 585c9a01 | `level4/closure_proofs/p5y_k5_cusum_external_authorization/README.md` |
| 585c9a01 | `level4/closure_proofs/p5y_k5_cusum_external_authorization/review/AMENDMENT_REVIEW.md` |
| 842d3565 | `level4/closure_proofs/p5y_k5_cusum_first_real_probe_protocol/protocol/EXECUTION_BINDING_AMENDMENT.json` |

Each of these commits has one parent: ff3b6a4a, then 585c9a01. No executor, adapter, frozen or science file changed,
so every finding of `AMENDMENT_REVIEW.md` still applies to the same bytes.

## 1. The committed amendment matches the reviewed draft

- **Keys and fields.** The committed file has exactly the draft's 11 keys, with no duplicate JSON keys. Only two fields
  differ from the draft:
  - `independent_review_sha256` =
    `9240e7b5163144476b572b39404866d8787ac0befc8bb3951a98a1dd3fc692a9`. This is the sha256 of the committed review
    file, which is byte-identical (`cmp`) to the file I wrote;
  - `independent_review_verdict` = `PASS_WITH_SCOPE_LIMITATION`, which is exactly my verdict.
- **Unchanged content.** The sources map, the evidence map, the entries, the schema, the status, the science sha256
  and the ack are all equal to the draft.
- **Amendment file.** Its sha256 is
  **`0c6809a2d56fc15603fc15a27bf79cc0e94977bf4370cacee9740295f1972bb4`**. The file is 4181 bytes, pure ASCII, with a
  final newline. The copy on vultr-02 in a fresh clone has the same sha256.

Result: **PASS.**

## 2. Committed once, after the freeze, and published

- **Committed once.** The amendment was introduced by 842d3565, and that is the only commit that touches it on any
  GitHub branch. It is a regular 100644 file, not a symlink.
- **After the freeze.** 852b2d65 is a strict ancestor of 842d3565.
- **Published.** 842d3565 is the GitHub tip. On vultr-02 the frozen verifier's own publication read worked: its
  `ls-remote` of the allow-listed GitHub origin returned 842d3565, equal to `origin/p5y-postk1-frontier`.
- **Commit time.** The amendment's committer time is 2026-09-18T15:13:31Z (epoch 1789744411). This is the lower bound
  for a later `AUTHORIZATION_UTC`.

Result: **PASS.**

## 3. The review was committed first

- **Order.** The review was introduced by 585c9a01, the parent of the amendment commit, and was not touched after
  that. It is a regular file, and the tree is clean.
- **Parsing.** The frozen `review_lines` parses it to exactly one verdict line (`PASS_WITH_SCOPE_LIMITATION`) and
  exactly one sources line.
- **Sources hash.** The sources line names
  `b437adba64cd4098d6f8998f01af159e7092c14b6597c219cc9ab130da97c015`. I recomputed this value from the committed map
  with the frozen `probe_rules.canonical`, and it matches.

Result: **PASS.**

## 4. The 20 pinned files

The pinned files are the 14 sources, the 5 evidence files and the review. For each one I checked that:
- it exists at its pinned sha256;
- it is a regular 100644 file and not a symlink;
- it has a clean working tree;
- it was introduced exactly once;
- its introducing commit is an ancestor of 842d3565, or equal to it.

The introducing commits are:
- the executor sources: 8ffcfaff, 2b9fdf8d, 52769488;
- `k5_minimality.py`: e8680998;
- `k5b_check.py`: d7d3c08b;
- the adapter: a2bb280d;
- the r5 evidence: f83cd182;
- the r5 review: 43767695;
- the E6 evidence: ff3b6a4a;
- the amendment review: 585c9a01.

Result: **PASS**, with no problems.

## 5. Frozen P06 and the full frozen verifier

I used the frozen verifier file `prelaunch_verify.py` (sha256 `54b198bc...`, unmodified) and `probe_rules.py`
(`5ce87758...`).

**`check_P06` in process, on my clone at 842d3565.**

| authorization input | result | detail |
|---|---|---|
| `PRODUCER_R4_IDENTITY.executor_binding_sha256` = `0c6809a2...` | PASS | "executor bound, qualified and independently reviewed" |
| the template's value, `SET_AT_ACTIVATION` | FAIL | "authorization names another executor binding" (the only clause) |

**Full verifier on vultr-02.** I ran it from a fresh GitHub clone in the new directory `/var/tmp/e5review-r1/repo`,
with `/root/work/rbg-cusum-aux5-venv/bin/python -B code/prelaunch_verify.py`, with its defaults: the inactive template
as authorization and no `--out`.
- Verdict: **REFUSED**, exit code 3.
- Primary reason: `P01: EXECUTION_NOT_AUTHORIZED: EXECUTION_AUTHORIZED is not true`.

| check | pass | detail |
|---|---|---|
| P01 | no | EXECUTION_NOT_AUTHORIZED: EXECUTION_AUTHORIZED is not true |
| P02 | no | authorization is not the regular file at protocol/AUTHORIZATION_ACTIVE.json; activation fields PROTOCOL_FREEZE_COMMIT, AUTHORIZED_BY, AUTHORIZATION_UTC and executor_binding_sha256 not filled |
| P03 | no | PROTOCOL_FREEZE_COMMIT != introducing commit 852b2d65c933 |
| P04 | no | AUTHORIZATION_ACTIVE.json not committed exactly once, unchanged and regular |
| P05 | yes | all protected hashes match |
| P06 | no | authorization names another executor binding |
| P07 | yes | host runtime identity matches |
| P08 | yes | no conflicting producer |
| P09 | yes | no sealed record for this protocol |
| P10 | yes | CPU ceiling valid |
| P11 | no | next slot slot-1 lacks exactly one committed LAUNCH_NOTICE (and nothing else) in the ledger |
| P12 | no | no valid AUTHORIZATION_UTC |

The report also records:
- the derived freeze commit is 852b2d65c9332facd59771da7940ab429a7e2f2f;
- the science sha256 is `9ace6896...`;
- HEAD and the published tip are both 842d3565.

Reading of the result:
- **P06 fails only on the expected clause.** That clause will clear only when a committed authorization names
  `0c6809a2...`.
- **Every other failure is expected.** P01, P02, P04, P11 and P12 fail only because the authorization is the inactive
  template, and no authorization, ledger or LAUNCH_NOTICE exists yet.
- **P03 fails on one clause only.** That clause is about the template's `PROTOCOL_FREEZE_COMMIT` placeholder. Every
  other freeze clause holds: the first parent is the literal, template and binding are once-only, the freeze record
  is good, the packet code is byte-equal, and the freeze is published.
- **Host checks pass today.** P07 (host runtime contract), P08, P09 and P10 all pass on vultr-02.

Both clones stayed clean (`git status --porcelain` empty).

Result: **PASS**, as expected.

## 6. No activation, and no result

**Git history.** I fetched all 15 GitHub branches plus `refs/pull/1/head` again and scanned their full name history
(20,919 distinct paths). None of the following exist:
- `AUTHORIZATION_ACTIVE.json`, `COUNTERSIGNATURE_ACTIVE.json` or `ATTEMPT_LEDGER.jsonl`;
- any path containing "sealed";
- any `k5-first-real-probe` path;
- any protocol `ledger/` or `evidence/` path;
- any executor `authorization/` path.

The only new activation-family path is the amendment itself, plus its review.

**Host.**
- `/root/work/k5-first-real-probe` does not exist.
- A search of `/root/work` and `/var/tmp` finds no authorization, countersignature, ledger or sealed-record file.
  - The only activation-family files it finds are two copies of the committed amendment: one in my clone, and one in
    `/var/tmp/extauth-pkt/e5`. That second directory is not mine. It is a clean checkout at 842d3565, and its copy
    has the same sha256 `0c6809a2...`.
- `/var/tmp/k5gov` is empty.

**Identities.**
- The science file still has sha256 `9ace6896d70b7a17225c03cd6d8092e3d33089d001dd3e2736894dd866f3780a`. It was
  introduced only by 852b2d65 and never touched on any branch.
- The executor identity recomputes to `ef1c86e40bff0b13e40e924ba27d0841aff71f7344d114f71f517ab3adfdd41b`.
- There is no change to the executor's `code/` or `config/` since a16d22b5, and all 279 `EXECUTOR_PINS` match.
- The committed guard policy is still `DENY`.

Result: **PASS.**

## Concerns and notes, ranked

1. **MEDIUM (procedure, next step).**
   - `AUTHORIZATION_ACTIVE.json` must set `PRODUCER_R4_IDENTITY.executor_binding_sha256` to exactly
     `0c6809a2d56fc15603fc15a27bf79cc0e94977bf4370cacee9740295f1972bb4`.
   - The countersignature's `execution_binding_amendment_sha256` must name the same value.
   - `AUTHORIZATION_UTC` must be:
     - at or after 2026-09-18T15:13:31Z;
     - within the hour before the authorization commit;
     - not in the future.
   - The authorization may be created only after a separate explicit user authorization message, as its template
     requires.
2. **LOW.** The pinned files (the 14 sources, the 5 evidence files and the two review-namespace files) are now
   permanently immutable. Editing any of them, including a typo fix to `AMENDMENT_REVIEW.md`, makes P06 refuse.
   - The README next to the review is not pinned.
   - E5 records may be added to the external-authorization namespace, as the README plans. They must not be added
     under the protocol namespace's `evidence/` or `ledger/`, and must not use an activation or sealed-record file
     name.
3. **LOW.** A few host facts can drift before launch and must be re-checked by the final preflight: P07 (host runtime
   contract, including libc, the kernel and the venv), P08 and P12. They pass today.
4. **INFO.** This run used the real GitHub publication read. That narrows one r5 scope limitation (the read was
   simulated during qualification), but a real end-to-end launch is still not exercised.
5. **INFO.** My read-only scratch directories `/var/tmp/amendreview-r1` and `/var/tmp/e5review-r1` remain on
   vultr-02. They hold clones, adapter outputs and the verifier's stdout report, and nothing the verifier reads.

E5_AMENDED_PACKET_REVIEW: PASS
