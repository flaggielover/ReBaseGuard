# Cell-308 MB-S successor campaign (r1): protocol DRAFT

**Status: DRAFT, NOT FROZEN.** Built by the builder (Phases 4–8) from the coordinator design
`research/governance/SUCCESSOR_ARCHITECTURE_308.md` and the binding review conditions (RC1, RC2, RC6, GC-6, GC-8, GC-10,
DR2, MBS-2/3/4/9/12). Nothing here authorizes a target evaluation: there is no freeze, no qualification, no grant and no
marker. **New cell-308 target evaluations: 0.** Cell 308 stays OPEN; r5 is unchanged; there is no r6; K5 and P5Y are
unchanged. Cell 309 is out of scope (S10).

**The user's recorded owner decisions (the three records of section 1; QC13-S binds each by sha256).** S16(c): the
freeze is permitted once every other S16 condition is met (original record, section 1). **MBS-6 = (i)**: an
INDETERMINATE-class outcome of MB-S is final for route MB on cell 308 (section 10). **MBS-7 = (i)**: MB-S's science is
MB r1's, unchanged; C11R-I2 and COR-T are not added within this campaign (section 2; owner supplement 1, section 9).
**MBS-8 = (i)**: MB r1's r3 caps, fixed; Q12 is a prospective pass / fail check of them (section 8). **Section 11.2 =
option (a)**: designated pre-freeze measurements, one freeze carrying the rule outputs, exact re-check at the official
qualification (section 11.2). **Owner supplement 2**: a memory-watchdog event in an official-qualification decoy under
the frozen MEM_CAP fails the qualification closed; only the canonical MEM_POLL_S branches are accepted; the sampler's
bound binds the observed spacing; EXCL_ALLOW's exact set equality is not weakened (section 11.2). **S1**: the grant
binds all three complete owner records (section 1). The decisions were adopted prospectively as the engineering
defaults of the decision brief, not because of any expected cell-308 result.

## 1. Scope, authority and history

* One exactly-once, **closure-only** evaluation of CUSUM K5 cell 308 (m = 5) under route **MB-S**: the science of MB r1
  unchanged, with a new lifecycle. Order: freeze → official qualification → independent qualification review → the
  user's explicit S1 ruling → grant → `execute` (launchd) → execution review → adjudication → adjudication review.
* **USER_RULING_REQUIRED (governance S1).** The grant must carry, verbatim and COMPLETE, the user's explicit ruling
  authorising a second consumed evaluation of cell 308 and re-affirming the C4 terms (U1–U8). By the user's own ruling
  (owner supplement 1, section 6; owner supplement 2, section 12) the S1 bytes are **all three complete owner
  records** (the original decisions and both supplements), never an excerpt and never a paraphrase:

  | record | research path | research commit | bytes | sha256 |
  |---|---|---|---|---|
  | `original` | `level4/closure_proofs/p5y_k5_cell308_research/ledger/USER_RULING_MBS308_OWNER_DECISIONS.txt` | `5c2394baac8aef43dcf9b675d323b0a7e2a9ccef` | 17291 | `34eb1d41b56742fda2ba7fb7b70a46de5e0219ba324aa510437cc6c6d1065ad1` |
  | `supplement_1` | `level4/closure_proofs/p5y_k5_cell308_research/ledger/USER_RULING_MBS308_OWNER_SUPPLEMENT_1.txt` | `8fc2b03856fa58084f6ba1bef8dea46429a99998` | 18797 | `3f7d477b24900b64c7e30b3180ae7114fe642753956e31fe185fc6ef129d33d6` |
  | `supplement_2` | `level4/closure_proofs/p5y_k5_cell308_research/ledger/USER_RULING_MBS308_OWNER_SUPPLEMENT_2.txt` | `74f386a54088a210a51bb81587225dae64def637` | 12941 | `4ba4a6662828137628902c941439f0af33309bde38410ab0cbba3baba90870b0` |

  The grant field `user_ruling_s1` is the deterministic index of the three, in that fixed order:
  `{"records": [{"record", "path", "commit", "bytes", "sha256", "verbatim"}, {…}, {…}], "index_sha256", "reaffirms_c4": true}`,
  where `verbatim` is the record's complete text and `index_sha256` is the sha256 of the canonical JSON of the rows
  `[record, path, commit, bytes, sha256]`. The driver's `check_grant` refuses unless each text re-hashes to the digest
  and length its entry states AND each entry equals the row above (the driver's `S1_OWNER_RECORDS`; the freeze
  manifest's `s1_owner_records` checks the same bytes in git), so a grant cannot carry other bytes, fewer records
  (one alone, or the two that were complete before supplement 2), a fourth record, the records in another order, a
  section-only excerpt or an added paraphrase; `reaffirms_c4` must be true and no other key is
  admitted in the field. The ruling is recorded before the freeze and is conditional on the chain below; it enters the
  grant only after QUALIFICATION_ACCEPTED.
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

**Robustness of the readings and of the lock (REVIEW_OPTIONB_LIVENESS_MBS308 findings O-1 to O-4 and K-1; builder5,
brief 50; no number changed).** (O-1) The start time is read with `TZ=UTC0` in the environment of `ps -o lstart=` (a
fixed POSIX zone, no tz database), for the recorded identity and for every later reading alike, so a change of the
system time zone during a run can no longer read a live recorded process as DEAD. (O-4) A command reading of the form
`(name)` (what `ps -o command=` prints, with exit 0, for an argument vector it cannot read, 0-1 s from exec or exit) is
a failed reading: never recorded, never compared, UNKNOWN (never evidence of death); a zombie's `<defunct>` stays a
reading. (O-2) The recover lock's name never exists without its complete identity record: the record is written and
fsync'd under a private staged name and then linked to the lock name (`link(2)` fails when the name exists, the
O_EXCL semantics), so no acquirer can read an empty or partial lock and break it as "no recorded identity". (O-3) A
LOCK_RACE put-back restores the other breaker's lock under the lock name and then removes the set-aside name, so the
lock keeps one name and its owner can release it; the lock reader accepts a second name (a crash inside either
two-name window), so such a crash can no longer wedge every later acquire. (K-1) The tests plant each reading failure
alone (the boot-UUID read; the command read) and require UNKNOWN.

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
(`kern.memorystatus_vm_pressure_level` = 1); free memory ≥ FREE_MEM_MIN_BYTES (vm_stat free + inactive + speculative +
purgeable; GC-10; set by R-FREE below); host exclusivity: no process above EXCL_CPU_PCT (R-EXCL-PCT below) CPU other
than this process tree and the allow-list EXCL_ALLOW (GC-10; set by R-ALLOW below; until the apply step the driver
carries the provisional values of the pre-freeze build: 2 GiB, 25 % and the 39 names the ratifier read in the driver ∪
{`spotlightknowledged.updater`, `cloudd`, `BackgroundShortcutRunner`, `modelcatalogd`}, ratification item 16; the
values the driver carries are in the rule-output table below); boot UUID recorded; no live campaign pidfile; **automatic OS installation disabled** (DR2 c:
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

**Caps (the user's decision MBS-8 = option (i): MB r1's r3 caps, FIXED; owner decisions section 4).** EVAL_CAP =
**8 h = 28 800 s per attempt, counted on awake time (CLOCK_UPTIME_RAW)**: from the marker or the resume start, never
across a sleep (sleep does not count); a hit is an execution failure → INDETERMINATE. Per-job CPU caps (RLIMIT_CPU in
fresh workers): RLR d4 / d6 / d8 = 1800 / 4200 / 8700 s; C2b N20 / N40 / N80 = 1800 / 1800 / 2700 s; C1b 1800 s; VER
1800 s. PRE_CAP = 1800 s before the marker; WORKERS = 5. These values are not derived from MB-S's own decoy runtimes
(option (ii) is not taken): **Q12 is a prospective pass / fail check of the fixed caps** (section 11) and never
derives, proposes or records a candidate cap; a Q12 failure stops the campaign before the target, and no cap is raised
after it inside this frozen campaign. The verifier checks mechanically that the driver carries exactly these values
(`section4_values`, in case `Q12_caps`). **Memory (GC-10):** a per-worker RSS watchdog kills a
worker above the cap (recorded; the pool breaks; INDETERMINATE, never a silent drop). The cap is the output of rule
R-MEM below (the ratification replaced the draft rule "3 × the largest per-job peak, at least 1 GiB" by the stricter
R-MEM). The provisional 3 GiB (ratified for the pre-freeze build) is the cap of the designated pre-freeze measurement
runs, as R-MEM step 1 states; the frozen driver carries the rule's output and the official decoys run with it
(section 11.2; dev decoy of the build: RLR d4 72 MB, C1B d4 70 MB, C2B N20 88 MB, VER d4 40 MB). A broken pool is
released by SIGKILL (the workers ignore SIGTERM), so a worker death cannot hang the driver.

**Constants set by rule at the freeze (CONSTANTS_RATIFICATION_MBS308, research `3c2a7854`,
CONSTANTS_RATIFIED_WITH_CHANGES, non-holder ratifier; review R3; sequenced by the user's section-11.2 ruling, option
(a): owner supplement 1, part I).** `MEM_CAP_BYTES`, `MEM_POLL_S` (if R-MEM step 6 changes it), `FREE_MEM_MIN_BYTES`,
`EXCL_CPU_PCT` and `EXCL_ALLOW` are frozen as the canonical outputs of the four rules below, never computed from any
target run, with every input recorded. Where the rule text below says "the official decoy runs of the MB-S
qualification" and "qualification readings", the user's ruling places the measurements that FEED the frozen values
before the freeze (the designated pre-freeze measurements, in the exact official configuration, committed as evidence)
and has the official qualification re-measure and re-apply the same rules (section 11.2); the rule text itself is
unchanged. The table shows the values the driver carries; it is written only by the reviewed apply step
(`code/mbs308_repin.py apply`), never by hand, and a test checks it against the driver.

<!-- MBS308-RULE-OUTPUTS-BEGIN (written only by code/mbs308_repin.py apply; never by hand) -->
| constant | value the driver carries | status |
|---|---|---|
| `MEM_CAP_BYTES` | `3221225472` | PROVISIONAL (pre-freeze build; not a rule output) |
| `MEM_POLL_S` | `2` | PROVISIONAL (pre-freeze build; not a rule output) |
| `FREE_MEM_MIN_BYTES` | `2147483648` | PROVISIONAL (pre-freeze build; not a rule output) |
| `EXCL_CPU_PCT` | `25` | PROVISIONAL (pre-freeze build; not a rule output) |
| `EXCL_ALLOW` | `BackgroundShortcutRunner`, `ControlCenter`, `Dock`, `Finder`, `ReportCrash`, `SystemUIServer`, `UserEventAgent`, `WindowServer`, `backupd`, `bird`, `bluetoothd`, `cfprefsd`, `cloudd`, `configd`, `coreaudiod`, `coreservicesd`, `diskarbitrationd`, `distnoted`, `fseventsd`, `hidd`, `kernel_task`, `launchd`, `logd`, `loginwindow`, `mds`, `mds_stores`, `mdworker`, `mdworker_shared`, `modelcatalogd`, `notifyd`, `opendirectoryd`, `powerd`, `remoted`, `runningboardd`, `securityd`, `spindump`, `spotlightknowledged.updater`, `symptomsd`, `syslogd`, `sysmond`, `thermalmonitord`, `trustd`, `watchdogd` (43 names) | PROVISIONAL (pre-freeze build; not a rule output) |
<!-- MBS308-RULE-OUTPUTS-END -->

Until the apply step the values are provisional (ratified for the pre-freeze build only). The rules are carried **verbatim** from the
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

### 8.1 Host-readiness checklist (builder5, brief 50; what must be true before the official qualification and before any execution)

Nothing here changes a system setting: the campaign only reads. A READ-ONLY report of every item is
`code/mbs308_qualify.py --host-report [--work DIR] [--out FILE]` (queries only: `pmset -g`, `ioreg -r`, `defaults read`,
`sysctl`, `vm_stat`, `ps`, `notifyutil -g`, `sw_vers`, `uname`, statvfs); each item carries its status (READY,
NOT_READY, USER_ACTION, RECORDED, UNKNOWN) and how it is checked. An unreadable reading is never RECORDED, and READY
needs a positive reading: an item whose reading could not be taken is UNKNOWN (reviewQ6 F-7; builder7, brief 56).

**The report is embedded in the records, and the operator's actions have a named place (reviewQ6 section 5, note (e);
builder7, brief 56 follow-up).** The official qualification embeds this report, as read at the start of the run, in
its record (`host_report` of `qualification/MBS308_QUALIFICATION.json`) and in its rule-input record (`host_report` of
`qualification/MBS308_RRULES_OFFICIAL_INPUTS.json`); the designated pre-freeze measurement embeds the report it takes
before its readings in its evidence (`host_report` of `evidence_prefreeze/MBS308_RRULES_DESIGNATED.json`). It is a
RECORDED field, not a gate, and brings no number: nobody judges its statuses there; what is checked is its structure
(the read-only report, every item of this checklist with a status, the reference below), so that a record WITHOUT
the embedded report fails: the derivation is not derived from such evidence, and `R_RULES_OFFICIAL` fails on such
evidence or on such a rule-input record. **Where the operator's actions are recorded** (what no reading can show:
the lid open and the host on AC for the whole run, the operator's apps quit, no concurrent sandbox-heavy work,
automatic OS installation disabled by the user): in the research ledger,
`level4/closure_proofs/p5y_k5_cell308_research/ledger/TARGET_INTEGRITY_LEDGER.jsonl` on `p5y-k5-cell308-research`
(the ledger QC13-S reads), as one line for the run written with the research namespace's `code/c308_quarantine.py`
`log_event` by the operator / coordinator, quoting the user's statement and its time. Every embedded report
references that place (`operator_actions`).

| item | before the official qualification | before `execute` / every `resume` | how it is checked |
|---|---|---|---|
| automatic macOS / critical-update installation disabled | required (the platform pins are taken from this host) | required (the no-update window runs from the marker to the deadline) | existing gate `no_automatic_os_install` (DR2 c; `AutomaticallyInstallMacOSUpdates` and `CriticalUpdateInstall` must be 0, a missing key is enabled); **disabling them is the user's action**, the campaign never changes it |
| automatic restart behaviour and scheduled power events | recorded | recorded | `pmset -g` `autorestart` and `pmset -g sched` (the scheduled / repeating power events by type; recorded, no gate; a scheduled restart / shutdown / sleep is for the operator to cancel): any restart is a reboot, detected by the boot UUID and classified CONSUMED_INTERRUPTED (resumable, budgeted); an update-triggered restart is excluded by the item above |
| AC power | required | required | existing gates `require_ac` / `ac_power`; every sample of the sleep channels records the power source (a non-AC reading makes a qualification runtime CONTAMINATED) |
| sleep prevention and the lid | required: lid open, on AC, for the whole run | required: lid open, on AC | existing: the supervised `caffeinate -i -m -s -w <pid>` (execute / resume; the official verifier's own `keep_awake`, `caffeinate -i -m -s`, for its whole run); **caffeinate cannot stop lid-close (clamshell) sleep: keeping the lid open is a user action**; the sleep channels K / S / L detect any sleep (Q12 needs CLEAN); `--host-report` reads the lid (`AppleClamshellState`) and the sleep timers |
| thermal level | 0 at the start | 0 at the start | existing gate `thermal_pressure_0` (recorded after the marker, never gating) |
| low-power mode | 0 | 0 | existing gate `lowpowermode_0` |
| disk | `QUAL_MIN_FREE_BYTES` on the `--work` volume and the ratified 2 GiB on the repository volume, before the verifier's start and before every heavy phase; the mutant runner before its start and before every target run | the ratified `MIN_FREE_DISK` 2 GiB on the repository volume (ratification item 23; section 8.2 checks it against measurements) | new gate (section 8.2) for the qualification; existing gate `free_disk_ge_2GiB` for the execution; a failed probe fails closed in both |
| memory pressure and free memory | normal (level 1); R-FREE's attainability readings (>= 10, 30 s apart, prepared host) | normal; free memory >= FREE_MEM_MIN | existing gates `memory_pressure_normal`, `free_memory_ge_min`; R-FREE attainability is recorded by the designated pre-freeze measurement and re-measured by the official qualification (R_RULES_OFFICIAL; section 11.2) |
| boot identity | recorded | recorded | existing gate `boot_uuid_recorded`; every identity and the journal carry it |
| host identity (platform pins) | the qualification host is the pinned host: PLATFORM_PINS are re-pinned at the freeze from its readings (`code/mbs308_repin.py platform --write-platform`, the pinned interpreter) | the readings must equal the pins | existing `check_platform` at preflight, execute, every resume and every computing mode (RC2 / DR2); a mismatch after the marker is terminal (close-indeterminate) |
| host exclusivity | the operator's apps quit; the prepared-state readings of R-EXCL-PCT / R-ALLOW | no process above EXCL_CPU_PCT outside the allow-list | existing gate `host_exclusive`; quitting apps is a user action; the gate fails closed on NO READING (a failed `ps`, or an output without a process row: reviewQ6 ruling (a)) |
| no other campaign job | none | none | existing gate `no_other_campaign_job` (pidfile LIVE; a pidfile whose recorded process is not POSITIVELY dead refuses too: a failed `ps` or boot-UUID reading is UNKNOWN, never dead) |
| no concurrent sandbox-heavy work | no other agent's suites or matrices on the host during the official run | none from the marker to the seal (the ENOSPC incident's cause) | a recorded user / coordinator action (the start gates cannot see a disk consumer that starts later), recorded in the research ledger as stated above |

### 8.2 Disk safety and the scratch lifecycle (builder5, brief 50; after the ENOSPC incident of 2026-09-30)

**Free space, fail closed.** Every free-space probe is `statvfs` (f_bavail × f_frsize) of the volume; a failed or
unreadable probe is never "enough space". Gates: (i) the driver's own `free_disk_ge_2GiB` (execute, every resume;
`free_disk_bytes` returns None on a failed probe and the gate requires an integer >= MIN_FREE_DISK: it already failed
closed, now tested at the gate and end to end at execute and resume); (ii) the qualification verifier, before its start
(in every mode, before its preconditions and before any record is written) and before every heavy phase (each suite,
the mutant matrix, QS-RESUME-DECOY): QUAL_MIN_FREE_BYTES on the `--work` volume and MIN_FREE_DISK on the repository
volume; (iii) the mutant runner, before its start and before every target run: QUAL_MIN_FREE_BYTES on its scratch
volume. A refusal before the start writes nothing; a refusal before a phase stops every later heavy phase, which fail
closed (`DISK_REFUSED`, or `not_run` in the matrix report). A test may plant a reading (`MBS308_TEST_DISK_FREE`: a
number, `fail`, or `file:<path>`, a file read at every probe so that a test can make the reading fall AFTER the start;
an unreadable file is a failed probe) that can only lower the real one or fail it.

**The scratch lifecycle (`code/mbs308_scratch.py`).** Every process that uses a scratch root records itself in
`<root>/.mbs308-lifecycle/` (its identity, ACTIVE, then FINISHED): the test library for every suite process, the
verifier (its work directory, and each heavy phase), the mutant runner (each phase). Classes: **ACTIVE** (any root
without a valid record, or with a record not FINISHED, or whose owner is not positively dead by
`mbs308_host.identity_state`; UNKNOWN is never dead; a FINISHED record of the calling process itself counts as
finished), **FINISHED** (completed runs' evidence: reports, JSON, logs, probes, verdicts; kept), **DISPOSABLE** (only
sandbox clones, i.e. `sbx` directories whose `.git` borrows objects from a bare base store alone, and bare base stores,
inside a FINISHED root; the nearest recorded root governs). Cleanup (dry-run by default) removes only disposable units
(clones before the store they borrow from; a store still borrowed is kept: the exact rule is the next paragraph),
re-verifies each just before deleting it, records every deletion value-free (`<root>/.mbs308-deletions.jsonl`) BEFORE
it happens (each record is written and fsync'd first, so the log is opened before the first deletion; a log that cannot
be opened or written stops the pass, `DELETIONS_LOG_UNWRITABLE`, and nothing (more) is deleted: no deletion is ever
unrecorded, and a record says that a deletion was started), and never removes a file, a unit of an ACTIVE
root, a symlink or anything reached through one, anything whose real path leaves the root, or anything that is, lies
under or contains a protected path: every worktree of the repository and its common dir (every ref, the target marker,
the pending-result ref, the journal and checkpoint refs, the spool, every seal and committed file), the campaign's
qualified worktree / git dir / common dir and MB r1's git dir as the driver names them, and `~/Library/Logs/ReBaseGuard`.
The mutant runner deletes each phase's sandboxes once its result file is written and verified, so a matrix holds at
most one sandbox at a time; the verifier does the same after each heavy phase. Roots made before this gate carry no
record and are ACTIVE: the tool never cleans them (their owner deletes them by hand).

**Base stores and their borrowers: the exact rule (reviewQ6 F-2 / G-3; builder7, brief 56).** A base store is deleted
only after everything that borrows from it, in whichever root that lies. Every process that uses a base store first
records itself INSIDE the store (`<store>/mbs308-borrowers/<pid>-<nonce>.json`): its identity and ACTIVE; then the real
path of each sandbox clone it is about to make from the store; FINISHED when it ends. The test library does this for
every suite process, whatever its scratch root, and does not use a store in which it cannot write its record; a
process that is killed leaves its record ACTIVE. Cleanup deletes a bare base store only when ALL of the following
hold, and checks them again just before the deletion: (1) the store is a disposable unit of a FINISHED root (above);
(2) it has a borrower register holding at least one record: a store without one cannot be shown to be unborrowed and
is kept (`BASE_STORE_BORROWERS_UNRECORDED`; its owner deletes it by hand); (3) every record of the register is valid
and FINISHED and its owner is positively dead by `mbs308_host.identity_state` (UNKNOWN is never dead; a FINISHED record
of the calling process itself counts as finished): an ACTIVE record, a live or UNKNOWN owner, an invalid or symlinked
record keeps the store (`BASE_STORE_IN_USE`); (4) no sandbox clone that the pass keeps under the cleaned root, and no
clone path that a record of the register names, under ANY root, still exists with the store in its alternates
(`BASE_STORE_IN_USE`). So a store with a live borrower is never deleted, whether the borrower's sandboxes lie under
the cleaned root or under another one, and a store goes only after the clones recorded for it. What the rule cannot
see, stated: a clone made by something that writes no record (a hand-made `git clone --shared`) and lying outside the
cleaned root keeps the store only while the store has no register at all (2).

**Thresholds (derived; inputs measured target-free on this host, 2026-09-30, by builder5; peak allocated bytes of the
scratch tree sampled every 2 s).**

| input | measured | source |
|---|---|---|
| one sandbox (a `--shared` clone checked out at 21e99cf0, 9185 files, and its `.git`) | 0.835 GiB | QS-STATIC peak; the runner's per-phase deletions |
| the base store (`git clone --bare --no-local` of the repository; grows with the repository) | 0.448 GiB (458.4 MiB) | allocated size of builder5's store |
| heaviest phase: QS-DISK (its own sandbox, and a nested verifier with its own base store and a full sandbox) | 2.119 GiB | QS-DISK peak |
| QS-STATE / QS-CRASH / QS-STATIC / QS-RESUME-DECOY (dev form) / one mutant phase | 0.844 / 0.850 / 0.835 / 0.835 / 0.836 GiB | peaks (one sandbox each) |
| QS-QUALIFY / QS-LAUNCH | 0.007 / 0.001 GiB | peaks |
| the full mutant matrix with per-mutant cleanup | at most one sandbox at a time (its peak: BUILD_REPORT section 16.8) | the runner's own meter |
| a synthetic sealed run (18 checkpoints, journal, pending, seal): git-dir growth / spool | 0.27-0.29 MB / 33-37 KB | two sandbox runs (uninterrupted; crash + resume) |
| real-science scale: dev decoy 297 block 0, 4 checkpoint blobs / its Stage-1 record | 39 KB / 54 KB | the dev decoy's sandbox |
| MB r1's full 5-block decoy record | 1.6 MB | ratification evidence Q |
| macOS swap growth | 1 GiB swapfile steps | ratification item 23 |

* **QUAL_MIN_FREE_BYTES = roundup_GiB(2 × (P_max + B) + 1 GiB) = 7 GiB**, with P_max = 2.119 GiB (the heaviest heavy
  phase), B = 0.448 GiB (the verifier's base store, which persists across its phases) and the swap step of item 23.
  Written margin: the factor 2 covers the base store's growth with the repository, run-to-run variation of the test
  artifacts, the records a phase writes and other host activity between the check and the phase's end; the swap step
  is item 23's. The check is repeated before every heavy phase, so the margin never has to cover more than one phase.
* **MIN_FREE_DISK (execution, ratified 2 GiB, item 23): consistent with the measurements; no amendment proposed.** The
  execution writes only MB-scale artifacts: a synthetic sealed run grows the git dir by < 0.3 MB; at real scale the
  checkpoints are about 0.73 × the Stage-1 record (39 KB vs 54 KB on the dev decoy) and a whole decoy record is 1.6 MB,
  so four attempts with the result, the pending blob and the seal stay below about 15 MB, and below 150 MB even for a
  record ten times a decoy's. 2 GiB = one swapfile step + > 6 × that generous bound. What 2 GiB cannot cover is OTHER
  processes filling the volume during the evaluation (the ENOSPC incident's cause): that is a host-discipline item (no
  sandbox-heavy work on the host from the marker to the seal; section 8.1), not a reason for a larger number; a ref or
  spool write that fails anyway takes the recorded fail-closed paths of section 5.

### 8.3 The final host preflight (owner decisions section 14), item by item (builder6, brief 54, part C2)

The user's owner decisions (section 14) list what is verified immediately before target consumption; any failure
stops before the marker. Each listed item is covered as follows. A **gate** refuses `execute` (and every `resume`)
before the marker / before the attempt counter moves; it exists only where an accepted text already makes it one.
The two items no accepted text makes a gate (the lid / sleep state, restart hazards) are **read-only recorded
readings** of `code/mbs308_qualify.py --host-report` (its `owner_section14` field carries this table) plus an
operator checklist line; nothing here changes a system setting.

| owner item | kind | covered by | operator checklist line |
|---|---|---|---|
| AC power | GATE | the driver's preflight gate `ac_power` and `require_ac` in pre_marker_common (execute and every resume refuse before the marker / before the attempt counter moves) | — |
| required lid/sleep state | RECORDED_READING | no accepted text makes the lid a gate (protocol 8.1: caffeinate cannot stop lid-close sleep; keeping the lid open is a user action): --host-report reads, read-only, the lid (ioreg AppleClamshellState) and the sleep / displaysleep / disksleep timers (pmset -g) and whether the sleep channels K / S / L are available; after the start any sleep is detected by K / S / L and recorded in the sealed record | the lid is open and the host is on AC before the launch and stays so until the seal |
| sleep prevention | MECHANISM | the supervised `caffeinate -i -m -s -w <pid>` started by keep_awake in pre_marker_common (re-spawned whenever it dies; every death and re-spawn recorded durably and in the sealed record) | — |
| automatic macOS/critical-update installation disabled as required | GATE | the driver's preflight gate `no_automatic_os_install` (DR2 c: AutomaticallyInstallMacOSUpdates and CriticalUpdateInstall must be 0; a missing key is enabled); read-only: disabling them is the user's action | — |
| restart hazards controlled | RECORDED_READING | update-triggered restarts are excluded by the gate `no_automatic_os_install`; --host-report reads, read-only, `pmset -g` autorestart and the scheduled power events (`pmset -g sched`: a scheduled restart / shutdown / sleep is a hazard); any restart is detected by the boot UUID and classified CONSUMED_INTERRUPTED (resumable within the frozen budget), never a result | no restart, shutdown or sleep is scheduled and no update restart is pending from the launch to the seal |
| thermal state | GATE | the driver's preflight gate `thermal_pressure_0` (recorded after the marker, never gating) | — |
| memory pressure | GATE | the driver's preflight gates `memory_pressure_normal` and `free_memory_ge_min` | — |
| free disk >= frozen threshold | GATE | the driver's preflight gate `free_disk_ge_2GiB` (MIN_FREE_DISK; a failed probe fails closed) | — |
| host identity | GATE | check_platform (the pinned interpreter and libpython with their sha256, the OS build, the architecture: the qualification host) and check_identity (the qualified worktree, git dir, common dir and branch) | — |
| boot identity | GATE | the driver's preflight gate `boot_uuid_recorded`; the journal and every process identity carry the boot UUID | — |
| platform pins | GATE | check_platform at preflight, execute, every resume and every computing mode (RC2 / DR2) | — |
| Git configuration safety | GATE | check_seal_preconditions (committer / author identity; the object store writable, a private index and a trial commit object with the current configuration; the branch ref; the git dir writable), check_clean (the tree clean, ignored files included; no index / HEAD / branch / packed-refs lock), check_not_evaluated (no campaign lockfile), and the driver's own fixed git environment (GIT_NO_REPLACE_OBJECTS=1, GIT_OPTIONAL_LOCKS=0; every durable write passes core.fsync / core.fsyncMethod explicitly); no accepted text names a further git setting | — |
| no stale/conflicting driver | GATE | the preflight gate `no_other_campaign_job` (a LIVE pidfile refuses), check_not_evaluated (a journal that is not a stale pre-marker intent refuses; campaign lockfiles refuse), check_helpers and check_grant (the driver and helper bytes are the granted, pinned bytes), the O_EXCL lock | — |
| exact frozen commit | GATE | check_grant (HEAD is the grant commit on the chain freeze -> qualification -> review -> grant as the grant names it; the driver sha256 and the freeze manifest bound), check_clean and check_bindings (every pinned file equals its blob at HEAD) | — |
| no existing MB-S marker | GATE | check_not_evaluated (any ref under refs/p5y-k5-cell308-mbs-r1/ other than a stale pre-marker intent refuses: CONSUMED) and the marker's compare-and-swap from zero | — |
| no pending-result state | GATE | check_not_evaluated (the pending-result ref refuses: CONSUMED; a result in the tree, in history or in the spool refuses: TARGET_ARTIFACT_EXISTS) | — |
| successor target count still zero | GATE | check_not_evaluated (no MB-S marker, journal attempt, checkpoint, pending result or result exists: zero successor target evaluations) and check_mbr1_state (MB r1's recorded state exactly: cell 308 consumed once, by MB r1) | — |

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
| INDEPENDENT_CHECK_FAILED, INCONSISTENT, C6_REFUSED, TARGET_EVALUATION_FAILED, POST_MARKER_RECORDING_FAILED, RESUME_CONTROL_FAILED, INDETERMINATE_CLOSED (value-free) | any post-marker failure, or the frozen terminal rules of §6 | **CELL308_EXECUTION_INDETERMINATE** (target consumed; no rerun under MB-S; **FINAL for route MB on cell 308**: MBS-6 = option (i), below) |
| CONTROL_FAILED | a control fails before the marker | no conclusion; target not consumed; STOP |

**Finality (the user's decision MBS-6 = option (i): final; owner decisions section 2).** An INDETERMINATE-class
outcome of MB-S is final for route MB on cell 308: it ends route MB on cell 308, and no further route-MB cell-308
evaluation is authorized after such an outcome. This replaces the earlier S7 wording of this table, which left a
further successor to a further governance process: under option (i) there is no further route-MB successor to govern. The
decision was adopted prospectively, as the engineering default of the decision brief, not because of any expected
cell-308 result. It does not reach beyond route MB: a scientifically distinct future route, if governance permits one,
remains subject to its own separately applicable governance, and the user's "do not reopen the changed-science branch"
(MBS-7) means only that, within THIS MB-S campaign, C11R-I2 and COR-T are not added and MB-S's frozen scientific
membership is not otherwise altered; it is not a permanent prohibition on separately governed future scientific work
(owner supplement 1, section 9).

## 11. Tests and qualification cases

Built tonight (target-free; synthetic evaluator; sandboxes; see BUILD_REPORT.md): the state machine and every recover
action; fault points F1–F12 by `os._exit` **and** SIGKILL; the simulations (worker death, reboot, stale lock, stale
pidfile, corrupt tmp, truncated / wrong-hash result, stale pending ref to a missing / wrong blob, concurrent recover,
memory watchdog, awake-time cap, platform change, launcher death, killed process group + session, caffeinate death);
the static RC1 / MBS-9 / MBS-12 checks; the mutant matrix.

Qualification (to be frozen): MB r1's case families QC01–QC13, Q8, Q12 (with host provenance) carried over with the
successor identity, **Q12 checking the FIXED caps (MBS-8 (i)) against the successor's own official decoy runtimes
measured under the launchd launcher (RC6)**, plus:

* **QS-STATE / QS-CRASH / QS-LAUNCH / QS-STATIC / QS-MUTANTS**: the test modules of this namespace, official mode.
* **MBR1_REPRO (RC2; BUILT in its full form by builder6, brief 54; evidence only at the official qualification).**
  Re-run the non-target decoy / ladder jobs of MB r1's
  official r3 qualification with the successor code and assert EXACT equality (timing keys `seconds`, `wall_seconds`,
  `cpu_seconds`, `cpu_cap` stripped at every depth, as MB r1 QC04) with MB r1's committed records
  `NSF/qualification/MB308_QC02_DECOY_297.json`, `MB308_QC03_DECOY_316_B3.json`, `MB308_QC04_*.json`. A mismatch is a
  STOP. The successor's records are the official QC02 / QC03 / QC04 records themselves (no extra run); MB r1's are
  pinned by sha256 and blob. Compared: each decoy record's identity (cell, blocks) and every certified part (Stage 1:
  every block, job, certificate digest, verification and pointwise record; every Stage-2 decoy bundle), the serial
  block-0 jobs and both ladder-determinism records; each comparison must be non-vacuous and detect a planted one-leaf
  mutation. Not compared: provenance (host, lifecycle, driver sha256, utc, walls, the cpu-caps record) and
  `stage1.workers` (MB r1's QC03 ran at 1 worker; the successor's official decoys run at WORKERS, as R-MEM step 1
  requires). Tiny (dev) form: block 0 of 297 at the dev ladder; the RLR d4 (192 leaves) and C2B N20 (43 leaves) job
  records equal MB r1's committed QC02 block-0 records exactly.
* **QS-RESUME-DECOY (MBS-9 ii; BUILT by builder5, brief 50; evidence only at the official qualification).** A
  complete decoy cell (297, all blocks, the frozen ladder: RLR, C2B, C1B; VER occurs only in the dev ladder; WORKERS)
  run uninterrupted (the driver's production `decoy` mode) and run through the checkpoint path, interrupted by SIGKILL
  after k = n // 2 durable checkpoints (n = the uninterrupted run's Stage-1 jobs) then resumed from the verified
  checkpoints; every certified leaf of the decoy output (Stage 1 and every Stage-2 decoy bundle included; timing keys
  stripped) must be byte-identical, the resume must serve k and compute n - k >= 1 with no rejected checkpoint. Case
  runner `tests/mbs308_resume_decoy.py` (value-free record); `--dev` runs the dev form (297 block 0, dev ladder, 2
  workers; never evidence). The job set, n, k and the output keys are read from the runs, so the case is the same under
  either option of MBS-7 (BUILD_REPORT section 16.6). Earlier dev form: 297 block 0 dev ladder, killed after 2
  checkpoints, resumed (2 served, 2 computed): Stage 1 (643 leaves) and 5 Stage-2 bundles (883 leaves) identical.
* **MBS-12 carry-overs**: C-A recomputes from committed inputs; `rehearse --cell 305` yields reproduction values and
  equality booleans only, tripwires armed (not run tonight: the builder does not evaluate 305–309); no decoy nearer the
  band than 297 / 316 (asserted); the successor's leak scanner (to be written for QC12) builds its planted strings at run
  time and carries no gain-beside-threshold phrase; no successor file reads C3_KNOCKOUT_RECONSTRUCTION.json (asserted).

### 11.1 Qualification plan (framework built by the non-holder builder4, research brief 46; NOT frozen)

The verifier `code/mbs308_qualify.py` (modes official / `--review` / `--dev`, as MB r1's; `--work` outside the
repository is required: the suites' sandboxes and a separate `--no-local` base store live there), the manifest writer
`code/mbs308_manifest.py` (runs only with `--freeze`, or `--out` outside the repository), the rule functions
`code/mbs308_rrules.py`, the case list `config/MBS308_QUALIFICATION_CASES.json` (case → gates → status; the governance
records QC13-S checks; the commit pins; the ratification's H3 readings), the tests `tests/test_mbs308_qualify.py` and
the mutants MQ01–MQ34 (appended after builder3's M01–M57). Discipline (MB r1's): every case summary carries a boolean `pass`; the aggregator fails loudly on
a missing or non-boolean `pass`, on a configured case that did not run and on an unknown case; a gate passes only when
every case mapped to it passes; a dev report is never an official PASS; the configuration and the verifier must agree.
Preconditions: HEAD = freeze (review: the qualification commit on it); no review, grant, result or other post-freeze
record in the worktree or in history; no ref under `refs/p5y-k5-cell308-mbs-r1/`; MB r1's recorded state exactly
(GC-8); no spool result; tracked tree clean, and (official) the namespace clean including ignored files; official runs
also need the host ready as section 8 states it (AC, the platform pins, the section-8 preflight gates without the
launcher gate, the sleep channels). The cases that differed between the options of MBS-7 / MBS-8, or depended on the
sequencing question of 11.2, are BUILT under the user's recorded owner decisions (MBS-6 (i), MBS-7 (i), MBS-8 (i),
section 11.2 option (a); the configuration's `owner_decisions` and each case's `decided_by`; non-holder builder6,
research brief 54). A case may still be DECLARED `PENDING_USER_DECISION`: it then returns `pass: false` with its
`depends_on` and no qualification can pass (none is declared at this revision).

**The decision-dependent cases (MBS-7 (i): the science unchanged).** MB r1's frozen implementations are carried,
re-targeted to the successor identity: MB r1's verifier functions (QC02 / QC03 / QC04 evaluations, the serial, ladder,
E4 and Monte-Carlo children, Q1, Q12 with its decision function and planted controls) are carried in
`code/mbs308_qualify.py`, and MB r1's qualification test modules (`tests/test_mb308_twosided.py`, `_a0.py`,
`_tptb.py`, `_guard.py`) are NOT copied: they are executed from MB r1's committed bytes at MB r1's paths (sha256 and
blob at 21e99cf0, checked at HEAD), as the science modules are; the guard test is bound to the successor's guard.
Deviations from MB r1's code are only those the successor architecture requires (BUILD_REPORT section 17 lists each):
the official decoys run as launchd jobs of the launcher, at WORKERS 5 (QC03 too), **one at a time and before every
other heavy phase** (the verifier's gated heavy phases; MB r1 spawned its decoys and children together), with the
frozen memory cap and poll; QC02 / QC03 also require the official configuration; Q12 also requires it (RC6) and does
not record the threshold `ceil(1.5 × projection)` (it never states a candidate cap); the decoy record carries every
R-MEM input. **Order of an official run:** preconditions → the qualification's own prepared-host readings (≥ 10,
≥ 30 s apart; the host still idle) → official decoy 297 → official decoy 316 → MB r1's children (serial, the ladder
pair, E4 together; then the Monte Carlo) → the rehearsal on cell 305's committed record and the in-process cases →
the evaluations (QC02–QC04, QC08, MBR1_REPRO, Q12_caps, R_RULES_OFFICIAL) → the decision-independent cases, the
suites, the mutant matrix, QS-RESUME-DECOY → QC12-S last. **Dev forms** (never evidence; `pass` false, with
`dev_checks_ok`): the decoy cases compute only on decoy 297 block 0 at the development ladder (run directly, 2
workers); QC01 is never run in dev; QC05, QC06, QC07 and QC09-SCI are loader checks in dev (pinned bytes and entry
signature; nothing executed).

| case | gates | status | depends on | content |
|---|---|---|---|---|
| `QS-STATIC` | Q12 | BUILT | none | tests/test_mbs308_static.py, official run |
| `QS-STATE` | Q12 | BUILT | none | tests/test_mbs308_state.py |
| `QS-CRASH` | Q12 | BUILT | none | tests/test_mbs308_crash.py |
| `QS-LAUNCH` | Q12 | BUILT | none | tests/test_mbs308_launch.py (synthetic launchd payload) |
| `QS-QUALIFY` | Q12 | BUILT | none | tests/test_mbs308_qualify.py: this verifier's own planted controls |
| `QS-DISK` | Q12 | BUILT | none | tests/test_mbs308_disk.py: the disk-safety and scratch-lifecycle gate (section 8.2), the re-pin tooling, the read-only host report (section 8.1); builder5 |
| `QS-CASES` | Q12, Q13 | BUILT | none | tests/test_mbs308_cases.py: the decision-dependent cases' own planted controls, the designated-measurement, derivation and apply tools on synthetic inputs, the owner records in the configuration, protocol and manifest; builder6 |
| `QS-MUTANTS` | Q12 | BUILT | none | the full mutant matrix; every mutant killed BY ASSERTION |
| `QC09-S` | Q9, Q12 | BUILT | none | the guard, adapted to the one-line guard diff (refusals; arming in a throw-away repository) |
| `QC09-SCI` | Q9 | BUILT | none (decided: MBS-7) | MB r1's in-process QC09 through every pinned science code path (carried test, bound to the successor's guard); refusals only |
| `QC11-S` | Q2, Q12 | BUILT | none | static structure (what QS-STATIC does not cover) and MB r1's science-byte checks |
| `QC12-S` | Q9 | BUILT | none | leak scans: pinned tail-figure patterns; committed-record tokens (counts only) |
| `QC13-S` | Q10, Q11 | BUILT | none | temporal and governance state by commit and path; the three owner records (the user's freeze decision S16(c), MBS-6 / 7 / 8; the section-11.2 / S1 supplement; owner supplement 2) and the second ratifier's readings (research `ca66e367`) are named and bound by sha256 (an altered or missing record fails closed); fails closed until the implementation review accepting the frozen build is named |
| `Q8-S` | Q2, Q8 | BUILT | none | freeze manifest |
| `R_RULES_CONTROLS` | Q13 | BUILT | none | planted controls through the four rule functions (with the second ratifier's readings and owner supplement 2: observed sampler spacing, event runs, the re-run's step-5 bound, the three cases of step 6, the official series' fail-closed status); the ratification's H3 evidence reproduces the item-16 list |
| `R_RULES_OFFICIAL` | Q13 | BUILT | none (decided: MBS-8; section 11.2) | section 11.2 option (a): canonical outputs B (official measurements) == A (designated pre-freeze measurements) == the frozen driver's constants, exactly, for each of the five; every built-in rule check; FAILS CLOSED with a distinct status on a memory-watchdog event in an official decoy (`QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP`) and on step 6's unrounded-quotient branch (`MEM_POLL_S_NONCANONICAL_BRANCH`) |
| `Q12_caps` | Q12 | BUILT | none (decided: MBS-8) | MB r1's Q12 on the FIXED caps (MBS-8 (i)) against the official decoy runtimes under the launchd launcher (RC6); 14 + 3 planted controls; the section-4 values check |
| `QC01` | Q2 | BUILT | none (decided: MBS-7) | committed-record rehearsal on cell 305 (C-A, C-B; equality only) |
| `QC02` | Q2, Q6, Q7, Q12 | BUILT | none (decided: MBS-7; MBS-8; section 11.2) | full Stage 1 + Stage 2 on decoy cover cell 297, as an official decoy (launchd launcher, WORKERS 5, frozen values); a memory-watchdog event fails it closed (`QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP`) |
| `QC03` | Q6 | BUILT | none (decided: MBS-7; MBS-8; section 11.2) | Stage 1 on blocks 0–2 of decoy cover cell 316, as an official decoy; a memory-watchdog event fails it closed |
| `QC04` | Q3 | BUILT | none (decided: MBS-7) | determinism (serial vs pooled; the REVIEW_A0 C4 ladder pair) |
| `QC05` | Q1, Q4, Q5, Q7 | BUILT | none (decided: MBS-7) | two-sided composition with mutants (carried test) |
| `QC06` | Q2, Q4 | BUILT | none (decided: MBS-7) | pointwise-certificate package (carried test) |
| `QC07` | Q5 | BUILT | none (decided: MBS-7) | TPT-B controls (E4 child and the carried formal test) |
| `QC08` | Q6 | BUILT | none (decided: MBS-7; MBS-8) | independent Monte Carlo on QC02's record |
| `Q1_theory` | Q1 | BUILT | none (decided: MBS-7) | the theorem text binding (MB r1's NSF copy of THEOREM_MB = the research file at bfa9ad3c) |
| `MBR1_REPRO` | Q3 | BUILT | none (decided: MBS-7) | RC2, full form: the official QC02 / QC03 / QC04 records == MB r1's committed official r3 records, exactly (timing stripped) |
| `QS-RESUME-DECOY` | Q3 | BUILT | none | MBS-9 (ii): a complete decoy cell, uninterrupted vs killed after k = n // 2 checkpoints and resumed (tests/mbs308_resume_decoy.py; official form at the official qualification only; builder5) |

MB r1's QC10 (MB r1's own exactly-once flows) is not carried: QS-STATE and QS-CRASH test the successor's lifecycle.

QC12-S scans every file as raw text and every JSON file ALSO as the parser decodes it (keys and string values: a
figure written with a JSON escape has no raw-text match and is seen all the same; the timing-key exemption is
unchanged); its planted controls, this one included, are built at run time from the pinned patterns (builder7, brief
56 follow-up).

### 11.2 The sequencing of the R-rules: the user's ruling, option (a)

**Ruling.** The user chose **section 11.2 option (a)**: designated pre-freeze measurement, then freeze the rule
outputs, then independently re-measure and check them during the official qualification (owner supplement 1, part I:
research `ledger/USER_RULING_MBS308_OWNER_SUPPLEMENT_1.txt`, commit `8fc2b03856fa58084f6ba1bef8dea46429a99998`, sha256
`3f7d477b24900b64c7e30b3180ae7114fe642753956e31fe185fc6ef129d33d6`). Options (b) (a two-step freeze), (c) (the frozen
code reads the values from the qualification evidence) and (d) (the host-state rules re-read at a pre-grant step) are
NOT used; if a later independent review proves option (a) mechanically impossible under the ratified rules, the
campaign stops before the freeze and reports the exact incompatibility (no silent substitution). The question the
ruling answers: the four rules of section 8 take measurements as inputs, while the official qualification runs at the
freeze commit and the manifest and the grant bind the driver's bytes, so the frozen code must already carry the values.

**Rulings on the rule text, implemented as written (no rule text and no rule number changed).** The second ratifier's
readings (research `governance/CONSTANTS_RATIFICATION_MBS308_READINGS_R1.md`, commit `ca66e367`, sha256
`b638e1b3433b54a1bef0479abf325091f712d0e325485ae928dbc7b208fbb2aa`) and the user's owner supplement 2 (research
`ledger/USER_RULING_MBS308_OWNER_SUPPLEMENT_2.txt`, commit `74f386a54088a210a51bb81587225dae64def637`, sha256
`4ba4a6662828137628902c941439f0af33309bde38410ab0cbba3baba90870b0`):

* **Sampler** (readings item 2; supplement 2, sections 4 and 5). R-MEM step 6's "≤ 0.5 s" binds the OBSERVED spacing
  of the sampler's readings (exactly 0.5 s is within); a run whose record shows a larger spacing, or does not state
  it (`max_spacing_ns`), is an invalid input: fail closed. The configured interval is 0.25 s
  (`mbs308_state.RssSampler.INTERVAL_S`): the builder's choice on dev evidence only (BUILD_REPORT section 17), to be
  independently reviewed before the freeze. The first-observation semantics of the growth rate are unchanged
  (READING-7 as confirmed).
* **Event runs** (readings item 4; supplement 2, section 6). A run with a memory-watchdog event is invalid and is
  cured only by the specific valid re-run the rule provides; a clean run of the same cell cures nothing.
* **Designated series** (supplement 2, sections 2 and 7): an event at the provisional 3 GiB is `STEP1_RERUN_REQUIRED`.
  The rule's one re-run is at the provisional cap doubled (6 GiB) and only within the step-5 bound, checked with the
  valid runs' P and D (which P and D stand in it when no other valid run exists is the owner's open point, reported);
  if it does not fit: STOP AND REPORT BEFORE FREEZE. There is no cap-override facility in the driver or the tools, no
  re-run limit, no further doubling, and nothing is inferred: the tools report and stop.
* **Official series** (supplement 2, section 1): ANY memory-watchdog event in an official decoy under the actual frozen
  MEM_CAP fails the case and the qualification CLOSED with the status
  `QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP`: no doubling, no qualification-only cap, no cure by another clean
  run, no grant, no target. The failed evidence is kept (the driver writes the run's record even when the decoy fails).
* **MEM_POLL_S** (readings item 6; supplement 2, sections 2 and 3). Only the canonical branches of step 6 give a
  value: the re-check holds (the re-checked value, unchanged: 2 s in the designated series, the frozen value in the
  official one) or the rule clips to exactly 0.5 s. On the unrounded-quotient branch (0.1 × MEM_CAP / g above 0.5 s)
  the status is `MEM_POLL_S_NONCANONICAL_BRANCH`: the derivation STOPS BEFORE FREEZE and reports the raw evidence
  (g, MEM_CAP, the re-checked value, the exact quotient labelled as not an output) and the branch; in the official
  series the qualification FAILS CLOSED. Nothing is rounded, no precision is chosen and no comparison value is made.
* **Canonical forms** (readings item 6): MEM_CAP_BYTES an integer multiple of 256 MiB, at least 1 GiB; MEM_POLL_S 2 or
  1/2; FREE_MEM_MIN_BYTES an integer multiple of 256 MiB, at least 2 GiB; EXCL_CPU_PCT one of 25, 35, 40, 45, 50;
  EXCL_ALLOW a set of exact basename strings, compared as a set (supplement 2, section 8: no tolerance, subset, union,
  intersection or sticky list). The derivation, the apply step and R_RULES_OFFICIAL refuse any other form.

**The chain (one freeze; no constant changes after the freeze).**

1. **Designated measurements, before the freeze** (`code/mbs308_measure.py designate`; target-free; on the final
   reviewed pre-freeze bytes; any platform re-pin precedes it). The prepared-host readings (≥ 10, ≥ 30 s apart, AC
   power; the inputs of R-FREE's attainability, R-EXCL-PCT and R-ALLOW, with executable paths) and then the
   official-configuration decoys, the same code path as QC02 / QC03's official form: the real driver's `decoy` on cell
   297 (every block) and cell 316 (blocks 0–2), each as a launchd job of the launcher, the frozen ladder, WORKERS 5,
   one run at a time, with the driver's then-current provisional MEM_CAP_BYTES (3 GiB) and MEM_POLL_S (2 s), as R-MEM
   step 1 states. The compact evidence `evidence_prefreeze/MBS308_RRULES_DESIGNATED.json` (the commit, the driver
   sha256, the platform readings, the boot UUID, the host provenance, every rule input; no certified decoy value) is
   committed prospectively. The tool refuses, or marks the evidence invalid (then nothing is written into the
   repository): on battery; on a sleep (channels K / S / L) or a thermal event during a run; when the host is not
   prepared (a process above the threshold that R-ALLOW can never admit must be quit by the operator: its basename and
   path class are reported; a threshold is never raised); when a run is not in the official configuration; when a
   run's sampler record is not a valid step-6 input (the OBSERVED spacing above 0.5 s, or not stated); when a decoy
   failed; and on any memory-watchdog event: `STEP1_RERUN_REQUIRED`, the tool stops, runs nothing more, and records
   the rule's one re-run cap (6 GiB) and whether it is within the step-5 bound, from the valid runs' figures (there is
   no cap-override facility; if the cap does not fit: STOP AND REPORT BEFORE FREEZE).

   *Designation rule: a PROPOSAL of builder6, flagged for the independent review and the owner (the second ratifier:
   whether a decoy with an invalid record may be measured again "must be fixed in the designation of the pre-freeze
   series before the runs"; no accepted text fixes it yet).* (i) The unit is the WHOLE series of one invocation: the
   prepared-host readings and every planned decoy. (ii) An invocation that ends invalid (for any reason of the fixed
   list above, decided by the tool before any derivation is run) designates nothing; its record is kept under `--work`
   as `INVALID_<n>_<utc>_…`, never overwritten, and is listed (name, sha256, status, reasons) in every later record
   made with that `--work`. (iii) A later invocation measures the whole series again: a single decoy is never
   re-measured into an existing series, and no run is ever selected among several. (iv) Once a series is designated
   (the evidence file exists under `evidence_prefreeze/`) the tool refuses to run again (`ALREADY_DESIGNATED`): no
   best-of-N, no replacement. (v) A memory-watchdog event is not a re-measurement case: (ii) applies to its record
   and the rule's own re-run (above) is the only cure the texts provide. (vi) No limit on the number of invalid series
   is set, because no accepted text sets one; every one is recorded.
2. **Derivation** (`code/mbs308_derive.py derive`): the EXISTING rule functions (`code/mbs308_rrules.py`; no rule text
   and no rule number changed) applied mechanically to the designated evidence give the canonical outputs **A**:
   `MEM_CAP_BYTES` (int), `MEM_POLL_S` (2, or 1/2 when the rule clips: the canonical branches only),
   `FREE_MEM_MIN_BYTES` (int), `EXCL_CPU_PCT` (int) and `EXCL_ALLOW` (the canonical sorted, de-duplicated list), each
   checked to be in its canonical form, with every built-in check of the rules recorded: step-1 valid inputs, step-5
   feasibility, the step-6 sampler validity and branch, R-FREE's attainability, R-ALLOW (b) and the never-added list,
   and no process left above the threshold. The derivation `evidence_prefreeze/MBS308_RRULES_DERIVATION.json` is
   committed. Its status is `OK`, or it STOPS BEFORE FREEZE with no output at all: `STEP1_RERUN_REQUIRED`,
   `MEM_POLL_S_NONCANONICAL_BRANCH` (the raw evidence and the branch reported), or `NOT_DERIVED`.
3. **Apply** (`code/mbs308_repin.py apply`; dry-run by default; no hand edit): A is written into the driver's five
   constants and into the rule-output table of section 8; nothing else may change with it (every other top-level
   statement of the driver and every byte of this protocol outside the table are checked to be identical;
   DRIVER_DIFF.md is regenerated by the validated generator). The apply step refuses a derivation that is not
   designated, not OK (a stop status is named as it is), with a rule check that does not hold, with an output that is
   not in its canonical form (MEM_POLL_S is only ever written as `2.0` or `0.5`; no quotient, no rounding), not
   reproduced from the committed evidence, or measured on other driver bytes.
4. **The freeze** carries the outputs A. There is ONE freeze.
5. **The official qualification runs with the ACTUAL FROZEN VALUES**: its decoys (QC02, QC03) run under the frozen
   MEM_CAP_BYTES and MEM_POLL_S; there is no separate 3 GiB / 2 s measurement configuration (owner supplement 1,
   section 3). It takes its own prepared-host readings and records every rule input.
6. **Re-measurement through the same rules**: case `R_RULES_OFFICIAL` re-applies the SAME rule functions to the
   official QC02 / QC03 records and the qualification's own readings, giving the canonical outputs **B** (the cap and
   poll the runs must have been made with are the frozen driver's; step 6 starts from the frozen driver's MEM_POLL_S).
7. **Exact comparison**: `R_RULES_OFFICIAL` passes iff, for each of the five outputs, **B == A == the constant the
   frozen driver carries**, exactly (integers; the exact rational; set equality of the canonical lists), every built-in
   check of the rules holds for A and for B, every official decoy is a valid input, and the frozen driver is the
   measured driver with exactly the five outputs applied. There is **no tolerance anywhere** and no raw observation is
   required to be equal; no superset / subset reading; no canonicalisation that could hide a difference. Two branches
   FAIL CLOSED with a distinct status, lifted by the aggregator to the qualification record
   (`fail_closed_statuses`): a memory-watchdog event in an official decoy
   (`QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP`; the later official decoys and MB r1's children are then not
   launched) and step 6's unrounded-quotient branch in the official series (`MEM_POLL_S_NONCANONICAL_BRANCH`; B has no
   MEM_POLL_S and no comparison value is made). A failed comparison is a qualification failure: STOP before the
   target, no tuning (owner decisions section 11).

**Where exact agreement depends on the host (stated, not resolved; BUILD_REPORT section 17.4).** The user's ruling says
that if exact canonical-output agreement is undefined or inappropriate for a specific output under the accepted rule,
the campaign stops before the freeze and identifies the output and the text. The builder's analysis names, for each of
the five outputs, every property of the rule that makes the agreement of two independent measurement series depend on
run-to-run host variation; the reviewer and the coordinator decide whether that clause applies. Nothing in the code
softens it.

**The Q12 side.** Under MBS-8 (i) the caps are fixed, so Q12 raises no sequencing question of its own: it reads the
official runtimes and passes or fails.

A fact for a reviewer: the driver's decoy record carries each job's `ru_maxrss` (`job_maxrss_bytes`) and the watchdog's
peak for the run (`worker_peak_rss_bytes`), and (builder5, brief 50, task 3; recorded fields of `main()`'s decoy branch
only, no carried function changed) the driver's own peak RSS `lifecycle.driver_maxrss_bytes` (ru_maxrss of RUSAGE_SELF:
R-MEM's D; read LAST, after the run's host-provenance collection, whose power-log read raises the driver's peak, and
immediately before the record is serialised: builder7, brief 56 follow-up), the fixed-rate RSS sampler `lifecycle.rss_sampler` (set interval 0.25 s; samples, failed reads, the largest
OBSERVED spacing `max_spacing_ns`, the driver's and the workers' peak RSS, `max_growth_bytes_per_s`: R-MEM step 6's g)
and the run's configuration `lifecycle.rmem_run` (workers, ladder, mem_cap_bytes, mem_poll_s, first_blocks,
launched_by_launchd: R-MEM step 1). A decoy that FAILS (builder6, brief 54 with owner supplement 2; recorded fields
only) still writes this record, with `decoy_failed` and no stage 1, and the failure is re-raised unchanged: a
memory-watchdog event is therefore mechanically detectable in both series.

### 11.3 Readings of the rule text (made by the rule functions; for the ratifier or a reviewer to confirm)

* READING-1: a prepared-state reading not on AC power is not a valid reading (R-FREE names AC as part of the prepared
  host; the same series serves R-EXCL-PCT and R-ALLOW (a)); "30 s apart" is checked as every consecutive gap ≥ 30 s.
* READING-2: R-MEM step 2's `worker_peak_rss_bytes` is recorded per RUN by the driver (the watchdog's peak over all
  workers), so P = max(every job's `job_maxrss_bytes`, every run's watchdog peak); a per-job ps peak is used when a
  record carries one.
* READING-3: in step 3 a (kind, rung)'s peak in one run is the largest step-2 job peak of that kind and rung in that run
  (its blocks); s compares those per-run peaks across the valid runs in which the (kind, rung) appears.
* READING-4: the hosting app is every process whose executable lies inside its bundle path (given as an input); its
  reading in one snapshot is the largest %cpu of those processes (the gate compares processes one by one).
* READING-5: "any Python interpreter" is a basename `python`, `pythonN` or `pythonN.M`, or any path inside a
  `Python.framework`. The ratification's H3 locations are given as directories, some abbreviated with "…"; condition
  (b) is tested on the location as stated (its prefix).
* READING-6 (CORRECTED by the second ratifier, readings R1 item 2; owner supplement 2, section 5): "a ≤ 0.5 s
  qualification sampler" binds the OBSERVED spacing of the sampler's readings, not its configured interval. A record
  whose largest observed spacing exceeds 0.5 s, or does not state it, is an invalid step-6 input (no g, no MEM_POLL_S);
  exactly 0.5 s is within the bound. The configured interval is not fixed by the text: 0.25 s here (section 11.2).
* READING-7 (CONFIRMED as written by the second ratifier, readings R1 item 3; owner supplement 2, section 4: not
  amended in this campaign): the growth rate of a process is taken between two consecutive readings of that process;
  a process's first reading starts its series, so the rise before a fresh worker's first reading is not counted.
* A decoy re-run after a watchdog event (step 1; readings R1 items 4 and 5; owner supplement 2, sections 6 and 7) runs
  with the provisional cap doubled, every re-run with that one cap; the functions report which runs must be re-run,
  never use an event run's peaks, never treat coverage of its cell by another clean run as a cure, and apply no rule
  until every event run has a valid re-run (`RERUN_REQUIRED`). "Within the step-5 bound" is a condition on the
  doubled cap with the valid runs' P and D. In the official series there is no re-run at all.
* READING-11 (builder6): R-MEM step 5's W_idle ("vm_stat wired down × page size in the prepared idle state") is taken
  as the LARGEST wired-down reading of the prepared-state series, so the feasibility holds for every reading of the
  series. It enters only the feasibility check, no output value.
* READING-12 (builder6): "the hosting app that runs the launcher" (R-EXCL-PCT; READING-4's bundle path) is read from
  the process ancestry of the measuring process: the application bundle (the path up to the first `.app` component) of
  the nearest ancestor whose executable lies inside a bundle; it is recorded with the ancestor chain and never taken
  from an argument. No hosting app found = `HOSTING_APP_NOT_IDENTIFIED` (the rule function's refusal).
* READING-13 (builder6): the "thermal event during a run" that invalidates a designated measurement run (and an
  official decoy as an R-rule input) is the host module's ThermalEvent power-log entry in the run's interval (an
  unreadable log fails closed). The thermal-pressure level is recorded at every sample and gates only the start (0),
  as section 8.1 states. Q12 keeps MB r1 r3's rule: thermal and load are recorded, never part of its pass.
* READING-14 (builder6): a prepared-state reading keeps every process the rules can use, with its executable path:
  every process above 25 %cpu (the smallest value EXCL_CPU_PCT can take; R-ALLOW (a) reads only processes above
  EXCL_CPU_PCT) and every process of the hosting app; this process and its children are excluded, as the driver's
  `busy_processes` excludes its own tree. A prepared-state series in which a process above the threshold is not
  admitted by R-ALLOW is not a prepared-host series (R-EXCL-PCT: such a process "must be quit"): the measurement is
  invalid and the official case fails.
* READING-15 (builder6): a "memory-watchdog event" is an entry of the run's watchdog record for a worker above the
  cap; the watchdog's release of an already-broken pool (`broken_pool_worker_killed`: a kill made because the pool
  broke) is not one. A run with only such entries is an invalid input (a failed decoy) but not an event run: no
  re-run at a doubled cap is called for and the official fail-closed status is not raised by it (the run fails the
  qualification as any failed decoy does). An entry the functions do not know counts as an event (fail closed).
* In the official qualification the rule functions take the cap and poll "each [run] runs with" (step 1) from the
  frozen driver, by the user's ruling (owner supplement 1, section 3); a decoy record carries the poll as the driver's
  float, so the run-configuration check compares it with the float value of the frozen constant, while step 6 uses the
  constant's exact rational.

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
