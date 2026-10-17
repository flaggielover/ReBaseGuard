# Cell-308 parallel-line evidence and document comparison

Date: 2026-10-15 (Asia/Tokyo). Source-only comparison; no tests, product/test/harness imports, host calls, repository edits, commits or pushes. The sole authored artifact is this file. `new_target_evaluations = 0`.

The two lines are parallel descendants, not successive versions of one shared draft. The Claude material is recovered from the parent-supplied immutable ref `37c62102` on `claude/cell-308-github-state-skb1g0`; the full commit SHA was unavailable, so no full SHA is asserted. Exact Git blob IDs and SHA256s bind every recovered input below. The Codex checkout is at `3b2442770ebc68b8c5672786c2213c9da18b5479`, with the reviewed development input pinned to `7eb3ba4d03f3b7898109073c83eb9b08f4589354`. A bare label such as “r4” or “revision 5” is ambiguous across these lines.

## Main comparison

| Question | Claude line at 37c62102 | Codex line, reviewed input 7eb3ba4d |
|---|---|---|
| Current supplied development records | Revision 5: recorded 87-test success on each of `/usr/bin/python3.11`, `python3.12`, `python3.13`; mutation record labels 113/113 KILLED | Preserved R7 reviews report one exact-input Linux 136-test baseline and 80 intended-property assertion kills; 112 platform methods plus 24 wrapper methods |
| Evidence retained in mutation record | Two source/test hashes, unmutated PASS/OK and each mutant's ID/property/status/final stderr line | Strict harness retains command, environment controls, counts, named outcomes, complete stdout/stderr, mutation anchors/transformed hash, six before/after input hashes, interpreter/kernel provenance and invalid reasons |
| Meaning of KILLED | Any completed subprocess with `returncode != 0` | Full baseline count and a structurally valid assertion-failure report; unittest errors, skips, malformed reports and other invalid runs become ERROR |
| Direct problem visible in supplied record | Four KILLED rows have error-only summaries; the other 109 have failure-only tails but no names/traces from which this review can attribute the intended property | Preserved independent evidence report explicitly attributes every one of 80 kills and describes zero unittest errors/skips/timeouts; this comparison did not reopen or reproduce the raw CI artifact |
| Independent review status | Review62 covers revision4/amendment r4, ending at `cd86c326b573c631749585a46638674e6d8417f4`; brief63 commissions review of revision5/r5, and is not the resulting review | Three permitted R7 review documents preserve bounded code/evidence conclusions for input7eb |
| Proposed governance vocabulary | Amendment r5: 21 D-* rows, also present in recovered `OPEN_DECISIONS`; all undecided | Codex-authored amendment r4/E1/E2: 20 D-* rows, all undecided; complete static science import list/pin-point wrapper remains A5 |
| Formal/operational status | PROPOSED, NOT ACCEPTED, NOT IN FORCE; formal route review, owner decisions and fresh S12 remain pending | Same proposed status and continuing prerequisites; observation-only wrapper with operational readiness False; A1/A2/A5 remain operational conditions |

Neither test count nor mutant count establishes relative completeness. The registries, property selection, wrapper coverage and classifiers differ. Python-version breadth in a concise record also does not establish a chosen official interpreter, actual-host suitability or governing acceptance.

## What the supplied Claude records establish, and their limits

`TEST_RUN.json` records class SYNTHETIC_VALIDATION, dev_only true, revision5, UTC `2026-10-15T01:24:36Z`. Its command is the template `<python> -B -W error::ResourceWarning -m unittest discover -s tests -v`. It records returncode0, `Ran 87 tests` and OK for each of three interpreter paths. The recovered test file has 87 textual `def test_` method definitions. Its two source/test SHA256 fields match the recovered bytes and the mutation record. This establishes internal byte/count consistency of the supplied record, not a fresh run here. The record lacks complete outputs, individual test names, exact interpreter version/build/executable digests and before/after imported-input hashes. Review62's separate 83-test results on versions3.11.17/3.12.3/3.13.16 apply to its earlier revision4 input and cannot be transferred to revision5.

`MUTANTS_RUN.json` contains 113 rows labelled KILLED, split by the recovered registry into M32/R10/X9/N14/Y9/P15/Z11/Q13. It says unmutated_suite PASS and unmutated_tail OK. Four rows visibly are not assertion-only results:

| ID | Weakened property as recorded | Stored tail |
|---|---|---|
| M29 | execute/resume launch gate without a launch record | `FAILED (errors=2)` |
| N04 | caller-asserted fields accepted in an attestation reference | `FAILED (errors=1)` |
| Y09 | cgroup_resources reads the leaf only | `FAILED (errors=1)` |
| Z09 | launcher-mode passed launch record ignored | `FAILED (errors=1)` |

The recovered harness at lines299–338 explains the labels: it runs mutations before the baseline; sets KILLED whenever a completed subprocess return code is nonzero (line321); retains only the last stderr line; runs the baseline afterwards; and binds only platform/test hashes. It does not require an assertion, matching full test count, matching outcome names or intended-property witness. It does not clear inherited `LX_PLATFORM_DIR` for the baseline, retain actual interpreter provenance, hash the harness in the execution record or detect before/after source changes. Its mutation subprocess command omits the standard-record command's `-W error::ResourceWarning` and `-v`. Timeouts are specified but uncaught: they would abort the harness, rather than receive a valid-kill classification. A completed import/syntax/runtime error or signal exit can receive KILLED under its nonzero-return rule.

Thus 113/113 is accurately described as **113 recorded nonzero mutant-suite exits under this classifier**, with four explicit error-only tails. It is not 113 proven intended-property assertion kills. The other109 failure-only tails may contain useful detection, but this record alone cannot verify per-mutant test counts, names, traces or attribution. No cause of the four errors is inferred without the missing traces.

The recovered hashes and Git blob identities below authenticate which bytes were supplied. Matching a record's claimed source hashes does not prove what was actually imported or executed, which interpreter ran the mutation harness, or that all outputs were retained. The separate download manifest is recovery provenance, not execution provenance.

The local harness core was inspected only as text. It matches the preserved input7eb harness Git blob `f32bb04448860db25035ef76723b6d7b5bbceede` and SHA256 `6fe09b9f1bd6f437bf561ed69290a154867618265338cfb9ec3b3fda7e89af74`. Its `_suite_record`, `classify_mutant`, `apply_mutation`, `input_hashes` and `main` provide the stricter boundaries summarized above. The permitted R7 evidence report separately records Actions run38644122257 at input7eb and complete 81-suite adjudication. That remains a claim of that preserved independent review in this comparison; no CI query or raw-artifact re-adjudication was performed here. Its 80 mutations target low-level platform code, so participating wrapper tests do not make complete wrapper mutation coverage.

## Review, vocabulary and document reconciliation

Recovered review62 states `DELTA_ACCEPTED_WITH_CONDITIONS`, `AMENDMENT_DRAFT_R4: FIT_WITH_CONDITIONS`, and `DEV_CODE_R4: FAIL_CLOSED_WITH_DEFECTS`. It explicitly accepts no amendment. Its findings G1–G11 and E1–E4 are findings/conditions about its own Claude revision4/r4. Its citation condition E1 withholds L-LIFE/L-UPD/L-PIN pin-point citation until repair plus fresh confirming review. Claude amendment5 maps proposed responses in §13 and states revision5 repair citation waits for its fresh delta review. Owner5 likewise says revision5's own review was not yet recorded at authorship. Brief63 names the expected output `REVIEW_CLOUD_R1_DELTA_R5.md` and commissions adversarial review; receiving the brief does not supply that output or its verdicts. Parent reports the expected current-branch connector lookup returns404; no positive conclusion about review63 availability follows from the recovered set. Its publication, exact input and outcome remain unverified here.

The Codex r4 §4 and Claude r5 §4 share20 decision IDs. Claude has the additional `D-PIN-POINT`, requiring a fixed science-import list; Codex carries that requirement as A5 rather than a twenty-first row. Claude's r5 D-HOST-LIFETIME additionally carries an accepting-review ledger binding, reviewer identity different from the coordinator and blob-level commit order; it says code implements the order item only. Codex's A1/A2/A5 and restricted `lx_verified.py` prototype follow a different design line. These are implementation/document alternatives to reconcile prospectively, not decisions already made.

Both draft lines preserve conservative D-RC2-SCOPE treatment, pending fresh S12, required host facts and the governing sequence. No supplied review establishes formal route/governance acceptance, actual-host attestation, independence of the eventual accepting reviewer, complete science-import/pin-point implementation, owner approval, qualification or target authority. Original accepted quotations/provider facts were not independently rechecked against their source documents/websites in this bounded comparison; references to excluded material were not followed.

The identical path `governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R4.md` names different authored documents on the two branches. Codex's r4 is grounded in the Codex brief61 review and20 decisions; Claude's review62 concerns a different r4 and21 decisions. Claude's r5 does not automatically supersede Codex's r4/E1/E2. A blind same-path overwrite or undifferentiated cherry-pick would lose authorship, conditions and source bindings.

The local continuation status still calls the original Claude branch “preserved at d423c7aa” and says original branches are unchanged. Those statements can describe Codex's preserved base and actions taken on its continuation. They are unsafe as a statement of the **current remote Claude head**, now supplied as37c62102. Any PR2 description that treats d423 as current Claude state, calls Codex r4 the sole/latest shared r4, declares the Claude line unchanged globally, or transfers Codex's strict80 verdict to Claude113 is stale or ambiguous. PR2 was not opened in this subreview; these are exact claims to check and correct if present, not assertions about its unread text. Codex's pinned136/80 result remains valid within its own cited evidence scope.

## Immutable byte bindings

`NS = level4/closure_proofs/p5y_k5_cell308_research`. All remote rows are ref37c62102 from the manifest. Both SHA256 and Git blob IDs were independently recomputed from every recovered file with `shasum -a 256` and `git hash-object`, and all match the manifest. Recovered files were not modified. The manifest itself has SHA256 `9f5f0db496ac23e28ca223cc0545c3a10d2b0e20f0deb988e70c30bb748ed41e`.

| Recovered basename → source relative to NS | Git blob ID | SHA256 |
|---|---|---|
| platform.py → streams/CLOUD_R1_LINUX_DEV/lx_platform.py | a4b9458798969c0d0419a8fbde2872866d69c76d | 8ccddf8531716fc2bc1c96a70f7b29c547586fcc74099adfcb7320fd8dea7169 |
| tests.py → streams/CLOUD_R1_LINUX_DEV/tests/test_lx_platform.py | ccc66729a3882ed104817a28297f973a1747d1cb | 2002dc8d996100afc24fc29a973225e0f1013bb579122976df770e43d0f264e8 |
| harness.py → streams/CLOUD_R1_LINUX_DEV/tests/run_mutants.py | 0424094bc356d8cf9389ac33f46a6265a65678c0 | 8fc73e9c8b82a533b09aea0ce5ff328df102ca01a6bf5d4f74d4911de1b8096c |
| test_record.json → streams/CLOUD_R1_LINUX_DEV/results/TEST_RUN.json | fc216aa83e3d7ebefb21fb98ae864d21526a2e40 | 23b350a812e4242261a8d04a18fb116b91e36dd065e9c1ffd8bd822ab37f9f13 |
| mutants.json → streams/CLOUD_R1_LINUX_DEV/results/MUTANTS_RUN.json | a5fbeb2e61478c1fef7f8d0ede43d51a36a6ce92 | fd5396b3256beda9cff36d7ac46eef29189ea90431525b66c95dc6c8af332d69 |
| amendment5.md → governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5.md | 427656fcb22bb8b883747e4d461685213062dcb9 | d0963b110baab7beb86fa80184b9ebf2aab21362d7c7e35745fc10b06f9ba933 |
| owner5.md → governance/new_host_route_cloud_r1/OWNER_DECISION_BRIEF_CLOUD_R1_R5.md | 8d72bbf89b344fdfe46fae85bbc2cc3297176403 | a0142eb09576b46367bda03b85f794104a7c2a0b280ec84c8d890e1cd597fbee |
| review62.md → reviews/REVIEW_CLOUD_R1_DELTA_R4.md | 635a0a964f8dc16ba8c452badf59dfbb99bb4c7d | 0a54a549345354a76da73bdae421244d0f0ecf10ebf6f7eb7525f362848203aa |
| brief63.md → ledger/briefs/63_reviewCLOUD_R1_DELTA4.txt | f3c0a26522b76eebbf1ea89eab026bcdf544d3e1 | d4f4902947f5c637a67163060134181d79723606b824f278576507c41434ca79 |

Local documents read at the named checkout/head (SHA256 of inspected bytes):

| Path relative to NS | SHA256 |
|---|---|
| reviews/REVIEW_CLOUD_R1_DELTA_R7_CODEX.md | f77de8b82d8253a881d0cdc1a8597d52327d5d679dfd1ce7d09787a02e6c074a |
| reviews/REVIEW_CLOUD_R1_DELTA_R7_CODEX_CODE.md | 030b40a719230a14fce25becb03d5aa8123e53a12d9aef3affdf4f21e64e75a3 |
| reviews/REVIEW_CLOUD_R1_DELTA_R7_CODEX_EVIDENCE.md | b2007895819d6265c22a8c189452e19410a8b9cd04535642669b29aa8c6689bb |
| governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R4.md | 0a9d720f2b715cda0f247d1500a807613a2e6f2a1265578fdada0ab2d85baa9b |
| governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R4_ERRATUM_E1.md | b73ecabf0dbf7fe2dda650b6f8c98808b03137faaa4cc69d8e1a4c35bc237e84 |
| governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R4_ERRATUM_E2.md | 36e2a5eee49259563a9dab5abad519bf82aa528bf3463eca7856d4279c55c994 |
| governance/new_host_route_cloud_r1/CONTINUATION_STATUS_CODEX_20261015.md | 8894ab52519ab6f0713ba5a4ea748666de0313f683f1b55cb33d49fbc38c751d |

## Integration sequence

1. Preserve both immutable lineages and qualify every r4/r5/revision label with branch and input. Amend current-state/PR prose additively so d423 is the shared historical base, not the current Claude head.
2. Obtain the actual review63 output if published, with its exact reviewed input and byte binding. Keep revision5 repairs marked pending fresh confirmation until that evidence exists; brief63 alone cannot close review62 conditions.
3. Build a prospective reconciliation map: Claude G1–G11/E1–E4 and21-row vocabulary against the Codex r4/E1/E2, A1/A2/A5, restricted wrapper and preserved strict-evidence requirements. Preserve both same-path r4 documents under unambiguous lineage bindings before integrating text.
4. Select any future code/document integration on property semantics and traceable witnesses. Carry the strict classifier and full-input/full-output evidence boundary forward. Do not aggregate113+80, relabel the four error-only rows as valid kills, or treat existing evidence as proof for combined bytes. Any future integrated input would need separately authorized exact-input validation and fresh independent review.
5. Keep formal route review, all unresolved decisions, actual-host evidence, fresh S12 and governing sequence gates explicit and unmet. This read-only comparison supplies no operational or scientific authority.

Exposure: only the named recovered files, manifest, seven permitted local documents and the explicit local harness core were read, plus the startup skill (which exempts dispatched subagents). No other current-agent report was read. No excluded audit/interruption/disclosure content, MB-r1 postexecution/target record or Cell309 content was opened. No broad namespace inventory, quarantine CLI, host/settings/secret inspection or candidate/science/decoy/qualification/drift/certificate/evaluator/target execution/import occurred. Historical references inside permitted documents were not followed. `new_target_evaluations = 0`.
