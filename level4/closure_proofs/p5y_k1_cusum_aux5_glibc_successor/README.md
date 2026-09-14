# CUSUM Aux5 new-glibc successor: governance freeze (proposal)

**Status: `PROPOSED_NOT_AUTHORIZED`.** This namespace is an additive, hash-addressable proposal for an independent countersignature.

It does **not**:
- authorize carry-over;
- run or authorize requalification (Q6);
- apply host containment;
- create a successor checkpoint, authorization, countersignature, runtime root or ledger;
- launch production.

No frozen predecessor namespace was modified. The predecessor runtime evidence was read only.

## Background

- **The run:** the CUSUM Aux5 production run (checkpoint `dd4c89d7`, authorization `b8f11ec0`, countersignature `1ceb92d4`) sealed cells 0–127.
- **The stop:** the frozen host guard stopped it (`HOST_DRIFT`) after unattended-upgrades replaced glibc `2.41-12+deb13u3` with `deb13u4` at 2026-09-14 06:10:59.785Z.
- **The audit:** the forensic audit shows a fail-closed stop, no post-drift admission or worker start, 128 verified pairs, and preserved old-runtime semantics for cells 124–127.
- **The proposal:** a successor on the new glibc that carries over cells 0–127 and produces cells 128–325. It is gated on Q6: bit and certificate identity of cells 318 and 323 with the predecessor qualification.

## Files

| File | Role |
|---|---|
| `HOST_DRIFT_FORENSIC_AUDIT.md` | Identities, glibc change, timeline, drift proofs, cells 124–127 analysis, integrity, terminal state, settled CPU |
| `CARRYOVER_PROTOCOL.md` | The explicit carry-over rule (R1–R18) and its four activation conditions |
| `config/REQUALIFICATION_PROTOCOL.json` | New-glibc requalification, frozen before execution (P1–P5 + Q6) |
| `config/Q6_REFERENCE.json` | Scientific and 28 certificate hashes per cell from the frozen qualification records |
| `config/CPU_CAP_CONTINUITY.json` | Absolute 300 CPU-h cap, predecessor settled 262,686,610,580 µs, residual 817,313,389,420 µs |
| `HOST_CONTAINMENT_PLAN.md` | Proposed, unapplied upgrade containment and its restore procedure |
| `SUCCESSOR_CHECKPOINT_SPEC.md` | Future checkpoint, ledger, pre-genesis and composite-audit/K4 requirements |
| `config/PREDECESSOR_BINDING.json` | Read-only binding of the terminal predecessor (collected twice, identical) |
| `config/GLIBC_SUCCESSOR_PROPOSAL.json` + `_HASH` | Proposal manifest: sha256 of every artifact above and every predecessor repo object |
| `code/glibc_successor.py` | Collector, builder, fail-closed verifier, Q6 evaluator, launch readiness |
| `tests/test_glibc_successor.py` | Adversarial governance tests (synthetic fixtures only) |

## Commands

```text
python -B code/glibc_successor.py verify-proposal        # exit 0 iff the proposal validates (Q6 not required)
python -B code/glibc_successor.py launch-readiness       # NOT_READY until Q6 PASS + countersignature + checkpoint
python -B tests/test_glibc_successor.py
# on rebaseguard-vultr-02, read-only, from a copy outside the repository:
python -B glibc_successor.py collect --checkout /root/work/postk1-aux5 --out BINDING.json
```
