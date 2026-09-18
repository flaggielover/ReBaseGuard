# Independent review of the proposed execution-binding amendment (first real CUSUM probe, r4)

Object reviewed: the draft of `level4/closure_proofs/p5y_k5_cusum_first_real_probe_protocol/protocol/EXECUTION_BINDING_AMENDMENT.json`.
It is not yet committed. I reviewed every field except the two placeholders (`independent_review_sha256` and
`independent_review_verdict`), which are to be filled from this file.

Reviewed against: GitHub `flaggielover/ReBaseGuard`, branch `p5y-postk1-frontier`, tip
`ff3b6a4a1c223fe4d0c99032fa5408cb5f64bc15`. I confirmed the tip by `git ls-remote` of GitHub and by a fresh blobless
clone. Review time: 2026-09-18 about 15:00 UTC.

## Verdict

REVIEW_VERDICT: PASS_WITH_SCOPE_LIMITATION

REVIEWED_AMENDMENT_SOURCES_SHA256: b437adba64cd4098d6f8998f01af159e7092c14b6597c219cc9ab130da97c015

The hash on the sources line is the sha256 of the canonical JSON of the draft's `executor_sources_sha256` map (14
entries). I computed it twice: once by hand with `sort_keys=True, separators=(",", ":"), ensure_ascii=True`, and once
by calling the frozen `probe_rules.canonical` from my clone. Both runs gave the same value. If the map changes in any
way, this review no longer applies, and frozen P06 will refuse.

Scope limitations (why the verdict is not plain PASS):
1. **Final bytes and commit order are outside this review.** The two placeholder fields and the commit order (review,
   then amendment, then authorization) do not exist yet. The frozen verifier checks them mechanically at launch
   (P04, P06). I state what they must be under item 10.
2. **The bound executor carries its r5 limitation.** The r5 static review found the following, and binding the
   executor does not change it:
   - the real-mode path of the executor is covered only statically and by unit rows; the governed end-to-end run used
     manufactured input;
   - the host is not a trust root;
   - the GitHub `ls-remote` publication read was simulated during qualification.
3. **Reviewer independence is limited.** I am a separate, fresh-context Claude session. I did not open the preparer's
   notes, scripts or intermediate files; I read only the draft amendment. I am not a human, and I am from the same
   model family as the preparer. Every check below was run from my own clones and my own commands.

No finding makes the frozen verifier refuse the draft as written, provided the placeholders are filled as item 10
states.

## What I did (method)

- **Local clone.** A fresh `git clone --filter=blob:none --single-branch --branch p5y-postk1-frontier` from GitHub, in
  a new scratch directory. For item 8 I also fetched every GitHub branch and `refs/pull/*` (trees only) into
  private refs of that clone.
- **Host clone.** On rebaseguard-vultr-02 I made a fresh GitHub clone in the new directory `/var/tmp/amendreview-r1`,
  at the same tip. There I ran only these read-only steps:
  - the adapter's `consume`;
  - the published `acceptance.py check`;
  - my own cross-check script;
  - the frozen verifier's `live_host_facts()` function (not the verifier itself).
  Both clones stayed clean (`git status --porcelain` empty).
- **Not done.** I did not run `supervisor.py`, `executor_cli.py` or any `qualify_*.py`. I created no activation
  object, ledger or amendment. I did not touch the guard, AWS or `/root/work/k5-first-real-probe`.

## 1. Executor identity

- **Recomputed identity.** I used the frozen rule from `authorization_interface.executor_identity`: sha256 of each of
  the 11 `IDENTITY_FILES`, then sha256 of the canonical JSON of that map. The result is
  **`ef1c86e40bff0b13e40e924ba27d0841aff71f7344d114f71f517ab3adfdd41b`**. This is the identity named in:
  - `evidence/qualification_r5/QUALIFICATION_RESULT_EXECUTOR.json`;
  - `evidence/qualification_r5/RUN_PROVENANCE.json`;
  - the draft's `amendment_rule_ack`.
- **Unchanged since the r5 freeze.** `git diff a16d22b5..HEAD` over the executor's `code/` and `config/` is empty.
  Five commits follow a16d22b5 (f83cd18, 4376769, 8635b1b, a2bb280, ff3b6a4), with no merges. In the executor
  namespace they only add files: r5 evidence, the r5 review, RESULT_R5.md, and one README line.
- **Pins.** All 279 files in `config/EXECUTOR_PINS.json` exist, are regular files, and match their sha256 at the tip.
  This includes the frozen verifier `prelaunch_verify.py` (`54b198bc...`), which also equals the preregistration's
  `packet_code_sha256`.

Result: **PASS.**

## 2. Source hashes (`executor_sources_sha256`, 14 entries)

For every entry I checked:
- the sha256 at the tip;
- that `git ls-files -s` mode is 100644 and the path is not a symlink;
- the commit that introduced it (`--diff-filter=A`), and that this commit is an ancestor of the tip;
- every commit that touched it.

Result: all 14 hashes match, all are regular 100644 files, and every introducing commit is an ancestor of the tip.
- The 11 executor identity files were last touched at or before a16d22b5.
- `k5_minimality.py` was introduced once, in e8680998.
- `k5b_check.py` was introduced once, in d7d3c08b.
- `consumption_adapter.py` was introduced once, in a2bb280d.

Checks against the frozen rules:
- **Frozen P06.** `executor_entry` and `consumption_adapter_entry` are keys of the map. Both frozen adapter pins are
  present by file name and hash: `k5_minimality.py` `3a54f0fb...` and `k5b_check.py` `ddd54dc4...`. These equal
  `SCIENCE_PREREGISTRATION_R4.k5b_consumption_adapter.pins`. No key uses a sealed-record name.
- **`binding_problems`.** All 11 `IDENTITY_FILES` are present under the exact prefix
  `level4/closure_proofs/p5y_k5_cusum_real_point_executor/`, at their current hashes.

Completeness:
- **Nothing extra.** The map holds the 11 identity files, the two frozen pins, and the adapter entry that P06
  requires.
- **Nothing missing.** The frozen code requires nothing else.
- **Transitive bindings** (these are sound, not gaps):
  - The adapter's acceptance harness and cross-check are bound through the pinned E6 `PROVENANCE.json`.
  - The R1-R4 modules, the point certificate and the protocol code are bound through the hash of
    `EXECUTOR_PINS.json` (279 pins), which the executor re-checks at attempt start and at seal.
  - The K1 Aux5 modules on the executor's `sys.path` (`ancestry5`, `manifest_v3`, `tcb5`, ...) are in neither the map
    nor the pins. They are bound through the preregistered producer identity `3692d0fe`, which the executor's Q04
    production gate checks (`manifest_v3.verify`, then TCB coverage over the committed manifest plus the executor
    pins). This is inherited r5 design, not an amendment gap.

Result: **PASS.**

## 3. `executor_entry`

- The draft names `code/executor_cli.py`. This is exactly the entry that the qualified synthetic amendment in
  `code/qualify_governed.py` writes (`f"{REL_NS}/code/executor_cli.py"`).
- That harness is byte-identical at the tip to the freeze a16d22b5. RUN_PROVENANCE shows the r5 qualification ran at
  a16d22b5 with a clean tree, and the governed part passed.
- `executor_cli.py` is in `IDENTITY_FILES`.
- The operator launches `supervisor.py`, which starts `executor_cli.py` as its child. Both are in the identity.

Result: **PASS.**

## 4. E6 consumption adapter

**Identity and history.**
- `code/consumption_adapter.py` has sha256 **`fbad7d33261fd47fc56c034d6a016f8427b81b51f9199f0e3a8f3e74df35973d`**.
- The commit order is spec + frozen acceptance protocol (8635b1b, E6_SPEC.md and E6_ACCEPTANCE_PROTOCOL.json), then
  code (a2bb280, adapter, cross-check, harness, tests), then evidence (ff3b6a4, acceptance_r1/*).
- Each of these files was touched exactly once, on a linear history. The spec and protocol therefore predate the
  code, and the code predates the evidence.

**Acceptance evidence.**
- `ACCEPTANCE_RESULT.json` (`0a35e0f2...`) records ACCEPTED, and all gates G01-G09 have `ok: true`.
- OBSERVED equals EXPECTED for m = 1, 2, 3, 5, with empty false-positive and false-negative sets. The sets are
  133..309, 145..309, 146..309 and 149..304.
- The expected ranges in the protocol equal `closed_by_k1` of `CUSUM_MINIMALITY_R1.json`. I recomputed that file's
  sha256 as `7feb576b...`.
- The provenance records commit a2bb280d at start and end, an empty porcelain, and harness and cross-check hashes
  that equal the committed files (`072d9fbd...` and `3d5447b0...`).
- The published `acceptance.py check` returns `E6_CHECK: true` with no problems, both locally and on the host.

**Source reading.** The adapter:
- loads the two frozen modules by executing exactly the bytes whose sha256 equals the pin;
- builds the cover with the frozen `load_cells` and addresses records with `record_path`;
- requires every record to equal its manifest entry, and the manifest and cover to equal their pins;
- applies the loader's own geometry rule;
- maps fields as the preregistration specifies (x_lo, x_hi, rho, e0 from the cover with `rat`; R, D, H from
  `R_interval`, `D_interval`, `R2_interval`; M from `M_R2`);
- calls `k5b_check.k5b_literal(cells)` once per m, with `mutation=None`.

What the adapter adds is glue only:
- **Strict parsing.** Its own `exact()` accepts only exact-rational strings where the frozen scan uses `Fraction(...)`.
  This is stricter and fails closed.
- **Cell-0 only.** L1 reaches only cell index 0; every later cell gets `L = None`.
- **Refusals.** Every other deviation raises a refusal.
- **Nothing result-dependent.** There is no branch on output. The code never references the R1 evidence or any
  real-probe output. Its imports are standard library only, and `k5b_check` and `k5_minimality` have `__main__`
  guards.

**Host re-run** (vultr-02, fresh GitHub clone at ff3b6a4a, records from
`/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records`):
- `consume` under system Python 3.13.5 with PYTHONHASHSEED 1 and 7, and under the contract venv Python 3.12.3, gave
  three byte-identical outputs. Their sha256 is `d4c315d6...`, equal to the committed `ADAPTER_OUTPUT.json`.
- **My own cross-check**, written independently of the committed `crosscheck.py`:
  - frozen `k5_minimality.verify(CUSUM_MINIMALITY_R1, records, cells)` returns no problems;
  - all 310 records equal their manifest entries;
  - I built the cells myself, with manifest-keyed addressing and my own cover filter, and called `k5b_literal`
    directly. For every m the pass set equals both R1 and the adapter's output;
  - every `H.lo <= 0`, which is the premise under which the literal theorem and the readiness variant coincide.

Result: **PASS.**

## 5. Evidence pins (`qualification_evidence_sha256`, 5 entries)

| file | introduced | sha256 matches |
|---|---|---|
| executor `evidence/qualification_r5/QUALIFICATION_RESULT_EXECUTOR.json` | f83cd18 | yes |
| executor `evidence/qualification_r5/RUN_PROVENANCE.json` | f83cd18 | yes |
| executor `review/EXECUTOR_STATIC_REVIEW_R5.md` | 4376769 | yes |
| adapter `evidence/acceptance_r1/ACCEPTANCE_RESULT.json` | ff3b6a4 | yes |
| adapter `evidence/acceptance_r1/PROVENANCE.json` | ff3b6a4 | yes |

- Each file was touched once, is a regular 100644 file, sits at or before the tip, and uses no sealed-record name.
- The qualification result shows 23/23 gates PASS, `QUALIFIED_AWAITING_EXTERNAL_AUTHORIZATION`, identity
  `ef1c86e4...`, and all 16 part files matching their `part_sha256`.

**Is the set appropriate?** Yes. It pins the two top-level results and their provenance, and these bind the rest by
hash:
- the r5 parts, through `part_sha256`;
- the E6 adapter output, cross-check and mutations, through ACCEPTANCE_RESULT;
- the E6 harness and acceptance protocol, through PROVENANCE.

The r5 static review is filed under the "qualification evidence" key. That is a loose fit for the key's name, but
harmless, because P06 treats every pinned file the same way.

Result: **PASS.**

## 6. Science preservation

- `SCIENCE_PREREGISTRATION_R4.json` has sha256 **`9ace6896d70b7a17225c03cd6d8092e3d33089d001dd3e2736894dd866f3780a`**,
  equal to the draft's `science_preregistration_sha256`.
- The file was introduced exactly once, by 852b2d65c9332facd59771da7940ab429a7e2f2f, and never touched again on any
  GitHub branch. That commit's only parent is 5da170dbf8f3a256e460d239db4644d39ca773bc.
- The r4 template and binding were introduced by the same commit and are unchanged.
- `FREEZE_RECORD_R4.json` was committed once, later, in cf09d6f.
- The packet code was last touched at the freeze and equals `packet_code_sha256`.

The amendment is a separate file carrying only the allowed keys. None of its fields is a science field, parameter or
verdict rule. The ack text names the science sha256 correctly and claims no change.

Result: **PASS.**

## 7. Keys, status, schema

- The draft's key set equals the 11 `allowed_keys` of the preregistration exactly, which is also the verifier's
  `AMENDMENT_KEYS`.
- `status` is `BOUND_QUALIFIED`.
- The schema string, `rebaseguard.p5y.k5.cusum-first-real-probe.execution-binding-amendment.v1`, is identical to the
  one fixed by the qualified synthetic amendment in `qualify_governed.py`.
- Compared with that synthetic shape, the draft differs in three ways:
  - it has one more source (`consumption_adapter.py`) and a different `consumption_adapter_entry` (the synthetic
    shape used `k5b_check.py`);
  - its evidence pins differ;
  - its ack is real.
  Neither P06 nor `binding_problems` depends on those differences beyond the checks already confirmed.

Result: **PASS.**

## 8. No real order-3 observation

- **Git history.** I scanned the full name history of all 15 GitHub branches plus `refs/pull/1/head` (non-shallow;
  20,916 distinct paths). None of the following exist:
  - `EXECUTION_BINDING_AMENDMENT.json`, `AUTHORIZATION_ACTIVE.json`, `COUNTERSIGNATURE_ACTIVE.json`,
    `ATTEMPT_LEDGER.jsonl`;
  - any path containing "sealed" (case-insensitive);
  - any `k5-first-real-probe` path;
  - any protocol `ledger/` or `evidence/` path;
  - any executor `authorization/` path.
  The same search does find the two templates, so the pattern works.
- **Host.** `/root/work/k5-first-real-probe` does not exist. A search of `/root/work` and `/var/tmp` for those
  activation and sealed-record file names found nothing. `/var/tmp/k5gov`, the synthetic governance scratch, is
  empty.

Result: **PASS.**

## 9. Canonical sources sha256

**`b437adba64cd4098d6f8998f01af159e7092c14b6597c219cc9ab130da97c015`**. It is written on the sources line above.

## 10. Activation order the frozen code requires

Derived from `prelaunch_verify` P02/P04/P06/P11/P12, `authorization_interface.countersignature_problems` and
`binding_problems`, and `supervisor.slot_binding_problems` and `governed_prelaunch`.

1. **Review file.** This file is committed byte-identical at
   `level4/closure_proofs/p5y_k5_cusum_external_authorization/review/AMENDMENT_REVIEW.md`. The commit must be the
   amendment commit or one of its ancestors, and the file must never be edited afterwards.
   - `independent_review_sha256` is the sha256 of exactly the committed bytes.
   - `independent_review_verdict` is the exact string `PASS_WITH_SCOPE_LIMITATION`.
2. **Amendment.** Committed once at the fixed path, strictly after 852b2d65, never modified, and published on the
   GitHub frontier. Never amend or rebase it: P04 compares against its committer time.
3. **Independent amended-packet check (E5).** Before any authorization, re-run the verifier with its default (the
   template) and review the amended packet statically.
   - REFUSED is expected, but P06 should fail on one clause only: "authorization names another executor binding",
     because the template carries `SET_AT_ACTIVATION`.
   - Any other failing P06 clause means the amendment is wrong.
4. **Authorization.** Only after a separate explicit user authorization message, create `AUTHORIZATION_ACTIVE.json`
   from `AUTHORIZATION_TEMPLATE_R4.json`, changing only the activation fields:
   - `EXECUTION_AUTHORIZED` true;
   - `PROTOCOL_FREEZE_COMMIT` = 852b2d65c9332facd59771da7940ab429a7e2f2f;
   - `PRODUCER_R4_IDENTITY.executor_binding_sha256` = sha256 of the committed amendment bytes;
   - a non-empty `AUTHORIZED_BY`;
   - `AUTHORIZATION_UTC` as an ISO string with an explicit offset. It must be no earlier than the amendment's committer
     time, and within [authorization commit time - 3600 s, + 60 s].

   Commit it once, strictly after the amendment, and publish it.
5. **Countersignature.** `authorization/COUNTERSIGNATURE_ACTIVE.json` in the executor namespace, with exactly the
   template's keys:
   - `status` COUNTERSIGNED and `EXECUTION_AUTHORIZED` true;
   - `protocol_authorization_sha256` and `execution_binding_amendment_sha256` set to the sha256 of the file bytes;
   - `attempt_slot` as the integer 1;
   - `nonce` of at least 32 lowercase hex characters;
   - `countersigner.identity` non-empty and `independent_of_execution_host` true;
   - `countersigner.utc` as a JSON number (epoch seconds) that is not in the future. An ISO string is refused.

   Commit it once, in a commit that descends from the authorization commit. The code does not check that it is
   published, but it should be.
6. **Ledger.** `ledger/ATTEMPT_LEDGER.jsonl` in the protocol namespace gets exactly one LAUNCH_NOTICE for `slot-1`,
   with exactly the keys `event`, `slot`, `authorization_sha256` and `utc`:
   - `authorization_sha256` is the sha256 of the authorization file bytes;
   - `utc` is ISO-8601 with an explicit offset and not earlier than `AUTHORIZATION_UTC`.

   The ledger is append-only and committed, and its last commit is published.
7. **Host guard.** On a fresh checkout of the frontier whose origin URL is allow-listed and whose
   `origin/p5y-postk1-frontier` equals `ls-remote`, with HEAD descending from the authorization commit and tracked
   protocol files clean, set `config/REAL_INPUT_GUARD.json` to `EXTERNAL_AUTHORIZATION`. This file is outside the
   identity and the pins.
   - The host's existing `/root/work/ReBaseGuard` is on `main` (c123b9bb). It is not such a checkout.
8. **Final preflight.** Run the verifier on `AUTHORIZATION_ACTIVE.json`: `LAUNCH_PERMITTED`, with P11 approving
   `slot-1`.
   - Host facts currently equal the frozen contract; `live_host_facts()` shows no difference.
   - There must be no conflicting producer process.
   - The namespace must not exist.
9. **Launch.** `supervisor.py launch --namespace /root/work/k5-first-real-probe --slot 1 --mode real`, with the
   default ceilings. Use no other mode on the execution host.

Nothing in the draft itself would make the frozen verifier refuse, as long as step 1 is followed exactly.

## Findings, ranked

1. **MEDIUM (procedure; not a defect of the draft).** The two placeholders must be filled exactly as step 1 says, and
   the review must be committed no later than the amendment. After that, every one of the 20 pinned files (14
   sources, 5 evidence files, this review) is permanently immutable: any edit makes P06 refuse.
2. **LOW (procedure).** The E5 amended-packet verifier run is expected to show exactly one P06 failure (the
   authorization-binding clause). Whoever runs it must read the P06 detail string, not just the overall verdict.
3. **LOW (runbook traps).**
   - `countersigner.utc` must be a number.
   - The LAUNCH_NOTICE `utc` must be ISO-8601 with an explicit offset, not a number (r5 review D-1).
   - `AUTHORIZATION_UTC` must fall after the amendment's committer time and within the hour before the authorization
     commit.
4. **LOW (by design).** After the amendment exists, E6 `acceptance.py run` would fail its own precondition gate G01.
   Only `check` remains usable. The binding rests on the pinned acceptance evidence, which is what the
   preregistration requires.
5. **INFO.** Three things are bound outside the sources map, all through frozen channels:
   - the executor does not import the adapter, because consumption happens after the result, and only for POSITIVE
     outcomes;
   - the Aux5 modules are bound through producer identity `3692d0fe`, not the map;
   - `executor_entry` is the child CLI, not the supervisor.
6. **INFO.** E6 acceptance ran under system Python 3.13.5, not the contract venv. I reproduced the output
   byte-identically under the venv's Python 3.12.3.
7. **INFO.** My host scratch directory `/var/tmp/amendreview-r1` remains on vultr-02. It holds a clone and three
   adapter output files, and nothing the verifier reads.
