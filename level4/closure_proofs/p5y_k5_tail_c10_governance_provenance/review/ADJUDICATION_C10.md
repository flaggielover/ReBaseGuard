# Final independent adjudication — C10 (C2 provenance repair and prospective adoption governance audit)

Adjudicator: fresh context, no prior involvement in C2–C10.
Worktree: `/Users/suzhe/ReBaseGuard-k5c10`, branch `p5y-k5-tail-c10-governance-provenance`, HEAD
`7f255f3d` ("review NOT_READY; both CRITICALs repaired, gate now applied").
Reviewed HEAD was `b10cdc7d`; the repair is the single commit `b10cdc7d..7f255f3d`.

**Method.** I read `REVIEW_C10_GOVERNANCE.md`, `README.md`, `config/DECISION_GATE_C10.json`, all four
evidence artifacts and all five `code/*.py` modules; I read the cited source documents myself
(`C2_ADJUDICATION.md`, `REVIEW_C9_STOP.md`, `C9_TOOLCHAIN.json`, `ADJUDICATION_C8.md`,
`c2_refined_registry.py`, `C9_ALPHA_LEVER.json`, `C3_BLOCKER.json`); and I re-executed C10's
producers in a scratchpad with `c10_common.write_evidence` monkey-patched to a capture stub, so **no
evidence file in the tree was rewritten**. I modified no file except this report. No AWS, no Vultr,
no SSH, no installs, no numpy/scipy/flint. `PYTHONINTMAXSTRDIGITS=0`.

I checked the code and the committed artifacts, not the commit message. Where the two disagree, I
report the artifacts.

---

## Executive finding

Both of C10's substantive answers are **correct**, and I verified each independently. The decision
gate is now **applied**, and the applied class **P2 + P5 is correct** under the gate's own
predicates.

But the claim under test — commit `7f255f3d`'s "**both CRITICALs repaired**" — is **not accurate as
committed**. Of the 2 CRITICAL and 8 MAJOR findings, **2 landed, 6 landed partially, 2 did not land
at all**, and the repair **introduced a blocking new defect**: `c10_governance.py` no longer runs to
completion. In three places the repair *records* a fix that provably does not exist:

1. `C10_ARCHAEOLOGY.json:13` and commit `7f255f3d` state the uncovered AST residue "is compared
   directly so a change there cannot slip through as `A_NO_DEFECT`". I planted residue-only
   mutations (the `K1_THREADS_PINNED` assignment inside the module-level `if`, and an `import` line)
   and the committed classifier expression returns **`A_NO_DEFECT`** in both cases. The flag is
   computed and published; the classifier never reads it.
2. `c10_mutations.py:178-191` says M14 "is re-run here with a deliberately false claim injected, and
   must record `NOT_REPRODUCED`". Nothing is re-run. A dict literal is constructed two lines above
   and compared to its own value. I planted an explicitly unverified absorbed claim in the ledger;
   M14 still reports **DETECTED**.
3. `C10_GOVERNANCE.json` simultaneously withdraws the cell-306 over-read (`:110`, "that was an
   over-read and is withdrawn") and, in `Q2_ANSWER` (`:2`), still rests Q2 on that same sentence with
   the word "**decisively**". One JSON object states a proposition and its withdrawal — structurally
   the identical defect Finding 3 condemned.

None of this changes any verdict, authorizes anything, or touches science. All of it is
evidence-layer work requiring zero compute. That is why the verdict below is conditional rather than
a rejection.

---

## Finding-by-finding disposition

| # | Sev | Finding (short) | Status | Evidence I checked |
|---|---|---|---|---|
| 1 | CRITICAL | Q2 omits C2 Condition 1; over-reads the cell-306 bullet; drops the binding precondition | **PARTIAL** | Condition 1 (`C2_ADJUDICATION.md:536-537`) is now quoted as `PRIMARY_AUTHORITY_condition_1` in `C10_GOVERNANCE.json:100-104` and in `README.md:63-71`, with `BINDING_PRECONDITION_ON_ANY_SUCCESSOR`; the cell-306 bullet is demoted to `corroborating_only_306_replacement_bullet` with a `CORRECTED_READING`; M07 now tests both. **But `Q2_ANSWER` (`C10_GOVERNANCE.json:2`) is unchanged**: it still says "— **decisively** — the same adjudication directs … 'a successor should freeze a replacement floor …'", names neither Condition 1 nor the precondition, and contradicts `:110` in the same object. `Q2_phase6_four_concepts.D_SUCCESSOR_GOVERNANCE_ADOPTION` (`:137-140`) is unchanged — the precondition was not propagated. `README.md:81-83` conclusion box still omits it. **No ledger entry for Condition 1** (`grep "recomputing any magnitude" HANDOVER_FACT_VERIFICATION.json` → 0); ledger entry 7 still carries the withdrawn bullet as the sole replacement authority. |
| 2 | CRITICAL | Q1 is an uncited reproduction of `REVIEW_C9_STOP.md`; the error attributed to C9 is false | **PARTIAL** | `README.md:12-17` now cites `REVIEW_C9_STOP.md`, marks C10's contribution as the measurement, and states the mis-attribution against C10. **But `C10_ARCHAEOLOGY.json:4` (`Q1_ANSWER`) still ends "C9 read a build-time self-hash as if it were a live integrity constraint"**, and `c10_archaeology.py:281-282` still writes it. `grep -rn "REVIEW_C9_STOP"` over the namespace hits **`README.md` only** — no evidence field, no ledger entry, no line citation. Item (c) half-landed: `README.md:44-46` carries the byte-reproducibility consequence; the numpy/BLAS non-determinism (`C9_TOOLCHAIN.json:131`, `determinism_claim_CORRECTED`) appears **nowhere** in C10 (`grep -rn "BLAS"` → only the OMP/OPENBLAS token inside the residue note). |
| 3 | MAJOR | broken taboo-enforcement detector; JSON stated a fact and its negation | **LANDED** | `c10_archaeology.py:179` now matches `!=\s*TABOO_SHA256\s*:\s*\n\s*raise`. I read `c2_refined_registry.py:58-68`: `_import()` line 63 is `if sha(...) != TABOO_SHA256:` followed by `raise SystemExit`. `C10_ARCHAEOLOGY.json:85-86` now publishes `taboo_dependency_enforced_at_runtime: true`, `taboo_enforcement_site_line: 63`, consistent with its sibling prose and with `README.md:38-39`. Re-ran the producer: reproduces. |
| 4 | MAJOR | `any_consumer_compares_it_to_HEAD` was a hardcoded literal | **LANDED (weak detector)** | `c10_archaeology.py:192-210` now enumerates all committed `*.py`. I reproduced it independently: **1461** files, **5** mentions — `c10_archaeology.py`, `c10_factcheck.py`, `c2_refined_registry.py` (the writer), `c9_factcheck.py`, `c9_toolchain.py` — exactly as `C10_ARCHAEOLOGY.json:77-83` publishes, each dispositioned. The substantive ask is met and the conclusion is true. Residual: the boolean is derived from a same-line-ish regex, not from the dispositioned list, and it has near-zero sensitivity — I planted two ordinary enforcing consumers (compare then `raise SystemExit`; compare then `sys.exit(1)`) and **neither is detected**. The key is also named `..._compares_it_to_HEAD` while the variable and predicate are `any_consumer_enforces`. |
| 5 | MAJOR | ledger declares methods it did not execute; two vacuous entries | **PARTIAL** | Fixed: the AST entry's method string is now honest (`c10_factcheck.py:47`, "checks the RECORDED result, not a fresh parse"); the F1 entry is now real (`:92-99` reads C3's own `G_is_registry_independent` from `C3_BLOCKER.json`); the gate entry (`:116-120`) no longer claims "unchanged" and records `gate_added_in`. **Not fixed:** `:42` still declares "counted commits after the registry commit" while reading `q1["registry_rebuilt_since"]`; `:52` still declares "recomputed sha256" while reading `q1["taboo_pin_still_matches"]`. Two of the three misstatements the review tabulated survive. Nothing was made independently recomputable inside `c10_factcheck.py`, as the fix asked. **New defect:** the gate entry's predicate includes `not (NS/"review"/"ADJUDICATION_C10.md").exists()` — writing *this file* flips that entry to `NOT_REPRODUCED` and `FACT_CHECK_CLASS` to `REFUSE` on any post-adjudication re-run. A ledger that cannot survive its own adjudication is not a ledger. |
| 6 | MAJOR | mutation suite contains the tautology class it claims to have removed | **PARTIAL** | M09 genuinely repaired (`c10_mutations.py:126-137` now reads the source text: "does not reopen, impeach or revisit any cell already adopted" and "governs future adoptions", plus C2 tree identity). M05 was already sound. **M14 is not repaired**: its decisive conjunct `probe["disposition"] == "REVIEW_SOURCED_UNVERIFIED"` compares a literal defined at `:188-189` to itself, and the surrounding comment describes an injection that does not occur. Probe: with an ledger entry reading `verification_method: "none performed, absorbed as written" / disposition: ABSORBED` planted, M14 still returns **DETECTED**. This is the mutant that should have caught Finding 2, and Finding 2's residue is still in the committed evidence while M14 passes. **M07** still conjoins the hardcoded `HAS_AN_EXPLICIT_LAPSE_CONDITION: True` (`c10_governance.py:43`) and two substring tests against C10's own prose. **M11** unchanged: `that_C8_decision_is_immutable is True` is C10's literal at `c10_governance.py:224`. "Mutations 14/14" still overstates coverage. |
| 7 | MAJOR | permanence scan is one file and four alternatives; gate predicate and ledger statement are repo-wide | **NOT LANDED** | `c10_governance.py:53-54` is byte-unchanged: same `txt` (= `C2_ADJUDICATION.md` only), same `immutab\|forever\|never be changed\|all future successors`. `DECISION_GATE_C10.json:17` still reads "**some committed artifact**"; ledger `:98` still reads "**no committed artifact**". Repo-wide, **280** files under `level4/closure_proofs/` contain that language. **Aggravated by the repair**: `any_claim_of_permanence == []` is now a conjunct of the applied `SUCCESSOR_RULE_ALLOWED` predicate (`c10_factcheck.py:128-130`), so the applied class P2 now rests on a predicate evaluated at a narrower scope than the gate declares. I checked the scope by hand across `p5y_k5_tail_*` and the substantive finding holds (every hit is about cells, verdicts, namespaces or maps, never the rule) — correct by my inspection, not by C10's scan. C10 also never surfaced the one committed artifact squarely on point, **`REVIEW_C9_STOP.md:286`, "the C2 gate is over-read as programme-wide immutability"**, which *supports* C10 and which a repo-wide scan would have returned. |
| 8 | MAJOR | C8's cell-306 margins imported without C8's adjudicator's caveat | **PARTIAL** | `README.md:100-102` adds a prose caveat. **The evidence does not**: `C10_GOVERNANCE.json:42-57` still publishes `uniform_A_margin: 1.1714309154998508` and `1.0670710354836621` bare, with no supply, no reconciliation, no alternate values and no citation. The review asked for all three margins with their clause/supply and a cite to `ADJUDICATION_C8.md:124-132`; none is present. I confirmed the three values exist (`C2_ADJUDICATION.md:476` → 1.1277; `:497` → 1.1555; `C8_ADOPTION.json` → 1.171431). No verdict moves — 306 fails F2 under all three. |
| 9 | MAJOR | AST comparison covers 209/270 lines; `A_NO_DEFECT` reachable over an unexamined diff | **NOT LANDED (instrumented, not fixed — and the artifact claims otherwise)** | `c10_archaeology.py:145-166` now measures coverage (209/270 current, 190/251 historical) and computes `uncovered_residue_identical`. I confirmed the real residue is identical between `e71378a0` and HEAD, so the published `true` is correct. **But the classifier at `:215-218` is unchanged** and reads only `bound`, `build_changed`, `changed`. Probe: mutating `os.environ["K1_THREADS_PINNED"] = "1"` → `"0"` (inside the module-level `if`, i.e. residue) gives `units_changed = []` → **`A_NO_DEFECT`**, with `uncovered_residue_identical = False` recorded and ignored. Same for an `import` line. The soundness gap is exactly as the review described it, and `C10_ARCHAEOLOGY.json:13` now asserts it is closed. M05 makes this worse: it *certifies* `classify([]) == "A_NO_DEFECT"` as correct behaviour. |
| 10 | MAJOR | Campaign A precedent stated as quoted fact; the quote was `null` | **PARTIAL** | `quote()` now uses `re.S` and normalises whitespace; `C10_GOVERNANCE.json:148` carries a real quote and I verified it against `C2_ADJUDICATION.md:455-456`. A `quote_was_None_in_the_first_pass_because` field documents the failure honestly. **Not fixed:** `quote()` (`c10_governance.py:23-28`) still returns `None` silently — no raise, no `NOT_FOUND` record — so the next wrapped pattern fails the same way; and the precedent ground still has **no entry in the fact-verification ledger**, the third item of the review's fix. |
| 11 | MINOR | the decision gate is never applied | **LANDED** | `c10_factcheck.py:122-145` evaluates three predicates and emits `APPLIED_DECISION_GATE` into `HANDOVER_FACT_VERIFICATION.json:2-14`. Class `["P2","P5"]` with the gate's own combination rule quoted. `DECISION_GATE_C10.json` itself is byte-unchanged by the repair commit — the gate was not tuned to the answer. See §"Is the applied class correct" below. |
| 12 | MINOR | N9 detector discards conditionals rather than classifying; scans `*.md` only, C2–C9 only; README overstates breadth | **NOT LANDED** | `c10_governance.py:114-115` still `continue`s on a `CONDITIONAL` hit; `AMBIGUOUS` (`:123`) still only fires if both kinds survive; still `rglob("*.md")` over `p5y_k5_tail_{c2…c9}` only; `README.md:112` still claims it "reports **AMBIGUOUS** rather than voting"; `README.md:85` still says "6 explicit assertions across **C2–C8**" while `C10_GOVERNANCE.json:83-98` shows the hits come from `c2_closure` (1) and `c3_closure` (3) only, with c4–c9 empty. Conclusion (N9 OPEN) is right — I verified it at `C2_ADJUDICATION.md:459, 549-551`, `OPEN_NOTES_DISPOSITION_C2.md:78-81` and `ADJUDICATION_C8.md:115-123`. |
| 13 | MINOR | `B0_16` contains a dead tautological conjunct | **NOT LANDED** | `c10_archaeology.py:118-119` still reads `not any(t in … for t in ())`. Byte-unchanged. |
| 14 | MINOR | README names a class `B` the classifier does not define | **NOT LANDED** | `README.md:48-49` still eliminates "not `B` (the edits are functional, not cosmetic)"; `c10_archaeology.py:215-218` still emits only `E/D/A/C`. `A_NO_DEFECT` — the reachable class Finding 9 shows can be reached wrongly — is still the one the README does not discuss. |
| 15 | MINOR | thresholds are infima but compared with `>=` | **NOT LANDED** | `c10_governance.py:212-213` still `>=`; `c10_factcheck.py:85-86` still `>=`; `README.md:90` still "up to 1.137406× against 1.096007× needed" — the exact phrasing `ADJUDICATION_C8.md:134-137` asked to be corrected. |
| 16 | MINOR | `best_alpha_tightening` is a max over inadmissible projection rows | **NOT LANDED** | `c10_governance.py:194` unchanged. I re-derived the projection: rows at 1.0786 and 1.0688 have `meets_closure: false`; the unconditional max 1.1374057041669792 coincides with the max over closing rows, so the published figure is right **by luck**. C9's own label `COUNTERFACTUAL_PROJECTION` is still carried in a field *name* only — `grep "COUNTERFACTUAL" README.md` → nothing, and C9's four undischarged assumptions appear nowhere. |
| 17 | MINOR | M12 `A and B or C` precedence | **NOT LANDED** | `c10_mutations.py:162-165` unchanged. Probe: A=True, B=True, C=False, so the label check is still load-bearing today and M12 is sound — one word of prose from vacuity, as the review said. |
| 18-20 | OBS | fixed-width quote windows; gate committed with the evidence; what the review could not settle | **carried** | `PRIMARY_AUTHORITY_condition_1.quote` (`:103`) runs past Condition 1 into Condition 2; `F1.lapse_quote` (`:63`) still merges into F2's definition. Gate still first appears in `d2166f03` alongside `C10_GOVERNANCE.json`; the gate discloses this itself (`:5`). |

### New defects introduced by the repair

| | Defect | Evidence |
|---|---|---|
| N1 | **`c10_governance.py` does not run.** `:319` prints `rule['adjudication_itself_directs_a_replacement']['quote']`, a key the repair renamed to `PRIMARY_AUTHORITY_condition_1`. I executed `main()`: it writes `C10_GOVERNANCE.json`, then raises `KeyError: 'adjudication_itself_directs_a_replacement'` and exits non-zero. One of C10's four producers cannot complete, so the campaign's evidence is **not reproducible end to end**. The dead `repl = quote(...)` at `:62` is the other half of the same half-finished rename. |
| N2 | `Q2_ANSWER` vs `corroborating_only_306_replacement_bullet.CORRECTED_READING` — a proposition and its withdrawal in one object; the defect class Finding 3 condemned, reintroduced in the campaign's headline field. |
| N3 | `C10_ARCHAEOLOGY.json:13` asserts a classifier property that is false (proved above). A false claim in committed evidence is worse than the omission it replaced. |
| N4 | `c10_mutations.py:178-191` comment describes an injection test that does not exist. |
| N5 | `c10_factcheck.py:119`'s gate entry is self-invalidating: the existence of this adjudication file forces `FACT_CHECK_CLASS = REFUSE` on re-run. |

### What survives attack

Verified independently and confirmed: Q1's arithmetic (`4ac24d9e1826…` at `e71378a0`; `629715c0afdf…`;
`0d1d8021a378…` = HEAD; registry added at `5a94568a`, one commit in its whole history →
`registry_rebuilt_since = 0`); the `main`/`verify` localisation; byte-identity of the five scientific
constants **and** of the module-level residue; the taboo pin `ced9422ca079…` still matching; N9 OPEN;
F1 invariant under α (C3's `G_is_registry_independent = true`); every README number reconciling with
`C8_ADOPTION.json` and `C9_ALPHA_LEVER.json`; `C10_MUTATIONS.json` and
`HANDOVER_FACT_VERIFICATION.json` reproducing to the exact committed `sha256`
(`69c7c4bb4b709178…`, `2f746128518e844b…`). Scope discipline is clean at the new HEAD: `git diff
fd3cb2d4..HEAD` touches 12 paths, **0 outside** the C10 namespace; no `COVERAGE_MAP_R6` anywhere; no
`"guard": "ALLOW"`/`"PERMIT"` anywhere; the C2 namespace tree at HEAD is `77ee62a4` = its published
head `ae4cbc2c`.

### Is the applied class correct?

**Yes — P2 + P5 is right, on facts I verified myself, notwithstanding the machinery.**

- `PROVENANCE_CLEAN` ("the hash resolves to a real commit of the producer AND no build-path unit
  differs between that commit and HEAD"): the hash resolves to `e71378a0`; build-path units are
  identical; and I additionally confirmed the uncovered residue — including the OMP/OPENBLAS/MKL
  thread-pinning block, the part of the "build path" the AST comparison does not see — is
  byte-identical between `e71378a0` and HEAD. **True.**
- `SUCCESSOR_RULE_ALLOWED`: the floor declares itself prospective (`C2_ADJUDICATION.md:422`);
  Condition 1 (`:536-537`) provides for replacement in terms; and I scanned the `p5y_k5_tail_*`
  namespaces by hand — no artifact asserts the *rule* binds all future successors immutably (every
  permanence hit is about cells, verdicts, namespaces or coverage maps), with
  `REVIEW_C9_STOP.md:286-298` affirmatively warning against the opposite reading. **True** — but
  established by my scan, not by C10's single-file one.
- `GOVERNANCE_BRIDGE_REQUIRED`: the replacement route the adjudication names is conditioned on
  closing N9, and N9 is open. **True.**
- `C2_RULE_GLOBAL_BINDING` is **never evaluated** by `c10_factcheck.py`, so P1 is excluded only by
  implication. I evaluated it: false. P1 does not apply; P3/P4/P6 do not apply.

---

## The 14 questions

**1. Is the REGISTRY_C2 hash mismatch explainable?**
Yes, completely, and it is not a defect. `REGISTRY_C2.json:code_sha256.c2_refined_registry` records
the *content* sha256 of `c2_refined_registry.py` as it stood at `e71378a0` (2026-09-20), the commit
at which the registry was built; the registry has exactly one commit in its history and was never
rebuilt. The producer was edited twice afterwards (`e9c230d3`, `2b045564`), and both edits are
confined to `verify()` and `main()`. The field is written inside `build()` as
`sha(HERE.read_bytes())` (`c2_refined_registry.py:177`) — a build-time self-record, not a live
constraint — and no committed consumer enforces it (5 of 1461 committed `.py` files mention it; all
are auditors or the producer). The dependency that *is* enforced at run time is `TABOO_SHA256` at
`c2_refined_registry.py:63`, which raises `SystemExit` on mismatch, and it still matches.
Two caveats C10 should carry and does not: the registry's output is **not** a pure function of its
source — `C9_TOOLCHAIN.json:131` records that the taboo candidate comes through numpy linear
algebra, so BLAS and architecture participate — and N10 (no build-host record) is open. The pin
records the **source**; nothing records the **stack**.

**2. Is historical C2 evidence still valid?**
Yes. The C2 namespace tree at HEAD is byte-identical to its published head (`77ee62a4` both sides),
the bound producer's entire build path and every scientific constant are unchanged, so the two later
edits cannot have touched the registry's content. Cell 305 remains PASS/ADOPTED and cell 306 remains
DO NOT ADOPT. The validity is the validity C2 always had — explicitly conditioned on N9 and N10,
both still open.

**3. Is r5 still valid?**
Yes, and it remains authoritative. `K5_COVERAGE_MAP_R5.json` (blob `f978eeb6`) reconstructs from its
per-cell verdicts; m=5 open is exactly {306, 307, 308, 309}; m=1/2/3 complete; cell 305 adopted. No
`COVERAGE_MAP_R6` exists on any local branch or in HEAD. C10 created none and changed no file
outside its own namespace. No r6 is licensed by anything in C10.

**4. Is C8 still valid?**
Yes, as adjudicated (ACCEPTED_WITH_CONDITIONS, `63a3f825`), and C10 does not disturb it. Two caveats
attach to C10's *use* of C8, not to C8: (i) C10 imports the most favourable of three unreconciled
cell-306 margins (1.171431 vs 1.1555 vs 1.1277, requirements 1.067071 / 1.081806 / 1.108452) and
records the caveat only in README prose, never in evidence; (ii) `ADJUDICATION_C8.md:134-137` asked
that these thresholds be written as strict infima (`> 1.067071×`), and C10 still uses `>=` and the
"up to … against … needed" phrasing. Neither moves any verdict: 306 fails F2 on all three.

**5. Is C9 still valid?**
Yes. C9's `HARD_STOP_BEFORE_AUTHORIZATION` stands, its fact check is PASS, it executed no
certification and evaluated no non-target cell. C10's attribution — "C9 read a build-time self-hash
as if it were a live integrity constraint" — is **false**, and I confirm it against C9's committed
text: `C9_TOOLCHAIN.json:132` records a true mismatch plus a reproducibility requirement ("any
execution must resolve which producer actually built the registry"), which C10's archaeology
*satisfies*. That correction has landed in C10's README and **not** in `C10_ARCHAEOLOGY.json:4` or
in the producer that writes it. Separately, C9's stop-review published the substance of Q1 first
(`REVIEW_C9_STOP.md:180-184`) and deserves the citation it now gets in the README only.

**6. Is the C2 1.25 adoption rule campaign-local or globally immutable?**
Neither. It is **line-scoped, prospective and expressly replaceable**. `C2_ADJUDICATION.md:422`: "It
is **prospective**: it governs future adoptions of K5 m = 5 tail cells from this verdict onward. It
does not reopen, impeach or revisit any cell already adopted…". Condition 1 (`:536-537`): "**The
floor above is now the standard** for K5 m = 5 tail adoptions, prospectively. A successor that
wishes to replace it must freeze the replacement **before** recomputing any magnitude." So: it binds
successors in the K5 m = 5 tail line by default (more than campaign-local), it is not a
programme-global invariant (Campaign A adopted cells 11–44 on enclosure + frozen K5-B with no
robustness requirement, `:455-456`), and it is not immutable — nothing in the corpus asserts
permanence of the *rule*; "permanent" attaches to adopted *cells*. `REVIEW_C9_STOP.md:286`
independently warns that reading the C2 gate as programme-wide immutability is an over-read. Note
also that ×1.25 is limb **F2** of the floor, not the floor: the floor is frozen-K5-B **and** (F1 or
F2), and F1 carries its own lapse condition tied to N9.

**7. May a future successor define a new prospective adoption rule?**
**Yes.**

**8. If yes, under what conditions?**
Cumulatively, all of:
- **(a) Freeze first.** The replacement must be frozen **before** the successor recomputes any
  magnitude (C2 Condition 1). This is the binding precondition C10's first pass omitted; it has
  teeth — `ADJUDICATION_C8.md:130-132` used exactly this to fault C8 for relaxing the floor's cost
  post hoc, and `REVIEW_C9_STOP.md:286-298` restates the same anti-tuning principle.
- **(b) Prospective only.** It may not be applied to any adoption already made, and may not
  re-adjudicate 305 or 306. Historical verdicts are immutable.
- **(c) It is an adoption gate, not a closure rule.** It cannot relax the frozen K5-B clause;
  scientific closure remains governed by K5-B.
- **(d) If it is the replacement the adjudication itself names** — agreement between two
  independent certifier implementations substituting for F1 — it is additionally conditioned on
  **closing N9**, which is open. Until N9 closes, F1 remains live by its own lapse clause and that
  route is unreachable.
- **(e) Programme form.** Frozen under the successor's own gate, qualified, independently reviewed
  and independently adjudicated, on the established freeze → qualify → review → adjudicate pattern.
- **(f) It must state its own prospectivity and scope**, as C2's did, so the next successor inherits
  a rule with the same replaceability discipline.

**9. Does that retroactively alter C2?**
**No.** C2's verdict (305 ADOPT, 306 DO NOT ADOPT, D_PARTIAL) is a past adjudication and is
immutable; the adjudication says in terms that it "does not reopen, impeach or revisit any cell
already adopted". A successor rule changes what a *future* adoption must satisfy. It does not change
what C2's floor required of adoptions made under it, and it does not reach back. Retroactive
alteration would mean re-adjudicating 305 or 306 under the new rule — which is forbidden.

**10. Could future cell-306 adoption be legal?**
Yes, in principle, by one of the three routes the adjudication itself names (`:501-506`): (i) a
second, independently written certifier reproducing the six operator constants for 306 — closing N9
— followed by a frozen replacement floor requiring two-implementation agreement in place of F1; or
(ii) further deterministic tightening bringing 306's uniform-A margin to ≥ 1.25; or (iii) a real
order-3 candidate under the R-stage's own frozen gate, after N1, N5 and N7. Independently, C8's
frozen rule 1 bound *C9's* selection, not every future campaign, so a future campaign that freezes
its own gate before its own result may prospectively target 306. As things stand 306 fails **both**
limbs (Γ under Lemma G = +0.019116; F2 fails on every published margin). **Nothing here is
authorized.** C10 does not authorize it and neither does this adjudication.

**11. Could future cell-307 adoption be legal after alpha closure?**
**Not under the inherited floor.** α can *close* 307 in projection — best projected tightening
1.137406× against 1.096007× needed — but adoption needs frozen-K5-B **and** (F1 or F2):
- **F2** needs 1.370009×; α's best projection (1.137406×) falls well short.
- **F1 is invariant under α.** F1 asks for Γ < 0 under a Lemma-G supply that does not depend on the
  Arb/FLINT registry — C3 records `G_is_registry_independent = true` — while α tightens that
  registry's own taboo supersolution. 307's Γ under Lemma G is +0.085118 and α cannot move it.
So α-closure yields a **closed-but-unadoptable** cell and no coverage-map change. Adoption would
become reachable only after N9 closes and a replacement floor is validly frozen, or under some other
validly frozen successor rule (conditions in Q8), or through a supply improvement that moves the
Lemma-G limb itself. Add the caveat C10 carries only in a field name: the α figure is C9's
`COUNTERFACTUAL_PROJECTION — not certified evidence`, with four assumptions undischarged by
execution.

**12. Must a governance bridge exist before certification?**
For **adoption**, yes — that is exactly what P5 records, and it is correct. No adoption of 306 or 307
is reachable until either N9 closes (which unlocks the named replacement route and simultaneously
lapses F1) or a successor validly freezes a different prospective rule first, per Q8. For
**certification/closure compute** the floor is not itself a bar — closure is governed by the frozen
K5-B clause — but on C10's own consequence table, and on the adjudication's "more margin is the
wrong instrument for the risk that is actually open", certifying ahead of the bridge buys a
closed-but-unadoptable cell. So: bridge before adoption, and bridge before compute is the rational
ordering. C10's guard is DENY throughout and authorizes neither; so does this adjudication.

**13. Is provisioning a certifying host justified now?**
**No — and neither C10 nor I may authorize it** (`DECISION_GATE_C10.json` forbidden conclusion 6;
`compute_boundary` all zeros; guard DENY). On the merits: the α purchase yields a
closed-but-unadoptable 307; the open risk is N9 — implementation independence — which margin does
not answer; and the α figure supporting the purchase is an uncertified counterfactual projection
with undischarged assumptions. If the programme ever does provision a host, the justified purchase
is the **second, independently written certifier** (which closes N9, bears on N10, and unlocks both
306 and 307), not an α ladder run. That is a decision for the user and the programme, not for this
campaign.

**14. What should the NEXT campaign do exactly?**
In this order, and the first item is the only one that is unconditionally authorized:

1. **C11 (zero-science, evidence-layer only) — discharge the conditions below.** Concretely: fix
   `c10_governance.py:319` (and remove the dead `repl` at `:62`) so the producer runs; rewrite
   `Q2_ANSWER` on Condition 1 with the freeze-before-recomputation precondition and delete the
   "decisively" over-read; propagate the precondition to
   `Q2_phase6_four_concepts.D_SUCCESSOR_GOVERNANCE_ADOPTION` and to the README conclusion box;
   rewrite `Q1_ANSWER` to drop the false C9 attribution, cite `REVIEW_C9_STOP.md:163-187` as prior
   art, and carry forward the numpy/BLAS non-determinism and N10; add ledger entries for Condition
   1, for the Campaign A precedent, and for the prior-art attribution; make the provenance
   classifier **consume** `uncovered_residue_identical` (or delete the claim that it does) and
   re-run; widen the permanence scan to `level4/closure_proofs/` with a wider alternation (or narrow
   the gate predicate and the ledger statement to the single file) and record
   `REVIEW_C9_STOP.md:286`; make M14 a genuine injection test and re-derive M07/M11 from the tree;
   parenthesise M12; filter the α projection to `meets_closure` rows and carry C9's
   `COUNTERFACTUAL_PROJECTION` label and its four assumptions verbatim; use strict `>` on the
   infima; publish all three cell-306 margins with their supplies and cite
   `ADJUDICATION_C8.md:124-132`; delete the `B0_16` dead conjunct; align the README's A/B/C/D/E
   taxonomy with the classifier's actual class set; make the gate ledger entry survive its own
   adjudication. Then have it independently reviewed and adjudicated again.
2. **Then, if the programme wants 306/307 reachable: freeze a successor adoption rule** under its
   own gate, **before recomputing any magnitude**, satisfying Q8(a)–(f), and put it through
   independent review and adjudication. This is a governance act and needs no compute.
3. **Only if the programme funds it, and only under an explicit user authorization: build the
   second, independently written certifier** of the six operator constants. That closes N9, bears on
   N10, and is the one purchase that unlocks both 306 and 307. It needs a host; neither C10 nor this
   adjudication authorizes provisioning one.
4. **Do not run the α ladder for 307 expecting an adoption.** It cannot produce one under the
   inherited floor.
5. **Keep r5 authoritative. No r6** unless and until an independent adjudicator hands over an
   adopting verdict with a non-empty adopted set.

---

## Conditions attached to this verdict

These are **blocking**. Until every one is discharged and independently re-verified, C10 may be
cited for its *reasoning* but its **evidence artifacts may not be cited as authority** by any
successor, and its README remains the only artifact in the namespace that states the corrected
readings.

1. **`c10_governance.py` must run to completion.** A campaign whose evidence cannot be regenerated
   has no reproducibility claim. (N1)
2. **`Q2_ANSWER` must be rewritten** on Condition 1 (`C2_ADJUDICATION.md:536-537`) carrying the
   freeze-before-recomputation precondition, and must stop calling the withdrawn cell-306 bullet
   decisive. The precondition must also appear in `D_SUCCESSOR_GOVERNANCE_ADOPTION`, in the README
   conclusion box, and as a ledger entry. (Finding 1)
3. **`Q1_ANSWER` must stop attributing to C9 an error C9 did not make**, and `REVIEW_C9_STOP.md`
   must be cited in the evidence and the ledger, not only in the README. (Finding 2)
4. **The residue claim must be made true or withdrawn.** Either the classifier consumes
   `uncovered_residue_identical`, or `C10_ARCHAEOLOGY.json:13` stops asserting that a residue change
   "cannot slip through as `A_NO_DEFECT`". (Finding 9 / N3)
5. **The permanence scan must match the scope of the gate predicate and the ledger statement it
   feeds** — widen the scan, or narrow both statements. It is now load-bearing for the applied
   class. (Finding 7)
6. **M14 must actually test what it names**, and its comment must describe what it does. M07 and M11
   must stop conjoining C10's own literals. (Finding 6 / N4)
7. **The two remaining misstated `verification_method` strings must be corrected**, and the gate
   ledger entry must survive the existence of this adjudication. (Finding 5 / N5)

The residual MINORs (12–18) are not blocking but should be swept in the same pass; leaving a known
tautology pattern in place after two rounds of being told about it is how this programme got here.

**Guard remains DENY. No scientific execution, no host provisioning, no operator certification, no
r6, no adoption of any cell is authorized by this adjudication. r5 remains authoritative. K5 remains
PARTIAL with m = 5 open at {306, 307, 308, 309}.**

---

ACCEPTED_WITH_CONDITIONS
