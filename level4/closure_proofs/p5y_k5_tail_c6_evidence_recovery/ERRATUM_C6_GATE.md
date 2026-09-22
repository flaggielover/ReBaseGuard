# Erratum to the frozen C6 gate

`config/FEASIBILITY_GATES_C6.json` is frozen at commit `59513c86`, sha256
`03c5643335602071e5c6e5e558d20e39d0fc40e81f8d25d0ac00a93c94801fba`. It is **not amended**.

## E1 — the six classification classes have a gap, and route E1 falls into it

The gate defines `HISTORICAL_REPLAY_REQUIRED` as requiring that the exact address *"was already evaluated under an
authorized historical campaign and could be reproduced by a future governed replay"*.

Route **E1** — tighten `A0` by operator certification — does not satisfy that. Its object is a *better* operator
tuple `(tau, D_lo, Abar)`, which C6's own `existence` field records as `OBJECT_ONLY_HYPOTHESIZED`: **it was never
evaluated by anyone, so there is nothing to replay.** Nor is it `TRUE_NEW_REAL_REQUIRED`, because the work is
operator-only, evaluates no scientific address, and the programme has consistently classified it zero-new-real —
C1 and C2 each spent CPU-hours of exactly this work under `ZERO_NEW_REAL`. And it is not `PROVENANCE_INSUFFICIENT`
or `NOT_LOAD_BEARING`.

The class E1 needs is **inputs present, new zero-new-real certification work required, blocked by toolchain**, and
the frozen gate does not have it. The first version of the classification **forced E1 into
`HISTORICAL_REPLAY_REQUIRED` and recorded nothing**; the gate's own refusal list says an error is recorded in an
erratum, not absorbed by taking the nearest label. The classification now reports
`GATE_CLASS_GAP__nearest_is_HISTORICAL_REPLAY_REQUIRED` and points here.

A successor gate must add the class. Found by the independent forensic review, item J-E1.

## E2 — what the forensic review corrected, and what it cost

Seven corrections. Two were in the campaign's advertised product, and those two are the ones worth reading.

**(a) The headline conflated inputs with results — the material defect.** `tc_producer.identity_gate` *requires* a
replay to reproduce the sealed quantities exactly and refuses otherwise. So a faithful A1 replay returns the
adopted `sup{F,D,H}` **bit-for-bit and delivers exactly zero of A1's gain**, by construction: the identity gate is
what makes it a replay rather than a new evaluation. C6 wrote the correct sentence for route A3 — *"Replayability
gets the inputs, not the result"* — and then omitted it for A1, and closed the headline with *"nothing needs to be
re-derived."* That clause is **withdrawn**. A reader acting on it would have installed two packages, re-run the
replay, obtained the adopted numbers to the last bit, and spent a campaign confirming
`identity_gate.identical = true` for a fifth time.

**(b) "Never serialized — anywhere, ever" was false of half of C6's own object.** C6 defines A1's required object
as the candidate polynomials *and their suprema*. The suprema are committed, at exact rational precision, in
`TCT_INPUTS_30{5..9}.json` for every tail cell. The claim is true of the **polynomials** and is now qualified.

The remaining five, all corrected at source:

* **Binding independence.** `ADOPTED_TAIL_INPUTS.json` carries `manifest_sha256` equal to the export manifest's own
  sha256 — it **names the manifest as its source** — and `tail_forecast_r2` asserts its fields are a byte-faithful
  transcription of the records the manifest lists. So it is a *verified transcription*, not a second independent
  witness. Cells 306–308 have **one** root binding plus one transcription; 309 additionally has corroborating
  **bytes** committed in a different campaign. `independent_committed_bindings: 2` was the wrong label and
  `PROVENANCE_BOUND` was keyed to it.
* **Leverage currency.** Every oracle figure C6 quotes is **DIAGNOSTIC** *and* computed under the **superseded
  frozen clause**; only E1's was labelled. And C5 had already quantified A1's *requirement* side — a **2.0561597 %**
  tightening of the candidate sup norms under C5-T (5.5356915 % under the frozen clause) voids the cell-309
  exclusion — while C6 said "NOT QUANTIFIABLE", which made A1 look less tractable than the committed record shows.
* **The frozen chain was not established.** C6 hashed 13 top-level import names. The transitive closure is **59
  modules**, two of which lie **outside** the `level4/closure_proofs` tree C6 scanned (`level4/src/
  rebaseguard_level4/ledger.py` and the `rebaseguard-proof/src/rebaseguard_certify` package). All are committed —
  the conclusion survives — but C6's evidence did not show it. The closure is now walked and hashed. (One
  unresolved name, `which`, is a regex false positive on the docstring prose "from which three identities are
  derived".)
* **Scientific identity was asserted on a byte basis.** The conclusion holds — byte equality with an
  already-adopted artifact trivially implies equality of every attribute the gate lists, since each is a function
  of the bytes — but `SCIENTIFICALLY_IDENTICAL: true` next to `PROVENANCE_LEVEL: P3` is the shape of reasoning the
  gate's `byte_identity_is_not_scientific_identity` clause exists to forbid. Renamed
  `BYTE_IDENTICAL_TO_ALREADY_ADOPTED_BYTES`, with the argument stated.
* **Precision defects.** `production_run`/`result_bearing` are now measured for all four cells, not generalised
  from 309 alone. `subdivision_depth` is recorded as absent at top level, with the reviewer's stronger finding
  (nested and **null** in all four) carried. The flat "24 iterations" is replaced by the per-`r`, per-cell counts
  (r = 0 is 25 at cell 306, 24 at 307/308/309). The "ONLY Chebyshev payloads committed" claim is dropped.
  `B0_18` was a hard-coded `True`, so "19/19" was 18 checks plus a label; it now asserts that every DATA route
  declaring `new_real_required` appears in the recorded inconsistency list.

## E3 — the reviewer's ruling on whether C6 was worth running, recorded against C6's interest

The forensic reviewer's judgement, which C6 accepts: **the recovery itself is worth roughly nothing** — four files
duplicating bytes the programme already adopted, capped at P3, feeding a consumer that never opens them. What
justifies the campaign is three cheap results: it **falsifies a binding instruction** (C5's adjudicator Condition
11(b) directs a successor to *"retrieve the K1 object candidate payloads from the external record store"*, and
those payloads do not exist — 0/326 records under a regex wider than C6's, with no JSON array longer than 10
elements anywhere in a record); it **repairs a real ledger inconsistency** (D4 declared `DATA` *and*
`new_real_required`); and it **proves** B1 rather than asserting it.

The reviewer also found that C6's own `NOT_LOAD_BEARING` method was inadequate — it grepped one file for five
substrings, and the chain `c5_common` loads *does* contain a raw-record reader (`tail_forecast_r2.adopted_state`
→ `read_records`). The **conclusion survives** on the call graph, which the reviewer re-derived: C5 never calls
`adopted_state`, and the consumer touches only the derived committed extracts. C6's method did not establish its
own correct answer.
