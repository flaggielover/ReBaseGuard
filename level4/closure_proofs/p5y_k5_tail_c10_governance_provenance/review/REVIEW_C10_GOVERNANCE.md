# Independent hostile review — C10 (C2 provenance repair and prospective adoption governance audit)

Reviewer: fresh context, no prior involvement in C2–C9.
Worktree: `/Users/suzhe/ReBaseGuard-k5c10`, branch `p5y-k5-tail-c10-governance-provenance`, HEAD `b10cdc7d`.
Method: independent `git` re-derivation, independent reading of the cited source documents, and
re-implementation of C10's detectors in a scratchpad. **I did not run C10's producers** (they rewrite
their own evidence) and I modified no file except this report. No AWS, no Vultr, no SSH, no installs,
no numpy/scipy/flint.

## Summary of what I could confirm

Before the findings, the parts that survive attack, because they matter for weighting the rest:

- **Q1's arithmetic is exactly right.** I recomputed all three producer hashes from git objects:
  `e71378a0` → `4ac24d9e1826…`, `e9c230d3` → `629715c0afdf…`, `2b045564` → `0d1d8021a378…`;
  HEAD = `0d1d8021a378…`. `REGISTRY_C2.json:code_sha256.c2_refined_registry` = `4ac24d9e1826…`.
  The pin resolves to `e71378a0`, which is an ancestor of the registry commit `5a94568a`.
  `REGISTRY_C2.json` has exactly one commit in its entire history, so `registry_rebuilt_since = 0`
  is true. `taboo_certify` = `ced9422ca079…` still matches (file lives at
  `p5y_k5_perron_deflated_resolvent/code/taboo_certify.py`, untouched since `760b3993`).
- **The diff localisation is right.** `git diff e71378a0 HEAD -- …/c2_refined_registry.py` touches
  only `verify()` and `main()`. The five scientific constants are byte-identical.
- **The field really is a build-time self-record.** `c2_refined_registry.py:177` emits
  `sha(HERE.read_bytes())` inside `build()`. I searched every `code_sha256` reference in the repo:
  no consumer compares it to HEAD. C10's reading is correct.
- **N9 really is OPEN.** I read the actual documents rather than trusting the scan:
  `p5y_k5_tail_c2_closure/OPEN_NOTES_DISPOSITION_C2.md:78-81` ("A second, independently written
  certifier is the real answer, and C2 has not built one") and
  `p5y_k5_tail_c8_operator_feasibility/review/ADJUDICATION_C8.md:115-123, 350, 456` all treat N9 as
  live. Nothing anywhere asserts it closed. **C10's conclusion is right** (its detector is not — F12).
- **The F1-invariance reasoning is correct.** F1 is `Γ < 0` under supply `G`
  (`c8_adoption.py:50-51`, `c8_chain.Chain`), built from `ADOPTED_TAIL_INPUTS.C_upper` and the frozen
  drift-aware norms. α is the taboo-supersolution rung; `C9_ALPHA_LEVER.json` records
  `same_geometry / same_depth / same_degree = true`, so α moves only registry-supplied atom
  constants. It cannot move `gamma(k, G)`. **The claim holds.**
- **Every number in `README.md` reconciles** with `C8_ADOPTION.json` and `C9_ALPHA_LEVER.json`:
  1.137406 / 1.096007 / 1.370009 / 1.067071 / 1.171431 / Γ_G 0.08511777 and 0.01911559. Mutations
  14/14 and fact verification 15/15 match the artifact counts. All four evidence `sha256` fields
  recompute correctly under `c10_common.write_evidence`'s own convention.
- **Scope discipline is clean.** `git diff fd3cb2d4..HEAD --name-only` returns 11 paths, all inside
  `p5y_k5_tail_c10_governance_provenance`. No `COVERAGE_MAP_R6` anywhere in HEAD. No
  `"guard": "ALLOW"` / `"PERMIT"` anywhere. No historical verdict re-adjudicated; cell 306 is not
  retroactively authorized in C9 — `C10_GOVERNANCE.json:53` explicitly declines to authorize it.
  **Item 6 of the review brief passes without qualification.**

So both headline answers are, in my judgement, *substantively correct*. The findings below are about
how C10 got there, what it left out, and what it claims to have verified but did not.

---

## Findings

### 1. CRITICAL — the Q2 answer omits C2 condition 1, which is both the strongest authority for C10's conclusion and a binding precondition C10 drops

**Where.** `evidence/phase5/C10_GOVERNANCE.json:2` (`Q2_ANSWER`); `README.md:36-56`;
`config/DECISION_GATE_C10.json:9`; `code/c10_governance.py:59, 267-275`.

C10 rests Q2 on four quotes and calls one of them decisive. The decisive one is
`C2_ADJUDICATION.md:501-503`:

> a **second, independently written certifier** reproducing the six operator constants for cell 306
> (closing N9), at which point … a successor should freeze a replacement floor requiring agreement
> between two independent certifier implementations rather than F1

Read in place — it is the **first of three bullets** under "*What will* [discharge this floor for
cell 306]", inside §"What this costs" — that sentence authorizes **one specific replacement**
(two-implementation agreement substituting for F1), **conditioned on closing N9**, for **cell 306**.
It does not, on its own, authorize a successor-defined rule generally. **C10 is over-reading it.**
The C8 adjudicator reads the same sentence narrowly and parenthetically
(`ADJUDICATION_C8.md:115-118`). `Q2_ANSWER`'s word "decisively" is not earned by that quote.

The conclusion is nevertheless **correct**, because of a passage C10 never cites.
`C2_ADJUDICATION.md:536-537`, "Conditions and notes attached to this verdict", item 1:

> **The floor above is now the standard** for K5 m = 5 tail adoptions, prospectively. A successor
> that wishes to replace it must freeze the replacement **before** recomputing any magnitude, as the
> D′ document itself insists.

That is a general, unconditional authorization of successor replacement — exactly what Q2 asks
about — **and it attaches a procedural precondition**. `grep -rn 'wishes to replace|now the
standard|freeze the replacement|recomputing any magnitude'` over the whole C10 namespace returns
**nothing**. C10 has neither the authority nor the condition.

The omission is not academic. `ADJUDICATION_C8.md:130-132` uses precisely this condition to fault
C8: *"C2 condition 1 says a successor wishing to replace the floor must freeze the replacement
*before* recomputing any magnitude, and C8 has relaxed the floor's cost by 1.4 % post hoc without
saying so."* C10's boxed conclusion (`README.md:54-56`) enumerates what a successor may **not** do —
re-adjudicate 305/306, apply its rule to a past adoption — and omits the one procedural constraint
the source actually imposes. A successor reading C10's README as its governance brief would freeze a
replacement rule without knowing it must do so before recomputing any magnitude, and would repeat
C8's error.

This also undercuts the gate's own soundness argument. `DECISION_GATE_C10.json:9` says the one
judgement that matters "is decided by QUOTED TEXT from the C2 adjudication, which C10 cannot alter."
The quoted text C10 selected is the narrow one; the text that actually decides it is absent.

**To fix.** Quote `C2_ADJUDICATION.md:536-537` as the primary authority for Q2; demote 501-503 to
corroboration and state its narrow scope (cell 306, conditioned on N9, F1-substitution only); add the
freeze-before-recomputation precondition to `Q2_ANSWER`, to the `README.md` conclusion box, and to
`Q2_phase6_four_concepts.D_SUCCESSOR_GOVERNANCE_ADOPTION`; add a ledger entry for it.

---

### 2. CRITICAL — Q1's result is an uncited reproduction of the C9 reviewer's published finding, and the error C10 attributes to C9 is not the error C9 made

**Where.** `README.md:10`; `evidence/phase1/C10_ARCHAEOLOGY.json:4` (`Q1_ANSWER`, final sentence);
whole of `code/c10_archaeology.py` Phase 1.

`README.md:10` states: *"C9 misread a build-time record as a live integrity constraint."*
`C10_ARCHAEOLOGY.json:4` repeats it. Two problems.

**(a) The finding is not C10's.** `p5y_k5_tail_c9_e1_cell307/review/REVIEW_C9_STOP.md:180-184`
already published it, in full, before C10 existed:

> I ran the check C9 did not. The registry was built at `e71378a0` (`4ac24d9e`); the producer was
> edited twice since, `e9c230d3` and `2b045564`, and both diffs are confined to `verify()` and the
> new `--out` flag — the `build` path is untouched. So the scientific claim survives, **by luck, not
> by verification**.

That is the bound commit, both divergence commits, and the `verify`/`main` localisation — i.e. every
load-bearing element of C10 Phase 1. `grep -rn 'REVIEW_C9|reviewer|review/'` over the C10 namespace
returns only the *name of mutant M14*. C10 cites the source nowhere, in README, evidence or ledger,
and presents the result as its own archaeology. For a campaign whose stated discipline is "verify
before absorb" and which runs a mutant literally named *"reviewer/adjudicator prose absorbed without
verification"* (`C10_MUTATIONS.json:85`), reproducing a reviewer's finding without attribution is a
failure at the centre of the campaign's own rules. (Reproducing it *is* the right thing to do —
recording it as original is not.)

**(b) The attributed error is false.** C9 never claimed the field was a live integrity constraint.
`C9_TOOLCHAIN.json:132` says: *"the committed registry records a c2_refined_registry hash that does
NOT match the committed file. C9's first pass asserted the recorded configuration was 'checkable
field by field' and never checked it. Any execution must resolve which producer actually built the
registry before claiming to reproduce or improve on it."* Every clause of that is **true**, and the
second clause is a *reproducibility* requirement that C10's own archaeology **satisfies** rather than
refutes. `C9_FACTCHECK`'s ledger entry (`C9 HANDOVER_FACT_VERIFICATION.json:71`) states only the
mismatch. `C9 README.md:74-78` is headed "A provenance discrepancy any execution must resolve first"
— not an integrity claim. C10 assigns a predecessor an error the predecessor did not commit, in the
README headline, with no quotation of C9 anywhere in C10 and no ledger entry supporting the
attribution. In a governance/provenance campaign this is the same failure class as C2 Finding J-1
(`C2_ADJUDICATION.md:406-416`): a characterisation with no committed support.

**(c) A material consequence is dropped.** The same reviewer paragraph continues
(`REVIEW_C9_STOP.md:183-184`): *"`c2_refined_registry.py:177` writes `sha(HERE.read_bytes())` into
every new registry, so a rebuild today cannot reproduce `REGISTRY_C2.json` byte-for-byte
regardless."* And `C9_TOOLCHAIN.json:131` records that the registry's output is **not** a pure
function of its source — *"the taboo candidate is obtained via numpy linear algebra, so BLAS and
architecture participate"*. C10 uses the `sha(HERE.read_bytes())` fact to argue the pin is harmless
and never states either consequence, although both bear directly on "the recorded field records what
built the registry". The pin records the **source**; it does not record the stack, and N10 is open
precisely because nothing does.

**To fix.** Cite `REVIEW_C9_STOP.md:163-187` as the origin of Q1 and mark the C10 result as an
independent reproduction; replace the "C9 misread…" sentences with a quotation of what C9 actually
wrote; record the non-byte-reproducibility of `REGISTRY_C2.json` and the numpy/BLAS dependence as
carried-forward facts under Q1 rather than omitting them.

---

### 3. MAJOR — a broken detector makes the archaeology contradict itself, and the ledger certifies the contradiction as REPRODUCED

**Where.** `code/c10_archaeology.py:148`; `evidence/phase1/C10_ARCHAEOLOGY.json:65-67`;
`code/c10_factcheck.py:51-53`; `evidence/governance/HANDOVER_FACT_VERIFICATION.json:44-52`;
`README.md:28-29`.

```python
taboo_enforced = 'TABOO_SHA256' in psrc and 'raise' in psrc.split("TABOO_SHA256")[-1][:400]
```

`split(...)[-1]` takes the text after the **last** occurrence of `TABOO_SHA256`, which is
`c2_refined_registry.py:177` — inside `build()`'s output dict. I reproduced it: the following 400
characters contain no `raise`, so `taboo_enforced` evaluates **False**. The real enforcement is at
`c2_refined_registry.py:63`, inside `_import()`, which raises `SystemExit` and is called by both
`cover()`/`build()` and `verify()`.

The result: `C10_ARCHAEOLOGY.json:67` publishes
`"taboo_dependency_enforced_at_runtime": false` **two lines below** its own sibling string
(`:65`) asserting *"The dependency that IS enforced at run time is TABOO_SHA256"*, and three lines
below `README.md:28-29` asserting the same. One JSON object states a fact and its negation.
`HANDOVER_FACT_VERIFICATION.json:49` then records the claim *"the **enforced** taboo_certify pin
still matches"* as `REPRODUCED` — certifying an enforcement its own machine-checked field denies.

The narrative is correct and the detector is wrong, which is the worse ordering: the human-written
conclusion was right, and the machine check that was supposed to police it silently disagreed and
nobody noticed.

**To fix.** Scan the whole source (or the `_import` unit specifically) rather than the tail after the
last token; assert consistency between `taboo_dependency_enforced_at_runtime` and the prose in the
same object; re-run and re-publish phase 1 and phase 16.

---

### 4. MAJOR — `any_consumer_compares_it_to_HEAD` is a hardcoded literal; no search was performed

**Where.** `code/c10_archaeology.py:196`; `evidence/phase1/C10_ARCHAEOLOGY.json:64`; `README.md:27`.

```python
"any_consumer_compares_it_to_HEAD": False,
```

This is the single fact that turns Q1 from "a discrepancy" into "not broken", and it is asserted, not
measured. No grep, no import graph, no consumer enumeration appears anywhere in C10. The adjacent
`evidence` string ("No consumer re-checks it against the working tree") is likewise prose.

I ran the search C10 did not: every `code_sha256` reference in `level4/` is either a writer
(`c1_tail_registry.py:153`, `c2_refined_registry.py:177`), a stored artifact, or a reader that does
not compare (`c9_toolchain.py:33, 157` — and `REVIEW_C9_STOP.md:174` says so explicitly). **The claim
is true.** But C10 did not establish it, and a reader cannot distinguish C10's verified facts from
its asserted ones here because both sit in the same object under the key `"evidence"`.

**To fix.** Enumerate readers of `code_sha256` mechanically, record the list and the disposition of
each, and derive the boolean from that list.

---

### 5. MAJOR — the fact-verification ledger states verification methods it did not execute, and two of its fifteen entries are vacuous

**Where.** `code/c10_factcheck.py:41-53, 89-94, 107-110`;
`evidence/governance/HANDOVER_FACT_VERIFICATION.json` throughout.

The ledger's own premise (`c10_factcheck.py:1-5`) is *"Every load-bearing factual claim C10 makes or
adopts is reproduced from the committed tree."* Of the 15 entries, only two actually recompute
anything from the tree (`:36-40` recomputes the bound blob's sha256; `:80-88` recomputes the max over
C9's projection). The rest read fields out of C10's own evidence JSONs while **declaring a method
they did not run**:

| ledger line | declared `verification_method` | what the code does |
|---|---|---|
| `:30` / code `:41-45` | "counted commits after the registry commit" | reads `q1["registry_rebuilt_since"]` |
| `:42` / code `:46-50` | "re-derived by parsing both blobs" | reads `arch[…]["units_changed"]`; no `ast` import in this module |
| `:51` / code `:51-53` | "recomputed sha256" | reads `q1["taboo_pin_still_matches"]` |

Re-reading a value you wrote in an earlier phase is not reproduction, and printing "re-derived by
parsing both blobs" next to it is a misstatement in the one artifact whose purpose is to stop exactly
that.

Two entries are vacuous:

- `c10_factcheck.py:89-94` — the F1-invariance entry passes iff
  `c307["alpha_can_satisfy_F1"] is False`. That value is the hardcoded literal `False` written at
  `c10_governance.py:185`. The check compares a literal to itself and can never fail.
- `c10_factcheck.py:107-110` — the entry *"the C10 decision gate predates the adjudication and is
  unchanged"* passes iff `(C.NS / GATE_SHA_FILE).exists()`. Neither "predates" nor "unchanged" is
  tested, and the file was already read two lines earlier, so existence is guaranteed.

`FACT_CHECK_CLASS = PASS` therefore rests partly on checks that cannot fail.

**To fix.** Recompute each NUMERICAL/GIT_HISTORY claim in `c10_factcheck.py` itself from git objects
and the AST, independently of the phase artifacts; replace the two vacuous predicates with real ones
(for the gate: compare the committed blob sha against a value frozen in an earlier commit, and record
the gate's commit id relative to each evidence commit).

---

### 6. MAJOR — the mutation suite contains the defect class it advertises having removed

**Where.** `code/c10_mutations.py:4, 96-100, 116-120, 136-141, 160-163`;
`evidence/mutations/C10_MUTATIONS.json`; `README.md:82-84`.

The producer docstring (`:4`) states *"No detector is a literal True."* That is false:

- **M14** (`:161-163`) — mutant *"reviewer/adjudicator prose absorbed without verification"*,
  detector: `(C.NS / "code" / "c10_factcheck.py").exists()`. A mutant about absorbing prose is
  "DETECTED" because a file is present on disk. This is the identical failure class to the M05
  tautology the README boasts of fixing (`README.md:82-83`), and it is the mutant that should have
  caught Finding 2.
- **M09** (`:116-120`) — passes iff `four["…"]["answer"] == "NO"` and
  `four["A_HISTORICAL_C2_VERDICT"]["mutable"] is False`. Both are string/bool literals written by
  `c10_governance.py:124-144`. The mutant verifies that C10 wrote what C10 wrote.
- **M07** (`:96-100`) — half of the conjunction is
  `rule["F1"]["HAS_AN_EXPLICIT_LAPSE_CONDITION"]`, a hardcoded `True` at `c10_governance.py:40`.
  (The other half — the extracted quote — is real.)
- **M11** (`:136-141`) — two of three conjuncts are C10's own literals
  (`that_C8_decision_is_immutable: True` at `c10_governance.py:195`, and a substring test against
  C10's own prose). Only `c9scope["non_target_cells_evaluated"] == []` reads the tree.

M05 itself is now genuinely sound (it re-executes the real classifier across five planted branch
inputs — I checked `:65-87`), which makes the remaining tautologies harder to excuse rather than
easier: the campaign knew the pattern and did not sweep for it.

`MUTATION_CLASS = PASS` and "Mutations **14/14**" (`README.md:84`) overstate the coverage achieved.

**To fix.** Re-derive every mutant predicate from the committed tree or from re-executed producer
logic, never from a field the campaign itself wrote; for M14 specifically, plant an unsourced
reviewer claim and require the ledger to emit `NOT_REPRODUCED`.

---

### 7. MAJOR — the permanence scan is one file and four regex alternatives; the gate predicate and the ledger statement are repo-wide

**Where.** `code/c10_governance.py:50-51`; `config/DECISION_GATE_C10.json:17`;
`evidence/governance/HANDOVER_FACT_VERIFICATION.json:85-87`;
`evidence/phase5/C10_GOVERNANCE.json:104, 111`; `README.md:50`.

```python
perm_hits = [l.strip() for l in txt.splitlines()
             if re.search(r"immutab|forever|never be changed|all future successors", l, re.I)]
```

`txt` is `C2_ADJUDICATION.md` **only**. But:

- the gate predicate `C2_RULE_GLOBAL_BINDING` (`DECISION_GATE_C10.json:17`) reads *"**some committed
  artifact** asserts the floor binds all future successors immutably"* — repo-wide;
- the ledger statement (`:85`) reads *"**no committed artifact** claims the floor is immutable for
  all future successors"* — repo-wide, while its own `source` field says `C2_ADJUDICATION.md`.

So the gate's negative-classification predicate is never tested at the scope it declares. The regex
is also narrow: "permanently", "in perpetuity", "binding on all successors", "cannot be replaced",
"unconditional", "standing rule" would all pass through.

I checked by hand: `permanent` occurs at `C2_ADJUDICATION.md:461, 484, 508` and every occurrence is
about **cells/adoptions**, not the rule — `permanence_finding` is substantively correct. But the
finding is correct by inspection, not by the scan that is cited for it, and the scan's scope does not
match the claim built on it.

**To fix.** Run the scan over every committed artifact in `level4/closure_proofs/`, widen the
alternation, and either narrow the ledger statement to the single file or widen the scan to match it.

---

### 8. MAJOR — C10 imports C8's cell-306 numbers without the caveat C8's own adjudicator attached to them

**Where.** `evidence/phase5/C10_GOVERNANCE.json:55, 57`; `code/c10_governance.py:163, 167-180`.

C10 publishes `uniform_A_margin = 1.1714309154998508` and
`tightening_to_be_ADOPTABLE_under_the_inherited_floor = 1.0670710354836621` for cell 306, taken
straight from `C8_ADOPTION.json`. `ADJUDICATION_C8.md:124-132` flags exactly these:

> **The margin is the most favourable of three, unreconciled.** C8 reports 1.171431 (C5-T clause);
> C3_BLOCKER publishes `uniform_A_margin = 1.1554876238748288` (frozen clause) … C2 §K's own
> application table gives 1.1277 for the adopted supply … The corresponding requirements are
> **1.067071 / 1.081806 / 1.108452**.

I confirmed the three values exist: `C2_ADJUDICATION.md:476` gives 1.1277, `:497` quotes 1.1555,
`C8_ADOPTION.json` gives 1.171431. C10 carries the most favourable of the three, states no supply for
it, offers no reconciliation, and does not mention that its source was adjudicated as unreconciled.
C10 is a provenance campaign: catching a number that three committed artifacts disagree about is
squarely in scope, and C10 read the very document that flags it (it quotes §K four times).

Note this does not change any verdict — 306 fails F2 under all three — but it is the headline number
in `Q2_phase11_cell306`.

**To fix.** Record all three margins with their clause/supply, cite `ADJUDICATION_C8.md:124-132`, and
state which one `Q2_phase11_cell306` uses and why.

---

### 9. MAJOR — the AST comparison covers 209 of 270 lines; the method claim overstates what it partitions

**Where.** `code/c10_archaeology.py:33-43, 187-188`;
`evidence/phase1/C10_ARCHAEOLOGY.json:9` (`method`);
`evidence/governance/HANDOVER_FACT_VERIFICATION.json:37`; `README.md:21-24`.

`units()` collects only module-level `FunctionDef`, `AsyncFunctionDef`, `ClassDef` and `Assign`
nodes. I parsed the HEAD blob and measured what that leaves out: **61 of 270 lines are in no unit at
all** — the module docstring, all twelve `import`/`from` statements, the module-level
`if "numpy" not in sys.modules:` block at lines **37-39** (which sets `OMP_NUM_THREADS`,
`OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`, `NUMEXPR_NUM_THREADS` and `K1_THREADS_PINNED`), and the
`if __name__` block. `AnnAssign` targets and decorator lists are likewise invisible.

The consequence is a soundness gap in the classifier, not a cosmetic one: a change confined to those
61 lines produces `changed == []` and therefore class **`A_NO_DEFECT`**
(`c10_archaeology.py:152-155`) — "no defect" declared over a diff the comparison never looked at. The
thread-pinning block is the one C9 identified as determinism-relevant
(`C9_TOOLCHAIN.json:131`: BLAS participates in the result), so it is precisely the region where an
invisible change would matter most.

`method` (`:9`) reads *"every top-level function, class and constant is extracted and compared"* —
true as written but presented as if it partitioned the file; `README.md:21-24` and the ledger entry
(`:37`, *"every build-path unit is identical"*) are read by any reasonable reader as "the whole build
path was compared". Nothing asserts that the union of units covers the file.

**To fix.** Assert that the extracted units cover every line of both blobs, or add a residual
"MODULE_LEVEL" unit holding everything outside the recognised node types, and re-run the
classification.

---

### 10. MAJOR — the Campaign A precedent is stated as quoted fact; the quote is `null` and the extraction silently failed

**Where.** `code/c10_governance.py:151`; `evidence/phase5/C10_GOVERNANCE.json:142`; `README.md:51-52`.

```python
"quote": quote(r"the programme's own precedent \(Campaign A's adjudication", 300),
```

The source text (`C2_ADJUDICATION.md:455-456`) wraps between "Campaign A's" and "adjudication", so
the literal-space regex does not match. I reproduced this: the pattern returns `None`; with `\s+` it
matches. `C10_GOVERNANCE.json:142` therefore carries `"quote": null`, and `quote()`
(`c10_governance.py:23-25`) returns `None` without raising or flagging.

`README.md:51-52` nevertheless lists this as one of six grounds for Q2: *"**Precedent**: the same
document records that Campaign A adopted cells 11–44 on a valid enclosure plus a frozen K5-B pass,
with *no* robustness requirement."* The claim **is true** (I verified it at `C2_ADJUDICATION.md:455-456`),
but C10's evidence contains no support for it, nothing detected the null, and it is the **only** one
of the six README grounds with **no entry in the fact-verification ledger at all**. An unsupported
transcription presented as a quoted finding is, again, C2 Finding J-1's failure class.

**To fix.** Make `quote()` raise or record `NOT_FOUND` on a miss; fix the regex; add a ledger entry
for the precedent ground.

---

### 11. MINOR — the decision gate is never applied; no artifact records a final class

**Where.** `config/DECISION_GATE_C10.json:22-30`; all evidence files.

The gate defines classes P1–P6 with a combination rule (*"P5 may be carried TOGETHER with
P1/P2/P3"*). `grep` for `FINAL_CLASS`, `final_class`, `"P1"`–`"P6"` across the namespace returns
nothing outside the gate itself. On the evidence, C10 lands in **P2 + P5**
(PROVENANCE_CLEAN + SUCCESSOR_RULE_ALLOWED, carried with GOVERNANCE_BRIDGE_REQUIRED), but the
campaign never says so, and an adjudicator must derive it. A gate that is frozen and then not
evaluated is decoration.

**To fix.** Emit the evaluated predicates and the resulting class into the evidence.

---

### 12. MINOR — the N9 detector is unsound in ways the README's own description denies; the conclusion is right anyway

**Where.** `code/c10_governance.py:73-106`;
`evidence/phase5/C10_GOVERNANCE.json:70-99`; `README.md:79-81`.

`README.md:80-81` says the fix *"reports **AMBIGUOUS** rather than voting."* It does not. The
`CONDITIONAL` filter at `:90-91` **discards** any segment containing `lapses when|when N9 is
closed|if N9|ever closed|until N9|once N9` before either assertion regex is tried; `AMBIGUOUS` is
reached only if both kinds survive the filter (`:99-100`). A document asserting "N9 is now closed" in
a sentence that happened to contain "once N9" would be dropped silently, not flagged. Discarding is
a vote.

Three further limits: the scan reads only `*.md` (JSON evidence is invisible); it covers only
`p5y_k5_tail_{c2…c9}` and so misses `p5y_k5_tail_operator_registry` (C1, where the N-notes
originate), `p5y_k5_m5_tail_closure` (Campaign A) and every other namespace; and because `r"N9[^.\n]{0,140}"`
stops at a newline, it **fails to detect the adjudication's own** `C2_ADJUDICATION.md:432-433`
("remains open") — the single most authoritative statement of N9's status in the programme.

Relatedly, `README.md:58` reports *"6 explicit assertions across **C2–C8**"*. The evidence
(`C10_GOVERNANCE.json:83-98`) shows the hits come from `c2_closure` (1) and `c3_closure` (3) only;
`c4`–`c9` are all empty. The README overstates the breadth of its own gating fact.

**This does not change the answer.** I verified N9 is OPEN by reading
`OPEN_NOTES_DISPOSITION_C2.md:78-81` and `ADJUDICATION_C8.md:115-123` directly. But the finding is
established by my reading, not by C10's scan, and the scan is weaker than the README describes it.

**To fix.** Classify rather than discard conditional segments; scan `*.json` too; widen the namespace
set to all of `level4/closure_proofs`; match across newlines; and correct `README.md:58` to name the
two namespaces the hits actually come from.

---

### 13. MINOR — check `B0_16` contains a tautology

**Where.** `code/c10_archaeology.py:117-118`.

```python
chk(16, "C10 contacted no remote host", not any(
    t in (C.NS / "code").as_posix() for t in ()) and not C.git_grep(...))
```

`for t in ()` iterates an empty tuple, so `any(...)` is always `False` and `not any(...)` is always
`True`. The first conjunct is dead. The second (the `rebaseguard-(aws|vultr)` grep) is real, so the
check still has content, but the residue is the same tautology pattern as M05/M14.

**To fix.** Delete the dead conjunct or supply the intended token list.

---

### 14. MINOR — the README's provenance taxonomy names a class the classifier does not define

**Where.** `README.md:31-33`; `code/c10_archaeology.py:152-155`.

`README.md:31-33` reads: *"Not `E` (the binding resolves), not `D` (no scientific logic changed), not
`B` (the edits are functional, not cosmetic)."* The classifier emits only `E_BROKEN_BINDING`,
`D_SCIENTIFIC_PRODUCER_DRIFT`, `A_NO_DEFECT`, `C_GOVERNANCE_DRIFT`. **There is no class B.** The one
class the README does *not* discuss (`A`) is the one that actually exists and is reachable — and is
the class Finding 9 shows can be reached wrongly. I grepped: this A/B/C/D/E taxonomy appears nowhere
else in the repository, so there is no external definition of `B` either.

**To fix.** Align the README's elimination argument with the classifier's actual class set, and
explain why `A_NO_DEFECT` was excluded.

---

### 15. MINOR — the adoption/closure thresholds are infima and are used with `>=`

**Where.** `code/c10_governance.py:183-184`; `code/c10_factcheck.py:85-86`; `README.md:63-64`.

`ADJUDICATION_C8.md:134-137` states explicitly: *"1.067071 is an **infimum**. At exactly that factor
the uniform-A margin is exactly 1.25 and Γ = 0 at ×1.25, so F2's strict inequality fails. The same
applies to 1.096007 / 1.438423 / 1.818354 … 'needs a real 1.067071× tightening' should read
'> 1.067071×'."*

C10 uses `best_alpha_tight >= need_close` and `>= need_adopt`, and `README.md:63` writes *"up to
1.137406× against 1.096007× needed"* — the exact phrasing the adjudicator asked to be corrected. With
1.137406 > 1.096007 strictly, no conclusion changes here, but the convention is carried forward
uncorrected into a document whose whole subject is the floor.

**To fix.** Use strict `>` and write the thresholds as `> x`.

---

### 16. MINOR — `best_alpha_tightening` is a max over all projection rows, including inadmissible ones

**Where.** `code/c10_governance.py:165`; `code/c10_factcheck.py:82`.

```python
best_alpha_tight = max(p["tightening"] for p in lever["projection"])
```

`C9_ALPHA_LEVER.json`'s projection contains rows with `Gamma_negative_projected: false` and
`meets_closure: false` (α = 109/100 and 11/10). Comparing an unconditional max against the closure
threshold is a category error: a tightening from a row that does not close is not evidence that α can
close. I checked the data — the max (1.1374057, at the `alpha_min` boundary row) happens to have
`meets_closure: true`, and the max restricted to closing rows is the same value — so **the published
number is correct**, but by luck. C9 already computes `meets_closure` per row and C10 ignores it.

Separately, `README.md:63` and `C10_GOVERNANCE.json:6` present 1.137406 with the hedge "in
projection" but without C9's own label, `COUNTERFACTUAL_PROJECTION -- not certified evidence`, or its
four undischarged assumptions (`C9_ALPHA_LEVER.json.assumptions_that_must_be_DISCHARGED_BY_EXECUTION`).
M12 asserts the label is carried; it is carried in the field *name* only.

**To fix.** Filter to `meets_closure` / `Gamma_negative_projected` rows; carry C9's label verbatim
alongside the figure in the README.

---

### 17. MINOR — M12's detector has an unintended boolean precedence

**Where.** `code/c10_mutations.py:145-148`.

`A and B or C` parses as `(A and B) or C`, so the `COUNTERFACTUAL` label check (`A`) can be bypassed
by `C` alone. I probed it: `C` is currently `False` ("projection" is present in
`Q2_consequence_cases` but "projected" is not), so the label check is load-bearing **today** and the
mutant is currently sound. It is one word of prose away from becoming vacuous.

**To fix.** Parenthesise.

---

### 18. OBSERVATION — extracted quotes are fixed-width character windows and run into unrelated text

**Where.** `code/c10_governance.py:23-25`; `evidence/phase5/C10_GOVERNANCE.json:63, 101, 108, 112`.

`quote()` returns `txt[m.start() : m.start()+span]`, so the stored quotes end mid-sentence and absorb
following material. `F1.lapse_quote` (`:63`) runs past the lapse condition into the **definition of
F2**; `prospectivity_quote` (`:112`) and `explicitly_does_not_reopen` (`:108`) both trail into the
floor's blockquote header; the replacement quote (`:101`) trails into the second and third discharge
bullets. Every one I checked is *faithful* — I verified all four against
`C2_ADJUDICATION.md:422-423, 432-433, 501-506` — but a quote that ends mid-word makes independent
verification harder than it needs to be, and in the case of `:63` it visually merges two distinct
rules.

**To fix.** Terminate quotes at a sentence or blockquote boundary.

---

### 19. OBSERVATION — the gate is committed in the same commit as the evidence it classifies

**Where.** `config/DECISION_GATE_C10.json:4-10`; git history.

`DECISION_GATE_C10.json` first appears in `d2166f03`, the **same commit** as
`evidence/phase5/C10_GOVERNANCE.json`, and after `d5513b12` which carries the archaeology. There is
therefore no independent freeze point for the gate at all. The gate discloses this itself (`:5`,
*"Frozen AFTER the archaeology and the governance reconstruction, BEFORE adjudication. C10 does not
claim blindness"*), which is honest and is why this is an observation rather than a finding. It
interacts with Finding 5's vacuous "predates the adjudication and is unchanged" ledger entry: there
is no commit-order fact for that entry to have checked.

---

### 20. OBSERVATION — what this review could not settle

- Whether `REGISTRY_C2.json`'s recorded `code_sha256` was in fact **written by a run of** `build()`
  at `e71378a0`, as opposed to transcribed. The hash matches the blob at that commit, which is
  consistent with a genuine build and is the strongest available evidence, but it is not proof, and
  no run log or host record exists (that is N10). C10 does not claim more than this; neither do I.
- Whether the programme's *intent* matches C10's governance reading. C10's own
  `WHAT_THIS_CANNOT_VERIFY` (`HANDOVER_FACT_VERIFICATION.json:3`) says this plainly and the
  `claim_kind` tagging is a genuine and well-judged piece of discipline — it is the best thing in the
  campaign and it is what allowed me to isolate Findings 1 and 2 quickly.

---

## Disposition

Both answers are, in substance, correct, and I verified each independently: the REGISTRY_C2 pin is a
resolved build-time record and not a broken binding; a successor may freeze a different prospective
adoption rule; N9 is open; F1 is invariant under α; scope discipline is clean; every published number
reconciles.

What blocks adjudication is not the conclusions but the support under them. Finding 1 means the
campaign's single load-bearing governance answer rests on a quote it over-reads while the controlling
passage — which imposes a precondition C10's conclusion omits — is never cited; a successor following
C10's README would repeat the error C8's adjudicator already found. Finding 2 means the Q1 result is
published as original when it was already in `REVIEW_C9_STOP.md`, and is accompanied by a
characterisation of C9 that C9's committed text does not support. Findings 3–6 mean the machinery
built to catch precisely these failures — the detectors, the ledger, the mutation suite — did not
run, contradicted itself, or checked literals against themselves. Each is fixable by citing text and
re-running producers; none requires new science, new compute or a host.

READY_TO_ADJUDICATE or NOT_READY:

NOT_READY
