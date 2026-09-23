# C11R pre-freeze review, round 2 (independent)

- **Reviewer:** fresh, independent pre-freeze reviewer. I had no part in C2-C11, in C11R, or in the first C11R review.
- **Reviewed commit:** `affdf8a33caa79a6adb3412cdf63e42a3fcbc440`, branch `p5y-k5-tail-c11r-n9-statement-alignment`. Verified at start: `git rev-parse HEAD` equals it and `git status --porcelain` is empty. The only change I made is this file, which is untracked.
- **Method.** I read the source. The probes are scratch scripts in the session scratchpad under `rev2/`:
  - `seal_probe.py`, `fw_probe.py`, `fw_key_probe.py`, `cmp_probe.py`
  - `v11_probe.py`, `v11_skip_probe.py`, `v6_v4_probe.py`, `selector_probe.py`
  - `lower_probe.py`, `fd_family_probe.py`, `fresh_probe.py`
  - `imports_probe.py`, `result_lang_probe.py`, `phi_cost_probe.py`

  Each imports campaign modules with bytecode writing disabled and calls single functions. Inputs were synthetic, on the non-target block NT = [5/2, 5/2 + 108337/1250000], or at e = 5/2.
- **What I did not do.**
  - I ran no producer.
  - I never ran `c11r_runs.py`, `c11r_qualify.py` or `c11r_compare.main()`.
  - I never loaded the quarantine, the old mixed table from history, or REGISTRY_C2's magnitude fields. The registry was touched only by `sha256` and a `grep -o` for the two cell-306 drift endpoints.
  - I computed nothing on cell 306's drift block.
  - I changed no git state.
- **Environment:** Python 3.14.5. numpy, scipy, flint, mpmath, sympy and gmpy2 are all absent. `PYTHONINTMAXSTRDIGITS=0`.
- **A disclosure of my own.** The brief told me to read `evidence/errata/C11R_ERRATA.json` first. That file contains three original magnitudes, rounded (see B-2). I therefore saw them. They are not reproduced anywhere in this review.
- **Status of this file:** COMPLETE. Every item from 1 to 20 and every judgement call from A to I was reached.

---

## Summary

The repair fixes much of what the first review found:
- errata revision 2 is candid, and E2 is properly retracted;
- the committed evidence is fresh against the committed code (independently recomputed);
- the drift layer is byte-identical to 49b17ab4;
- the upper and lower selectors are exact (brute-force verified);
- the D_lo sub-solution route is mathematically sound;
- no target science, qualification, runs artifact or comparison exists.

The rulings on the selector (A), on moving validation off the open cells (D) and on "stronger by fewer premises" (G) go the author's way.

**The campaign should still not freeze.** Five defects are load-bearing. Three of them sit in the post-result path, where they cannot be fixed after the run without editing frozen code in the presence of results.

1. **CRITICAL: the frozen comparator refuses every genuine runs artifact** (B-1).
   - `c11r_compare.verify_seal` rejects any artifact whose JSON text contains the substring `"magnitudes"`.
   - The only emission path, `c11r_schema.emit_runs`, always writes the key `contains_original_magnitudes`.
   - So Phase 15 cannot run as frozen, and no test reaches the defect.
2. **MAJOR: the firewall's "proof by AST" is false on the committed tree** (B-2).
   - Three pre-result modules load original magnitudes:
     - `c11r_status` json-loads the quarantine;
     - `c11r_b0` json-loads every JSON file under `closure_proofs/`, the registry included;
     - `c11r_policy`, which freezes the configuration, reads the first review's markdown, which carries three rounded originals.
   - The errata artifact and its producer restate those originals.
   - The scanner missed 12 of the 14 leak paths I planted.
   - FIREWALL PASS, G16 and M03 ("ANY path") would be frozen as false certificates.
3. **MAJOR: statement equivalence is still tautological in production, one level up** (B-3).
   - Both sides are instances of one template, `c11r_schema.statement`, keyed only by the constant's name.
   - Nothing ties a statement to the certificate that supposedly proves it. In `cmp_probe.py`, a runs artifact whose F_H certificate says kernel `K_e`, route `original_certify_block` and `certified: false` still gets tau and C_T EQUIVALENT and STRONGER. A forged Abar value passes as STRONGER.
4. **MAJOR: the post-run checks exist only inside the mutation suite** (B-4).
   - `trace_values`, `refuted_but_sent` and `dispositions_consistent` are called by no production verifier.
   - So M14, M28 and M38 detect with detectors the pipeline never runs, and gate predicates G8 and G10 have no evaluator.
5. **MAJOR: `c11r_qualify.py` is stale against the repair and will crash** (B-5).
   - It loads the deleted `evidence/screen/C11R_SCREEN.json`.
   - Its resource plan contradicts the frozen policy.
   - Its Q5 still computes inside open cell 307's block.
   - `c11r_status` cannot see any of this, because qualify has no artifact yet.

---

## Load-bearing findings

### B-1. CRITICAL: the comparator's seal check rejects every artifact the producer can emit

**The defect.**
- `code/c11r_compare.py:78-80`:
  ```python
  for key in ("magnitudes", "value_float", "original_value", "original_values"):
      if key in disk.decode():
          problems.append(f"the runs artifact contains a {key!r} field")
  ```
- `code/c11r_schema.py:129-130`, inside `emit_runs`, which is the only constructor of a runs artifact:
  ```python
  P_SEAL: {"sealed_before_comparison": True, "contains_original_magnitudes": False}}
  ```

**The probe (`rev2/seal_probe.py`).**
1. Build a synthetic artifact with `c11r_mutations.base_runs`, which calls `c11r_runs.assemble`.
2. Add `provenance` and `sha256`.
3. Serialise it exactly as `write_evidence` does.

Result: `S.validate_runs(...) == []`, but the content test hits `['magnitudes']`. The context is `"seal": { "contains_original_magnitudes": false`. Every sealed genuine artifact therefore yields `REFUSE`.

**Why nothing caught it.**
- M26 exercises only the pure `verify_seal_bytes` and the real tree, where no runs artifact exists, so `"no runs artifact on disk"`.
- Its clean control never passes a producer-built artifact through the content test.
- The comparator self-test never calls `verify_seal`.

**Why it blocks.** At Phase 15 the only way forward is to edit the comparator after the target values exist. That is what a freeze exists to prevent. Nothing binds the comparator's hash at the freeze either: the gate binds only the policy and statement hashes. So the edit would not even be mechanically detectable, beyond the mutation artifact going stale.

### B-2. MAJOR: the original-value firewall does not hold, and its proof reports PASS

**The claim.** `evidence/firewall/C11R_FIREWALL.json` has `FIREWALL_CLASS: PASS` and `offenders: []`. `c11r_firewall.py:3-7` says only `c11r_table.py` and `c11r_compare.py` can load a magnitude. E8 says "the six original magnitudes live only in a quarantine artifact".

**What is actually on the committed tree.**

| Where | What it loads |
|---|---|
| `code/c11r_status.py:36-38, 131-132` | `rglob("*.json")` over `evidence/`, then `json.loads` of each file. That includes `evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json`, which the committed status lists as a checked artifact. |
| `code/c11r_b0.py:92-96` | `C.CLOSURE.rglob("*.json")`, then `json.loads` of every JSON file under `closure_proofs/`. That includes `REGISTRY_C2.json` and the quarantine. |
| `code/c11r_policy.py:132` (`disclosed_failures`) | The whole of `review/REVIEW_C11R_PREFREEZE.md`, via `read_text()`. That file contains three original magnitudes to 4-5 significant figures, each on three lines (checked with `grep -c` only). |
| `evidence/errata/C11R_ERRATA.json`, `code/c11r_errata.py` | E2's factual sequence restates the same three rounded originals and ratios to them. `c11r_status` loads this artifact. |

As far as I can see, none of these loads feeds a decision:
- status and B0 only hash and scan keys;
- the policy regex-extracts per-box rows after `chosen` is fixed, which I checked from the code order at lines 257-275.

But E8's defect class, originals reaching a pre-result module, has recurred in the module that freezes the configuration, and the proof says it has not.

**The scanner's coverage (`rev2/fw_probe.py`).** I ran `c11r_firewall.analyse_source` on 14 synthetic leak paths. It flagged 2 of them: a direct `open()` of the quarantine name, and `C.load` of a literal quarantine path. It missed 12:
- a glob/rglob load (the `c11r_status` pattern);
- a protected name built by concatenation;
- a protected name built by f-string;
- `from c11r_compare import load_original_magnitudes` (only `ast.Import` aliases are tracked);
- taint through a `for` target;
- taint through a walrus;
- taint through a function argument;
- `C.git("show", "HEAD:.../REGISTRY_C2.json")` (`git` is not in `LOADER_ATTRS`);
- `importlib.import_module` plus `getattr`;
- `subprocess.run(["cat", ...quarantine])`;
- reading the review markdown;
- reading the errata JSON.

The last two carry originals but are not in `PROTECTED`.

M03 is named "reading original magnitudes from ANY path" and records DETECTED against 8 planted sources the author wrote. This is the C8/C10 "presence-check-as-detection" defect again.

### B-3. MAJOR: the equivalence check compares a template with itself

**How both sides are built.**
- `code/c11r_table.py:255-266` builds the original statements with `S.statement(k, ...)`.
- `code/c11r_runs.py:86` builds the independent statements with the same `S.statement(constant, ...)`.

Every EXACT field comes from the same dicts in `c11r_schema.py:24-56`, looked up by the constant's name: quantity, kernel, convention, direction, state_set and proposition. The drift domain is also shared, because `c11r_runs.main` takes E from the statement table (`c11r_runs.py:140`).

**What `EQ.compare` can therefore return.** For any artifact `assemble` can emit, it returns EQUIVALENT for Abar, tau and C_T, and STRONGER for D_lo, and nothing else. `rev2/cmp_probe.py` confirms "exact fields identical: True" for all four.

**What is never checked.** Neither `check_internal` nor `compare` reads the `certificates` block. In the probe, an artifact with these certificates:
- F_H: `kernel="K_e"`, `route="original_certify_block"`, `certified=False`, `margin_lower_bound="-1"`;
- F_D: `certified=False`;

passes `validate_runs` with no problems. The comparator still returns tau and C_T `('EQUIVALENT', 'STRONGER')` and D_lo `('STRONGER', 'STRONGER')`. Halving the Abar value, which no certificate produced, gives `('EQUIVALENT', 'STRONGER')`.

The certificate's `kernel` string is itself hard-coded beside the `atom_removed` flag (`c11r_runs.py:188`). Nothing records which kernel was actually used.

"Neither side is built from the other" is literally true. But the first review's minimum item 2, "build the independent proposition from the runs artifact's own fields, including kernel, quantity, state and provenance", is satisfied in letter only. Those fields are declarations, not facts about the run.

**Consequences in production.** INVALID, NOT_EQUIVALENT, INDEPENDENCE_VIOLATION and DISAGREES are all unreachable, since no independent route produces an opposite-direction bound. With D1 and D2 hard-coded NOT_IMPLEMENTED, `N9_VERDICT` is AGREEMENT_INSUFFICIENT for every possible run. That is disclosed conditionally, but the commit message's "All five N9 classifications are now reachable" is false for production.

The per-target numeric classes are real and do vary.

### B-4. MAJOR: the post-run guards are defined only in the mutation suite

`trace_values` (`c11r_mutations.py:119`), `refuted_but_sent` (:147) and `dispositions_consistent` (:152) are called only inside `c11r_mutations.py` (grep). No production verifier runs them on the real artifact: not the comparator, not the qualifier, and no gate evaluator (none exists).

- G8 ("NOT_IMPLEMENTED only where the policy says") has no production evaluator.
- G10 ("screened before certified") has no production evaluator.
- M14, M28 and M38 report DETECTED, but the detector lives in the test.

This is the C7 lesson "guards in the wrong module / tests that raise their own refusal". Together with B-3, it means Phase 15 would not check that the reported values are the certified ones.

### B-5. MAJOR: `c11r_qualify.py` would crash, and it contradicts the frozen policy

- **It crashes.** Line 141, `C.load(C.NS / "evidence" / "screen" / "C11R_SCREEN.json")`: this repair deleted that file (`git diff --stat 49b17ab4 affdf8a3`). Qualify would run Q1-Q9 and a 3-depth cost probe, then raise FileNotFoundError.
- **It contradicts the policy.**

  | | `c11r_qualify.py` (lines 146-166) | Frozen policy |
  |---|---|---|
  | Candidates to certify | 2 | 3 families |
  | Resource cap | 5400 s, 4 candidates, max depth 5 | 10800 s, one configuration |
  | Retries | "Deepening is permitted only after re-screening" | "no escalation, no retry" |

- **Its Q5 is on an open cell.** Q5 (line 83) computes the scalar-collapse probe at e = 18355/10000, which lies inside open cell 307's block [1.7885921, 1.882413]. That contradicts `c11r_validate.py:9-12` and the commit message ("every validation ... runs on the non-target block").
- **It is invisible to `c11r_status`.** Status checks artifacts, and qualify has none, so status reports CONSISTENT while a frozen module is stale. This is exactly the E4 class the status module was built to catch (see item 16).

---

## Item-by-item

**1. Cell 306 drift block in every place: PASS.**
- `C11R_N9_STATEMENTS.json` gives `e_lo = 680769/400000` and `e_hi = 17885921/10000000`, with 9 contiguous sub-blocks covering the block exactly. `e0 ± rho` reproduces the block.
- All six `original_statements` and the gate's `target.drift_domain` use it.
- The table's recorded input hash `1b2b8349…` equals the current REGISTRY_C2 file hash. `grep -o` shows the two endpoint strings in the registry.
- The width is exactly 108337/1250000.
- `c11r_runs` takes E only from the table. No other module computes on it: policy, validation and mutations use NT.

**2. Cell 307 not substituted: PASS, with one MODERATE exception.**
- 307's block appears only as mutant values: the equivalence self-test at `c11r_equiv.py:195` and M22.
- The exception is `c11r_qualify.py` Q5, which computes at e = 18355/10000 inside 307's block (B-5). It uses manufactured weights and substitutes nothing, but it breaks the stated "off every open cell" rule.

**3. Independence, including transitive imports: PASS.**
- The transitive closure of all `c11r_*.py` is 21 modules. `rev2/imports_probe.py` recomputed it: the C11R modules, plus `c11_certifier`, `c11_common` and `c7_gaussian`.
- Import roots contain no forbidden-graph module and no backend.
- There are no `importlib`, `__import__`, `exec`, `eval` or `run_path` calls.
- `c7_gaussian` imports only `fractions`. `c11_certifier` imports only `c11_common` and `c7_gaussian`.
- The backend is absent from the environment (`importlib.util.find_spec`).

**4. Block-uniform drift soundness: PASS.**
- `c11r_idrift.py` is byte-identical to 49b17ab4 (`git diff --quiet`; sha256 `dd611a71…` at both).
- F_K and F_H are certified only by the reviewed `supersolution_margin_iv` on `X.cover(D)` (`c11r_runs.py:216`). The new factored data only chooses a member.
- `PhiCache` monkeypatches `G.Phi` with an unbounded `lru_cache`. That is bit-transparent, because Phi is a pure function of an exact Fraction (V15; my V6 and V11 probes also ran under it).
- The one route that does not pass through the reviewed module is F_D (`c11r_boxdata.subsolution_margin_iv`). It is new code; I review it in item 17.

**5. u-partition validity, including `box_upper_coeffs`: PASS, with one MINOR note.**
- I compared the two panel loops line by line: same `u0`/`u1`, same z-range, same `m_lo`, same point-argument mass, same atom test. For w = A − B·m with A ≥ 5B, `max(0, ·)` is inactive, because `m_lo ≤ 5 − step`.
- Recomputed on NT (`rev2/v11_probe.py`, `v11_skip_probe.py`):
  - the reviewed margin minus the factored margin lies in [−6.2e-96, 0] over 19 comparisons;
  - these include the boundary member A = 5B, a box at m ∈ [75/16, 5], and the depth-5 origin box at 64 panels, where the Khat atom-skip branch actually fires (2 panels skipped);
  - `mu = 2^-60` dominates.
- MINOR: the committed V11 never exercises the skip branch. At 16 panels on its boxes, 0 panels are skipped. My probe covers it.

**6. Scalar collapse at e = 5/2: PASS.** `rev2/v6_v4_probe.py` gives 17/17 bit-equal. These are my own weights and states, not V6's list: kernel, box bound at 12 panels, and alarm probability.

**7. Atom convention and K_e = Khat_e + atom: PASS.**
- On NT: 9 new (weight, state) pairs, maximum separation −0.0058, so consistent.
- At the scalar e = 5/2: the midpoints of K_e w and Khat_e w + atom are identical, and the enclosure width is 7e-95.
- Note that the block-level V4 is a weak test: 0.05-wide enclosures overlap easily. The scalar form is the sharp one; M06 at a 1/4 window shift is also detected.

**8. Policy prospective and original-value-free: PASS in its rule, with caveats.**
- The selection rule and the configuration rule reference no original value and no comparison threshold.
- The configuration is chosen at `c11r_policy.py:257-270`, before `disclosed_failures()` runs.
- Caveat (B-2): the policy module loads the first review's text, which carries originals.
- Caveat: it re-publishes historical target-block box margins and screen minima from 38f59993 in its evidence. This is disclosed, not decisive, and computed in revision 1, not now.
- MODERATE: the frozen policy declares an execution check ("certified alpha ≤ alpha_pw_max") and a stop label (`SELECTOR_CERTIFIER_MISMATCH`). Neither exists in `c11r_runs.py` (grep). These are fixes recorded but never wired in (C10 lesson).

**9. Firewall: FAIL.** See B-2.

**10. Comparator's independent side: PARTIAL, MAJOR.** It is read from `targets[k].statement`, and nothing is copied from the original. But it is template-equal to the original and unchecked against the certificates. See B-3.

**11. Direction asymmetry: PASS, with one MINOR note.**
- `classify_numeric` uses the original's direction. D_lo is the only LOWER bound. The boundaries match the frozen table (≤ 2·orig; ≥ orig/2).
- The self-test covers D_lo below half the original and above the original.
- MINOR: `FACTOR = 2` and the inequalities are hard-coded in `c11r_compare.py`. The output cites the statement table as `comparison_rule_source`, but nothing checks that the two agree. M10 checks the table only.

**12. Mutation freshness and real schema paths: PARTIAL.**
- Freshness is independently verified (`rev2/fresh_probe.py`, quarantine skipped): all 11 other artifacts are FRESH, and each recorded code closure equals `code_closure` recomputed now.
- Run-artifact mutants are built with `c11r_runs.assemble` and read through `c11r_schema` accessors.
- The gaps are B-1 (the seal path is untested) and B-4 (the detectors are not in production).
- Minor: reads not made through `C.load` are not bound as inputs. Examples are M07's `cusum_layer1.py` and M10's 49b17ab4 gate blob.

**13. M26 and M28 fire, with controls: PASS as stated.**
- I re-executed M28's logic on an `assemble`-built artifact: mutant flagged, clean control not flagged.
- But M28's detector exists only in the suite (B-4), and M26's clean control never reaches the real content check (B-1).

**14. E1 and the absence of results: PASS.**
- `git log --all` shows no `C11R_RUNS.json`, `C11R_QUALIFICATION.json`, `C11R_COMPARISON.json` or `C11R_AUTHORIZATION.json` in any commit.
- There is no `evidence/runs/` on disk.
- No campaign process is running (`ps`).
- E1's record is consistent with this.

**15. E2 chronology and retraction: PASS, with MINOR notes.**
- The revision-1 sentence exists only under `RETRACTED_sentence_from_revision_1`, with status "RETRACTED -- false; do not rely on it". It is not live anywhere else in code, config or evidence (grep).
- MINOR: it remains live in the immutable 38f59993 commit message, which the retraction does not name.
- E2's replacement restates three original values (B-2).

**16. Stale evidence (E4) and whether status would catch a recurrence: PARTIAL, MODERATE.**
- Status catches the literal E4 pattern: producer, closure and input hashes, plus the V6-count contradiction. Its controls are executed.
- It misses the general class:
  - modules without artifacts: qualify is stale while status reports CONSISTENT (B-5);
  - inputs not read through `C.load`: the review markdown, git blobs, `cusum_layer1.py`, the R5 map, B0's whole-tree scan;
  - contradictions other than V6, such as qualify's cap against the policy's cap, or the policy's declared checks against the runs code.

**17. The D_lo sub-solution route: PASS on soundness, MODERATE on the record.**
- **The argument is correctly stated.**
  - Iterating u ≤ h_1 + Khat u gives u ≤ Σ_{k<n} Khat^k h_1 + Khat^n u.
  - Khat 1 ≤ K 1 = 1 − h_1 ≤ 1 − h_min pointwise, so Khat^n u ≤ ‖u‖(1 − h_min)^n → 0.
  - R is closed under alarm-free moves: if both arms stay positive, p' + m' = p + m − 1.
  - D_e = d(atom) ≥ α, for each e separately.
- **The box lower bound is rigorous.**
  - Panels are taken inside the intersection window [d − C + e_hi, C − b + e_lo].
  - Every panel that meets the union atom window [c − K, K − a] is dropped. That can only lower a sum of non-negative terms.
  - Each kept panel contributes u(m_lo)·mass_lo, with m_lo = c − z_hi − K.
  - The alarm-probability bound `h1_box_lower` uses the correct extremal corner (a, c) with e_hi on the upper tail and e_lo on the lower tail.
- **Checked on NT** (`rev2/lower_probe.py`): 3 boxes, including the depth-5 origin box, with 12-15 state/drift probes each.
  - The lower Khat bound is ≤ the pointwise value (slack ≥ 0.016).
  - `h1lo` is ≤ the pointwise h_1, with slack ≥ 3e-16, so it is tight.
  - The factored form matches the rigorous one to ~1e-96.
- **The selector is exact.** `select_lower` equals brute force over all 1001 grid values of β, and α + 1/1000 fails (`rev2/selector_probe.py`).
- **The classification is honest.** It is "INDEPENDENT_STATEMENT_IMPLEMENTED (target run pending)", with dependencies () and h_min > 0 and u ≥ 0 certified in the same pass.
- **The record is wrong about the family** (judgement C).

**18. D1/D2 scope: PASS, with one MINOR note.**
- Both are recorded as PROSPECTIVELY_REACHABLE_BUT_NOT_IMPLEMENTED in the policy and in the runs `not_impl` reason.
- MINOR: the policy's "exact dependency list" omits "sup_source_derivative bounds", which the statement table's `additional_machinery_D_requires` includes.

**19. No pre-written scientific conclusion: PASS textually.**
- `rev2/result_lang_probe.py` scanned every string in every `c11r_*.py` and every artifact except the quarantine, using the gate's phrases, M35's phrases and seven more.
- All 31 hits are quotations of revision 1, planted controls, negations ("that N9 is closed while…" under `forbidden_conclusions`) or V5's `predicted` field.
- The structural caveat is B-3: the N9 verdict is fixed by construction.

**20. No target science, qualification or runs before this review: PASS.** See item 14. In this turn, all numerical evidence is on NT or at e = 5/2, with the one exception of qualify's Q5 (not run, and at cell 307, not 306).

---

## Judgement calls

**A. The selector: legitimate, and not tuning.**
- The optimisation is a deterministic function of frozen inputs: family, grid, `b_max`/`beta_max`, `mu`, rounding, tie-break, depth and panels. It is applied once, with no human decision and no escalation after any target quantity exists.
- Its objective, the minimal certified A or maximal α, is the certifier's own. It references no original value and no threshold.
- Its choice is then re-proved by the independent rigorous routine. It is the certifier returning its best bound at a fixed resolution.
- "Tuning a candidate using a target certification result" means a decision (human or rule) that reacts to an observed target outcome, and above all one that can move the answer toward the original. Neither is possible here: the objective is monotone toward tightness.
- The grid ranges were chosen by an author who knows the originals. But a binding range (B = `b_max`) can only loosen A, which moves toward INSUFFICIENT. It cannot manufacture agreement.
- I verified the ternary search against brute force on NT: 4001 values of B for K and Khat, and 1001 values of β. All are identical, and the reviewed certifier accepts the choice and rejects one grid step less.
- MINOR: at coarse configurations the optimum sits at `B = b_max` (depth 2, 8 panels on NT gives B = 4). The runs artifact should flag a boundary optimum.

**B. The configuration: the rule is prospective, but the cap margin is not acceptable as argued.**
- Minimising λ1 subject to a cost cap uses geometry and NT cost only. λ1 failing to cover the actual loss is acceptable for a ranking figure, and the author discloses it.
- But the "pessimistic" premise is contradicted by the policy's own live probe. Live cost per box-panel was 0.4294, 0.4505 and 0.4648 against frozen constants of 0.37, 0.42 and 0.44. That is 16%, 7% and 6% slower, not faster.
- At the live P64 speed, depth 5 / 64 panels models to 363·65·0.4505 + 84·1.558 ≈ 10,761 s, which is 99.6% of the 10,800 s cap, not 93%.
- The source of the constants, "policy evidence 2bfbe5a304f35dc3", is not in any commit (`git log --all -S`). The constants are transcribed from an artifact that no longer exists: the M29 defect class.
- The cap is checked only between boxes and before each family, never inside a certification. F_D, the new D_lo route, always runs last. There is no cost re-probe at Phase 14. Whether D_lo is certified or lost to RESOURCE_CAP therefore depends on machine load at execution.
- Fix: refuse to start Phase 14 if a fresh probe predicts overrun (or raise the cap), and commit the cost source.
- The policy design was informed by disclosed revision-1 target-block margins. The only lever that knowledge gives is "finer", which is monotone, so it cannot bias toward agreement.

**C. The D_lo family: keeping it was right, but the stated reason is wrong.**
- On NT, the linear family's pointwise ceiling (`rev2/fd_family_probe.py`: 84 states, β over 1001 grid values) is α ≤ 0.9748. The float reference d(atom) is 0.978-0.982.
- So the family is not loose. V14's α = 0.345 is box and panel loss at depth 3 / 16 panels, not at the frozen depth 5 / 64. The frozen config's u-panel z-width is about 0.26, against about 0.69 in V14.
- The policy's `F_D_non_target_tightness` reading misattributes the cause and quotes a figure from a non-frozen configuration. It says "SOUND but LOOSE… near a third… a richer family is a candidate for a successor". It is labelled non-target, but it reads as a quantitative expectation.
- Not refining after learning something was the right discipline. The record should now say that the NT gap is configuration loss and drop the "near a third" figure. MODERATE.

**D. All validation moved off open cells: nothing needed on cell 306's block was lost.**
- The checks are drift-independent identities and soundness tests.
- The NT cost model transfers to the target. At depth 5 / 64 panels, every u-panel endpoint denominator divides 2^15·5^8 for both blocks (400000 = 2^7·5^5 and 10^7 = 2^7·5^7 both divide it). This is an algebraic argument, with no target computation. A synthetic timing shows Phi's cost moves only ~7% per 2 extra denominator bits.
- NT's largest |u| (≈ 8.1) exceeds the target's (≈ 7.3), so no new series-refusal regime arises.
- The exception is Q5 (B-5).

**E. Load/store in the firewall: sound in itself, MINOR.**
- A plain `Store` subscript reads nothing, so N6 is correctly clean.
- `d["magnitudes"] += 1` (AugAssign reads and writes, but has Store context) is missed.
- So are `.pop()`, `.setdefault()` and `.items()` iteration (`rev2/fw_key_probe.py`).
- The real weakness is B-2, not this change.

**F. M35's docstring exclusion: sound today, MINOR.**
- No campaign code emits `__doc__` (grep for `__doc__`, `inspect.` and `getdoc` is empty), so a docstring cannot reach output.
- The exclusion is fragile to a future `print(__doc__)`.
- M35 scans only `c11r_compare.py`, not the other emitters (`c11r_runs`, `c11r_status`).

**G. "Stronger by fewer premises": logically right, guarded only declaratively.**
- The same conclusion under fewer hypotheses implies the conditional statement.
- The guard, `ROUTE_REQUIRED_DEPENDENCIES` by route label, only checks the artifact's own labels against its own declared dependencies. It cannot see a producer that consumes a premise it did not declare.
- For the sub-solution route I checked by reading `c11r_boxdata.py`. No C_T or tau enters. The two side conditions, u ≥ 0 and h_min > 0 (NT: 0.00135), are certified in the same pass, and `certified` requires both.
- Statement-level STRONGER is independent of the value, and the direction-aware numeric rule decides afterwards, which is correct.

**H. The author's disclosure: inadequate as recorded, MODERATE.**
- The ad-hoc quarantine load appears nowhere in the committed record. I grepped code, config and evidence for "ad-hoc", "ad hoc" and "loaded the quarantine", and checked both repair commit messages. It exists only in the brief to me.
- The campaign's own errata policy is "recorded where a reader will find them", and E5 is the lesson about unrecorded conduct. It needs an erratum.
- Substantively it is plausibly harmless, since the values were already known from revision 1. I can confirm only that no artifact records it, not that no choice changed.

**I. Things the campaign has not noticed.** These are B-1 to B-5, plus:
- **(a)** The gate binds the policy and statement hashes, but not `c11r_compare.py`, `c11r_equiv.py`, `c11r_schema.py` or `c11r_boxdata.py`. A post-freeze edit to the comparator, which B-1 would force, leaves no frozen trace. MODERATE.
- **(b)** G10's pointwise screen cannot fire on a box-feasible member, because box feasibility at the covering box implies a positive pointwise margin. It is a consistency check that cannot fail on substance, not a screen. MINOR.
- **(c)** The certificate records no drift domain and no `atom_removed` flag. The run's provenance of "what was proved over what" rests on hard-coded strings (see B-3). MAJOR, folded into B-3.
- **(d)** The commit message's "All five N9 classifications are now reachable" and "catching 8/8 planted load paths" are true only of self-written controls. MINOR.
- **(e)** A stale `code/__pycache__/c11r_screen.cpython-314.pyc` remains for the deleted module. It is ignored by git and harmless (sourceless imports do not use `__pycache__`). MINOR.

---

## Severity index

| # | Severity | Finding | Location |
|---|---|---|---|
| B-1 | CRITICAL | Seal check rejects every producer-built artifact (`"magnitudes"` substring vs `contains_original_magnitudes`); untested | `c11r_compare.py:78-80`; `c11r_schema.py:129-130` |
| B-2 | MAJOR | Firewall PASS false. Status and B0 load the quarantine and registry; the policy reads review text carrying originals; errata restate them; scanner missed 12 of 14 planted paths | `c11r_status.py:36-38,131`; `c11r_b0.py:92-96`; `c11r_policy.py:132`; `c11r_errata.py`/errata E2; `c11r_firewall.py:34-41,87-91` |
| B-3 | MAJOR | Statement equivalence template-tautological; certificates never consulted; forged value and uncertified certificate pass | `c11r_schema.py:24-102`; `c11r_table.py:255`; `c11r_runs.py:86,188`; `c11r_equiv.py:53-142` |
| B-4 | MAJOR | `trace_values`, `refuted_but_sent` and `dispositions_consistent` exist only in the mutation suite; G8/G10 unevaluated | `c11r_mutations.py:119-155` |
| B-5 | MAJOR | Qualify loads a deleted artifact (crash), contradicts the policy (cap, candidates, retries), runs Q5 inside cell 307 | `c11r_qualify.py:83,141,146-166` |
| 16 | MODERATE | Status blind to modules without artifacts and to reads outside `C.load` | `c11r_status.py` |
| B / C | MODERATE | Cost constants not pessimistic on the policy's own probe (99.6% of cap at live speed); cost source uncommitted; D_lo last and lost first; F_D looseness misattributed to the family | `c11r_policy.py:48-59,224-236`; policy evidence |
| 8 | MODERATE | Policy-declared execution check and stop label not implemented in runs | `c11r_policy.py:341-355` vs `c11r_runs.py` |
| H | MODERATE | Ad-hoc quarantine load not recorded in any committed erratum | errata |
| I(a) | MODERATE | Comparator, equiv, schema and boxdata hashes not bound at freeze | gate |
| 2 | MODERATE | Q5 computes at e = 18355/10000 inside cell 307 | `c11r_qualify.py:83` |
| 5, 11, 15, 18, E, F, A, I(b,d,e) | MINOR | V11 never hits the skip branch; FACTOR not read from the frozen rule; retracted sentence live in 38f59993 message; D1/D2 list missing one item; AugAssign/pop; docstring fragility; boundary-B flag; G10 vacuous; self-control claims; stale pyc | as cited |

**What is right and should be kept:**
- errata revision 2, including the honest E2 retraction;
- the provenance and freshness layer;
- `c11r_idrift.py`, unchanged;
- the factored upper coefficients and both exact selectors;
- the D_lo sub-solution mathematics and its rigorous box lower bound;
- the direction-aware numeric rule;
- the equivalence self-test's planted controls;
- the NT-only validation;
- the pre-result state.

**Minimum to reach READY_TO_FREEZE:**
1. **Seal check.** Replace the substring test with a structural key check. Add an executed clean control that passes an `assemble`-built, provenance-bound artifact through the full `verify_seal` content path, for example by factoring it into a pure function of bytes and the producer hash.
2. **Firewall.**
   - Keep status and B0 from json-loading the quarantine and registry, or declare them as hash-only readers with a reason.
   - Stop `c11r_policy` reading the review text; derive the rows into a magnitude-free artifact once.
   - Describe the originals in E2 without restating the digits.
   - Extend the scanner to ImportFrom, the `git show` helper, glob loads, for/walrus/argument taint and built names, each with a planted positive.
3. **Statement-to-certificate binding.**
   - Record the actual `atom_removed` flag and drift domain in each certificate.
   - Derive the statement's kernel and convention from them.
   - Have the production comparator, or a post-run verifier that the gate names for G8, G10 and G14, check target status against `certified`, run `trace_values`, `refuted_but_sent` and `dispositions_consistent`, and check the route against the certificate.
   - Bind the comparator, equiv, schema and boxdata hashes in the gate.
4. **Qualify.** Bring `c11r_qualify.py` in line with the repaired policy: remove the deleted-screen load, align the cap, candidates and retry text, and move Q5 off cell 307. Or withdraw it from the freeze and state the qualification plan.
5. **Record.**
   - Add an erratum for the ad-hoc quarantine load.
   - Re-attribute the F_D looseness to configuration loss.
   - Correct the "pessimistic" cost claim and commit its source, or add a Phase-14 pre-start re-probe that refuses on predicted overrun.
   - Implement or delete `alpha_pw_max` and `SELECTOR_CERTIFIER_MISMATCH`.
6. **Regenerate and hold.** Regenerate all evidence, re-run status, and hold the tree fixed for the next review.

Load-bearing blockers:
- B-1 (CRITICAL): `c11r_compare.verify_seal` refuses every genuine runs artifact, so Phase 15 cannot run without a post-result edit to the comparator.
- B-2 (MAJOR): the firewall's PASS is false. Original magnitudes reach `c11r_status`, `c11r_b0` and `c11r_policy`, and the errata restate them. The scanner misses 12 of 14 planted load paths.
- B-3 (MAJOR): statement equivalence is template-tautological and never checked against the certificates. An uncertified or original-route certificate and a forged value pass as EQUIVALENT/STRONGER.
- B-4 (MAJOR): the value-trace, screen-order and disposition guards exist only in the mutation suite. No production verifier evaluates G8 or G10.
- B-5 (MAJOR): `c11r_qualify.py` loads a deleted artifact and would crash. It contradicts the frozen policy and computes inside open cell 307.
NOT_READY
