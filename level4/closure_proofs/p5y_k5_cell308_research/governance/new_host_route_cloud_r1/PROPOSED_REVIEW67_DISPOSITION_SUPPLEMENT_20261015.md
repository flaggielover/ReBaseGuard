# Proposed supplement: disposition of review 67 on the combined development source

**PROPOSED_NOT_ACCEPTED_NOT_IN_FORCE · DEVELOPMENT ONLY.** This supplement answers review 67
(`reviews/REVIEW_REVIEW66_REPAIR_DELTA.md`, recorded verbatim). Review 67 is a fresh bounded review of `774f2183..2f39e9f4`.
This supplement accepts nothing and decides nothing.
* All 21 D-* decisions remain undecided, and `DECIDED` is empty.
* `JOURNAL_READER_REVIEWED = False` and `PIN_POINT_MODULES = None`.
* A1, A2 and A5 remain unmet.

Supplement r66 is not edited. Its §2 is **replaced** by §2 below, and its M4 row's statement about `--strict`
("only promotes warnings … no hiding construction depends on it") is **withdrawn** (N1). The new source is bound by
the ledger line of its commit and by its own native run.

## 1. Findings

| finding (review 67) | disposition on the new source |
|---|---|
| N1 MAJOR: without `--strict`, a deleted rejection under a tree entry whose name is `<review dir>/veto.md` (fsck `fullPathname`, a warning) is invisible to the pathspec-limited history scan, and the attestation is ACCEPTED | `--strict` is restored in `_history_complete`, so any fsck warning refuses as unavailable evidence. Test `test_review67_warning_class_tree_name_refuses` builds the reviewer's construction. It asserts that the full listing shows the entry, that the pathspec-limited `rev-list` misses that commit, and that the result is refused for "history completeness". Mutant RV49 drops `--strict`. The zero-padded-mode history that supplement r66 had newly accepted is refused again (§2). The pathspec-independent scan the reviewer prefers is **not** adopted: it would list every commit's full tree, and strict fsck already refuses the warning-class names that make the two views differ. |
| N2 MAJOR: `git log` runs repository-configured signature programs (`log.showSignature` + `gpg.program` / `gpg.ssh.program`) after fsck | The isolation adds `-c log.showSignature=false`. Test `test_review67_signature_program_never_runs`: a commit carrying a `gpgsig` header, with the repository's own `log.showSignature=true` and a marker-writing `gpg.program`. No marker is written, and the repository is accepted. Mutant RV50. Keys `git log` reads, checked for this call shape (`--format=%H --no-patch`, no pathspec): `log.decorate`, `notes.*` and `log.mailmap` affect only formats not used; `log.follow` needs one pathspec; `diff.*` drivers are off (`--no-textconv`, `--no-ext-diff`); pagers need a terminal. A binary or `-diff` attribute does not hide a commit from `-S` (checked on git 2.43). This check covers the named mechanisms, not every configuration git may honour (§2). |
| N3 MINOR: refused-repository list incomplete | §2 now lists a repository owned by another user (git's dubious-ownership refusal, reported as "attestation not committed at HEAD"). `safe.directory` is deliberately not passed: git's ownership check guards against exactly this class of repository-configured command. The second item (a local `log.showSignature` with signed commits) is no longer refused after N2. The N2 test's legitimate repository is accepted. |
| N4 NOTE: global attributes are read via `HOME` | The isolation adds `-c core.attributesFile=/dev/null`. Test `test_review67_global_attributes_file_is_not_read`: `check-attr` under the isolation reports `unspecified` although `$HOME/.config/git/attributes` sets `diff`. Mutant RV51. |
| N5 MINOR: RZ1, RZ4 and RZ5 survive | The forged-CDAT case asserts HISTORICAL again, so reading the graph's parent data is detected: RV52 = RZ1. `test_review65_local_fsck_or_promisor_configuration_refuses` adds subtests for `extensions.partialClone` alone and for `remote.upstream.promisor`: RV53 = RZ4, RV54 = RZ5. RZ6 (`--no-full`) is outcome-equivalent on its construction and is not registered. Witnesses for N1, N2 and N4 are RV49–RV51. |
| N6 NOTE: wording and records | The `_git_env` docstring now names git 2.43.0 (checked) and 2.44 and later. The forged-graph test's docstring no longer says "full strict fsck". Native run 38756465002 (2f39e9f4: success, 181/181, artifact 11986430317) was recorded by a ledger line in commit 73018725, before this supplement. A ledger line states the 3.11 / 3.13 wording difference between the 2288bec1 message and ledger 503. Both are true: the gate ran all three. |
| N7 NOTE: the in-repository class cannot be closed by in-repository checks | **Agreed.** §2 now describes the precondition as defence in depth, not a closure. The class rests on D-HOST-LIFETIME item (i), the ledger binding of the reviewed commit and attestation blob, and item (ii), a non-coordinator reviewer. Both stay carried and undecided. |

## 2. What the completeness precondition does (replaces supplement r66 §2)

`_history_complete` returns True only when all three of these hold, under the isolation:
1. `rev-parse --is-shallow-repository` prints exactly `false`.
2. `git config --includes --name-only --list` lists no `fsck.*` key and no partial-clone or promisor key.
3. `git fsck --full --strict --no-dangling` exits 0.

Any failure, timeout (60 s per git call) or other answer refuses as unavailable evidence. Under the isolation:
* replace refs and grafts are ignored;
* the commit-graph is never read;
* no fsmonitor command, lazy fetch or `git log` signature program runs;
* global and system configuration, the system attributes file and the global attributes file are not read;
* git sees only an allow-listed environment.

**It is defence in depth, not a closure (review 67 N7).** Every review since 64 has found another mechanism by
which the reading repository's own files make git report a history other than the one a checkout shows. The check
runs git, git reads the repository's configuration, and git does not re-hash objects on read. It can therefore show,
at most, that git's own strict verification found nothing wrong at the moment of the check, for the mechanisms named
above.

**It does not establish:**
* that the history is the one that was reviewed, because a consistent rewrite has new commit ids and passes every
  in-repository check;
* that nothing changed between the check and the reads;
* that no other repository-configured behaviour affects the reads;
* reviewer authority.

These rest on D-HOST-LIFETIME items (i) and (ii), which stay carried.

**Legitimate repositories refused (fail-closed; to be listed in the D-HOST-LIFETIME procedure):**
* shallow clones;
* partial clones, and repositories with promisor keys;
* repositories with any `fsck.*` key;
* any `git fsck --full --strict` error or warning in any object, including old history (e.g. zero-padded tree modes,
  bad time zones);
* an index whose entries name missing objects, because fsck checks the index;
* a repository owned by another user (git's dubious-ownership check; reported as "attestation not committed at
  HEAD");
* any git call exceeding 60 s, for example on large repositories;
* an attestation path spelled other than its exact tree path (e.g. `./att/HOST.json`).

The repository checked out in this session is shallow, so it refuses every attestation. N1's and N2's constructions
were measured on git 2.43.0. Their behaviour on the native runner's git 2.55.0 is shown only by the native run of
RV49 and RV50.

## 3. Harness

Group RV grows to RV01–RV54, so the registry has 187 mutants.
* RV31 is re-anchored to the strict fsck line, with the same weakening.
* RV44 is re-anchored: it removes the fsmonitor line, with the same weakening.
* The workflow expects 187 mutants and 188 suites. The suite has 224 tests.
