# Receipt: owner statement 6, scoped administrative checks and preservation of scan evidence (Cell-308 Cloud route r1), 2026-10-18

**Status: OWNER-ISSUED DIRECTION (recorded verbatim) · RECEIPT · ADMINISTRATIVE EFFECTS ONLY.**

Statement 6 grants none of the following:
* an A14b clearance;
* a risk, materiality or T6 ruling;
* a policy adoption;
* any scientific or operational authorization.

`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The record

| item | value |
|---|---|
| verbatim copy | `OWNER_STATEMENT_6_SCOPED_ADMIN_CHECK_AND_PRESERVATION_20261018.txt`. Byte-identical to the upload (`cmp`): 11,950 bytes, sha256 `ed4b6c8f65712a6d4f21dd0b6e06fb9f24e122eec2458639722b0b059dc7a04f`. Tail-figure count before reading: 0 |
| reference state | PR3 head `17fbe82ac5fef227c4a346570b38a8c09da52977`, draft, unmerged. No newer commits on the remote |

## 2. The conflict, and what stops (statement 6 §1)

* **The conflict.** `c308_quarantine.py --scan` calls `scan(root=NS)`, and `_scan_tree` walks the whole research namespace. That walk reads the excluded files (dispositions erratum E1 §E1.2).
* **What stops.** The coordinator no longer runs that command against the real namespace, nor any other invocation that reaches the same files.
* **Still unresolved.** C-1 to C-5 stay **UNRESOLVED** under statement 4.
  * Neither this statement nor any PASS line finds that observation content reached the coordinator, or that it did not.
  * It does not excuse the earlier access, and it does not establish the coordinator's independence.

## 3. The historical substitution for commit 17fbe82a (an observation, unapproved at the time)

The coordinator ran a scoped invocation before commit `17fbe82a`. **It was not approved when it ran.** It is **not** a
pre-commit check under the procedure approved now, and it is **not** a full-namespace pass. Its defects, against the
procedure now approved:

* **Inputs.** It used **working-tree copies**, not staged index blobs.
* **No manifest.** It recorded no blob ids, modes or per-file hashes.
* **A derived file for the ledger.** It represented the ledger by a file of the added lines only, under `ledger/`. The
  real ledger blob was not scanned.
* **Unconfined loading.** It imported the scanner **from the real research tree**. So the module's namespace, and its
  read of `ledger/TAIL_FIGURE_PATTERNS.json`, were in the real tree. Only the scan root was confined.
* **Fixtures outside scratch.** The built-in controls created their temporary fixtures in the system default
  temporary directory.
* **No post-commit check** of the committed blobs against what was scanned.

Its reported result was: 6 text files, 0 findings, 0 sanctioned matches, verdict PASS. That remains a historical
observation only.

## 4. Prospective approval, as applied (statement 6 §2–§5)

**Scope.** The approved check is the coordinator's **SCOPED_ADMINISTRATIVE_CHECK**. It applies **only** to documentary
commits that are already authorized, and it covers **only** the exact staged blobs on an explicit permitted path list.
It replaces the full-namespace command **for those commits only**.

**The whole-namespace obligation.**
* **Source: not identified within the permitted scope.** The scanner's own comments refer to incident reviews C5 and
  C8. The briefs-index header names the `--scan` command.
* The coordinator does not search for the source documents. It does not relabel the scoped check as that obligation.
* If the obligation is binding, it **remains unsatisfied** until a separately authorized operator and scope satisfy
  it. It is **not** a prerequisite for the A6b Phase 1.

**Scanner and configuration**, both at pin `17fbe82ac5fef227c4a346570b38a8c09da52977`, both unchanged:

| item | path (under NS) | blob | bytes | sha256 |
|---|---|---|---|---|
| scanner | `code/c308_quarantine.py` | `e103c196ef0e393d9a7bca038ca8ab38d5841f11` | 19,470 | `72d529cc352208fe6dc9c2045d991a799eb0fcca2f2fe3b2969cd5b7554faa12`: **MATCH with the owner's binding** |
| configuration | `ledger/TAIL_FIGURE_PATTERNS.json` | `ab0104c6b534171d0969768810d7f0f8c1d05517` | 1,327 | `0dc2addcd6ac667c6866736ab913a2513b6ec848636d2fbb04051d02ab49cbf5` |

* The configuration was copied as opaque bytes. It was not displayed and its patterns were not printed.
* **No conflicting accepted access restriction on it is known.** The coordinator's earlier tail-figure helper also
  loaded it by process. It printed counts only, apart from the file's schema line and the number of patterns, which
  were displayed once earlier in this session.

**The scratch tool.** It is private and is not in the repository:

| file | bytes | sha256 |
|---|---|---|
| `adminqc_tool/adminqc.py` | 6,568 | `a2c20447371abb5dcb2d215a48c9eac2f9942a8e9640ae63b5d2a69dd602afe8` |
| `adminqc_tool/runner.py` | 590 | `68bc4fbf26362c6bc3857860ae68e5b3644314e26f42a9b001d5ef7926527c7d` |

**What the tool does:**
1. It reads the change set with `git diff --raw --no-abbrev -M`, from the index or from a commit against its parent.
2. It **stops** on any of the following: a rename or copy; a status other than A, M or D; a mode other than `100644`
   on an added or modified file; an absolute path, a traversal path or a path outside the namespace; any change not on
   the permitted list. An out-of-scope change is reported by count only, without its name.
3. It treats a deletion as metadata only.
4. It extracts **index or commit blobs** by object id into a fresh `input_root`, at their namespace-relative paths, and
   refuses any path that would escape that root.
5. It copies the scanner and the configuration, by blob id, into a separate `tool_ns`, and verifies their length and
   SHA256.
6. It runs `python3 -I -B` (Python 3.13.16) with a minimal environment, and `TMPDIR`, `HOME` and the working
   directory all inside the private area.
7. The runner loads the isolated copy, checks that the module's namespace **is** `tool_ns`, and calls
   `scan(root=input_root)` with the built-in controls on.
8. The full result is written privately and is never displayed. Only counts, flags and the verdict are printed.
9. The tool re-reads the change set and refuses the result if it changed during the check.

## 5. The bounded verification of 17fbe82a, performed now (statement 6 §6)

**Not backdated.** It is not a pre-commit check of that commit, and it does not clear C-5.

* **Parent identity verified first:** `17fbe82a^` = `412214d870f7ccc4d842c35b01bdc8b0ac5cd864`.
* **Permitted path list:** the six paths that commit was authorized to change. The five statement-5 records are
  listed as files 1–5 below, and the sixth is `ledger/TARGET_INTEGRITY_LEDGER.jsonl`. No change lay outside the list.

**Receipt.** `SCOPED_ADMINISTRATIVE_CHECK`, label `RECHECK_17fbe82a_VS_412214d8`, checked at `2026-10-18T04:29:23Z`.

| # | path (under `governance/new_host_route_cloud_r1/` unless shown) | status | oid | bytes | sha256 |
|---|---|---|---|---|---|
| 1 | `A14B_ROW_DISPOSITIONS_R1_ERRATUM_E1_20261018.md` | A | `f51cb7ed…8fd6` | 5,035 | `bc41616d…5e70` |
| 2 | `FINDINGS_STATUS_REGISTER_R2_ERRATUM_E8_20261018.md` | A | `1fb64c27…a34e6` | 957 | `2efd2576…7c7f` |
| 3 | `OWNER_STATEMENT_5_RECEIPT_20261018.md` | A | `e8b1e373…0c72` | 4,970 | `5cf6ec1a…71ee9` |
| 4 | `OWNER_STATEMENT_5_ROW_DISPOSITIONS_AND_LIMITS_20261018.txt` | A | `54cae0d5…47aa` | 8,386 | `89430b74…00e1` |
| 5 | `READINESS_MATRIX_R4_ERRATUM_E8_20261018.md` | A | `28d67713…7fff` | 2,082 | `cd6940ae…8e60` |
| 6 | `ledger/TARGET_INTEGRITY_LEDGER.jsonl` | M | `2882cd23…15bc` | 532,570 | `2fd49b41…ca11` |

All six have mode `100644`.

**Results:**
* text files scanned: 6; `.py` files scanned: 0;
* **findings: 0** (by kind: none); sanctioned-text matches: 0; sanctioned historical-read `.py`: 0;
* report-only: SUPPRESSED_LITERAL 0, ATTENTION_DRIFT_LITERAL 0;
* controls: `.py` negative control **detected**; text negative control **detected**;
* **verdict: PASS** (scoped).

The full result is kept unopened in the private run directory.

## 6. Preservation of the old scan outputs (statement 6 §7)

* **Which files.** The earlier full-scan outputs are `scan.json`, `scan2.json`, `scan3.json`, `scan4.json`, `scan5.json` and `scan6.json`, at the root of the coordinator's scratchpad (`/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/`). These names come from a listing earlier in this conversation; no new listing was made.
* **How they are kept.** They are **unopened, unhashed, unparsed, uncopied and undeleted**. Their parent area has had no cleanup and no permission change.
* **Preservation limit.** The scratchpad is in an ephemeral cloud container, which is reclaimed after inactivity or when the session ends. **Durable custody cannot be established.** They have not been exported.
* No forensic reader is appointed. Any later examination needs its own authority and scope.

## 7. A6b

* The Phase 1 appointment is separate and unchanged.
* A genuinely new Codex candidate, launched by the owner, may fetch only the brief at `412214d8`
  (`aa096077…4725`). It then submits its disclosure and stops.
* The coordinator does not launch it or message it.
* Phase 1 does not grant Phase 2.
