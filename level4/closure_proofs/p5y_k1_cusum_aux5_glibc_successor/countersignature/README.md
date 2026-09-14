# Independent carry-over countersignature: CUSUM Aux5 new-glibc successor

**Verdict: `APPROVED_CARRYOVER_AND_SUCCESSOR_LAUNCH` (frozen label). What it grants: `CARRYOVER_AUTHORIZED = YES`, `PRODUCTION_LAUNCH_AUTHORIZED = NO`.**

The label is fixed by `SUCCESSOR_CHECKPOINT_SPEC.md` §1 and `glibc_successor.COUNTERSIGN_VERDICT`. It does not launch anything. The countersignature is **necessary but not sufficient** for production. Production additionally requires:
- a valid successor checkpoint;
- a successor run authorization;
- a passing successor launch preflight;
- an explicit operator command.

## Files

| File | Role |
|---|---|
| `../config/COUNTERSIGNATURE.json` | The machine-readable countersignature, at the path the frozen spec names |
| `COUNTERSIGNATURE_HASH` | sha256 of that file |
| `README.md` | This adjudication record (its sha256 is bound inside the countersignature) |
| `code/carryover_countersignature.py` | Deterministic builder and fail-closed verifier |
| `tests/test_carryover_countersignature.py` | Adversarial tests (temporary copies only) |

```text
python -B countersignature/code/carryover_countersignature.py verify    # exit 0 iff the countersignature is valid
python -B countersignature/tests/test_carryover_countersignature.py
```

Countersignature validity does **not** require a successor checkpoint; checkpoint existence belongs to launch readiness. The verifier also proves that the countersignature alone leaves `glibc_successor.launch_readiness` at `NOT_READY` (`SUCCESSOR_CHECKPOINT_ABSENT`).

## 1. What is approved

1. **Carry-over set.** Cells 0–127 are the predecessor carry-over set: the 128 verified (record, envelope) pairs of the terminal predecessor ledger, unchanged.
2. **Successor universe.** Cells 128–325 (198 cells) are the only successor production universe.
3. **Composite model.** `SUCCESSOR_PRODUCTION_RESULT = OLD_CARRYOVER ⊎ NEW_SUCCESSOR`, a disjoint union covering exactly 0–325 (`CARRYOVER_PROTOCOL.md` §2, R12–R14).
4. **Cells 124–127 are admissible.**
   - Their reservations and worker process starts (05:37:52–05:39:53Z) precede the libc replacement (06:10:59.785Z) by at least 31 minutes.
   - The frozen HOST_DRIFT rule halts admissions only, so in-flight attempts seal.
   - dpkg replaces the file by rename, so the running processes kept the old mapped bytes.
   - The certifier starts no child process.
   - Their envelopes and seals verify.
5. **Q6 is sufficient runtime-equivalence evidence.**
   - Under glibc `2.41-12+deb13u4`, cells 318 and 323 (2 repeats each) reproduce the predecessor qualification scientific hashes and all 28 certificate hashes per cell exactly.
   - P1–P5 pass.
   - `Q6_RESULT.json` rebuilds byte for byte from committed evidence.
6. **The K4 composite attestation is admissible.** It is the additive consumer path defined in `SUCCESSOR_CHECKPOINT_SPEC.md` §6, subject to conditions (b) and (c).
7. **Predecessor ledger preserved.** The predecessor HALTED ledger, journal, reaper, records and envelopes stay immutable historical evidence. The terminal disposition is never cleared, reclassified, settled or written.
8. **Predecessor authorization preserved.** The old 128 records stay governed by the predecessor authorization `b8f11ec0…` (`CUSUM-AUX5-PROD-AUTH-001`), its active countersignature `1ceb92d4…` (issuance r2) and checkpoint `dd4c89d7…`. Nothing here re-authorizes, relabels or mutates them.
9. **One continuous cap.** The absolute 300 CPU-h campaign cap is accounted continuously across both ledgers (§4).

## 2. Adjudication of the opposing frozen clause

**Clause.** `level4/closure_proofs/p5y_k1_cover_ledger_successor/CHECKPOINT.md`, line 215 (file sha256 `c487421f…`), in the paragraph that begins "Resume identity includes new checkpoint hash, exact cell-table hash, backend hash, …" (line 213):

> "Old records are evidence only; they cannot satisfy new coverage."

**Finding: `NOT_PROHIBITIVE` for this successor model.**

1. **No new coverage.** The old records do not satisfy the new successor ledger's coverage. That ledger's universe is exactly 128–325, and cells 0–127 are not rows in it. A successor attempt on any of them is refused (`check_no_recomputation`, R12).
2. **Still predecessor-authorized.** The old records are satisfied only as coverage of their own predecessor authorization and ledger, which admitted them before the drift.
3. **No resume or import.** There is no resume record, no import transition, and no predecessor reaper or ledger row read into the successor. The clause governs resume identity, and nothing is resumed.
4. **Successor covers 128–325 only.** Fresh attempts under its own authorization-born genesis produce every successor cell, including 318 and 323.
5. **The union is explicitly governed.** The final scientific result is the explicit, hash-bound, pre-launch disjoint union approved here. It is never a silent carry-over, and never a claim that the predecessor ledger completed.
6. **K4 path is new and additive.** The composite K4 attestation is a new consumer path approved by this countersignature. It does not replace the predecessor's sanctioned consumer path for the predecessor ledger.

**The purpose of the clause is also met.** Cell table, producer identity `3692d0fe…` (which includes the backend-library hashes) and runtime contract `bc75c9ea…` are unchanged. The frozen drift rule asks for "requalification and a new checkpoint", not recomputation.

**Other frozen provisions, also adjudicated**

| Provision | Effect |
|---|---|
| Predecessor `sanctioned_consumer_path` (`PROVENANCE_CHECKPOINT` `dd4c89d7`) and `prov_integrity.audit` (`INTEGRITY_READY_FOR_ADJUDICATION` requires disposition `COMPLETE`) | The predecessor ledger can never be disposition-bearing on its own, and that stays true. Composite consumption of its 128 pairs is a separate, additive path, allowed only under conditions (b) and (c). |
| `K4_ASSEMBLY_CHECKPOINT.json` `integrity.CUSUM` and `k4_assembly.check_cusum_attestation` | They require an attestation schema, `cells_verified == 326`, all scientific hashes verified, one producer identity, and a producer checkpoint sha. They do not require one physical ledger. |
| PS1 `GENERATION_TRANSITION.json` | Precedent for keeping a halt authoritative forever. It is not a scientific carry-over precedent (`historical_results_affected: NONE`). Lacking such a precedent is not a blocker: this rule is explicit, frozen before the Q6 result, result-agnostic (all-or-nothing, cut at a non-scientific event) and independently reviewed. |

## 3. Binding conditions

- **(a) Full checkpoint bindings.** The successor checkpoint and launch preflight must enforce every binding in `SUCCESSOR_CHECKPOINT_SPEC.md`. That includes the exact host and runtime identity (all facts of `REQUALIFICATION_PROTOCOL.json` `host` and the 11 system-library hashes), the containment POST_STATE, and production universe exactly 128–325.
- **(b) Composite audit tolerance.** The future composite audit must run the frozen `prov_integrity.audit` unchanged on the predecessor. It may tolerate exactly:
  - `D_halt`, only for the bound HOST_DRIFT stop;
  - `D_unsettled_supervisor_runs`, only for `R20260913T115713Z-103963`.

  Any other predecessor audit issue must fail closed.
- **(c) K4 checkpoint and disclosure.** The future K4 composite attestation uses the successor checkpoint as `producer_checkpoint_sha256`, and that checkpoint binds the predecessor checkpoint `dd4c89d7…`. Both provenance halves are explicitly disclosed: each half's ledger state, genesis, authorization block and pairs.
- **(d) Necessary, not sufficient.** This countersignature is necessary but not sufficient for production launch: `CARRYOVER_AUTHORIZED = YES` but `PRODUCTION_LAUNCH_AUTHORIZED = NO` until a valid successor checkpoint, run authorization and launch preflight all exist and pass.
- **(e) Fail closed on drift.** Any reboot (a boot id other than the one bound at checkpoint), provider maintenance, or host or runtime identity drift before or during successor production must fail closed.

## 4. CPU continuity

```text
PREDECESSOR_SETTLED_CPU_US = 262686610580   (ledger 262,686,468,127 + supervisor settlement 71,506 + keeper exit 70,947)
ABSOLUTE_CAP_US            = 1080000000000  (300 CPU-h, the predecessor genesis cap)
SUCCESSOR_RESIDUAL_CAP_US  = 817313389420   (successor genesis cap, never changed)
ADMISSION_INVARIANT        = 115/100
```

- **No reset.** Predecessor CPU cannot be reset or removed.
- **Qualification CPU.** Q6 used 8,354.386 CPU-s, with c_max 2,109.124 CPU-s. It is excluded from the cap and disclosed.
- **No raise.** The absolute cap may not be raised.
- **No double charge.** Old cells are charged once, only through the residual cap. There is no import transition.
- **No undercharge.** The predecessor supervisor settlement and the keeper exit are included.

## 5. Review record

- **Re-verification before issuance.** A fresh clone at `575a1ee2`:
  - the proposal and predecessor binding verify;
  - `q6_result.py verify` exits 0;
  - `Q6_RESULT.json` rebuilds byte for byte, and all 4 `run.log` files match their bound hashes;
  - 11/11 Q6 tests and 24/24 proposal tests pass;
  - protected predecessor trees are unchanged;
  - `origin/main` is `1cb45382` (GitHub).
- **Live, read-only, on rebaseguard-vultr-02 at signing.**
  - The predecessor `ledger.json`, `journal.jsonl`, `reaper.jsonl` and all 256 record and envelope files are unchanged; no file was modified after the final seal.
  - The boot id is unchanged, libc is `9792e3cb…`, containment is applied, no certifier or ledger process is running, and no successor runtime root exists.
- **Independence.**
  - This reviewer session did not author the proposal freeze (`3e26bb30`) or the Q6 commit (`74d6efb3`).
  - It performed the preceding independent review.
  - It authored only the evidence-repair commit `575a1ee2`: four `run.log` files byte-identical to the host copies and to hashes already bound in `Q6_RESULT.json`, adding no scientific or governance content.

## 6. Not done here

No successor checkpoint, run authorization, carry-over manifest, runtime root or ledger was created. No qualification, no production, no package, service or timer change, no AWS / SR / PS1 access, and no change to `origin/main`.
