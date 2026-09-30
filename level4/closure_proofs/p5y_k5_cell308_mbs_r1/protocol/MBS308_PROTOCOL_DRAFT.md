# Cell-308 MB-S successor campaign (r1): protocol DRAFT

**Status: DRAFT, NOT FROZEN.** Built by the builder (Phases 4–8) from the coordinator design
`research/governance/SUCCESSOR_ARCHITECTURE_308.md` and the binding review conditions (RC1, RC2, RC6, GC-6, GC-8, GC-10,
DR2, MBS-2/3/4/9/12). Nothing here authorizes a target evaluation: there is no freeze, no qualification, no grant and no
marker. **New cell-308 target evaluations: 0.** Cell 308 stays OPEN; r5 is unchanged; there is no r6; K5 and P5Y are
unchanged. Cell 309 is out of scope (S10).

## 1. Scope, authority and history

* One exactly-once, **closure-only** evaluation of CUSUM K5 cell 308 (m = 5) under route **MB-S**: the science of MB r1
  unchanged, with a new lifecycle. Order: freeze → official qualification → independent qualification review → the
  user's explicit S1 ruling → grant → `execute` (launchd) → execution review → adjudication → adjudication review.
* **USER_RULING_REQUIRED (governance S1).** The grant must carry, verbatim, the user's explicit ruling authorising a
  second consumed evaluation of cell 308 and re-affirming the C4 terms (U1–U8); the driver's `check_grant` refuses a
  grant whose `user_ruling_s1` is not a non-empty verbatim text with its sha256 and `reaffirms_c4: true`.
* **MB r1 is history only**: consumed (marker `refs/p5y-k5-cell308-mb-r1/target-consumed` → `afa93072`), interrupted,
  **CELL308_EXECUTION_INDETERMINATE, not scientifically negative**; no value of the lost run exists. MB-S never writes
  MB r1's refs, never reads them for arming, and asserts MB r1's recorded state exactly before it may consume (GC-8,
  §9). The adjudication must record that cell 308 has been consumed twice.
* **Closure is not adoption.** No floor change, no r6, no K5 / P5Y closure, no main-branch integration, no push.

## 2. The science and the criterion (carried over from MB r1, unchanged)

* **Theorem MB r1** (`NSF/theory/THEOREM_MB.md`), the decisions D1–D14 of MB r1 protocol §3 (partition, hulls,
  RLR ladder d 4/6/8, pointwise ladder C2b N 20/40/80 and C1b d 8/10/12, admission rule D5, envelope D6, members D7,
  D8, TPT-B consumer D9, what is computed on the target D10, workers / caps D11, primary vs independent D12, D13,
  verification budgets D14), controls C-A / C-B (before the marker), Stage 2 and the frozen criterion
  **Γ_dec := g_hi + max(P*_B, P_hi) < 0 in exact rationals** (Γ_dec = 0 does not close), and MB r1's section 5.4
  decision rule (`decide`), all unchanged. MB r1's protocol §3–§6 and §8 apply verbatim (read from
  `NSF/protocol/MB308_PROTOCOL.md`; that file is history and is not modified).
* **Determinism argument (S4).** The science is exact and deterministic (MB r1 QC04). With byte-identical science and
  pinned inputs, the successor's value is the value the lost run would have produced; no selection effect is possible.
  Checkpointed resumption preserves this: a resumed evaluation is **one evaluation, not a rerun** (§6).
* **RC1: what is unchanged, by path, sha256 and git blob** (the science modules are executed from MB r1's committed
  bytes at MB r1's paths, never copied; MB r1's research pins come with them):

| path | sha256 | git blob at 21e99cf0 | pinned by |
|---|---|---|---|
| `level4/closure_proofs/p5y_k5_cell308_mb_r1/code/mb308_a0core.py` | `0873604379bb5008f385ed09c7ae2f0694a402a91881b6a9d2e45649af332de6` | `379469a2c4e3432a64ca28fe318a7fd803cb8816` | MB r1 science module (SCIENCE_PINS) |
| `level4/closure_proofs/p5y_k5_cell308_mb_r1/code/mb308_stage1.py` | `23296f837eb7520b36c32bba08d238d940c14a8753e8ce8cadb05f0990f2ec98` | `518150ba19991894d6cdd2621f8e60ce9784313c` | MB r1 science module (SCIENCE_PINS) |
| `level4/closure_proofs/p5y_k5_cell308_mb_r1/code/mb308_supply.py` | `af1a818b68459ada53773557e10153ae4ae3edc232d52e93fd19814e4da59b58` | `8c4463e7191bb267ff7e2f00603b9c1a4f61ff18` | MB r1 science module (SCIENCE_PINS) |
| `level4/closure_proofs/p5y_k5_cell308_mb_r1/code/mb308_consumer.py` | `c233bdb6235cd8a44bcf187be7d6686a4684f8619bed21ade9130432c5c09188` | `2ffdfa631551065e5b0440a0edd09d92ff1a64cd` | MB r1 science module (SCIENCE_PINS) |
| `level4/closure_proofs/p5y_k5_cell308_mb_r1/code/mb308_pinned.py` | `5c221a0e70a708c580f13e1cd622556930f047f3c0b302227a8d9b18c52220a2` | `e714650d79aa0bb6ad644784403b0ce01accb78f` | MB r1 science module (SCIENCE_PINS) |
| `level4/closure_proofs/p5y_k5_tail_overnight_research/streams/C_308/LR/cusum/c1b_gauss.py` | `3189208d6c4ce37ce7dd1e013caf58ae454f35211fd36154b2afa8b96cd9c43f` | `61d756cb8dace8c1ed3adf3eb66f1132a62e7798` | mb308_pinned.PINS[c1b_gauss] |
| `level4/closure_proofs/p5y_k5_tail_overnight_research/streams/C_308/LR/cusum/c1b_kernel.py` | `dfdc871b18ff132a95ed98d7354e3e95fbbc749cc473629923e4dec19bc4c41e` | `b5b8dcf05724f067f2df337ab7900900be97dc40` | mb308_pinned.PINS[c1b_kernel] |
| `level4/closure_proofs/p5y_k5_tail_overnight_research/streams/C_308/LR/cusum/c1b_float.py` | `2a14067cd0c629f5d9b18a56bf66e439acd9802dc62a166e5ff5f7e2d5726f5f` | `6b3b8e23f6dd99e3512091474c2c7527e5817d25` | mb308_pinned.PINS[c1b_float] |
| `level4/closure_proofs/p5y_k5_tail_overnight_research/streams/C_308/LR/cusum/c1b_pw.py` | `f10c2cf14691e56699aa823800381d799eb6bdbdf47fdfcf5f28e1f1abb839d0` | `607fc7075446b1d8ca9853a6430f928ff4ae3e76` | mb308_pinned.PINS[c1b_pw] |
| `level4/closure_proofs/p5y_k5_tail_overnight_research/streams/C_308/LR/cusum/c1b_prov.py` | `d12c2a2183e6636ec3fa1379db8024c5402f6b7e1f8cb6f7ad11b3ce6d20cf47` | `530b4b222bcb9d21a41f45ca094bfe2ca4cc5b6d` | mb308_pinned.PINS[c1b_prov] |
| `level4/closure_proofs/p5y_k5_tail_overnight_research/streams/C_308/LR/cusum/c1b_certpw.py` | `48080dd4df193a1474113ea792ab550fe325f51cb0e4d0e1c8a3e3bebd195c25` | `807b64fed49a29546b1e4a81676529015bb01c75` | mb308_pinned.PINS[c1b_certpw] |
| `level4/closure_proofs/p5y_k5_tail_c7_e2_lambda309/code/c7_gaussian.py` | `bd73b5b46766ca4272cdf5db3c7258e45e81599e712f9984cd03a5455cea9815` | `be492720abb628184962b54440c99a971c8d9f0a` | mb308_pinned.PINS[c7_gaussian] |
| `level4/closure_proofs/p5y_k5_tail_overnight_research/streams/C_308/A0X/gen/c2b_common.py` | `2f059c0aa5761d571da6af82b86d0ab788d1a608740116c9f2cd59fc025d49b5` | `3960490f4b4165c14905a5a74452a9f78e2b823d` | mb308_pinned.PINS[c2b_common] |
| `level4/closure_proofs/p5y_k5_tail_overnight_research/streams/C_308/A0X/gen/c2b_exact.py` | `fb94e7cec4d2379ab5999c056410fcfc58ac5efee06a074b0c756619d238c8e5` | `49e72fe09a92c6f2776faf1203627a1c2f838f09` | mb308_pinned.PINS[c2b_exact] |
| `level4/closure_proofs/p5y_k5_tail_overnight_research/streams/C_308/A0X/gen/c2b_float.py` | `b33e3f908fc5166e80ebc7faf99a0aee537e93b5eba78ebe5ce9762aa7739d4f` | `fa24dfe4508d6eb1e8c0df997789925e1b5bbaa8` | mb308_pinned.PINS[c2b_float] |
| `level4/closure_proofs/p5y_k5_tail_overnight_research/streams/C_308/A0X/gen/c2b_certify.py` | `1c7e111be4cf50f1644decd98d4ce8f20526741f18a596d551cffa1f7993e8de` | `2d92ba8ec15a8dffd563f36820ddbd1edbab7917` | mb308_pinned.PINS[c2b_certify] |
| `level4/closure_proofs/p5y_k5_cell307_rlr_r1/code/rlr307_stage1.py` | `6fa9f69168d619a194c1e508e9bb264c01715998dc755e8bd481846758cf685f` | `cadb9f83d8be9f7ce5dd913fc1eb77b0f2e40ba8` | mb308_pinned.PINS[rlr307_stage1] |
| `level4/closure_proofs/p5y_k5_cell307_rlr_r1/code/rlr307_independent.py` | `91a75ea8f4c5a6183efc0eeec4eff3315abaafd92c4a4c8bc5d94c6d44cf94f4` | `85397b5538bd0906e3f92f7312b573d71ad94404` | mb308_pinned.PINS[rlr307_independent] |
| `level4/closure_proofs/p5y_k5_cell308_research/streams/VERIFY/vd_verify.py` | `cd4cec35e86d8036618a53c85d76f685d1475847af4fac9b879ba33c37cefc7f` | `2b50f8dd5c530b4e987cac66b4b8a4e37895392b` | mb308_pinned.PINS[vd_verify] |
| `level4/closure_proofs/p5y_k5_cell308_research/streams/VERIFY/vd_adapt.py` | `1b2acd616f3dc75b5cb812c0508977b001cd4f8d0518ca81513fcfb9907dc761` | `3ffc0fef9d483eca4c823de7368bd4f54be08237` | mb308_pinned.PINS[vd_adapt] |
| `level4/closure_proofs/p5y_k5_cell308_research/code/c308_quarantine.py` | `72d529cc352208fe6dc9c2045d991a799eb0fcca2f2fe3b2969cd5b7554faa12` | `e103c196ef0e393d9a7bca038ca8ab38d5841f11` | mb308_pinned.PINS[c308_quarantine] |
| `level4/closure_proofs/p5y_k5_cell308_research/streams/ASSEMBLY/tptb_tail.py` | `b373a8b4389b6e572a2297c069606c790b7e8bb6ede9e05619fc8308256862c2` | `1995004c6c499fb8c1af79e459bf684fe1bf47e4` | mb308_pinned.PINS[tptb_tail] |
| `level4/closure_proofs/p5y_k5_cell308_research/streams/ASSEMBLY/frozen_path_loader.py` | `97c0feb34e6fc31f436adbe1e5afa871e5f3ddaf28f9726dcc89fe1ca5fac18a` | `26fdb8f7580d8a619861b312a381f78b49aeb763` | mb308_pinned.PINS[frozen_path_loader] |
| `level4/closure_proofs/p5y_k5_cell308_research/streams/ASSEMBLY/decoy_gen.py` | `457472689cfcb70761707cde027c9f1ee971dd6edec4261ecdc84dedeae61ed6` | `621a7a56c142ef9656af021af36b535184227ddc` | mb308_pinned.PINS[decoy_gen] |
| `level4/closure_proofs/p5y_k5_tail_c2_closure/code/c2_d5_forecast.py` | `bd7854bce2434215c0a72eeb825ff87db4c729e80b0e4d125911e806a084f06b` | `18403dbec85513355414beb6869746703f7bbda2` | mb308_pinned.PINS[fp_c2_d5] |
| `level4/closure_proofs/p5y_k5_m5_tail_closure/code/tct_rule.py` | `f5a343e7f7bfb742d0a41c38512e27e7311d0919b38bcea0dfe98775c73d9a3e` | `98f6eee4d867455065e20043fcf47ae54ffcad1e` | mb308_pinned.PINS[fp_tctr] |
| `level4/closure_proofs/p5y_k5_lower_front_order3/code/tc_rule.py` | `8d402d11f6fc06ea2af88e3d3a01e376fefbe8ebacd8418f772116010e57afd5` | `ce101d175360a3a82b7eebc5a6ac4409a41f2f1d` | mb308_pinned.PINS[fp_tcr] |
| `level4/closure_proofs/p5y_k5_perron_deflated_resolvent/code/deflated_consume.py` | `ef5d0474183053bb7cde3075bda66f99211706a9bf7bf27e31fe994ff8b87e72` | `a0a836fa83c6d85d02bd377e8f2dc3ebfcc436ef` | mb308_pinned.PINS[fp_dc] |
| `level4/closure_proofs/p5y_k5_order3_readiness_audit/code/k5_minimality.py` | `3a54f0fb290a9b8a07c861653d4399e6c588afdaef77ee51473f778c6c988885` | `fbd624aaecbbfed4846970530e0c53db1f6d6a64` | mb308_pinned.PINS[fp_km] |
| `level4/closure_proofs/p5y_k5_tail_overnight_research/streams/E_assembly/tpt.py` | `05cebc9cd3278e1099ed2faf0c2ca5b32ee155f85be93654a80892873e4beab8` | `c6d4cdde3f04c8012672a6d5bd03654f96693c00` | mb308_pinned.PINS[fp_tpt] |
| `level4/closure_proofs/p5y_k5_cell308_research/streams/INDEP/mb_independent.py` | `32aa83a866005ad737424225ff8bfcb3898ebb79b3598e37d80a1e89a16ca4c0` | `8aacb252b57b85f1fe3444250fb3aec74b1dc5d5` | mb308_pinned.INDEP_PIN (F2) |
| `level4/closure_proofs/p5y_k5_cell308_research/streams/INDEP_TUPLE/tuple_independent.py` | `47ae88dcc792779b247ae1827e66c9f460a5e1b2c56e6b081a828ae245e6cbc8` | `86061897e6cc294223e35de3480e9503f18ce707` | mb308_pinned.TUPLE_PIN (F3) |
| `level4/closure_proofs/p5y_k5_cell308_research/streams/VERIFY/vd_pl.py` | `1f10c9506422adf11e001c05d39dda59c7081c595abae45a1540ab05e0aa1221` | `0764c0b11d7723a4d1d6a699a468ba2a1018e005` | mb308_pinned.C2B_PL_HOOK (vd_pl) |
| `level4/closure_proofs/p5y_k5_m5_tail_closure/code/tail_forecast_r2.py` | `5ab31ae56c0174697a7f5805e212b46334803e9e3371a77f82871d60716b96cd` | `edec817e57f162a7c2bc90300bc6dc64e8d830ff` | mb308_consumer.PINS[tail_forecast_r2] |
| `level4/closure_proofs/p5y_k5b_consumption_adapter/code/consumption_adapter.py` | `fbad7d33261fd47fc56c034d6a016f8427b81b51f9199f0e3a8f3e74df35973d` | `0516a15b2d832e4f7681d5dc770afaa06ca02862` | mb308_consumer.PINS[adapter] |
| `level4/closure_proofs/p5y_k1_cover_ledger_successor/config/cells.json` | `341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f` | `30e40fc0e7213fe54cc30cd1f18fa61cdbef03d8` | mb308_consumer.PINS[cells_json] |
| `level4/closure_proofs/p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json` | `29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334` | `e6e0e26e25831a9c88ef44c2801f49bc5647ebd8` | mb308_consumer.PINS[record_manifest] |
| `level4/closure_proofs/p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json` | `485fb1254e459683f48815c239d18d29119d651d0e77876f772c3fee9d29a37d` | `0ba3c6dc876ff6b27406a584a28f7e1a80e95f62` | mb308_consumer.PINS[adopted_inputs] |
| `level4/closure_proofs/p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_305.json` | `e1390b427e5f7dcf2f997fe039ea3658554cba86f6e472f3c8f339ac0e93df76` | `499ccafe5cc90908ab8c97f6f228ee49eab5dd21` | mb308_consumer.PINS[tct_inputs_305] |
| `level4/closure_proofs/p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_308.json` | `386f4a7774d69b0c319918fc6f4aa010ae6a8c349fca941c24e13a2111c418c2` | `866ddab11c9b17e9a26055c51f04c7c2c456631e` | mb308_consumer.PINS[tct_inputs_308] |
| `level4/closure_proofs/p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json` | `87bb1cfacb09c2a144cab0270427d91980ea742b36fd80f8963265a22d2eebb3` | `f6d84bdb5ef078fdd51667b0d44e8622049be7e6` | mb308_consumer.PINS[registry_c1] |
| `level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json` | `1b2b834939fcd80a81ddc8f029f46705b53cefeb46c0cc925a99c2b8e856fdd6` | `1a3adfd3d893790498f9776d32121deb76469077` | mb308_consumer.PINS[registry_c2] |
| `level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json` | `784f25eecd65bad3bf687727590a0c0e91a683c5d30817c3bda80d6f373fe983` | `a191557f24c305824f88e39edec38edaf9c49b48` | mb308_consumer.PINS[c2_forecast] |
| `level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json` | `e2197051e493df898295a692c580ed676e771f7dfae5a1675d8d8e9b979f684c` | `f978eeb6b41188eabaf3c6d590c9178d711f1ce6` | mb308_consumer.PINS[coverage_r5] |
| `level4/closure_proofs/p5y_k5_tail_floor_r2/config/K5_TAIL_ADOPTION_FLOOR_R2.json` | `eb2b4196dd23a8353e25093ff6bfa30d18634dd7f52968ec3c7000ea9b624238` | `0ddfac300b9219984188a4f6aede60efc25c4434` | mb308_consumer.PINS[floor_rule] |

45 distinct files.


  In `code/mbs308_driver.py` every science-glue function is **text-identical** to MB r1's driver at `c46434a3`
  (== `21e99cf0` bytes): controls, compose_and_consume, decide, target_geometry, admitted_pairs, prepare_target,
  stage1 and public_stage1 (the Stage-1 admission and aggregation rules), load_science, _worker_init, _worker_job,
  _set_job_cap, _ser_block, evaluate_target, failure_kind, the decoy / rehearsal helpers and the plumbing they call.
  `tests/test_mbs308_static.py` asserts this by AST source segments, and (MBS-9 i) closes over every module-level name
  they reference: every referenced def, import and assignment is text-identical except a listed, reasoned set (the
  guard, the host module, the four science-module handles executed from pinned bytes, `ProcessPoolExecutor` / `wait`
  rebound to the checkpointing pool, the helper-pin table and the lineage). `code/mbs308_guard.py` differs from
  MB r1's guard in exactly one line, the marker constant (GUARD_DIFF.md; asserted). DRIVER_DIFF.md classifies every
  hunk of the driver diff.

## 3. Identity

* Namespace `level4/closure_proofs/p5y_k5_cell308_mbs_r1` (NSS); branch `p5y-k5-cell308-mbs-r1` from `21e99cf0`;
  worktree `/Users/suzhe/ReBaseGuard-c308mbs`; git dir `/Users/suzhe/ReBaseGuard/.git/worktrees/ReBaseGuard-c308mbs`.
* Refs: `refs/p5y-k5-cell308-mbs-r1/target-consumed` (marker → grant commit), `…/journal` (→ journal blob),
  `…/ckpt` (→ checkpoint tree), `…/pending-result` (→ result blob).
* Spool: `<git dir>/mbs308-spool/` (0700; outside the worktree; never tracked; never /private/tmp): `result.json`,
  `result.json.tmp`, set-aside files `*.rejected-<reason>-<utc>-<nonce>` (never read again), `driver.pid`,
  `recover.lock`, `host-events.jsonl`, `launch/` (transient plists).
* Result path: `NSS/evidence/execution/MBS308_CELL308_RESULT.json` (schema `rebaseguard.p5y.k5.cell308-mbs-r1.result.v1`).
* Grant `NSS/authorization/MBS308_GRANT.json` (schema `…grant.v1`, route `MB-S`), chain freeze → qualification
  (`NSS/qualification/MBS308_QUALIFICATION.json`) → review (`NSS/review/MBS308_QUALIFICATION_REVIEW.md`, line 2
  exactly `QUALIFICATION_ACCEPTED`) → grant, binding the driver sha256 and the manifest `NSS/protocol/MBS308_FREEZE.json`.

## 4. The durable state machine (architecture §2, as built)

`status` is read-only and deterministic: it classifies from refs, the spool, the journal, the process table, the boot
session UUID and the current platform readings, and prints **the state name only**. `recover` is the only dispatcher and
performs exactly the frozen action.

| state | defined by (checked in this order) | `recover` action |
|---|---|---|
| NO_TARGET_CONSUMED | no marker (a stale pre-marker ARMING journal, or a sealed CONTROL_FAILED record, may exist) | none (`execute` only at a valid grant; it takes over a stale intent) |
| SEALED | the branch holds the result path and its blob verifies with status TARGET_EVALUATED | materialize if missing; journal catch-up |
| INDETERMINATE | the branch holds the result path and the record is the value-free INDETERMINATE record, a post-marker failure status, or fails verification | materialize if missing; terminal, no rerun |
| PENDING_RESULT | the pending ref names a blob whose bytes verify | seal-only: seal → materialize |
| RESULT_DURABLE_UNSEALED | `result.json` in the spool verifies (a stale pending ref is recorded and replaced by CAS from its stale value) | seal-only: object store → pending → seal → materialize |
| CONSUMED_UNRECORDED | marker and: no journal, an invalid journal, a journal not bound to the marker's grant / granted driver, a CLOSING / ABORTED_INTENT journal, the journal's checkpoint tree not contained in the ckpt ref, a job with 2 consecutive checkpoint failures, the resume budget exhausted, the 7-day deadline passed, or **the platform changed (RC2 / DR2)** — all only when the recorded process is positively dead (see *Liveness* below) | close-indeterminate (value-free record) |
| CONSUMED_COMPUTING | marker, journal ARMING … PENDING_RESULT, and the recorded process identity (pid, start time, boot UUID, command sha256) is **not positively dead**: ALIVE (every field matches under the **same boot UUID**) or UNKNOWN (a `ps` or boot-UUID reading failed; see *Liveness* below) | wait; `resume`, `close-indeterminate`, `seal-only`, `execute` refuse |
| CONSUMED_INTERRUPTED | otherwise (the recorded process is positively dead: its pid is gone, the pid belongs to another process, or the boot UUID changed; or no process identity is recorded; checkpoints permit; budget and deadline remain; same platform) | `resume` (mandatory) |

**Liveness of a recorded process identity (liveness delta; REVIEW_IMPLEMENTATION_MBS308_DELTA_R3 §3).** The
classifier's CONSUMED_COMPUTING test, the O_EXCL recover lock (`Lock.acquire`, taken by `execute`, `resume`,
`seal-only`, `close-indeterminate` and `recover`'s lockfile move) and the git-lockfile staleness test below use one
rule: a RECORDED identity counts as alive unless `HOST.identity_state` finds positive evidence of death (the boot UUID
changed, the pid does not exist, or the pid now belongs to another process: another start time or command). A failed
`ps` or boot-UUID reading is UNKNOWN, never evidence of death, and a field that was never recorded is never compared.
No recorded identity (none, or a record naming no pid) means no process. **Fail-closed consequence:** while `ps` keeps
failing for a recorded pid that still exists, or the boot-UUID read keeps failing at all, the run stays
CONSUMED_COMPUTING (`recover` waits, exit 8; `resume`, `close-indeterminate` and `seal-only` refuse) and a recover lock
naming that identity is never broken (LOCKED). There is no timeout: however long the failure lasts, nothing resumes,
seals or closes while the recorded process may still be running. It ends only on positive evidence, when the boot UUID
reads again and either differs from the recorded one (a reboot) or the recorded pid is gone or belongs to another
process; the table above then applies as written (a deadline that passed meanwhile gives CONSUMED_UNRECORDED and
close-indeterminate). The two other users of the stricter all-fields-match test are unchanged by this delta: the
pidfile's LIVE / STALE reading (the preflight's other-job gate) and `check_not_evaluated`'s stale pre-marker intent
takeover (before the marker; the marker CAS decides).

**Stale git lockfiles (repair R1 iii; correction C-1; note N-3).** Every classification also lists the campaign's git
lockfiles (`refs/p5y-k5-cell308-mbs-r1/*.lock` and the branch lock: what a reset inside one of the campaign's own ref
writes leaves). They are **stale** only when every recorded campaign process (the O_EXCL recover lock's holder, the
pidfile, the journal's recorded process) is positively dead (a failed `ps` or boot-UUID reading is UNKNOWN, never
dead) and no process has any of them open (`lsof`). They do not change the state. `recover`,
in every state except CONSUMED_COMPUTING and **before** resume / seal / close, performs the frozen, recorded,
value-free action: under the O_EXCL lock it re-verifies staleness and **moves** each lockfile into
`<spool>/git-locks-aside/` (never deletes it; never renames it inside `refs/`, where it would read as a ref), appending
one record (name, size, birth / change times, destination, who) to `<spool>/recover-actions.jsonl`. Held (not stale)
lockfiles: `recover` does nothing and exits 8. `execute`, `resume`, `seal-only` and `close-indeterminate` refuse
`GIT_LOCKED` while any campaign lockfile exists. A durable pre-marker intent whose marker write failed
(ABORTED_INTENT, no marker) is taken over by the next `execute` like a stale ARMING intent.

**`packed-refs.lock` is never a campaign lockfile (C-1).** It blocks only ref deletion, which the campaign never
performs, so the campaign never creates or owns it: whenever it exists it belongs to some other git process of the
shared repository (gc, pack-refs, a ref deletion in any worktree), and a live git holder has no open descriptor, so
`lsof` cannot prove it stale. The campaign never lists, moves or deletes it. Before the marker, MB r1's carried
`check_clean` refuses `GIT_LOCKED` while it exists (nothing consumed; git releases its own lock). After the marker it
does not block the campaign's ref creates and updates, and a ref write that fails for any reason takes the recorded
`RefWriteError` path of §5 (fail closed); the campaign never works around a git lock.

A verified sealed / pending / spool record wins over the journal (a crash between an artifact write and the journal
update is resolved by the artifact). A file whose canonical layout, self sha256, schema, completeness (`complete: true`
and a terminal status), cell, grant or driver binding fails is **never used**; `result.json.tmp` is never read.

## 5. Persistence contract (architecture §3, as built)

1. The evaluation completes; the record is built in memory (status, mechanical outcome, all records, lifecycle and host
   provenance), `complete: true`.
2. `serialize`: MB r1's layout (indent 1, sorted keys, self sha256), **after one JSON round trip**, so that the self
   sha256 re-verifies from the bytes (MB r1's hashed the pre-normalization object; an int-keyed dict sorts numerically
   before and lexically after a round trip, so MB r1's hash was not re-verifiable — a latent MB r1 defect, harmless
   there because MB r1 never re-verified it).
3. `result.json.tmp`: `O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW` (0600), full write, `fsync` + `F_FULLFSYNC` (a stale tmp is
   renamed aside first).
4. `rename(tmp, result.json)`, directory `fsync` + `F_FULLFSYNC`.
5. Read-back: byte equality and self sha256, else the write fails.
6. Journal → RESULT_DURABLE (result sha256 only).
7. `git -c core.fsync=loose-object,reference -c core.fsyncMethod=fsync hash-object -w`, blob id verified, pending ref
   by CAS from zero (or from a classified stale value); journal → PENDING_RESULT.
8. Seal: private-index commit adding only the result path; branch update by CAS; journal → SEALED
   (INDETERMINATE_SEALED for a failure record).
9. Materialize with `O_EXCL|O_NOFOLLOW`, fsync, read back.

**Ref writes (repair R1 i, ii).** Every ref update is a compare-and-swap. After a failed `update-ref` the ref is
re-read: only "the ref no longer holds the expected old value" is a conflict (another process owns the run:
LostOwnership / JournalConflict / CONSUMED). Any other failure (a stale lockfile, I/O, an unreadable ref) is recorded
and retried on MB r1's frozen seal-retry schedule (`SEAL_RETRY_DELAYS`, reused; no new number), then raised as an
infrastructure failure: a failed checkpoint write is recorded and the evaluation continues; before the marker it
refuses (nothing consumed); after the durable artifacts exist (spool result, pending ref, seal) a failed journal
advance, a conflict included, is recorded and **never stops the seal**: the artifacts decide.

If the spool write fails, the object store is still tried; if both fail the process exits with the journal COMPUTING
(state INTERRUPTED once the process is dead): `recover` resumes (all jobs are checkpointed, so only Stage 2 and the
persistence are redone). Fault points F4–F12 are placed at the steps above (§11).

## 6. Checkpoint governance and resume (architecture §4)

* **What.** Each completed Stage-1 job record is written durably when the job completes: a blob
  (schema `…ckpt.v1`: job key, the record's sha256, the grant, the driver sha256, the attempt number, the journal seq
  that started the attempt, the platform digest, and the record in a lossless tagged JSON that preserves Fractions,
  floats, tuples, dict key types **and dict insertion order**), entered into a flat tree under
  `refs/…/ckpt` by CAS. A checkpoint is never a result (no Stage 2, no decision, no `complete`).
* **How it enters the science.** MB r1's `stage1` is unchanged: it uses the names `ProcessPoolExecutor` and `wait`,
  which MB-S binds to `CheckpointingPool` (serves a verified checkpoint as an already-completed future — never
  recomputed — and submits the rest; records per-job peak RSS; runs the memory watchdog) and `checkpointing_wait` (after
  each wait, writes one checkpoint per newly completed computed job, in the main thread). The aggregation over all
  records is MB r1's own code.
* **Who reads it.** Only `resume`, after `GUARD.arm_target` (the marker names the grant at HEAD), and never after a
  terminal state (**MBS-4**: `verified_records` refuses once the journal is SEALED / INDETERMINATE_SEALED / CLOSING or a
  record is sealed on the branch). No channel prints or materializes checkpoint content; the classifier reads only the
  tree listing. Checkpoints are recorded by count and tree hash, and never deleted.
* **Verification at resume** (each failure = that job is recomputed, and counted): signed canonical bytes, schema, the
  job identity (entry name = checkpoint name = job = the record's kind/block/rung: never job A served as B), grant,
  driver sha256, platform digest, attempt ∈ previous attempts **and** journal seq = the seq that started that attempt
  (not another attempt, not a future seq), record sha256, lossless decode.
* **Mandatory continuation.** After the marker the operator's only permitted actions are `recover` and `resume`
  (`status` is read-only). Frozen terminal rules: (a) a checkpoint failing verification is recomputed; the same job
  failing twice in a row → CONSUMED_UNRECORDED (resume stops **without computing**); (b) at most **3** resumes
  (attempt ≤ 4); (c) **7 days** after the marker; (d) a platform change (RC2 / DR2). Past any of them:
  `close-indeterminate`, which refuses in every other state (**no discretionary abandonment**).
* **Why checkpoints + resume (RC6, decided in advance).** A host reset, a hosting-app death or a lid sleep in the
  middle of a multi-hour Stage 1 otherwise wastes the one evaluation (MB r1's fate). Resumption cannot select an
  outcome: the science is deterministic, a resumed evaluation yields the same bytes of every certified leaf as an
  uninterrupted one (tested: synthetic evaluator, byte-identical sealed target; dev decoy 297, every certified leaf of
  Stage 1 and of five Stage-2 decoy bundles identical), and every resume is budgeted, bound and recorded.
* **Attempt bookkeeping.** The journal is advanced only at state transitions (ARMING, COMPUTING at each attempt start,
  the resume's verification counts, RESULT_DURABLE, PENDING_RESULT, SEALED / INDETERMINATE_SEALED, CLOSING) — never per
  job (**MBS-3**). The EVAL_CAP applies per attempt, on awake time (§8).

## 7. Launch and detachment (architecture §5)

* `code/mbs308_launch.py execute|resume|recover` installs a transient LaunchAgent (plist in `<spool>/launch/`, never
  ~/Library/LaunchAgents; label `org.rebaseguard.mbs308.<mode>.<utc>`; ProgramArguments = the pinned interpreter
  `-I -S -B` + driver + mode; RunAtLoad true; KeepAlive false; AbandonProcessGroup true; ProcessType Standard; logs in
  `~/Library/Logs/ReBaseGuard/mbs308/`; WorkingDirectory the worktree; `MBS308_LAUNCH_LABEL` = the label) and starts it
  with `launchctl bootstrap gui/<uid>`. `execute` is refused unless the driver's `preflight` passes first; `resume`
  unless `status` prints CONSUMED_INTERRUPTED. The preflight runs synchronously with the timeout **PRE_CAP_S + 100 s**,
  a rule and not a number (ratification item 31): the launcher reads PRE_CAP_S from the driver's own bytes, so the
  driver's own PRE_CAP refusal always comes before the launcher's kill, and the timeout follows any change of PRE_CAP_S.
* The launcher records label, pid, PPID, PGID, SID, uid, start time, boot UUID, command sha256 and **proves detachment
  by test, not by PPID = 1**: not a descendant of the launcher's tree, a different session, launchd names the job as
  running with this pid. With `--wait` it boots the job out when it ends; `cleanup <label>` boots out a finished job.
* **Boot-out (repair R2).** After `launchctl bootstrap` the launcher never boots the job out on its own evidence of
  failure (the job may already have passed the marker; a job not properly launched is refused by the driver's own
  launchd check). `--wait` and `cleanup <label>` boot a job out only when its **recorded identity** (pid, start time,
  boot UUID, command sha256) is positively dead (the pid is gone, belongs to another process, or the boot UUID
  changed); a failing, timed-out or unparseable `launchctl print` decides nothing, and a job whose identity was never
  recorded is never booted out automatically. A field of the identity that was never recorded (a `ps` or boot-UUID
  read failed at launch) is never compared (note N-2): while the pid exists such an identity is UNKNOWN, never dead;
  once the pid is gone it is dead.
* The driver's `execute` and `resume` refuse unless `XPC_SERVICE_NAME` **equals** the label (the hosting app exports
  `XPC_SERVICE_NAME=0`, so presence alone proves nothing), the parent is launchd and `launchctl print` names this pid.
* Caffeinate is supervised: `caffeinate -i -m -s -w <driver pid>` is re-spawned whenever it dies; every spawn, death and
  re-spawn is recorded durably (`host-events.jsonl`) and in the sealed record.
* Workers carry a parent-death watch (the driver's pid is passed explicitly: a worker that starts after the driver died
  exits at once instead of blocking forever on the call queue).

## 8. Host contract (architecture §6) and platform (RC2, DR2)

**Preflight gates** (each refuses before the marker, or before the attempt counter moves at `resume`): AC power;
lowpowermode 0; thermal-pressure level 0; free disk ≥ 2 GiB on the repository volume; memory pressure normal
(`kern.memorystatus_vm_pressure_level` = 1); free memory ≥ FREE_MEM_MIN (vm_stat free + inactive + speculative +
purgeable; GC-10; provisional 2 GiB, frozen by R-FREE below); host exclusivity: no process above EXCL_CPU_PCT (25 %;
R-EXCL-PCT below) CPU other than this process tree and the allow-list EXCL_ALLOW (GC-10; provisional: the 39 names
the ratifier read in the driver ∪ {`spotlightknowledged.updater`, `cloudd`, `BackgroundShortcutRunner`,
`modelcatalogd`}, ratification item 16; frozen by R-ALLOW below); boot UUID recorded; no live campaign pidfile; **automatic OS installation disabled** (DR2 c:
`defaults read /Library/Preferences/com.apple.SoftwareUpdate` AutomaticallyInstallMacOSUpdates and CriticalUpdateInstall
must be 0; a missing key is enabled; AutomaticDownload and ConfigDataInstall are recorded; read-only, never changed);
launched by the launcher (execute / resume only).

**Platform pins (RC2), re-verified at `execute`, at every `resume` and in every mode that computes (decoy, rehearse)**:

| pin | value (this host, provisional; re-pinned at freeze from the qualification host) |
|---|---|
| interpreter | `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14`, sha256 `bd3498159da515acf12963b736f3e7e7599619204348868e018bbbc9e0fc9343` |
| libpython | `/Library/Frameworks/Python.framework/Versions/3.14/Python`, sha256 `34463f1b2fc9b5507f493af35080960ba3e86b94c0832c83ea771f8f252b5a55` |
| sys.version | `3.14.5 (v3.14.5:5607950ef23, May 10 2026, 07:38:09) [Clang 21.0.0 (clang-2100.0.123.102)]` |
| OS build | `25F84` (`sw_vers -buildVersion`) |
| architecture | `arm64` (`uname -m`) |

The journal records the platform readings of the marker attempt. **A platform mismatch at resume is the frozen terminal
rule `close-indeterminate` (CONSUMED_UNRECORDED), never a mixed-platform resume** (DR2 b). The no-update window runs
from the marker to the 7-day deadline.

**Recorded, never gating after the marker** (MB r1 E3): sleep channels K / S / L, power, thermal, load, memory pressure,
boot UUID, caffeinate deaths and re-spawns, per-job peak RSS. Host provenance never changes a status, an outcome or
exactly-once. A reboot is detected by the boot UUID and is CONSUMED_INTERRUPTED, never a result.

**Caps.** MB r1's caps are unchanged: per-job CPU caps (RLIMIT_CPU in fresh workers), PRE_CAP 1800 s before the marker,
**EVAL_CAP 8 h per attempt, counted on CLOCK_UPTIME_RAW** (awake time: from the marker or the resume start, never
across a sleep; a hit is an execution failure → INDETERMINATE). **Memory (GC-10):** a per-worker RSS watchdog kills a
worker above the cap (recorded; the pool breaks; INDETERMINATE, never a silent drop). Provisional cap 3 GiB, ratified
for the pre-freeze build and as the measurement cap of the official decoys only; the frozen cap is the output of rule
R-MEM below (the ratification replaced the draft rule "3 × the largest per-job peak, at least 1 GiB" by the stricter
R-MEM), derived at qualification from the official decoy runs only (dev decoy of the build: RLR d4 72 MB, C1B d4
70 MB, C2B N20 88 MB, VER d4 40 MB). A broken pool is released by
SIGKILL (the workers ignore SIGTERM), so a worker death cannot hang the driver.

**Constants set by rule at the freeze (CONSTANTS_RATIFICATION_MBS308, research `3c2a7854`,
CONSTANTS_RATIFIED_WITH_CHANGES, non-holder ratifier; review R3).** `MEM_CAP_BYTES`, `FREE_MEM_MIN_BYTES`,
`EXCL_CPU_PCT` and `EXCL_ALLOW` are frozen as the outputs of the four rules below, computed from the official
qualification evidence and never from any target run, with every input recorded in the qualification. The values in
the code are provisional (ratified for the pre-freeze build only). The rules are carried **verbatim** from the
ratification's section "Written rules" (its dev-input illustration is not part of the rules; its optional builder
recommendation, a path test for R-ALLOW (b), is not taken in this build, so R-ALLOW (b) is checked and recorded for each
addition at the freeze). In R-ALLOW, "the current 39 names" are the 39 names of `EXCL_ALLOW` that the ratifier read
(driver sha256 `7bc2a619…`; the same 39 names at
`35cabb50`).

**R-MEM (MEM_CAP).**
1. *Inputs.* The OFFICIAL decoy runs of the MB-S qualification: the real driver's `decoy` under the launchd launcher,
   frozen ladder, WORKERS 5, the decoy cells of the qualification plan. Each runs with the provisional cap (3 GiB) and
   MEM_POLL_S 2 s. A decoy with any memory-watchdog event is **not a valid input**. It is re-run with the provisional
   cap doubled, within the step-5 bound.
2. P = max over every job of every valid official decoy of max(`job_maxrss_bytes` [ru_maxrss of the job's fresh worker],
   `worker_peak_rss_bytes` [watchdog ps]). D = the driver's own peak RSS in those runs (the qualification records
   ru_maxrss of RUSAGE_SELF).
3. s = max over each (kind, rung) that appears in two or more valid runs of (largest peak / smallest peak). s = 1 if no
   rung appears twice.
4. **MEM_CAP = roundup_256MiB(max(k × P, 1 GiB)), k = max(3, 2s).**
5. *Feasibility (host readings at qualification).* MEM_CAP + (WORKERS − 1) × P + D ≤ hw.memsize − W_idle, where W_idle
   is vm_stat "wired down" × page size in the prepared idle state. If violated, the qualification **fails on memory**.
   k, WORKERS and the floor are never reduced silently.
6. *Poll re-check.* g = the highest RSS growth rate seen by a ≤ 0.5 s qualification sampler. Require
   g × MEM_POLL_S ≤ 0.1 × MEM_CAP; otherwise MEM_POLL_S = max(0.5 s, 0.1 × MEM_CAP / g).

**R-FREE (FREE_MEM_MIN).** FREE_MEM_MIN = max(2 GiB, roundup_256MiB(MEM_CAP + (WORKERS − 1) × P + D)), with the R-MEM
values. It is measured as the driver's own `free_memory_bytes` (vm_stat free + inactive + speculative + purgeable).

*Attainability.* The qualification records ≥ 10 readings, 30 s apart, of the prepared host (AC power, the operator's
apps quit, the hosting app idle). At least 3 consecutive readings must reach FREE_MEM_MIN. Otherwise it records
GATE_UNATTAINABLE: `execute` cannot start on this host, and the value is never reduced silently.

**R-EXCL-PCT (EXCL_CPU_PCT).** EXCL_CPU_PCT = 25. There is exactly one exception. If the hosting app that runs the
launcher, which cannot be quit, exceeds 25 in any prepared-state reading, then EXCL_CPU_PCT = min(50,
roundup_5(1.25 × its maximum reading)). The ceiling of 50 is half the median official-decoy worker reading (about 99),
so a process computing like a worker is always refused. Any other process above the threshold must be quit (or pass
R-ALLOW); it is never a reason to raise the threshold.

**R-ALLOW (EXCL_ALLOW).** The frozen list = the current 39 names ∪ the basename (`comm.rsplit('/')[-1]`, as
`busy_processes` computes it) of every process that meets both conditions:
- (a) it exceeds EXCL_CPU_PCT in any prepared-state qualification reading (≥ 10, 30 s apart) or in this ratification's
  H3 readings;
- (b) its executable path lies under `/System/`, `/usr/libexec/`, `/usr/sbin/`, `/sbin/` or `/Library/Apple/`
  (SIP-protected OS locations).

Never added: anything under `/Applications`, `/Users`, `/opt`, `/usr/local`, `/Library/Frameworks`, `/usr/bin` or
`/bin` (tools a user can invoke), any Python interpreter, or the hosting app. Each addition is recorded with its path
and reading.

The sixteen other ratified items stand as built (ratification table). The ref-write retry schedule of repair R1 (i)
reuses MB r1's frozen `SEAL_RETRY_DELAYS` = 0.5, 1, 2, 4 s (review item 33; source (a), MB r1's driver; completion
only; no new number).

## 9. Pre-marker checks (MB r1's, re-targeted) and GC-8

Interpreter flags `-I -S -B`; identity (worktree, git dir, common dir, branch); **MB r1's recorded state exactly**
(`refs/p5y-k5-cell308-mb-r1/target-consumed` → `afa930727d084a5b70e6b85d30ca8f34c0e8ae74` is the only ref under that
prefix; no MB r1 pending ref; no `mb308-cell308-emergency-result.json` in MB r1's git dir, this git dir or the common
dir; no `NSF/evidence` path in the worktree, at HEAD or on MB r1's branch — a named, reviewed exception, never a
prefix wildcard); no prior MB-S evaluation (no MB-S ref except a stale ARMING intent, no result anywhere, no spool
result file); guarded paths; clean tree; the grant chain and the S1 ruling; science modules (sha256 + blob, also at
HEAD); every research pin (sha256 + blob; MBS-9 iv); lineage; r5 as expected, no r6; seal preconditions (with a
**nonce-carrying** object-store probe, never MB r1's probe bytes); CPU caps; AC; platform; host gates incl. the
launcher; the O_EXCL lock; then controls C-A and C-B (reproduction only, tripwires armed, before the marker; either
failing ⇒ CONTROL_FAILED, sealed, target not consumed).

Then: the journal **intent** (ARMING, CAS from zero or from a stale intent) → fault F1 → the marker (CAS from zero; on
failure the intent is closed as ABORTED_INTENT, which classifies CONSUMED_UNRECORDED, so a refused intent can never make
an unrecorded run look resumable) → F2 → journal COMPUTING (attempt 1) → pidfile → evaluation.

## 10. Frozen outcome table (MB r1 §8 carried over)

| sealed status | condition | conclusion |
|---|---|---|
| TARGET_EVALUATED | all checks pass and **Γ_dec < 0** (exact) | **CELL308_CLOSED_UNDER_MB** |
| TARGET_EVALUATED | all checks pass and Γ_dec ≥ 0 | **CELL308_NOT_CLOSED_UNDER_MB** |
| INDEPENDENT_CHECK_FAILED, INCONSISTENT, C6_REFUSED, TARGET_EVALUATION_FAILED, POST_MARKER_RECORDING_FAILED, RESUME_CONTROL_FAILED, INDETERMINATE_CLOSED (value-free) | any post-marker failure, or the frozen terminal rules of §6 | **CELL308_EXECUTION_INDETERMINATE** (target consumed; no rerun under MB-S; any further successor needs a further governance process and user ruling, S7) |
| CONTROL_FAILED | a control fails before the marker | no conclusion; target not consumed; STOP |

## 11. Tests and qualification cases

Built tonight (target-free; synthetic evaluator; sandboxes; see BUILD_REPORT.md): the state machine and every recover
action; fault points F1–F12 by `os._exit` **and** SIGKILL; the simulations (worker death, reboot, stale lock, stale
pidfile, corrupt tmp, truncated / wrong-hash result, stale pending ref to a missing / wrong blob, concurrent recover,
memory watchdog, awake-time cap, platform change, launcher death, killed process group + session, caffeinate death);
the static RC1 / MBS-9 / MBS-12 checks; the mutant matrix.

Qualification (to be frozen): MB r1's case families QC01–QC13, Q8, Q12 (with host provenance) carried over with the
successor identity, **Q12 re-derived from the successor's own official decoy runtimes measured under the launchd
launcher (RC6)**, plus:

* **QS-STATE / QS-CRASH / QS-LAUNCH / QS-STATIC / QS-MUTANTS**: the test modules of this namespace, official mode.
* **MBR1_REPRO (RC2; designed, run tonight only in its tiny form).** Re-run the non-target decoy / ladder jobs of MB r1's
  official r3 qualification with the successor code and assert EXACT equality (timing keys `seconds`, `wall_seconds`,
  `cpu_seconds`, `cpu_cap` stripped at every depth, as MB r1 QC04) with MB r1's committed records
  `NSF/qualification/MB308_QC02_DECOY_297.json`, `MB308_QC03_DECOY_316_B3.json`, `MB308_QC04_*.json`. A mismatch is a
  STOP. Tiny form run tonight: block 0 of 297 at the dev ladder; the RLR d4 (192 leaves) and C2B N20 (43 leaves) job
  records equal MB r1's committed QC02 block-0 records exactly.
* **QS-RESUME-DECOY (MBS-9 ii; designed, run tonight only in the dev form).** A complete decoy cell (297, all blocks,
  the frozen ladder: RLR, C2B, C1B; VER occurs only in the dev ladder) run uninterrupted and run interrupted by SIGKILL
  after k checkpoints then resumed; every certified leaf of Stage 1 and of every Stage-2 decoy bundle must be
  byte-identical. Dev form tonight: 297 block 0 dev ladder (RLR, C1B, C2B, VER), killed after 2 checkpoints, resumed
  (2 served, 2 computed): Stage 1 (643 leaves) and 5 Stage-2 bundles (883 leaves) identical.
* **MBS-12 carry-overs**: C-A recomputes from committed inputs; `rehearse --cell 305` yields reproduction values and
  equality booleans only, tripwires armed (not run tonight: the builder does not evaluate 305–309); no decoy nearer the
  band than 297 / 316 (asserted); the successor's leak scanner (to be written for QC12) builds its planted strings at run
  time and carries no gain-beside-threshold phrase; no successor file reads C3_KNOCKOUT_RECONSTRUCTION.json (asserted).

## 12. Liabilities carried forward verbatim (S5)

Incidents 01–03 and residue; H4.3b; coordinator disclosures I-a…I-e and E1′; the F2 / F3 exposures through theorem
texts; the quarantine breach of stream A's R1 / R4 (amendment 1); single-implementation RLR block certificates;
result-chasing risk MEDIUM–HIGH; incident-independence review conditions C1–C9; the C4 conditions U1–U8 as the minimum
for any new ruling; MB r1 consumed, interrupted, INDETERMINATE, not negative; cell 308 consumed twice.

## 13. Exit codes

0 sealed TARGET_EVALUATED (or nothing to do); 2 refused (nothing consumed / changed); 3 CONTROL_FAILED sealed; 4
unsealed but durable (run recover); 5 sealed failure / INDETERMINATE record; 6 nothing durable, or resume stopped by the
two-failures rule (run recover); 7 sealed, not materialized (run recover); 8 CONSUMED_COMPUTING (wait); 9 lost
ownership (another attempt advanced the journal; nothing more written).
