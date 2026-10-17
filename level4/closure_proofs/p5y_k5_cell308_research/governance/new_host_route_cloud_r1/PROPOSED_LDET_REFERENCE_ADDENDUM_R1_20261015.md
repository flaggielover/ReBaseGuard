# PROPOSED L-DET reference addendum, draft r1 — MBR1_REPRO reference records and comparison functions (Cell 308, Cloud route r1)

> **Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE · DEVELOPMENT/PREPARATION ONLY.** This draft answers the condition that
> amendment r5 §5 item 1 carries into the formal route review (review 60 F5 / N10): "each record's path, commit and
> sha256, and the sha256 of the strip and serializer functions (item 4), are listed by a non-holder in a reference
> addendum that is **part of the text the formal route review accepts**, before OD-3 is put to the owner." It becomes
> that addendum only if the formal route review verifies and accepts it. It authorizes no L-DET run, no qualification,
> no host and no OD-3 decision. `new_target_evaluations = 0` · `cell309_activity = none`.

## 0. How this was compiled, and its limits

* **Compiler.** The Claude Cloud coordinator of the 2026-10-14/15 session. Non-holder status is **self-declared and
  unverified**: in this session the coordinator opened none of the E1″ material
  (`ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`, REVIEW_EXECUTION_INTERRUPTION*, the interruption assessment, the incident
  audit) and no MB r1 postexec or target-run file. **Disclosure:** while locating the pin commit the coordinator printed
  the one-line commit subject of `21e99cf0` (truncated to 160 characters); it names an MB r1 postexec recovery record. No
  file, tree or diff of that commit was listed or opened, and this draft does not use that commit as its anchor (§1).
  The formal route review must establish the compiler's non-holder status independently; a self-declaration is not
  that evidence.
* **Method (read-only, value-free).** Git object reads only: `git rev-parse <commit>:<path>` for blob ids,
  `git cat-file blob <id> | sha256sum` for sha256, `git log --find-object` for the introducing commit, `git merge-base
  --is-ancestor` for ancestry. **No record's content was printed, parsed or opened**; no value of any record is stated
  here, so E8 is not engaged. Function digests come from parsing candidate source text obtained by `git show` with
  Python `ast` (nothing imported or executed; script `reviews/scratch_LDET_REFERENCE_20261015/fn_digests.py.txt`,
  output `FUNCTION_DIGESTS_142D97A9.json`).
* **Clone.** The checkout is a shallow clone (`.git/shallow` has one boundary). The introducing commit below was found
  within the available history; a full-history clone should confirm it (§3 item 3).

## 1. Reference records (MB r1's committed official r3 non-target records)

Source of the case-to-file mapping: the candidate's `MBR1_RECORD_PINS` (`mbs308_qualify.py` lines 1822–1839 at
`142d97a9`), whose sha256 and blob prefixes all match the bytes below. Accepted text naming the case set: route A1 §3 /
`registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md` ("QC02 (decoy 297), QC03 (decoy 316, blocks 0–2), and the QC04
validation-drift ladder pair").

| case | candidate key | path | sha256 | git blob |
|---|---|---|---|---|
| QC02 (decoy 297, every block, Stage 1 and Stage-2 bundles) | `decoy297` | `level4/closure_proofs/p5y_k5_cell308_mb_r1/qualification/MB308_QC02_DECOY_297.json` | `14e1ac26e483f90e7845eab92d7e6ff629e497a6ca9ba521b4b7aca734e04f02` | `1096a8533a2cbe80aa9550be80cddfc532d0a6ea` |
| QC03 (decoy 316, blocks 0–2) | `decoy316` | `level4/closure_proofs/p5y_k5_cell308_mb_r1/qualification/MB308_QC03_DECOY_316_B3.json` | `678025c1420f6162047a441d8ee60b384cbcdb85d028a929a3680cc581922998` | `581843963b8cd8821e678ed8dba58e4a166dd041` |
| QC04 serial block 0 of decoy 297 (see §3 item 2) | `serial` | `level4/closure_proofs/p5y_k5_cell308_mb_r1/qualification/MB308_QC04_SERIAL_297_B0.json` | `d697870767caab5a2771a6c0772c15d0e7485280e7110821d73ae654b7227671` | `26e1b0c845703f8fd871aa03c0aaf0548821d697` |
| QC04 ladder-determinism record A | `det_a` | `level4/closure_proofs/p5y_k5_cell308_mb_r1/qualification/MB308_QC04_LADDER_DET_A.json` | `fc6d02271aa7f6d049b0029e764153e4c09d2f2f030fcecc5e7021979940f540` | `e8be508c567d94912b814671069cc9caef882238` |
| QC04 ladder-determinism record B | `det_b` | `level4/closure_proofs/p5y_k5_cell308_mb_r1/qualification/MB308_QC04_LADDER_DET_B.json` | `e3952991a0a3815de660afe5457fe3857bc0d1f6bee85c379c58840cdade8cb5` | `f51dd0eeee4895451dbb0443dfad0a9103e94700` |

**Commit facts (verified 2026-10-15):**
* Every one of the five blobs was first introduced by commit `7eb057bbbcb3c8d18afc852c1d90f0b3fc0fefc8`
  (committer date 2026-09-29T19:22:35+09:00), found with `git log --all --find-object`.
* Freeze r3 `c46434a3` is an ancestor of `7eb057bb`, and **none** of the five paths exists at `c46434a3`. The r3
  records therefore post-date freeze r3, the case amendment r5 §5 item 1 anticipated ("it may post-date freeze r3").
* `7eb057bb` is an ancestor of the candidate `142d97a9`; none of the five paths changes in `7eb057bb..142d97a9`, and
  the blobs at `142d97a9` are identical.
* The candidate's comment binds the pins "at 21e99cf0"; the same five blobs are present there. This draft anchors on
  the introducing commit `7eb057bb` instead (see the disclosure in §0).
* None of the five paths exists on the research tip `88a16f74` or on this integration branch: L-DET must read them from
  the pinned commit by blob id, never from a working tree.

## 2. Comparison and serializer functions (amendment r5 §5 item 4)

Files at the candidate `142d97a9`:

| file | git blob | sha256 |
|---|---|---|
| `level4/closure_proofs/p5y_k5_cell308_mbs_r1/code/mbs308_qualify.py` | `0ac40ba9cec0d3c01498d5706e41d4309a926a97` | `52120a2401e7bf18adf26aed3d1a52892a2e946632d76d73d4ea0f54b7e639d3` |
| `level4/closure_proofs/p5y_k5_cell308_mbs_r1/code/mbs308_driver.py` | `80c88355f25745c920a5128deb76fd93fee205ff` | `117624e9477f6b315f1c9a63920d10e79a0f8819aafad5d0eeff50adf71beab1` |

Definitions (top-level; `source_sha256` = sha256 of the exact source segment, interpreter-independent; `ast_sha256` =
sha256 of `ast.dump(node, include_attributes=False)` under CPython 3.13.16, whose dump format may differ in other
versions):

| file | definition | lines | source_sha256 | ast_sha256 |
|---|---|---|---|---|
| `mbs308_qualify.py` | `TIMING_KEYS` | 94–94 | `2b247c9883f7bdff86cbb2ac7eb4f4fe90c2e29a9bc42f499c28fe8fcc595fbd` | `16a7771c1d2bcb5b99cd981b1949a005d799da570bdab88121775430c058f2b6` |
| `mbs308_qualify.py` | `strip_timing` | 1109–1114 | `2853b9dfcebbd59ad8394d4e1f4510d3d199eb9c69001a69d80107d641a6dc50` | `a654543e96ff564a41372e03a9dfdd948d6d726280417e3083ee62edfd4343f3` |
| `mbs308_qualify.py` | `MBR1_RECORD_PINS` | 1823–1839 | `941286057e59004620035681a20690ce0d53d9cdaa7aad2ba1f9fc7d3bc3f6dd` | `92f635127c4a5215f771b611fe6630a293ed758aafc60b3ffdace8e149a8855a` |
| `mbs308_qualify.py` | `pinned_bytes` | 1852–1860 | `930ea615ec1b642ee1d6b90f41276941b2802d2dbf711005674c525ab8314dba` | `e6880060c68b63ff14763f579e3996ffe0bb6142d89e66735c8316398bb6efba` |
| `mbs308_qualify.py` | `_strip_decoy_timing` | 2409–2416 | `164379ef3ab00e8e6fe4fd7e090a4390ffd895411f7069cb00550950892adfd6` | `3c401aa74fd7b1c02316bb22c6178773682f3c7adc6fb74b22d133dcce0a5687` |
| `mbs308_qualify.py` | `_leaves` | 2419–2424 | `036589bae0eeea739d1e78f47ed3f8b85952adf61384981ee2fbed4cb72a5689` | `f8d9d3c7c4ded910c00e2de9a6fc8746ccd57f839659dc075cceda01cf7442e9` |
| `mbs308_qualify.py` | `_public` | 2427–2434 | `f1a79ac8b92e08e0ffe42ca9fc15f030a032ee165c38b8ce7dffd52e126c3f24` | `d3543d5d6ced4342c0ecfc00857af500e0f15a84ccf27e49a79c03a8793ca01f` |
| `mbs308_qualify.py` | `_serial_view` | 2437–2443 | `e7b35757a8bf420a98e13fbb61ec09b5bc5c96268116c8a87bf220bf2e05603f` | `fcd833e76bbcfc77cf2b0b6a077f9799911f885346e04d0ed04eeb91a6b3b150` |
| `mbs308_qualify.py` | `_ladder_view` | 2446–2450 | `5bbd365eb3baad8115889f61ee5abad360a62042805fd391952f46c94c254241` | `eafb23f6def68705fab21fa600f8ba4805578990c6e278a498a12ec3b6af827f` |
| `mbs308_qualify.py` | `_decoy_view` | 2453–2464 | `8d39c956f8b45d03f9974f1969acee9643715a33c3cd48f9dbee43525d12772a` | `8359981dafff953901dc84654b72a3c6e846a7c03bf5cfa54217e906f56a524b` |
| `mbs308_qualify.py` | `_compare` | 2467–2469 | `f7e7d90e993486dc2545e8308d06542f5f5eb37c1ae63b3f4dd1661dc9e59d1d` | `6e434e53452428e8961c836b98f55ad19c9c794def72f7c9179f88c5f1087b81` |
| `mbs308_qualify.py` | `_planted` | 2472–2490 | `ac6f3664b24648d501609c03c172d03beca674c80e0e75828c5eec44fa0ab7aa` | `9ba28b3103362c3511ccca9f08fddb6cebc0d55e1bd466dc80db956f30d0d15e` |
| `mbs308_qualify.py` | `_job_rows` | 2536–2546 | `2a477455430e93be6fc52578872c80368443444b48321f43696c59c615b2a09f` | `5a86004be4d8c061c8accf9597f25b49ebaf097dfadda4c8f6eb14ce075e3589` |
| `mbs308_qualify.py` | `mbr1_repro` | 2549–2579 | `48eb4cc05c3360b5350014a5037861434066d7bc6b24bc1ad1ee4ba406498bc4` | `60daa6947b827c3227b750032d3dca35d1bbbc5ee68c3eafe30ce575e7030e3e` |
| `mbs308_driver.py` | `fs` | 317–319 | `b3be3c314aa4676d6523306e1d2cd93fdb2be4a48f9dfdea5be022700a00e49b` | `8d84092005d81297bf016aefd40538b87a7f5f7293819fb77aba5862ac095d02` |
| `mbs308_driver.py` | `jsonable` | 345–352 | `7e1499ac6f7a7c622fa99ed50b0b2f0ca27d18cda3686b71a40190a746189224` | `24733b913f36d345fcb7db705c50ee6428f35cd7f4d9ece7de3f840dfd3fa192` |

What these implement in the candidate (read from source, not run):
* **Strip.** `TIMING_KEYS = {seconds, wall_seconds, cpu_seconds}`; `_strip_decoy_timing` removes those keys and
  `cpu_cap` at every depth; `strip_timing` removes `TIMING_KEYS` only (used by `_serial_view` / `_ladder_view`, while
  `_ladder_view` drops the job-level `cpu_cap` itself).
* **Views.** `_public` drops `_`-prefixed keys (the driver's publication projection); `_decoy_view` compares identity
  (cell, blocks) and every certified part, excluding provenance (host, lifecycle, driver sha256, utc, walls, cpu caps)
  and `stage1.workers`; `_serial_view` and `_ladder_view` as named.
* **Comparison.** `_compare` = equality of the two views after `json.loads`, plus a non-vacuity count; `_planted`
  mutates one middle leaf and requires the same comparison to differ; `mbr1_repro` requires every row equal, non-vacuous
  and control-detected.
* **Serializer.** Successor records are written by `json.dumps(jsonable(out), indent=1, sort_keys=True) + "\n"`
  (`mbs308_driver.py` lines 1879 / 1895); `jsonable` renders `Fraction` through `fs` and drops `_`-prefixed keys.

## 3. Gaps found while compiling (for the formal review; none is resolved here)

1. **Item 4(b) is not implemented by the candidate.** Amendment r5 §5 item 4 proposes both (a) exact equality of every
   certified leaf "in exact rationals" and (b) byte equality of the serialised records after the timing strip. The
   candidate implements a structural comparison after `json.loads` only. Two consequences: (i) JSON **number** leaves
   are compared as Python numbers (`int` exactly, non-integers as `float`), so two decimal spellings that parse to the
   same double, or `1` and `1.0`, compare equal; only leaves serialised as strings (the `fs` rendering of rationals)
   are compared textually; (ii) MB r1's records were
   written by MB r1's own driver, not by the candidate's serializer, so a byte comparison needs a **canonical
   re-serialization of both stripped views**, which no accepted text defines. **[PROPOSED, not decided]:** parse both
   sides with `json.loads(..., parse_float=decimal.Decimal)` (exact decimal text preserved), apply the pinned views, and
   compare `json.dumps(view, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)` byte for byte, in
   addition to (a). This is a **new comparison rule** and must be labelled so; it changes no science.
2. **Case set.** The accepted text names three cases (QC02, QC03, the QC04 ladder pair). The candidate's full form also
   compares `MB308_QC04_SERIAL_297_B0.json` (the QC04 serial block-0 record). Comparing it is stricter, not weaker, but
   the formal review should state whether it belongs to MBR1_REPRO's reference set.
3. **Shallow clone.** Confirm §1's introducing commit on a full-history clone.
4. **Non-holder.** The compiler's status must be established by the formal review (§0).
5. **Interpreter-dependence of `ast_sha256`.** Use `source_sha256` as the binding digest, or fix the interpreter
   (D-INTERPRETER) before relying on `ast_sha256`.

## 4. What remains before OD-3 (unchanged by this draft)

The formal route review accepting the amendment and this addendum (or a corrected one); D-RC2-SCOPE and
D-INTERPRETER decided; a host (OD-1) meeting H1–H8; the reviewed Linux successor build (ROUTE_PREPARATION step 4) as
the only code path; then the owner's OD-3. All 21 D-* decisions remain undecided.
