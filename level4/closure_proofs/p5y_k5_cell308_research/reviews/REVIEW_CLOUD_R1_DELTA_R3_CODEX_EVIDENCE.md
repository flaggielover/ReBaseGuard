# Cell308 brief 61: independent evidence and provenance review

Reviewer: fresh independent evidence/provenance subagent for brief 61; no authorship of the reviewed material or reviews 59/60.

Date: 2026-10-15 (JST). Repository: `/Users/suzhe/.codex/worktrees/cell308-review61/ReBaseGuard`. Delta: `ff9006ac..d423c7aacc4d1cc15f3c7d77aecb5257a0175392`. HEAD was verified as that immutable SHA; initial `git status --short` was empty. At the final status check, untracked `.github/` and `docs/superpowers/plans/2026-10-15-cell308-review61-continuation.md` were present; this subagent did not create or open them and notified the parent of the concurrent workspace change. Tracked evidence bytes matched immutable HEAD during the hash review.

Scope: Q5 record bindings, preservation, static mutation classification checks, documentation consistency, and read-only inspection of the scanner's gate. Full fail-closed/governance verdicts belong to the parent review. No result here accepts the proposed amendment.

## Exposure and execution disclosure

Read the three Cloud review briefs 59–61; the changed ledger lines and surrounding diff context; relevant portions of `BRIEF_INDEX.md` and review 60; the development README, platform code, tests, mutation harness and recorded results; and `code/c308_quarantine.py`. Read/hash-compared the explicitly listed Cloud governance/owner/feasibility/inventory/erratum files below. Used Git metadata to verify preservation of review-59 scratch. The scanner source contains quarantine identifiers; it was read as code only.

No forbidden audit, interruption review, coordinator exposure disclosure, MB-r1 postexecution/target-run record, or Cell309 file/branch/record was opened. No accidental contact occurred. No candidate, science, cell, drift, certificate, qualification or decoy code was executed. No scanner or quarantine guard was executed. No tests or mutant suite were executed by this subagent: Linux runtime verification is delegated to the parent. The only Python executed here parsed syntax/JSON and recomputed hashes; it did not import repository modules. No repository file was edited, committed or pushed.

## Q5 result

**The record hashes match the committed files.** All 13 SHA-256 bindings in the three new ledger lines match independently recomputed file bytes and the immutable HEAD blobs. The ledger delta appends three JSON lines and removes zero. The new lines bind briefs 59/60, the review-60 artifact, and the revision-3 code/documents/results/brief 61. Briefs and index entries name the same files and delta scopes. Brief 61 issuance is explicitly recorded in the revision-3 line.

**Runtime claims remain UNVERIFIED by this subagent.** `TEST_RUN.json` records 75 successful tests on `/usr/bin/python3.11`, `.12`, and `.13`, with ResourceWarning elevated to an error. `MUTANTS_RUN.json` records baseline PASS and 65/65 KILLED, including R01–R10 = 10 and X01–X09 = 9. Their code/test SHA-256 fields match HEAD. Static inspection finds exactly 75 `test_*` methods and 65 mutant entries; all mutation anchors occur exactly once in sequence, all mutated sources parse successfully, and result IDs/properties match the committed harness. Those checks establish record/source consistency, not an independent replay.

The mutation record has 64 `FAILED (failures=...)` tails and one `FAILED (errors=1)` tail, M29. See E2 for classification limits. It is not valid to label M29 an unrelated-error false kill from that tail alone.

### Recomputed new-ledger hashes

Paths are relative to `level4/closure_proofs/p5y_k5_cell308_research/`. Every row matched both the bound SHA and committed/working bytes.

| File | Recomputed SHA-256 |
|---|---|
| `ledger/briefs/59_reviewCLOUD_R1.txt` | `9b78af71ebe17a0f9e94061933849a2528f01053903840f6c55398f4acd688eb` |
| `ledger/briefs/60_reviewCLOUD_R1_DELTA.txt` | `54e3ef2dcd4523ce6538812e35b95ef1fc47792cde9d4aeebee7f65251068fdc` |
| `reviews/REVIEW_CLOUD_R1_DELTA_R2.md` | `8c242e5fb5d44473e86fb5cb34e9701b2988b56eb83a86b167d9c1069151c7e9` |
| `governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R3.md` | `5f121941f48c2295de0c6b72573e6bf4c3fb4c1c7f3477f152e2101152757d17` |
| `governance/new_host_route_cloud_r1/OWNER_DECISION_BRIEF_CLOUD_R1_R3.md` | `3291feb1901991d97142ac52c8ede7e14f04c7430c82c9fa0be818d960b65ffe` |
| `streams/CLOUD_R1_LINUX_DEV/lx_platform.py` | `6978cba7e10521e00b78428b02c10f6455ab2baa43c90cfa9a4a0b8c8934897c` |
| `streams/CLOUD_R1_LINUX_DEV/lx_inventory.py` | `8ea74ed3621e805066727a4ca3f20253f9a85c90857aca8d8e41e02607cfa597` |
| `streams/CLOUD_R1_LINUX_DEV/tests/test_lx_platform.py` | `e7f9b2d60d45eb338082068ccd8d6d1ac0441135665b808c453aac133f44495f` |
| `streams/CLOUD_R1_LINUX_DEV/tests/run_mutants.py` | `9feca6b477b1103b263b6f97911563a78ba26b6203605fc569662e93a1046b6a` |
| `streams/CLOUD_R1_LINUX_DEV/results/TEST_RUN.json` | `2d1685940d855e9d1925670012b98d3445d4b18d5f840e4933205bd89d4f9e28` |
| `streams/CLOUD_R1_LINUX_DEV/results/MUTANTS_RUN.json` | `e2db08c23013f03ccacb29b54d5094db47d0ba61f8b020251b7ebfb7a2b29f2c` |
| `streams/CLOUD_R1_LINUX_DEV/README_DEV_ONLY.md` | `003f6722cd2ff63cf5fcf545136aa4a40cb492c25a829b2b5897f571f80c7559` |
| `ledger/briefs/61_reviewCLOUD_R1_DELTA2.txt` | `c4b3caa4b0e9a902d8439e7cee36ae9243cf127800a899ad90b715d17ebedc75` |

### Preservation

The Cloud governance directory delta contains only two additions, the r3 amendment and r3 owner brief. Every preexisting file in that directory remains byte-unchanged by Git blob identity. Explicit `git show` byte comparisons additionally confirmed these reviewed documents (abbreviated directory `governance/new_host_route_cloud_r1/`):

| Preserved file | SHA-256 at both endpoints |
|---|---|
| `CLOUD_FEASIBILITY_R2.md` | `02a030ad51ed7589e381fb72ff0fafda42035cf8b3f3945b81d3c324d9ce848d` |
| `OFFICIAL_PROVIDER_FACTS_20261014.md` | `4da1d9388dae19c456a1b916c6b6f009370d377f5a7e40d9f8761008ea881c92` |
| `PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1.md` | `386f49f30113769467c4e1f70031224d8b648e77d8896e5f5ac7a18b67589054` |
| `OWNER_DECISION_BRIEF_CLOUD_R1.md` | `c7960a9a6f23471c6602b43ce8e30fc877d924e9fe6f1cb90b919acab9e180d4` |
| `CLOUD_HOST_INVENTORY_R2_20261014.json` | `a0fb55046e36a503b3b7870d77eb6a1c05c8a180206ef85e14fab3152959f44d` |
| `PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R2.md` | `e61b09632059958d84f0a6357c3e2dfed36dcf8469e847c5b6684160b58b9dfe` |
| `OWNER_DECISION_BRIEF_CLOUD_R1_R2.md` | `22e3be21aac020c7f2d564e3fa7e7a776f538b500139d079d327bc8614f20f98` |
| `CLOUD_FEASIBILITY_R2_ERRATUM_E1.md` | `0a40fd651985e89e18532e4da347023d2f08cfd0396d322d598fb639438c9aef` |
| `OFFICIAL_PROVIDER_FACTS_20261014_ERRATUM_E1.md` | `c329d2aa7145c750ede07737a5c20fb830751cb3783a4a966b8b21a659d521fd` |
| `CLOUD_HOST_INVENTORY_R2B_20261014.json` | `d41fae8a5c49cd88048d3b9b5dc81c5790a353685bfa4df6942bbd66eb19bc0c` |
| `USER_AUTHORIZATION_20261014.md` | `a202596d3ac2e417565b437bb3791ed479dd230e7abaee1e2ee0a0636bc650b9` |
| `ROUTE_PREPARATION.md` | `80c9f5a07191592b0d606cc713708ababd62acd4e8fd7b481ec08411f4b3be99` |

Review 59 remains byte-identical with SHA `c394c035c26ae8f5c3f73d98207a6fbc6cb240502a112fc76cd4d889e3f56ebf`; brief 59 remains byte-identical with its hash above. The complete `reviews/scratch_CLOUD_R1` tree has the same tree object `ca9ea144196f1a4279270a391ded304c4e5d6f52` at both endpoints. Development source/tests/results are intentionally revised in place and are not claimed preserved. Scanner source and `ledger/briefs/BRIEF_CHECK.json` have no delta; the latter's contents were not opened. New index assertions of zero tail hits were not independently rerun here.

## Actionable findings

### E1 — MINOR: revision-3 documentation contains stale counts and revision labels

Locations: `streams/CLOUD_R1_LINUX_DEV/README_DEV_ONLY.md:27,42`; `lx_platform.py:1`; `tests/test_lx_platform.py:1`; `tests/run_mutants.py:5–6,207–208`.

README says **74** tests, while the committed AST count and TEST_RUN both show **75**. Its open-decision reference is still amendment **r2 §4**. Both module/test first-line descriptions still say revision 2, despite the revision-3 body/records. Harness description says N01–N12, while its actual set is N01–N14. It also says nothing outside a temporary directory is written although its optional output argument writes an arbitrary output path and the README demonstrates a write to `results/MUTANTS_RUN.json`.

Required correction: align revision/count/range/reference labels with revision 3 and qualify the harness write statement to its no-output-argument mode. The brief's explicit no-output-argument rule was followed and protects the review run; no repository write occurred here.

### E2 — NOTE: mutation records do not establish failure attribution

Locations: `tests/run_mutants.py:172–174,190–200`; `results/MUTANTS_RUN.json` M29; `tests/test_lx_platform.py:881–884`; `lx_platform.py:983–984`.

The harness labels every nonzero suite exit KILLED and preserves only the last stderr line. It runs baseline afterward and inherits `LX_PLATFORM_DIR` for that baseline, while hashing SRC. It records neither per-mutant failure names/tracebacks/test count nor the interpreter/host/run command. Thus an import failure, transient host failure, or error in an unrelated test can be indistinguishable from a valid kill in the persisted record. All mutated sources are syntax-valid, so no current syntax-error kill was found.

M29's lone recorded `errors=1` has a plausible and precise intended cause: it removes the execute/resume launch-gate insertion when `launched=None`; the test directly subscripts that required key and should raise `KeyError('launched_by_systemd')` at line 884. Such an error is a sound kill of this weakening. Its actual traceback remains UNVERIFIED here; the parent was asked to capture it. The other 64 recorded failures also require fresh traceback attribution for a fully independent verification.

Required verification/correction: replay on a suitable Linux host with `LX_PLATFORM_DIR` unset for the baseline; capture test count, failure/error names and tracebacks for each mutant; classify unrelated test/import/host failures as invalid runs. A related required-key KeyError may count as a behavioral kill, explicitly documented. Baseline should pass before mutation testing and be tied to the actual imported module bytes. Preserve interpreter/command/environment provenance with the evidence. This is an evidence-strength limitation, not a demonstrated revision-3 fail-open path.

Counts within this subreview: BLOCKING 0; MAJOR 0; MINOR 1; NOTE 1.

## Scanner implementation and safe, limited command

`c308_quarantine.py:326–377` statically reads every Python/text file in its supplied root. The public `scan(root)` always enables both planted negative controls. It emits PASS only if both controls pass and the unsanctioned finding list is empty. `REPORT_ONLY` values (`SUPPRESSED_LITERAL`, `ATTENTION_DRIFT_LITERAL`) and sanctioned historical/text findings are reported separately and do not gate PASS. The CLI at lines 422–428 ignores any supplied root path: `--scan` calls `scan()` with full NS and exits zero only for PASS. Running without `--scan` calls cell/drift guard selftests and is outside this task's execution scope.

**Do not use the CLI full-NS scan under these exposure restrictions.** It would read forbidden material. The following exact command, supplied to the parent but not run by this subagent, scans a seven-file target-free D1 projection, imports no platform/science code, keeps controls enabled, sanitizes hit values, and fails on any non-PASS result. Importing the scanner reads its sanctioned `ledger/TAIL_FIGURE_PATTERNS.json` pattern table; this read is intrinsic to the scanner. It does not establish a verdict for the full namespace, governance documents, ledger or reviewer scratch.

```sh
python3 -B - <<'PY'
import json
import shutil
import sys
import tempfile
from pathlib import Path

ns = Path('level4/closure_proofs/p5y_k5_cell308_research').resolve()
src = ns / 'streams/CLOUD_R1_LINUX_DEV'
files = (
    'lx_platform.py', 'lx_inventory.py',
    'tests/test_lx_platform.py', 'tests/run_mutants.py',
    'README_DEV_ONLY.md', 'results/TEST_RUN.json', 'results/MUTANTS_RUN.json',
)
sys.path.insert(0, str(ns / 'code'))
import c308_quarantine as q
with tempfile.TemporaryDirectory(prefix='cell308-review61-scan-') as td:
    root = Path(td)
    for rel in files:
        destination = root / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src / rel, destination)
    result = q.scan(root)
    safe = {k: result[k] for k in (
        'verdict', 'py_files_scanned', 'text_files_scanned', 'py_file_list',
        'py_negative_control_detected', 'text_negative_control_detected',
        'report_only_counts',
    )}
    for key in ('findings', 'report_only', 'sanctioned_historical_read_py', 'sanctioned_text'):
        safe[key] = [{k: hit[k] for k in ('file', 'line', 'kind')} for hit in result[key]]
    print(json.dumps(safe, indent=2))
    raise SystemExit(0 if result['verdict'] == 'PASS' else 1)
PY
```

Expected coverage is four Python files and three text files, plus the scanner's synthetic controls. Full-NS PASS is UNVERIFIED. Static scan does not establish fail-closed platform behavior or governance acceptance.

## Fresh Linux verification requirements sent to the parent

Run from the immutable development stream, keep results untouched, and use an environment with `LX_PLATFORM_DIR` unset. The suite needs Linux `/proc`, glibc libm/libc/ld-linux mappings, git, and historical candidate commit `142d97a9` for the permitted read-only constant check. It has live process/zombie/SIGKILL behavior and no macOS skip guard. The r1 inventory comparison and live-preflight test contain host-specific expectations, so host-related failures must be attributed explicitly.

```sh
python3 -B -W error::ResourceWarning -m unittest discover -s tests -v
python3 -B tests/run_mutants.py
```

The mutation harness does not elevate ResourceWarning itself; that difference must be recorded rather than silently equating its invocation with TEST_RUN. Run only interpreters already present; verify the claimed CPython 3.11.17/3.12.3/3.13.16 paths/versions if available. Unsupported or unavailable versions remain UNVERIFIED. Preserve fresh raw baseline/mutant output outside the repository and compare hashes and counts to the above records. The parent's Linux replay, not this static subreview, supplies the fresh-run portion of Q5.
