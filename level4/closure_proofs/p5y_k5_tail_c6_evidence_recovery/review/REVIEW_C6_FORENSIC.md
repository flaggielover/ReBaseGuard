# Independent fresh-context forensic review — P5Y / K5 Campaign C6

Reviewer: fresh context, no prior involvement. Target `/Users/suzhe/ReBaseGuard-k5c6`, branch `p5y-k5-tail-c6`,
HEAD `756a6d93`, namespace `level4/closure_proofs/p5y_k5_tail_c6_evidence_recovery`.

Read-only throughout. Nothing in the working tree was created, edited, committed or deleted; `git status` was clean
at start and at end. All scratch output is under the session scratchpad. **AWS was not contacted**: no
`rebaseguard-aws` tool schema was ever loaded into this session and no call was made. `rebaseguard-vultr` was used
in **read-only** mode only — `status`, `ls/find/stat`, `sha256sum`, and `python3` scripts that only read, hash and
regex. No kernel, no certifier, no Order3Certifier, no R-stage, nothing that computes a scientific quantity. I made
**zero** modifications on the Vultr host.

I re-derived every load-bearing number rather than accepting it. Where I agree with C6 I say what I ran.

---

## Executive summary

The **forensic core of C6 is true and I verified all of it independently**:

* The K1 object *candidate payloads* were never serialized. 0/326 sealed records and 0/10 committed records
  contain a payload key, under a **wider** regex than C6 used, and no record contains any JSON array longer than
  10 elements.
* All four open tail cells' sealed records exist, are byte-identical to what `ADOPTED_TAIL_INPUTS` names, and
  **predate C6 by six days** (mtime *and* ctime `2026-09-16 05:53:11 UTC`).
* External evidence mutations: **0**, verified by me, not by C6's assertion.
* The recovery is **not load-bearing** — correct conclusion, reached by C6 with an insufficient method (§ NL).
* C6 closes no cell, creates no r6, claims no exhaustion, authorizes no R-stage. Clean.

Against that, there are **six material defects**, two of which are in the campaign's advertised product:

1. **E1 is in the wrong class** under the gate's own definition (§J-E1). A *better* operator tuple was never
   evaluated by anyone; it cannot be "replayed". C6 forced it into `HISTORICAL_REPLAY_REQUIRED` instead of
   recording that the gate's six classes have a gap.
2. **The headline overstates A1.** `tc_producer.identity_gate` *requires* a replay to reproduce the sealed
   quantities exactly. A faithful A1 replay therefore delivers the adopted `sup{F,D,H}` bit-for-bit and **exactly
   zero** of A1's gain. "Nothing needs to be re-derived" is false of A1's and E1's *results* (§G).
3. **"Two independent committed bindings" is not independent** for cells 306–308: `ADOPTED_TAIL_INPUTS` carries
   `manifest_sha256 = 29ad1f9b…`, which is the export manifest's own sha256 — it names its source (§B).
4. **Leverage figures are quoted from a superseded clause, unlabelled**, while the one figure C5 *did* quantify
   (2.0562 %) is omitted under a claim of "NOT QUANTIFIABLE" (§K).
5. **Frozen-chain completeness is not established by C6's evidence.** C6 hashes 13 paths; the real transitive
   closure is larger. I checked the rest myself; the conclusion survives, the evidence does not support it (§G).
6. **"Never serialized — anywhere, ever" is false of half of A1's own required object**: the suprema
   `cert.sup[fam,r,0]` are committed, at exact rational precision, for every tail cell (§F, §G).

All six are correctable by erratum without re-running anything.

---

## A. Do the recovered bytes truly PREDATE C6?

**PASS.**

C6's three commits are `7dae3080` 2026-09-22 12:37:46 +0900, `59513c86` 12:38:56, `756a6d93` 12:41:10, i.e.
**03:37–03:41 UTC on 2026-09-22**. The Vultr clock reads `2026-09-22T03:49:04+00:00` and is NTP-synchronised.

From the host, read-only:

```
aux5_CUSUM_306_256.json size=279738 mtime=2026-09-16 05:53:11.358989209 ctime=2026-09-16 05:53:11.358989209
aux5_CUSUM_307_256.json size=280035 mtime=2026-09-16 05:53:11.358989209 ctime=...358989209
aux5_CUSUM_308_256.json size=280311 mtime=2026-09-16 05:53:11.362989254 ctime=...362989254
aux5_CUSUM_309_256.json size=280226 mtime=2026-09-16 05:53:11.362989254 ctime=...362989254
COMPOSITE_EXPORT/           dir mtime Sep 16 05:53
COMPOSITE_EXPORT_MANIFEST.json  size=35312  mtime=2026-09-16 05:53:11.386989531
COMPOSITE_AUDIT.json            size=117383 mtime=2026-09-16 05:50:07.572870270
```

`find /root/work/postk1-runs/closure-r1 -newermt '2026-09-17'` returns **nothing**. **ctime** is identical to
mtime on every record, so not even a metadata touch has occurred since 2026-09-16 — a copy, a chmod or a rewrite
by C6 would have moved ctime to 2026-09-22. This is the strongest available disproof and it is decisive.

Historical run structure is consistent and self-labelling. There are **7149** `aux5_CUSUM_*.json` files under
`/root/work/postk1-runs`. For the four tail cells, the files outside the export cluster at **9719–9841 bytes** and
every one I opened carries the key `SYNTHETIC_FIXTURE_NOT_SCIENCE` — acceptance/dev fixtures, exactly as C6 warns
(C6 does not mention the self-labelling key; it corroborates C6). The **280 kB** sealed records exist in exactly
**one** place each (`k4_records/`), so there is no ambiguity about which copy was recovered.

Independent corroboration in Git: the cell-309 record is committed at `10769e07`, **2026-09-16 18:18:24 +0900**,
six days before C6, and hashes to `95be4c65…` — identical to the bytes on the host.

Nothing here could have been written by C6.

---

## B. Are the provenance chains REAL?

**PASS_WITH_NOTES — one claim must be corrected; the P3 cap is honest and, if anything, under-reports.**

**Binding 1 — the export manifest.** Verified from the committed
`p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json`
(326 `files` entries, sha `29ad1f9b…`): the four `k4_records/aux5_CUSUM_30{6,7,8,9}_256.json` entries equal
`9c9da15b…`, `28bacf0a…`, `e8d7a412…`, `95be4c65…`. Identical to the bytes I hashed on the host. Independently, I
re-ran the manifest's whole integrity check on the host: **326 OK, 0 mismatch**, total record bytes **93,093,045**
— C6's figures exactly.

**Binding 2 — `ADOPTED_TAIL_INPUTS.record_sha256`.** Verified: the four `cells[*].record_sha256` match.

**The two are NOT independent.** `ADOPTED_TAIL_INPUTS.json` carries a top-level field
`manifest_sha256 = 29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334`, which is *exactly* the
sha256 of the committed export manifest. The adopted extract **declares the export manifest as its source**. And
`p5y_k5_m5_tail_closure/code/tail_forecast_r2.py` (lines ~120–347) reads the manifest, reads the records from it,
and then asserts `ad["record_sha256"] == st["hashes"][k]` and that every adopted field is byte-faithful to the
record. So binding 2 is a *verified transcription of binding 1*, not a second witness.

This does not weaken the recovery — a verified transcription is good evidence — but
`independent_committed_bindings: 2` is the wrong label, and it is the label the classifier uses to set
`PROVENANCE_BOUND` (`>= 2`). **Required correction:** for 306/307/308 the honest count is *one root binding plus
one verified restatement*; for 309 it is *two* (the root, plus a byte-identical copy committed independently in
`p5y_k5b_k1_premise_binding_audit` at `10769e07`, which is real corroborating **bytes**, not a hash reference).

A third hash reference exists that C6 did not count: `TCT_INPUTS_30{5..9}.json` each carry
`k1_record_sha256` equal to the same value. Same root, same campaign — it would not have added independence, and
C6 is not wrong to omit it, but it should be named.

**Is the P3 cap honest, pessimistic, or hiding something?** Honest, and mildly *under*-stated. I reproduced both
broken links myself:

* `producer_manifest_hash = b55a2da1fea0c7ee889f8da6a4b893c12d3ef24e2bc02d19bd5488187fd30fd9` in **all four**
  records (C6 checked only 309), against the committed
  `p5y_k1_cusum_aux5_successor/manifests/producer_manifest_v3.json` at `611bd0a9…`. **Does not close.**
* the export manifest's `composite_audit_sha256 = fa1d79b5…`, against the committed `COMPOSITE_AUDIT.json` at
  `2ec4dcbb…` and the external one at `2ec4dcbb…`. **Does not close against either.**

C6 reports this as two links failing. The sharper reading, which C6 misses: the committed and external audits
**agree with each other** and the manifest names a **third** value. So the anomaly is localized in the manifest —
and the manifest is the very artifact carrying the 326 record hashes that binding 1 rests on. That is a
*stronger* reason to cap at P3 than the one C6 gives, not a weaker one. C6 is not being needlessly pessimistic
and is not hiding a worse problem; it under-analysed the one it found.

The `no_inference_rule` was obeyed: nothing was upgraded.

---

## C. Is a historical file being mistaken for an authorized result?

**PASS.**

I confirmed the self-report on the host for **all four** records (C6 reports only 309's):

```
306/307/308/309:  production_run = false   result_bearing = false
                  campaign = p5y_k1_cusum_aux5_successor   adjudicated = null
                  detector = CUSUM  precision_bits = 256  cell_index matches
```

C6 records these verbatim, refuses to interpret them, and names the refusal as **a reason the level is capped at
P3**. That is the right call, and it is the *only* call the frozen gate permits: the `no_inference_rule` forbids
guessing what a field means in order to raise a provenance level, and the alternative — asserting that
`production_run=false` is a checkpoint-classification artefact rather than a statement about scientific standing —
would be exactly the inference the gate prohibits. Refusing to interpret does not undermine the recovery because
C6 never leans on these records for anything: their standing is invoked solely through the `already_adopted`
exception, i.e. from the programme's prior adoption of the same bytes, not from C6's reading of the fields.

Two notes. (i) C6 should record the fields for all four cells, not 309 alone — the generalisation is true but
undemonstrated in the artifact. (ii) This should be carried forward as a **named open blocker for C7**, not a
footnote inside `C6_PROVENANCE.json`: any future attempt to raise these records above P3 must first establish the
semantics of `production_run` / `result_bearing` in the Aux5 schema.

---

## D. Does scientific identity match?

**PASS_WITH_NOTES — right conclusion, inverted justification, wrong field name.**

The gate says plainly: *"byte_identity_is_not_scientific_identity"*, and lists nine attributes that must match
exactly (model, m, cell/address, precision bits, convention, derivative order, normalization, frozen producer
semantics, the scientific fields consumed). C6 sets `SCIENTIFICALLY_IDENTICAL: true` with
`identity_basis: "sha256 equality with the bytes ADOPTED_TAIL_INPUTS already names"`, and checks **none** of the
nine.

Is that a category error? In this specific case, **no** — but only by accident of direction. The gate's warning is
aimed at the case where two *different* files are argued to be scientifically the same. Here the file is the
*same file*: byte equality with an already-adopted artifact trivially implies equality of all nine attributes,
because they are all functions of the bytes. The conclusion is sound.

The *framing* is wrong, and in a programme with this provenance discipline the framing matters. The field asserts
a scientific property on a byte-level basis, which is the shape of reasoning the gate exists to forbid; a reader
skimming `C6_CLASSIFICATION.json` sees `SCIENTIFICALLY_IDENTICAL: true` next to `PROVENANCE_LEVEL: P3`. **Required
correction:** rename the field to `BYTE_IDENTICAL_TO_ALREADY_ADOPTED_BYTES`, and state the one-line argument
(same bytes ⇒ same address, same bits, same producer semantics) rather than leaving it implicit.

I did spot-check the address attributes anyway, from the host: `cell_index` 306/307/308/309, `detector` CUSUM,
`precision_bits` 256, `campaign` `p5y_k1_cusum_aux5_successor` — consistent with the tail-cell addresses and with
`TCT_INPUTS_30x.k1_record_sha256`. No mismatch.

---

## E. Does any C6 "reconstruction" secretly recompute science?

**PASS.** I read all three producers in full and re-ran all three.

* `c6_b0_audit.py` — `git` subprocesses, sha256, JSON/regex parsing of committed artifacts. No compute.
* `c6_forensics.py` — sha256 of 13 committed paths, `git log --all --name-only`, a regex payload scan over
  committed records, `json.loads` of one committed record for token counting, and provenance link comparisons.
  It consumes the **recorded** external inventory rather than re-contacting the host. No compute.
* `c6_classify.py` — refuses unless the gate hashes to `03c56433…`; then reads the two committed evidence files,
  does one substring grep of `c5_common.py`, and emits a dict of hand-written prose. No compute.

No module imports numpy, flint, scipy or any certifier; none calls `prepare()`, `all_residuals()`, `Order3Certifier`
or any R-stage entry point; none writes anything outside its `--out` path.

**Reproduction.** I re-ran all three into the scratchpad:

```
C6_MISSING_EVIDENCE_GRAPH.json   IDENTICAL
C6_PROVENANCE.json               IDENTICAL
C6_CLASSIFICATION.json           IDENTICAL   (classifier's own sha prefix 777fa3b997d6b49c)
C6_B0_AUDIT.json                 identical except head (756a6d93 vs 69bff424) and uncommitted_at_audit (0 vs 1)
```

Those two B0 deltas are expected and are themselves evidence: the committed B0 records
`head = 69bff424` — the **C5 predecessor head** — proving B0 ran before any C6 commit existed. B0 reproduces
**19/19 PASS**.

**Corroborating impossibility.** This host cannot run the science even by accident:
`numpy, scipy, flint, python_flint, mpmath, sympy, gmpy2` → all `find_spec() is None`; `pip list` shows exactly
one package (`pip 26.1.1`) on CPython `3.14.5`. `tc_producer.identity_gate` does `from flint import ctx`, so any
replay would abort at import. C6's absence claim is true and I verified it directly.

No reconstruction was performed. `RECONSTRUCTED_ADMISSIBLE` is used for nothing.

---

## F. Is an old address being mistaken for a new one?

**PASS_WITH_NOTES.**

For A1/A3 the address genuinely is old, and the proof is stronger than the one C6 gives. The committed
`TCT_INPUTS_30{5..9}.json` each carry:

```
mode = "replay_measurement"   identity_gate = {fields_compared: 262, identical: true}
order3_fields_present = false  k1_record_sha256 = <the sealed record's sha>
```

`tct_inputs.measure()` runs `cls(cell, bits=256).prepare(); cert.all_residuals(); cert.aux_residuals()` and then
`TP.identity_gate(...)`, which raises `TCProducerRefusal` unless the recomputation equals the sealed record
exactly (and refuses outright if fewer than 150 fields were compared; 262 were). So the programme has **already
executed** `Aux3Certifier.prepare()` at cells 305–309 and proved the output identical to the historical run. The
address is old, demonstrably.

**The note.** C6 defines A1's required object as *"the frozen K1 object candidates F_r, D_r, H_r **and their
suprema** `cert.sup[fam, r, 0]`"*. The suprema half of that object **is committed**, at exact rational precision,
for every tail cell — `tct_inputs.py` emits `"sup": {fam: _fstr(mag(cert.sup[fam, r, 0])) for fam in ("F","D","H")}`,
and e.g. `TCT_INPUTS_309.json` contains `/r/0/sup/F = 262811212386249/281474976710656`, `/r/0/sup/D`, `/r/0/sup/H`,
and so on for `r = 0..4`. C5's ledger says so too ("TCT_INPUTS_*.json carries only their sup VALUES"). C6
acknowledges it in one field of the graph (`logical_identity`, "which TCT_INPUTS records as sup.{F,D,H}") — but the
README asserts *"The K1 object candidates were never serialized — anywhere, ever"* and the classification's
`serialization_search` says the same without qualification. **That sentence is false of the object as C6 itself
defines it.** It is true of the *polynomials*. Fix the wording in both places.

---

## G. Is a NEW address being mislabeled as replay? *(the most important item)*

**PASS_WITH_NOTES on the narrow question; a material overreach at route level.**

### G.1 The narrow question: does `Aux3Certifier.prepare()` at 306–309 reproduce an evaluated address?

**Yes.** Evidence, all verified:

* `TCT_INPUTS_306..309` exist, committed, with `identity_gate.identical = true` over 262 fields and
  `mode = "replay_measurement"` — the recomputation has already been done and matched.
* `tct_inputs.py`'s docstring exemption is **conditioned**, and the conditions are machine-enforced:
  "No order-3 candidate of F is proposed and no order-3 field of F is written, so this is not a new real
  scientific evaluation". `tc_producer.run(...)` selects `Order3Certifier` only in `mode == "real"`; the replay
  path builds `ReplayAux3Certifier(Aux3Certifier)`. `tct_inputs.measure()` then raises
  `TCTInputRefusal("an order-3 field of F leaked into the replay measurement")` if any `G`-prefixed field appears,
  and all five committed files record `order3_fields_present: false`.
* `_candidates_order3()` produces candidates for `S`, `h`, `W` — the *source* objects — not for `F'''`. So it does
  not trip the docstring's own exclusion.

**C6 is entitled to lean on the docstring** for the materialization of the candidates. I checked this rather than
accepting it, and it holds.

### G.2 The overreach: a replay delivers exactly zero of A1's gain

`tc_producer.identity_gate` (lines 163–208) **requires exact equality** of the recomputed quantities against the
sealed record: every `residuals[*].delta_mid`, every `eps_mid`, every `eps_cell`, and every
`auxiliary_evidence.candidate_suprema` key (at 53-bit rendering, with the 256-bit value required to be no larger).
`sup["F"/"D"/"H", r, 0]` is not compared directly but feeds `eps_mid`/`eps_cell` through `order2.py` lines
161–162 and 196–198, and the chain is deterministic exact-rational code at fixed precision.

Consequence: **a faithful replay returns the adopted `sup{F,D,H}` bit-for-bit.** A1's mechanism, in C5's own
ledger, is *"tighten the candidate sup norms sF, sD, sH"*. A replay tightens nothing — by construction, because
the identity gate is precisely what makes it a replay rather than a new evaluation. To obtain A1's gain you must
apply a **different sup routine** to the recovered candidates, producing a value the frozen identity gate would
reject as non-identical.

C6 half-concedes this in one field — *"the achievable gain is the slack in THAT routine"* — and then contradicts
it everywhere that matters:

* `A1.missing_what`: *"A TOOLCHAIN. Not data and not science."*
* headline: *"Nothing was lost; nothing needs to be re-derived."*
* ranking: *"A1 — regenerable from committed code, needs a flint host; oracle closes all three."*

For A3, C6 writes the correct sentence — *"Replayability gets the inputs, not the result"* — and then omits it
for A1. **That sentence belongs verbatim in the A1 entry and in the headline.** A C7 that reads C6 as written
will install numpy and python-flint, run the replay, obtain the adopted numbers to the last bit, and have spent a
campaign confirming `identity_gate.identical = true` for a fifth time.

### G.3 An unstated principle carries the A1-vs-D4 asymmetry

C6 classifies *"re-certifying the K1 objects with a joint estimator that no historical campaign ever ran"* (D4) as
`TRUE_NEW_REAL_REQUIRED` — *"That is an address never evaluated"* — while classifying *"a tighter sup from a
better sup routine at the same cell"* (A1) as `HISTORICAL_REPLAY_REQUIRED`. Both are a new estimator applied to
the same objects at the same cell.

There **is** a principled distinction available — D4 needs a *new quantity* (a correlation between R and D), A1
needs a *tighter bound on the same quantity* — and I think it is the right one. But C6 never states it, and the
gate's classes are supposed to be mechanical. **Required:** state the principle explicitly, or the asymmetry
reads as fitted.

### G.4 The frozen-chain verification is incomplete

C6 hashes 13 paths and concludes `frozen_chain_all_committed: true`, which the determinism argument rests on.
That list is `tc_producer._import_chain()`'s **top-level** imports plus `cells.json`, `tct_inputs`, `tc_producer`.
The real transitive closure is larger. `aux_certifier.py` additionally imports `ancestry`, `cusum_layer1`,
`cusum_layer2`, `aux_collocation` (which `_candidates_order3()` calls directly:
`aux_collocation.collocation_order3`, `aux_collocation.objects_order3`), and
`rebaseguard_certify.polynomial`; `order2.py` additionally imports `opnorms`, `sharp_norms`, `sharp_certifier`.

I located every one of them: all seven extra modules are committed under `level4/closure_proofs`, and
`rebaseguard_certify` is committed at `rebaseguard-proof/src/rebaseguard_certify/` — **outside** the
`closure_proofs` tree C6 scanned. So **the conclusion survives**, but C6's evidence does not establish it, and one
dependency lives in a directory C6 never looked at. Derive the chain from `_import_chain()` plus a transitive
import walk, and hash the closure.

---

## H. Was external evidence modified?

**PASS. Verified independently: 0 mutations.**

* `find /root/work/postk1-runs/closure-r1 -newermt '2026-09-17'` → empty.
* mtime **and ctime** on all four records, the manifest and `COMPOSITE_AUDIT.json` are unchanged since
  2026-09-16 05:50–05:53 UTC. A read-only copy would not move them; a write would have moved ctime.
* Re-running the manifest integrity check gives 326 OK / 0 mismatch / 93,093,045 bytes — identical to C6's
  recorded figures, so nothing has drifted between C6's session and mine.
* Every command in my own session was `ls/find/stat/sha256sum/du` or a `python3` heredoc that only opens files
  for reading. I created no file, removed none, and changed no permission.

---

## I. Was AWS contacted?

**PASS, with the scope of my evidence stated.**

What I can verify transcript-independently:

* No `rebaseguard-aws` tool schema was loaded in **my** session, and I made no call.
* No AWS-side path, host or identifier appears anywhere in C6's artifacts or code. The AWS repo root is
  `/home/ubuntu/work/ReBaseGuard`; `grep -rn "ubuntu\|aws\|AWS"` over the whole C6 namespace returns **five**
  hits, all of them the *negative* assertion (README, gate, inventory, classification, classifier source). There
  is no AWS-derived datum, path, log fragment or hash in any artifact.
* Every external number in C6 I re-derived from the **Vultr** host: the four record hashes and sizes, 326 files,
  93,093,045 bytes, the manifest sha, the external audit sha `2ec4dcbb…`, 7149 `aux5` files. Nothing in C6
  requires an AWS source, and nothing in it is unexplained by the Vultr host plus the committed corpus.
* The gate forbids contact; `C6_EXTERNAL_INVENTORY.json` records `contacted: false, "no tool loaded, no call made"`.

What I **cannot** verify: I have no access to C6's transcript, so I cannot prove a call was not made and
discarded. My finding is that the artifact set contains **no trace** of AWS contact and requires none. That is
the strongest statement available from the evidence.

---

## J. Are the DATA vs NEW_REAL classifications justified per route?

### A1 — `HISTORICAL_REPLAY_REQUIRED` — **PASS_WITH_NOTES, material**

Correct at the level of the **object** (§G.1). Wrong at the level of the **route**. The replay reproduces the
adopted suprema exactly (§G.2); the suprema are already committed (§F); the gain needs a new estimator whose
output the frozen identity gate would reject. `missing_what: "A TOOLCHAIN. Not data and not science."` must
become something like *"a toolchain for the inputs; the result has never been derived by anyone and still must
be."* This is the single most consequential correction in the review.

The *positive* finding is real and valuable: C5's adjudicator issued **Condition 11(b)** — *"retrieve the K1
object candidate payloads from the external record store and tighten sup{F,D,H}"*. There are **no payloads in
that store.** I verified this with a wider net than C6's: over all 326 sealed records, the regex
`"(numerators|denominators|coeffs|coefficients|payload|cheb|poly|candidate|monomials|terms|series)"` gives **0**
hits, and a structural walk of a full record finds **no JSON array longer than 10 elements** anywhere (the two
longest are `/changes` at 10 and `whole_cell_refinement/*/trail` at 9). A degree-12 multivariate candidate cannot
hide in that. C6 has falsified a binding instruction, and that alone justifies the campaign.

### A3 — `HISTORICAL_REPLAY_REQUIRED` — **PASS**

C6 states the limitation correctly: *"Replayability gets the inputs, not the result"*, `missing_what: "A
TOOLCHAIN, plus a theorem that does not exist yet"`, leverage *"unknown and doubly contingent"*. Consistent with
C5's ledger (`mechanism`: exploit cancellation in `phi''' = S''' + 3K1·Hhat + 3K2·Dhat + K3·Fhat`). No complaint.

### D4 — `DATA` → `TRUE_NEW_REAL_REQUIRED` — **PASS, and this is C6's cleanest work**

The C5 ledger genuinely carries `kill_kind: "DATA"` **and** `new_real_required: true` on D4 — I read it directly.
B0 catches it mechanically (`B0_18`, and `c5_ledger_inconsistency` names the route, both fields and the finding).
The reclassification is right: I walked the 463-key set of a sealed record and there is `R_interval`,
`D_interval`, `R2_interval`, `M_R2`, `R_interval_mag`, `D_interval_mag` — the two enclosures, certified
independently, and **nothing relating them**. No joint, covariance, correlation or product field in any schema.
`OBJECT_ONLY_HYPOTHESIZED` / `existence_proof: "none"` is exactly right, and C6 does not pretend the ceiling is
known (`g_hi` is 59–60 % of the closure deficit, which matches C5's ledger `target`).

### E1 — `DATA` → `HISTORICAL_REPLAY_REQUIRED` — **FAIL on the class**

The gate defines `HISTORICAL_REPLAY_REQUIRED` as: *"the object is absent from every store, but the exact
scientific address **was already evaluated** under an authorized historical campaign and **could be reproduced by
a future governed replay** without creating a new address."*

C6's own entry says E1's object is *"a tighter certified operator tuple (tau, D_lo, Abar)"* with
`existence: "OBJECT_ONLY_HYPOTHESIZED (a BETTER tuple)"`. **A better tuple was never evaluated by anyone and
cannot be reproduced by a replay.** There is nothing to replay. The class does not fit, and C6 chose it anyway.

What is true: E1's *inputs* are committed — I verified the Chebyshev candidate payloads exist under
`p5y_k5_tail_operator_registry/evidence/registry_c1/` (`taboo_cell_30{5..9}.json`, `arl_cell_30{5..9}.json`,
`taboo_block_30{5..9}.json`, all containing `"numerators"`), for every tail cell. And it is true that operator
certification is programme-classified zero-new-real. The honest class is something the gate does not have:
*inputs present, new zero-new-real certification work required, blocked by toolchain*. The gate's refusal list
says an error in the gate *"is recorded in an erratum"* — that is the required remedy here, not silently taking
the nearest class.

C6 calls this *"the strongest reclassification in C6"*. It is not a discovery at all. C5's ledger already records
E1's `kill_reason` as *"operator certification needs python-flint, which is absent on this host"*, and C5's
adjudicator Condition 11(c) already says *"operator certification of A0 on a host that has python-flint"*. C6
changed the **label**, not the facts. Say so.

(One small overclaim: *"the operator candidate payloads are the ONLY Chebyshev payloads committed under
level4/closure_proofs"*. `grep -rl '"numerators"'` also returns `p5y_k5_perron_deflated_resolvent/evidence/
registry_r1/` and three `PROBE.json` files. Same *kind* of object at other cells, so the claim's substance holds;
the word "ONLY" does not.)

### B1 — `TRUE_NEW_REAL_REQUIRED` confirmed — **PASS, and I strengthened it**

C6 counted eight tokens (`sub_`, `subcell`, `partition`, `subinterval`, `sub_block`, `e_lo`, `e_hi`, `split`) →
all zero. I re-ran on all four records on the host **and added `subdivision`**, which C6's token list would have
missed because `subdivision_depth` does not contain `sub_`. Result: the key **does exist** — and its value is
**`null` in all four records**. So there is genuinely no sub-interval structure, and B1's conclusion is now better
supported than C6 left it. `whole_cell_refinement` is keyed `0..4` (per `r`) with `iterations`,
`contraction_below_one`, `converged: true` and a 9-element `trail` — a fixed point on the whole cell, not a
partition, exactly as C6 says.

One imprecision: C6 asserts "**24** iterations" as a property of the record, derived from the one committed copy
(cell 309). On the host, `r=0` gives **24** at 307/308/309 but **25** at 306. Immaterial to the conclusion; it
should not be stated as a flat fact.

---

## K. Is C5 route leverage computed against r5?

**PASS_WITH_NOTES — the r5 part is fine; the *clause* part is a real defect.**

**r5.** B0 verifies `K5_COVERAGE_MAP_R5.json` hashes to `e2197051…`, that its `inputs.coverage_map_r4_sha256` is
`a3bddd83…`, that no `_R6` map exists, and that the open set is `m=5 → {306,307,308,309}` with `m=1,2,3` empty. I
re-ran B0 and got 19/19. Correct.

**The clause.** Every oracle figure C6 quotes is a C5 phase-2 knockout row, and I checked them against
`C5_SENSITIVITY.json`:

| C6 quotes | C5 source | status in C5 | clause |
|---|---|---|---|
| A1 "sup F/D/H → 0 closes 307, 308 and (by 0.00035) 309" | `-0.103207 / -0.049231 / -0.000347` | **DIAGNOSTIC** | **frozen** |
| E1 "307 (−0.0602), 308 (−0.0030), 309 (+0.0468)" | `-0.06023472 / -0.00301356 / +0.04677533` | **DIAGNOSTIC** | frozen |
| A3 "bounded above by the f_G → 0 oracle, which closes all three" | `-0.173324 / -0.128674 / -0.089759` | **DIAGNOSTIC** | frozen |

The transcription is faithful. Two things are not carried:

1. **All of them are DIAGNOSTIC.** C5 states the reason: *"every scaled row aligns the independent TC-T
   crosscheck to the frozen path and is therefore DIAGNOSTIC"*. C6 labels only E1's ("at the diagnostic Lambda").
   The others are presented bare.
2. **All of them are against the clause C5-T replaced.** C5's adjudicator adopted C5-T as the authoritative
   transport. At cell 309 the baseline Γ moves from `+0.004661130` (frozen) to `+0.001708896` (C5-T) — every
   frozen-clause margin at 309 is ≈ **0.00295 pessimistic**. The A1 row "closes 309 by 0.00035" becomes ≈ 0.0033
   under C5-T; penalty improvement is 1.211–1.295 % per cell. C6's `planning_only_leverage_ranking` is built on
   these unlabelled numbers.

**And the omission that matters most.** C6's A1 entry says: *"leverage_achievable: NOT QUANTIFIABLE without the
replay… C6 does not guess it."* C5 **already quantified it**, in `C5_FORECAST.json`:

```
4_source_supply_cut_that_would_void_it_percent:
    candidate_sup_norms_supF_supD_supH              = 2.0561597 %   (under C5-T)
    candidate_sup_norms_under_the_FROZEN_clause     = 5.5356915 %
5_can_a_tighter_transport_void_it.but:
    "a 2.0562% tightening of the candidate sup norms would void the exclusion, and route A1 which would
     deliver exactly that is DATA-blocked, not refuted."
```

So the *requirement* side is known to four decimal places, and C5 names A1 as the route that supplies it. C6's
"NOT QUANTIFIABLE" is true only of the *delivery* side (how much slack the certifier's sup routine has). Stating
one without the other makes A1 look less tractable than the committed record shows, in a ranking whose only
purpose is planning. **Required:** carry 2.0562 % (C5-T) / 5.5357 % (frozen) into the A1 entry, and label every
quoted oracle as DIAGNOSTIC and frozen-clause.

---

## L. Are C4's and C5's scoped conclusions still correctly stated?

**PASS_WITH_NOTES.**

**The 0.944 % figure.** Verified from two independent C5 artifacts: `C5_ADJUDICATION.md` — *"`Gamma = +0.001709`
at `B = 3.297250282`, **0.944 %** of critical `A0`"* — and `C5_FORECAST.json`
`2_margin_in_C4s_own_currency_critical_A0 = {critical_A0_C5T: 3.266415728, C4_certified_floor_B: 3.297250282,
slack_percent_C5T: 0.9439874, slack_percent_frozen: 2.5827058}`. C6 writes *"C5-T left the cell-309 exclusion on
0.944 % of critical-A0 slack"* — correct, correctly attributed to C5-T, and in C4's currency (critical `A0`),
where C4's own published figure was 2.583 %.

**Compliance with C5's binding conditions.** `grep` over the whole C6 namespace: **2.583 % / 2.58 % never
appears**. That satisfies C5's disposition note 1 (*"C4's 2.583 % may not be quoted again without the 0.944 %
beside it"*) and binding condition 2 (*"Any restatement must name the C5-T clause and carry the margins in
`c4_exclusion_fragility`, not C4's 2.58 %"*). Condition 1 (no restatement without re-deriving under one's own
clause or executing E2) is satisfied in substance: C6 has no clause of its own and quotes C5-T's own figure
rather than re-deriving a number it has no standing to produce.

**C4's E2 figures.** `3.297250282` is C4's certified `Λ₃₀₉` lower bound (`C4_CERTIFICATE.json`
`lower_bound_float: 3.297250281519544`), and the Monte-Carlo truth is `4.04731 ± 0.00092` per C4's adjudication.
C6's *"3.297250282 against a Monte-Carlo truth near 4.047"* is accurate, and C6 correctly keeps E2 as needing a
**certified** lower bound (the MC is uncertified — C5 flagged exactly this when it re-opened E2).

**C5 closed nothing.** Verified: `C5_FORECAST.adopted_cells = []`, `C5_PRIMARY_CLASS = "MARGINAL"`, B0 check
`B0_04_c5_adopted_empty` re-runs true, `c5_adopted: []` in C6's B0 artifact, `c5_conditions: 11`,
`c5_verdict_scope_limited: true`, handover string matched. C6 states this correctly throughout.

**The omission.** C6 nowhere carries two C5 scope limits that a C7 reading C6's ranking will need:
(i) C5-T's premise `x_lo > 0` **fails at cell 0** (both detectors), so C5-T is not a blanket clause — and cell 0
is the one cell the single real order-3 probe closed; (ii) C5's exhaustion result is of the **transport family
only** and *"may never be restated as deterministic exhaustion"*. C6 misstates neither, but a forensic successor
whose output is a route ranking should carry the scope sentences attached to the routes it ranks.

---

## Ruling: is the frozen gate genuinely prospective?

**Temporal integrity: verified clean.** `git cat-file -p 59513c86:…/FEASIBILITY_GATES_C6.json | sha256` =
`03c5643335602071e5c6e5e558d20e39d0fc40e81f8d25d0ac00a93c94801fba` — identical to the working tree, so the gate
has not moved since the freeze. `59513c86` adds **exactly one file**. At `59513c86`, both
`evidence/leverage/C6_CLASSIFICATION.json` and `code/c6_classify.py` are **ABSENT**.
`git log --all --name-only -- '*C6_CLASSIFICATION*'` returns exactly one commit, `756a6d93`. `git fsck
--lost-found` surfaces one dangling commit, `1301f8bb` — the unrelated 2026-09-01 P6 screening-array commit that
C5's adjudicator already identified. No backdating, no hidden tree.

**Prospective in the sense that matters? Partly. Here is the finding the gate explicitly asks for.**

*Not fitted:* the **six classes** are generic. I applied them mechanically to a route the gate did not anticipate
(E1) and they produced a **gap**, not a convenient answer — which is precisely what an unfitted taxonomy does.
The **P4 minimum** is not fitted either, and the evidence is that C6 **fails it**: every recovered object lands at
P3 and `admissible_for_NEW_scientific_reuse` is `false` across the board. A threshold written to be passed does
not get missed by the campaign that wrote it.

*Fitted:* the **`already_adopted_exception`** is shaped to the outcome. It is the clause that lets four P3 records
be reported as `RECOVERED_ADMISSIBLE`, it was written into a gate frozen *after* those records were already in
hand and hash-verified (phases 3–5 are in `7dae3080`, 70 seconds before the freeze), and it carries its own
anti-abuse rider (*"may not use the exception to manufacture a P4"*) — an author writing a rule for an unknown
future does not usually need to fence it against himself. C6 **uses it correctly** and states the basis every
time, as required. But it should be read as a **disclosed accommodation for evidence already in hand**, not as a
prospective rule, and an adjudicator should weigh it that way.

*The handling of the gap is a defect.* The gate's refusals say *"no class… may be amended after freeze; an error
is recorded in an erratum"*. E1 fits no class; C6 took the nearest one and recorded nothing. That is the one place
where the post-hoc freeze actually cost something.

**Net:** the disclosure is honest and complete, the temporal integrity is provable, the classes and the P4 floor
are not fitted, and the outcome was constrained rather than flattered by them. The `already_adopted_exception` is
the exception, and C6 flagged the need for scrutiny itself.

---

## Ruling: is "the project is missing a TOOLCHAIN" an honest headline?

**Half honest, half rhetorical softening. It must be rewritten.**

*Honest:* numpy and python-flint really are absent (verified: `pip list` → one package; every relevant
`find_spec` → `None`), the E1 inputs really are committed, and the frozen chain really is present. "Not missing
DATA" is **true and is C6's genuine contribution** — it retires C5's belief that the payloads were sitting in a
90 MB store waiting to be fetched.

*Rhetorical:* three ways.

1. **It conflates inputs with results.** For A1 the toolchain buys the *candidates*; the *tightening* has never
   been derived by anyone, and the frozen identity gate guarantees a replay will not derive it (§G.2). For E1 the
   toolchain buys a *re-run*; a *better tuple* has never existed. "Nothing was lost; nothing needs to be
   re-derived" is false of both results.
2. **For E1 it restates C5.** C5's ledger already said python-flint is absent; C5's adjudicator already
   recommended "a host that has python-flint". Presenting this as C6's "strongest reclassification" inflates a
   relabel into a discovery.
3. **"Missing a toolchain" is softer than "we cannot do this work here" in exactly the way that matters** — it
   implies `pip install` is the remaining obstacle. The obstacle is: a governed certifying host, a replay whose
   output is provably identical to the sealed record, and *then* new certified work whose result no one has ever
   computed, under an authorization C6 does not have and cannot grant.

**Defensible replacement:** *"For A1 and E1 the project is not missing data. The inputs are committed or exactly
regenerable from committed code. Obtaining the gain still requires new certified work, on a host with numpy and
python-flint, that no campaign has performed — a replay reproduces the adopted values by construction."*

---

## Ruling: is the recovery NOT_LOAD_BEARING, and was C6 worth running?

**The claim is correct. C6's method for establishing it is not adequate, and I had to redo it.**

C6's phase-6 check greps **one file** (`c5_common.py`) for five substrings. That is not a chain traversal, and it
would have missed the truth: the chain `c5_common.frozen_stack()` loads **does** contain a raw-record reader.
`c5_common` → `c2_d5_forecast` → `tail_forecast_r2`, and `tail_forecast_r2.adopted_state(records_dir)` calls
`A.read_records(KM, records_dir, cover, manifest)`; `c2_d5_forecast.main()` invokes it with `--records DIR`. Any
grep of the *loaded chain* for `aux5` or `records` would have fired.

The conclusion nonetheless **holds**, and I verified it on the call graph rather than on text: C5 never calls
`adopted_state`. `c5_common.committed_inputs()` reads `ADOPTED_TAIL_INPUTS.json`, `cells.json`, `REGISTRY_C1.json`,
`REGISTRY_C2.json`; `cell_supply()` reads `TCT_INPUTS_{cell}.json`; and the consumer
`c2_d5_forecast.direct(T, R, meas, aux, A, ad, cov, KM)` touches only `meas`, `aux`, `ad` and `cov` —
`Gam = (R_interval.hi − e0·D_interval.lo) + rho·x_hi·M`, all from the derived committed extracts. `knock()`
implements the A1 oracle by scaling `meas["r"][r]["sup"][F|D|H]`, i.e. the **TCT_INPUTS** values. No raw record is
opened anywhere in the C5 path. So recovering the records changes no field the clause consumes and cannot move
any Γ. **NOT_LOAD_BEARING is right**, and C6 deserves credit for saying so instead of dressing the recovery up —
this is the most creditable single decision in the campaign.

Incidentally the recovery buys slightly more than C6 claims: with local copies a C7 can re-run not only the
`tct_inputs` identity gate but `tail_forecast_r2`'s extract-faithfulness assertions (that every adopted field is
byte-faithful to the record it claims to copy). Still reproducibility, not science.

**Was C6 worth running? Yes — but not for the recovery, and C6 should say that in those words.**

The recovery is worth roughly nothing: four files that duplicate bytes the programme already adopted, capped at
P3, feeding a consumer that never opens them. If that were all of C6, it would not have been worth the campaign.

What justifies C6 is three cheap, durable results:

1. **It falsifies a binding instruction.** C5's adjudicator Condition 11(b) directs the successor to retrieve
   candidate payloads from the external store. Those payloads **do not exist** — 0/326 records, 0/10 committed
   records, under a regex wider than C6's, with no JSON array longer than 10 elements anywhere in a record. A C7
   obeying Condition 11(b) would have spent a campaign hunting a file that was never written. Removing a wrong
   instruction from the record of a programme this heavily conditioned is worth more than most tightenings.
2. **It repairs a real ledger inconsistency** (D4: `DATA` + `new_real_required: true`), mechanically, and
   reclassifies the route correctly.
3. **It proves B1 rather than asserting it** — and my extra token (`subdivision_depth`, null in all four records)
   makes that proof stronger, not weaker.

Against those: C6 also ships a headline a hurried reader will take as *"install two packages and A1 is done"*,
which is the opposite of useful and is the single thing most likely to cost the programme a campaign. **Net
positive, conditional on the headline being fixed.**

---

## Ruling: does anything in C6 license closing a cell, r6, exhaustion, or the R-stage?

**No. C6 is clean on all four, and this is the part I attacked hardest for false comfort.**

* `C6_conclusions_withheld` sets `K5_cells_closed: null`, `coverage_map_revision: null`,
  `broader_deterministic_exhaustion_established: false`, `R_stage_prerequisite_satisfied: false`.
* **r6:** none exists. B0 check `B0_08_no_r6` scans `CP.rglob("K5_COVERAGE_MAP_*.json")` for `_R6`; I re-ran it
  (true) and confirmed r5 `e2197051…` is authoritative and unmodified.
* **Exhaustion:** `grep -rni "exhaust"` over the namespace returns only the **negative** uses (the gate's
  prohibition, the withheld-conclusions block, and `p5y_k5_tail_c5_exhaustion` as a *path component*). The token
  `DETERMINISTIC_TRANSPORT_FAMILY_EXHAUSTED` does not appear at all.
* **Closure:** adopted set unchanged; no cell is reported closed, tightened or adopted; `ranking_is_planning_only`
  is stated explicitly and the ranking carries no Γ.
* **R-stage:** no authorization, launch notice, countersignature or amendment artifact exists in the namespace;
  `REAL_SCIENTIFIC_COMPUTE = DENY` appears in every evidence file;
  `new_real_scientific_addresses_evaluated = 0` and `scientific_kernel_evaluations = 0` throughout — and are
  *true*, since the host cannot import flint.
* `git diff 69bff424 756a6d93 --name-only` touches **only** paths under `p5y_k5_tail_c6_evidence_recovery`. No
  predecessor artifact was modified; C2/C3 seal manifests re-verify at 156 and 21 entries, 0 deviations.

---

## Section verdicts

| § | Item | Verdict |
|---|---|---|
| A | Bytes predate C6 | **PASS** |
| B | Provenance chains real; P3 cap honest | **PASS_WITH_NOTES** |
| C | `production_run` / `result_bearing` not interpreted | **PASS** |
| D | Scientific identity | **PASS_WITH_NOTES** |
| E | No hidden recompute; artifacts reproduce | **PASS** |
| F | Old address not mistaken for new | **PASS_WITH_NOTES** |
| G | New address mislabelled as replay | **PASS_WITH_NOTES** (material overreach at route level) |
| H | External evidence unmodified | **PASS** |
| I | AWS not contacted | **PASS** |
| J | Per-route classification | A1 **PASS_WITH_NOTES**, A3 **PASS**, D4 **PASS**, E1 **FAIL**, B1 **PASS** |
| K | Leverage against r5 / the live clause | **PASS_WITH_NOTES** |
| L | C4/C5 scoped conclusions | **PASS_WITH_NOTES** |
| — | Gate prospective / not fitted | **PASS_WITH_NOTES** |
| — | "Missing a TOOLCHAIN" headline | **FAIL as written** |
| — | NOT_LOAD_BEARING | **PASS** (conclusion) / method inadequate |
| — | Licenses closure, r6, exhaustion, R-stage | **PASS — licenses none** |

## Required corrections before adjudication (all by erratum; nothing needs re-running)

1. **E1's class.** Record that the gate's six classes have no slot for *inputs-present, zero-new-real
   certification required, toolchain-blocked*, and that E1 was placed in the nearest class. Withdraw "the
   strongest reclassification in C6"; C5 already recorded the python-flint block.
2. **A1 and the headline.** Add C6's own A3 sentence — *"Replayability gets the inputs, not the result"* — to A1,
   and rewrite the headline so it does not assert that nothing needs re-deriving. Note that
   `tc_producer.identity_gate` guarantees a faithful replay reproduces the adopted values exactly.
3. **Binding independence.** Correct `independent_committed_bindings` for 306–308 (one root binding + one
   verified transcription; `ADOPTED_TAIL_INPUTS.manifest_sha256` = the export manifest's sha256). 309 keeps two.
4. **Leverage currency.** Label every quoted oracle **DIAGNOSTIC** and **frozen-clause**; carry C5's quantified
   requirement, 2.0562 % (C5-T) / 5.5357 % (frozen), into A1 instead of "NOT QUANTIFIABLE".
5. **Frozen chain.** Derive the chain transitively and hash the closure, including `aux_collocation`, `ancestry`,
   `cusum_layer1`, `cusum_layer2`, `opnorms`, `sharp_norms`, `sharp_certifier` and
   `rebaseguard-proof/src/rebaseguard_certify/` — which lies outside the tree C6 scanned. (All are present; I
   checked. The claim is true; C6's evidence did not show it.)
6. **"Never serialized anywhere, ever."** Qualify to *the candidate polynomials*; the suprema
   `cert.sup[fam,r,0]` are committed in `TCT_INPUTS_30{5..9}.json` for every tail cell.
7. **Minor, worth fixing while open:** record `production_run`/`result_bearing` for all four cells; state
   `subdivision_depth: null` in the B1 evidence; drop "ONLY Chebyshev payloads"; do not state "24 iterations" as
   a flat fact (306 is 25); note that `B0_18` is a hard-coded `True` and therefore vacuous, so "19/19" is really
   18 checks plus a label.

None of these touches the guard, the mutation count, the AWS boundary, the four forbidden conclusions, or the
verified forensic core. All are corrigible in text.

HANDOVER: READY_TO_ADJUDICATE_WITH_NOTES
