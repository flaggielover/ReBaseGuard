# C11R pre-freeze review, round 3 (independent)

- Reviewed commit: eaca931ef8ad9e6a611395fc50dcc2beb9808bf7 (branch p5y-k5-tail-c11r-n9-statement-alignment, worktree /Users/suzhe/ReBaseGuard-k5c11r)
- Date: 2026-09-23
- Reviewer: new independent reviewer (no prior involvement in C11R rounds 1-2)
- Precondition: HEAD == eaca931ef8ad9e6a611395fc50dcc2beb9808bf7 and `git status --porcelain` empty — VERIFIED at start of review.
- Numerics policy for this review: no evaluation on any open-cell drift block; any numerics only on NT = [5/2, 5/2 + 108337/1250000] or e = 5/2. No original cell-306 magnitude is written here; values are referred to by artifact and field name only.

(Written incrementally. Status: COMPLETE — all 30 required attacks reached.)

**Summary.** The round-3 repair fixes B-1 (seal accepts genuine artifacts, verified end to end), B-2 in substance (no pre-comparison module reads protected content at runtime; errata and artifacts are value-clean), B-3 (propositions are reconstructed from certificate facts, not constant names), B-4 (guards are production functions in the verdict path) and B-5 (qualifier rebuilt on the frozen policy, NT only). The cost basis is committed and mechanically derived; the cap was not raised; nothing target-informed moved the configuration; the D_lo record is correct and independently confirmed on NT. ONE load-bearing defect remains: the frozen toolchain, policy and statement table are not bound on the Phase 13-15 path (R3-1, demonstrated), so the certificate module's own integrity argument for consistently-forged records does not hold as implemented. Several non-blocking defects (N-1..N-10) should be fixed or restated in the same repair.

## Method

- Read in full: every module in `code/` (c11r_common, schema, certificate, equiv, compare, runs, boxdata, idrift, policy, cost, qualify, gate, firewall, status, b0, table, errata, mutations, validate, regen), every JSON artifact except the quarantine's values, both earlier reviews, and the errata.
- All writes happened in two scratch clones made by `git clone --no-local` and checked out at eaca931e: `work/clone` (probes that commit) and `work/clone2` (runtime traces). Probe scripts are in the scratch directory next to this file: `seal_probe.py`, `forge_probe.py`, `fw_probe.py`, `trace.py` + `analyse_trace.py`, `leak_scan.py`, `nt_rehearsal.py`.
- **Runtime ground truth for the firewall.** `trace.py` runs a module under a Python audit hook (`sys.addaudithook`). It logs every `open` (path and mode), every `subprocess.Popen` argv and every directory listing. Traced in clone2: b0, errata, equiv, gate, firewall, mutations, policy, validate, status (full and `--verify-only`) and `qualify --self-test`. `status --verify-only` was also traced in the primary checkout.
- **Not run:** c11r_runs.py, c11r_compare.main, c11r_qualify.main, c11r_table.py (either mode), c11r_regen.py and c11r_cost.py. No authorization, and no `evidence/runs|qualification|comparison` directory, was created anywhere, including the clones. The seal probe committed a synthetic runs artifact under `evidence/r3probe_*/` in scratch clone 1 only, with `c11r_compare.RUNS_REL` redirected to it.
- **Numerics.** The only numerics were on NT = [5/2, 5/2 + 108337/1250000] or at e = 5/2. The one exception is exact-rational bookkeeping on the cell-306 block endpoints themselves (denominators and containment); no kernel was evaluated there. Synthetic certificates carry only the label of the cell-306 block, exactly as the campaign's own self-tests do.
- **Quarantine.** It was read only by `leak_scan.py`. That script prints counts and digit-masked contexts and writes nothing. No value from it appears in this review or in any file I wrote.

## Attacks

### 1. B-1: seal/schema compatibility — PASS

**Checked.**
- `c11r_schema.seal_problems` now checks the seal on typed fields: `seal.contains_original_magnitudes is False` and `seal.sealed_before_comparison is True`.
- It also runs `forbidden_payload`, an exact-key walk over the parsed JSON.
- `validate_runs` calls it. `emit_runs` (the producer) and `c11r_compare.verify_seal` (the comparator) both go through `validate_runs`, so the two sides share one definition.
- No substring scan of text remains (grep).

**How: `seal_probe.py` part A, run in scratch clone 1 end to end.** No such end-to-end run existed in round 2. The steps:
1. Build the certificates with `c11r_compare.synthetic_certs` and assemble the artifact with `c11r_runs.assemble` (the only emission path).
2. Write it with `C.write_evidence(..., producer=c11r_runs.py)`, as `c11r_runs.main` does. The path was `evidence/r3probe_A/C11R_RUNS.json`, not `evidence/runs/`.
3. Commit it, point `c11r_compare.RUNS_REL` at it, and call the real `verify_seal()`, followed by `run_comparison` with synthetic magnitudes.

**Result.**
- The file text contains the key `"contains_original_magnitudes"`.
- `validate_runs(loaded file) == []`.
- `verify_seal()` problems `== []`.
- The comparison ran: 4 targets classified, D1/D2 INSUFFICIENT, verdict AGREEMENT_INSUFFICIENT.
- The comparator's own self-test also passes the typed controls: a true seal is rejected; the word "magnitudes" in prose is accepted; a real `original_value` key is rejected.

B-1 is repaired, and the round-2 remedy of an executed clean control through the real content path now holds.

### 2. B-2: firewall truth in production — PASS for the frozen tree; DEFECT (non-blocking) in what the analyser is claimed to prove

**(a) Ground truth at runtime: clean.** Each traced module read only its allowlisted inputs, Python source, and the R5 map via `git show` (B0).

| Module traced | Allowlisted artifacts opened | Other reads |
|---|---|---|
| status `--verify-only` | the 13 allowlisted artifacts | none |
| status (full) | the 13 allowlisted artifacts | none |
| B0 | none | the R5 map via `git show` (the declared external input); count-only `git grep` |
| errata | none | none |
| equiv | the statement table | none |
| gate | table, policy | none |
| firewall | 9 | none |
| mutations | 5 | none |
| policy | table, validation, cost | none |
| validate | none | Python source only |
| qualify `--self-test` | policy, cost | none |

- Across all of these, no protected file, off-allowlist namespace file or external data file was opened, and the only writes were each producer's own artifact. The status rows are the `--verify-only` run in the primary checkout plus the full run in clone2. The validate row is its full run (705 s in clone2).
- Protected files were touched only through `git hash-object` / `git rev-parse` (object ids): the quarantine, REGISTRY_C2, and both reviews.
- `git grep` was used only with `-q`, `-l` or `-c`.

**(b) Read resolution is not vacuous for data.**
- I re-solved the analyser on the real modules alone, without the planted controls sharing `_MATCH_CACHE`.
- Every data read resolves to a named allowlisted artifact, the R5 map, the runs path (compare only), or a protected file (table/compare only).
- The patterns that resolve to no file fall into three groups:
  - argv tokens (`-B`, `--leak-check`);
  - `.../c11_n9_independent_certifier/code/c11r_*.py`: the `_sha()` fallback in mutations, which is code-shaped and hash-only;
  - `code/--leak-check`.
- No data-artifact path is among them.
- The artifact's list mixes in control-world tokens (`-c`, `200`, `HEAD`, `tau`), because the cache is global. This is cosmetic.

**(c) The allowed readers' loader functions are unreachable from pre-comparison modules.**
- The loaders flagged by the firewall are `c11r_compare.{verify_seal, load_original_magnitudes, main}` and `c11r_table.{leak_check, main}`.
- They are called only inside their own modules (grep).
- c11r_mutations imports c11r_compare but calls only pure functions: `run_comparison`, `synthetic_certs`, `verify_seal_bytes`, `self_test` and `FACTOR`. Its trace confirms it.
- Regen launches `c11r_table.py --leak-check` as a separate process. That process emits counts only.

**(d) DEFECT: new leak paths the analyser misses (`fw_probe.py`).**
- I planted 20 new sources, each of which reads the quarantine at runtime, through the production `control_world` + `analyse`.
- **14 were missed** (reported clean):
  - `pathlib.Path(C.NS, "evidence", "quarantine", name)`: the multi-argument `Path`; `fold_call` folds only `args[0]`.
  - `"%s/evidence/quarantine/..." % C.NS`.
  - `subprocess.run([sys.executable, "-c", "print(open('evidence/quarantine/...').read())"])` and the same with a literal `python3`.
  - A loader called through a dict of functions.
  - An aliased loader (`L = C.load; L(q)`).
  - An aliased `open` (`o = open; o(q)`).
  - `linecache.getlines(q)`.
  - `fileinput.input(q)`.
  - `urllib.request.urlopen("file://...")`.
  - `map(C.load, [q])`.
  - `functools.partial(C.load, q)()`.
  - A method with a path parameter called on an instance (`R().get(q)`). Deferred parameter sinks are judged only at call sites the analyser recognises.
  - A shell pipeline `git show HEAD:$(...)`.
- 6 were caught: `os.open`, lambda, `str.replace`, `*args`, `listdir` then load, and `blob_at`.
- None of the missed constructs occurs in any production module (grep, plus the traces in (a)). So the committed FIREWALL_CLASS = PASS is true of this tree.
- But three claims describe the analyser as a proof when it is a heuristic whose controls are the known attacks:
  - G16: "every content read ... resolves, by load-path dataflow";
  - M03: "reading original magnitudes ... by ANY path";
  - E14's repair text.
- This is the round-2 pattern again, "controls written to match the known attacks", although the tree itself is clean.
- **Non-blocking** because the frozen tree is clean at runtime. Two ways to fix it:
  - restate G16 as a heuristic scan backed by a runtime trace; or
  - make the firewall mechanical: an audit hook installed by `c11r_common` that refuses `open`/`subprocess` access to `is_protected` paths outside the two sanctioned modules.

### 3. Directory-glob leakage (status, B0, any traversal) — PASS

- **status** walks `C.PRE_RESULT_ARTIFACTS` via `load_allowlisted`. Its inventory is `git ls-files` (names only). The quarantine, both reviews, the reviewed machinery and history are compared by object id (`git hash-object` / `git rev-parse`), not content (trace confirmed).
- **B0** finds guard settings with names-only `git grep -l/-q` and literal exclusions of every `is_protected` JSON, and requires `scanned == total - protected` (3343 = 3353 - 10). The C11 verdict comes from count-only `git grep -c`.
- **Other traversals.** The only other traversals in the tree are `C.HERE.glob("c11r_*.py")` (code) in firewall, qualify, mutations and table, `code_closure`, and `(C.NS/"code").glob("*.py")` in B0. The traces show directory listings only of the three code directories and of the Python stdlib.
- NOTE: B0_10 excludes protected files from its guard scan. An ALLOW setting inside an adjudication or quarantine JSON would therefore be invisible to it; see item 27 for my own whole-repo scan.

### 4. Review-text leakage — PASS

- No production module opens a `REVIEW_*` or `ADJUDICATION_*` file. They are classified PROTECTED by `C.is_protected` (prefix and `review` segment).
- status checks the two preserved reviews only by `git hash-object` against `git rev-parse <commit>:<path>` (trace).
- `c11r_policy.py` no longer reads the first review. Its only inputs are the table, validation and cost (source, provenance and trace agree).
- `read_code` forces a `.py` suffix, so it cannot read review prose.

### 5. Errata leakage and the value-based leak check — PASS (errata clean); NOTE on the method

**What I scanned (`leak_scan.py`).**
- Every file ever tracked in the namespace at eaca931e, except the quarantine.
- The external closure modules and the R5 map.
- All seven commit messages 440bcd91..eaca931e, including eaca931e's own message, which the committed leak check could not cover (it ran before that commit).

**Forms searched, per original value.** This is wider than the production leak check:
- the exact rational;
- decimal renderings rounded half-even, rounded half-up and truncated, at 1–10 places, with and without a leading zero;
- scientific notation at 1–8 digits;
- the float repr;
- long numerators.

**Result.**
- No match at ≥ 4 decimals, as an exact rational, in scientific notation or as a float repr, in any production module, pre-result artifact or commit message. This includes `evidence/errata/C11R_ERRATA.json` and `code/c11r_errata.py`, and 2–3-decimal forms as well.
- 1-decimal forms collide with ubiquitous short literals. I inspected them with every digit masked and judged them coincidental; they are not reported further.
- The only true hits are in `review/REVIEW_C11R_PREFREEZE.md` (4-decimal and exact-rational forms). That is expected: it is protected and immutable, and it also serves as a positive control for my scanner.
- Errata E2 describes the revision-1 exposure by artifact and field name (`constants.<k>.value_float`), without digits.
- NOTE: E10 quotes one revision-1 target-block box margin (to 5 decimals). That is historical target-computation output, not an original magnitude, and it cannot steer any frozen choice.
- **Verdict:** `LEAK_CLASS = PASS` is substantively true.

**NOTE on the method (`c11r_table.leak_patterns`, `LEAK_METHOD`).**
- The patterns are fixed in decimal places (4–8), not significant figures.
- A value of magnitude ≥ 10 rounded to 2–3 decimals carries ≥ 4 significant figures and is not generated. Neither are 1–3-decimal forms or scientific notation.
- Commit messages are disclosure-only, and ratios cannot be enumerated.
- My wider scan closes this for the current tree. The production check should switch to significant-figure forms (and 1–3 decimals for |v| ≥ 10) so that a future regeneration is covered too.

### 6. The disclosed ad-hoc quarantine reads (E11, E21) — PASS (as a record); NOTE

**What the record says.**
- E11 (round 2): a hand-run script loaded the quarantine to check the statement table for leaks.
- E21 (round 3): a shell loop json-loaded every tracked JSON under `evidence/` and `config/`, the quarantine included, printing only provenance paths.
- Both are recorded as governance deviations, found or disclosed by the author, and the E11 entry answers round-2 judgement H.
- Being ad hoc, neither can be verified mechanically. E20 (a rounded original typed from memory into a draft) shows the channel is real and is candidly recorded.

**Could either read have affected anything frozen? Checked mechanically: no.**
- **The policy's inputs** are the table, validation and cost, confirmed by provenance and by the trace.
- **Unchanged since revision 2** (diffed against affdf8a3): the candidate set {4,5,6}×{32,64,128}, the cap of 10800 s / 8192 MB, the grid 1/1000, `b_max` = 4, `beta_max` = 1, `mu` = 2^-60, and lambda1.
- **The configuration does not depend on the one new author choice (SF = 3/2).** My independent re-derivation from the committed cost artifact gives D4/P128 for every SF in [1, 37/20].
- **D5/P64 was already out.** At SF = 1 its estimate is 1.017 × the cap, so it was excluded by the corrected measurement, not by SF.
- **No channel toward agreement.** Candidates are chosen by the frozen optimiser at execution. The move D5/P64 → D4/P128 goes to a coarser depth, so it can only loosen bounds, never move them toward agreement.

### 7. B-3: certificate → proposition reconstruction — PASS on name-independence; DEFECT (BLOCKER R3-1) on the adequacy of the stated binding argument

**Name-independence: PASS.**
- **How the constants are found.** `c11r_certificate.reconstruct` derives which constants a certificate proves from `DEDUCTIONS[(certifier module, function, reported kernel)]`. It never uses the target's constant name.
  - A K_e supersolution yields only Abar.
  - A Khat_e supersolution yields tau and C_T.
  - The sub-solution yields only D_lo.
  - The derivative route is `implemented: False`.
- **How the proposition is built.** Kernel, convention, direction, drift domain, premises, family and candidate function come from the certificate. The numerical bound is recomputed from the certified weight: `w(0,0)`, or the maximum of `poly_eval_iv` over `X.cover(depth)` for C_T.
- **What `evaluate_target` refuses.** It refuses:
  - a constant that is not among the cited certificate's yields;
  - any value that differs from the recomputed bound.
- **So a matching constant name cannot produce EQUIVALENT.** The following are all INVALID and push the run to EXECUTION_INVALID:
  - the round-2 counterexamples (M13, M19–M21, ADV01–ADV05);
  - my consistent relabel of the Khat_e run as K_e cited for Abar (`forge_probe.py` F9'), which turns tau and C_T INVALID.
- **What is still templated.** `quantity`, `proposition` and `state_set` are looked up from `c11r_schema` by the derived constant name. `STATE_SET_R` is a constant on both sides, so its equality is by construction. The fact behind it is the cover check (`cover.function == c11_certifier.cover` at the certified depth) plus `cover ⊇ R` (item 12). This is acceptable: the deduction table is the frozen semantic map and lives in the gate-bound toolchain.
- **NOTE.** The "reported kernel" is a pure function of the `atom_removed` argument: `supersolution_margin_iv` returns `"Khat_e" if atom_removed else "K_e"`, and `subsolution_margin_iv` returns the constant `"Khat_e"`. So the kernel-versus-argument check is record consistency, not independent evidence. The docstring says as much.

**The stated limit.** A consistently forged record (different weight, recomputed digest, matching value) is detectable only by re-execution. The docstring says the record's integrity "rests on the seal ... by a producer whose hash is bound at the seal, and on the authorization binding the producer's hash". **That argument is inadequate as implemented.**

*What is actually bound.*
1. **`verify_seal` binds only `c11r_runs.py`, and only to the seal commit.** It checks that `provenance.producer_sha256` equals `c11r_runs.py` *at the seal commit*. It never compares against the frozen value, `N9R_GATE_C11R.json` `post_seal_toolchain_sha256["c11r_runs.py"]`.
2. **The expected certifier hashes come from the same tree as the record.** They are `CV.certifier_hashes(seal_commit)`, i.e. `c11r_idrift.py` and `c11r_boxdata.py` *as committed at the seal*. The certificate's `certifier.module_sha256` is written from the same tree at run time, so the check can only prove self-consistency. It cannot prove that the frozen, reviewed certifier ran.
3. **The top-level bindings are never checked.** Nothing compares `runs.policy_sha256`, `runs.statements_sha256` or `runs.provenance.code_closure` with the frozen policy, table or gate (`forge_probe.py` F11: an artifact bound to another policy and table compares normally).
4. **The authorization binds only `c11r_runs.py`.** `c11r_runs.check_authorization` binds guard, cell, policy, table and `c11r_runs.py`'s own hash, not the certifier modules or the rest of its closure. `c11r_runs.main` never checks the tree against the gate's toolchain.
5. **Execution never consults the qualification.** `c11r_runs.main` does not read `evidence/qualification/` at all, although it is in `ALLOWED_NS_INPUTS`. So the Phase-12 checks do not reach Phase 14:
   - Q3 (toolchain matches the gate);
   - Q4 (idrift is the reviewed version);
   - Q16 (same host as the cost measurement).
6. **Every "binding" on the execution and comparison path compares a SELF-DECLARED `sha256` field and never recomputes the content hash.**
   - This applies to `check_authorization`'s `policy["sha256"]` and `stmt["sha256"]`, and to the gate's `policy_sha256` and `statements_sha256`. `C.load` does not verify the body.
   - Demonstrated in memory, with no authorization file written: I took the frozen policy, changed `configuration.chosen` to depth 6 / 128 panels and `cap_seconds` to 10^6, and left its `sha256` field alone. Its body no longer hashes to that field, yet `c11r_runs.check_authorization(auth_bound_to_frozen_policy, edited_policy, ...)` returns `[]`.
   - At comparison, G19 checks the certificates against whatever policy file is on disk.
   - Only `c11r_status` (body-hash CORRUPT) and the qualifier (Q1/Q2) would notice, and neither is on the Phase 13→15 path.

*Demonstration (`seal_probe.py` part B, scratch clone 1).*
1. Commit an edit to `code/c11r_boxdata.py`. It is a one-line comment, standing for any post-freeze edit. `c11r_runs.py` is untouched, so any authorization bound to its hash stays valid.
2. Build the runs artifact through `assemble` + `write_evidence`, and commit it (the seal).
3. Real `verify_seal()`: `problems == []`.
4. `run_comparison` with `certifier_hashes(seal_commit)`: all four implementable targets classified normally, no guard failure. The certifier hash the comparator expected (`3da533c8…`) differs from the one the gate froze (`6bd427f9…`).
5. Then revert the edit in a later commit. The tree now matches the gate again, so `c11r_status`'s toolchain check and the qualifier's Q3 both see nothing. The sealed artifact still compares normally.

*Consequence.* A runs artifact produced by a certifier other than the frozen, reviewed one is sealed, compared and classified as if it were a certificate of the frozen certifier. No mechanical check on the Phase 13→15 path notices it. This is:
- the "consistent forgery" the limit says is covered by producer binding;
- the C7/C10 defect classes: "frozen values bound only in prose/elsewhere" and "guard in the wrong module". The gate records the binding, but only status and the qualifier read it, and neither runs at Phase 14 or 15.

*Why it blocks.* It would let a target run be mis-stated and mis-classified. The fix is small and must be made before the freeze, because it is a change to the comparator:
- recompute the content hash of the policy, the table and the gate wherever they are "bound", in `check_authorization`, `runs.main` and the comparator, instead of trusting their `sha256` fields;
- take `expected_certifier_sha` and the expected runs-producer hash from the gate committed at the seal (or require equality with it);
- check `runs.policy_sha256`, `runs.statements_sha256` and `runs.provenance.code_closure` against the frozen policy, table and gate;
- have `c11r_runs.main` refuse unless the working tree's toolchain equals the gate's binding (or have the authorization bind the gate's hash);
- add an executed control in which a seal commit with an edited certifier is refused.

### 8. Forged-certificate controls — PASS for the listed controls; NOTE on gaps

**The campaign's own controls.**
- ADV01–ADV13 (16 rows) all run through the production `run_comparison`.
- I re-ran the suite in clone2: `MUTATION_CLASS = PASS`, all 16 caught, each with an unrelated-mutation control that stays unflagged.

**My own forgeries (`forge_probe.py`, synthetic values).**
- **Caught:** F9', the consistent Khat_e → K_e relabel cited for Abar. The co-cited tau and C_T become INVALID.
- **Not caught, as expected:** F6, a consistent re-digested widening of F_K's drift block to [0, 100]. It gives STRONGER. This is the stated re-execution limit.
- **Not caught, gaps:**
  - **F11:** `policy_sha256` and `statements_sha256` pointing at another policy and table. This belongs to R3-1.
  - **F11b:** the top-level `drift_block` naming cell 307. Harmless, because propositions come from the certificates, but unchecked.
  - **F1:** `certifier_result.boxes` set to 1, although the cover has 97 boxes. A free cross-check against `len(X.cover(depth))` is not made.
  - **F18:** certificate dict key and `certificate_id` disagree.
  - **F21:** a certified implementable target demoted to `NOT_CERTIFIED`. It silently becomes INSUFFICIENT; nothing checks that a NOT_CERTIFIED target's certificate fails to reconstruct.
- F1, F18 and F21 are MINOR, because the artifact is produced once by the runner and sealed. F11 is part of R3-1.

### 9. Numerical agreement vs statement equivalence — PASS

- **Order.** `run_comparison` decides the statement first (`EQ.compare(original, reconstructed)`) and classifies the number only when the statement is EQUIVALENT or STRONGER. Otherwise the target is INVALID and "the number is not compared".
- **Separate results.** The two are recorded separately (`statement` and `numeric`). The separation control (A_K 1111/100 → 25, same proposition) yields EQUIVALENT both times, with the numeric class moving AGREES → INSUFFICIENT. It passes in the committed artifact, and in my clone2 re-run.
- **The exact-equality rule.** `v == o → INVALID ("copied")` can never misfire on a legitimate result. I checked, printing booleans only, that no original lies on the 1/1000 selector grid. Every independent value for Abar, tau, C_T and D_lo is a grid value.

### 10. K_e / Khat_e distinction — PASS

**Where the kernel comes from.**

| Constant | Original kernel (statement table) | Independent route | Deduction key |
|---|---|---|---|
| Abar | K_e (`full=True`) | F_K: `supersolution_margin_iv`, `atom_removed=False` | K_e |
| tau, C_T | Khat_e | F_H: same certifier, `atom_removed=True` | Khat_e |
| D_lo | Khat_e | F_D: sub-solution, which drops the atom union | Khat_e |

- The table cross-checks its semantics against `c11r_schema.KERNEL/DIRECTION` (a `need()` hard stop).
- The swaps are all refused: M13, M19, M20, M21, ADV03, ADV04 and my F9'.

**NOTE (consequence of the configuration, not a defect of the distinction).**
- At depth 3 the origin box has no removable atom window: my NT rehearsal at D3/P16 skipped 0 panels, and F_H's selection equals F_K's exactly.
- At the frozen D4/P128 the policy's own `atom_removal_fraction_origin_box` is 0.2017, against 0.4276 at D5/P64.
- So the Khat_e bound removes only part of the atom mass near the origin at the frozen configuration. This is sound (an over-count only raises an upper bound), but it may leave tau and C_T close to the K_e bound. See item 21.

### 11. Upper/lower direction, including the asymmetric factor-2 rule for D_lo — PASS; MINOR carried

- **`classify_numeric` matches the frozen table exactly.**
  - UPPER: STRONGER if v ≤ o; AGREES if o < v ≤ 2o; otherwise INSUFFICIENT.
  - LOWER (D_lo, the only one): STRONGER if v ≥ o; AGREES if o/2 ≤ v < o; otherwise INSUFFICIENT.
- `gate.comparison_rule` is a verbatim copy of `table.comparison_semantics_frozen_before_results`.
- **DISAGREES** is correct in both senses: an independent UPPER bound below an original LOWER bound, or an independent LOWER bound above an original UPPER bound.
- **ADV05a/ADV05b** (a lower target citing an upper certificate; a deduction flipped to UPPER) are INVALID.
- **MINOR (carried from round 2).** `FACTOR = 2` is hard-coded in the comparator and is never checked against the table at run time. M10's check (`rule_changed`) lives only in the mutation suite (item 17). Protection rests on the comparator's gate hash, which the comparator itself does not enforce (R3-1).

### 12. State / reachable set — PASS

- **The cover contains R.** `c11_certifier.cover(depth)` keeps every dyadic box that meets R (`box_meets_R`), so cover ⊇ R by construction. Sampled check: a 201×201 lattice of R shows 0 uncovered points at depths 4 and 5.
- **Consequences for the certificates.**
  - A certificate must name `c11_certifier.cover` at its own certified depth (ADV07 is refused otherwise).
  - C_T's value is recomputed as the maximum over the cover, which is ≥ the supremum over R, so it is a valid upper bound.
- **Not reopened:** the accepted round-1 finding that the original's X equals R.
- **NOTE:** the `state_set` string is a shared constant, so its equality is by construction (item 7).

### 13. Drift interval (exact rationals; cell 306 not 307; no substitution) — PASS

- **The block.** The table's `drift_domain` is [680769/400000, 17885921/10000000]. I compared it with REGISTRY_C2's cell-306 block using exact Fractions, printing drift fields only: equal. Width 108337/1250000, 9 sub-rows. Cell 307 is [17885921/10000000, 1882413/1000000].
- **Where it appears.** All six `original_statements` and the gate's `target.drift_domain` use it.
- **Only `c11r_runs.main` builds a kernel block from it** (`grep Blk(`). Every other `Blk` in the tree is NT or the scalar e = 5/2.
- **No substitution passes.**
  - `reconstruct` refuses a single point (scalar, midpoint, endpoint).
  - A strict sub-interval is SUBSET → WEAKER → INVALID.
  - Cell 307 is INCOMPARABLE → INVALID (M16–M18, M22, M25, ADV06).
  - A superset is STRONGER, which is logically sound. A forged superset is the re-execution limit (F6).
- NT = [5/2, 5/2 + 108337/1250000] lies strictly above the m=5 tail span's upper end, 2092283/1000000.

### 14. Conditional / unconditional semantics — PASS

- **The routes.**
  - The sub-solution route declares `premises: ()`. `h_min > 0` and `u ≥ 0` are certified in the same pass and are required by `holds`.
  - The independent D_lo is therefore unconditional, so FEWER premises → STRONGER against the original's `[C_T, tau]`.
  - The derivative route would declare `C_T_independent`/`tau_independent`, which normalise to the original's premise set (SAME).
- **Refusals.**
  - A conditional certificate presented without its premises is refused (ADV10, ADV13).
  - An ORIGINAL constant as a premise is an independence violation.
  - `reconstruct` also refuses premises a route does not consume.
- The record carries `unconditional: not premises`. Not reopened: "stronger by fewer premises", which was accepted.

### 15. B-4: production guards — PASS

- **Where they live.** `evaluate_target` (value trace), `screen_order` (G10), `dispositions` (G8) and `configuration_adherence` (G19) are all in `c11r_certificate`, combined by `evaluate_run`.
- **Who calls them.**
  - `c11r_runs.assemble` runs `evaluate_run` and seals its result as `self_check`.
  - `c11r_compare.run_comparison` re-runs it and does not trust `self_check`.
- **Effect on the verdict.** A G8, G10 or G19 failure gives EXECUTION_INVALID (`guards_ok`). A value-trace failure makes the target INVALID and so also gives EXECUTION_INVALID.
- **The gate names its evaluators** by module and function (G2, G8, G10, G18, run). `c11r_gate.main` refuses if one is missing.
- **MINOR.** G19 is evaluated and enters the verdict, but it is not a gate predicate: the gate has G1–G18, and `EVALUATORS` has no G19. The certificate module's docstring says all four guards are "bound by module and function name in the frozen gate", which is inaccurate for G19.

### 16. G8 and G10 actually evaluated in production — PASS; NOTE

- **Evidence.**
  - M28: G10 through `evaluate_run`, and `run_comparison` returns EXECUTION_INVALID.
  - M38: G8, same path.
  - The comparator self-test includes a G10 violation (EXECUTION_INVALID) and a G19-only case.
  - All three reproduced in clone2.
- **NOTE (carried from round 2).** G10 checks labels the runner writes, `screen_classification` and `sent_to_certification`. The real "screen before certify" ordering is enforced by the control flow of `c11r_runs.main`. A box-feasible member is always pointwise-feasible, so G10 cannot fail on substance, only on a mislabelled record.

### 17. Mutations exercise production guards, not copies — PASS for the run-artifact and certificate mutants; DEFECT (non-blocking) in the module's claim

**Mutants that do go through production functions.** M13–M26, M28, M31, M34–M39 and ADV01–ADV13 call the production functions:
- `c11r_certificate.{reconstruct, evaluate_run, …}`;
- `c11r_compare.run_comparison` / `verify_seal_bytes`;
- `c11r_schema.{validate_runs, seal_problems, forbidden_payload}`;
- `c11r_status.{freshness, contradictions}`;
- `c11r_gate.scan_*`;
- `c11r_runs.check_authorization`;
- `c11r_firewall.run_controls`.

Their run artifacts are built by `c11r_runs.assemble` from `make_certificate`. The trace confirms that no guard logic is duplicated for these.

**The claim is too strong.** The module docstring says "It defines no guard" and "Every detector is a PRODUCTION function". Several mutants are decided by logic defined in the suite:

| Mutant | Detector | Production counterpart |
|---|---|---|
| M01 | `imports_in` | a duplicate of `c11r_qualify.import_scan` |
| M02 | `imports_in` | a duplicate of `c11r_qualify.import_scan` |
| M07 | a regex over `cusum_layer1.py` for K/H | none in production |
| M08 | `rigorous()` | none |
| M10 | `rule_changed` | **none**: no production code compares `c11r_compare.FACTOR` with the frozen rule |
| M12 | `scope_problems` | B0_08 and B0_11 |

M04–M06, M09, M18b, M24 and M29 are mathematical property checks on NT; for those, suite-local comparisons are appropriate.

**Why M10 matters.** M10 ("an agreement threshold changed after the gate froze it") is DETECTED only by a test-local rule. In production, the protection is the gate hash of `c11r_compare.py`, which is not enforced on the comparison path (R3-1). This is the recurring "guard in the test, not the pipeline" class. Non-blocking by itself: fix it with R3-1, or restate the claim.

### 18. B-5: the qualifier uses the frozen policy only — PASS

- **The configuration is re-derived, not copied.** `rederive_configuration` takes the frozen `config/C11R_POLICY.json` and the committed cost artifact. It re-applies the policy's own pure rule (`POL.cost_model`, `POL.choose`) and requires the frozen choice. It also refuses a changed safety factor, a changed cap or a different cost artifact.
- **The self-test's planted controls** (a tampered choice, a raised cap, a different CPU) are all rejected.
- **No stale inputs.** The retired-screen load is gone, as are the old 5400 s cap, the candidate count and the retry text. `main` reads allowlisted artifacts only.
- **Result.** `--self-test`: ALL_PASS. Its trace shows only policy and cost opened, and it writes nothing.
- **Gap (under R3-1).** Qualification is not consumed by execution. Q3, Q4 and Q16 therefore do not bind Phase 14.

### 19. The qualifier touches no open cell — PASS

- `NT = Blk(5/2, 5/2 + 108337/1250000)` and `E_NT = 5/2` are the only drift values used. Q13/Q14 and the self-test's scalar-collapse and atom-decomposition checks run there.
- Q15 re-runs `c11r_equiv.py`, which uses the cell-306 and cell-307 blocks only as labels on statement records; no kernel is evaluated.
- The firewall's open-cell-literal scan finds nothing in any module. My `grep Blk(` agrees.

### 20. Corrected, committed cost basis — PASS on non-target, host, producer hash, raw data and derivation; DEFECT (non-blocking) on "sequential"

**What holds.**
- `evidence/cost/C11R_COST.json` is measured on NT only. Its `block` string is checked by `policy.cost_model`.
- It records the host identity (node, CPU, Python, executable) and 7 boxes × 3 panel counts of raw per-box timings.
- It is bound to `c11r_cost.py` by hash: `producer_sha256` equals the current file, and the body hashes to its own `sha256`.
- I recomputed the derived constants from the raw observations with my own code, independently of `derive()`: identical.
- The policy is bound to this artifact's `sha256`.

**Transfer from NT to the target (algebra only).** At D4/P128 every u-panel endpoint denominator divides 2^12·5^8 for both NT and the cell-306 block, so the arithmetic Phi works on the same bit sizes. This is the round-2 transfer argument, re-derived for the new configuration.

**DEFECT: the "sequential" claim is established by a detector that cannot see the processes it looks for.**
- `c11r_common.classified_processes` keeps only processes whose `comm` basename is in `("python3", "python", "python3.14", …)`.
- On this host, the recorded executable `/Library/Frameworks/Python.framework/.../bin/python3` runs as `.../Python.app/Contents/MacOS/Python`, so its basename is `Python`.
- **Demonstration.** Two live processes executing campaign code, with `closure_proofs` in their argv (my NT rehearsals), were running. `C.classified_processes()["campaign_workers"]` returned `[]`, and the only interpreter it saw at all was an unrelated venv `python`.

**What that makes vacuous.**
- `sequential.campaign_workers_before/after = 0` in the cost artifact;
- the "not measured sequentially" refusal in `policy.cost_model`;
- B0_14;
- regen's pre-flight "no campaign worker running".

These are the "presence check as detection" and "tests that cannot fail" lesson classes.

**Why it is not blocking.**
- Contamination by a concurrent job can only inflate the measured cost.
- The frozen choice is invariant for every safety factor in [1, 37/20] (item 21).
- D5/P64 exceeds the cap even at SF = 1.

So the configuration is unaffected. But E12's repair ("sequential") is not actually established, and B0_14 cannot catch an E1-type stray run. Fix the classifier: compare case-insensitively, include `Python`, or classify by argv.

### 21. Prospective safety factor and the configuration change — PASS; NOTE (E24 and a known-dominated configuration)

**The change is clean.**
- **The cap was not raised.** It is 10800 s / 8192 MB in both revision 2 (affdf8a3) and revision 3.
- **Nothing else moved.** The candidate set, grid, `b_max`, `beta_max`, `mu` and the lambda1 rule are all unchanged. The safety factor 3/2 is declared in the module.
- **The change is forced by the corrected measurement, not by the safety factor.** At SF = 1, D5/P64 already models to 1.017 × the cap. The chosen D4/P128 is identical for every SF in [1, 37/20].
- **Inputs.** Only NT cost and geometry enter. The move is to a coarser depth, which can only loosen bounds.

**NOTE for the user: E24 is OPEN.**
- The policy's own NT loss check finds the frozen D4/P128 dominated. D5/P32 is cheaper (5363 s against 5837 s) and has lower NT worst loss (0.718 against 0.852 for w = 12 − 3/2 m; 0.514 against 0.634 for w = 10 − m).
- D4/P128 also removes only 0.2017 of the origin-box atom window (item 10).
- The author declined to change the rule in a repair round, and recorded it.
- Changing a configuration rule on NT-only evidence before any target run would not be post-result tuning. It is a prospective decision for the user.
- It does not contaminate, mis-state or mis-classify anything. But with ONE execution and no retry, it may spend the run at a configuration the campaign's own evidence ranks worse.
- The NT rehearsal (item 22) quantifies this.

### 22. Corrected D_lo interpretation (V14/V17; E13; `target_scope.F_D_non_target_record`) — PASS; confirmed independently on NT

**The record is read mechanically.**
- `F_D_non_target_record` is read from the validation artifact (policy provenance input `C11R_VALIDATION.json`), not transcribed.
- The family's NT pointwise ceiling is `ceiling_alpha` 0.97476 (V17), against the float reference d(atom) ≈ 0.978–0.982 (`ceiling_to_reference_min` 0.9925).
- V14's `alpha` = 69/200 is certified at the coarse `[3, 16]`.
- The record says these are NT facts, not predictions. E13 retracts the round-2 "near a third … loose" reading. V17's concave search and its skip rule are conservative: skipping a state can only raise the ceiling.

**Independent confirmation (`nt_rehearsal.py`).** I ran the Phase-14 selection logic on NT only: the data pass, `select_upper` for K and H, and `select_lower`, with no certification.

| Configuration | NT alpha (F_D) | F_K = F_H: A | Khat panels skipped | Time |
|---|---|---|---|---|
| D3/P16 | 69/200 (reproduces V14) | — | — | — |
| D4/P128 (frozen) | 151/250 = 0.604 | 2043/500 | 2 | 3932 s |
| D5/P32 | 747/1000 | 2007/500 | 0 | 3443 s |

- **The attribution to configuration loss is right.** alpha climbs toward the family ceiling as the configuration refines, so the family is not intrinsically loose.

**NOTE, NT facts only, for N-8.**
- **Ranking.** D5/P32 beats the frozen D4/P128 on both families' selected bounds, at lower modelled cost. This corroborates E24.
- **Khat_e gives no benefit on NT.** At both configurations the Khat_e selection coincides exactly with the K_e selection (`F_H ≡ F_K`): the few atom panels the box bound can skip do not bind on NT. The Khat_e certificate is still sound, and it is still a tau/C_T statement. But on NT it is no tighter than the K_e bound.
- **The metric that would show this is ignored by the rule.** The policy records `atom_removal_fraction_origin_box` as a continuous proxy, 0.2017 and 0.254 at these configurations. Whether a panel is actually skipped depends on grid alignment with the drift block, and the lambda1 rule ignores both.

This is a design-effectiveness matter for the user's prospective decision. It has no bearing on freeze integrity.

### 23. Provenance / freshness (`c11r_status`) — PASS

**Status in the primary checkout.** I ran `python3 -B code/c11r_status.py --verify-only` there under the audit tracer.
- Output: artifacts 12, not fresh `[]`, contradictions `[]`, class failures `{}`, committed status report FRESH, `STATUS_CLASS = CONSISTENT`.
- **It wrote nothing:**
  - `git status --porcelain --ignored` is byte-identical before and after;
  - the mtime and size of every file in the namespace are unchanged;
  - the trace records no write-mode `open`;
  - HEAD is still eaca931e.

**Independent recomputation of freshness,** with my own AST closure and hashing code, not `c11r_status`. For all 13 allowlisted artifacts:
- the body hashes to its `sha256`;
- the producer hash equals the current file;
- the recorded code closure equals the recomputed closure;
- every recorded input matches the current bytes, or, for protected inputs, the current `git hash-object`.

Result: 0 not fresh.

**Coverage.** Modules without artifacts (runs, compare, certificate, schema, equiv, boxdata, idrift, common) are covered through status's check of the tree against the gate's `post_seal_toolchain_sha256`, which currently matches. That check looks at the working tree only (R3-1).

**Reproducibility.** I re-ran 8 producers in clone2: errata, equiv, gate, firewall, mutations, policy, validate (705 s) and B0.
- **Byte-identical to the committed artifacts:** errata, equivalence, gate and **policy**. So the frozen configuration reproduces.
- **Equal in content, differing only in hashes, `seconds` or provenance input ids:** firewall, policy evidence and validation.
- **Mutations** differ in one field, `M12.detail.files_changed_since_C11`, because HEAD moved from 6ae05833 to eaca931e.
- **B0** differs as expected in a scratch clone: detached HEAD, and the `ls-remote` trap.
- `VALIDATION_CLASS`, `MUTATION_CLASS`, `EQUIV_CLASS` and `FIREWALL_CLASS` reproduce as PASS / PASS / READY / PASS.

### 24. No target science in this branch's history since C11 HEAD 440bcd91 — PASS (no target certification ever); NOTE

**History.**
- Seven commits: 49b17ab4, 38f59993, 6d7cd546, 9801276c, affdf8a3, 6ae05833, eaca931e.
- No runs, qualification, comparison or authorization artifact exists under any ref (`git log --all` for `*C11R_RUNS*`, `*C11R_QUALIFICATION*`, `*C11R_COMPARISON*`, `*C11R_AUTHORIZATION*` and the three evidence directories: 0 each).
- E1's aborted two-minute run wrote nothing.

**NOTE: target-block screening exists in retired history.** Revision 1's `code/c11r_screen.py` and `evidence/screen/C11R_SCREEN.json` (added 49b17ab4, removed 9801276c) are a pointwise necessary-condition screen computed on the cell-306 block. That artifact's `drift_block` is cell 306's. It is disclosed in E1, E2, E9 and E10, and superseded. The round-2 re-publication of those margins in the policy evidence is gone.

**This commit.** eaca931e adds computations only on NT: cost, validation V17, policy NT loss validation, and mutations.

So "no target science" holds in the sense the brief states it: no target certification has ever run.

### 25. No qualification artifact / run — PASS

- There is no `evidence/qualification/` on disk and none in any commit.
- `c11r_qualify.main` was not run by me. `c11r_regen.NEVER` includes it, and `regen.main` asserts that it is absent from `ORDER`.
- Only `--self-test` exists as an executed path. It writes nothing, and the trace confirms it.

### 26. No `evidence/runs/` in the tree or in any commit — PASS

- Absent on disk, and absent in every commit under every ref of the primary repository.
- My synthetic seal probe artifacts exist only in scratch clone 1, under `evidence/r3probe_*`, on a local branch there. Nothing was pushed.

### 27. Guard DENY everywhere — PASS for C11R; NOTE on out-of-scope artifacts

**C11R.**
- `config/N9R_GATE_C11R.json` has `guard: DENY`.
- `config/C11R_AUTHORIZATION.json` does not exist, so `c11r_runs.authorised` refuses (M36 real-tree detail).

**Whole repository at HEAD.** I scanned with `git grep -l -i` (names only, protected files included, all file types) for any `"*guard*": "ALLOW"` and for `"EXECUTION_AUTHORIZED": true`. The guard-key hits:

| File | What it is |
|---|---|
| `c11r_b0.py` | B0's planted control string |
| `c11r_mutations.py` | M36's synthetic authorization dict |
| two C10 markdown reports | prose |
| `p5y_k5_lower_front_order3/.../ADJUDICATION_R1.json` | the historical record key `guard_state_at_run_head: ALLOW` |

None is a live guard setting.

**NOTE.** `EXECUTION_AUTHORIZED: true` stands in two other campaigns' files, both unchanged since C11 HEAD (B0_11) and outside C11R's scope:
- `p5y_k5_cusum_first_real_probe_protocol/protocol/AUTHORIZATION_ACTIVE.json`;
- `p5y_k5_cusum_real_point_executor/authorization/COUNTERSIGNATURE_ACTIVE.json`.

B0_10 would not see them (it matches only the key `guard`), and it excludes protected files. Whoever owns those protocols should confirm they are exhausted.

### 28. N9 scope — PASS

The subset limit is stated everywhere it matters:
- **Gate `SCOPE`:** "if D1 and D2 are not independently certified, N9 remains OPEN whatever the other four constants yield", and "independent same-statement certification of a SUBSET of the six ... is not N9 closure".
- **`forbidden_conclusions`:** includes "that N9 is closed while any of the six constants lacks an independent statement".
- **Policy:** `target_scope.N9` says the same.

**Mechanically.**
- `run_comparison` returns N9_CLOSED only when all six classes are AGREES or STRONGER.
- D1 and D2 are always INSUFFICIENT: "no certified value (status NOT_IMPLEMENTED)".
- So in production the verdict can be at best AGREEMENT_INSUFFICIENT. This is stated per path in the comparator's docstring and in E19.
- M11 (NOT_IMPLEMENTED counted as a pass) is refused.

### 29. D1/D2 still unimplemented — PASS

- **Nothing produces them.** The `DEDUCTIONS` derivative route is `implemented: False`; the supersolution and sub-solution routes do not yield D1 or D2.
- **The runner marks them NOT_IMPLEMENTED.** `c11r_runs.assemble` does so for every constant outside `implementable_under_this_policy` = {Abar, tau, C_T, D_lo}, with the full dependency list.
- **Any claim is refused, on two independent grounds:**
  - `reconstruct` refuses with "route not implemented" or "cannot produce";
  - G8 treats any status other than NOT_IMPLEMENTED for D1 or D2 as a violation.

  Controls: M37, ADV09, ADV10, ADV13.
- **MINOR (carried from round 2).** The policy's `D1_D2_require` list omits "sup_source_derivative bounds", which the table's `additional_machinery_D_requires` includes. It is record-only.

### 30. Historical verdict preservation — PASS; MINOR

- **Both prior reviews are byte-identical to their commits.**
  - `review/REVIEW_C11R_PREFREEZE.md` equals 6d7cd546.
  - `review/REVIEW_C11R_PREFREEZE_R2.md` equals 6ae05833.
  - Checked with `git diff --quiet`; status's object-id check agrees.
- **Nothing outside the namespace changed.** `git diff --name-only 440bcd91 eaca931e` outside it is empty. So C2–C10 and C11 artifacts are untouched, the C11 verdict remains EXECUTION_INVALID (B0_04, count-only grep), and the r5 map is unchanged and authoritative.
- **No r6** (B0_08).
- **Main refs, recorded separately in `evidence/b0/C11R_B0.json`:**
  - `LOCAL_MAIN_REF = c123b9bb…`, which equals `refs/heads/main` now;
  - `REMOTE_MAIN_REF = 1cb45382…`, which equals `refs/remotes/origin/main` now.

  I did not query the network.
- **MINOR.** B0_06 ("r5 is the authoritative coverage map") cannot fail. The map's `revision` field is null, so the check passes only because the constant `R5_PATH` contains "R5". This is the "test that cannot fail" class. The fact itself holds by the other checks.

---

## Load-bearing BLOCKERS

### R3-1 (MAJOR): the frozen toolchain, policy and statement table are not bound on the execution → seal → comparison path

The chain Phase 12 → 13 → 14 → 15 is linked only by the hash of `c11r_runs.py` and by the self-declared `sha256` fields of the policy and the table.

**The four gaps.**
1. **The comparator derives its expectations from the tree it is checking.** `c11r_compare.verify_seal` / `main` take `expected_certifier_sha = CV.certifier_hashes(seal_commit)` and the producer hash from `c11r_runs.py` at the seal commit. The gate's `post_seal_toolchain_sha256` is never consulted. `runs.policy_sha256`, `runs.statements_sha256` and `runs.provenance.code_closure` are never checked against the frozen policy, table or gate.
2. **Execution checks neither the gate nor the qualification.** `c11r_runs.check_authorization` / `main` bind guard, cell, policy `sha256` field, table `sha256` field and `c11r_runs.py`'s own hash. They never check the tree's toolchain against the gate, and never read the qualification.
3. **No binding recomputes a content hash.** A policy edited in place, with its `sha256` field left alone, passes `check_authorization`. Demonstrated with depth 6 / 128 panels and `cap_seconds` 10^6.
4. **Only status (optional) and the qualifier (Phase 12, not consumed) compare the tree with the gate,** and they compare the current working tree, not the seal commit.

**Reproduce (scratch clone only; `seal_probe.py`).**
1. Commit any edit to `code/c11r_boxdata.py`.
2. Build a runs artifact with `c11r_runs.assemble`, write it with `C.write_evidence(producer=c11r_runs.py)`, and commit it under a redirected `RUNS_REL`.
3. Run `c11r_compare.verify_seal()`: problems `[]`.
4. Run `run_comparison(..., certifier_hashes(seal_commit))`: every target is classified normally, and there is no guard failure. The certificate's certifier hash `3da533c8…` differs from the gate's `6bd427f9…`.
5. Revert the edit in a later commit. The tree matches the gate again, and the sealed artifact still compares normally.

**Consequence.** The certificate module states that a consistently forged record is covered by "the seal ... producer whose hash is bound at the seal" and "the authorization binding the producer's hash". That argument does not cover the certifiers, the policy or the table. A target run produced by a non-frozen certifier or configuration would be sealed and classified as if it were frozen.

**Why it must be fixed before the freeze.** The repair changes post-seal toolchain modules (`c11r_compare.py`, `c11r_runs.py`), which cannot be edited after results exist.

**Minimum fix.**
- Recompute content hashes wherever something is bound.
- Take the expected certifier and producer hashes from the gate committed at the seal, and check the runs artifact's policy, table and code closure against it.
- Make `c11r_runs.main` refuse unless the tree's toolchain equals the gate, or bind the gate hash in the authorization.
- Add executed controls for (i) an edited-then-reverted certifier and (ii) an in-place edited policy.

## Non-blocking observations (should be fixed or restated; none on its own would let a target run be contaminated, mis-stated or mis-classified)

- **N-1 (MODERATE; item 2d). The firewall analyser is a heuristic presented as a proof.**
  - 14 of 20 new planted leak paths are missed: multi-argument `Path`, `%`-formatting, `python -c`, higher-order and aliased loaders or `open`, `linecache`, `fileinput`, `urlopen`, methods with path parameters, shell substitution.
  - The frozen tree is clean at runtime.
  - Fix: restate G16, M03 ("ANY path") and E14, or add a runtime audit-hook guard in `c11r_common`.
- **N-2 (MODERATE; item 20). The campaign-worker detector is blind on the recorded host.**
  - `classified_processes` never sees a framework-build Python, whose `comm` basename is `Python`.
  - That makes vacuous: the cost artifact's "sequential" fields, `policy.cost_model`'s sequential refusal, B0_14, and regen's pre-flight.
  - The configuration is unaffected.
- **N-3 (MINOR–MODERATE; item 17). `c11r_mutations`' "defines no guard" is inaccurate.** M01, M02, M07, M08, M10 and M12 are decided by suite-local logic. M10 (a changed factor-2 threshold) has no production detector at all.
- **N-4 (MINOR; item 5). The production leak check generates decimal-place forms (4–8 dp) only.**
  - Missing: significant-figure forms, 1–3 dp for |v| ≥ 10, and scientific notation.
  - My wider scan found nothing, so this matters only for future regenerations.
  - eaca931e's own commit message was not covered by the committed leak check. My scan covers it: clean.
- **N-5 (MINOR; items 8 and 15).** Several small gaps:
  - `certifier_result.boxes` is not cross-checked against `len(X.cover(depth))`;
  - the certificate dict key is not checked against `certificate_id`;
  - a NOT_CERTIFIED implementable target whose certificate reconstructs cleanly is not flagged;
  - the top-level `runs.drift_block` is unchecked;
  - G19 is evaluated but is not a gate predicate, although a docstring says it is gate-bound.
- **N-6 (MINOR; items 11 and 29, carried).**
  - `FACTOR = 2` is hard-coded in the comparator and never checked against the frozen rule at run time.
  - The policy's D1/D2 requirement list omits "sup_source_derivative bounds".
- **N-7 (MINOR; item 30).** B0_06 cannot fail (the map's `revision` is null, and the path constant contains "R5"). B0_10 excludes protected JSON from its guard scan and matches only the key `guard`.
- **N-8 (MODERATE for the user's decision, not a defect of freeze integrity; items 10, 21 and 22).**
  - E24 is OPEN: the declared lambda1 rule picks D4/P128, which the campaign's own NT evidence ranks below the cheaper D5/P32.
  - Execution is one run with no retry.
  - Whether to amend the configuration rule prospectively, on NT evidence only, before the freeze is a legitimate user decision, not post-result tuning.
- **N-9 (MINOR; items 2 and 23). Records and residue.**
  - `code/__pycache__/c11r_screen.cpython-314.pyc` survives for the deleted module. It is ignored by git and harmless.
  - The firewall artifact's list of patterns that resolve to no file mixes in control-world tokens.
- **N-10 (NOTE; item 27).** Two other campaigns' authorization files carry `EXECUTION_AUTHORIZED: true`. They are outside C11R and unchanged since C11 HEAD.

**What is right and should be kept.**
- B-1 repaired and exercised end to end.
- The runtime-clean firewall. No production module reads a protected file: traced for 10 producers, plus `status --verify-only` in the primary checkout.
- The value-clean errata and artifacts.
- Name-independent certificate reconstruction, and the production guards (value trace, G8, G10, G19) in the verdict path.
- A qualifier rebuilt on the frozen policy, on NT only.
- A committed, reproducible and mechanically derived NT cost basis, with the cap unchanged.
- Candid errata E11–E24.
- Byte-reproducible policy, gate, errata and equivalence artifacts.
- The pre-result state intact.

## Blocker list

- R3-1 (MAJOR): the frozen toolchain, policy and statement table are not bound on the execution → seal → comparison path.
  - The comparator's expected certifier and producer hashes are taken from the seal commit's own tree, not from the gate's `post_seal_toolchain_sha256`.
  - `runs.policy_sha256`, `statements_sha256` and `code_closure` are never checked.
  - The authorization binds only `c11r_runs.py`, plus the self-declared (unrecomputed) `sha256` fields of policy and table.
  - The runner checks neither the gate toolchain nor the qualification.
  - Reproduced: a certifier edit committed before the seal, then reverted, is sealed and compared normally, and status/qualifier cannot see it. An in-place-edited policy passes `check_authorization`.

DISPOSITION: NOT_READY
