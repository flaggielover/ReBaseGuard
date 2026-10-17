# Erratum E1 to the L-DET specification packet — open questions resolved, FR1 corrections (Cell-308 Cloud route r1)

**Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE · NOT EXECUTED.** This erratum corrects
`LDET_SPECIFICATION_PACKET_20261016.md` (sha256 `f0f367a9…80e4`) and adds notes to the reference addendum
`PROPOSED_LDET_REFERENCE_ADDENDUM_R1_20261015.md` (sha256 `4efcd152…5277`). Both are preserved unchanged. Its source is
the formal route review FR1 (`reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR1.md`, sha256 `af150ef4…b6df`; LDET_SPEC:
ACCEPTED_WITH_CONDITIONS; findings G4, G6, G21–G24, G29–G31).

It runs no case and opens no record. `new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The three open questions of packet §1, resolved (proposals)

| question | resolution (PROPOSED) | basis |
|---|---|---|
| Do (a) and (b) together read "exact equality of every certified leaf, timing stripped" (route A1 §3)? | **Yes, and only together.** MATCH requires (a) **and** (b) on every compared record. Neither may ever be used alone. (b) alone cannot tell a Decimal leaf from a string holding the same text. (a) alone cannot tell an `fs` string from a number of equal value. The conjunction closes both holes | FR1 F4, G21 |
| Does `_public` apply on both sides? | **Yes.** Every pinned view function is applied identically to the reference bytes and the successor bytes. An asymmetric view would compare different objects, and "exact equality" would be undefined | symmetry of the comparison; FR1 endorses the view list (F4) |
| The leaf-count floor | **Structural, not a reference count:** the compared certified-leaf count must be **> 0 for every job and every case**, as the candidate's non-vacuity check does. The counts are recorded at the L-DET attempt itself. No agent parses the reference records before OD-3, so the open eligibility question of FR1 G23 does not arise | FR1 G23 (its second option) |

## 2. Corrected comparison rule (replaces packet §1 rows "(a)", "(b)", "control"; FR1 G21, G22, G31)

| part | definition |
|---|---|
| (a) exact rational | Each leaf of the view converts exactly: <ul><li>`int` stays as it is;</li><li>`Decimal` becomes `Fraction(Decimal)`;</li><li>a string becomes a Fraction **only if** it matches `^-?(0\|[1-9][0-9]*)/[1-9][0-9]*$` **and** gcd(numerator, denominator) = 1 (the exact grammar `mbs308_driver.fs` writes for a normalised `Fraction`, driver lines 317–319 at `142d97a9`, as FR1 read it).</li></ul> Every other string is compared as a string. A boolean compares as a boolean, never as an integer. `Fraction(str)` is never applied to an unmatched string. Trees are equal only with equal key sets at every level and equal leaf **types** after conversion |
| (b) canonical bytes | A reviewed canonical writer emits JSON tokens itself:<ul><li>object keys sorted by code point;</li><li>separators `,` and `:`, no whitespace;</li><li>strings as JSON strings (`ensure_ascii=False`);</li><li>`int` as its decimal digits;</li><li>`Decimal` as an **unquoted JSON number token**, in exact plain decimal text with no exponent;</li><li>`true` / `false` / `null`.</li></ul>`json.dumps(default=…)` is not used, because its `default` hook can only return a serialisable object, so a Decimal would be written as a quoted string. The two UTF-8 byte strings must be identical |
| integer digit limit | The comparator process sets `sys.set_int_max_str_digits(0)` before parsing and records the value. This is a process setting of the reviewed comparator, not a host setting. Without it, CPython's default limit (4300 digits) could raise on a large `fs` numerator and turn a valid attempt into INCOMPLETE, which would consume the one attempt. Any other parse error stays INCOMPLETE (fail closed) |
| controls | Two controls, both on a copy of the successor side:<ol><li>the candidate's `_planted` (one middle leaf changed). Both (a) and (b) must report a difference;</li><li>an **exactness control**. One Decimal leaf has a decimal digit appended beyond the precision a double can hold, so `float()` of the leaf is unchanged. Both (a) and (b) must report a difference.</li></ol>If either control fails, the attempt is INCOMPLETE |
| outcome | MATCH only if (a) and (b) are equal for every case, every job and case is non-vacuous (§1), and both controls are detected. Anything else is MISMATCH or INCOMPLETE |

## 3. Relation to MBR1_REPRO and the L-DET commit (FR1 G4)

As amendment r5 erratum E1.3:
* L-DET is an additional pre-gate, bound to a named commit of the reviewed successor build.
* The accepted MBR1_REPRO runs again at the official qualification on the frozen commit. It is not a repeat, and a
  mismatch there is STOP.
* The evaluation-path files are byte-identical between the L-DET commit and the freeze.

Packet §0 gains a step 0, "MBS-7 recorded by the owner (amendment r5 erratum E1.1)", and a step 2a, "the
platform window H1 / H3 / H8 begins at the interpreter build" (erratum E1.4).

## 4. Interpreter and L-PIN (FR1 G6, G24; replaces packet §5 "Pins at the pin point")

**D-INTERPRETER (recommendation kept):** CPython 3.14.5 built from the official source tarball on the named host, with
these recorded:
* the tarball's sha256;
* the compiler and its version;
* the configure flags.

It is built **before any decoy or L-DET run** and never changed after an L-DET outcome. Whether it builds on the named
host's toolchain is a host fact (CANNOT_ASSESS_WITHOUT_HOST).

**L-PIN for a non-dpkg interpreter.** The development reader `_python_packages` uses `dpkg -S`, so it cannot pin a
source-built interpreter. The successor's L-PIN therefore pins:
1. a **build-provenance record**: the tarball sha256, compiler, flags, configure output digest and install prefix;
2. a **sha256 manifest of the installation prefix**: `bin/python3.14`, `lib/libpython3.14*.so*` if shared,
   `lib/python3.14/**` (the pure-Python stdlib, including `fractions.py`, `decimal.py`, `json/`) and
   `lib/python3.14/lib-dynload/*`. It is checked at the pin point;
3. **libpython explicitly:**
   * for a shared build, `libpython3.14.so.1.0` must be a member of the mapped-object set;
   * for a static build, the executable's sha256 covers it;
   * the build record says which;
4. the system shared objects mapped at the pin point (`libc.so.6`, `libm.so.6`, the loader, and any other) by path and
   sha256, with their dpkg package versions where dpkg owns them;
5. the kernel release and os-release.

**Workers and late mappings:**
* The pin is taken, or verified identical, **in every worker process** after its imports.
* At the end of each job, the set of mapped objects is re-read. Any object mapped after the pin point makes the attempt
  INCOMPLETE before the marker, or close-indeterminate after it (RC2 pin rule).
* The L-DET pins are binding for every later computing step (amendment r5 erratum E1.2 item 2).

## 5. Notes on the reference addendum (FR1 G29, G30)

* **G29.** The five reference paths held two earlier generations of records:
  * blobs added at `3a05aef7` (qualification at freeze r1 `a7fe3028`, FAIL) and deleted at `29b68d5e`;
  * blobs added at `d031dad8` (qualification at freeze r2, FAIL) and deleted by freeze r3 `c46434a3`.

  The r3 records are introduced at `7eb057bb`, as FR1 confirmed on a history-complete clone. The addendum's "none of the
  five paths exists at `c46434a3`" is true but incomplete. This is why every read is **by blob id**, never by path at
  a commit.
* **G30.** `source_sha256` means `hashlib.sha256(ast.get_source_segment(source, node).encode("utf-8"))`. FR1
  recomputed all 16 values that way. Decorators are not included, because `get_source_segment` starts at the `def` or
  `class` line.
* **Reference-list re-derivation (packet §4 remedy).** FR1, an eligible non-holder by its disclosure, re-derived the
  list independently from `MBR1_RECORD_PINS` and the history: the five blob ids, the introducing commit, the ancestry,
  and no later change. It agrees with the addendum. FR1 disclosed name-level contact (commit subjects of pre-grant
  qualification commits; ref-name counts) and no target-run material.

## 6. Status after this erratum

FR1's LDET_SPEC condition 10 is addressed in text, and condition 5 by erratum E1.3. Both still need the fresh bounded
check of the corrected texts, and then the owner's adoption. OD-3 is not put to the owner until then.
