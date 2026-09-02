# What failed in P8, what P8R repairs, and what it deliberately does not

## 1. The authoritative finding

`P8 = FAIL`, 16 PASS / 5 FAIL, fixed by
`p8_model_class_robustness/INDEPENDENT_ADJUDICATION.md` at commit
`5411e2c7c5ff9af2fb983a5b5a48c1e360bca2e8`. Four of the five failures were
*scientific* (`G4`, `G4-D`, `G4-F`, `G7`). The fifth, `G14`, was procedural, and
under P8's own frozen verdict rule an integrity-spine failure forces `FAIL`
regardless of everything else.

Verified independently at the start of this campaign: exactly one commit in the
repository's history touches the P8 namespace (`5411e2c`, the adjudication
commit that first tracked it), and nothing after it modifies any P8 file.

## 2. The `G14` defect, decomposed

| # | defect | what P8R does instead | checked by |
|---|---|---|---|
| D1 | **No pre-result temporal anchor.** The P8 tree was untracked; filesystem birth times were the only ordering evidence. | Checkpoint A is a real commit containing the protocol, gates, plans, the complete executable surface, the tests and the digests, and **no** production result. | `I1` reads `git ls-tree` of the anchor and fails if any `results/` file other than the pre-campaign protected-tree manifest is present |
| D2 | **Declared budget ≠ executed budget.** `EXPERIMENT_PROTOCOL.md` §5 said E2 used 250,000 cycles per search evaluation and 2,048,000 for verification; the executable and every artifact used 163,840 and 1,024,000. | Every budget exists in exactly one place, `config.py`. Prose quotes it; it never restates it independently. | `I13` re-derives the executed counts from the stored trace and compares them to `config` |
| D3 | **Result-driven amendment.** Amendment `A2` added a 614,400-cycle refinement phase *after* the first-pass verification was seen to miss. | The search is fixed-length and non-adaptive: `CAL_S1_ITERATIONS` then `CAL_S2_ITERATIONS` evaluations, no early stop, no best-of selection, no phase that can be added later. If the holdout rejects, the **pre-frozen** retry ladder runs; if that rejects, the family is `CALIBRATION_FAILED`. | `I7` (config byte-identical to the anchor), plus a test that the search body contains no `break` and no `min`/`argmin` |
| D4 | **Reused acceptance address.** The refinement re-verified at `("p8_sr_calibration_verify", batch=7)` — the very sample whose failure triggered it. | Three separate address classes. `CAL_VERIFY_1` is read once per family and never again. The retry's acceptance sample is a pre-reserved second class, `CAL_VERIFY_2`. There is no third. | `I4` plus `tests/test_address_separation.py`, which checks the executed trace and the class tag digests |
| D5 | **Unverifiable protocol integrity.** P8's provenance record hashed neither `THEORY.md`, nor `EXPERIMENT_PROTOCOL.md`, nor `CLOSURE_GATES.md`, and recorded source only after source had changed. | `PROTOCOL_DIGEST.json` hashes every frozen prose artifact; `SOURCE_MANIFEST.json` hashes every executable file; both are committed **in** the anchor. | `I2`, `I3`, `I6` compare the working tree and the anchor blob, from git |

## 3. What P8R does **not** repair

These are scientific findings. They are re-asked under frozen rules and reported
as they come out. None of them is a repair target, and no threshold protecting
them may move (`I7`).

| P8 finding | status in P8R |
|---|---|
| `G4`: the cross-family window-separability law is rejected (spreads 22.7%, 36.0%, 49.3% against a 10% bound) | re-asked as `S7` with the identical 10% threshold |
| `G4-D`: detector invariance of `K` is rejected (`t5`/`m=5` residual 3.63% against 3%) | re-asked as `S7D` with the identical 3% threshold |
| `G4-F`: family invariance of `K` is rejected | re-asked as `S7F` with the identical 10% threshold |
| `G7`: literal P7-boundary transfer fails (4 of 6 families, 5 required) | re-asked as `S10` with the identical 5-of-6 rule, on an explicitly declared sub-family grid |
| detector transfer is **measured absent** in the tested cells | re-asked as `S12` under a symmetric pre-frozen rule that can return `SUPPORTED`, `REJECTED` or `INCONCLUSIVE` |
| `P8-T1` is a **conditional** theorem | inherited as conditional; `S15` and `LIMITATIONS.md` keep it that way |
| the `t3`/`m=20` attraction claim is **not certified** | re-asked as `S15` under a deliberately conservative three-way rule |
| P8's Gaussian SR estimates sit 0.7–0.8% below P3 while agreeing with P7 — a `KNOWN_PREEXISTING_DISCREPANCY` | re-asked as `S16`; P8R does not own or resolve the P3 numbers either, and the frozen decision table can also return `NEW_DEFECT_CANDIDATE` |
| novelty is not independently adjudicated | `NOVELTY_STATUS = NOT_ESTABLISHED`, permanently, for a repair campaign |

## 4. What P8R inherits unchanged, and why

The P8 adjudication verified two things about the implementation that would be
wasteful and risky to rewrite:

* `WINDOW_EXTRACTION = EXACT` — the ring-buffer window was checked against an
  independent naive reference across 1,024 stopped paths, every window size and
  the 255/256/257 and 4095/4096/4097 boundaries, with a maximum discrepancy of
  `8.881784197001252e-16`;
* `P8_CRN_IDENTITY = PASS` — the addressable-primitive layer, itself the output
  of the successful P6R2b Gate-9 repair.

P8R therefore copies `families.py`, `detectors.py`, `stopped.py`, `chain.py` and
`analysis.py` byte-for-byte (each carries a provenance note) and rewrites only
what the defect touches: a new `addressing.py`, a `primitives.py` that requires
minted tags, a new `calibrate.py`, and a `config.py` that is the single budget
authority. `tests/test_crn_identity.py` re-proves both properties for P8R's own
address system rather than citing P8 for them.

The **entropy namespace is new** (`0x50385F52_4D435201`, distinct from P8's
`0x50385F4D_43520001`), so P8R is an independent seed realisation of the same
estimands, not a replay of P8's field. Where P8R agrees with P8 that is
evidence; where it disagrees, `S13` and `S16` are the places that say so.

## 5. Runtime pilot, disclosed

Before the anchor, throughput was measured and the calibration update rule was
checked for convergence on a scratch copy of this tree at reduced budgets
(`level4/closure_proofs/_p8r_smoke/`, deleted before Checkpoint A). Two things
came out of it and are recorded here because they shaped the frozen protocol:

1. Wall-clock cost per row block, which fixed the production budgets in
   `PRODUCTION_PLAN.md`.
2. **`ARL_0` is not linear in the SR natural threshold `A`** over the range the
   contaminated families need — measured locally it behaves like `A^beta` with
   `beta` near 0.47. A plain proportional update would not reach the operating
   point within the frozen iteration count, so the frozen update is a log-log
   secant (`calibrate._update`). This is a statement about the *shape* of the
   `ARL_0(A)` curve, established from scratch runs at addresses no P8R result
   uses, and it fixes no verdict, no gate threshold and no estimand.

Neither observation is a production result and neither is used as evidence for
any `S`-question. The scratch tree is not part of the campaign and does not
exist in the anchor commit.

## 6. What would make P8R fail

`FAIL_CANDIDATE` if any integrity gate is `FAIL` **or** `UNVERIFIABLE`. In
particular: a result whose commit does not descend from the anchor; a frozen
prose file or `config.py` that differs from its anchor blob; a calibration trace
that touched a verification address; an executed budget that disagrees with the
declared one; a result artifact with no working generator; any protected tree
that moved.

`PARTIAL_CANDIDATE` if integrity holds but a mandatory question could not be
resolved at all.

`CLOSED_CANDIDATE` if integrity holds and every mandatory question is resolved —
whatever the resolutions are.
