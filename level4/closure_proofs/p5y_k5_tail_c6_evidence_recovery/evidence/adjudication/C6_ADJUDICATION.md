# Independent fresh-context adjudication — P5Y / K5 Campaign C6

Adjudicator: fresh context, no prior involvement in C6 or its predecessors. Target
`/Users/suzhe/ReBaseGuard-k5c6`, branch `p5y-k5-tail-c6`, HEAD `b65ed607`, namespace
`level4/closure_proofs/p5y_k5_tail_c6_evidence_recovery`.

Read-only throughout. I created, edited, committed and deleted nothing in the working tree; all scratch output is
under the session scratchpad. **AWS was not contacted**: no `rebaseguard-aws` schema was loaded into this session
and no call was made. `rebaseguard-vultr` was used in read-only mode only (`status`, and `python3`/shell that open
files for reading, hash, stat and regex). I ran no kernel, no certifier, no `Order3Certifier`, no R-stage.

I treated every claim by the campaign **and by its forensic reviewer** as unproven until checked. I re-derived the
load-bearing numbers rather than accepting them, and I found errors in both.

---

## What I verified independently, before ruling

**Toolchain absence (load-bearing for C6's conclusion).** Local host, CPython 3.14.5: `numpy`, `flint`, `sympy`,
`mpmath`, `gmpy2` all `ModuleNotFoundError`. **And on the worker**: `find_spec` for `numpy`, `scipy`, `flint`,
`python_flint`, `mpmath`, `sympy`, `gmpy2` → all `None` on `rebaseguard-vultr-02`. `tc_producer` does
`from flint import ctx`, so no replay can even import on either host. C6's absence claim is true, and true of
more hosts than C6 checked (see Q8, N9).

**The external store.** From the host, read-only, re-running the manifest's own integrity check:
326 entries, **326 hash_ok, 0 mismatch, 93,093,045 bytes** — C6's figures exactly. Payload scan with a
**12-alternative** regex (`numerators|denominators|coeffs|coefficients|payload|cheb|poly|candidate|monomials|terms|series|bernstein_coeffs`),
wider than C6's five and wider than the reviewer's eleven: **0 hits over all 326 records**. A structural walk of
all four tail records finds the **longest JSON array anywhere is 10**, at `/changes`. A degree-12 multivariate
candidate cannot hide in that. **The candidate polynomials were never serialized. This is true.**

**The four records.** sha256 and byte length match C6's inventory exactly
(`9c9da15b…`/279738, `28bacf0a…`/280035, `e8d7a412…`/280311, `95be4c65…`/280226). `production_run=false`,
`result_bearing=false`, `campaign=p5y_k1_cusum_aux5_successor`, `adjudicated=null`, `cell_index` matching,
`precision_bits=256`, `producer_manifest_hash=b55a2da1…` — in **all four**, as C6 now claims.

**Zero mutations.** `mtime == ctime == 1789537991.358989/.362989` (2026-09-16 05:53:11 UTC) on all four records;
nothing under `closure-r1` is newer than Sep 16 07:00. ctime equal to mtime rules out even a metadata touch, by
C6 or by me. C6's commits are 2026-09-22 03:37–03:41 UTC, six days later.

**Both broken upstream links reproduce.** `producer_manifest_hash = b55a2da1…` against committed
`producer_manifest_v3.json` at `611bd0a9…` — does not close. Manifest's
`composite_audit_sha256 = fa1d79b5…` against the committed audit `2ec4dcbb…` **and** the external audit
`2ec4dcbb…` — closes against neither. The committed and external audits **agree with each other**; the manifest
names a third value, and the manifest is the artifact carrying the 326 record hashes. The P3 cap is honest and,
as the reviewer said, under-states the problem.

**Binding independence.** `ADOPTED_TAIL_INPUTS.manifest_sha256 = 29ad1f9b…` = the sha256 of the committed export
manifest. It names its source. Correction 3's factual basis is confirmed: for 306–308 there is one root binding
plus one verified transcription, not two witnesses. 309's bytes are separately committed at `95be4c65…`.

**The frozen chain.** All **59** modules in C6's transitive closure are **git-tracked**, and every recorded
sha256 matches the file on disk. Likewise all 13 top-level entries. The determinism premise for A1 is materially
established (though not by C6's own derivation — see N6).

**The address is old.** `TCT_INPUTS_305…309` are committed with `mode = "replay_measurement"`,
`identity_gate = {fields_compared: 262, identical: true}`, `order3_fields_present: false`, `k1_record_sha256`
equal to the manifest's value for each cell, and `r/0/sup/{F,D,H}` present **at exact rational precision**.

**C5's record.** `C5_ROUTE_LEDGER`: D4 carries `kill_kind: "DATA"` **and** `new_real_required: true` — the
inconsistency is real. A1's `kill_reason` states *"the payloads live in the external 90 MB K1 record store"*.
Condition 11(b) directs a successor to *"retrieve the K1 object candidate payloads from the external record
store"*. Condition 11(c) already says *"operator certification of `A0` on a host that has python-flint"*.
`adopted_cells = []`. r5 = `e2197051…`, no `_R6` map exists anywhere in the tree.

**C5's quantities.** `2.0561597034…%` (C5-T) and `5.535691483…%` (frozen) source-supply cut voiding the
cell-309 exclusion; `slack_percent_C5T = 0.9439874…`. Knockout **8** is labelled `knob = "sup F/D/H -> 0"` with
Γ = −0.103207 / −0.049231 / −0.000347, `status: DIAGNOSTIC`; knockout **1** is
`knob = "fG -> 0 (perfect order-3 surrogate)"` with −0.173324 / −0.128674 / −0.089759, `DIAGNOSTIC`;
the atom-constant floor rows are −0.0602347 / −0.0030136 / +0.0467753, `status: DIAGNOSTIC`. Baseline Γ at 309
moves +0.004661130 (frozen) → +0.001708896 (C5-T). **Every figure C6 quotes is correctly transcribed and is
correctly labelled DIAGNOSTIC and frozen-clause.**

**Reproduction.** I re-ran all three producers into the scratchpad. `C6_MISSING_EVIDENCE_GRAPH.json`,
`C6_PROVENANCE.json` and `C6_CLASSIFICATION.json` are **byte-identical** to the committed artifacts; `C6_B0_AUDIT.json`
differs only in `head` and `uncommitted_at_audit`, and reproduces **19/19 PASS**. No producer imports numpy, scipy,
flint or any certifier; none calls `prepare()`, `all_residuals()` or `Order3Certifier`.

**Gate integrity.** `git cat-file -p 59513c86:…/FEASIBILITY_GATES_C6.json | sha256` =
`03c5643335602071e5c6e5e558d20e39d0fc40e81f8d25d0ac00a93c94801fba` = the working tree. That commit adds exactly one
file. `C6_CLASSIFICATION.json` and `c6_classify.py` are absent at the freeze and appear in exactly one commit.

**The three refs are real.** `origin` is `https://github.com/flaggielover/ReBaseGuard.git`;
`git ls-remote --heads origin main` → `1cb45382…`; local `main` → `c123b9bb…`; the worker's HEAD → `c123b9bb…`.
The known scratch-clone `ls-remote` trap does **not** apply here. Repo counts: 607 commits today (603 + C6's four),
34 heads + 24 remotes = 58 branches, 36 tags — C6's "603 / 58 / 36" was accurate when scanned.

**D4, checked myself.** A sealed record has **466** distinct keys. `R_interval`, `D_interval`, `R2_interval`,
`M_R2`, `R_interval_mag`, `D_interval_mag` are present, per `m`, as independently certified outward-rational
enclosures. There is **no** joint, correlation, covariance or cross field relating R and D anywhere in the schema.

**E1's inputs, checked myself.** `p5y_k5_tail_operator_registry/evidence/registry_c1/` contains
`taboo_cell_30{5..9}`, `arl_cell_30{5..9}`, `taboo_block_30{5..9}`, all carrying `"numerators"`. E1's inputs are
committed for every tail cell.

### Findings of my own, not in the reviewer's report

* **N1 — a correction introduced a false statement.** `subdivision_depth` is **integer `0`, not `null`**. It lives
  at `/producer/runtime/subdivision_depth` and equals `0` in all four records. The reviewer reported it "nested and
  **null** in all four"; C6 copied that into `C6_MISSING_EVIDENCE_GRAPH.json` verbatim — *"the forensic reviewer
  located the key nested and NULL in all four"* — without checking it. B1's conclusion is unharmed (a depth of 0
  supports it at least as well as a null), but C6 now ships a false factual claim that arrived **through** a
  correction, on the reviewer's authority. This is exactly the handover failure mode of adopting a reviewer's
  output unverified.
* **N2 — correction 7 half-applied.** I measured `whole_cell_refinement` iterations at r = 0: **306 → 25**,
  307 → 24, 308 → 24, 309 → 24. The graph's corrected text is right. But `C6_CLASSIFICATION.json`'s B1 entry
  **still** reads *"whole_cell_refinement is a 24-iteration fixed point"*. Two C6 artifacts now disagree.
* **N3 — correction 6 half-applied.** The reviewer said explicitly *"Fix the wording in **both places**."* README
  and the graph's `was_it_ever_serialized` are fixed. `C6_CLASSIFICATION.json`'s A1 entry is **not**: it still
  carries `ever_serialized: false` and a `serialization_search` ending *"0 payload keys, and no candidate hash
  exists anywhere"*, unqualified, while `required_object` still includes *"and their suprema"* — which are
  committed.
* **N4 — the most consequential residual defect. A1's machine-readable class is still wrong.**
  `A1.C6_CLASSIFICATION = "HISTORICAL_REPLAY_REQUIRED"` sits beside A1's own prose stating the result *"has never
  been derived by anyone and still must be"*. By C6's own corrected reasoning A1 falls into **exactly the same
  gate-class gap as E1** — inputs present or exactly regenerable, new certification work required, toolchain-blocked
  — yet C6 recorded `GATE_CLASS_GAP` for E1 alone. A consumer reading the class field gets "replay"; a consumer
  reading the prose gets "never derived". The hazard the reviewer identified is fixed in prose and left standing in
  the field a machine reads.
* **N5 — B0_18's repair is a tautology.** `expected` is computed by the *identical* predicate over the *identical*
  source as `c5_ledger_inconsistency`, so the assertion cannot fail. The reviewer objected to a hard-coded `True`;
  C6 replaced it with a self-comparison. "19/19" still contains one check carrying no information.
* **N6 — correction 5's repaired artifact repeats the same pattern.** `transitive_chain()` returns
  `"all_committed": True if resolved else False` — committedness asserted from non-emptiness — and the 13-module
  dict sets `committed` from `Path.exists()`. Neither consults git. I verified the claim is **materially true**
  (all 59 tracked, all hashes matching), so the conclusion survives; the evidence for it is still unearned.
* **N7 — third instance.** `broken_upstream_links.manifest_to_audit.closes_against_committed` /
  `closes_against_external` / `external_audit_sha256`, and all four cells in
  `record_self_report.measured_for_all_four_open_cells`, are **hard-coded literals**, not computed. I verified every
  one is factually correct on the host. Correct but not derived.
* **N8 — the replacement for the "ONLY" overclaim under-enumerates.** C6 now names
  `p5y_k5_perron_deflated_resolvent/evidence/registry_r1` "and three PROBE.json files". `grep -rl '"numerators"'`
  returns **316** files under `p5y_k5_perron_deflated_resolvent` and **105** under `p5y_k5_tail_c2_closure`, among
  others. E1's substance is unaffected; another reviewer figure transcribed without verification.
* **N9 — no host in scope has the toolchain.** C6 says "absent on **this** host" and its ranking says E1 "needs
  only a flint host". I checked the programme's worker: `rebaseguard-vultr-02` also lacks flint, numpy, scipy,
  mpmath, sympy and gmpy2. AWS is forbidden. So within C6's and a C7's permitted reach **there is no certifying
  host at all**. C6 never checked this, and it makes A1 and E1 materially less actionable than the ranking presents.
* **N10 — the DIAGNOSTIC attribution is over-unified.** C5's `crosscheck_note` makes *scaled* rows DIAGNOSTIC;
  E1's row is DIAGNOSTIC for a different reason (it rests on C4's **uncertified Monte-Carlo** Λ). C6 attributes all
  three to the scaled-row mechanism. Immaterial to planning-only status; imprecise as provenance.
* **N11 — a second C5 ledger inconsistency goes unflagged.** C5's A1 carries `new_real_required: false`. C6's own
  corrected A1 finding contradicts it: the gain has never been derived and the frozen producer refuses to emit it.
  C6 repaired D4's inconsistency and left an equivalent one at A1 unremarked.

---

## 1. Which DATA-blocked routes were genuinely recoverable?

**None of the four.** This is a harder answer than C6 gives, and it follows from C6's own evidence.

* **A1, A3** — the required object is absent from every store. I confirmed 0/326 under a wider regex than either C6
  or the reviewer used, and 0/10 in git. It is *regenerable*, not recoverable, and C6 correctly refused to
  regenerate it (regeneration runs `Aux3Certifier.prepare()` + `all_residuals()`, which is not serialization-only,
  and cannot import on either host).
* **E1** — nothing was ever missing to recover. Its inputs have been committed all along (`registry_c1`,
  verified), and its object — a *better* operator tuple — never existed. "Recoverable" does not apply in either
  direction.
* **D4** — the object was never computed by anyone. I walked a 466-key record: two independently certified
  enclosures, nothing relating them. Nothing to recover.

What C6 *did* recover — the four open tail cells' sealed K1 records — was on **no route's critical path**, was
never classified as missing by C5, and is `NOT_LOAD_BEARING`. So the count of DATA-blocked routes unblocked by
recovery is **zero**, and C6 now says as much in its own erratum E3. The correct headline is not "the data was
there"; it is **"C5's DATA classification was wrong in four different ways, none of them fixable by fetching a
file."**

## 2. Which objects have P4/P5 provenance?

**None produced or recovered by C6.** All four recovered records are **P3**, with
`admissible_for_NEW_scientific_reuse: false`. I reproduced both failing links by raw bytes myself
(`producer_manifest_hash` ≠ committed manifest; `composite_audit_sha256` matches neither the committed nor the
external audit, which agree with each other). The gate's `no_inference_rule` was obeyed — nothing was upgraded.

Their standing is invoked **solely** through the gate's `already_adopted_exception`, and C6 states that basis every
time, as the gate requires: `basis_invoked: "ALREADY_ADOPTED …, NOT a C6 P4"`. That is correct handling. It also
means the standing belongs to the predecessors' adoption of those bytes (ADOPTED_TAIL_INPUTS, TCT_INPUTS, C2–C5
consumption), not to C6.

One further P3 blocker is correctly carried rather than guessed: `production_run = false` and
`result_bearing = false` in all four records (I confirmed all four). C6 records them verbatim, refuses to interpret
them, and names the refusal as a reason for the cap. That is the only reading the `no_inference_rule` permits.

**C6 fails its own gate's P4 floor on every object it recovered.** That is evidence the floor was not written to be
passed.

## 3. Which reconstructions are lossless?

**None was performed.** `RECONSTRUCTED_ADMISSIBLE` is used for nothing in C6, and I confirmed no producer performs
any transformation of scientific values.

Four **byte-level recoveries** occurred, and those are trivially lossless: sha256 equality with the bytes
`ADOPTED_TAIL_INPUTS` names, which I verified for all four cells against the committed manifest, the adopted
extract and `TCT_INPUTS.k1_record_sha256`. C6 correctly renamed this from `SCIENTIFICALLY_IDENTICAL` to
`BYTE_IDENTICAL_TO_ALREADY_ADOPTED_BYTES` and states the argument (same bytes ⇒ same address, bits and producer
semantics, each being a function of the bytes). The conclusion is sound and the framing is now the right way round.

The one reconstruction that *would* be lossless — regenerating the A1 candidates from the fully committed,
exact-rational 59-module closure — was correctly **not** run.

## 4. Which routes merely require historical replay?

**For their inputs: A1 and A3. For their gain: none.** The distinction is the whole substance of C6's corrected
finding and it must not be collapsed.

The *address* is genuinely old, and the proof is stronger than C6's: `TCT_INPUTS_305…309` record
`mode = "replay_measurement"` with `identity_gate.identical = true` over **262** fields and
`order3_fields_present: false`. The programme has already executed `Aux3Certifier.prepare()` at these cells and
proved the output identical to the sealed run.

But no route's *gain* is obtainable by replay (Q(b) below establishes why for A1). A3 additionally needs a theorem
that does not exist. E1 has nothing to replay at all. So "merely requires historical replay" is true of the
**materialization of A1's and A3's inputs** and of nothing else in C6's universe — and A1's class field still says
otherwise (N4).

## 5. Which routes require true new-real?

**D4 and B1**, both confirmed on evidence I re-derived myself.

* **D4** — `TRUE_NEW_REAL_REQUIRED`, reclassified from C5's `DATA`. I walked the 466-key schema: `R_interval`,
  `D_interval`, `R2_interval`, `M_R2` and the magnitudes are present per `m`; there is no joint, correlation,
  covariance or cross field anywhere. `existence: OBJECT_ONLY_HYPOTHESIZED`, `existence_proof: "none"` is exactly
  right, and C6 does not pretend the ceiling is known. **This is C6's cleanest work.**
* **B1** — `TRUE_NEW_REAL_REQUIRED` confirmed. Eight sub-structure tokens are 0 in all four records (I re-ran
  them), `whole_cell_refinement` is a per-`r` fixed point on the whole cell, and `subdivision_depth` exists as a
  schema slot that was **never filled** (value `0`, not `null` — N1). Restricting a whole-cell certificate to a
  sub-interval cannot tighten it, because its value *is* the whole-cell supremum. Sound.

**A1 and E1 require neither.** Their work is new certified work that the programme classifies zero-new-real, at no
new address — which is precisely the class the frozen gate does not have. **E2** requires a theorem.

## 6. Which recovered routes are scientifically load-bearing?

**None.** The conclusion is correct and I checked it on the call graph rather than on C6's method.

`c5_common.committed_inputs()` reads `ADOPTED_TAIL_INPUTS.json`, `cells.json`, `REGISTRY_C1.json`,
`REGISTRY_C2.json`; `cell_supply()` reads `TCT_INPUTS_{cell}.json`; the consumer computes
Γ from the derived committed extracts; and the A1 oracle is implemented by scaling `meas[...]["sup"][F|D|H]`,
i.e. the **TCT_INPUTS** values. No raw `aux5_CUSUM_*_256.json` is opened in the C5 path. Recovering the records
therefore adds no field the current K5-B clause consumes and cannot move any Γ.

C6's own method for this — one grep of one file for five substrings — is **inadequate**, and would have missed that
the loaded chain does contain a raw-record reader (`tail_forecast_r2.adopted_state` → `read_records`). C6 records
that failure against itself in erratum E3 while leaving the inadequate method in the artifact. The conclusion
survives on the call graph; C6 did not establish its own correct answer.

Saying `NOT_LOAD_BEARING` out loud, instead of dressing up four recovered files as a result, is the single most
creditable decision in the campaign.

## 7. Which C5 route classifications should change?

| route | C5 | C6 | I rule |
|---|---|---|---|
| A1 | `DATA` | `HISTORICAL_REPLAY_REQUIRED` | **Direction accepted, class REJECTED.** Not DATA — correct. But the route-level class must be the missing class, as for E1, not `HISTORICAL_REPLAY_REQUIRED` (N4). |
| A3 | `DATA` | `HISTORICAL_REPLAY_REQUIRED` | **Accepted for the inputs**, with C6's own limitation sentence, which A3 carries correctly. Doubly contingent; leverage unknown. |
| D4 | `DATA` (+ `new_real_required: true`) | `TRUE_NEW_REAL_REQUIRED` | **Accepted.** The inconsistency is real and the reclassification is right. |
| E1 | `DATA` | `GATE_CLASS_GAP__nearest_is_HISTORICAL_REPLAY_REQUIRED` | **Accepted**, including the withdrawal of "the strongest reclassification in C6". C5's ledger and Condition 11(c) already named the python-flint block; C6 changed the label, not the facts. |
| B1 | `NEW_REAL` | `TRUE_NEW_REAL_REQUIRED` | **Accepted**, now proven rather than asserted. |
| E2 | `RE_OPENED_LIVE` | `NOT_AN_EVIDENCE_PROBLEM` | **Accepted.** Analytic work, no recovery, and the only lever restoring the 309 margin. |

Two further changes C6 should have made and did not:

* **C5's A1 `new_real_required: false` must change** (N11) — C6's own finding contradicts it.
* **C5's A1 `kill_reason` and Condition 11(b) must be struck as falsified.** The text *"the payloads live in the
  external 90 MB K1 record store"* and the instruction to *"retrieve the K1 object candidate payloads from the
  external record store"* are both false of a store I re-scanned at 0/326 under a wider net. This is the single
  most valuable thing C6 did and it belongs in the successor's conditions, not only in an erratum.

## 8. Is there now a zero-new-real deterministic route worth a separate C7?

**Yes — but a different C7 from the one C6's ranking implies, and the ranking's premise is false.**

The zero-new-real candidates are **E1** and **A1**: both are operator/replay work the programme has consistently
classified `ZERO_NEW_REAL`, both evaluate no new scientific address, and both have inputs that are committed (E1) or
exactly regenerable from a 59-module closure I verified is entirely git-tracked (A1).

But C6's ranking says E1 "needs only a flint host" and A1 "needs a flint host", and **no such host exists in
scope** (N9): the local machine lacks the toolchain, `rebaseguard-vultr-02` lacks it too, and AWS is forbidden. A
C7 chartered on C6's ranking as written would open, discover it cannot import flint on either permitted host, and
close — reproducing C6's block at campaign cost. C6 never checked the worker.

Further, for A1 the toolchain is **not sufficient even with a host**: the frozen identity gate refuses the
non-identical output that A1's gain requires (Q(b)). A1 needs a host, *and* a producer protocol that permits a
non-identical sup, *and* an unknown quantity of slack in the certifier's sup routine against a **known** 2.0562%
(C5-T) requirement.

So a C7 is warranted, and its cheapest-first order is **not** C6's:

1. **E2** — needs no recovery, no toolchain and no host: a sharper *certified* lower bound on Λ₃₀₉. It is the only
   lever that restores the margin C5-T consumed (0.944% of critical `A0`), and it is pure analysis. It is the only
   item a C7 can start on today.
2. **Host provisioning** as an explicit, separately governed prerequisite — not a parenthesis inside a route entry.
3. **E1** once a governed flint host exists — zero-new-real, closes 307, barely closes 308, does not close 309
   (all DIAGNOSTIC, frozen-clause).
4. **A1** only after the protocol question is settled, since a faithful replay is provably worthless.

## 9. Is broader deterministic exhaustion established?

**NO.** Emphatically, and for two independent reasons.

C6 withholds it explicitly (`broader_deterministic_exhaustion_established: false`), the frozen gate forbids it
(*"evidence recovery alone can never establish it"*), and I confirmed independently that no exhaustion claim exists
anywhere in the namespace: `grep -rni "exhaust"` returns only prohibitions, the withheld-conclusions block and
`p5y_k5_tail_c5_exhaustion` as a path component. The token `DETERMINISTIC_TRANSPORT_FAMILY_EXHAUSTED` does not
appear at all.

The deeper reason is structural and C6 is right about it: evidence recovery cannot establish exhaustion, because
establishing exhaustion requires showing no route delivers the bound, whereas C6 showed only what evidence exists
for routes already enumerated. C6 in fact moves the programme *away* from exhaustion — it confirms two genuinely
open new-real routes (B1, D4) and leaves two zero-new-real routes (A1, E1) live but unexecuted.

One gap against C6: it does not carry C5's two exhaustion scope limits, which a successor reading C6's ranking will
need — C5-T's premise `x_lo > 0` **fails at cell 0**, and C5's exhaustion is of the **transport family only** and
*"may never be restated as deterministic exhaustion"*. C6 misstates neither, but a campaign whose output is a route
ranking should carry the scope sentences attached to the routes it ranks. Condition 6 below.

**K5 remains PARTIAL, m = 5 open at {306, 307, 308, 309}, r5 authoritative.**

## 10. Is the R-stage prerequisite satisfied?

**NO.** Withheld explicitly (`R_stage_prerequisite_satisfied: false`) and verified by me on four independent
grounds:

* `REAL_SCIENTIFIC_COMPUTE = DENY` appears in every C6 evidence file; `new_real_scientific_addresses_evaluated = 0`
  and `scientific_kernel_evaluations = 0` throughout.
* Those zeros are not merely asserted — they are **physically enforced**. Neither permitted host can import flint
  or numpy, so no kernel could have run even by accident.
* No authorization packet, launch notice, countersignature, amendment or slot-binding artifact exists anywhere in
  the namespace.
* `git diff 69bff424 HEAD --name-only` touches only paths under `p5y_k5_tail_c6_evidence_recovery`; C2/C3 seal
  manifests re-verify at 156 and 21 entries with 0 deviations.

C6 also correctly keeps B1 — the largest lever — labelled *"a governed new K1 address and **NOT** the R-stage"*,
which is the distinction C5's Condition 10 exists to protect. Nothing in C6 moves the R-stage premise one step
closer, and C6 does not pretend otherwise.

---

## (a) Were the reviewer's seven corrections actually made, at source, and are they correct?

**Four of seven fully and correctly; two partially; one partly, and with a new false statement.** All are in the
producers, not bolted onto the JSON — I confirmed by re-running all three and getting byte-identical output, so the
artifacts are genuinely generated from the corrected source. But "at source" is not the same as "completely", and
three corrections stop short of the places the reviewer named.

| # | correction | ruling |
|---|---|---|
| 1 | E1's class → record the gap, withdraw "strongest reclassification" | **MADE, CORRECT.** `GATE_CLASS_GAP__nearest_is_HISTORICAL_REPLAY_REQUIRED` in source, `GATE_DEFECT` and `NOT_a_C6_discovery` fields added, `ERRATUM_C6_GATE.md` E1 written, gate **not** amended. I verified C5's Condition 11(c) and ledger `kill_reason` both predate C6, so the withdrawal is correct. |
| 2 | A1 + headline: replayability gets inputs, not result | **MADE IN PROSE, NOT IN THE CLASS FIELD.** `REPLAYABILITY_GETS_THE_INPUTS_NOT_THE_RESULT` is present verbatim; `missing_what` now reads *"a TOOLCHAIN for the INPUTS. The RESULT has never been derived by anyone and still must be."*; the headline is rewritten and the old clause recorded as `withdrawn_headline`. **But `A1.C6_CLASSIFICATION` is still `HISTORICAL_REPLAY_REQUIRED`** (N4). |
| 3 | binding independence | **MADE, CORRECT.** `root_bindings` = 1 for 306–308, 2 for 309; `PROVENANCE_BOUND` re-keyed from `>= 2` to `>= 1` on root bindings; `ADOPTED_TAIL_INPUTS_declares_the_export_manifest_as_its_source` computed, not asserted. I verified `manifest_sha256` = the manifest's own sha256. |
| 4 | leverage currency | **MADE, CORRECT.** I verified 2.0561597% / 5.535691% in `C5_FORECAST.json`, and that **all three** quoted oracle rows carry `status: DIAGNOSTIC` and are frozen-clause. The C5-T shift (+0.004661130 → +0.001708896) is correct. Minor: the single attribution over-unifies two different reasons for DIAGNOSTIC (N10). |
| 5 | frozen chain transitively | **MADE IN SUBSTANCE, DERIVATION STILL UNEARNED.** The closure is walked and hashed at 59 modules including the two outside `level4/closure_proofs`. I confirmed all 59 are git-tracked with matching hashes — so the claim is **true**. But `all_committed` is still `True if resolved else False`, which consults no git (N6). |
| 6 | "never serialized anywhere, ever" | **HALF MADE.** Fixed in README and in the graph. **Not fixed in `C6_CLASSIFICATION.json`'s A1 entry**, where `ever_serialized: false` and an unqualified `serialization_search` remain — the reviewer said "both places" (N3). |
| 7 | the five minor items | **PARTLY, AND ONE IS NOW FALSE.** `production_run`/`result_bearing` for four cells: present and factually right, but hard-coded (N7). `subdivision_depth`: stated as **null**, which is **false** — it is `0` (N1). "24 iterations": fixed in the graph, **still flat in the B1 route entry** (N2). "ONLY Chebyshev": dropped, replacement under-enumerates (N8). `B0_18`: no longer hard-coded but now **tautological** (N5). |

**The three specific things I was asked to check:**

* **Does the headline still claim "nothing needs to be re-derived"?** **No.** The clause is gone, the replacement
  says the opposite (*"obtaining the gain still requires NEW CERTIFIED WORK THAT NO CAMPAIGN HAS PERFORMED …
  'Missing a toolchain' is true of the INPUTS and false of the RESULTS"*), and the withdrawal is recorded in the
  artifact and in erratum E2(a). Correctly done.
* **Does A1 carry the replayability-vs-result limitation?** **In prose, yes, prominently. In its class field, no.**
  This is the residual defect that matters most, because the class field is the machine-readable answer.
* **Is E1's gate-class gap recorded rather than absorbed?** **Yes, properly.** The class name itself announces the
  gap, the gate is left unamended, and the erratum states what the missing class is and that a successor gate must
  add it. This is model handling of a frozen-gate defect.

## (b) Is the A1 finding sound?

**Yes — sound, and I can state the mechanism more precisely than C6 does. And it carries a conclusion C6 has
established without saying: A1 is *harder* than C5 thought.**

I read `tc_producer.identity_gate` (lines 163–208), `tct_inputs.py`, `order2.py` and `aux_certifier.py`.

**What the gate actually enforces.** Three different strengths, and the distinction matters:

1. Every `cert.residuals[*]["delta_mid"]`, every `record["eps_mid"]` node and every `record["eps_cell"]` node is
   compared by **exact rational equality** (`mag(...) != F(val)` → diff) at the ambient `workprec(256)`.
2. The `auxiliary_evidence.candidate_suprema` entries — which is where `cert.sup[fam, r, 0]` appears directly — are
   compared **at 53 bits**: `coarse[name] != F(val)` → diff, plus `fine[name] > F(val)` → diff. So the 53-bit
   rendering must match exactly and the 256-bit value must be **no larger**.
3. `if checked < 150: raise TCProducerRefusal`. The tail cells record 262 fields compared.

Point 2 alone would tolerate a *sub-53-bit-ulp* tightening — the gate accepts a smaller 256-bit sup that renders
identically at 53 bits. So "bit-for-bit" is not quite the right description of the suprema comparison, and C6/the
reviewer overstate it slightly.

**But the conclusion holds, via point 1.** `sup[{H,F,D}, r, 0]` propagates into the compared quantities:
`order2._env2_H` (lines 161–162) returns `k[2]·sup[H,r,0] + k[4]·sup[F,r,0] + 2·k[3]·sup[D,r,0]`, and
`order2._dres_H` (lines 196–198) adds `Z_RANGE·(sup[H,r,0]·eps_zi(1) + sup[F,r,0]·eps_zi(3) + 2·sup[D,r,0]·eps_zi(2))`.
These feed `_tighten` → `delta_cell`/`eps` at 256 bits, and those are compared by **exact** equality. A tightening
of the magnitude A1 requires — C5 quantified it at **2.0561597%** under C5-T — changes `eps_mid`/`eps_cell` at 256
bits with certainty and the gate raises `TCProducerRefusal`.

**So: a faithful replay returns the adopted `sup{F,D,H}` and delivers exactly zero of A1's gain, by construction.**
The identity gate is the thing that makes a replay a replay. A1's gain requires a *different* sup routine whose
output the frozen gate would reject as non-identical. C6's corrected finding is right.

**Is A1 a live route?** **Live, but materially harder than C5 thought, and harder than C6's class field admits.**

* Not dead. The candidates are exactly regenerable from a closure I verified is complete and git-tracked; the
  requirement is **quantified** (2.0562% C5-T / 5.5357% frozen); the oracle closes all three cells; the address is
  old, so no new-real authorization is needed for the materialization.
* But C5 believed A1 was a *retrieval*: fetch payloads from a 90 MB store, tighten, done — `new_real_required:
  false`, Condition 11(b). **Every part of that is now false.** The payloads never existed (0/326, verified twice);
  the regeneration yields the adopted numbers; and the tightening has never been computed by anyone. A1 now needs
  (i) a certifying host that does not exist in scope (N9), (ii) a producer protocol permitting a non-identical sup,
  which does not exist and would itself need governance, and (iii) an unknown amount of slack in the certifier's
  own sup routine, which no committed artifact exposes.
* **C6 has therefore quietly established that A1 is harder than C5 thought, and it does not say so in those
  words.** Its prose says the result "still must be" derived; its class field says `HISTORICAL_REPLAY_REQUIRED`;
  its ranking places A1 second with "needs a flint host". A reader who takes the class and the ranking — the two
  most machine-legible fields — still gets C5's wrong picture in softer form. A1 belongs in the same declared
  gate-class gap as E1, and the successor must record it there.

## (c) Was C6 worth running?

**I agree with the reviewer, and I will sharpen the ledger in both directions.**

**The recovery is worth approximately nothing**, and C6 says so itself in erratum E3 — four files duplicating bytes
the programme already adopted, capped at P3, feeding a consumer that never opens them. I verified each step of that:
the bytes are identical to what `ADOPTED_TAIL_INPUTS` names, the provenance caps at P3 on two links that fail by
raw bytes, and the C5 consumer opens no raw record. Had that been all of C6, the campaign would not have been worth
its cost.

**What justifies it is the falsification, and it is worth more than most tightenings.** C5's adjudicator issued
Condition 11(b) — a *binding* instruction to a successor to *"retrieve the K1 object candidate payloads from the
external record store"* — and those payloads do not exist. I re-verified this with a wider net than either C6 or
the reviewer used: **0 hits over 326 records** on twelve payload-key alternatives, and the **longest JSON array
anywhere in a tail record is 10 elements**. A degree-12 multivariate candidate cannot hide there. A C7 obeying
Condition 11(b) would have spent a campaign hunting a file that was never written. In a programme carrying eleven
binding conditions per adjudication, **removing a false instruction from the record is a first-class result**, and
it is the kind of result only a forensic campaign produces.

Two more, both cheap and both real: the **D4 repair** (I read the inconsistency in the C5 ledger directly — `DATA`
and `new_real_required: true` cannot both be the kill kind) and the **B1 proof** (asserted by C5, now demonstrated;
and my own check strengthens it further — the schema has a `subdivision_depth` slot and it holds `0`).

**Against that, three debits the reviewer did not fully price:**

1. C6 **partially re-creates the hazard it is credited with removing.** The reviewer's headline objection was that
   a hurried reader would take C6 as "install two packages and A1 is done". The prose is fixed; the class field and
   the ranking are not (N4). A machine consumer, or a hurried one, still reads "replay".
2. C6 **shipped a false statement that arrived through a correction** (N1, `subdivision_depth` null vs 0), by
   adopting a reviewer finding without checking it. For a campaign whose entire product is forensic accuracy, that
   is a pointed failure — and it is the documented handover-discipline trap of trusting a reviewer's output.
3. The **pattern of unearned assertions survives its own repair** (N5, N6, N7). The reviewer caught one hard-coded
   `True`; C6 replaced it with a tautology and left three more hard-coded conclusions in place. Every one is
   factually correct — I checked each on the host — but a forensic artifact whose conclusions are typed in rather
   than computed is not self-verifying, which is the property C6 exists to provide.

**Net: worth running, clearly, and cheaply — but for one falsification and two repairs, not for a recovery, and
with a product that still mis-signals its own most important finding in the field most likely to be read
mechanically.** C6's contribution is real and smaller than its structure implies.

## (d) Is the frozen gate sound governance?

**Partly. It is sound *because* it is disclosed and *because* the outcome was constrained rather than flattered by
it — but it is a disclosed-accommodation gate, not a prospective one, and the class gap is the concrete cost.**

**Temporal integrity: provable, and I re-verified it.** The gate hashes to `03c56433…` at commit `59513c86` and in
the working tree; that commit adds exactly one file; both `C6_CLASSIFICATION.json` and `c6_classify.py` are absent
at the freeze; exactly one commit in all history touches `C6_CLASSIFICATION.json`. There is no backdating and no
hidden tree. The classifier also *refuses to run* unless the gate hashes to its frozen value, which I confirmed by
reproducing it. That is real enforcement.

**Not fitted, and the evidence is that C6 fails its own gate.** The six classes are generic, and when applied
mechanically to a route the gate did not anticipate they produced a **gap** rather than a convenient label — which
is exactly what an unfitted taxonomy does. The **P4 minimum** is plainly not fitted: every object C6 recovered
lands at **P3** with `admissible_for_NEW_scientific_reuse: false`. A threshold written to be passed does not get
missed by the campaign that wrote it. And the `what_C6_may_NOT_conclude` list holds: all four forbidden conclusions
are withheld.

**Fitted, and it matters.** The `already_adopted_exception` is shaped to the outcome. It is the sole clause that
lets four P3 records be reported as `RECOVERED_ADMISSIBLE`; it was written into a gate frozen **70 seconds** after
the commit containing those already-hash-verified records; and it carries its own anti-abuse rider (*"may not use
the exception to manufacture a P4"*) — an author writing for an unknown future does not usually need to fence a
rule against himself. C6 **uses it correctly** and declares the basis every time, as required. But it should be
read as a disclosed accommodation for evidence already in hand.

**Freezing after B0–5/10/11 is the structural weakness, and the class gap is its bill.** A gate that discloses
every expected classification in advance is admirably transparent — `prior_evidence_known_at_freeze` names the
expected headline, and explicitly invites the reviewer to find fitting. But a gate written knowing the answers is
not tested by them. The missing class — *inputs present, new zero-new-real certification work required, blocked by
toolchain* — is the programme's **most common situation** (C1, C2, C5 and now A1 and E1 all sit in it). A genuinely
prospective taxonomy would very likely have included it. Instead the gate's six classes forced E1 into the wrong
label, and the refusal list's remedy (an erratum) had to be invoked in the campaign's first application of its own
classes.

**Ruling: acceptable governance, with two required repairs in the successor gate** — add the missing class, and
freeze the gate **before** the evidence phases it classifies, not seventy seconds after them. The
`already_adopted_exception` should survive but be declared prospectively rather than written around evidence in
hand. And the gate's honesty in disclosing the expectation, and in asking to be attacked for fitting, is a genuine
governance strength that I do not want to understate: it is why this adjudication could reach a finding at all.

## (e) Does anything in C6 license closing a cell, creating r6, claiming exhaustion, or authorizing the R-stage?

**No. None of the four. C6 is clean here, and I attacked this hardest for false comfort.**

* **Closing a cell.** `K5_cells_closed: null`. The adopted set is unchanged at `[]`. No cell is reported closed,
  tightened or adopted anywhere. `ranking_is_planning_only` is stated explicitly and the ranking carries no Γ.
  C6 creates no closure forecast and no prospective closure gate, as its own `closure_separation` clause requires.
* **r6.** `coverage_map_revision: null`. I searched the whole tree: the only coverage maps are R3, R4 and R5.
  r5 (`e2197051…`) is authoritative and byte-unmodified; `B0_08_no_r6` re-runs true.
* **Exhaustion.** `broader_deterministic_exhaustion_established: false`. Only negative uses of "exhaust" appear;
  `DETERMINISTIC_TRANSPORT_FAMILY_EXHAUSTED` does not appear at all. C6 in fact argues the opposite (Q9).
* **R-stage.** `R_stage_prerequisite_satisfied: false`. No authorization, launch notice, countersignature,
  amendment or slot binding exists. Guard `DENY` in every evidence file; zero new-real addresses and zero kernel
  evaluations — **and physically impossible**, since neither permitted host can import flint or numpy.

Nor does anything license them **implicitly**. The one place where implicit licensing could have crept in is the
planning ranking, and it is correctly fenced: every figure in it is labelled DIAGNOSTIC and superseded-clause, and
the gate's own words (*"may NOT alter scientific adoption"*) are carried into the artifact. The `already_adopted`
basis is invoked to admit *bytes*, never to admit a *result*. **K5 remains PARTIAL with m = 5 open at
{306, 307, 308, 309}.**

## (f) Independent verification of the boundaries

* **AWS never contacted.** I loaded no `rebaseguard-aws` schema in this session and made no AWS call. Across the
  whole C6 namespace, `grep -rniE "aws|ubuntu|ps1"` returns only **negative assertions** (README, gate, inventory,
  classification, classifier source) plus the reviewer's own discussion — no AWS-side path, host, log fragment,
  identifier or hash. Every external number in C6 I re-derived from the **Vultr** host or the committed corpus:
  the four record hashes and sizes, 326 files, 93,093,045 bytes, the manifest sha `29ad1f9b…`, the external audit
  sha `2ec4dcbb…`, `producer_manifest_hash b55a2da1…`. **Nothing in C6 requires an AWS source and nothing in it is
  unexplained without one.** Scope of my finding: I cannot audit C6's transcript, so I cannot prove no call was
  made and discarded; the artifact set bears no trace and requires none, which is the strongest available statement.
* **Vultr read-only only.** My own session: `status`, plus `ls`/`find`, and `python3` heredocs that only `open(...)`
  for reading, `hashlib`, `os.stat`, `json.loads` and `re`. I created no file, removed none, changed no permission,
  installed nothing and started no service. C6's recorded `mutating_commands_used: []` is consistent with what I
  observe on the host.
* **0 external evidence mutations.** Verified, not accepted: `mtime == ctime` on all four records at
  2026-09-16 05:53:11 UTC, identical before and after my session; nothing under `closure-r1` newer than
  Sep 16 07:00; the manifest integrity re-check still gives **326 OK / 0 mismatch / 93,093,045 bytes**. A copy
  would not move mtime; a write would have moved ctime. Neither moved. C6's commits postdate the bytes by six days.
* **0 scientific kernel evaluations.** Verified three ways: no C6 producer imports numpy, scipy, flint or any
  certifier, and none calls `prepare()`, `all_residuals()` or `Order3Certifier`; all three producers reproduce
  byte-identically under my own re-run; and **both permitted hosts lack the toolchain entirely**, so no kernel
  could have run even accidentally.
* **Guard DENY.** `REAL_SCIENTIFIC_COMPUTE = DENY` appears in every C6 evidence artifact and is re-asserted by
  `B0_11_guard_deny` across C2–C5, which I re-ran (true). `new_real_scientific_addresses_evaluated = 0` and
  `scientific_kernel_evaluations = 0` throughout. `git diff 69bff424 HEAD --name-only` touches only paths under
  `p5y_k5_tail_c6_evidence_recovery`; C2/C3 seal manifests re-verify at 156 and 21 entries, 0 deviations.

---

# VERDICT

**ACCEPTED_WITH_SCOPE_LIMITATION**

C6's forensic core is **true**, and I verified all of it independently rather than accepting it: the candidate
polynomials were never serialized anywhere (0/326 under a regex wider than either C6's or the reviewer's, longest
array 10); the four sealed records exist, are byte-identical to already-adopted evidence, and predate C6 by six days
by mtime *and* ctime; provenance honestly caps at P3 on two links that fail by raw bytes; the recovery is
`NOT_LOAD_BEARING`; D4's reclassification repairs a real ledger inconsistency; B1 is proven rather than asserted;
and C5's binding Condition 11(b) is **falsified**. All four forbidden conclusions are withheld, the guard is DENY,
external mutations are zero, and AWS bears no trace of contact. The campaign is worth what it claims to be worth in
its own erratum E3 — a falsification and two repairs — and no more.

The acceptance is **scope-limited** on five grounds, none of which touches the guard, the mutation count, the AWS
boundary or the forbidden conclusions, and all of which are correctable in text without re-running anything:

1. **A1's machine-readable class is wrong** and contradicts A1's own prose. A1 belongs in the same declared
   gate-class gap as E1; it is recorded as `HISTORICAL_REPLAY_REQUIRED` (N4).
2. **A false statement is in the product**: `subdivision_depth` is `0`, not `null`, and C6 adopted the error from
   its reviewer without checking (N1).
3. **Two corrections are half-applied** — correction 6 not carried into the classification's A1 entry, correction 7
   not carried into the classification's B1 entry, leaving two C6 artifacts in disagreement (N2, N3).
4. **The unearned-assertion pattern survives its own repair**: `B0_18` is now tautological rather than hard-coded,
   `all_committed` is asserted from non-emptiness, and four self-report blocks plus two broken-link verdicts are
   typed in rather than computed (N5, N6, N7). All are factually correct — I verified each — but none is
   self-verifying.
5. **The ranking rests on a premise C6 never checked**: there is **no certifying host in scope at all**, the
   worker lacking flint exactly as the local machine does (N9). "Needs only a flint host" overstates availability.

I also record, **against the campaign's presentation and in its favour on substance**, that C6 has established
something it does not state plainly: **A1 is harder than C5 believed**, not easier. C5 thought A1 was a file
retrieval with `new_real_required: false`. It is in fact new certified work, at a gain no one has ever computed,
which the frozen identity gate provably refuses to emit, on a toolchain no permitted host has. That is C6's most
important finding and its own class field still hides it.

Nothing in C6 closes a cell, creates r6, establishes exhaustion, or authorizes the R-stage. **K5 remains PARTIAL,
m = 5 open at {306, 307, 308, 309}, r5 authoritative, guard DENY.**

## EVIDENCE STATUS PER ROUTE

**A1** — object (candidate polynomials) **NEVER SERIALIZED**, confirmed 0/326 + 0/10 under a wider regex; suprema
**ARE** committed at exact rational precision in `TCT_INPUTS_30{5..9}.json`; inputs **EXACTLY REGENERABLE** from a
59-module closure verified entirely git-tracked, at an address already evaluated (`identity_gate.identical`, 262
fields); **gain NOT obtainable by replay** — `identity_gate` compares `eps_mid`/`eps_cell` by exact rational
equality at 256 bits and `sup{F,D,H}` propagates into them via `order2` 161–162 / 196–198, so any material
tightening is refused; requirement quantified by C5 at **2.0562% (C5-T) / 5.5357% (frozen)**, delivery-side slack
unknown; C5's "payloads in the external store" **FALSIFIED**; **class as recorded (`HISTORICAL_REPLAY_REQUIRED`)
REJECTED** — belongs in the declared gate-class gap; **HARDER THAN C5 THOUGHT**; live, blocked by no-host +
no-protocol; not load-bearing for any recovered byte.

**A3** — object status **as A1** (candidates never serialized, exactly regenerable); additionally requires an
**unwritten cancellation theorem** bounding `phi''' = S''' + 3K1·Hhat + 3K2·Dhat + K3·Fhat`; C6's limitation
sentence (*"replayability gets the inputs, not the result"*) correctly present here; **HISTORICAL_REPLAY_REQUIRED
for the inputs, ACCEPTED**; leverage doubly contingent, bounded above by the `f_G → 0` oracle
(−0.173324 / −0.128674 / −0.089759, **DIAGNOSTIC**, frozen clause); no evidence deficit beyond A1's.

**D4** — object (**joint** certified information on R and D at `e0`) **NEVER EXISTED**; verified independently on a
466-key walk: `R_interval`, `D_interval`, `R2_interval`, `M_R2` present per `m` as independent outward-rational
enclosures, **no joint / correlation / covariance / cross field in any schema**; `OBJECT_ONLY_HYPOTHESIZED`,
`existence_proof: none`; **TRUE_NEW_REAL_REQUIRED — ACCEPTED**, reclassification from C5's `DATA` correct and it
repairs a genuine ledger inconsistency (`DATA` + `new_real_required: true`); ceiling unknown, `g_hi` is 59–60% of
the closure deficit; **C6's cleanest work**.

**E1** — inputs **NEVER MISSING**: `taboo_cell_30{5..9}`, `arl_cell_30{5..9}`, `taboo_block_30{5..9}` committed
with `"numerators"` for every tail cell, verified; object (a **better** operator tuple `(tau, D_lo, Abar)`)
**OBJECT_ONLY_HYPOTHESIZED — never evaluated, nothing to replay**; **FITS NO CLASS IN THE FROZEN GATE**, correctly
recorded as `GATE_CLASS_GAP` with the defect in `ERRATUM_C6_GATE.md` and the gate left unamended — **ACCEPTED**;
**NOT a C6 discovery** — C5's ledger and Condition 11(c) already named the python-flint block, correctly withdrawn;
zero-new-real by programme classification; blocked by a certifying host that **exists on neither permitted host**;
oracle −0.0602 / −0.0030 / +0.0468 (**DIAGNOSTIC**, frozen clause) — closes 307, barely 308, **not** 309.

**B1** — **TRUE_NEW_REAL_REQUIRED, CONFIRMED and independently strengthened**; eight sub-structure tokens 0 in all
four sealed records (re-run by me); `whole_cell_refinement` is a per-`r` whole-cell fixed point, r = 0 giving
**25 at 306** and 24 at 307/308/309; `subdivision_depth` **present at `/producer/runtime/subdivision_depth` with
value `0`** — the schema has a subdivision slot that was never filled, which supports B1 *better* than the "null"
C6 records (**C6's statement here is FALSE as written**, conclusion unaffected); restriction of a whole-cell
certificate cannot tighten it, its value *is* the whole-cell supremum; largest lever, a **governed new K1 address
and NOT the R-stage**; classification entry still carries the uncorrected flat "24-iteration".

**E2** — **NOT_AN_EVIDENCE_PROBLEM — ACCEPTED**; no recovery required and none possible: needs a **theorem**, a
sharper *certified* lower bound on `Lambda_309` against C4's ladder/Wald minorant `3.297250282` versus an
uncertified Monte-Carlo truth near `4.047`; nothing in the corpus bounds `E_a[tau]` from below at all (C5 phase-2
swept it); the **only** lever restoring the cell-309 margin that C5-T consumed (**0.944%** of critical `A0`,
verified in two independent C5 artifacts); **needs no toolchain and no host — the only route a C7 can start today**,
and therefore the correct first item, which C6's ranking places third.

## CONDITIONS

Binding on any successor (C7 or otherwise) that consumes C6.

1. **Do not read A1 as replayable.** `A1.C6_CLASSIFICATION = "HISTORICAL_REPLAY_REQUIRED"` is **rejected by this
   adjudication** at route level. A1 is replayable for its *inputs* only; its *gain* has never been computed and
   `tc_producer.identity_gate` provably refuses to emit it. A successor must record A1 in the same class gap as E1,
   and must not plan an A1 replay expecting a tightening.
2. **Strike C5's Condition 11(b) as falsified.** *"Retrieve the K1 object candidate payloads from the external
   record store"* directs a successor at payloads that do not exist — 0/326 sealed records under twelve payload-key
   alternatives, longest JSON array 10, plus 0/10 in git. C5's A1 `kill_reason` (*"the payloads live in the external
   90 MB K1 record store"*) is likewise false. No successor may act on either.
3. **Correct C5's A1 `new_real_required: false`.** C6's own corrected finding contradicts it and C6 did not flag it.
   A successor must reconcile this second ledger inconsistency as C6 reconciled D4's.
4. **Correct the `subdivision_depth` statement before any reuse.** The key exists at
   `/producer/runtime/subdivision_depth` with integer value **`0`**, not `null`, in all four records. B1's
   conclusion stands and is strengthened; the recorded fact is false and was adopted from a reviewer unverified.
5. **Finish corrections 6 and 7 in `C6_CLASSIFICATION.json`.** A1's `ever_serialized`/`serialization_search` must be
   qualified to the *polynomials* (the suprema are committed); B1's flat "24-iteration" must become the per-cell
   counts (25 at 306). Two C6 artifacts currently disagree and the classification is the one a consumer reads.
6. **Carry C5's two exhaustion scope limits alongside any route ranking derived from C6.** C5-T's premise
   `x_lo > 0` **fails at cell 0** (both detectors), and C5's exhaustion is of the **transport family only** and may
   never be restated as deterministic exhaustion. C6 ranks routes without carrying the scope sentences attached to
   them.
7. **Treat host provisioning as a separately governed prerequisite, not a parenthesis.** Neither the local host nor
   `rebaseguard-vultr-02` has flint, numpy, scipy, mpmath, sympy or gmpy2, and AWS must not be contacted. No A1 or
   E1 work may be chartered until a governed certifying host exists, and any such provisioning is a change to the
   programme's compute surface requiring the user's decision — not a campaign's.
8. **Sequence a C7 as E2 first.** E2 needs no recovery, no toolchain and no host, and is the only lever that
   restores the cell-309 margin. C6's ranking places E1 and A1 above it on a premise (host availability) that is
   false. Re-rank before chartering.
9. **The successor gate must add the missing class** — *inputs present, new zero-new-real certification work
   required, blocked by toolchain* — and must be frozen **before** the evidence phases it classifies, not after
   them. The `already_adopted_exception` may be retained only if declared prospectively.
10. **No P3 object may be adopted as new scientific evidence.** All four recovered records are P3 with
    `admissible_for_NEW_scientific_reuse: false`. Any attempt to raise them must **first** establish the semantics
    of `production_run` / `result_bearing` in the Aux5 schema, and must close the two links that fail by raw bytes
    (`producer_manifest_hash` ≠ `611bd0a9…`; manifest's `composite_audit_sha256 = fa1d79b5…` matching neither the
    committed nor the external audit, which agree at `2ec4dcbb…`). The anomaly is localized in the manifest that
    carries all 326 record hashes; treat that as a standing provenance risk, not a curiosity.
11. **Conclusions a successor may not draw from C6 under any outcome:** no K5 cell closes or is adopted; **no r6**
    — r5 (`e2197051…`) remains authoritative; **no broader deterministic exhaustion** — evidence recovery can never
    establish it, and C6 in fact leaves four routes open; **no R-stage authorization** — the prerequisite is not
    satisfied and `REAL_SCIENTIFIC_COMPUTE` stays **DENY**.
12. **Do not cite C6's recovery as a scientific gain.** Its own erratum E3 rules the recovery worth roughly
    nothing, and I concur: it buys reproducibility (a C7 can run the `tct_inputs` identity gate, and
    `tail_forecast_r2`'s extract-faithfulness assertions, from local copies) and no Γ. C6's value is the
    falsification of Condition 11(b), the D4 repair and the B1 proof. Cite those.
13. **Verify reviewer findings before absorbing them.** C6 transcribed at least two reviewer figures without
    checking — one false (`subdivision_depth` null) and one under-enumerated (the `"numerators"` inventory). A
    successor must re-derive any finding it carries from a reviewer, and must not treat a review's authority as
    evidence.
14. **No hard-coded conclusions in a forensic artifact.** `B0_18` is now a tautology, `all_committed` is asserted
    from non-emptiness, and six further values are typed in rather than computed. Every one happens to be true — I
    verified each against the host and against git — but a forensic producer must compute what it asserts, or the
    artifact cannot be audited by re-running it.

HANDOVER: ADJUDICATION COMPLETE
