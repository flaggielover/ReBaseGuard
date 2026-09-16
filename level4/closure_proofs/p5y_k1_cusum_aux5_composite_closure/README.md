# CUSUM Aux5 composite closure

**`CUSUM_AUX5_COMPOSITE_CLOSURE = CLOSED`. `K4_ATTESTATION = PASS`.**

The governed CUSUM Aux5 production universe is the disjoint union of two authorized campaigns:

```text
predecessor production        cells   0-127   128 cells   disposition HALTED    (carried over, never recomputed)
glibc-successor production    cells 128-325   198 cells   disposition COMPLETE
--------------------------------------------------------------------------------------------------------------
governed composite            cells   0-325   326 cells   composite audit COMPLETE, K4 attestation PASS
```

**Scope.** This namespace closes the CUSUM Aux5 composite production universe and nothing else. It is not a K1
verdict, not a P5Y verdict, and it says nothing about the SR / PS1 line, which remains separate and ongoing. No K4
scientific value is evaluated here: the attestation is an integrity attestation over the 326 (record, envelope)
pairs, with `k4_values_evaluated = false`.

**The predecessor is not rewritten.** Its historical disposition stays `HALTED`. "CLOSED" is a property of the
composite, reached by carrying the predecessor's 128 verified pairs forward unchanged — not by re-running them and
not by re-labelling that campaign.

## 1. Lineage

1. **Predecessor production** (checkpoint `dd4c89d7…`, authorization `b8f11ec0…`, countersignature `1ceb92d4…`)
   sealed cells 0-127 and was stopped fail-closed by the frozen host guard (`HOST_DRIFT`) when unattended-upgrades
   replaced glibc `2.41-12+deb13u3` with `deb13u4` on 2026-09-14 at 06:10:59Z. The forensic audit
   (`../p5y_k1_cusum_aux5_glibc_successor/HOST_DRIFT_FORENSIC_AUDIT.md`) established that the stop admitted nothing
   after the drift, started no worker after it, and left 128 verified pairs and old-runtime semantics for cells
   124-127.
2. **Q6 requalification** re-ran the frozen qualification for the representative cells 318 and 323 under the new
   glibc and found bit identity: the same scientific hashes and all 28 certificate hashes per cell
   (`Q6_RESULT.json`, `894f2e8a…`). That is what makes the runtime change inert for the frozen producer, and it is
   the technical precondition for carrying the old cells over instead of recomputing them.
3. **Carry-over countersignature** `e1ee7fb1…` authorized the carry-over rule itself: cells 0-127 stay the
   predecessor's pairs, cells 128-325 are the only successor production universe, and the composite is their
   disjoint union.
4. **Successor checkpoint** `f9380847…` and **run authorization** `0c7621d4…` froze the successor campaign, which
   ran 2026-09-14 13:34Z → 2026-09-16 05:32Z on `rebaseguard-vultr-02` under host containment, sealing all 198
   cells with no failed and no torn attempt.
5. **Terminal closure** (this namespace) settled the ledger, re-audited both halves, attested the composite and
   exported the 326 records.

## 2. Why the predecessor cells were not recomputed

Recomputation was not needed and would have been the weaker choice: Q6 shows the producer is bit-inert across the
glibc change, the 128 pairs were already sealed and envelope-bound under their own authorization, and their record
bytes are re-verified by every composite audit. The carry-over is therefore an evidence-preserving union, not a
convenience. The frozen audit tolerates exactly two predecessor issues — `D_halt` (the bound HOST_DRIFT stop) and
`D_unsettled_supervisor_runs` — and refuses on anything else; no new exception was introduced for this closure.

## 3. Settlement

The frozen supervisor never settles its own final run, so the successor audit could never be ready before an
explicit settlement (`SETTLEMENT_REPAIR.md` in the successor namespace). `gs_entry.py settle` was run once, from
the frozen checkout and the bound venv:

| Quantity | µs |
|---|---|
| Committed before settlement | 412,497,973,063 |
| Supervisor extra (`REAPER_RUSAGE`) | 381,577 |
| Keeper overhead, charged once by record id | 53,463,987 |
| **Committed after settlement** | **412,551,818,627** |
| Science CPU (unchanged by settlement) | 412,353,959,598 |
| Successor residual cap | 817,313,389,420 |

Settlement changed no scientific record and no provenance envelope: the 396 attempt files and 198 envelopes
re-hashed byte-identically afterwards, and disposition, universe and cap were untouched. The predecessor settled
262,686,610,580 µs, so the campaign used 675,238,429,207 µs of the absolute 1,080,000,000,000 µs (300 CPU-h) cap.
Qualification and Q6 CPU are excluded from the cap and disclosed separately.

## 4. Results of the gated closure

| Gate | Result |
|---|---|
| Successor integrity (frozen `prov_integrity.audit`) | PASS — 198/198 sealed, every record, envelope, binding and scientific hash verified, no issue, no settlement blocker |
| Composite audit (`gs_entry.py composite-audit`) | **COMPLETE**, `K4_READY`, `problems []` |
| Carry-over half | 128 verified pairs, cells 0-127, terminal predecessor ledger state `b3cee6ff…` |
| Successor half | 198 verified pairs, cells 128-325, ledger state `241af4f1…` |
| Partition | union exactly 0-325, overlap 0, missing 0, duplicates 0, one producer identity `3692d0fe…` |
| Qualification firewall | no qualification or Q6 record appears in either half or in the export |
| K4 composite attestation (`gs_entry.py attest`) | **PASS**, `cells_verified = 326`, binds the successor checkpoint, which binds the predecessor checkpoint |
| Export (`gs_entry.py export`) | 326 records, one per verified pair, bytes re-checked against the audit |
| Successor failed / torn cells | 0 / 0 (no infra tear, all 198 exits rc 0) |
| Predecessor mutated | NO — the binding re-collected byte-identically (`0676fc82…`) after closure |

## 5. What is in this namespace

| Path | Role |
|---|---|
| `config/CLOSURE_VERDICT.json` | machine-readable verdict and the authoritative hashes |
| `config/ARTIFACT_HASHES.json` | hash inventory: committed artifacts, governance objects, external evidence, CPU accounting |
| `ARTIFACT_INVENTORY.md` | what is committed, what stays external, and how to verify a retrieved archive |
| `evidence/closure_r1/` | the seven small terminal artifacts, byte-identical to the host |
| `code/verify_closure.py` | deterministic verifier and record builder (`verify`, `build`, `--export-tree`) |
| `tests/test_verify_closure.py` | adversarial tests on temporary copies (14) |

```bash
python -B code/verify_closure.py                    # verifies the Git-resident package alone
python -B code/verify_closure.py --export-tree DIR  # also verifies a retrieved 326-record export tree
python -B tests/test_verify_closure.py
```

The verifier rebuilds the K4 attestation from the committed audit with the frozen successor code and requires
canonical equality, so the closure claim is checkable from this repository without contacting the production host.

## 6. Archival policy

The 326 exported record files (~88.8 MiB) are **not** committed. Git keeps the export manifest, which binds every
record by sha256, plus both tree digests. The record bytes themselves remain on `rebaseguard-vultr-02` under
`/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/`, together with the terminal runtime (`ledger.json`,
`journal.jsonl`, `attempts/`, `provenance/`). `ARTIFACT_INVENTORY.md` states exactly what a retrieved archive must
satisfy. The external tree is **not** reproducible from this repository: it can only be re-derived by re-running
the frozen export against the terminal runtime, or re-obtained from the host.

## 7. Host state

Containment (disabled apt timers, masked services, the freeze drop-in, 8 holds) held unchanged through the whole
campaign — `CONTAINMENT_PRE_RESTORE.json` matches the bound `POST_STATE.json` field for field. It was then restored
per `HOST_CONTAINMENT_PLAN.md` §3 steps 1-6, and `CONTAINMENT_POST_RESTORE.json` equals the recorded pre-containment
state. Step 7 (a supervised `unattended-upgrade -v`) was deliberately not run. Unattended upgrades are live again,
so the qualified library hashes recorded in `HOST_AT_CLOSURE.json` are a snapshot: any later campaign on this host
must rebind its host facts.
