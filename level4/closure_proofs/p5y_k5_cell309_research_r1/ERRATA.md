# Cell-309 research campaign r1: errata

Commits are immutable, so corrections live here. Each entry names what is corrected and where the correction is.

| id | item | correction | source |
|---|---|---|---|
| E-1 | commit f0dbaa79 message: "exact-truth FSM 12/12 (premise-level controls with power)" | Overstated. The genuine checks passed 12/12. Of the mutant controls, M1 was caught 12/12 only after the premise-level truth checks were added (in a later edit), M3 was caught 0/12, M2 was not applicable, and the exit status ignored mutants. Corrected: the FSM test's exit status now requires M1 12/12 and M4 ≥ 1, and M3 is covered by the exact two-sided assembly test | review R1 B4/B6 |
| E-2 | `registry/PHASE3_ROUTE_COMPARISON.md` "12/12, including premise-level controls" | Reworded in place (marked) | review R1 B6 |
| E-3 | `ledger/ZERO_TARGET_LEDGER.jsonl`: retroactive correction line saying the real-kernel probe at [1/2, 17/32] ran after the declaration commit f0dbaa79 "(2026-09-29T13:3xZ)" | The declaration commit's time is 13:44:15Z, not 13:3xZ. The claim that the probe ran after it rests on the coordinator's session transcript (tool-call order) and **cannot be verified from the repository** (the probe itself left no timestamp). The probe used a block that is in the declaration, out of band, on the real kernel at e ≤ 17/32. Its ordering relative to the declaration therefore carries no target risk, but it is recorded as unverifiable | review R1 G4 |
| E-4 | `README.md` "no push without explicit authorization" | Superseded by two user authorizations, recorded in README §"Push authorizations": one checkpoint push, then a standing checkpoint-push permission for this branch only, with a nine-check procedure (`code/checkpoint_push.py`) | review R1 G5 |
| E-5 | `theory/THEOREM_SRK.md` §2 ("strictly better exactly when…"), `theory/PHASE1_RESULTS.md` (Theorem L, O3-N "iff", SC-SRK "iff") | Corrected in place, each marked "[Corrected per review R1 B6]" | review R1 B6 |
| E-6 | `tests/test_srk_envelope.py` "planted shrink" control | It was vacuous (always true). Replaced by a sampling soundness control that catches four wrong-corner mutants | review R1 B4 |
| E-7 | decoy certificates in `evidence/srk_decoys/` produced before commit (repair) | Produced from more than one code state, with no producer hash and with `kernel` outside the hashed body. They are **preliminary**: moved to `evidence/srk_decoys_prelim/`, kept as history, and superseded by a single-code-state rerun | review R1 B3/B5 |
