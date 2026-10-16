# L-DET specification packet — Cell-308 Cloud route r1 (preparation for the formal route review)

**Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE · NOT EXECUTED.** This packet specifies what the formal route review
must fix for gate L-DET (amendment r5 §5) and the reference addendum (`PROPOSED_LDET_REFERENCE_ADDENDUM_R1_20261015.md`,
sha256 `4efcd152…5277`). It runs no case, opens no record and authorizes no OD-3. `new_target_evaluations = 0` ·
`cell309_activity = none`.

## 0. Required order (unchanged)

1. The accepted amendment and the accepted reference addendum, with the relevant owner decisions:
   * D-RC2-SCOPE;
   * D-INTERPRETER;
   * D-PIN-POINT;
   * D-LDET-REPEAT.
2. Actual-host evidence H1–H8 for the one host chosen under OD-1, accepted under the attestation procedure.
3. The reviewed Linux successor build (ROUTE_PREPARATION step 4) as the only code path.
4. The owner's OD-3.
5. Only then one L-DET attempt on that host.

None of these holds today.

## 1. Comparison semantics (amendment r5 §5 item 4)

The candidate's `_compare` (`mbs308_qualify.py` lines 2467–2469 at `142d97a9`) is **structural only**: equality of
two views after `json.loads`, plus a non-vacuity count. It does not implement §5 item 4. Two consequences:
* non-integer JSON numbers are compared as floats, so `1` and `1.0` compare equal;
* there is no byte comparison (addendum §3 item 1).

**Proposed specification (a new comparison rule; changes no science):**

| part | definition |
|---|---|
| inputs | (R) the reference record bytes, read by blob id from commit `7eb057bb` (§3); (S) the successor's record bytes as written by the reviewed successor build |
| parse | `json.loads(b.decode("utf-8", errors="strict"), parse_float=decimal.Decimal, parse_int=int, parse_constant=<raise>)`; duplicate keys refused (`object_pairs_hook` that raises); NaN / Infinity refused |
| view | the pinned view functions of the reference addendum §2 (`_decoy_view`, `_serial_view`, `_ladder_view`, `_public`, `strip_timing`, `_strip_decoy_timing`, by `source_sha256`), applied to both sides |
| (a) exact rational | every leaf of the view converted exactly: `int` as is; `Decimal` → `fractions.Fraction(Decimal)`; a string in the grammar that `mbs308_driver.fs` writes for a `Fraction` → `Fraction(string)`. The exact grammar is to be stated by the reviewer from the pinned `fs` source; this packet does not assume it; other strings compared as strings; booleans compared as booleans (never as integers). Equality is of the converted trees, with key sets equal at every level |
| (b) canonical bytes | `json.dumps(view, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=_canon)` encoded UTF-8, where `_canon(Decimal)` is the exact decimal text `format(d, "f")` normalised to remove an exponent, never a float. The two byte strings must be identical |
| non-vacuity | the count of compared certified leaves per case is recorded and must be at least the count fixed in the accepted addendum (the reviewer computes it once on the reference side, value-free: a count, not a value) |
| control | the candidate's `_planted` construction (one middle leaf mutated) must make both (a) and (b) report a difference |
| outcome | MATCH only if (a) and (b) are equal for every case, non-vacuous and control-detected; anything else, including any parse or view error, is MISMATCH or INCOMPLETE |

**Open for the reviewer:**
* whether (a) and (b) together are the right reading of "exact equality of every certified leaf, timing stripped" (route
  A1 §3);
* whether `_public` applies on both sides;
* the leaf-count floor.

## 2. Case set and the QC04 serial record

[ACCEPTED] route A1 §3 names three cases: "QC02 (decoy 297), QC03 (decoy 316, blocks 0–2), and the QC04
validation-drift ladder pair". The candidate's `MBR1_RECORD_PINS` also compares `MB308_QC04_SERIAL_297_B0.json`.

**Proposed (recommended ruling, for the formal review):**
* Include the QC04 serial block-0 record as a **fourth** compared record, labelled an addition beyond the accepted case
  set. It is stricter, not weaker, and it is in MB r1's committed r3 record set.
* Its inclusion is fixed **before** OD-3, never after a result.
* A mismatch on it stops the route exactly like the other three.

Authority: the formal route reviewer, then the owner (part of OD-3).

## 3. Reference-pin provenance

Re-verified **2026-10-16** in this session by git object hashing only (no record opened or printed):

| record | blob at `142d97a9` | sha256 |
|---|---|---|
| `…/p5y_k5_cell308_mb_r1/qualification/MB308_QC02_DECOY_297.json` | `1096a853…` | `14e1ac26…4f02` |
| `…/MB308_QC03_DECOY_316_B3.json` | `58184396…` | `678025c1…2998` |
| `…/MB308_QC04_SERIAL_297_B0.json` | `26e1b0c8…` | `d6978707…7227671` |
| `…/MB308_QC04_LADDER_DET_A.json` | `e8be508c…` | `fc6d0227…f540` |
| `…/MB308_QC04_LADDER_DET_B.json` | `f51dd0ee…` | `e3952991…8cb5` |
| `…/p5y_k5_cell308_mbs_r1/code/mbs308_qualify.py` | `0ac40ba9…` | `52120a24…39d3` |
| `…/code/mbs308_driver.py` | `80c88355…` | `117624e9…beab1` |

All equal the addendum's values; full ids are in the addendum §1–§2. **Still open:**
* The checkout is **shallow** (`git rev-parse --is-shallow-repository` = true).
* The introducing commit `7eb057bb` and the ancestry facts must be confirmed on a **full-history clone** by the
  reviewer.
* The reviewer must also confirm that no later commit on the candidate line changes the five blobs.

## 4. Compiler non-holder status

The addendum's compiler (the 2026-10-14/15 Cloud coordinator) is **self-declared** non-holder and disclosed printing the
one-line subject of `21e99cf0`.

**Recommended remedy (procedural, removes the dependence):**
* The formal route reviewer, who must be an eligible non-holder (S13 with E1 D3), **re-derives** the whole reference
  list independently on a full-history clone, from the accepted case set and the candidate's `MBR1_RECORD_PINS`, by git
  object reads only.
* The reviewer then compares it with the addendum.
* Agreement makes the list the reviewer's own. A difference stops before OD-3.

## 5. Source and interpreter bindings

* **Binding digest:** `source_sha256` of each pinned definition (interpreter-independent), not `ast_sha256`, whose dump
  format varies by CPython version (addendum §3 item 5).
* **Successor code path:** the reviewed Linux successor build at a named commit. Its evaluation-path files are bound by
  sha256 in the accepted amendment. S11 byte identity holds for the science modules (governance A1 S11).
* **Interpreter (D-INTERPRETER):** named before any run, with:
  * version;
  * source tarball sha256;
  * compiler and version;
  * configure flags;
  * resulting executable sha256 and libpython sha256.

  CPython 3.14.5 is the macOS campaign's version (brief R2 §9). It is absent on the session hosts (inventories r2, r2b,
  r3). An equal version number does not make the platform equal (route A1 §1).
* **Pins at the pin point (L-PIN):**
  * interpreter path and sha256;
  * every mapped shared object, including `libm.so.6`, `libc.so.6` and the loader;
  * package versions;
  * kernel and os-release.

  These are taken after the fixed import list (D-PIN-POINT, A5) is imported.

## 6. Protocol rules carried unchanged (amendment r5 §5 items 5–9)

* One attempt per owner host decision.
* Every attempt recorded.
* No repeat of a failed or incomplete attempt (D-LDET-REPEAT open; recommended: keep no repeat).
* No host shopping.
* E8: no record or value next to a cell-308 quantity.
* Runtimes excluded from caps evidence.
* A match shows reproduction of non-target records only. It does not restore the decisive argument (D-RC2-SCOPE).

## 7. Review materials the formal route reviewer needs

* this packet;
* the reference addendum;
* amendment r5 §5;
* route A1 §1 and §3;
* the candidate files at `142d97a9` (for the function sources only, by blob id);
* a full-history clone;
* the eligibility and exposure rules of `S12_RISK_REVIEW_BRIEF_DRAFT_20261016.md` §2.

The reviewer opens no qualification record's content beyond what the accepted comparison needs, and runs nothing.
