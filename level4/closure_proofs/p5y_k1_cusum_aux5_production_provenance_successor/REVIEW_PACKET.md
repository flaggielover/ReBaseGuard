# Independent-review packet: CUSUM Aux5 production-provenance successor

**Request:** a second independent countersignature. This packet authorizes nothing, and the authoring session has not created a countersignature. Production stays unlaunchable until the reviewer commits `config/COUNTERSIGNATURE.json`, then `prov_entry.py preflight` prints READY, and then an operator runs the launch command.

| Object | sha256 |
|---|---|
| Successor checkpoint `config/PROVENANCE_CHECKPOINT.json` | `dd4c89d773c411355d93d0d703e40c027f9913e11e116e4bfe35117f84b4baf2` |
| Run authorization `config/RUN_AUTHORIZATION.json` (authorization commit `9719cba2`) | `b8f11ec05efc2476f733dd989ae02b542dc9efa374f24fa0a27688d76ec2b329` |
| Envelope schema document `config/ENVELOPE_SCHEMA.json` | `decda981cb1b31ecbe461b4620c8a624b6fde89f92c7b2bfd2aa143629ded197` |
| Synthetic acceptance `evidence/acceptance_r1/ACCEPTANCE_RESULT.json` | `e7139f2cc3d3924f7bc99576a5b8f210f669f5450821cb9d39a26e81a1ba1fb8` |
| Freeze record `config/FREEZE_RECORD.json` | recorded in `RESULT.md` (it cannot contain its own hash) |
| Blocked predecessor checkpoint (preserved, fenced) | `4026f296bd7b32bea24a0f73422f4fc8df1f0c1d04aea952ee7ed0f5313c3c5c` |

## 1. Authoritative governance rule

Derivation: `GOVERNANCE_AUDIT.md`.

```text
AUTHORITATIVE_PRODUCTION_AUTHORITY =
  pre-result hash-bound run authorization (separate from the frozen K1/certifier guard, which is never flipped)
  -> governed production ledger of that authorization
  -> sealed record + production provenance object binding {record bytes, scientific hash, authorization,
     checkpoint, producer, cell, run, kind, binding digest}
  -> integrity-audit admission before adjudication
INLINE_RESULT_BEARING_FLAG_REQUIRED    = NO
EXTERNAL_HASH_BOUND_PROVENANCE_ALLOWED = YES
```

**Sources:**
- K1 `CHECKPOINT.md`: "explicit separate production authorization … must not flip the guard";
- PS1 `LAUNCH_AUTHORIZATION.json` (`result_bearing: false` on the object);
- PS1 `production_provenance.py` (the TEMPORAL, CHECKPOINT, KIND and BINDING layers);
- PS1 `_seal_one` and `production/` (T3/T4/T5 science artifacts have no production field; the sealed record references them by sha256);
- `global_budget.commit`;
- the Lane C audit;
- the K4 checkpoint integrity clause.

## 2. PS1 precedent mapping

Detail: `PS1_PRECEDENT_MAPPING.md`. Every PS1 sealed-record field, `production_provenance` layer, launch-authorization field, launcher gate and Lane C audit maps to EXACT or STRONGER, or to INAPPLICABLE with a stated reason (multi-host role/shard/handoff, the SR patch universe, the SR partition successor id, and a status value kept inside the bound record). `PS1_PROVENANCE_EQUIVALENCE = PASS`.

## 3. Run-level pre-authorization

The authorization is `RUN_AUTHORIZATION.json`, schema `…production-run-authorization.v1`, status `PRE_RESULT_AUTHORIZATION_AWAITING_INDEPENDENT_COUNTERSIGNATURE`. It binds:
- the production checkpoint `dd4c89d7` and the predecessor (BLOCKED);
- the producer identity (`3692d0fe…`, runtime contract `bc75c9ea…`);
- the worker argv template, 4 workers on cores 0, 2, 4, 6;
- the full bound host facts of rebaseguard-vultr-02;
- the exact universe: 326 cells, cell-index sha, geometry digest, cells table sha, m ∈ {1,2,3,5}, 256 bits, far field `CUSUM:-1:far_field:all_m` INHERITED;
- the cap (1.08·10¹² µs = 300 CPU-h, R = 3.6·10⁹ µs, invariant 115/100);
- run id `CUSUM-AUX5-PROD-R1`, ledger id `61eb8565…`, runtime root, ledger and journal schemas;
- the envelope schema and its file sha;
- the executor sources and EXECUTOR_HASH.

Every field is recomputed from the live specification on every load (`verify_authorization`).

**Countersignature requirements** (`verify_countersignature`):
- schema `…production-countersignature.v1`;
- `verdict = APPROVED_FOR_PRODUCTION_LAUNCH`;
- binds `authorization_sha256`, `production_checkpoint_sha256`, `production_run_id`, `mode = PRODUCTION`, `synthetic = false`, and `freeze_record_sha256`;
- `reviewer`, and `reviewer_independent_of_authoring_session = true`;
- committed in git (P07).

**No retroactive authorization.** A ledger can only be created after the authorization and countersignature verify. Its genesis state and journal entry 0 carry the authorization block, a ledger born without the block is refused, and inserting the block later is refused (acceptance t09).

## 4. Per-record provenance envelope

Schema: `config/ENVELOPE_SCHEMA.json`. Code: `code/prov_envelope.py`.

| Section | Binds |
|---|---|
| `scientific_record` | Record path and sha256; record schema; precision bits; scientific_content_hash; auxiliary_evidence_hash; certificate digest and count; the certifier-constant flags as observed |
| `cell` | CUSUM cell index, frozen geometry row and its sha, cells table sha, m values |
| `producer` | The eight identity fields (manifest, runtime contract, producer identity, kind, path, schema, version, campaign) |
| `checkpoint` | Production checkpoint sha; predecessor sha and status |
| `authorization` | Authorization sha, id, run id, ledger id, countersignature sha, executor hash |
| `ledger` | Ledger id, attempt id, supervisor run id, genesis entry sha, and the RESERVED / RUNNING / SEAL entries (seq, sha, t_wall) |
| `host_runtime` | Host name, machine-id sha, runtime contract, boot id, core, pid |
| `cpu_accounting` | charge_usec, evidence class, bucket, ledger reference |
| `qualification` | Not a qualification record; membership test; the four qualification record shas |

It also carries the schema, kind, task_kind `SCIENCE`, synthetic, mode, the composite rule, the record-flag semantics statement, and `binding_sha256`.

- **Object sha256:** the envelope file sha256 is bound in the ledger (`attempts[aid].provenance`, PROVENANCE_BOUND entry), in the audit and in the K4 attestation.
- **Immutability:** read-only once bound; rebinding refused (DUPLICATE_ENVELOPE).
- **Verification:** `verify_pair` recomputes the entire envelope from the record, ledger, journal and authorization, and requires exact equality.

## 5. Adversarial test evidence

Synthetic only, on rebaseguard-vultr-02, clean checkout `9719cba2`: **19/19 PASS**.

| Required case | Test | Refusal |
|---|---|---|
| Valid record + valid envelope → accepted | t01 (+ t17: 326 pairs, frozen K4 integrity gate accepts the pair-verified attestation; assembly not run) | accepted |
| Record only → refused | t02 | PAIR_INCOMPLETE; audit, export and attestation refuse |
| Envelope only → refused | t02 | PAIR_INCOMPLETE |
| Qualification record + forged envelope → refused | t03 | QUALIFICATION_RECORD_REUSE |
| Swapped envelopes between cells → refused | t04 | RECORD_MISMATCH / CELL_MISMATCH; on-disk swap refused by the audit |
| Changed scientific bytes → refused | t05 | RECORD_MISMATCH (incidental and scientific edits); in-place edit refused by the audit |
| Wrong producer → refused | t06 | PRODUCER_MISMATCH / PRODUCER_IDENTITY |
| Wrong checkpoint → refused | t07 | CHECKPOINT_MISMATCH / INCOMPATIBLE_RUN_STATE |
| Wrong run authorization → refused | t08 | NO_PRE_RESULT_AUTHORIZATION / AUTHORIZATION_MISMATCH / AUTHORIZATION_INVALID / COUNTERSIGNATURE_INVALID |
| Envelope created without pre-result authorization → refused | t09 | COUNTERSIGNATURE_MISSING (no ledger created); NO_PRE_RESULT_AUTHORIZATION (after-the-fact and retroactive); SELF_AUTHORIZATION_REFUSED |
| Duplicate envelope → refused | t10 | DUPLICATE_ENVELOPE / ENVELOPE_MISMATCH / HOST_RUNTIME_MISMATCH; stray file refused by the audit |
| Stale / replayed envelope → refused | t11 | LEDGER_LINKAGE (torn attempt); cross-run replay refused |
| Corrupted ledger linkage → refused | t12 | ENVELOPE_NOT_BOUND_TO_LEDGER / RECORD_MISMATCH / JOURNAL_CORRUPT / LEDGER_ROLLBACK_OR_MUTATION |

| Additional property | Test |
|---|---|
| Crash between SEALED and PROVENANCE_BOUND | t13: the unbound attempt is bound deterministically on restart; audit ready |
| Supervisor SIGKILL | t14: recovered seal carries a valid envelope (REAPER_RUSAGE, RECONCILED_SEALED) |
| Record flags other than the certifier constants | t15: `flags_true` / `no_flags` → RECORD_FLAGS; never bound |
| Lifecycle under the provenance layer | t16: drain, failure halt, and cap exhaustion leave every sealed attempt bound |
| Production isolation | t18: no production countersignature exists; production authz refused; launch refused; both production roots untouched |
| Entrypoint before the freeze | t19: exactly P01, P06, P07 and P08 fail |

## 6. Why the internal false flags do not invalidate the composite artifact

- **They are frozen certifier bytes.** `production_run=false`, `result_bearing=false` and `scientific_certification_of_full_cover=false` are constants of the frozen, qualified Aux5 certifier. They sit inside the scientific hash and are identical in qualification and production.
- **Changing them is impossible without breaking the qualification.** Doing so would change the qualified producer identity and invalidate the determinism qualification.
- **What they literally assert is true.** A scientific record by itself authorizes nothing and is not a production result, and the composite rule says the same.
- **They are the certifier-side image of the K1 guard.** Every CUSUM certifier refuses `PRODUCTION_ENABLED`, and the frozen K1 checkpoint forbids flipping that guard and requires a separate authorization. A record that emitted `production_run=true` would contradict frozen governance.
- **The PS1 precedent is identical in structure.** Its science artifacts carry no production field, its governance objects declare `result_bearing: false` of themselves, and production status lives in the sealed provenance-bearing record bound to the pre-result authorization.
- **The layer enforces constancy.** The verifier requires the flags to be exactly the certifier constants (RECORD_FLAGS) and records them verbatim in the envelope. Their constancy is part of what is checked, never overridden.

The disposition belongs to the pair (scientific record, valid envelope). The envelope never claims that the record says otherwise.

## 7. Residuals the reviewer should weigh

1. **Digest, not signature.** As with PS1's `binding`, an adversary who can rewrite the whole ledger, journal and envelopes consistently is out of scope. The countersignature is identified by content and git commit, not by cryptographic signature.
2. **Frozen K4 code trusts its attestation file.** The adjudicator must recompute the attestation with `prov_integrity.verify_k4_attestation` against checkpoint `dd4c89d7`. This is equivalent to the PS1 SR path (Lane C JSON).
3. **`CLOSURE_REPORT_SKELETON.md` §3 still names Aux4.** The adjudicator fills it from the successor integrity audit; there is no code path.
4. **Single-session authorship.** The rule, design, tests and this packet were written by one agent session. That is why a second countersignature is required.
